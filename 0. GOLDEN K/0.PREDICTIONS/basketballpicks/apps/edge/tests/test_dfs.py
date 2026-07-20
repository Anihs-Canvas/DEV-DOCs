"""Pure tests for the DFS pick'em math (apps.edge.dfs) — validated against the
bball-04 §3 worked numbers. Runs with plain pytest, no Django/DB."""


import pytest

from apps.edge import dfs


def test_breakeven_matches_memo_table():
    # bball-04 §3a: UD 2/3/4/5-pick breakevens.
    assert dfs.breakeven_per_leg(3.0, 2) == pytest.approx(0.5774, abs=1e-4)
    assert dfs.breakeven_per_leg(6.0, 3) == pytest.approx(0.5503, abs=1e-4)
    assert dfs.breakeven_per_leg(10.0, 4) == pytest.approx(0.5623, abs=1e-4)
    assert dfs.breakeven_per_leg(20.0, 5) == pytest.approx(0.5493, abs=1e-4)


def test_odd_leg_power_plays_have_lowest_breakevens():
    # 3-pick (0.5503) and 5-pick (0.5493) beat 2-pick (0.5774) and 4-pick (0.5623).
    assert dfs.breakeven_per_leg(6.0, 3) < dfs.breakeven_per_leg(3.0, 2)
    assert dfs.breakeven_per_leg(20.0, 5) < dfs.breakeven_per_leg(10.0, 4)


def test_bernoulli_joint_reproduces_memo_worked_example():
    # p1=p2=0.58: rho 0.0/0.10/0.20 -> P 0.336/0.361/0.385 (bball-04 §3c).
    assert dfs.joint_all_hit_bernoulli(0.58, 0.58, 0.00) == pytest.approx(0.3364, abs=1e-3)
    assert dfs.joint_all_hit_bernoulli(0.58, 0.58, 0.10) == pytest.approx(0.3608, abs=1e-3)
    assert dfs.joint_all_hit_bernoulli(0.58, 0.58, 0.20) == pytest.approx(0.3851, abs=1e-3)


def test_entry_ev_power_matches_memo():
    # EV = P_joint*M - 1 at M=3. rho=0 -> +0.9%, rho=0.10 -> +8.2%.
    assert dfs.entry_ev_power([0.58, 0.58], 3.0, rho=0.0)["ev"] == pytest.approx(0.009, abs=2e-3)
    assert dfs.entry_ev_power([0.58, 0.58], 3.0, rho=0.10)["ev"] == pytest.approx(0.082, abs=2e-3)


def test_rho_is_hard_capped_at_015():
    # joint_all_hit must never credit above RHO_CAP even if asked for 0.20.
    capped = dfs.joint_all_hit([0.58, 0.58], rho=0.20)
    at_cap = dfs.joint_all_hit_bernoulli(0.58, 0.58, dfs.RHO_CAP)
    assert capped == pytest.approx(at_cap, abs=1e-9)


def test_positive_correlation_beats_line_edge():
    # the memo's headline (bball-04 §3c): a +0.9% line-only 2-pick (p=0.58) becomes
    # +8.2% at rho=0.10 — the correlation increment EXCEEDS the line edge itself.
    ev0 = dfs.entry_ev_power([0.58, 0.58], 3.0, rho=0.0)["ev"]      # ~+0.9%
    ev_corr = dfs.entry_ev_power([0.58, 0.58], 3.0, rho=0.10)["ev"]  # ~+8.2%
    assert ev0 > 0 and (ev_corr - ev0) > ev0


def test_negative_correlation_lowers_all_hit():
    assert dfs.joint_all_hit([0.6, 0.6], rho=-0.2) < dfs.joint_all_hit([0.6, 0.6], rho=0.0)


def test_gaussian_copula_3leg_between_independent_and_perfect():
    indep = 0.6**3
    j = dfs.joint_all_hit([0.6, 0.6, 0.6], rho=0.15)
    assert indep < j < 0.6  # correlated all-hit exceeds independence, below min marginal


def test_poisson_binomial_pmf_exact():
    pmf = dfs.poisson_binomial_pmf([0.5, 0.5])
    assert list(pmf) == pytest.approx([0.25, 0.5, 0.25])
    assert dfs.poisson_binomial_pmf([0.6, 0.7, 0.8]).sum() == pytest.approx(1.0)


def test_count_dist_independent_equals_poisson_binomial():
    p = [0.55, 0.6, 0.65]
    ind = dfs.count_dist(p, rho=0.0)
    assert ind == pytest.approx(dfs.poisson_binomial_pmf(p))


def test_count_dist_correlated_is_reproducible_and_normalized():
    p = [0.55, 0.6, 0.65]
    a = dfs.count_dist(p, rho=0.15, seed=1)
    b = dfs.count_dist(p, rho=0.15, seed=1)
    assert a == pytest.approx(b)  # seeded → reproducible
    assert a.sum() == pytest.approx(1.0)


def test_flex_ev_uses_full_distribution():
    # a 3-leg flex paying 2.25x on 3/3 and 1.25x on 2/3 (illustrative).
    res = dfs.entry_ev_flex([0.6, 0.6, 0.6], {3: 2.25, 2: 1.25}, rho=0.0)
    pmf = dfs.poisson_binomial_pmf([0.6, 0.6, 0.6])
    expected = pmf[3] * 2.25 + pmf[2] * 1.25 - 1.0
    assert res["ev"] == pytest.approx(expected, abs=1e-9)


def test_quarter_kelly_entry_audit_shape():
    a = dfs.quarter_kelly_entry(p_joint=0.40, mult=3.0, kelly_multiplier=0.25, stake_cap_pct=0.02)
    full = (0.40 * 3.0 - 1.0) / (3.0 - 1.0)  # 0.10
    assert a["kelly_full"] == pytest.approx(full)
    assert a["kelly_scaled"] == pytest.approx(full * 0.25)
    assert a["stake_fraction"] == pytest.approx(min(full * 0.25, 0.02))
    assert set(a) == {"kelly_full", "kelly_multiplier", "kelly_scaled", "stake_cap_pct",
                      "cap_bound", "stake_fraction"}


def test_quarter_kelly_floors_at_zero_for_negative_ev():
    a = dfs.quarter_kelly_entry(p_joint=0.30, mult=3.0, kelly_multiplier=0.25, stake_cap_pct=0.02)
    assert a["stake_fraction"] == 0.0  # p*M-1 = -0.1 < 0 -> full kelly floored at 0


def test_slate_cap_scales_shared_leg_exposure_down():
    entries = [
        {"stake_fraction": 0.04, "legs": {"a", "b"}},
        {"stake_fraction": 0.05, "legs": {"b", "c"}},
    ]
    out = dfs.slate_exposure_cap(entries, max_aggregate_pct=0.06)
    assert out["capped_total"] == pytest.approx(0.06)
    assert out["scale_applied"] == pytest.approx(0.06 / 0.09)
    # leg "b" appears in both entries → its exposure accumulates
    assert out["leg_exposure"]["b"] > out["leg_exposure"]["a"]


def test_slate_cap_noop_when_under_budget():
    entries = [{"stake_fraction": 0.01, "legs": {"a"}}]
    out = dfs.slate_exposure_cap(entries, max_aggregate_pct=0.10)
    assert out["scale_applied"] == 1.0
