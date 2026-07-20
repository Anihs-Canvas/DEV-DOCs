"""Ingestion audit + cross-source identity + the NBA-mandated injury feed
[bball-01 §2].

* JobRun — audits every sync (copied verbatim from safepicks). The
  soak-gate metric is a query over these rows.
* GameSourceRef / TeamSourceRef / PlayerSourceRef — a source's external id
  for a canonical row, so one source can ADOPT an entity another created
  instead of duplicating it or mutating its row (ADR 007). PlayerSourceRef
  is new: nba_api player ids feed the per-player game-log endpoint.
* InjuryReport — the league-mandated, public NBA injury feed (much cleaner
  than soccer's). The final report ~30 min pre-tip is the critical capture
  that triggers the usage-cascade repricing across 300 prop lines.

The *SourceRef / InjuryReport tables are the write targets Agent 2 fills from
apps/ingestion/sources/. Player stays FIRST-CLASS here (unlike soccer): these
reference apps.core.Player directly.
"""

from django.db import models


class JobRun(models.Model):
    STATUS_RUNNING = "running"
    STATUS_OK = "ok"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"  # designed no-op: missing key / budget floor
    STATUS_CHOICES = [
        (STATUS_RUNNING, "running"),
        (STATUS_OK, "ok"),
        (STATUS_FAILED, "failed"),
        (STATUS_SKIPPED, "skipped"),
    ]

    job_name = models.CharField(max_length=64)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_RUNNING)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["job_name", "-started_at"])]

    def __str__(self) -> str:
        return f"{self.job_name} @ {self.started_at:%Y-%m-%d %H:%M} [{self.status}]"


class GameSourceRef(models.Model):
    """A source's external id for a Game — lets the_odds_api / nba_api ADOPT a
    game another source created instead of duplicating it (ADR 007)."""

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="source_refs")
    source = models.CharField(max_length=32)
    external_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="uniq_game_ref"),
        ]
        indexes = [models.Index(fields=["game", "source"])]

    def __str__(self) -> str:
        return f"{self.source}:{self.external_id} -> game {self.game_id}"


class TeamSourceRef(models.Model):
    """A source's id for a Team (e.g. odds_api team keys -> canonical Team)."""

    team = models.ForeignKey("core.Team", on_delete=models.CASCADE, related_name="source_refs")
    source = models.CharField(max_length=32)
    external_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="uniq_team_ref"),
        ]
        indexes = [models.Index(fields=["team", "source"])]

    def __str__(self) -> str:
        return f"{self.source}:{self.external_id} -> team {self.team_id}"


class PlayerSourceRef(models.Model):
    """A source's id for a Player — nba_api player ids feed the per-player
    game-log endpoint; odds_api prop payloads resolve to a canonical Player."""

    player = models.ForeignKey(
        "core.Player", on_delete=models.CASCADE, related_name="source_refs"
    )
    source = models.CharField(max_length=32)
    external_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="uniq_player_ref"),
        ]
        indexes = [models.Index(fields=["player", "source"])]

    def __str__(self) -> str:
        return f"{self.source}:{self.external_id} -> player {self.player_id}"


class InjuryReport(models.Model):
    """NBA-mandated official injury/availability item. The final report ~30 min
    pre-tip is the highest-value capture (the usage-cascade trigger)."""

    STATUS_OUT = "OUT"
    STATUS_DOUBTFUL = "DOUBTFUL"
    STATUS_QUESTIONABLE = "QUESTIONABLE"
    STATUS_PROBABLE = "PROBABLE"
    STATUS_GTD = "GTD"
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_CHOICES = [
        (STATUS_OUT, "out"),
        (STATUS_DOUBTFUL, "doubtful"),
        (STATUS_QUESTIONABLE, "questionable"),
        (STATUS_PROBABLE, "probable"),
        (STATUS_GTD, "game-time decision"),
        (STATUS_AVAILABLE, "available"),
    ]

    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="injury_reports")
    team = models.ForeignKey("core.Team", on_delete=models.PROTECT, related_name="injury_reports")
    player = models.ForeignKey(
        "core.Player", on_delete=models.PROTECT, related_name="injury_reports"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    reason = models.CharField(max_length=128, blank=True)  # injury/rest/personal
    reported_at = models.DateTimeField()  # when WE first captured the item
    source = models.CharField(max_length=32)
    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "game", "player"], name="uniq_injury_item"
            ),
        ]
        indexes = [models.Index(fields=["player", "-reported_at"])]

    def __str__(self) -> str:
        return f"{self.player.canonical_name} ({self.status}) game {self.game_id}"
