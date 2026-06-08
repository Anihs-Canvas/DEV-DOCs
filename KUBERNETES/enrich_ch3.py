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
# CHAPTER 10: Hooks - Weights, Deletion Policies, Failure Handling
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                <div class="section-block">
                    <h4>10.7 Hook Weights - Controlling Execution Order</h4>
                    <p>When multiple hooks of the same type exist, weights determine execution order. Lower weights run FIRST. The default weight is <code>0</code>. Weights can be negative or positive.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Hook Weight Execution Order</div>
<pre>
WEIGHT:  -10           -5            0             5             10
         |              |             |             |              |
pre-install:  [init-secret]  [create-ns]  [default-job]  [migrate-db]  [seed-data]
                (runs first)                                  (runs last)

SAME WEIGHT hooks execute in an undefined order (don't rely on it!)
Use different weights to guarantee ordering.
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Exam Scenario:</strong> "You need to run a DB backup (Job A), then a schema migration (Job B), then a data seed (Job C) before installing the app. How do you ensure order?" Answer: Use pre-install hooks with weights: Job A weight=-10, Job B weight=-5, Job C weight=0. The exam tests weight ordering frequently.</div></div>
                </div>
                <div class="section-block">
                    <h4>10.8 Hook Deletion Policies - Cleanup Strategies</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Policy</th><th>When Resource is Deleted</th><th>Use Case</th></tr></thead>
                        <tbody>
                            <tr><td><code>before-hook-creation</code></td><td>Before a new hook of the same type runs</td><td>Replacing temporary resources; default for most hooks</td></tr>
                            <tr><td><code>hook-succeeded</code></td><td>After the hook resource completes successfully</td><td>One-time migration jobs; cleanup after success</td></tr>
                            <tr><td><code>hook-failed</code></td><td>After the hook resource fails</td><td>Leave failed resources for debugging; auto-cleanup on success</td></tr>
                        </tbody>
                    </table></div>
<pre>
# Hook with deletion policy:
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded, before-hook-creation
    # Multiple policies can be combined with commas

# This means: Delete on success AND delete before next hook of same type
</pre>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">GOTCHA</div><div class="ckad-gotcha-content"><strong>Resource Lifecycle:</strong> Hooks are NOT managed as part of the release. They are NOT updated during <code>helm upgrade</code> unless the hook resource definition changes. If you change a hook's template, Helm will re-create the hook resource on the next operation.</div></div>
                </div>
                <div class="section-block">
                    <h4>10.9 Hook Failure Handling & Timeouts</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Hook Failure Behavior</h5>
                            <ul>
                                <li>If a hook fails, the entire operation (install/upgrade/delete) <strong>fails</strong></li>
                                <li>Failed hooks are NOT automatically retried</li>
                                <li>Use <code>--timeout</code> to set hook timeout (default: 5 min)</li>
                                <li>Hooks can be Jobs or Pods — Jobs are recommended (restartPolicy: Never)</li>
                            </ul>
                        </div>
                        <div class="split-side">
                            <h5>Debugging Failed Hooks</h5>
<pre>
# Check hook status:
kubectl get jobs -l helm.sh/hook
kubectl logs job/hook-job-name

# Check hook events:
kubectl describe job/hook-job-name

# Force re-run by deleting hook resource:
kubectl delete job/hook-job-name
helm upgrade myapp ./chart  # Re-creates hook

# See hook errors in release:
helm status myapp
</pre>
                        </div>
                    </div>
                </div>
'''
    insert_before_qa(ch10_s, ch11_s, content, "Ch10: Hook Weights & Policies")

# ============================================================
# CHAPTER 11: Testing & Validation - CI/CD Integration
# ============================================================
ch11_s = chapter_starts.get(11, -1)
ch12_s = chapter_starts.get(12, -1)
if ch11_s > 0 and ch12_s > ch11_s:
    content = '''
                <div class="section-block">
                    <h4>11.8 Test Pod Design Patterns</h4>
                    <p>Well-designed test pods are the difference between catching issues early and debugging production failures. Here are the key patterns:</p>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">SMOKE</div><h5>Smoke Test</h5><p>Verify the application started and responds. Quick HTTP GET to the service endpoint. Runs fast (~5s).</p><pre>
containers:
- name: smoke-test
  image: curlimages/curl
  command: ["curl", "-f", "http://{{ .Release.Name }}-svc/health"]
</pre></div>
                        <div class="info-card"><div class="card-icon">INTEG</div><h5>Integration Test</h5><p>Verify database connectivity and basic CRUD operations. Takes longer (~30s) but validates the full stack.</p><pre>
containers:
- name: integration-test
  image: anihpj-test:latest
  command: ["./run-tests.sh"]
  env:
  - name: DB_HOST
    value: {{ .Release.Name }}-postgresql
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>11.9 CI/CD Integration - Automated Testing Workflow</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm Test in CI/CD Pipeline</div>
<pre>
GIT PUSH
    |
    v
[1] helm lint ./chart --strict              (1s  - syntax check)
    |
    v
[2] helm template test ./chart --debug      (2s  - render check)
    |
    v
[3] helm install test ./chart --dry-run     (3s  - API validation)
    |
    v
[4] helm install ci-test ./chart -n ci      (30s - actual deploy)
    |
    v
[5] helm test ci-test -n ci --logs          (60s - run test pods)
    |
    v
[6] helm uninstall ci-test -n ci            (10s - cleanup)
    |
    v
[PASS/FAIL]  --  Total time: ~2 minutes per PR
</pre>
                    </div>
                    <div class="info-box tip"><h5>CI/CD Best Practices</h5><ul><li><strong>Always run lint first</strong> - catches 80% of issues in 1 second</li><li><strong>Use dedicated CI namespace</strong> - never test in production namespaces</li><li><strong>Auto-cleanup</strong> - uninstall test releases after testing</li><li><strong>Set timeouts</strong> - <code>helm test --timeout 5m</code> prevents hung CI jobs</li><li><strong>Parallelize</strong> - test multiple charts in parallel using different namespaces</li></ul></div>
                </div>
                <div class="section-block">
                    <h4>11.10 values.schema.json - Advanced Validation</h4>
                    <p>Beyond basic type checking, JSON Schema can enforce complex business rules for chart values.</p>
<pre>
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Number of replicas (1-100)"
    },
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string", "pattern": "^[a-z0-9./-]+$" },
        "tag": { "type": "string", "minLength": 1 },
        "pullPolicy": { "enum": ["Always", "IfNotPresent", "Never"] }
      }
    },
    "ingress": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "host": { "type": "string", "format": "hostname" }
      },
      "if": { "properties": { "enabled": { "const": true } } },
      "then": { "required": ["host"] }
    }
  },
  "required": ["replicaCount", "image"]
}
</pre>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">GOTCHA</div><div class="ckad-gotcha-content"><strong>Conditional Validation:</strong> The <code>if/then</code> pattern above says: IF ingress.enabled is true, THEN host is required. This prevents users from enabling ingress without specifying a hostname. JSON Schema Draft 7 features like <code>if/then/else</code> and <code>$ref</code> are fully supported in Helm 3.</div></div>
                </div>
