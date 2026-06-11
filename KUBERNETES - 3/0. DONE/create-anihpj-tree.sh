#!/bin/bash
# ─────────────────────────────────────────────────────────────
# create-anihpj-tree.sh
# Creates the full anihpj/jobpost directory skeleton at /lpj/
# Run: sudo ./create-anihpj-tree.sh
# ─────────────────────────────────────────────────────────────
set -e

ROOT="/lpj"

echo "🏗️  Creating anihpj/jobpost tree at $ROOT ..."

# ── anihpj/ (Django project root) ─────────────────────────
mkdir -p "$ROOT/anihpj"

touch "$ROOT/anihpj/__init__.py"
touch "$ROOT/anihpj/settings.py"
touch "$ROOT/anihpj/urls.py"
touch "$ROOT/anihpj/wsgi.py"
touch "$ROOT/anihpj/asgi.py"
touch "$ROOT/anihpj/celery.py"

# ── jobpost/ (Main Django app) ─────────────────────────────
mkdir -p "$ROOT/jobpost/templates/jobpost"
mkdir -p "$ROOT/jobpost/static/jobpost"
mkdir -p "$ROOT/jobpost/migrations"

touch "$ROOT/jobpost/__init__.py"
touch "$ROOT/jobpost/models.py"
touch "$ROOT/jobpost/views.py"
touch "$ROOT/jobpost/urls.py"
touch "$ROOT/jobpost/serializers.py"
touch "$ROOT/jobpost/admin.py"
touch "$ROOT/jobpost/tests.py"
touch "$ROOT/jobpost/tasks.py"
touch "$ROOT/jobpost/permissions.py"
touch "$ROOT/jobpost/templates/jobpost/base.html"
touch "$ROOT/jobpost/templates/jobpost/job_list.html"
touch "$ROOT/jobpost/templates/jobpost/job_detail.html"
touch "$ROOT/jobpost/templates/jobpost/apply.html"
touch "$ROOT/jobpost/static/jobpost/style.css"
touch "$ROOT/jobpost/static/jobpost/main.js"
touch "$ROOT/jobpost/migrations/0001_initial.py"

# ── api/ (REST API app) ────────────────────────────────────
mkdir -p "$ROOT/api"

touch "$ROOT/api/__init__.py"
touch "$ROOT/api/views.py"
touch "$ROOT/api/urls.py"
touch "$ROOT/api/serializers.py"

# ── Docker & project root files ────────────────────────────
touch "$ROOT/Dockerfile"
touch "$ROOT/Dockerfile.dev"
touch "$ROOT/docker-compose.yml"
touch "$ROOT/requirements.txt"
touch "$ROOT/manage.py"

# ── k8s/base/ (Core Kubernetes manifests) ──────────────────
mkdir -p "$ROOT/k8s/base"

touch "$ROOT/k8s/base/namespace.yaml"
touch "$ROOT/k8s/base/web-deployment.yaml"
touch "$ROOT/k8s/base/api-deployment.yaml"
touch "$ROOT/k8s/base/db-statefulset.yaml"
touch "$ROOT/k8s/base/web-service.yaml"
touch "$ROOT/k8s/base/api-service.yaml"
touch "$ROOT/k8s/base/db-service.yaml"
touch "$ROOT/k8s/base/configmap.yaml"
touch "$ROOT/k8s/base/secrets.yaml"

# ── k8s/cilium/ (Cilium network policies) ──────────────────
mkdir -p "$ROOT/k8s/cilium"

touch "$ROOT/k8s/cilium/cnp-baseline.yaml"
touch "$ROOT/k8s/cilium/cnp-l7.yaml"
touch "$ROOT/k8s/cilium/cnp-dns.yaml"
touch "$ROOT/k8s/cilium/ccnp-host-firewall.yaml"
touch "$ROOT/k8s/cilium/cidrgroup-vpn.yaml"

# ── k8s/ingress/ ───────────────────────────────────────────
mkdir -p "$ROOT/k8s/ingress"

touch "$ROOT/k8s/ingress/ingress.yaml"
touch "$ROOT/k8s/ingress/gateway.yaml"

# ── k8s/monitoring/ ────────────────────────────────────────
mkdir -p "$ROOT/k8s/monitoring"

touch "$ROOT/k8s/monitoring/servicemonitor.yaml"
touch "$ROOT/k8s/monitoring/grafana-dashboard.yaml"

# ── scripts/ ───────────────────────────────────────────────
mkdir -p "$ROOT/scripts"

touch "$ROOT/scripts/cilium-setup.sh"
touch "$ROOT/scripts/connectivity-test.sh"
touch "$ROOT/scripts/deploy.sh"

# ── ops/ (Operations artifacts — LFCS + daily ops practice) ─
mkdir -p "$ROOT/ops/logs"
mkdir -p "$ROOT/ops/systemd"
mkdir -p "$ROOT/ops/backups"
mkdir -p "$ROOT/ops/cron"

touch "$ROOT/ops/logs/app.log"
touch "$ROOT/ops/logs/error.log"
touch "$ROOT/ops/logs/access.log"
touch "$ROOT/ops/systemd/jobpost.service"
touch "$ROOT/ops/systemd/celery.service"
touch "$ROOT/ops/cron/anihpj-crontab"

# ── Root files ─────────────────────────────────────────────
touch "$ROOT/.gitignore"
touch "$ROOT/.dockerignore"
touch "$ROOT/Makefile"
touch "$ROOT/README.md"

# ── Permissions ────────────────────────────────────────────
chmod 600 "$ROOT/k8s/base/secrets.yaml"

# ── Ownership ──────────────────────────────────────────────
if [ -n "$SUDO_USER" ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "$ROOT"
fi

echo ""
echo "✅ Done! Created at $ROOT"
echo "   $(find "$ROOT" -type d | wc -l) directories"
echo "   $(find "$ROOT" -type f | wc -l) files"
echo ""
find "$ROOT" -maxdepth 3 -type f | sort