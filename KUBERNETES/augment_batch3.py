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
# CHAPTER 12: Chart Repositories - Add repo management, Artifact Hub, air-gapped
# ============================================================
ch12_s = chapter_starts.get(12, -1)
ch13_s = chapter_starts.get(13, -1)
if ch12_s > 0 and ch13_s > ch12_s:
    content = '''
                <div class="section-block">
                    <h4>12.10 Repository Management - Complete Command Reference</h4>
                    <div class="terminal-block">
                        <div class="terminal-title">Every Repo Command You Need</div>
<pre>
# ADD REPOSITORIES
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable
helm repo add myrepo https://myrepo.io/charts --username user --password pass

# LIST & SEARCH
helm repo list                          # Show all configured repos
helm search repo nginx                  # Search ALL repos for "nginx"
helm search repo bitnami/nginx          # Search specific repo
helm search repo --versions bitnami/nginx  # Show ALL versions
helm search hub nginx                   # Search Artifact Hub (broader)

# UPDATE & REMOVE
helm repo update                        # Refresh all repo indexes
helm repo remove bitnami                # Remove a repo
helm repo index ./charts                # Generate index.yaml for local repo

# SHOW CHART DETAILS
helm show chart bitnami/nginx           # Chart.yaml contents
helm show values bitnami/nginx          # Default values.yaml
helm show readme bitnami/nginx          # README.md
helm show all bitnami/nginx             # Everything
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>12.11 Artifact Hub - The Helm Chart Marketplace</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Artifact Hub Architecture</div>
<pre>
ARTIFACT HUB (artifacthub.io)
═══════════════════════════════════════════════════════════
    A centralized discovery platform for cloud-native artifacts

SUPPORTED ARTIFACT TYPES:
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Helm     │ OPA      │ Falco    │ Tinkerbell│ KubeArmor│
│ Charts   │ Policies │ Rules    │ Templates │ Profiles │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ OLM      │ Tekton   │ KCL      │ Inspektor │ Headlamp │
│ Operators│ Tasks    │ Packages │ Gadget    │ Plugins  │
└──────────┴──────────┴──────────┴──────────┴──────────┘

CHART SUBMISSION:
1. Package chart: helm package ./mychart
2. Push to OCI or HTTP repo
3. Add repository URL to Artifact Hub
4. Artifact Hub scans index.yaml and lists your chart

SEARCH TIPS:
helm search hub nginx --max-col-width=0  # Full width output
helm search hub "database" --list-repo-url  # Show repo URLs
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>12.12 Air-Gapped & Offline Environments</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Download Charts for Offline Use</h5><pre>
# Download chart + dependencies to local .tgz:
helm pull bitnami/postgresql --version 12.1.0 --destination ./offline-charts/

# Download with all dependencies:
helm pull bitnami/postgresql --version 12.1.0 --untar
cd postgresql && helm dependency update
cd .. && helm package postgresql
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Set Up Local Repository</h5><pre>
# Create index for local charts:
helm repo index ./offline-charts/

# Serve with any HTTP server:
python3 -m http.server 8080 --directory ./offline-charts/

# Add to Helm:
helm repo add local http://localhost:8080
helm install myapp local/mychart
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Use OCI for Air-Gapped</h5><pre>
# Push to internal OCI registry:
helm push mychart-0.1.0.tgz oci://internal-registry.local/charts

# Pull and install:
helm pull oci://internal-registry.local/charts/mychart --version 0.1.0
helm install myapp ./mychart-0.1.0.tgz
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch12_s, ch13_s, content, "Ch12: Repo Management & Air-Gapped")

# ============================================================
# CHAPTER 13: Security - Add Network Policies, SecurityContext, supply chain
# ============================================================
ch13_s = chapter_starts.get(13, -1)
ch14_s = chapter_starts.get(14, -1)
if ch13_s > 0 and ch14_s > ch13_s:
    content = '''
                <div class="section-block">
                    <h4>13.10 Pod Security Standards in Helm Charts</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🔒</div><h5>Restricted Security Context</h5><pre>
