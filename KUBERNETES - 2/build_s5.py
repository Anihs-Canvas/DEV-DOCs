# Build S5 through S20 — Category 1 Architecture
# Each scenario follows S1 template exactly

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

marker = '    <!-- ═══════════════════════════════════════════════════════════\n         APPENDICES — CONTENT GOES HERE'

# ─── S5: Agent CrashLoop — Wrong Cilium ConfigMap Value ───
s5 = r'''    <!-- ═══════════════ S5: Pod Stuck in Init Phase ═══════════════ -->
    <div class="scenario-block" id="sc-s5">
        <div class="sc-header">
            <div class="sc-badge">S5</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S5 — Category 1: Architecture</div>
                <h4>Pod Stuck in Init:Error — Init Container Fails Due to Missing ConfigMap</h4>
                <div class="sc-desc"><strong>The Problem:</strong> The API deployment includes an init container that sources a database connection string from a ConfigMap. But the ConfigMap name is misspelled. The init container fails, keeping the main API container from starting. Your job: find why the pod is stuck and fix it.</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML (ConfigMap name typo)</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s5-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s5-code" class="language-bash">cat > s5-deploy.yaml << 'EOF'
<span class="token comment"># ============================================
#  1. NAMESPACE
# ============================================</span>
apiVersion: v1
kind: Namespace
metadata:
  name: anihpj
---
<span class="token comment"># ============================================
#  2. CONFIGMAP — DB connection config  ✅ OK
# ============================================</span>
apiVersion: v1
kind: ConfigMap
metadata:
  name: anihpj-db-config
  namespace: anihpj
data:
  DB_HOST: "anihpj-db.anihpj.svc.cluster.local"
  DB_PORT: "5432"
---
<span class="token comment"># ============================================
#  3. API DEPLOYMENT  ❌ BUG!
#  Init container references "anihpj-db-confg" (typo!)
#  Should be "anihpj-db-config"
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
      initContainers:
      - name: check-db
        image: busybox
        command: ['sh','-c','echo "DB at $DB_HOST:$DB_PORT"']
        envFrom:
        - configMapRef:
            name: anihpj-db-confg
      containers:
      - name: api
        image: nginx:alpine
        ports:
        - containerPort: 8080
---
<span class="token comment"># ============================================
#  4. API SERVICE  ✅ OK
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
kubectl apply -f s5-deploy.yaml</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error</h4>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj</code> → API pod stuck at <strong>Init:Error</strong> ❌</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>2.</strong> Describe pod: <code>kubectl describe pod -n anihpj &lt;api-pod&gt;</code> → "not found: configmap anihpj-db-confg" ❌</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>3.</strong> List ConfigMaps: <code>kubectl get configmaps -n anihpj</code> → anihpj-db-config exists ✅</span></div>
                    <div class="lookat-item"><span class="li-check pass">✓</span><span><strong>4.</strong> Notice the naming: ConfigMap is <code>anihpj-db-config</code> but init container references <code>anihpj-db-confg</code> ✅</span></div>
                    <div class="lookat-item"><span class="li-check fail">✗</span><span><strong>5.</strong> Root cause: <strong>typo in configMapRef name</strong> — "confg" vs "config" ❌</span></div>
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    <div class="lookat-item"><span class="li-num">1</span><span><strong>Get pod status:</strong> <code>kubectl get pods -n anihpj</code> → Init:Error</span></div>
                    <div class="lookat-item"><span class="li-num">2</span><span><strong>Check init container logs:</strong> <code>kubectl logs -n anihpj &lt;api-pod&gt; -c check-db</code></span></div>
                    <div class="lookat-item"><span class="li-num">3</span><span><strong>Describe pod events:</strong> <code>kubectl describe pod -n anihpj &lt;api-pod&gt;</code><br><span class="li-finding discovery">→ ConfigMap "anihpj-db-confg" not found</span></span></div>
                    <div class="lookat-item"><span class="li-num">4</span><span><strong>Verify ConfigMap name:</strong> <code>kubectl get cm -n anihpj</code> → anihpj-db-config</span></div>
                    <div class="lookat-item"><span class="li-num">5</span><span><strong>Root cause:</strong> <span class="li-finding root-cause">Typo in configMapRef — "anihpj-db-confg" instead of "anihpj-db-config". Kubernetes can't find the ConfigMap, init container fails, pod never starts.</span></span></div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — Patch the Deployment</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s5-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s5-fix" class="language-bash"><span class="token comment"># Fix: Update the configMapRef name</span>
kubectl patch deployment anihpj-api -n anihpj --type='json' -p='[{"op":"replace","path":"/spec/template/spec/initContainers/0/envFrom/0/configMapRef/name","value":"anihpj-db-config"}]'

<span class="token comment"># Wait for rollout</span>
kubectl rollout status deployment anihpj-api -n anihpj</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — API Pod Running</h4>
                        <p>After fixing the ConfigMap reference, the init container runs successfully and the main API container starts. This teaches that init containers have their own failure modes — they must complete before the main container starts, and any reference error (ConfigMap, Secret, image) blocks the entire pod.</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa5')">🔍 Show Full Answer</button>
            <div class="sc-answer" id="sc-sa5">
                <h5>🧠 Diagnostic Tenet</h5>
                <div class="tenet-flow">
                    <div class="tenet-step"><div class="step-num">①</div><div class="step-label">Pod stuck in Init → init container problem</div></div>
                    <div class="tenet-step"><div class="step-num">②</div><div class="step-label">kubectl describe pod → error message</div></div>
                    <div class="tenet-step"><div class="step-num">③</div><div class="step-label">Verify referenced resources exist</div></div>
                    <div class="tenet-step"><div class="step-num">④</div><div class="step-label">Compare names character-by-character</div></div>
                    <div class="tenet-step"><div class="step-num">⑤</div><div class="step-label">Fix reference → pod starts</div></div>
                </div>
                <p><strong>Tenet:</strong> Init containers are a common source of pod startup failures. <code>kubectl describe pod</code> shows the exact error. ConfigMap/Secret name typos are the most frequent cause — they prevent the init container from even starting.</p>
                <h5>📟 Error State</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj
<span class="output">NAME          READY   STATUS      RESTARTS   AGE
anihpj-api-x  0/1     Init:Error  0          2m</span></div>
                <div class="cmd-output"><span class="prompt">$</span> kubectl describe pod -n anihpj anihpj-api-x | tail -5
<span class="output">Events:
Warning  Failed   2m    kubelet  Error: configmap "anihpj-db-confg" not found</span></div>
                <h5>📟 AFTER Fix</h5>
                <div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj
<span class="output">NAME          READY   STATUS    RESTARTS   AGE
anihpj-api-x  1/1     Running   0          30s   ✅</span></div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup</h4>
                    <div class="code-block">
                        <div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s5-cleanup')">📋 Copy</button></div>
                        <pre><code id="sc-s5-cleanup" class="language-bash">kubectl delete namespace anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

if marker in content:
    content = content.replace(marker, s5 + '\n' + marker)
    print(f'S5 inserted! </main>={content.count("</main>")} scenario IDs={content.count("scenario-block\" id=")}')
else:
    print('ERROR: marker not found')
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done with S5')
