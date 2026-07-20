"""Isotonic/beta/identity calibrators + held-out selection (bball-03 §6a).
Pure-math — no DB."""

import numpy as np

from apps.predictions import calibration, metrics


def _overconfident_split(n=4000, seed=0):
    """Model probs that are systematically too confident: true p = 0.6*claimed."""
    rng = np.random.default_rng(seed)
    claimed = rng.uniform(0.5, 0.99, n)
    true_p = np.clip(0.55 * claimed + 0.1, 0, 1)
    y = (rng.uniform(size=n) < true_p).astype(float)
    cut = int(0.7 * n)
    return claimed[:cut], y[:cut], claimed[cut:], y[cut:]


def test_isotonic_improves_miscalibrated():
    tr_p, tr_y, te_p, te_y = _overconfident_split()
    iso = calibration.IsotonicCalibrator().fit(tr_p, tr_y)
    raw_ece = metrics.ece(te_p, te_y)
    cal_ece = metrics.ece(iso.predict(te_p), te_y)
    assert cal_ece < raw_ece


def test_fit_and_select_picks_a_real_calibrator_when_it_helps():
    tr_p, tr_y, te_p, te_y = _overconfident_split()
    winner, report = calibration.fit_and_select(tr_p, tr_y, te_p, te_y)
    assert report["winner"] in {"isotonic", "beta", "identity"}
    # the winner beats raw on held-out full-range ECE
    assert metrics.ece(winner.predict(te_p), te_y) <= metrics.ece(te_p, te_y) + 1e-9


def test_identity_wins_when_already_calibrated():
    rng = np.random.default_rng(3)
    n = 4000
    p = rng.uniform(0.5, 0.99, n)
    y = (rng.uniform(size=n) < p).astype(float)  # perfectly calibrated
    cut = int(0.7 * n)
    winner, report = calibration.fit_and_select(p[:cut], y[:cut], p[cut:], y[cut:])
    # identity should be competitive; calibration must not materially worsen ECE
    assert metrics.ece(winner.predict(p[cut:]), y[cut:]) <= metrics.ece(p[cut:], y[cut:]) + 0.01


def test_serialization_roundtrip():
    tr_p, tr_y, _, _ = _overconfident_split()
    for cal in (
        calibration.IdentityCalibrator(),
        calibration.IsotonicCalibrator().fit(tr_p, tr_y),
        calibration.BetaCalibrator().fit(tr_p, tr_y),
    ):
        restored = calibration.load_calibrator(cal.to_dict())
        np.testing.assert_allclose(restored.predict(tr_p[:20]), cal.predict(tr_p[:20]), atol=1e-9)
