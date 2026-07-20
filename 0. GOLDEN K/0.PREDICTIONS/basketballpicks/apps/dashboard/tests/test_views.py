"""Dashboard render tests [bball-01 §1] — the read-only product pages render
(200) and degrade cleanly to designed empty states before data accrues."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_renders(client):
    resp = client.get(reverse("dashboard:home"))
    assert resp.status_code == 200
    assert b"forward-CLV" in resp.content or b"CLV" in resp.content


def test_clv_gate_renders_empty(client):
    resp = client.get(reverse("dashboard:clv-gate"), {"days": 30})
    assert resp.status_code == 200
    assert b"Forward-CLV Gate" in resp.content
    # the frozen-threshold banner is always present
    assert b"Pre-registered" in resp.content


def test_edge_page_renders(client):
    resp = client.get(reverse("dashboard:edge"))
    assert resp.status_code == 200
    assert b"Edge Today" in resp.content


def test_predictions_page_renders(client):
    resp = client.get(reverse("dashboard:predictions"))
    assert resp.status_code == 200
    assert b"Predictions" in resp.content
