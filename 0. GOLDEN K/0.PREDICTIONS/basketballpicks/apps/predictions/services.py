"""Persistence for the core + prop models (bball-03; mirrors safepicks'
services.py — engines are pure, services own the ORM writes, ADR 003).

`apps.core` is imported LAZILY inside the write functions: this module stays
importable during the parallel scaffold build (core lands from another agent),
and the pure-math engines it wraps have zero ORM dependency. Nothing here flips
`is_active` — promotion is a human review decision (bball-03 §7a).
"""

from apps.predictions.engines.prop_stats import StatDistribution
from apps.predictions.gaussian_core import CoreTeamModel, GameContext
from apps.predictions.models import ModelVersion, Prediction, PropPrediction
from apps.predictions.prop_calibration import CALIBRATABLE_MARKETS

CORE_MODEL_NAME = "core-v1"
PLAYER_MODEL_NAME = "player-v1"


def ensure_model_version(name: str, algo: str, **defaults) -> ModelVersion:
    """Get-or-create a registry row (is_active stays False unless a human sets
    it). Never overwrites an existing row's fields."""
    mv, _ = ModelVersion.objects.get_or_create(
        name=name,
        defaults={
            "algo": algo,
            "feature_set_version": defaults.get("feature_set_version", ""),
            "train_window": defaults.get("train_window", ""),
            "is_active": False,
            "metrics": defaults.get("metrics", {}),
        },
    )
    return mv


def ensure_core_model_version() -> ModelVersion:
    return ensure_model_version(
        CORE_MODEL_NAME, "ridge_gaussian", train_window="decayed ridge efficiency + margin-elo"
    )


def ensure_player_model_version() -> ModelVersion:
    return ensure_model_version(
        PLAYER_MODEL_NAME, "minutes_usage", train_window="minutes->usage->per-stat distribution"
    )


def persist_core_prediction(game_id: int, prob_vector: dict, model_version: ModelVersion) -> Prediction:
    """Upsert the one CORE Prediction row for a game/model. `prob_vector` carries
    the distribution block (source of truth) + the priced ladder."""
    obj, _ = Prediction.objects.update_or_create(
        game_id=game_id,
        model_version=model_version,
        market=Prediction.MARKET_CORE,
        defaults={"prob_vector": prob_vector},
    )
    return obj


def build_and_persist_core(
    ctx: GameContext, game_id: int, model: CoreTeamModel | None = None, model_version: ModelVersion | None = None
) -> Prediction:
    """Run core-v1 on a prepared GameContext and store the Prediction row.
    Callers assemble the GameContext from the features layer (ratings/pace/elo)
    as of a date strictly before tipoff."""
    model = model or CoreTeamModel()
    model_version = model_version or ensure_core_model_version()
    return persist_core_prediction(game_id, model.prob_vector(ctx), model_version)


def persist_prop_prediction(
    game_id: int,
    player_id: int,
    market_key: str,
    distribution: StatDistribution,
    proj_minutes: float,
    model_version: ModelVersion,
) -> PropPrediction:
    """Upsert one PropPrediction row from a materialized stat distribution. The
    §5 calibrate-vs-noise verdict is set from the market key: only the
    calibratable markets carry `calibration_gate=True` (the edge engine never
    trusts our point projection on noise markets)."""
    payload = distribution.materialize()
    obj, _ = PropPrediction.objects.update_or_create(
        game_id=game_id,
        player_id=player_id,
        market_key=market_key,
        model_version=model_version,
        defaults={
            "proj_minutes": round(float(proj_minutes), 2),
            "mean": round(distribution.mean(), 3),
            "dist": distribution.family,
            "dist_params": distribution.params,
            "pmf": payload["pmf"],
            "support_start": payload["support_start"],
            "calibration_gate": market_key in CALIBRATABLE_MARKETS,
        },
    )
    return obj
