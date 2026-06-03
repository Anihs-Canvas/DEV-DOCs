#!/usr/bin/env python3
"""Generate Category 4: Network Observability — Batch 1: S55-S57"""
import re, textwrap

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_text, tenet_steps, tenet_text, before_outputs, after_outputs):
    """Generate a scenario block matching S1 reference exactly."""
    # error_items: list of (pass/fail, text)
    # debug_items: list of (num, step_label, command, finding_type, finding_text)
    #   finding_type: 'discovery' or 'root-cause'
    # tenet_steps: list of labels
    # before_outputs: list of cmd-output strings
    # after_outputs: list of cmd-output strings

    ei_html = ''.join(
        f'<div class="lookat-item"><span class="li-check {"pass" if t == "pass" else "fail"}">{"✓" if t == "pass" else "✗"}</span><span>{txt}</span></div>\n'
        for t, txt in error_items
    )

    di_html = ''.join(
        f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n'
        for num, label, cmd, ftype, ftext in debug_items
    )

    # Tenet flow
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

# ======================== S55 ========================
s55 = sc(55,
    "Deploy Hubble and Observe anihpj Flows in Real-Time",
    "You deployed anihpj but cannot see any network flows. Hubble is installed but <strong>not observing traffic for the anihpj namespace</strong>. Your job: enable Hubble and observe all anihpj flows in real-time.",
    """<span class="token comment"># Hubble is deployed but flows are empty for anihpj</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment api -n anihpj --port=80
kubectl expose deployment web -n anihpj --port=80

<span class="token comment"># Generate traffic</span>
kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true

<span class="token comment"># Try Hubble — ❌ BUG: no flows!</span>
hubble observe -n anihpj
<span class="token comment"># (empty output or "no flows")</span>""",
    [
        ("pass", "<strong>1.</strong> Hubble is running: <code>kubectl get pods -n kube-system | grep hubble</code> → Pods are present ✅"),
        ("pass", "<strong>2.</strong> Cilium agent is healthy: <code>cilium status</code> → OK ✅"),
        ("fail", "<strong>3.</strong> Observe anihpj namespace: <code>hubble observe -n anihpj</code> → <strong>EMPTY — no flows!</strong> ❌"),
        ("fail", "<strong>4.</strong> Observe all namespaces: <code>hubble observe</code> → flows from other namespaces but <strong>anihpj missing</strong> ❌"),
        ("fail", "<strong>5.</strong> Check Hubble Relay: <code>kubectl logs -n kube-system deploy/hubble-relay</code> → <strong>connection refused to peer service</strong> ❌"),
    ],
    [
        (1, "Check Hubble Relay status:", "kubectl get svc -n kube-system hubble-peer", "discovery", "hubble-peer Service has no endpoints — Relay cannot discover peers"),
        (2, "Check Hubble peer service endpoints:", "kubectl get endpoints -n kube-system hubble-peer", "discovery", "<none> — No Cilium agents registered as Hubble peers!"),
        (3, "Check if Hubble is enabled in Cilium:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -A2 hubble", "discovery", "enable-hubble: \"false\" — Hubble is DISABLED in ConfigMap"),
        (4, "Check Cilium agent Hubble socket:", "kubectl exec -n kube-system ds/cilium -- ls /var/run/cilium/hubble.sock", "discovery", "No such file — Hubble socket not created because Hubble is disabled"),
        (5, "Root cause identified:", "Hubble must be explicitly enabled in Cilium ConfigMap", "root-cause", "enable-hubble is set to \"false\" in cilium-config; the Hubble gRPC socket is never created, so Relay cannot aggregate flows"),
    ],
    """<span class="token comment"># Fix: Enable Hubble via Cilium ConfigMap</span>
kubectl patch configmap -n kube-system cilium-config \\
  --patch '{"data":{"enable-hubble":"true"}}'

<span class="token comment"># Restart Cilium agents to pick up the new config</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system

<span class="token comment"># Restart Hubble Relay</span>
kubectl rollout restart deploy/hubble-relay -n kube-system
kubectl wait --for=condition=available deploy/hubble-relay -n kube-system --timeout=120s

<span class="token comment"># Verify Hubble peers are registered</span>
kubectl get endpoints -n kube-system hubble-peer""",
    "Hubble Enabled and Observing anihpj Flows",
    "Hubble flows now display all anihpj traffic in real-time. FORWARDED and DROPPED flows are visible with source/destination pod, verdict, and protocol. The anihpj namespace is fully observable.",
    ["Deploy anihpj, generate traffic", "hubble observe -n anihpj → EMPTY", "Check hubble-peer endpoints → none", "enable-hubble: \"false\" in ConfigMap", "Patch ConfigMap → Restart agents"],
    "Always verify <code>enable-hubble</code> is set to <code>\"true\"</code> in the <code>cilium-config</code> ConfigMap. Without it, the Hubble gRPC socket is never created on Cilium agents, hubble-peer Service has no endpoints, and Hubble Relay cannot aggregate any flows — resulting in empty <code>hubble observe</code> output.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT\n(empty — no flows at all)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n kube-system hubble-peer\n<span class="output">NAME          ENDPOINTS   AGE\nhubble-peer   &lt;none&gt;      10m    ← No Cilium agents registered</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cm -n kube-system cilium-config -o yaml | grep enable-hubble\n<span class="output">enable-hubble: "false"    ← Hubble DISABLED!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n kube-system hubble-peer\n<span class="output">NAME          ENDPOINTS                       AGE\nhubble-peer   10.0.1.5:4244,10.0.2.7:4244     30s   ✅ Peers registered!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj --from-label app=web --to-label app=api\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT\n12:05:01.123        anihpj/web-xxx:45678     anihpj/api-xxx:80        FORWARDED\n12:05:02.456        anihpj/web-yyy:34567     anihpj/api-yyy:80        FORWARDED</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT   PROTO\n12:05:01.123        anihpj/web-xxx:45678     anihpj/api-xxx:80        FORWARDED TCP\n12:05:02.456        anihpj/web-yyy:34567     anihpj/api-yyy:80        FORWARDED TCP\n12:05:03.789        anihpj/api-xxx:54321     anihpj/anihpj-db:5432    FORWARDED TCP</span></div>',
    ]
)

