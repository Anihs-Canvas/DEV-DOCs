"""Admin for the ingestion audit trail + injury feed."""

from django.contrib import admin

from apps.ingestion.models import (
    GameSourceRef,
    InjuryReport,
    JobRun,
    PlayerSourceRef,
    TeamSourceRef,
)


@admin.register(JobRun)
class JobRunAdmin(admin.ModelAdmin):
    list_display = ("job_name", "status", "started_at", "finished_at")
    list_filter = ("status", "job_name")
    date_hierarchy = "started_at"


@admin.register(InjuryReport)
class InjuryReportAdmin(admin.ModelAdmin):
    list_display = ("player", "status", "team", "game", "reported_at")
    list_filter = ("status", "source")
    date_hierarchy = "reported_at"


admin.site.register(GameSourceRef)
admin.site.register(TeamSourceRef)
admin.site.register(PlayerSourceRef)
