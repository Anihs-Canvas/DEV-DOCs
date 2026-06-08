import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

def insert_before_qa_end(ch_start, ch_end, new_content, label):
    global html, changes
    chapter = html[ch_start:ch_end]
    # Find the closing </div> of the cka-exam-questions div
    qa_start = chapter.rfind('class="cka-exam-questions"')
    if qa_start < 0:
        print("  {}: No Q&A section".format(label))
        return False
    # Find the matching closing </div> for cka-exam-questions
    search_start = qa_start + 30
    depth = 1
    pos = search_start
    while depth > 0 and pos < len(chapter):
        no = chapter.find('<div', pos)
        nc = chapter.find('</div>', pos)
        if nc < 0: break
        if no >= 0 and no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            if depth == 0:
                qa_close = nc
            pos = nc + len('</div>')
    if depth != 0:
        print("  {}: Could not find Q&A closing".format(label))
        return False
    abs_insert = ch_start + qa_close
    html = html[:abs_insert] + new_content + '\n' + html[abs_insert:]
    changes += 1
    print("  {}: Added Q&As".format(label))
    return True

chapter_starts = {}
for ch in range(1, 22):
    pos = html.find('id="ch{}"'.format(ch))
    if pos >= 0:
        chapter_starts[ch] = pos

# ============================================================
# CHAPTER 4: Values — Add more Q&As
# ============================================================
ch4_s = chapter_starts.get(4, -1)
ch5_s = chapter_starts.get(5, -1)
if ch4_s > 0 and ch5_s > ch4_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">What happens when you use <code>-f file1.yaml -f file2.yaml</code> and both files define <code>replicaCount</code>?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The LAST file wins. <code>file2.yaml</code>'s <code>replicaCount</code> is used. Non-conflicting keys from BOTH files are preserved (deep merge).</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Multiple <code>-f</code> files are merged left-to-right. Each subsequent file overrides conflicting keys from previous files. Non-conflicting keys are preserved from all files. This is a deep merge, not a replacement.</p><pre>
# file1.yaml:        file2.yaml:        RESULT:
replicaCount: 2      replicaCount: 5    replicaCount: 5  (file2 wins)
image:               image:             image:
  repo: nginx          tag: latest        repo: nginx    (from file1)
                                         tag: latest     (from file2)
</pre></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">How do you prevent a chart from being installed on Kubernetes versions older than 1.25?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Set <code>kubeVersion: "&gt;=1.25.0-0"</code> in Chart.yaml. Helm will refuse to install on clusters older than 1.25. The <code>-0</code> suffix allows pre-release K8s versions.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>kubeVersion</code> uses SemVer constraints. <code>&gt;=1.25.0</code> means 1.25.0 or newer. <code>&gt;=1.25.0-0</code> includes pre-releases like v1.25.0-alpha.1. This is different from <code>.Capabilities.KubeVersion</code> in templates which checks at render time.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">What does <code>--set-json</code> do and when should you use it?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>--set-json</code> sets a value from a JSON string, preserving complex types (arrays, nested objects). Use it when <code>--set</code> can't handle the complexity — e.g., arrays, multi-level nesting.</p><pre>
# --set handles simple values:
--set image.tag=v2.0

# --set-json handles complex structures:
--set-json 'resources={"limits":{"cpu":"500m","memory":"512Mi"}}'
--set-json 'env=[{"name":"DEBUG","value":"false"}]'
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>--set</code> auto-detects types and works well for simple scalar values. <code>--set-json</code> (Helm 3.7+) accepts valid JSON and preserves the exact structure. Use it for arrays, nested objects, or when you need precise type control.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">You run <code>helm install app ./chart --set image.tag=v1.0</code>. Then <code>helm upgrade app ./chart --reset-values</code>. What image tag is used?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The chart's <strong>default</strong> <code>image.tag</code> from <code>values.yaml</code>. <code>--reset-values</code> discards ALL previously set values (including the <code>--set image.tag=v1.0</code> from install). Only the chart's values.yaml and any new <code>-f</code>/<code>--set</code> flags are used.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Without <code>--reset-values</code> or <code>--reuse-values</code>, Helm remembers previous <code>--set</code> values (sticky behavior). <code>--reset-values</code> is the ONLY way to completely discard old <code>--set</code> values and start fresh from the chart's defaults.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">How do you share a common image registry across all subcharts without repeating it?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use the <strong><code>global</code></strong> key in the parent chart's <code>values.yaml</code>. All subcharts automatically have access to <code>.Values.global</code> without any import.</p><pre>
# Parent values.yaml:
global:
  imageRegistry: myregistry.io
  imagePullSecrets:
    - name: regcred

