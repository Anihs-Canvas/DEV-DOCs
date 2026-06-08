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
# CHAPTER 10: Hooks - CRD hooks, cleanup patterns
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                <div class="section-block">
                    <h4>10.15 CRDs and Hooks — Special Handling</h4>
                    <p>Custom Resource Definitions (CRDs) have special handling in Helm. They're not hooks — they use the <code>crds/</code> directory instead.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>crds/ Directory (Helm 3+)</h5>
                            <ul>
                                <li>Files in <code>crds/</code> are applied BEFORE any templates</li>
                                <li>CRDs are NOT managed as part of the release</li>
                                <li>They are NEVER updated or deleted by Helm</li>
                                <li>No template rendering — they're raw YAML</li>
                                <li>The old <code>crd-install</code> hook was removed in Helm 3</li>
                            </ul>
<pre>
anihpj-chart/
├── crds/
│   └── jobposts.example.com.yaml
├── templates/
│   └── jobpost-cr.yaml  # Uses the CRD
</pre>
                        </div>
                        <div class="split-side">
                            <h5>CRD Best Practices</h5>
                            <ul>
                                <li>Place EXACTLY ONE CRD per file</li>
                                <li>CRDs should be minimal — only what's needed</li>
                                <li>Use a SEPARATE chart for CRDs in production</li>
                                <li>CRDs survive <code>helm uninstall</code></li>
                                <li>Manual deletion required: <code>kubectl delete crd NAME</code></li>
                            </ul>
<pre>
# crds/jobposts.example.com.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: jobposts.anihpj.example.com
spec:
  group: anihpj.example.com
  names:
    kind: JobPost
    plural: jobposts
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
</pre>
                        </div>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>CRD Gotcha:</strong> If you upgrade a chart and the CRD template changes, the existing CRD is NOT updated. You must manually apply CRD changes. This prevents accidental breaking changes to custom resources. For production, manage CRDs in a separate Helm chart with its own lifecycle.</div></div>
                </div>
'''
    insert_before_qa(ch10_s, ch11_s, content, "Ch10: CRDs & Hooks")

# ============================================================
# CHAPTER 8: Add the Dockerfile for anihpj (user's original request)
# ============================================================
ch8_s = chapter_starts.get(8, -1)
ch9_s = chapter_starts.get(9, -1)
if ch8_s > 0 and ch9_s > ch8_s:
    content = '''
                <div class="section-block">
                    <h4>8.11 Building the anihpj Container — Complete Dockerfile</h4>
                    <p>The anihpj/jobpost Django application needs a container image before Helm can deploy it. Here's the production-ready multi-stage Dockerfile.</p>
                    <div class="terminal-block">
                        <div class="terminal-title">Dockerfile — Multi-stage Build for anihpj</div>
<pre>
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.12-slim
WORKDIR /app

# Create non-root user
RUN groupadd -r anihpj && useradd -r -g anihpj anihpj

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/anihpj/.local

# Copy application code
COPY --chown=anihpj:anihpj . .

# Set environment
ENV PATH=/home/anihpj/.local/bin:$PATH \\
    PYTHONUNBUFFERED=1 \\
    DJANGO_SETTINGS_MODULE=anihpj.settings

# Collect static files and run as non-root
RUN python manage.py collectstatic --noinput

USER anihpj
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \\
  CMD python manage.py check --deploy || exit 1

CMD ["gunicorn", "anihpj.wsgi:application", \\
     "--bind", "0.0.0.0:8000", \\
     "--workers", "4", \\
     "--access-logfile", "-"]
</pre>
                    </div>
                    <div class="info-box tip"><h5>Docker Build & Push for Helm</h5><pre>
# Build the image:
docker build -t anihpj:v2.0.0 .

# Tag for registry:
docker tag anihpj:v2.0.0 myregistry.io/anihpj:v2.0.0

# Push to registry:
docker push myregistry.io/anihpj:v2.0.0

# Now reference in values.yaml:
image:
  repository: myregistry.io/anihpj
  tag: v2.0.0

# Deploy with Helm:
helm upgrade --install anihpj ./anihpj-chart \\
  --set image.tag=v2.0.0 -n production --atomic --wait
