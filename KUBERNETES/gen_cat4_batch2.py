#!/usr/bin/env python3
"""Generate Category 4: Network Observability — Batch 2: S58-S60"""
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

# ======================== S58 ========================
s58 = sc(58,
    "Export Hubble Flows to JSON and Analyze with jq",
    "You need to programmatically analyze anihpj traffic patterns. Hubble's terminal output is human-readable but <strong>not machine-parseable</strong>. Your job: export flows to JSON and use jq to extract specific insights about anihpj traffic (top talkers, verdict distribution, latency patterns).",
    """<span class="token comment"># Deploy anihpj and generate traffic</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api --replicas=2
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># Generate multiple requests</span>
for i in $(seq 20); do
  kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true
done

<span class="token comment"># ❌ BUG: Default text output is hard to parse</span>
hubble observe -n anihpj
<span class="token comment"># Human-readable but can't filter, count, or aggregate with jq</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble flows visible: <code>hubble observe -n anihpj</code> → FORWARDED flows seen ✅"),
        ("pass", "<strong>2.</strong> Traffic is flowing: <code>kubectl exec -n anihpj deploy/web -- wget http://api:80</code> → 200 OK ✅"),
        ("fail", "<strong>3.</strong> Default output is unstructured: <code>hubble observe -n anihpj | wc -l</code> → <strong>hundreds of text lines, cannot count by verdict</strong> ❌"),
        ("fail", "<strong>4.</strong> Cannot extract top source pods: <strong>text output requires manual parsing, no way to group/count</strong> ❌"),
        ("fail", "<strong>5.</strong> Cannot calculate latency percentiles: <strong>text output lacks structured latency fields for analysis</strong> ❌"),
    ],
    [
        (1, "Use JSON output format:", "hubble observe -n anihpj -o json", "discovery", "Each flow becomes a structured JSON object with time, source, destination, verdict, l4, l7, and summary fields"),
        (2, "Extract verdict distribution:", "hubble observe -n anihpj -o json | jq -r '.flow.verdict' | sort | uniq -c", "discovery", "Count of FORWARDED vs DROPPED flows — reveals policy impact"),
        (3, "Find top source pods:", "hubble observe -n anihpj -o json | jq -r '.flow.source.pod_name' | sort | uniq -c | sort -rn", "discovery", "Identifies which pods generate the most traffic"),
        (4, "Analyze L7 HTTP metrics:", "hubble observe -n anihpj -o json | jq '.flow.l7' | jq 'select(. != null)' | jq -r '.http.method + \" \" + .http.url'", "discovery", "Extracts HTTP method, path, and status code from L7 flows"),
        (5, "Root cause identified:", "Default text output is for human reading only", "root-cause", "Without -o json, Hubble output cannot be piped to jq for structured analysis; JSON mode unlocks programmatic traffic analysis"),
    ],
    """<span class="token comment"># Fix: Export to JSON and analyze with jq</span>

<span class="token comment"># 1. Count flows by verdict</span>
hubble observe -n anihpj -o json | jq -r '.flow.verdict' | sort | uniq -c

<span class="token comment"># 2. Top source pods by flow count</span>
hubble observe -n anihpj -o json | jq -r '.flow.source.pod_name' | sort | uniq -c | sort -rn | head -10

<span class="token comment"># 3. Extract HTTP status codes from L7 flows</span>
hubble observe -n anihpj -o json | jq 'select(.flow.l7.type == "RESPONSE") | .flow.l7.http' | jq -r '[.status, .method, .url] | @tsv'

<span class="token comment"># 4. Calculate average latency (forward direction)</span>
hubble observe -n anihpj -o json | jq '[.flow.traffic_direction] | length'

<span class="token comment"># 5. Export to file for offline analysis</span>
hubble observe -n anihpj --last 1000 -o json > anihpj-flows.json""",
    "Structured Flow Analysis with JSON + jq",
    "Using <code>-o json</code> with jq, flows can now be filtered, counted, grouped, and aggregated. Top talkers, verdict distribution, HTTP method/status breakdown, and latency analysis are all available for programmatic consumption.",
    ["Default text output is unstructured", "Switch to -o json for JSON output", "jq extracts .flow.verdict for verdict counting", "jq groups by .flow.source.pod_name for top talkers", "jq selects L7 HTTP fields for method/status analysis"],
    "Hubble JSON output is the gateway to programmatic observability. Every flow becomes a JSON object with <code>.flow</code>, <code>.node_name</code>, <code>.time</code>, and nested <code>.l4</code>/<code>.l7</code> fields. Use <code>jq</code> selectors to count verdicts, group by source/destination, filter by protocol, and extract L7 HTTP/Kafka/DNS details. For large datasets, use <code>--last N</code> to limit flows and <code>-o jsonpb</code> for streaming output.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE             DESTINATION        VERDICT\n12:00:01  anihpj/web-xxx:45678  anihpj/api:80       FORWARDED\n12:00:02  anihpj/web-yyy:34567  anihpj/api:80       FORWARDED\n... (unstructured — cannot count by verdict)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj | grep -c FORWARDED\n<span class="output">grep: unreliable — depends on text format, misses context</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj -o json | jq -r \'.flow.verdict\' | sort | uniq -c\n<span class="output">    47 FORWARDED\n     3 DROPPED       ✅ Clear verdict distribution</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj -o json | jq -r \'.flow.source.pod_name\' | sort | uniq -c | sort -rn\n<span class="output">    25 anihpj/web-xxx\n    18 anihpj/web-yyy\n     7 anihpj/api-xxx    ✅ Top talkers identified</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj -o json | jq \'select(.flow.l7.type == "RESPONSE") | .flow.l7.http\' | jq -r \'[.status, .method, .url] | @tsv\'\n<span class="output">200     GET     /api/jobs\n200     GET     /api/jobs\n404     POST    /admin     ✅ HTTP breakdown</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> ls -la anihpj-flows.json\n<span class="output">-rw-r--r-- 1 user user 245K Dec 16 12:05 anihpj-flows.json    ✅ Exported for offline analysis</span></div>',
    ]
)

# ======================== S59 ========================
s59 = sc(59,
    "Deploy Hubble UI and Access anihpj Service Map",
    "You want to visualize anihpj's network traffic using the Hubble UI Service Map. Hubble is enabled but the <strong>Hubble UI is not accessible</strong>. Your job: deploy the Hubble UI, expose it, and verify the anihpj Service Map shows traffic flows.",
    """<span class="token comment"># Deploy anihpj with traffic</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api --replicas=2
kubectl create deployment db -n anihpj --image=postgres:15 -l app=anihpj,tier=db
kubectl expose deployment api -n anihpj --port=80
kubectl expose deployment db -n anihpj --port=5432

<span class="token comment"># Generate traffic</span>
for i in $(seq 30); do
  kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true
  kubectl exec -n anihpj deploy/api -- nc -zv db 5432 2>&1 || true
done

<span class="token comment"># ❌ BUG: Hubble UI not accessible</span>
cilium hubble ui
<span class="token comment"># Error: Unable to connect or UI not deployed</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble enabled: <code>kubectl get cm -n kube-system cilium-config -o yaml | grep enable-hubble</code> → \"true\" ✅"),
        ("pass", "<strong>2.</strong> Hubble Relay running: <code>kubectl get pods -n kube-system -l k8s-app=hubble-relay</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Start Hubble UI: <code>cilium hubble ui</code> → <strong>Error: no Hubble UI deployment found</strong> ❌"),
        ("fail", "<strong>4.</strong> Check Hubble UI deployment: <code>kubectl get deploy -n kube-system -l k8s-app=hubble-ui</code> → <strong>No resources found</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble UI not installed: the UI component is separate from Relay and must be explicitly deployed ❌"),
    ],
    [
        (1, "Check if Hubble UI is deployed:", "kubectl get all -n kube-system -l k8s-app=hubble-ui", "discovery", "No resources — Hubble UI not installed; it is a separate component from Hubble Relay"),
        (2, "Check Helm values for Hubble UI:", "helm get values cilium -n kube-system | grep -A5 hubble.ui", "discovery", "hubble.ui.enabled: false — UI was not enabled during Cilium installation"),
        (3, "Enable Hubble UI via Helm upgrade:", "helm upgrade cilium cilium/cilium -n kube-system --reuse-values --set hubble.ui.enabled=true", "discovery", "Helm upgrade adds the Hubble UI Deployment, Service, and RBAC resources"),
        (4, "Alternative: Use cilium CLI to enable:", "cilium hubble enable --ui", "discovery", "The cilium CLI can enable Hubble UI if Hubble was enabled via CLI"),
        (5, "Root cause identified:", "Hubble UI is an optional component not installed by default", "root-cause", "Hubble UI must be explicitly enabled via Helm (hubble.ui.enabled=true) or cilium CLI; without it, there is no web frontend for the Service Map"),
    ],
    """<span class="token comment"># Fix 1: Enable Hubble UI via Helm</span>
helm upgrade cilium cilium/cilium -n kube-system \\
  --reuse-values \\
  --set hubble.ui.enabled=true \\
  --set hubble.ui.service.type=ClusterIP

<span class="token comment"># Wait for Hubble UI to be ready</span>
kubectl wait --for=condition=available deploy/hubble-ui -n kube-system --timeout=120s

<span class="token comment"># Fix 2: Access Hubble UI (port-forward)</span>
kubectl port-forward -n kube-system svc/hubble-ui 8081:80 &

<span class="token comment"># Or use cilium CLI</span>
cilium hubble ui""",
    "Hubble UI Service Map Shows anihpj Traffic",
    "After enabling <code>hubble.ui.enabled=true</code> and deploying the UI, the Hubble UI Service Map visualizes anihpj traffic. Web→API flows appear as green (FORWARDED) lines. The dependency graph shows web, api, and db nodes with real-time traffic metrics.",
    ["cilium hubble ui → Error: not deployed", "kubectl get deploy hubble-ui → not found", "Helm values: hubble.ui.enabled=false", "helm upgrade with hubble.ui.enabled=true", "port-forward → Service Map shows anihpj"],
    "Hubble UI is a separate optional component from Hubble Relay. The Relay aggregates flows; the UI visualizes them. Always verify <code>hubble.ui.enabled=true</code> in Helm values. For production, consider exposing Hubble UI via Cilium Ingress (with auth) instead of port-forward. The Service Map uses color coding: <strong>green</strong> = FORWARDED, <strong>red</strong> = DROPPED, <strong>yellow</strong> = error responses.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium hubble ui\n<span class="output">🔭 Opening Hubble UI...\nError: Unable to connect to Hubble UI: deployment "hubble-ui" not found in namespace "kube-system"\nRun "cilium hubble enable --ui" to deploy it.</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get deploy,svc -n kube-system -l k8s-app=hubble-ui\n<span class="output">No resources found in kube-system namespace.    ← UI not installed!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> helm get values cilium -n kube-system | grep -A3 "hubble.ui"\n<span class="output">hubble:\n  ui:\n    enabled: false      ← UI explicitly disabled</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get deploy,svc -n kube-system -l k8s-app=hubble-ui\n<span class="output">NAME                         READY   UP-TO-DATE   AVAILABLE   AGE\ndeployment.apps/hubble-ui    1/1     1            1           30s\nNAME                 TYPE        CLUSTER-IP     PORT(S)   AGE\nservice/hubble-ui    ClusterIP   10.96.100.50   80/TCP    30s    ✅ UI deployed!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium hubble ui\n<span class="output">🔭 Opening Hubble UI...\nForwarding from 0.0.0.0:12000 -> 80\nWeb UI is available at http://localhost:12000    ✅ Service Map accessible!</span></div>',
    ]
)

