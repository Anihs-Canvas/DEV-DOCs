"""TEAM-market odds storage (bball-01 §2 apps/odds/models.py).

Player props are NOT here — they are first-class in apps/props (bball-01 §1: props
are the product, player-grained, two-sided, carry their own de-vig + settlement).
This app owns only TEAM markets (moneyline / spread / total) plus the shared
`Bookmaker` registry that PropLine also points at. OddsSnapshot is a near-copy of
safepicks' OddsSnapshot, re-scoped from Match to core.Game.
"""

from django.db import models


class Bookmaker(models.Model):
    """The book registry (bball-01 §2). Two flags matter for the props edge:

    * `is_sharp` — the de-vig ANCHOR set. Post the 2025-07-23 Pinnacle public-API
      shutdown (bball-06 §0) NO free tier serves a Pinnacle prop board, so in the
      $0 build the workhorse anchor is a soft-book CONSENSUS pseudo-book, not a
      single sharp book. Pinnacle survives only as a ~8-boards/mo OddsPapi AUDIT
      feed (bball-06 §1.D1) — flagged `is_sharp=True, is_audit_only=True`.
    * `is_dfs` — Underdog / PrizePicks / Pick6 pick'em: fixed-payout, no two-way
      price, EXCLUDED from odds-devig and handled on the line-difference / payout-
      multiplier path (bball-05 §1). Underdog classic advertises no limiting, so
      `limits_winners=False` — the durable venue (bball-04 §3d).
    """

    name = models.CharField(max_length=32, unique=True)
    is_sharp = models.BooleanField(default=False)  # pinnacle (audit-only free)
    is_dfs = models.BooleanField(default=False)  # underdog / prizepicks / pick6
    limits_winners = models.BooleanField(default=True)  # DK/FD/MGM=True; underdog=False
    is_aggregate = models.BooleanField(default=False)  # market_max / market_avg
    # A book that CONTRIBUTES to the soft-consensus anchor. The anchor-
    # contamination guardrail (bball-06 §7) leaves a book OUT of the consensus
    # when we are grading an edge against that same book (leave-one-out), so this
    # flag defines the consensus panel membership. DFS + audit books are never in.
    in_soft_consensus = models.BooleanField(default=False)
    is_audit_only = models.BooleanField(default=False)  # oddspapi Pinnacle: audit, never bet-vs

    def __str__(self) -> str:
        return self.name


class OddsSnapshot(models.Model):
    """One book's team-market quote at one instant. Live polling writes a REAL
    captured_at time SERIES per combo; the last pre-tip row per combo is flagged
    is_closing once tipoff passes (safepicks capture_closing_lines pattern)."""

    MARKET_ML = "ML"
    MARKET_SPREAD = "SPREAD"
    MARKET_TOTAL = "TOTAL"
    MARKET_CHOICES = [
        (MARKET_ML, "moneyline"),
        (MARKET_SPREAD, "point spread (line on row)"),
        (MARKET_TOTAL, "game total (line on row)"),
    ]

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="odds")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.PROTECT, related_name="odds")
    market = models.CharField(max_length=8, choices=MARKET_CHOICES)
    selection = models.CharField(max_length=8)  # HOME|AWAY | OVER|UNDER
    line = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    decimal_odds = models.DecimalField(max_digits=8, decimal_places=3)
    captured_at = models.DateTimeField()  # REAL capture time (the datum)
    is_closing = models.BooleanField(default=False)
    source = models.CharField(max_length=32, blank=True)
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "game",
                    "bookmaker",
                    "market",
                    "selection",
                    "line",
                    "is_closing",
                    "captured_at",
                ],
                name="uniq_team_odds_row",
            ),
        ]
        indexes = [
            models.Index(fields=["game", "market"]),
            models.Index(fields=["market", "is_closing"]),
            models.Index(fields=["game", "captured_at"]),
        ]

    def __str__(self) -> str:
        closing = "C" if self.is_closing else "-"
        return f"{self.game_id} {self.bookmaker.name} {self.market} {self.selection} {closing}"
