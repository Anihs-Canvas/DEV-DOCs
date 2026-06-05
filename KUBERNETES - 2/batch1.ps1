$f = "KCSA.html"
$c = Get-Content $f -Raw
$changes = 0

function Add-Questions($anchor, $newQs) {
    $script:c = $script:c.Substring(0, $script:c.IndexOf($anchor) + $anchor.Length) + $newQs + $script:c.Substring($script:c.IndexOf($anchor) + $anchor.Length)
    $script:changes++
}

# Ch9: +1 (9->10) - PSS chapter
Add-Questions "Enforce blocks, audit logs, warn displays. Use all three for gradual rollout.</p></details></div>" @'

                    <div class="drill-scenario"><h5>Q10: What is the evolution of pod security in Kubernetes?</h5><ol><li>PSA → PSP → OPA</li><li>PSP (deprecated v1.21) → PSA (built-in v1.23) → OPA/Kyverno for custom policies</li><li>RBAC → NetworkPolicy → PSS</li><li>OPA → Kyverno → PSP</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. PSP→PSA→OPA/Kyverno.</strong> PodSecurityPolicy deprecated v1.21, removed v1.25. Pod Security Admission (PSA) is built-in since v1.23. OPA and Kyverno provide custom policy engines beyond PSA.</p></details></div>
'@

Write-Host "Ch9: +1"

# Ch10: +6 (4->10) - AuthN/AuthZ
Add-Questions "automountServiceAccountToken: false for pods that do not need API access.</p></details></div>" @'

                    <div class="drill-scenario"><h5>Q5: What does the view ClusterRole NOT allow by default?</h5><ol><li>Reading pods</li><li>Reading Secrets</li><li>Reading services</li><li>Reading deployments</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Reading Secrets.</strong> The built-in view role cannot read Secrets by default — you must create a separate Role for Secret access. This is a common exam trap.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: What is the difference between projected volume tokens and legacy SA tokens?</h5><ol><li>No difference</li><li>Projected tokens are time-bound (1hr), audience-scoped, auto-rotated. Legacy tokens are non-expiring JWT secrets</li><li>Legacy tokens are more secure</li><li>Projected tokens are deprecated</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Time-bound and scoped.</strong> Projected volume tokens (TokenRequest API) expire, have audience binding, and auto-rotate. Legacy SA tokens stored as Secrets have no expiry — never use them.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: Can a RoleBinding reference a ClusterRole?</h5><ol><li>No — only Roles</li><li>Yes — grants cluster-wide permissions limited to that namespace</li><li>Only via ClusterRoleBinding</li><li>Only for cluster-admin</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Yes, namespace-limited.</strong> Binding a ClusterRole via RoleBinding grants those permissions ONLY within the binding''s namespace — powerful for namespace admins needing read-only node access.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: Which OIDC feature makes it superior to static token files?</h5><ol><li>Faster authentication</li><li>Short-lived tokens, MFA support, centralized revocation</li><li>No certificates needed</li><li>Works without internet</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Short-lived tokens + MFA.</strong> OIDC issues short-lived JWTs (1hr), supports MFA at IDP level, and can be centrally revoked. Static tokens never expire and can''t be rotated without restarting API server.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: What are aggregated ClusterRoles used for?</h5><ol><li>Faster API responses</li><li>Composing multiple ClusterRoles using label selectors — like how admin/edit/view roles work</li><li>Network policies</li><li>Storage management</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Role composition.</strong> Aggregated ClusterRoles combine other ClusterRoles matching labels. The built-in admin/edit/view roles aggregate sub-roles for different API groups automatically.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: What RBAC principle should guide all permissions?</h5><ol><li>Maximum privilege for convenience</li><li>Least privilege — grant only what is needed, nothing more</li><li>Always use cluster-admin</li><li>Disable RBAC entirely</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Least privilege.</strong> Grant minimum permissions needed. Use namespace-scoped Roles. Bind groups not users. Audit RBAC monthly with kubectl auth can-i.</p></details></div>
'@

Write-Host "Ch10: +6"

