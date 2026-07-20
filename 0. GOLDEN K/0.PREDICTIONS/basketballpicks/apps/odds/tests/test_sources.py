"""Pure tests for the FREE odds source parsers (apps.odds.sources.*) + the shared
market/odds primitives. No Django/DB, no network."""

import pytest

from apps.odds.sources import bovada, common, prizepicks, the_odds_api, underdog
from apps.odds.sources.common import ParsedPropQuote

# ---- vocabulary + odds conversion ------------------------------------------


def test_normalize_market_odds_api_keys():
    assert common.normalize_market("player_points") == "points"
    assert common.normalize_market("player_points_rebounds_assists") == "pra"
    assert common.normalize_market("player_blocks_steals") == "blocks_steals"


def test_normalize_market_freetext_labels():
    assert common.normalize_market("Pts+Rebs+Asts") == "pra"
    assert common.normalize_market("3-PT Made") == "threes"
    assert common.normalize_market("Rebounds") == "rebounds"


def test_normalize_market_unknown_is_none():
    assert common.normalize_market("player_dunks") is None
    assert common.normalize_market(None) is None


def test_market_keys_match_prop_market_vocab():
    # every mapped market is a lowercase PropMarket.key (predictions contract)
    for v in common.MARKETS:
        assert v == v.lower()


def test_american_to_decimal():
    assert common.american_to_decimal(150) == pytest.approx(2.5)
    assert common.american_to_decimal(-120) == pytest.approx(1.83333, abs=1e-4)
    assert common.american_to_decimal(None) is None
    assert common.american_to_decimal(0) is None


def test_parsed_quote_two_sided_flag():
    assert ParsedPropQuote("s", "b", "P", "points", 24.5, 1.9, 1.95).two_sided()
    dfs_q = ParsedPropQuote("s", "b", "P", "points", 24.5, payout_mult=1.0, is_dfs=True)
    assert not dfs_q.two_sided()


# ---- The Odds API ----------------------------------------------------------


def test_the_odds_api_parses_two_sided_props():
    payload = {
        "bookmakers": [
            {"key": "draftkings", "markets": [
                {"key": "player_points", "outcomes": [
                    {"name": "Over", "description": "LeBron James", "point": 24.5, "price": 1.90},
                    {"name": "Under", "description": "LeBron James", "point": 24.5, "price": 1.95},
                ]},
                {"key": "player_dunks", "outcomes": [  # unmapped -> skipped
                    {"name": "Over", "description": "X", "point": 0.5, "price": 2.0}]},
            ]}
        ]
    }
    quotes = the_odds_api.parse_event_props(payload)
    assert len(quotes) == 1
    q = quotes[0]
    assert q.market == "points" and q.over_price == 1.90 and q.under_price == 1.95
    assert q.book == "draftkings" and q.two_sided()


def test_the_odds_api_free_event_ids():
    assert the_odds_api.parse_event_ids([{"id": "abc"}, {"id": "def"}, {}]) == ["abc", "def"]


# ---- Underdog (DFS venue #1) -----------------------------------------------


def test_underdog_parses_pickem_leg_with_no_price():
    payload = {
        "players": [{"id": "p1", "first_name": "Nikola", "last_name": "Jokic"}],
        "appearances": [{"id": "a1", "player_id": "p1"}],
        "over_under_lines": [
            {"stat_value": "12.5",
             "over_under": {"appearance_stat": {"stat": "rebounds", "appearance_id": "a1"}},
             "options": [{"choice": "higher", "payout_multiplier": "1"},
                         {"choice": "lower", "payout_multiplier": "1"}]},
        ],
    }
    quotes = underdog.parse(payload)
    assert len(quotes) == 1
    q = quotes[0]
    assert q.is_dfs and q.player_name == "Nikola Jokic" and q.market == "rebounds"
    assert q.line == 12.5 and q.over_price is None and q.under_price is None


# ---- PrizePicks (DFS venue #2) ---------------------------------------------


def test_prizepicks_parses_and_flags_odds_type():
    payload = {
        "data": [{"type": "projection", "id": "1",
                  "attributes": {"line_score": 8.5, "stat_type": "Assists", "odds_type": "demon"},
                  "relationships": {"new_player": {"data": {"id": "99", "type": "new_player"}}}}],
        "included": [{"type": "new_player", "id": "99", "attributes": {"name": "Trae Young"}}],
    }
    quotes = prizepicks.parse(payload)
    assert len(quotes) == 1
    q = quotes[0]
    assert q.market == "assists" and q.line == 8.5 and q.is_dfs
    assert q.dfs_odds_type == "demon" and q.player_name == "Trae Young"


# ---- Bovada (datacenter-reachable backbone) --------------------------------


def test_bovada_parses_team_style_outcomes():
    payload = [{
        "events": [{
            "displayGroups": [{
                "markets": [{
                    "statType": "player_points",
                    "outcomes": [
                        {"description": "Jayson Tatum", "type": "Over",
                         "price": {"decimal": "1.90", "handicap": "27.5"}},
                        {"description": "Jayson Tatum", "type": "Under",
                         "price": {"decimal": "1.87", "handicap": "27.5"}},
                    ],
                }]
            }]
        }]
    }]
    quotes = bovada.parse(payload)
    assert len(quotes) == 1
    assert quotes[0].market == "points" and quotes[0].line == 27.5 and quotes[0].two_sided()
