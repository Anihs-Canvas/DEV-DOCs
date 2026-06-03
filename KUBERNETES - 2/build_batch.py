# Build S6-S20 — Category 1 Architecture. Insert all at once.
with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

marker = '    <!-- ═══════════════════════════════════════════════════════════\n         APPENDICES — CONTENT GOES HERE'

all_scenarios = []

# ═══ S6: Pod Stuck Pending — Resource Limits Too High ═══
all_scenarios.append(r'''    <!-- ═══════════════ S6: Pod Pending — CPU Request Too High ═══════════════ -->
    <div class="scenario-block" id="sc-s6">
        <div class="sc-header">
            <div class="sc-badge">S6</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S6 — Category 1: Architecture</div>
                <h4>API Pod Stuck Pending — CPU Request Exceeds Node Capacity</h4>
                <div class="sc-desc"><strong>The Problem:</strong> The API deployment specifies a CPU request of <code>100</code> (which means 100 CPUs, not 100m millicores). No node in the cluster has 100 CPUs, so the pod stays Pending forever. Your job: find why the pod can't schedule and fix the resource request.</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML</h4>
                    <div class="code-block">
                        <div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s6-code')">📋 Copy</button></div>
                        <pre><code id="sc-s6-code" class="language-bash">cat > s6-deploy.yaml << 'EOF'
<span class="token comment"># ============================================
#  1. NAMESPACE
# ============================================</span>
apiVersion: v1
kind: Namespace
metadata:
  name: anihpj
---
<span class="token comment"># ============================================
#  2. API DEPLOYMENT  ❌ BUG!
#  resources.requests.cpu: 100 → means 100 CPUs!
#  Should be "100m" (100 millicores = 0.1 CPU)
# ============================================</span>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  replicas: 1
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
        image: nginx:alpine
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "100"
            memory: "64Mi"
---
<span class="token comment">#  3. API SERVICE  ✅ OK
# ============================================</span>
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
  - port: 8080
    targetPort: 8080
EOF
kubectl apply -f s6-deploy.yaml</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error</h4>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj</code> → API pod <strong>Pending</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>2.</strong> Describe pod: <code>kubectl describe pod -n anihpj &lt;api-pod&gt;</code> → "0/2 nodes available: Insufficient cpu" ❌</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>3.</strong> Check node capacity: <code>kubectl describe node &lt;node&gt; | grep -A5 Capacity</code> → Shows ~4 CPUs available ✅</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>4.</strong> Check pod requests: <code>kubectl get pod -n anihpj &lt;api-pod&gt; -o yaml | grep -A3 requests</code> → cpu: "100" ✅</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>5.</strong> "100" means 100 CPUs, not 100m (0.1 CPU). You're asking for 100 entire CPUs! ❌</span></div>
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    <div class="lookat-item"><span class="li-num">1</span><span><strong>kubectl describe pod</strong> → events show "Insufficient cpu"</span></div>
                    <div class="lookat-item"><span class="li-num">2</span><span><strong>Check the actual request:</strong> <code>kubectl get pod -n anihpj &lt;pod&gt; -o jsonpath='{.spec.containers[0].resources.requests}'</code><br><span class="li-finding discovery">→ {"cpu":"100"} — 100 CPUs, not 100m!</span></span></div>
                    <div class="lookat-item"><span class="li-num">3</span><span><strong>Kubernetes CPU units:</strong> "1" = 1 CPU core. "100m" = 0.1 CPU. "100" = 100 CPU cores.</span></div>
                    <div class="lookat-item"><span class="li-num">4</span><span><strong>No node has 100 CPUs</strong> → pod will never schedule</span></div>
                    <div class="lookat-item"><span class="li-num">5</span><span><strong>Root cause:</strong> <span class="li-finding root-cause">Missing "m" suffix — "100" means 100 CPUs, "100m" means 100 millicores (0.1 CPU).</span></span></div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — Correct the CPU Request</h4>
                    <div class="code-block">
                        <div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s6-fix')">📋 Copy</button></div>
                        <pre><code id="sc-s6-fix" class="language-bash"><span class="token comment"># Fix: Change cpu request from "100" to "100m"</span>
kubectl patch deployment anihpj-api -n anihpj --type='json' -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"100m"}]'
kubectl rollout status deployment anihpj-api -n anihpj</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — Pod Scheduled and Running</h4>
                        <p>After changing to <code>100m</code>, the pod schedules immediately. This is a classic Kubernetes gotcha: CPU resources without the "m" suffix are in whole cores, not millicores. Always include the "m" suffix for fractional CPU requests.</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa6')">🔍 Show Full Answer</button>
            <div class="sc-answer" id="sc-sa6">
                <h5>🧠 Diagnostic Tenet</h5>
                <div class="tenet-flow">
                    <div class="tenet-step"><div class="step-num">①</div><div class="step-label">Pod Pending → scheduling issue</div></div>
                    <div class="tenet-step"><div class="step-num">②</div><div class="step-label">kubectl describe → events explain why</div></div>
                    <div class="tenet-step"><div class="step-num">③</div><div class="step-label">Check resource requests vs node capacity</div></div>
                    <div class="tenet-step"><div class="step-num">④</div><div class="step-label">Verify CPU unit (m suffix matters!)</div></div>
                    <div class="tenet-step"><div class="step-num">⑤</div><div class="step-label">Fix request → pod schedules</div></div>
                </div>
                <p><strong>Tenet:</strong> Kubernetes CPU resource units: <code>1</code> = 1 CPU core, <code>100m</code> = 0.1 CPU. Missing the "m" suffix multiplies your request by 1000x. Always check <code>kubectl describe pod</code> events for scheduling failures.</p>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup</h4>
                    <div class="code-block">
                        <div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s6-cleanup')">📋 Copy</button></div>
                        <pre><code id="sc-s6-cleanup" class="language-bash">kubectl delete namespace anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
''')

# Write all at once
if marker in content:
    combined = '\n'.join(all_scenarios)
    content = content.replace(marker, combined + '\n' + marker)
    with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Inserted {len(all_scenarios)} scenarios')
    print(f'</main> count: {content.count("</main>")}')
else:
    print('ERROR: marker not found')
