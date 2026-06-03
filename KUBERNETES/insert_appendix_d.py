#!/usr/bin/env python3
"""Insert Appendix D and exam-overview section into cilium-test-prep.html"""

HTML = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

appendix_d = '''
    <!-- ═══════════════ APPENDIX D ═══════════════ -->
    <section class="chapter-section" id="apx-d">
        <h2><span>📋 Appendix D: Dockerfile &amp; Deployment Reference</span><span class="chapter-badge">Quick Ref</span></h2>
        <div class="chapter-intro">
            <p>Complete Dockerfile, Kubernetes manifests, and deployment workflow reference for the <strong>anihpj/jobpost</strong> Django application used across all 100 lab scenarios. Keep this appendix handy when working through Part 3 labs.</p>
        </div>

        <div class="section-block">
            <h3>D.1 Dockerfile for anihpj/jobpost</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">Dockerfile</span><button class="copy-btn" onclick="copyToClipboard(this, 'apxd-dockerfile')">📋 Copy</button></div>
                <pre><code id="apxd-dockerfile">FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc libpq-dev netcat-openbsd curl dnsutils iputils-ping \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run with gunicorn for production-like behavior
CMD ["gunicorn", "anihpj.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30"]
</code></pre>
            </div>

            <h3>D.2 requirements.txt</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">requirements.txt</span><button class="copy-btn" onclick="copyToClipboard(this, 'apxd-reqs')">📋 Copy</button></div>
                <pre><code id="apxd-reqs">Django>=4.2,&lt;5.0
gunicorn>=21.2
psycopg2-binary>=2.9
django-cors-headers>=4.0
djangorestframework>=3.14
</code></pre>
            </div>

            <h3>D.3 Kubernetes Deployment (with Cilium annotations)</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">anihpj-deploy.yaml</span><button class="copy-btn" onclick="copyToClipboard(this, 'apxd-k8s')">📋 Copy</button></div>
                <pre><code id="apxd-k8s">---
apiVersion: v1
kind: Namespace
metadata:
  name: anihpj
  labels:
    app: anihpj
---
# Web Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-web
  namespace: anihpj
  labels:
    app: anihpj
    tier: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: anihpj
      tier: web
  template:
    metadata:
      labels:
        app: anihpj
        tier: web
    spec:
      containers:
      - name: web
        image: anihpj/jobpost:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: API_URL
          value: "http://anihpj-api.anihpj.svc:8000"
        - name: DATABASE_URL
          value: "postgres://user:pass@anihpj-db.anihpj.svc:5432/jobpost"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
---
# API Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-api
  namespace: anihpj
  labels:
    app: anihpj
    tier: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anihpj
      tier: api
  template:
    metadata:
      labels:
        app: anihpj
        tier: api
    spec:
      containers:
      - name: api
        image: anihpj/jobpost:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          value: "postgres://user:pass@anihpj-db.anihpj.svc:5432/jobpost"
        resources:
          requests:
            cpu: 150m
            memory: 192Mi
          limits:
            cpu: 750m
            memory: 384Mi
---
# Web Service
apiVersion: v1
kind: Service
metadata:
  name: anihpj-web
  namespace: anihpj
spec:
  selector:
    app: anihpj
    tier: web
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
---
# API Service
apiVersion: v1
kind: Service
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  selector:
    app: anihpj
    tier: api
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
</code></pre>
            </div>

            <h3>D.4 CiliumNetworkPolicy for anihpj</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">anihpj-cnp.yaml</span><button class="copy-btn" onclick="copyToClipboard(this, 'apxd-cnp')">📋 Copy</button></div>
                <pre><code id="apxd-cnp">---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: anihpj-policy
  namespace: anihpj
spec:
  endpointSelector:
    matchLabels:
      app: anihpj
  ingress:
  # Allow web → api
  - fromEndpoints:
    - matchLabels:
        tier: web
    toPorts:
    - ports:
      - port: "8000"
        protocol: TCP
  egress:
  # Allow DNS
  - toEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
  # Allow api → database (if using in-cluster DB)
  - toEndpoints:
    - matchLabels:
        tier: database
    toPorts:
    - ports:
      - port: "5432"
        protocol: TCP
  # Allow outbound HTTP/HTTPS
  - toEntities:
    - world
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      - port: "443"
        protocol: TCP
---
# Default deny for anihpj namespace
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: anihpj-default-deny
  namespace: anihpj
spec:
  endpointSelector: {}
  ingress:
  - fromEntities:
    - all
  egress:
  - toEntities:
    - all
</code></pre>
            </div>

            <h3>D.5 Common Deployment Commands</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">Deployment Workflow</span><button class="copy-btn" onclick="copyToClipboard(this, 'apxd-cmds')">📋 Copy</button></div>
                <pre><code id="apxd-cmds"># 1. Build and push Docker image
docker build -t anihpj/jobpost:latest .
docker push anihpj/jobpost:latest

# 2. Deploy to Kubernetes
kubectl apply -f anihpj-deploy.yaml

# 3. Verify deployment
kubectl get pods -n anihpj -o wide
kubectl get svc -n anihpj

# 4. Check Cilium endpoints
cilium endpoint list -n anihpj

# 5. Verify connectivity (from within cluster)
kubectl exec -n anihpj deploy/anihpj-web -- curl -s http://anihpj-api.anihpj.svc:8000/health

# 6. Apply CiliumNetworkPolicy
kubectl apply -f anihpj-cnp.yaml

# 7. Verify policy enforcement
cilium policy get -n anihpj
hubble observe -n anihpj --verdict DROPPED

# 8. Run Cilium connectivity test
cilium connectivity test --test 'pod-to-pod,service,dns,networkpolicy'

# 9. Scale for testing
kubectl scale deploy/anihpj-api -n anihpj --replicas=5

# 10. Debug with Hubble
hubble observe -n anihpj --from-pod anihpj/web --to-pod anihpj/api
</code></pre>
            </div>

            <h3>D.6 Pod-to-Pod Communication Flow</h3>
            <div class="diagram-container">
                <div class="diagram-title">anihpj Application Traffic Flow on Cilium</div>
                <pre>
  ┌─────────────────────────────────────────────────────────┐
  │                    anihpj Namespace                      │
  │                                                         │
  │  ┌──────────┐    HTTP :8000    ┌──────────┐             │
  │  │   WEB    │ ───────────────→ │   API    │             │
  │  │ (2 reps) │ ←── Cilium ───→ │ (3 reps) │             │
  │  └──────────┘   eBPF Policy   └──────────┘             │
  │       │                              │                   │
  │       │ DNS :53                      │ DB :5432          │
  │       ▼                              ▼                   │
  │  ┌──────────┐                  ┌──────────┐             │
  │  │ CoreDNS  │                  │ Postgres │             │
  │  │(kube-sys)│                  │ (anihpj) │             │
  │  └──────────┘                  └──────────┘             │
  │                                                         │
  │  Cilium Data Plane:                                     │
  │  • Identity-based policy (not IP-based)                 │
  │  • eBPF in kernel (no iptables)                         │
  │  • WireGuard encryption (optional)                      │
  │  • Hubble observability (all flows visible)             │
  └─────────────────────────────────────────────────────────┘
</pre>
            </div>
        </div>
    </section>
'''

