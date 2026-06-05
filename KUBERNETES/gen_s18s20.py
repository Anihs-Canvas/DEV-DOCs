#!/usr/bin/env python
import os; os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')
with open('cka_test_prep.html','r',encoding='utf-8') as f: h=f.read()
P=h.rfind('<footer class="footer">')
C=lambda t:f'<span class="token comment"># {t}</span>'
M=lambda p,o:f'<span class="prompt">$</span> {p}\n<span class="output">{o}</span>'
N=lambda: 'kubectl delete namespace anihpj'

def S(num,status,title,desc,dc,ei,di,ts,tt,eo,ao,fc,vt,cc):
    e='\n'.join(f'                    <div class="lookat-item"><span class="li-check fail">✗</span><span>{x}</span></div>' for x in ei)
    d='\n'.join(f'                    <div class="lookat-item"><span class="li-num">{i+1}</span><span>{x}</span></div>' for i,x in enumerate(di))
    t='\n'.join(f'                    <div class="tenet-step"><div class="step-num">{"①②③④⑤"[i]}</div><div class="step-label">{x}</div></div>' for i,x in enumerate(ts))
    e2='\n'.join(f'                <div class="cmd-output">{x}</div>' for x in eo)
    a2='\n'.join(f'                <div class="cmd-output">{x}</div>' for x in ao)
    return f'''
    <div class="scenario-block" id="sc-s{num}">
        <div class="sc-header"><div class="sc-badge">S{num}</div><div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{num} — Category 2: Troubleshooting <span class="sc-status debug">{status}</span></div>
                <h4>{title}</h4>
                <div class="sc-desc"><strong>The Problem:</strong> {desc}</div>
        </div></div>
        <div class="sc-body">
            <div class="sc-step"><div class="sc-step-num deploy">1</div><div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the Setup (CONTAINS THE BUG)</h4>
                    <p style="color:var(--text-secondary);margin-bottom:10px;font-size:14px;">The setup below contains an intentional misconfiguration.</p>
                    <div class="code-block"><div class="code-header"><span class="code-lang">BASH — Apply to cluster</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{num}-code')">📋 Copy</button></div>
                    <pre><code id="sc-s{num}-code">{dc}</code></pre></div>
            </div></div>
            <div class="sc-step error-spot"><div class="sc-step-num">⚠</div><div class="sc-step-content"><h4>⚠️ Observe the Error — Spot What's Broken</h4>
{e}
            </div></div>
            <div class="sc-step debug-find"><div class="sc-step-num">🔍</div><div class="sc-step-content"><h4>🔍 Debug — Find the Root Cause</h4>
{d}
            </div></div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{num}')">🔍 Show Full Answer &amp; Expected Command Outputs</button>
            <div class="sc-answer" id="sc-sa{num}">
                <h5>🧠 Diagnostic Tenet (Thought Process)</h5>
                <div class="tenet-flow">{t}</div>
                <p><strong>Tenet:</strong> {tt}</p>
                <h5>📟 Command Outputs — ERROR State (BEFORE fix)</h5>
{e2}
                <h5>📟 Command Outputs — AFTER Fix</h5>
{a2}
            </div>
            <div class="sc-step"><div class="sc-step-num" style="background:linear-gradient(135deg,#d2991d,#3fb950);">🔧</div><div class="sc-step-content">
                    <button class="sc-fix-toggle" onclick="var el=document.getElementById('sc-s{num}-fix-drop');el.classList.toggle('show');if(el.classList.contains('show'))Prism.highlightAllUnder(el);" style="color:#3fb950;border-color:rgba(63,185,80,0.25);background:rgba(63,185,80,0.08);">🔧 Fix — Apply the Correction</button>
                    <div class="sc-answer" id="sc-s{num}-fix-drop"><div class="code-block"><div class="code-header"><span class="code-lang">BASH — Fix commands</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{num}-fix')">📋 Copy</button></div>
                    <pre><code id="sc-s{num}-fix">{fc}</code></pre></div></div>
            </div></div>
            <div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution"><h4>✅ Verify — Issue Resolved</h4><p>{vt}</p></div></div></div>
            <div class="sc-step"><div class="sc-step-num" style="background:linear-gradient(135deg,#6e7681,#8b949e);">🧹</div><div class="sc-step-content">
                    <button class="sc-fix-toggle" onclick="var el=document.getElementById('sc-s{num}-cleanup-drop');el.classList.toggle('show');if(el.classList.contains('show'))Prism.highlightAllUnder(el);" style="color:#8b949e;border-color:rgba(139,148,158,0.25);background:rgba(139,148,158,0.08);">🧹 Cleanup — Delete All Resources</button>
                    <div class="sc-answer" id="sc-s{num}-cleanup-drop"><div class="code-block"><div class="code-header"><span class="code-lang">BASH</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{num}-cleanup')">📋 Copy</button></div>
                    <pre><code id="sc-s{num}-cleanup">{cc}</code></pre></div></div>
            </div></div>
        </div>
    </div>'''

