# Build S3 through S20 for Category 1 Architecture
# Each follows the exact same structure as S1 and S2

scenarios = []

# S3: Web Pod Can't Resolve API Service DNS — Missing CoreDNS Egress CNP
s3 = r'''    <!-- ═══════════════ S3: Service Endpoints Empty — Wrong Port Name ═══════════════ -->
    <div class="scenario-block" id="sc-s3">
        <div class="sc-header">
            <div class="sc-badge">S3</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S3 — Category 1: Architecture</div>
                <h4>Service Has No Endpoints — Wrong targetPort Name in Service Definition</h4>
                <div class="sc-desc"><strong>The Problem:</strong> You deploy the anihpj stack. All pods are Running. Web can reach API by pod IP directly. But the API Service has <strong>no endpoints</strong> — and the service definition looks identical to S1 at first glance. Your job: find the subtle port naming bug.</div>
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
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s3-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s3-code" class="language-bash">cat > s3-deploy.yaml << 'EOF'
<span class="token comment"># ============================================
#  1. NAMESPACE
# ============================================</span>
apiVersion: v1
kind: Namespace
metadata:
  name: anihpj
---
<span class="token comment"># ============================================
#  2. API — nginx with named port  ✅ OK
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
        - name: http-api
          containerPort: 8080
---
<span class="token comment"># ============================================
#  3. API SERVICE  ❌ BUG!
#  targetPort: http-ap1 — typo! Should be http-api
#  Service can't match the named port on the pod
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
    targetPort: http-ap1
---
<span class="token comment"># ============================================
#  4. WEB  ✅ OK
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
EOF
kubectl apply -f s3-deploy.yaml</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error — Spot What's Broken</h4>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj</code> → All Running ✅</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>2.</strong> Check Cilium endpoints: <code>cilium endpoint list</code> → Endpoints exist for all pods ✅</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>3.</strong> Check Service endpoints: <code>kubectl get endpoints -n anihpj anihpj-api</code> → <strong>&lt;none&gt;</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>4.</strong> Test via Service DNS: <code>kubectl exec -n anihpj &lt;web-pod&gt; -- wget -qO- http://anihpj-api:8080</code> → <strong>FAILS!</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>5.</strong> Direct pod-to-pod IP: <code>wget -qO- http://&lt;api-pod-ip&gt;:8080</code> → Works! Pod networking is fine ✅</span></div>
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    <div class="lookat-item"><span class="li-num">1</span><span><strong>Describe the Service:</strong> <code>kubectl describe svc -n anihpj anihpj-api</code><br><span class="li-finding discovery">→ targetPort: http-ap1 — this must match a named port on the pod</span></span></div>
                    <div class="lookat-item"><span class="li-num">2</span><span><strong>Check pod's container ports:</strong> <code>kubectl get pod -n anihpj &lt;api-pod&gt; -o yaml | grep -A3 ports</code><br><span class="li-finding discovery">→ Pod has containerPort named "http-api" — NOT "http-ap1"</span></span></div>
                    <div class="lookat-item"><span class="li-num">3</span><span><strong>Understand the mismatch:</strong> When targetPort is a string (not a number), Kubernetes matches it to the pod's named port. "http-ap1" ≠ "http-api"</span></div>
                    <div class="lookat-item"><span class="li-num">4</span><span><strong>Why endpoints are empty:</strong> kube-controller-manager can't resolve the named port → no Endpoints object created</span></div>
                    <div class="lookat-item"><span class="li-num">5</span><span><strong>Root cause identified:</strong> <span class="li-finding root-cause">Typo in targetPort name — "http-ap1" instead of "http-api". Named port references must match EXACTLY.</span></span></div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — Patch the Service targetPort</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — patch the service</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s3-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s3-fix" class="language-bash"><span class="token comment"># Fix 1: Patch the service targetPort name</span>
kubectl patch svc anihpj-api -n anihpj --type='json' -p='[{"op":"replace","path":"/spec/ports/0/targetPort","value":"http-api"}]'

<span class="token comment"># OR: Use numeric port instead (simpler, no name matching needed)</span>
<span class="token comment"># kubectl patch svc anihpj-api -n anihpj -p '{"spec":{"ports":[{"port":8080,"targetPort":8080}]}}'</span>

<span class="token comment"># Verify endpoints populate</span>
kubectl get endpoints -n anihpj anihpj-api</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — Service Endpoints Populated, DNS Works</h4>
                        <p>After fixing the targetPort name, the Service Endpoints object populates with the API pod IPs. Web can reach API via Service DNS. This teaches that <strong>named ports on Services must match named ports on Pods exactly</strong> — it's a common pitfall when copying YAML between environments.</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa3')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa3">
                <h5>🧠 Diagnostic Tenet</h5>
                <div class="tenet-flow">
                    <div class="tenet-step"><div class="step-num">①</div><div class="step-label">IP works, Service fails → Service config issue</div></div>
                    <div class="tenet-step"><div class="step-num">②</div><div class="step-label">Check endpoints → EMPTY</div></div>
                    <div class="tenet-step"><div class="step-num">③</div><div class="step-label">Check Service port definition</div></div>
                    <div class="tenet-step"><div class="step-num">④</div><div class="step-label">Compare with Pod's named ports</div></div>
                    <div class="tenet-step"><div class="step-num">⑤</div><div class="step-label">Fix mismatch → verify endpoints</div></div>
                </div>
                <p><strong>Tenet:</strong> Named port references on Services must match named ports on Pods character-for-character. When targetPort is a string, Kubernetes performs name-based matching. A single character typo results in an empty Endpoints object with no error message — the Service simply has no backends.</p>
                <h5>📟 Error State</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n anihpj
<span class="output">NAME         ENDPOINTS   AGE
anihpj-api   &lt;none&gt;      2m   ← EMPTY!</span></div>
                <div class="cmd-output"><span class="prompt">$</span> kubectl describe svc -n anihpj anihpj-api
<span class="output">Port:  8080/TCP
TargetPort:  http-ap1/TCP   ← BUG: should be http-api
Endpoints:   &lt;none&gt;
Selector:    app=anihpj,tier=api</span></div>
                <div class="cmd-output"><span class="prompt">$</span> kubectl get pod -n anihpj anihpj-api-xxx -o jsonpath='{.spec.containers[0].ports}'
<span class="output">[{"containerPort":8080,"name":"http-api","protocol":"TCP"}]  ← Pod has "http-api"</span></div>
                <h5>📟 AFTER Fix</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl get endpoints -n anihpj anihpj-api
<span class="output">NAME         ENDPOINTS                       AGE
anihpj-api   10.0.1.11:8080,10.0.2.12:8080   5s   ✅</span></div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste to clean up</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s3-cleanup')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s3-cleanup" class="language-bash"><span class="token comment"># Delete the namespace</span>
kubectl delete namespace anihpj
kubectl get all -n anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

# Write S3 to the file
with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert S3 before Appendices
marker = '    <!-- ═══════════════════════════════════════════════════════════\n         APPENDICES — CONTENT GOES HERE'
if marker in content:
    content = content.replace(marker, s3 + '\n' + marker)
    with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('S3 inserted successfully!')
    print(f'</main> count: {content.count("</main>")}')
    print(f'scenario-block count: {content.count("scenario-block")}')
else:
    print('Marker not found!')
