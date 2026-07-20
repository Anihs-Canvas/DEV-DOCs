"""Pure tests for the props de-vig + line-shift repricer (apps.props.devig_engine)
and the soft-consensus builder (apps.props.consensus). No Django/DB."""


import pytest
from scipy import stats

from apps.props import consensus
from apps.props import devig_engine as de

# ---- (2a) native two-way de-vig -------------------------------------------


def test_fair_two_way_removes_vig_and_sums_to_one():
    f = de.fair_two_way(1.90, 1.95)
    assert f["p_over"] + f["p_under"] == pytest.approx(1.0)
    # both prices imply >0.5; the fair over is a touch under the raw implied.
    assert 0.48 < f["p_over"] < 0.53
    assert f["method_spread"] >= 0.0


def test_fair_two_way_reports_both_methods_for_sensitivity_screen():
    f = de.fair_two_way(1.50, 2.70)
    assert "p_over_shin" in f and "p_over_mult" in f
    assert f["method_spread"] == pytest.approx(abs(f["p_over_shin"] - f["p_over_mult"]))


def test_fair_two_way_rejects_bad_prices():
    assert de.fair_two_way(1.0, 2.0) == {}
    assert de.fair_two_way(None, 1.9) == {}


# ---- continuity ------------------------------------------------------------


def test_continuity_threshold():
    assert de.continuity_threshold(24.5) == 24.5  # over 24.5 == >=25 == >24.5
    assert de.continuity_threshold(24.0) == 24.5  # over 24 (integer) == >=25
    assert de.continuity_threshold(7.5) == 7.5
    assert de.continuity_threshold(7.0) == 7.5


# ---- (2b) CDF fit + reprice (the props-only wrinkle) ----------------------


def test_fit_cdf_recovers_known_normal_from_two_points():
    mu, sigma = 25.0, 8.0
    pts = [
        de.AnchorPoint(24.5, 1 - stats.norm.cdf((24.5 - mu) / sigma)),
        de.AnchorPoint(27.5, 1 - stats.norm.cdf((27.5 - mu) / sigma)),
    ]
    cdf = de.fit_cdf(pts, "points")
    assert cdf.mu == pytest.approx(mu, abs=0.05)
    assert cdf.sigma == pytest.approx(sigma, abs=0.05)
    assert not cdf.from_default_sigma


def test_single_point_uses_market_default_sigma():
    cdf = de.fit_cdf([de.AnchorPoint(24.5, 0.52)], "points")
    assert cdf.from_default_sigma
    assert cdf.sigma == de.DEFAULT_SIGMA["points"]
    # the single point is reproduced exactly
    assert cdf.p_over(24.5) == pytest.approx(0.52, abs=1e-6)


def test_reprice_flags_extrapolation_past_cap():
    mu, sigma = 25.0, 8.0
    pts = [de.AnchorPoint(24.5, 1 - stats.norm.cdf((24.5 - mu) / sigma)),
           de.AnchorPoint(27.5, 1 - stats.norm.cdf((27.5 - mu) / sigma))]
    cdf = de.fit_cdf(pts, "points")

    near = de.reprice(cdf, 26.0)   # 1.5 units from 27.5 -> within cap
    far = de.reprice(cdf, 21.5)    # 3.0 units from 24.5 -> past cap
    assert near.within_cap and far.within_cap is False
    assert far.reprice_units == pytest.approx(3.0)
    # repriced prob still matches the underlying Normal
    assert far.p_over == pytest.approx(1 - stats.norm.cdf((21.5 - mu) / sigma), abs=1e-6)


def test_dfs_vs_sharp_line_shift_produces_a_real_edge():
    # sharp says ~21.5 (p_over 0.50); DFS posts 18.5 -> repriced p_over should be
    # well above the 3-pick breakeven, the whole thesis of §2b.
    mu, sigma = 21.5, 8.0
    pts = [de.AnchorPoint(21.5, 0.50),
           de.AnchorPoint(24.5, 1 - stats.norm.cdf((24.5 - mu) / sigma))]
    cdf = de.fit_cdf(pts, "points")
    rp = de.reprice(cdf, 18.5)  # 3 units away -> uncapped, but shows the mechanism
    assert rp.p_over > 0.60


# ---- MODEL path (consume predictions.PropPrediction) -----------------------


def test_prob_over_from_pmf_materialized_ladder():
    # support_start=0, pmf over {0,1,2,3}; over 1.5 -> P(X in {2,3}).
    assert de.prob_over_from_pmf([0.1, 0.2, 0.3, 0.4], 0, 1.5) == pytest.approx(0.7)
    # support offset
    assert de.prob_over_from_pmf([0.5, 0.5], 5, 5.0) == pytest.approx(0.5)  # X in {5,6}; >5 -> {6}


def test_prob_over_from_dist_families():
    assert de.prob_over_from_dist("poisson", {"lam": 8.0}, 7.5) == pytest.approx(
        1 - stats.poisson.cdf(7, 8.0)
    )
    assert de.prob_over_from_dist("neg_binom", {"r": 5, "p": 0.4}, 7.5) == pytest.approx(
        1 - stats.nbinom.cdf(7, 5, 0.4)
    )
    assert de.prob_over_from_dist("normal", {"mu": 25, "sigma": 8}, 24.5) == pytest.approx(
        1 - stats.norm.cdf((24.5 - 25) / 8)
    )


def test_prob_over_from_dist_rejects_closed_form_less_family():
    with pytest.raises(ValueError):
        de.prob_over_from_dist("copula", {}, 20.0)


# ---- consensus builder + LEAVE-ONE-OUT guardrail ---------------------------


def _q(book, line, over, under, is_dfs=False):
    return consensus._Quote(book, line, over, under, is_dfs)


def test_consensus_needs_a_panel_and_excludes_dfs():
    # only a DFS quote -> no soft panel -> no consensus.
    res = consensus.build_consensus_at([_q("underdog", 24.5, None, None, is_dfs=True)],
                                       "points", 24.5)
    assert res.p_over is None and res.n_books == 0


def test_consensus_medians_multiple_books():
    quotes = [_q("draftkings", 24.5, 1.90, 1.95), _q("fanduel", 24.5, 1.87, 1.98),
              _q("bovada", 24.5, 1.91, 1.93)]
    res = consensus.build_consensus_at(quotes, "points", 24.5)
    assert res.n_books == 3 and 0.45 < res.p_over < 0.55
    assert res.within_cap


def test_leave_one_out_removes_the_graded_book():
    quotes = [_q("draftkings", 24.5, 1.90, 1.95), _q("fanduel", 24.5, 1.87, 1.98),
              _q("bovada", 24.5, 1.91, 1.93)]
    full = consensus.build_consensus_at(quotes, "points", 24.5)
    loo = consensus.build_consensus_at(quotes, "points", 24.5, exclude_book="draftkings")
    assert "draftkings" not in loo.books and full.n_books - 1 == loo.n_books
    assert loo.excluded_book == "draftkings"


def test_pinnacle_and_aggregates_never_enter_the_panel():
    quotes = [_q("pinnacle", 24.5, 1.90, 1.95), _q("market_max", 24.5, 2.0, 2.0),
              _q("draftkings", 24.5, 1.90, 1.95), _q("fanduel", 24.5, 1.88, 1.97)]
    res = consensus.build_consensus_at(quotes, "points", 24.5)
    assert set(res.books) == {"draftkings", "fanduel"}
