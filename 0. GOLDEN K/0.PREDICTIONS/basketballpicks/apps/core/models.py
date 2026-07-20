"""Core domain — reference entities, schedule + results, and the PLAYER-FIRST
box-score grain that is basketballpicks' whole reason to exist [bball-01 §2].

THE CONTRACT. Every other app imports from here:

    from apps.core.models import (
        League, Team, Player, Game, TeamBoxScore, PlayerBoxScore,
    )

Conventions carried from safepicks:
* DecimalField for anything money/odds/minutes-shaped; PositiveSmallInt for
  counting stats.
* everything UTC.
* the verbatim source row is retained in `raw` for re-parsing.
* cross-source identity via *SourceRef / *Alias (never mutate another
  source's row — ADR 007); those live in apps/ingestion/models.py, the
  name-resolution aliases live here alongside the entities they resolve.
"""

from django.db import models


class League(models.Model):
    """A competition we ingest (NBA, WNBA, NCAAB, EURO, ...)."""

    code = models.CharField(max_length=16, unique=True)  # NBA, WNBA, NCAAB, EURO
    name = models.CharField(max_length=64)
    level = models.CharField(max_length=16)  # pro | college | intl
    # {nba_api: "00", odds_api: "basketball_nba", ...} — never the identity,
    # just cross-source hints (identity is `code`).
    source_ids = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Season(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="seasons")
    name = models.CharField(max_length=16)  # "2025-26"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["league", "name"], name="uniq_season_per_league"),
        ]

    def __str__(self) -> str:
        return f"{self.league.code} {self.name}"


class Team(models.Model):
    canonical_name = models.CharField(max_length=64)
    abbreviation = models.CharField(max_length=8)  # LAL, BOS, ...
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    conference = models.CharField(max_length=16, blank=True)  # East|West (blank college/intl)
    division = models.CharField(max_length=24, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["canonical_name", "league"], name="uniq_team_name_per_league"
            ),
        ]

    def __str__(self) -> str:
        return self.canonical_name


class TeamAlias(models.Model):
    """Cross-source name resolution [ADR 007]. The admin list filtered on
    status=pending IS the manual review queue (mirrors safepicks TeamAlias)."""

    STATUS_AUTO = "auto"
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CHOICES = [
        (STATUS_AUTO, "auto"),
        (STATUS_PENDING, "pending review"),
        (STATUS_CONFIRMED, "confirmed"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="aliases")
    source = models.CharField(max_length=32)  # "nba_api", "odds_api", ...
    alias_name = models.CharField(max_length=64)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_AUTO)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "team aliases"
        constraints = [
            models.UniqueConstraint(
                fields=["source", "alias_name", "team"], name="uniq_team_alias_per_source_team"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source}:{self.alias_name} -> {self.team.canonical_name}"


class Player(models.Model):
    """FIRST-CLASS (soccer had none). The high-cardinality core: props are
    player-grained and the box-score minutes/usage grain drives everything."""

    STATUS_ACTIVE = "active"
    STATUS_TWO_WAY = "two_way"
    STATUS_TEN_DAY = "10day"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_TWO_WAY, "two-way"),
        (STATUS_TEN_DAY, "10-day"),
        (STATUS_INACTIVE, "inactive"),
    ]

    canonical_name = models.CharField(max_length=80)
    current_team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="roster"
    )
    primary_position = models.CharField(max_length=4, blank=True)  # G|F|C|G-F...
    birthdate = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    source_ids = models.JSONField(default=dict, blank=True)  # {nba_api: 2544, ...}

    class Meta:
        constraints = [
            # NULL current_team is treated as distinct by Postgres, so free
            # agents / unresolved names never collide; the PlayerAlias table
            # (below) carries the cross-source id resolution.
            models.UniqueConstraint(
                fields=["canonical_name", "current_team"], name="uniq_player_name_per_team"
            ),
        ]
        indexes = [models.Index(fields=["canonical_name"])]

    def __str__(self) -> str:
        return self.canonical_name


