# Generates Part 2 Categories 2 & 3 and appends to file
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find insertion point - after last ts-issue before </main> or <script>
insert_marker = '</div>\n</main>'
if insert_marker not in content:
    # Footer was lost, find where to insert
    # Look for the closing of ST10's ts-advice followed by closing divs
    marker = 'Tests ability to diagnose and fix — not just identify.</div>\n    </div>'
    if marker in content:
        pos = content.find(marker) + len(marker)
    else:
        print("ERROR: Cannot find insertion point")
        exit(1)
else:
    pos = content.find(insert_marker)

# Build Part 2 Cat 2 & 3 HTML
ts_html = '''

    <!-- ═══ TR11-TR15: Pod Startup Issues ═══ -->
    <div class="ts-section-header"><h3>📌 TR11–TR15: Pod Startup Failures</h3></div>

    <div class="ts-issue" id="ts-tr11"><div class="ts-issue-header"><div class="ts-issue-num">TR11</div><div class="ts-issue-header-content"><div class="ts-category">🔧 CATEGORY 2: TROUBLESHOOTING — Issue TR11</div><div class="ts-title">Pod Stuck in ImagePullBackOff — Can't Pull Image</div><p class="ts-symptom"><strong>🔍 Symptom:</strong> Pod shows STATUS: ImagePullBackOff or ErrImagePull. <code>kubectl describe pod</code> shows "Failed to pull image" or "unauthorized." Pod never starts.</p></div></div>
        <pre style="color:var(--accent-orange);font-size:12px;margin:8px 0;">
<span class="ts-cmd">  kubectl describe pod anihpj-web-x</span>
<span class="ts-out">  Events:</span>
<span class="ts-err">    Warning  Failed      Failed to pull image "anihpj/web:v2":
      pull access denied for anihpj/web, repository does not 
      exist or may require 'docker login'</span></pre>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>
                <li><span class="cause-likely">Image tag doesn't exist:</span> Typo in tag (v2 vs 2.0). Check registry: <code>docker pull &lt;image&gt;</code>.</li>
                <li><span class="cause-likely">Private registry without imagePullSecrets:</span> <code>kubectl create secret docker-registry regcred --docker-server=&lt;url&gt; --docker-username=&lt;user&gt; --docker-password=&lt;pw&gt;</code>.</li>
                <li><span class="cause-likely">Image registry unreachable:</span> Node can't reach registry. <code>curl https://registry.example.com/v2/</code> from node.</li>
                <li><span class="cause-likely">Network policy blocking egress to registry:</span> Pod/node can't reach external registry.</li>
                <li><span class="cause-likely">Docker Hub rate limiting:</span> Anonymous pulls limited to 100/6h. Authenticate to get 200/6h.</li>
            </ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>
                <li><span class="cause-less-likely">imagePullPolicy: Never but image not locally cached on node</span></li>
                <li><span class="cause-less-likely">Proxy settings not configured for containerd to reach registry</span></li>
                <li><span class="cause-less-likely">Registry certificate expired or self-signed not trusted</span></li>
                <li><span class="cause-less-likely">Image too large — pull timeout (default 2 min)</span></li>
                <li><span class="cause-less-likely">Disk full on node — can't store pulled image layers</span></li>
            </ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>
                <li><span class="cause-new-cluster">No imagePullSecrets configured in ServiceAccount</span></li>
                <li><span class="cause-new-cluster">containerd configured with wrong registry mirrors</span></li>
                <li><span class="cause-new-cluster">Node has no internet access — air-gapped environment</span></li>
                <li><span class="cause-new-cluster">Default imagePullPolicy is Always but registry is rate-limiting</span></li>
                <li><span class="cause-new-cluster">Image uses manifest list but node architecture not supported (ARM vs AMD64)</span></li>
            </ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At:</strong> <code>kubectl describe pod</code> — Events section. <code>crictl pull &lt;image&gt;</code> on node to test registry access. <code>kubectl get sa -o yaml | grep imagePullSecrets</code>.</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>1. Fix image tag: check <code>kubectl describe pod</code> for exact image name<br>2. Create pull secret: <code>kubectl create secret docker-registry regcred ...</code><br>3. Add to pod: <code>imagePullSecrets: - name: regcred</code><br>4. Add to SA: <code>kubectl patch sa default -p '{"imagePullSecrets":[{"name":"regcred"}]}'</code><br>5. Pre-pull image on nodes for air-gapped: <code>crictl pull &lt;image&gt;</code> on all nodes</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> ImagePullBackOff is the most common pod startup failure. First check: is the image name correct? Then: is it public or private? For private registries, you NEED imagePullSecrets — either on the pod or the ServiceAccount. CKA exam tip: <code>kubectl create secret docker-registry</code> is the command to memorize.</div>
    </div>

    <div class="ts-issue" id="ts-tr12"><div class="ts-issue-header"><div class="ts-issue-num">TR12</div><div class="ts-issue-header-content"><div class="ts-category">🔧 CATEGORY 2: TROUBLESHOOTING — Issue TR12</div><div class="ts-title">Pod CrashLoopBackOff — Container Exits Immediately</div><p class="ts-symptom"><strong>🔍 Symptom:</strong> Pod shows CrashLoopBackOff. Container starts and exits repeatedly. <code>kubectl logs</code> may show error or be empty. Application failing at startup.</p></div></div>
        <pre style="color:var(--accent-orange);font-size:12px;margin:8px 0;">
<span class="ts-cmd">  kubectl get pods</span>
<span class="ts-out">  NAME              READY   STATUS            RESTARTS   AGE</span>
<span class="ts-err">  anihpj-api-xxx    0/1     CrashLoopBackOff  12         5m</span>

<span class="ts-cmd">  kubectl logs anihpj-api-xxx --previous</span>
<span class="ts-err">  Error: Unable to connect to database at postgres:5432</span></pre>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>
                <li><span class="cause-likely">Application misconfiguration:</span> Wrong DB host, missing env vars, invalid config. Check: <code>kubectl logs &lt;pod&gt; --previous</code>.</li>
                <li><span class="cause-likely">Dependency not ready:</span> App tries to connect to DB/Redis before it's available. Use initContainers.</li>
                <li><span class="cause-likely">Wrong command or args:</span> <code>kubectl get pod -o yaml | grep -A5 command</code>. Container runs wrong process.</li>
                <li><span class="cause-likely">Missing volume mount:</span> App expects config file at /etc/app/config.yaml but volume not mounted.</li>
                <li><span class="cause-likely">Exit code 1 (generic error):</span> Application logic error. Check app logs for the specific error.</li>
            </ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>
                <li><span class="cause-less-likely">Container requires root but restricted by PodSecurity</span></li>
                <li><span class="cause-less-likely">Liveness probe failing immediately — kills healthy startup</span></li>
                <li><span class="cause-less-likely">SELinux context preventing file access</span></li>
                <li><span class="cause-less-likely">Shared volume with wrong permissions — can't write</span></li>
                <li><span class="cause-less-likely">Resource limits too low — OOMKilled at startup (check Exit Code 137)</span></li>
            </ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>
                <li><span class="cause-new-cluster">Service not yet created — app resolves DNS but gets NXDOMAIN</span></li>
                <li><span class="cause-new-cluster">ConfigMap mounted but key has wrong name</span></li>
                <li><span class="cause-new-cluster">Secret not base64 encoded — app gets garbage value</span></li>
                <li><span class="cause-new-cluster">PodSecurityPolicy blocking the user/group the container wants</span></li>
                <li><span class="cause-new-cluster">Container expects specific kernel capabilities not granted</span></li>
            </ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At:</strong> <code>kubectl logs &lt;pod&gt; --previous</code> — logs from crashed container. <code>kubectl describe pod</code> — exit code. Exit 0=normal, 1=app error, 137=OOMKilled, 143=SIGTERM.</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>1. <code>kubectl logs &lt;pod&gt; --previous</code> — read crash logs<br>2. Fix configuration (env vars, ConfigMaps, Secrets)<br>3. Add initContainer to wait for dependencies<br>4. Increase resources if OOMKilled<br>5. Use <code>command: ["sleep","3600"]</code> temporarily to debug inside container</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> CrashLoopBackOff with no logs means the container exited before writing to stdout. Try <code>kubectl logs --previous</code> to see the last crash's output. If still empty, the app is crashing so early it can't even log. Override the command with <code>sleep infinity</code>, exec in, and run the app manually to debug. Exit codes are your friend: 137=OOM, 143=SIGTERM, 1=app error.</div>
    </div>

    <div class="ts-issue" id="ts-tr13"><div class="ts-issue-header"><div class="ts-issue-num">TR13</div><div class="ts-issue-header-content"><div class="ts-category">🔧 CATEGORY 2: TROUBLESHOOTING — Issue TR13</div><div class="ts-title">Pod Stuck in ContainerCreating — Volume Issues</div><p class="ts-symptom"><strong>🔍 Symptom:</strong> Pod stuck ContainerCreating for minutes. Events show "Unable to attach or mount volumes" or "timed out waiting for volume." PVC/CSI related.</p></div></div>
        <pre style="color:var(--accent-orange);font-size:12px;margin:8px 0;">
<span class="ts-cmd">  kubectl describe pod anihpj-db-0</span>
<span class="ts-out">  Events:</span>
<span class="ts-err">    Warning  FailedMount  Unable to attach or mount volumes:
      unmounted volumes=[db-data], unattached volumes=[db-data]:
      timed out waiting for the condition</span></pre>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>
                <li><span class="cause-likely">PVC not Bound:</span> <code>kubectl get pvc</code> — must be Bound, not Pending.</li>
                <li><span class="cause-likely">CSI driver node plugin not running on this specific node</span></li>
                <li><span class="cause-likely">Volume in wrong AZ:</span> EBS volume in us-east-1a, pod on us-east-1b node.</li>
                <li><span class="cause-likely">ConfigMap/Secret referenced but doesn't exist:</span> <code>kubectl get cm,secret -n &lt;ns&gt;</code>.</li>
                <li><span class="cause-likely">Volume already attached to another node:</span> Multi-attach not supported for block storage.</li>
            </ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>
                <li><span class="cause-less-likely">kubelet PLEG not healthy — delays volume operations</span></li>
                <li><span class="cause-less-likely">Node has reached max volume attachments limit</span></li>
                <li><span class="cause-less-likely">DiskPressure on node — kubelet can't create volume directories</span></li>
                <li><span class="cause-less-likely">CSI socket file missing: /var/lib/kubelet/plugins/... no socket</span></li>
                <li><span class="cause-less-likely">fsGroup change taking too long on large volume (SELinux relabeling)</span></li>
            </ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>
                <li><span class="cause-new-cluster">StorageClass uses Immediate binding — volume created in wrong AZ</span></li>
                <li><span class="cause-new-cluster">CSI driver not installed: <code>kubectl get csidriver</code> — empty</span></li>
                <li><span class="cause-new-cluster">Cloud credentials missing for CSI provisioner to attach volume</span></li>
                <li><span class="cause-new-cluster">Pod references secret in different namespace (not allowed)</span></li>
                <li><span class="cause-new-cluster">Volume snapshot being used as source but snapshot controller not installed</span></li>
            </ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At:</strong> <code>kubectl describe pod</code> — Events. <code>kubectl get pvc,pv</code>. <code>kubectl get volumeattachment</code>. <code>kubectl get pods -n kube-system | grep csi</code>.</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>1. <code>kubectl get pvc</code> — ensure Bound<br>2. Check CSI pods: <code>kubectl get pods -n kube-system -l app=&lt;csi-driver&gt;</code><br>3. Use WaitForFirstConsumer in StorageClass for AZ correctness<br>4. Create missing ConfigMap/Secret<br>5. Force-detach stuck volume: <code>kubectl delete volumeattachment &lt;name&gt;</code></p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> "ContainerCreating" is the most frustrating state because it's always a different cause. The pod Events section tells you exactly what's stuck — read it carefully. If it's a volume issue, check PVC status first. If it's CSI-related, check CSI driver pods. The #1 CKA trap: pod references a ConfigMap that doesn't exist.</div>
    </div>

    <div class="ts-issue" id="ts-tr14"><div class="ts-issue-header"><div class="ts-issue-num">TR14</div><div class="ts-issue-header-content"><div class="ts-category">🔧 CATEGORY 2: TROUBLESHOOTING — Issue TR14</div><div class="ts-title">Pod Stuck in Terminating — Won't Delete</div><p class="ts-symptom"><strong>🔍 Symptom:</strong> <code>kubectl delete pod</code> hangs or pod stuck Terminating for 10+ minutes. Finalizers or preStop hooks blocking deletion.</p></div></div>
        <pre style="color:var(--accent-orange);font-size:12px;margin:8px 0;">
<span class="ts-cmd">  kubectl get pods</span>
<span class="ts-out">  NAME              READY   STATUS        RESTARTS   AGE</span>
<span class="ts-err">  anihpj-web-xxx    0/1     Terminating   0          30m</span>

<span class="ts-cmd">  kubectl describe pod anihpj-web-xxx | grep -A3 Finalizers</span>
<span class="ts-out">  Finalizers:</span>
<span class="ts-err">    example.com/custom-cleanup    # ← Controller not removing this!</span></pre>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>
                <li><span class="cause-likely">Finalizer set by custom controller that's no longer running:</span> <code>kubectl get pod -o yaml | grep finalizers</code>.</li>
                <li><span class="cause-likely">preStop hook hanging:</span> Script in preStop never exits. Check: <code>kubectl get pod -o yaml | grep -A5 preStop</code>.</li>
                <li><span class="cause-likely">Grace period too long:</span> Default 30s may be overridden. <code>terminationGracePeriodSeconds</code> set to >300.</li>
                <li><span class="cause-likely">Pod has PVC with retain policy:</span> PV protection finalizer blocks pod deletion.</li>
                <li><span class="cause-likely">Pod is part of StatefulSet with PVC:</span> PVC finalizer prevents pod deletion.</li>
            </ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>
                <li><span class="cause-less-likely">kubelet on node crashed — can't process pod termination</span></li>
                <li><span class="cause-less-likely">Node not reachable — API server can't tell kubelet to delete</span></li>
                <li><span class="cause-less-likely">Docker/containerd daemon hung — can't stop containers</span></li>
                <li><span class="cause-less-likely">NFS volume stuck — unmount hangs indefinitely</span></li>
                <li><span class="cause-less-likely">Admission webhook blocking pod deletion</span></li>
            </ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>
                <li><span class="cause-new-cluster">Custom controller registered finalizer but never deployed</span></li>
                <li><span class="cause-new-cluster">MutatingWebhookConfiguration adding finalizers to all pods</span></li>
                <li><span class="cause-new-cluster">PodDisruptionBudget prevents eviction during node drain</span></li>
                <li><span class="cause-new-cluster">Foreground deletion propagation stuck on dependent objects</span></li>
                <li><span class="cause-new-cluster">etcd unavailable — deletion can't be persisted</span></li>
            </ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At:</strong> <code>kubectl get pod -o yaml | grep -A10 finalizers</code>. <code>kubectl describe pod</code> — look for preStop hook and status.</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>1. Remove finalizers: <code>kubectl patch pod &lt;name&gt; -p '{"metadata":{"finalizers":[]}}'</code><br>2. Force delete: <code>kubectl delete pod &lt;name&gt; --force --grace-period=0</code><br>3. Find and fix the controller that set the finalizer<br>4. Shorten grace period: <code>kubectl delete pod &lt;name&gt; --grace-period=5</code><br>5. If NFS: unmount forcefully on node: <code>umount -f /var/lib/kubelet/pods/.../volumes/...</code></p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> Stuck Terminating pods are almost always finalizer issues. The nuclear option: <code>kubectl patch pod &lt;name&gt; -p '{"metadata":{"finalizers":[]}}'</code> followed by <code>kubectl delete pod &lt;name&gt; --force --grace-period=0</code>. On the CKA exam, you may need to identify which controller's finalizer is stuck and delete that controller's resources too.</div>
    </div>

    <div class="ts-issue" id="ts-tr15"><div class="ts-issue-header"><div class="ts-issue-num">TR15</div><div class="ts-issue-header-content"><div class="ts-category">🔧 CATEGORY 2: TROUBLESHOOTING — Issue TR15</div><div class="ts-title">Pod OOMKilled (Exit Code 137) — Memory Limit Exceeded</div><p class="ts-symptom"><strong>🔍 Symptom:</strong> Pod restarts with exit code 137 (128+9=SIGKILL). <code>kubectl describe pod</code> shows OOMKilled. Application using more memory than its limit.</p></div></div>
        <pre style="color:var(--accent-orange);font-size:12px;margin:8px 0;">
<span class="ts-cmd">  kubectl describe pod anihpj-api-xxx | grep -A3 State</span>
<span class="ts-out">  State:  Running</span>
<span class="ts-out">    Started:  Thu, 04 Jun 2026 10:00:00</span>
<span class="ts-err">  Last State: Terminated</span>
<span class="ts-err">    Reason: OOMKilled</span>
<span class="ts-err">    Exit Code: 137</span></pre>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>
                <li><span class="cause-likely">Memory limit too low for workload:</span> <code>resources: limits: memory: 128Mi</code> but app needs 512Mi.</li>
                <li><span class="cause-likely">Memory leak in application:</span> Memory grows over time until limit hit. Check: <code>kubectl top pod</code> over time.</li>
                <li><span class="cause-likely">Traffic spike:</span> App handles more concurrent requests, using more memory. Needs higher limit.</li>
                <li><span class="cause-likely">No memory limit set:</span> Pod uses node's available memory until node OOM kills it.</li>
                <li><span class="cause-likely">Java/Python app with default high heap: JVM defaults to 1/4 of container memory.</span></li>
            </ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>
                <li><span class="cause-less-likely">Init container using too much memory before main container starts</span></li>
                <li><span class="cause-less-likely">Sidecar container consuming unexpected memory</span></li>
                <li><span class="cause-less-likely">EmptyDir volume using memory (tmpfs) — counts toward pod memory limit</span></li>
                <li><span class="cause-less-likely">Kernel memory not accounted — cgroups v1 limitation</span></li>
                <li><span class="cause-less-likely">Memory limit is Burstable QoS — pod can be OOMKilled before Guaranteed pods</span></li>
            </ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>
                <li><span class="cause-new-cluster">No default memory limits via LimitRange in namespace</span></li>
                <li><span class="cause-new-cluster">HPA scaling too slow — pods OOM before new pods start</span></li>
                <li><span class="cause-new-cluster">Node overcommitted — total limits > node capacity</span></li>
                <li><span class="cause-new-cluster">Memory eviction thresholds not tuned for workload patterns</span></li>
                <li><span class="cause-new-cluster">Java apps without -XX:MaxRAMPercentage — use all container memory</span></li>
            </ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At:</strong> <code>kubectl describe pod</code> — Last State: OOMKilled. <code>kubectl top pod</code> — current memory usage. <code>kubectl get pod -o yaml | grep -A3 resources</code>.</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>1. Increase limit: <code>resources: limits: memory: 512Mi</code><br>2. Match request=limit for Guaranteed QoS: set same value for both<br>3. Profile app memory usage under load and set limit 20% above peak<br>4. For Java: <code>-XX:MaxRAMPercentage=75.0</code> to use 75% of container limit<br>5. Set up HPA based on memory to scale before OOM</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> OOMKilled (exit 137) is the most common pod restart reason. Always set memory limits, and always set memory REQUESTS equal to limits for production workloads (Guaranteed QoS). This prevents the pod from being the first target during node memory pressure. Java tip: <code>-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0</code> — without this, Java ignores container limits.</div>
    </div>

<footer class="footer"><p>CKA Test Preparation | Built with ❤️ for CKA candidates | © 2025</p><p>200 MCQs · 100 Troubleshooting Issues · 100 Lab Scenarios · 15 Decision Trees · Novice → Professional → Beyond</p></footer>
</main>
'''

# Strip old TS content from TR10 to footer, insert new batch
footer_marker = '<footer class="footer">'
ts10_end = content.find('</div>\n    </div>\n\n    <!-- ═══ TR11')
if ts10_end < 0:
    ts10_end = content.find('Tests ability to diagnose and fix')
    ts10_end = content.find(footer_marker, ts10_end)
else:
    # TR10 ends somewhere, find next footer
    pass

# Simple approach: replace from TR10 end to footer
old_footer_pos = content.find(footer_marker)
# Find the closing of TR10 (last issue before footer)
tr10_close = content.rfind('</div>\n    </div>', 0, old_footer_pos)
if tr10_close > 0:
    tr10_close += len('</div>\n    </div>')
    content = content[:tr10_close] + ts_html + content[old_footer_pos + len(footer_marker):]
    # Remove duplicate footer - find and strip extra content
    # content already has the new footer

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Added TR11-TR15. Size: {len(content):,} chars')
