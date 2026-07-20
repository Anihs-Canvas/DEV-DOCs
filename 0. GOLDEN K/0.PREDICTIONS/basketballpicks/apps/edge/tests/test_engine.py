"""Pure tests for edge detection + the anchor-contamination guardrail
(apps.edge.engine). No Django/DB."""

import pytest

from apps.edge import engine


def test_edge_vs_fair():
    assert engine.edge_vs_fair(2.0, 0.55) == pytest.approx(0.10)
    assert engine.edge_vs_fair(1.8, 0.5) == pytest.approx(-0.10)


# ---- contamination tiers (the guardrail) ----------------------------------


def test_pinnacle_anchor_is_tier0_clean():
    c = engine.assess_contamination(anchor="pinnacle", venue_is_dfs=False,
                                    excluded_book=None, venue_book="draftkings")
    assert c.tier == engine.TIER_PINNACLE_AUDITED and not c.rejected


def test_consensus_vs_dfs_is_tier1_bankable():
    c = engine.assess_contamination(anchor="consensus", venue_is_dfs=True,
                                    excluded_book=None, venue_book="underdog")
    assert c.tier == engine.TIER_CONSENSUS_VS_DFS
    assert not c.rejected and c.edge_mult == 1.0 and c.needs_pinnacle_audit


def test_soft_book_with_leave_one_out_is_tier2():
    c = engine.assess_contamination(anchor="consensus", venue_is_dfs=False,
                                    excluded_book="draftkings", venue_book="draftkings")
    assert c.tier == engine.TIER_CONSENSUS_LEAVE1OUT and not c.rejected


def test_soft_book_inside_own_benchmark_is_tier3_rejected():
    # no leave-one-out → the book is inside its own fair benchmark → phantom edge.
    c = engine.assess_contamination(anchor="consensus", venue_is_dfs=False,
                                    excluded_book=None, venue_book="draftkings")
    assert c.tier == engine.TIER_CONTAMINATED and c.rejected


def test_model_anchor_is_tier4_double_threshold_half_stake():
    c = engine.assess_contamination(anchor="model", venue_is_dfs=False,
                                    excluded_book=None, venue_book="underdog")
    assert c.tier == engine.TIER_MODEL_ANCHORED
    assert c.edge_mult == 2.0 and c.stake_mult == 0.5


# ---- soft-line evaluation --------------------------------------------------


def _tier1():
    return engine.assess_contamination(anchor="consensus", venue_is_dfs=True,
                                       excluded_book=None, venue_book="underdog")


def test_evaluate_soft_line_flags_positive_ev_side():
    cont = engine.assess_contamination(anchor="consensus", venue_is_dfs=False,
                                       excluded_book="fanduel", venue_book="fanduel")
    # p_true(over)=0.60; over priced 1.80 -> edge = 0.08 > 3% -> qualifies OVER.
    cand = engine.evaluate_soft_line(book="fanduel", market_key="points", line=24.5,
                                     over_price=1.80, under_price=2.00, p_true_over=0.60,
                                     contamination=cont, min_edge=0.03)
    assert cand.side == "OVER" and cand.qualifies and cand.edge == pytest.approx(0.08)


def test_evaluate_soft_line_rejects_contaminated_anchor():
    cont = engine.assess_contamination(anchor="consensus", venue_is_dfs=False,
                                       excluded_book=None, venue_book="fanduel")
    assert engine.evaluate_soft_line(book="fanduel", market_key="points", line=24.5,
                                     over_price=1.80, under_price=2.00, p_true_over=0.60,
                                     contamination=cont, min_edge=0.03) is None


def test_evaluate_soft_line_rejects_method_fragile_edge():
    cont = _tier1()
    assert engine.evaluate_soft_line(book="dk", market_key="points", line=24.5,
                                     over_price=1.80, under_price=2.00, p_true_over=0.60,
                                     contamination=cont, min_edge=0.03,
                                     method_spread=0.05, max_method_spread=0.02) is None


def test_evaluate_soft_line_drops_uncapped_extrapolation():
    cont = _tier1()
    assert engine.evaluate_soft_line(book="dk", market_key="points", line=24.5,
                                     over_price=1.80, under_price=2.00, p_true_over=0.60,
                                     contamination=cont, min_edge=0.03, within_cap=False) is None


def test_model_anchored_needs_double_edge():
    cont = engine.assess_contamination(anchor="model", venue_is_dfs=False,
                                       excluded_book=None, venue_book="underdog")
    # edge 0.04 clears 3% but NOT the doubled 6% model threshold.
    cand = engine.evaluate_soft_line(book="dk", market_key="rebounds", line=7.5,
                                     over_price=1.86, under_price=2.00, p_true_over=0.559,
                                     contamination=cont, min_edge=0.03)
    assert cand is not None and not cand.qualifies  # 0.04 < 0.06


# ---- DFS leg evaluation ----------------------------------------------------


def test_evaluate_dfs_leg_qualifies_above_breakeven_plus_margin():
    cont = _tier1()
    # 3-pick mult 6 breakeven 0.5503; p_true 0.62 > 0.5503+0.03 -> qualifies.
    cand = engine.evaluate_dfs_leg(book="underdog", market_key="points", line=18.5, side="OVER",
                                   p_true=0.62, mult=6.0, n_legs=3, contamination=cont, margin=0.03)
    assert cand.qualifies and cand.venue == "DFS" and cand.price is None


def test_evaluate_dfs_leg_demon_demands_more_edge():
    cont = _tier1()
    # p_true 0.59 clears standard 3-pick (0.5503+0.03=0.5803) but not demon (+0.02 -> 0.6003).
    std = engine.evaluate_dfs_leg(book="prizepicks", market_key="points", line=18.5, side="OVER",
                                  p_true=0.59, mult=6.0, n_legs=3, contamination=cont)
    dem = engine.evaluate_dfs_leg(book="prizepicks", market_key="points", line=18.5, side="OVER",
                                  p_true=0.59, mult=6.0, n_legs=3, contamination=cont,
                                  dfs_odds_type="demon")
    assert std.qualifies and not dem.qualifies


# ---- pinnacle audit (K6) ---------------------------------------------------


def test_audit_verdict_empty_runs_clean():
    v = engine.audit_verdict([])
    assert v["n"] == 0 and not v["kill"]


def test_audit_verdict_flags_systematic_bias():
    biases = [0.05, 0.045, 0.06, 0.055]  # consensus systematically over sharp
    v = engine.audit_verdict(biases)
    assert v["kill"] and v["mean_bias"] > engine.PINNACLE_BIAS_KILL


def test_audit_verdict_tolerates_noise():
    biases = [0.01, -0.015, 0.005, -0.01]  # noisy, centered near zero
    assert not engine.audit_verdict(biases)["kill"]


def test_pinnacle_bias_sign():
    assert engine.pinnacle_bias(0.60, 0.55) == pytest.approx(0.05)