# ======================== S56 ========================
s56 = sc(56,
    "Debug Hubble Showing No Flows for anihpj Namespace",
    "Hubble is enabled and works for other namespaces, but <strong>the anihpj namespace shows no flows</strong>. Pods are running and communicating, yet Hubble reports zero traffic. Your job: find why Hubble is blind to the anihpj namespace.",
    """<span class="token comment"># Hubble works for default namespace but NOT anihpj</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine
kubectl create deployment api -n anihpj --image=nginx:alpine
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># Generate traffic</span>
kubectl exec -n anihpj deploy/web -- wget -qO- http://api:80 2>&1 || true

<span class="token comment"># ❌ BUG: No flows for anihpj</span>
hubble observe -n anihpj
<span class="token comment"># (empty)</span>

<span class="token comment"># But other namespaces work!</span>
hubble observe -n default""",
    [
        ("pass", "<strong>1.</strong> Hubble enabled: <code>kubectl get cm -n kube-system cilium-config -o yaml | grep enable-hubble</code> → \"true\" ✅"),
        ("pass", "<strong>2.</strong> Hubble Relay running: <code>kubectl get pods -n kube-system | grep hubble-relay</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Observe anihpj: <code>hubble observe -n anihpj</code> → <strong>EMPTY!</strong> ❌"),
        ("fail", "<strong>4.</strong> Observe default namespace: <code>hubble observe -n default</code> → <strong>flows visible!</strong> So Hubble works but blind to anihpj ❌"),
        ("fail", "<strong>5.</strong> Check Cilium endpoints for anihpj: <code>kubectl get cep -n anihpj</code> → <strong>No CiliumEndpoints!</strong> ❌"),
    ],
    [
        (1, "Check if Cilium manages the namespace:", "kubectl get ns anihpj -o yaml | grep cilium", "discovery", "No Cilium annotations on namespace — namespace may be excluded from Cilium management"),
        (2, "Check CiliumEndpoint CRDs for anihpj:", "kubectl get cep -n anihpj", "discovery", "No resources found — Cilium is NOT managing endpoints in this namespace"),
        (3, "Check pod labels:", "kubectl get pods -n anihpj --show-labels", "discovery", "Pods are labeled but no io.cilium annotations — Cilium not injecting endpoints"),
        (4, "Verify Cilium is CNI for the node:", "kubectl get nodes -o yaml | grep -A5 annotations | grep cilium", "discovery", "Node has cilium.io annotations — Cilium IS the CNI, but the namespace might be excluded"),
        (5, "Root cause identified:", "Check namespace label io.cilium/network-policy", "root-cause", "The anihpj namespace is missing the Cilium namespace label; without it, Cilium does not create CiliumEndpoints or observe flows in that namespace"),
    ],
    """<span class="token comment"># Fix: Label the namespace so Cilium manages it</span>
kubectl label namespace anihpj io.cilium/network-policy=true --overwrite

<span class="token comment"># Recreate pods so Cilium creates CiliumEndpoints</span>
kubectl rollout restart deployment -n anihpj web api
kubectl wait --for=condition=ready pod -n anihpj -l app --timeout=120s

<span class="token comment"># Verify CiliumEndpoints created</span>
kubectl get cep -n anihpj""",
    "anihpj Flows Visible in Hubble",
    "After labeling the namespace with <code>io.cilium/network-policy=true</code> and restarting the pods, Cilium creates CiliumEndpoint CRDs for all anihpj pods. Hubble now observes and reports all flows in the anihpj namespace.",
    ["hubble observe -n anihpj → EMPTY", "hubble observe -n default → WORKS", "kubectl get cep -n anihpj → EMPTY", "Namespace missing io.cilium label", "Label namespace → Restart pods → Flows appear"],
    "Cilium only manages namespaces that carry its namespace label (typically <code>io.cilium/network-policy</code> or <code>io.cilium/auto-create-endpoints</code>). Without this label, even though Cilium is the CNI and routes pod traffic, it does not create CiliumEndpoint CRDs or observe flows via Hubble for pods in that namespace.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT\n(empty)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n default\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT\n12:05:01.123        default/nginx-xxx:45678   default/nginx-yyy:80    FORWARDED    ← Works!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cep -n anihpj\n<span class="output">No resources found in anihpj namespace.    ← Cilium not managing!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ns anihpj -o yaml | grep -E "labels:|io.cilium"\n<span class="output">  labels:\n    kubernetes.io/metadata.name: anihpj    ← Missing io.cilium label!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cep -n anihpj\n<span class="output">NAME         ENDPOINT ID   IDENTITY ID   IPV4        STATUS\nweb-xxx      1234          56789         10.0.1.10   ready    ✅\nweb-yyy      1235          56790         10.0.2.11   ready    ✅\napi-xxx      1236          56791         10.0.1.12   ready    ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE                   DESTINATION              VERDICT\n12:05:01.123        anihpj/web-xxx:45678     anihpj/api-xxx:80        FORWARDED\n12:05:02.456        anihpj/web-yyy:34567     anihpj/api-yyy:80        FORWARDED    ✅ Flows visible!</span></div>',
    ]
)

