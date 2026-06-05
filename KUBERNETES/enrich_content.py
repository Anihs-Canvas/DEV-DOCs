import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

fixes = 0

# === HELPER: Replace the answer section for a scenario ===
def enrich(h, s, new_tenet_steps, new_before_cmds, new_after_cmds):
    """Replace the tenet-flow steps and cmd-output blocks in a scenario's answer section."""
    global fixes
    
    # Find the answer section
    ans_start = h.index(f'id="sc-sa{s}"')
    # Find the closing of sc-answer (before the fix step)
    # Look for </div>\n            <div class="sc-step"><div class="sc-step-num" style="background:linear-gradient
    fix_pattern = f'<div class="sc-step"><div class="sc-step-num" style="background:linear-gradient(135deg,#d2991d,#3fb950)'
    ans_end = h.find(fix_pattern, ans_start)
    if ans_end == -1:
        print(f"  WARN: Can't find fix step after S{s} answer")
        return h
    
    answer_section = h[ans_start:ans_end]
    
    # Find the tenet-flow div
    tf_start = answer_section.index('<div class="tenet-flow">')
    tf_end = answer_section.index('</div>', answer_section.index('</div>\n', tf_start) + 6)
    # Actually, find </div> right before <p><strong>Tenet:
    tenet_p = answer_section.index('<p><strong>Tenet:')
    # The tenet-flow closing is the </div> just before <p><strong>
    tf_close = answer_section.rfind('</div>', 0, tenet_p)
    
    existing_tenet = answer_section[tf_start:tf_close+6]
    
    # Build new tenet-flow
    ts_html = '<div class="tenet-flow">'
    for ts in new_tenet_steps:
        ts_html += f'\n                    <div class="tenet-step"><div class="step-num">{ts[0]}</div><div class="step-label">{ts[1]}</div></div>'
    ts_html += '</div>'
    
    # Replace tenet-flow in answer
    new_answer = answer_section[:tf_start] + ts_html + answer_section[tf_close+6:]
    
    # Now handle cmd-outputs
    # Find BEFORE fix section
    before_idx = new_answer.index('<h5>📟 Command Outputs — ERROR State (BEFORE fix)</h5>')
    after_idx = new_answer.index('<h5>📟 Command Outputs — AFTER Fix</h5>')
    
    # Build new BEFORE cmds
    before_html = '<h5>📟 Command Outputs — ERROR State (BEFORE fix)</h5>'
    for cmd in new_before_cmds:
        before_html += f'\n                <div class="cmd-output"><span class="prompt">$</span> {cmd[0]}\n<span class="output">{cmd[1]}</span></div>'
    
    # Build new AFTER cmds
    after_html = '<h5>📟 Command Outputs — AFTER Fix</h5>'
    for cmd in new_after_cmds:
        after_html += f'\n                <div class="cmd-output"><span class="prompt">$</span> {cmd[0]}\n<span class="output">{cmd[1]}</span></div>'
    
    # Replace in answer
    before_end = new_answer.index('</div>', after_idx - 50)
    # Find the closing </div> of the last AFTER cmd-output - it's the </div> before the answer section closing
    answer_close = new_answer.rindex('</div>')
    
    new_answer = new_answer[:before_idx] + before_html + '\n                ' + after_html + '\n            '
    
    # Replace in full HTML
    h = h[:ans_start] + new_answer + h[ans_end:]
    fixes += 1
    return h

# ===================================================================
# S18: OOMKilled — Set Memory Limits for Django App
# ===================================================================
h = enrich(h, 18,
    [("①","Pod restarts → Check describe"),
     ("②","OOMKilled 137 → Memory leak"),
     ("③","No limits set → BestEffort QoS"),
     ("④","Set 256Mi limit → Burstable QoS"),
     ("⑤","Pod stable → No more OOM")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   5"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A5 'Last State'","Last State: Terminated\n  Reason: OOMKilled\n  Exit Code: 137\n  Started: 2025-01-15T10:30:00Z\n  Finished: 2025-01-15T10:32:15Z"),
     ("kubectl top pod -n anihpj","NAME          CPU   MEMORY\nanihpj-api   50m   380Mi   ← climbing! No ceiling!")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A2 'Limits'","Limits:\n      memory: 256Mi"),
     ("kubectl top pod -n anihpj","NAME          CPU   MEMORY\nanihpj-api   45m   180Mi   ← stable under limit")])

