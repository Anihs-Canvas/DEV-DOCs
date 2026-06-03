#!/usr/bin/env python3
"""Insert CAT4-CAT8 troubleshooting issues into cilium-test-prep.html"""

HTML = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

def LI(t, c="cause-likely"): return f'<li><span class="{c}">{t}</span></li>'

def TS(cat, cn, color, iid, title, symp, ml, ll, nc, look, sol, adv, diag=""):
    return f'''    <div class="ts-issue" id="ts-{iid}-detail">
        <div class="ts-issue-header"><div class="ts-issue-num">{iid.upper()}</div><div class="ts-issue-header-content">
                <div class="ts-category">{color} CATEGORY {cat}: {cn} — Issue {iid.upper()}</div>
                <div class="ts-title">{title}</div>
                <p class="ts-symptom"><strong>🔍 Symptom:</strong> {symp}</p></div></div>{diag}
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>{"".join(ml)}</ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>{"".join(ll)}</ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>{"".join(nc)}</ol></div></div>
        <div class="ts-lookat"><strong>🔍 What to Look At / Take Note Of:</strong> {look}</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>{sol}</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> {adv}</div>
        <div class="ts-footer-spacer"></div></div>'''

def CAT_SECTION(iid, name, badge, intro):
    return f'''
<!-- CATEGORY {iid} -->
<section class="chapter-section" id="ts-cat{iid}">
<h2><span>Category {iid}: {name}</span><span class="chapter-badge">{badge}</span></h2>
<div class="chapter-intro"><p>{intro}</p></div>
</section>
'''

def SH(iid, title): return f'    <div class="ts-section-header" id="ts-{iid}"><h3>{title}</h3></div>\n'

# =====================================================================
# CATEGORY 4: OBSERVABILITY (OB1-OB10)
# =====================================================================
cat4 = CAT_SECTION(4, "Observability", "OB1-OB10", "10 troubleshooting issues covering Hubble, flow visibility, metrics, Grafana, Prometheus alerts, and sysdump analysis.")
cat4 += SH("ob1", "📡 OB1–OB5: Hubble &amp; Flow Visibility")

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob1", "Hubble Relay — No Agents Connected",
    "`hubble relay status` = 0 peers. `hubble observe` = 'no peers'. Hubble UI shows 'No agents'. Port-forward works but no data.",
    [LI("Hubble not enabled on agents: `--set hubble.enabled=true`. Check `cilium status | grep Hubble`."), LI("Relay can't reach Peer Service: `kubectl get svc,ep hubble-peer -n kube-system`. Must exist."), LI("TLS certs missing: `cilium hubble enable` generates certs. Relay-agent communication uses TLS."), LI("Agents not restarted after Hubble enabled: `kubectl -n kube-system rollout restart ds/cilium`."), LI("NetworkPolicy blocking ports 4244 (Hubble gRPC) or 80 (Peer Service).")],
    [LI("Relay pod crash looping: `kubectl logs deploy/hubble-relay`", "cause-less-likely"), LI("Peer Service endpoints empty", "cause-less-likely"), LI("gRPC max message size exceeded for large clusters", "cause-less-likely"), LI("Hubble Relay OOM", "cause-less-likely"), LI("IPv6-only cluster misconfiguration", "cause-less-likely")],
    [LI("hubble.enabled=false (default) in Helm", "cause-new-cluster"), LI("hubble.relay.enabled not set", "cause-new-cluster"), LI("TLS certs not generated", "cause-new-cluster"), LI("hubble-peer Service not created by Helm", "cause-new-cluster"), LI("RBAC missing for hubble-relay", "cause-new-cluster")],
    "`cilium status | grep Hubble`. `cilium hubble relay status`. `kubectl logs deploy/hubble-relay -n kube-system`. Peer Service: `kubectl get svc,ep hubble-peer -n kube-system`. Relay = aggregation layer for all agents.",
    "1. `cilium hubble enable` — enables Hubble + Relay + UI<br>2. `cilium status | grep Hubble` — all three OK?<br>3. `cilium hubble relay status` — check peer count<br>4. `kubectl logs deploy/hubble-relay -n kube-system`<br>5. `kubectl exec deploy/hubble-relay -- hubble list-nodes`",
    "Without Relay, you query each agent individually. For anihpj: always deploy Relay for cluster-wide visibility. Common mistake: enabling Hubble but forgetting Relay."

) + TS(4, "OBSERVABILITY", "🔵", "ob2", "Hubble Observe — Empty Output / Timeout",
    "`hubble observe` returns nothing. `hubble observe --follow` hangs. Port-forward works but no flows visible.",
    [LI("Hubble server not enabled: `cilium config | grep hubble`. Must show enabled with socket path."), LI("Flow export not on: agents need Hubble. `cilium status | grep Hubble` per node."), LI("Wrong socket: default unix:///var/run/cilium/hubble.sock."), LI("No matching traffic: default shows recent flows. Idle cluster = no output."), LI("Namespace filter too narrow: `-n kube-system` excludes app traffic in `anihpj`.")],
    [LI("Hubble ring buffer full — oldest events evicted", "cause-less-likely"), LI("Flow API rate limiting", "cause-less-likely"), LI("CLI version mismatch with server", "cause-less-likely"), LI("BPF ring buffer perf event lost (kernel backpressure)", "cause-less-likely"), LI("TLS handshake timeout CLI→Relay", "cause-less-likely")],
    [LI("Hubble not enabled: `--set hubble.enabled=false` default", "cause-new-cluster"), LI("hubble-relay not deployed", "cause-new-cluster"), LI("hubble-ui not deployed", "cause-new-cluster"), LI("Port-forward to wrong service", "cause-new-cluster"), LI("No traffic yet — cluster just installed", "cause-new-cluster")],
    "`cilium status | grep Hubble`. Start broad: `hubble observe --verdict DROPPED` — always shows if policies exist. Generate traffic: `cilium connectivity test`.",
    "1. `cilium status` — all Hubble OK?<br>2. `cilium hubble port-forward &`<br>3. `hubble observe --verdict DROPPED`<br>4. `hubble observe -n anihpj`<br>5. Generate test traffic: `kubectl exec deploy/web -- curl http://anihpj-api`",
    "Hubble = 'tcpdump for Kubernetes'. For anihpj: always start with `hubble observe --verdict DROPPED` to see policy blocks. Then narrow by namespace/pod."

) + TS(4, "OBSERVABILITY", "🔵", "ob3", "Hubble UI — Blank Dashboard",
    "Hubble UI loads but shows 'No flows'. Service map empty. Flow table shows zero records. Browser console shows API errors.",
    [LI("UI can't reach Relay: `kubectl get svc hubble-ui -n kube-system`. UI proxies through Relay."), LI("No traffic in time range: default = last 5 min. Generate: `cilium connectivity test`."), LI("Namespace filter stuck from previous session: clear all filters."), LI("Relay has 0 peers: `cilium hubble relay status` — 0 peers = no data for UI."), LI("CORS/browser issue: check browser dev tools → Network → API calls failing.")],
    [LI("UI pod OOM with large cluster flow data", "cause-less-likely"), LI(">100K flows/sec overloads browser", "cause-less-likely"), LI("UI version vs Relay version incompatible", "cause-less-likely"), LI("WebSocket connection to Relay dropping", "cause-less-likely"), LI("Browser local storage corrupted", "cause-less-likely")],
    [LI("hubble.ui.enabled not in Helm values", "cause-new-cluster"), LI("UI Service not exposed (need port-forward/Ingress)", "cause-new-cluster"), LI("UI pod not scheduled (resources)", "cause-new-cluster"), LI("Relay DNS not resolvable from UI", "cause-new-cluster"), LI("No Ingress for external UI access", "cause-new-cluster")],
    "`kubectl get pods -n kube-system | grep hubble`. `cilium hubble ui` opens browser. Generate traffic before checking UI.",
    "1. `cilium hubble ui` — auto-port-forward<br>2. Generate traffic: `kubectl exec deploy/web -- curl -s http://anihpj-api`<br>3. `cilium hubble relay status`<br>4. Clear ALL UI filters<br>5. Browser dev tools → Network tab",
    "Hubble UI = visual troubleshooting. For anihpj: bookmark `cilium hubble ui`. The service map visualizes all pod-to-pod communication. Essential for understanding your app's network behavior."

) + TS(4, "OBSERVABILITY", "🔵", "ob4", "Hubble Metrics Missing in Prometheus",
    "Prometheus shows no hubble_* metrics. `curl <agent>:9965/metrics` returns empty or connection refused.",
    [LI("Metrics list not set: `--set hubble.metrics.enabled='{drop,tcp,flow,dns,http}'`. Empty list = nothing exported."), LI("Port 9965 not open: separate from agent metrics (9962). `cilium status | grep Metrics`."), LI("ServiceMonitor/PodMonitor not created: Prometheus needs discovery config."), LI("Firewall blocking 9965: security groups must allow Prometheus → agent:9965."), LI("Metric names must match exactly: `hubble.metrics` is a list — wrong name = no metric.")],
    [LI("Prometheus scraping wrong port (9090 not 9965)", "cause-less-likely"), LI("All values 0 — no traffic in cluster", "cause-less-likely"), LI("Prometheus relabel dropping Cilium targets", "cause-less-likely"), LI("Agent restarting faster than scrape interval", "cause-less-likely"), LI("IPv6 address not handled by scrape config", "cause-less-likely")],
    [LI("hubble.metrics not in Helm — empty default", "cause-new-cluster"), LI("Prometheus not installed", "cause-new-cluster"), LI("ServiceMonitor CRD not installed", "cause-new-cluster"), LI("No Prometheus annotation on Cilium pods", "cause-new-cluster"), LI("NetworkPolicy blocking Prometheus→agent:9965", "cause-new-cluster")],
    "`cilium status | grep Metrics`. `curl <node-ip>:9965/metrics | grep hubble`. Port map: 9962=agent, 9964=Envoy, 9965=Hubble.",
    "1. `cilium hubble enable --metrics 'drop,tcp,flow,port-distribution,dns,http'`<br>2. `curl <node-ip>:9965/metrics`<br>3. Create ServiceMonitor for port 9965<br>4. Check Prometheus targets: 9965, path /metrics<br>5. Import Grafana dashboard 15514 (Hubble)",
    "Hubble metrics bridge flow logs and dashboards. For anihpj: enable drop, tcp, flow, http at minimum. Import Grafana dashboard ID 15514 for instant Hubble visualization."

) + TS(4, "OBSERVABILITY", "🔵", "ob5", "Flow Export to External SIEM/Collector Fails",
    "Hubble export configured (Kafka/ES/Splunk) but external system receives no flows. Export appears configured but silent.",
    [LI("Export config not set: `cilium config | grep hubble-export`. Needs explicit output target config."), LI("Collector unreachable: DNS resolution from agent to collector. `kubectl exec ds/cilium -- nc -zv <host> <port>`."), LI("TLS for export missing: if collector needs TLS, certs must be configured."), LI("File path not writable: if file export, agent needs write permissions."), LI("Flow filter too restrictive: export uses same filter — if nothing matches, nothing exported.")],
    [LI("Export buffer full — backpressure from slow collector", "cause-less-likely"), LI("Kafka topic auto-create disabled", "cause-less-likely"), LI("Message format mismatch (JSON vs Protobuf)", "cause-less-likely"), LI("Agent DNS cache stale for collector hostname", "cause-less-likely"), LI("Flow rate exceeds collector ingest capacity", "cause-less-likely")],
    [LI("Export not in Helm values", "cause-new-cluster"), LI("External collector not yet provisioned", "cause-new-cluster"), LI("Network isolation: cluster can't reach collector", "cause-new-cluster"), LI("TLS secrets for export not created", "cause-new-cluster"), LI("No monitoring for export pipeline health", "cause-new-cluster")],
    "`cilium config | grep hubble-export`. `kubectl logs ds/cilium | grep -i 'export|kafka|elastic'`. `kubectl exec ds/cilium -- nc -zv <collector> <port>`.",
    "1. Configure: `cilium config set hubble-export-file-path /var/log/cilium/flows.json`<br>2. Or Kafka: `cilium hubble enable --kafka-brokers <broker>:9092 --kafka-topic hubble`<br>3. Test: `kubectl exec ds/cilium -- nc -zv <collector> <port>`<br>4. Check agent logs for export errors<br>5. Verify flow filter includes your traffic",
    "Hubble export = network telemetry pipeline. For anihpj: export to Elasticsearch + Kibana for long-term flow storage. Hubble's local ring buffer is transient — export gives you historical data for compliance and analysis."
)