# ======================== S57 ========================
s57 = sc(57,
    "Filter Hubble Flows — Show Only DROPPED anihpj Traffic",
    "You suspect a CiliumNetworkPolicy is dropping traffic for anihpj. Hubble shows all flows (FORWARDED + DROPPED), but you need to <strong>filter only DROPPED flows</strong> to identify which specific connections are being denied. Your job: use Hubble filters to isolate dropped traffic.",
    """<span class="token comment"># Deploy anihpj with a restrictive CNP (drops api→db)</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true

cat > cnp-restrict.yaml << 'EOF'
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: restrict-db
  namespace: anihpj
spec:
  endpointSelector:
    matchLabels: {app: anihpj, tier: db}
  ingress:
  - fromEndpoints:
    - matchLabels: {app: anihpj, tier: web}
    toPorts:
    - ports: [{port: "5432"}]
EOF
kubectl apply -f cnp-restrict.yaml

kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
kubectl create deployment db -n anihpj --image=postgres:15 -l app=anihpj,tier=db
kubectl expose deployment api -n anihpj --port=80
kubectl expose deployment db -n anihpj --port=5432

<span class="token comment"># Generate traffic (some will be dropped)</span>
kubectl exec -n anihpj deploy/api -- wget -qO- http://db:5432 2>&1 || true

<span class="token comment"># ❌ BUG: Hubble shows everything — need to isolate DROPPED only</span>
hubble observe -n anihpj""",
    [
        ("pass", "<strong>1.</strong> Hubble running: <code>kubectl get pods -n kube-system | grep hubble-relay</code> → Running ✅"),
        ("pass", "<strong>2.</strong> All flows visible: <code>hubble observe -n anihpj</code> → FORWARDED and DROPPED flows mixed ✅"),
        ("fail", "<strong>3.</strong> Unfiltered output is noisy: <code>hubble observe -n anihpj</code> → <strong>hundreds of FORWARDED flows obscuring the DROPPED ones</strong> ❌"),
        ("fail", "<strong>4.</strong> No verdict filter used: output includes DNS, HTTP, TCP — <strong>need to narrow down to policy drops only</strong> ❌"),
        ("fail", "<strong>5.</strong> Cannot tell which exact connection is being denied: <strong>need per-flow verdict detail</strong> ❌"),
    ],
    [
        (1, "Use --verdict flag:", "hubble observe -n anihpj --verdict DROPPED", "discovery", "Shows only DROPPED flows — api → db:5432 appears as DROPPED"),
        (2, "Add protocol filter:", "hubble observe -n anihpj --verdict DROPPED --protocol TCP", "discovery", "Further isolates to TCP drops — removes UDP/DNS noise"),
        (3, "Filter by source pod:", "hubble observe -n anihpj --from-pod anihpj/deploy/api --verdict DROPPED", "discovery", "DROPPED flows from api: db port 5432 — CNP is blocking api→db"),
        (4, "Check policy verdict:", "hubble observe -n anihpj --verdict DROPPED -o json | jq '.flow.policy_match_type'", "discovery", "policy_match_type: 1 — L3/L4 policy denied the connection"),
        (5, "Root cause identified:", "CNP restrict-db allows only web→db ingress", "root-cause", "The CNP explicitly allows ingress from tier=web only on port 5432; api (tier=api) is not in the allow list, so its traffic to db is DROPPED"),
    ],
    """<span class="token comment"># Fix 1: Filter Hubble to see only relevant dropped flows</span>
hubble observe -n anihpj --verdict DROPPED --protocol TCP

<span class="token comment"># Fix 2: Use JSON output to inspect policy details</span>
hubble observe -n anihpj --verdict DROPPED -o json | jq '.'

<span class="token comment"># Fix 3 (if you want to fix the policy, not just observe):</span>
<span class="token comment"># Add api tier to the allow list in the CNP</span>
kubectl patch cnp restrict-db -n anihpj --type='json' -p='[{"op":"add","path":"/spec/ingress/0/fromEndpoints/-","value":{"matchLabels":{"app":"anihpj","tier":"api"}}}]'""",
    "DROPPED Flows Isolated and Identified",
    "Using <code>hubble observe --verdict DROPPED</code> with protocol and source-pod filters, only the dropped connections are displayed. The CNP blocking api→db is clearly identified. JSON output with jq reveals the exact policy rule causing the drop.",
    ["hubble observe -n anihpj → mixed FORWARDED+DROPPED", "--verdict DROPPED → only denied flows", "--from-pod + --protocol → pinpoint api→db", "JSON output → policy_match_type confirms L3/L4 deny", "CNP restrict-db allows only web, not api"],
    "Always use <code>--verdict DROPPED</code> (or <code>--verdict ERROR</code>) to isolate problematic flows. Combine with <code>--from-pod</code>, <code>--to-pod</code>, <code>--protocol</code>, <code>--to-port</code> filters for precision. For deep analysis, <code>-o json</code> with <code>jq</code> exposes <code>policy_match_type</code>, <code>drop_reason_desc</code>, and <code>event_type</code> fields that reveal exactly why each flow was dropped.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE            DESTINATION       VERDICT\n12:05:01.123        anihpj/web-xxx    anihpj/api:80     FORWARDED\n12:05:01.456        anihpj/web-yyy    anihpj/db:5432    FORWARDED\n12:05:02.789        anihpj/api-xxx    anihpj/db:5432    DROPPED    ← Buried in noise!\n12:05:03.012        anihpj/web-xxx    anihpj/api:80     FORWARDED\n... 200 more FORWARDED lines ...</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj --verdict DROPPED\n<span class="output">TIMESTAMP          SOURCE            DESTINATION       VERDICT\n12:05:02.789        anihpj/api-xxx    anihpj/db:5432    DROPPED\n12:05:04.123        anihpj/api-yyy    anihpj/db:5432    DROPPED    ← Only drops!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj --from-pod anihpj/deploy/api --verdict DROPPED\n<span class="output">TIMESTAMP          SOURCE            DESTINATION       VERDICT\n12:05:02.789        anihpj/api-xxx    anihpj/db:5432    DROPPED\n12:05:04.123        anihpj/api-yyy    anihpj/db:5432    DROPPED    ✅ api→db drops only</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj --verdict DROPPED -o json | jq ".flow.policy_match_type"\n<span class="output">1    ← L3/L4 policy denial (not L7, not auth, not proxy)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl describe cnp restrict-db -n anihpj | grep -A5 "fromEndpoints"\n<span class="output">  ingress:\n  - fromEndpoints:\n    - matchLabels:\n        app: anihpj\n        tier: web      ← Only web allowed! Not api!</span></div>',
    ]
)


# ====== Assemble and insert ======
all_scenarios = s55 + '\n\n' + s56 + '\n\n' + s57

# Find insertion point: after S54 closing, before <section class="chapter-section" id="appendices">
insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
else:
    print("ERROR: Could not find appendices insertion point!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)

print("✅ Batch 1 (S55-S57) inserted successfully!")
print(f"File size: {len(html.encode('utf-8'))} bytes")
