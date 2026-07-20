"""Dashboard URLs [bball-01 §1] — mounted at the site root."""

from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("predictions", views.predictions, name="predictions"),
    path("edge", views.edge, name="edge"),
    path("clv-gate", views.clv_gate, name="clv-gate"),
]