# ======================== S60 ========================
s60 = sc(60,
    "Debug Hubble Relay Not Connecting to Peer Service",
    "Hubble Relay is deployed but <strong>fails to connect to Hubble peers</strong>. hubble observe returns 'connection refused' or 'unavailable'. Your job: diagnose why Hubble Relay cannot discover or connect to the Cilium agent Hubble gRPC endpoints.",
    """<span class="token comment"># Deploy anihpj and try to observe</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine
kubectl expose deployment web -n anihpj --port=80

<span class="token comment"># ❌ BUG: Hubble Relay unavailable</span>
hubble observe -n anihpj
<span class="token comment"># Error: rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing: dial tcp: connect: connection refused"</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble Relay pod running: <code>kubectl get pods -n kube-system -l k8s-app=hubble-relay</code> → Running ✅"),
        ("pass", "<strong>2.</strong> Cilium agents running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → All Running ✅"),
        ("fail", "<strong>3.</strong> Try to observe: <code>hubble observe -n anihpj</code> → <strong>rpc error: Unavailable, connection refused</strong> ❌"),
        ("fail", "<strong>4.</strong> Check Hubble Relay logs: <code>kubectl logs -n kube-system deploy/hubble-relay</code> → <strong>failed to connect to peer service</strong> ❌"),
        ("fail", "<strong>5.</strong> Check peer service: <code>kubectl get endpoints -n kube-system hubble-peer</code> → <strong>&lt;none&gt; — No peer endpoints!</strong> ❌"),
    ],
    [
        (1, "Check Hubble peer service:", "kubectl describe svc -n kube-system hubble-peer", "discovery", "Service exists but has no endpoints — no Cilium agents are registered as Hubble peers"),
        (2, "Check if Hubble is enabled on agents:", "kubectl exec -n kube-system ds/cilium -- cilium status | grep -i hubble", "discovery", "Hubble: Disabled — agents are not running Hubble gRPC server on port 4244"),
        (3, "Verify Hubble socket on agent:", "kubectl exec -n kube-system ds/cilium -- ls -la /var/run/cilium/hubble.sock", "discovery", "No such file — Hubble socket was never created because Hubble is disabled"),
        (4, "Check Relay TLS config:", "kubectl logs -n kube-system deploy/hubble-relay | grep -i tls", "discovery", "TLS handshake error: Hubble Relay expects TLS but agents don't have TLS configured — or vice versa"),
        (5, "Root cause identified:", "Hubble Relay needs Hubble-enabled agents to connect to via hubble-peer service", "root-cause", "Either enable-hubble is false on agents (no gRPC server on port 4244) OR TLS configuration mismatch between Relay and agents prevents the connection"),
    ],
    """<span class="token comment"># Fix 1: Enable Hubble on Cilium agents</span>
kubectl patch configmap -n kube-system cilium-config \\
  --patch '{"data":{"enable-hubble":"true"}}'

<span class="token comment"># Fix 2: Restart agents so they start Hubble gRPC server</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system

<span class="token comment"># Fix 3: Verify peer endpoints register</span>
kubectl wait --for=jsonpath='{.subsets[0].addresses[0].ip}' \\
  endpoints/hubble-peer -n kube-system --timeout=120s

<span class="token comment"># Fix 4: Restart Hubble Relay to connect to new peers</span>
kubectl rollout restart deploy/hubble-relay -n kube-system
kubectl wait --for=condition=available deploy/hubble-relay -n kube-system --timeout=120s

<span class="token comment"># Fix 5: If TLS mismatch, check certificates</span>
kubectl get secret -n kube-system hubble-relay-client-certs
kubectl get secret -n kube-system hubble-server-certs""",
    "Hubble Relay Connected and Serving Flows",
    "After enabling Hubble on agents and restarting Relay, hubble-peer Service has endpoints (one per Cilium agent), Hubble Relay connects successfully, and <code>hubble observe</code> returns flows from all nodes. The Relay aggregates flows from all peered agents.",
    ["hubble observe → Unavailable / connection refused", "Hubble Relay logs: failed to connect to peer", "hubble-peer endpoints → <none>", "enable-hubble: false in ConfigMap", "Enable Hubble → Restart agents → Restart Relay → Peers register"],
    "Hubble Relay acts as a <strong>multi-node flow aggregator</strong>. It discovers Hubble gRPC servers on Cilium agents via the <code>hubble-peer</code> Kubernetes Service (headless, port 4244). Each Cilium agent registers as a peer endpoint when Hubble is enabled. Relay then establishes gRPC streams to all peers and aggregates flows. If any peer is unreachable, Relay logs the error but continues serving from available peers.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing: dial tcp: connect: connection refused"\nLevel 11: connection to gRPC server failed</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system deploy/hubble-relay | tail -5\n<span class="output">level=error msg="Failed to connect to peer" peer=10.0.1.5:4244 error="dial tcp: connect: connection refused"\nlevel=error msg="Failed to connect to peer" peer=10.0.2.7:4244 error="dial tcp: connect: connection refused"</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n kube-system hubble-peer\n<span class="output">NAME          ENDPOINTS   AGE\nhubble-peer   &lt;none&gt;      15m    ← No agents registered as peers</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- cilium status | grep -i hubble\n<span class="output">Hubble:   Disabled    ← Agents not running Hubble gRPC</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n kube-system hubble-peer\n<span class="output">NAME          ENDPOINTS                       AGE\nhubble-peer   10.0.1.5:4244,10.0.2.7:4244     30s    ✅ Agents registered!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system deploy/hubble-relay | tail -3\n<span class="output">level=info msg="Connected to peer" peer=10.0.1.5:4244\nlevel=info msg="Connected to peer" peer=10.0.2.7:4244    ✅ Relay connected!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE             DESTINATION        VERDICT\n12:05:01.123        anihpj/web-xxx     anihpj/api:80      FORWARDED    ✅ Flows flowing!</span></div>',
    ]
)

# ====== Assemble and insert ======
all_scenarios = s58 + '\n\n' + s59 + '\n\n' + s60

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
else:
    print("ERROR: Could not find appendices insertion point!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)

print("✅ Batch 2 (S58-S60) inserted successfully!")
print(f"File size: {len(html.encode('utf-8'))} bytes")
