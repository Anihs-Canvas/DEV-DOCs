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
# CHAPTER 15: 95%+ Strategy - Advanced exam techniques
# ============================================================
ch15_s = chapter_starts.get(15, -1)
ch16_s = chapter_starts.get(16, -1)
if ch15_s > 0 and ch16_s > ch15_s:
    content = '''
                <div class="section-block">
                    <h4>15.14 The 95%+ Strategy — What Separates Top Scorers</h4>
                    <p>Getting 70-85% is knowing Helm. Getting 95%+ is knowing Helm's traps. Here's what the top 5% do differently.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">The 95%+ Mental Model</div>
<pre>
70-85% SCORER                          95%+ SCORER
═══════════════════════════════════     ═══════════════════════════════════
Reads the question → types command      Reads the question → checks NAMESPACE
                                        FIRST, then types command

helm install app ./chart                helm install app ./chart \\
                                          -n EXACT-NAMESPACE-FROM-QUESTION \\
                                          --create-namespace --atomic --wait

Uses default values                     Checks if question requires SPECIFIC
                                        values.yaml or --set overrides

helm lint ./chart                       helm lint ./chart --strict --quiet
                                        (--strict treats warnings as errors)

Forgets --dry-run on upgrades           ALWAYS dry-runs before every upgrade
                                        helm upgrade app ./chart --dry-run

Doesn't verify after install            Shows verification commands in answer:
                                        helm list -n NS; helm history -n NS;
                                        kubectl get all -n NS

Leaves broken releases                  helm uninstall broken-release -n NS
                                        before re-attempting
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>15.15 The 10 Most Common Point-Losing Mistakes (And How to Never Make Them)</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>#</th><th>Mistake</th><th>Points Lost</th><th>The 95%+ Fix</th></tr></thead>
                        <tbody>
                            <tr><td>1</td><td>Wrong namespace</td><td>100% of question</td><td>Read namespace FIRST. Type <code>-n NS</code> BEFORE the command. Make it the FIRST thing you type.</td></tr>
                            <tr><td>2</td><td>Missing --create-namespace</td><td>Install fails</td><td>Always add <code>--create-namespace</code> on install. Remove only if the question says "namespace already exists."</td></tr>
                            <tr><td>3</td><td>Not using --atomic</td><td>Partial failures</td><td>Every production install/upgrade gets <code>--atomic --wait</code>. The ONLY exception: the question explicitly says "do not rollback on failure."</td></tr>
                            <tr><td>4</td><td>Forgetting --reuse-values vs --reset-values</td><td>Wrong config</td><td>Mantra: "New install = use -f file. Upgrade keeping old = --reuse-values. Upgrade fresh = --reset-values -f new-file."</td></tr>
                            <tr><td>5</td><td>Not saving answer file immediately</td><td>Lost work</td><td>Copy every successful command to the answer file THE MOMENT it works. Don't wait until the end.</td></tr>
                            <tr><td>6</td><td>Spending >5 min on one question</td><td>5+ missed questions</td><td>Set a hard 5-minute timer per question. Flag and skip. Come back with remaining time.</td></tr>
                            <tr><td>7</td><td>Editing templates instead of values</td><td>Wrong approach</td><td>If the question says "change replicas to 5", use <code>--set replicaCount=5</code> or edit values.yaml. NEVER edit templates/deployment.yaml.</td></tr>
                            <tr><td>8</td><td>Not running helm lint first</td><td>Debugging waste</td><td><code>helm lint --strict</code> takes 1 second. It catches typos, missing fields, bad YAML. ALWAYS run it before install.</td></tr>
                            <tr><td>9</td><td>Leaving failed releases undeleted</td><td>Name conflicts</td><td>After a failed attempt: <code>helm uninstall NAME -n NS</code> then re-try. Failed releases block the name.</td></tr>
                            <tr><td>10</td><td>Not verifying after operations</td><td>Unnoticed failures</td><td>After every install/upgrade: <code>helm list -n NS; helm history NAME -n NS; helm status NAME -n NS</code>. Show the examiner you verified.</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>15.16 Speed Techniques — Save 15+ Minutes</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">⚡</div><h5>Command Patterns to Type Fast</h5><pre>
# Pattern 1: Install template
hi NAME ./chart -n NS --create-ns --atomic --wait

# Pattern 2: Upgrade template
hu NAME ./chart -n NS --atomic --wait

# Pattern 3: Rollback template
hr NAME -n NS  # to previous

# Pattern 4: Get info
hgm NAME -n NS | head -20  # manifest
hgv NAME -n NS --all | head -20  # values
hhist NAME -n NS  # history

KEY: hi=helm install, hu=helm upgrade,
hr=helm rollback, hgm=helm get manifest,
hgv=helm get values, hhist=helm history
</pre></div>
                        <div class="info-card"><div class="card-icon">🎯</div><h5>Answer File Strategy</h5><pre>
# For EVERY question, save:
# 1. The exact command you ran
# 2. Verification output
echo "Q1: helm install app ./chart \\
  -n web --create-ns --atomic" >> answers.txt
helm list -n web >> answers.txt

# For template questions:
echo "Q5: template fix:" >> answers.txt
cat templates/deployment.yaml >> answers.txt

# SAVE IMMEDIATELY after each question.
# The answer file IS your score.
</pre></div>
                    </div>
                </div>
'''
    insert_before_qa(ch15_s, ch16_s, content, "Ch15: 95% Strategy")