'''
    insert_before_qa(ch11_s, ch12_s, content, "Ch11: Test Patterns & Schema")

# ============================================================
# CHAPTER 12: Chart Repositories - OCI, Signing, Private Repos
# ============================================================
ch12_s = chapter_starts.get(12, -1)
ch13_s = chapter_starts.get(13, -1)
if ch12_s > 0 and ch13_s > ch12_s:
    content = '''
                <div class="section-block">
                    <h4>12.7 OCI-Based Charts - The Modern Standard</h4>
                    <p>Since Helm 3.8.0, OCI (Open Container Initiative) registries are the recommended way to store and distribute Helm charts. This means charts live alongside container images in the same registry.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>OCI Workflow</h5>
<pre>
# Login to OCI registry:
helm registry login myregistry.io \\
  --username myuser --password mypass

# Package the chart:
helm package ./anihpj-chart

# Push to OCI registry:
helm push anihpj-0.1.0.tgz \\
  oci://myregistry.io/helm-charts

# Pull from OCI registry:
helm pull oci://myregistry.io/helm-charts/anihpj \\
  --version 0.1.0

# Install directly from OCI:
helm install anihpj \\
  oci://myregistry.io/helm-charts/anihpj \\
  --version 0.1.0
</pre>
                        </div>
                        <div class="split-side">
                            <h5>OCI vs Traditional Repos</h5>
                            <div class="compare-table"><table>
                                <tr><th>Feature</th><th>OCI</th><th>Traditional</th></tr>
                                <tr><td>Storage</td><td>Any OCI registry</td><td>HTTP server + index.yaml</td></tr>
                                <tr><td>Auth</td><td>Registry-native</td><td>Basic auth / TLS</td></tr>
                                <tr><td>Versioning</td><td>OCI tags</td><td>SemVer in index</td></tr>
                                <tr><td>Tooling</td><td>helm push/pull</td><td>helm repo add/index</td></tr>
                            </table></div>
                        </div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>12.8 Chart Signing & Provenance Verification</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Chart Signing Workflow</div>
<pre>
CHART AUTHOR                                CHART CONSUMER
+---------------------+                    +---------------------+
| 1. Generate keypair |                    | 1. Import public key|
|    helm gpg gen key  |                    |    gpg --import key |
+----------+----------+                    +----------+----------+
           |                                          |
           v                                          v
+---------------------+                    +---------------------+
| 2. Package + Sign   |                    | 2. Verify signature |
|    helm package      |                    |    helm verify       |
|    --sign --key '..' | ---- .tgz.prov -->|    chart-0.1.0.tgz  |
|    --keyring ~/.gnupg|                    |    --keyring pubring |
+---------------------+                    +---------------------+

helm package --sign produces: chart-0.1.0.tgz + chart-0.1.0.tgz.prov
The .prov file is a detached signature (OpenPGP clearsigned)
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Provenance on the Exam:</strong> You may be asked to verify a chart's integrity. Remember: <code>helm verify</code> checks the provenance file. <code>helm install --verify</code> does verification during installation. The keyring path must be correct.</div></div>
                </div>
                <div class="section-block">
                    <h4>12.9 Private Repository Setup - ChartMuseum & Harbor</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">MUSEUM</div><h5>ChartMuseum</h5><p>Lightweight, open-source Helm chart repository server. Supports multiple storage backends (S3, GCS, Azure, local, Swift). Easy to deploy as a Helm chart itself.</p><pre>
# Deploy ChartMuseum:
helm repo add chartmuseum https://chartmuseum.github.io/charts
helm install chartmuseum chartmuseum/chartmuseum \\
  --set env.open.DISABLE_API=false
</pre></div>
                        <div class="info-card"><div class="card-icon">HARBOR</div><h5>Harbor</h5><p>Enterprise-grade container + Helm chart registry. Built-in RBAC, vulnerability scanning, replication, and OCI support. CNCF Graduated project.</p><pre>
# Add Harbor as Helm repo:
helm repo add harbor https://harbor.mycompany.com/chartrepo/library \\
  --username admin --password xxx

# Or use OCI:
helm registry login harbor.mycompany.com
helm push chart.tgz oci://harbor.mycompany.com/library
</pre></div>
                    </div>
                </div>
'''
    insert_before_qa(ch12_s, ch13_s, content, "Ch12: OCI, Signing, Private Repos")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
