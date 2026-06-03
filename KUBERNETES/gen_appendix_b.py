"""Generate Appendix B: Top 50 Troubleshooting Commands for cilium-test-prep.html"""

import re

HTML_FILE = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html'

# ── 50 Commands organized by category ──
commands = [
    # ===== CAT 1: Architecture (10) =====
    ("Architecture", "1", "cilium status", "cilium status [--wait] [--output json]",
     "First diagnostic command — shows overall Cilium health", "--wait (block until ready), --output json (machine-readable)",
     "When Cilium agent or operator is not behaving as expected. Always run this first to get a high-level health overview of all Cilium components (agent, operator, clustermesh, etc.)."),
    ("Architecture", "1", "cilium endpoint list", "cilium endpoint list [-o json] [--namespace NS]",
     "Lists all Cilium-managed endpoints with identity, state, and addressing", "-o json (structured output), --namespace (filter by namespace)",
     "When pods seem connected but traffic isn't flowing. Check endpoint state (ready/regenerating/disconnecting), security identity, and IPv4/IPv6 addresses."),
    ("Architecture", "1", "cilium endpoint get", "cilium endpoint get ENDPOINT_ID",
     "Detailed view of a single endpoint including policy enforcement status", "No special flags — pass the numeric endpoint ID from 'cilium endpoint list'",
     "When you need deep-dive info on one pod's Cilium state: policy revision, labels, MAC, interface, and log entries for that specific endpoint."),
    ("Architecture", "1", "cilium identity list", "cilium identity list [-o json] [--namespace NS]",
     "Lists all security identities currently allocated in the cluster", "-o json, --namespace",
     "When you suspect identity allocation issues — stale identities, identity conflicts between clusters, or high identity count causing performance problems."),
    ("Architecture", "1", "cilium bpf ipcache list", "cilium bpf ipcache list",
     "Dumps the BPF IP cache — maps pod IPs to security identities in kernel space", "No common flags — direct kernel map dump",
     "When pod-to-pod traffic is dropped despite correct policies. If an IP is missing from ipcache, Cilium can't map it to an identity for policy lookup."),
    ("Architecture", "1", "cilium node list", "cilium node list [-o json]",
     "Lists all nodes known to Cilium with their internal IP, tunnel IP, and health status", "-o json",
     "When cross-node traffic fails. Verify that all nodes appear with correct IPs and that tunnel endpoints are properly assigned."),
    ("Architecture", "1", "cilium encrypt status", "cilium encrypt status",
     "Shows WireGuard/IPSec encryption status per node", "No flags — single status command",
     "When you've enabled transparent encryption but aren't sure if it's active. Shows encryption type, key count, and per-node peer status."),
    ("Architecture", "1", "cilium-dbg monitor", "cilium-dbg monitor [--type TYPE] [-v]",
     "Live event monitor — shows endpoint events, policy updates, drops in real-time", "--type (agent|debug|policy-verdict|trace|drop), -v (verbose)",
     "Real-time debugging of what Cilium is doing right now. Invaluable for catching transient issues like momentary drops or policy reloads."),
    ("Architecture", "1", "kubectl get cep -n NS", "kubectl get cep -n NAMESPACE [-o wide] [-o yaml]",
     "Lists CiliumEndpoint CRDs — one per pod — showing identity, networking, and policy state", "-n (namespace), -o wide/yaml/json",
     "When a pod has networking issues but is Running. CEP shows the Cilium-level state: is the endpoint ready? What identity is assigned?"),
    ("Architecture", "1", "cilium connectivity test", "cilium connectivity test [--flow-validation disabled]",
     "Runs a comprehensive end-to-end connectivity test suite", "--flow-validation (enabled by default, checks Hubble flows too)",
     "After fresh install, upgrade, or config change. Validates pod-to-pod, pod-to-service, DNS, network policy, and encryption all at once."),

    # ===== CAT 2: Network Policy (8) =====
    ("Network Policy", "2", "cilium policy get", "cilium policy get [--namespace NS] [-o json]",
     "Displays all CiliumNetworkPolicies currently enforced", "--namespace (filter), -o json",
     "When you need to see what policies are loaded and active. Useful for confirming a just-applied policy is actually being enforced."),
    ("Network Policy", "2", "cilium policy trace", "cilium policy trace --src-pod NS/POD --dst-pod NS/POD --dport PORT --protocol TCP",
     "Traces what policy decision would be made for a hypothetical or real flow", "--src-pod, --dst-pod, --dport, --protocol, --src-identity, --dst-identity, --http-method, --http-path",
     "THE most important policy debugging command. Before troubleshooting dropped traffic, run a policy trace to see if a policy is blocking it — and which rule."),
    ("Network Policy", "2", "cilium policy validate", "cilium policy validate POLICY.yaml",
     "Validates a CiliumNetworkPolicy YAML without applying it", "Pass the YAML file path — checks syntax, schema, and logical correctness",
     "Before applying a new CNP, always validate it. Catches common mistakes like invalid entity names, missing required fields, or conflicting rules."),
    ("Network Policy", "2", "cilium-dbg monitor --type policy-verdict", "cilium-dbg monitor --type policy-verdict -v",
     "Shows live policy decisions — ALLOW or DENY — for every packet evaluated", "-v (verbose shows full labels and identities)",
     "When a specific flow is being dropped and you need to see WHY in real-time. Shows the exact policy name and rule that caused the verdict."),
    ("Network Policy", "2", "hubble observe --verdict DROPPED", "hubble observe --verdict DROPPED [-n NAMESPACE] [--from-pod NS/POD] [--to-pod NS/POD]",
     "Shows all dropped flows observed by Hubble", "--verdict (DROPPED|FORWARDED|ERROR), --from-pod, --to-pod, --protocol, --to-port",
     "The easiest way to find what's being blocked. Filter by namespace, pod, or port to narrow down which policy (or lack thereof) is dropping traffic."),
    ("Network Policy", "2", "kubectl describe cnp POLICY", "kubectl describe cnp POLICY_NAME [-n NAMESPACE]",
     "Detailed view of a CiliumNetworkPolicy including its spec and enforcement status", "-n (namespace)",
     "When a CNP doesn't seem to be working — check if it's actually been parsed correctly and what the effective rules look like from Kubernetes perspective."),
    ("Network Policy", "2", "cilium bpf policy get", "cilium bpf policy get ENDPOINT_ID",
     "Dumps the BPF policy map for a specific endpoint — the actual kernel-level rules", "Pass the numeric endpoint ID",
     "When policy trace says something but traffic behaves differently. This shows what's actually loaded in the kernel, which is the ground truth."),
    ("Network Policy", "2", "kubectl get ccnp", "kubectl get ccnp [-o wide]",
     "Lists all CiliumClusterwideNetworkPolicies (policies that apply to all namespaces)", "-o wide (shows more detail)",
     "When a policy seems to apply everywhere unexpectedly — a CCNP might be the culprit. These apply cluster-wide, not namespace-scoped."),

    # ===== CAT 3: Service Mesh (7) =====
    ("Service Mesh", "3", "cilium service list", "cilium service list [-o json]",
     "Lists all Kubernetes Services that Cilium is managing (KPR mode)", "-o json",
     "When KPR is enabled and services aren't load balancing correctly. Check if the service appears here with the right backend endpoints."),
    ("Service Mesh", "3", "cilium bpf lb list", "cilium bpf lb list",
     "Dumps the BPF load balancer maps — shows the actual kernel-level service-to-backend mapping", "No common flags — direct kernel map dump",
     "When services appear in 'cilium service list' but traffic isn't being load balanced. This shows what the BPF datapath actually routes to."),
    ("Service Mesh", "3", "cilium-dbg monitor --type trace", "cilium-dbg monitor --type trace [-v]",
     "Shows packet trace events — the path a packet takes through the Cilium datapath", "-v (verbose shows full headers)",
     "When you need to understand the full lifecycle of a packet: ingress → policy evaluation → load balancing → egress. Shows each BPF hook traversal."),
    ("Service Mesh", "3", "cilium bpf ct list", "cilium bpf ct list GLOBAL",
     "Dumps the BPF connection tracking table (conntrack)", "GLOBAL (global table), ENDPOINT_ID (per-endpoint table)",
     "When connections mysteriously reset or new connections can't establish. Full conntrack tables drop new connections; stale entries cause resets."),
    ("Service Mesh", "3", "cilium bpf nat list", "cilium bpf nat list",
     "Dumps the BPF NAT table — shows source NAT mappings for masquerading", "No common flags — direct kernel map dump",
     "When pods can reach internal services but not external endpoints. NAT issues often cause one-directional connectivity or wrong source IPs."),
    ("Service Mesh", "3", "kubectl get ingress -A", "kubectl get ingress --all-namespaces [-o wide]",
     "Lists all Cilium Ingress resources across namespaces", "-A (all namespaces), -o wide (shows hosts and address)",
     "When Cilium Ingress isn't routing traffic. Check that the Ingress resource exists, has an ADDRESS assigned, and the host matches your request."),
    ("Service Mesh", "3", "cilium-dbg monitor --type drop", "cilium-dbg monitor --type drop [-v]",
     "Shows all packets dropped by the Cilium datapath with drop reason codes", "-v (verbose shows full details)",
     "When you're losing packets but don't know why. Drop reasons include: policy_denied, stale_ipsec, invalid_source, ct_lookup_failed, etc."),

    # ===== CAT 4: Network Observability (6) =====
    ("Network Observability", "4", "hubble observe", "hubble observe [-n NAMESPACE] [--since TIMESTAMP] [--from-pod NS/POD] [--to-pod NS/POD] [--verdict VERDICT]",
     "Observes all network flows in real-time with rich metadata", "-n (namespace), --since (time range), --from-pod, --to-pod, --verdict, --protocol, --http-method, --http-path, --to-port, -o json",
     "The primary observability command. Use this for ANY connectivity issue — it shows what's flowing, what's dropped, and full L7 metadata for HTTP/DNS/gRPC."),
    ("Network Observability", "4", "hubble status", "hubble status [--server SERVER]",
     "Shows Hubble connectivity status and available components", "--server (specify Hubble server address)",
     "When 'hubble observe' returns no output. Check if Hubble Relay is connected, if TLS is configured correctly, and what flows are available."),
    ("Network Observability", "4", "hubble relayer status", "hubble relay status",
     "Shows Hubble Relay status — connected peers, aggregated cluster count", "No flags — single status command",
     "In multi-cluster setups when flows from some clusters are missing. Shows which peer Hubble instances are connected to the relay."),
    ("Network Observability", "4", "cilium hubble port-forward", "cilium hubble port-forward &",
     "Port-forwards Hubble Relay and Hubble UI to localhost for browser access", "& (run in background)",
     "Quickest way to access Hubble UI or Hubble CLI against a remote cluster. Forwards port 4245 (Hubble gRPC) and 12000 (Hubble UI)."),
    ("Network Observability", "4", "hubble observe -o json | jq", "hubble observe -o json [filters...] | jq 'FILTER'",
     "Exports Hubble flows as JSON for programmatic analysis", "-o json, pipe to jq for filtering/summarization",
     "When you need to analyze flow patterns, count by verdict, group by HTTP status code, or export for reporting. Combine with jq for powerful analysis."),
    ("Network Observability", "4", "cilium metrics list", "cilium metrics list [-p PORT]",
     "Lists all Prometheus metrics currently exported by the Cilium agent", "-p (Cilium agent metrics port, default 9962)",
     "When setting up Prometheus scraping or debugging missing metrics. Confirm the metric name and labels before building PromQL queries or Grafana panels."),

    # ===== CAT 5: Installation & Configuration (6) =====
    ("Installation & Config", "5", "cilium install", "cilium install [--version VERSION] [--helm-set KEY=VALUE] [--dry-run]",
     "Installs Cilium on a Kubernetes cluster via Helm", "--version (pin version), --helm-set (override any Helm value), --dry-run (preview without applying)",
     "CLI installation method. The --helm-set flag allows overriding any Helm value inline. Always use --dry-run first on production clusters."),
    ("Installation & Config", "5", "cilium upgrade", "cilium upgrade [--version VERSION] [--helm-set KEY=VALUE]",
     "Upgrades an existing Cilium installation", "--version, --helm-set",
     "When upgrading Cilium versions. The CLI handles the correct upgrade sequence: preflight checks, agent upgrade, operator upgrade, and post-upgrade validation."),
    ("Installation & Config", "5", "cilium sysdump", "cilium sysdump [-o OUTPUT_DIR] [--output-filename ARCHIVE.tar.gz]",
     "Collects comprehensive diagnostic data from the entire cluster", "-o (output directory), --output-filename (archive name)",
     "Before opening a support ticket or GitHub issue. Collects logs, endpoints, policies, BPF maps, system info, and node dumps from ALL nodes automatically."),
    ("Installation & Config", "5", "cilium config", "cilium config [KEY] [VALUE]",
     "Views or sets the Cilium ConfigMap configuration", "KEY (view specific config), KEY VALUE (set config)",
     "To check or change Cilium's runtime configuration. Key settings: tunnel, kube-proxy-replacement, enable-ipv4, enable-ipv6, cluster-id, cluster-name."),
    ("Installation & Config", "5", "cilium preflight", "cilium preflight [--assume-yes]",
     "Runs pre-upgrade validation checks before upgrading Cilium", "--assume-yes (auto-acknowledge)",
     "Before any Cilium upgrade. Validates CRD compatibility, daemonset readiness, and checks for any blockers that could cause upgrade failure."),
    ("Installation & Config", "5", "helm get values cilium", "helm get values cilium -n kube-system [-a]",
     "Shows the current Helm values used to deploy Cilium", "-n kube-system (Cilium's namespace), -a (all values including defaults)",
     "When you need to know exactly how Cilium was configured. Shows both user-supplied and default values. Essential before upgrades or when troubleshooting config-related issues."),

    # ===== CAT 6: Cluster Mesh (5) =====
    ("Cluster Mesh", "6", "cilium clustermesh status", "cilium clustermesh status [--context CONTEXT]",
     "Shows Cluster Mesh health — connected clusters, global services, identity sync", "--context (kubeconfig context for a specific cluster)",
     "First command when cross-cluster communication fails. Shows connected clusters count, service synchronization state, and identity sharing status."),
    ("Cluster Mesh", "6", "cilium clustermesh connect", "cilium clustermesh connect --destination-context DST [OPTIONS]",
     "Connects two Cilium clusters into a mesh", "--destination-context (target cluster kubeconfig context)",
     "When setting up or repairing Cluster Mesh. Establishes the TLS-secured etcd connection between clusters and triggers initial service/identity sync."),
    ("Cluster Mesh", "6", "cilium clustermesh disconnect", "cilium clustermesh disconnect --destination-context DST",
     "Disconnects a cluster from the mesh", "--destination-context",
     "When decomissioning a cluster or troubleshooting mesh issues. Gracefully removes the cluster from the mesh without disrupting remaining clusters."),
    ("Cluster Mesh", "6", "kubectl get globalnetworksets", "kubectl get globalnetworksets",
     "Lists all GlobalNetworkSets — CRDs that define cross-cluster network sets", "No special flags — standard kubectl",
     "When cross-cluster CIDR-based policies aren't working. GlobalNetworkSets define IP ranges that span clusters for policy federation."),
    ("Cluster Mesh", "6", "cilium service list --all-clusters", "cilium service list [--all-clusters]",
     "Shows services from ALL clusters in the mesh, not just local", "--all-clusters (show global services too)",
     "When a global service should be accessible but isn't. Check if the remote service is visible locally (synced) and if backends include remote cluster pods."),

    # ===== CAT 7: eBPF (5) =====
    ("eBPF", "7", "bpftool prog list", "bpftool prog list [--json] [-p]",
     "Lists all loaded eBPF programs with IDs, types, tags, and attachment points", "--json (machine-readable), -p (pretty print)",
     "To see what eBPF programs Cilium has loaded on a node. Each program has an ID, type (XDP/TC/cgroup/socket), and shows how many BPF maps it uses."),
    ("eBPF", "7", "bpftool map list", "bpftool map list [--json] [-p]",
     "Lists all eBPF maps with IDs, types, key/value sizes, and entry counts", "--json, -p",
     "To check BPF map utilization. Look for maps with max_entries near capacity — these can cause drops or failures when creating new endpoints/policies."),
    ("eBPF", "7", "bpftool map dump", "bpftool map dump id MAP_ID [--json]",
     "Dumps the contents of a specific BPF map", "id (map ID from 'bpftool map list'), --json",
     "To inspect the actual kernel data: policy maps, conntrack tables, NAT tables, and IP cache. The definitive source of truth for what Cilium has loaded in the kernel."),
    ("eBPF", "7", "bpftool prog show id PROG_ID", "bpftool prog show id PROG_ID [--json] [--pretty]",
     "Shows detailed info about a specific eBPF program — runtime stats, JIT status, map IDs", "id (program ID), --json, --pretty (human-readable)",
     "When you need to verify a specific Cilium eBPF program is loaded and attached correctly. Check run_time (how long it's been active) and attached state."),
    ("eBPF", "7", "mount | grep bpf", "mount | grep bpf",
     "Checks if the BPF filesystem (bpffs) is mounted", "No flags — pipe to grep",
     "When Cilium fails to start or BPF maps can't be pinned. bpffs must be mounted at /sys/fs/bpf for Cilium to persist maps and programs across agent restarts."),

    # ===== CAT 8: BGP & External Networking (3) =====
    ("BGP &amp; External", "8", "cilium bgp peers", "cilium bgp peers [--asn ASN]",
     "Shows BGP peering status — session state, routes received, prefixes advertised", "--asn (filter by autonomous system number)",
     "When BGP-based load balancing isn't working. Shows each peer's session state (Established/Connect/Active), route count, and last error."),
    ("BGP &amp; External", "8", "cilium bgp routes available", "cilium bgp routes available ipv4 unicast [--peer PEER_IP]",
     "Shows BGP routes available for advertisement to peers", "--peer (filter by peer IP)",
     "When a peer isn't receiving expected routes. Check what routes Cilium has available to advertise — if the LB IP isn't here, LB IPAM may be the issue."),
    ("BGP &amp; External", "8", "kubectl get l2announcementpolicies", "kubectl get l2announcementpolicies [-A] [-o wide]",
     "Lists L2 Announcement policies (ARP/NDP responder for LoadBalancer IPs)", "-A (all namespaces), -o wide",
     "When L2 announcements aren't working for bare metal. Check that the policy exists, matches the right service/namespace labels, and the node is the elected leader."),
]