# S18: OOMKilled
h=h[:P]+S(18,"OOMKilled","OOMKilled — Set Memory Limits for Django App",
    "The anihpj-api pod gets OOMKilled — deployed without memory limits, the app consumes all node memory.",
    f'''{C("anihpj/ └── 01-api-deployment.yaml ← No memory limit (BUG!)")}
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
        image: python:3.11-alpine
        command: ["sh","-c","python -c 'import time; d=[];\\nwhile True: d.append(\"x\"*10**6); time.sleep(0.05)'"]
        resources:
          requests:
            memory: "64Mi"     {C("❌ BUG! No limit — OOMKilled!")}
EOF''',
    ['<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → RESTARTS climbing','<strong>2.</strong> <code>kubectl describe pod</code> → <strong>OOMKilled, Exit Code 137</strong>'],
    ['<strong>Check termination:</strong> <code>kubectl describe pod -n anihpj &lt;pod&gt; | grep -A5 "Last State"</code><br><span class="li-finding discovery">→ Reason: OOMKilled, Exit Code: 137 (128+SIGKILL 9)</span>','<strong>Check memory:</strong> <code>kubectl top pod -n anihpj</code><br><span class="li-finding discovery">→ Memory climbing past 300Mi — no ceiling!</span>','<strong>Root cause:</strong> <span class="li-finding root-cause">No memory limit. Python app consumes increasing memory until kernel OOM killer terminates it. Exit 137 = OOMKilled.</span>'],
    ['Pod restarts → Describe','OOMKilled 137 → Memory issue','Set limit → Pod stable'],
    "Exit code 137 = OOMKilled. Always set memory limits. On CKA: Exit 137 + restarts = check limits.",
    [M('kubectl describe pod -n anihpj anihpj-api-xxx | grep -A5 "Last State"','Last State: Terminated\n  Reason: OOMKilled\n  Exit Code: 137')],
    [M('kubectl get pods -n anihpj','NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0')],
    f'''{C("Patch deployment with memory limit")}
kubectl patch deploy anihpj-api -n anihpj -p '{{"spec":{{"template":{{"spec":{{"containers":[{{"name":"api","resources":{{"limits":{{"memory":"256Mi"}}}}}}]}}}}}}}}'
kubectl rollout restart deploy anihpj-api -n anihpj''',
    'Pod stays Running 1/1. Container OOM capped inside at 256Mi.',N())+'\n'+h[P:]

