"""stats.nba.com (nba_api) — the richest FREE player-level source [bball-02 S1].

NBA schedule + TEAM box + PLAYER box (+ optional advanced usage/pace). Keyless
but IP/rate-limited: browser headers + a gentle bucket are supplied by
``harvest.nba_api_client``; this module is PURE (no ORM), mirroring the
safepicks ``sources/*`` pattern — thin fetchers take an injected BudgetedClient,
parse fns take the decoded ``resultSets`` envelope, services own persistence,
tests feed recorded payloads.

stats.nba.com returns ``{"resultSets": [{"name","headers","rowSet":[[...]]}]}``.
Endpoints used:
  * scoreboardv2            — the day's games (GameHeader + LineScore)
  * boxscoretraditionalv2   — PlayerStats + TeamStats for one game
  * boxscoreadvancedv2      — USG_PCT / PACE / OFF_RATING / DEF_RATING (optional;
                              feeds the props usage-cascade signal, bball-01 §2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal

from apps.ingestion.http import BudgetedClient, Priority

SOURCE = "nba_api"
LEAGUE_ID = "00"  # stats.nba.com LeagueID for the NBA

# GameHeader.GAME_STATUS_ID -> core.Game status
STATUS_MAP = {1: "SCHEDULED", 2: "LIVE", 3: "FINAL"}

# per-endpoint TTLs [bball-02 §4]: a final box is immutable, a schedule drifts.
TTL_SCOREBOARD_S = 1800.0
TTL_BOXSCORE_FINAL_S = 7 * 24 * 3600.0  # effectively immutable once FINAL

# boxscoretraditionalv2 requires the full period-range params or it 400s.
_BOX_RANGE = {
    "StartPeriod": 0,
    "EndPeriod": 14,
    "StartRange": 0,
    "EndRange": 55800,
    "RangeType": 2,
}


@dataclass
class ParsedGame:
    game_id: str
    status: str
    status_id: int
    game_date: date
    tipoff_utc: datetime
    home_team_id: str
    away_team_id: str
    home_abbr: str
    away_abbr: str
    home_name: str
    away_name: str
    home_score: int | None
    away_score: int | None
    num_ot: int
    period_scores: dict
    raw: dict = field(default_factory=dict)


@dataclass
class ParsedTeamBox:
    game_id: str
    team_id: str
    team_abbr: str
    team_name: str
    minutes: Decimal | None
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
    pace: Decimal | None = None
    off_rtg: Decimal | None = None
    def_rtg: Decimal | None = None
    raw: dict = field(default_factory=dict)


@dataclass
class ParsedPlayerBox:
    game_id: str
    team_id: str
    player_id: str
    player_name: str
    start_position: str
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
    usage_rate: Decimal | None = None
    raw: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def result_sets(payload: dict) -> dict[str, list[dict]]:
    """Zip every ``resultSets`` entry into ``{name: [rowdict, ...]}`` so callers
    read cells by column name, never by brittle positional index."""
    out: dict[str, list[dict]] = {}
    for rs in payload.get("resultSets") or payload.get("resultSet") or []:
        if not isinstance(rs, dict):
            continue
        headers = rs.get("headers") or []
        name = rs.get("name") or ""
        rows = [dict(zip(headers, row, strict=False)) for row in rs.get("rowSet") or []]
        out[name] = rows
    return out


def parse_minutes(value) -> Decimal | None:
    """stats.nba.com MIN is 'MM:SS' ('34:30' -> 34.5), sometimes a bare number,
    None/'' for a DNP. Returns minutes as a Decimal, or None when absent."""
    if value in (None, ""):
        return None
    s = str(value)
    if ":" in s:
        mm, _, ss = s.partition(":")
        try:
            minutes = Decimal(mm or "0")
            seconds = Decimal(ss or "0")
        except (ValueError, ArithmeticError):
            return None
        return (minutes + seconds / Decimal(60)).quantize(Decimal("0.01"))
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except (ValueError, ArithmeticError):
        return None


def _i(row: dict, key: str, default=0):
    v = row.get(key)
    if v in (None, ""):
        return default
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return default


def _game_date(row: dict) -> date:
    raw = (row.get("GAME_DATE_EST") or row.get("GAME_DATE") or "")[:10]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return datetime.now(UTC).date()


def _period_scores(home: dict, away: dict) -> tuple[dict, int]:
    """Per-quarter + OT scores from two LineScore rows; also the OT count."""

    def quarters(row: dict) -> list[int]:
        return [_i(row, f"PTS_QTR{q}") for q in range(1, 5)]

    def overtimes(row: dict) -> list[int]:
        return [_i(row, f"PTS_OT{n}") for n in range(1, 11)]

    ots_home, ots_away = overtimes(home), overtimes(away)
    num_ot = max(
        (n for n in range(1, 11) if ots_home[n - 1] or ots_away[n - 1]), default=0
    )
    period_scores = {
        "Q": {"home": quarters(home), "away": quarters(away)},
        "OT": {
            "home": ots_home[:num_ot],
            "away": ots_away[:num_ot],
        },
    }
    return period_scores, num_ot


# ---------------------------------------------------------------------------
# parsers
# ---------------------------------------------------------------------------


def parse_scoreboard(payload: dict) -> list[ParsedGame]:
    """Games for one day from scoreboardv2 (GameHeader + LineScore). Scores are
    read from LineScore only once present — a SCHEDULED game has none."""
    sets = result_sets(payload)
    line_by_game_team: dict[tuple[str, str], dict] = {}
    for row in sets.get("LineScore", []):
        line_by_game_team[(str(row.get("GAME_ID")), str(row.get("TEAM_ID")))] = row

    out: list[ParsedGame] = []
    for gh in sets.get("GameHeader", []):
        game_id = str(gh.get("GAME_ID") or "")
        if not game_id:
            continue
        home_id = str(gh.get("HOME_TEAM_ID") or "")
        away_id = str(gh.get("VISITOR_TEAM_ID") or "")
        home_ls = line_by_game_team.get((game_id, home_id), {})
        away_ls = line_by_game_team.get((game_id, away_id), {})
        status_id = _i(gh, "GAME_STATUS_ID", 1)
        status = STATUS_MAP.get(status_id, "SCHEDULED")

        def _abbr(ls: dict) -> str:
            return ls.get("TEAM_ABBREVIATION") or ""

        def _name(ls: dict) -> str:
            city = ls.get("TEAM_CITY_NAME") or ls.get("TEAM_CITY") or ""
            nick = ls.get("TEAM_NAME") or ls.get("TEAM_NICKNAME") or ""
            return f"{city} {nick}".strip() or _abbr(ls)

        home_pts = _i(home_ls, "PTS", None) if status == "FINAL" else None
        away_pts = _i(away_ls, "PTS", None) if status == "FINAL" else None
        period_scores, num_ot = _period_scores(home_ls, away_ls)

        gdate = _game_date(gh)
        # scoreboardv2 carries no precise tip time; the date (ET) is the
        # load-bearing slate key. The T-45m pre-tip sweep firms the time up.
        tipoff = datetime(gdate.year, gdate.month, gdate.day, tzinfo=UTC)

        out.append(
            ParsedGame(
                game_id=game_id,
                status=status,
                status_id=status_id,
                game_date=gdate,
                tipoff_utc=tipoff,
                home_team_id=home_id,
                away_team_id=away_id,
                home_abbr=_abbr(home_ls),
                away_abbr=_abbr(away_ls),
                home_name=_name(home_ls),
                away_name=_name(away_ls),
                home_score=home_pts,
                away_score=away_pts,
                num_ot=num_ot,
                period_scores=period_scores,
                raw=gh,
            )
        )
    return out


def parse_team_boxscores(payload: dict) -> list[ParsedTeamBox]:
    out: list[ParsedTeamBox] = []
    for row in result_sets(payload).get("TeamStats", []):
        out.append(
            ParsedTeamBox(
                game_id=str(row.get("GAME_ID") or ""),
                team_id=str(row.get("TEAM_ID") or ""),
                team_abbr=row.get("TEAM_ABBREVIATION") or "",
                team_name=(f"{row.get('TEAM_CITY', '')} {row.get('TEAM_NAME', '')}").strip(),
                minutes=parse_minutes(row.get("MIN")),
                pts=_i(row, "PTS"),
                reb=_i(row, "REB"),
                ast=_i(row, "AST"),
                stl=_i(row, "STL"),
                blk=_i(row, "BLK"),
                tov=_i(row, "TO"),
                pf=_i(row, "PF"),
                fgm=_i(row, "FGM"),
                fga=_i(row, "FGA"),
                tpm=_i(row, "FG3M"),
                tpa=_i(row, "FG3A"),
                ftm=_i(row, "FTM"),
                fta=_i(row, "FTA"),
                raw=row,
            )
        )
    return out


def parse_player_boxscores(payload: dict) -> list[ParsedPlayerBox]:
    out: list[ParsedPlayerBox] = []
    for row in result_sets(payload).get("PlayerStats", []):
        minutes = parse_minutes(row.get("MIN"))
        start_position = (row.get("START_POSITION") or "").strip()
        comment = (row.get("COMMENT") or "").strip()
        dnp = minutes is None or (bool(comment) and minutes is None)
        plus_minus = row.get("PLUS_MINUS")
        out.append(
            ParsedPlayerBox(
                game_id=str(row.get("GAME_ID") or ""),
                team_id=str(row.get("TEAM_ID") or ""),
                player_id=str(row.get("PLAYER_ID") or ""),
                player_name=row.get("PLAYER_NAME") or "",
                start_position=start_position,
                started=bool(start_position),
                dnp=dnp,
                minutes=minutes,
                pts=_i(row, "PTS"),
                oreb=_i(row, "OREB"),
                dreb=_i(row, "DREB"),
                reb=_i(row, "REB"),
                ast=_i(row, "AST"),
                stl=_i(row, "STL"),
                blk=_i(row, "BLK"),
                tov=_i(row, "TO"),
                pf=_i(row, "PF"),
                fgm=_i(row, "FGM"),
                fga=_i(row, "FGA"),
                tpm=_i(row, "FG3M"),
                tpa=_i(row, "FG3A"),
                ftm=_i(row, "FTM"),
                fta=_i(row, "FTA"),
                plus_minus=None if plus_minus in (None, "") else _i(row, "PLUS_MINUS"),
                raw=row,
            )
        )
    return out


def parse_advanced(payload: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    """(player_advanced_by_id, team_advanced_by_id) from boxscoreadvancedv2 —
    the USG_PCT / PACE / OFF_RATING / DEF_RATING overlay merged onto the box."""

    def _d(row: dict, key: str) -> Decimal | None:
        v = row.get(key)
        if v in (None, ""):
            return None
        try:
            return Decimal(str(v))
        except (ValueError, ArithmeticError):
            return None

    sets = result_sets(payload)
    players = {
        str(r.get("PLAYER_ID")): {
            "usage_rate": _d(r, "USG_PCT"),
            "pace": _d(r, "PACE"),
            "off_rtg": _d(r, "OFF_RATING"),
            "def_rtg": _d(r, "DEF_RATING"),
        }
        for r in sets.get("PlayerStats", [])
    }
    teams = {
        str(r.get("TEAM_ID")): {
            "pace": _d(r, "PACE"),
            "off_rtg": _d(r, "OFF_RATING"),
            "def_rtg": _d(r, "DEF_RATING"),
        }
        for r in sets.get("TeamStats", [])
    }
    return players, teams


# ---------------------------------------------------------------------------
# fetchers (thin: URL + priority + TTL; client owns budget/rate/backoff)
# ---------------------------------------------------------------------------


def fetch_scoreboard(
    client: BudgetedClient, game_date: date, priority: Priority = Priority.LOW
) -> dict:
    return client.get_json(
        "scoreboardv2",
        {"GameDate": f"{game_date:%m/%d/%Y}", "LeagueID": LEAGUE_ID, "DayOffset": 0},
        priority=priority,
        ttl_s=TTL_SCOREBOARD_S,
    )


def fetch_boxscore_traditional(
    client: BudgetedClient,
    game_id: str,
    *,
    is_final: bool = True,
    priority: Priority = Priority.NORMAL,
) -> dict:
    return client.get_json(
        "boxscoretraditionalv2",
        {"GameID": game_id, **_BOX_RANGE},
        priority=priority,
        ttl_s=TTL_BOXSCORE_FINAL_S if is_final else 0.0,
    )


def fetch_boxscore_advanced(
    client: BudgetedClient,
    game_id: str,
    *,
    is_final: bool = True,
    priority: Priority = Priority.NORMAL,
) -> dict:
    return client.get_json(
        "boxscoreadvancedv2",
        {"GameID": game_id, **_BOX_RANGE},
        priority=priority,
        ttl_s=TTL_BOXSCORE_FINAL_S if is_final else 0.0,
    )
