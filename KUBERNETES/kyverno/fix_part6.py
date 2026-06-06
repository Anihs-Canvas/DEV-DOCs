"""Fix Part 6 gaps — enrich 6.3 data model examples + add 6.11 lease/txn commands"""

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# FIX 1: 6.3 — Enrich nodes section with full detail from txt
# ============================================================
old_nodes = '''│   └── 📄 fe-01, fe-02                   # → status.conditions, status.capacity,
│                                          #   status.addresses, spec.taints,
│                                          #   status.nodeInfo (kubeletVersion, osImage,
│                                          #   containerRuntimeVersion, kernelVersion)'''

new_nodes = '''│   ├── 📄 cp-01, cp-02, cp-03              # → k8s.io.api.core.v1.Node
│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05  #   Contains: status.conditions (Ready,
│   └── 📄 fe-01, fe-02                      #     MemoryPressure, DiskPressure,
│                                            #     PIDPressure, NetworkUnavailable),
│                                            #     status.capacity (cpu, memory, pods,
│                                            #     ephemeral-storage), status.addresses
│                                            #     (InternalIP, Hostname), spec.taints,
│                                            #     spec.unschedulable, status.nodeInfo
│                                            #     (kubeletVersion, osImage,
│                                            #     containerRuntimeVersion, kernelVersion)'''

html = html.replace(old_nodes, new_nodes)
print("FIX 1: 6.3 nodes section enriched with full conditions/capacity/addresses detail")

# ============================================================
# FIX 2: 6.3 — Add specific PV example with NFS details
# ============================================================
old_pv = '''├── 📁 persistentvolumes/ & persistentvolumeclaims/'''

new_pv = '''├── 📁 persistentvolumes/                  # PVs (cluster-wide storage)
│   └── 📄 pv-001                         # → capacity: 100Gi, accessModes:
│                                          #   [ReadWriteOnce], reclaimPolicy: Retain,
│                                          #   nfs: {server: "10.0.0.100",
│                                          #         path: "/exports/data"}
│
├── 📁 persistentvolumeclaims/             # PVCs (namespace-scoped)
│   └── 📁 default/
│       └── 📄 webapp-data                # → Bound to PV pv-001
│
├── 📁 clusterroles/                       # Cluster-wide RBAC roles
│   ├── 📄 cluster-admin
│   ├── 📄 edit
│   └── 📄 view
│
├── 📁 clusterrolebindings/                # Binding ClusterRoles to subjects
│   └── 📄 cluster-admin-binding          # → subjects: [{kind: User,
│                                          #   name: "carol@anihpj.io"}]
│
├── 📁 roles/                              # Namespace-scoped RBAC roles
│   └── 📁 default/
│       └── 📄 deployer                   # → rules: [{apiGroups: ["apps"],
│                                          #   resources: ["deployments"],
│                                          #   verbs: ["get","list","update","patch"]}]
│
├── 📁 rolebindings/                       # Binding Roles to subjects
│   └── 📁 default/
│       └── 📄 deployer-binding'''

html = html.replace(old_pv, new_pv)
print("FIX 2: 6.3 enriched with PV, PVC, ClusterRole, ClusterRoleBinding, Role, RoleBinding examples")

# ============================================================
# FIX 3: 6.11 — Add lease and transaction commands
# ============================================================
old_eof_611 = '''                <tr><td><code class="inline">etcdctl alarm disarm</code></td><td>Clear alarms after fixing the issue</td></tr>
            </table>
        </div>'''

new_eof_611 = '''                <tr><td><code class="inline">etcdctl alarm disarm</code></td><td>Clear alarms after fixing the issue</td></tr>
                <tr><td colspan="2"><strong>⏱️ Lease & Election</strong></td></tr>
                <tr><td><code class="inline">etcdctl lease grant 60</code></td><td>Create a 60-second lease — returns a lease ID</td></tr>
                <tr><td><code class="inline">etcdctl lease keep-alive &lt;lease-id&gt;</code></td><td>Keep a lease alive (Kubernetes uses this for node heartbeats)</td></tr>
                <tr><td><code class="inline">etcdctl lease revoke &lt;lease-id&gt;</code></td><td>Revoke a lease — all keys attached to it are deleted</td></tr>
                <tr><td colspan="2"><strong>🔄 Transactions</strong></td></tr>
                <tr><td><code class="inline">etcdctl txn -i</code></td><td>Interactive transaction: compare value of key and conditionally put/get. Used for distributed locking: "If /lock == unlocked → put /lock locked; else → get /lock"</td></tr>
            </table>
        </div>'''

html = html.replace(old_eof_611, new_eof_611)
print("FIX 3: 6.11 enriched with lease commands + transaction example")

# ============================================================
# FIX 4: 6.3 — Fix old entries (clusterroles/roles were merged)
# ============================================================
old_cr = '''├── 📁 clusterroles/ & clusterrolebindings/
├── 📁 roles/ & rolebindings/'''

# After FIX 2, the clusterroles/roles entries should no longer exist in the old form
# since we replaced the PV section that was on the same line. Check if they still exist:
if old_cr in html:
    html = html.replace(old_cr, '')
    print("FIX 4: Removed old merged clusterroles/roles lines (now expanded)")
else:
    print("FIX 4: Old clusterroles/roles already replaced — skipping")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nFinal: {html.count(chr(10))} lines')