# S19: Init Container
h=h[:P]+S(19,"InitContainer","Init Container Failure — Wait for Database to Be Ready",
    "The anihpj-api initContainer checks the wrong DB port (5433 instead of 5432) and never completes.",
    f'''{C("anihpj/ └── 01-api-pod.yaml ← Init container wrong port (BUG!)")}
kubectl create namespace anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: anihpj-api
  namespace: anihpj
spec:
  initContainers:
  - name: wait-for-db
    image: busybox:1.36
    command: ["sh","-c","until nc -z anihpj-db 5433; do echo waiting...; sleep 2; done; echo ready!"]    {C("❌ BUG! PostgreSQL is on 5432!")}
  containers:
  - name: api
    image: nginx:alpine
---
apiVersion: v1
kind: Service
metadata:
  name: anihpj-db
  namespace: anihpj
spec:
  ports:
  - port: 5432
    targetPort: 5432
EOF''',
    ['<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → STATUS: <strong>Init:0/1</strong>','<strong>2.</strong> <code>kubectl logs -n anihpj anihpj-api -c wait-for-db</code> → "waiting..." forever'],
    ['<strong>Check DB port:</strong> <code>kubectl get svc -n anihpj anihpj-db</code><br><span class="li-finding discovery">→ Port 5432 — init checking 5433!</span>','<strong>Root cause:</strong> <span class="li-finding root-cause">Init container checks port 5433, but DB is on 5432. Init never completes, blocking main container.</span>'],
    ['Init:0/1 → Check init logs','Wrong port found → Fix','Init succeeds → Pod Running'],
    "Init containers must complete first. Check logs with <code>kubectl logs &lt;pod&gt; -c &lt;init-container&gt;</code>.",
    [M('kubectl get pods -n anihpj','NAME         READY   STATUS\nanihpj-api   0/1     Init:0/1'),M('kubectl logs -n anihpj anihpj-api -c wait-for-db','waiting...\nwaiting...')],
    [M('kubectl logs -n anihpj anihpj-api -c wait-for-db','ready!'),M('kubectl get pods -n anihpj','NAME         READY   STATUS\nanihpj-api   1/1     Running')],
    f'''{C("Fix: replace pod with corrected port")}
kubectl get pod anihpj-api -n anihpj -o yaml | sed 's/5433/5432/g' | kubectl replace --force -f -''',
    'Init completes, main container starts. Pod Running 1/1.',N())+'\n'+h[P:]

# S20: Pod Stuck Terminating  
h=h[:P]+S(20,"Finalizers","Pod Stuck Terminating — Remove Finalizer Blocking Deletion",
    "You delete a pod but it stays Terminating forever — an orphaned finalizer blocks the deletion.",
    f'''{C("anihpj/ └── 01-stuck-pod.yaml ← Orphaned finalizer (BUG!)")}
kubectl create namespace anihpj
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: stuck-pod
  namespace: anihpj
  finalizers:
  - custom.io/cleanup    {C("❌ BUG! No controller handles this finalizer")}
spec:
  containers:
  - name: nginx
    image: nginx:alpine
EOF
kubectl delete pod stuck-pod -n anihpj &
{C("Pod stays Terminating!")}''',
    ['<strong>1.</strong> <code>kubectl get pods -n anihpj</code> → STATUS: <strong>Terminating</strong> for minutes'],
    ['<strong>Check finalizers:</strong> <code>kubectl get pod stuck-pod -n anihpj -o yaml | grep -A2 finalizers</code><br><span class="li-finding discovery">→ finalizers: [custom.io/cleanup] — orphaned!</span>','<strong>Root cause:</strong> <span class="li-finding root-cause">Orphaned finalizer blocks deletion. Kubernetes waits for controller to process it. Must manually remove.</span>'],
    ['Pod stuck Terminating','Check finalizers → orphaned','Remove finalizer → Pod deleted'],
    "Finalizers are pre-deletion hooks. Orphaned ones block deletion. Fix: <code>kubectl patch ... -p '{\"metadata\":{\"finalizers\":[]}}'</code>.",
    [M('kubectl get pods -n anihpj','NAME        READY   STATUS\nstuck-pod   1/1     Terminating')],
    [M('kubectl get pods -n anihpj','No resources found in anihpj namespace.')],
    f'''{C("Remove the blocking finalizer")}
kubectl patch pod stuck-pod -n anihpj -p '{{"metadata":{{"finalizers":[]}}}}' --type=merge''',
    'Pod deleted instantly after removing the finalizer.',N())+'\n'+h[P:]

with open('cka_test_prep.html','w',encoding='utf-8') as f: f.write(h)
print('S18-S20 done.')