# OB6-OB10
cat4 += SH("ob6", "📈 OB6–OB10: Metrics, Dashboards &amp; Alerts")
cat4 += TS(4, "OBSERVABILITY", "🔵", "ob6", "Cilium Agent Metrics Missing from Prometheus",
    "Prometheus shows no cilium_* metrics. `curl <agent>:9962/metrics` returns empty. Agent metrics port not responding.",
    [LI("Agent metrics port 9962: different from Hubble (9965). `--set prometheus.enabled=true`."), LI("ServiceMonitor selects wrong port: 9962=agent, 9964=Envoy, 9965=Hubble."), LI("Firewall blocking 9962: security groups must allow Prometheus scrape."), LI("KPR strict may interfere: if KPR redirects, metrics path may change."), LI("prometheus.enabled=false in Helm: check values.")],
    [LI("Agent restarting frequently — metrics reset", "cause-less-likely"), LI("Scrape interval > metric lifetime", "cause-less-likely"), LI("Agent memory pressure → timeout", "cause-less-likely"), LI("IPv6 bind failure", "cause-less-likely"), LI("Cardinality explosion → scrape timeout", "cause-less-likely")],
    [LI("prometheus.enabled not in Helm values", "cause-new-cluster"), LI("Prometheus operator not installed", "cause-new-cluster"), LI("ServiceMonitor not created for agent", "cause-new-cluster"), LI("RBAC for Prometheus pod discovery missing", "cause-new-cluster"), LI("Wrong port in ServiceMonitor (9965 vs 9962)", "cause-new-cluster")],
    "`cilium status | grep Metrics`. `curl <node-ip>:9962/metrics | head -5`. Three ports: 9962=agent, 9964=Envoy, 9965=Hubble. Each needs own ServiceMonitor.",
    "1. `--set prometheus.enabled=true` in Helm<br>2. `curl <node-ip>:9962/metrics` — cilium_* metrics?<br>3. ServiceMonitor for 9962 (agent)<br>4. ServiceMonitor for 9965 (Hubble)<br>5. ServiceMonitor for 9964 (Envoy, if L7)",
    "Three metrics endpoints! For anihpj: enable all three. Agent = Cilium health. Envoy = L7 proxy stats. Hubble = flow-derived metrics. Each needs its own Prometheus scrape config."

) + TS(4, "OBSERVABILITY", "🔵", "ob7", "Grafana Dashboard — Missing Cilium Panels",
    "Imported dashboard 15513/15514 but panels show 'No data'. Prometheus works for other dashboards.",
    [LI("Wrong data source name: dashboard hardcodes 'Prometheus'. Yours may be 'prometheus' or 'thanos'."), LI("Metrics not enabled: specific metrics needed. `cilium metrics list` — verify set."), LI("Deprecated metric names: Cilium renames metrics between versions. Check dashboard vs Cilium version."), LI("Template variables fail: node/pod variables may not resolve in your cluster."), LI("Time range too short: metrics scraped every 30s. Need 5+ min of data.")],
    [LI("Grafana Prometheus plugin outdated", "cause-less-likely"), LI("Dashboard JSON for wrong Cilium version", "cause-less-likely"), LI("Custom recording rules missing", "cause-less-likely"), LI("Agent labels don't match dashboard filters", "cause-less-likely"), LI("Grafana timezone vs Prometheus timestamps", "cause-less-likely")],
    [LI("No Cilium metrics enabled at all", "cause-new-cluster"), LI("Prometheus not scraping Cilium agents", "cause-new-cluster"), LI("Wrong dashboard imported (non-Cilium)", "cause-new-cluster"), LI("Grafana data source not configured", "cause-new-cluster"), LI("Dashboard imported before metrics existed", "cause-new-cluster")],
    "Grafana → Dashboard settings → Variables → check. `cilium metrics list`. Official dashboards: 15513 (Cilium Agent), 15514 (Hubble).",
    "1. `cilium metrics list` — verify metrics enabled<br>2. Prometheus: `up{job='cilium-agent'}` — returns all nodes?<br>3. Data source name must match dashboard variable<br>4. Import latest dashboard from cilium.io<br>5. Time range: 'Last 15 minutes' minimum",
    "Official Grafana dashboards: ID 15513 (Agent) and 15514 (Hubble). For anihpj: start with these, then customize for app-specific HTTP metrics."

) + TS(4, "OBSERVABILITY", "🔵", "ob8", "cilium monitor — Event Flood, Can't Find Relevant Event",
    "`cilium monitor` outputs thousands/sec. Can't isolate the one dropped packet you need.",
    [LI("No filter: shows ALL events. Use `--type drop` for drops only, `--type policy-verdict` for policies."), LI("Too many endpoints: filter by ID: `cilium monitor --from <ep-id> --to <ep-id>`."), LI("Verbose mode overwhelming: `-v` shows hex dumps. Skip unless deep debugging."), LI("No related-to filter: `--related-to <ep-id>` shows events for specific endpoint."), LI("Better tool available: `hubble observe` is for data plane flows. `cilium monitor` = control plane.")],
    [LI("Debug logging enabled in production: disable `--set debug.enabled=true`", "cause-less-likely"), LI("Event buffer too small → dropped events", "cause-less-likely"), LI("JSON mode not used: `-o json` for programmatic parsing", "cause-less-likely"), LI("Multiple monitors → event duplication", "cause-less-likely"), LI("Agent restart replaying ring buffer events", "cause-less-likely")],
    [LI("Production with debug logging: wrong config", "cause-new-cluster"), LI("Unfamiliar with monitor filter flags", "cause-new-cluster"), LI("Using monitor instead of hubble for flow debugging", "cause-new-cluster"), LI("Events not correlated with Hubble flows", "cause-new-cluster"), LI("No event retention policy", "cause-new-cluster")],
    "`cilium monitor --type drop -n anihpj` = only drops. `hubble observe --verdict DROPPED` = better for data plane. Monitor = control plane. Hubble = data plane.",
    "1. `cilium monitor --type drop` — policy drops<br>2. `cilium monitor --from <ep-id> --to <ep-id>`<br>3. `cilium monitor --type policy-verdict`<br>4. Prefer `hubble observe --verdict DROPPED` for flows<br>5. `cilium monitor -o json | grep <keyword>`",
    "monitor = WHY Cilium does something. Hubble = WHAT happened to traffic. For anihpj: use Hubble first (flow visibility), then monitor for control plane debugging."

) + TS(4, "OBSERVABILITY", "🔵", "ob9", "Prometheus Alert Rules Not Firing",
    "Alert rules for Cilium configured but never fire. `cilium status` shows degraded but no alert. AlertManager silent.",
    [LI("Expression threshold wrong: test in Prometheus console first. e.g., `cilium_endpoint_regenerations_total > 0`."), LI("Metric name changed between versions: verify exact name in `curl <agent>:9962/metrics`."), LI("'for' duration too long: 15m means issue must persist 15 minutes. Reduce to 1m for quick detection."), LI("Evaluation interval too slow: default 1m. Issue resolves before alert fires."), LI("Label selectors mismatch: alert rule labels must match actual metric labels.")],
    [LI("Rule file syntax error silently ignored", "cause-less-likely"), LI("AlertManager not configured as alert target", "cause-less-likely"), LI("Inhibit rules suppressing Cilium alerts", "cause-less-likely"), LI("Expression returns empty vector (no time series)", "cause-less-likely"), LI("Agent label changed between Cilium versions", "cause-less-likely")],
    [LI("No Cilium alert rules created at all", "cause-new-cluster"), LI("Prometheus not scraping Cilium endpoints", "cause-new-cluster"), LI("AlertManager not deployed", "cause-new-cluster"), LI("Alert routing not configured", "cause-new-cluster"), LI("Staging metrics differ from production", "cause-new-cluster")],
    "Prometheus → Alerts tab → check rule state. `curl <prom>:9090/api/v1/rules | grep cilium`. Test expression in console first.",
    "1. Test: `cilium_agent_endpoint_regenerations_total > 0` in Prometheus console<br>2. `promtool test rules /path/to/rules.yml`<br>3. `for`: 1m critical, 5m warning<br>4. `amtool alert` — check AlertManager<br>5. Route to Slack/email/PagerDuty",
    "Critical alerts: agent down, unreachable nodes, high policy drops, encryption errors. For anihpj: alert on `rate(hubble_drop_total[5m]) > 10` and `cilium_unreachable_nodes > 0`."

) + TS(4, "OBSERVABILITY", "🔵", "ob10", "cilium sysdump — Too Large / Can't Analyze",
    "`cilium sysdump` = 500MB+ zip. Can't find relevant logs. Timeout collecting from slow nodes. Support can't open the file.",
    [LI("No node filter: collects ALL nodes. Use `--node-list node-1,node-2`."), LI("BPF map dumps huge: large clusters = huge maps. Skip with selective collection."), LI("Hubble flows bloated: if export on, flows massive. Use `--since` flag."), LI("Collection timeout: slow nodes. Increase `--timeout` or target responsive nodes."), LI("Old logs included: use `--since 1h` for recent issues only.")],
    [LI("Disk space on sysdump node insufficient", "cause-less-likely"), LI("Compression of 500MB+ takes minutes", "cause-less-likely"), LI("Network transfer of large zip to support", "cause-less-likely"), LI("BPF map binary format not human-readable", "cause-less-likely"), LI("Sensitive data (IPs, endpoints) in logs", "cause-less-likely")],
    [LI("No sysdump retention policy", "cause-new-cluster"), LI("Sysdump from whole cluster vs affected nodes", "cause-new-cluster"), LI("No automation for collection", "cause-new-cluster"), LI("Support can't open 500MB+ files", "cause-new-cluster"), LI("No sysdump analysis tooling", "cause-new-cluster")],
    "`cilium sysdump --node-list node-1`. First files to check: `cilium-status.log`, `cilium-agent.log`, `cilium-config.yaml`. Typical: 50-200MB per node.",
    "1. `cilium sysdump --node-list <bad-node>`<br>2. `--since 1h` for recent only<br>3. Skip BPF maps if not needed<br>4. Analyze: start with status.log and agent.log<br>5. Automate: cronjob for weekly rotation",
    "cilium sysdump = first response to any Cilium issue. For anihpj: script it — `cilium sysdump --node-list $(kubectl get nodes -l node-role=worker -o name | head -3) --since 30m` and upload to S3."
)

print("✅ CAT4 generated: 10 issues")

