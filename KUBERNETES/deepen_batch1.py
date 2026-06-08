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
# CHAPTER 4: Deep conceptual content - the WHY behind values
# ============================================================
ch4_s = chapter_starts.get(4, -1)
ch5_s = chapter_starts.get(5, -1)
if ch4_s > 0 and ch5_s > ch4_s:
    content = '''
                <div class="section-block">
                    <h4>4.10 The Philosophy of Values - Why Helm Separates Config from Templates</h4>
                    <p>This is possibly the most important conceptual shift in Helm: <strong>separating WHAT gets deployed (templates) from HOW it's configured (values)</strong>. This separation is what makes Helm charts reusable across environments, teams, and organizations.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">The Values-Template Contract</div>
<pre>
THE HELM CONTRACT
═══════════════════════════════════════════════════════════════

values.yaml (INPUT)          templates/ (TRANSFORM)       K8s YAML (OUTPUT)
─────────────────────        ─────────────────────        ─────────────────
replicaCount: 3        →     replicas: {{ .Values.   →    replicas: 3
                               replicaCount }}

image:                        containers:                   containers:
  repository: anihpj    →     - image: {{ .Values.   →     - image: myreg.io/
  tag: v2.0                    image.repository }}:             anihpj:v2.0
  pullPolicy: Always           {{ .Values.image.tag }}

service:                      spec:                         spec:
  type: LoadBalancer    →       type: {{ .Values.    →       type: LoadBalancer
  port: 80                      service.type }}              ports:
                                ports:                       - port: 80
                                - port: {{ .Values.
                                  service.port }}

THE KEY INSIGHT:
The template is a FUNCTION: f(values) = K8s YAML
Change the values → Change the output → WITHOUT touching templates!
This is the same principle as function parameters in programming.
</pre>
                    </div>
                    <div class="info-box tip"><h5>Why This Matters for the Exam</h5><p>When a question asks "change the number of replicas from 2 to 5," you should NEVER edit templates/deployment.yaml. Instead, use <code>--set replicaCount=5</code> or edit values.yaml and run <code>helm upgrade</code>. The exam tests this separation constantly — modifying templates when you should modify values is a common mistake that costs points.</p></div>
                </div>
                <div class="section-block">
                    <h4>4.11 The --set Flag - When to Use and When to Avoid</h4>
                    <div class="split-panel">
                        <div class="split-side split-good">
                            <h5>✅ Use --set for:</h5>
                            <ul>
                                <li>Quick overrides during development</li>
                                <li>CI/CD pipelines (inject build tag)</li>
                                <li>Secrets injection (password from env var)</li>
                                <li>One-off testing</li>
                                <li>Simple scalar values</li>
                            </ul>
                        </div>
                        <div class="split-side split-bad">
                            <h5>❌ Avoid --set for:</h5>
                            <ul>
                                <li>Complex nested structures</li>
                                <li>Production deployments (not reproducible)</li>
                                <li>Multiple values (hard to read)</li>
                                <li>Lists and arrays (use --set-json instead)</li>
                                <li>Anything you'd want in version control</li>
                            </ul>
                        </div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>--set vs --set-string:</strong> <code>--set replicaCount=5</code> produces an integer 5. <code>--set-string replicaCount=5</code> produces the string "5". <code>--set enabled=false</code> produces boolean false. <code>--set-string enabled=false</code> produces string "false" (which is truthy!). Use <code>--set-string</code> only when you explicitly need string type to override Helm's auto-detection.</div></div>
                </div>
                <div class="section-block">
                    <h4>4.12 Subchart Values - The Global Scope Pattern</h4>
                    <p>When a chart has subcharts (dependencies), values are scoped. Understanding this scoping is critical for configuring complex deployments correctly.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Values Scope in Parent-Subchart Hierarchy</div>
<pre>
VALUES SCOPE VISUALIZATION
═══════════════════════════════════════════════════════════════

Parent Chart (anihpj) values.yaml:
┌─────────────────────────────────────────────┐
│ replicaCount: 3         ← Parent only       │
│ image:                                       │
│   repository: anihpj    ← Parent only        │
│                                              │
│ postgresql:              ← SCOPE GATE        │
│   enabled: true                              │
│   auth:                                      │
│     password: secret123 ← Subchart visible   │
│                                              │
│ redis:                   ← SCOPE GATE        │
│   enabled: false                             │
│                                              │
│ global:                  ← GLOBAL SCOPE      │
│   imageRegistry: my.io   ← All subcharts see │
└─────────────────────────────────────────────┘

HOW SUBCHARTS ACCESS VALUES:
1. Subchart's OWN values.yaml (lowest priority)
2. Parent's section for that subchart (e.g., .Values.postgresql.auth.password)
3. Parent's global section (e.g., .Values.global.imageRegistry)

KEY: Subcharts CANNOT access parent's top-level values directly!
postgresql subchart CANNOT see .Values.replicaCount
postgresql subchart CAN see .Values.global.imageRegistry
</pre>
                    </div>
                </div>
'''
    insert_before_qa(ch4_s, ch5_s, content, "Ch4: Values Philosophy & Scoping")

