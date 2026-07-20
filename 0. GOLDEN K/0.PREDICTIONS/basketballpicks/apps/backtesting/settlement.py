"""SETTLEMENT service — box score -> EdgePick grading [bball-05 §3].

Reads FINAL games' PlayerBoxScore (and team scores) and writes the terminal
status of every published EdgePick, applying the pre-committed VOID policy of
bball-05 §3d:

  * DNP / inactive / minutes==0                 -> VOID (universal book rule)
  * two-way / 10-day player + UNDER side         -> VOID (Porter rule)
  * exact line hit                               -> PUSH
  * game POSTPONED past the grace window         -> VOID
  * OT                                           -> INCLUDED (full-game box)
  * stat corrections                             -> settle on first FINAL, then a
                                                    48h re-grade pass; flips logged.

Idempotent + row-locked (select_for_update per pick, the safepicks `_claim_open`
discipline) so a re-grade never double-counts. A pick already terminal and
settled MORE than the re-grade window ago is frozen and skipped. The pure
stat-vs-line kernel is backtesting.engine; this module owns only the ORM + the
VOID policy that needs the ORM row.

edge/portfolio own the EdgePick/Bet/DFSEntry MODELS; this service only advances
`status`/`settled_at`/`audit` on already-published rows — it defines nothing.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.backtesting import engine
from apps.core.models import Game, PlayerBoxScore, Player

logger = logging.getLogger(__name__)

REGRADE_WINDOW_H = 48  # nba_api box scores revise for ~24-48h (bball-05 §3d)
POSTPONED_GRACE_H = 6  # a PPD game past this -> VOID its picks

_TWO_WAY_STATUSES = (Player.STATUS_TWO_WAY, Player.STATUS_TEN_DAY)

# grade outcome -> EdgePick status literal (bball-01 EdgePick.status vocabulary)
_OUTCOME_STATUS = {
    engine.WIN: "WON",
    engine.LOSE: "LOST",
    engine.PUSH: "PUSH",
    engine.VOID: "VOID",
}
_TERMINAL = set(_OUTCOME_STATUS.values())


# ---------------------------------------------------------------------------
# per-pick grading (VOID policy -> pure kernel)
# ---------------------------------------------------------------------------


def _grade_prop_pick(pick, now, grace_h) -> str | None:
    """VOID policy for a player-prop pick, falling through to engine.grade_prop.
    Returns a grade outcome (WIN/LOSE/PUSH/VOID) or None if not gradable yet."""
    line = pick.prop_line
    game = line.game
    if game.status == Game.STATUS_POSTPONED and now - game.tipoff_utc > timedelta(hours=grace_h):
        return engine.VOID
    if game.status != Game.STATUS_FINAL:
        return None
    player = line.player
    # Porter rule: never grade an UNDER the book would have voided on a
    # two-way / 10-day player (bball-05 §3d).
    if pick.side == engine.UNDER and getattr(player, "status", "") in _TWO_WAY_STATUSES:
        return engine.VOID
    box = (
        PlayerBoxScore.objects.filter(game=game, player=player)
        .only("dnp", "minutes", "pts", "reb", "ast", "stl", "blk", "tov", "tpm", "fgm", "ftm")
        .first()
    )
    if box is None or box.dnp or float(box.minutes) == 0.0:
        return engine.VOID  # DNP / inactive / 0 minutes
    market_key = line.market.key
    return engine.grade_prop(market_key, pick.side, box, pick.line if pick.line is not None else line.line)


def _grade_team_pick(pick, now, grace_h) -> str | None:
    """VOID policy + grade for a team-market pick (odds_snapshot-backed)."""
    snap = pick.odds_snapshot
    game = snap.game
    if game.status == Game.STATUS_POSTPONED and now - game.tipoff_utc > timedelta(hours=grace_h):
        return engine.VOID
    if game.status != Game.STATUS_FINAL or game.home_score is None or game.away_score is None:
        return None
    return engine.grade_team(snap.market, pick.side, game.home_score, game.away_score, pick.line)


def grade_pick(pick, *, now=None, grace_h=POSTPONED_GRACE_H) -> str | None:
    """Grade one EdgePick to an engine outcome, or None if not settleable yet.
    Pure read (no writes) so it is reusable by portfolio Bet/DFSEntry settling."""
    now = now or timezone.now()
    if pick.prop_line_id:
        return _grade_prop_pick(pick, now, grace_h)
    if pick.odds_snapshot_id:
        return _grade_team_pick(pick, now, grace_h)
    return None


# ---------------------------------------------------------------------------
# idempotent, row-locked settle pass
# ---------------------------------------------------------------------------


def _settle_one(pick_id: int, now, grace_h, regrade_window_h, stats) -> None:
    with transaction.atomic():
        pick = (
            _edge_pick_model()
            .objects.select_for_update()
            .select_related("prop_line__game", "prop_line__player", "prop_line__market", "odds_snapshot__game")
            .get(pk=pick_id)
        )
        # a terminal pick settled longer ago than the re-grade window is frozen.
        if (
            pick.status in _TERMINAL
            and pick.settled_at is not None
            and now - pick.settled_at > timedelta(hours=regrade_window_h)
        ):
            stats["frozen"] += 1
            return
        outcome = grade_pick(pick, now=now, grace_h=grace_h)
        if outcome is None:
            stats["not_ready"] += 1
            return
        new_status = _OUTCOME_STATUS[outcome]
        trail = {"graded_at": now.isoformat(), "outcome": outcome, "status": new_status}
        if pick.status == "OPEN":
            pick.status = new_status
            pick.settled_at = now
            _merge_audit(pick, {"settlement": trail})
            pick.save(update_fields=["status", "settled_at", "audit"])
            stats["settled"] += 1
        elif pick.status == new_status:
            stats["unchanged"] += 1  # idempotent no-op
        else:
            # stat-correction re-grade flip inside the window (bball-05 §3d).
            old = pick.status
            pick.status = new_status
            pick.settled_at = now
            _merge_audit(pick, {"settlement": trail, "regrade_flip": {"from": old, "to": new_status}})
            pick.save(update_fields=["status", "settled_at", "audit"])
            stats["flipped"] += 1
            logger.warning("settle: pick %s re-graded %s -> %s", pick_id, old, new_status)


def settle_edge_picks(
    *, now=None, grace_h=POSTPONED_GRACE_H, regrade_window_h=REGRADE_WINDOW_H
) -> dict:
    """Grade every settleable EdgePick: OPEN picks plus terminal picks still
    inside the 48h stat-correction re-grade window. Row-locked + idempotent."""
    now = now or timezone.now()
    EdgePick = _edge_pick_model()
    cutoff = now - timedelta(hours=regrade_window_h)
    candidate_ids = list(
        EdgePick.objects.filter(
            Q(status="OPEN") | Q(status__in=_TERMINAL, settled_at__gte=cutoff)
        ).values_list("id", flat=True)
    )
    stats = {
        "candidates": len(candidate_ids),
        "settled": 0,
        "flipped": 0,
        "unchanged": 0,
        "frozen": 0,
        "not_ready": 0,
    }
    for pick_id in candidate_ids:
        _settle_one(pick_id, now, grace_h, regrade_window_h, stats)
    return stats


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _edge_pick_model():
    """Lazy import so this module loads even while apps.edge is mid-build
    (parallel scaffold) — the model is resolved only when a settle actually
    runs, post-integration."""
    from apps.edge.models import EdgePick

    return EdgePick


def _merge_audit(pick, extra: dict) -> None:
    audit = dict(pick.audit or {})
    audit.update(extra)
    pick.audit = audit