# =====================================================================
# CATEGORY 5: INSTALLATION (IN1-IN10)
# =====================================================================
cat5 = CAT_SECTION(5, "Installation & Configuration", "IN1-IN10", "10 troubleshooting issues covering install failures, Helm issues, kernel incompatibility, CNI conflicts, upgrade problems, and configuration errors.")
cat5 += SH("in1", "💿 IN1–IN5: Installation &amp; Bootstrap Failures")
cat5 += TS(5, "INSTALLATION", "🟠", "in1", "Cilium Agent CrashLoopBackOff After Install",
    "After `helm install cilium`, agent pods in CrashLoopBackOff. `kubectl logs` shows BPF/kernel errors. `cilium status` shows agent down.",
    [LI("Kernel too old: `uname -r`. Cilium needs 5.10+ for core eBPF. 5.4+ with CO-RE + BTF."), LI("BPF filesystem not mounted: `mount | grep bpf`. Cilium needs /sys/fs/bpf mounted."), LI("kube-proxy still running: conflict. `kubectl get pods -n kube-system -l k8s-app=kube-proxy`."), LI("CNI config conflict: old CNI config in /etc/cni/net.d/. Remove old .conflist files."), LI("Missing kernel modules: `lsmod | grep -E 'vxlan|geneve|ipip'`. Tunnel module needed.")],
    [LI("AppArmor/SELinux blocking eBPF syscalls", "cause-less-likely"), LI("kernel.unprivileged_bpf_disabled=1", "cause-less-likely"), LI("Cilium agent binary corrupted (image pull issue)", "cause-less-likely"), LI("Node filesystem readonly", "cause-less-likely"), LI("Container runtime not supporting Cilium CNI", "cause-less-likely")],
    [LI("Wrong Helm values for cloud provider: EKS needs eni, AKS needs azure, etc.", "cause-new-cluster"), LI("Kernel version not checked before install", "cause-new-cluster"), LI("No pre-flight check: `cilium preflight` not run", "cause-new-cluster"), LI("CNI conflist from previous CNI still present", "cause-new-cluster"), LI("Kubelet --network-plugin not set to cni", "cause-new-cluster")],
    "`kubectl logs ds/cilium -n kube-system`. `uname -r` on node. `mount | grep bpf`. `lsmod | grep vxlan`. `kubectl describe pod -n kube-system -l k8s-app=cilium`.",
    "1. Check kernel: `uname -r` must be ≥5.10 (5.4 with BTF)<br>2. Mount bpffs: `mount -t bpf bpffs /sys/fs/bpf`<br>3. Remove kube-proxy: `kubectl delete ds -n kube-system kube-proxy`<br>4. Clean CNI config: `rm /etc/cni/net.d/*.conflist` (keep Cilium)<br>5. Run preflight: `cilium preflight` before install",
    "CrashLoopBackOff after install = almost always kernel or CNI conflict. For anihpj: run `cilium preflight` BEFORE install. It validates kernel, mounts, and CNI readiness. Saves hours of debugging."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in2", "Helm Install Hangs / Times Out",
    "`helm install cilium cilium/cilium` hangs at 'Waiting for Cilium to become ready'. Times out after 5 minutes. Pods are Pending or ImagePullBackOff.",
    [LI("Image pull failure: `kubectl describe pod -n kube-system -l k8s-app=cilium`. Check image registry access."), LI("Node taints not tolerated: Cilium DaemonSet needs toleration for control-plane/worker taints."), LI("Resource requests too high: nodes don't have enough CPU/memory. Reduce requests."), LI("Helm wait timeout too short: increase `--timeout 10m` for slow clusters."), LI("Pre-install Job (preflight) stuck: Check `kubectl get jobs -n kube-system | grep cilium`.")],
    [LI("DNS resolution failing: agent can't resolve kube-apiserver", "cause-less-likely"), LI("Helm release in pending-install state from previous failed install", "cause-less-likely"), LI("Webhook not ready: Cilium validating webhook blocking self", "cause-less-likely"), LI("Storage provisioner slow for etcd PV (cluster mesh)", "cause-less-likely"), LI("CRD schema too large causing API timeout", "cause-less-likely")],
    [LI("Image registry not accessible (air-gapped env)", "cause-new-cluster"), LI("Helm repo not added: `helm repo add cilium https://helm.cilium.io`", "cause-new-cluster"), LI("Values.yaml has wrong cluster config", "cause-new-cluster"), LI("K8s version too old for this Cilium version", "cause-new-cluster"), LI("NodeSelector preventing scheduling on any node", "cause-new-cluster")],
    "`kubectl get pods -n kube-system -l k8s-app=cilium -o wide`. `kubectl describe pod` for events. `kubectl get events -n kube-system --sort-by='.lastTimestamp'`.",
    "1. `kubectl describe pod -n kube-system -l k8s-app=cilium` — check events<br>2. Image pull: verify `docker pull quay.io/cilium/cilium:v<version>` on node<br>3. Tolerations: check nodes for taints `kubectl describe nodes | grep Taint`<br>4. Increase timeout: `helm install ... --timeout 15m`<br>5. `helm list -n kube-system` — check for stuck releases",
    "Helm install timeout = usually image pull or scheduling issue. For anihpj: pre-pull images to all nodes before install. Use `helm install --wait --timeout 15m` for slow environments."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in3", "CNI Conflict — Pods Stuck in ContainerCreating",
    "After installing Cilium, new pods stuck in 'ContainerCreating'. `kubectl describe pod` shows 'network: failed to setup network' or 'CNI plugin not initialized'.",
    [LI("Old CNI config still in /etc/cni/net.d/: Multiple .conflist files = kubelet picks wrong one. Remove non-Cilium configs."), LI("Cilium agent not ready on node: `cilium status` — agent must be 'OK' before pods can be created."), LI("Cilium CNI plugin binary missing: /opt/cni/bin/cilium-cni must exist (installed by DaemonSet init container)."), LI("CNI chaining misconfigured: if using chaining, primary CNI must be healthy for Cilium to attach."), LI("Kubelet CNI args wrong: --cni-conf-dir and --cni-bin-dir must point to Cilium config.")],
    [LI("Node reboot cleared /opt/cni/bin (tmpfs mount)", "cause-less-likely"), LI("Cilium CNI socket permissions wrong (root-only)", "cause-less-likely"), LI("Concurrent CNI ADD calls overwhelming agent", "cause-less-likely"), LI("Network namespace leak from old pods", "cause-less-likely"), LI("Cilium agent restarting during CNI call", "cause-less-likely")],
    [LI("Previous CNI not fully removed before Cilium install", "cause-new-cluster"), LI("CNI conflist not updated to Cilium's conflist", "cause-new-cluster"), LI("cilium-cni binary not in /opt/cni/bin", "cause-new-cluster"), LI("Kubelet config still references old CNI plugin", "cause-new-cluster"), LI("No drain of node before CNI migration", "cause-new-cluster")],
    "`ls /etc/cni/net.d/` — only 05-cilium.conflist should exist. `ls /opt/cni/bin/` — cilium-cni must be present. `kubectl describe pod` — events show exact CNI error.",
    "1. `ls /etc/cni/net.d/` — remove old .conflist files<br>2. `ls /opt/cni/bin/cilium-cni` — must exist<br>3. Restart Cilium agent: `kubectl -n kube-system delete pod -l k8s-app=cilium`<br>4. Check kubelet CNI config: `cat /var/lib/kubelet/kubeadm-flags.env`<br>5. Recreate stuck pods: `kubectl delete pod <name>`",
    "CNI conflicts = #1 post-install issue. For anihpj: before installing Cilium, drain one node, remove all CNI configs, install Cilium, uncordon. Then repeat for other nodes. One-node-at-a-time migration."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in4", "cilium connectivity test Fails — Specific Scenarios",
    "`cilium connectivity test` fails on specific scenarios like 'client-egress-l7' or 'pod-to-pod-encryption'. Some tests pass, others don't.",
    [LI("L7 tests fail: L7 policy tests need Envoy proxy. `cilium status | grep Proxy`. If proxy not running, L7 tests fail."), LI("Encryption tests fail: WireGuard/IPSec not enabled. `cilium encrypt status` — check if encryption is active."), LI("Hubble tests fail: Hubble Relay not connected. `cilium hubble relay status`."), LI("DNS tests fail: CoreDNS issue, not Cilium. Check `kubectl get pods -n kube-system -l k8s-app=kube-dns`."), LI("Bandwidth tests fail: Bandwidth Manager not enabled. `cilium status | grep Bandwidth`.")],
    [LI("Connectivity test pods can't schedule (node taints)", "cause-less-likely"), LI("Test namespace cleanup failed from previous run", "cause-less-likely"), LI("NetworkPolicy in test namespace blocking test traffic", "cause-less-likely"), LI("Hubble flow validation slow: use `--flow-validation=disabled`", "cause-less-likely"), LI("Test timeout on slow nodes", "cause-less-likely")],
    [LI("connectivity test run before Cilium fully ready", "cause-new-cluster"), LI("Not all Cilium features enabled (Enovy, Hubble, encryption)", "cause-new-cluster"), LI("KPR not strict — NodePort tests may fail", "cause-new-cluster"), LI("MTU issues between nodes", "cause-new-cluster"), LI("Cloud firewall blocking test traffic", "cause-new-cluster")],
    "Map failures to features: L7→Envoy, encryption→WireGuard/IPSec, Hubble→Relay, bandwidth→Bandwidth Manager. `cilium connectivity test --flow-validation=disabled` if Hubble is off.",
    "1. Identify failing scenario: client-egress-l7 = Envoy issue, pod-to-pod-encryption = WireGuard issue<br>2. `cilium status` — verify all components OK<br>3. Enable missing features: `cilium hubble enable`, `cilium encrypt enable`<br>4. `cilium connectivity test --flow-validation=disabled --test '!encryption'`<br>5. Run individual test: `cilium connectivity test --test pod-to-pod`",
    "connectivity test = Cilium's healthcheck. For anihpj: run after every install and upgrade. If some tests fail, it tells you exactly which features need attention. Use `--test` flag to run specific scenarios."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in5", "Cilium ConfigMap Changes Not Applied",
    "Edited cilium-config ConfigMap but changes not reflected. `cilium config view` shows old values. Agent behavior unchanged.",
    [LI("Agent doesn't auto-reload: ConfigMap changes need agent restart. `kubectl -n kube-system rollout restart ds/cilium`."), LI("ConfigMap format wrong: some values are bool, some string. `debug: 'true'` vs `debug: true` matters."), LI("Config key typo: Cilium silently ignores unknown keys. Verify exact key names via `cilium config view`."), LI("Helm values override ConfigMap: if installed via Helm, Helm manages the ConfigMap. Manual edits reverted."), LI("ConfigMap not propagated to all agents: check agent logs for config reload events.")],
    [LI("ConfigMap too large causing API timeout on update", "cause-less-likely"), LI("Agent restarting but picking up cached old config", "cause-less-likely"), LI("Multiple ConfigMaps (cilium vs cilium-config)", "cause-less-likely"), LI("Config change needs cilium-operator restart too", "cause-less-likely"), LI("Immutable ConfigMap field changed (needs delete+recreate)", "cause-less-likely")],
    [LI("Editing ConfigMap instead of Helm values (Helm-managed install)", "cause-new-cluster"), LI("Unknown config key format", "cause-new-cluster"), LI("No agent restart after ConfigMap change", "cause-new-cluster"), LI("cilium config set used but Helm reverts on next sync", "cause-new-cluster"), LI("ConfigMap in wrong namespace (not kube-system)", "cause-new-cluster")],
    "`cilium config view` — current runtime config. `kubectl describe cm cilium-config -n kube-system`. For Helm: use `helm upgrade --reuse-values --set key=value`.",
    "1. For CLI install: `cilium config set Key=Value` (auto-restarts agents)<br>2. For Helm: `helm upgrade cilium cilium/cilium --reuse-values --set key=value`<br>3. Manual: edit CM, then `kubectl -n kube-system rollout restart ds/cilium`<br>4. Verify: `cilium config view | grep <key>`<br>5. Check agent logs: `kubectl logs ds/cilium | grep config`",
    "ConfigMap management depends on install method. For anihpj (Helm): always use `helm upgrade` to change config. Never manually edit cilium-config if Helm manages it — changes will be reverted on next Helm operation."
)

# IN6-IN10
cat5 += SH("in6", "⚙️ IN6–IN10: Upgrades, Uninstall &amp; Air-Gap")
cat5 += TS(5, "INSTALLATION", "🟠", "in6", "Upgrade Fails — CRD Schema Incompatibility",
    "`helm upgrade cilium` fails with 'CRD schema validation error'. `cilium upgrade` also fails. Agents won't start after partial upgrade.",
    [LI("CRD schema updated: newer Cilium adds/removes CRD fields. Must `kubectl apply -f` new CRDs BEFORE Helm upgrade."), LI("Stale CRDs from old version: deprecated CRDs cause conflicts. `kubectl get crd | grep cilium` — compare with new version."), LI("Helm 3-way merge conflict: old manifest, new manifest, live state diverge. Helm can't resolve."), LI("Webhook version mismatch: old webhook not compatible with new CRDs. Delete old webhooks first."), LI("In-progress Cilium operations: endpoints being created during upgrade cause race condition.")],
    [LI("etcd database size limit hit during CRD migration", "cause-less-likely"), LI("CRD conversion webhook timeout on large clusters", "cause-less-likely"), LI("Custom resources in terminating state blocking CRD update", "cause-less-likely"), LI("Helm release secret corruption", "cause-less-likely"), LI("API server rejecting CRD due to field validation changes", "cause-less-likely")],
    [LI("Upgrade notes not read: skipped BREAKING CHANGES section", "cause-new-cluster"), LI("CRDs not applied before Helm upgrade", "cause-new-cluster"), LI("Skipping multiple minor versions (shouldn't skip >2)", "cause-new-cluster"), LI("No staging environment for upgrade testing", "cause-new-cluster"), LI("Backup not taken before upgrade", "cause-new-cluster")],
    "ALWAYS read upgrade notes. `kubectl get crd | grep cilium`. `kubectl apply -f <new-crds>.yaml` BEFORE Helm upgrade. Test in staging.",
    "1. Read upgrade notes: https://docs.cilium.io/en/stable/operations/upgrade/<br>2. Apply new CRDs: `kubectl apply -f crds.yaml` for new version<br>3. `helm upgrade cilium cilium/cilium --version <new>`<br>4. `cilium status` — wait for all agents OK<br>5. `cilium connectivity test` — verify function",
    "CRD schema changes are the #1 upgrade failure. For anihpj: ALWAYS apply CRDs first, THEN upgrade Helm. If upgrade fails mid-way, DO NOT revert — Cilium supports forward-only upgrades. Reverting with partially applied CRDs = disaster."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in7", "Helm Rollback After Failed Upgrade",
    "Upgraded Cilium, something broke, tried `helm rollback`. Now agents crash with 'unknown BPF map format' or 'version mismatch'.",
    [LI("eBPF programs newer than agent: old agent can't read BPF maps created by new agent. Rollback = agent downgrades but BPF stays new."), LI("CRD schema too new: new CRDs applied, old Cilium doesn't understand new fields → crashes."), LI("ConfigMap has new keys: old agent ignores unknown keys but may crash on required new keys."), LI("cilium-operator version mismatch: operator may be new while agents are old (or vice versa)."), LI("Hubble/Envoy version mismatch: Relay expects new flow format, old agents send old format.")],
    [LI("BPF map pinning conflict: old agent tries to reuse new agent's pinned maps", "cause-less-likely"), LI("Identity cache format changed between versions", "cause-less-likely"), LI("Encryption key format changed (WireGuard/IPSec)", "cause-less-likely"), LI("Hubble flow protocol buffer schema changed", "cause-less-likely"), LI("CiliumEndpoint CRD status fields changed", "cause-less-likely")],
    [LI("Rollback attempted without reading rollback docs", "cause-new-cluster"), LI("CRD changes not reverted before rollback", "cause-new-cluster"), LI("No staging test of rollback procedure", "cause-new-cluster"), LI("Backup not taken before upgrade", "cause-new-cluster"), LI("Assumed rollback is safe for all versions", "cause-new-cluster")],
    "Rollback risk: eBPF programs in kernel are from NEW version. Old agent may not understand them. Solution: restart pods (forces BPF program reload). Test rollback in staging.",
    "1. After rollback: `kubectl -n kube-system rollout restart ds/cilium`<br>2. Delete all pods in affected namespaces (forces CNI re-invoke)<br>3. `cilium cleanup` on nodes if BPF maps corrupted<br>4. `cilium connectivity test` after rollback<br>5. For CRD issues: manually revert CRDs to old version YAML",
    "Cilium rollback is NOT seamless due to eBPF programs persisting in kernel. For anihpj: prefer forward fix (upgrade to patched version) over rollback. If you must rollback: restart ALL pods to reload eBPF programs with old agent format."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in8", "Cilium Uninstall — Pods Lose Network",
    "Ran `cilium uninstall` or `helm uninstall cilium`. All pods lose networking. New pods stuck in ContainerCreating. Cluster partially broken.",
    [LI("CNI config removed but no replacement: /etc/cni/net.d/05-cilium.conflist deleted. Kubelet can't set up pod network."), LI("No alternative CNI installed: Cilium was the only CNI. Cluster has no network fabric now."), LI("Existing pod veth pairs deleted: Cilium agent removed veth pairs on shutdown. Existing pods lose connectivity."), LI("BPF programs unloaded: all eBPF-based routing/policy gone. Packets dropped by kernel."), LI("IPAM state lost: pod IPs may conflict after reinstall of new CNI.")],
    [LI("iptables rules left over causing partial connectivity", "cause-less-likely"), LI("Conntrack entries stale after CNI removal", "cause-less-likely"), LI("Node routing table stale with Cilium routes", "cause-less-likely"), LI("bpffs not cleaned up causing mount issues for new CNI", "cause-less-likely"), LI("Cilium endpoints stuck in terminating", "cause-less-likely")],
    [LI("No migration plan: Cilium uninstalled without new CNI ready", "cause-new-cluster"), LI("All nodes affected simultaneously (no drain)", "cause-new-cluster"), LI("Production cluster used as test environment", "cause-new-cluster"), LI("No backup of Cilium config before uninstall", "cause-new-cluster"), LI("Uninstall command run on wrong cluster context", "cause-new-cluster")],
    "BEFORE uninstall: have new CNI ready. Drain one node at a time. `/etc/cni/net.d/` must have new CNI config before removing Cilium.",
    "1. BEFORE uninstalling: deploy new CNI (Calico, Flannel, etc.)<br>2. Drain one node: `kubectl drain node-1 --ignore-daemonsets`<br>3. Uninstall Cilium from that node<br>4. Install new CNI on that node<br>5. Uncordon: `kubectl uncordon node-1`<br>6. Repeat for each node",
    "NEVER uninstall Cilium without a replacement CNI ready. For anihpj: migrate node-by-node: drain → uninstall Cilium → install new CNI → uncordon. This preserves pod connectivity throughout migration."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in9", "Air-Gapped Install — Image Pull Failures",
    "Cilium installed in air-gapped environment. All pods in ImagePullBackOff. Can't reach quay.io/cilium from isolated network.",
    [LI("Images not mirrored: agent, operator, hubble-relay, hubble-ui, clustermesh-apiserver, preflight, envoy. All must be in private registry."), LI("Image tag mismatch: mirrored images must have exact tags matching Helm chart version."), LI("Registry authentication: private registry needs imagePullSecrets in Cilium ServiceAccount or DaemonSet."), LI("Helm values not updated: `image.repository`, `operator.image.repository`, etc. must point to private registry."), LI("Init container image also needs mirroring: Cilium uses init containers for CNI setup and sysdump.")],
    [LI("Private registry CA not trusted by nodes", "cause-less-likely"), LI("Registry rate limiting (even for private registries)", "cause-less-likely"), LI("Image architecture mismatch (arm64 vs amd64)", "cause-less-likely"), LI("Helm chart downloaded but images not mirrored in parallel", "cause-less-likely"), LI("Digest-based references not updated to private registry", "cause-less-likely")],
    [LI("Air-gap not detected during planning", "cause-new-cluster"), LI("No private registry available", "cause-new-cluster"), LI("Image list not extracted from Helm chart", "cause-new-cluster"), LI("Helm chart not available offline", "cause-new-cluster"), LI("No image sync automation (Skopeo/Crane)", "cause-new-cluster")],
    "`kubectl describe pod -n kube-system -l k8s-app=cilium` — check image pull errors. `helm show values cilium/cilium | grep image` — all image references.",
    "1. Extract all images: `helm template cilium cilium/cilium | grep 'image:' | sort -u`<br>2. Mirror: `skopeo copy docker://quay.io/cilium/cilium:v1.15 docker://my-registry/cilium/cilium:v1.15`<br>3. Update Helm values: `--set image.repository=my-registry/cilium/cilium`<br>4. Set imagePullSecrets for private registry auth<br>5. Download Helm chart: `helm pull cilium/cilium --version v1.15`",
    "Air-gap = mirror ALL images first. For anihpj: list all images (`helm template | grep image:`), mirror to internal registry, update Helm values. Test in non-air-gapped first, then replicate to isolated environment."
)

