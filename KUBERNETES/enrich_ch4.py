import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

def insert_before_qa(ch_start, ch_end, new_content, label):
    global html, changes
    chapter = html[ch_start:ch_end]
    qa_pos = chapter.rfind('class="cka-exam-questions"')
    drill_pos = chapter.rfind('class="ckad-practice-drill"')
    insert_marker = max(qa_pos, drill_pos)
    if insert_marker < 0:
        print("  {}: No Q&A section".format(label))
        return False
    pre = chapter[:insert_marker]
    cmt = pre.rfind('<!--')
    if cmt > insert_marker - 500 and 'Practice' in chapter[cmt:cmt+100]:
        insert_marker = cmt
    abs_insert = ch_start + insert_marker
    html = html[:abs_insert] + new_content + '\n' + html[abs_insert:]
    changes += 1
    print("  {}: Added content".format(label))
    return True

chapter_starts = {}
for ch in range(1, 21):
    pos = html.find('id="ch{}"'.format(ch))
    if pos >= 0:
        chapter_starts[ch] = pos

# ============================================================
# CHAPTER 13: Security - Sealed Secrets, Vault, RBAC Patterns
# ============================================================
ch13_s = chapter_starts.get(13, -1)
ch14_s = chapter_starts.get(14, -1)
if ch13_s > 0 and ch14_s > ch13_s:
    content = '''
                <div class="section-block">
                    <h4>13.7 Secrets Management Strategies - Comparison</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Strategy</th><th>Security Level</th><th>Complexity</th><th>Best For</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Sealed Secrets</strong></td><td>Medium (encrypted, Git-safe)</td><td>Low</td><td>GitOps workflows; simple setup</td></tr>
                            <tr><td><strong>External Secrets Operator</strong></td><td>High (syncs from vault)</td><td>Medium</td><td>AWS/GCP/Azure secrets integration</td></tr>
                            <tr><td><strong>HashiCorp Vault</strong></td><td>Very High (dynamic secrets)</td><td>High</td><td>Enterprise; dynamic DB credentials</td></tr>
                            <tr><td><strong>SOPS + helm-secrets</strong></td><td>High (encrypted values)</td><td>Medium</td><td>Encrypted values.yaml files</td></tr>
                            <tr><td><strong>CI/CD Injection</strong></td><td>Medium (pipeline-only)</td><td>Low</td><td>Simple setups; --set from CI vars</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>13.8 Helm-Specific RBAC Patterns</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm RBAC - Least Privilege Model</div>
<pre>
MINIMUM PERMISSIONS FOR HELM (per namespace):
=============================================
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: helm-deployer
  namespace: anihpj-prod
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps", "services", "pods"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["secrets"]  # For release storage
  verbs: ["get", "list", "create", "update", "delete"]

CI/CD SERVICE ACCOUNT gets helm-deployer Role.
HUMAN OPERATORS get read-only (helm list, helm get) Role.
EMERGENCY ACCESS: Temporary RoleBinding via break-glass process.
</pre>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">GOTCHA</div><div class="ckad-gotcha-content"><strong>RBAC on the Exam:</strong> If Helm can't create Secrets in the release namespace, <code>helm install</code> will fail because Helm 3 stores release info in Secrets. Always grant Secret read/write permissions in the target namespace for the Helm service account.</div></div>
                </div>
                <div class="section-block">
                    <h4>13.9 Image Vulnerability Scanning for Helm Charts</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Scan Chart Images</h5><p>Use Trivy, Grype, or Snyk to scan all container images referenced in your chart's values.yaml and templates.</p><pre>
# Scan all images in a chart:
helm template ./chart | grep 'image:' | awk '{print $2}' | tr -d '"' | \\
  xargs -I {} trivy image {}
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Enforce Policy</h5><p>Use OPA/Gatekeeper or Kyverno to block deployments with CRITICAL/HIGH CVEs. Integrate with admission webhooks.</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Sign Trusted Charts</h5><p>Only allow installation of charts with valid provenance (<code>helm install --verify</code>). Block unsigned charts in production.</p></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch13_s, ch14_s, content, "Ch13: Secrets & RBAC")

# ============================================================
# CHAPTER 15: Exam Strategy - Detailed Time Management & Setup
# ============================================================
ch15_s = chapter_starts.get(15, -1)
ch16_s = chapter_starts.get(16, -1)
if ch15_s > 0 and ch16_s > ch15_s:
    content = '''
                <div class="section-block">
                    <h4>15.9 Exam Day - Minute-by-Minute Plan</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">120-Minute Exam Time Budget</div>