# ============================================================
# CHAPTER 16: Add Timed Exam Simulation Lab - Scored
# ============================================================
ch16_s = chapter_starts.get(16, -1)
ch17_s = chapter_starts.get(17, -1)
if ch16_s > 0 and ch17_s > ch16_s:
    content = '''
                <div class="section-block">
                    <h4>16.11 Lab 11: Timed 30-Minute Sprint — 10 Tasks (30 min, 10 points each)</h4>
                    <p>This lab is designed to be done AGAINST THE CLOCK. Set a 30-minute timer. No pausing. No looking at answers until time is up. Score yourself honestly. Repeat until you score 90+.</p>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">T1</div><div class="ps-content"><h5>Create & Install (3 min, 10 pts)</h5><pre>
# Create a chart named "sprint" and install it as "sprint-dev"
# in namespace "sprint-ns" with 2 replicas
# VERIFICATION: helm list -n sprint-ns shows sprint-dev deployed
helm create sprint
helm install sprint-dev ./sprint --set replicaCount=2 -n sprint-ns --create-namespace --atomic --wait
helm list -n sprint-ns</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T2</div><div class="ps-content"><h5>Values Override (3 min, 10 pts)</h5><pre>
# Create values-custom.yaml with service.type=NodePort and service.port=8080
# Upgrade sprint-dev using this file
cat > values-custom.yaml <<EOF
service:
  type: NodePort
  port: 8080
EOF
helm upgrade sprint-dev ./sprint -f values-custom.yaml -n sprint-ns --atomic --wait
helm get values sprint-dev -n sprint-ns --all | grep -E "type|port"</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T3</div><div class="ps-content"><h5>Rollback (2 min, 10 pts)</h5><pre>
# Rollback sprint-dev to revision 1 and verify
helm rollback sprint-dev 1 -n sprint-ns
helm history sprint-dev -n sprint-ns
# Revision 3 should be DEPLOYED with rev 1 config</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T4</div><div class="ps-content"><h5>Second Environment (3 min, 10 pts)</h5><pre>
# Install the same sprint chart as "sprint-prod" in "sprint-prod-ns"
# with 5 replicas and service.type=ClusterIP
helm install sprint-prod ./sprint \
  --set replicaCount=5 --set service.type=ClusterIP \
  -n sprint-prod-ns --create-namespace --atomic --wait
helm list -n sprint-prod-ns</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T5</div><div class="ps-content"><h5>Dry-Run & Lint (3 min, 10 pts)</h5><pre>
# Lint the sprint chart with --strict, then do a dry-run upgrade
# of sprint-prod with replicaCount=10
helm lint ./sprint --strict
helm upgrade sprint-prod ./sprint --set replicaCount=10 \
  -n sprint-prod-ns --dry-run --debug 2>&1 | head -30</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T6</div><div class="ps-content"><h5>Template Debugging (4 min, 10 pts)</h5><pre>
# Render the sprint chart templates locally and save to rendered.yaml
# Then extract ONLY the Deployment kind from the rendered output
helm template sprint-dev ./sprint > rendered.yaml
grep -A 50 "kind: Deployment" rendered.yaml | head -30</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T7</div><div class="ps-content"><h5>Package & Repo (4 min, 10 pts)</h5><pre>
# Package the sprint chart, then create a local repo index
helm package ./sprint
# Creates sprint-0.1.0.tgz
mkdir -p local-repo
mv sprint-0.1.0.tgz local-repo/
helm repo index local-repo/
helm repo add local file://$(pwd)/local-repo
helm repo update
helm search repo local/</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T8</div><div class="ps-content"><h5>Release Inspection (3 min, 10 pts)</h5><pre>
# Show the manifest, values, and history of sprint-prod
helm get manifest sprint-prod -n sprint-prod-ns | head -20
helm get values sprint-prod -n sprint-prod-ns --all | head -20
helm history sprint-prod -n sprint-prod-ns</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T9</div><div class="ps-content"><h5>Dependency Addition (3 min, 10 pts)</h5><pre>
# Add a dependency to sprint/Chart.yaml and update
# Dependency: common chart (or skip if no network)
cat >> sprint/Chart.yaml <<EOF
dependencies:
  - name: common
    version: "^2.0.0"
    repository: "https://charts.bitnami.com/bitnami"
EOF
# helm dependency update sprint/  (requires network)</pre></div></div>
                        <div class="ps-step"><div class="ps-num">T10</div><div class="ps-content"><h5>Cleanup (2 min, 10 pts)</h5><pre>
# Uninstall both releases and verify nothing remains
helm uninstall sprint-dev -n sprint-ns
helm uninstall sprint-prod -n sprint-prod-ns
helm list -A | grep sprint  # Should be empty
# Score: __/100</pre></div></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">🎯</div><div class="ckad-tip-content"><strong>Scoring Rubric:</strong> 10 pts per task. 70+ = exam-ready. 85+ = strong. 95+ = guaranteed pass. Time yourself strictly. If you finish with &gt;5 minutes remaining AND score 95+, you're in the top tier. Repeat this lab daily until you hit 95+ in under 25 minutes.</div></div>
                </div>
'''
    insert_before_qa(ch16_s, ch17_s, content, "Ch16: Timed Sprint Lab")

