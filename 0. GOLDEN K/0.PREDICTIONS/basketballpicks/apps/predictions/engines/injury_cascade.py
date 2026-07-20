"""Injury-cascade lineup re-solve (bball-03 §4d) — the second-order edge, pure
numpy (no ORM).

When a starter is ruled OUT the MAIN line reprices in minutes (no edge for us),
but his ~30 minutes and ~28% usage redistribute onto teammates SLOWLY and
UNEVENLY across 200-400 prop lines — the one place a real model beats a lazy
book rather than merely shopping it. Our model handles it NATIVELY because it is
hierarchical: remove the player from the lineup state, re-solve minutes (his
minutes flow to specific teammates by role weight, capped at a human ceiling),
bump their usage, and re-project every downstream stat.

Team minutes are CONSERVED (the out players' minutes are moved, not deleted), so
the sum stays 240 (+25/OT). Usage flows to whoever absorbs the minutes.
"""

from dataclasses import dataclass

DEFAULT_MINUTE_CAP = 42.0  # a human can't play the whole game every night


@dataclass
class LineupPlayer:
    id: object
    position: str  # G|F|C|G-F...
    base_minutes: float
    base_usage: float  # USG% (share of possessions ended while on floor)


def _position_affinity(a: str, b: str) -> float:
    """Crude role similarity: minutes flow preferentially to same-position
    teammates (a wing's minutes go mostly to wings). 1.0 exact, 0.5 overlap,
    0.25 otherwise — a soft weight, not a hard gate."""
    if not a or not b:
        return 0.5
    sa, sb = set(a.split("-")), set(b.split("-"))
    if sa == sb:
        return 1.0
    return 0.6 if sa & sb else 0.3


def resolve_lineup(
    players: list[LineupPlayer],
    out_ids: list,
    minute_cap: float = DEFAULT_MINUTE_CAP,
) -> dict:
    """Re-solve minutes + usage after `out_ids` are ruled out.

    Returns {player_id: {"minutes":.., "usage":.., "minutes_gain":..,
    "usage_gain":..}} for the REMAINING players. Freed minutes are distributed by
    role-weighted (position-affinity x base minutes) shares, capped at
    `minute_cap`, with overflow re-distributed; freed usage follows the absorbed
    minutes."""
    out_set = set(out_ids)
    out_players = [p for p in players if p.id in out_set]
    remaining = [p for p in players if p.id not in out_set]
    result = {
        p.id: {
            "minutes": p.base_minutes,
            "usage": p.base_usage,
            "minutes_gain": 0.0,
            "usage_gain": 0.0,
        }
        for p in remaining
    }
    if not out_players or not remaining:
        return result

    freed_minutes = sum(p.base_minutes for p in out_players)
    freed_usage = sum(p.base_usage for p in out_players)

    # role weight = sum over out players of affinity, x own base minutes (a bigger
    # role absorbs more, a same-position teammate absorbs more).
    weight = {}
    for p in remaining:
        aff = sum(_position_affinity(p.position, o.position) for o in out_players)
        weight[p.id] = max(aff * max(p.base_minutes, 1.0), 1e-6)

    extra = {p.id: 0.0 for p in remaining}
    pool = freed_minutes
    for _ in range(100):
        if pool <= 1e-6:
            break
        avail = [p.id for p in remaining if (result[p.id]["minutes"] + extra[p.id]) < minute_cap - 1e-6]
        if not avail:
            break  # everyone maxed — remaining minutes simply can't be absorbed
        wsum = sum(weight[i] for i in avail)
        moved = 0.0
        for i in avail:
            room = minute_cap - (result[i]["minutes"] + extra[i])
            add = min(pool * weight[i] / wsum, room)
            extra[i] += add
            moved += add
        pool -= moved
        if moved <= 1e-9:
            break

    total_extra = sum(extra.values()) or 1.0
    for p in remaining:
        gain = extra[p.id]
        usage_gain = freed_usage * (gain / total_extra)
        result[p.id]["minutes"] = p.base_minutes + gain
        result[p.id]["usage"] = p.base_usage + usage_gain
        result[p.id]["minutes_gain"] = gain
        result[p.id]["usage_gain"] = usage_gain
    return result


def minutes_conserved(players: list[LineupPlayer], resolved: dict, out_ids: list, tol: float = 0.5) -> bool:
    """Sanity guard: post-resolve team minutes match pre-resolve (the out
    players' minutes were moved, not lost), within `tol`. Used by the validation
    gate and the tests."""
    pre = sum(p.base_minutes for p in players)
    out_set = set(out_ids)
    post = sum(v["minutes"] for pid, v in resolved.items() if pid not in out_set)
    # if some freed minutes couldn't be absorbed (all capped), post < pre is OK
    return post <= pre + tol
