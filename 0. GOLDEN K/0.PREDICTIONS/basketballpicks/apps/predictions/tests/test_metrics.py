"""Calibration metric suite: band-ECE/bias (ported) + CRPS/PIT (net-new,
bball-03 §6b). Pure-math — no DB."""

import numpy as np
import pytest

from apps.predictions import metrics


def test_band_bias_sign_and_scope():
    # claims 0.90 in-band, outcomes hit 0.70 -> +0.20 overconfident
    probs = np.array([0.90, 0.90, 0.90, 0.90, 0.90, 0.5])  # 0.5 is outside band
    outcomes = np.array([1.0, 0, 1, 0, 0, 1])
    bias, n = metrics.band_bias(probs, outcomes)
    assert n == 5
    assert bias == pytest.approx(0.90 - 0.4, abs=1e-9)


def test_brier_and_logloss():
    assert metrics.brier([1.0, 0.0], [1.0, 0.0]) == 0.0
    assert metrics.logloss([0.9, 0.1], [1, 0]) < metrics.logloss([0.6, 0.4], [1, 0])


def test_crps_gaussian_matches_ensemble():
    rng = np.random.default_rng(0)
    mu, sigma, y = 5.0, 12.0, 3.0
    closed = float(metrics.crps_gaussian(mu, sigma, y))
    samples = rng.normal(mu, sigma, 200000)
    approx = metrics.crps_ensemble(samples, y)
    assert approx == pytest.approx(closed, rel=0.02)


def test_crps_rewards_sharper_correct_forecast():
    # tighter sigma centered on truth scores better (lower CRPS)
    sharp = float(metrics.crps_gaussian(10, 8, 10))
    wide = float(metrics.crps_gaussian(10, 16, 10))
    assert sharp < wide


def test_pit_calibration_error_zero_for_uniform():
    pits = np.linspace(0, 1, 10000, endpoint=False) + 0.5 / 10000
    assert metrics.pit_calibration_error(pits, bins=10) == pytest.approx(0.0, abs=1e-3)


def test_pit_slope_detects_over_and_under_confidence():
    # U-shaped (mass at the ends) = OVERconfident -> positive slope
    u_shaped = np.concatenate([np.full(500, 0.02), np.full(500, 0.98)])
    assert metrics.pit_slope(u_shaped) > 0
    # humped (mass in the middle) = UNDERconfident -> negative slope
    humped = np.full(1000, 0.5)
    assert metrics.pit_slope(humped) < 0


def test_pit_histogram_shape():
    hist = metrics.pit_histogram(np.linspace(0, 1, 1000), bins=10)
    assert len(hist) == 10
    assert sum(b["n"] for b in hist) == 1000