# values.yaml
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault

containerSecurityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
</pre></div>
                        <div class="info-card"><div class="card-icon">🛡️</div><h5>Template Usage</h5><pre>
# templates/deployment.yaml
spec:
  securityContext:
    {{- toYaml .Values.podSecurityContext | nindent 4 }}
  containers:
  - name: {{ .Chart.Name }}
    securityContext:
      {{- toYaml .Values.containerSecurityContext | nindent 6 }}
</pre></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Security on the Exam:</strong> Questions may ask you to "ensure the pod runs as non-root" or "drop all capabilities." The answer is always in the securityContext. Include sensible defaults in values.yaml and use <code>toYaml</code> in templates.</div></div>
                </div>
                <div class="section-block">
                    <h4>13.11 Chart Supply Chain Security</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Sign Charts</h5><p>Use GPG/PGP to sign charts. The <code>.prov</code> file is a detached signature that proves authenticity.</p><pre>
helm package --sign --key 'mykey' --keyring ~/.gnupg/secring.gpg ./chart
# Produces: chart-0.1.0.tgz + chart-0.1.0.tgz.prov
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Verify Before Install</h5><pre>
helm verify chart-0.1.0.tgz --keyring ~/.gnupg/pubring.gpg
helm install --verify myapp chart-0.1.0.tgz
# Fails if signature is invalid or missing
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Scan Images in Charts</h5><pre>
# Extract all images from a chart:
helm template ./chart | grep 'image:' | awk '{print $2}' | tr -d '"'
# Scan each with Trivy:
trivy image nginx:1.25
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch13_s, ch14_s, content, "Ch13: Pod Security & Supply Chain")

# ============================================================
# CHAPTER 15: Exam Strategy - Add mental models, quick reference cards
# ============================================================
ch15_s = chapter_starts.get(15, -1)
ch16_s = chapter_starts.get(16, -1)
if ch15_s > 0 and ch16_s > ch15_s:
    content = '''
                <div class="section-block">
                    <h4>15.12 Mental Models for the Exam</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🧠</div><h5>The Install Decision Tree</h5><pre>
Is this a NEW app?
  YES -> helm install NAME ./chart -n NS
  NO  -> Does it need CHANGES?
           YES -> helm upgrade NAME ./chart -n NS
           NO  -> Done!

Did the upgrade FAIL?
  YES -> helm rollback NAME -n NS
  NO  -> Done!

Need to REMOVE?
  YES -> helm uninstall NAME -n NS

Need to CHECK what's deployed?
  -> helm list -A
  -> helm history NAME -n NS
  -> helm get manifest NAME -n NS
</pre></div>
                        <div class="info-card"><div class="card-icon">🔍</div><h5>The Debug Decision Tree</h5><pre>
Chart won't LINT?
  -> Check Chart.yaml syntax
  -> Check template {{ }} balance
  -> helm lint ./chart --strict

Template won't RENDER?
  -> Check .Values.xxx exists
  -> Add | default "fallback"
  -> helm template ./chart --debug

Install FAILS?
  -> helm install --dry-run --debug
  -> Check namespace exists
  -> Check RBAC permissions

Release DRIFTS?
  -> helm get manifest | kubectl diff -f -
  -> helm upgrade --reuse-values
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>15.13 Quick Reference Card - Print Before Exam</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">THE HELM EXAM CHEAT SHEET</div>
<pre>
═══════════════════════════════════════════════════════════════
VALUE PRECEDENCE: --set > -f (last wins) > values.yaml
═══════════════════════════════════════════════════════════════
INSTALL:  helm install NAME ./chart -n NS --create-namespace
UPGRADE:  helm upgrade NAME ./chart -n NS --atomic --wait
ROLLBACK: helm rollback NAME [REV] -n NS
UNINSTALL: helm uninstall NAME -n NS --keep-history
LIST:     helm list -A | helm list -n NS --failed
HISTORY:  helm history NAME -n NS
GET:      helm get manifest|values|hooks|notes NAME -n NS
═══════════════════════════════════════════════════════════════
LINT:     helm lint ./chart --strict
TEMPLATE: helm template NAME ./chart --debug
DRYRUN:   helm install NAME ./chart --dry-run --debug
TEST:     helm test NAME -n NS --logs
═══════════════════════════════════════════════════════════════
PACKAGE:  helm package ./chart
PUSH OCI: helm push FILE.tgz oci://REGISTRY/REPO
PULL OCI: helm pull oci://REGISTRY/REPO/CHART --version X
DEP:      helm dependency update
REPO:     helm repo add NAME URL; helm repo update
═══════════════════════════════════════════════════════════════
template  = writes directly to output (NO piping)
include   = returns string (CAN pipe through functions)
default   = fallback value if null/empty
required  = error if null/empty
toYaml    = convert object to YAML string
nindent N = newline + indent N spaces
quote     = wrap in double quotes
b64enc    = base64 encode (for Secrets)
tpl       = render a string as a template
lookup    = query K8s API at render time
═══════════════════════════════════════════════════════════════
</pre>
                    </div>
                </div>
'''
    insert_before_qa(ch15_s, ch16_s, content, "Ch15: Mental Models & Cheat Sheet")

