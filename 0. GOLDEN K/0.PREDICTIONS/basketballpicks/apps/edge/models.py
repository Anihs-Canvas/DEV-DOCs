"""edge — THE HERO PUBLISHER (devig + line-shop selection) [bball-01 §2].

Mirror of apps/safepicks/models.py, re-centered on DEVIG: the benchmark is the
sharp/consensus fair prob, NOT a model. The model (predictions.PropPrediction) is a
SECONDARY input used only on thin/neglected lines — we harvest bookmaker laziness,
we do not out-forecast the sharp price (bball-01 §6.2). Every candidate that fails a
gate writes NO row; the audit trail lives on the row that IS published + a JobRun.

Owns: RiskProfile, EdgeRule (the pre-registered per-cell gate), ProductionModel,
PipelineState (circuit breaker + ramp), EdgePick (the product row). FKs point at
props.PropLine / odds.OddsSnapshot / predictions.PropPrediction (string refs, no
import cycle).
"""

from django.db import models


class RiskProfile(models.Model):
    """Staking + exposure rails (safepicks RiskProfile, retuned for props/DFS).
    KELLY is primary because the durable venue is DFS pick'em, whose bet is a
    multiplier ENTRY, not a single price (bball-04 §3e)."""

    MODE_FLAT = "FLAT"
    MODE_KELLY = "KELLY"
    MODE_CHOICES = [(MODE_FLAT, "flat"), (MODE_KELLY, "kelly")]

    name = models.CharField(max_length=32, unique=True, default="default")
    staking_mode = models.CharField(max_length=8, choices=MODE_CHOICES, default=MODE_KELLY)
    flat_stake_pct = models.DecimalField(max_digits=6, decimal_places=4, default=0.01)
    kelly_fraction = models.DecimalField(max_digits=4, decimal_places=3, default=0.25)  # quarter
    max_stake_pct_bankroll = models.DecimalField(max_digits=5, decimal_places=4, default=0.02)
    min_edge = models.DecimalField(max_digits=6, decimal_places=4, default=0.03)  # EV vs fair
    # avoid longshots — props hold 6-10%
    max_prop_odds = models.DecimalField(max_digits=6, decimal_places=3, default=3.0)
    max_open_picks = models.PositiveSmallIntegerField(default=40)
    max_player_exposure_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0.03)
    max_game_exposure_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0.05)
    # DFS correlation rails (bball-04 §3c/§3e)
    dfs_max_legs = models.PositiveSmallIntegerField(default=6)
    dfs_max_correlated_legs = models.PositiveSmallIntegerField(default=2)
    dfs_max_slate_exposure_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0.10)
    slippage_haircut = models.DecimalField(max_digits=5, decimal_places=4, default=0.015)
    completeness_min = models.DecimalField(max_digits=4, decimal_places=3, default=0.80)
    circuit_breakers = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.staking_mode})"


class EdgeRule(models.Model):
    """Per (venue, prop_market, league_level) CELL — the pre-registered gate
    (bball-05 §4d). `enabled` earns ON only via forward CLV (a props mini-G1); ALL
    cells start DISABLED (bball-04 §6b). Thresholds are frozen constants moved only
    by a dated ADR — no goalpost-moving to rescue a dying cell (the soccer trap)."""

    VENUE_DFS = "DFS"
    VENUE_SOFTBOOK = "SOFTBOOK"
    VENUE_CHOICES = [(VENUE_DFS, "dfs pick'em"), (VENUE_SOFTBOOK, "soft sportsbook")]

    cell = models.CharField(max_length=16, unique=True)  # E1a ...
    venue = models.CharField(max_length=16, choices=VENUE_CHOICES)
    prop_market = models.ForeignKey(  # null => team-market cell
        "props.PropMarket", null=True, blank=True,
        on_delete=models.CASCADE, related_name="edge_rules",
    )
    league_level = models.CharField(max_length=16, default="NBA")  # NBA|WNBA|NCAAB|EURO
    min_edge = models.DecimalField(max_digits=6, decimal_places=4, default=0.03)
    min_devig_prob = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    dfs_margin = models.DecimalField(max_digits=5, decimal_places=4, default=0.03)
    book_whitelist = models.JSONField(default=list, blank=True)  # which soft books count
    # bball-06 §4c CONFIRM/KILL cell state, driven by the forward CLV_venue harness.
    STATE_DISABLED = "DISABLED"
    STATE_HOLD = "HOLD"
    STATE_CONFIRMED = "CONFIRMED"
    STATE_KILLED = "KILLED"
    STATE_CHOICES = [
        (STATE_DISABLED, "disabled at birth"),
        (STATE_HOLD, "paper-trading, deploy nothing"),
        (STATE_CONFIRMED, "forward-CLV confirmed"),
        (STATE_KILLED, "killed by the pre-registered criterion"),
    ]
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default=STATE_DISABLED)
    enabled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.cell} [{self.venue}/{self.league_level}] {self.state}"