# Ch11: +5 (5->10) - Secrets Management
Add-Questions "This Secret type stores Docker registry credentials. Used as imagePullSecrets in pod specs to authenticate to private registries like ghcr.io.</p></details></div>" @'

                    <div class="drill-scenario"><h5>Q6: What is the difference between Sealed Secrets and External Secrets Operator?</h5><ol><li>No difference</li><li>Sealed Secrets uses asymmetric encryption (no external deps); ESO syncs from cloud secret managers</li><li>Sealed Secrets is deprecated</li><li>ESO requires no external services</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Different architectures.</strong> Sealed Secrets: public key encrypts, private key in cluster decrypts — no external dependency. ESO: syncs secrets from AWS/Azure/GCP secret managers into K8s Secrets — requires cloud provider.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: Why should Secrets be mounted as files rather than env vars?</h5><ol><li>Files are faster</li><li>Env vars are visible via kubectl exec -- env and often leaked in logs/crash dumps</li><li>K8s requires file mounts</li><li>Files support larger data</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Env var exposure.</strong> Environment variables appear in kubectl exec -- env, process listings, crash dumps, and debug endpoints. File mounts (tmpfs) are isolated to the pod''s filesystem.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What does SOPS encrypt that makes it GitOps-friendly?</h5><ol><li>Entire Git repository</li><li>Individual values in YAML/JSON files — structure visible, secrets encrypted</li><li>Container images</li><li>Network traffic</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Individual YAML values.</strong> SOPS encrypts specific values while keeping the YAML structure readable. FluxCD natively decrypts SOPS at reconciliation time. ArgoCD needs argocd-vault-plugin.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: Which K8s Secret type stores TLS certificates?</h5><ol><li>Opaque</li><li>kubernetes.io/tls</li><li>kubernetes.io/dockerconfigjson</li><li>kubernetes.io/basic-auth</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. kubernetes.io/tls.</strong> TLS secrets require tls.crt and tls.key keys. Used for Ingress TLS termination. cert-manager creates these automatically from Let''s Encrypt certificates.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: What is the #1 misconception about Kubernetes Secrets?</h5><ol><li>They are encrypted by default</li><li>Base64 is encoding NOT encryption — Secrets are plaintext in etcd by default</li><li>Secrets are stored in memory only</li><li>Secrets auto-expire</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Base64 ≠ encryption.</strong> Default Secrets are base64-ENCODED, not encrypted. Anyone with etcd access can decode all Secrets. Always enable EncryptionConfiguration with aescbc or KMS.</p></details></div>
'@

Write-Host "Ch11: +5"

# Ch12: +6 (4->10) - Network Policies
Add-Questions "Database pods should have NO outbound connectivity — they only respond to incoming queries. This prevents data exfiltration if the DB is compromised.</p></details></div>" @'

                    <div class="drill-scenario"><h5>Q5: What is the difference between ipBlock and podSelector in NetworkPolicies?</h5><ol><li>No difference</li><li>ipBlock restricts by CIDR (external IPs); podSelector restricts by pod labels (internal)</li><li>podSelector is for external traffic</li><li>ipBlock is deprecated</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. External vs internal.</strong> ipBlock selects traffic by IP CIDR ranges (external). podSelector and namespaceSelector select by K8s labels (internal pods). Both can be combined in one rule.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: CiliumNetworkPolicy supports FQDN-based egress. What does this enable?</h5><ol><li>Faster pod startup</li><li>Allow egress to specific domain names (e.g., api.github.com) rather than IP ranges</li><li>Better CPU performance</li><li>Automatic scaling</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Domain-based rules.</strong> FQDN policies allow egress to specific domains. The CNI resolves DNS and dynamically updates allowed IPs — perfect for cloud APIs with changing IPs.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: What is micro-segmentation in the context of K8s networking?</h5><ol><li>Splitting clusters into smaller clusters</li><li>Dividing pods into security zones (DMZ/App/Data) with strict NetworkPolicies between zones</li><li>Using smaller container images</li><li>Running fewer pods per node</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Security zone isolation.</strong> Micro-segmentation creates security zones where traffic flows only through defined paths. DMZ zone can only reach App zone; App zone can only reach Data zone. Compromise in one zone doesn''t spread.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What does podSelector: {} with policyTypes: [Ingress, Egress] and NO rules achieve?</h5><ol><li>Allow all traffic</li><li>Default-deny-all — blocks all ingress AND all egress for all pods in namespace</li><li>Only deny ingress</li><li>No effect</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Total isolation.</strong> Empty podSelector selects all pods. No ingress/egress rules = nothing allowed. Pods in this namespace are completely isolated. Always add DNS egress exception.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: Which namespaceSelector pattern allows traffic from pods in namespace with label "env=prod"?</h5><ol><li>namespaceSelector: {}</li><li>namespaceSelector: {matchLabels: {env: prod}}</li><li>podSelector: {matchLabels: {env: prod}}</li><li>ipBlock: {cidr: 0.0.0.0/0}</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. namespaceSelector with matchLabels.</strong> namespaceSelector filters by namespace labels, not pod labels. Use this to allow all pods from a labeled namespace regardless of their individual pod labels.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: Why is Flannel NOT suitable for production security?</h5><ol><li>Too expensive</li><li>Flannel does NOT support NetworkPolicy enforcement — zero pod isolation possible</li><li>Too slow</li><li>Only works on Windows</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. No NetworkPolicy support.</strong> Flannel provides only basic pod networking. Without NetworkPolicy support, you cannot enforce any pod-to-pod traffic rules. Use Calico, Cilium, or Weave for production.</p></details></div>
