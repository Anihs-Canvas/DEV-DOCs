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
# CHAPTER 19: Advanced Patterns - Post-Renderers, Feature Toggles, Library Charts
# ============================================================
ch19_s = chapter_starts.get(19, -1)
ch20_s = chapter_starts.get(20, -1)
if ch19_s > 0 and ch20_s > ch19_s:
    content = '''
                <div class="section-block">
                    <h4>19.7 Post-Renderers - Helm + Kustomize Integration</h4>
                    <p>Post-renderers let you modify rendered YAML AFTER Helm template rendering but BEFORE applying to Kubernetes. This enables combining Helm's templating with Kustomize's patching.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Post-Renderer Pipeline</div>
<pre>
values.yaml          templates/            kustomization.yaml
    |                     |                       |
    v                     v                       |
+-----------------------------+                   |
| Helm Template Engine        |                   |
| (Go Templates + Sprig)     |                   |
+-------------+---------------+                   |
              |                                   |
              v                                   v
         Rendered YAML    +    Kustomize Patches
              |                     |
              +----------+----------+
                         |
                         v
              +-------------------+
              | Post-Renderer     |
              | (kustomize build) |
              +---------+---------+
                        |
                        v
              Final YAML -> kubectl apply

helm install anihpj ./chart \\
  --post-renderer ./kustomize-wrapper.sh
</pre>
                    </div>
<pre>
# kustomize-wrapper.sh:
#!/bin/bash
cat <&0 > rendered.yaml
kustomize build . && rm rendered.yaml

# kustomization.yaml:
resources:
- rendered.yaml
patchesStrategicMerge:
- increase-replicas.yaml
</pre>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>When to use Post-Renderers:</strong> Use them when you need Kustomize-style patching on top of Helm templating. Common use cases: adding common labels to ALL resources, injecting sidecars, or applying organization-specific security policies that shouldn't be in the chart.</div></div>
                </div>
                <div class="section-block">
                    <h4>19.8 Feature Toggles & Conditional Resources</h4>
                    <p>Use values to control which resources are deployed. This is essential for creating flexible charts that adapt to different environments.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>Toggle Pattern</th><th>Template Code</th><th>Use Case</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Resource Toggle</strong></td><td><code>{{ if .Values.ingress.enabled }}...{{ end }}</code></td><td>Enable/disable entire resources (Ingress, HPA, PVC)</td></tr>
                            <tr><td><strong>Feature Flag</strong></td><td><code>{{ if .Values.features.monitoring }}...{{ end }}</code></td><td>Enable features (Prometheus annotations, sidecars)</td></tr>
                            <tr><td><strong>Environment Switch</strong></td><td><code>{{ if eq .Values.env "prod" }}...{{ end }}</code></td><td>Environment-specific behavior (production-only resources)</td></tr>
                            <tr><td><strong>Version Gating</strong></td><td><code>{{ if semverCompare ">=1.25" .Capabilities.KubeVersion.GitVersion }}...{{ end }}</code></td><td>API version compatibility across clusters</td></tr>
                            <tr><td><strong>Multi-Tenant</strong></td><td><code>{{ if .Values.tenant.isShared }}...{{ end }}</code></td><td>Shared vs dedicated tenant resources</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>19.9 Starter Charts - Organizational Standards</h4>
                    <p>Starter charts are templates for <code>helm create</code>. They encode your organization's standards so every new chart starts compliant.</p>
<pre>
# Create a starter chart:
mkdir -p $HELM_HOME/starters/microservice/
cp -r my-standard-chart/* $HELM_HOME/starters/microservice/

# Use the starter:
helm create my-svc --starter=microservice

# STARTER CHART BEST PRACTICES:
# 1. Include pre-configured _helpers.tpl with org-standard labels
# 2. Pre-set securityContext with non-root user
# 3. Include resource limits/requests with sensible defaults
# 4. Pre-configure liveness/readiness probes
# 5. Add .helmignore for common patterns (node_modules, .git, *.md)
# 6. Include values.schema.json for validation
</pre>
                </div>
'''
    insert_before_qa(ch19_s, ch20_s, content, "Ch19: Post-Renderers & Starters")

