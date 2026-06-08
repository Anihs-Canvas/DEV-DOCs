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
for ch in range(1, 22):
    pos = html.find('id="ch{}"'.format(ch))
    if pos >= 0:
        chapter_starts[ch] = pos

# ============================================================
# CHAPTER 7: Add Chart Tips & Tricks from official docs
# ============================================================
ch7_s = chapter_starts.get(7, -1)
ch8_s = chapter_starts.get(8, -1)
if ch7_s > 0 and ch8_s > ch7_s:
    content = '''
                <div class="section-block">
                    <h4>7.16 Chart Development Tips & Tricks (from Official Docs)</h4>
                    <p>These are battle-tested techniques from Helm chart maintainers, compiled from the official Chart Development Tips and Tricks guide.</p>
                    
                    <h5>Using the tpl Function — Template Inside a Template</h5>
                    <p>The <code>tpl</code> function evaluates a string AS a template. This is powerful for injecting template strings via values or external files.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">How tpl Works</div>
<pre>
# values.yaml
templateString: "{{ .Values.name }}"
name: "Tom"

# Template:
evaluated: {{ tpl .Values.templateString . }}
# Output: evaluated: Tom

# ADVANCED: Rendering external config files
# values.yaml:
firstName: Peter
lastName: Parker

# files/conf/app.conf:
firstName={{ .Values.firstName }}
lastName={{ .Values.lastName }}

# Template:
{{ tpl (.Files.Get "conf/app.conf") . }}
# Output:
firstName=Peter
lastName=Parker
</pre>
                    </div>

                    <h5>Creating Image Pull Secrets Automatically</h5>
<pre>
# values.yaml
imageCredentials:
  registry: quay.io
  username: someone
  password: sillyness
  email: someone@host.com

# _helpers.tpl
{{- define "imagePullSecret" }}
{{- with .Values.imageCredentials }}
{{- printf "{\\"auths\\":{\\"%s\\":{\\"username\\":\\"%s\\",\\"password\\":\\"%s\\",\\"email\\":\\"%s\\",\\"auth\\":\\"%s\\"}}}" .registry .username .password .email (printf "%s:%s" .username .password | b64enc) | b64enc }}
{{- end }}
{{- end }}

# templates/secret.yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: {{ template "imagePullSecret" . }}
</pre>

                    <h5>Automatically Rolling Deployments on Config Change</h5>
                    <p>Use <code>sha256sum</code> in a Deployment annotation to trigger automatic pod restarts when ConfigMaps or Secrets change:</p>
<pre>
kind: Deployment
spec:
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
# Each time the ConfigMap or Secret changes, the Deployment's pod template
# annotation changes → triggers a rolling update automatically!
</pre>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Gotcha:</strong> In library charts, you cannot use <code>$.Template.BasePath</code>. Instead, use <code>{{ include "mylibchart.configmap" . | sha256sum }}</code> referencing the named template directly.</div></div>

                    <h5>Preventing Helm from Uninstalling a Resource</h5>
                    <p>The annotation <code>helm.sh/resource-policy: keep</code> tells Helm to NEVER delete this resource — even during <code>helm uninstall</code>. The resource becomes orphaned (no longer managed by Helm).</p>
<pre>
kind: Secret
metadata:
  annotations:
    "helm.sh/resource-policy": keep
  name: critical-data
# This Secret survives helm uninstall!
# WARNING: helm install --replace will conflict with orphaned resources
</pre>
                </div>
'''
    insert_before_qa(ch7_s, ch8_s, content, "Ch7: Chart Tips & Tricks")

