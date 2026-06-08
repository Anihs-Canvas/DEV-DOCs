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
# CHAPTER 10: Hooks - Add real-world patterns, rollback hooks, test hooks
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                <div class="section-block">
                    <h4>10.13 Hook Patterns for Rollback Operations</h4>
                    <p>Rollback hooks are often overlooked but critical for data integrity. They run during <code>helm rollback</code> and can save you from data corruption.</p>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">⏪</div><h5>Pre-Rollback: Backup Current State</h5><pre>
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-pre-rollback-backup
  annotations:
    "helm.sh/hook": pre-rollback
    "helm.sh/hook-weight": "-10"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: backup
        image: postgres:15
        command: ["pg_dump", "-h", "{{ .Release.Name }}-postgresql",
                  "-U", "anihpj", "-f", "/backup/pre-rollback-{{ .Release.Revision }}.sql"]
</pre></div>
                        <div class="info-card"><div class="card-icon">🔄</div><h5>Post-Rollback: Verify & Restore</h5><pre>
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-post-rollback-verify
  annotations:
    "helm.sh/hook": post-rollback
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: verify
        image: anihpj:{{ .Values.image.tag }}
        command: ["python", "manage.py", "check", "--deploy"]
</pre></div>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Rollback Hook Gotcha:</strong> During rollback, Helm creates a NEW revision with the old configuration. Pre-rollback hooks run BEFORE the old resources are restored. Post-rollback hooks run AFTER restoration. The <code>.Release.Revision</code> in the hook template is the NEW revision number, not the target.</div></div>
                </div>
                <div class="section-block">
                    <h4>10.14 Hook Execution - Concurrency & Parallelism</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Hook Execution Model</div>
<pre>
HOOK EXECUTION ORDER (DEFAULT: SERIAL)
═══════════════════════════════════════════════════════════════

pre-install hooks:
  [Weight: -10] → Job A runs → completes → Job B starts
  [Weight: -5]  → Job B runs → completes → Job C starts
  [Weight: 0]   → Job C runs → completes
  (ALL hook resources of one weight complete before next weight)

SAME WEIGHT BEHAVIOR:
  [Weight: 0] Job A ──┐
  [Weight: 0] Job B ──┤ Started together (since Helm 3.2+)
  [Weight: 0] Job C ──┘
  (Same-weight hooks can run concurrently)

