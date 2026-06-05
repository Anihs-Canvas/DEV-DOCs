"""
Enrich helm.html chapters with missing CKA-pattern components:
- helm-exam-tip (TIP)
- helm-chapter-relevance (REL)
- visual-summary (VS)
- helm-exam-questions (PQ)
"""
import re

with open('helm.html', 'r', encoding='utf-8') as f:
    data = f.read()

print(f'Before: {len(data)} chars')

# Define enrichment content per chapter
# Each entry: (chapter_id, insert_before_pattern, html_to_insert, description)

insertions = []

# ═══ Ch3: Installing Your First Chart (missing TIP) ═══
insertions.append((
    'ch3',
    r'(id="ch3".*?</div>)\s*(<div class="section-block" id="s3-1")',
    '''
            <div class="helm-exam-tip">
                <h5>Installation Patterns Are on the Exam</h5>
                <p>Certification exams test your ability to install charts correctly. Master these patterns:</p>
                <ul>
                    <li><strong>Always name your releases</strong> &#x2014; <code>helm install my-release bitnami/nginx</code> (not auto-generated names)</li>
                    <li><strong>Understand --set vs -f</strong> &#x2014; <code>--set</code> for quick overrides, <code>-f values.yaml</code> for complete configurations</li>
                    <li><strong>Know the difference</strong> between <code>helm install</code> (new), <code>helm upgrade</code> (existing), and <code>helm upgrade --install</code> (either)</li>
                    <li><strong>--dry-run</strong> renders templates without applying &#x2014; ALWAYS use it before production deploys</li>
                </ul>
            </div>
''',
    'Ch3: TIP'
))

# ═══ Ch4: Chart Structure (missing TIP, PQ) ═══
insertions.append((
    'ch4',
    r'(id="ch4".*?</div>)\s*(<!-- .*?Section 4\.1)',
    '''
            <div class="helm-exam-tip">
                <h5>Chart Structure Is Foundational Knowledge</h5>
                <p>You MUST know every file and directory in a Helm chart. Exam scenarios include:</p>
                <ul>
                    <li><strong>Chart.yaml fields</strong> &#x2014; <code>apiVersion: v2</code>, <code>type: application|library</code>, <code>version</code> vs <code>appVersion</code></li>
                    <li><strong>templates/ directory</strong> &#x2014; All YAML files here are rendered through Go templates. <code>NOTES.txt</code> displays post-install messages.</li>
                    <li><strong>.helmignore</strong> &#x2014; Works like <code>.gitignore</code>. Excludes files from packaged chart (README, tests, etc.).</li>
                    <li><strong>values.yaml</strong> &#x2014; Default configuration. Overridden by <code>-f</code> or <code>--set</code> at install/upgrade time.</li>
                </ul>
            </div>
''',
    'Ch4: TIP'
))

# ═══ Ch5: Templating Fundamentals (missing REL, TIP, PQ) ═══
insertions.append((
    'ch5',
    r'(id="ch5".*?chapter-intro.*?</div>)',
    # Insert after chapter-intro
    r'\1' + '''
            <div class="learning-objectives"><h4>&#x1F3AF; What You'll Learn</h4><ul>
                <li>&#x2705; Master Go template syntax: {{ }}, pipelines, conditionals, loops</li>
                <li>&#x2705; Understand the built-in objects: .Values, .Release, .Chart, .Files, .Template</li>
                <li>&#x2705; Use template functions: default, quote, include, required, toYaml</li>
                <li>&#x2705; Template the anihpj deployment from scratch with real values</li>
            </ul></div>

            <div class="helm-chapter-relevance">
                <span class="relevance-label">&#x1F393; Helm Certification Relevance</span>
                <div class="relevance-domains">
                    <span class="helm-domain-badge">Go Templates</span>
                    <span class="helm-domain-badge">Built-in Objects</span>
                    <span class="helm-domain-badge">Template Functions</span>
                </div>
            </div>

            <div class="helm-exam-tip">
                <h5>Templating Is the #1 Exam Topic</h5>
                <p>Expect at least 30% of the exam to involve writing or debugging templates. Key areas:</p>
                <ul>
                    <li><strong>{{ .Values.key }}</strong> &#x2014; Always use dot notation. Missing values cause nil pointer errors; use <code>default</code> as fallback.</li>
                    <li><strong>Whitespace control</strong> &#x2014; <code>{{- }}</code> trims left whitespace, <code>{{ -}}</code> trims right. Critical for valid YAML.</li>
                    <li><strong>Named templates</strong> &#x2014; <code>{{ define }}</code> + <code>{{ include }}</code> for reusable snippets in _helpers.tpl.</li>
                </ul>
            </div>
''',
    'Ch5: LO+REL+TIP'
))