# Any subchart template:
image: "{{ .Values.global.imageRegistry }}/myapp:v1.0"
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The <code>global</code> namespace is special — it's automatically available to ALL subcharts without explicit <code>import-values</code>. The parent chart can also override subchart-specific global values. Use <code>global</code> for truly cross-cutting concerns like registry, pull secrets, and common labels.</p></div></details></div>
'''
    insert_before_qa_end(ch4_s, ch5_s, content, "Ch4: +5 Q&As")

# ============================================================
# CHAPTER 6: Templating — Add more Q&As  
# ============================================================
ch6_s = chapter_starts.get(6, -1)
ch7_s = chapter_starts.get(7, -1)
if ch6_s > 0 and ch7_s > ch6_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">What does <code>{{- </code> (dash) do in a template?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The dash <code>-</code> trims whitespace. <code>{{-</code> trims LEFT whitespace. <code>-}}</code> trims RIGHT whitespace. <code>{{- ... -}}</code> trims BOTH sides. Without the dash, whitespace (newlines, spaces) around the action is preserved in output.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Whitespace control is critical for clean YAML output. Without <code>-</code>, template actions leave blank lines in the rendered YAML. <code>{{- .Values.name -}}</code> ensures the value is tightly wrapped with no extra whitespace. Exam tip: always use <code>-</code> for clean output.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">How do you access a file's content inside a template?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use the <code>.Files.Get</code> object. <code>{{ .Files.Get "config.json" }}</code> returns the file content as a string. <code>.Files.GetBytes</code> returns bytes. <code>.Files.Glob</code> matches patterns. <code>.Files.AsConfig</code> and <code>.Files.AsSecrets</code> produce ConfigMap/Secret-ready YAML.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Files must be inside the chart directory (not in templates/) and NOT excluded by .helmignore. <code>.Files.Get</code> throws an error if the file doesn't exist — use <code>.Files.Glob</code> to check existence first. Files are loaded at render time, not at package time.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">What's the difference between <code>.Chart.Version</code> and <code>.Chart.AppVersion</code>?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>.Chart.Version</code> is the CHART version (from Chart.yaml's <code>version</code> field — SemVer). <code>.Chart.AppVersion</code> is the APPLICATION version (from <code>appVersion</code> field — informational only). Change the chart version on every chart modification. Change appVersion when the app inside changes.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Chart version controls Helm upgrades and is required. AppVersion is optional and purely informational — it doesn't affect Helm's behavior. Both are accessible in templates for labeling: <code>app.kubernetes.io/version: {{ .Chart.AppVersion }}</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">How do you conditionally include a resource based on a boolean value?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use <code>{{ if .Values.ingress.enabled }}...{{ end }}</code> to wrap the entire resource. The resource is only rendered if the condition is true.</p><pre>
{{ if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "mylib.fullname" . }}
spec:
  rules:
  - host: {{ .Values.ingress.host }}
{{ end }}
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the standard pattern for optional resources (Ingress, HPA, PVC, ServiceAccount). The ENTIRE resource block is wrapped in the conditional. Values like <code>ingress.enabled: false</code> in values.yaml completely omit the resource from rendered output.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">What is <code>.Release.IsInstall</code> and <code>.Release.IsUpgrade</code> used for?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>These booleans tell you whether the current operation is an install or upgrade. <code>.Release.IsInstall</code> is <code>true</code> only during <code>helm install</code>. <code>.Release.IsUpgrade</code> is <code>true</code> during <code>helm upgrade</code>. Both are <code>false</code> during <code>helm template</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Use these to differentiate behavior: run database migrations only on install, skip certain resources on upgrades, or show different NOTES.txt messages. Combined with <code>.Release.Revision</code> (increments on each install/upgrade/rollback).</p></div></details></div>
'''
    insert_before_qa_end(ch6_s, ch7_s, content, "Ch6: +5 Q&As")

