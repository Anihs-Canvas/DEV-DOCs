"""Golden tests for the EuroLeague PURE parser — recorded Schedules + classic
Boxscore payloads; no ORM, no network."""

from decimal import Decimal

from apps.ingestion.sources import euroleague

SCHEDULE = {
    "item": [
        {
            "gamecode": "1", "gameday": "1", "played": "true",
            "date": "2025-10-02 20:00:00",
            "homecode": "MAD", "awaycode": "BAR",
            "hometeam": "Real Madrid", "awayteam": "FC Barcelona",
            "homescore": "88", "awayscore": "82",
        },
        {
            "gamecode": "2", "gameday": "1", "played": False,
            "date": "2025-10-03 20:00:00",
            "homecode": "PAN", "awaycode": "OLY",
            "hometeam": "Panathinaikos", "awayteam": "Olympiacos",
        },
    ]
}


def _stat_line(**over):
    base = {
        "Points": 0, "FieldGoalsMade2": 0, "FieldGoalsAttempted2": 0,
        "FieldGoalsMade3": 0, "FieldGoalsAttempted3": 0, "FreeThrowsMade": 0,
        "FreeThrowsAttempted": 0, "OffensiveRebounds": 0, "DefensiveRebounds": 0,
        "TotalRebounds": 0, "Assistances": 0, "Steals": 0, "Turnovers": 0,
        "BlocksFavour": 0, "FoulsCommited": 0,
    }
    base.update(over)
    return base


BOXSCORE = {
    "Stats": [
        {
            "Team": "Real Madrid", "TeamCode": "MAD",
            "totr": _stat_line(
                Minutes="200:00", Points=88, FieldGoalsMade2=20, FieldGoalsAttempted2=35,
                FieldGoalsMade3=12, FieldGoalsAttempted3=28, FreeThrowsMade=12,
                FreeThrowsAttempted=15, TotalRebounds=35, Assistances=22, Steals=7,
                Turnovers=10, BlocksFavour=3, FoulsCommited=18,
            ),
            "PlayersStats": [
                dict(_stat_line(
                    Points=15, FieldGoalsMade2=3, FieldGoalsAttempted2=6, FieldGoalsMade3=3,
                    FieldGoalsAttempted3=5, TotalRebounds=2, DefensiveRebounds=2, Assistances=5,
                    Steals=1, Turnovers=2, FoulsCommited=2,
                ), Player_ID="P001", Player="Sergio Llull", Dorsal="23", Minutes="25:30",
                    StartFive=1, Valuation=16),
                dict(_stat_line(), Player_ID="P002", Player="DNP Player", Minutes="DNP",
                     StartFive=0, Valuation=0),
            ],
        },
        {
            "Team": "FC Barcelona", "TeamCode": "BAR",
            "totr": _stat_line(Minutes="200:00", Points=82, FieldGoalsMade2=22,
                               FieldGoalsAttempted2=40, FieldGoalsMade3=8, FieldGoalsAttempted3=24,
                               FreeThrowsMade=14, FreeThrowsAttempted=18, TotalRebounds=30),
            "PlayersStats": [],
        },
    ]
}


class TestSchedule:
    def test_played_and_scheduled(self):
        games = euroleague.parse_schedule(SCHEDULE, "E2025")
        assert len(games) == 2
        g1 = next(g for g in games if g.game_code == "1")
        assert g1.played is True and g1.status == "FINAL"
        assert (g1.home_score, g1.away_score) == (88, 82)
        assert (g1.home_code, g1.away_code) == ("MAD", "BAR")
        assert g1.tipoff_utc is not None
        g2 = next(g for g in games if g.game_code == "2")
        assert g2.played is False and g2.status == "SCHEDULED"
        assert g2.home_score is None and g2.away_score is None


class TestBoxscore:
    def test_home_away_and_team_totals(self):
        teams, players = euroleague.parse_boxscore(BOXSCORE, "1", "MAD", "BAR")
        assert len(teams) == 2
        mad = next(t for t in teams if t.team_code == "MAD")
        assert mad.is_home is True
        # fgm = FGM2 + FGM3 = 20 + 12; tpm = FGM3 = 12
        assert (mad.fgm, mad.fga, mad.tpm, mad.tpa) == (32, 63, 12, 28)
        assert mad.pts == 88 and mad.reb == 35
        assert mad.minutes == Decimal("200.00")
        bar = next(t for t in teams if t.team_code == "BAR")
        assert bar.is_home is False

    def test_player_stats_and_dnp(self):
        _teams, players = euroleague.parse_boxscore(BOXSCORE, "1", "MAD", "BAR")
        assert len(players) == 2
        llull = next(p for p in players if p.player_id == "P001")
        assert llull.started is True and llull.dnp is False
        assert llull.minutes == Decimal("25.50")
        assert (llull.pts, llull.fgm, llull.tpm, llull.reb, llull.ast) == (15, 6, 3, 2, 5)
        assert llull.valuation == 16
        dnp = next(p for p in players if p.player_id == "P002")
        assert dnp.dnp is True and dnp.minutes is None
