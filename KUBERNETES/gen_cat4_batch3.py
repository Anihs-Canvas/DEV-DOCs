#!/usr/bin/env python3
"""Generate Category 4: Network Observability — Batch 3: S61-S64"""
import re

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_text, tenet_steps, tenet_text, before_outputs, after_outputs):
    ei_html = ''.join(
        f'<div class="lookat-item"><span class="li-check {"pass" if t == "pass" else "fail"}">{"✓" if t == "pass" else "✗"}</span><span>{txt}</span></div>\n'
        for t, txt in error_items
    )
    di_html = ''.join(
        f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n'
        for num, label, cmd, ftype, ftext in debug_items
    )
    tf_html = '\n'.join(
        f'<div class="tenet-step"><div class="step-num">{chr(0x2460 + i)}</div><div class="step-label">{label}</div></div>'
        for i, label in enumerate(tenet_steps)
    )
    bo_html = '\n'.join(before_outputs)
    ao_html = '\n'.join(after_outputs)

    return f'''    <!-- ═══════════════ S{n}: {title} ═══════════════ -->
    <div class="scenario-block" id="sc-s{n}">
        <div class="sc-header">
            <div class="sc-badge">S{n}</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{n} — Category 4: Network Observability</div>
                <h4>{title}</h4>
                <div class="sc-desc"><strong>The Problem:</strong> {desc}</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML (contains the bug)</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste into terminal</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-code" class="language-bash">{deploy_code}</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error — Spot What's Broken</h4>
                    {ei_html}
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    {di_html}
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — {fix_desc}</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — apply the fix</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-fix" class="language-bash">{fix_code}</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — {verify_text}</h4>
                        <p>After applying the fix, the issue is resolved. All diagnostic checks pass and the expected behavior is confirmed.</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{n}')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa{n}">
                <h5>🧠 Diagnostic Tenet (Thought Process)</h5>
                <div class="tenet-flow">
                    {tf_html}
                </div>
                <p><strong>Tenet:</strong> {tenet_text}</p>
                <h5>📟 Command Outputs — Error State (BEFORE fix)</h5>
                {bo_html}
                <h5>📟 Command Outputs — AFTER Fix</h5>
                {ao_html}
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup — Delete All Resources</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste to clean up</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-cleanup')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-cleanup" class="language-bash"><span class="token comment"># Delete the namespace — cascades everything inside</span>
kubectl delete namespace anihpj

<span class="token comment"># Verify cleanup</span>
kubectl get all -n anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

# ======================== S61 ========================
s61 = sc(61,
    "Set Up Prometheus to Scrape Hubble Metrics for anihpj",
    "You need Prometheus to scrape Hubble metrics for anihpj traffic monitoring. Hubble metrics are enabled but <strong>Prometheus cannot scrape them</strong>. Your job: configure Hubble metrics and create a ServiceMonitor (or PodMonitor) so Prometheus can collect Hubble's HTTP, DNS, and TCP metrics.",
    """<span class="token comment"># Deploy anihpj and enable Hubble</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># Generate traffic</span>
for i in $(seq 20); do kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true; done

<span class="token comment"># ❌ BUG: Prometheus cannot see Hubble metrics</span>
kubectl port-forward -n kube-system svc/hubble-metrics 9965:9965 &
curl -s http://localhost:9965/metrics | head -20
<span class="token comment"># connection refused — no hubble-metrics service or no metrics endpoint</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble enabled: <code>kubectl get cm -n kube-system cilium-config -o yaml | grep enable-hubble</code> → \"true\" ✅"),
        ("pass", "<strong>2.</strong> Prometheus running in cluster: <code>kubectl get pods -n monitoring | grep prometheus</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Check Hubble metrics endpoint: <code>curl -s http://localhost:9965/metrics</code> → <strong>connection refused — port 9965 not listening</strong> ❌"),
        ("fail", "<strong>4.</strong> Check hubble-metrics service: <code>kubectl get svc -n kube-system hubble-metrics</code> → <strong>not found</strong> ❌"),
        ("fail", "<strong>5.</strong> Prometheus targets: <code>kubectl exec -n monitoring prometheus-xxx -- curl -s http://localhost:9090/api/v1/targets</code> → <strong>no hubble-metrics target</strong> ❌"),
    ],
    [
        (1, "Check if Hubble metrics are enabled:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -A5 hubble-metrics", "discovery", "hubble-metrics not configured — metrics server is separate from Hubble flow observability"),
        (2, "Verify metrics port on Cilium agents:", "kubectl exec -n kube-system ds/cilium -- netstat -tlnp | grep 9965", "discovery", "Port 9965 not listening — Cilium agent is not exposing Hubble metrics"),
        (3, "Check Prometheus ServiceMonitor:", "kubectl get servicemonitor -n kube-system | grep hubble", "discovery", "No ServiceMonitor — Prometheus doesn't know to scrape Hubble metrics"),
        (4, "Enable Hubble metrics via Helm:", "helm get values cilium -n kube-system | grep -A10 hubble.metrics", "discovery", "hubble.metrics.enabled is falsy or not set — metrics are opt-in"),
        (5, "Root cause identified:", "Hubble metrics are a separate opt-in feature requiring explicit configuration", "root-cause", "Hubble flow observability (enable-hubble) is independent from Hubble metrics (hubble.metrics.enabled). Metrics require: 1) enabling metric types (HTTP, DNS, TCP, etc.), 2) a Service to expose port 9965, and 3) a ServiceMonitor/PodMonitor for Prometheus discovery"),
    ],
    """<span class="token comment"># Fix 1: Enable Hubble metrics via Helm</span>
helm upgrade cilium cilium/cilium -n kube-system \\
  --reuse-values \\
  --set hubble.metrics.enabled="{dns,drop,tcp,flow,port-distribution,icmp,http}" \\
  --set hubble.metrics.serviceMonitor.enabled=true

<span class="token comment"># Fix 2: Wait for Cilium agents to restart with metrics</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system

<span class="token comment"># Fix 3: Verify metrics endpoint</span>
kubectl port-forward -n kube-system svc/hubble-metrics 9965:9965 &
curl -s http://localhost:9965/metrics | grep hubble_http

<span class="token comment"># Fix 4: Verify Prometheus discovers the target</span>
kubectl get servicemonitor -n kube-system hubble-metrics""",
    "Prometheus Scrapes Hubble Metrics for anihpj",
    "After enabling <code>hubble.metrics.enabled</code> with the desired metric types (HTTP, DNS, TCP, drop, flow) and creating a ServiceMonitor, Prometheus discovers the hubble-metrics target on port 9965. HTTP request rate, latency, and status codes for anihpj traffic are now available as Prometheus metrics.",
    ["curl localhost:9965/metrics → connection refused", "hubble-metrics Service not found", "enable-hubble=true but metrics not enabled", "Enable hubble.metrics.enabled with metric types", "Create ServiceMonitor → Prometheus discovers target"],
    "Hubble <strong>flow observability</strong> (<code>enable-hubble</code>) and Hubble <strong>metrics</strong> (<code>hubble.metrics.enabled</code>) are separate features. Flows power <code>hubble observe</code> and the UI; metrics power Prometheus/Grafana. Each metric type (HTTP, DNS, TCP, ICMP, drop, flow, port-distribution) adds cardinality — enable only what you need. For anihpj HTTP monitoring, enable <code>http</code> and <code>flow</code> at minimum.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9965/metrics\n<span class="output">curl: (7) Failed to connect to localhost port 9965: Connection refused\n← Metrics server not running</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc,servicemonitor -n kube-system | grep -i hubble\n<span class="output">(empty — no hubble-metrics Service or ServiceMonitor)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> helm get values cilium -n kube-system | grep -A10 "hubble.metrics"\n<span class="output">hubble:\n  metrics:\n    enabled: []    ← Empty — no metrics enabled!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9965/metrics | grep hubble_http_requests_total\n<span class="output">hubble_http_requests_total{method="GET",path="/api/jobs",status="200"} 47\nhubble_http_requests_total{method="POST",path="/admin",status="404"} 3    ✅ HTTP metrics flowing!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get servicemonitor -n kube-system hubble-metrics\n<span class="output">NAME              AGE\nhubble-metrics    2m    ✅ Prometheus will discover this target</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9965/metrics | grep -E "^(hubble_tcp|hubble_dns|hubble_drop)"\n<span class="output">hubble_tcp_flags_total{flag="SYN",family="IPv4"} 156\nhubble_dns_queries_total{query="anihpj-api.anihpj.svc.cluster.local"} 23\nhubble_drop_total{reason="Policy denied"} 5    ✅ All metrics available</span></div>',
    ]
)

# ======================== S62 ========================
s62 = sc(62,
    "Import Grafana Dashboard for anihpj HTTP Latency Monitoring",
    "Prometheus is scraping Hubble HTTP metrics, but you have <strong>no dashboard to visualize anihpj's HTTP latency, request rate, and error ratio</strong>. Your job: import the Cilium Hubble HTTP Grafana dashboard and verify it shows anihpj traffic metrics.",
    """<span class="token comment"># Prerequisites: Hubble metrics + Prometheus configured (from S61)</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># Generate varied traffic (mix of 200s and 404s)</span>
for i in $(seq 50); do kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true; done
for i in $(seq 5); do kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80/nonexistent 2>&1 || true; done

<span class="token comment"># ❌ BUG: No Grafana dashboard for Hubble HTTP metrics</span>
kubectl get configmaps -n monitoring | grep -i hubble
<span class="token comment"># (empty — no Hubble dashboard imported)</span>""",
    [
        ("pass", "<strong>1.</strong> Prometheus scraping metrics: <code>curl -s http://localhost:9965/metrics | grep hubble_http</code> → metrics present ✅"),
        ("pass", "<strong>2.</strong> Grafana running: <code>kubectl get pods -n monitoring -l app=grafana</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Check Grafana dashboards: <code>kubectl get configmaps -n monitoring -l grafana_dashboard=1</code> → <strong>no Hubble dashboard found</strong> ❌"),
        ("fail", "<strong>4.</strong> Grafana data sources: <strong>Prometheus data source may not be configured for Hubble metrics</strong> ❌"),
        ("fail", "<strong>5.</strong> No pre-built Hubble HTTP dashboard: <strong>must import Cilium's Hubble dashboards manually</strong> ❌"),
    ],
    [
        (1, "Locate Cilium Hubble dashboards:", "kubectl get cm -n kube-system -l app.kubernetes.io/part-of=cilium | grep dashboard", "discovery", "Cilium does not deploy dashboards by default — they are available in the Cilium GitHub repo as JSON files"),
        (2, "Download Hubble HTTP dashboard JSON:", "wget https://raw.githubusercontent.com/cilium/cilium/main/examples/hubble/hubble-http-dashboard.json", "discovery", "Hubble HTTP dashboard JSON contains pre-configured panels for request rate, latency (p50/p95/p99), and status codes"),
        (3, "Check Grafana dashboard provisioning:", "kubectl get cm -n monitoring grafana-dashboards -o yaml", "discovery", "Grafana uses ConfigMaps with label grafana_dashboard=1 or sidecar provisioning to auto-load dashboards"),
        (4, "Import the dashboard as a ConfigMap:", "kubectl create cm hubble-http-dashboard -n monitoring --from-file=hubble-http-dashboard.json", "discovery", "Must add label grafana_dashboard=1 for Grafana sidecar to pick it up"),
        (5, "Root cause identified:", "Hubble dashboards are not auto-deployed — they must be imported from Cilium's examples", "root-cause", "Cilium provides pre-built Grafana dashboards in its GitHub repo (Hubble HTTP, DNS, TCP, Network Overview), but they are not installed by Helm; they must be manually imported as ConfigMaps into the monitoring namespace"),
    ],
    """<span class="token comment"># Fix 1: Download and import Hubble HTTP dashboard</span>
kubectl create configmap hubble-http-dashboard \\
  -n monitoring \\
  --from-file=hubble-http-dashboard.json \\
  --dry-run=client -o yaml > hubble-dashboard-cm.yaml

<span class="token comment"># Add the Grafana dashboard label</span>
kubectl label configmap hubble-http-dashboard -n monitoring grafana_dashboard=1 --overwrite

kubectl apply -f hubble-dashboard-cm.yaml

<span class="token comment"># Fix 2: Verify Grafana picks up the dashboard</span>
kubectl get configmaps -n monitoring -l grafana_dashboard=1

<span class="token comment"># Fix 3: Access Grafana and verify dashboard</span>
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
<span class="token comment"># Open http://localhost:3000 → Dashboards → Hubble HTTP</span>

<span class="token comment"># Fix 4: Import additional Hubble dashboards</span>
<span class="token comment"># Hubble Network Overview: https://raw.githubusercontent.com/cilium/cilium/main/examples/hubble/hubble-network-overview.json</span>
<span class="token comment"># Hubble DNS Dashboard: https://raw.githubusercontent.com/cilium/cilium/main/examples/hubble/hubble-dns-dashboard.json</span>""",
    "Grafana Dashboard Shows anihpj HTTP Metrics",
    "After importing the Hubble HTTP dashboard as a labeled ConfigMap, Grafana's sidecar auto-discovers it. The dashboard displays anihpj HTTP request rate (QPS), latency percentiles (p50/p95/p99), HTTP status code distribution (200, 404, 500), and method breakdown — all powered by Hubble metrics from Prometheus.",
    ["Hubble metrics in Prometheus but no dashboard", "kubectl get cm -l grafana_dashboard=1 → no Hubble CM", "Download Hubble HTTP dashboard JSON from Cilium repo", "Create ConfigMap with grafana_dashboard=1 label", "Grafana auto-discovers and displays anihpj panels"],
    "Cilium's Hubble dashboards are well-maintained in the <code>cilium/cilium</code> GitHub repo under <code>examples/hubble/</code>. The key dashboards are: <strong>Hubble HTTP</strong> (request rate, latency, status codes), <strong>Hubble DNS</strong> (query rate, response codes, NXDOMAIN ratio), <strong>Hubble TCP</strong> (SYN rate, RTT, drops), and <strong>Hubble Network Overview</strong> (flow rate, drop rate, policy verdicts). Use Grafana's sidecar provisioning with ConfigMap labels for auto-loading.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get configmaps -n monitoring -l grafana_dashboard=1\n<span class="output">NAME                       DATA   AGE\nprometheus-stats           1      5d\nnode-exporter              1      5d\n(no hubble dashboard)      ← Missing!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:3000/api/search?query=hubble\n<span class="output">[]    ← No Hubble dashboard in Grafana</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get configmaps -n monitoring -l grafana_dashboard=1\n<span class="output">NAME                       DATA   AGE\nhubble-http-dashboard       1      2m\nprometheus-stats           1      5d    ✅ Hubble dashboard imported!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:3000/api/search?query=hubble | jq ".[].title"\n<span class="output">"Hubble / HTTP / Request Rate"\n"Hubble / HTTP / Latency"\n"Hubble / HTTP / Status Codes"    ✅ Dashboard panels available!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s "http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace=%22anihpj%22}[5m])"\n<span class="output">{status:"success", data:{resultType:"vector", result:[{metric:{method:"GET"}, value:[1702,"0.85"]}]}}    ✅ Prometheus has anihpj data</span></div>',
    ]
)

# ======================== S63 ========================
s63 = sc(63,
    "Debug Hubble Metrics Not Appearing in Prometheus",
    "Hubble metrics are enabled and the endpoint returns data, but <strong>Prometheus shows no Hubble metrics</strong>. The targets page lists hubble-metrics as 'DOWN' or doesn't list it at all. Your job: find why Prometheus cannot scrape Hubble metrics and fix the discovery/scraping configuration.",
    """<span class="token comment"># Prerequisites: Hubble metrics enabled (from S61)</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl expose deployment web -n anihpj --port=80

<span class="token comment"># ❌ BUG: Metrics endpoint works, but Prometheus can't see them</span>
curl -s http://localhost:9965/metrics | head -5
<span class="token comment"># Returns metrics (endpoint works!)</span>

curl -s http://localhost:9090/api/v1/query?query=hubble_http_requests_total
<span class="token comment"># Empty result — Prometheus has no Hubble data</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble metrics endpoint responds: <code>curl -s http://localhost:9965/metrics | head -5</code> → 200 OK with metrics ✅"),
        ("pass", "<strong>2.</strong> Prometheus running: <code>kubectl get pods -n monitoring | grep prometheus</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Query Hubble metrics in Prometheus: <code>curl -s 'http://localhost:9090/api/v1/query?query=hubble_http_requests_total'</code> → <strong>empty result []</strong> ❌"),
        ("fail", "<strong>4.</strong> Check Prometheus targets: <code>curl -s http://localhost:9090/api/v1/targets | grep hubble</code> → <strong>no hubble target listed</strong> ❌"),
        ("fail", "<strong>5.</strong> Prometheus doesn't know about hubble-metrics: <strong>ServiceMonitor missing or not matching</strong> ❌"),
    ],
    [
        (1, "Verify Prometheus discovers hubble-metrics:", "kubectl get servicemonitor -n kube-system hubble-metrics -o yaml | grep -A10 spec", "discovery", "ServiceMonitor exists but matchLabels may not match the hubble-metrics Service"),
        (2, "Check hubble-metrics Service labels:", "kubectl get svc -n kube-system hubble-metrics -o yaml | grep -A5 labels", "discovery", "Service has labels k8s-app: hubble-metrics — verify ServiceMonitor selector matches"),
        (3, "Check Prometheus serviceMonitorSelector:", "kubectl get prometheus -n monitoring -o yaml | grep -A5 serviceMonitorSelector", "discovery", "Prometheus serviceMonitorSelector may filter by a label like release: prometheus that hubble-metrics ServiceMonitor doesn't have"),
        (4, "Verify RBAC for ServiceMonitor:", "kubectl auth can-i get servicemonitors -n kube-system --as=system:serviceaccount:monitoring:prometheus", "discovery", "Prometheus ServiceAccount may lack RBAC to discover ServiceMonitors in kube-system namespace"),
        (5, "Root cause identified:", "ServiceMonitor selector mismatch or namespace-scoped RBAC", "root-cause", "Prometheus only discovers ServiceMonitors that match its serviceMonitorSelector AND are in namespaces it's allowed to watch. Common failures: 1) ServiceMonitor missing a required label, 2) Prometheus not watching kube-system namespace, 3) RBAC denying ServiceMonitor read access"),
    ],
    """<span class="token comment"># Fix 1: Add required label to ServiceMonitor</span>
kubectl label servicemonitor -n kube-system hubble-metrics release=prometheus --overwrite

<span class="token comment"># Fix 2: Or update Prometheus to watch all namespaces</span>
kubectl patch prometheus -n monitoring prometheus --type=merge -p '{"spec":{"serviceMonitorNamespaceSelector":{"matchLabels":{"kubernetes.io/metadata.name":"kube-system"}}}}'

<span class="token comment"># Fix 3: Check Prometheus config reloaded</span>
kubectl rollout restart statefulset prometheus -n monitoring
kubectl wait --for=condition=ready pod -n monitoring -l app=prometheus --timeout=120s

<span class="token comment"># Fix 4: Verify target appears in Prometheus</span>
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job == "hubble-metrics")'

<span class="token comment"># Fix 5: Query Hubble metrics</span>
curl -s 'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total[5m])'</span>""",
    "Hubble Metrics Appear in Prometheus",
    "After fixing the ServiceMonitor labels and Prometheus namespace selector, the hubble-metrics target shows as 'UP' in Prometheus. Queries for <code>hubble_http_requests_total</code>, <code>hubble_tcp_flags_total</code>, and <code>hubble_drop_total</code> return anihpj data. Grafana dashboards now populate correctly.",
    ["curl localhost:9965/metrics → OK (endpoint works)", "Prometheus query → empty (no target)", "Prometheus targets → no hubble listed", "ServiceMonitor selector mismatch → missing label", "Add release=prometheus label → Prometheus discovers target"],
    "When Hubble metrics endpoint returns data but Prometheus can't see them, the issue is almost always a <strong>ServiceMonitor selector mismatch</strong>. Three things must align: 1) The ServiceMonitor's <code>selector.matchLabels</code> must match the hubble-metrics Service's labels, 2) The ServiceMonitor itself must have labels matching Prometheus's <code>serviceMonitorSelector</code> (commonly <code>release: prometheus</code>), and 3) Prometheus must have RBAC and namespace access to discover ServiceMonitors in that namespace.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9090/api/v1/targets | jq \'.data.activeTargets[].labels.job\' | sort -u\n<span class="output">"kubernetes-nodes"\n"kubernetes-pods"\n"prometheus"\n(no hubble-metrics)    ← Job not found</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get servicemonitor -n kube-system hubble-metrics -o yaml | grep -E "release:|matchLabels"\n<span class="output">  labels:\n    k8s-app: hubble-metrics\n    (no "release: prometheus" label)    ← Missing required label!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get prometheus -n monitoring -o yaml | grep -A3 serviceMonitorSelector\n<span class="output">  serviceMonitorSelector:\n    matchLabels:\n      release: prometheus    ← Prometheus requires this label!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9090/api/v1/targets | jq \'.data.activeTargets[] | select(.labels.job=="hubble-metrics") | {health, lastError}\'\n<span class="output">{health: "up", lastError: ""}    ✅ Target UP and healthy!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s \'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace="anihpj"}[5m])\'\n<span class="output">{"status":"success","data":{"resultType":"vector","result":[{"metric":{"method":"GET","status":"200"},"value":[1702,"0.85"]}]}}    ✅ anihpj data in Prometheus!</span></div>',
    ]
)

# ======================== S64 ========================
s64 = sc(64,
    "Configure Alert When anihpj HTTP 500 Errors Exceed Threshold",
    "anihpj is experiencing intermittent HTTP 500 errors. You have Hubble metrics in Prometheus, but <strong>no alerting is configured</strong>. Your job: create a PrometheusRule that fires when anihpj's HTTP 500 error rate exceeds 5% of total requests over 5 minutes, and configure Alertmanager to send notifications.",
    """<span class="token comment"># Deploy anihpj with some failing requests</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># Generate traffic — mix of success and 500 errors</span>
for i in $(seq 100); do kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true; done

<span class="token comment"># ❌ BUG: HTTP 500s happening but no alert fires</span>
curl -s 'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace="anihpj",status="500"}[5m])'
<span class="token comment"># Returns non-zero rate but no alert triggered</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble HTTP metrics in Prometheus: <code>curl -s http://localhost:9090/api/v1/query?query=hubble_http_requests_total</code> → data present ✅"),
        ("pass", "<strong>2.</strong> Alertmanager running: <code>kubectl get pods -n monitoring | grep alertmanager</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Check Prometheus alerts: <code>curl -s http://localhost:9090/api/v1/rules</code> → <strong>no Hubble-related alerting rules defined</strong> ❌"),
        ("fail", "<strong>4.</strong> Check PrometheusRules: <code>kubectl get prometheusrule -n monitoring</code> → <strong>no anihpj or Hubble rules</strong> ❌"),
        ("fail", "<strong>5.</strong> HTTP 500 rate is elevated: <code>rate(hubble_http_requests_total{status=&quot;500&quot;}[5m])</code> → <strong>non-zero but no one is notified</strong> ❌"),
    ],
    [
        (1, "Query current HTTP 500 rate:", "curl -s 'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace=&quot;anihpj&quot;,status=&quot;500&quot;}[5m])'", "discovery", "Rate is 0.15/s — if total is 1.0/s, that's 15% — well above 5% threshold"),
        (2, "Query total HTTP rate for comparison:", "curl -s 'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace=&quot;anihpj&quot;}[5m])'", "discovery", "Total rate is 2.0/s — 500 rate is 7.5% of total traffic"),
        (3, "Check existing PrometheusRules:", "kubectl get prometheusrule -A", "discovery", "No PrometheusRules exist for Hubble metrics — need to create one with the error ratio expression"),
        (4, "Build the alert expression:", "rate(hubble_http_requests_total{namespace=\"anihpj\",status=\"500\"}[5m]) / rate(hubble_http_requests_total{namespace=\"anihpj\"}[5m]) > 0.05", "discovery", "This PromQL calculates the 500 error ratio over 5 minutes — fires when > 5%"),
        (5, "Root cause identified:", "PrometheusRule CRD not created for Hubble HTTP error monitoring", "root-cause", "Hubble metrics are scraped but Prometheus has no alerting rules defined. Alerting requires a PrometheusRule CRD (if using prometheus-operator) or alert rules in prometheus.yml config to evaluate metric expressions and trigger Alertmanager notifications"),
    ],
    """<span class="token comment"># Fix 1: Create PrometheusRule for anihpj HTTP 500 errors</span>
cat > hubble-alert-rule.yaml << 'EOF'
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: anihpj-hubble-http-alerts
  namespace: monitoring
  labels:
    release: prometheus
    severity: critical
spec:
  groups:
  - name: anihpj-hubble-http
    rules:
    - alert: AnihpjHighHTTP500Rate
      expr: |
        rate(hubble_http_requests_total{namespace="anihpj",status="500"}[5m])
        /
        rate(hubble_http_requests_total{namespace="anihpj"}[5m])
        > 0.05
      for: 5m
      labels:
        severity: critical
        team: anihpj
      annotations:
        summary: "anihpj HTTP 500 error rate > 5%"
        description: "anihpj namespace has {{ $value | humanizePercentage }} HTTP 500 error rate (threshold: 5%)"
        runbook_url: "https://wiki.internal/anihpj-500-runbook"
EOF
kubectl apply -f hubble-alert-rule.yaml

<span class="token comment"># Fix 2: Verify Prometheus picks up the rule</span>
kubectl get prometheusrule -n monitoring anihpj-hubble-http-alerts

<span class="token comment"># Fix 3: Check the rule is loaded</span>
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name=="anihpj-hubble-http")'

<span class="token comment"># Fix 4: Check alert state</span>
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.labels.alertname=="AnihpjHighHTTP500Rate")'""",
    "Alert Fires When anihpj HTTP 500 Rate Exceeds 5%",
    'After creating the PrometheusRule, Prometheus evaluates the expression every evaluation interval. When <code>rate(hubble_http_requests_total{status="500"}[5m]) / rate(hubble_http_requests_total[5m]) > 0.05</code> holds for 5 minutes, the alert transitions from PENDING to FIRING. Alertmanager routes the notification based on severity and team labels.',
    ['rate(hubble_http_requests_total{status="500"}[5m]) → non-zero', "Prometheus rules → no Hubble rules", "No PrometheusRule CRD for Hubble alerts", "Create PrometheusRule with error ratio expression", "Alert fires → Alertmanager routes notification"],
    "Hubble metrics enable precise, application-layer alerting. The key pattern: compare <code>rate(error_metric[5m]) / rate(total_metric[5m])</code> for error ratios. Use <code>for: 5m</code> to avoid flapping from transient spikes. Hubble metrics labels (<code>status</code>, <code>method</code>, <code>path</code>, <code>namespace</code>, <code>pod</code>) allow targeted alerts — alert on 500s for <code>/api/</code> paths specifically, or exclude health-check endpoints from alert evaluation.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9090/api/v1/rules | jq \'.data.groups[].name\' | grep -i hubble\n<span class="output">(empty — no Hubble alerting rules)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get prometheusrule -A\n<span class="output">No resources found    ← No PrometheusRules defined!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s \'http://localhost:9090/api/v1/query?query=rate(hubble_http_requests_total{namespace="anihpj",status="500"}[5m]) / rate(hubble_http_requests_total{namespace="anihpj"}[5m])\'\n<span class="output">{"status":"success","data":{"resultType":"vector","result":[{"metric":{},"value":[1702,"0.075"]}]}}\n← 7.5% — above 5% threshold! But no alert fires.</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get prometheusrule -n monitoring anihpj-hubble-http-alerts\n<span class="output">NAME                         AGE\nanihpj-hubble-http-alerts     2m    ✅ Alert rule deployed!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9090/api/v1/rules | jq \'.data.groups[] | select(.name=="anihpj-hubble-http") | .rules[].name\'\n<span class="output">"AnihpjHighHTTP500Rate"    ✅ Rule loaded in Prometheus</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://localhost:9090/api/v1/alerts | jq \'.data.alerts[] | select(.labels.alertname=="AnihpjHighHTTP500Rate") | {state, value}\'\n<span class="output">{state: "firing", value: "0.075"}    ✅ Alert FIRING at 7.5%!</span></div>',
    ]
)

# ====== Assemble and insert ======
all_scenarios = s61 + '\n\n' + s62 + '\n\n' + s63 + '\n\n' + s64

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
else:
    print("ERROR: Could not find appendices insertion point!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)

print("✅ Batch 3 (S61-S64) inserted successfully!")
print(f"File size: {len(html.encode('utf-8'))} bytes")