# ============================================================
# APPENDIX E: Common Errors - Expand significantly
# ============================================================
app_e_start = html.find('id="appendix-e"')
app_f_start = html.find('id="appendix-f"')
if app_e_start > 0 and app_f_start > app_e_start:
    chapter = html[app_e_start:app_f_start]
    qa_pos = chapter.rfind('class="cka-exam-questions"')
    insert_marker = qa_pos if qa_pos > 0 else chapter.rfind('</div>')
    if insert_marker < 0:
        insert_marker = len(chapter) - 100
    abs_insert = app_e_start + insert_marker
    
    content = '''
                <div class="section-block">
                    <h4>E.2 Additional Error Patterns</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Error Message</th><th>Root Cause</th><th>Fix</th></tr></thead>
                        <tbody>
                            <tr><td><code>Error: "helm upgrade" requires 2 arguments</code></td><td>Missing release name or chart path</td><td><code>helm upgrade NAME ./chart</code></td></tr>
                            <tr><td><code>Error: chart requires kubeVersion: >=1.25.0 which is incompatible with Kubernetes v1.24.0</code></td><td>Chart kubeVersion constraint blocks old K8s</td><td>Upgrade cluster or use older chart version</td></tr>
                            <tr><td><code>Error: file 'Chart.yaml' already exists in the chart</code></td><td>Running helm create in existing chart dir</td><td>Use a different directory or remove existing files</td></tr>
                            <tr><td><code>Error: release NAME failed: services "NAME" already exists</code></td><td>Resource from another release or manual creation</td><td>Delete conflicting resource or use different release name</td></tr>
                            <tr><td><code>Error: looks like "URL" is not a valid chart repository</code></td><td>Repo index.yaml missing or malformed</td><td>Verify URL, check index.yaml exists</td></tr>
                            <tr><td><code>Error: no cached repository for ...</code></td><td>helm repo update not run after adding repo</td><td><code>helm repo update</code></td></tr>
                            <tr><td><code>Error: UPGRADE FAILED: has no deployed releases</code></td><td>Tried to upgrade a non-existent release</td><td>Use <code>helm install</code> first or <code>--install</code> flag</td></tr>
                            <tr><td><code>Error: failed to download "chart.tgz"</code></td><td>Dependency not downloaded or network issue</td><td><code>helm dependency update</code></td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>E.3 Template-Specific Error Patterns</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Common Template Error Messages Decoded</div>
<pre>
ERROR: nil pointer evaluating interface {}.XXX
  MEANS: You accessed .Values.XXX but XXX is undefined
  FIX:   Use {{ .Values.XXX | default "fallback" }}
  CHECK:  Is XXX defined in values.yaml?

ERROR: template: CHART/templates/DEPLOY.yaml:15: unexpected "}"
  MEANS: Missing or extra {{ }} delimiter
  FIX:   Check line 15 for unbalanced braces
  CHECK:  Count {{ and }} - they must match

ERROR: at < .Values.image >: wrong type for value; expected string; got int
  MEANS: Type mismatch - value is number but template expects string
  FIX:   Use {{ .Values.image | toString }} or {{ .Values.image | quote }}
  CHECK:  Is the value type correct in values.yaml?

ERROR: executing "CHART/templates/DEPLOY.yaml" at <include "FULLNAME" .>: 
       error calling include: template "FULLNAME" not defined
  MEANS: Named template is referenced but not defined in _helpers.tpl
  FIX:   Define the template with {{ define "FULLNAME" }}...{{ end }}
  CHECK:  Is the template name spelled correctly?
</pre>
                    </div>
                </div>
'''
    html = html[:abs_insert] + content + '\n' + html[abs_insert:]
    changes += 1
    app_f_start = html.find('id="appendix-f"')  # Update position
    print("  AppE: Expanded errors")