'@

Write-Host "Ch12: +6"

# Ch13: +6 (4->10) - Audit Logging
Add-Questions "Multiple 403s from the same user/IP suggest someone probing what they can access — a common reconnaissance technique before an attack.</p></details></div>" @'

                    <div class="drill-scenario"><h5>Q5: What 4 pieces of information does Metadata audit level capture?</h5><ol><li>Everything including request body</li><li>Who (user), What (verb/resource), When (timestamp), Where (source IP) — without request/response body</li><li>Only timestamps</li><li>Only error codes</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Who/what/when/where.</strong> Metadata captures user, verb, resource, namespace, source IP, response code — everything needed for forensics without the overhead of request/response bodies.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: Which audit backend is better for centralized SIEM integration?</h5><ol><li>Log file</li><li>Webhook backend — sends audit events as HTTP POST to external collector</li><li>Stdout</li><li>Both are equal</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Webhook backend.</strong> Webhook sends audit events to external systems (Splunk, ELK, custom SIEM) in real-time. Log file requires log shippers to collect and forward.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: Why would you use RequestResponse level specifically for Secret access?</h5><ol><li>It is required by K8s</li><li>To capture exactly WHICH secret was read and by whom — critical for breach investigation</li><li>It is faster than Metadata</li><li>No reason — Metadata is always better</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Forensic detail for Secrets.</strong> For Secret access, you need to know exactly which Secret was accessed. Metadata only shows "someone read a secret" — not which one. RequestResponse captures the full details.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What happens if audit log disk fills up on the API server?</h5><ol><li>Nothing — logs auto-delete</li><li>API server stops accepting requests — cluster outage</li><li>Old logs are compressed</li><li>Logs are sent to cloud</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cluster outage.</strong> If the audit log disk fills and no rotation is configured, the API server stops. Always set --audit-log-maxsize, --audit-log-maxbackup, --audit-log-maxage for automatic rotation.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: Which audit stage captures the request after authorization but before admission?</h5><ol><li>RequestReceived</li><li>ResponseStarted</li><li>ResponseComplete</li><li>Panic</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 1. RequestReceived.</strong> Audit stages: RequestReceived (after auth, before admission), ResponseStarted (headers sent), ResponseComplete (body sent), Panic (request caused panic).</p></details></div>
                    <div class="drill-scenario"><h5>Q10: How should you ship audit logs for long-term retention?</h5><ol><li>Keep them on API server disk</li><li>Fluent Bit/Fluentd → Loki/ELK/Splunk → long-term S3/GCS archival</li><li>Delete after 24 hours</li><li>Email them daily</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Centralized pipeline.</strong> API server → audit log file → Fluent Bit (DaemonSet) → Loki/ELK/Splunk → S3 archival. Retain for compliance period (typically 1-7 years depending on framework).</p></details></div>
'@

Write-Host "Ch13: +6"

Set-Content $f -Value $c -NoNewline
Write-Host "Total changes: $changes. File saved."