cat5 += TS(5, "INSTALLATION", "🟠", "in10", "Wrong Cloud Provider Defaults — Suboptimal Performance",
    "Cilium installed with default Helm values on EKS/AKS/GKE. Performance poor, some features broken. Routing inefficient.",
    [LI("Cloud auto-detection overridden: Cilium auto-detects cloud but custom values may override. Check `cilium config` for ipam.mode, routingMode."), LI("EKS: should use eni IPAM mode, not cluster-pool. `--set ipam.mode=eni`."), LI("AKS: should use azure IPAM mode. `--set ipam.mode=azure`."), LI("GKE: needs specific settings for Dataplane V2 compatibility. GKE auto-pilot has restrictions."), LI("Security groups not configured: cloud firewall may block VXLAN/Geneve between nodes.")],
    [LI("Instance type limits: AWS ENI has IP limits per instance type", "cause-less-likely"), LI("Cloud NAT gateway for egress interfering with Cilium routing", "cause-less-likely"), LI("Cloud LoadBalancer health checks conflicting with Cilium NodePort", "cause-less-likely"), LI("Managed node group replacing custom node config", "cause-less-likely"), LI("Cloud API rate limiting for IP assignment (ENI/Azure)", "cause-less-likely")],
    [LI("cilium install without cloud-specific flags", "cause-new-cluster"), LI("Default Helm values used for production cloud deployment", "cause-new-cluster"), LI("Cloud provider CNI not considered for chaining", "cause-new-cluster"), LI("No cloud-specific testing before production", "cause-new-cluster"), LI("Documentation for another cloud provider followed", "cause-new-cluster")],
    "`cilium status | grep -E 'IPAM|Routing|Encapsulation'`. Check cloud-specific docs. EKS: eni mode. AKS: azure mode. GKE: geneve with specific settings.",
    "1. EKS: `--set ipam.mode=eni --set eni.enabled=true --set routingMode=native`<br>2. AKS: `--set ipam.mode=azure --set azure.enabled=true`<br>3. GKE: `--set ipam.mode=kubernetes --set tunnel=geneve`<br>4. Check security groups allow inter-node UDP 8472/6081<br>5. Review cloud-specific Cilium docs",
    "Cloud-specific Cilium setup matters. For anihpj: if running on EKS, use ENI mode for native AWS networking performance. Default cluster-pool mode works but adds unnecessary overlay overhead in cloud environments."
)

print("✅ CAT5 generated: 10 issues")

# =====================================================================
# CAT6: CLUSTER MESH (CM1-CM10), CAT7: eBPF (EB1-EB10), CAT8: BGP (BG1-BG6)
# =====================================================================

cat6 = CAT_SECTION(6, "Cluster Mesh", "CM1-CM10", "10 troubleshooting issues covering Cluster Mesh connectivity, etcd, global services, cross-cluster policies, and Egress Gateway.")
cat6 += SH("cm1", "🌐 CM1–CM5: Cluster Mesh Connectivity &amp; etcd")
cat6 += TS(6, "CLUSTER MESH", "🟢", "cm1", "Cluster Mesh Not Connecting — Clusters Isolated",
    "`cilium clustermesh connect` succeeds but `cilium clustermesh status` shows clusters disconnected. No cross-cluster pod communication.",
    [LI("etcd unreachable: shared etcd must be accessible from ALL clusters. Check `nc -zv <etcd-ip> 2379` from Cilium nodes."), LI("TLS certs mismatch: certs generated per cluster must share same CA. `cilium clustermesh status` shows TLS errors."), LI("Network between nodes: all worker nodes must have IP reachability between clusters. Check firewalls."), LI("Non-overlapping pod CIDRs: critical requirement. Check `cilium config | grep cluster-pool-ipv4-cidr` per cluster."), LI("Unique cluster.id and cluster.name: must be different per cluster. `cilium config | grep cluster-id`.")],
    [LI("etcd cluster split-brain causing inconsistent state", "cause-less-likely"), LI("MTU mismatch between cluster networks", "cause-less-likely"), LI("DNS for etcd resolving to wrong IP in one cluster", "cause-less-likely"), LI("etcd defrag needed: too many revisions", "cause-less-likely"), LI("Firewall stateful rule dropping long-lived etcd watch connection", "cause-less-likely")],
    [LI("Shared etcd not provisioned", "cause-new-cluster"), LI("Cluster IDs not set or duplicated", "cause-new-cluster"), LI("Pod CIDRs overlapping (both clusters use 10.0.0.0/8)", "cause-new-cluster"), LI("TLS certs not generated with correct cluster IDs", "cause-new-cluster"), LI("cilium clustermesh enable not run on each cluster", "cause-new-cluster")],
    "`cilium clustermesh status`. `kubectl exec -n kube-system ds/cilium -- nc -zv <etcd> 2379`. Non-overlapping CIDRs: MUST be unique. Cluster IDs: MUST be 1, 2, 3...",
    "1. Verify etcd: `kubectl exec ds/cilium -- nc -zv <etcd-ip> 2379`<br>2. Check CIDRs: `cilium config | grep cluster-pool` — must NOT overlap<br>3. Check IDs: `cilium config | grep cluster-id` — must be unique<br>4. Regenerate certs: `cilium clustermesh disable; cilium clustermesh enable`<br>5. `cilium clustermesh status` — should show connected",
    "Cluster Mesh = shared etcd + unique IDs + non-overlapping CIDRs + network connectivity. For anihpj: start with two small test clusters before attempting production mesh. The etcd is the heart — monitor it closely."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm2", "Global Service — Backends Not Aggregating Across Clusters",
    "Service annotated with `global-service: true` but only shows local backends. `cilium service list` shows backends from only one cluster.",
    [LI("Annotation missing on one cluster: BOTH clusters need the annotation on the SAME service name/namespace."), LI("Service name mismatch: namespace and name must match exactly across clusters."), LI("Cluster Mesh etcd not syncing: check `cilium clustermesh status` for identity/service sync status."), LI("Service type not supported: some service types (ExternalName, headless) don't aggregate across clusters."), LI("CiliumEndpointSlice not enabled: global services rely on CES for backend propagation.")],
    [LI("Service port definitions different across clusters", "cause-less-likely"), LI("Backend labels don't match service selector in remote cluster", "cause-less-likely"), LI("Remote backends in NotReady state", "cause-less-likely"), LI("etcd watch on service key not triggering update", "cause-less-likely"), LI("Service affinity set to 'local' preventing remote backends", "cause-less-likely")],
    [LI("Annotation only on one cluster's service", "cause-new-cluster"), LI("Service created with different names across clusters", "cause-new-cluster"), LI("Cluster Mesh not fully connected", "cause-new-cluster"), LI("Global service feature not understood", "cause-new-cluster"), LI("Testing with kubectl from only one cluster", "cause-new-cluster")],
    "`cilium clustermesh status` — services synced? `cilium service list` — backends with cluster-id prefix. `kubectl get svc -n <ns> <name> -o yaml` on BOTH clusters.",
    "1. Verify annotation on BOTH clusters: `kubectl annotate svc <name> -n <ns> io.cilium/global-service=true`<br>2. `cilium clustermesh status` — check services synced<br>3. `cilium service list` — backends from all clusters?<br>4. `hubble observe --to-service <ns>/<name>` — see cross-cluster flows<br>5. Check service affinity: `io.cilium/service-affinity: none`",
    "Global services = same VIP in all clusters, backends aggregated. For anihpj: create identical Service YAML in both clusters, annotate BOTH with global-service=true. Use service-affinity to control routing preference."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm3", "Cross-Cluster Pod Communication — Packets Blackholed",
    "Cluster Mesh connected, but pod in cluster-1 can't ping pod in cluster-2. Hubble shows packets leaving cluster-1 but never arriving at cluster-2.",
    [LI("Tunnel between clusters not established: `ip link show cilium_vxlan` — must be UP. Tunnel carries cross-cluster traffic."), LI("Node routes missing for remote cluster: in native routing, each node needs routes to remote pod CIDRs."), LI("Firewall between clusters: cloud security groups/firewall must allow UDP 8472 (VXLAN) or 6081 (Geneve)."), LI("MTU blackhole: tunnel overhead (50 bytes) + cross-cluster link MTU may be lower. Test with smaller packets."), LI("Identity not propagated: remote pod identity not synced via etcd. `cilium identity list | grep <pod-ip>`.")],
    [LI("etcd identity sync lag: new pods take seconds to propagate", "cause-less-likely"), LI("Cross-cluster connection tracking table full", "cause-less-likely"), LI("Network fabric has asymmetric routing between clusters", "cause-less-likely"), LI("Bidirectional tunnel: return path uses different tunnel", "cause-less-likely"), LI("Cilium cluster mesh apiserver not running", "cause-less-likely")],
    [LI("Tunnel mode not consistent across clusters", "cause-new-cluster"), LI("Node IPs not advertised between cluster networks", "cause-new-cluster"), LI("Cloud VPC peering not configured", "cause-new-cluster"), LI("Pod CIDRs overlapping (even partially)", "cause-new-cluster"), LI("No inter-cluster route propagation (BGP/static)", "cause-new-cluster")],
    "`cilium bpf tunnel list` — cross-cluster tunnel entries. `ip route | grep <remote-pod-cidr>`. `ping -M do -s 1400 <remote-pod-ip>` — MTU test.",
    "1. `ip link show cilium_vxlan` — UP on all nodes?<br>2. Check firewall: allow UDP 8472 (VXLAN) between ALL cluster nodes<br>3. MTU: `ping -M do -s 1400 <remote-pod-ip>` — find max<br>4. `cilium bpf tunnel list` — remote cluster tunnel entries?<br>5. `cilium clustermesh status` — identities synced?",
    "Cross-cluster pod comm = tunnel + routes + firewall. For anihpj: the #1 issue is firewall/security groups blocking inter-cluster node traffic. Always verify with `nc -u <remote-node> 8472` before debugging Cilium internals."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm4", "etcd Split-Brain — Both Clusters Active for Same Service",
    "etcd cluster for Cluster Mesh experiences split-brain. Both clusters think they own the same global service. Traffic loops or goes to wrong backends.",
    [LI("etcd network partition: etcd nodes can't reach each other. Each partition elects own leader. Check etcd metrics."), LI("Insufficient etcd nodes: 3-node etcd tolerates 1 failure. If 2 of 3 go down, quorum lost."), LI("etcd auto-compaction disabled: large etcd database causes slow replication, leading to timeouts."), LI("Cluster Mesh etcd separate from K8s etcd: best practice. Sharing K8s etcd = noisy neighbor issues."), LI("etcd client load balancer sending traffic to wrong node.")],
    [LI("etcd disk latency spikes causing leader election flapping", "cause-less-likely"), LI("etcd snapshot recovery from stale backup", "cause-less-likely"), LI("Network QoS dropping etcd heartbeat packets", "cause-less-likely"), LI("etcd member corruption requiring rejoin", "cause-less-likely"), LI("Cluster Mesh watching wrong etcd prefix", "cause-less-likely")],
    [LI("Single etcd node for Cluster Mesh (no HA)", "cause-new-cluster"), LI("K8s etcd reused for Cluster Mesh", "cause-new-cluster"), LI("etcd not monitored for quorum health", "cause-new-cluster"), LI("No etcd backup configured", "cause-new-cluster"), LI("etcd deployed in same failure domain as clusters", "cause-new-cluster")],
    "`etcdctl endpoint health --cluster`. `etcdctl endpoint status --cluster`. Odd number of etcd nodes (3, 5, 7). Separate from K8s etcd.",
    "1. etcd cluster: minimum 3 nodes, odd number, separate failure domains<br>2. `etcdctl endpoint health` — all healthy?<br>3. Monitor etcd metrics: leader changes, fsync duration, proposal failures<br>4. Auto-compaction: `--auto-compaction-mode=periodic --auto-compaction-retention=1h`<br>5. Backup: `etcdctl snapshot save /backup/clustermesh-$(date).db`",
    "Cluster Mesh etcd is the central nervous system. For anihpj: use dedicated etcd cluster (3 nodes minimum), NOT the K8s etcd. Monitor quorum health. Backup before any Cluster Mesh changes."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm5", "Cross-Cluster NetworkPolicy Not Enforcing",
    "CNP with `fromEntities: [cluster]` not allowing traffic from remote cluster. Or policy blocks all cross-cluster traffic unexpectedly.",
    [LI("fromEntities: [cluster] means ALL clusters: includes local too. For remote-only, use `fromEntities: [remote-cluster]`."), LI("Identity not synced: remote pod's identity must be in local etcd. Check `cilium identity list`."), LI("Policy enforcement mode: must be 'always' or 'default' (not 'never'). `cilium config | grep policy-enforcement`."), LI("CNP not applied in remote cluster: policies are cluster-scoped. Apply in BOTH clusters if needed."), LI("Label-based policy: labels must match remote pod's labels. Identities derived from labels.")],
    [LI("Policy imported but identity cache stale for remote pods", "cause-less-likely"), LI("CIDR-based policy not matching remote pod CIDRs", "cause-less-likely"), LI("L7 policy not applicable cross-cluster (needs Envoy proxying)", "cause-less-likely"), LI("Policy update propagation delay via etcd", "cause-less-likely"), LI("CiliumEndpoint status not updated for remote endpoints", "cause-less-likely")],
    [LI("No cross-cluster policies created (assumed open)", "cause-new-cluster"), LI("Default-deny policy also denies remote clusters", "cause-new-cluster"), LI("fromEntities: [cluster] not in policy", "cause-new-cluster"), LI("Policies only applied in one cluster", "cause-new-cluster"), LI("Misunderstanding cluster entity scope", "cause-new-cluster")],
    "`cilium identity list | grep <remote-cluster-id>`. `cilium policy get` — check entity rules. `hubble observe --verdict DROPPED` for cross-cluster drops.",
    "1. Add `fromEntities: [cluster]` or `[remote-cluster]` in CNP<br>2. Apply policy in BOTH clusters (policies are cluster-scoped)<br>3. `cilium identity list` — remote identities present?<br>4. `cilium policy get` — verify policy allows cross-cluster<br>5. `hubble observe --verdict DROPPED --from-cluster <id>`",
    "Cross-cluster policies need explicit entity rules. For anihpj: start with permissive policies between clusters, then tighten. Remember: `fromEntities: [cluster]` includes ALL clusters in the mesh, including local."
)

