"""EuroLeague official feeds (the euroleague-api source) — the cleanest FREE
international PLAYER-box + schedule feed [bball-02 S3].

PURE parser (no ORM). Uses the classic live.euroleague.net JSON feeds that the
``euroleague-api`` package wraps:
  * ``Schedules?seasonCode=E2025``          — the season's games (codes + teams)
  * ``Results?seasonCode=E2025&gameCode=N``  — final scores for a game
  * ``Boxscore?seasonCode=E2025&gameCode=N`` — TEAM + PLAYER box for a game

Season codes: ``E2025`` == the 2025-26 EuroLeague season. Boxscore PlayersStats
carry the classic field names (FieldGoalsMade2/3, TotalRebounds, Valuation,
StartFive, Minutes 'MM:SS'). Endpoint shapes MUST be spot-verified on the first
live sync (the bball-02 §2 "(verify)" flag) — the recorded-fixture tests lock
the PARSE logic, which is the load-bearing part.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal

from apps.ingestion.http import BudgetedClient, Priority

SOURCE = "euroleague"
COMPETITION = "E"  # EuroLeague (EuroCup would be 'U' in Phase 2)

TTL_SCHEDULE_S = 6 * 3600.0
TTL_BOXSCORE_FINAL_S = 7 * 24 * 3600.0


def season_code(start_year: int) -> str:
    """2025 -> 'E2025' (the 2025-26 season)."""
    return f"E{start_year}"


def season_name(start_year: int) -> str:
    return f"{start_year}-{(start_year + 1) % 100:02d}"


@dataclass
class ParsedGame:
    game_code: str
    season_code: str
    round_num: int | None
    played: bool
    tipoff_utc: datetime | None
    home_code: str
    away_code: str
    home_name: str
    away_name: str
    home_score: int | None
    away_score: int | None
    raw: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "FINAL" if self.played else "SCHEDULED"


@dataclass
class ParsedTeamBox:
    game_code: str
    team_code: str
    team_name: str
    is_home: bool
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
    raw: dict = field(default_factory=dict)


@dataclass
class ParsedPlayerBox:
    game_code: str
    team_code: str
    player_id: str
    player_name: str
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
    valuation: int | None
    raw: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def parse_minutes(value) -> Decimal | None:
    """'MM:SS' -> Decimal minutes; 'DNP'/''/None -> None (did not play)."""
    if value in (None, ""):
        return None
    s = str(value).strip()
    if s.upper() in ("DNP", "DNS", "--"):
        return None
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


def _i(row: dict, *keys, default=0) -> int:
    for key in keys:
        v = row.get(key)
        if v not in (None, ""):
            try:
                return int(round(float(v)))
            except (TypeError, ValueError):
                continue
    return default


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%b %d, %Y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# schedule parser
# ---------------------------------------------------------------------------


def parse_schedule(payload: dict, scode: str) -> list[ParsedGame]:
    """Games from a Schedules/Results feed. Accepts the classic ``{'item':[...]}``
    envelope or a bare list; scores present only for played games."""
    items = payload.get("item") if isinstance(payload, dict) else payload
    if items is None and isinstance(payload, dict):
        items = payload.get("items") or payload.get("data") or []
    out: list[ParsedGame] = []
    for it in items or []:
        game_code = str(it.get("gamecode") or it.get("gameCode") or it.get("code") or "")
        if not game_code:
            continue
        played = _truthy(it.get("played"))
        home_score = _i(it, "homescore", "homeScore", "scoreA", default=None) if played else None
        away_score = _i(it, "awayscore", "awayScore", "scoreB", default=None) if played else None
        out.append(
            ParsedGame(
                game_code=game_code,
                season_code=scode,
                round_num=_i(it, "gameday", "round", "gamenumber", default=None),
                played=played,
                tipoff_utc=_parse_dt(it.get("date") or it.get("startDate") or it.get("datetime")),
                home_code=str(it.get("homecode") or it.get("homeCode") or it.get("codeA") or ""),
                away_code=str(it.get("awaycode") or it.get("awayCode") or it.get("codeB") or ""),
                home_name=it.get("hometeam") or it.get("homeTeam") or it.get("teamA") or "",
                away_name=it.get("awayteam") or it.get("awayTeam") or it.get("teamB") or "",
                home_score=home_score,
                away_score=away_score,
                raw=it,
            )
        )
    return out


def _truthy(v) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "1", "yes", "played")


# ---------------------------------------------------------------------------
# boxscore parser
# ---------------------------------------------------------------------------


def _stat_fields(row: dict) -> dict:
    """Map the classic PlayersStats/team-total field names to core columns."""
    fgm2, fga2 = _i(row, "FieldGoalsMade2"), _i(row, "FieldGoalsAttempted2")
    fgm3, fga3 = _i(row, "FieldGoalsMade3"), _i(row, "FieldGoalsAttempted3")
    return {
        "pts": _i(row, "Points"),
        "oreb": _i(row, "OffensiveRebounds"),
        "dreb": _i(row, "DefensiveRebounds"),
        "reb": _i(row, "TotalRebounds"),
        "ast": _i(row, "Assistances", "Assists"),
        "stl": _i(row, "Steals"),
        "blk": _i(row, "BlocksFavour", "Blocks"),
        "tov": _i(row, "Turnovers"),
        "pf": _i(row, "FoulsCommited", "FoulsCommitted"),
        "fgm": fgm2 + fgm3,
        "fga": fga2 + fga3,
        "tpm": fgm3,
        "tpa": fga3,
        "ftm": _i(row, "FreeThrowsMade"),
        "fta": _i(row, "FreeThrowsAttempted"),
    }


def parse_boxscore(
    payload: dict, game_code: str, home_code: str = "", away_code: str = ""
) -> tuple[list[ParsedTeamBox], list[ParsedPlayerBox]]:
    """TEAM + PLAYER box from the classic Boxscore feed ``{'Stats':[t1, t2]}``.
    The first Stats entry is the home team, the second the away (the classic
    convention); ``home_code``/``away_code`` from the schedule override it."""
    stats = payload.get("Stats") or payload.get("stats") or []
    team_rows: list[ParsedTeamBox] = []
    player_rows: list[ParsedPlayerBox] = []

    for pos, team_block in enumerate(stats):
        team_name = team_block.get("Team") or team_block.get("team") or ""
        tcode = str(team_block.get("TeamCode") or team_block.get("code") or "")
        is_home = pos == 0
        if home_code and tcode:
            is_home = tcode == home_code
        elif away_code and tcode:
            is_home = tcode != away_code

        totals = team_block.get("totr") or team_block.get("Totals") or {}
        tf = _stat_fields(totals)
        # team totals carry only combined REB (no oreb/dreb split on the row)
        tf.pop("oreb", None)
        tf.pop("dreb", None)
        team_rows.append(
            ParsedTeamBox(
                game_code=game_code,
                team_code=tcode or team_name,
                team_name=team_name,
                is_home=is_home,
                minutes=parse_minutes(totals.get("Minutes")),
                raw=team_block,
                **tf,
            )
        )

        for p in team_block.get("PlayersStats") or team_block.get("playersStats") or []:
            minutes = parse_minutes(p.get("Minutes"))
            pf = _stat_fields(p)
            player_rows.append(
                ParsedPlayerBox(
                    game_code=game_code,
                    team_code=tcode or team_name,
                    player_id=str(p.get("Player_ID") or p.get("PlayerCode") or "").strip(),
                    player_name=(p.get("Player") or "").strip(),
                    started=_truthy(p.get("StartFive")),
                    dnp=minutes is None,
                    minutes=minutes,
                    valuation=_i(p, "Valuation", default=None),
                    raw=p,
                    **pf,
                )
            )
    return team_rows, player_rows


# ---------------------------------------------------------------------------
# fetchers
# ---------------------------------------------------------------------------


def fetch_schedule(
    client: BudgetedClient, scode: str, priority: Priority = Priority.LOW
) -> dict:
    return client.get_json(
        "Schedules",
        {"seasonCode": scode},
        priority=priority,
        ttl_s=TTL_SCHEDULE_S,
    )


def fetch_results(
    client: BudgetedClient, scode: str, game_code: str, priority: Priority = Priority.NORMAL
) -> dict:
    return client.get_json(
        "Results",
        {"seasonCode": scode, "gameCode": game_code},
        priority=priority,
        ttl_s=TTL_SCHEDULE_S,
    )


def fetch_boxscore(
    client: BudgetedClient,
    scode: str,
    game_code: str,
    *,
    is_final: bool = True,
    priority: Priority = Priority.NORMAL,
) -> dict:
    return client.get_json(
        "Boxscore",
        {"seasonCode": scode, "gameCode": game_code},
        priority=priority,
        ttl_s=TTL_BOXSCORE_FINAL_S if is_final else 0.0,
    )
