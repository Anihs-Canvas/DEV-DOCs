"""Generate Appendix C: anihpj/jobpost Full File Structure for cilium-test-prep.html"""

HTML_FILE = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html'

lines = []
lines.append('')
lines.append('    <!-- ═══════════════ APPENDIX C: ANIHPJ/JOBPOST FULL FILE STRUCTURE ═══════════════ -->')
lines.append('    <section class="chapter-section" id="apx-c">')
lines.append('        <h2><span>📂 Appendix C: anihpj/jobpost Full File Structure</span><span class="chapter-badge">Project Reference</span></h2>')
lines.append('')
lines.append('        <div class="aq-info">')
lines.append('            <p>Complete file structure and reference for the <strong>anihpj/jobpost</strong> Django application — the primary application used across all 100 Part 3 lab scenarios (S1-S100). This appendix serves as your quick-reference for all application files, Kubernetes manifests, Cilium policies, and deployment scripts referenced throughout the exam preparation material.</p>')
lines.append('            <p><strong>Application:</strong> Django 4.2 job posting platform (web + REST API + PostgreSQL backend) | <strong>Framework:</strong> Django + DRF + Celery + Gunicorn | <strong>Infrastructure:</strong> Kubernetes + Cilium CNI</p>')
lines.append('        </div>')
lines.append('')