# CM6-CM10: Egress GW & Advanced
cat6 += SH("cm6", "🚪 CM6–CM10: Egress Gateway &amp; Advanced Cluster Mesh")
cat6 += TS(6, "CLUSTER MESH", "🟢", "cm6", "Egress Gateway — Traffic Not Exiting via Gateway Node",
    "CiliumEgressGatewayPolicy created but pod egress still exits from its own node. Gateway node configured but not used.",
    [LI("Gateway node label mismatch: policy nodeSelector must match labels on gateway nodes. `kubectl get nodes -l <label>`."), LI("Egress IP conflict: egress IP must not be assigned to any node interface. Must be a 'floating' IP."), LI("Policy destination CIDRs wrong: pod traffic only matches if destination matches policy CIDRs."), LI("Egress Gateway not compatible with L7 policies: any L7 rule auto-disables Egress GW for that endpoint."), LI("CiliumEndpointSlice (CES) incompatibility: Egress GW doesn't work with CES enabled. Disable CES.")],
    [LI("Kernel IP forwarding disabled on gateway node", "cause-less-likely"), LI("Source NAT (SNAT) not working for egress traffic", "cause-less-likely"), LI("Gateway node NIC doesn't have route to egress destination", "cause-less-likely"), LI("Conntrack entries for egress flows conflicting", "cause-less-likely"), LI("Multiple egress policies with overlapping CIDRs", "cause-less-likely")],
    [LI("Egress GW not enabled in Helm: `--set egressGateway.enabled=true`", "cause-new-cluster"), LI("Gateway node not labeled for policy selection", "cause-new-cluster"), LI("Egress IP not allocated from dedicated pool", "cause-new-cluster"), LI("CES enabled (incompatible with Egress GW)", "cause-new-cluster"), LI("Policy namespace selector not matching pod namespace", "cause-new-cluster")],
    "`cilium status | grep Egress`. `kubectl get cegp -A`. `kubectl get nodes -l <gateway-label>`. `cilium-dbg bpf egress list`.",
    "1. Enable: `--set egressGateway.enabled=true`<br>2. Label gateway node: `kubectl label node <gw-node> cilium.io/egress-gateway=true`<br>3. Create CiliumEgressGatewayPolicy with nodeSelector<br>4. Verify: `cilium-dbg bpf egress list`<br>5. Test: `kubectl exec <pod> -- curl ifconfig.me` (should show egress IP)",
    "Egress GW gives fixed source IP for outbound traffic. For anihpj: label dedicated gateway nodes, create policy for specific destination CIDRs. Remember: incompatible with L7 policies and CES. Choose: L7 inspection OR fixed egress IP."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm7", "Cluster Mesh TLS Cert Rotation — Connection Lost",
    "Rotated Cluster Mesh TLS certs. Now clusters can't connect. `cilium clustermesh status` shows TLS errors. Cross-cluster traffic stopped.",
    [LI("New certs not distributed to all clusters: each cluster needs updated certs before old ones expire."), LI("CA changed without updating trust chain: if root CA changed, all certs must be reissued by new CA."), LI("Cert SAN/CN mismatch: certs include cluster IDs in SAN. New cert must include correct cluster IDs."), LI("Old cert cache: Cilium agent may have cached old cert. Restart agents after cert rotation."), LI("Intermediate cert not included: full chain must be in cert file. Missing intermediate = TLS failure.")],
    [LI("Cert not valid yet (clock skew between clusters)", "cause-less-likely"), LI("Private key not matching new certificate", "cause-less-likely"), LI("Cert format changed (PEM vs DER)", "cause-less-likely"), LI("etcd also needs new TLS certs for the new CA", "cause-less-likely"), LI("Cluster Mesh apiserver pod using old cert mount", "cause-less-likely")],
    [LI("Cert rotation not planned before expiry", "cause-new-cluster"), LI("No cert monitoring/alerting for expiry", "cause-new-cluster"), LI("Manual cert generation with errors", "cause-new-cluster"), LI("Only one cluster's cert rotated", "cause-new-cluster"), LI("No rollback plan if rotation fails", "cause-new-cluster")],
    "`cilium clustermesh status` — TLS errors. `openssl x509 -in <cert> -text -noout` — check expiry and SAN. Cert rotation must be coordinated across all clusters.",
    "1. Generate new certs with same CA for all clusters<br>2. Distribute new certs to all clusters first (don't delete old yet)<br>3. Restart Cluster Mesh apiserver in each cluster<br>4. `cilium clustermesh status` — verify all connected<br>5. Remove old certs after 24h verification period",
    "TLS cert rotation for Cluster Mesh = coordinated operation. For anihpj: use cert-manager to auto-rotate, or set calendar reminders 30 days before expiry. Rotate ALL clusters within same maintenance window."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm8", "Cluster Mesh Performance — High Latency Cross-Cluster",
    "Cross-cluster pod-to-pod latency 10x higher than same-cluster. Simple ping: 2ms local, 50ms cross-cluster. Throughput also degraded.",
    [LI("Geographic distance: clusters in different regions have inherent latency. Speed of light: ~1ms per 200km."), LI("Tunnel encapsulation overhead: VXLAN adds 50 bytes, may cause fragmentation. Use native routing if possible."), LI("Network path suboptimal: traffic may hairpin through shared etcd location or VPN concentrator."), LI("MTU issues: fragmentation adds latency. Test path MTU: `ping -M do -s <size> <remote-pod>`."), LI("etcd latency: identity/service lookups may hit slow etcd. Check etcd disk latency.")],
    [LI("Inter-cluster link saturated: bandwidth contention", "cause-less-likely"), LI("VPN tunnel encryption overhead on top of VXLAN", "cause-less-likely"), LI("TCP incast/congestion on cross-cluster path", "cause-less-likely"), LI("Intermediate router buffer bloat", "cause-less-likely"), LI("DNS resolution for remote services slow", "cause-less-likely")],
    [LI("Clusters deployed in different continents", "cause-new-cluster"), LI("No latency requirements defined before mesh setup", "cause-new-cluster"), LI("Low-bandwidth inter-cluster link", "cause-new-cluster"), LI("Tunnel mode when native routing is possible", "cause-new-cluster"), LI("No latency monitoring between clusters", "cause-new-cluster")],
    "`cilium-health status` — cross-cluster latency. Native routing > tunnel for cross-cluster. Co-locate clusters in same region for low latency.",
    "1. `cilium-health status` — measure cross-cluster latency<br>2. Use native routing (not tunnel) for same-region clusters<br>3. Ensure direct network path (no hairpin through VPN)<br>4. Test with `ping -M do -s 1400` <remote-pod> for MTU<br>5. Monitor: Prometheus latency metrics per cross-cluster path",
    "Cross-cluster latency = physics + network. For anihpj: if clusters are in different regions, expect 20-50ms minimum. Design your app to tolerate cross-region latency. Use service affinity to prefer local backends."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm9", "Egress Gateway Failover — Single Point of Failure",
    "Only one gateway node labeled. When it goes down, ALL egress traffic stops. Pods can't reach external services until gateway recovers.",
    [LI("Single gateway node: Egress GW policy uses nodeSelector matching only one node. No redundancy."), LI("No automatic failover: if labeled node dies, egress stops. Need multiple gateway nodes."), LI("Egress IP doesn't float: if gateway IP is tied to one node, failover requires IP reassignment."), LI("Health check missing: no monitoring for gateway node availability."), LI("No standby gateway: no second node with same labels for failover.")],
    [LI("BGP not configured for egress IP advertisement on failover", "cause-less-likely"), LI("Conntrack state not synced between gateway nodes", "cause-less-likely"), LI("Egress policy sticky to first gateway node", "cause-less-likely"), LI("ARP cache on upstream router caching old gateway MAC", "cause-less-likely"), LI("Kubernetes Lease for egress not releasing fast enough", "cause-less-likely")],
    [LI("Single gateway = single point of failure", "cause-new-cluster"), LI("Gateway node not redundant by design", "cause-new-cluster"), LI("No failover testing performed", "cause-new-cluster"), LI("Egress GW configured without understanding failover behavior", "cause-new-cluster"), LI("Gateway running other critical workloads", "cause-new-cluster")],
    "Label multiple gateway nodes: `kubectl label node gw-1 gw-2 cilium.io/egress-gateway=true`. Cilium auto-distributes egress across labeled nodes. Test failover by cordoning one gateway.",
    "1. Label multiple gateway nodes with same label<br>2. Verify: `kubectl get nodes -l cilium.io/egress-gateway=true`<br>3. Cilium auto-distributes: no manual config needed<br>4. Test failover: `kubectl cordon gw-1` — traffic moves to gw-2<br>5. Use BGP for egress IP advertisement with multiple paths",
    "Egress GW = high availability by multiple gateway nodes. For anihpj: label at least 2 (preferably 3) gateway nodes. Cilium auto-distributes egress across them. If one fails, others take over automatically."
)

cat6 += TS(6, "CLUSTER MESH", "🟢", "cm10", "Cluster Mesh with Overlapping Services — Conflicting Backends",
    "Same service name exists in both clusters with global-service annotation, but backends from cluster-1 and cluster-2 have different container versions. Traffic routes unpredictably.",
    [LI("Service affinity not set: default 'none' = round-robin across ALL clusters. Set `io.cilium/service-affinity: local`."), LI("Backend versions differ: if both clusters run different app versions, users see inconsistent behavior."), LI("No canary/blue-green strategy: global service merges ALL backends blindly."), LI("Health checks not excluding unhealthy remote backends: a remote backend may be up but serving errors."), LI("Weight-based routing not configured: can't control what percentage goes to each cluster.")],
    [LI("Session affinity (sticky sessions) pinning users to wrong cluster version", "cause-less-likely"), LI("Backend capacity mismatch: one cluster has more replicas → gets more traffic", "cause-less-likely"), LI("Remote backend latency higher → slower responses for portion of users", "cause-less-likely"), LI("Cilium load balancer algorithm not considering backend location", "cause-less-likely"), LI("DNS caching by clients pointing to local cluster VIP even for remote backends", "cause-less-likely")],
    [LI("Both services deployed independently without coordination", "cause-new-cluster"), LI("No version consistency strategy across clusters", "cause-new-cluster"), LI("Global service used without understanding backend aggregation", "cause-new-cluster"), LI("GitOps deploying different versions to each cluster", "cause-new-cluster"), LI("No cross-cluster deployment orchestration", "cause-new-cluster")],
    "`cilium service list` — shows backends with cluster-id prefix. Use service affinity for predictable routing. Keep app versions consistent across clusters OR use canary routing.",
    "1. Set affinity: `kubectl annotate svc <name> io.cilium/service-affinity=local`<br>2. Keep same app version in both clusters (standard practice)<br>3. For canary: use different service names (api-stable, api-canary)<br>4. Monitor per-cluster backend health before aggregating<br>5. `hubble observe --to-service <ns>/<name>` — see backend distribution",
    "Global services merge backends from all clusters. For anihpj: keep app versions identical across clusters. If you need canary across clusters, use separate services with traffic split via CNP, not global-service aggregation."
)

