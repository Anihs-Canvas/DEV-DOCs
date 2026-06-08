import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ============================================================
# FIX: Broken appendix divs (same pattern as chapter divs)
# ============================================================
for app_id in ['appendix-a', 'appendix-b', 'appendix-c', 'appendix-d', 'appendix-e', 'appendix-f']:
    aid = 'id="{}"'.format(app_id)
    pos = html.find(aid)
    if pos < 0:
        continue
    # Check if preceded by <div
    pre = html[max(0, pos-30):pos]
    if '<div' in pre:
        continue
    # Find newline before id
    nl = html.rfind('\n', 0, pos)
    if nl < 0:
        continue
    indent = html[nl+1:pos]
    old = html[nl+1:pos+len(aid)+1]
    new = indent + '<div ' + aid + '>'
    html = html[:nl+1] + new + html[pos+len(aid)+1:]
    changes += 1
    print("Fixed: {} div".format(app_id))

# ============================================================
# NEW: Add Chapter 21 before Part 8 - Helm 4
# Insert between Ch20 Q&A end and Appendix A start
# ============================================================
# Find the end of Ch20's Q&A
ch20_id = html.find('id="ch20"')
appendix_a_id = html.find('id="appendix-a"')

if ch20_id > 0 and appendix_a_id > ch20_id:
    # Find the Q&A closing </div> before appendix-a
    insert_pos = html.rfind('</div>', 0, appendix_a_id)
    # Find the cka-exam-questions closing
    qa_close = html.rfind('class="cka-exam-questions"', 0, appendix_a_id)
    
    # We want to insert right before the appendix opening
    # Find the comment before appendix
    app_comment = html.rfind('<!--', 0, appendix_a_id)
    if app_comment > qa_close and 'APPENDIX' in html[app_comment:app_comment+50].upper():
        insert_pos = app_comment
    
    new_chapter = '''
                        <!-- ═══════════════════════════════════════════════════════════════ -->
            <!--            PART 8: HELM 4 — THE NEXT GENERATION                 -->
            <!-- ═══════════════════════════════════════════════════════════════ -->

            <!-- ─── Chapter 21: Helm 4 Overview & Migration ─── -->
            <div id="ch21">
                <div class="chapter-intro">
                    <h3>Chapter 21: Helm 4 Overview & Migration — What's New in the Next Generation</h3>
                    <p>Helm v4.0.0 was released in 2025, representing the most significant evolution since the Tiller removal in v3. It introduces WebAssembly plugins, server-side apply, OCI digest support, multi-document values, and a stable SDK API — while maintaining full backwards compatibility with v2 charts. This chapter covers everything you need to know about Helm 4 for certification and production use.</p>
                    <div class="chapter-meta">
                        <span class="meta-tag">🆕 Helm 4</span>
                        <span class="meta-tag">🔴 Advanced</span>
                        <span class="meta-tag">⏱️ ~1.5 hours</span>
                        <span class="meta-tag">🔄 Migration</span>
                    </div>
                </div>

                <div class="learning-objectives">
                    <h4>What You'll Learn</h4>
                    <ul>
                        <li>✅ Understand all Helm 4 breaking changes and how to adapt</li>
                        <li>✅ Master new features: Wasm plugins, server-side apply, OCI digests</li>
                        <li>✅ Know renamed/deprecated CLI flags and their replacements</li>
                        <li>✅ Understand Helm-Kubernetes version skew policy (n-3)</li>
                        <li>✅ Plan migration from Helm 3 to Helm 4</li>
                    </ul>
                </div>

                <div class="section-block">
                    <h4>21.1 Helm 4 — The Big Picture</h4>
                    <p>Helm 4 is a significant evolution from v3, introducing breaking changes, new architectural patterns, and enhanced functionality. It was compiled against Kubernetes 1.34 client APIs and supports <strong>n-3 version skew</strong> (compatible with K8s 1.34, 1.33, 1.32, and 1.31).</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm Version History & Evolution</div>
<pre>
HELM VERSION EVOLUTION
═══════════════════════════════════════════════════════════════

v1.0 (2016)     v2.0 (2016)       v3.0 (2019)        v4.0 (2025)
┌─────────┐     ┌──────────┐      ┌──────────┐       ┌──────────┐
│ Client- │     │ Client + │      │ Client   │       │ Client   │
│ Server  │────>│ Tiller   │─────>│ ONLY     │──────>│ + Wasm   │
│ (proto) │     │ (gRPC)   │      │ (REST)   │       │ Plugins  │
└─────────┘     └──────────┘      └──────────┘       └──────────┘
                                     │                    │
                                     │                    ├─ Server-Side Apply
                                     │                    ├─ OCI Digest Support
                                     │                    ├─ Multi-Doc Values
                                     │                    ├─ kstatus Watcher
                                     │                    ├─ Stable SDK API
                                     │                    └─ Custom Template Funcs
</pre>
                    </div>
                </div>

                <div class="section-block">
                    <h4>21.2 Breaking Changes — What You Must Know</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Breaking Change</th><th>Helm 3 Behavior</th><th>Helm 4 Behavior</th><th>Migration Action</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Post-Renderers as Plugins</strong></td><td><code>--post-renderer ./script.sh</code> (any executable)</td><td><code>--post-renderer PLUGIN_NAME</code> (plugin only)</td><td>Convert scripts to plugins; update CI/CD</td></tr>
                            <tr><td><strong>Registry Login</strong></td><td><code>helm registry login https://registry.io/repo</code> (full URL)</td><td><code>helm registry login registry.io</code> (domain only)</td><td>Remove path from login URLs</td></tr>
                            <tr><td><strong>Plugin System</strong></td><td>Executable-based plugins only</td><td>Optional WebAssembly (Wasm) runtime; 3 plugin types: CLI, getter, post-renderer</td><td>Existing plugins still work; explore Wasm for new plugins</td></tr>
                            <tr><td><strong>SDK API</strong></td><td>Unstable, frequent breaking changes</td><td>Stable API (breaking changes complete)</td><td>Update SDK imports; test thoroughly</td></tr>
                            <tr><td><strong>Charts v3</strong></td><td>Charts v2 (apiVersion: v2)</td><td>v2 charts unchanged; Charts v3 coming soon</td><td>No immediate action; plan for v3 features</td></tr>
                        </tbody>
                    </table></div>
                </div>

                <div class="section-block">
                    <h4>21.3 CLI Flag Changes — Renamed & Deprecated</h4>
                    <p>Several common flags have been renamed for clarity. The old flags still work but emit deprecation warnings.</p>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🔄</div><h5>Renamed Flags (old → new)</h5><pre>
--atomic    → --rollback-on-failure
--force     → --force-replace

# These are NOT removed yet, but
# emit deprecation warnings.
# Update your scripts and CI/CD.
</pre></div>
                        <div class="info-card"><div class="card-icon">🗑️</div><h5>Deprecated Flags (helm template only)</h5><pre>
--hide-notes
--render-subchart-notes

# These have no effect in Helm 4.
# Template output never includes
# NOTES.txt content.
# Will be removed in Helm 5.
</pre></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam & Certification:</strong> If the exam tests Helm 4, remember: <code>--rollback-on-failure</code> replaces <code>--atomic</code>. <code>--force-replace</code> replaces <code>--force</code>. Old flags still work but expect to see the new names in documentation and exam scenarios.</div></div>
                </div>

                <div class="section-block">
                    <h4>21.4 Major New Features</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🔌</div><h5>WebAssembly Plugin System</h5><p>Optional Wasm-based runtime for enhanced security and expanded capabilities. Three plugin types: CLI plugins, getter plugins, and post-renderer plugins. Existing plugins continue to work unchanged.</p><pre>
# CLI plugin (still works as before):
helm plugin install https://github.com/user/plugin

# Wasm plugin (new, optional):
helm plugin install ./myplugin.wasm
</pre></div>
                        <div class="info-card"><div class="card-icon">📋</div><h5>Server-Side Apply</h5><p>Helm 4 defaults to server-side apply for NEW releases. Upgrades follow the previous apply method (latching). Existing Helm 3 releases continue using client-side apply after upgrade.</p><pre>
# Force server-side apply:
helm upgrade --server-side NAME ./chart

# Force client-side apply:
helm upgrade --server-side=false NAME ./chart
</pre></div>
                    </div>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">🔐</div><h5>OCI Digest Support</h5><p>Install charts by SHA256 digest for supply chain security. Non-matching digests are rejected — preventing tampering.</p><pre>
# Install by digest (immutable):
helm install myapp \\
  oci://registry.io/charts/app@sha256:abc123...

# Pull by digest:
helm pull oci://registry.io/charts/app \\
  --version 1.0.0 --verify
</pre></div>
                        <div class="info-card"><div class="card-icon">📄</div><h5>Multi-Document Values</h5><p>Split complex values across multiple YAML documents in a single file. Perfect for environment-specific overrides with shared base config.</p><pre>
# values.yaml (multi-doc):
---
replicaCount: 3
image:
  repository: anihpj
---
# staging overrides:
replicaCount: 1
image:
  tag: latest
---
# production overrides:
replicaCount: 5
image:
  tag: v2.0.0
</pre></div>
                    </div>
                </div>

                <div class="section-block">
                    <h4>21.5 kstatus Integration — Better Resource Monitoring</h4>
                    <p>Helm 4 integrates with the Kubernetes <code>kstatus</code> library for more detailed, structured status reporting during installs and upgrades. This replaces the basic "is the pod running?" check with comprehensive resource status.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Helm 3 Status (basic)</h5>
<pre>
helm status myapp -n prod
NAME: myapp
STATUS: deployed
REVISION: 1
NOTES: ...
# That's it — very minimal info
</pre>
                        </div>
                        <div class="split-side">
                            <h5>Helm 4 kstatus (detailed)</h5>
<pre>
helm status myapp -n prod
NAME: myapp
STATUS: deployed (3/3 ready)
REVISION: 1
RESOURCES:
✓ Deployment/myapp  [3/3 replicas]
✓ Service/myapp     [ClusterIP: 10.0.1.5]
✓ ConfigMap/myapp   [configured]
⚠ Ingress/myapp     [reconciling]
# Per-resource status with details!
</pre>
                        </div>
                    </div>
                </div>

                <div class="section-block">
                    <h4>21.6 Custom Template Functions via Plugins</h4>
                    <p>Helm 4 lets you extend the template engine with your own functions through the plugin system. Organizations can add domain-specific template functions without modifying Helm itself.</p>
<pre>
# Define a custom function in a plugin:
# This function generates standardized resource names

# In your template:
metadata:
  name: {{ customName "deployment" .Release.Name .Chart.Name }}
  # customName is a plugin-provided function

# Plugin registration:
# helm plugin install ./org-template-functions.wasm
# Now all charts can use {{ customName }}, {{ orgLabel }}, etc.
</pre>
                    <div class="info-box tip"><h5>Use Cases</h5><ul><li>Organization-standard naming conventions (enforced centrally)</li><li>Security policy injection (add securityContext automatically)</li><li>Cloud-provider-specific helpers (AWS/GCP/Azure resource naming)</li><li>Compliance labeling (automatically add required labels)</li></ul></div>
                </div>

                <div class="section-block">
                    <h4>21.7 Helm-Kubernetes Version Skew Policy</h4>
                    <p>Helm 4 follows an <strong>n-3 version skew policy</strong>: it supports the Kubernetes version it was compiled against, plus the three previous minor versions.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>Helm Version</th><th>Compiled Against K8s</th><th>Supported K8s Versions</th></tr></thead>
                        <tbody>
                            <tr><td>4.2.x</td><td>1.35.x</td><td>1.35.x, 1.34.x, 1.33.x, 1.32.x</td></tr>
                            <tr><td>4.1.x</td><td>1.34.x</td><td>1.34.x, 1.33.x, 1.32.x, 1.31.x</td></tr>
                            <tr><td>4.0.x</td><td>1.34.x</td><td>1.34.x, 1.33.x, 1.32.x, 1.31.x</td></tr>
                        </tbody>
                    </table></div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Forward Compatibility:</strong> Helm does NOT guarantee forward compatibility. Do not use a Helm version compiled against K8s 1.34 with a K8s 1.36 cluster. Always ensure your Helm version's compiled K8s version is >= your cluster version.</div></div>
                </div>

                <div class="section-block">
                    <h4>21.8 Upgrading from Helm 3 to Helm 4</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Pre-Upgrade Testing</h5><p>Test ALL existing charts and releases with Helm 4 before upgrading production. Pay special attention to post-renderer integrations and CI/CD pipelines that use renamed flags.</p><pre>
# Test with Helm 4 binary:
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 | bash
helm4 lint ./all-charts --strict
helm4 template test ./chart --debug
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Update Scripts & CI/CD</h5><p>Replace renamed flags: <code>--atomic</code> → <code>--rollback-on-failure</code>, <code>--force</code> → <code>--force-replace</code>. Update post-renderer references from executable paths to plugin names. Fix registry login commands (remove URL paths).</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Verify Release Compatibility</h5><p>Helm 4 is backwards-compatible with all existing releases. Helm 3 releases continue working after upgrade. New releases will default to server-side apply; existing releases retain their previous apply method (latching behavior).</p></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Plugin Migration</h5><p>Existing plugins work without changes. Consider migrating security-sensitive plugins to Wasm for enhanced isolation. Test all three plugin types: CLI, getter, and post-renderer.</p></div></div>
                    </div>
                </div>

                <!-- ─── Chapter 21 Practice Questions ─── -->
                <div class="cka-exam-questions">
                    <div class="exam-question-item"><span class="eq-number">Q1</span><div class="eq-question">What is the biggest architectural change in Helm 4 compared to Helm 3?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The <strong>WebAssembly (Wasm) plugin system</strong> — enabling plugin types for CLI, getters, and post-renderers. Also: server-side apply defaults, OCI digest support, and a stable SDK API.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Unlike Helm 3's executable-only plugins, Helm 4 introduces an optional Wasm runtime that provides enhanced security isolation and expanded capabilities. Three plugin types are now supported, enabling deeper customization of Helm's core behavior.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q2</span><div class="eq-question">What replaces <code>--atomic</code> in Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><code>--rollback-on-failure</code>. <code>--atomic</code> still works but emits a deprecation warning. Similarly, <code>--force</code> is replaced by <code>--force-replace</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The rename improves clarity: <code>--rollback-on-failure</code> explicitly states what happens, while <code>--atomic</code> was ambiguous. Always use the new flag names in new scripts and CI/CD pipelines.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q3</span><div class="eq-question">How does Helm 4 handle post-renderers differently?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Post-renderers are now implemented as <strong>plugins</strong> (not arbitrary executables). You pass a plugin name instead of a script path: <code>--post-renderer myplugin</code>. This requires converting existing post-renderer scripts to plugins.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a breaking change. If you have a <code>kustomize-wrapper.sh</code> post-renderer, you need to package it as a plugin. Helm 4 also introduces three hook post-render strategies: combined (default), separate, and nohooks — controlling whether hooks are sent to post-renderers.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q4</span><div class="eq-question">What is the Helm 4 version skew policy?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p><strong>n-3</strong>: Helm supports the Kubernetes minor version it was compiled against, plus the three previous minor versions. Example: Helm 4.2.x (compiled against K8s 1.35) supports K8s 1.35, 1.34, 1.33, and 1.32.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Previously, Helm 3 had an n-1 policy. Helm 4 extends this to n-3, giving you more flexibility. However, forward compatibility is NOT guaranteed — don't use an older Helm with a newer K8s cluster.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">Q5</span><div class="eq-question">How does server-side apply work in Helm 4?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Helm 4 defaults to server-side apply for NEW releases. Existing releases from Helm 3 continue using client-side apply (latching behavior). You can override with <code>--server-side</code> or <code>--server-side=false</code>.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Server-side apply uses Kubernetes' native field management, providing better conflict detection when multiple tools manage the same resources. The latching behavior ensures existing Helm 3 releases don't suddenly change behavior after upgrading the Helm binary.</p></div></details></div>
                </div>

                <!-- ─── Visual Summary: Chapter 21 ─── -->
                <div class="visual-summary"><div class="vs-grid">
                    <div class="vs-item"><span class="vs-icon">🆕</span><span class="vs-label">Helm 4</span><span class="vs-detail">Released 2025</span></div>
                    <div class="vs-item"><span class="vs-icon">🔌</span><span class="vs-label">Wasm Plugins</span><span class="vs-detail">3 plugin types</span></div>
                    <div class="vs-item"><span class="vs-icon">📋</span><span class="vs-label">Server-Side Apply</span><span class="vs-detail">Default for new releases</span></div>
                    <div class="vs-item"><span class="vs-icon">🔐</span><span class="vs-label">OCI Digests</span><span class="vs-detail">Immutable installs</span></div>
                    <div class="vs-item"><span class="vs-icon">🔄</span><span class="vs-label">n-3 Skew</span><span class="vs-detail">Broader K8s support</span></div>
                    <div class="vs-item"><span class="vs-icon">📊</span><span class="vs-label">kstatus</span><span class="vs-detail">Detailed monitoring</span></div>
                </div></div>
            </div>
'''
    html = html[:insert_pos] + new_chapter + '\n' + html[insert_pos:]
    changes += 1
    print("Added: Chapter 21 - Helm 4 Overview")

