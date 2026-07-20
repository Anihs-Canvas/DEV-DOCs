"""Ratings & player-form feature layer [bball-01 §2, bball-03 §2c/§4].

Owns the opponent-adjusted efficiency ratings (ridge), the margin-Elo
cold-start/ensemble rating, and the player-form / minutes-projection
state that feeds the props model. Pure-math estimators live in
`ratings.py` / `elo.py` (no ORM); the materialized rows live in
`models.py`.
"""

from django.apps import AppConfig


class FeaturesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.features"
    verbose_name = "Features"