print("✅ CAT6 generated: 10 issues")

# =====================================================================
# CAT7: eBPF (EB1-EB10)
# =====================================================================
cat7 = CAT_SECTION(7, "eBPF", "EB1-EB10", "10 troubleshooting issues covering BPF verifier failures, map limits, CO-RE issues, bpftool debugging, program limits, and XDP/TC hook problems.")
cat7 += SH("eb1", "🧬 EB1–EB5: eBPF Program &amp; Map Issues")
cat7 += TS(7, "eBPF", "🟣", "eb1", "eBPF Verifier Rejecting Cilium Programs",
    "Cilium agent logs show 'BPF program rejected by verifier'. Agent won't start. `cilium status` shows BPF errors. Certain features broken.",
    [LI("Kernel too old: eBPF features require specific kernel versions. 5.10+ recommended. `uname -r`."), LI("BTF (BPF Type Format) missing: CO-RE needs BTF. `ls /sys/kernel/btf/`. Kernel 5.4+ with CONFIG_DEBUG_INFO_BTF."), LI("Program complexity too high: verifier limit ~1M instructions (5.1+). Older kernels have lower limits."), LI("Kernel config missing eBPF options: CONFIG_BPF, CONFIG_BPF_SYSCALL, CONFIG_BPF_JIT must be enabled."), LI("JIT compiler disabled: `sysctl net.core.bpf_jit_enable`. Must be 1 for performance. Verifier may reject without JIT.")],
    [LI("Spectre mitigation: kernel enables BPF speculation barrier (slower but safer)", "cause-less-likely"), LI("Stack size limit (512 bytes) exceeded in complex program", "cause-less-likely"), LI("Helper function restricted by kernel lockdown mode", "cause-less-likely"), LI("BPF program array full (max tail calls)", "cause-less-likely"), LI("Memory locking limit (RLIMIT_MEMLOCK) too low", "cause-less-likely")],
    [LI("Kernel not compiled with required eBPF features", "cause-new-cluster"), LI("Running very old kernel (<4.19) with new Cilium", "cause-new-cluster"), LI("Custom kernel with eBPF features disabled", "cause-new-cluster"), LI("Cloud VM with restricted kernel (GKE Sandbox, Fargate)", "cause-new-cluster"), LI("BPF subsystem in kernel not enabled", "cause-new-cluster")],
    "`uname -r`. `ls /sys/kernel/btf/`. `sysctl net.core.bpf_jit_enable`. `grep CONFIG_BPF /boot/config-$(uname -r)`.",
    "1. Upgrade kernel to 5.10+ (or 5.4 with BTF)<br>2. Verify BTF: `ls /sys/kernel/btf/vmlinux`<br>3. Enable JIT: `sysctl -w net.core.bpf_jit_enable=1`<br>4. Check kernel config: `grep BPF /boot/config-$(uname -r)`<br>5. Use Cilium's CO-RE image for wider kernel compatibility",
    "eBPF verifier = safety guarantee. For anihpj: use a supported kernel (5.10+). Cilium's CO-RE image improves compatibility across kernel versions. AWS EKS optimized AMI, Ubuntu 22.04, and RHEL 9 all work well."
)

cat7 += TS(7, "eBPF", "🟣", "eb2", "BPF Map Limit Exhausted — Can't Create New Endpoints",
    "New pods stuck without network. Agent logs: 'cannot create BPF map: too many maps'. `bpftool map show | wc -l` shows thousands of maps.",
    [LI("Per-endpoint maps exhausted: each pod gets multiple BPF maps (policy, conntrack, LB, etc.). Max maps per system limited."), LI("Memory locked limit (RLIMIT_MEMLOCK) too low: BPF maps consume locked memory. `ulimit -l`."), LI("Map pinning failure: maps pinned to /sys/fs/bpf/. If bpffs full or inode exhausted, can't pin new maps."), LI("Cilium endpoint leak: deleted pods' endpoints not cleaned up. `cilium endpoint list` — stale endpoints."), LI("Identity allocation exhausted: max identities (default 65535) reached. `cilium identity list | wc -l`.")],
    [LI("Kernel memory fragmentation preventing large BPF map allocation", "cause-less-likely"), LI("BPF map creation rate limiting by kernel", "cause-less-likely"), LI("System-wide BPF map count sysctl limit", "cause-less-likely"), LI("Concurrent map creation from multiple Cilium agents on same node (race)", "cause-less-likely"), LI("Orphaned maps from Cilium agent restart not cleaned", "cause-less-likely")],
    [LI("Cluster scaling beyond expected pod count per node", "cause-new-cluster"), LI("No BPF map monitoring/alerting", "cause-new-cluster"), LI("RLIMIT_MEMLOCK not increased for Cilium", "cause-new-cluster"), LI("Stale endpoints from frequent pod churn", "cause-new-cluster"), LI("Map limit hit during load test / spike", "cause-new-cluster")],
    "`bpftool map show | wc -l`. `cilium endpoint list` — stale endpoints? `ulimit -l` — locked memory. `df -i /sys/fs/bpf` — inode exhaustion?",
    "1. `cilium endpoint list` — delete stale: `cilium endpoint delete <id>`<br>2. Increase RLIMIT_MEMLOCK for Cilium DaemonSet<br>3. `sysctl -w net.core.bpf_jit_limit=100000000`<br>4. Monitor: `bpftool map show | wc -l` trend over time<br>5. Reduce per-node pod density if at limit",
    "BPF maps are finite resources. For anihpj: monitor map count per node. If approaching limits, reduce pod density or increase kernel limits. `bpftool map show` is your friend for understanding map usage."
)

cat7 += TS(7, "eBPF", "🟣", "eb3", "bpftool Can't Dump Cilium Maps — Permission Denied",
    "`bpftool map dump pinned /sys/fs/bpf/tc/globals/cilium_ct4_global` returns 'Permission denied' or 'No such file'. Can't inspect Cilium's BPF state.",
    [LI("bpftool run as wrong user: must be root (or CAP_BPF+CAP_NET_ADMIN). `sudo bpftool map dump ...`."), LI("Map path wrong: Cilium pins maps at `/sys/fs/bpf/tc/globals/cilium_*`. Check `ls /sys/fs/bpf/tc/globals/`."), LI("Kernel lockdown: in lockdown mode, BPF map reads restricted. Check `cat /sys/kernel/security/lockdown`."), LI("bpffs mounted with wrong options: must be mounted with `mode=0700` or accessible by root."), LI("Map not pinned: not all Cilium maps are pinned. Per-endpoint maps may only exist in memory.")],
    [LI("SELinux context blocking bpftool access to bpffs", "cause-less-likely"), LI("AppArmor profile restricting bpftool", "cause-less-likely"), LI("Map created by one agent namespace, accessed from another", "cause-less-likely"), LI("bpftool binary too old for kernel's BPF features", "cause-less-likely"), LI("Map was deleted between listing and dumping (race)", "cause-less-likely")],
    [LI("bpftool not installed on nodes", "cause-new-cluster"), LI("User not aware bpftool needs root", "cause-new-cluster"), LI("Cilium maps in unexpected location", "cause-new-cluster"), LI("Lockdown security policy enabled on new kernel", "cause-new-cluster"), LI("No BPF debugging tools available", "cause-new-cluster")],
    "`sudo ls /sys/fs/bpf/tc/globals/`. `sudo bpftool map show pinned /sys/fs/bpf/tc/globals/cilium_ct4_global`. Use root or CAP_BPF.",
    "1. `sudo ls /sys/fs/bpf/tc/globals/` — list all pinned maps<br>2. `sudo bpftool map dump pinned /sys/fs/bpf/tc/globals/cilium_ct4_global`<br>3. Check lockdown: `cat /sys/kernel/security/lockdown` — should be 'none'<br>4. Install bpftool: `apt install bpftool` or from kernel source<br>5. Use `cilium bpf ct list` as alternative (CLI wrapper)",
    "bpftool = kernel-level visibility. For anihpj: install bpftool on all worker nodes for debugging. `sudo bpftool map show` gives you the full picture of Cilium's eBPF resource usage."
)

cat7 += TS(7, "eBPF", "🟣", "eb4", "BPF Conntrack Table Full — New Connections Dropped",
    "New TCP connections timeout. Hubble shows established connections work but new SYN packets dropped. `cilium bpf ct list` shows millions of entries.",
    [LI("Conntrack table size too small: default varies by kernel. LRU map auto-evicts but may be too slow. `cilium bpf ct list global | wc -l`."), LI("TCP TIME_WAIT entries accumulating: too many short-lived connections. Application needs connection pooling."), LI("Conntrack GC interval too long: stale entries not cleaned fast enough. `cilium config | grep conntrack-gc-interval`."), LI("UDP conntrack timeout: UDP 'connections' have long timeout (180s default). DNS queries can fill table."), LI("DSR or NAT mode creating asymmetric conntrack entries that don't get cleaned.")],
    [LI("Conntrack table fragmentation causing false 'full'", "cause-less-likely"), LI("BPF map pre-allocation causing unused reserved entries", "cause-less-likely"), LI("Kernel conntrack (nf_conntrack) conflicting with BPF conntrack", "cause-less-likely"), LI("Connection tracking for dropped packets (useless entries)", "cause-less-likely"), LI("Conntrack sync between agent restarts duplicating entries", "cause-less-likely")],
    [LI("Application with connection leak (no pooling)", "cause-new-cluster"), LI("No conntrack monitoring/alerting", "cause-new-cluster"), LI("Default conntrack table size for high-density cluster", "cause-new-cluster"), LI("Microservices with direct pod-to-pod without service", "cause-new-cluster"), LI("No connection reuse (HTTP/1.0 style)", "cause-new-cluster")],
    "`cilium bpf ct list global | wc -l`. `bpftool map dump pinned .../cilium_ct4_global | wc -l`. Hubble: `hubble observe --verdict DROPPED --tcp-flags SYN`.",
    "1. Check table: `cilium bpf ct list global | wc -l`<br>2. Application fix: use HTTP keep-alive / connection pooling<br>3. Reduce conntrack GC interval: `cilium config set conntrack-gc-interval 300s`<br>4. Reduce UDP timeout: `cilium config set conntrack-udp-timeout 30s`<br>5. Scale: increase conntrack table size via Helm values",
    "Conntrack = connection tracking. For anihpj: if you see millions of entries, your app likely has a connection leak. Use connection pooling (Django: CONN_MAX_AGE for DB). Monitor conntrack size trend."
)

cat7 += TS(7, "eBPF", "🟣", "eb5", "CO-RE Relocation Failure — Wrong Kernel Struct Offsets",
    "Cilium agent logs show 'CO-RE relocation failed' or 'BTF type not found'. Agent falls back to non-CO-RE mode. Performance degraded.",
    [LI("BTF info missing: kernel compiled without CONFIG_DEBUG_INFO_BTF. `ls /sys/kernel/btf/vmlinux` — must exist."), LI("Kernel too old for BTF: BTF available since 4.18 but reliable since 5.4. Check kernel version."), LI("Cilium image not CO-RE: need cilium/cilium:vX.Y.Z (not -legacy). CO-RE images are default since 1.12."), LI("BTF mismatch: Cilium compiled against different kernel BTF than running kernel."), LI("Custom kernel with modified struct layouts: CO-RE can't resolve non-standard changes.")],
    [LI("BTF file corrupted or truncated on disk", "cause-less-likely"), LI("CO-RE requires CAP_SYS_ADMIN for BTF loading", "cause-less-likely"), LI("Kernel lockdown preventing BTF introspection", "cause-less-likely"), LI("Cilium compiled with wrong LLVM/clang version for CO-RE", "cause-less-likely"), LI("vmlinux BTF too large for BPF program complexity limit", "cause-less-likely")],
    [LI("Legacy kernel without BTF support", "cause-new-cluster"), LI("Cilium image type wrong (non-CO-RE for modern kernel)", "cause-new-cluster"), LI("Kernel config not checked before Cilium install", "cause-new-cluster"), LI("Custom kernel without debug info", "cause-new-cluster"), LI("Cloud minimal kernel without BTF", "cause-new-cluster")],
    "`ls /sys/kernel/btf/vmlinux`. `bpftool btf dump file /sys/kernel/btf/vmlinux | head`. Cilium CO-RE images since v1.12 are default.",
    "1. Check BTF: `ls -la /sys/kernel/btf/vmlinux` — must exist<br>2. Upgrade kernel to 5.4+ with BTF<br>3. Use CO-RE Cilium image (default since 1.12)<br>4. Verify: `cilium status | grep CO-RE`<br>5. Fallback: Cilium auto-falls back to non-CO-RE if BTF unavailable",
    "CO-RE = one eBPF binary for all kernel versions. For anihpj: use Cilium's CO-RE image with kernel 5.4+ that has BTF. If BTF is missing, Cilium falls back gracefully to legacy mode. AWS EKS, Ubuntu, and RHEL all support BTF."
)