# ===================================================================
# S19: Init Container Failure — Wait for Database to Be Ready
# ===================================================================
h = enrich(h, 19,
    [("①","Pod stuck Init → Check init container"),
     ("②","Init container logs → nc fails"),
     ("③","DB not ready yet → Add retry loop"),
     ("④","Init container succeeds → Main starts"),
     ("⑤","Pod Running → App connected")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   0/1     Init:0/1"),
     ("kubectl logs -n anihpj anihpj-api -c init-db-check","nc: connect to anihpj-db (10.96.1.5) port 5432 (tcp) failed: Connection refused"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A3 'Init'","Init Containers:\n  init-db-check:\n    State: Terminated\n      Exit Code: 1")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running"),
     ("kubectl logs -n anihpj anihpj-api -c init-db-check","anihpj-db (10.96.1.5:5432) open\nDatabase is ready!"),
     ("kubectl logs -n anihpj anihpj-api","Django connected to PostgreSQL\nStarting development server at http://0.0.0.0:8000")])

# ===================================================================
# S20: Pod Stuck Terminating — Remove Finalizer Blocking Deletion
# ===================================================================
h = enrich(h, 20,
    [("①","kubectl delete pod → Stuck Terminating"),
     ("②","Check finalizers → custom/finalizer"),
     ("③","No controller handles it → Remove"),
     ("④","Patch to remove finalizer → Pod deleted"),
     ("⑤","New pod created → Running")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Terminating"),
     ("kubectl get pod anihpj-api -n anihpj -o json | jq '.metadata.finalizers'","[\"custom/finalizer\"]"),
     ("kubectl describe pod -n anihpj anihpj-api | tail -10","Finalizers:  custom/finalizer\nEvents:\n  Warning  FailedDelete  (x15)  pod has finalizers")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running"),
     ("kubectl get pod anihpj-api -n anihpj -o json | jq '.metadata.finalizers'","null")])

# ===================================================================
# S23: Startup Probe — Give anihpj-api 120s to Boot
# ===================================================================
h = enrich(h, 23,
    [("①","Pod restarts → Check probe events"),
     ("②","Startup probe failing at 10s → App needs 60s"),
     ("③","Liveness kills before startup completes"),
     ("④","Set failureThreshold=12 (120s) → App boots"),
     ("⑤","Pod Ready → Probe passes")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Running   4"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A5 'Startup'","Startup:  http-get http://:80/ delay=0s timeout=1s period=10s failure=1\n  Warning  Unhealthy  Startup probe failed: HTTP 503"),
     ("kubectl logs -n anihpj anihpj-api --previous","Django initializing... migrations apply 45/60s\nStartup probe killed before ready!")],
    [("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A3 'Startup'","Startup: http-get http://:80/ delay=0s timeout=1s period=10s failure=12\n  Normal  Started  Container started"),
     ("curl -s http://anihpj-api.anihpj:80/healthz","OK  ✅")])

