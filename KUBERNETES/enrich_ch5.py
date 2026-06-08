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
# CHAPTER 14: CI/CD - GitOps with Argo CD + GitHub Actions
# ============================================================
ch14_s = chapter_starts.get(14, -1)
ch15_s = chapter_starts.get(15, -1)
if ch14_s > 0 and ch15_s > ch14_s:
    content = '''
                <div class="section-block">
                    <h4>14.7 GitOps with Helm + Argo CD</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">GitOps Workflow - Argo CD + Helm</div>
<pre>
GIT REPOSITORY                      ARGO CD                      KUBERNETES
+------------------+           +------------------+          +------------------+
| helm-charts/     |           | Argo CD          |          | Production       |
|   anihpj/        |  git pull |                  |  sync    | Cluster          |
|     Chart.yaml   |---------->| Application CRD  |--------->| + namespace: prod|
|     values.yaml  |  (every   |   source:        |  (every  |   anihpj-prod    |
|     values-prod  |   3 min)  |     repoURL: git |   3 min) |   release v3     |
|     templates/   |           |     path: anihpj  |          |                  |
+------------------+           |     targetRev:    |          +------------------+
                               |       main        |
                               +------------------+

ARGOCD APPLICATION YAML:
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: anihpj-prod
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/helm-charts
    targetRevision: main
    path: anihpj
    helm:
      values: |
        replicaCount: 3
        image:
          tag: v2.0.0
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
</pre>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>GitOps Exam Question:</strong> "How do you ensure a Helm release stays in sync with its Git repository?" Answer: Use Argo CD or Flux CD with automated sync. The Application CRD watches the Git repo and automatically reconciles the cluster state with the desired state. <code>selfHeal: true</code> detects and fixes manual changes (drift).</div></div>
                </div>
                <div class="section-block">
                    <h4>14.8 GitHub Actions Pipeline - Complete Example</h4>
<pre>
# .github/workflows/helm-release.yml
name: Helm Chart CI/CD

on:
  push:
    branches: [main]
    paths: ['anihpj-chart/**']

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Helm
        uses: azure/setup-helm@v4
      - name: Setup Kind
        uses: helm/kind-action@v1
      - name: Lint
        run: helm lint ./anihpj-chart --strict
      - name: Template Render
        run: helm template test ./anihpj-chart --debug
      - name: Install + Test
        run: |
          helm install ci-test ./anihpj-chart -n ci --create-namespace --wait
          helm test ci-test -n ci --logs
          helm uninstall ci-test -n ci

  publish:
    needs: lint-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Package & Push
        run: |
          helm package ./anihpj-chart
          helm registry login ghcr.io -u \${{ github.actor }} -p \${{ secrets.GH_TOKEN }}
          helm push anihpj-*.tgz oci://ghcr.io/\${{ github.repository_owner }}/charts
</pre>
                </div>
                <div class="section-block">
                    <h4>14.9 Blue-Green & Canary Deployments with Helm</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Blue-Green Strategy</h5>
<pre>
# Deploy GREEN (new version):
helm install anihpj-green ./chart \\
  --set image.tag=v2.0 \\
  --set service.name=anihpj-green \\
  -n production

# Test GREEN:
curl http://anihpj-green.production.svc

# Switch traffic to GREEN:
kubectl patch svc anihpj-prod -n production \\
  -p '{"spec":{"selector":{"version":"green"}}}'

# Decommission BLUE:
helm uninstall anihpj-blue -n production
</pre>
                        </div>
                        <div class="split-side">
                            <h5>Canary Strategy</h5>
<pre>
# Deploy CANARY (10% traffic):
helm install anihpj-canary ./chart \\
  --set image.tag=v2.0 \\
  --set replicaCount=1 \\
  -n production

# Traffic split via Ingress/Service Mesh:
# 90% -> anihpj-stable (v1.0)
# 10% -> anihpj-canary (v2.0)

# Monitor canary for 30 min:
helm test anihpj-canary -n production

# Promote canary to stable:
helm upgrade anihpj-stable ./chart \\
  --set image.tag=v2.0 -n production
helm uninstall anihpj-canary -n production
</pre>
                        </div>
                    </div>
                </div>
'''
    insert_before_qa(ch14_s, ch15_s, content, "Ch14: GitOps & Deployment Strategies")