# EB6-EB10: Advanced eBPF
cat7 += SH("eb6", "⚡ EB6–EB10: XDP, Tail Calls &amp; Performance")
cat7 += TS(7, "eBPF", "🟣", "eb6", "XDP Program Not Attaching — Acceleration Disabled",
    "`--set bpf.acceleration=native` set but XDP not active. `bpftool net show` shows no XDP programs. Performance not improved for DDoS protection.",
    [LI("Driver not supporting XDP: `ethtool -i <iface>` — driver must support native XDP. Common: mlx5, i40e, bnxt_en, virtio_net."), LI("XDP attached to wrong interface: Cilium attaches XDP to devices in `devices` config. Verify `cilium config | grep devices`."), LI("XDP offload mode: 'native' needs driver support. 'generic' mode works everywhere but slower. Try 'generic' as fallback."), LI("Kernel too old for XDP features: XDP improvements in newer kernels. 5.10+ recommended."), LI("XDP program already attached: only one XDP program per interface. Check for conflicts.")],
    [LI("XDP program verifier complexity too high for driver", "cause-less-likely"), LI("Multi-queue NIC with XDP requiring specific queue config", "cause-less-likely"), LI("XDP metadata not supported by driver", "cause-less-likely"), LI("Interrupt configuration conflicting with XDP polling", "cause-less-likely"), LI("XDP redirect to different NUMA node (performance impact)", "cause-less-likely")],
    [LI("bpf.acceleration set without checking driver support", "cause-new-cluster"), LI("Cloud VM with emulated NIC (no XDP native support)", "cause-new-cluster"), LI("Devices not specified in Cilium config", "cause-new-cluster"), LI("XDP feature expected but not needed for Cilium core", "cause-new-cluster"), LI("Generic XDP tried first and performance was poor (gave up)", "cause-new-cluster")],
    "`ethtool -i eth0 | grep driver`. `bpftool net show`. `cilium config | grep -E 'devices|acceleration'`. XDP = optional. TC is Cilium's primary hook.",
    "1. Check driver: `ethtool -i eth0` — supports native XDP?<br>2. Try generic: `--set bpf.acceleration=generic`<br>3. Verify: `bpftool net show | grep xdp`<br>4. Specify devices: `--set devices=eth0`<br>5. Accept: XDP is optional — Cilium's TC-based datapath works without it",
    "XDP = early packet drop (pre-SKB, very fast). For anihpj: XDP is optional optimization. Cilium's TC-based datapath is the workhorse. Only enable XDP if you have supported NICs and need DDoS protection."
)

cat7 += TS(7, "eBPF", "🟣", "eb7", "eBPF Tail Call Limit Exceeded — Policy Chain Truncated",
    "Complex Cilium policy chain hits tail call limit (33). Policies partially applied. Some rules silently skipped. Agent logs show 'tail call limit reached'.",
    [LI("Tail call limit = 33 per chain: Cilium chains TC ingress→policy→LB→forward. Complex CNP adds more hops."), LI("Too many CNP rules: each rule section may add tail calls. Combine rules to reduce hops."), LI("Multiple feature chains: encryption + L7 + bandwidth + egress GW can stack beyond 33."), LI("Per-endpoint program complexity: each endpoint has its own chain. Many pods = many chains (per-pod limit separate)."), LI("Kernel version: tail call limit increased in 5.10 (from 32 to 33). Still limited.")],
    [LI("Tail call map exhaustion (per-endpoint tail call map full)", "cause-less-likely"), LI("Indirect tail call recursion causing infinite loop protection trigger", "cause-less-likely"), LI("BPF prog array map fragmentation", "cause-less-likely"), LI("Prog array map update race during policy change", "cause-less-likely"), LI("Tail call not inlined by JIT causing extra instructions", "cause-less-likely")],
    [LI("Too many separate CNP rules (combine related rules)", "cause-new-cluster"), LI("All features enabled simultaneously (pick subset)", "cause-new-cluster"), LI("No awareness of tail call limit during policy design", "cause-new-cluster"), LI("Legacy kernel with lower tail call limits", "cause-new-cluster"), LI("Policy per-microservice pattern creating chain explosion", "cause-new-cluster")],
    "`bpftool prog show` — chain visualization. Each Cilium feature adds tail calls: policy=1-2, LB=1-2, encryption=1, host-routing=1, bandwidth=1. Budget: 33.",
    "1. Audit: `bpftool prog show | grep -c cilium`<br>2. Combine CNP rules into fewer sections<br>3. Disable unused features: `--set bandwidthManager.enabled=false`<br>4. Simplify policy: use broader CIDR rules instead of per-pod<br>5. Upgrade kernel to 5.10+ for slightly higher limits",
    "Tail call limit = 33 per chain. For anihpj: each feature (policy, LB, encryption, bandwidth, host-routing) adds to the chain. If you enable everything, you may hit the limit. Prioritize: policy + LB are essential, others are optional."
)

cat7 += TS(7, "eBPF", "🟣", "eb8", "BPF Program Pre-Compilation Failures — Agent Slow Start",
    "Cilium agent takes 5+ minutes to start. Logs show 'compiling BPF programs'. On pod churn, new endpoints take seconds to get network.",
    [LI("No CO-RE: without CO-RE, Cilium compiles eBPF for EACH endpoint from C source. Slow with many templates."), LI("LLVM/clang slow: eBPF compilation uses clang. Host CPU contention slows compile."), LI("Many endpoint templates: different policy configs per namespace = more unique program templates to compile."), LI("Template caching disabled: Cilium caches compiled templates. If cache cleared, recompiles all."), LI("initContainer doing compilation: Cilium pre-compiles in init container. If it times out, agent compiles at runtime.")],
    [LI("clang version incompatibility: too old or too new clang", "cause-less-likely"), LI("Compilation artifacts not cleaned → disk full", "cause-less-likely"), LI("Node CPU throttling (cloud burst credits exhausted)", "cause-less-likely"), LI("Compilation log level too verbose (compiling with -g)", "cause-less-likely"), LI("Kernel header mismatch causing recompilation", "cause-less-likely")],
    [LI("Non-CO-RE image used unnecessarily", "cause-new-cluster"), LI("Node under-provisioned for eBPF compilation", "cause-new-cluster"), LI("Thousands of pods per node (unique program templates)", "cause-new-cluster"), LI("No template caching strategy", "cause-new-cluster"), LI("Init container resource limits too low", "cause-new-cluster")],
    "Use CO-RE image (default). Check init container logs. `cilium status | grep -i compile`. Use `--set bpf.precompile=true` for pre-compilation.",
    "1. Use CO-RE image: `quay.io/cilium/cilium:v1.15` (not -legacy)<br>2. Pre-compile: `--set bpf.precompile=true` (init container does it)<br>3. Increase init container CPU: `--set resources.initContainer.cpu=500m`<br>4. Reduce pod density per node if startup times too high<br>5. Monitor: `kubectl logs ds/cilium -c init` for compilation time",
    "eBPF compilation speed matters. For anihpj: use CO-RE image (not legacy). CO-RE skips per-endpoint compilation — programs load directly. If startup is slow, check if you're accidentally using the legacy image."
)

cat7 += TS(7, "eBPF", "🟣", "eb9", "Perf Ring Buffer — Hubble Events Lost Under Load",
    "Under high traffic, Hubble drops events. `hubble observe` shows gaps in flow sequence. 'events lost' counter in Hubble metrics increasing.",
    [LI("Ring buffer too small: Hubble ring buffer for flows has fixed size. At high PPS, buffer fills faster than Relay reads."), LI("Hubble Relay too slow: single Relay instance reading from all agents. Add more Relay replicas or increase resources."), LI("Flow export not enabled: if not exporting, ring buffer is only storage. Enable export for buffer relief."), LI("CPU contention: Hubble's user-space reader shares CPU with agent. On overloaded nodes, reader starves."), LI("Filtering too aggressive: Hubble observes ALL flows. Use `--allowlist` and `--denylist` to filter at agent level.")],
    [LI("BPF ring buffer implementation (newer, better) vs perf buffer (older)", "cause-less-likely"), LI("Kernel perf subsystem overloaded from other tools", "cause-less-likely"), LI("IRQ affinity causing ring buffer processing on same CPU as traffic", "cause-less-likely"), LI("Memory pressure causing ring buffer page allocation failure", "cause-less-likely"), LI("Hubble gRPC stream backpressure from slow client", "cause-less-likely")],
    [LI("Hubble ring buffer size not tuned for traffic volume", "cause-new-cluster"), LI("Single Hubble Relay for large cluster", "cause-new-cluster"), LI("No flow export for buffer relief", "cause-new-cluster"), LI("Hubble filtering not configured at agent level", "cause-new-cluster"), LI("No monitoring of Hubble event loss metric", "cause-new-cluster")],
    "`hubble observe --output json | jq '.time' | head`. Hubble metrics: `hubble_flows_processed_total` vs `hubble_flows_lost_total`. Ring buffer size configurable.",
    "1. Monitor: `hubble_flows_lost_total` metric in Prometheus<br>2. Enable flow export to external storage (Kafka/ES)<br>3. Increase ring buffer: `--set hubble.ringBufferSize=32768`<br>4. Filter at agent: `--set hubble.exportAllowlist='{...}'`<br>5. Scale Hubble Relay: more replicas for more read throughput",
    "Hubble event loss = observability gap. For anihpj: enable flow export to Kafka/ES for long-term storage. Hubble's ring buffer is for real-time, not historical. Monitor loss rate — >1% indicates buffer tuning needed."
)

cat7 += TS(7, "eBPF", "🟣", "eb10", "Cilium eBPF Host Routing Not Accelerating",
    "eBPF Host Routing enabled but pod-to-pod latency unchanged. `cilium config | grep host-routing` shows true but no performance improvement.",
    [LI("Host routing only benefits same-node pod-to-pod: bypasses iptables/netfilter for veth→veth direct forwarding. Cross-node still uses tunnel/routing."), LI("Kernel too old: eBPF Host Routing optimal on 5.10+. Older kernels may not support full bypass."), LI("iptables still processing: if kube-proxy not fully replaced, iptables still in path. `iptables -t nat -L | wc -l`."), LI("BPF Host Routing program not attached: `bpftool prog show | grep host-routing`. Must see program on veth interfaces."), LI("Same-node traffic pattern missing: if all traffic is cross-node, host routing doesn't help. Test with same-node pods.")],
    [LI("veth driver not supporting XDP redirect for host routing", "cause-less-likely"), LI("Network namespace setup overhead dominating latency", "cause-less-likely"), LI("CPU governor not 'performance' — frequency scaling adds latency", "cause-less-likely"), LI("IRQ affinity causing cross-NUMA memory access for forwarding", "cause-less-likely"), LI("Conntrack lookup still happening even with host routing", "cause-less-likely")],
    [LI("Host routing enabled but KPR not strict", "cause-new-cluster"), LI("All traffic is cross-node (no same-node benefit)", "cause-new-cluster"), LI("Expected cross-node latency improvement (not how it works)", "cause-new-cluster"), LI("No latency baseline before enabling", "cause-new-cluster"), LI("Kernel doesn't support eBPF redirect for veth", "cause-new-cluster")],
    "`bpftool prog show | grep host`. `cilium bpf endpoint list` — look for host-routing flag. Host routing benefits same-node traffic most. Cross-node uses tunnel/native routing.",
    "1. Verify: `cilium config | grep host-routing` — true?<br>2. `bpftool prog show | grep host` — program attached?<br>3. Test same-node pods: `kubectl exec pod-a -- ping pod-b` (same node)<br>4. Ensure KPR is strict (iptables not in path)<br>5. Measure: `hubble observe --from-pod a --to-pod b` — latency visible",
    "eBPF Host Routing = veth→veth direct forwarding, bypassing host network stack. For anihpj: benefits are most visible with same-node pod-to-pod traffic. If all your pod communication is cross-node, host routing won't help much."
)

print("✅ CAT7 generated: 10 issues")

# =====================================================================
# CAT8: BGP & EXTERNAL (BG1-BG6)
# =====================================================================
cat8 = CAT_SECTION(8, "BGP & External Networking", "BG1-BG6", "6 troubleshooting issues covering BGP peering, LB IPAM, L2 announcements, and external connectivity.")
cat8 += SH("bg1", "🌍 BG1–BG6: BGP, LB IPAM &amp; External Networking")
cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg1", "BGP Peering Not Establishing — Session Stuck in Connect/Active",
    "CiliumBGPPeeringPolicy created but BGP session never reaches Established. `cilium-dbg bgp peers` shows 'Connect' or 'Active'. No routes advertised.",
    [LI("Peer IP unreachable: `ping <peer-router-ip>` from Cilium node. Must be L3 reachable. Check routes/firewall."), LI("ASN mismatch: local ASN in policy must match Cilium config `cluster.id` (if using cluster ID as ASN) or explicit ASN."), LI("BGP port 179 blocked: firewall/security group must allow TCP 179 between Cilium node and peer router."), LI("nodeSelector not matching: policy nodeSelector must match at least one node. `kubectl get nodes -l <selector>`."), LI("GoBGP not running: `cilium status | grep BGP`. BGP control plane must be active.")],
    [LI("MD5 password mismatch (if authentication configured)", "cause-less-likely"), LI("Peer router expecting multi-hop BGP (TTL >1) but Cilium using TTL=1", "cause-less-likely"), LI("BGP session collision detection (both sides trying to connect)", "cause-less-likely"), LI("Peer router has max-prefix limit exceeded for this session", "cause-less-likely"), LI("BGP timer mismatch: hold/keepalive timers incompatible", "cause-less-likely")],
    [LI("BGP not enabled in Helm: `--set bgp.enabled=true`", "cause-new-cluster"), LI("No BGP peer router configured (ToR/upstream)", "cause-new-cluster"), LI("CiliumBGPPeeringPolicy not created", "cause-new-cluster"), LI("Node not in nodeSelector scope", "cause-new-cluster"), LI("Firewall blocking TCP 179", "cause-new-cluster")],
    "`cilium-dbg bgp peers`. `cilium status | grep BGP`. `kubectl get ciliumbgppeeringpolicy`. `nc -zv <peer-ip> 179`. Check nodeSelector matches nodes.",
    "1. `cilium-dbg bgp peers` — session state?<br>2. `ping <peer-router-ip>` from Cilium node<br>3. `nc -zv <peer-ip> 179` — TCP port open?<br>4. Check selector: `kubectl get nodes -l <selector>` — nodes match?<br>5. `cilium status | grep BGP` — BGP control plane OK?",
    "BGP peering = L3 reachability + TCP 179 + correct ASNs. For anihpj: the #1 issue is firewall blocking TCP 179. Always verify with `nc -zv <peer-ip> 179` from a Cilium node before debugging Cilium BGP internals."
)

cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg2", "LB IPAM — Service Stuck in Pending (No External IP Assigned)",
    "LoadBalancer Service created but external IP stays `<pending>`. `kubectl describe svc` shows 'no IPs available'. LB IPAM not working.",
    [LI("LB IPAM not enabled: `--set lbIPAM.enabled=true`. Check `cilium config | grep lb-ipam`."), LI("No CiliumLoadBalancerIPPool created: IPAM needs a pool CRD with CIDR ranges. `kubectl get ciliumloadbalancerippool`."), LI("Pool exhausted: all IPs from pool assigned to existing services. Add more CIDRs or remove unused services."), LI("Service namespace/name not matching pool selector: pool can have serviceSelector to limit which services get IPs."), LI("Cilium operator not running: operator assigns IPs from pool. `kubectl get pods -n kube-system -l name=cilium-operator`.")],
    [LI("IP conflict with existing node/VM IP in same CIDR", "cause-less-likely"), LI("Pool CIDR overlaps with cluster pod/service CIDR", "cause-less-likely"), LI("Cilium operator leader election issue delaying IP assignment", "cause-less-likely"), LI("Multiple pools with overlapping selectors causing conflict", "cause-less-likely"), LI("Service type changed from LoadBalancer after IP assigned", "cause-less-likely")],
    [LI("lbIPAM.enabled not in Helm values", "cause-new-cluster"), LI("No IPPool CRD created", "cause-new-cluster"), LI("Pool CIDR too small for expected services", "cause-new-cluster"), LI("cilium-operator not deployed", "cause-new-cluster"), LI("LB IPAM feature not documented in deployment runbook", "cause-new-cluster")],
    "`kubectl get ciliumloadbalancerippool -A`. `kubectl describe svc <name>`. `cilium status | grep LB-IPAM`. `cilium-dbg bgp routes advertised` — check if IP is being announced.",
    "1. Create IPPool: `kubectl apply -f ippool.yaml` with CIDR: 192.168.100.0/24<br>2. Enable: `--set lbIPAM.enabled=true`<br>3. `kubectl get svc <name>` — wait for EXTERNAL-IP<br>4. Check pool: `kubectl describe ciliumloadbalancerippool <name>`<br>5. Combine with BGP to advertise assigned IPs",
    "LB IPAM = Cilium's built-in LoadBalancer IP allocator. For anihpj: create an IPPool with enough IPs for all your services, enable LB IPAM, then use BGP to advertise these IPs to the external network. No cloud provider needed!"
)

cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg3", "BGP Routes Advertised But Traffic Blackholed",
    "BGP session Established. Routes visible on peer router. But external traffic to Service LoadBalancer IP arrives at node and gets dropped.",
    [LI("Service backend not on BGP speaker node: if externalTrafficPolicy=Local, traffic arriving at node without backend is dropped."), LI("NodePort not listening: BGP advertises node IP, but NodePort range not open. Check `iptables -t nat -L CILIUM-NODEPORT`."), LI("KPR not strict: if kube-proxy still running, NodePort is handled by kube-proxy, not Cilium. iptables rules may conflict."), LI("Backend pod not ready: Cilium only advertises routes for services with at least one ready backend."), LI("BGP next-hop unreachable: peer router can't reach the advertised next-hop (Cilium node IP).")],
    [LI("ECMP (multi-path) hash causing packets to land on wrong node", "cause-less-likely"), LI("Reverse path filter (rp_filter) on node dropping external traffic", "cause-less-likely"), LI("Conntrack for external traffic not working (asymmetric path)", "cause-less-likely"), LI("LoadBalancer IP not assigned to any node interface", "cause-less-likely"), LI("ARP for LoadBalancer IP not answered (L2 scenario)", "cause-less-likely")],
    [LI("BGP route advertised before service has ready backends", "cause-new-cluster"), LI("externalTrafficPolicy not configured", "cause-new-cluster"), LI("KPR not strict (iptables may handle NodePort unreliably)", "cause-new-cluster"), LI("Backend pods not scheduled on BGP speaker nodes", "cause-new-cluster"), LI("No end-to-end test from external host to service IP", "cause-new-cluster")],
    "`cilium service list` — service IP with backends. `cilium-dbg bgp routes advertised`. `curl --connect-timeout 3 <service-external-ip>:<port>` from external host.",
    "1. Verify backends: `cilium service list | grep <svc-ip>`<br>2. Check KPR: `cilium status | grep KubeProxyReplacement` — must be 'Strict'<br>3. externalTrafficPolicy: `kubectl get svc <name> -o yaml | grep externalTrafficPolicy`<br>4. Ensure backends on BGP speaker nodes (or set policy to Cluster)<br>5. Test: `curl <external-ip>:<port>` from outside cluster",
    "BGP route advertisement ≠ traffic working. For anihpj: after BGP is up, test with `curl` from an external host. The #1 issue: externalTrafficPolicy=Local with no backend on the ingress node. Use `externalTrafficPolicy: Cluster` for simpler setup."
)

cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg4", "L2 Announcements — Service IP Not Responding to ARP",
    "L2 Announcements configured for bare metal. Service LoadBalancer IP doesn't respond to ARP. External clients can't resolve MAC for service IP.",
    [LI("L2 Announcements not enabled: `--set l2announcements.enabled=true` (beta feature)."), LI("CiliumL2AnnouncementPolicy not created: CRD must exist with service selector. `kubectl get ciliuml2announcementpolicy`."), LI("Leader election not complete: only one node per service holds lease. Check `kubectl get lease -n kube-system | grep l2announce`."), LI("Service IP not in L2 domain: L2 = same broadcast domain. Works only within same VLAN/subnet — not across routers."), LI("ARP responder not active: node with lease should respond to ARP for service IP. Check `ip neigh show | grep <svc-ip>`.")],
    [LI("ARP suppression on switch (ARP inspection) blocking gratuitous ARP", "cause-less-likely"), LI("Multiple nodes responding to ARP (race condition)", "cause-less-likely"), LI("ARP cache timeout on client: old MAC cached", "cause-less-likely"), LI("VLAN tagging mismatch between node and client", "cause-less-likely"), LI("Network switch MAC table overflow from service IP flapping", "cause-less-likely")],
    [LI("l2announcements.enabled not in Helm (beta feature)", "cause-new-cluster"), LI("No CiliumL2AnnouncementPolicy created", "cause-new-cluster"), LI("Cluster not bare metal (L2 doesn't work across routers)", "cause-new-cluster"), LI("Feature expectation: L2 is simpler than BGP but limited to same L2 domain", "cause-new-cluster"), LI("No client in same L2 domain to test ARP", "cause-new-cluster")],
    "`kubectl get ciliuml2announcementpolicy`. `kubectl get lease -n kube-system | grep l2announce`. `arp -a | grep <svc-ip>` from client in same L2 domain.",
    "1. Enable: `--set l2announcements.enabled=true`<br>2. Create policy: `kubectl apply -f l2-policy.yaml`<br>3. Verify lease: `kubectl get lease -n kube-system | grep l2`<br>4. Test ARP: `arping <svc-ip>` from same L2 client<br>5. If no response: check leader node has service IP on interface",
    "L2 Announcements = simpler than BGP but limited. For anihpj: use L2 for office/campus LAN where BGP routers aren't available. Limitation: single L2 domain, one leader per service, ~15-20s failover. BGP is better for production data centers."
)

cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg5", "BGP Graceful Restart — Traffic Disrupted During Cilium Restart",
    "Cilium agent restart causes brief traffic disruption. BGP session flaps, routes withdrawn, traffic blackholes for 30-90 seconds during restart.",
    [LI("Graceful restart not enabled: Cilium supports graceful restart but needs `bgp.gracefulRestart.enabled=true`."), LI("Peer router doesn't support graceful restart helper mode: both sides need to support GR."), LI("Restart time too long: graceful restart has a time limit. If agent restart exceeds GR timer, routes are withdrawn."), LI("eBPF program persistence not leveraged: while eBPF programs survive restart, BGP session does not. Need GR for route preservation."), LI("BFD acceleration of failure detection: if BFD is on, failure detected in <1s, before GR can activate.")],
    [LI("GR stale routes not marked correctly by peer router", "cause-less-likely"), LI("Route refresh not supported by peer (older BGP implementation)", "cause-less-likely"), LI("Multiple BGP peers: one doesn't support GR → partial route withdrawal", "cause-less-likely"), LI("GR restart timer mismatch with peer", "cause-less-likely"), LI("TCP session not preserved during restart (new 3-way handshake)", "cause-less-likely")],
    [LI("Graceful restart not tested during Cilium deployment", "cause-new-cluster"), LI("BGP peer is basic router without GR support", "cause-new-cluster"), LI("Cilium upgrade procedures don't account for BGP session preservation", "cause-new-cluster"), LI("No redundancy: single BGP peer → single point of failure", "cause-new-cluster"), LI("GR configuration not in CiliumBGPPeeringPolicy", "cause-new-cluster")],
    "`cilium-dbg bgp peers` — GR capability negotiated? `cilium status | grep BGP`. eBPF programs persist during restart — data plane survives if BGP routes survive via GR.",
    "1. Enable GR: `bgp.gracefulRestart.enabled: true` in Helm or CiliumBGPPeeringPolicy<br>2. Verify peer supports GR: check peer router config<br>3. Test: restart Cilium agent, monitor `cilium-dbg bgp peers`<br>4. eBPF persistence + GR = minimal disruption<br>5. For zero-downtime: deploy multiple BGP peers with ECMP",
    "Graceful restart preserves BGP routes during Cilium agent restart. Combined with eBPF program persistence, this minimizes traffic disruption. For anihpj: test GR during maintenance windows to verify your BGP peer supports it."
)

cat8 += TS(8, "BGP & EXTERNAL", "🟤", "bg6", "Cilium Ingress/Gateway External Traffic — TLS Not Terminating",
    "External HTTPS traffic reaches Cilium Ingress but TLS handshake fails. Browser shows 'SSL_ERROR_RX_RECORD_TOO_LONG' or certificate error.",
    [LI("TLS Secret not configured for Ingress/Gateway: `kubectl get secret <tls-name> -n <ns>`. Must have tls.crt and tls.key."), LI("TLS section missing from Ingress/Gateway: Ingress `spec.tls[].hosts` must include the hostname, Gateway listener `tls.mode=Terminate`."), LI("Cert hostname mismatch: browser SNI doesn't match cert CN/SAN. Use wildcard cert or exact hostname match."), LI("Port 443 not opened: Ingress/Gateway listener must be on port 443 for HTTPS. Check Gateway `listeners[].port`."), LI("HTTP/2 ALPN negotiation failing: client tries HTTP/2 but Envoy not configured for it.")],
    [LI("Intermediate CA cert not included in tls.crt (incomplete chain)", "cause-less-likely"), LI("TLS 1.0/1.1 disabled on client side (requires TLS 1.2+)", "cause-less-likely"), LI("Envoy TLS context not loaded from Secret (RBAC/permission issue)", "cause-less-likely"), LI("Cipher suite mismatch: client proposes ciphers Envoy doesn't support", "cause-less-likely"), LI("OCSP stapling failure causing client rejection", "cause-less-likely")],
    [LI("TLS Secret not created before Ingress/Gateway", "cause-new-cluster"), LI("External DNS not pointing to correct IP (BGP/LB IP)", "cause-new-cluster"), LI("Cilium Ingress/Gateway not configured for external traffic", "cause-new-cluster"), LI("No external LoadBalancer IP assigned for Ingress", "cause-new-cluster"), LI("Self-signed cert in production (browser trust issue)", "cause-new-cluster")],
    "`kubectl get secret <tls-name> -o yaml`. `openssl s_client -connect <external-ip>:443 -servername <hostname>`. `cilium-dbg envoy config | grep tls`.",
    "1. Create TLS Secret: `kubectl create secret tls anihpj-tls --cert=cert.pem --key=key.pem -n anihpj`<br>2. Add TLS to Ingress/Gateway spec<br>3. Verify: `openssl s_client -connect <ip>:443 -servername anihpj.example.com`<br>4. Check Envoy config: `kubectl exec ds/cilium -- cilium-dbg envoy config | grep tls`<br>5. External DNS: A record → BGP-advertised LoadBalancer IP",
    "External HTTPS into Cilium Ingress/Gateway = TLS Secret + DNS + BGP/LB IP. For anihpj: use cert-manager to auto-provision Let's Encrypt certificates. Combined with Cilium's BGP + LB IPAM, you get a complete external-facing setup without cloud load balancers."
)

print("✅ CAT8 generated: 6 issues")

# =====================================================================
# INSERT INTO HTML
# =====================================================================

with open(HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Insert before PART 3 banner using line-based approach
all_cats = cat4 + "\n" + cat5 + "\n" + cat6 + "\n" + cat7 + "\n" + cat8 + "\n\n"
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if 'PART 3' in line and '<!--' in line and 'part-banner' not in line and i > 6000:
        insert_idx = i
        break
if insert_idx:
    lines.insert(insert_idx, all_cats.rstrip('\n'))
    content = '\n'.join(lines)
    print(f"✅ CAT4-CAT8 inserted before PART 3 (line {insert_idx})")
else:
    print("❌ PART 3 marker not found!")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("\n🎉 ALL troubleshooting issues (CAT3-CAT8) inserted!")
