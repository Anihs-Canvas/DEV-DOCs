"""Core team model + player-prop model, model registry, calibration hooks
[bball-03]. Team markets are market-GRADE (a calibrated anchor + devig cross-
check); the player-prop distributions are the differentiator that feeds the edge
engine (apps.edge / apps.props consume PropPrediction)."""

from django.apps import AppConfig


class PredictionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.predictions"
    verbose_name = "Predictions"
