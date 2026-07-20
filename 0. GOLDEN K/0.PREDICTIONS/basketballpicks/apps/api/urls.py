"""API v1 routes [bball-01 §1]. Read-only paper surface over predictions,
edge picks, and the forward-CLV gate."""

from django.urls import path

from apps.api import views

app_name = "api"

urlpatterns = [
    path("predictions/today", views.predictions_today, name="predictions-today"),
    path("edge/today", views.edge_today, name="edge-today"),
    path("edge/cells", views.edge_cells, name="edge-cells"),
    path("clv/gate", views.clv_gate, name="clv-gate"),
    path("games/<int:game_id>/prediction", views.game_prediction, name="game-prediction"),
    path("games/<int:game_id>/props", views.game_props, name="game-props"),
]
