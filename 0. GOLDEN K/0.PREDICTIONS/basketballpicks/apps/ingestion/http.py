"""Budgeted HTTP layer for live data sources [bball-01 §4 / bball-02 §4].

COPIED VERBATIM from the safepicks ingestion/http.py infra (the scaffold marks
this COPY-VERBATIM; it is pure infrastructure with zero soccer coupling). Every
outbound call goes through BudgetedClient, which stacks:

* DailyBudget — per-source daily unit counter (Redis-backed when available so
  workers share it; in-process fallback otherwise) with a PRIORITY RESERVE: as
  budget is consumed, low-priority work is refused first.
* TokenBucket — steady request rate with injectable clock/sleep so tests are
  deterministic.
* ResponseCache — per-endpoint TTL cache (Redis when available, in-process
  fallback). Cache hits cost NO budget.
* Backoff — exponential + jitter on 429/5xx/transport errors.

Pure infrastructure: no ORM. Source modules (sources/nba_api.py,
sources/espn_basketball.py, sources/euroleague.py) supply URLs + parsing;
services own persistence. The per-source BudgetedClient FACTORIES for
basketballpicks live in ``apps/ingestion/harvest.py`` (nba_api_client /
espn_basketball_client / euroleague_client) so they can read the basketball
settings block; this module stays source-agnostic. Everything (transport,
clock, sleep, rng) is injectable — tests never touch the network.
"""

import json
import logging
import random
import threading
import time as _time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from enum import IntEnum

from django.conf import settings

logger = logging.getLogger(__name__)

USER_AGENT = "basketballpicks-live/0.1 (research; contact: local)"
DEFAULT_TIMEOUT_S = 30
MAX_RETRIES = 4
BACKOFF_BASE_S = 1.0
RETRYABLE_HTTP = {429, 500, 502, 503, 504}


class TransportError(Exception):
    """Request failed after retries (network or retryable HTTP status)."""


class BudgetExhausted(Exception):
    """The daily budget (or this priority's reserve floor) is spent."""

    def __init__(self, source: str, priority: "Priority", spent: int, limit: int):
        self.source, self.priority, self.spent, self.limit = source, priority, spent, limit
        super().__init__(
            f"{source}: budget refused at priority {priority.name} ({spent}/{limit} spent)"
        )


class Priority(IntEnum):
    """Degradation order — lower value = protected longer."""

    CRITICAL = 0  # final-window prop/injury polling: protected first
    HIGH = 1  # T-24h polling, closing capture
    NORMAL = 2  # results, box scores
    LOW = 3  # discovery / schedule sweeps: sacrificed first


# A request at priority p is allowed only while spent < limit * (1 - floor).
RESERVE_FLOORS = {
    Priority.CRITICAL: 0.00,
    Priority.HIGH: 0.05,
    Priority.NORMAL: 0.15,
    Priority.LOW: 0.30,
}


# ---------------------------------------------------------------------------
# stores: Redis when reachable, in-process fallback
# ---------------------------------------------------------------------------


class InProcessStore:
    """Minimal shared-nothing fallback for budget counters + cache."""

    def __init__(self):
        self._counters: dict[str, int] = {}
        self._cache: dict[str, tuple[float, str]] = {}
        self._lock = threading.Lock()

    def incr_by(self, key: str, amount: int) -> int:
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + amount
            return self._counters[key]

    def get_count(self, key: str) -> int:
        return self._counters.get(key, 0)

    def cache_get(self, key: str, now: float) -> str | None:
        item = self._cache.get(key)
        if item is None:
            return None
        expires_at, body = item
        if now >= expires_at:
            self._cache.pop(key, None)
            return None
        return body

    def cache_set(self, key: str, body: str, ttl_s: float, now: float) -> None:
        with self._lock:
            self._cache[key] = (now + ttl_s, body)


class RedisStore:
    """Same interface over Redis — shared across worker processes."""

    def __init__(self, client):
        self._r = client

    def incr_by(self, key: str, amount: int) -> int:
        value = self._r.incrby(key, amount)
        self._r.expire(key, 2 * 24 * 3600)
        return int(value)

    def get_count(self, key: str) -> int:
        v = self._r.get(key)
        return int(v) if v is not None else 0

    def cache_get(self, key: str, now: float) -> str | None:  # noqa: ARG002 (Redis owns TTL)
        v = self._r.get(key)
        if v is None:
            return None
        return v.decode("utf-8") if isinstance(v, bytes) else str(v)

    def cache_set(self, key: str, body: str, ttl_s: float, now: float) -> None:  # noqa: ARG002
        self._r.set(key, body, ex=max(1, int(ttl_s)))


_default_store: "InProcessStore | RedisStore | None" = None
_store_lock = threading.Lock()


def default_store():
    """Redis if it answers a ping quickly, else in-process; resolved once."""
    global _default_store
    with _store_lock:
        if _default_store is None:
            try:
                import redis

                client = redis.Redis.from_url(
                    settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1
                )
                client.ping()
                _default_store = RedisStore(client)
                logger.info("http budget/cache store: redis (%s)", settings.REDIS_URL)
            except Exception:
                _default_store = InProcessStore()
                logger.info("http budget/cache store: in-process fallback (redis unreachable)")
        return _default_store


# ---------------------------------------------------------------------------
# budget + rate limiter + cache
# ---------------------------------------------------------------------------


