#!/usr/bin/env python
import os; os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')
with open('cka_test_prep.html','r',encoding='utf-8') as f: h=f.read()
P=h.rfind('<footer class="footer">')

# Template with {N} placeholders
TPL='''
    <div class="scenario-block" id="sc-s{N}">
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
                        <div class="code-header">
                            <span class="code-lang">BASH — Fix commands</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{N}-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{N}-fix">{FC}</code></pre>
                        </div>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — Issue Resolved</h4>
                        <p>{VT}</p>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background:linear-gradient(135deg,#6e7681,#8b949e);">🧹</div>
                <div class="sc-step-content">
                    <button class="sc-fix-toggle" onclick="var el=document.getElementById('sc-s{N}-cleanup-drop');el.classList.toggle('show');if(el.classList.contains('show'))Prism.highlightAllUnder(el);" style="color:#8b949e;border-color:rgba(139,148,158,0.25);background:rgba(139,148,158,0.08);">🧹 Cleanup — Delete All Resources</button>
                    <div class="sc-answer" id="sc-s{N}-cleanup-drop">
                        <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{N}-cleanup')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{N}-cleanup">{CC}</code></pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>'''

def LI(text): return f'                    <div class="lookat-item"><span class="li-check fail">✗</span><span>{text}</span></div>'
def DI(text): return f'                    <div class="lookat-item"><span class="li-num">{{n}}</span><span>{text}</span></div>'
def TENET(i,text): return f'                    <div class="tenet-step"><div class="step-num">{"①②③④⑤"[i]}</div><div class="step-label">{text}</div></div>'
def CMD(p,o): return f'                <div class="cmd-output"><span class="prompt">$</span> {p}\n<span class="output">{o}</span></div>'
def CMT(t): return f'<span class="token comment"># {t}</span>'