</pre></div>
                </div>
'''
    insert_before_qa(ch8_s, ch9_s, content, "Ch8: Dockerfile for anihpj")

# ============================================================
# CHAPTER 17: Add time-management and prioritization Q&As
# ============================================================
ch17_s = chapter_starts.get(17, -1)
ch18_s = chapter_starts.get(18, -1)
if ch17_s > 0 and ch18_s > ch17_s:
    content = '''
                <div class="section-block">
                    <h4>17.9 Rapid-Fire Knowledge Check — 60-Second Questions</h4>
                    <p>These test your instant recall. You should answer each in under 60 seconds. If you can't, review the referenced chapter.</p>
                </div>
                <div class="cka-exam-questions">
                    <div class="exam-question-item"><span class="eq-number">R1</span><div class="eq-question">What flag makes helm install wait for all pods to be ready?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>--wait</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>--wait</code> blocks until all Pods, PVCs, Services, and minimum replicas of Deployments/StatefulSets are in a ready state. Combine with <code>--timeout</code> to set a maximum wait time.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R2</span><div class="eq-question">What's the difference between template and include?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>template</code> writes directly to output (no piping). <code>include</code> returns a string (can pipe through functions like <code>nindent</code>, <code>quote</code>).</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Always use <code>include</code> for named templates in resource definitions. Only use <code>template</code> for standalone output where you don't need to transform the result.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R3</span><div class="eq-question">Where does Helm 3 store release history?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Kubernetes Secrets named <code>sh.helm.release.v1.&lt;name&gt;.v&lt;rev&gt;</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Default storage backend. Each revision gets a separate Secret in the release namespace. Label for filtering: <code>owner=helm</code>. Max 1MB per Secret — use SQL backend for larger manifests.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R4</span><div class="eq-question">What flag auto-rolls back on upgrade failure?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>--atomic</code> (Helm 3) / <code>--rollback-on-failure</code> (Helm 4)</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>If the upgrade fails, <code>--atomic</code> automatically rolls back to the last successful revision. Combine with <code>--cleanup-on-fail</code> to remove failed resources.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R5</span><div class="eq-question">What annotation makes a resource a Helm hook?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>"helm.sh/hook": &lt;type&gt;</code> where type is pre-install, post-install, pre-upgrade, etc.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Hook types: pre/post-install, pre/post-upgrade, pre/post-delete, pre/post-rollback, test. Combined with weight and delete-policy annotations to control execution.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R6</span><div class="eq-question">How do you list releases across all namespaces?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>helm list -A</code> or <code>helm list --all-namespaces</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>helm list -A --failed</code> shows only failed releases. <code>helm list -n NS</code> scopes to a specific namespace.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R7</span><div class="eq-question">What's the Helm command to see rendered templates without installing?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>helm template NAME ./chart</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Renders templates locally without connecting to Kubernetes. Use <code>--debug</code> for detailed output. Different from <code>--dry-run</code> which DOES connect to the K8s API for validation.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R8</span><div class="eq-question">How do you add a chart repository?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>helm repo add NAME URL</code> then <code>helm repo update</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Repositories are stored in <code>repositories.yaml</code>. Always run <code>helm repo update</code> after adding to fetch the index. Use <code>helm repo list</code> to see configured repos.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R9</span><div class="eq-question">What function prevents nil pointer errors in templates?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>default</code> — e.g., <code>{{ .Values.opt | default "fallback" }}</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>default</code> returns the fallback if the value is nil, empty string, false, zero, or empty collection. <code>required</code> does the opposite — it throws an error if the value is empty.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">R10</span><div class="eq-question">What flag installs a chart if it doesn't exist, and upgrades if it does?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>--install</code> on <code>helm upgrade</code>: <code>helm upgrade --install NAME ./chart</code></p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the idempotent deploy pattern. Safe for CI/CD — works whether it's the first deploy or the hundredth. Combine with <code>--atomic --wait --create-namespace</code> for production.</p></div></details></div>
                </div>
'''
    insert_before_qa(ch17_s, ch18_s, content, "Ch17: Rapid-Fire Q&As")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
