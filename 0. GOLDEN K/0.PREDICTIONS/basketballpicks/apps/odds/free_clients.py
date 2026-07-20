"""BudgetedClient factories for the $0 odds stack (bball-06 §4a).

Each free source gets its OWN BudgetedClient (its own DailyBudget + TokenBucket +
TTL cache) exactly like safepicks' http.py per-source singletons — but wired to
the FREE tiers only (bball-06: NO paid tiers; total mandatory spend to a verdict
is $0). The BudgetedClient itself lives in apps/ingestion/http.py (bball-01 §5
COPY-VERBATIM, owned by the ingestion agent), so it is imported LAZILY inside each
factory: this module imports cleanly even before the ingestion app is wired, and
the pure parse modules in sources/ never need it at all.

*** FREE-SIGNUP TODOs (read keys from settings; NONE hard-coded, NO paid tier) ***
Every setting is read via getattr(settings, NAME, default) so a missing key is a
no-op skip_job (bball-05 §2f "no key, no crash"), never an import/crash. The
operator must complete these free signups and set the env vars:

  TODO(signup): SPORTSGAMEODDS_API_KEY   — free "Amateur" tier, no card.
                https://sportsgameodds.com  (10 req/min, 2,500 objects/mo).
                PRIMARY structured soft-book prop+team feed (bball-06 §1.A1).
  TODO(signup): THE_ODDS_API_KEY         — free "Starter" tier (500 credits/mo).
                https://the-odds-api.com   NB: free tier has NO player props;
                use it for TEAM markets + the Betfair-exchange team anchor, and
                only spot single-event prop pulls (bball-06 §1.A2). Do NOT buy
                the $99 Business tier — it no longer ships Pinnacle either.
  TODO(signup): ODDSPAPI_API_KEY         — free tier (250 req/mo ~ 8 boards/mo).
                https://oddspapi.io  The ONLY free Pinnacle trickle left; spent
                ONLY at closing on flagged marquee games as the sharp AUDIT /
                anti-contamination guardrail (bball-06 §1.D1, §7). VERIFY on first
                key — longevity/ToS risk; treat as could-vanish.
  Bovada / Underdog / PrizePicks need NO key — reverse-engineered public JSON,
  browser User-Agent + polite poll only (bball-06 §1.A3, §1.B).
"""

from django.conf import settings

# ---- polite defaults for keyless / fragile scrape endpoints (bball-06 §2f) ----
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)


def _cfg(name: str, default):
    return getattr(settings, name, default)


def _lazy_http():
    """Import the shared BudgetedClient toolkit lazily so this module never hard-
    depends on the ingestion app being present at import time."""
    from apps.ingestion import http

    return http


# ---------------------------------------------------------------------------
# (A) SPORTSBOOK PROP + TEAM FEEDS — the de-vig raw material
# ---------------------------------------------------------------------------


def sportsgameodds_client():
    """SGO free Amateur tier — the backbone soft-book prop+team feed. The binding
    constraint is 2,500 OBJECTS/mo, budgeted like credits: reserve floors protect
    the CRITICAL final-window pulls to the last object (bball-06 §4a)."""
    http = _lazy_http()
    key = _cfg("SPORTSGAMEODDS_API_KEY", "")
    return http.BudgetedClient(
        source="sportsgameodds",
        base_url=_cfg("SPORTSGAMEODDS_BASE_URL", "https://api.sportsgameodds.com/v2"),
        headers={"X-Api-Key": key} if key else {},
        budget=http.DailyBudget("sportsgameodds", _cfg("SPORTSGAMEODDS_DAILY_BUDGET", 80)),
        bucket=http.TokenBucket(_cfg("SPORTSGAMEODDS_RATE_PER_MIN", 8)),
    )


