"""ESPN keyless basketball API — the wehoop (WNBA) + hoopR (NCAA Men's D1)
turnkey PLAYER-box + schedule source [bball-02 S2].

wehoop / hoopR are thin wrappers over ESPN's undocumented ``site.api.espn.com``
basketball feed; harvesting it directly reuses the BudgetedClient budget/cache
and needs no R/py runtime. One shared PURE parser serves every basketball slug
(WNBA + men's/women's college); the per-league services just pass a different
slug + core League code.

Endpoints (base = .../sports/basketball):
  * ``{slug}/scoreboard?dates=YYYYMMDD`` — the day's games
  * ``{slug}/summary?event={id}``        — TEAM + PLAYER box for one game

Player box stat columns (ESPN order): MIN FG 3PT FT OREB DREB REB AST STL BLK
TO PF +/- PTS — where FG/3PT/FT are 'made-attempted' strings ('8-15').
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from apps.ingestion.http import BudgetedClient, Priority

SOURCE = "espn_basketball"

# core League.code -> ESPN basketball slug.
LEAGUE_SLUGS = {
    "WNBA": "wnba",
    "NCAAB": "mens-college-basketball",
    "NCAAW": "womens-college-basketball",
    "NBA": "nba",
}

# regulation period COUNT per slug — NBA/WNBA/women's college play 4 quarters,
# men's college plays 2 halves. Anything past regulation is overtime, so
# num_ot = period - regulation. Default 4 (protects the props-priority WNBA).
REGULATION_PERIODS = {
    "wnba": 4,
    "nba": 4,
    "womens-college-basketball": 4,
    "mens-college-basketball": 2,
}


def _num_ot(slug: str, period: int) -> int:
    reg = REGULATION_PERIODS.get((slug or "").lower(), 4)
    return max(0, period - reg) if period and period > reg else 0

# ESPN status.type.name -> core.Game status (unlisted names fall back to state).
STATUS_MAP = {
    "STATUS_SCHEDULED": "SCHEDULED",
    "STATUS_PRE": "SCHEDULED",
    "STATUS_TBD": "SCHEDULED",
    "STATUS_DELAYED": "SCHEDULED",
    "STATUS_IN_PROGRESS": "LIVE",
    "STATUS_FIRST_HALF": "LIVE",
    "STATUS_SECOND_HALF": "LIVE",
    "STATUS_HALFTIME": "LIVE",
    "STATUS_END_PERIOD": "LIVE",
    "STATUS_END_OF_PERIOD": "LIVE",
    "STATUS_OVERTIME": "LIVE",
    "STATUS_FINAL": "FINAL",
    "STATUS_FINAL_OT": "FINAL",
    "STATUS_POSTPONED": "PP",
    "STATUS_CANCELED": "PP",
    "STATUS_CANCELLED": "PP",
    "STATUS_SUSPENDED": "PP",
    "STATUS_FORFEIT": "PP",
}
_STATE_FALLBACK = {"pre": "SCHEDULED", "in": "LIVE"}

TTL_SCOREBOARD_S = 900.0
TTL_SUMMARY_FINAL_S = 7 * 24 * 3600.0

# player stat labels we key on (ESPN "names"/"keys" arrays)
_STAT_KEYS = ["MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "+/-", "PTS"]


@dataclass
class ParsedGame:
    event_id: str
    slug: str
    status: str
    status_name: str
    tipoff_utc: datetime
    period: int
    num_ot: int
    home_team_id: str
    away_team_id: str
    home_abbr: str
    away_abbr: str
    home_name: str
    away_name: str
    home_score: int | None
    away_score: int | None
    venue: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class ParsedTeamBox:
    event_id: str
    team_id: str
    is_home: bool
    team_abbr: str
    team_name: str
    pts: int
    reb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    fgm: int
    fga: int
    tpm: int
    tpa: int
    ftm: int
    fta: int
    raw: dict = field(default_factory=dict)


@dataclass
class ParsedPlayerBox:
    event_id: str
    team_id: str
    player_id: str
    player_name: str
    position: str
    started: bool
    dnp: bool
    minutes: Decimal | None
    pts: int
    oreb: int
    dreb: int
    reb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    fgm: int
    fga: int
    tpm: int
    tpa: int
    ftm: int
    fta: int
    plus_minus: int | None
    raw: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def map_status(name: str, state: str = "", completed: bool = False) -> str:
    mapped = STATUS_MAP.get((name or "").upper())
    if mapped:
        return mapped
    st = (state or "").lower()
    if st in _STATE_FALLBACK:
        return _STATE_FALLBACK[st]
    if st == "post":
        return "FINAL" if completed else "PP"
    return "SCHEDULED"


def parse_kickoff(iso: str) -> datetime:
    s = (iso or "").strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(UTC)


def _int_or_none(v) -> int | None:
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _team_name(team: dict) -> str:
    return (
        team.get("displayName") or team.get("name") or team.get("shortDisplayName") or ""
    ).strip()


def parse_minutes(value) -> Decimal | None:
    """ESPN basketball MIN is a whole-minute string ('34'); 'MM:SS' handled too.
    A DNP row carries '0' / '' / None."""
    if value in (None, ""):
        return None
    s = str(value).strip()
    if s in ("", "--", "0"):
        return Decimal("0") if s == "0" else None
    if ":" in s:
        mm, _, ss = s.partition(":")
        try:
            return (Decimal(mm or "0") + Decimal(ss or "0") / Decimal(60)).quantize(Decimal("0.01"))
        except (ValueError, ArithmeticError):
            return None
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except (ValueError, ArithmeticError):
        return None


def _made_att(value) -> tuple[int, int]:
    """Split an ESPN 'made-attempted' cell ('8-15') into (made, attempted)."""
    if not value or value in ("--", "-"):
        return 0, 0
    made, _, att = str(value).partition("-")

    def _i(x: str) -> int:
        try:
            return int(x)
        except (TypeError, ValueError):
            return 0

    return _i(made), _i(att)


def _num(value) -> int:
    if value in (None, "", "--"):
        return 0
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# scoreboard parser
# ---------------------------------------------------------------------------


def _slug(payload: dict) -> str:
    leagues = payload.get("leagues") or []
    if leagues:
        return leagues[0].get("slug") or ""
    return ""


def parse_scoreboard(payload: dict) -> list[ParsedGame]:
    slug = _slug(payload)
    out: list[ParsedGame] = []
    for ev in payload.get("events") or []:
        comps = ev.get("competitions") or []
        if not comps:
            continue
        comp = comps[0]
        sides = {c.get("homeAway"): c for c in comp.get("competitors") or []}
        home, away = sides.get("home"), sides.get("away")
        if not home or not away:
            continue
        event_id = str(ev.get("id") or comp.get("id") or "")
        raw_date = ev.get("date") or comp.get("date")
        if not event_id or not raw_date:
            continue

        st = (comp.get("status") or ev.get("status") or {})
        st_type = st.get("type") or {}
        name = st_type.get("name") or ""
        state = st_type.get("state") or ""
        completed = bool(st_type.get("completed"))
        status = map_status(name, state, completed)
        period = _int_or_none(st.get("period")) or 0
        num_ot = _num_ot(slug, period)

        home_score = _int_or_none(home.get("score")) if completed else None
        away_score = _int_or_none(away.get("score")) if completed else None
        venue = ((comp.get("venue") or {}).get("fullName")) or ""

        out.append(
            ParsedGame(
                event_id=event_id,
                slug=slug,
                status=status,
                status_name=name,
                tipoff_utc=parse_kickoff(raw_date),
                period=period,
                num_ot=num_ot,
                home_team_id=str((home.get("team") or {}).get("id") or ""),
                away_team_id=str((away.get("team") or {}).get("id") or ""),
                home_abbr=(home.get("team") or {}).get("abbreviation") or "",
                away_abbr=(away.get("team") or {}).get("abbreviation") or "",
                home_name=_team_name(home.get("team") or {}),
                away_name=_team_name(away.get("team") or {}),
                home_score=home_score,
                away_score=away_score,
                venue=venue,
                raw=ev,
            )
        )
    return out


# ---------------------------------------------------------------------------
# summary (box) parser
# ---------------------------------------------------------------------------


def game_meta(summary: dict) -> ParsedGame | None:
    """A ParsedGame reconstructed from a summary payload's header, so a box
    harvest can upsert the Game even when the scoreboard pass did not run."""
    header = summary.get("header") or {}
    comps = header.get("competitions") or []
    if not comps:
        return None
    comp = comps[0]
    sides = {c.get("homeAway"): c for c in comp.get("competitors") or []}
    home, away = sides.get("home"), sides.get("away")
    if not home or not away:
        return None
    st_type = (comp.get("status") or {}).get("type") or {}
    completed = bool(st_type.get("completed"))
    period = _int_or_none((comp.get("status") or {}).get("period")) or 0
    slug = str((header.get("league") or {}).get("slug") or "")
    return ParsedGame(
        event_id=str(header.get("id") or comp.get("id") or ""),
        slug=slug,
        status=map_status(st_type.get("name") or "", st_type.get("state") or "", completed),
        status_name=st_type.get("name") or "",
        tipoff_utc=parse_kickoff(comp.get("date") or ""),
        period=period,
        num_ot=_num_ot(slug, period),
        home_team_id=str((home.get("team") or {}).get("id") or ""),
        away_team_id=str((away.get("team") or {}).get("id") or ""),
        home_abbr=(home.get("team") or {}).get("abbreviation") or "",
        away_abbr=(away.get("team") or {}).get("abbreviation") or "",
        home_name=_team_name(home.get("team") or {}),
        away_name=_team_name(away.get("team") or {}),
        home_score=_int_or_none(home.get("score")) if completed else None,
        away_score=_int_or_none(away.get("score")) if completed else None,
        raw=header,
    )


def _home_away_by_team_id(summary: dict) -> dict[str, bool]:
    """team_id -> is_home, read from the summary header competitors."""
    out: dict[str, bool] = {}
    header = summary.get("header") or {}
    for comp in header.get("competitions") or []:
        for c in comp.get("competitors") or []:
            tid = str((c.get("team") or {}).get("id") or "")
            if tid:
                out[tid] = c.get("homeAway") == "home"
    return out


def parse_boxscore(summary: dict) -> tuple[list[ParsedTeamBox], list[ParsedPlayerBox]]:
    """Parse TEAM + PLAYER box rows from a summary payload."""
    event_id = str((summary.get("header") or {}).get("id") or "")
    box = summary.get("boxscore") or {}
    home_away = _home_away_by_team_id(summary)

    team_rows = _parse_team_box(box, event_id, home_away)
    player_rows = _parse_player_box(box, event_id)
    return team_rows, player_rows


def _parse_team_box(box: dict, event_id: str, home_away: dict[str, bool]) -> list[ParsedTeamBox]:
    out: list[ParsedTeamBox] = []
    for entry in box.get("teams") or []:
        team = entry.get("team") or {}
        team_id = str(team.get("id") or "")
        stats = {}
        for s in entry.get("statistics") or []:
            key = s.get("name") or s.get("label") or ""
            stats[key] = s.get("displayValue")
        fgm, fga = _made_att(stats.get("fieldGoalsMade-fieldGoalsAttempted"))
        tpm, tpa = _made_att(stats.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted"))
        ftm, fta = _made_att(stats.get("freeThrowsMade-freeThrowsAttempted"))
        out.append(
            ParsedTeamBox(
                event_id=event_id,
                team_id=team_id,
                is_home=home_away.get(team_id, False),
                team_abbr=team.get("abbreviation") or "",
                team_name=_team_name(team),
                pts=_num(stats.get("points")),
                reb=_num(stats.get("totalRebounds") or stats.get("rebounds")),
                ast=_num(stats.get("assists")),
                stl=_num(stats.get("steals")),
                blk=_num(stats.get("blocks")),
                tov=_num(stats.get("turnovers") or stats.get("totalTurnovers")),
                pf=_num(stats.get("fouls") or stats.get("personalFouls")),
                fgm=fgm,
                fga=fga,
                tpm=tpm,
                tpa=tpa,
                ftm=ftm,
                fta=fta,
                raw=entry,
            )
        )
    return out


def _stat_index(keys: list[str]) -> dict[str, int]:
    return {k: i for i, k in enumerate(keys)}


def _parse_player_box(box: dict, event_id: str) -> list[ParsedPlayerBox]:
    out: list[ParsedPlayerBox] = []
    for team_block in box.get("players") or []:
        team = team_block.get("team") or {}
        team_id = str(team.get("id") or "")
        for stat_group in team_block.get("statistics") or []:
            keys = stat_group.get("keys") or stat_group.get("names") or _STAT_KEYS
            idx = _stat_index(keys)
            for ath in stat_group.get("athletes") or []:
                out.append(_parse_athlete(ath, event_id, team_id, idx))
    return out


def _parse_athlete(ath: dict, event_id: str, team_id: str, idx: dict[str, int]) -> ParsedPlayerBox:
    athlete = ath.get("athlete") or {}
    stats = ath.get("stats") or []

    def cell(label: str):
        i = idx.get(label)
        if i is None or i >= len(stats):
            return None
        return stats[i]

    did_not_play = bool(ath.get("didNotPlay")) or not stats
    minutes = None if did_not_play else parse_minutes(cell("MIN"))
    fgm, fga = _made_att(cell("FG"))
    tpm, tpa = _made_att(cell("3PT"))
    ftm, fta = _made_att(cell("FT"))
    pm = cell("+/-")
    position = ((athlete.get("position") or {}).get("abbreviation")) or ""
    return ParsedPlayerBox(
        event_id=event_id,
        team_id=team_id,
        player_id=str(athlete.get("id") or ""),
        player_name=athlete.get("displayName") or athlete.get("shortName") or "",
        position=position,
        started=bool(ath.get("starter")),
        dnp=did_not_play,
        minutes=minutes,
        pts=_num(cell("PTS")),
        oreb=_num(cell("OREB")),
        dreb=_num(cell("DREB")),
        reb=_num(cell("REB")),
        ast=_num(cell("AST")),
        stl=_num(cell("STL")),
        blk=_num(cell("BLK")),
        tov=_num(cell("TO")),
        pf=_num(cell("PF")),
        fgm=fgm,
        fga=fga,
        tpm=tpm,
        tpa=tpa,
        ftm=ftm,
        fta=fta,
        plus_minus=None if pm in (None, "", "--") else _num(pm),
        raw=ath,
    )


# ---------------------------------------------------------------------------
# fetchers
# ---------------------------------------------------------------------------


def fetch_scoreboard(
    client: BudgetedClient, slug: str, game_date, priority: Priority = Priority.LOW
) -> dict:
    return client.get_json(
        f"{slug}/scoreboard",
        {"dates": f"{game_date:%Y%m%d}", "limit": 400},
        priority=priority,
        ttl_s=TTL_SCOREBOARD_S,
    )


def fetch_summary(
    client: BudgetedClient,
    slug: str,
    event_id: str,
    *,
    is_final: bool = True,
    priority: Priority = Priority.NORMAL,
) -> dict:
    return client.get_json(
        f"{slug}/summary",
        {"event": event_id},
        priority=priority,
        ttl_s=TTL_SUMMARY_FINAL_S if is_final else 0.0,
    )
