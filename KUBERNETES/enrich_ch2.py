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
# CHAPTER 6: Go Templating - Built-in Objects Deep Dive + Common Patterns
# ============================================================
ch6_s = chapter_starts.get(6, -1)
ch7_s = chapter_starts.get(7, -1)
if ch6_s > 0 and ch7_s > ch6_s:
    content = '''
                <div class="section-block">
                    <h4>6.8 Built-in Objects - Complete Reference</h4>
                    <p>Every Helm template has access to these built-in objects. Understanding them is critical for the certification exam — you'll need to know exactly which object to use for common tasks.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>Object</th><th>Key Properties</th><th>Example Usage</th><th>When to Use</th></tr></thead>
                        <tbody>
                            <tr><td><code>.Release</code></td><td>.Name, .Namespace, .Revision, .IsUpgrade, .IsInstall, .Service</td><td><code>{{ .Release.Name }}</code></td><td>Release-specific metadata; labeling resources</td></tr>
                            <tr><td><code>.Values</code></td><td>Your values.yaml structure</td><td><code>{{ .Values.image.tag }}</code></td><td>Accessing user configuration</td></tr>
                            <tr><td><code>.Chart</code></td><td>.Name, .Version, .AppVersion, .Type, .ApiVersion</td><td><code>{{ .Chart.Version }}</code></td><td>Chart metadata in labels/annotations</td></tr>
                            <tr><td><code>.Files</code></td><td>.Get(name), .GetBytes(name), .Glob(pattern), .AsConfig(), .AsSecrets()</td><td><code>{{ .Files.Get "config.json" }}</code></td><td>Embedding static files in ConfigMaps/Secrets</td></tr>
                            <tr><td><code>.Capabilities</code></td><td>.KubeVersion, .APIVersions.Has()</td><td><code>{{ .Capabilities.KubeVersion.GitVersion }}</code></td><td>K8s version detection; API availability check</td></tr>
                            <tr><td><code>.Template</code></td><td>.Name, .BasePath</td><td><code>{{ .Template.Name }}</code></td><td>Rarely used directly; template identification</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>6.9 Template Syntax - Beyond the Basics</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Action Delimiters</h5>
                            <ul>
                                <li><code>{{ }}</code> — Output something (renders to YAML)</li>
                                <li><code>{{- -}}</code> — Trim whitespace (left/right/both)</li>
                                <li><code>{{/* */}}</code> — Template comments (NOT in output)</li>
                                <li><code>{{&nbsp;}}</code> — Whitespace-sensitive</li>
                            </ul>
                            <div class="info-box tip"><h5>Whitespace Control</h5><p><code>{{- .Values.name }}</code> trims left whitespace. <code>{{ .Values.name -}}</code> trims right. <code>{{- .Values.name -}}</code> trims both. Always use <code>-</code> for clean YAML output!</p></div>
                        </div>
                        <div class="split-side">
                            <h5>Variable Assignment</h5>
                            <ul>
                                <li><code>{{ $var := "value" }}</code> — Define variable</li>
                                <li><code>{{ $var = "new" }}</code> — Reassign (no colon)</li>
                                <li><code>{{ range $i, $v := .List }}</code> — Loop index+value</li>
                                <li><code>{{ with $val := .Nested }}</code> — Scoped variable</li>
                            </ul>
<pre>
# Common variable patterns:
{{ $fullName := include "anihpj.fullname" . }}
{{ $labels := include "anihpj.labels" . | nindent 4 }}

# In a range loop:
{{ range $env, $val := .Values.env }}
  - name: {{ $env }}
    value: {{ $val | quote }}
{{ end }}
</pre>
                        </div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>6.10 The .Files Object - Embedding Static Content</h4>
                    <p>The <code>.Files</code> object gives templates access to non-template files in the chart. This is essential for ConfigMaps containing configuration files, certificates, or scripts.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">.Files Object Methods</div>
<pre>
CHART STRUCTURE
anihpj-chart/
  files/
    nginx.conf         .Files.Get "files/nginx.conf"
    app-config.json    .Files.Get "files/app-config.json"
    certs/
      tls.crt          .Files.Glob "certs/*"
      tls.key
  templates/
    configmap.yaml     Uses {{ .Files.Get }} to embed

.Files.Get "path"        Returns file content as string
.Files.GetBytes "path"   Returns file content as []byte
.Files.Glob "pattern"    Returns list of matching file paths
.Files.AsConfig "path"   Returns file(s) as ConfigMap-ready YAML
.Files.AsSecrets "path"  Returns file(s) as Secret-ready YAML
</pre>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">GOTCHA</div><div class="ckad-gotcha-content"><strong>Exam Gotcha:</strong> Files in <code>.helmignore</code> are NOT accessible via <code>.Files</code>. Also, <code>.Files.Get</code> throws an error if the file doesn't exist — use <code>.Files.Glob</code> to check existence first.</div></div>
                </div>
                <div class="section-block">
                    <h4>6.11 The .Capabilities Object - API Version Detection</h4>
                    <p>One of the most powerful and exam-relevant built-in objects. <code>.Capabilities</code> lets templates detect the Kubernetes cluster version and available APIs at render time.</p>
<pre>
# Check Kubernetes version:
{{ if semverCompare ">=1.25-0" .Capabilities.KubeVersion.GitVersion }}
apiVersion: networking.k8s.io/v1  # Use v1 Ingress (K8s 1.19+)
{{ else }}
apiVersion: networking.k8s.io/v1beta1  # Legacy Ingress
{{ end }}

# Check if an API is available:
{{ if .Capabilities.APIVersions.Has "monitoring.coreos.com/v1" }}
# Deploy ServiceMonitor (Prometheus Operator is installed)
{{ end }}

# Check for specific resource:
{{ if .Capabilities.APIVersions.Has "autoscaling/v2/HorizontalPodAutoscaler" }}
apiVersion: autoscaling/v2
{{ else }}
apiVersion: autoscaling/v2beta2
{{ end }}
</pre>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Exam Tip:</strong> Questions about API version compatibility are common. Always check the cluster's K8s version BEFORE deciding which API version to use. <code>.Capabilities.KubeVersion.GitVersion</code> returns something like <code>v1.29.0</code> — use <code>semverCompare</code> for comparisons.</div></div>
                </div>
'''
    insert_before_qa(ch6_s, ch7_s, content, "Ch6: Built-in Objects & Capabilities")