class ProductionModel(models.Model):
    """family -> active model_version_name (safepicks verbatim). families =
    points_thin | reb | ast | wnba_* | euro_pir (bball-01 §2)."""

    family = models.CharField(max_length=32, unique=True)
    model_version_name = models.CharField(max_length=64)
    enabled = models.BooleanField(default=False)
    notes = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return f"{self.family} -> {self.model_version_name}"


class PipelineState(models.Model):
    """Circuit breaker + ramp (safepicks verbatim). One singleton-ish row the
    publisher checks before writing any pick."""

    STATE_RUNNING = "RUNNING"
    STATE_PAUSED = "PAUSED"
    STATE_TRIPPED = "TRIPPED"
    STATE_CHOICES = [
        (STATE_RUNNING, "running"),
        (STATE_PAUSED, "paused"),
        (STATE_TRIPPED, "circuit tripped"),
    ]

    name = models.CharField(max_length=32, unique=True, default="default")
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default=STATE_PAUSED)
    ramp_stage = models.CharField(max_length=16, default="paper")  # paper -> pilot -> full
    tripped_reason = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}:{self.state}@{self.ramp_stage}"


class EdgePick(models.Model):
    """One published +EV pick (the safepicks Pick analog). DEVIG-CENTRIC: the
    benchmark is `sharp_fair_prob`, not the model; `prop_prediction` is NULLABLE —
    a pure line-shop pick has no model. The anchor-contamination TIER (edge.engine)
    is stored on every row so the honesty harness can split realized ROI/CLV by how
    clean each pick's benchmark was."""

    # ---- what was taken ----
    prop_line = models.ForeignKey(
        "props.PropLine", null=True, blank=True, on_delete=models.PROTECT, related_name="edge_picks"
    )
    odds_snapshot = models.ForeignKey(
        "odds.OddsSnapshot", null=True, blank=True,
        on_delete=models.PROTECT, related_name="edge_picks",
    )
    prop_prediction = models.ForeignKey(  # only when the MODEL helped (thin line)
        "predictions.PropPrediction", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="edge_picks",
    )
    cell = models.CharField(max_length=16)  # EdgeRule.cell at publish
    venue = models.CharField(max_length=16)  # DFS | SOFTBOOK
    market_key = models.CharField(max_length=24)
    side = models.CharField(max_length=8)  # OVER | UNDER | HOME | YES
    line = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # ---- the devig benchmark + edge ----
    sharp_fair_prob = models.DecimalField(max_digits=6, decimal_places=5)  # p_true, taken side
    book_implied_devig = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    model_prob = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    edge = models.DecimalField(max_digits=7, decimal_places=5)  # price·fair − 1 (soft) / p−be (DFS)
    ev = models.DecimalField(max_digits=7, decimal_places=5)
    stake_fraction = models.DecimalField(max_digits=7, decimal_places=5, default=0)
    min_acceptable_price = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )

    # ---- anchor-contamination guardrail (bball-06 §7) ----
    anchor = models.CharField(max_length=16, default="consensus")  # consensus|pinnacle|model
    contamination_tier = models.PositiveSmallIntegerField(default=1)  # edge.engine tier 0-4
    excluded_book = models.CharField(max_length=32, blank=True)  # leave-one-out book
    pinnacle_audited = models.BooleanField(default=False)
    pinnacle_bias = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)

    # ---- lifecycle ----
    published_at = models.DateTimeField()
    expires_at = models.DateTimeField()  # tipoff
    STATUS_OPEN = "OPEN"
    STATUS_WON = "WON"
    STATUS_LOST = "LOST"
    STATUS_PUSH = "PUSH"
    STATUS_VOID = "VOID"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_RETRACTED = "RETRACTED"
    STATUS_CHOICES = [
        (STATUS_OPEN, "open"), (STATUS_WON, "won"), (STATUS_LOST, "lost"),
        (STATUS_PUSH, "push"), (STATUS_VOID, "void"), (STATUS_EXPIRED, "expired"),
        (STATUS_RETRACTED, "retracted"),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_OPEN)
    settled_at = models.DateTimeField(null=True, blank=True)
    audit = models.JSONField(default=dict, blank=True)  # full gate trail + devig inputs

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["prop_line", "cell"], name="uniq_edgepick_line_cell"),
        ]
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["-published_at"]),
            models.Index(fields=["contamination_tier", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.venue} {self.market_key} {self.side} {self.line} [{self.status}]"
