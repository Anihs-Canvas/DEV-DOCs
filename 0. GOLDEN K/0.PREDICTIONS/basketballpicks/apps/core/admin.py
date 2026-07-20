"""Light admin registration for the core reference + results models.

The alias review queues (TeamAlias / PlayerAlias filtered on status=pending)
are the manual name-resolution surface [ADR 007]."""

from django.contrib import admin

from apps.core.models import (
    Game,
    League,
    Player,
    PlayerAlias,
    PlayerBoxScore,
    Season,
    Team,
    TeamAlias,
    TeamBoxScore,
)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "level")
    search_fields = ("code", "name")


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("league", "name", "start_date", "end_date")
    list_filter = ("league",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("canonical_name", "abbreviation", "league", "conference")
    list_filter = ("league", "conference")
    search_fields = ("canonical_name", "abbreviation")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("canonical_name", "current_team", "primary_position", "status")
    list_filter = ("status", "primary_position")
    search_fields = ("canonical_name",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "status", "tipoff_utc", "home_score", "away_score")
    list_filter = ("status", "season")
    date_hierarchy = "tipoff_utc"


@admin.register(TeamAlias)
class TeamAliasAdmin(admin.ModelAdmin):
    list_display = ("source", "alias_name", "team", "status")
    list_filter = ("status", "source")
    search_fields = ("alias_name",)


@admin.register(PlayerAlias)
class PlayerAliasAdmin(admin.ModelAdmin):
    list_display = ("source", "alias_name", "player", "status")
    list_filter = ("status", "source")
    search_fields = ("alias_name",)


admin.site.register(TeamBoxScore)
admin.site.register(PlayerBoxScore)
