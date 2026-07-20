"""FORWARD-CLV VALIDATION GATE — the honesty discipline soccer lacked
[bball-05 §4]. The safepicks paper_clv.py analog, re-keyed to player props.

PURPOSE. For EVERY soft/DFS selection we would FLAG as +EV (a line the
sharp/consensus fair prob at OPEN says is underpriced), record it at flag-time
and, at that game's lock (tipoff), measure whether the market moved TOWARD us.
Forward-only by construction: empty report today, real numbers as open->closing
prop pairs accrue. Pure READ-SIDE — no ORM writes anywhere in this module.

THREE CLV MEASURES per flagged pick (bball-05 §4b), #3 is the verdict metric:
  (1) same-book PRICE CLV  = O_open / O_close (same book, same line) - 1
      Positive = the book itself shortened your side. Soft books only; None when
      the book moved its line (no same-line close) or for price-less DFS.
  (2) LINE-MOVE CLV        = signed points the line drifted TOWARD your pick
      = (close_line - open_line) for OVER, (open_line - close_line) for UNDER.
      The honest measure for DFS (price is fixed; only the NUMBER moves).
  (3) SHARP-BEAT CLV       = p_fair_sharp_CLOSE * O_taken - 1   *** the gate ***
      EV of the price you took measured against the SHARP's OWN closing fair
      prob (the best available estimate of truth). Soft: O_taken = your soft
      price. DFS: O_taken = the published payout multiplier (a REAL price, never
      fabricated); a price-less DFS leg contributes to line-move only.

Realized ROI-at-flag is carried too (settle via engine.grade_prop, P&L at the
taken price) but CLV, not ROI, is the primary signal at these sample sizes.

FLAG universe (bball-05 §4a) — the sharp-anchor set, market list, leagues and
FLAG_EDGE_MIN are FROZEN CONSTANTS committed BEFORE data collection (the
pre-registration). Soft path flags on edge = O_open_soft * p_fair_open - 1;
DFS path flags on the line-disagreement p_fair_open - BREAKEVEN_DFS.

Every cell (venue x market x league) starts DISABLED. This gate produces a
CONFIRM/KILL/HOLD RECOMMENDATION only — it writes nothing live. Moving a
threshold requires a dated ADR (§4d); the constants below are not tuned to
incoming data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta

from apps.backtesting import engine
from apps.core.models import Game, Player, PlayerBoxScore

# props.PropLine / props.PropConsensus are imported LAZILY inside _scan_game so
# the pure flag/measure/verdict logic (and its tests) load without a hard
# dependency on apps.props during the parallel build.

EPS = 1e-9

# ===========================================================================
# PRE-REGISTERED CONSTANTS — FROZEN. Move only via a dated ADR (never to
# rescue a dying cell). This is the whole point (bball-05 §7).
# ===========================================================================

# --- the flag universe (§4a) ---
FLAG_EDGE_MIN = 0.03  # min soft EV / DFS line-implied edge to enter the universe
FLAG_LEAGUES = ("NBA", "WNBA", "NCAAB", "EURO")
FLAG_MARKETS = (
    "points",
    "rebounds",
    "assists",
    "pra",
    "pr",
    "pa",
    "ra",
    "threes",
    "blocks",
    "steals",
    "turnovers",
)
# sharp/consensus anchor preference for p_fair (§2d): a true sharp first, the
# soft-consensus pseudo-book last. Coverage is split per anchor so a
# Pinnacle-collapse reads as COVERAGE, not efficiency.
ANCHOR_PREFERENCE = ("pinnacle", "circa", "consensus")
BREAKEVEN_DFS = 0.5  # a price-less pick'em leg's fair breakeven = pure coin flip

# --- CONFIRM / KILL thresholds (§4d), per (venue, market, league) CELL ---
CONFIRM_MIN_N = 500  # flagged picks with a sharp-beat measure
CONFIRM_MIN_SHARP_BEAT = 0.020  # mean sharp-beat CLV >= +2.0%
CONFIRM_MIN_WEEKS = 8  # sustained across >= 8 distinct tipoff weeks
CONFIRM_ROI_CI_FLOOR = -0.005  # realized-ROI CI lower bound > -0.5%
KILL_MIN_N = 300
KILL_SHARP_BEAT_CI_UPPER = 0.010  # CLV<=0 with CI upper bound < +1.0%
BOOTSTRAP_ITER = 2000
BOOTSTRAP_SEED = 20260719

VERDICT_CONFIRM = "CONFIRM"
VERDICT_KILL = "KILL"
VERDICT_HOLD = "HOLD"


# ===========================================================================
# flagged-pick model
# ===========================================================================


@dataclass
class FlaggedPick:
    game_id: int
    league: str
    venue: str  # SOFTBOOK | DFS
    book: str
    market: str  # props.PropMarket.key
    player_id: int
    side: str  # OVER | UNDER
    tipoff_date: date
    open_line: float
    close_line: float
    anchor_open: str | None
    anchor_close: str | None
    o_taken: float | None  # soft price OR DFS payout multiplier (real prices only)
    p_fair_open: float
    p_fair_close: float | None
    flag_edge: float  # the +EV quantity that put it in the universe
    price_clv: float | None  # (1) same-book price CLV
    line_move_clv: float  # (2) signed line drift toward the pick, in points
    sharp_beat_clv: float | None  # (3) *** the verdict metric ***
    dfs_line_edge: float | None  # DFS: p_fair - 0.5 (line-space report)
    settled: bool = False
    outcome: str | None = None
    pnl: float | None = None  # realized P&L per unit at the taken price

    @property
    def cell(self) -> str:
        return f"{self.venue}:{self.market}:{self.league}"


# ===========================================================================
# sharp/consensus fair ladders (line-normalization — the #1 correctness hazard)
# ===========================================================================


def _anchor_rank(anchor: str):
    try:
        return ANCHOR_PREFERENCE.index(anchor)
    except ValueError:
        return None


def _fair_ladder(rows, is_closing: bool) -> dict[float, tuple[float, str]]:
    """line -> (fair_prob_over, anchor) from PropConsensus rows for one
    (game, player, market). Per line keep the best-ranked anchor; tie-break by
    capture time (earliest for open, latest for close)."""
    best: dict[float, tuple] = {}
    for r in rows:
        if r.is_closing != is_closing:
            continue
        rank = _anchor_rank(r.anchor)
        if rank is None:
            continue
        line = float(r.line)
        cur = best.get(line)
        newer = (not is_closing and r.captured_at < cur[1]) or (
            is_closing and r.captured_at > cur[1]
        ) if cur is not None else False
        if cur is None or rank < cur[0] or (rank == cur[0] and newer):
            best[line] = (rank, r.captured_at, float(r.fair_prob_over), r.anchor)
    return {line: (v[2], v[3]) for line, v in best.items()}


def _fair_at_line(ladder: dict[float, tuple[float, str]], target: float, side: str):
    """Fair prob for `side` at `target` line, interpolated across the anchor's
    O/U ladder (bball-05 §2d) — NEVER compare probs at different lines. Returns
    (p_fair, anchor) or (None, None) when the line cannot be bracketed."""
    if not ladder:
        return None, None
    if target in ladder:
        fair_over, anchor = ladder[target]
    else:
        lines = sorted(ladder)
        below = [ln for ln in lines if ln < target]
        above = [ln for ln in lines if ln > target]
        if not below or not above:
            return None, None  # honest skip: no fabricated extrapolation
        lo, hi = below[-1], above[0]
        fo_lo, an_lo = ladder[lo]
        fo_hi, an_hi = ladder[hi]
        w = (target - lo) / (hi - lo)
        fair_over = fo_lo + w * (fo_hi - fo_lo)  # fair_over is monotone in line
        anchor = an_lo if w < 0.5 else an_hi
    p = fair_over if side == engine.OVER else 1.0 - fair_over
    return p, anchor


# ===========================================================================
# per (player, market, book) open/close prop pairs
# ===========================================================================


@dataclass
class _BookPair:
    book: str
    is_dfs: bool
    open_line: float
    close_line: float
    open_over: float | None
    open_under: float | None
    close_over: float | None
    close_under: float | None
    payout_mult: float | None


def _book_pairs(lines) -> list[_BookPair]:
    """For a (game, player, market) slice of PropLine rows, the earliest-open
    and closing quote per non-sharp, non-aggregate book (the pick is TAKEN at a
    soft/DFS price; sharp books are anchor-only, aggregates excluded)."""
    per_book: dict[str, dict] = {}
    for row in lines:
        book = row.bookmaker
        if book.is_sharp or book.is_aggregate:
            continue
        slot = per_book.setdefault(book.name, {"is_dfs": book.is_dfs, "open": None, "close": None})
        if row.is_closing:
            cur = slot["close"]
            if cur is None or row.captured_at > cur.captured_at:
                slot["close"] = row
        else:
            cur = slot["open"]
            if cur is None or row.captured_at < cur.captured_at:
                slot["open"] = row
    pairs = []
    for name, slot in per_book.items():
        o, c = slot["open"], slot["close"]
        if o is None or c is None:
            continue  # need BOTH an open datum and a closing benchmark
        pairs.append(
            _BookPair(
                book=name,
                is_dfs=slot["is_dfs"],
                open_line=float(o.line),
                close_line=float(c.line),
                open_over=_f(o.over_price),
                open_under=_f(o.under_price),
                close_over=_f(c.over_price),
                close_under=_f(c.under_price),
                payout_mult=_f(o.payout_mult),
            )
        )
    return pairs


def _f(value):
    return None if value is None else float(value)


# ===========================================================================
# flag + measure one side
# ===========================================================================


def _side_price(pair: _BookPair, side: str, closing: bool):
    over = pair.close_over if closing else pair.open_over
    under = pair.close_under if closing else pair.open_under
    return over if side == engine.OVER else under


def _measure_side(
    pair: _BookPair, side: str, open_ladder, close_ladder, league, market, game, box_getter
) -> FlaggedPick | None:
    p_fair_open, anchor_open = _fair_at_line(open_ladder, pair.open_line, side)
    if p_fair_open is None:
        return None

    o_open = _side_price(pair, side, closing=False)
    # --- flag test (§4a) ---
    if pair.is_dfs:
        flag_edge = p_fair_open - BREAKEVEN_DFS
        o_taken = pair.payout_mult  # real price only; never fabricated
    else:
        if o_open is None:
            return None
        flag_edge = o_open * p_fair_open - 1.0
        o_taken = o_open
    if flag_edge < FLAG_EDGE_MIN - EPS:
        return None  # not in the pre-registered +EV universe

    # --- three CLV flavors (§4b) ---
    p_fair_close, anchor_close = _fair_at_line(close_ladder, pair.open_line, side)

    price_clv = None
    if not pair.is_dfs and abs(pair.close_line - pair.open_line) < EPS:
        o_close = _side_price(pair, side, closing=True)
        if o_open and o_close and o_close > 1.0:
            price_clv = o_open / o_close - 1.0

    if side == engine.OVER:
        line_move_clv = pair.close_line - pair.open_line
    else:
        line_move_clv = pair.open_line - pair.close_line

    sharp_beat_clv = None
    if p_fair_close is not None and o_taken is not None:
        sharp_beat_clv = p_fair_close * o_taken - 1.0

    dfs_line_edge = (p_fair_open - 0.5) if pair.is_dfs else None

    pick = FlaggedPick(
        game_id=game.id,
        league=league,
        venue="DFS" if pair.is_dfs else "SOFTBOOK",
        book=pair.book,
        market=market,
        player_id=None,  # filled by caller (it holds the player id)
        side=side,
        tipoff_date=game.tipoff_utc.date(),
        open_line=pair.open_line,
        close_line=pair.close_line,
        anchor_open=anchor_open,
        anchor_close=anchor_close,
        o_taken=None if o_taken is None else round(o_taken, 4),
        p_fair_open=round(p_fair_open, 5),
        p_fair_close=None if p_fair_close is None else round(p_fair_close, 5),
        flag_edge=round(flag_edge, 5),
        price_clv=None if price_clv is None else round(price_clv, 5),
        line_move_clv=round(line_move_clv, 3),
        sharp_beat_clv=None if sharp_beat_clv is None else round(sharp_beat_clv, 5),
        dfs_line_edge=None if dfs_line_edge is None else round(dfs_line_edge, 5),
    )

    # --- realized ROI at flag (settle if the game is final) ---
    box = box_getter()
    if box is not None:
        outcome = _settle_flag(pick, market, side, box)
        if outcome is not None:
            pick.settled = True
            pick.outcome = outcome
            if o_taken is not None:
                pick.pnl = round(engine.pnl_per_unit(outcome, o_taken), 5)
    return pick


def _settle_flag(pick, market, side, box) -> str | None:
    """VOID policy (bball-05 §3d) then engine.grade_prop. VOIDs count in the
    harness (the biggest CLV signal is a vanished line) but never inflate ROI."""
    player_status = getattr(box, "_player_status", "")
    if side == engine.UNDER and player_status in (Player.STATUS_TWO_WAY, Player.STATUS_TEN_DAY):
        return engine.VOID
    if box.dnp or float(box.minutes) == 0.0:
        return engine.VOID
    return engine.grade_prop(market, side, box, pick.open_line)


# ===========================================================================
# aggregation + significance (seeded bootstrap CIs, §4c) + verdict (§4d)
# ===========================================================================


def _bootstrap_ci(values, n_iter=BOOTSTRAP_ITER, seed=BOOTSTRAP_SEED):
    """Seeded percentile bootstrap 95% CI on the mean. i.i.d. resample — one
    game contributes many correlated legs (a star's PTS/PRA/threes move
    together) so the CI is modestly too narrow; noted, not hidden (a game-block
    bootstrap is the honest upgrade, bball-05 §4c)."""
    import numpy as np

    arr = np.asarray([v for v in values if v is not None], dtype=float)
    n = len(arr)
    if n == 0:
        return None, None
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_iter, n))
    means = arr[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def _mean(values):
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 5) if vals else None


def _share_positive(values):
    vals = [v for v in values if v is not None]
    return round(sum(1 for v in vals if v > 0) / len(vals), 4) if vals else None


def _summarize(picks: list[FlaggedPick]) -> dict:
    n = len(picks)
    sharp = [p.sharp_beat_clv for p in picks if p.sharp_beat_clv is not None]
    sb_lo, sb_hi = _bootstrap_ci(sharp)
    settled = [p for p in picks if p.pnl is not None]
    pnls = [p.pnl for p in settled]
    roi_lo, roi_hi = _bootstrap_ci(pnls)
    weeks = len({(p.tipoff_date.isocalendar().year, p.tipoff_date.isocalendar().week) for p in picks})
    return {
        "n": n,
        "n_sharp_beat": len(sharp),
        "price_clv_mean": _mean([p.price_clv for p in picks]),
        "line_move_mean": _mean([p.line_move_clv for p in picks]),
        "sharp_beat_mean": _mean(sharp),
        "sharp_beat_ci_lo": None if sb_lo is None else round(sb_lo, 5),
        "sharp_beat_ci_hi": None if sb_hi is None else round(sb_hi, 5),
        "sharp_beat_share_pos": _share_positive(sharp),
        "line_move_share_pos": _share_positive([p.line_move_clv for p in picks]),
        "dfs_line_edge_mean": _mean([p.dfs_line_edge for p in picks]),
        "weeks": weeks,
        "n_settled": len(settled),
        "roi_mean": _mean(pnls),
        "roi_ci_lo": None if roi_lo is None else round(roi_lo, 5),
        "roi_ci_hi": None if roi_hi is None else round(roi_hi, 5),
    }


def _verdict(summary: dict) -> str:
    """Frozen pre-registered decision (§4d). HOLD until a threshold fires; all
    cells start DISABLED so CONFIRM is a recommendation, never an auto-enable."""
    sb_mean = summary["sharp_beat_mean"]
    sb_lo = summary["sharp_beat_ci_lo"]
    sb_hi = summary["sharp_beat_ci_hi"]
    roi_lo = summary["roi_ci_lo"]
    roi_hi = summary["roi_ci_hi"]
    n_sb = summary["n_sharp_beat"]

    # KILL: enough evidence AND (sharp-beat non-positive with a tight upper CI,
    # OR realized ROI CI wholly negative).
    if n_sb >= KILL_MIN_N and sb_mean is not None and sb_mean <= 0.0:
        if sb_hi is not None and sb_hi < KILL_SHARP_BEAT_CI_UPPER:
            return VERDICT_KILL
    if summary["n_settled"] >= KILL_MIN_N and roi_hi is not None and roi_hi < 0.0:
        return VERDICT_KILL

    # CONFIRM: every clause must hold on settled/measured flagged picks.
    if (
        n_sb >= CONFIRM_MIN_N
        and sb_mean is not None
        and sb_mean >= CONFIRM_MIN_SHARP_BEAT
        and sb_lo is not None
        and sb_lo > 0.0
        and summary["weeks"] >= CONFIRM_MIN_WEEKS
        and roi_lo is not None
        and roi_lo > CONFIRM_ROI_CI_FLOOR
    ):
        return VERDICT_CONFIRM
    return VERDICT_HOLD


def _grouped(picks: list[FlaggedPick], key_fn, with_verdict: bool) -> dict:
    buckets: dict[str, list[FlaggedPick]] = {}
    for p in picks:
        buckets.setdefault(key_fn(p), []).append(p)
    out = {}
    for key, rows in sorted(buckets.items()):
        summ = _summarize(rows)
        if with_verdict:
            summ["verdict"] = _verdict(summ)
        out[key] = summ
    return out


# ===========================================================================
# public entry point
# ===========================================================================


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def compute_prop_clv(date_from, date_to) -> dict:
    """Forward-CLV read over games tipping in [date_from, date_to] (inclusive)
    that carry BOTH an open and a closing prop capture AND a sharp/consensus
    fair. Returns overall + by_market + by_book + by_league + by_venue +
    by_anchor cells, each with the three CLV means, seeded bootstrap CIs on the
    sharp-beat metric, realized ROI, week count, and a per-cell CONFIRM/KILL/HOLD
    verdict. The empty case (0 pairs) returns a clean zero report — the correct
    output today (forward-only)."""
    d_from, d_to = _as_date(date_from), _as_date(date_to)
    games = list(
        Game.objects.filter(tipoff_utc__date__gte=d_from, tipoff_utc__date__lte=d_to)
        .select_related("season__league")
    )

    picks: list[FlaggedPick] = []
    n_games_with_pairs = 0
    for game in games:
        league = game.season.league.code
        if league not in FLAG_LEAGUES:
            continue
        game_had_pair = _scan_game(game, league, picks)
        if game_had_pair:
            n_games_with_pairs += 1

    overall = _summarize(picks)
    overall["verdict"] = _verdict(overall)
    return {
        "window": {"from": d_from.isoformat(), "to": d_to.isoformat()},
        "n_games_scanned": len(games),
        "n_games_with_pairs": n_games_with_pairs,
        "n_flagged": len(picks),
        "thresholds": {
            "flag_edge_min": FLAG_EDGE_MIN,
            "flag_markets": list(FLAG_MARKETS),
            "flag_leagues": list(FLAG_LEAGUES),
            "anchor_preference": list(ANCHOR_PREFERENCE),
            "confirm_min_n": CONFIRM_MIN_N,
            "confirm_min_sharp_beat": CONFIRM_MIN_SHARP_BEAT,
            "confirm_min_weeks": CONFIRM_MIN_WEEKS,
            "confirm_roi_ci_floor": CONFIRM_ROI_CI_FLOOR,
            "kill_min_n": KILL_MIN_N,
            "kill_sharp_beat_ci_upper": KILL_SHARP_BEAT_CI_UPPER,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "all_cells_start_disabled": True,
        },
        "overall": overall,
        "by_cell": _grouped(picks, lambda p: p.cell, with_verdict=True),
        "by_market": _grouped(picks, lambda p: p.market, with_verdict=True),
        "by_book": _grouped(picks, lambda p: p.book, with_verdict=False),
        "by_league": _grouped(picks, lambda p: p.league, with_verdict=True),
        "by_venue": _grouped(picks, lambda p: p.venue, with_verdict=True),
        "by_anchor": _grouped(picks, lambda p: p.anchor_open or "none", with_verdict=False),
        "picks": [_pick_dict(p) for p in picks],
    }


def _scan_game(game: Game, league: str, picks: list[FlaggedPick]) -> bool:
    """Flag + measure every side of every (player, market, book) open->close
    pair for one game. Returns whether the game had at least one measurable
    pair (independent of the flag screen)."""
    from apps.props.models import PropConsensus, PropLine  # lazy (parallel build)

    prop_lines = list(
        PropLine.objects.filter(game=game).select_related("bookmaker", "market", "player")
    )
    if not prop_lines:
        return False
    consensus = list(PropConsensus.objects.filter(game=game).select_related("market"))

    # group PropLines + consensus by (player_id, market_key)
    lines_by: dict[tuple, list] = {}
    for row in prop_lines:
        lines_by.setdefault((row.player_id, row.market.key), []).append(row)
    cons_by: dict[tuple, list] = {}
    for row in consensus:
        cons_by.setdefault((row.player_id, row.market.key), []).append(row)

    # settled box scores for this game (final games only), cached per player
    box_cache: dict[int, object] = {}
    is_final = game.status == Game.STATUS_FINAL

    def _box_getter_for(player_id):
        def _get():
            if not is_final:
                return None
            if player_id not in box_cache:
                box = (
                    PlayerBoxScore.objects.filter(game=game, player_id=player_id)
                    .select_related("player")
                    .first()
                )
                if box is not None:
                    box._player_status = getattr(box.player, "status", "")
                box_cache[player_id] = box
            return box_cache[player_id]

        return _get

    had_pair = False
    for (player_id, market_key), lines in lines_by.items():
        if market_key not in FLAG_MARKETS:
            continue
        pairs = _book_pairs(lines)
        if pairs:
            had_pair = True
        cons_rows = cons_by.get((player_id, market_key), [])
        open_ladder = _fair_ladder(cons_rows, is_closing=False)
        close_ladder = _fair_ladder(cons_rows, is_closing=True)
        if not open_ladder:
            continue  # no OPEN fair -> cannot flag honestly
        box_getter = _box_getter_for(player_id)
        for pair in pairs:
            for side in (engine.OVER, engine.UNDER):
                pick = _measure_side(
                    pair, side, open_ladder, close_ladder, league, market_key, game, box_getter
                )
                if pick is not None:
                    pick.player_id = player_id
                    picks.append(pick)
    return had_pair


def _pick_dict(p: FlaggedPick) -> dict:
    d = asdict(p)
    d["tipoff_date"] = p.tipoff_date.isoformat()
    d["cell"] = p.cell
    return d
