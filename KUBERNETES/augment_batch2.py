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
# CHAPTER 5: Release Management - Add rollback strategy, history management, status codes
# ============================================================
ch5_s = chapter_starts.get(5, -1)
ch6_s = chapter_starts.get(6, -1)
if ch5_s > 0 and ch6_s > ch5_s:
    content = '''
                <div class="section-block">
                    <h4>5.10 Release History & Rollback Strategy</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Release Revision Timeline</div>
<pre>
RELEASE: anihpj-prod (namespace: production)
═══════════════════════════════════════════════════════════
REV  STATUS       DEPLOYED    CHART    APP VER   DESCRIPTION
───────────────────────────────────────────────────────────
1    SUPERSEDED   10:00 AM    0.1.0    v1.0.0    Initial install
2    SUPERSEDED   10:30 AM    0.1.1    v1.0.1    Bug fix
3    SUPERSEDED   11:00 AM    0.2.0    v2.0.0    Major upgrade
4    FAILED       11:15 AM    0.2.1    v2.0.1    BROKEN - rolled back
5    DEPLOYED     11:16 AM    0.2.0    v2.0.0    Rollback to rev 3 ← CURRENT

MAX HISTORY: 10 (default) — oldest revisions auto-deleted!
Set with: helm install --history-max 20

ROLLBACK COMMANDS:
helm rollback anihpj-prod 3 -n production     # Go to revision 3
helm rollback anihpj-prod 0 -n production     # Rollback to PREVIOUS
helm rollback anihpj-prod --wait -n production # Rollback + wait for ready

KEY INSIGHT: helm rollback CREATES a new revision (6) with
the config from revision 3. Revision 3 is not re-activated.
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>5.11 --reuse-values vs --reset-values - Critical Difference</h4>
                    <div class="split-panel">
                        <div class="split-side split-bad">
                            <h5>❌ --reuse-values (DANGER)</h5>
                            <p>Reuses ALL previously set values (including --set values from last install). Can cause unexpected config if you forget what was set before.</p>
<pre>
# First install:
helm install app ./chart --set image.tag=v1.0
# Later upgrade (INTENT: change replicas only):
helm upgrade app ./chart --reuse-values --set replicaCount=5
# RESULT: image.tag STILL v1.0 (reused!) + replicaCount=5
</pre>
                        </div>
                        <div class="split-side split-good">
                            <h5>✅ --reset-values (SAFE)</h5>
                            <p>Discards ALL previous --set values. Uses ONLY what is in the chart's values.yaml + new -f files + new --set values.</p>
<pre>
# First install:
helm install app ./chart --set image.tag=v1.0
# Later upgrade (INTENT: start fresh):
helm upgrade app ./chart --reset-values -f values-v2.yaml
# RESULT: ALL previous --set values discarded.
# Only values-v2.yaml + chart defaults used.
</pre>
                        </div>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Exam Gotcha:</strong> If the question says "upgrade the release but keep all previously configured values," use <code>--reuse-values</code>. If it says "start fresh with new values," use <code>--reset-values</code>. These flags are mutually exclusive — you can't use both.</div></div>
                </div>
                <div class="section-block">
                    <h4>5.12 Release Status Codes - What Each Means</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Status</th><th>Meaning</th><th>Can helm install?</th><th>Recovery Action</th></tr></thead>
                        <tbody>
                            <tr><td><code>deployed</code></td><td>Release is running normally</td><td>❌ Name in use</td><td>Use <code>helm upgrade</code></td></tr>
                            <tr><td><code>failed</code></td><td>Install/upgrade failed</td><td>❌ Name in use</td><td><code>helm rollback</code> or <code>helm uninstall</code></td></tr>
                            <tr><td><code>superseded</code></td><td>Old revision replaced by newer</td><td>N/A (historical)</td><td>Rollback target</td></tr>
                            <tr><td><code>pending-install</code></td><td>Install in progress</td><td>❌ Locked</td><td>Wait or delete pending secret</td></tr>
                            <tr><td><code>pending-upgrade</code></td><td>Upgrade in progress</td><td>❌ Locked</td><td>Wait or delete pending secret</td></tr>
                            <tr><td><code>pending-rollback</code></td><td>Rollback in progress</td><td>❌ Locked</td><td>Wait or delete pending secret</td></tr>
                            <tr><td><code>uninstalled</code></td><td>Release removed</td><td>✅ Can re-install</td><td>Use <code>helm install</code> (name is free)</td></tr>
                            <tr><td><code>unknown</code></td><td>Helm can't determine state</td><td>Check history</td><td>Investigate release secrets</td></tr>
                        </tbody>
                    </table></div>
                </div>
'''
    insert_before_qa(ch5_s, ch6_s, content, "Ch5: Rollback & Status Codes")

