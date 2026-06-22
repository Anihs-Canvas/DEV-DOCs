
$file = 'c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html'
$txt = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

function Add-Code($answerId, $codeBlock) {
    $escapedId = [regex]::Escape($answerId)
    $pattern = "(id=`"$escapedId`".*?)</p>\s*(</div>)"
    if ($script:txt -match $pattern) {
        $full = $Matches[0]
        $before = $Matches[1]
        $after = $Matches[2]
        $repl = $before + '</p>' + "`n" + $codeBlock + "`n" + $after
        $script:txt = $script:txt.Replace($full, $repl)
        return $true
    }
    return $false
}

# Build the enhancements list directly
$enhancements = New-Object System.Collections.ArrayList

# Ch2
[void]$enhancements.Add(@{id='ch2-a1'; code=@'
<div class="diagram-container"><div class="diagram-title">ArgoCD Drift Detection Flow</div><div class="diagram-body"><pre># Manual change (imperative command)
kubectl scale deployment anihpj --replicas=5

# ArgoCD detects drift (within 3 minutes):
#   Desired state (Git):     replicas: 3
#   Actual state (Cluster):  replicas: 5
#   DRIFT DETECTED -> auto-revert to 3

# CORRECT GitOps workflow:
# 1. Edit deployment.yaml: replicas: 5
# 2. git commit -m "Scale anihpj to 5"
# 3. git push
# 4. ArgoCD syncs -> replicas becomes 5</pre></div></div>
'@})
[void]$enhancements.Add(@{id='ch2-a4'; code=@'
<div class="diagram-container"><div class="diagram-title">The 5 Universal K8s Object Fields</div><div class="diagram-body"><pre>apiVersion: apps/v1       # 1. API group/version
kind: Deployment           # 2. Resource type
metadata:                  # 3. Identity (name, labels, namespace)
  name: anihpj-api
spec:                      # 4. Desired state (YOU write)
  replicas: 3
status:                    # 5. Actual state (CONTROLLER writes)
  availableReplicas: 3
# "resources" is inside spec.containers[].resources
# It is NOT a top-level field</pre></div></div>
'@})

# Ch7
[void]$enhancements.Add(@{id='ch7-a1'; code=@'
<div class="diagram-container"><div class="diagram-title">Three Pillars of Observability with anihpj</div><div class="diagram-body"><pre>METRICS (Prometheus):    "Is something broken?"
  http_requests_total{status="500"} -> Counter
  http_request_duration_seconds    -> Histogram
  ALERT when error_rate > 1% for 5 minutes

LOGS (Loki):             "WHY is it broken?"
  {app="anihpj"} |= "ERROR" | json

TRACES (OpenTelemetry):  "WHERE is the bottleneck?"
  web(200ms) -> api(150ms) -> db(800ms!) -> fix db query</pre></div></div>
'@})
[void]$enhancements.Add(@{id='ch7-a3'; code=@'
<pre><code class="language-yaml"># Prometheus ServiceMonitor: Auto-discover anihpj metrics
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: anihpj-api
spec:
  selector:
    matchLabels:
      app: anihpj-api
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics</code></pre>
'@})
[void]$enhancements.Add(@{id='ch7-a5'; code=@'
<pre><code class="language-promql"># PromQL Quick Reference for CNPA Exam
# Error rate of anihpj API (last 5 minutes)
rate(http_requests_total{app="anihpj-api",status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))</code></pre>
'@})

# Ch9
[void]$enhancements.Add(@{id='ch9-a1'; code=@'
<pre><code class="language-yaml"># Kyverno Policy: Require resource limits on ALL pods
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-limits
    match:
      resources:
        kinds: [Pod]
    validate:
      message: "Every container must set CPU and memory limits"
      pattern:
        spec:
          containers:
          - resources:
              limits:
                cpu: "?*"
                memory: "?*"</code></pre>
'@})
[void]$enhancements.Add(@{id='ch9-a3'; code=@'
<div class="diagram-container"><div class="diagram-title">Kubernetes Admission Control Flow</div><div class="diagram-body"><pre>kubectl apply -f pod.yaml
       |
       v
[Authentication] -> WHO are you? (X.509 cert, OIDC token)
       |
       v
[Authorization]  -> Can you DO this? (RBAC)
       |
       v
[Mutating Webhooks]  -> MODIFY request (inject sidecar)
       |
       v
[Validating Webhooks] -> ACCEPT or REJECT (Kyverno/OPA)
       |
       v
[etcd] Persisted ONLY if ALL checks pass</pre></div></div>
'@})

# Ch10
[void]$enhancements.Add(@{id='ch10-a2'; code=@'
<pre><code class="language-yaml"># RBAC: Least-privilege for anihpj API ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: anihpj-api-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]           # Read-only only
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: anihpj-api-binding
subjects:
- kind: ServiceAccount
  name: anihpj-api-sa
roleRef:
  kind: Role
  name: anihpj-api-reader
  apiGroup: rbac.authorization.k8s.io</code></pre>
'@})
[void]$enhancements.Add(@{id='ch10-a5'; code=@'
<pre><code class="language-yaml"># Pod SecurityContext: CNPA Restricted Profile
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
  containers:
  - name: api
    securityContext:
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
      seccompProfile:
        type: RuntimeDefault</code></pre>
'@})

# Ch11
[void]$enhancements.Add(@{id='ch11-a2'; code=@'
<pre><code class="language-yaml"># GitHub Actions: Trivy vulnerability scan in CI
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: registry.anihpj.com/jobpost:${GITHUB_SHA}
    format: table
    exit-code: 1              # FAIL on CRITICAL CVEs
    severity: CRITICAL,HIGH</code></pre>
'@})

# Ch12
[void]$enhancements.Add(@{id='ch12-a1'; code=@'
<div class="diagram-container"><div class="diagram-title">Fail-Fast CI Pipeline: Ordered by Cost</div><div class="diagram-body"><pre>git push triggers:
  |
  v
[LINT: ~30s]    <- CHEAPEST gate
  | FAIL -> STOP (feedback in 30s)
  v
[TEST: ~2min]   <- Medium cost
  | FAIL -> STOP (feedback in 2.5min)
  v
[BUILD: ~3min]  <- Expensive (Docker image)
  | FAIL -> STOP (feedback in 5.5min)
  v
[SCAN: ~1min]   <- Vulnerability check
  |
  v
[SIGN + PUSH]   <- Artifact ready for ArgoCD</pre></div></div>
'@})

# Ch14
[void]$enhancements.Add(@{id='ch14-a3'; code=@'
<pre><code class="language-yaml"># Rolling Update: Zero-downtime (K8s default)
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 1 extra pod during update
      maxUnavailable: 0  # Zero downtime!
  template:
    spec:
      containers:
      - name: api
        image: anihpj-api:v2.3.1</code></pre>
'@})

# Ch17
[void]$enhancements.Add(@{id='ch17-a1'; code=@'
<div class="diagram-container"><div class="diagram-title">Reconciliation Loop — Pseudocode</div><div class="diagram-body"><pre># Every controller runs this INFINITE LOOP
while True:
    # 1. OBSERVE
    desired = etcd.get("spec.replicas")   # "3"
    actual  = count_running_pods()        # "2"
    
    # 2. DIFF
    if desired != actual:                 # 3 != 2
        # 3. ACT: converge
        create_pod()                      # +1 pod
    
    sleep(1)  # Check again in 1 second</pre></div></div>
'@})

# Ch19
[void]$enhancements.Add(@{id='ch19-a1'; code=@'
<pre><code class="language-yaml"># Crossplane Claim: Developer creates THIS to get a database
apiVersion: anihpj.io/v1alpha1
kind: PostgreSQL
metadata:
  name: anihpj-db
spec:
  engine: postgres
  version: "15"
  storage: 50Gi
# Crossplane provisions: RDS + SecurityGroup + SubnetGroup
# Connection details in Secret: anihpj-db-connection</code></pre>
'@})
[void]$enhancements.Add(@{id='ch19-a7'; code=@'
<pre><code class="language-hcl"># Bootstrap: Terraform creates the FIRST cluster
resource "aws_eks_cluster" "bootstrap" {
  name     = "anihpj-bootstrap"
  role_arn = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}
# Then: install Crossplane + ArgoCD on this cluster
# All future infra: Crossplane Claims
# All future clusters: CAPI Cluster CRs</code></pre>
'@})

# Ch20
[void]$enhancements.Add(@{id='ch20-a1'; code=@'
<pre><code class="language-yaml"># Operator CRD: Declare WHAT (not HOW)
apiVersion: anihpj.io/v1alpha1
kind: JobBoard
metadata:
  name: production-board
spec:
  image: anihpj/jobpost:v2.1.0
  replicas: 3
  database:
    engine: postgres
    size: 50Gi
  monitoring: true
# Operator creates: Deployment + Service + Ingress
# + ServiceMonitor + provisions RDS</code></pre>
'@})

# Apply all
$ok = 0; $fail = 0
foreach ($e in $enhancements) {
    if (Add-Code $e.id $e.code) { $ok++ } else { Write-Host "FAILED: $($e.id)"; $fail++ }
}
Write-Host "Added: $ok / Failed: $fail"
[System.IO.File]::WriteAllText($file, $txt, (New-Object System.Text.UTF8Encoding $false))
