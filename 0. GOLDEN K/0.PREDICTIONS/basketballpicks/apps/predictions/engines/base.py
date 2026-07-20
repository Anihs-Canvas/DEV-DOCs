"""Engine registry contract (bball-03 §7a; mirrors safepicks' one-engine-per-
family discipline). Each engine owns its ModelVersion row, its calibration slot
and its §5 calibrate-vs-noise verdict, so any family can be retrained or dropped
without touching the others.

`calibratable` encodes the bball-03 §5 map directly: rebounds/points/pra/assists/
spread/ml/total = True (enter the trusted pool once they clear the gate);
blocks/steals/threes/first-basket/thin-quarter = False (display / devig only,
never our own edge — the cards/BTTS analog). No ORM in the math paths.
"""


class MarketEngine:
    name: str = ""  # ModelVersion name, e.g. "player-v1"
    algo: str = ""
    family: str = ""  # human label / catalog key
    persists_predictions: bool = True
    calibratable: bool = False  # bball-03 §5 gate eligibility
    train_window: str = ""

    def model_version_defaults(self) -> dict:
        return {
            "algo": self.algo,
            "feature_set_version": "",
            "train_window": self.train_window,
            "is_active": False,  # promotion is a human gate decision, never a build side effect
            "metrics": {
                "family": self.family,
                "calibratable": self.calibratable,
                "persists_predictions": self.persists_predictions,
            },
        }

    def ensure_model_version(self):
        from apps.predictions.models import ModelVersion

        mv, _ = ModelVersion.objects.get_or_create(
            name=self.name, defaults=self.model_version_defaults()
        )
        return mv