# ============================================================
# ADD: Sidebar entry for Chapter 21
# ============================================================
sidebar_pos = html.find('<!-- Chapter 20 in sidebar -->')
if sidebar_pos < 0:
    sidebar_pos = html.find('Chapter 20</a>')
if sidebar_pos > 0:
    # Find the end of the Chapter 20 sidebar entry
    li_close = html.find('</li>', sidebar_pos)
    if li_close > 0:
        # Find the next </li> which closes the Part 7 group
        next_li = html.find('</li>', li_close + 5)
        # Insert new sidebar entry for Part 8 + Chapter 21
        sidebar_entry = '''
                                <li><span class="toc-part" onclick="toggleSections('part8')">▼ PART 8: HELM 4 — THE NEXT GENERATION</span>
                                    <ul id="part8">
                                        <li><a href="#ch21">Chapter 21: Helm 4 Overview & Migration</a>
                                            <ul>
                                                <li><a href="#ch21">21.1 The Big Picture</a></li>
                                                <li><a href="#ch21">21.2 Breaking Changes</a></li>
                                                <li><a href="#ch21">21.3 CLI Flag Changes</a></li>
                                                <li><a href="#ch21">21.4 Major New Features</a></li>
                                                <li><a href="#ch21">21.5 kstatus Integration</a></li>
                                                <li><a href="#ch21">21.6 Custom Template Functions</a></li>
                                                <li><a href="#ch21">21.7 Version Skew Policy</a></li>
                                                <li><a href="#ch21">21.8 Upgrading Helm 3 → 4</a></li>
                                            </ul>
                                        </li>
                                    </ul>
                                </li>
'''
        html = html[:next_li+5] + sidebar_entry + html[next_li+5:]
        changes += 1
        print("Added: Sidebar entry for Chapter 21")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal changes: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
