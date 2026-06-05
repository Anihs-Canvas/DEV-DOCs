$f = "KCSA.html"
$c = Get-Content $f -Raw

# Use the exact anchor text from the file
$anchor = "nothing allowed.</p></details></div>"
$idx = $c.IndexOf($anchor)
Write-Host "Anchor at: $idx"

$newQs = @'

                    <div class="drill-scenario"><h5>Q3: Which CNI plugin supports L7 (HTTP path/method) NetworkPolicies?</h5><ol><li>Flannel</li><li>Cilium</li><li>Calico</li><li>Weave</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cilium.</strong> Cilium uses eBPF for L7 policies (HTTP method/path, gRPC, Kafka, DNS). Calico supports L3/L4 only. Flannel has NO NetworkPolicy support.</p></details></div>
                    <div class="drill-scenario"><h5>Q4: Why must DNS egress (port 53 UDP) be allowed in NetworkPolicies?</h5><ol><li>Required by API server</li><li>Without DNS, pods cannot resolve Service names</li><li>DNS uses less bandwidth</li><li>K8s requirement</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service resolution breaks.</strong> Without DNS egress, pods cannot resolve Service DNS names. Always add DNS egress to kube-system with any default-deny policy.</p></details></div>
                    <div class="drill-scenario"><h5>Q5: What security risk does hostPath volume pose?</h5><ol><li>No risk</li><li>Direct host filesystem access — enables container escape</li><li>Slower I/O</li><li>Only works on Linux</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Host filesystem access.</strong> hostPath mounts node directories into pods. A compromised container can read/write host files. PSS Restricted blocks hostPath entirely.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: How should Secrets be mounted for maximum security?</h5><ol><li>As environment variables</li><li>As tmpfs (memory-backed) file mounts</li><li>Hardcoded in Dockerfile</li><li>In ConfigMaps</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. tmpfs file mounts.</strong> K8s mounts Secrets as tmpfs by default — memory-only. Environment variables expose secrets via kubectl exec -- env.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: What does AlwaysPullImages admission controller prevent?</h5><ol><li>Pod creation</li><li>Using cached/stale images — force fresh pull on every pod start</li><li>Network egress</li><li>Secret access</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cached image attacks.</strong> AlwaysPullImages contacts the registry every pod start. Prevents exploiting cached images that may be tampered with on the node.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What is kube-proxy''s function in K8s networking?</h5><ol><li>Encrypt pod traffic</li><li>Program iptables/IPVS rules for Service-to-pod routing</li><li>Scan images</li><li>Manage RBAC</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service networking rules.</strong> kube-proxy programs iptables/IPVS. Secure port 10249. eBPF-based CNIs (Cilium) can replace kube-proxy entirely.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: What is the recommended production Ingress TLS setup?</h5><ol><li>HTTP only</li><li>Self-signed certificates</li><li>TLS 1.3 + cert-manager auto-renewing certificates</li><li>TLS 1.0 with any certificate</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 3. TLS 1.3 + auto-renewal.</strong> Use cert-manager with Let''s Encrypt. Enforce TLS 1.3 minimum. Never use self-signed certs in production.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: How do you secure kubeconfig files?</h5><ol><li>Commit to GitHub</li><li>chmod 600 ~/.kube/config — owner-only access</li><li>Email to teammates</li><li>Store on shared drive</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. chmod 600.</strong> Restrict to owner-only. Use separate contexts. Never commit to Git. Use client certificates over static tokens.</p></details></div>
'@

$c = $c.Substring(0, $idx + $anchor.Length) + $newQs + $c.Substring($idx + $anchor.Length)
Set-Content $f -Value $c -NoNewline
Write-Host "Ch8 done: 10 questions"