# ── Generate HTML ──
lines = []
lines.append('')
lines.append('    <!-- ═══════════════ APPENDIX B: TOP 50 TROUBLESHOOTING COMMANDS ═══════════════ -->')
lines.append('    <section class="chapter-section" id="apx-b">')
lines.append('        <h2><span>📋 Appendix B: Top 50 Troubleshooting Commands</span><span class="chapter-badge">Quick Reference</span></h2>')
lines.append('')
lines.append('        <div class="aq-info">')
lines.append('            <p>These <strong>50 essential commands</strong> are organized by the 8 Linux Foundation CCA exam domains. Each entry includes the command syntax, common flags, and — most importantly — <em>when to use it</em> in real troubleshooting scenarios. Master these commands and you\'ll be able to diagnose any Cilium issue in the exam and in production.</p>')
lines.append('            <p><strong>Pro tip:</strong> In the exam environment, you won\'t have access to external docs. Memorize the <em>purpose</em> of each command (column 3) and the most important flags (column 4).</p>')
lines.append('        </div>')
lines.append('')

# Group by category
from collections import OrderedDict
cat_names = {
    "Architecture": "1. Architecture",
    "Network Policy": "2. Network Policy",
    "Service Mesh": "3. Service Mesh",
    "Network Observability": "4. Network Observability",
    "Installation &amp; Config": "5. Installation &amp; Configuration",
    "Cluster Mesh": "6. Cluster Mesh",
    "eBPF": "7. eBPF",
    "BGP &amp; External": "8. BGP &amp; External Networking",
}
cat_colors = {
    "1": "#58a6ff", "2": "#3fb950", "3": "#d2991d", "4": "#a371f7",
    "5": "#f85149", "6": "#79c0ff", "7": "#56d364", "8": "#e5534b",
}