exam_overview = '''
    <!-- ═══════════════ EXAM OVERVIEW ═══════════════ -->
    <section class="chapter-section" id="exam-overview">
        <h2><span>🎯 Cilium CCA Exam Overview</span><span class="chapter-badge">Certification Guide</span></h2>
        <div class="chapter-intro">
            <p>Everything you need to know about the <strong>Cilium Certified Associate (CCA)</strong> exam — format, domains, scoring, preparation strategy, and exam-day tips.</p>
        </div>

        <div class="section-block">
            <h3>Exam Format</h3>
            <table style="width:100%; border-collapse:collapse; margin:12px 0;">
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Duration</td><td style="padding:8px 12px; border:1px solid #30363d;">90 minutes</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Questions</td><td style="padding:8px 12px; border:1px solid #30363d;">~60 multiple-choice &amp; multiple-select</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Passing Score</td><td style="padding:8px 12px; border:1px solid #30363d;">~65-70% (varies by exam version)</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Delivery</td><td style="padding:8px 12px; border:1px solid #30363d;">Online proctored OR testing center</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Prerequisites</td><td style="padding:8px 12px; border:1px solid #30363d;">CKA recommended but NOT required</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Cost</td><td style="padding:8px 12px; border:1px solid #30363d;">~$250 USD (check cilium.io for current pricing)</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d; font-weight:600;">Validity</td><td style="padding:8px 12px; border:1px solid #30363d;">2 years</td></tr>
            </table>

            <h3>Exam Domains (Weight Distribution)</h3>
            <table style="width:100%; border-collapse:collapse; margin:12px 0;">
                <tr style="background:#1c2128;"><th style="padding:8px 12px; border:1px solid #30363d; text-align:left;">#</th><th style="padding:8px 12px; border:1px solid #30363d; text-align:left;">Domain</th><th style="padding:8px 12px; border:1px solid #30363d; text-align:left;">Weight</th></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d;">1</td><td style="padding:8px 12px; border:1px solid #30363d;">Architecture</td><td style="padding:8px 12px; border:1px solid #30363d;">20%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d;">2</td><td style="padding:8px 12px; border:1px solid #30363d;">Network Policy</td><td style="padding:8px 12px; border:1px solid #30363d;">18%</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d;">3</td><td style="padding:8px 12px; border:1px solid #30363d;">Service Mesh</td><td style="padding:8px 12px; border:1px solid #30363d;">16%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d;">4</td><td style="padding:8px 12px; border:1px solid #30363d;">Observability</td><td style="padding:8px 12px; border:1px solid #30363d;">10%</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d;">5</td><td style="padding:8px 12px; border:1px solid #30363d;">Installation &amp; Configuration</td><td style="padding:8px 12px; border:1px solid #30363d;">10%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d;">6</td><td style="padding:8px 12px; border:1px solid #30363d;">Cluster Mesh</td><td style="padding:8px 12px; border:1px solid #30363d;">10%</td></tr>
                <tr><td style="padding:8px 12px; border:1px solid #30363d;">7</td><td style="padding:8px 12px; border:1px solid #30363d;">eBPF</td><td style="padding:8px 12px; border:1px solid #30363d;">10%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px; border:1px solid #30363d;">8</td><td style="padding:8px 12px; border:1px solid #30363d;">BGP &amp; External Networking</td><td style="padding:8px 12px; border:1px solid #30363d;">6%</td></tr>
            </table>

            <h3>How to Use This Study Guide</h3>
            <div style="margin:12px 0; padding:12px; background:#1c2128; border-radius:8px; border-left:3px solid var(--accent);">
                <p><strong>📚 Recommended Study Path (4-6 weeks):</strong></p>
                <ol style="margin:8px 0 8px 20px; line-height:1.8;">
                    <li><strong>Week 1-2:</strong> Work through Part 1 MCQs (200 questions) domain by domain. Read ALL explanations — even for questions you got right.</li>
                    <li><strong>Week 3:</strong> Complete Part 2 Troubleshooting Issues (100 issues). Focus on the "Most Likely Causes" — these are the exam's scenario-based questions.</li>
                    <li><strong>Week 4:</strong> Hands-on practice with Part 3 Lab Scenarios (S1-S100). Deploy anihpj, inject bugs, fix them. Nothing beats real Cilium debugging experience.</li>
                    <li><strong>Week 5:</strong> Review Appendices. Memorize the Top 50 Commands (Appendix B). Review decision trees (Appendix E) for rapid troubleshooting.</li>
                    <li><strong>Week 6:</strong> Take full practice exams (200 MCQs timed). Score 80%+ consistently before scheduling your exam.</li>
                </ol>
            </div>

            <h3>Exam-Day Tips</h3>
            <ul style="margin:8px 0 8px 20px; line-height:1.8;">
                <li><strong>⌛ Time Management:</strong> 90 minutes for ~60 questions = ~1.5 min per question. Flag tough ones and return later. Don't get stuck.</li>
                <li><strong>🔑 Key Topics to Master:</strong> CiliumNetworkPolicy syntax (L3/L4/L7), Hubble observe commands, KPR modes, Cluster Mesh prerequisites, eBPF hook points, BGP peering config.</li>
                <li><strong>⚠️ Common Pitfalls:</strong> Confusing CiliumNetworkPolicy with Kubernetes NetworkPolicy syntax. Forgetting that L7 policies disable socket LB. Assuming Cluster Mesh auto-encrypts cross-cluster traffic.</li>
                <li><strong>💻 Hands-On Is Essential:</strong> The CCA tests practical knowledge. You should be able to: deploy Cilium, write a CNP, debug with Hubble, run connectivity test, and interpret `cilium status` output — all from memory.</li>
                <li><strong>📋 Pre-Exam Checklist:</strong> Stable internet (if online), quiet room, government ID ready, system compatibility test completed 24h before.</li>
            </ul>

            <h3>Key Commands to Memorize</h3>
            <div class="code-block">
                <div class="code-header"><span class="code-lang">Must-Know CCA Commands</span></div>
                <pre><code># Status & Health
cilium status                    # Overall Cilium health
cilium status --verbose          # Detailed component status
cilium connectivity test         # Validate Cilium installation

# Endpoints & Identity
cilium endpoint list             # All local endpoints
cilium endpoint get &lt;id&gt;         # Specific endpoint details
cilium identity list             # All identities (local + remote)

# Policy
cilium policy get                # All policies
cilium policy import &lt;file&gt;      # Import CNP from YAML
kubectl get cnp -A              # All CiliumNetworkPolicies

# Observability
hubble observe                   # Live flow log
hubble observe --verdict DROPPED # Only dropped packets
hubble observe -n &lt;namespace&gt;    # Namespace-scoped
cilium monitor --type drop       # Control plane drop events

# Service & Load Balancing
cilium service list              # All services with backends
cilium bpf lb list               # Maglev BPF map
cilium-dbg bgp peers             # BGP peer status

# Encryption
cilium encrypt status            # Encryption status (WireGuard/IPSec)

# Cluster Mesh
cilium clustermesh status        # Mesh connectivity
cilium clustermesh connect        # Connect clusters

# Troubleshooting
cilium sysdump                   # Collect ALL state for support
cilium bpf ct list global        # Connection tracking table
cilium-dbg bpf policy get &lt;id&gt;   # BPF policy for endpoint
kubectl logs -n kube-system ds/cilium --tail=100  # Agent logs
</code></pre>
            </div>
        </div>
    </section>
'''

# Read file, find insertion points
with open(HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Insert Appendix D before Appendix E
appendix_e_marker = '    <section class="chapter-section" id="apx-e">'
if appendix_e_marker in content:
    content = content.replace(appendix_e_marker, appendix_d + "\n" + appendix_e_marker, 1)
    print("✅ Appendix D inserted before Appendix E")
else:
    print("❌ Appendix E marker not found!")

# Insert exam-overview before Part 1 (the first MCQ section)
exam_marker = '    <!-- ═══════════════ PART 1 ═══════════════ -->'
if exam_marker in content:
    content = content.replace(exam_marker, exam_overview + "\n\n" + exam_marker, 1)
    print("✅ exam-overview inserted before Part 1")
else:
    print("❌ Part 1 marker not found!")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("\n🎉 Appendix D + exam-overview inserted!")