# ============================================================
# CHAPTER 9: Chart Dependencies - Global Values, Conditionals, Version Constraints
# ============================================================
ch9_s = chapter_starts.get(9, -1)
ch10_s = chapter_starts.get(10, -1)
if ch9_s > 0 and ch10_s > ch9_s:
    content = '''
                <div class="section-block">
                    <h4>9.7 Dependency Conditions & Tags - Selective Subchart Enablement</h4>
                    <p>Not every environment needs every dependency. Use <code>condition</code> and <code>tags</code> in Chart.yaml to selectively enable/disable subcharts.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Using Conditions</h5>
<pre>
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled

# values.yaml
postgresql:
  enabled: true
redis:
  enabled: false  # Skip redis in this env
</pre>
                        </div>
                        <div class="split-side">
                            <h5>Using Tags</h5>
<pre>
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    tags:
      - database
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    tags:
      - cache

# values.yaml
tags:
  database: true   # Enable all DB deps
  cache: false     # Disable all cache deps
</pre>
                        </div>
                    </div>
                    <div class="info-box tip"><h5>Condition vs Tag Logic</h5><p>For a subchart to be enabled: ALL its tags must be <code>true</code> AND its condition (if any) must be <code>true</code>. If both condition and tags are set, the condition is checked first — if the condition path is defined and evaluates to false, the chart is disabled regardless of tags.</p></div>
                </div>
                <div class="section-block">
                    <h4>9.8 Global Values - Sharing Config Across Subcharts</h4>
                    <p>The <code>global</code> key in values.yaml is special — it's automatically available to ALL subcharts without explicit import. This is the standard way to share configuration like image registry, pull secrets, or common labels.</p>
<pre>
# Parent chart values.yaml
global:
  imageRegistry: myregistry.io
  imagePullSecrets:
    - name: regcred
  commonLabels:
    environment: production
    team: backend

postgresql:
  enabled: true
  # This subchart automatically has access to .Values.global.imageRegistry
  # without any import statement!

# In subchart template:
image: {{ .Values.global.imageRegistry }}/postgresql:{{ .Values.image.tag }}
</pre>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">GOTCHA</div><div class="ckad-gotcha-content"><strong>Global Gotcha:</strong> Subcharts can override global values in their own values.yaml, but the parent chart's global values take precedence. Also, <code>global</code> is NOT automatically available to the parent's own templates — you still need to reference it explicitly as <code>.Values.global.xxx</code>.</div></div>
                </div>
                <div class="section-block">
                    <h4>9.9 Importing Child Values - exports vs imports</h4>
                    <p>Sometimes a parent chart needs to use a value exposed by a subchart (like a dynamically-generated password or service name). Use the <code>exports</code> key in the child chart and the <code>import-values</code> key in the parent.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Child-to-Parent Value Flow</div>
<pre>
CHILD CHART (postgresql):            PARENT CHART (anihpj):
+---------------------------+        +-----------------------------+
| values.yaml:              |        | Chart.yaml:                 |
|   auth:                   |        | dependencies:               |
|     password: changeme    |        |   - name: postgresql        |
|                           |        |     import-values:          |
| CHILD exports password    |        |       - child: auth.password|
| to parent via import      |───────>|         parent: db.password |
+---------------------------+        |                             |
                                     | templates/deployment.yaml:  |
                                     |   env:                      |
                                     |     - name: DB_PASSWORD     |
                                     |       value: {{ .Values.db. |
                                     |         password }}         |
                                     +-----------------------------+
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Exam Scenario:</strong> "You have a WordPress chart that depends on MariaDB. How do you pass the MariaDB-generated password to the WordPress deployment?" Answer: Use <code>import-values</code> in Chart.yaml to map the child's exported value to a parent value, then reference it in the WordPress template.</div></div>
                </div>
                <div class="section-block">
                    <h4>9.10 Dependency Version Constraints - SemVer in Practice</h4>
                    <p>Helm uses <strong>SemVer 2</strong> for dependency version constraints. Understanding version ranges is critical for reproducible deployments.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>Constraint</th><th>Meaning</th><th>Matches</th></tr></thead>
                        <tbody>
                            <tr><td><code>12.0.0</code></td><td>Exact version</td><td>Only 12.0.0</td></tr>
                            <tr><td><code>>=12.0.0 <13.0.0</code></td><td>Version range</td><td>12.0.0 through 12.x.x</td></tr>
                            <tr><td><code>~12.0.0</code></td><td>Patch-level flex (~>)</td><td>>=12.0.0, <12.1.0</td></tr>
                            <tr><td><code>^12.0.0</code></td><td>Minor-level flex (^)</td><td>>=12.0.0, <13.0.0</td></tr>
                            <tr><td><code>12.x.x</code></td><td>Wildcard (x = any)</td><td>Any 12.x.x</td></tr>
                            <tr><td><code>>=12.0.0 || 18.x.x</code></td><td>OR condition</td><td>12+ OR any 18.x</td></tr>
                            <tr><td><code>*</code></td><td>Any version</td><td>All versions (use sparingly!)</td></tr>
                        </tbody>
                    </table></div>
                    <div class="info-box warning"><h5>Version Constraint Warning</h5><p>Always use <strong>explicit version ranges</strong> or pin to specific versions. Using <code>*</code> or overly broad ranges can pull in breaking changes. <code>helm dependency update</code> respects Chart.lock — if Chart.lock exists, it downloads exactly those versions for reproducibility.</p></div>
                </div>
'''
    insert_before_qa(ch9_s, ch10_s, content, "Ch9: Dependencies Deep Dive")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