def the_odds_api_client():
    """The Odds API free Starter tier (500 credits/mo). /events is FREE; spend
    credits on TEAM markets + Betfair anchor, plus spot single-event prop pulls.
    apiKey is a query param owned by the source module (never in the cache key)."""
    http = _lazy_http()
    return http.BudgetedClient(
        source="the_odds_api",
        base_url=_cfg("THE_ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4"),
        budget=http.DailyBudget("the_odds_api", _cfg("THE_ODDS_API_DAILY_BUDGET", 16)),
        bucket=http.TokenBucket(_cfg("THE_ODDS_API_RATE_PER_MIN", 10)),
    )


def bovada_client():
    """Bovada public JSON — the ONLY book whose JSON is reachable from a datacenter
    IP without a 403 (bball-06 §1.A3), so it is the always-on reliability backbone
    of the soft panel. Keyless; browser UA + slow polite bucket + TTL cache."""
    http = _lazy_http()
    return http.BudgetedClient(
        source="bovada",
        base_url=_cfg("BOVADA_BASE_URL", "https://www.bovada.lv/services/sports/event/coupon"),
        headers={"User-Agent": _BROWSER_UA, "Accept": "application/json"},
        budget=http.DailyBudget("bovada", _cfg("BOVADA_DAILY_BUDGET", 5000)),
        bucket=http.TokenBucket(_cfg("BOVADA_RATE_PER_MIN", 6)),  # ~1 req / 10s
    )


# ---------------------------------------------------------------------------
# (B) DFS PICK'EM — the venues we bet against (keyless, browser UA, fragile)
# ---------------------------------------------------------------------------


def underdog_client():
    """Underdog classic vs-house — the PRIME durable venue (advertises no limiting,
    bball-06 §1.B2). Needs a browser UA + Referer; less aggressively gated than PP.
    Free but fragile → generous safety-ceiling budget, no-op skip on 403."""
    http = _lazy_http()
    return http.BudgetedClient(
        source="underdog",
        base_url=_cfg("UNDERDOG_BASE_URL", "https://api.underdogfantasy.com/beta/v5"),
        headers={
            "User-Agent": _BROWSER_UA,
            "Accept": "application/json",
            "Referer": "https://www.google.com/",
        },
        budget=http.DailyBudget("underdog", _cfg("UNDERDOG_DAILY_BUDGET", 5000)),
        bucket=http.TokenBucket(_cfg("UNDERDOG_RATE_PER_MIN", 6)),
    )


def prizepicks_client():
    """PrizePicks public JSON (bball-06 §1.B1) — Cloudflare-gated to datacenter IPs
    (403), live with a residential IP + browser UA. P2P "Arena" conversion has
    degraded its vs-house edge (bball-04 §3d) → DFS source #2, lower priority."""
    http = _lazy_http()
    return http.BudgetedClient(
        source="prizepicks",
        base_url=_cfg("PRIZEPICKS_BASE_URL", "https://api.prizepicks.com"),
        headers={"User-Agent": _BROWSER_UA, "Accept": "application/json"},
        budget=http.DailyBudget("prizepicks", _cfg("PRIZEPICKS_DAILY_BUDGET", 5000)),
        bucket=http.TokenBucket(_cfg("PRIZEPICKS_RATE_PER_MIN", 4)),
    )


# ---------------------------------------------------------------------------
# (D) THE SHARP AUDIT — anti-contamination guardrail
# ---------------------------------------------------------------------------


def oddspapi_client():
    """OddsPapi free tier — the only free Pinnacle left (250 req/mo ~ 8 boards/mo).
    Spent ONLY at closing on flagged marquee games for a low-n sharp CROSS-CHECK
    (bball-06 §1.D1). Tiny budget, HIGH priority to protect it. This is the single
    thread of independent sharp truth guarding against anchor contamination
    (bball-06 §7 / K6)."""
    http = _lazy_http()
    return http.BudgetedClient(
        source="oddspapi",
        base_url=_cfg("ODDSPAPI_BASE_URL", "https://api.oddspapi.io/v4"),
        headers={"User-Agent": _BROWSER_UA},
        budget=http.DailyBudget("oddspapi", _cfg("ODDSPAPI_DAILY_BUDGET", 8)),
        bucket=http.TokenBucket(_cfg("ODDSPAPI_RATE_PER_MIN", 2)),
    )
