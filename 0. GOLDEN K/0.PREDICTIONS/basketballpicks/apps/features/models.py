"""Materialized ratings + player-form state (bball-01 §2 apps/features).

Team side: opponent-adjusted efficiency (pace / off_rtg / def_rtg) plus the
margin-Elo, one `TeamRating` row per (team, as_of_date, rating_type). Player
side: `PlayerForm` rolling state and `MinutesProjection` — the master prop
driver (bball-03 §4a). Everything is dated by information available BEFORE the
game (leakage guard, bball-03 §7c); the estimators that produce these values are
the pure-math `ratings.py` / `elo.py` modules.
"""

from django.db import models


class TeamRating(models.Model):
    """One rating value for a team as of a date. `rating_type` distinguishes the
    pace/efficiency channels (bball-03 §2b/2c) from the margin-Elo (§2c-ii); the
    ridge run stores off_rtg + def_rtg + pace on the same as_of_date so the core
    model reads one coherent snapshot."""

    TYPE_ELO = "elo_margin"  # margin-aware Elo (cold-start prior + ensemble member)
    TYPE_OFF = "off_rtg"  # opponent-adjusted offensive rating, pts / 100 poss
    TYPE_DEF = "def_rtg"  # opponent-adjusted defensive rating, pts allowed / 100
    TYPE_PACE = "pace"  # possessions / 48, opponent-adjustable tendency
    TYPE_CHOICES = [
        (TYPE_ELO, "margin elo"),
        (TYPE_OFF, "adjusted offensive rating"),
        (TYPE_DEF, "adjusted defensive rating"),
        (TYPE_PACE, "pace"),
    ]

    team = models.ForeignKey("core.Team", on_delete=models.CASCADE, related_name="ratings")
    as_of_date = models.DateField()
    rating_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=3)
    # league-average context the value is expressed against (pts/100 or pace),
    # so the core model can reconstruct absolute expectations without a second query.
    league_baseline = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    model_version = models.CharField(max_length=32, default="core-v1")
    extra = models.JSONField(default=dict, blank=True)  # e.g. {"hca": .., "n_games": ..}

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "as_of_date", "rating_type", "model_version"],
                name="uniq_team_rating_per_day",
            ),
        ]
        indexes = [models.Index(fields=["team", "rating_type", "as_of_date"])]

    def __str__(self) -> str:
        return f"{self.team_id} {self.rating_type}={self.value} @ {self.as_of_date}"


class PlayerForm(models.Model):
    """Rolling, decayed player state (bball-01 §2). `minutes_trend` is the role-
    change detector the minutes model leans on; averages are recency-weighted, not
    naive last-N (bball-03 §3 recent-form note)."""

    player = models.ForeignKey("core.Player", on_delete=models.CASCADE, related_name="forms")
    as_of_date = models.DateField()
    games_window = models.SmallIntegerField(default=10)
    minutes_avg = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    minutes_sd = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    minutes_trend = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    usage_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # USG%
    pts_per_min = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    reb_per_min = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    ast_per_min = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    tpm_per_min = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    # per-stat variance-to-mean ratios (overdispersion) the NB prop models need.
    vmr = models.JSONField(default=dict, blank=True)  # {"reb": 1.4, "ast": 1.3, ...}
    n_games = models.SmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "as_of_date", "games_window"], name="uniq_player_form"
            ),
        ]
        indexes = [models.Index(fields=["player", "-as_of_date"])]

    def __str__(self) -> str:
        return f"form {self.player_id} @ {self.as_of_date} ({self.games_window}g)"


class MinutesProjection(models.Model):
    """The master prop driver (bball-03 §4a): a minutes DISTRIBUTION, not a point.
    `p_active` carries injury/DNP risk; the mixture/blowout parameters live in
    `params` so the props chain reconstructs the full distribution. Lineup-state
    conditioned (which teammates are in) via `lineup_hash`."""

    SOURCE_MODEL = "model"
    SOURCE_MANUAL = "manual"
    SOURCE_VEGAS = "vegas_implied"

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="minutes_proj")
    player = models.ForeignKey("core.Player", on_delete=models.PROTECT, related_name="minutes_proj")
    proj_minutes = models.DecimalField(max_digits=6, decimal_places=2)  # distribution mean
    minutes_sd = models.DecimalField(max_digits=6, decimal_places=2, default=6)
    p_active = models.DecimalField(max_digits=5, decimal_places=4, default=1)  # P(not DNP)
    source = models.CharField(max_length=16, default=SOURCE_MODEL)
    lineup_hash = models.CharField(max_length=32, blank=True, default="")
    params = models.JSONField(default=dict, blank=True)  # blowout haircut, mixture weights
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "player", "source"], name="uniq_minutes_proj"
            ),
        ]
        indexes = [models.Index(fields=["game", "player"])]

    def __str__(self) -> str:
        return f"min {self.player_id} @ {self.game_id} = {self.proj_minutes}"


class FeatureSnapshot(models.Model):
    """Frozen feature vector at build time (leakage guard + reproducibility,
    bball-03 §7c). Game grain (team-model features) OR player grain (props
    features) — `player` null for the former."""

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="snapshots")
    player = models.ForeignKey(
        "core.Player", on_delete=models.CASCADE, related_name="snapshots", null=True, blank=True
    )
    feature_set_version = models.CharField(max_length=16)
    features = models.JSONField()
    completeness = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "player", "feature_set_version"], name="uniq_feature_snapshot"
            ),
        ]

    def __str__(self) -> str:
        grain = f"player {self.player_id}" if self.player_id else "team"
        return f"snapshot {self.feature_set_version} {grain} @ game {self.game_id}"