# ============================================================
# CHAPTER 17: Add tricky multi-concept Q&As for 95%+
# ============================================================
ch17_s = chapter_starts.get(17, -1)
ch18_s = chapter_starts.get(18, -1)
if ch17_s > 0 and ch18_s > ch17_s:
    content = '''
                <div class="section-block">
                    <h4>17.8 95%+ Challenge Questions — Multi-Concept Scenarios</h4>
                    <p>These questions combine 2-3 Helm concepts — exactly like the hardest exam questions. If you can answer these correctly, you're ready for 95%+.</p>
                </div>
                <div class="cka-exam-questions">
                    <div class="exam-question-item"><span class="eq-number">H1</span><div class="eq-question"><strong>Scenario:</strong> You <code>helm install app ./chart -n prod --set image.tag=v1.0</code>. A colleague runs <code>helm upgrade app ./chart -n prod --reuse-values</code> without any flags. What image tag is now deployed?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>v1.0</strong>. <code>--reuse-values</code> preserves ALL previously set values, including the <code>--set image.tag=v1.0</code> from the original install. Even though no <code>--set</code> was used in the upgrade, the old --set value is remembered and reused.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the #1 gotcha with --reuse-values. Helm remembers ALL values from the previous release — including --set values, -f file values, AND chart defaults merged together. Using --reuse-values means "keep everything exactly as it was, only change what I explicitly override now." If you use --reuse-values and DON'T override the image tag, it stays at v1.0 even if the chart's values.yaml now says v2.0.</p><pre>
# TRACE THE VALUES:
# Initial install: helm install app ./chart --set image.tag=v1.0 -n prod
#   Computed values: {replicaCount: 1 (default), image.tag: v1.0 (--set)}
# 
# Upgrade with --reuse-values:
#   helm upgrade app ./chart -n prod --reuse-values
#   Computed values: {replicaCount: 1 (reused), image.tag: v1.0 (REUSED!)}
#   Chart's values.yaml says v2.0 but --reuse-values ignores it!
# 
# Upgrade WITHOUT --reuse-values (also no --reset-values):
#   helm upgrade app ./chart -n prod
#   Computed values: {replicaCount: 1 (chart default), image.tag: v1.0 (REMEMBERED!)}
#   Even without --reuse-values, previous --set values are remembered!
#   This is the "sticky --set" behavior.
# 
# Upgrade with --reset-values:
#   helm upgrade app ./chart -n prod --reset-values
#   Computed values: {replicaCount: 1 (chart default), image.tag: v2.0 (chart default)}
#   ONLY --reset-values truly discards previous --set values.
</pre></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">H2</span><div class="eq-question"><strong>Scenario:</strong> Your chart has a template: <code>{{ .Values.db.password | b64enc }}</code>. The value in values.yaml is <code>db.password: changeme</code>. You install with <code>--set db.password=secret123</code>. What is the base64-encoded value in the Secret?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>c2VjcmV0MTIz</code> — the base64 encoding of <strong>"secret123"</strong>. Because <code>--set</code> has the highest precedence, it overrides <code>values.yaml</code>'s <code>changeme</code>. The template receives <code>secret123</code>, and <code>b64enc</code> encodes that.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This tests value precedence AND template function understanding simultaneously. <code>--set</code> is priority #1, so the template sees "secret123" not "changeme". <code>b64enc</code> encodes whatever string it receives. The Secret's data field will contain the base64 of "secret123".</p><pre>
# Value precedence in action:
# values.yaml:     db.password = "changeme"    (priority 5, lowest)
# --set:           db.password = "secret123"   (priority 1, highest)
# Template sees:   "secret123"
# b64enc output:   c2VjcmV0MTIz

# Verify:
echo -n "secret123" | base64
# c2VjcmV0MTIz
</pre></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">H3</span><div class="eq-question"><strong>Scenario:</strong> Your Deployment template uses <code>{{ include "mylib.labels" . | nindent 4 }}</code> inside a <code>range .Values.env</code> block. The template fails with "nil pointer." Why?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Inside <code>range</code>, the dot (<code>.</code>) is rebound to the current loop element. So <code>.</code> no longer refers to the root context. <code>include "mylib.labels" .</code> passes the loop element (an env var) instead of the root, causing the nil pointer.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the classic "dot rebinding" trap. Inside <code>range</code> and <code>with</code>, <code>.</code> changes. You must save the root context before entering a scope-changing block. ALWAYS use <code>{{- $ := . -}}</code> at the top of templates that use range/with.</p><pre>
# WRONG — dot is rebound inside range:
{{ range .Values.env }}
  labels:
    {{ include "mylib.labels" . | nindent 4 }}  ← . is now an env item!
  - name: {{ .name }}
{{ end }}

# RIGHT — save root context first:
{{- $root := . -}}
{{ range .Values.env }}
  labels:
    {{ include "mylib.labels" $root | nindent 4 }}  ← $root is the original .
  - name: {{ .name }}  ← . here is the env item (correct)
{{ end }}
</pre></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">H4</span><div class="eq-question"><strong>Scenario:</strong> You run <code>helm upgrade app ./chart --atomic --timeout 2m</code>. The pre-upgrade hook takes 90 seconds, the post-upgrade hook takes 60 seconds, and pods take 30 seconds to become ready. Does the upgrade succeed?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>NO — it times out.</strong> Total time: 90s (pre-hook) + 60s (post-hook) + 30s (pods) = <strong>180 seconds</strong>. But <code>--timeout 2m</code> = 120 seconds. The upgrade fails and <code>--atomic</code> triggers auto-rollback.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The --timeout is a TOTAL timeout for the ENTIRE operation — hooks + resource creation + waiting for readiness. If hooks consume most of the time budget, there's none left for the actual deployment. Always calculate: hook time + pod startup time + buffer = minimum timeout.</p><pre>
# TIMEOUT CALCULATION:
# Pre-install hooks:  0s (none) or variable
# Pre-upgrade hooks:  90s
# Resource creation:  5s
# Pod startup:       30s
# Post-install hooks: 60s
# ─────────────────────────
# TOTAL NEEDED:      185s
# 
# SAFE TIMEOUT: --timeout 5m (300s = 185s + 115s buffer)
# AGGRESSIVE:  --timeout 4m (240s = just enough)
# FAIL:         --timeout 2m (120s < 185s needed)
</pre></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">H5</span><div class="eq-question"><strong>Scenario:</strong> Your chart is at version 0.1.0. You make a breaking change to the template structure (renamed several value keys). What version should the chart be, and how do you communicate this to users?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Bump to <strong>0.2.0</strong> (MINOR version increment for breaking changes pre-1.0.0). Document ALL renamed keys in the CHANGELOG and NOTES.txt. After 1.0.0, breaking changes require a MAJOR version bump (1.0.0 → 2.0.0).</p><pre>
# SemVer for charts:
# MAJOR.MINOR.PATCH
# 
# Pre-1.0.0 (0.x.y):
#   PATCH (0.1.0→0.1.1): Bug fixes, no behavior change
#   MINOR (0.1.0→0.2.0): Breaking changes allowed
# 
# Post-1.0.0:
#   PATCH (1.0.0→1.0.1): Bug fixes, backwards-compatible
#   MINOR (1.0.0→1.1.0): New features, backwards-compatible
#   MAJOR (1.0.0→2.0.0): Breaking changes
# 
# DEPRECATION PATTERN:
# 1. v1.0.0: Add new key, deprecate old key (NOTES.txt warning)
# 2. v1.1.0: Old key still works but loud warnings
# 3. v2.0.0: Remove old key entirely (MAJOR bump)
</pre></div></details></div>
                </div>
'''
    insert_before_qa(ch17_s, ch18_s, content, "Ch17: 95% Challenge Q&As")

