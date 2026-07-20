"""Data-source clients, sync jobs, raw storage, ETL orchestrator [bball-01 §3]."""

from django.apps import AppConfig


class IngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ingestion"
    verbose_name = "Ingestion"
