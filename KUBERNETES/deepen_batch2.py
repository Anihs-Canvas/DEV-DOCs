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
# CHAPTER 11: Testing Deep Dive - The role of tests in the Helm workflow
# ============================================================
ch11_s = chapter_starts.get(11, -1)
ch12_s = chapter_starts.get(12, -1)
if ch11_s > 0 and ch12_s > ch11_s:
    content = '''
                <div class="section-block">
                    <h4>11.11 The Testing Pyramid for Helm Charts</h4>
                    <p>Just like software testing, Helm chart validation has layers. Each layer catches different types of errors at different speeds. Running only one layer leaves gaps.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm Testing Pyramid</div>
<pre>
HELM TESTING PYRAMID (Fastest → Most Thorough)
═══════════════════════════════════════════════════════════════

                    ┌─────┐
                    │ E2E │  helm test (real cluster, real data)
                    │     │  SLOW (30-120s) - Catches: integration, connectivity
                    ├─────┤
                    │DRY  │  helm install --dry-run --debug
                    │RUN  │  MEDIUM (3-5s) - Catches: API validation, K8s errors
                    ├─────┤
                    │TMPL │  helm template --debug
                    │     │  FAST (1-2s) - Catches: render errors, nil pointers
                    ├─────┤
                    │LINT │  helm lint --strict
                    │     │  INSTANT (<1s) - Catches: YAML syntax, missing fields
                    └─────┘

EVERY CI PIPELINE SHOULD RUN ALL FOUR LAYERS IN ORDER.
If lint fails, stop — don't waste time on template/dry-run.
If template fails, stop — don't waste time on dry-run.
If dry-run fails, stop — don't waste time on helm test.
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>11.12 Understanding helm test Internals</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Test Discovery</h5><p>Helm looks for resources annotated with <code>helm.sh/hook: test</code> in the release's stored manifest. These were deployed during install/upgrade but are NOT normal resources — they're hook resources.</p></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Test Execution</h5><p>Tests run in <strong>weight order</strong> (like other hooks). Each test pod/job is created, and Helm waits for it to complete successfully (exit code 0). Tests can be pods (run once) or jobs (restartPolicy: Never).</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Result Collection</h5><p>Helm collects exit codes and logs from each test resource. <code>helm test --logs</code> prints logs even for successful tests. Failed tests show the error output automatically.</p></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Test Cleanup</h5><p>Tests with <code>helm.sh/hook-delete-policy: hook-succeeded</code> are deleted after passing. Failed tests are preserved for debugging. You can re-run tests anytime with <code>helm test</code> — they execute against the current release state.</p></div></div>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Test Gotcha:</strong> Tests run against the LIVE cluster, not a sandbox. A bad test can corrupt data. Always ensure test pods have appropriate RBAC and resource limits. Test pods should be read-only (no mutations) unless explicitly testing write operations.</div></div>
                </div>
'''
    insert_before_qa(ch11_s, ch12_s, content, "Ch11: Testing Pyramid")

# ============================================================
# CHAPTER 12: Repository deep dive - HTTP vs OCI architecture
# ============================================================
ch12_s = chapter_starts.get(12, -1)
ch13_s = chapter_starts.get(13, -1)
if ch12_s > 0 and ch13_s > ch12_s:
    content = '''
                <div class="section-block">
                    <h4>12.13 Traditional HTTP vs OCI Repository - Architecture Comparison</h4>
                    <p>Understanding the underlying architecture helps you choose the right repository type and debug connection issues.</p>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Traditional HTTP Repository</h5>
<pre>
ARCHITECTURE:
+--------+     +------------+     +----------+
| Helm   |────>| HTTP Server|────>| Storage  |
| CLI    |     | (nginx, S3)|     | (.tgz    |
+--------+     +------------+     |  files)  |
                                  +----------+

KEY FILE: index.yaml
- Lists all charts + versions
- Contains URLs + SHA256 digests
- Downloaded on helm repo update
- Cached locally at ~/.cache/helm

COMMANDS:
helm repo add NAME URL
helm repo update
helm search repo NAME
helm pull REPO/CHART --version X
</pre>
                        </div>
                        <div class="split-side">
                            <h5>OCI-Based Repository</h5>
<pre>
ARCHITECTURE:
+--------+     +------------+     +----------+
| Helm   |────>| OCI        |────>| Blob     |
| CLI    |     | Registry   |     | Storage  |
+--------+     | (Docker,   |     +----------+
               | Harbor,    |
               | ECR, GCR)  |
               +------------+

KEY CONCEPT: Charts as OCI artifacts
- Charts stored as OCI manifests
- Tags used for versioning
- Same auth as Docker (docker login)
- No index.yaml - registry API for listing

COMMANDS:
helm registry login REGISTRY
helm push FILE.tgz oci://REGISTRY/REPO
helm pull oci://REGISTRY/REPO/CHART --version X
helm show chart oci://REGISTRY/REPO/CHART --version X
</pre>
                        </div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>OCI is the Future:</strong> The Helm project recommends OCI for new chart repositories. OCI registries provide better security (built-in auth, RBAC), immutability (digest-based), and integration with existing container infrastructure. Traditional HTTP repos are still supported but no longer the recommended approach.</div></div>
                </div>
'''
    insert_before_qa(ch12_s, ch13_s, content, "Ch12: HTTP vs OCI Architecture")