# ============================================================
# CHAPTER 7: Template Functions - Add Sprig function reference, pipeline patterns
# ============================================================
ch7_s = chapter_starts.get(7, -1)
ch8_s = chapter_starts.get(8, -1)
if ch7_s > 0 and ch8_s > ch7_s:
    content = '''
                <div class="section-block">
                    <h4>7.13 Most-Used Sprig Functions - Quick Reference</h4>
                    <div class="card-grid three-col">
                        <div class="info-card"><div class="card-icon">📝</div><h5>String Functions</h5><pre>
{{ "hello" | upper }}        HELLO
{{ "HELLO" | lower }}        hello
{{ "hello" | title }}        Hello
{{ "hello" | quote }}        "hello"
{{ "a-b-c" | replace "-" "." }}  a.b.c
{{ "  hi  " | trim }}        hi
{{ .Name | nospace }}        removes spaces
{{ .Name | indent 4 }}       +4 spaces
{{ .Name | nindent 4 }}      +4 spaces + newline
</pre></div>
                        <div class="info-card"><div class="card-icon">🔢</div><h5>Type & Conversion</h5><pre>
{{ .Values | toYaml }}       YAML string
{{ .Values | toJson }}       JSON string
{{ $yaml | fromYaml }}       parsed object
{{ $json | fromJson }}       parsed object
{{ 5 | toString }}           "5"
{{ "5" | atoi }}             5 (int)
{{ .Values.enabled | toBool }}  boolean
{{ .Values.list | toJson | indent 4 }}
</pre></div>
                        <div class="info-card"><div class="card-icon">🔀</div><h5>Flow Control Helpers</h5><pre>
{{ default "fallback" .Val }}   null->fallback
{{ required "err" .Val }}       null->error
{{ empty .Val }}                 true if nil/""/0
{{ coalesce .A .B .C }}         first non-null
{{ ternary "yes" "no" .Bool }}  if/else inline
{{ .List | first }}             first element
{{ .List | last }}              last element
{{ .List | join "," }}          CSV string
{{ .List | has "item" }}       contains check
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>7.14 Pipeline Patterns - Chaining for Clean Templates</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Common Pipeline Chains</div>
<pre>
VALUE EXTRACTION + FORMATTING PATTERNS:
═══════════════════════════════════════════════════════════

{{ .Values.image.tag | default "latest" | quote }}
    │                    │                   │
    └─ get value         └─ fallback         └─ wrap in quotes
    Result: "v2.0" or "latest"

{{ include "anihpj.labels" . | nindent 4 }}
    │                            │
    └─ render named template     └─ indent 4 + newline
    Result: (indented label block)

{{ .Values.config | toYaml | indent 8 }}
    │                   │           │
    └─ get object       └─ to YAML  └─ indent 8 spaces
    Result: (indented YAML for ConfigMap data)

{{ range .Values.env }}
  - name: {{ .name | upper | quote }}
    value: {{ .value | quote }}
{{ end }}
    │            │        │
    └─ iterate   └─ upper └─ quote
    Result: (list of uppercased, quoted env vars)
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>7.15 Date & Certificate Functions</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Date Functions</h5>
<pre>
{{ now }}                   2024-01-15 10:30:00
{{ now | date "2006-01-02" }}  2024-01-15
{{ now | date "15:04:05" }}    10:30:00
{{ now | htmlDate }}        2024-01-15
{{ now | dateModify "-24h" }}  yesterday
</pre>
                        </div>
                        <div class="split-side">
                            <h5>Crypto Functions</h5>
<pre>
{{ "secret" | sha256sum }}  hex hash
{{ "data" | b64enc }}       base64 encoded
{{ .Files.Get "cert.pem" | sha256sum }}
</pre>
                            <h5>Encoding Functions</h5>
<pre>
{{ .Value | b64enc }}       base64 encode
{{ .Secret | b64dec }}      base64 decode
{{ .Data | b32enc }}        base32 encode
</pre>
                        </div>
                    </div>
                </div>
'''
    insert_before_qa(ch7_s, ch8_s, content, "Ch7: Sprig Functions & Pipelines")

# ============================================================
# CHAPTER 8: Building anihpj Templates - Add complete template walkthrough
# ============================================================
ch8_s = chapter_starts.get(8, -1)
ch9_s = chapter_starts.get(9, -1)
if ch8_s > 0 and ch9_s > ch8_s:
    content = '''
                <div class="section-block">
                    <h4>8.9 _helpers.tpl - Complete Naming Convention</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Standard _helpers.tpl Pattern</div>
<pre>
{{/*
Expand the name of the chart.
*/}}
{{- define "anihpj.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited.
*/}}
{{- define "anihpj.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "anihpj.labels" -}}
helm.sh/chart: {{ include "anihpj.chart" . }}
{{ include "anihpj.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "anihpj.selectorLabels" -}}
app.kubernetes.io/name: {{ include "anihpj.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Naming Convention for Exam:</strong> Always use <code>include "FULLNAME" .</code> (not <code>template</code>) in your resource templates. <code>include</code> returns a string you can pipeline through other functions. <code>template</code> writes directly to output and cannot be piped. This is tested frequently.</div></div>
                </div>
                <div class="section-block">
                    <h4>8.10 Complete Deployment Template for anihpj</h4>
                    <div class="terminal-block">
                        <div class="terminal-title">templates/deployment.yaml - Full Production-Ready Template</div>
<pre>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "anihpj.fullname" . }}
  labels:
    {{- include "anihpj.labels" . | nindent 4 }}
  annotations:
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    # Forces pod restart when ConfigMap changes
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "anihpj.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "anihpj.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.port }}
        {{- if .Values.probes.liveness }}
        livenessProbe:
          httpGet:
            path: {{ .Values.probes.path }}
            port: http
          initialDelaySeconds: {{ .Values.probes.initialDelay }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        env:
        {{- range .Values.env }}
        - name: {{ .name }}
          value: {{ .value | quote }}
        {{- end }}
</pre>
                    </div>
                </div>
'''
    insert_before_qa(ch8_s, ch9_s, content, "Ch8: Templates Deep Dive")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
