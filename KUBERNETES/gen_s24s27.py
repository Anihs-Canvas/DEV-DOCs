#!/usr/bin/env python
import os; os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')
with open('cka_test_prep.html','r',encoding='utf-8') as f: h=f.read()
P=h.rfind('<footer class="footer">')

def CMT(t): return f'<span class="token comment"># {t}</span>'
def CMD(p,o): return f'                <div class="cmd-output"><span class="prompt">$</span> {p}\n<span class="output">{o}</span></div>'
def LI(t): return f'                    <div class="lookat-item"><span class="li-check fail">✗</span><span>{t}</span></div>'
def DB(n,t): return f'                    <div class="lookat-item"><span class="li-num">{n}</span><span>{t}</span></div>'
def TN(i,t): return f'                    <div class="tenet-step"><div class="step-num">{"①②③④⑤"[i]}</div><div class="step-label">{t}</div></div>'

TPL='''    <div class="scenario-block" id="sc-s{N}">
        <div class="sc-header">
            <div class="sc-badge">S{N}</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{N} — Category 2: Troubleshooting <span class="sc-status debug">{STATUS}</span></div>
                <h4>{TITLE}</h4>
                <div class="sc-desc"><strong>The Problem:</strong> {DESC}</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the Setup (CONTAINS THE BUG)</h4>
                    <p style="color:var(--text-secondary);margin-bottom:10px;font-size:14px;">The YAML below contains an intentional misconfiguration.</p>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — Apply to cluster</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{N}-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{N}-code">{DC}</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error — Spot What's Broken</h4>
{EI}
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
{DI}
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{N}')">🔍 Show Full Answer &amp; Expected Command Outputs</button>
            <div class="sc-answer" id="sc-sa{N}">
                <h5>🧠 Diagnostic Tenet (Thought Process)</h5>
                <div class="tenet-flow">{TS}</div>
                <p><strong>Tenet:</strong> {TT}</p>
                <h5>📟 Command Outputs — ERROR State (BEFORE fix)</h5>
{EO}
                <h5>📟 Command Outputs — AFTER Fix</h5>
{AO}
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background:linear-gradient(135deg,#d2991d,#3fb950);">🔧</div>
                <div class="sc-step-content">
                    <button class="sc-fix-toggle" onclick="var el=document.getElementById('sc-s{N}-fix-drop');el.classList.toggle('show');if(el.classList.contains('show'))Prism.highlightAllUnder(el);" style="color:#3fb950;border-color:rgba(63,185,80,0.25);background:rgba(63,185,80,0.08);">🔧 Fix — Apply the Correction</button>
                    <div class="sc-answer" id="sc-s{N}-fix-drop">
                        <div class="code-block">
                        <div class="code-header"><span class="code-lang">BASH — Fix commands</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{N}-fix')">📋 Copy</button></div>
                        <pre><code id="sc-s{N}-fix">{FC}</code></pre></div>
                    </div>
                </div>
            </div>
            <div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution"><h4>✅ Verify — Issue Resolved</h4><p>{VT}</p></div></div></div>
            <div class="sc-step">
                <div class="sc-step-num" style="background:linear-gradient(135deg,#6e7681,#8b949e);">🧹</div>
                <div class="sc-step-content">
                    <button class="sc-fix-toggle" onclick="var el=document.getElementById('sc-s{N}-cleanup-drop');el.classList.toggle('show');if(el.classList.contains('show'))Prism.highlightAllUnder(el);" style="color:#8b949e;border-color:rgba(139,148,158,0.25);background:rgba(139,148,158,0.08);">🧹 Cleanup — Delete All Resources</button>
                    <div class="sc-answer" id="sc-s{N}-cleanup-drop">
                        <div class="code-block"><div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{N}-cleanup')">📋 Copy</button></div>
                        <pre><code id="sc-s{N}-cleanup">{CC}</code></pre></div>
                    </div>
                </div>
            </div>
        </div>
    </div>'''