# ============================================================
# CHAPTER 20: Troubleshooting - Debug Commands, Common Error Patterns
# ============================================================
ch20_s = chapter_starts.get(20, -1)
appendix_a_pos = html.find('id="appendix-a"')
if ch20_s > 0 and appendix_a_pos > ch20_s:
    content = '''
                <div class="section-block">
                    <h4>20.8 Helm Debugging Command Reference</h4>
                    <div class="terminal-block">
                        <div class="terminal-title">The Complete Debug Toolkit</div>
<pre>
# QUICK CHECKS (seconds)
helm lint ./chart --strict              # Validate chart structure
helm version                            # Check Helm client version
helm env                                # Show Helm environment variables
kubectl version                         # Check K8s cluster version

# RENDER INSPECTION (seconds)
helm template RELEASE ./chart --debug   # Render templates locally
helm install RELEASE ./chart --dry-run --debug  # Simulate + debug
helm get manifest RELEASE -n NS         # See deployed manifests
helm get values RELEASE -n NS --all     # See all computed values
helm get notes RELEASE -n NS            # See NOTES.txt output

# RELEASE DIAGNOSTICS (minutes)
helm status RELEASE -n NS               # Current release state
helm history RELEASE -n NS              # All revisions + status
helm list -A --failed                   # Find failed releases
kubectl get secrets -l owner=helm -A    # All release storage secrets

# DRIFT DETECTION
helm diff upgrade RELEASE ./chart -n NS # Diff against current (needs plugin)
kubectl diff -f <(helm get manifest RELEASE -n NS)  # Native diff

# DEEP DEBUG
helm get manifest RELEASE -n NS | kubectl explain -f -  # Validate resources
kubectl describe deploy RELEASE -n NS    # Pod events & conditions
kubectl logs -l app=RELEASE -n NS --tail=100  # App logs
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>20.9 Error Pattern Recognition - Quick Diagnosis</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Symptom</th><th>Likely Cause</th><th>First Command to Run</th></tr></thead>
                        <tbody>
                            <tr><td><code>Error: cannot re-use a name that is still in use</code></td><td>Release name already exists in namespace</td><td><code>helm list -A | grep NAME</code></td></tr>
                            <tr><td><code>Error: rendered manifests contain a resource that already exists</code></td><td>Resources from another release or manual creation</td><td><code>kubectl get all -n NS -l app!=RELEASE</code></td></tr>
                            <tr><td><code>nil pointer evaluating interface {}.xxx</code></td><td>Accessing undefined value in template</td><td>Check template for <code>.Values.xxx</code> without <code>default</code></td></tr>
                            <tr><td><code>Error: UPGRADE FAILED: another operation is in progress</code></td><td>Previous helm operation still running (pending state)</td><td><code>helm history RELEASE -n NS</code> + check pending state</td></tr>
                            <tr><td><code>Error: create: failed to create: Secret too long</code></td><td>Rendered manifests exceed 1MB Secret size limit</td><td>Split chart or use SQL storage driver</td></tr>
                            <tr><td><code>Error: found in Chart.yaml but missing in charts/</code></td><td>Dependencies not downloaded</td><td><code>helm dependency update</code></td></tr>
                            <tr><td>Pods stuck in Pending</td><td>Resource limits, PVC issues, or node selectors</td><td><code>kubectl describe pod POD -n NS</code></td></tr>
                            <tr><td>Hook never runs</td><td>Wrong annotation, wrong hook type, or weight mismatch</td><td><code>kubectl get jobs -l helm.sh/hook -n NS</code></td></tr>
                            <tr><td>Values don't match expected</td><td>Precedence confusion or --reuse-values on upgrade</td><td><code>helm get values RELEASE -n NS --all</code></td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>20.10 Release Recovery Strategies</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Pending Install/Upgrade Stuck</h5><p>If <code>helm install</code> or <code>helm upgrade</code> gets stuck in <code>pending-*</code> state, you need to manually resolve it:</p><pre>
# Find the stuck release:
kubectl get secret -l owner=helm,status=pending-upgrade -n NS
# Delete the pending secret to unblock:
kubectl delete secret -l owner=helm,status=pending-upgrade -n NS
# Rollback to last good state:
helm rollback RELEASE -n NS
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Complete Release Recovery from Backup</h5><pre>
# If ALL release secrets are lost but you have Chart + values:
helm install REPLACEMENT ./chart \\
  -f recovered-values.yaml \\
  --set "fullnameOverride=ORIGINAL-NAME" \\
  -n NS --create-namespace

# The fullnameOverride ensures resources match existing names
# This is a last-resort recovery when no release history exists
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Preventing Future Disasters</h5><pre>
# Backup all release secrets:
kubectl get secrets -l owner=helm -A -o yaml > helm-backup-$(date +%Y%m%d).yaml

# Or use the SQL storage driver for >1MB releases:
# helm install RELEASE ./chart --storage-driver sql
# See helm.sh/docs for SQL backend configuration
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch20_s, appendix_a_pos, content, "Ch20: Debug Reference & Recovery")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