# ── Section 1: Complete Directory Tree ──
lines.append('        <h3>🌳 Complete Directory Tree</h3>')
lines.append('        <div class="file-tree">')
lines.append('<pre>anihpj/')
lines.append('\u2502')
lines.append('\u251c\u2500\u2500 \U0001f4c1 anihpj/                          # Django project root')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 __init__.py')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 settings.py                  # Django settings (DB, apps, middleware)')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 urls.py                      # Root URL routing')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 wsgi.py                      # WSGI entry for Gunicorn')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 asgi.py                      # ASGI entry')
lines.append('\u2502   \u2514\u2500\u2500 \U0001f4c4 celery.py                    # Celery config (background tasks)')
lines.append('\u2502')
lines.append('\u251c\u2500\u2500 \U0001f4c1 jobpost/                         # Main Django app')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 __init__.py')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 models.py                    # Job, Company, Application models')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 views.py                     # View logic (web + API)')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 urls.py                      # App URL routing')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 serializers.py               # DRF serializers for API')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 admin.py                     # Django admin registration')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 tests.py                     # Unit and integration tests')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 tasks.py                     # Celery background tasks')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 permissions.py               # Custom DRF permissions')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c1 templates/')
lines.append('\u2502   \u2502   \u2514\u2500\u2500 \U0001f4c1 jobpost/')
lines.append('\u2502   \u2502       \u251c\u2500\u2500 \U0001f4c4 base.html            # Base template')
lines.append('\u2502   \u2502       \u251c\u2500\u2500 \U0001f4c4 job_list.html        # Job listing page')
lines.append('\u2502   \u2502       \u251c\u2500\u2500 \U0001f4c4 job_detail.html      # Single job view')
lines.append('\u2502   \u2502       \u2514\u2500\u2500 \U0001f4c4 apply.html           # Job application form')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c1 static/')
lines.append('\u2502   \u2502   \u2514\u2500\u2500 \U0001f4c1 jobpost/')
lines.append('\u2502   \u2502       \u251c\u2500\u2500 \U0001f4c4 style.css')
lines.append('\u2502   \u2502       \u2514\u2500\u2500 \U0001f4c4 main.js')
lines.append('\u2502   \u2514\u2500\u2500 \U0001f4c1 migrations/')
lines.append('\u2502       \u2514\u2500\u2500 \U0001f4c4 0001_initial.py')
lines.append('\u2502')
lines.append('\u251c\u2500\u2500 \U0001f4c1 api/                             # REST API app')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 __init__.py')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 views.py                     # APIView classes')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c4 urls.py                      # /api/v1/ routes')
lines.append('\u2502   \u2514\u2500\u2500 \U0001f4c4 serializers.py               # API-specific serializers')
lines.append('\u2502')
lines.append('\u251c\u2500\u2500 \U0001f4c4 Dockerfile                       # Multi-stage production build')
lines.append('\u251c\u2500\u2500 \U0001f4c4 Dockerfile.dev                   # Development build')
lines.append('\u251c\u2500\u2500 \U0001f4c4 docker-compose.yml               # Local dev with PostgreSQL + Redis')
lines.append('\u251c\u2500\u2500 \U0001f4c4 requirements.txt                 # Python dependencies')
lines.append('\u251c\u2500\u2500 \U0001f4c4 manage.py                        # Django management CLI')
lines.append('\u2502')
lines.append('\u251c\u2500\u2500 \U0001f4c1 k8s/                             # Kubernetes manifests')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c1 base/')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 namespace.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 web-deployment.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 api-deployment.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 db-statefulset.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 web-service.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 api-service.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 db-service.yaml')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 configmap.yaml')
lines.append('\u2502   \u2502   \u2514\u2500\u2500 \U0001f4c4 secrets.yaml')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c1 cilium/')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 cnp-baseline.yaml        # L3/L4 baseline policies')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 cnp-l7.yaml              # L7 HTTP rules')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 cnp-dns.yaml             # DNS policies')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 ccnp-host-firewall.yaml  # Host firewall CCNP')
lines.append('\u2502   \u2502   \u2514\u2500\u2500 \U0001f4c4 cidrgroup-vpn.yaml       # CIDRGroup for VPN ranges')
lines.append('\u2502   \u251c\u2500\u2500 \U0001f4c1 ingress/')
lines.append('\u2502   \u2502   \u251c\u2500\u2500 \U0001f4c4 ingress.yaml             # Cilium Ingress')
lines.append('\u2502   \u2502   \u2514\u2500\u2500 \U0001f4c4 gateway.yaml             # Gateway API')
lines.append('\u2502   \u2514\u2500\u2500 \U0001f4c1 monitoring/')
lines.append('\u2502       \u251c\u2500\u2500 \U0001f4c4 servicemonitor.yaml')
lines.append('\u2502       \u2514\u2500\u2500 \U0001f4c4 grafana-dashboard.yaml')
lines.append('\u2502')
lines.append('\u2514\u2500\u2500 \U0001f4c1 scripts/')
lines.append('    \u251c\u2500\u2500 \U0001f4c4 cilium-setup.sh              # Cilium installation + verification')
lines.append('    \u251c\u2500\u2500 \U0001f4c4 connectivity-test.sh         # End-to-end connectivity checks')
lines.append('    \u2514\u2500\u2500 \U0001f4c4 deploy.sh                    # Full deployment script')
lines.append('</pre>')
lines.append('        </div>')
lines.append('')