grouped = OrderedDict()
for cmd in commands:
    cat_key = cmd[0]
    if cat_key not in grouped:
        grouped[cat_key] = []
    grouped[cat_key].append(cmd)

cmd_num = 0
for cat_key, cmds in grouped.items():
    cat_num = cmds[0][1]
    cat_label = cat_names.get(cat_key, cat_key)
    lines.append('')
    lines.append(f'        <h3><span class="cmd-cat-pill" style="background:{cat_colors[cat_num]};color:#fff;padding:3px 12px;border-radius:12px;font-size:0.85em;">{cat_label}</span> <span style="color:var(--text-secondary);font-size:0.8em;">({len(cmds)} commands)</span></h3>')
    lines.append('')
    lines.append('        <div class="cmd-table-wrap">')
    lines.append('        <table class="cmd-table">')
    lines.append('            <tr><th>#</th><th>Command Syntax</th><th>Purpose</th><th>Common Flags</th><th>When to Use</th></tr>')

    for i, (_, _, syn, full_syntax, purpose, flags, when) in enumerate(cmds):
        cmd_num += 1
        # Escape HTML in syntax
        syn_esc = syn.replace('&amp;', '&').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        full_esc = full_syntax.replace('&amp;', '&').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        purpose_esc = purpose.replace('<', '&lt;').replace('>', '&gt;')
        flags_esc = flags.replace('<', '&lt;').replace('>', '&gt;')
        when_esc = when.replace('<', '&lt;').replace('>', '&gt;')

        row_class = 'cmd-row-even' if i % 2 == 0 else 'cmd-row-odd'
        lines.append(f'            <tr class="{row_class}"><td class="cmd-num">C{cmd_num:02d}</td><td class="cmd-syn"><code>{syn_esc}</code><span class="cmd-full">{full_esc}</span></td><td class="cmd-purpose">{purpose_esc}</td><td class="cmd-flags">{flags_esc}</td><td class="cmd-when">{when_esc}</td></tr>')

    lines.append('        </table>')
    lines.append('        </div>')