class DailyBudget:
    """Per-source daily unit budget with priority reserve floors. Units are
    whatever the source bills: requests (nba_api/espn) or credits (the_odds_api
    charges markets x regions per call) — ADR 007."""

    def __init__(self, source: str, limit: int, store=None, clock: Callable[[], float] = None):
        self.source = source
        self.limit = int(limit)
        self.store = store if store is not None else default_store()
        self.clock = clock or _time.time

    def _key(self) -> str:
        day = _time.strftime("%Y%m%d", _time.gmtime(self.clock()))
        return f"budget:{self.source}:{day}"

    @property
    def spent(self) -> int:
        return self.store.get_count(self._key())

    def allow(self, priority: Priority, cost: int = 1) -> bool:
        ceiling = self.limit * (1.0 - RESERVE_FLOORS[priority])
        return self.spent + cost <= ceiling

    def check(self, priority: Priority, cost: int = 1) -> None:
        if not self.allow(priority, cost):
            raise BudgetExhausted(self.source, priority, self.spent, self.limit)

    def charge(self, cost: int = 1) -> int:
        return self.store.incr_by(self._key(), cost)


class TokenBucket:
    """Classic token bucket; refills continuously at rate_per_min. acquire()
    blocks (via the injected sleeper) until a token exists."""

    def __init__(
        self,
        rate_per_min: float,
        capacity: float | None = None,
        clock: Callable[[], float] = None,
        sleeper: Callable[[float], None] = None,
    ):
        self.rate_per_s = rate_per_min / 60.0
        self.capacity = capacity if capacity is not None else max(1.0, rate_per_min / 6.0)
        self.tokens = self.capacity
        self.clock = clock or _time.monotonic
        self.sleeper = sleeper or _time.sleep
        self._last = self.clock()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self._last) * self.rate_per_s)
        self._last = now

    def acquire(self) -> float:
        """Take one token; returns seconds slept (0.0 when a token was free)."""
        slept = 0.0
        with self._lock:
            while True:
                self._refill()
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return slept
                deficit = (1.0 - self.tokens) / self.rate_per_s
                self.sleeper(deficit)
                slept += deficit


class ResponseCache:
    """TTL cache over the shared store; keys are full request URLs."""

    def __init__(self, store=None, clock: Callable[[], float] = None):
        self.store = store if store is not None else default_store()
        self.clock = clock or _time.time

    def get(self, url: str) -> str | None:
        return self.store.cache_get(f"httpcache:{url}", self.clock())

    def set(self, url: str, body: str, ttl_s: float) -> None:
        if ttl_s > 0:
            self.store.cache_set(f"httpcache:{url}", body, ttl_s, self.clock())


# ---------------------------------------------------------------------------
# transport + client
# ---------------------------------------------------------------------------


def urllib_transport(url: str, headers: dict, timeout: float = DEFAULT_TIMEOUT_S) -> str:
    """Real transport (stdlib urllib per project convention, ADR 007).
    Raises urllib.error.HTTPError / URLError; BudgetedClient owns retries."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (https only)
        return resp.read().decode("utf-8", errors="replace")


class BudgetedClient:
    """The single gateway for a source's HTTP traffic.

    get_json() applies, in order: cache -> budget check (priority reserve) ->
    token bucket -> transport with backoff+jitter -> budget charge per real
    attempt -> cache store. `requests_made` / `cache_hits` feed the JobRun
    stats of the calling service.
    """

    def __init__(
        self,
        source: str,
        base_url: str,
        headers: dict | None = None,
        budget: DailyBudget | None = None,
        bucket: TokenBucket | None = None,
        cache: ResponseCache | None = None,
        transport: Callable[..., str] = urllib_transport,
        sleeper: Callable[[float], None] = None,
        rng: random.Random | None = None,
    ):
        self.source = source
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.budget = budget or DailyBudget(source, limit=1000)
        self.bucket = bucket or TokenBucket(rate_per_min=60)
        self.cache = cache or ResponseCache()
        self.transport = transport
        self.sleeper = sleeper or _time.sleep
        self.rng = rng or random.Random()
        self.requests_made = 0
        self.cache_hits = 0

    def url_for(self, path: str, params: dict | None = None) -> str:
        query = urllib.parse.urlencode(sorted((params or {}).items()))
        return f"{self.base_url}/{path.lstrip('/')}" + (f"?{query}" if query else "")

    def get_json(
        self,
        path: str,
        params: dict | None = None,
        *,
        priority: Priority = Priority.NORMAL,
        ttl_s: float = 0.0,
        cost: int = 1,
    ) -> "dict | list":
        url = self.url_for(path, params)
        if ttl_s > 0:
            cached = self.cache.get(url)
            if cached is not None:
                self.cache_hits += 1
                return json.loads(cached)

        self.budget.check(priority, cost)

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            if attempt:
                delay = BACKOFF_BASE_S * (2 ** (attempt - 1)) + self.rng.uniform(0, BACKOFF_BASE_S)
                logger.warning(
                    "%s: retry %d/%d after %.2fs (%r)",
                    self.source, attempt, MAX_RETRIES, delay, last_exc,
                )
                self.sleeper(delay)
            self.bucket.acquire()
            self.budget.charge(cost)  # every real attempt bills the provider
            self.requests_made += 1
            try:
                body = self.transport(url, self.headers)
                if ttl_s > 0:
                    self.cache.set(url, body, ttl_s)
                return json.loads(body)
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP:
                    raise  # 4xx contract errors surface immediately
                last_exc = exc
            except urllib.error.URLError as exc:
                last_exc = exc
        raise TransportError(f"{self.source}: gave up after {MAX_RETRIES} retries ({last_exc!r})")