# ============================================================
# CHAPTER 17: Practice Questions - Add more domain-specific Q&A
# ============================================================
ch17_s = chapter_starts.get(17, -1)
ch18_s = chapter_starts.get(18, -1)
if ch17_s > 0 and ch18_s > ch17_s:
    # Ch17 already has some Q&A. Add a "Scenario-Based Questions" section
    content = '''
                <div class="section-block">
                    <h4>17.6 Scenario-Based Challenge Questions</h4>
                    <p>These multi-step scenarios test your ability to combine multiple Helm concepts — just like the real exam.</p>
                </div>
                <div class="cka-exam-questions">
                    <div class="exam-question-item"><span class="eq-number">S1</span><div class="eq-question"><strong>Scenario:</strong> You need to deploy WordPress with MariaDB in production. WordPress must connect to MariaDB, and both must be in the same namespace. MariaDB's root password should NEVER be in values.yaml. How do you set this up?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>1. Add MariaDB as a dependency in Chart.yaml with a condition. 2. Use <code>--set</code> or a sealed secret for the MariaDB password. 3. Import MariaDB's credentials into WordPress values via <code>import-values</code>. 4. Use <code>helm install wordpress ./chart --set mariadb.auth.rootPassword=$(generate-password)</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This tests three concepts simultaneously: subchart dependencies, secrets management, and value importing. The key insight is that you should never hardcode passwords — always inject them at deploy time or use an external secrets manager.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">S2</span><div class="eq-question"><strong>Scenario:</strong> A release <code>anihpj-prod</code> revision 17 is broken. Revision 15 was known good. However, someone manually deleted 3 releases' Secrets. <code>helm rollback</code> fails. What do you do?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>1. Check which revisions still exist: <code>helm history anihpj-prod</code>. 2. If revision 15's Secret is deleted, you cannot rollback to it. 3. Instead, retrieve a known-good values file and redeploy: <code>helm upgrade anihpj-prod ./chart -f values-good.yaml --reset-values</code>. 4. Implement a backup strategy for release Secrets going forward.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Helm stores each revision as a Secret. If the Secret is deleted, that revision is permanently lost. This is why production environments should back up Helm release Secrets or use an external SQL storage backend. <code>--reset-values</code> is critical here — it discards all previous --set values and uses only what's in the values file.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">S3</span><div class="eq-question"><strong>Scenario:</strong> Your chart's Deployment template renders differently on K8s 1.24 vs 1.28 because the API version changed. How do you make the chart compatible with both?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use <code>.Capabilities.APIVersions.Has</code> or <code>semverCompare</code> on <code>.Capabilities.KubeVersion</code> to conditionally select the correct API version in the template.</p><pre>
{{ if .Capabilities.APIVersions.Has "apps/v1" }}
apiVersion: apps/v1
{{ else }}
apiVersion: apps/v1beta2
{{ end }}
kind: Deployment
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The <code>.Capabilities</code> object is Helm's way of detecting what the target cluster supports. Always use it when a resource API version is deprecated across K8s versions. This is especially relevant for Ingress (networking.k8s.io/v1 vs v1beta1), PodSecurityPolicy (removed in 1.25), and CronJob (batch/v1 vs batch/v1beta1).</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">S4</span><div class="eq-question"><strong>Scenario:</strong> You run <code>helm upgrade anihpj ./chart --atomic --timeout 3m</code>. The upgrade starts, a pre-upgrade hook runs for 2 minutes, then the new pods start but one stays in Pending for 3 more minutes. What happens?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The upgrade will <strong>time out after 3 minutes total</strong> and automatically <strong>rollback</strong> (because of <code>--atomic</code>). The hook's 2 minutes counts toward the timeout! The pending pod never gets a chance to start. Helm marks the release as <code>failed</code> and reverts to the previous revision.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>--timeout</code> is a TOTAL timeout for the entire operation, including hooks. If hooks take 2 minutes and pods need 3 minutes to start, you need at least <code>--timeout 6m</code>. Always set generous timeouts in production — the default 5 minutes is often insufficient for complex deployments with hooks and large images.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">S5</span><div class="eq-question"><strong>Scenario:</strong> Your team wants to share common label templates, security context definitions, and naming conventions across 5 different microservice charts. Each chart should import these shared definitions without duplicating code. What Helm feature enables this?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>Library Charts</strong> (<code>type: library</code> in Chart.yaml). Create a library chart with <code>{{ define "..." }}</code> blocks for common patterns. Each microservice chart adds the library as a dependency and uses <code>{{ include "..." . }}</code> to invoke the shared templates.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Library charts are the Helm equivalent of shared code libraries. They contain only <code>templates/</code> (no deployable resources) and expose named templates via <code>define</code>. This is the DRY (Don't Repeat Yourself) pattern for Helm at organizational scale. Change one library template, and all consuming charts benefit on next upgrade.</p></div></details></div>
                </div>
'''
    insert_before_qa(ch17_s, ch18_s, content, "Ch17: Scenario Questions")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
