import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

def insert_before_qaclose(ch_start, ch_end, new_content, label):
    global html, changes
    chapter = html[ch_start:ch_end]
    # Find cka-exam-questions and its closing </div> using a simple approach
    qa_start = chapter.find('class="cka-exam-questions"')
    if qa_start < 0:
        print("  {}: No Q&A".format(label))
        return False
    
    # From qa_start, count <div and </div> to find the matching close
    pos = qa_start
    depth = 0
    in_div = False
    while pos < len(chapter):
        next_open = chapter.find('<div', pos)
        next_close = chapter.find('</div>', pos)
        if next_close < 0:
            break
        if 0 <= next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth <= 0:
                qa_close = next_close + 6
                break
            pos = next_close + 6
    
    if depth > 0:
        print("  {}: Could not find Q&A close (depth={})".format(label, depth))
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

# Ch6 Q&As
ch6_s = chapter_starts.get(6, -1)
ch7_s = chapter_starts.get(7, -1)
if ch6_s > 0 and ch7_s > ch6_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">What does <code>{{- </code> (dash) do in a template?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The dash <code>-</code> trims whitespace. <code>{{-</code> trims LEFT whitespace. <code>-}}</code> trims RIGHT. <code>{{- ... -}}</code> trims BOTH. Without the dash, extra newlines appear in rendered YAML.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Whitespace control is critical for clean YAML output. Always use <code>{{-</code> and <code>-}}</code> at template boundaries. The dash chomps the adjacent whitespace including newlines.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">How do you access a file's content inside a template?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use <code>{{ .Files.Get "config.json" }}</code>. Returns file content as string. <code>.Files.GetBytes</code> returns bytes. <code>.Files.Glob "*.json"</code> matches patterns. Files must be in the chart directory and NOT excluded by .helmignore.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>.Files.Get</code> throws an error if the file doesn't exist — check with <code>.Files.Glob</code> first. <code>.Files.AsConfig</code> and <code>.Files.AsSecrets</code> produce ConfigMap/Secret-ready YAML automatically.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">What is the difference between <code>.Chart.Version</code> and <code>.Chart.AppVersion</code>?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>.Chart.Version</code> = chart's SemVer version (required). <code>.Chart.AppVersion</code> = application version (optional, informational). Change chart version on every chart change; appVersion when the application inside changes.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Chart version drives Helm upgrades. AppVersion is just metadata — useful for labeling: <code>app.kubernetes.io/version: {{ .Chart.AppVersion }}</code>. Both come from Chart.yaml.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">How do you conditionally include a resource using <code>if</code>?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Wrap the entire resource in <code>{{ if .Values.ingress.enabled }}...{{ end }}</code>. When the condition is false, the resource is completely omitted from rendered output. Use this for optional resources like Ingress, HPA, and PVC.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the standard pattern for optional resources. The condition checks a boolean from values.yaml. Combine with <code>else</code> for alternative resources: <code>{{ if .Values.tls }}...secure config...{{ else }}...basic config...{{ end }}</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">What are <code>.Release.IsInstall</code> and <code>.Release.IsUpgrade</code>?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Booleans indicating the current operation type. <code>.Release.IsInstall</code> is true during <code>helm install</code>. <code>.Release.IsUpgrade</code> is true during <code>helm upgrade</code>. Both are false during <code>helm template</code> (no cluster interaction).</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Use these to differentiate install vs upgrade behavior: run migrations only on fresh installs, skip certain resources on upgrades, show different NOTES.txt messages. <code>.Release.Revision</code> also increments on each install/upgrade/rollback.</p></div></details></div>
'''
    insert_before_qaclose(ch6_s, ch7_s, content, "Ch6: +5 Q&As")

# Ch10 Q&As
ch10_s = chapter_starts.get(10, -1)
ch11_s = chapter_starts.get(11, -1)
if ch10_s > 0 and ch11_s > ch10_s:
    content = '''
                    <div class="exam-question-item"><span class="eq-number">Q11</span><div class="eq-question">Can a single resource be multiple hook types?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>Yes.</strong> Use comma-separated values: <code>"helm.sh/hook": post-install,post-upgrade</code>. The resource runs on both events.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Multi-hook resources are common for DB migrations (run after install AND upgrade). Each lifecycle event triggers the hook independently. The same template definition is reused across events.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q12</span><div class="eq-question">Do hook resources get deleted during <code>helm uninstall</code>?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>No.</strong> Hook resources are NOT managed as part of the release. They persist after uninstall unless they have <code>hook-succeeded</code> or <code>before-hook-creation</code> delete policies. Pre/post-delete hooks are the exception — they run DURING uninstall.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Hook resources live independently of the release. Use <code>helm.sh/hook-delete-policy</code> for automatic cleanup, or periodically run <code>kubectl delete job -l helm.sh/hook</code> to clean up completed hook Jobs.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q13</span><div class="eq-question">How do you limit execution time for a hook Job?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use Kubernetes Job's <code>activeDeadlineSeconds</code> in the hook template spec. If exceeded, the Job is terminated and the hook fails. Different from Helm's <code>--timeout</code> which applies to the entire operation.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p><code>activeDeadlineSeconds: 300</code> gives the hook 5 minutes max. Exceeding it causes the entire install/upgrade to fail. Use both: per-hook timeouts via activeDeadlineSeconds, overall operation timeout via <code>--timeout</code>.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q14</span><div class="eq-question">Do hooks have access to <code>.Values</code> and <code>.Release</code>?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>Yes.</strong> Hooks are regular templates with special annotations. They have FULL access to ALL built-in objects: <code>.Values</code>, <code>.Release</code>, <code>.Chart</code>, <code>.Files</code>, <code>.Capabilities</code>, and <code>.Template</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Hooks render at the same time as other templates and share the same context. Use <code>.Values.db.password</code> for migration hooks, <code>.Release.Name</code> for hook resource naming, <code>.Files.Get</code> for SQL migration scripts embedded in the chart.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q15</span><div class="eq-question">What is the difference between hook weight -5 and +5?</div><details><summary>Answer &amp; Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>-5 runs FIRST.</strong> Lower weights execute before higher weights. Default is 0. Negative = early (backups, pre-checks). Positive = later (notifications, post-processing). Same-weight hooks may run in any order.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Weights are strings sorted numerically: -10, -5, 0, +5, +10. Always use distinct weights when ordering matters. The exam may ask you to "ensure Job A runs before Job B" — give Job A a lower (more negative) weight than Job B.</p></div></details></div>
'''
    insert_before_qaclose(ch10_s, ch11_s, content, "Ch10: +5 Q&As")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