for n, status, title, desc, dc, ei, di, ts, tt, eo, ao, fc, vt, cc in [
(21,"Liveness","Liveness Probe Misconfigured — Premature Pod Kill on Startup",
 "The anihpj-api pod needs 60s to start, but the liveness probe kicks in at 5s, killing it before boot completes.",
 CMT("anihpj/ └── api-deployment.yaml ← Liveness too aggressive (BUG!)")+"""
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
        command: ["sh","-c","sleep 40; nginx -g 'daemon off;'"]
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 5    """+CMT("❌ BUG! App needs 40s, probe at 5s!")+"""
          periodSeconds: 3
          failureThreshold: 2
EOF""",
 [LI('<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → RESTARTS climbing, never Ready'),
  LI('<strong>2.</strong> <code>kubectl describe pod</code> → "Liveness probe failed"'),
  LI('<strong>3.</strong> Pod trapped in restart loop — API never comes up!')],
 [DI('<strong>Check probe config:</strong> <code>kubectl describe pod -n anihpj &lt;pod&gt; | grep -A5 Liveness</code><br><span class="li-finding discovery">→ initialDelaySeconds: 5 — too fast! App needs ~40s!</span>').replace('{n}','1'),
  DI('<strong>Check previous logs:</strong> <code>kubectl logs -n anihpj &lt;pod&gt; --previous</code><br><span class="li-finding discovery">→ Container killed before nginx started</span>').replace('{n}','2'),
  DI('<strong>Root cause:</strong> <span class="li-finding root-cause">initialDelaySeconds=5 but startup takes 40s. Liveness probe kills the container before the app is ready, causing endless restart loop.</span>').replace('{n}','3')],
 "\n".join([TENET(0,'Pod never Ready → Check events'),TENET(1,'Liveness failing → Too early'),TENET(2,'Fix initialDelaySeconds'),TENET(3,'Pod Ready → API online')]),
 "Liveness probes should give enough time for startup. If your app needs 40s, set initialDelaySeconds=60+. Better yet, use startupProbe.",
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   5'),CMD('kubectl describe pod -n anihpj anihpj-api-xxx | grep -A3 Liveness','Liveness: http-get http://:80/healthz delay=5s\n  Warning  Unhealthy  Liveness probe failed')]),
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0')]),
 CMT("Fix: increase initialDelaySeconds + periodSeconds")+"""
kubectl patch deploy anihpj-api -n anihpj -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","livenessProbe":{"initialDelaySeconds":60,"periodSeconds":10,"failureThreshold":3}}]}}}}'
kubectl rollout restart deploy anihpj-api -n anihpj""",
 "Pod starts, waits 60s before liveness kicks in, becomes Ready 1/1.",
 "kubectl delete namespace anihpj"),

(22,"Readiness","Readiness Probe Failing — anihpj-api /health Returns 500",
 "The anihpj-api pod starts but never becomes Ready. The readiness probe checks /health which returns 500 because the database isn't connected.",
 CMT("anihpj/ └── api-deployment.yaml ← /health returns 500 (BUG!)")+"""
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
        readinessProbe:
          httpGet:
            path: /health    """+CMT("❌ BUG! /health returns 500 when DB is down!")+"""
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
EOF""",
 [LI('<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → READY 0/1, STATUS Running'),
  LI('<strong>2.</strong> <code>kubectl describe pod</code> → "Readiness probe failed: HTTP 500"'),
  LI('<strong>3.</strong> Pod runs but never receives traffic — API effectively DOWN!')],
 [DI('<strong>Check probe response:</strong> <code>kubectl exec -n anihpj &lt;pod&gt; -- wget -qO- http://localhost/health</code><br><span class="li-finding discovery">→ 500 Internal Server Error — DB connection failed!</span>').replace('{n}','1'),
  DI('<strong>Check endpoints:</strong> <code>kubectl get endpoints -n anihpj anihpj-api</code><br><span class="li-finding discovery">→ No endpoints — pod not added to Service!</span>').replace('{n}','2'),
  DI('<strong>Root cause:</strong> <span class="li-finding root-cause">Readiness probe /health returns 500. The pod runs but isn\'t added to Service endpoints, so it never receives traffic.</span>').replace('{n}','3')],
 "\n".join([TENET(0,'Pod Running 0/1 → Check probe'),TENET(1,'/health returns 500 → DB issue'),TENET(2,'Fix endpoint → /health 200'),TENET(3,'Pod Ready 1/1 → Traffic flows')]),
 "Readiness probe fails = pod excluded from Service endpoints. Check the probe endpoint. On CKA: Running but not Ready = readiness probe issue.",
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS\nanihpj-api   0/1     Running'),CMD('kubectl describe pod -n anihpj anihpj-api-xxx | grep Readiness','Warning  Unhealthy  Readiness probe failed: HTTP 500')]),
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS\nanihpj-api   1/1     Running'),CMD('kubectl get endpoints -n anihpj anihpj-api','NAME         ENDPOINTS\nanihpj-api   10.244.1.5:80')]),
 CMT("Fix: Point readiness probe to / instead of /health")+"""
kubectl patch deploy anihpj-api -n anihpj -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","readinessProbe":{"httpGet":{"path":"/"}}}]}}}}'""",
 "Pod becomes Ready 1/1. Service endpoints populated, traffic flows normally.",
 "kubectl delete namespace anihpj"),

(23,"StartupProbe","Startup Probe — Give anihpj-api 120s to Boot Before Liveness",
 "The anihpj-api takes 90s to boot. Without a startupProbe, the liveness probe kills it before it finishes starting.",
 CMT("anihpj/ └── api-deployment.yaml ← No startupProbe (BUG!)")+"""
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
        command: ["sh","-c","sleep 90; nginx -g 'daemon off;'"]
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30    """+CMT("❌ BUG! App takes 90s to start — liveness kills it!")+"""
          periodSeconds: 10
          failureThreshold: 3
EOF""",
 [LI('<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → Pod restarts repeatedly, never Ready'),
  LI('<strong>2.</strong> <code>kubectl describe pod</code> → Liveness kills pod before nginx starts at 90s')],
 [DI('<strong>Check probe timing:</strong> <code>kubectl describe pod -n anihpj &lt;pod&gt; | grep -A5 Liveness</code><br><span class="li-finding discovery">→ delay=30s, but app startup takes 90s — gap of 60s!</span>').replace('{n}','1'),
  DI('<strong>Check restarts:</strong> <code>kubectl get pods -n anihpj</code><br><span class="li-finding discovery">→ RESTARTS counter climbing — pod never stays up</span>').replace('{n}','2'),
  DI('<strong>Root cause:</strong> <span class="li-finding root-cause">No startupProbe. Liveness starts at 30s but app needs 90s. StartupProbe would disable liveness checks until the app is fully started.</span>').replace('{n}','3')],
 "\n".join([TENET(0,'Pod restarting → Check timing'),TENET(1,'App needs 90s, liveness at 30s'),TENET(2,'Add startupProbe → Liveness waits'),TENET(3,'Pod starts → Ready')]),
 "startupProbe disables liveness and readiness until it succeeds. For slow-starting apps, always use startupProbe. On CKA: if a slow app keeps getting killed, add startupProbe.",
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   4')]),
 "\n".join([CMD('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0')]),
 CMT("Fix: Add startupProbe with 120s timeout (24 failures * 5s period)")+"""
kubectl patch deploy anihpj-api -n anihpj --type strategic -p '
spec:
  template:
    spec:
      containers:
      - name: api
        startupProbe:
          httpGet:
            path: /
            port: 80
          periodSeconds: 5
          failureThreshold: 24
        livenessProbe:
          initialDelaySeconds: 0
'""",
 "Pod starts in 90s, startupProbe succeeds after ~120s, liveness takes over. Pod Ready 1/1.",
 "kubectl delete namespace anihpj"),
]:
    data = {'N':n,'STATUS':status,'TITLE':title,'DESC':desc,'DC':dc,'EI':ei,'DI':di,'TS':ts,'TT':tt,'EO':eo,'AO':ao,'FC':fc,'VT':vt,'CC':cc}
    html = TPL
    for k,v in data.items():
        html = html.replace('{'+k+'}', str(v))
    h = h[:P] + html + '\n' + h[P:]

with open('cka_test_prep.html','w',encoding='utf-8') as f: f.write(h)
print('S21-S23 created.')