<pre>
TIME    PHASE                    ACTIVITIES
=============================================================================
0-5     SETUP                    Aliases, env vars, helm env, kubectl config
5-10    SCAN                     Read ALL questions, flag easy/medium/hard
10-15   WARM-UP                  Answer 3-5 easiest questions (build momentum)
15-35   EASY PASS                Answer all "easy" flagged questions (~15 Qs)
35-75   MEDIUM PASS              Answer all "medium" flagged questions (~25 Qs)
75-100  HARD PASS                Answer "hard" flagged questions (~15 Qs)
100-110 REVIEW                    Re-check flagged answers, fix typos
110-120 FINAL                    Copy answers, verify aliases, final submit
=============================================================================

FLAG SYSTEM:
  ! = Easy (can answer in <1 min)
  !! = Medium (needs 2-3 min)
  !!! = Hard (needs 5+ min, may skip)
  ? = Unsure (come back after review)

NEVER spend >5 minutes on any single question.
Skip and flag - come back if time permits.
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>15.10 Essential Exam Aliases & Environment</h4>
                    <div class="terminal-block">
                        <div class="terminal-title">Copy these FIRST - Paste into exam terminal</div>
<pre>
# === HELM EXAM ALIASES ===
alias h=helm
alias hi='helm install'
alias hu='helm upgrade'
alias hr='helm rollback'
alias hl='helm list'
alias hls='helm list -A'
alias hg='helm get'
alias hgm='helm get manifest'
alias hgv='helm get values'
alias hhist='helm history'
alias hlint='helm lint --strict'
alias htemplate='helm template --debug'
alias hdry='helm install --dry-run --debug'
alias htest='helm test --logs'
alias hpkg='helm package'
alias hrepo='helm repo'
alias hdep='helm dependency'

# === KUBECTL ALIASES ===
alias k=kubectl
alias kg='kubectl get'
alias kd='kubectl describe'
alias kga='kubectl get all'
alias kgs='kubectl get secrets'
alias kaf='kubectl apply -f'

# === ENVIRONMENT ===
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"
export HELM_EXPERIMENTAL_OCI=1
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Critical:</strong> The first 2 minutes of the exam should be spent copying your prepared alias file. This saves 2-3 seconds PER COMMAND, which adds up to 10+ minutes saved over the full exam. Practice typing these aliases from memory before exam day.</div></div>
                </div>
                <div class="section-block">
                    <h4>15.11 Top 15 Exam Mistakes - Don't Lose Points</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>#</th><th>Mistake</th><th>Impact</th><th>How to Avoid</th></tr></thead>
                        <tbody>
                            <tr><td>1</td><td>Forgetting <code>--namespace</code></td><td>Deploying to wrong namespace = 0 points</td><td>Always use <code>-n</code> flag. Set context namespace.</td></tr>
                            <tr><td>2</td><td>Not using <code>--dry-run</code></td><td>Failed installs waste time</td><td>Always dry-run before actual install</td></tr>
                            <tr><td>3</td><td>Missing <code>--atomic</code></td><td>Partial deployments hard to debug</td><td>Use <code>--atomic --wait</code> for clean rollback</td></tr>
                            <tr><td>4</td><td>Wrong values precedence</td><td>Unexpected configuration</td><td>Memorize: --set > -f (last wins) > values.yaml</td></tr>
                            <tr><td>5</td><td>Template whitespace errors</td><td>Invalid YAML output</td><td>Use <code>{{- -}}</code> for whitespace control</td></tr>
                            <tr><td>6</td><td>Nil pointer dereference</td><td>Template render fails</td><td>Use <code>default</code> function on ALL nullable values</td></tr>
                            <tr><td>7</td><td>Not running <code>helm lint</code></td><td>Syntax errors discovered late</td><td>Lint takes 1 second - always do it first</td></tr>
                            <tr><td>8</td><td>Forgetting <code>helm dependency update</code></td><td>Missing subchart dependencies</td><td>Run after any Chart.yaml dependency change</td></tr>
                            <tr><td>9</td><td>Hook weight conflicts</td><td>Unpredictable hook execution</td><td>Use unique weights for each hook</td></tr>
                            <tr><td>10</td><td>Wrong SemVer constraint</td><td>Dependency resolution fails</td><td>Use explicit ranges: >=1.0.0 <2.0.0</td></tr>
                            <tr><td>11</td><td>Not saving rendered output</td><td>Can't debug failed installs</td><td>Pipe to file: <code>helm template . > out.yaml</code></td></tr>
                            <tr><td>12</td><td>Using <code>template</code> instead of <code>include</code></td><td>Can't pipeline through functions</td><td><code>include</code> returns string; <code>template</code> writes directly</td></tr>
                            <tr><td>13</td><td>Missing <code>.helmignore</code></td><td>Large chart packages include junk</td><td>Always create .helmignore with node_modules, .git, etc.</td></tr>
                            <tr><td>14</td><td>Not testing hooks</td><td>Hook failures block deploy</td><td>Test hooks with <code>helm test</code> before production</td></tr>
                            <tr><td>15</td><td>Copy-paste without adapting</td><td>Wrong namespace/name/values</td><td>Always review pasted commands before executing</td></tr>
                        </tbody>
                    </table></div>
                </div>