# ============================================================
# CHAPTER 10: Add official Hook Lifecycle step-by-step
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                <div class="section-block">
                    <h4>10.12 The Complete Hook Lifecycle — Step by Step (from Official Docs)</h4>
                    <p>The official Helm documentation defines the exact 13-step lifecycle for a <code>helm install</code> with hooks. Understanding this precise sequence is critical for debugging hook-related issues.</p>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>User runs helm install</h5><p><code>helm install foo ./chart</code> — The Helm client sends the install request to the Helm library (SDK).</p></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Helm library install API is called</h5><p>The SDK's install function is invoked with the chart, values, and options.</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>CRDs in crds/ directory are installed</h5><p>Any Custom Resource Definitions in the <code>crds/</code> directory are applied FIRST, before any templates are rendered. CRDs are NOT managed as part of the release — they're never updated or deleted by Helm.</p></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Templates are rendered</h5><p>After verification, the library renders all templates in <code>templates/</code> (except <code>_*.tpl</code> helper files and <code>NOTES.txt</code>).</p></div></div>
                        <div class="ps-step"><div class="ps-num">5</div><div class="ps-content"><h5>Pre-install hooks are prepared</h5><p>The library identifies all resources with <code>helm.sh/hook: pre-install</code> annotation and loads them into Kubernetes.</p></div></div>
                        <div class="ps-step"><div class="ps-num">6</div><div class="ps-content"><h5>Hooks are sorted by weight</h5><p>Default weight is 0. Sorted by weight (ascending), then by resource kind, then by name. Lower weights execute FIRST.</p></div></div>
                        <div class="ps-step"><div class="ps-num">7</div><div class="ps-content"><h5>Lowest-weight hook is loaded</h5><p>The hook with the lowest weight (most negative) is applied to Kubernetes first.</p></div></div>
                        <div class="ps-step"><div class="ps-num">8</div><div class="ps-content"><h5>Helm waits until the hook is "Ready"</h5><p>For Jobs/Pods: wait until successful completion (exit 0). For other resources: wait until Kubernetes marks them as loaded. If ANY hook fails, the ENTIRE install fails.</p></div></div>
                        <div class="ps-step"><div class="ps-num">9</div><div class="ps-content"><h5>Non-hook resources are loaded</h5><p>After all pre-install hooks succeed, the actual release resources (Deployments, Services, etc.) are applied to Kubernetes. If <code>--wait</code> is set, Helm waits for all resources to be ready before proceeding.</p></div></div>
                        <div class="ps-step"><div class="ps-num">10</div><div class="ps-content"><h5>Post-install hooks are prepared</h5><p>Resources with <code>helm.sh/hook: post-install</code> are identified.</p></div></div>
                        <div class="ps-step"><div class="ps-num">11</div><div class="ps-content"><h5>Post-install hooks execute</h5><p>Post-install hooks run (sorted by weight). These run AFTER all release resources are deployed and ready (if --wait).</p></div></div>
                        <div class="ps-step"><div class="ps-num">12</div><div class="ps-content"><h5>Release object is returned</h5><p>The library returns the release object (metadata, status, notes) to the Helm client.</p></div></div>
                        <div class="ps-step"><div class="ps-num">13</div><div class="ps-content"><h5>Client exits</h5><p><code>helm install</code> completes. The release is now in <code>deployed</code> state (or <code>failed</code> if any hook or resource failed).</p></div></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam Relevance:</strong> Understanding this 13-step process helps you answer questions like: "When does a pre-install hook run?" (step 7-8, before any resources). "Why did my hook fail?" (step 8 — check hook logs). "Can I have multiple hooks of the same type?" (yes, step 6 — they're sorted by weight).</div></div>
                </div>
'''
    insert_before_qa(ch10_s, ch11_s, content, "Ch10: Hook Lifecycle Steps")

# ============================================================
# CHAPTER 3: Add official glossary-style definitions
# ============================================================
ch3_s = chapter_starts.get(3, -1)
ch4_s = chapter_starts.get(4, -1)
if ch3_s > 0 and ch4_s > ch3_s:
    content = '''
                <div class="section-block">
                    <h4>3.10 Chart Archive & Distribution — Packaging Deep Dive</h4>
                    <p>When you run <code>helm package</code>, Helm creates a <strong>chart archive</strong> — a tarred and gzipped file (<code>.tgz</code>) that contains the entire chart directory. This is what gets uploaded to repositories and OCI registries.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Chart Archive Creation & Distribution Flow</div>
<pre>
CHART DIRECTORY → PACKAGE → ARCHIVE → REPOSITORY → INSTALL
═══════════════════════════════════════════════════════════════

anihpj/                       helm package
├── Chart.yaml                ./anihpj
├── values.yaml          →    anihpj-0.1.0.tgz
├── templates/                 (gzipped tar archive)
│   ├── deployment.yaml
│   └── service.yaml
└── charts/
    └── postgresql-12.x.tgz

The .tgz archive contains:
1. All template files (templates/)
2. Chart.yaml (metadata)
3. values.yaml (defaults)
4. charts/ (bundled dependencies)
5. .helmignore patterns applied
6. OPTIONAL: .prov (provenance signature file)

KEY PROPERTIES:
• Immutable — once published, a version should never change
• SemVer 2 versioned — MAJOR.MINOR.PATCH
• Can be signed with GPG for integrity verification
• OCI registries store charts as OCI artifacts (not .tgz files)
</pre>
                    </div>
                </div>
'''
    insert_before_qa(ch3_s, ch4_s, content, "Ch3: Chart Archive & Distribution")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