lines.append('')
lines.append('        <div class="aq-tips">')
lines.append('            <h4>💡 Exam Day Command Strategy</h4>')
lines.append('            <ul>')
lines.append('                <li><strong>Always start with:</strong> <code>cilium status</code> and <code>hubble observe --verdict DROPPED</code> — these answer 60% of exam scenarios.</li>')
lines.append('                <li><strong>Policy issues:</strong> <code>cilium policy trace</code> before anything else — it tells you exactly which rule is (or isn\'t) matching.</li>')
lines.append('                <li><strong>Service issues:</strong> <code>cilium service list</code> → <code>cilium bpf lb list</code> — check control plane vs kernel state.</li>')
lines.append('                <li><strong>Multi-cluster:</strong> <code>cilium clustermesh status</code> — always the first step, shows connectivity and sync state at a glance.</li>')
lines.append('                <li><strong>Kernel problems:</strong> <code>bpftool prog list</code> → <code>bpftool map list</code> — reveal what\'s actually loaded in the eBPF subsystem.</li>')
lines.append('                <li><strong>Collect evidence:</strong> <code>cilium sysdump</code> captures everything. If you\'re stuck, run it and inspect the files — the answer is usually in there.</li>')
lines.append('            </ul>')
lines.append('        </div>')
lines.append('')
lines.append('    </section>')

appendix_b_html = '\n'.join(lines)

# ── Insert into file ──
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find insertion point: between </section> closing apx-a and <!-- FOOTER -->
marker = '\n\n    <!-- ═══════════════ FOOTER ═══════════════ -->'
if marker in content:
    new_content = content.replace(marker, appendix_b_html + marker, 1)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'✅ Appendix B inserted! File: {len(new_content):,} bytes')
    print(f'   Commands: {cmd_num} across {len(grouped)} categories')
else:
    print('❌ Could not find FOOTER marker!')
