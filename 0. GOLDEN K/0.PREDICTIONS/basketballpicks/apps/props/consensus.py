"""The soft-book CONSENSUS pseudo-book anchor (bball-06 §1.D2, §4b).

Post the Pinnacle public-API shutdown (bball-06 §0) no free tier serves a Pinnacle
prop board, so the bball-05 §2d "market_consensus" FALLBACK is PROMOTED to the
primary anchor: for each (player, market) we de-vig every non-DFS soft book quoting
it and fit ONE repriceable consensus distribution (reusing devig_engine.fit_cdf).
Evaluating that CDF at a venue's line does the line-normalization (§2b) for free.

*** ANCHOR-CONTAMINATION GUARDRAIL (bball-06 §7 — the single biggest $0 risk) ***
The consensus is a de-vig of the SAME soft market we grade an edge against, so when
all soft books share a blind spot the "truth" is wrong WITH them and a phantom edge
appears. The structural mitigation lives HERE: `exclude_book` implements a
LEAVE-ONE-OUT consensus — when the edge engine prices a soft book's line, it rebuilds
the anchor WITHOUT that book, so a book never votes on its own fairness. Residual
shared-error is caught downstream by the OddsPapi Pinnacle audit (edge.engine, K6).

Pure core (build_consensus_at) is unit-tested with plain quote objects; the ORM
materialiser reads PropLine and writes PropConsensus.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from . import devig_engine as de

# Books whose de-vig NEVER enters the consensus panel: DFS pick'em (no two-way
# price), the OddsPapi audit book (must stay independent), and aggregates.
EXCLUDED_FROM_PANEL = frozenset(
    {"underdog", "prizepicks", "pick6", "pinnacle", "market_max", "market_avg"}
)


@dataclass(frozen=True, slots=True)
class ConsensusResult:
    p_over: float | None
    n_books: int
    books: tuple[str, ...]
    method_spread: float  # median per-book |shin − mult| — the method-sensitivity screen
    reprice_units: float
    within_cap: bool
    from_default_sigma: bool
    excluded_book: str | None


def _panel_quotes(quotes, exclude_book):
    seen = {}
    for q in quotes:
        if getattr(q, "is_dfs", False):
            continue
        book = q.book.lower()
        if book in EXCLUDED_FROM_PANEL or book == (exclude_book or "").lower():
            continue
        if q.over_price is None or q.under_price is None:
            continue
        # keep the freshest / first quote per book at each line
        seen.setdefault((book, float(q.line)), q)
    return list(seen.values())


def build_consensus_at(quotes, market: str, target_line: float, *, exclude_book: str | None = None,
                       method: str = "shin") -> ConsensusResult:
    """Consensus P(over target_line): fit a CDF to every panel book's de-vigged
    line, evaluate at target_line. `exclude_book` = the leave-one-out guardrail."""
    panel = _panel_quotes(quotes, exclude_book)
    if not panel:
        return ConsensusResult(None, 0, (), 0.0, 0.0, False, False, exclude_book)

    points: list[de.AnchorPoint] = []
    spreads: list[float] = []
    books: list[str] = []
    for q in panel:
        fair = de.fair_two_way(q.over_price, q.under_price, method=method)
        if not fair:
            continue
        points.append(de.AnchorPoint(line=float(q.line), p_over=fair["p_over"]))
        spreads.append(fair["method_spread"])
        books.append(q.book.lower())

    cdf = de.fit_cdf(points, market)
    if cdf is None:
        return ConsensusResult(None, 0, (), 0.0, 0.0, False, False, exclude_book)
    rp = de.reprice(cdf, target_line)
    return ConsensusResult(
        p_over=rp.p_over,
        n_books=len(set(books)),
        books=tuple(sorted(set(books))),
        method_spread=statistics.median(spreads) if spreads else 0.0,
        reprice_units=rp.reprice_units,
        within_cap=rp.within_cap,
        from_default_sigma=rp.from_default_sigma,
        excluded_book=exclude_book,
    )


# ---------------------------------------------------------------------------
# ORM materialiser (runs post-integration; read PropLine → write PropConsensus)
# ---------------------------------------------------------------------------


def materialise_consensus(game, *, at=None, is_closing=False):
    """Read this game's soft PropLine snapshots and write one PropConsensus row per
    (player, market, line) actually quoted by a DFS/soft venue we might bet. Anchor
    is always "consensus" here; the "pinnacle" audit rows are written by the edge
    layer from OddsPapi. Idempotent by the model's unique key. Returns rows written.

    NB: no-op-clean on empty input (safepicks empty-runs-clean discipline)."""
    from django.utils import timezone

    from .models import PropConsensus, PropLine

    at = at or timezone.now()
    lines = list(
        PropLine.objects.filter(game=game, is_closing=is_closing)
        .select_related("player", "market", "bookmaker")
    )
    if not lines:
        return 0

    # group all quotes per (player, market) so one CDF fit serves every line
    from collections import defaultdict

    by_pm: dict[tuple, list] = defaultdict(list)
    targets: dict[tuple, set] = defaultdict(set)
    for pl in lines:
        key = (pl.player_id, pl.market_id)
        # adapt the ORM row to the pure-quote duck type
        by_pm[key].append(
            _Quote(pl.bookmaker.name, float(pl.line),
                   _f(pl.over_price), _f(pl.under_price), pl.bookmaker.is_dfs)
        )
        targets[key].add((float(pl.line), pl.market.key))

    written = 0
    for (player_id, market_id), quotes in by_pm.items():
        for target_line, market_key in targets[(player_id, market_id)]:
            res = build_consensus_at(quotes, market_key, target_line)
            if res.p_over is None:
                continue
            _, created = PropConsensus.objects.update_or_create(
                game=game, player_id=player_id, market_id=market_id, line=target_line,
                anchor=PropConsensus.ANCHOR_CONSENSUS, excluded_book="", is_closing=is_closing,
                captured_at=at,
                defaults={
                    "fair_prob_over": round(res.p_over, 5),
                    "method": "shin",
                    "n_books": res.n_books,
                    "method_spread": round(res.method_spread, 5),
                },
            )
            written += 1 if created else 0
    return written


@dataclass(frozen=True, slots=True)
class _Quote:
    book: str
    line: float
    over_price: float | None
    under_price: float | None
    is_dfs: bool


def _f(v):
    return float(v) if v is not None else None
