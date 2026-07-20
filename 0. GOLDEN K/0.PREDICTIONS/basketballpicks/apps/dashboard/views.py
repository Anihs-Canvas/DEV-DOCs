"""Dashboard views [bball-01 §1] — thin by convention; every context is
assembled in apps.dashboard.services (read-only). Local product pages, no login.
"""

from django.shortcuts import render

from apps.dashboard import services


def home(request):
    """Redirect-ish landing: the forward-CLV gate is the project's headline."""
    return render(request, "dashboard/home.html", services.base_context())


def predictions(request):
    day = None
    raw = request.GET.get("date")
    if raw:
        from datetime import date

        try:
            day = date.fromisoformat(raw)
        except ValueError:
            day = None
    return render(request, "dashboard/predictions.html", services.predictions_context(day))


def edge(request):
    return render(request, "dashboard/edge.html", services.edge_context())


def clv_gate(request):
    try:
        days = max(1, int(request.GET.get("days", "90")))
    except ValueError:
        days = 90
    return render(request, "dashboard/clv_gate.html", services.clv_gate_context(days))
