"""Model registry + probability/distribution store (bball-03 §7a; mirrors
safepicks ModelVersion/Prediction, extended for basketball's distributions).

Three tables, all owned here (per the core-model contract):

* ModelVersion — named, champion/challenger registry row (core-v1, elo-v1,
  stack-v1, blend-v1, player-v1). `is_active` flips ONLY on human promotion
  review (bball-03 §7a) — never as a build side effect.
* Prediction — one CORE row per game carrying the margin+total DISTRIBUTION
  params (the source of truth from which any spread/total/team-total on the
  ladder is priced, bball-03 §2e) plus the derived market prob vector.
* PropPrediction — the player layer (bball-03 §4): minutes -> usage -> per-stat
  DISTRIBUTION, stored as params + a materialized pmf so downstream consumers
  (apps.edge / apps.props devig engine) can price ANY line/alt-line WITHOUT
  re-instantiating the model. `market_key` is a stable string
  (points|rebounds|assists|pra|...) that matches props.PropMarket.key — a
  deliberate decouple so this app carries no hard FK into the props app.
"""

from django.db import models


class ModelVersion(models.Model):
    """One named model generation (bball-03 §7a). Carries algo + feature-set +
    train window + held-out metrics + artifact pointer. `is_active` is a human
    promotion decision only."""

    name = models.CharField(max_length=64, unique=True)  # core-v1 | elo-v1 | player-v1 ...
    algo = models.CharField(max_length=32)  # ridge_gaussian | elo | gbm_stack | minutes_usage ...
    feature_set_version = models.CharField(max_length=16, blank=True, default="")
    trained_at = models.DateTimeField(auto_now_add=True)
    train_window = models.CharField(max_length=64, blank=True, default="")
    # logloss, brier, band_ece, band_bias, CRPS, PIT-uniformity — the §6 suite
    metrics = models.JSONField(default=dict, blank=True)
    artifact_uri = models.CharField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.algo}){' *' if self.is_active else ''}"


class Prediction(models.Model):
    """One team-model row per (game, model_version). `prob_vector` holds BOTH the
    predictive distribution params under `dist` (mu/sigma for margin & total,
    family, dof/skew) AND the derived market probabilities — so the row alone
    prices the whole spread/total/team-total ladder (bball-03 §2e).

    Canonical prob_vector shape (core-v1):
      {
        "dist": {"margin": {"mu":.., "sigma":.., "family":"normal|t|skewnorm",
                            "dof":.., "skew":..},
                 "total":  {"mu":.., "sigma":.., "family":..},
                 "team_total": {"home_sigma":.., "away_sigma":..}},
        "ML":     {"HOME":p, "AWAY":p},
        "SPREAD": {"line": -4.5, "HOME": p_cover, "AWAY": 1-p_cover},
        "TOTAL":  {"line": 224.5, "OVER": p, "UNDER": 1-p},
        "TEAM_TOTAL": {"HOME": {"line":.., "OVER":p}, "AWAY": {...}},
        "meta": {"model":"core-v1", "sigma_widened": bool, "ensemble": {...}}
      }
    Downstream re-prices any other line off `dist` directly.
    """

    MARKET_CORE = "CORE"

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="predictions")
    model_version = models.ForeignKey(
        ModelVersion, on_delete=models.CASCADE, related_name="predictions"
    )
    market = models.CharField(max_length=16, default=MARKET_CORE)
    prob_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "model_version", "market"], name="uniq_prediction"
            ),
        ]
        indexes = [models.Index(fields=["game", "market"])]

    def __str__(self) -> str:
        return f"{self.model_version_id}:{self.market} for game {self.game_id}"


class PropPrediction(models.Model):
    """The player layer (bball-03 §4). One row per (game, player, market_key,
    model_version) carrying the projected minutes (the master driver), the stat
    distribution family + params, and a materialized pmf/support so any line is
    priceable downstream without this app's code.

    `dist_params` families (bball-03 §4c):
      neg_binom  {"r":.., "p":..}                 rebounds, assists
      poisson    {"lam":..}                        blocks/steals (noise — devig only)
      compound   {"lam2":.., "lam3":.., "lamft":..} points (2P/3P/FT convolution)
      normal     {"mu":.., "sigma":..}             minutes-like / continuous
      copula     {"marginals":[...], "corr":[[...]]} PRA / P+R / combos

    `pmf` + `support_start`: P(X = support_start + i) = pmf[i]. A consumer prices
    over/under any line L as  P(X > L) = sum(pmf[i] for support_start+i > L).
    `calibration_gate` records whether this market cleared the §5 calibrate-vs-
    noise gate (rebounds/points/PRA/assists = trusted; blocks/steals/threes/
    first-basket = display/devig-only — never our own edge).
    """

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="prop_predictions")
    player = models.ForeignKey(
        "core.Player", on_delete=models.PROTECT, related_name="prop_predictions"
    )
    market_key = models.CharField(max_length=24)  # matches props.PropMarket.key
    model_version = models.ForeignKey(
        ModelVersion, on_delete=models.PROTECT, related_name="prop_predictions"
    )
    proj_minutes = models.DecimalField(max_digits=6, decimal_places=2)  # master driver
    mean = models.DecimalField(max_digits=7, decimal_places=3)  # projected stat mean
    dist = models.CharField(max_length=16, default="neg_binom")
    dist_params = models.JSONField(default=dict)
    pmf = models.JSONField(default=list, blank=True)  # materialized ladder (counting stats)
    support_start = models.SmallIntegerField(default=0)
    # §5 map: True only for markets that cleared the calibration gate. Noise
    # markets are stored (for devig display) but flagged so the edge engine never
    # trusts our point projection as an edge.
    calibration_gate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "player", "market_key", "model_version"],
                name="uniq_prop_prediction",
            ),
        ]
        indexes = [
            models.Index(fields=["game", "market_key"]),
            models.Index(fields=["player", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.market_key} {self.player_id} @ game {self.game_id} mean={self.mean}"