# ============================================================
# CHAPTER 9: Dependencies — Add more Q&As
# ============================================================
ch9_s = chapter_starts.get(9, -1)
ch10_s = chapter_starts.get(10, -1)
if ch9_s > 0 and ch10_s > ch9_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">What's the difference between <code>helm dependency update</code> and <code>helm dependency build</code>?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>helm dependency update</code> fetches from REMOTE repositories (network required). <code>helm dependency build</code> reads from <code>Chart.lock</code> and the local <code>charts/</code> directory (no network). Use <code>update</code> to resolve versions; use <code>build</code> in CI for reproducible builds.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>update</code> downloads new .tgz files and updates Chart.lock. <code>build</code> only works if Chart.lock exists — it uses the locked versions without network access. In CI/CD, commit Chart.lock and use <code>build</code> for deterministic, offline-safe dependency resolution.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">How do you add a dependency from a local file path (not a remote repo)?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use <code>repository: file://../path/to/chart</code> in Chart.yaml. The path is relative to the chart directory. This is useful for development, monorepos, and testing before publishing.</p><pre>
dependencies:
  - name: my-common-chart
    version: 0.1.0
    repository: file://../common-chart
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>File-based dependencies are resolved from the local filesystem. The chart is COPIED into <code>charts/</code> during <code>helm dependency update</code>. This is great for monorepos where charts live side by side. The version must match the Chart.yaml of the local chart.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">Your umbrella chart has 3 subcharts. How do you pass the same namespace to all of them?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Subcharts inherit the release namespace automatically. No explicit configuration needed. All resources from the umbrella chart and its subcharts are deployed to the namespace specified with <code>-n</code> or <code>--namespace</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>When you run <code>helm install myapp ./umbrella -n prod</code>, ALL subcharts are deployed to the <code>prod</code> namespace. Subcharts do NOT get their own namespaces. If you need different namespaces, deploy each chart as an independent release.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">What is the purpose of <code>Chart.lock</code> and should you commit it to Git?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>Chart.lock</code> pins EXACT dependency versions and SHA256 digests. <strong>YES, commit it to Git.</strong> It ensures reproducible builds — everyone (and CI/CD) gets the exact same dependency versions.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Without Chart.lock, <code>helm dependency update</code> might resolve different versions over time (e.g., if a new patch of postgresql is released). Chart.lock locks the exact version and digest for cryptographic integrity. Do NOT commit <code>charts/*.tgz</code> files — add them to <code>.gitignore</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">How do you completely disable a subchart conditionally?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use a <code>condition</code> in Chart.yaml mapped to a values key. When that value is <code>false</code>, the subchart is skipped entirely.</p><pre>
# Chart.yaml:
dependencies:
  - name: redis
    condition: redis.enabled

# values.yaml:
redis:
  enabled: false  # Redis NOT deployed

# Or override at install:
helm install app ./chart --set redis.enabled=true
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Conditions provide runtime toggling of dependencies. Combined with <code>tags</code>, you can group dependencies: <code>tags: [database]</code> and <code>tags: database: false</code> disables all DB-related subcharts at once. Both condition AND all tags must be true for the subchart to be enabled.</p></div></details></div>
'''
    insert_before_qa_end(ch9_s, ch10_s, content, "Ch9: +5 Q&As")

# ============================================================
# CHAPTER 10: Hooks — Add more Q&As
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">Can a single resource be multiple hook types? Give an example.</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Yes — use a comma-separated list in the annotation: <code>"helm.sh/hook": post-install,post-upgrade</code>. The resource runs on both install and upgrade.</p><pre>
metadata:
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "5"
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Multi-hook resources are common for database migrations (run after every install AND upgrade), cache warming, or API key rotation. The same hook resource definition is re-used across multiple lifecycle events. Each event triggers it independently.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">What happens to hook resources when you run <code>helm uninstall</code>?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Hook resources are <strong>NOT</strong> automatically deleted during <code>helm uninstall</code>. They are not managed as part of the release. To clean them up, use <code>helm.sh/hook-delete-policy</code> or manually delete them with <code>kubectl</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a critical operational detail. Pre/post-delete hooks are the exception — they run DURING uninstall. But hooks from previous installs/upgrades persist. Use <code>hook-succeeded</code> delete policy for one-time hooks, or periodically clean up with <code>kubectl delete job -l helm.sh/hook</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">How do you set a maximum execution time for a hook Job?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use the Job's <code>activeDeadlineSeconds</code> in the hook template. This is a Kubernetes Job feature, not a Helm feature. If the Job exceeds this time, it's terminated and the hook fails.</p><pre>
spec:
  activeDeadlineSeconds: 300  # 5 minutes max
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: hook-job
        ...
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Helm's <code>--timeout</code> applies to the ENTIRE operation. <code>activeDeadlineSeconds</code> applies to a specific Job. Use both: <code>activeDeadlineSeconds</code> for per-hook timeouts, <code>--timeout</code> for the overall operation budget. A hook exceeding activeDeadlineSeconds causes the entire operation to fail.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">Can hooks access <code>.Values</code>, <code>.Release</code>, and other template objects?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>Yes.</strong> Hooks are regular template files with special annotations. They have FULL access to <code>.Values</code>, <code>.Release</code>, <code>.Chart</code>, <code>.Files</code>, <code>.Capabilities</code>, and <code>.Template</code>. Use them just like any other template.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Hooks are rendered at the same time as other templates during install/upgrade. They share the same context. This means you can use <code>.Values.db.password</code> in a migration hook, <code>.Release.Name</code> for naming, or <code>.Files.Get</code> for SQL scripts.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">What's the difference between a hook weight of -5 and +5?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>-5 runs FIRST.</strong> Lower weights execute before higher weights. Default weight is 0. Negative weights run early (backups, pre-checks). Positive weights run later (notifications, post-processing).</p><pre>
Weight: -10  →  -5  →  0 (default)  →  +5  →  +10
        │       │        │              │       │
     backup  init-secret validate    migrate  notify
     (first)                                  (last)
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Weights are strings that Helm sorts numerically. Same-weight hooks may run in any order (don't rely on it). Use distinct weights for guaranteed ordering. The exam may ask you to "ensure Job A runs before Job B" — the answer is to give Job A a lower weight.</p></div></details></div>
'''
    insert_before_qa_end(ch10_s, ch11_s, content, "Ch10: +5 Q&As")

# ============================================================
# CHAPTER 21: Helm 4 — Add more Q&As
# ============================================================
ch21_s = chapter_starts.get(21, -1)
app_a_pos = html.find('id="appendix-a"')
if ch21_s > 0 and app_a_pos > ch21_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q6</span><div class="eq-question">How do you install a chart by OCI digest in Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>helm install myapp oci://registry.io/charts/app@sha256:abc123...</code>. The digest ensures cryptographic integrity — the chart is rejected if the digest doesn't match. This prevents supply chain attacks.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Digest-based installs use the SHA256 hash of the chart archive. If anyone tampers with the chart, the digest won't match and Helm rejects it. This is like <code>docker pull image@sha256:...</code> — you get EXACTLY what you expect, no more, no less.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q7</span><div class="eq-question">What is kstatus and how does it improve Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>kstatus</strong> is a Kubernetes SIG-CLI library that provides structured, per-resource status reporting. Instead of a binary "deployed/failed", Helm 4 can show detailed status for each resource: Pods ready/total, Services assigned, Ingresses reconciling.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>In Helm 3, <code>helm status</code> gives minimal information. kstatus integration in Helm 4 gives you per-resource health: ✓ Deployment ready (3/3), ⚠ Ingress reconciling, ✗ Job failed. This makes troubleshooting dramatically faster during deployments.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q8</span><div class="eq-question">What does "latching behavior" mean for server-side apply in Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Helm 4 remembers the apply method (client-side or server-side) used when a release was FIRST created. On subsequent upgrades, it uses the SAME method. New releases default to server-side apply; Helm 3 releases keep client-side apply after upgrading to Helm 4.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This prevents breaking changes when upgrading from Helm 3 to 4. Your existing Helm 3 releases continue using client-side apply even after you upgrade the Helm binary to v4. New releases created with Helm 4 use server-side apply by default. You can override with <code>--server-side</code> or <code>--server-side=false</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q9</span><div class="eq-question">Can you use existing Helm 3 plugins with Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>Yes.</strong> Existing executable-based plugins continue to work. The new WebAssembly (Wasm) runtime is optional. Plugins can be CLI plugins, getter plugins, or post-renderer plugins — all three types are supported.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Helm 4's plugin system is backwards-compatible. Existing plugins work unchanged. The Wasm runtime provides enhanced security isolation for new plugins but is not required. Migrate security-sensitive plugins to Wasm for better sandboxing.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q10</span><div class="eq-question">You have a Helm 3 CI/CD pipeline. What MUST you change before upgrading to Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>1. Update <code>--atomic</code> to <code>--rollback-on-failure</code> (old flag still works but deprecated). 2. Update post-renderer references from executable paths to plugin names. 3. Fix <code>helm registry login</code> URLs (remove path, domain only). 4. Test ALL charts with Helm 4 binary before production switch.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The minimum changes: rename flags in CI scripts, convert post-renderer scripts to plugins, and fix registry login commands. Helm 4 is backwards-compatible with all chart templates and existing releases, so the actual chart content doesn't need changes.</p></div></details></div>
'''
    insert_before_qa_end(ch21_s, app_a_pos, content, "Ch21: +5 Q&As")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