HOOK TIMEOUT:
  Default: 5 minutes for ALL hooks combined
  Override: --timeout 10m
  Per-hook timeout: NOT supported (use Job's activeDeadlineSeconds)

HOOK FAILURE:
  One hook fails → ENTIRE operation fails
  --atomic: auto-rollback on ANY hook failure
  Failed hooks are preserved for debugging (unless hook-failed policy)
</pre>
                    </div>
                </div>
'''
    insert_before_qa(ch10_s, ch11_s, content, "Ch10: Rollback Hooks & Concurrency")

# ============================================================
# CHAPTER 12: Repositories - Add repo security, mirroring, troubleshooting
# ============================================================
ch12_s = chapter_starts.get(12, -1)
ch13_s = chapter_starts.get(13, -1)
if ch12_s > 0 and ch13_s > ch12_s:
    content = '''
                <div class="section-block">
                    <h4>12.14 Repository Security & Authentication Patterns</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🔐</div><h5>Authenticated Repositories</h5><pre>
# HTTP Basic Auth:
helm repo add private https://charts.company.com \\
  --username myuser --password mypass

# Token-based (Bearer):
helm repo add private https://charts.company.com \\
  --username token --password "$GITLAB_TOKEN"

# TLS Client Certificates:
helm repo add secure https://charts.secure.com \\
  --cert-file client.crt \\
  --key-file client.key \\
  --ca-file ca.crt
</pre></div>
                        <div class="info-card"><div class="card-icon">🪞</div><h5>Repository Mirroring</h5><pre>
# Mirror a public repo to private:
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Pull ALL charts for mirroring:
for chart in $(helm search repo bitnami -l -o json | jq -r '.[].name'); do
  helm pull $chart --destination ./mirror/
done

# Create local index:
helm repo index ./mirror/
# Host via nginx/S3/internal registry
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>12.15 Repository Troubleshooting Guide</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Symptom</th><th>Diagnosis</th><th>Fix</th></tr></thead>
                        <tbody>
                            <tr><td><code>Error: no repositories found</code></td><td>No repos configured</td><td><code>helm repo add bitnami https://charts.bitnami.com/bitnami</code></td></tr>
                            <tr><td><code>Error: looks like "URL" is not a valid chart repository</code></td><td>index.yaml missing or malformed</td><td>Verify URL; curl -s URL/index.yaml | head</td></tr>
                            <tr><td><code>Error: failed to fetch</code></td><td>Network issue or repo down</td><td><code>helm repo update --debug</code>; check proxy settings</td></tr>
                            <tr><td><code>Error: no cached repository for ...</code></td><td>Repo added but not updated</td><td><code>helm repo update</code></td></tr>
                            <tr><td><code>Error: chart not found</code></td><td>Chart name or version doesn't exist</td><td><code>helm search repo REPO/CHART --versions</code></td></tr>
                            <tr><td>Certificate errors</td><td>TLS verification failed</td><td>Add <code>--ca-file</code> or <code>--insecure-skip-tls-verify</code> (not recommended)</td></tr>
                        </tbody>
                    </table></div>
                </div>
'''
    insert_before_qa(ch12_s, ch13_s, content, "Ch12: Repo Security & Troubleshooting")

# ============================================================
# CHAPTER 13: Security - Add network policies, admission control, CVE scanning
# ============================================================
ch13_s = chapter_starts.get(13, -1)
ch14_s = chapter_starts.get(14, -1)
if ch13_s > 0 and ch14_s > ch13_s:
    content = '''
                <div class="section-block">
                    <h4>13.12 Network Policies for Helm-Deployed Applications</h4>
                    <p>Helm can deploy NetworkPolicies alongside your application to enforce zero-trust networking. This is a critical production security practice often tested on the exam.</p>
<pre>
# templates/networkpolicy.yaml
{{ if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "anihpj.fullname" . }}
spec:
  podSelector:
    matchLabels:
      {{- include "anihpj.selectorLabels" . | nindent 6 }}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend  # Only allow frontend pods
    ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgresql  # Only allow DB egress
    ports:
    - protocol: TCP
      port: 5432
  - to:  # Allow DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
{{ end }}
</pre>
                </div>
                <div class="section-block">
                    <h4>13.13 Admission Control Integration</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm + Admission Controllers Security Pipeline</div>
<pre>
helm install          kubectl apply        ADMISSION WEBHOOK       K8s API
    |                      |                      |                    |
    v                      v                      v                    v
Rendered YAML ──────> API Request ──────> Validate/Mutate ──────> Apply Resource
                                            |
                              ┌─────────────┼─────────────┐
                              │             │             │
                         OPA/Gatekeeper  Kyverno      Pod Security
                         (Rego policies) (CNCF)       Standards
                              │             │             │
                              └─────────────┼─────────────┘
                                            |
                                BLOCK: privilege escalation
                                BLOCK: hostPath volumes
                                BLOCK: runAsRoot containers
                                MUTATE: add resource limits
                                MUTATE: inject sidecars
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam Insight:</strong> Questions about "preventing insecure deployments" should mention admission controllers. Helm alone cannot enforce policy — it generates YAML. Use OPA/Gatekeeper or Kyverno to validate Helm-rendered manifests before they reach the API server.</div></div>
                </div>
'''
    insert_before_qa(ch13_s, ch14_s, content, "Ch13: Network Policies & Admission Control")

# ============================================================
# CHAPTER 19: Advanced Patterns - Add schema evolution, multi-arch, deprecation
# ============================================================
ch19_s = chapter_starts.get(19, -1)
ch20_s = chapter_starts.get(20, -1)
if ch19_s > 0 and ch20_s > ch19_s:
    content = '''
                <div class="section-block">
                    <h4>19.10 Chart Schema Evolution & Deprecation Strategy</h4>
                    <p>As charts evolve, you need strategies for handling breaking changes in values.yaml without breaking existing deployments.</p>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Add, Don't Remove</h5><p>New values should be ADDED with sensible defaults. Old values should be KEPT but marked as deprecated. Never remove a value key that existing deployments might reference.</p><pre>
# values.yaml v2.0 — BACKWARDS COMPATIBLE:
replicaCount: 3
image:  # OLD way (deprecated, still works)
  repository: anihpj
  tag: v2.0
imageRef: anihpj:v2.0  # NEW way (preferred)
# Template handles both:
image: "{{ .Values.imageRef | default (printf "%s:%s" .Values.image.repository .Values.image.tag) }}"
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Deprecation Warnings</h5><p>Use NOTES.txt to warn users about deprecated values. Use <code>required</code> for values being removed in the next major version.</p><pre>
{{ if .Values.image.repository }}
NOTE: 'image.repository' is deprecated. Use 'imageRef' instead.
{{ end }}
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Major Version Bumps</h5><p>Bump the chart MAJOR version when removing deprecated values. Users can pin to the old major version until they migrate.</p></div></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>19.11 Multi-Architecture Chart Patterns</h4>
                    <p>Support ARM64, AMD64, and other architectures in a single chart using <code>.Capabilities</code> and template conditionals.</p>
<pre>
# values.yaml
image:
  repository: anihpj
  tag: v2.0
  
# Auto-detect architecture in templates:
{{ $arch := .Values.arch | default "amd64" }}

# Or detect from node:
nodeSelector:
  kubernetes.io/arch: {{ $arch }}

# Multi-arch image tag pattern:
image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}-{{ $arch }}"
# Produces: anihpj:v2.0-amd64 or anihpj:v2.0-arm64

# For multi-arch manifest images (preferred):
image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
# Single tag, registry serves correct arch automatically
</pre>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Production Tip:</strong> Use multi-arch manifest images (OCI image indexes) whenever possible. A single image tag that works on both ARM and AMD removes the need for architecture-specific templates. Only use arch-specific templates when targeting specialized hardware (GPU, edge devices).</div></div>
                </div>
'''
    insert_before_qa(ch19_s, ch20_s, content, "Ch19: Schema Evolution & Multi-Arch")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
