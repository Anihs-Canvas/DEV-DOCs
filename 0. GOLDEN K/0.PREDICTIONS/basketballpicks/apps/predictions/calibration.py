"""Probability calibrators (bball-03 §6a) — ported wholesale from safepicks.

Three candidates fit on the chronological first ~70% of walk-forward
predictions and judged on the held-out ~30% by band-ECE / band-bias; the winner
is selected per (league, market/line, side). IdentityCalibrator competes so
calibration can never make an already-honest market worse. Pure sklearn/numpy —
no ORM (fit-side commands own persistence; the served side loads the artifact).
"""

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

EPS = 1e-6


class IdentityCalibrator:
    """No-op candidate: calibration must never make things worse."""

    kind = "identity"

    def fit(self, probs, outcomes) -> "IdentityCalibrator":
        return self

    def predict(self, probs) -> np.ndarray:
        return np.asarray(probs, dtype=float)

    def to_dict(self) -> dict:
        return {"kind": self.kind}

    @classmethod
    def from_dict(cls, d: dict) -> "IdentityCalibrator":
        return cls()


class IsotonicCalibrator:
    kind = "isotonic"

    def __init__(self, x=None, y=None):
        self._x, self._y = x, y

    def fit(self, probs, outcomes) -> "IsotonicCalibrator":
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
        iso.fit(np.asarray(probs, dtype=float), np.asarray(outcomes, dtype=float))
        self._x = np.asarray(iso.X_thresholds_, dtype=float)
        self._y = np.asarray(iso.y_thresholds_, dtype=float)
        return self

    def predict(self, probs) -> np.ndarray:
        return np.interp(np.asarray(probs, dtype=float), self._x, self._y)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "x": self._x.tolist(), "y": self._y.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> "IsotonicCalibrator":
        return cls(np.asarray(d["x"], dtype=float), np.asarray(d["y"], dtype=float))


class BetaCalibrator:
    """Beta calibration (Kull et al. 2017): logistic on (ln p, -ln(1-p))."""

    kind = "beta"

    def __init__(self, a: float = 1.0, b: float = 1.0, c: float = 0.0):
        self.a, self.b, self.c = a, b, c

    @staticmethod
    def _features(probs) -> np.ndarray:
        p = np.clip(np.asarray(probs, dtype=float), EPS, 1 - EPS)
        return np.column_stack([np.log(p), -np.log(1.0 - p)])

    def fit(self, probs, outcomes) -> "BetaCalibrator":
        lr = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        lr.fit(self._features(probs), np.asarray(outcomes, dtype=float))
        self.a = float(lr.coef_[0][0])
        self.b = float(lr.coef_[0][1])
        self.c = float(lr.intercept_[0])
        return self

    def predict(self, probs) -> np.ndarray:
        z = self._features(probs) @ np.array([self.a, self.b]) + self.c
        return 1.0 / (1.0 + np.exp(-z))

    def to_dict(self) -> dict:
        return {"kind": self.kind, "a": self.a, "b": self.b, "c": self.c}

    @classmethod
    def from_dict(cls, d: dict) -> "BetaCalibrator":
        return cls(d["a"], d["b"], d["c"])


def load_calibrator(d: dict):
    if d["kind"] == "identity":
        return IdentityCalibrator.from_dict(d)
    if d["kind"] == "isotonic":
        return IsotonicCalibrator.from_dict(d)
    if d["kind"] == "beta":
        return BetaCalibrator.from_dict(d)
    raise ValueError(f"unknown calibrator kind: {d['kind']}")


def fit_and_select(train_probs, train_outcomes, test_probs, test_outcomes):
    """Fit all three; return (winner, report) by held-out band-ECE (falling back
    to full-range ECE when the band is empty)."""
    from apps.predictions.metrics import band_ece, ece

    candidates = {}
    for cal in (IdentityCalibrator(), IsotonicCalibrator(), BetaCalibrator()):
        cal.fit(train_probs, train_outcomes)
        calibrated = cal.predict(test_probs)
        b_ece, band_n = band_ece(calibrated, test_outcomes)
        candidates[cal.kind] = {
            "calibrator": cal,
            "band_ece": b_ece,
            "band_n": band_n,
            "full_ece": ece(calibrated, test_outcomes),
        }

    def score(entry: dict) -> float:
        return entry["band_ece"] if not np.isnan(entry["band_ece"]) else entry["full_ece"]

    winner_kind = min(candidates, key=lambda k: score(candidates[k]))
    report = {
        kind: {k: v for k, v in entry.items() if k != "calibrator"}
        for kind, entry in candidates.items()
    }
    return candidates[winner_kind]["calibrator"], {"winner": winner_kind, "candidates": report}