# ===================================================================
# S30: Audit Log — Track Who Deleted the anihpj Namespace
# ===================================================================
h = enrich(h, 30,
    [("①","Namespace gone → Check audit logs"),
     ("②","Locate audit log file → /var/log/kubernetes/audit.log"),
     ("③","Search for delete namespace → Find user"),
     ("④","Identify user: system:admin → RBAC check"),
     ("⑤","Recreate namespace → Restore resources")],
    [("kubectl get ns anihpj","Error from server (NotFound): namespaces \"anihpj\" not found"),
     ("cat /var/log/kubernetes/audit.log | grep 'anihpj' | grep 'delete' | jq '.user'","{\"username\": \"system:admin\", \"groups\": [\"system:masters\"]}"),
     ("cat /var/log/kubernetes/audit.log | grep 'anihpj' | jq '{user, timestamp, verb}'","{\"user\": \"system:admin\", \"timestamp\": \"2025-01-15T11:30:00Z\", \"verb\": \"delete\"}")],
    [("kubectl get ns anihpj","NAME     STATUS   AGE\nanihpj   Active   30s"),
     ("kubectl get all -n anihpj","No resources found in anihpj namespace."),
     ("cat /var/log/kubernetes/audit.log | grep 'anihpj' | grep 'create' | tail -1","{\"user\": \"kubernetes-admin\", \"verb\": \"create\", \"objectRef\": {\"name\": \"anihpj\"}}")])