# ============================================================
# CHAPTER 20: More tricky troubleshooting for 95%+
# ============================================================
ch20_s = chapter_starts.get(20, -1)
app_a_pos = html.find('id="appendix-a"')
if ch20_s > 0 and app_a_pos > ch20_s:
    content = '''
                <div class="section-block">
                    <h4>20.11 Tricky Troubleshooting — The Hardest Debugging Scenarios</h4>
                    <p>These are the scenarios that separate 85% from 95%+ scorers. When Helm behaves unexpectedly, these patterns help you diagnose the root cause in seconds.</p>
                </div>
                <div class="section-block">
                    <h4>20.11a The "Silent Failure" Pattern — Template Renders But Resource Is Wrong</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">Debugging the Silent Failure</div>
<pre>
SYMPTOM: helm install succeeds, but the deployed resource has wrong values.
         No error message — the template rendered, just incorrectly.

ROOT CAUSE CHECKLIST:
□ Are you inside a 'with' or 'range' block where '.' was rebound?
  → Check if .Values.xxx is accessing the wrong context
  
□ Did you use 'template' instead of 'include'?
  → template writes directly, can't be piped. Use include for pipelines.
  
□ Is there a whitespace issue?
  → {{ .Values.port }} vs {{- .Values.port -}}. The - matters!
  
□ Did a previous --set value persist?
  → helm get values RELEASE -n NS --all (check computed values)
  
□ Is the values.yaml YAML indented correctly?
  → YAML is whitespace-sensitive. Check for tabs vs spaces.

DEBUG COMMAND:
helm get manifest RELEASE -n NS | grep -A 20 "kind: Deployment"
# Shows EXACTLY what was deployed
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>20.11b The "Sticky --set" Trap — Why Your Values Won't Change</h4>
<pre>
SCENARIO:
$ helm install app ./chart --set image.tag=v1.0
$ helm upgrade app ./chart  # NO --set, NO --reuse-values
# Expected: image.tag should be the chart default (v2.0)
# Reality: image.tag is STILL v1.0!

WHY: Helm REMEMBERS previous --set values unless you use --reset-values.
     This is called the "sticky --set" behavior.

FIX:
Option A: helm upgrade app ./chart --reset-values -f values.yaml
Option B: helm upgrade app ./chart --set image.tag=v2.0
Option C: helm upgrade app ./chart --reset-values  (uses chart defaults only)

PRO TIP: Always use --reset-values when you want a truly fresh start.
         --reuse-values keeps everything (including deprecated --set).
         No flag = previous --set values are remembered (sticky).
</pre>
                </div>
'''
    insert_before_qa(ch20_s, app_a_pos, content, "Ch20: Tricky Troubleshooting")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
