"""Golden tests for the nba_api (stats.nba.com) PURE parser — recorded
resultSets payloads fed to the parse fns; no ORM, no network. (Runs under the
project's pytest-django once the app is integrated.)"""

from decimal import Decimal

from apps.ingestion.sources import nba_api

SCOREBOARD = {
    "resultSets": [
        {
            "name": "GameHeader",
            "headers": [
                "GAME_ID", "GAME_DATE_EST", "GAME_STATUS_ID", "GAME_STATUS_TEXT",
                "HOME_TEAM_ID", "VISITOR_TEAM_ID",
            ],
            "rowSet": [
                ["0022500500", "2026-01-15T00:00:00", 3, "Final", 1610612747, 1610612738],
                ["0022500501", "2026-01-15T00:00:00", 1, "7:30 pm ET", 1610612744, 1610612739],
            ],
        },
        {
            "name": "LineScore",
            "headers": [
                "GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_CITY_NAME", "TEAM_NAME",
                "PTS", "PTS_QTR1", "PTS_QTR2", "PTS_QTR3", "PTS_QTR4", "PTS_OT1",
            ],
            "rowSet": [
                ["0022500500", 1610612747, "LAL", "Los Angeles", "Lakers", 118, 30, 28, 30, 25, 5],
                ["0022500500", 1610612738, "BOS", "Boston", "Celtics", 115, 25, 30, 30, 28, 2],
                ["0022500501", 1610612744, "GSW", "Golden State", "Warriors", 0, 0, 0, 0, 0, 0],
                ["0022500501", 1610612739, "CLE", "Cleveland", "Cavaliers", 0, 0, 0, 0, 0, 0],
            ],
        },
    ]
}

BOX_TRADITIONAL = {
    "resultSets": [
        {
            "name": "PlayerStats",
            "headers": [
                "GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_CITY", "PLAYER_ID",
                "PLAYER_NAME", "START_POSITION", "COMMENT", "MIN", "FGM", "FGA", "FG3M",
                "FG3A", "FTM", "FTA", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO",
                "PF", "PTS", "PLUS_MINUS",
            ],
            "rowSet": [
                ["0022500500", 1610612747, "LAL", "Los Angeles", 2544, "LeBron James", "F",
                 "", "38:24", 10, 20, 2, 6, 5, 6, 1, 7, 8, 9, 1, 1, 3, 2, 27, 8],
                ["0022500500", 1610612747, "LAL", "Los Angeles", 99999, "Bench Guy", "",
                 "DNP - Coach's Decision", None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None],
            ],
        },
        {
            "name": "TeamStats",
            "headers": [
                "GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_CITY", "TEAM_NAME", "MIN",
                "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "OREB", "DREB", "REB", "AST",
                "STL", "BLK", "TO", "PF", "PTS",
            ],
            "rowSet": [
                ["0022500500", 1610612747, "LAL", "Los Angeles", "Lakers", "265:00", 44, 90,
                 12, 33, 18, 22, 10, 35, 45, 25, 7, 5, 12, 18, 118],
            ],
        },
    ]
}

BOX_ADVANCED = {
    "resultSets": [
        {
            "name": "PlayerStats",
            "headers": ["GAME_ID", "TEAM_ID", "PLAYER_ID", "USG_PCT", "PACE", "OFF_RATING", "DEF_RATING"],
            "rowSet": [["0022500500", 1610612747, 2544, 0.315, 99.5, 118.2, 110.1]],
        },
        {
            "name": "TeamStats",
            "headers": ["GAME_ID", "TEAM_ID", "PACE", "OFF_RATING", "DEF_RATING"],
            "rowSet": [["0022500500", 1610612747, 99.5, 116.0, 112.0]],
        },
    ]
}


class TestParseMinutes:
    def test_mmss(self):
        assert nba_api.parse_minutes("38:24") == Decimal("38.40")
        assert nba_api.parse_minutes("0:00") == Decimal("0.00")

    def test_dnp_and_blank(self):
        assert nba_api.parse_minutes(None) is None
        assert nba_api.parse_minutes("") is None


class TestScoreboard:
    def test_two_games_status_and_scores(self):
        games = nba_api.parse_scoreboard(SCOREBOARD)
        assert len(games) == 2
        final = next(g for g in games if g.game_id == "0022500500")
        assert final.status == "FINAL" and final.status_id == 3
        assert (final.home_abbr, final.away_abbr) == ("LAL", "BOS")
        assert (final.home_score, final.away_score) == (118, 115)
        assert final.num_ot == 1  # PTS_OT1 populated for both teams
        assert final.period_scores["Q"]["home"] == [30, 28, 30, 25]
        assert final.home_name == "Los Angeles Lakers"

    def test_scheduled_game_has_no_score(self):
        games = nba_api.parse_scoreboard(SCOREBOARD)
        sched = next(g for g in games if g.game_id == "0022500501")
        assert sched.status == "SCHEDULED"
        assert sched.home_score is None and sched.away_score is None
        assert sched.num_ot == 0


class TestBoxScores:
    def test_player_box_started_dnp_and_stats(self):
        rows = nba_api.parse_player_boxscores(BOX_TRADITIONAL)
        assert len(rows) == 2
        lebron = next(r for r in rows if r.player_id == "2544")
        assert lebron.started is True and lebron.dnp is False
        assert lebron.minutes == Decimal("38.40")
        assert (lebron.pts, lebron.reb, lebron.ast, lebron.tpm) == (27, 8, 9, 2)
        assert lebron.plus_minus == 8
        bench = next(r for r in rows if r.player_id == "99999")
        assert bench.dnp is True and bench.started is False
        assert bench.minutes is None and bench.plus_minus is None

    def test_team_box(self):
        rows = nba_api.parse_team_boxscores(BOX_TRADITIONAL)
        assert len(rows) == 1
        t = rows[0]
        assert t.team_abbr == "LAL" and t.pts == 118
        assert (t.fgm, t.fga, t.tpm) == (44, 90, 12)
        assert t.minutes == Decimal("265.00")

    def test_advanced_overlay(self):
        players, teams = nba_api.parse_advanced(BOX_ADVANCED)
        assert players["2544"]["usage_rate"] == Decimal("0.315")
        assert teams["1610612747"]["pace"] == Decimal("99.5")