# ============================================================
# CHAPTER 6: Deep conceptual content - Go templates from scratch
# ============================================================
ch6_s = chapter_starts.get(6, -1)
ch7_s = chapter_starts.get(7, -1)
if ch6_s > 0 and ch7_s > ch6_s:
    content = '''
                <div class="section-block">
                    <h4>6.12 Understanding the Template Rendering Pipeline - Step by Step</h4>
                    <p>When you run <code>helm install</code>, Helm doesn't just substitute values. It runs a full rendering pipeline that transforms templates + values into valid Kubernetes YAML. Understanding each step helps debug template issues.</p>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Load Chart</h5><p>Helm reads Chart.yaml, values.yaml, and ALL files in templates/ (recursively). Files matching .helmignore patterns are excluded. The chart is loaded into memory as a Go struct.</p></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Build Values</h5><p>Helm merges values in precedence order: chart's values.yaml → parent chart values → -f files (in order) → --set overrides. This produces a single merged <code>.Values</code> object.</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Execute Templates</h5><p>Each file in templates/ is processed by Go's <code>text/template</code> engine with the Sprig function library. The <code>.</code> (dot) is set to the root context containing .Values, .Release, .Chart, .Files, .Capabilities, and .Template.</p></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Concatenate & Parse as YAML</h5><p>All rendered template output is concatenated into one big YAML stream. Helm parses this stream to extract individual Kubernetes resource objects (separated by <code>---</code>).</p></div></div>
                        <div class="ps-step"><div class="ps-num">5</div><div class="ps-content"><h5>Sort & Apply</h5><p>Resources are sorted by kind (Namespaces first, then Secrets, ConfigMaps, Services, Deployments, etc.). This ensures dependencies are created in the right order. Then <code>kubectl apply</code> is called for each resource.</p></div></div>
                        <div class="ps-step"><div class="ps-num">6</div><div class="ps-content"><h5>Store Release</h5><p>The rendered manifest, computed values, and chart metadata are compressed, base64-encoded, and stored as a Kubernetes Secret named <code>sh.helm.release.v1.&lt;name&gt;.v&lt;rev&gt;</code>.</p></div></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>6.13 The Dot (.) - Helm's Most Important Concept</h4>
                    <p>In Go templates, <code>.</code> (dot) is the <strong>current context</strong>. It changes meaning depending on where you are in the template. Mastering the dot is essential for writing correct templates.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">How the Dot Changes Context</div>
<pre>
DOT CONTEXT VISUALIZATION
═══════════════════════════════════════════════════════════════

TOP LEVEL:
{{ .Values.image.tag }}    . = {Values: {...}, Release: {...}, Chart: {...}}
                              ↑
                          The ENTIRE root object

INSIDE with:
{{ with .Values.image }}     . = .Values.image = {repository: "anihpj", tag: "v2.0"}
  {{ .repository }}          .repository = "anihpj" ✓ (dot is now image object)
  {{ .tag }}                 .tag = "v2.0" ✓
{{ end }}

INSIDE range:
{{ range .Values.env }}      . = each element of the env list
  {{ .name }}                .name = "DEBUG" (dot is the current env item)
  {{ .value }}               .value = "true"
{{ end }}

DOT IS REBOUND INSIDE: with, range, define blocks
DOT IS PRESERVED BY: if/else blocks

CRITICAL: Inside {{ range }}, you CANNOT access .Values anymore!
Because . now points to the loop variable, not the root.
FIX: Save the root: {{ $root := . }} before range, then use {{ $root.Values.xxx }}
</pre>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>The #1 Template Error:</strong> Accessing <code>.Values.something</code> inside a <code>range</code> or <code>with</code> block without saving the root context first. Always do <code>{{- $ := . -}}</code> at the top of templates that use range/with to preserve access to the root.</div></div>
                </div>
'''
    insert_before_qa(ch6_s, ch7_s, content, "Ch6: Pipeline & Dot Context")