# ═══ Ch6: Built-in Objects (missing REL, TIP, VS) ═══
insertions.append((
    'ch6',
    r'(id="ch6".*?chapter-intro.*?</div>)',
    r'\1' + '''
            <div class="learning-objectives"><h4>&#x1F3AF; What You'll Learn</h4><ul>
                <li>&#x2705; Master .Release object fields (Name, Namespace, Revision, IsInstall, IsUpgrade)</li>
                <li>&#x2705; Use .Chart for metadata-driven templates</li>
                <li>&#x2705; Access .Files for ConfigMap/file injection</li>
                <li>&#x2705; Apply template functions: default, required, toYaml, include</li>
            </ul></div>

            <div class="helm-chapter-relevance">
                <span class="relevance-label">&#x1F393; Helm Certification Relevance</span>
                <div class="relevance-domains">
                    <span class="helm-domain-badge">Built-in Objects</span>
                    <span class="helm-domain-badge">Template Functions</span>
                    <span class="helm-domain-badge">.Files Access</span>
                </div>
            </div>

            <div class="helm-exam-tip">
                <h5>Built-in Objects Appear in Every Template</h5>
                <p>You will use these objects in every chart you build. Memorize the key fields:</p>
                <ul>
                    <li><strong>.Release.Name</strong> &#x2014; The release name. Use it in labels to identify which release owns a resource.</li>
                    <li><strong>.Release.Namespace</strong> &#x2014; Where the release is installed. Critical for cross-namespace references.</li>
                    <li><strong>.Chart.Version</strong> &#x2014; Your chart's version from Chart.yaml. Useful for labeling resources.</li>
                    <li><strong>.Files.Get</strong> &#x2014; Read file contents into ConfigMaps. Use <code>{{ .Files.Get \"config.json\" }}</code>.</li>
                </ul>
            </div>
''',
    'Ch6: LO+REL+TIP'
))

# ═══ Ch7: Dependencies (missing REL, TIP, VS, PQ) ═══
insertions.append((
    'ch7',
    r'(id="ch7".*?chapter-intro.*?</div>)',
    r'\1' + '''
            <div class="learning-objectives"><h4>&#x1F3AF; What You'll Learn</h4><ul>
                <li>&#x2705; Declare chart dependencies in Chart.yaml</li>
                <li>&#x2705; Understand condition and tags for optional dependencies</li>
                <li>&#x2705; Use subcharts and access their values</li>
                <li>&#x2705; Package and distribute charts with dependencies</li>
            </ul></div>

            <div class="helm-chapter-relevance">
                <span class="relevance-label">&#x1F393; Helm Certification Relevance</span>
                <div class="relevance-domains">
                    <span class="helm-domain-badge">Dependencies</span>
                    <span class="helm-domain-badge">Subcharts</span>
                    <span class="helm-domain-badge">Chart.yaml</span>
                </div>
            </div>

            <div class="helm-exam-tip">
                <h5>Dependency Management Is Production-Critical</h5>
                <p>Real applications always have dependencies (database, cache, queue). Exam scenarios:</p>
                <ul>
                    <li><strong>Chart.yaml dependencies</strong> &#x2014; Declared under <code>dependencies:</code> with name, version, repository</li>
                    <li><strong>helm dependency update</strong> &#x2014; Downloads dependencies into charts/ subdirectory. Creates Chart.lock.</li>
                    <li><strong>Conditional deps</strong> &#x2014; <code>condition: postgresql.enabled</code> lets users opt-in/out of dependencies</li>
                    <li><strong>Value scoping</strong> &#x2014; Subchart values go under the dependency name: <code>postgresql.auth.database</code></li>
                </ul>
            </div>
''',
    'Ch7: LO+REL+TIP'
))

# ═══ Ch8: Hooks & Lifecycle (missing REL, TIP) ═══
insertions.append((
    'ch8',
    r'(id="ch8".*?chapter-intro.*?</div>)',
    r'\1' + '''
            <div class="learning-objectives"><h4>&#x1F3AF; What You'll Learn</h4><ul>
                <li>&#x2705; Use Helm hooks for pre/post-install, upgrade, delete operations</li>
                <li>&#x2705; Understand hook weights and deletion policies</li>
                <li>&#x2705; Create database migration hooks for anihpj</li>
            </ul></div>

            <div class="helm-chapter-relevance">
                <span class="relevance-label">&#x1F393; Helm Certification Relevance</span>
                <div class="relevance-domains">
                    <span class="helm-domain-badge">Hooks</span>
                    <span class="helm-domain-badge">Lifecycle Management</span>
                    <span class="helm-domain-badge">Job Resources</span>
                </div>
            </div>

            <div class="helm-exam-tip">
                <h5>Hooks Are the Answer to Complex Deployments</h5>
                <p>When install order matters (DB migrations before app start), hooks are the solution:</p>
                <ul>
                    <li><strong>Hook types:</strong> pre-install, post-install, pre-upgrade, post-upgrade, pre-delete, post-delete, test</li>
                    <li><strong>Weights</strong> &#x2014; Lower numbers execute first. DB migration = -5, data seed = -3, app deploy = 0.</li>
                    <li><strong>Deletion policies:</strong> <code>before-hook-creation</code> (default), <code>hook-succeeded</code>, <code>hook-failed</code></li>
                </ul>
            </div>
''',
    'Ch8: LO+REL+TIP'
))

# Now apply all insertions
for ch_id, pattern, replacement, desc in insertions:
    match = re.search(pattern, data, re.DOTALL)
    if match:
        # Determine if replacement is a regex substitution or literal
        if replacement.startswith(r'\1'):
            # It's a substitution using captured group
            new_text = re.sub(pattern, replacement, data[match.start():match.end()], flags=re.DOTALL)
            data = data[:match.start()] + new_text + data[match.end():]
        else:
            # It's a replacement of the captured groups
            new_text = re.sub(pattern, replacement, data[match.start():match.end()], flags=re.DOTALL)
            data = data[:match.start()] + new_text + data[match.end():]
        print(f'{desc}: OK')
    else:
        print(f'{desc}: PATTERN NOT FOUND - {ch_id}')

with open('helm.html', 'w', encoding='utf-8') as f:
    f.write(data)

print(f'After: {len(data)} chars')
print('Done!')
