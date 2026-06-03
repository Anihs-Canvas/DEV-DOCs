# Build S4 through S20 for Category 1 Architecture
# Using the Python approach for reliability

import sys

def insert_scenario(scenario_html, scenario_num):
    with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    marker = '    <!-- ═══════════════════════════════════════════════════════════\n         APPENDICES — CONTENT GOES HERE'
    if marker in content:
        content = content.replace(marker, scenario_html + '\n' + marker)
        with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
            f.write(content)
        mc = content.count('</main>')
        sc = content.count('scenario-block')
        print(f'S{scenario_num} inserted! </main>={mc} scenario-block={sc//2} IDs')
        return True
    print(f'ERROR: Marker not found for S{scenario_num}')
    return False

# ─── S4: DNS Resolution Fails — kube-dns Service IP Wrong ───
s4 = r'''    <!-- ═══════════════ S4: DNS Resolution Blocked ═══════════════ -->
    <div class="scenario-block" id="sc-s4">
        <div class="sc-header">
            <div class="sc-badge">S4</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S4 — Category 1: Architecture</div>
                <h4>DNS Resolution Fails — Web Pod Can't Resolve anihpj-api Service Name</h4>
                <div class="sc-desc"><strong>The Problem:</strong> All pods are Running. Pod-to-pod IP communication works. But when the web pod tries to reach <code>anihpj-api</code> (without FQDN), DNS resolution <strong>fails</strong>. Using the full FQDN <code>anihpj-api.anihpj.svc.cluster.local</code> also fails. Your job: debug why CoreDNS can't resolve the service name.</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML (CoreDNS blocked by policy)</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s4-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s4-code" class="language-bash">cat > s4-deploy.yaml << 'EOF'
<span class="token comment"># ============================================
#  1. NAMESPACE
# ============================================</span>
apiVersion: v1
kind: Namespace
metadata:
  name: anihpj
---
<span class="token comment"># ============================================
#  2. API DEPLOYMENT & SERVICE  ✅ OK
# ============================================</span>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  replicas: 2
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
---
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
---
<span class="token comment"># ============================================
#  3. WEB DEPLOYMENT  ✅ OK
# ============================================</span>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-web
  namespace: anihpj
spec:
  replicas: 1
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
        image: nginx:alpine
        ports:
        - containerPort: 8000
---
<span class="token comment"># ============================================
#  4. NETWORK POLICY  ❌ BUG!
#  Allows same-namespace traffic BUT blocks egress
#  to kube-system where CoreDNS runs!
# ============================================</span>
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: anihpj-default-deny
  namespace: anihpj
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}    ← Only allows egress to pods in THIS namespace!
                         ← CoreDNS is in kube-system → BLOCKED!
EOF
kubectl apply -f s4-deploy.yaml</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error — Spot What's Broken</h4>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj</code> → All Running ✅</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>2.</strong> Direct pod-to-pod IP: <code>wget -qO- http://&lt;api-ip&gt;:8080</code> → Works! ✅</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>3.</strong> DNS test: <code>kubectl exec -n anihpj &lt;web-pod&gt; -- nslookup anihpj-api</code> → <strong>TIMEOUT!</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>4.</strong> DNS to external: <code>nslookup google.com</code> → <strong>Also fails!</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>5.</strong> Check NetworkPolicy: <code>kubectl get networkpolicy -n anihpj</code> → anihpj-default-deny exists ✅</span></div>
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    <div class="lookat-item"><span class="li-num">1</span><span><strong>Check NetworkPolicy rules:</strong> <code>kubectl describe networkpolicy -n anihpj</code><br><span class="li-finding discovery">→ Egress only allows traffic to pods in same namespace</span></span></div>
                    <div class="lookat-item"><span class="li-num">2</span><span><strong>Where is CoreDNS?</strong> <code>kubectl get pods -n kube-system -l k8s-app=kube-dns</code><br><span class="li-finding discovery">→ CoreDNS runs in kube-system namespace — NOT anihpj</span></span></div>
                    <div class="lookat-item"><span class="li-num">3</span><span><strong>Test DNS from pod without policy:</strong> Create a test pod in default namespace → DNS works</span></div>
                    <div class="lookat-item"><span class="li-num">4</span><span><strong>Check Hubble for dropped DNS:</strong> <code>hubble observe -n anihpj --to-port 53 --verdict DROPPED</code></span></div>
                    <div class="lookat-item"><span class="li-num">5</span><span><strong>Root cause identified:</strong> <span class="li-finding root-cause">NetworkPolicy allows egress only within same namespace. CoreDNS runs in kube-system. DNS UDP packets to port 53 are DROPPED.</span></span></div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — Add Egress Rule to kube-system for DNS</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — patch or replace the NetworkPolicy</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s4-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s4-fix" class="language-bash"><span class="token comment"># Fix: Add DNS egress to kube-system namespace</span>
cat > s4-fix-policy.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: anihpj-default-deny
  namespace: anihpj
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
EOF
kubectl apply -f s4-fix-policy.yaml</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — DNS Resolution Restored</h4>
                        <p>After adding the egress rule to kube-system on UDP 53, DNS queries from the anihpj namespace reach CoreDNS. The web pod can resolve <code>anihpj-api</code>. This teaches that NetworkPolicies apply to ALL egress traffic — including DNS to kube-system — and namespace isolation requires explicit allow rules for external services.</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa4')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa4">
                <h5>🧠 Diagnostic Tenet</h5>
                <div class="tenet-flow">
                    <div class="tenet-step"><div class="step-num">①</div><div class="step-label">IP works, DNS fails → DNS path broken</div></div>
                    <div class="tenet-step"><div class="step-num">②</div><div class="step-label">Check if ANY DNS works (internal + external)</div></div>
                    <div class="tenet-step"><div class="step-num">③</div><div class="step-label">Look for NetworkPolicies in namespace</div></div>
                    <div class="tenet-step"><div class="step-num">④</div><div class="step-label">Check CoreDNS location (kube-system)</div></div>
                    <div class="tenet-step"><div class="step-num">⑤</div><div class="step-label">Hubble verify DROPPED on port 53 → Fix</div></div>
                </div>
                <p><strong>Tenet:</strong> DNS is the #1 thing broken by over-restrictive NetworkPolicies. Pods need egress to kube-system on UDP 53 to reach CoreDNS. Hubble's <code>--verdict DROPPED</code> filter is the fastest way to confirm this.</p>
                <h5>📟 Error State</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj anihpj-web-xxx -- nslookup anihpj-api
<span class="output">;; connection timed out; no servers could be reached</span></div>
                <div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj --to-port 53 --verdict DROPPED
<span class="output">TIMESTAMP    SOURCE                   DESTINATION          VERDICT
12:00:01     anihpj/anihpj-web-xxx     kube-system/kube-dns  DROPPED</span></div>
                <h5>📟 AFTER Fix</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj anihpj-web-xxx -- nslookup anihpj-api
<span class="output">Name:   anihpj-api.anihpj.svc.cluster.local
Address: 10.96.100.50   ✅ DNS works!</span></div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s4-cleanup')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s4-cleanup" class="language-bash">kubectl delete namespace anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

if not insert_scenario(s4, 4):
    sys.exit(1)
