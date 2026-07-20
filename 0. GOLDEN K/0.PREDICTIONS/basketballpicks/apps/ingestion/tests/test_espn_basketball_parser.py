"""Golden tests for the shared ESPN basketball PURE parser (wehoop WNBA +
hoopR NCAA-M). Recorded scoreboard + summary payloads; no ORM, no network."""

from decimal import Decimal

from apps.ingestion.sources import espn_basketball as espn

SCOREBOARD = {
    "leagues": [{"slug": "wnba"}],
    "events": [
        {
            "id": "401620001",
            "date": "2026-06-15T23:00Z",
            "competitions": [
                {
                    "status": {"type": {"name": "STATUS_FINAL", "state": "post", "completed": True}, "period": 5},
                    "venue": {"fullName": "Barclays Center"},
                    "competitors": [
                        {"homeAway": "home", "score": "90",
                         "team": {"id": "20", "abbreviation": "NY", "displayName": "New York Liberty"}},
                        {"homeAway": "away", "score": "88",
                         "team": {"id": "5", "abbreviation": "LV", "displayName": "Las Vegas Aces"}},
                    ],
                }
            ],
        },
        {
            "id": "401620002",
            "date": "2026-06-16T00:00Z",
            "competitions": [
                {
                    "status": {"type": {"name": "STATUS_SCHEDULED", "state": "pre", "completed": False}, "period": 0},
                    "competitors": [
                        {"homeAway": "home", "score": "0",
                         "team": {"id": "6", "abbreviation": "SEA", "displayName": "Seattle Storm"}},
                        {"homeAway": "away", "score": "0",
                         "team": {"id": "9", "abbreviation": "MIN", "displayName": "Minnesota Lynx"}},
                    ],
                }
            ],
        },
    ],
}

SUMMARY = {
    "header": {
        "id": "401620001",
        "league": {"slug": "wnba"},
        "competitions": [
            {
                "date": "2026-06-15T23:00Z",
                "status": {"type": {"name": "STATUS_FINAL", "state": "post", "completed": True}, "period": 5},
                "competitors": [
                    {"homeAway": "home", "score": "90", "team": {"id": "20", "abbreviation": "NY"}},
                    {"homeAway": "away", "score": "88", "team": {"id": "5", "abbreviation": "LV"}},
                ],
            }
        ],
    },
    "boxscore": {
        "teams": [
            {
                "team": {"id": "20", "abbreviation": "NY", "displayName": "New York Liberty"},
                "statistics": [
                    {"name": "fieldGoalsMade-fieldGoalsAttempted", "displayValue": "32-70"},
                    {"name": "threePointFieldGoalsMade-threePointFieldGoalsAttempted", "displayValue": "9-25"},
                    {"name": "freeThrowsMade-freeThrowsAttempted", "displayValue": "17-19"},
                    {"name": "totalRebounds", "displayValue": "38"},
                    {"name": "assists", "displayValue": "20"},
                    {"name": "steals", "displayValue": "7"},
                    {"name": "blocks", "displayValue": "4"},
                    {"name": "turnovers", "displayValue": "11"},
                    {"name": "fouls", "displayValue": "16"},
                    {"name": "points", "displayValue": "90"},
                ],
            },
            {
                "team": {"id": "5", "abbreviation": "LV", "displayName": "Las Vegas Aces"},
                "statistics": [
                    {"name": "fieldGoalsMade-fieldGoalsAttempted", "displayValue": "34-72"},
                    {"name": "points", "displayValue": "88"},
                ],
            },
        ],
        "players": [
            {
                "team": {"id": "20", "abbreviation": "NY"},
                "statistics": [
                    {
                        "keys": ["MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST",
                                 "STL", "BLK", "TO", "PF", "+/-", "PTS"],
                        "athletes": [
                            {
                                "starter": True, "didNotPlay": False,
                                "athlete": {"id": "1001", "displayName": "Sabrina Ionescu",
                                            "position": {"abbreviation": "G"}},
                                "stats": ["36", "9-18", "4-9", "3-3", "1", "4", "5", "6",
                                          "2", "0", "3", "2", "+8", "25"],
                            },
                            {
                                "starter": False, "didNotPlay": True,
                                "athlete": {"id": "1002", "displayName": "Deep Bench",
                                            "position": {"abbreviation": "F"}},
                                "reason": "DNP-COACH", "stats": [],
                            },
                        ],
                    }
                ],
            }
        ],
    },
}


class TestScoreboard:
    def test_final_with_overtime(self):
        games = espn.parse_scoreboard(SCOREBOARD)
        assert len(games) == 2
        f = next(g for g in games if g.event_id == "401620001")
        assert f.status == "FINAL"
        assert (f.home_abbr, f.away_abbr) == ("NY", "LV")
        assert (f.home_score, f.away_score) == (90, 88)
        assert f.num_ot == 1  # wnba regulation = 4 quarters, period 5 => 1 OT
        assert f.venue == "Barclays Center"

    def test_scheduled_no_score(self):
        games = espn.parse_scoreboard(SCOREBOARD)
        s = next(g for g in games if g.event_id == "401620002")
        assert s.status == "SCHEDULED"
        assert s.home_score is None and s.away_score is None
        assert s.num_ot == 0

    def test_mens_college_ot_uses_two_halves(self):
        payload = {
            "leagues": [{"slug": "mens-college-basketball"}],
            "events": [{
                "id": "9", "date": "2026-01-15T00:00Z",
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL", "completed": True}, "period": 3},
                    "competitors": [
                        {"homeAway": "home", "score": "80", "team": {"id": "1", "abbreviation": "DUKE"}},
                        {"homeAway": "away", "score": "78", "team": {"id": "2", "abbreviation": "UNC"}},
                    ],
                }],
            }],
        }
        g = espn.parse_scoreboard(payload)[0]
        assert g.num_ot == 1  # 2 regulation halves, period 3 => 1 OT


class TestBoxscore:
    def test_team_and_player_box(self):
        teams, players = espn.parse_boxscore(SUMMARY)
        ny = next(t for t in teams if t.team_id == "20")
        assert ny.is_home is True
        assert (ny.fgm, ny.fga, ny.tpm) == (32, 70, 9)
        assert (ny.ftm, ny.fta) == (17, 19)
        assert (ny.pts, ny.reb, ny.ast) == (90, 38, 20)

        assert len(players) == 2
        sabrina = next(p for p in players if p.player_id == "1001")
        assert sabrina.started is True and sabrina.dnp is False
        assert sabrina.minutes == Decimal("36.00")
        assert (sabrina.pts, sabrina.reb, sabrina.tpm) == (25, 5, 4)
        assert sabrina.plus_minus == 8
        assert sabrina.position == "G"
        bench = next(p for p in players if p.player_id == "1002")
        assert bench.dnp is True and bench.minutes is None

    def test_game_meta_reconstructs_game(self):
        meta = espn.game_meta(SUMMARY)
        assert meta is not None
        assert meta.event_id == "401620001" and meta.status == "FINAL"
        assert meta.home_team_id == "20" and meta.away_team_id == "5"