class PlayerAlias(models.Model):
    """Cross-source player-name resolution — mirrors TeamAlias."""

    STATUS_AUTO = "auto"
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CHOICES = [
        (STATUS_AUTO, "auto"),
        (STATUS_PENDING, "pending review"),
        (STATUS_CONFIRMED, "confirmed"),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="aliases")
    source = models.CharField(max_length=32)
    alias_name = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_AUTO)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "player aliases"
        constraints = [
            models.UniqueConstraint(
                fields=["source", "alias_name", "player"],
                name="uniq_player_alias_per_source_player",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source}:{self.alias_name} -> {self.player.canonical_name}"


class Game(models.Model):
    """The Match analog — schedule + status + home/away scores."""

    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_LIVE = "LIVE"  # in-play
    STATUS_FINAL = "FINAL"
    STATUS_POSTPONED = "PP"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "scheduled"),
        (STATUS_LIVE, "live"),
        (STATUS_FINAL, "final"),
        (STATUS_POSTPONED, "postponed"),
    ]

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="games")
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_games")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_games")
    tipoff_utc = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    period_scores = models.JSONField(default=dict, blank=True)  # {"Q":[..], "OT":[..]}
    num_ot = models.PositiveSmallIntegerField(default=0)  # OT changes prop-minutes math
    venue = models.CharField(max_length=64, blank=True)
    home_rest_days = models.SmallIntegerField(null=True, blank=True)  # B2B flag input
    away_rest_days = models.SmallIntegerField(null=True, blank=True)
    pace = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # poss/48
    source = models.CharField(max_length=32)
    external_id = models.CharField(max_length=128)
    raw = models.JSONField(default=dict, blank=True)  # verbatim source row

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="uniq_game_source_id"),
        ]
        indexes = [
            models.Index(fields=["tipoff_utc"]),
            models.Index(fields=["season", "tipoff_utc"]),
            models.Index(fields=["status", "tipoff_utc"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.away_team.abbreviation} @ {self.home_team.abbreviation} "
            f"({self.tipoff_utc:%Y-%m-%d})"
        )


class TeamBoxScore(models.Model):
    """Per-team final line for one game."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="team_boxscores")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="team_boxscores")
    is_home = models.BooleanField()

    pts = models.PositiveSmallIntegerField(default=0)
    reb = models.PositiveSmallIntegerField(default=0)
    ast = models.PositiveSmallIntegerField(default=0)
    stl = models.PositiveSmallIntegerField(default=0)
    blk = models.PositiveSmallIntegerField(default=0)
    tov = models.PositiveSmallIntegerField(default=0)
    pf = models.PositiveSmallIntegerField(default=0)

    fgm = models.PositiveSmallIntegerField(default=0)
    fga = models.PositiveSmallIntegerField(default=0)
    tpm = models.PositiveSmallIntegerField(default=0)  # three-pointers made
    tpa = models.PositiveSmallIntegerField(default=0)
    ftm = models.PositiveSmallIntegerField(default=0)
    fta = models.PositiveSmallIntegerField(default=0)

    minutes = models.DecimalField(max_digits=6, decimal_places=1)  # 240 (+25/OT)
    pace = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    off_rtg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    def_rtg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["game", "team"], name="uniq_team_boxscore"),
        ]
        indexes = [models.Index(fields=["team", "-game_id"])]

    def __str__(self) -> str:
        return f"{self.team.abbreviation} {self.pts} (game {self.game_id})"


class PlayerBoxScore(models.Model):
    """*** THE differentiator table *** — minutes/usage grain per player-game.

    `minutes` is the master prop driver; `usage_rate` is the injury-cascade
    signal. Combos (PRA / PR / PA / RA / double-double) are DERIVED from these
    columns at settle time (props.settle), never stored — one source of truth.
    A DNP row is minutes=0 / dnp=True with zeroed counting stats.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player_boxscores")
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="boxscores")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="player_boxscores")
    started = models.BooleanField(default=False)
    dnp = models.BooleanField(default=False)  # DNP-CD / inactive
    minutes = models.DecimalField(max_digits=6, decimal_places=2)  # 34.50 — master driver

    pts = models.PositiveSmallIntegerField(default=0)
    oreb = models.PositiveSmallIntegerField(default=0)
    dreb = models.PositiveSmallIntegerField(default=0)
    reb = models.PositiveSmallIntegerField(default=0)
    ast = models.PositiveSmallIntegerField(default=0)
    stl = models.PositiveSmallIntegerField(default=0)
    blk = models.PositiveSmallIntegerField(default=0)
    tov = models.PositiveSmallIntegerField(default=0)
    pf = models.PositiveSmallIntegerField(default=0)

    fgm = models.PositiveSmallIntegerField(default=0)
    fga = models.PositiveSmallIntegerField(default=0)
    tpm = models.PositiveSmallIntegerField(default=0)  # three-pointers made
    tpa = models.PositiveSmallIntegerField(default=0)
    ftm = models.PositiveSmallIntegerField(default=0)
    fta = models.PositiveSmallIntegerField(default=0)

    plus_minus = models.SmallIntegerField(null=True, blank=True)
    usage_rate = models.DecimalField(  # USG% — the cascade signal
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["game", "player"], name="uniq_player_boxscore"),
        ]
        indexes = [
            models.Index(fields=["player", "-game_id"]),
            models.Index(fields=["game", "team"]),
        ]

    def __str__(self) -> str:
        return f"{self.player.canonical_name} {self.pts}p/{self.reb}r/{self.ast}a (game {self.game_id})"


class PlayByPlay(models.Model):
    """OPTIONAL / DEFERRED (nba_api gives it free but it is heavy). Build only
    if in-play / minute-distribution modelling is greenlit; otherwise treat as
    an unmounted scope — the props MVP does not need it."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="plays")
    period = models.SmallIntegerField()
    game_clock = models.CharField(max_length=16, blank=True)  # "10:32"
    event_type = models.CharField(max_length=32)
    player = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="plays"
    )
    team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="plays"
    )
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "play-by-play"
        indexes = [models.Index(fields=["game", "period"])]

    def __str__(self) -> str:
        return f"game {self.game_id} P{self.period} {self.event_type}"
