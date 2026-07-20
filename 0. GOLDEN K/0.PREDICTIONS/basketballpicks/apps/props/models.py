"""apps/props — THE differentiator data app (bball-01 §1/§2).

Player props are split OUT of odds/predictions because they ARE the product: they
are player-grained, natively two-sided (over AND under on ONE row), high-cardinality
(200-400 lines/night), and carry their own de-vig + settlement. This module owns
PropMarket (the market catalogue), PropLine (the two-sided, DFS-aware snapshot) and
PropConsensus (the devigged sharp-fair anchor).

CONTRACT: this app does NOT define PropPrediction — the minutes→usage→per-stat model
output lives in apps.predictions (bball-03, Agent 3) and is CONSUMED by apps.edge.
FK identity comes from apps.core (Game, Player); we never mutate a core row.
"""

from django.db import models


class PropMarket(models.Model):
    """Catalogue of prop market TYPES. `settle_expr` maps a market to
    PlayerBoxScore columns (grading is one grader over this expr, never a per-
    market reimplementation — bball-05 §3b). `stat_family` picks the CDF family
    the repricer fits: count → Neg-Binom/Poisson, continuous → (skew-)Normal,
    yesno → binary (bball-04 §2b)."""

    FAMILY_COUNT = "count"
    FAMILY_CONTINUOUS = "continuous"
    FAMILY_YESNO = "yesno"
    FAMILY_CHOICES = [
        (FAMILY_COUNT, "low-count / right-skew"),
        (FAMILY_CONTINUOUS, "continuous-ish (CLT)"),
        (FAMILY_YESNO, "binary yes/no"),
    ]

    key = models.CharField(max_length=24, unique=True)  # PTS|REB|AST|PRA|THREES|...
    label = models.CharField(max_length=48)
    settle_expr = models.CharField(max_length=64)  # "pts" | "pts+reb+ast" | "dd(...)"
    stat_family = models.CharField(max_length=16, choices=FAMILY_CHOICES, default=FAMILY_CONTINUOUS)
    is_combo = models.BooleanField(default=False)  # PRA / PR / ...
    # bball-03 §5 map: blocks/steals/threes/first_basket are variance-dominated /
    # anti-predictive — devig-or-display only, NEVER a model-edge claim.
    model_edge_allowed = models.BooleanField(default=True)
    default_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.key


class PropLine(models.Model):
    """One book's TWO-SIDED quote for one player's one market at one instant.

    Differs from odds.OddsSnapshot's one-selection-per-row: props are two-way, so
    over AND under prices sit on ONE row. DFS pick'em legs carry payout_mult and
    leave the prices NULL (a pick'em leg has no two-way price — bball-05 §1). Live
    polling writes a REAL captured_at time series per combo; the last pre-tip row
    per combo is flagged is_closing once tipoff passes."""

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="prop_lines")
    player = models.ForeignKey("core.Player", on_delete=models.PROTECT, related_name="prop_lines")
    market = models.ForeignKey(PropMarket, on_delete=models.PROTECT, related_name="lines")
    bookmaker = models.ForeignKey(
        "odds.Bookmaker", on_delete=models.PROTECT, related_name="prop_lines"
    )
    line = models.DecimalField(max_digits=6, decimal_places=2)  # 24.5
    over_price = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    under_price = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    payout_mult = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)  # DFS
    dfs_odds_type = models.CharField(max_length=12, blank=True)  # standard|demon|goblin
    is_closing = models.BooleanField(default=False)
    captured_at = models.DateTimeField()
    source = models.CharField(max_length=32)  # sportsgameodds|bovada|the_odds_api|underdog|...
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "game",
                    "player",
                    "market",
                    "bookmaker",
                    "line",
                    "is_closing",
                    "captured_at",
                ],
                name="uniq_prop_line_row",
            ),
        ]
        indexes = [
            models.Index(fields=["game", "market"]),
            models.Index(fields=["player", "-captured_at"]),
            models.Index(fields=["market", "is_closing"]),
        ]

    def __str__(self) -> str:
        return f"{self.player_id} {self.market_id} {self.line} @{self.bookmaker_id}"


class PropConsensus(models.Model):
    """Devigged SHARP-fair prob per (game,player,market,line) — the line-shop
    benchmark. `anchor` records WHICH source supplied p_fair:

      * "consensus" — the soft-book CONSENSUS pseudo-book (bball-06 §1.D2), the
        workhorse in the $0 build (Pinnacle is gone). This is the CONTAMINATION-
        prone anchor: it is a de-vig of the same soft market we grade against.
      * "pinnacle" — the rare OddsPapi audit pull (bball-06 §1.D1), independent
        sharp truth. Coverage is split per anchor so a consensus-only stretch is
        read as COVERAGE, not efficiency (the bball-05 §2d honesty trap).

    `excluded_book` records the leave-one-out book removed from the consensus when
    this row anchors an edge against that same book (the structural guardrail)."""

    ANCHOR_CONSENSUS = "consensus"
    ANCHOR_PINNACLE = "pinnacle"

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="prop_consensus")
    player = models.ForeignKey(
        "core.Player", on_delete=models.PROTECT, related_name="prop_consensus"
    )
    market = models.ForeignKey(PropMarket, on_delete=models.PROTECT)
    line = models.DecimalField(max_digits=6, decimal_places=2)
    fair_prob_over = models.DecimalField(max_digits=6, decimal_places=5)
    method = models.CharField(max_length=16, default="shin")  # shin|multiplicative
    anchor = models.CharField(max_length=16, default=ANCHOR_CONSENSUS)
    n_books = models.PositiveSmallIntegerField(default=0)  # panel size behind the median
    excluded_book = models.CharField(max_length=32, blank=True)  # leave-one-out guardrail
    # method-sensitivity: |shin_p − mult_p|; a wide gap => the edge is method-
    # fragile and must not be trusted (bball-04 §2a).
    method_spread = models.DecimalField(max_digits=6, decimal_places=5, default=0)
    is_closing = models.BooleanField(default=False)
    captured_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "player", "market", "line", "anchor", "excluded_book",
                        "is_closing", "captured_at"],
                name="uniq_prop_consensus_row",
            ),
        ]
        indexes = [
            models.Index(fields=["game", "market"]),
            models.Index(fields=["anchor", "is_closing"]),
        ]

    def __str__(self) -> str:
        return f"{self.player_id} {self.market_id} {self.line} [{self.anchor}]"
