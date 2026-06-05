$f = "KCSA.html"
$c = Get-Content $f -Raw

# Find Ch8 drill end
$ch8Anchor = 'Nothing allowed.</p></details></div>'
$idx = $c.IndexOf($ch8Anchor)
if ($idx -lt 0) { Write-Host "Ch8 anchor NOT found"; exit 1 }
Write-Host "Ch8 anchor found at position $idx"

# Get everything after the anchor
$after = $c.Substring($idx + $ch8Anchor.Length)

# New Q3-Q10
$newQs = @'
                    <div class="drill-scenario"><h5>Q3: Which CNI plugin supports L7 (HTTP path/method) NetworkPolicies?</h5><ol><li>Flannel</li><li>Cilium</li><li>Calico</li><li>Weave</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cilium.</strong> Cilium uses eBPF for L7 policies (HTTP method/path, gRPC, Kafka, DNS). Calico supports L3/L4 only. Flannel has NO NetworkPolicy support.</p></details></div>
                    <div class="drill-scenario"><h5>Q4: Why must DNS egress (port 53 UDP) always be allowed in NetworkPolicies?</h5><ol><li>Required by API server</li><li>Without DNS, pods cannot resolve Service names — everything breaks</li><li>DNS uses less bandwidth</li><li>K8s certification requirement</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service resolution breaks.</strong> With default-deny, always add DNS egress to kube-system. Without it, pods cannot resolve Service DNS names like anihpj-api.anihpj.svc.cluster.local.</p></details></div>
                    <div class="drill-scenario"><h5>Q5: What security risk does hostPath volume pose?</h5><ol><li>No risk — safe by design</li><li>Direct host filesystem access — enables container escape</li><li>Slower I/O than other volumes</li><li>Only works on Linux</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Host filesystem access.</strong> hostPath mounts node directories into pods. Compromised container can read/write host files or plant persistence. PSS Restricted blocks hostPath.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: How should Secrets be mounted for maximum security?</h5><ol><li>As environment variables</li><li>As tmpfs (memory-backed) file mounts</li><li>Hardcoded in Dockerfile</li><li>In ConfigMaps alongside config</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. tmpfs file mounts.</strong> K8s mounts Secrets as tmpfs — memory-only, never disk. Environment variables expose secrets via kubectl exec -- env. File mounts are more secure.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: What does AlwaysPullImages admission controller prevent?</h5><ol><li>Pod creation</li><li>Using cached/stale images — forces fresh pull on every pod start</li><li>Network egress</li><li>Secret access from containers</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cached image attacks.</strong> AlwaysPullImages contacts the registry on every pod start, preventing attackers from exploiting cached images that may have been tampered with on the node.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What is the security role of kube-proxy in K8s networking?</h5><ol><li>Encrypt pod traffic</li><li>Program iptables/IPVS rules for Service-to-pod traffic routing</li><li>Scan images for CVEs</li><li>Manage RBAC</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service networking rules.</strong> kube-proxy programs iptables/IPVS rules. Secure its metrics port (10249). eBPF-based CNIs like Cilium can replace kube-proxy entirely.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: What is the recommended production Ingress TLS setup?</h5><ol><li>HTTP only — no TLS needed</li><li>Self-signed certificates</li><li>TLS 1.3 with cert-manager auto-renewing certificates</li><li>TLS 1.0 with any certificate</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 3. TLS 1.3 + auto-renewal.</strong> cert-manager with Let''s Encrypt automates TLS lifecycle. Enforce TLS 1.3 minimum. Never use self-signed certs in production.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: How should you secure kubeconfig files?</h5><ol><li>Commit to public GitHub</li><li>chmod 600 ~/.kube/config — owner read/write only</li><li>Email to teammates</li><li>Store on shared drive</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. chmod 600.</strong> Restrict to owner-only. Use separate contexts per cluster. Never commit to Git. Prefer client certificates over static tokens for authentication.</p></details></div>
'@

$c = $c.Substring(0, $idx + $ch8Anchor.Length) + $newQs + $after
Set-Content $f -Value $c -NoNewline
Write-Host "Ch8 updated: +8 questions (2->10)"