# ============================================================
# APPENDIX F: Exam Quick Facts - Expand with study resources
# ============================================================
app_f_start2 = html.find('id="appendix-f"')
footer_start = html.find('id="footer"')
if footer_start < 0:
    footer_start = html.find('<!-- FOOTER -->')
if footer_start < 0:
    footer_start = len(html) - 500

if app_f_start2 > 0 and footer_start > app_f_start2:
    chapter = html[app_f_start2:footer_start]
    qa_pos = chapter.rfind('class="cka-exam-questions"')
    insert_marker = qa_pos if qa_pos > 0 else chapter.rfind('</div>')
    if insert_marker < 0:
        insert_marker = len(chapter) - 100
    abs_insert = app_f_start2 + insert_marker
    
    content = '''
                <div class="section-block">
                    <h4>F.2 Study Resources & Links</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">📚</div><h5>Official Resources</h5><ul><li><strong>Helm Docs:</strong> helm.sh/docs</li><li><strong>Artifact Hub:</strong> artifacthub.io</li><li><strong>CNCF Helm Page:</strong> cncf.io/projects/helm</li><li><strong>Helm GitHub:</strong> github.com/helm/helm</li><li><strong>Chart Best Practices:</strong> helm.sh/docs/chart_best_practices</li></ul></div>
                        <div class="info-card"><div class="card-icon">🎓</div><h5>Supplementary Learning</h5><ul><li><strong>Go Template Docs:</strong> pkg.go.dev/text/template</li><li><strong>Sprig Functions:</strong> masterminds.github.io/sprig</li><li><strong>SemVer Spec:</strong> semver.org</li><li><strong>Kubernetes API Refs:</strong> kubernetes.io/docs/reference</li></ul></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>F.3 Exam Day Checklist</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Before Exam (Night Before)</h5><ul><li>✅ Practice typing aliases 5 times from memory</li><li>✅ Review value precedence order</li><li>✅ Review helm install/upgrade/rollback commands</li><li>✅ Review template functions: default, required, include vs template</li><li>✅ Sleep 8 hours</li></ul></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>During Exam (First 5 Minutes)</h5><ul><li>✅ Copy-paste aliases into terminal</li><li>✅ Set environment variables</li><li>✅ Verify helm version and cluster access</li><li>✅ Read ALL questions (flag: easy/medium/hard)</li></ul></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>During Exam (Per Question)</h5><ul><li>✅ helm lint before every install</li><li>✅ --dry-run before actual deploy</li><li>✅ --atomic --wait for safety</li><li>✅ helm history to verify state</li><li>✅ Copy working commands to answer file immediately</li></ul></div></div>
                    </div>
                </div>
'''
    html = html[:abs_insert] + content + '\n' + html[abs_insert:]
    changes += 1
    print("  AppF: Expanded exam facts")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
