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
# CHAPTER 1: Add the Shipping Port / Container analogy the user requested
# ============================================================
ch1_s = chapter_starts.get(1, -1)
ch2_s = chapter_starts.get(2, -1)
if ch1_s > 0 and ch2_s > ch1_s:
    content = '''
                <div class="section-block">
                    <h4>1.8 The Shipping Port Analogy — Understanding Helm Through Physical Metaphors</h4>
                    <p>Kubernetes concepts are abstract. Physical analogies make them intuitive. The shipping port analogy has become the standard way to explain how Helm, Kubernetes, and containers work together — because it maps perfectly to real-world logistics.</p>
                    <div class="diagram-container">
                        <div class="diagram-title">The Complete Shipping Port Analogy</div>
<pre>
THE SHIPPING PORT — HOW HELM, KUBERNETES & CONTAINERS WORK TOGETHER
═══════════════════════════════════════════════════════════════════════════

                        THE HARBOR (KUBERNETES CLUSTER)
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
    │  │ BERTH A     │    │ BERTH B     │    │ BERTH C     │              │
    │  │ (Namespace: │    │ (Namespace: │    │ (Namespace: │              │
    │  │  dev)       │    │  staging)   │    │  production)│              │
    │  │             │    │             │    │             │              │
    │  │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │              │
    │  │  │ SHIP  │  │    │  │ SHIP  │  │    │  │ SHIP  │  │              │
    │  │  │ anihpj│  │    │  │ anihpj│  │    │  │ anihpj│  │              │
    │  │  │ -dev  │  │    │  │ -stg  │  │    │  │ -prod │  │              │
    │  │  │ ███   │  │    │  │ ███   │  │    │  │ ███   │  │              │
    │  │  │ ███   │  │    │  │ ███   │  │    │  │ ███   │  │              │
    │  │  └───────┘  │    │  └───────┘  │    │  └───────┘  │              │
    │  └─────────────┘    └─────────────┘    └─────────────┘              │
    │                                                                      │
    │              ┌──────────────────────────┐                           │
    │              │  PORT AUTHORITY           │                           │
    │              │  (Kubernetes API Server)  │                           │
    │              │  - Validates manifests    │                           │
    │              │  - Enforces RBAC rules    │                           │
    │              │  - Schedules workloads    │                           │
    │              └──────────────────────────┘                           │
    └─────────────────────────────────────────────────────────────────────┘

ANALOGY MAPPINGS:
────────────────────────────────────────────────────────────────────────
CONCEPT              SHIPPING ANALOGY              WHAT IT DOES
────────────────────────────────────────────────────────────────────────
Helm CLI       =     Harbor Master                 Reads the manifest,
                                                    directs ships to berths

Chart          =     Shipping Manifest             Blueprint: what's in each
                 (Bill of Lading)                  container, how many, where

Release        =     Ship at a Berth               A running instance of the
                 (anihpj-dev at Berth A)           application

Values         =     Cargo Instructions            What goes IN the containers
                 (replicaCount, image tag)         (how many crates, which version)

Namespace      =     Berth / Dock                  Isolated parking spot for ships
                 (Berth A = dev namespace)

Repository     =     Warehouse / Depot             Where manifests (charts) are
                 (Artifact Hub)                    stored and retrieved from

K8s API Server =     Port Authority                Validates, authorizes, schedules
                                                    all port activities

kubelet        =     Dock Worker                   Loads/unloads containers at berth

Container      =     Shipping Container            Standardized box holding cargo
                 (Docker container)                (your application code)

Pod            =     Set of Containers              One or more containers that
                 on a Pallet                       travel and dock together

Scheduler      =     Berth Assignment Office       Decides which berth (node)
                                                    a ship goes to

etcd           =     Port Log Book                 Records EVERYTHING that happens
                 (the ledger)                      in the port — immutable records

Service        =     Ship-to-Ship Radio            Enables communication between
                 (internal comms)                  ships at different berths

Ingress        =     Customs Gate                  The entry point for external
                 (external access)                 traffic into the port

ConfigMap      =     Ship Configuration Sheet      Non-sensitive config data
                 (posted on the bridge)

Secret         =     Sealed Envelope               Sensitive data (passwords, keys)
                 (for captain's eyes only)

HPA            =     Automatic Crane               Scales containers up/down based
                 (load-based scaling)              on cargo demand (CPU/memory)

Rollback       =     Emergency Return to Port      Ship goes back to previous
                 (revert to last good state)       successful manifest version
</pre>
                    </div>
                    <div class="card-grid two-col">
                        <div class="info-card"><div class="card-icon">⛵</div><h5>Why This Analogy Works</h5><p>Just as a harbor master doesn't own the ships but coordinates their movement, Helm doesn't run your app — it <strong>orchestrates deployment</strong>. The harbor master reads the manifest (Chart), checks with port authority (API server), and directs the ship to the correct berth (namespace). If something goes wrong, the harbor master can redirect the ship (rollback) to a previous safe position.</p></div>
                        <div class="info-card"><div class="card-icon">🧠</div><h5>How to Use This for the Exam</h5><p>When you encounter abstract Helm concepts, mentally map them to the shipping analogy. "Install a chart in a namespace" becomes "direct a ship to a berth using its manifest." "Rollback a release" becomes "return a ship to its last known good position." This makes multi-tenancy, release management, and RBAC intuitive.</p></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam Mental Model:</strong> Every Helm exam question can be reframed in shipping terms. "Install chart X with values Y in namespace Z" = "Direct ship X carrying cargo Y to berth Z." This model is especially helpful for understanding WHY namespaces matter (different berths, different rules) and WHY rollbacks work (the port log book records every ship movement).</div></div>
                </div>
'''
    insert_before_qa(ch1_s, ch2_s, content, "Ch1: Shipping Port Analogy")