# ===================================================================
# S31: ServiceAccount Missing — Pod Can't Access API Server
# ===================================================================
h = enrich(h, 31,
    [("①","kubectl exec → 403 Forbidden"),
     ("②","Check SA mount → default not found"),
     ("③","default SA was deleted → Recreate"),
     ("④","New SA token mounted → API access"),
     ("⑤","Pod can list pods → Working")],
    [("kubectl exec -n anihpj anihpj-api -- curl -k https://kubernetes.default.svc/api","Error: 403 Forbidden"),
     ("kubectl get sa -n anihpj","NAME      SECRETS\n(empty — no ServiceAccounts!)"),
     ("kubectl describe pod -n anihpj anihpj-api | grep -A3 'ServiceAccount'","ServiceAccount: default\nMounts:\n  /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxx (not found)")],
    [("kubectl get sa -n anihpj","NAME      SECRETS   AGE\ndefault   1         10s"),
     ("kubectl exec -n anihpj anihpj-api -- curl -sk https://kubernetes.default.svc/api/v1/namespaces/anihpj/pods","{\"kind\": \"PodList\", \"items\": [...]}"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running")])

# ===================================================================
# S36: kubeconfig Wrong Context
# ===================================================================
h = enrich(h, 36,
    [("①","kubectl get pods → connection refused"),
     ("②","Check current context → wrong-cluster"),
     ("③","kubectl config view → context mismatch"),
     ("④","Switch to correct context → anihpj-cluster"),
     ("⑤","kubectl works → Pods visible")],
    [("kubectl get pods","The connection to the server localhost:8080 was refused - did you specify the right host or port?"),
     ("kubectl config current-context","wrong-cluster"),
     ("kubectl config view --minify","apiVersion: v1\nclusters:\n- cluster:\n    server: https://127.0.0.1:6443\n  name: wrong-cluster\ncontexts:\n- context:\n    cluster: wrong-cluster\n    user: wrong-admin\n  name: wrong-cluster\ncurrent-context: wrong-cluster")],
    [("kubectl config use-context anihpj-admin@anihpj-cluster","Switched to context \"anihpj-admin@anihpj-cluster\"."),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running"),
     ("kubectl config current-context","anihpj-admin@anihpj-cluster")])

# ===================================================================
# S37: StorageClass Not Default — PVC Without storageClassName
# ===================================================================
h = enrich(h, 37,
    [("①","PVC Pending → Check describe"),
     ("②","No default StorageClass → Check SC list"),
     ("③","PVC has no storageClassName → No SC to bind"),
     ("④","Set default annotation → PVC binds"),
     ("⑤","Pod starts → Volume mounted")],
    [("kubectl get pvc -n anihpj","NAME             STATUS    VOLUME\nanihpj-db-data   Pending"),
     ("kubectl get sc","NAME          PROVISIONER                    RECLAIMPOLICY\nfast-ssd-sc   kubernetes.io/no-provisioner   Retain\n(no default annotation!)"),
     ("kubectl describe pvc -n anihpj anihpj-db-data | grep -A3 Events","Events:\n  Warning  ProvisioningFailed  storageclass.storage.k8s.io \"\" not found\n  (PVC has no storageClassName and no default SC exists)")],
    [("kubectl annotate sc fast-ssd-sc storageclass.kubernetes.io/is-default-class=true","storageclass.storage.k8s.io/fast-ssd-sc annotated"),
     ("kubectl get pvc -n anihpj","NAME             STATUS   VOLUME\nanihpj-db-data   Bound    anihpj-db-pv"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-db-0   1/1     Running")])

# ===================================================================
# S38: Service Type LoadBalancer Pending
# ===================================================================
h = enrich(h, 38,
    [("①","Service EXTERNAL-IP → Pending"),
     ("②","Check service type → LoadBalancer"),
     ("③","No cloud provider → No LB provisioner"),
     ("④","Change to NodePort → Accessible"),
     ("⑤","App reachable via NodePort")],
    [("kubectl get svc -n anihpj","NAME        TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)\nanihpj-api  LoadBalancer   10.96.1.100   &lt;pending&gt;     80:30080/TCP"),
     ("kubectl describe svc -n anihpj anihpj-api | grep -A3 Events","Events:\n  Warning  CreatingLoadBalancerFailed  Error creating load balancer: cloud provider not configured"),
     ("kubectl get nodes -o wide","NAME      STATUS   EXTERNAL-IP\nnode01    Ready    192.168.1.10   ← bare metal, no cloud LB")],
    [("kubectl get svc -n anihpj","NAME        TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)\nanihpj-api  NodePort   10.96.1.100   &lt;none&gt;       80:30080/TCP"),
     ("curl http://192.168.1.10:30080/healthz","OK  ✅"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running")])

# ===================================================================
# S39: ConfigMap Too Large — Exceeds 1MB Limit
# ===================================================================
h = enrich(h, 39,
    [("①","kubectl apply → Request entity too large"),
     ("②","Check ConfigMap size → 1.2MB > 1MB limit"),
     ("③","etcd has 1.5MB total limit per object"),
     ("④","Split into multiple ConfigMaps or use Secret"),
     ("⑤","Apply succeeds → Pod reads config")],
    [("kubectl apply -f large-config.yaml","Error from server (RequestEntityTooLarge): the object is too large (1.2MB), max allowed size is 1MB"),
     ("ls -lh config-data.json","-rw-r--r-- 1 root root 1.2M Jan 15 11:00 config-data.json"),
     ("kubectl get cm -n anihpj large-config 2>&1 || echo 'NOT FOUND'","Error from server (NotFound): configmaps \"large-config\" not found\nNOT FOUND")],
    [("kubectl get cm -n anihpj","NAME               DATA   AGE\nanihpj-config-a    1      10s\nanihpj-config-b    1      10s"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS\nanihpj-api   1/1     Running"),
     ("kubectl exec -n anihpj anihpj-api -- cat /etc/config/part-a | wc -c","614400  (600KB — under limit)")])

# ===================================================================
# S40: Too Many Open Files — ulimit in Container
# ===================================================================
h = enrich(h, 40,
    [("①","Pod crashes → Check logs for EMFILE"),
     ("②","ulimit -n shows 1024 → Too low"),
     ("③","App opens 2000+ file descriptors"),
     ("④","Set securityContext with higher ulimit"),
     ("⑤","Pod stable → No more EMFILE")],
    [("kubectl logs -n anihpj anihpj-api --previous","Error: EMFILE: too many open files, open '/data/cache/idx_3847'\n  at process_open (native)"),
     ("kubectl exec -n anihpj anihpj-api -- sh -c 'ulimit -n'","1024"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   0/1     Error     6")],
    [("kubectl exec -n anihpj anihpj-api -- sh -c 'ulimit -n'","65536"),
     ("kubectl get pods -n anihpj","NAME          READY   STATUS    RESTARTS\nanihpj-api   1/1     Running   0"),
     ("kubectl logs -n anihpj anihpj-api | tail -3","Listening on port 8000\nFile descriptors open: 1847/65536")])

print(f"\nEnriched {fixes} scenarios with expanded tenet-steps and cmd-outputs.")

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("File saved.")