# ── Section 2: File Descriptions Table ──
lines.append('        <h3>📋 File &amp; Directory Descriptions</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>Path</th><th>Type</th><th>Purpose</th><th>Referenced In</th></tr>')
descs = [
    ("anihpj/settings.py", "Config", "Django settings: database, installed apps, middleware, CORS, Celery broker", "S1, S4, S14, S65"),
    ("anihpj/urls.py", "Routing", "Root URL configuration — maps /admin, /api/v1/, / to apps", "S1, S42"),
    ("anihpj/wsgi.py", "Entry", "WSGI application entry point for Gunicorn production server", "S1, S65, Appendix D"),
    ("anihpj/celery.py", "Config", "Celery task queue configuration (Redis broker, result backend)", "S1, S45"),
    ("jobpost/models.py", "Model", "Django ORM models: Job, Company, Application, User", "S1, S2, S23"),
    ("jobpost/views.py", "View", "View logic: job listing, detail, application form handling", "S1, S23, S44"),
    ("jobpost/serializers.py", "API", "DRF serializers for Job, Company, Application models", "S2, S23"),
    ("jobpost/tasks.py", "Async", "Celery background tasks: email notifications, job expiry", "S1, S45"),
    ("jobpost/templates/", "UI", "Django templates: base.html, job_list.html, job_detail.html, apply.html", "S1, S42"),
    ("api/views.py", "API", "REST API ViewSets and APIView classes for /api/v1/ endpoints", "S2, S23, S58"),
    ("api/urls.py", "Routing", "API URL routing: /api/v1/jobs/, /api/v1/companies/, etc.", "S2"),
    ("Dockerfile", "Build", "Multi-stage production Dockerfile (builder + runtime stages)", "S65, Appendix D"),
    ("Dockerfile.dev", "Build", "Development Dockerfile with runserver for hot-reload", "S65"),
    ("docker-compose.yml", "Dev", "Local development environment: Django + PostgreSQL + Redis", "S65"),
    ("requirements.txt", "Deps", "Python dependencies: Django 4.2, DRF 3.14, Gunicorn, Celery, psycopg2", "S65, Appendix D"),
]
for i, (path, ftype, purpose, refs) in enumerate(descs):
    rc = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
    lines.append(f'            <tr class="{rc}"><td class="cmd-syn"><code>{path}</code></td><td class="cmd-num">{ftype}</td><td class="cmd-purpose">{purpose}</td><td class="cmd-when">{refs}</td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# ── Section 3: Dockerfile Reference ──
lines.append('        <h3>🐳 Dockerfile Reference</h3>')
lines.append('')
lines.append('        <h4>Production Dockerfile (Multi-Stage)</h4>')
lines.append('        <div class="code-block">')
lines.append('            <div class="code-header">')
lines.append('                <span class="code-lang">Dockerfile — Production Build</span>')
lines.append('''                <button class="copy-btn" onclick="copyToClipboard(this, 'apxc-dockerfile')">📋 Copy</button>''')
lines.append('            </div>')
lines.append('''            <pre><code id="apxc-dockerfile"># Stage 1: Build''')
lines.append('FROM python:3.11-slim AS builder')
lines.append('WORKDIR /app')
lines.append('COPY requirements.txt .')
lines.append('RUN pip install --no-cache-dir --user -r requirements.txt')
lines.append('')
lines.append('# Stage 2: Production')
lines.append('FROM python:3.11-slim')
lines.append('WORKDIR /app')
lines.append('COPY --from=builder /root/.local /root/.local')
lines.append('COPY . .')
lines.append('ENV PATH=/root/.local/bin:$PATH')
lines.append('ENV PYTHONUNBUFFERED=1')
lines.append('RUN python manage.py collectstatic --noinput')
lines.append('EXPOSE 8000')
lines.append('''CMD ["gunicorn", "anihpj.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]</code></pre>''')
lines.append('        </div>')
lines.append('')

lines.append('        <h4>Development Dockerfile</h4>')
lines.append('        <div class="code-block">')
lines.append('            <div class="code-header">')
lines.append('                <span class="code-lang">Dockerfile.dev — Development Build</span>')
lines.append('''                <button class="copy-btn" onclick="copyToClipboard(this, 'apxc-dockerfile-dev')">📋 Copy</button>''')
lines.append('            </div>')
lines.append('''            <pre><code id="apxc-dockerfile-dev">FROM python:3.11-slim''')
lines.append('WORKDIR /app')
lines.append('COPY requirements.txt .')
lines.append('RUN pip install -r requirements.txt')
lines.append('COPY . .')
lines.append('EXPOSE 8000')
lines.append('''CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]</code></pre>''')
lines.append('        </div>')
lines.append('')

# ── Section 4: requirements.txt ──
lines.append('        <h3>📦 Python Dependencies (requirements.txt)</h3>')
lines.append('        <div class="code-block">')
lines.append('            <div class="code-header">')
lines.append('                <span class="code-lang">requirements.txt</span>')
lines.append('''                <button class="copy-btn" onclick="copyToClipboard(this, 'apxc-reqs')">📋 Copy</button>''')
lines.append('            </div>')
lines.append('''            <pre><code id="apxc-reqs">Django==4.2''')
lines.append('djangorestframework==3.14')
lines.append('gunicorn==21.2')
lines.append('psycopg2-binary==2.9')
lines.append('celery==5.3')
lines.append('redis==5.0')
lines.append('django-cors-headers==4.3')
lines.append('django-filter==23.5')
lines.append('''drf-yasg==1.21  # Swagger API docs</code></pre>''')
lines.append('        </div>')
lines.append('')

# ── Section 5: K8s Manifests ──
lines.append('        <h3>☸️ Kubernetes Manifests Overview</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>File</th><th>Kind</th><th>Purpose</th><th>Key Specs</th></tr>')
k8s_files = [
    ("base/namespace.yaml", "Namespace", "Creates 'anihpj' namespace for resource isolation", "name: anihpj"),
    ("base/web-deployment.yaml", "Deployment", "Django web frontend (Gunicorn)", "replicas: 2, image: anihpj:latest, containerPort: 8000"),
    ("base/api-deployment.yaml", "Deployment", "Django REST API backend", "replicas: 2, image: anihpj-api:latest, containerPort: 8001"),
    ("base/db-statefulset.yaml", "StatefulSet", "PostgreSQL database with persistent storage", "replicas: 1, image: postgres:15, PVC: 10Gi"),
    ("base/web-service.yaml", "Service", "ClusterIP for web frontend", "port: 80, targetPort: 8000, type: ClusterIP"),
    ("base/api-service.yaml", "Service", "ClusterIP for REST API", "port: 8001, targetPort: 8001, type: ClusterIP"),
    ("base/db-service.yaml", "Service", "Headless service for PostgreSQL", "port: 5432, targetPort: 5432, clusterIP: None"),
    ("base/configmap.yaml", "ConfigMap", "Django settings: DEBUG, ALLOWED_HOSTS, DB_HOST", "DB_HOST: anihpj-db, DB_NAME: anihpj"),
    ("base/secrets.yaml", "Secret", "Sensitive data: DB password, Django SECRET_KEY", "type: Opaque, base64 encoded"),
]
for i, (f, kind, purpose, specs) in enumerate(k8s_files):
    rc = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
    lines.append(f'            <tr class="{rc}"><td class="cmd-syn"><code>{f}</code></td><td class="cmd-num">{kind}</td><td class="cmd-purpose">{purpose}</td><td class="cmd-when">{specs}</td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# ── Section 6: Cilium Policies ──
lines.append('        <h3>🔒 Cilium Network Policies Reference</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>File</th><th>Kind</th><th>Purpose</th><th>Applied In</th></tr>')
pol_files = [
    ("cilium/cnp-baseline.yaml", "CiliumNetworkPolicy", "L3/L4 baseline: web→api:8001, api→db:5432, deny web→db", "S21, S22, S33"),
    ("cilium/cnp-l7.yaml", "CiliumNetworkPolicy", "L7 HTTP: GET /api/jobs, POST /api/jobs, deny POST /admin", "S23, S30, S35"),
    ("cilium/cnp-dns.yaml", "CiliumNetworkPolicy", "DNS egress: allow anihpj-db.anihpj.svc.cluster.local, block external", "S24, S25"),
    ("cilium/ccnp-host-firewall.yaml", "CiliumClusterwideNetworkPolicy", "Host firewall: allow SSH from office CIDR, deny all other ingress", "S28, S9"),
    ("cilium/cidrgroup-vpn.yaml", "CiliumCIDRGroup", "VPN CIDR group for office networks (10.99.0.0/16, 172.30.0.0/16)", "S27"),
]
for i, (f, kind, purpose, refs) in enumerate(pol_files):
    rc = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
    lines.append(f'            <tr class="{rc}"><td class="cmd-syn"><code>{f}</code></td><td class="cmd-num">{kind}</td><td class="cmd-purpose">{purpose}</td><td class="cmd-when">{refs}</td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# ── Section 7: Ingress & Monitoring ──
lines.append('        <h3>🌐 Ingress &amp; Monitoring Manifests</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>File</th><th>Kind</th><th>Purpose</th><th>Applied In</th></tr>')
ing_files = [
    ("ingress/ingress.yaml", "Ingress", "Cilium Ingress: TLS termination, host: anihpj.example.com → web:80", "S42, S43, S50"),
    ("ingress/gateway.yaml", "Gateway", "Gateway API HTTPRoute for canary: 90% v1, 10% v2", "S44, S51"),
    ("monitoring/servicemonitor.yaml", "ServiceMonitor", "Prometheus ServiceMonitor for Hubble metrics scraping", "S61, S63"),
    ("monitoring/grafana-dashboard.yaml", "ConfigMap", "Grafana dashboard JSON for anihpj HTTP latency dashboard", "S62"),
]
for i, (f, kind, purpose, refs) in enumerate(ing_files):
    rc = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
    lines.append(f'            <tr class="{rc}"><td class="cmd-syn"><code>{f}</code></td><td class="cmd-num">{kind}</td><td class="cmd-purpose">{purpose}</td><td class="cmd-when">{refs}</td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# ── Section 8: Scripts ──
lines.append('        <h3>🛠️ Deployment &amp; Verification Scripts</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>Script</th><th>Purpose</th><th>Key Commands</th></tr>')
script_files = [
    ("scripts/cilium-setup.sh", "Install Cilium with Hubble + verify all components", "cilium install, cilium status --wait, cilium connectivity test, cilium hubble enable"),
    ("scripts/connectivity-test.sh", "End-to-end connectivity: deploy anihpj, test web→api→db", "kubectl apply -f k8s/base/, kubectl wait, curl tests, hubble observe"),
    ("scripts/deploy.sh", "Full deployment: namespace → secrets → DB → API → web → ingress", "kubectl apply -f k8s/ sequentially with readiness checks"),
]
for i, (s, purpose, cmds) in enumerate(script_files):
    rc = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
    lines.append(f'            <tr class="{rc}"><td class="cmd-syn"><code>{s}</code></td><td class="cmd-purpose">{purpose}</td><td class="cmd-when"><code>{cmds}</code></td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# ── Tips ──
lines.append('        <div class="aq-tips">')
lines.append('            <h4>💡 How to Use This Appendix</h4>')
lines.append('            <ul>')
lines.append('                <li><strong>Quick lookup:</strong> When a scenario references a file (e.g., "apply cnp-baseline.yaml"), find it here to understand its role in the application.</li>')
lines.append('                <li><strong>Recreate locally:</strong> Use the directory tree and Dockerfile to set up anihpj/jobpost on your own cluster for hands-on practice with the S1-S100 scenarios.</li>')
lines.append('                <li><strong>Exam context:</strong> The CCA exam may ask about application architecture patterns. Knowing how anihpj\'s three tiers (web→api→db) map to Cilium policies is directly applicable.</li>')
lines.append('                <li><strong>Policy reference:</strong> The Cilium policy files in <code>k8s/cilium/</code> are real, production-ready examples you can adapt for any multi-tier application.</li>')
lines.append('            </ul>')
lines.append('        </div>')
lines.append('')
lines.append('    </section>')

appendix_c_html = '\n'.join(lines)

# ── Insert into file ──
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

marker = '\n\n    <!-- ═══════════════ FOOTER ═══════════════ -->'
if marker in content:
    new_content = content.replace(marker, appendix_c_html + marker, 1)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'✅ Appendix C inserted! File: {len(new_content):,} bytes')
    # Count sections
    section_count = appendix_c_html.count('<h3>')
    table_count = appendix_c_html.count('<table')
    print(f'   Sections: {section_count} | Tables: {table_count}')
else:
    print('❌ Could not find FOOTER marker!')