# ============================================================
# CHAPTER 2: Add CLI workflow patterns, troubleshooting installs
# ============================================================
ch2_s = chapter_starts.get(2, -1)
ch3_s = chapter_starts.get(3, -1)
if ch2_s > 0 and ch3_s > ch2_s:
    content = '''
                <div class="section-block">
                    <h4>2.10 Common Installation Issues & Solutions</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Issue</th><th>Symptom</th><th>Root Cause</th><th>Fix</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Wrong K8s context</strong></td><td><code>helm list</code> shows wrong releases</td><td>KUBECONFIG points to wrong cluster</td><td><code>kubectl config current-context</code> then <code>kubectl config use-context CORRECT</code></td></tr>
                            <tr><td><strong>No cluster connection</strong></td><td><code>Unable to connect to the server</code></td><td>Cluster unreachable or kubeconfig expired</td><td><code>kubectl cluster-info</code> to verify; refresh credentials</td></tr>
                            <tr><td><strong>Old Helm version</strong></td><td><code>Error: unknown flag</code></td><td>Using Helm 2 binary with Helm 3 commands</td><td><code>helm version</code> — should show v3.x or v4.x</td></tr>
                            <tr><td><strong>PATH issues</strong></td><td><code>helm: command not found</code></td><td>Helm binary not in PATH</td><td><code>export PATH=$PATH:/usr/local/bin</code> or move binary</td></tr>
                            <tr><td><strong>Plugin conflicts</strong></td><td>Unexpected behavior after plugin install</td><td>Plugin overrides core functionality</td><td><code>helm plugin list</code>; <code>helm plugin uninstall NAME</code></td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>2.11 First 5 Minutes After Installation — Verification Checklist</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>Verify Binary</h5><pre>
helm version              # Should show: version.BuildInfo{Version:"v3.x"}
helm version --short      # Compact output: v3.16.0
which helm                # Confirm binary location
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>Verify Cluster Connectivity</h5><pre>
helm list -A              # List all releases (should work, maybe empty)
kubectl cluster-info      # Verify K8s cluster is reachable
kubectl get nodes         # Confirm nodes are healthy
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Add Essential Repositories</h5><pre>
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo bitnami/nginx  # Test repo access
</pre></div></div>
                        <div class="ps-step"><div class="ps-num">4</div><div class="ps-content"><h5>Test a Quick Deployment</h5><pre>
helm install test-nginx bitnami/nginx --wait --timeout 2m
helm test test-nginx
helm uninstall test-nginx
# All should complete without errors
</pre></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch2_s, ch3_s, content, "Ch2: Troubleshooting & Verification")

# ============================================================
# CHAPTER 5: Add release inspection patterns, get command deep dive
# ============================================================
ch5_s = chapter_starts.get(5, -1)
ch6_s = chapter_starts.get(6, -1)
if ch5_s > 0 and ch6_s > ch5_s:
    content = '''
                <div class="section-block">
                    <h4>5.13 The helm get Command Family — Complete Reference</h4>
                    <p><code>helm get</code> is actually a family of subcommands that retrieve different aspects of a release. Knowing which subcommand to use for each scenario is essential on the exam.</p>
                    <div class="card-grid three-col">
                        <div class="info-card"><div class="card-icon">📋</div><h5>helm get manifest</h5><p>Returns the FULL rendered Kubernetes YAML that was applied to the cluster. This is the complete set of resources Helm manages for this release.</p><pre>
