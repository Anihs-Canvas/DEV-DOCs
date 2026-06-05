$f = "KCSA.html"
$c = Get-Content $f -Raw

# Ch8: Add 8 Qs
$ch8old = 'Nothing allowed.</p></details></div>
                </div>
            </div>

        </section>

        <!-- ============================================ -->
        <!--              PART 3: SECURITY FUNDAMENTALS   -->'

$ch8new = 'Nothing allowed.</p></details></div>
                    <div class="drill-scenario"><h5>Q3: Which CNI plugin supports L7 (HTTP path/method) NetworkPolicies?</h5><ol><li>Flannel</li><li>Cilium</li><li>Calico</li><li>Weave</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cilium.</strong> Cilium uses eBPF and supports L7 policies (HTTP method/path, gRPC, Kafka, DNS). Calico supports L3/L4 only. Flannel has NO NetworkPolicy support whatsoever.</p></details></div>
                    <div class="drill-scenario"><h5>Q4: Why must DNS egress (port 53 UDP) always be allowed in NetworkPolicies?</h5><ol><li>DNS is required by the API server</li><li>Without DNS, pods cannot resolve Service names — everything breaks</li><li>DNS uses less bandwidth than HTTP</li><li>It is a K8s certification requirement</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service resolution breaks.</strong> If DNS egress is blocked, pods cannot resolve Service DNS names (e.g., anihpj-api.anihpj.svc.cluster.local). Even with default-deny, always add a DNS egress rule to kube-system namespace.</p></details></div>
                    <div class="drill-scenario"><h5>Q5: What security risk does hostPath volume pose?</h5><ol><li>No risk — it is safe by design</li><li>Direct host filesystem access — enables container escape and host compromise</li><li>Slower I/O than other volume types</li><li>Only works on Linux nodes</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Direct host filesystem access.</strong> hostPath mounts a node directory into the pod. Compromised container can read/write host files, access other pods data, or plant persistence. PSS Restricted blocks hostPath entirely.</p></details></div>
                    <div class="drill-scenario"><h5>Q6: How should Secrets be mounted in pods for maximum security?</h5><ol><li>As environment variables</li><li>As tmpfs (memory-backed) file mounts — never touches node disk</li><li>Hardcoded in the Dockerfile</li><li>In ConfigMaps alongside config data</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. tmpfs file mounts.</strong> K8s mounts Secrets as tmpfs by default — memory-only, never written to disk. Environment variables expose secrets via kubectl exec -- env. File mounts are more secure.</p></details></div>
                    <div class="drill-scenario"><h5>Q7: What does the AlwaysPullImages admission controller prevent?</h5><ol><li>Pods from being created</li><li>Using cached/stale images — forces fresh pull from registry on every pod start</li><li>Network egress from pods</li><li>Secret access from containers</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Cached image attacks.</strong> AlwaysPullImages ensures kubelet contacts the registry on every pod start. Prevents attackers from exploiting cached images that may have been tampered with on the node.</p></details></div>
                    <div class="drill-scenario"><h5>Q8: What is the security function of kube-proxy in a cluster?</h5><ol><li>Encrypt pod-to-pod traffic</li><li>Program iptables/IPVS rules so Service ClusterIPs route to healthy backend pods</li><li>Scan container images for CVEs</li><li>Manage RBAC policies</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Service networking rules.</strong> kube-proxy programs iptables/IPVS rules for Service-to-pod traffic routing. Secure its metrics port (10249) behind localhost. eBPF-based CNIs like Cilium can replace kube-proxy entirely.</p></details></div>
                    <div class="drill-scenario"><h5>Q9: What is the recommended Ingress TLS configuration for production?</h5><ol><li>HTTP only — TLS not needed for internal traffic</li><li>Self-signed certificates</li><li>TLS 1.3 minimum with cert-manager auto-renewing certificates</li><li>TLS 1.0 with any certificate</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 3. TLS 1.3 with auto-renewal.</strong> Use cert-manager with Let''s Encrypt for automatic TLS certificate lifecycle. Enforce TLS 1.3 minimum. Never use self-signed certs in production — they train users to bypass security warnings.</p></details></div>
                    <div class="drill-scenario"><h5>Q10: How should you protect kubeconfig files from unauthorized access?</h5><ol><li>Commit to public GitHub repository</li><li>chmod 600 ~/.kube/config — restrict to owner read/write only</li><li>Email to team members for backup</li><li>Store on a shared network drive</li></ol></div>
                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. chmod 600.</strong> Restrict kubeconfig to owner-only access. Use separate contexts per cluster. Never commit to Git. Use `kubectl config set-credentials` with client certificates instead of static tokens for authentication.</p></details></div>
                </div>
            </div>

        </section>

        <!-- ============================================ -->
        <!--              PART 3: SECURITY FUNDAMENTALS   -->'

if ($c.Contains($ch8old)) { 
    $c = $c.Replace($ch8old, $ch8new)
    Set-Content $f -Value $c -NoNewline
    Write-Host "Ch8 updated: +8 questions (2->10)" 
} else { 
    Write-Host "ERROR: Ch8 anchor NOT found" 
}