# ============================================================
# CHAPTER 16: More hands-on lab scenarios for exam prep
# ============================================================
ch16_s = chapter_starts.get(16, -1)
ch17_s = chapter_starts.get(17, -1)
if ch16_s > 0 and ch17_s > ch16_s:
    content = '''
                <div class="section-block">
                    <h4>16.10 Lab 10: Full Certification Simulation (45 min)</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Task 1-3: Basic Operations (10 min)</h5><pre>
# Task 1: Create a chart named "webapp" with helm create
# Task 2: Install it as "webapp-dev" in namespace "dev"
# Task 3: Upgrade it to 3 replicas
helm create webapp
helm install webapp-dev ./webapp -n dev --create-namespace
helm upgrade webapp-dev ./webapp --set replicaCount=3 -n dev
helm history webapp-dev -n dev  # Verify revision 2
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Task 4-5: Values Management (10 min)</h5><pre>
# Task 4: Create values-staging.yaml with replicaCount=2, service.type=NodePort
# Task 5: Install as "webapp-staging" in "staging" using that values file
cat > values-staging.yaml <<EOF
replicaCount: 2
service:
  type: NodePort
EOF
helm install webapp-staging ./webapp -f values-staging.yaml -n staging --create-namespace
helm get values webapp-staging -n staging  # Verify values
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Task 6-7: Hooks & Tests (10 min)</h5><pre>
# Task 6: Add a pre-install hook (Job) that runs "echo Pre-install check"
# Task 7: Add a test pod that runs "curl http://webapp-dev.dev.svc"
# Create templates/hooks/pre-install.yaml and templates/tests/test-conn.yaml
# Then: helm upgrade webapp-dev ./webapp -n dev
# Then: helm test webapp-dev -n dev --logs
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Task 8-10: Advanced Operations (15 min)</h5><pre>
# Task 8: Rollback webapp-staging to revision 1
helm rollback webapp-staging 1 -n staging

# Task 9: Package the chart and push to OCI registry
helm package ./webapp
helm push webapp-0.1.0.tgz oci://localhost:5000/charts

# Task 10: Uninstall all releases and verify cleanup
helm uninstall webapp-dev -n dev
helm uninstall webapp-staging -n staging
helm list -A  # Should be empty (for webapp)
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch16_s, ch17_s, content, "Ch16: Certification Simulation Lab")

# ============================================================
# CHAPTER 18: Operations at Scale - Storage backends, performance, monitoring
# ============================================================
ch18_s = chapter_starts.get(18, -1)
ch19_s = chapter_starts.get(19, -1)
if ch18_s > 0 and ch19_s > ch18_s:
    content = '''
                <div class="section-block">
                    <h4>18.7 Release Storage Backends - Secrets vs ConfigMaps vs SQL</h4>
                    <p>Helm 3 supports multiple storage backends for release information. The choice impacts performance, scalability, and disaster recovery capability.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>Backend</th><th>Max Size</th><th>Performance</th><th>Best For</th><th>Recovery</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Secret (default)</strong></td><td>1 MB</td><td>Fast (etcd-native)</td><td>Normal charts (&lt;1MB rendered)</td><td>kubectl backup</td></tr>
                            <tr><td><strong>ConfigMap</strong></td><td>1 MB</td><td>Fast (etcd-native)</td><td>Legacy (Helm 2 compat)</td><td>kubectl backup</td></tr>
                            <tr><td><strong>SQL (PostgreSQL, MySQL)</strong></td><td>Unlimited</td><td>Moderate (DB query)</td><td>Very large manifests (&gt;1MB)</td><td>DB backup/restore</td></tr>
                        </tbody>
                    </table></div>
                    <div class="diagram-container">
                        <div class="diagram-title">Storage Backend Decision Flow</div>
<pre>
CHOOSING A STORAGE BACKEND:
═══════════════════════════════════════════════════════════════

Is your rendered manifest < 1MB?
  ├── YES → Use Secrets (default). Nothing to configure.
  │         helm install NAME ./chart  (uses Secrets)
  │
  └── NO → Use SQL backend.
            Set HELM_DRIVER=sql
            Configure HELM_DRIVER_SQL_CONNECTION_STRING
            helm install NAME ./chart --storage-driver sql

SQL CONNECTION STRING FORMAT:
PostgreSQL: postgresql://user:pass@host:5432/helm?sslmode=disable
MySQL:      mysql://user:pass@tcp(host:3306)/helm

SETUP:
export HELM_DRIVER=sql
export HELM_DRIVER_SQL_CONNECTION_STRING="postgresql://helm:pass@db:5432/helm"
helm install NAME ./chart  # Auto-uses SQL
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>18.8 Helm Performance Optimization</h4>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">⚡</div><h5>Install/Upgrade Speed</h5><ul><li><strong>--wait vs --no-hooks:</strong> --wait blocks until pods are ready. Skip for CI testing with --no-hooks</li><li><strong>--timeout:</strong> Lower timeout means faster failure detection. Default 5m is often too long for CI</li><li><strong>Parallel installs:</strong> Different namespaces can install in parallel safely</li><li><strong>Chart size:</strong> Large templates/ directory slows rendering. Use .helmignore to exclude unnecessary files</li></ul></div>
                        <div class="info-card"><div class="card-icon">📊</div><h5>Release List Performance</h5><ul><li><strong>helm list -A:</strong> Scans ALL namespaces. Slow with 1000+ releases. Use <code>-n NS</code> to scope</li><li><strong>Release Secrets:</strong> Each revision is a Secret. Set <code>--history-max 5</code> to limit storage</li><li><strong>Label filtering:</strong> <code>kubectl get secrets -l owner=helm,name=myapp</code> is faster than helm list</li><li><strong>SQL backend:</strong> Scales better than Secrets for 1000+ releases</li></ul></div>
                    </div>
                </div>
'''
    insert_before_qa(ch18_s, ch19_s, content, "Ch18: Storage Backends & Performance")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