'''
    insert_before_qa(ch15_s, ch16_s, content, "Ch15: Exam Strategy")

# ============================================================
# CHAPTER 16: Hands-On Labs - Additional Lab Scenarios
# ============================================================
ch16_s = chapter_starts.get(16, -1)
ch17_s = chapter_starts.get(17, -1)
if ch16_s > 0 and ch17_s > ch16_s:
    content = '''
                <div class="section-block">
                    <h4>16.6 Lab 6: Multi-Environment Deployment with Values Files (15 min)</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Create Environment Values Files</h5><pre>
# values-dev.yaml
replicaCount: 1
image:
  tag: latest
  pullPolicy: Always
ingress:
  enabled: false
resources:
  limits:
    cpu: 200m
    memory: 256Mi

# values-prod.yaml
replicaCount: 3
image:
  tag: v2.0.0
  pullPolicy: IfNotPresent
ingress:
  enabled: true
  host: anihpj.example.com
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Deploy to Both Environments</h5><pre>
helm install anihpj-dev ./anihpj-chart -f values-dev.yaml -n dev --create-namespace
helm install anihpj-prod ./anihpj-chart -f values-prod.yaml -n production --create-namespace
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Verify Different Configurations</h5><pre>
# Check replicas in each env:
kubectl get deploy -n dev anihpj-dev -o jsonpath='{.spec.replicas}'  # Should be 1
kubectl get deploy -n production anihpj-prod -o jsonpath='{.spec.replicas}'  # Should be 3

# Check ingress (should only exist in prod):
kubectl get ingress -n dev      # Should be empty
kubectl get ingress -n production  # Should show anihpj-prod
</pre></div></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>16.7 Lab 7: Hook-Based Database Migration (20 min)</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Create Migration Hook Template</h5><pre>
# templates/hooks/db-migrate.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: anihpj:{{ .Values.image.tag }}
        command: ["python", "manage.py", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ .Release.Name }}-db-secret
              key: url
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Test the Migration Hook</h5><pre>
# Install initial version:
helm install anihpj ./anihpj-chart -n staging --create-namespace

# Verify hook ran:
kubectl get jobs -n staging -l helm.sh/hook
helm history anihpj -n staging

# Upgrade (triggers pre-upgrade hook):
helm upgrade anihpj ./anihpj-chart --set image.tag=v2.1 -n staging
</pre></div></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>16.8 Lab 8: OCI Chart Publishing & Distribution (15 min)</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Package and Push to OCI Registry</h5><pre>
# Set OCI support:
export HELM_EXPERIMENTAL_OCI=1

# Login to registry:
helm registry login ghcr.io -u YOUR_USERNAME

# Package chart:
helm package ./anihpj-chart

# Push to OCI:
helm push anihpj-0.1.0.tgz oci://ghcr.io/YOUR_ORG/helm-charts

# List remote charts:
helm show chart oci://ghcr.io/YOUR_ORG/helm-charts/anihpj --version 0.1.0
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Install from OCI Registry</h5><pre>
# Pull and install:
helm pull oci://ghcr.io/YOUR_ORG/helm-charts/anihpj --version 0.1.0

# Install directly:
helm install anihpj oci://ghcr.io/YOUR_ORG/helm-charts/anihpj \\
  --version 0.1.0 -n production --create-namespace
</pre></div></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>16.9 Lab 9: Troubleshooting Broken Releases (15 min)</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Debug a Failed Installation</h5><pre>
# Simulate a failure: install with invalid image tag
helm install broken ./anihpj-chart --set image.tag=INVALID_TAG -n debug

# Check status:
helm status broken -n debug
helm history broken -n debug

# Get rendered manifests to find the error:
helm get manifest broken -n debug | grep -A5 image

# Fix and upgrade:
helm upgrade broken ./anihpj-chart --set image.tag=v2.0 -n debug
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Detect and Fix Release Drift</h5><pre>
# Someone manually edited a deployment:
kubectl scale deploy broken-anihpj --replicas=10 -n debug

# Detect drift:
kubectl diff -f <(helm get manifest broken -n debug)

# Fix by re-applying Helm state:
helm upgrade broken ./anihpj-chart --reuse-values -n debug
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch16_s, ch17_s, content, "Ch16: Additional Labs")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