NS='kubectl delete namespace anihpj'

# S24-S27: exec probe, http probe path, container logs, metrics-server
scenarios = [
(24,"ExecProbe","Exec Probe — livenessProbe with Wrong Shell Command",
 "The anihpj-api pod has an exec liveness probe running /bin/false. It always fails and the pod gets killed repeatedly.",
 CMT("anihpj/ - api-pod.yaml ← Exec probe fails (BUG!)")+"""
kubectl create namespace anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  containers:
  - name: api
    image: nginx:alpine
    livenessProbe:
      exec:
        command:
        - /bin/false    """+CMT("❌ BUG! /bin/false always exits 1 — probe always fails!")+"""
      initialDelaySeconds: 10
      periodSeconds: 5
EOF""",
 "\n".join([LI('<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → RESTARTS climbing'),LI('<strong>2.</strong> <code>kubectl describe pod</code> → "Liveness probe failed: command /bin/false exited with 1"'),LI('<strong>3.</strong> Pod killed repeatedly — API never starts!')]),
 "\n".join([DB(1,'<strong>Check probe command:</strong> <code>kubectl describe pod -n anihpj anihpj-api | grep -A5 Liveness</code><br><span class="li-finding discovery">→ exec [/bin/false] — always exits 1 (failure)!</span>'),DB(2,'<strong>Test manually:</strong> <code>kubectl exec -n anihpj anihpj-api -- /bin/false; echo exit=$?</code><br><span class="li-finding discovery">→ exit=1 — any non-zero = unhealthy</span>'),DB(3,'<strong>Root cause:</strong> <span class="li-finding root-cause">Exec probe uses /bin/false which exits 1. Liveness treats exit 0 as success. Must use a command that returns 0 when healthy.</span>')]),
 "\n".join([TN(0,'Pod restarting → Check probe'),TN(1,'exec exits 1 → Failure'),TN(2,'Fix command → /bin/true or proper check'),TN(3,'Pod Ready')]),
 "Exec probes use exit codes: 0=healthy, non-zero=unhealthy. Always test with kubectl exec first. On CKA: failing exec probe = check command exit code.",
 "\n".join([CMD('kubectl get pods -n anihpj','NAME         READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   6'),CMD('kubectl describe pod -n anihpj anihpj-api | grep -A3 Liveness','Liveness: exec [/bin/false]\n  Warning  Unhealthy  Liveness probe failed: command /bin/false exited with 1')]),
 "\n".join([CMD('kubectl get pods -n anihpj','NAME         READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0')]),
 CMT("Fix: Change exec command to /bin/true or real health check")+"""
kubectl get pod anihpj-api -n anihpj -o yaml | sed 's|/bin/false|/bin/true|' | kubectl replace --force -f -""",
 "Pod stays Running. Exec probe returns 0 (success).",NS),

(25,"HTTPProbe","HTTP Probe Wrong Path — /healthz vs /health",
 "The liveness probe checks /healthz but the app only serves /. The probe gets 404 and kills the pod.",
 CMT("anihpj/ - api-deployment.yaml ← Wrong probe path (BUG!)")+"""
kubectl create namespace anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  replicas: 1
  selector:
    matchLabels:
      app: anihpj-api
  template:
    metadata:
      labels:
        app: anihpj-api
    spec:
      containers:
      - name: api
        image: nginx:alpine
        livenessProbe:
          httpGet:
            path: /healthz    """+CMT("❌ BUG! nginx only serves / — /healthz returns 404!")+"""
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
EOF""",
 "\n".join([LI('<strong>1.</strong> <code>kubectl get pods</code> → RESTARTS climbing'),LI('<strong>2.</strong> <code>kubectl describe pod</code> → "Liveness probe failed: HTTP 404"'),LI('<strong>3.</strong> Probe hitting wrong endpoint — pod never Ready!')]),
 "\n".join([DB(1,'<strong>Check probe path:</strong> <code>kubectl describe pod | grep -A5 Liveness</code><br><span class="li-finding discovery">→ path: /healthz — nginx doesn\'t serve this!</span>'),DB(2,'<strong>Test endpoint:</strong> <code>kubectl exec &lt;pod&gt; -- wget -qO- http://localhost/healthz</code><br><span class="li-finding discovery">→ 404 Not Found — endpoint doesn\'t exist!</span>'),DB(3,'<strong>Root cause:</strong> <span class="li-finding root-cause">Probe path /healthz returns 404. HTTP probes treat >= 400 as failure. Must use valid endpoint like /.</span>')]),
 "\n".join([TN(0,'Pod restarting → Check probe'),TN(1,'404 from /healthz → Wrong path'),TN(2,'Fix path to / → 200 OK'),TN(3,'Pod Ready')]),
 "HTTP probes: 2xx/3xx=healthy, 4xx/5xx=unhealthy. Verify the endpoint exists before deploying. On CKA: 404 probe = wrong path.",
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   3'),CMD('kubectl describe pod | grep -A3 Liveness','Liveness: http-get http://:80/healthz\n  Warning  Unhealthy  Liveness probe failed: HTTP 404')]),
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0')]),
 CMT("Fix: Change probe path from /healthz to /")+"""
kubectl patch deploy anihpj-api -n anihpj -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","livenessProbe":{"httpGet":{"path":"/"}}}]}}}}'""",
 "Pod stays Running with 200 OK responses.",NS),

(26,"ContainerLogs","Missing Container Logs — anihpj Writing to File, Not stdout",
 "The anihpj-api pod writes logs to /var/log/api.log instead of stdout. kubectl logs shows nothing.",
 CMT("anihpj/ - api-pod.yaml ← Logs to file not stdout (BUG!)")+"""
kubectl create namespace anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  containers:
  - name: api
    image: busybox:1.36
    command: ["sh","-c"]
    args:
    - |
      while true; do
        echo "$(date) - Request processed" >> /var/log/api.log    """+CMT("❌ BUG! Writing to file, not stdout!")+"""
        sleep 5
      done
EOF""",
 "\n".join([LI('<strong>1.</strong> <code>kubectl logs -n anihpj anihpj-api</code> → <strong>(no output)</strong>'),LI('<strong>2.</strong> Container running but no logs visible — can\'t debug!'),LI('<strong>3.</strong> kubectl logs is the primary CKA debugging tool!')]),
 "\n".join([DB(1,'<strong>Check command:</strong> <code>kubectl get pod -n anihpj anihpj-api -o yaml | grep -A5 args</code><br><span class="li-finding discovery">→ Output redirected to file: >> /var/log/api.log — NOT stdout!</span>'),DB(2,'<strong>Check file inside:</strong> <code>kubectl exec -n anihpj anihpj-api -- cat /var/log/api.log</code><br><span class="li-finding discovery">→ Logs ARE being written — just to the wrong place</span>'),DB(3,'<strong>Root cause:</strong> <span class="li-finding root-cause">App writes to file, not stdout/stderr. kubectl logs only captures PID 1 stdout/stderr. Use tee to write to both, or use a sidecar.</span>')]),
 "\n".join([TN(0,'kubectl logs empty → Check app'),TN(1,'Output to file → Not stdout'),TN(2,'Fix: tee to stdout + file'),TN(3,'kubectl logs shows output')]),
 "kubectl logs only captures stdout/stderr (12-factor app principle). For file-logging apps, use tee or a sidecar. On CKA: empty kubectl logs = wrong output stream.",
 "\n".join([CMD('kubectl logs -n anihpj anihpj-api','(no output)'),CMD('kubectl exec -n anihpj anihpj-api -- tail -3 /var/log/api.log','Mon Jun  4 10:00:01 UTC - Request processed\nMon Jun  4 10:00:06 UTC - Request processed')]),
 "\n".join([CMD('kubectl logs -n anihpj anihpj-api','Mon Jun  4 10:05:01 UTC - Request processed\nMon Jun  4 10:05:06 UTC - Request processed')]),
 CMT("Fix: Use tee to write to both stdout AND file")+"""
kubectl delete pod anihpj-api -n anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  containers:
  - name: api
    image: busybox:1.36
    command: ["sh","-c"]
    args:
    - |
      while true; do
        msg="$(date) - Request processed"
        echo "$msg" | tee -a /var/log/api.log    """+CMT("✅ tee writes to both stdout and file")+"""
        sleep 5
      done
EOF""",
 "kubectl logs now shows output. Both stdout and file logging work.",NS),

(27,"MetricsServer","metrics-server Not Reporting — Debug kubelet Summary API",
 "kubectl top returns error. The metrics-server isn't running, blocking HPA and resource monitoring.",
 CMT("SIMULATE: metrics-server not deployed (BUG!)")+"""
"""+CMT("Check if metrics-server exists")+"""
kubectl get deployment metrics-server -n kube-system 2>&1
"""+CMT("Try kubectl top — it will fail")+"""
kubectl top nodes""",
 "\n".join([LI('<strong>1.</strong> <code>kubectl top nodes</code> → "error: Metrics API not available"'),LI('<strong>2.</strong> <code>kubectl top pods</code> → Same error — no resource metrics!')]),
 "\n".join([DB(1,'<strong>Check metrics-server:</strong> <code>kubectl get pods -n kube-system -l k8s-app=metrics-server</code><br><span class="li-finding discovery">→ No pods found — not deployed!</span>'),DB(2,'<strong>Check API service:</strong> <code>kubectl get apiservice v1beta1.metrics.k8s.io</code><br><span class="li-finding discovery">→ AVAILABLE: False — API not registered</span>'),DB(3,'<strong>Root cause:</strong> <span class="li-finding root-cause">metrics-server not installed. kubectl top and HPA rely on it to collect kubelet resource metrics via the Summary API.</span>')]),
 "\n".join([TN(0,'kubectl top fails → Check API'),TN(1,'No metrics-server → Not installed'),TN(2,'Deploy metrics-server'),TN(3,'kubectl top works → HPA ready')]),
 "metrics-server is required for kubectl top, HPA, VPA. Without it, resource metrics are unavailable. On CKA: kubectl top failing = check metrics-server deployment in kube-system.",
 "\n".join([CMD('kubectl top nodes','error: Metrics API not available'),CMD('kubectl get pods -n kube-system -l k8s-app=metrics-server','No resources found in kube-system namespace.')]),
 "\n".join([CMD('kubectl top nodes','NAME     CPU(cores)   MEMORY(bytes)\nnode01   150m         2Gi\nnode02   200m         3Gi')]),
 CMT("Fix: Deploy metrics-server")+"""
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl wait --for=condition=Ready pod -l k8s-app=metrics-server -n kube-system --timeout=120s
kubectl top nodes""",
 "kubectl top works. HPA can now use CPU/memory metrics for autoscaling.",
 CMT("No cleanup needed — metrics-server is a cluster component")),
]

for n,s,title,desc,dc,ei,di,ts,tt,eo,ao,fc,vt,cc in scenarios:
    html = TPL.replace('{N}',str(n)).replace('{STATUS}',s).replace('{TITLE}',title).replace('{DESC}',desc).replace('{DC}',dc).replace('{EI}',ei).replace('{DI}',di).replace('{TS}',ts).replace('{TT}',tt).replace('{EO}',eo).replace('{AO}',ao).replace('{FC}',fc).replace('{VT}',vt).replace('{CC}',cc)
    h = h[:P] + html + '\n' + h[P:]

with open('cka_test_prep.html','w',encoding='utf-8') as f: f.write(h)
print('S24-S27 created.')