helm get manifest myapp -n prod
# Shows ALL resources Helm deployed
# deployment, service, configmap, etc.
# Useful for: diffing, backups,
# debugging resource issues
</pre></div>
                        <div class="info-card"><div class="card-icon">⚙️</div><h5>helm get values</h5><p>Returns the values used for this release. <code>--all</code> shows computed values (merged with defaults). <code>--revision N</code> shows values from a specific revision.</p><pre>
helm get values myapp -n prod
# Shows USER-SUPPLIED values only

helm get values myapp -n prod --all
# Shows ALL computed values
# (user values + chart defaults merged)

helm get values myapp -n prod --revision 3
# Shows values from revision 3
</pre></div>
                        <div class="info-card"><div class="card-icon">📝</div><h5>helm get hooks</h5><p>Returns all hook resources for the release. Useful for debugging hook failures or verifying hook configurations.</p><pre>
helm get hooks myapp -n prod
# Shows hook resources:
# pre-install, post-upgrade, etc.

helm get notes myapp -n prod
# Shows NOTES.txt output
# (post-install message)

helm get all myapp -n prod
# Shows EVERYTHING combined
</pre></div>
                    </div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam Pattern:</strong> Questions that ask "what was deployed?" → <code>helm get manifest</code>. "What values were used?" → <code>helm get values --all</code>. "Why did the hook fail?" → <code>helm get hooks</code>. "What did the user see after install?" → <code>helm get notes</code>.</div></div>
                </div>
'''
    insert_before_qa(ch5_s, ch6_s, content, "Ch5: helm get Deep Dive")

# ============================================================
# CHAPTER 17: Add more domain-specific practice Q&A
# ============================================================
ch17_s = chapter_starts.get(17, -1)
ch18_s = chapter_starts.get(18, -1)
if ch17_s > 0 and ch18_s > ch17_s:
    content = '''
                <div class="section-block">
                    <h4>17.7 Production Readiness Questions</h4>
                </div>
                <div class="cka-exam-questions">
                    <div class="exam-question-item"><span class="eq-number">P1</span><div class="eq-question">Your chart deploys successfully in dev but fails in production with <code>Error: UPGRADE FAILED: rendered manifests contain a resource that already exists</code>. What's the most likely cause and fix?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The production namespace likely has pre-existing resources with the same names. Check what's already there with <code>kubectl get all -n production</code>. Either: (1) delete conflicting resources, (2) use a different release name, or (3) set <code>fullnameOverride</code> to avoid naming conflicts.</p></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Helm uses the release name + chart name to generate resource names via the <code>fullname</code> template in _helpers.tpl. If someone manually created resources or another release used the same naming pattern, conflicts occur. <code>fullnameOverride</code> in values.yaml lets you explicitly set the resource name prefix.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">P2</span><div class="eq-question">You need to deploy the same chart 5 times in the same namespace with different configurations. What's the best practice?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Use <strong>different release names</strong> with different values files. Each release name creates a separate Helm release with its own resources, history, and lifecycle.</p><pre>