# ============================================================
# CHAPTER 9: Deep dive - Subchart vs Umbrella patterns, dependency resolution
# ============================================================
ch9_s = chapter_starts.get(9, -1)
ch10_s = chapter_starts.get(10, -1)
if ch9_s > 0 and ch10_s > ch9_s:
    content = '''
                <div class="section-block">
                    <h4>9.11 Subchart vs Umbrella Chart - When to Use Each Pattern</h4>
                    <p>These are two fundamentally different approaches to composing Helm deployments. Understanding when to use each is a mark of Helm proficiency.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>📦 Umbrella Chart Pattern</h5>
                            <div class="info-box tip"><p>ONE chart that declares OTHER charts as dependencies. The umbrella chart owns everything.</p></div>
<pre>
anihpj-umbrella/
  Chart.yaml:
    dependencies:
    - name: postgresql
    - name: redis
    - name: anihpj-app
  values.yaml:
    postgresql:
      auth:
        password: xxx
    redis:
      enabled: true
    anihpj-app:
      replicaCount: 3

INSTALL: helm install full-stack ./umbrella
ONE command deploys everything.
All releases share ONE namespace.
</pre>
                        </div>
                        <div class="split-side">
                            <h5>🔗 Independent Release Pattern</h5>
                            <div class="info-box"><p>EACH chart is deployed as a SEPARATE release. They're connected via service discovery.</p></div>
<pre>
# Deploy infrastructure first:
helm install postgresql bitnami/postgresql -n infra
helm install redis bitnami/redis -n infra

# Deploy application:
helm install anihpj ./anihpj-chart -n app \
  --set db.host=postgresql.infra.svc

Each release is INDEPENDENT.
Can upgrade/rollback individually.
Can span multiple namespaces.
</pre>
                        </div>
                    </div>
                    <div class="compare-table"><table>
                        <thead><tr><th>Factor</th><th>Umbrella Chart</th><th>Independent Releases</th></tr></thead>
                        <tbody>
                            <tr><td>Deployment</td><td>Single command</td><td>Multiple commands</td></tr>
                            <tr><td>Rollback</td><td>All or nothing</td><td>Per-component</td></tr>
                            <tr><td>Version Coupling</td><td>Tight (one Chart.lock)</td><td>Loose (independent)</td></tr>
                            <tr><td>Namespace</td><td>Shared namespace</td><td>Separate namespaces possible</td></tr>
                            <tr><td>Best For</td><td>Simple apps, demos, dev</td><td>Production, microservices</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>9.12 How helm dependency update Actually Works</h4>
                    <p>Understanding the internal mechanics of dependency resolution helps debug "chart not found" and version conflict errors.</p>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Read Chart.yaml Dependencies</h5><p>Helm reads the <code>dependencies</code> array. For each dependency, it checks: name, version constraint, repository URL, optional condition, and tags.</p></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Check Chart.lock (if exists)</h5><p>If <code>Chart.lock</code> exists, Helm compares its entries with Chart.yaml. If they match, it uses the locked versions (reproducible). If they differ, it downloads new versions. If Chart.lock is missing, it resolves fresh.</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Fetch Repository Index</h5><p>For each repository URL, Helm downloads <code>index.yaml</code> (cached locally). The index contains all available chart versions with their URLs and digests.</p></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Solve Version Constraints</h5><p>Helm finds all versions matching the constraint (e.g., <code>>=12.0.0 &lt;13.0.0</code>) and picks the highest version. The selected version's .tgz URL is recorded in Chart.lock with its SHA256 digest for integrity verification.</p></div></div>
                        <div class="ps-step"><div class="ps-num">5</div><div class="ps-content"><h5>Download .tgz to charts/</h5><p>The .tgz file is downloaded to <code>charts/</code> directory. These are NOT committed to Git (add <code>charts/*.tgz</code> to .gitignore). Chart.lock IS committed for reproducible builds.</p></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch9_s, ch10_s, content, "Ch9: Patterns & Dependency Resolution")

# ============================================================
# CHAPTER 10: Deep dive - How hooks interact with the release lifecycle
# ============================================================
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                <div class="section-block">
                    <h4>10.10 Hooks Deep Dive - How Helm Manages Hook Resources Differently</h4>
                    <p>Hooks are not just "resources that run at a specific time." They are managed by Helm through a completely different lifecycle than normal resources. Understanding this difference prevents confusion when hooks don't behave as expected.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Normal Resource vs Hook Resource Lifecycle</div>
<pre>
NORMAL RESOURCE LIFECYCLE:
═══════════════════════════════════════════════════════════════
helm install → resource CREATED → helm tracks it → helm upgrade updates it
helm uninstall → resource DELETED

HOOK RESOURCE LIFECYCLE:
═══════════════════════════════════════════════════════════════
helm install → hook CREATED → hook RUNS → hook DELETED (per policy)
helm upgrade → hook RE-CREATED (even if unchanged!) → hook RUNS → hook DELETED
helm uninstall → hook NOT deleted (unless it's a pre/post-delete hook)

KEY DIFFERENCES:
1. Hooks are NEVER part of the release manifest.
   helm get manifest does NOT include hook resources.

2. Hooks are NOT updated during helm upgrade.
   They are DELETED and RE-CREATED on every operation.

3. Hook failures BLOCK the entire operation.
   If a pre-install hook fails, NO resources are installed.
   If a post-upgrade hook fails, the upgrade is marked FAILED.
   (--atomic will auto-rollback on hook failure)

4. Hook resources are labeled:
   helm.sh/hook: <type>
   helm.sh/hook-weight: <number>
   helm.sh/hook-delete-policy: <policy>
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>10.11 Real-World Hook Patterns for anihpj</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🗄️</div><h5>Database Migration (pre-upgrade)</h5><p>Run Django migrations before new code rolls out. If migration fails, the upgrade is blocked and old version stays running.</p><pre>
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command: ["python", "manage.py", "migrate", "--noinput"]
</pre></div>
                        <div class="info-card"><div class="card-icon">💾</div><h5>Backup Before Upgrade (pre-upgrade)</h5><p>Dump the database before any schema changes. Runs with weight -10 (before migration).</p><pre>
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-backup
  annotations:
    "helm.sh/hook": pre-upgrade
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
                  "-U", "anihpj", "-f", "/backup/pre-upgrade.sql"]
</pre></div>
                    </div>
                </div>
'''
    insert_before_qa(ch10_s, ch11_s, content, "Ch10: Hook Lifecycle & anihpj Patterns")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
