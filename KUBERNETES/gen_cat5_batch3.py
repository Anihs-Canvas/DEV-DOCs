#!/usr/bin/env python3
"""Generate Category 5: Installation & Configuration — Batch 3: S71-S74"""
import re

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_short, verify_detail, tenet_steps, tenet_text, before_outputs, after_outputs):
    ei_html = ''.join(f'<div class="lookat-item"><span class="li-check {"pass" if t=="pass" else "fail"}">{"✓" if t=="pass" else "✗"}</span><span>{txt}</span></div>\n' for t,txt in error_items)
    di_html = ''.join(f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n' for num,label,cmd,ftype,ftext in debug_items)
    tf_html = ''.join(f'<div class="tenet-step"><div class="step-num">{chr(0x2460+i)}</div><div class="step-label">{lbl}</div></div>\n' for i,lbl in enumerate(tenet_steps))
    bo_html = '\n'.join(before_outputs)
    ao_html = '\n'.join(after_outputs)

    return f'''    <!-- ═══════════════ S{n}: {title} ═══════════════ -->
    <div class="scenario-block" id="sc-s{n}">
        <div class="sc-header">
            <div class="sc-badge">S{n}</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{n} — Category 5: Installation &amp; Configuration</div>
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
                            <span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span>
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
                        <h4>✅ Verify — {verify_short}</h4>
                        <p>{verify_detail}</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{n}')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa{n}">
                <h5>🧠 Diagnostic Tenet (Thought Process)</h5>
                <div class="tenet-flow">{tf_html}</div>
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

# ======================== S71 ========================
s71 = sc(71,
    "Fix Cilium Status Showing Errors After Helm Upgrade",
    "After a Helm upgrade, <code>cilium status</code> reports <strong>multiple component errors</strong> even though pods appear Running. The Operator reports Controller=Degraded, Hubble Relay shows warnings, and some endpoints are in warning state. Your job: diagnose and fix the status errors.",
    r"""<span class="token comment"># Cilium was upgraded via Helm</span>
helm upgrade cilium cilium/cilium -n kube-system --version 1.16.0

<span class="token comment"># Deploy anihpj</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># ❌ BUG: cilium status shows errors</span>
cilium status
<span class="token comment"># Operator:       Degraded
# Hubble:         Warning
# Controllers:    1/6 failing</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium pods Running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → All Running ✅"),
        ("pass", "<strong>2.</strong> anihpj pods Running: <code>kubectl get pods -n anihpj</code> → All Running ✅"),
        ("fail", "<strong>3.</strong> cilium status shows errors: <code>cilium status</code> → <strong>Operator: Degraded, Controllers: failing</strong> ❌"),
        ("fail", "<strong>4.</strong> Operator logs: <code>kubectl logs -n kube-system deploy/cilium-operator</code> → <strong>\"Failed to reconcile CRD — schema version mismatch\"</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble Relay warnings: <code>kubectl logs -n kube-system deploy/hubble-relay</code> → <strong>\"TLS certificate expiring in 30 days\"</strong> ❌"),
    ],
    [
        (1, "Check Operator logs for CRD reconciliation:", "kubectl logs -n kube-system deploy/cilium-operator | grep -i error", "discovery", "Failed to update CiliumNode CRD: no matches for kind CiliumNode in version cilium.io/v2 — CRD was not upgraded with Helm"),
        (2, "Check Helm CRD management:", "helm list -n kube-system | grep cilium", "discovery", "Helm upgrade used --skip-crds flag or the chart's CRDs were not applied — Cilium Operator can't reconcile old CRD schema"),
        (3, "Verify all CRDs match agent version:", "kubectl get crd | grep cilium | awk '{print $1, $2}'", "discovery", "ciliumnodes.cilium.io shows STORED version as v2alpha1 but agent expects v2 — version mismatch after upgrade"),
        (4, "Check Hubble TLS certificate expiry:", "kubectl get secret -n kube-system hubble-server-certs -o yaml | grep -A5 cert", "discovery", "Hubble Relay TLS certificates are approaching expiry — the status warning is legitimate and requires cert rotation"),
        (5, "Root cause identified:", "Post-upgrade status errors stem from CRD version mismatch and stale TLS certificates", "root-cause", "Helm does not automatically upgrade CRDs during chart upgrade (--skip-crds is default). The Operator sees old CRD schema and reports reconciliation errors. Additionally, Hubble Relay's internal TLS certs have a 90-day validity and flag warnings at 30 days. Both issues require explicit CRD upgrade and cert rotation"),
    ],
    r"""<span class="token comment"># Fix 1: Manually upgrade CRDs to v2</span>
kubectl apply -f https://raw.githubusercontent.com/cilium/cilium/v1.16.0/install/kubernetes/cilium/crds/all-crds.yaml

<span class="token comment"># Fix 2: Restart Operator to pick up new CRD schema</span>
kubectl rollout restart deploy/cilium-operator -n kube-system
kubectl wait --for=condition=available deploy/cilium-operator -n kube-system --timeout=120s

<span class="token comment"># Fix 3: Rotate Hubble TLS certificates</span>
kubectl delete secret -n kube-system hubble-server-certs
kubectl delete secret -n kube-system hubble-relay-client-certs
kubectl rollout restart deploy/hubble-relay -n kube-system
kubectl rollout restart ds/cilium -n kube-system

<span class="token comment"># Fix 4: Verify status</span>
cilium status --wait""",
    "Cilium Status All OK",
    "All Cilium Components Reporting Healthy",
    '<code>cilium status</code> shows all components <strong>OK</strong>. Operator reports Controller=OK with no reconciliation errors. Hubble Relay is healthy with renewed TLS certificates. All anihpj endpoints are in ready state. <code>cilium endpoint list</code> shows all pods with valid identities.',
    ["cilium status → Operator Degraded", "Operator logs → CRD version mismatch", "CRDs at old version, agent expects new", "Apply new CRDs → restart Operator", "Refresh TLS certs → all status OK"],
    "After any Cilium upgrade, always check: 1) <strong>CRD versions</strong> match the agent version (<code>kubectl get crd | grep cilium</code>), 2) <strong>Operator reconciliation</strong> is successful (no Degraded state), and 3) <strong>TLS certificate expiry</strong> for Hubble Relay (90-day validity, warning at 30 days). Helm's default <code>--skip-crds</code> means you must apply CRDs manually during major upgrades.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       Degraded    ← ERROR!\n /¯¯\\__/¯¯\\    Hubble:         Warning     ← TLS expiry!\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       Controllers:    1/6 failing (CiliumNode)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system deploy/cilium-operator | grep -i "crd\|reconcil"\n<span class="output">level=error msg="Failed to reconcile CiliumNode" error="no matches for kind CiliumNode in version cilium.io/v2alpha1" subsys=controller\nlevel=error msg="CRD schema version mismatch" expected=v2 current=v2alpha1</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       Controllers:    all OK (6/6)    ✅</span></div>',
    ]
)

# ======================== S72 ========================
s72 = sc(72,
    "Configure Cilium with External etcd for anihpj Production",
    "For production high availability, you configure Cilium to use an <strong>external etcd cluster</strong> instead of Kubernetes CRDs. After switching, <strong>Cilium agents fail to start</strong> — they cannot connect to the external etcd. Your job: debug the etcd connection and fix the configuration.",
    r"""<span class="token comment"># External etcd cluster: etcd.anihpj.internal:2379</span>
<span class="token comment"># Configure Cilium to use external etcd</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --set etcd.enabled=true \
  --set etcd.ssl=true \
  --set etcd.endpoints[0]=https://etcd.anihpj.internal:2379

<span class="token comment"># ❌ BUG: Cilium agents can't connect to etcd</span>
kubectl get pods -n kube-system -l k8s-app=cilium
<span class="token comment"># cilium-xxxxx   0/1     CrashLoopBackOff   3</span>

kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine
<span class="token comment"># web-xxx   0/1     Pending   ← No CNI available</span>""",
    [
        ("pass", "<strong>1.</strong> External etcd cluster running: <code>curl -k https://etcd.anihpj.internal:2379/version</code> → JSON response ✅"),
        ("pass", "<strong>2.</strong> Helm upgrade applied: <code>helm list -n kube-system | grep cilium</code> → deployed ✅"),
        ("fail", "<strong>3.</strong> Cilium agents CrashLoop: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → <strong>CrashLoopBackOff</strong> ❌"),
        ("fail", "<strong>4.</strong> Agent logs: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>\"Failed to connect to etcd: x509: certificate signed by unknown authority\"</strong> ❌"),
        ("fail", "<strong>5.</strong> anihpj pods Pending: <strong>No CNI — kubelet cannot assign pod IPs</strong> ❌"),
    ],
    [
        (1, "Check Cilium agent etcd connection:", "kubectl logs -n kube-system ds/cilium | grep -i etcd", "discovery", "x509: certificate signed by unknown authority — the etcd server's TLS certificate is not trusted by Cilium agents"),
        (2, "Verify etcd TLS certificates are in Kubernetes secrets:", "kubectl get secret -n kube-system cilium-etcd-secrets -o yaml | grep -c data", "discovery", "Secret cilium-etcd-secrets does not exist — the external etcd CA cert, client cert, and client key were never provided to Cilium"),
        (3, "Check Helm values for etcd TLS config:", "helm get values cilium -n kube-system | grep -A10 etcd", "discovery", "etcd.ssl=true is set but etcd.ssl.caCert, etcd.ssl.clientCert, and etcd.ssl.clientKey values are empty — TLS is enabled but certificates are missing"),
        (4, "Test etcd connectivity manually from a node:", "curl --cacert /etc/etcd/ca.crt --cert /etc/etcd/client.crt --key /etc/etcd/client.key https://etcd.anihpj.internal:2379/version", "discovery", "Manual connection works with proper certs — confirms the issue is missing certs in Cilium's config, not etcd itself"),
        (5, "Root cause identified:", "TLS is enabled but no certificates provided to Cilium for external etcd", "root-cause", "When etcd.ssl=true is set, Cilium requires: 1) CA certificate (to verify the etcd server), 2) Client certificate (for mutual TLS), and 3) Client key. These must be provided via Kubernetes TLS secrets and referenced in Helm values (etcd.ssl.caCert, etcd.ssl.clientCert, etcd.ssl.clientKey) or stored in a pre-existing secret named cilium-etcd-secrets"),
    ],
    r"""<span class="token comment"># Fix 1: Create Kubernetes TLS secret from etcd certs</span>
kubectl create secret generic cilium-etcd-secrets \
  -n kube-system \
  --from-file=etcd-ca.crt=/etc/etcd/ca.crt \
  --from-file=etcd-client.crt=/etc/etcd/client.crt \
  --from-file=etcd-client.key=/etc/etcd/client.key

<span class="token comment"># Fix 2: Reconfigure Cilium with etcd certs</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set etcd.ssl=true \
  --set etcd.endpoints[0]=https://etcd.anihpj.internal:2379 \
  --set etcd.ssl.caCert=/etc/cilium/etcd-ca.crt \
  --set etcd.ssl.clientCert=/etc/cilium/etcd-client.crt \
  --set etcd.ssl.clientKey=/etc/cilium/etcd-client.key

<span class="token comment"># Fix 3: Restart Cilium agents</span>
kubectl rollout restart ds/cilium -n kube-system
cilium status --wait""",
    "External etcd Connected",
    "Cilium Connected to External etcd",
    'Cilium agents connect to the external etcd cluster via <strong>mutual TLS</strong>. <code>cilium status</code> shows KVStore: OK with the etcd endpoint. Identities and state are stored in the external etcd. anihpj pods are Running with IPs. <code>etcdctl --endpoints=https://etcd.anihpj.internal:2379 get --prefix cilium/</code> shows Cilium state stored in etcd.',
    ["Helm set etcd.enabled=true, etcd.ssl=true", "Agents CrashLoop → x509: unknown authority", "No cilium-etcd-secrets → certs not provided", "Create TLS secret + Helm values for certs", "Restart agents → KVStore OK → anihpj Running"],
    "External etcd requires three certificates for mutual TLS: <strong>CA cert</strong> (to verify the etcd server), <strong>client cert</strong> (to authenticate Cilium to etcd), and <strong>client key</strong>. These must be loaded from a Kubernetes secret. The Helm values <code>etcd.ssl.caCert</code>, <code>etcd.ssl.clientCert</code>, and <code>etcd.ssl.clientKey</code> specify the file paths inside the Cilium agent container. Without all three, the agent cannot establish a trusted TLS connection and crashes.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i etcd\n<span class="output">level=fatal msg="Failed to connect to etcd" error="x509: certificate signed by unknown authority" endpoint=https://etcd.anihpj.internal:2379\nlevel=fatal msg="Unable to initialize KVStore" subsys=kvstore</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get secret -n kube-system cilium-etcd-secrets\n<span class="output">Error from server (NotFound): secrets "cilium-etcd-secrets" not found    ← No TLS certs!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium status | grep -i kvstore\n<span class="output">KVStore:           Ok    etcd: 1/1 connected, has-quorum, https://etcd.anihpj.internal:2379 (v3.5.0)    ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> etcdctl --endpoints=https://etcd.anihpj.internal:2379 get --prefix cilium/state/identities/v1/ --keys-only | head -5\n<span class="output">cilium/state/identities/v1/id/1\ncilium/state/identities/v1/id/128\ncilium/state/identities/v1/id/256    ✅ Cilium state in etcd!</span></div>',
    ]
)

# ======================== S73 ========================
s73 = sc(73,
    "Debug CiliumEndpointSlice Migration Issues",
    "You enable CiliumEndpointSlice (CES) for better scalability, but after enabling, <strong>some anihpj endpoints are missing from cilium endpoint list</strong>. Hubble doesn't show flows for certain pods. Your job: debug the CES migration and fix endpoint visibility.",
    r"""<span class="token comment"># Enable CiliumEndpointSlice for scalability</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set bpf.masquerade=true \
  --set endpointSlice.enabled=true

<span class="token comment"># Deploy anihpj with many pods</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=5
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=5

<span class="token comment"># ❌ BUG: Some endpoints missing</span>
cilium endpoint list
<span class="token comment"># Shows only 6 endpoints — but 10 pods exist!</span>
kubectl get pods -n anihpj
<span class="token comment"># 10 pods Running</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium agents Running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → All Running ✅"),
        ("pass", "<strong>2.</strong> CES enabled: <code>kubectl get ciliumendpointslice -A</code> → CES objects exist ✅"),
        ("fail", "<strong>3.</strong> Endpoint count mismatch: <code>cilium endpoint list | wc -l</code> → <strong>6 endpoints for 10 pods!</strong> ❌"),
        ("fail", "<strong>4.</strong> Some pods not in CEP: <code>kubectl get cep -n anihpj</code> → <strong>only 6 CiliumEndpoints, 4 pods have no CEP</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble missing flows: <code>hubble observe -n anihpj</code> → <strong>flows only for 6 pods — 4 are invisible!</strong> ❌"),
    ],
    [
        (1, "Check CiliumEndpointSlice objects:", "kubectl get ces -A", "discovery", "CES objects exist but some have fewer endpoints than expected — the migration from per-endpoint CEP to CES may have missed pods created during the transition"),
        (2, "Compare CEP count vs pod count:", "echo \"Pods: $(kubectl get pods -n anihpj --no-headers | wc -l)\" && echo \"CEPs: $(kubectl get cep -n anihpj --no-headers | wc -l)\"", "discovery", "Pod count (10) vs CEP count (6) — 4 pods are running without a CiliumEndpoint, meaning no identity or policy applies to them"),
        (3, "Check agent logs for CES sync errors:", "kubectl logs -n kube-system ds/cilium | grep -i \"endpointslice\|ces\"", "discovery", "CES sync delay: agent's local cache still uses CEP model, CES update from API server is lagging, causing stale endpoint state"),
        (4, "Verify CES identity mapping:", "kubectl get ces -n anihpj -o yaml | grep -A5 identities", "discovery", "CES shows 6 identities but no identity mapping for the 4 missing pods — identity allocation failed during CES transition"),
        (5, "Root cause identified:", "CES migration leaves endpoints in limbo during the CEP-to-CES transition", "root-cause", "When CES is enabled on a running cluster, existing CEPs are gradually migrated to CES. During the transition window, new pods may not get registered in either CEP or CES — the agent's endpoint management switches models mid-flight. Restarting Cilium agents forces a clean reconciliation of all endpoints into CES"),
    ],
    r"""<span class="token comment"># Fix 1: Force Cilium agent restart to reconcile all endpoints into CES</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system --timeout=300s

<span class="token comment"># Fix 2: Delete stale CEPs to force CES recreation</span>
kubectl delete cep -n anihpj --all

<span class="token comment"># Fix 3: Verify all pods have CES entries</span>
kubectl get ces -n anihpj -o yaml | grep -c "name:"
<span class="token comment"># Should match pod count</span>

<span class="token comment"># Fix 4: Verify endpoints visible</span>
cilium endpoint list
<span class="token comment"># Should show all 10 endpoints</span>""",
    "All Endpoints Visible in CES",
    "All 10 anihpj Pods Have Endpoints in CES",
    'After restarting Cilium agents, all 10 anihpj pods are registered in CiliumEndpointSlice. <code>cilium endpoint list</code> shows all 10 endpoints with valid identities. <code>kubectl get ces -n anihpj</code> shows endpoints grouped by identity. Hubble observes flows for all pods. The CES migration is complete with no missing endpoints.',
    ["10 pods Running → only 6 endpoints", "Some pods have no CEP → no identity", "CES sync lag during migration transition", "Restart agents → force full reconciliation", "All 10 endpoints visible → Hubble sees all"],
    "CiliumEndpointSlice (CES) groups endpoints by <strong>security identity</strong> instead of creating one CEP per pod. This dramatically reduces Kubernetes API load at scale (one CES per identity vs one CEP per pod). During CES migration, always <strong>restart Cilium agents</strong> after enabling to force a clean endpoint reconciliation. Stale CEPs can be safely deleted — the agent will recreate them as CES entries.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj --no-headers | wc -l\n<span class="output">10    ← 10 pods running</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cep -n anihpj --no-headers | wc -l\n<span class="output">6     ← Only 6 have CiliumEndpoints!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium endpoint list\n<span class="output">ENDPOINT   POLICY (ingress)   POLICY (egress)   IDENTITY   IPV4         STATUS\n1234       Enabled            Enabled           128        10.0.1.10    ready\n1235       Enabled            Enabled           128        10.0.1.11    ready\n(only 6 of 10 endpoints shown)</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium endpoint list\n<span class="output">ENDPOINT   POLICY (ingress)   POLICY (egress)   IDENTITY   IPV4         STATUS\n1234-1243  10 endpoints shown — all ready    ✅ All 10 visible!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ces -n anihpj\n<span class="output">NAME                  AGE\nanihpj-web           2m\nanihpj-api           2m    ✅ Endpoints grouped by identity in CES</span></div>',
    ]
)

# ======================== S74 ========================
s74 = sc(74,
    "Fix System Requirements Check Failing — Kernel Too Old for BBR",
    "You attempt to enable BBR congestion control and Bandwidth Manager for anihpj, but <strong>Cilium agents fail with kernel compatibility errors</strong>. The nodes run Ubuntu 20.04 with kernel 5.4 — too old for BBR. Your job: verify system requirements and fix the configuration to work with the available kernel.",
    r"""<span class="token comment"># Try to enable Bandwidth Manager with BBR</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set bandwidthManager.enabled=true \
  --set bandwidthManager.bbr=true

<span class="token comment"># ❌ BUG: Agents crash — kernel too old</span>
kubectl get pods -n kube-system -l k8s-app=cilium
<span class="token comment"># cilium-xxxxx   0/1     CrashLoopBackOff   5</span>

kubectl logs -n kube-system ds/cilium | grep -i bbr
<span class="token comment"># "BBR requires kernel 5.18+ — current kernel: 5.4.0"</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium installed: <code>cilium version</code> → OK ✅"),
        ("pass", "<strong>2.</strong> Nodes available: <code>kubectl get nodes</code> → 3 Ready ✅"),
        ("fail", "<strong>3.</strong> Agents CrashLoop: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → <strong>CrashLoopBackOff after enabling BBR</strong> ❌"),
        ("fail", "<strong>4.</strong> Kernel version check: <code>uname -r</code> on node → <strong>5.4.0 — too old for BBR (needs 5.18+)</strong> ❌"),
        ("fail", "<strong>5.</strong> Bandwidth Manager also fails: <strong>requires BPF Host Routing which needs kernel 5.10+ with specific config</strong> ❌"),
    ],
    [
        (1, "Check kernel version on all nodes:", "kubectl get nodes -o wide && kubectl debug node/<node> --image=busybox -- uname -r", "discovery", "All nodes running kernel 5.4.0 — Cilium BBR requires 5.18+, Bandwidth Manager requires 5.10+ with BTF and BPF Host Routing"),
        (2, "Check kernel features available:", "kubectl exec -n kube-system ds/cilium -- cilium kernel-check", "discovery", "Missing: CONFIG_TCP_CONG_BBR not compiled, BTF not available, BPF Host Routing unsupported — multiple kernel config requirements not met"),
        (3, "Verify Cilium minimum requirements:", "cilium status | grep -i kernel", "discovery", "Cilium itself supports kernel 5.4 but specific features (BBR, BW Mgr, KPR strict) have higher requirements"),
        (4, "Check if BTF is available:", "ls /sys/kernel/btf/vmlinux 2>/dev/null", "discovery", "BTF missing — kernel was not compiled with CONFIG_DEBUG_INFO_BTF=y, which is required for CO-RE and many BPF features"),
        (5, "Root cause identified:", "Feature-specific kernel requirements not met — kernel 5.4 is too old for BBR and Bandwidth Manager", "root-cause", "Cilium features have tiered kernel requirements: Basic CNI works on 5.4+, KPR needs 5.10+, Bandwidth Manager needs 5.10+ with BTF and BPF Host Routing, BBR needs 5.18+. The kernel check command (cilium kernel-check) validates each node's kernel config against the enabled features"),
    ],
    r"""<span class="token comment"># Fix 1: Disable BBR — fall back to EDT (Earliest Departure Time)</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set bandwidthManager.enabled=true \
  --set bandwidthManager.bbr=false

<span class="token comment"># Fix 2: Verify Bandwidth Manager works without BBR (if kernel >= 5.10)</span>
<span class="token comment"># If kernel is 5.4, disable Bandwidth Manager entirely:</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set bandwidthManager.enabled=false

<span class="token comment"># Fix 3 (long term): Upgrade kernel to 5.18+ for full BBR support</span>
<span class="token comment"># Ubuntu 22.04+ or kernel 5.18+ via HWE</span>
apt-get install linux-generic-hwe-22.04

<span class="token comment"># Fix 4: Run kernel check after changes</span>
kubectl exec -n kube-system ds/cilium -- cilium kernel-check""",
    "BBR Disabled Gracefully",
    "Cilium Running with Kernel-Compatible Features",
    'Cilium agents are healthy with feature set matching the available kernel. <code>cilium kernel-check</code> shows which features are compatible. Bandwidth Manager uses <strong>EDT (Earliest Departure Time)</strong> instead of BBR — still functional for bandwidth limiting. If kernel is 5.4, Bandwidth Manager is disabled and Cilium runs in basic CNI mode. All anihpj pods are Running.',
    ["Enable BBR → agents CrashLoopBackOff", "Check kernel: 5.4 → BBR needs 5.18+", "cilium kernel-check → missing BTF + BBR", "Disable BBR → use EDT or disable BW Mgr", "Agents healthy → anihpj Running"],
    "Always run <code>cilium kernel-check</code> before enabling advanced features. Cilium's tiered requirements: <strong>5.4+</strong> for basic CNI, <strong>5.10+ with BTF</strong> for KPR/BW Manager/eBPF Host Routing, <strong>5.18+</strong> for BBR. When kernel is too old, gracefully degrade feature set rather than forcing agent crashes. Use <strong>EDT</strong> (Earliest Departure Time) as BBR alternative — it provides fair queueing without kernel 5.18+.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- cilium kernel-check\n<span class="output">Kernel: 5.4.0-110-generic\n  CONFIG_TCP_CONG_BBR: MISSING (needed for BBR)\n  CONFIG_DEBUG_INFO_BTF: MISSING (needed for CO-RE)\n  BPF Host Routing: UNSUPPORTED (need 5.10+)\n  Bandwidth Manager: UNSUPPORTED (need 5.10+ with BTF)\n[!] 4 features unavailable — check kernel version</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i "bbr\|kernel"\n<span class="output">level=fatal msg="BBR congestion control requires kernel 5.18 or newer" current=5.4.0 subsys=bandwidth-manager\nlevel=fatal msg="Failed to initialize bandwidth manager"</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- cilium kernel-check\n<span class="output">Kernel: 5.4.0-110-generic\n  Bandwidth Manager: disabled (matching kernel capabilities)\n  BBR: disabled (kernel too old)\n  EDT: available (fair queueing fallback)\n  Basic CNI: fully supported    ✅ Features match kernel!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       Kernel: 5.4.0 (features matched)    ✅</span></div>',
    ]
)

# ====== Assemble ======
all_scenarios = s71 + '\n\n' + s72 + '\n\n' + s73 + '\n\n' + s74

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 3 (S71-S74) inserted!")
else:
    print("ERROR: appendices marker not found!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File size: {len(html.encode('utf-8'))} bytes")