helm install anihpj-api ./chart -f values-api.yaml -n services
helm install anihpj-worker ./chart -f values-worker.yaml -n services
helm install anihpj-scheduler ./chart -f values-scheduler.yaml -n services
# All in the same namespace, all from the same chart,
# but independent releases with different configs
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is the microservice deployment pattern. One chart, many releases. Each release gets its own Secret for history storage (<code>sh.helm.release.v1.RELEASE-NAME.vN</code>). They can be upgraded, rolled back, and uninstalled independently — even in the same namespace.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">P3</span><div class="eq-question"><code>helm list -n prod</code> shows a release in <code>pending-upgrade</code> state for 10 minutes. What happened and how do you fix it?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>The previous <code>helm upgrade</code> command was interrupted (Ctrl+C, network timeout, or terminal closed) before completing. Helm left a <code>pending-upgrade</code> Secret that blocks further operations. Find and delete it:</p><pre>
kubectl get secrets -n prod -l owner=helm,status=pending-upgrade
kubectl delete secret -n prod -l owner=helm,status=pending-upgrade
helm rollback RELEASE -n prod  # Return to last good state
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>When Helm starts an operation, it creates a "pending" Secret to lock the release. If the operation is interrupted, the lock persists. Deleting the pending Secret removes the lock, but the release may be in an inconsistent state — always rollback to be safe.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">P4</span><div class="eq-question">How do you identify which Kubernetes resources were created by which Helm release?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Helm automatically adds labels to all deployed resources. You can filter by these labels:</p><pre>
# Find all resources from a specific release:
kubectl get all -n prod -l app.kubernetes.io/instance=myapp

# Find all Helm-managed resources:
kubectl get all -A -l app.kubernetes.io/managed-by=Helm

# Find resources from a specific chart:
kubectl get all -A -l helm.sh/chart=anihpj-0.1.0
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>The standard labels (from _helpers.tpl) include: <code>app.kubernetes.io/instance</code> (release name), <code>app.kubernetes.io/managed-by: Helm</code>, <code>helm.sh/chart</code> (chart name + version). These are the "fingerprint" Helm leaves on every resource it manages. Use them to audit, filter, and debug.</p></div></details></div>
                    <div class="exam-question-item"><span class="eq-number">P5</span><div class="eq-question">Your organization requires all deployments to have specific security labels. Where should you add them — in each template file or somewhere centralized?</div><details><summary>Answer & Explanation</summary><div class="eq-answer"><span class="eq-answer-label">Answer</span><p>Add them to <strong>_helpers.tpl</strong> as a named template that ALL resource templates include. This way, changing the labels in one place updates all resources.</p><pre>
{{- define "anihpj.securityLabels" -}}
security.company.com/data-classification: {{ .Values.security.dataClass }}
security.company.com/compliance: sox-pci
security.company.com/team: {{ .Values.security.team | default "platform" }}
{{- end }}
# Then in every template:
metadata:
  labels:
    {{- include "anihpj.labels" . | nindent 4 }}
    {{- include "anihpj.securityLabels" . | nindent 4 }}
</pre></div><div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>Centralizing labels in _helpers.tpl is the DRY (Don't Repeat Yourself) pattern for Helm. This also makes it easy to add a Library Chart with standard labels that all your organization's charts can import.</p></div></details></div>
                </div>
'''
    insert_before_qa(ch17_s, ch18_s, content, "Ch17: Production Questions")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
