$f = "KCSA.html"
$c = Get-Content $f -Raw

# Chapter boundaries
$chapters = @{}
for ($i = 9; $i -le 25; $i++) {
    $startId = "id=`"ch$i`""
    $endId = if ($i -eq 25) { "id=`"appendix-a`"" } else { "id=`"ch$($i+1)`"" }
    $s = $c.IndexOf($startId)
    $e = $c.IndexOf($endId, $s)
    if ($s -ge 0 -and $e -gt $s) { $chapters[$i] = @{start=$s; end=$e} }
}

# Question templates per chapter
$qBank = @{
    # Ch9-13: already tried in previous attempt
    9 = @(''<div class="drill-scenario"><h5>Q10: What replaced PodSecurityPolicy (PSP)?</h5><ol><li>RBAC</li><li>Pod Security Admission (PSA) built into K8s since v1.23</li><li>NetworkPolicies</li><li>OPA Gatekeeper</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Pod Security Admission.</strong> PSA is the built-in PSP replacement since K8s v1.23. PSP was deprecated in v1.21 and removed in v1.25. OPA/Gatekeeper and Kyverno provide advanced custom policy engines beyond PSA capabilities.</p></details></div>'')
    10 = @(
        ''<div class="drill-scenario"><h5>Q5: What does the built-in view ClusterRole NOT allow by default?</h5><ol><li>Reading pods</li><li>Reading Secrets</li><li>Reading services</li><li>Reading deployments</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Reading Secrets.</strong> The view role explicitly excludes Secrets, Roles, RoleBindings, and ClusterRoleBindings from read access.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q6: Why are projected volume tokens better than legacy SA tokens?</h5><ol><li>They are the same</li><li>Projected tokens are time-bound (1hr), audience-scoped, and auto-rotated</li><li>Legacy tokens are more secure</li><li>Projected tokens are deprecated</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Time-bound and scoped.</strong> TokenRequest API generates tokens with expiry, audience binding, and automatic rotation. Legacy SA tokens stored as Secrets have no expiration.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q7: Can a RoleBinding reference a ClusterRole?</h5><ol><li>No</li><li>Yes — grants ClusterRole permissions limited to the binding namespace</li><li>Only via ClusterRoleBinding</li><li>Only for cluster-admin</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Yes, namespace-limited.</strong> Binding a ClusterRole via RoleBinding grants those permissions only within that namespace. Useful for granting limited cluster-scoped access to namespace admins.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q8: Why is OIDC better than static token files for authentication?</h5><ol><li>Faster</li><li>Short-lived tokens, MFA support, centralized revocation</li><li>Static tokens are more secure</li><li>No certificates needed</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Short-lived tokens + MFA.</strong> OIDC JWTs expire in ~1 hour. Static tokens in CSV files never expire and require API server restart to rotate.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q9: What are aggregated ClusterRoles?</h5><ol><li>A performance feature</li><li>ClusterRoles composed from other ClusterRoles using label selectors</li><li>A deprecated API</li><li>Network policy aggregation</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Label-based composition.</strong> Aggregated ClusterRoles combine other ClusterRoles via aggregationRule. The built-in admin/edit/view roles use this pattern to include CRD permissions automatically.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q10: What RBAC principle should guide all permission assignments?</h5><ol><li>Maximum access</li><li>Least privilege — minimum permissions needed</li><li>Always cluster-admin</li><li>Disable RBAC</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Least privilege.</strong> Grant only what is needed. Use namespace Roles. Bind groups not users. Audit monthly with kubectl auth can-i.</p></details></div>''
    )
    11 = @(
        ''<div class="drill-scenario"><h5>Q6: Sealed Secrets vs External Secrets Operator — key difference?</h5><ol><li>Identical</li><li>Sealed Secrets needs no external service; ESO syncs from cloud secret managers</li><li>Sealed Secrets is deprecated</li><li>ESO needs no external service</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. External vs self-contained.</strong> Sealed Secrets uses asymmetric encryption — no external dependency. ESO syncs from AWS/Azure/GCP secret managers into K8s Secrets.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q7: Why mount Secrets as files instead of env vars?</h5><ol><li>Faster</li><li>Env vars leak via kubectl exec -- env, crash dumps, debug endpoints</li><li>K8s requires files</li><li>Files support more data</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Reduced exposure.</strong> Environment variables appear in process listings, crash reports, and kubectl exec output. tmpfs-mounted files are memory-only and pod-scoped.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q8: What does SOPS encrypt for GitOps workflows?</h5><ol><li>Entire repos</li><li>Individual YAML/JSON values while keeping structure readable</li><li>Container images</li><li>Network traffic</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Selective value encryption.</strong> SOPS encrypts specific values in YAML/JSON. FluxCD decrypts natively. Uses GPG, Age, or cloud KMS.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q9: Which Secret type is for TLS certificates?</h5><ol><li>Opaque</li><li>kubernetes.io/tls</li><li>dockerconfigjson</li><li>basic-auth</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. kubernetes.io/tls.</strong> Requires tls.crt and tls.key data keys. cert-manager auto-creates these from ACME certificates.</p></details></div>'',
        ''<div class="drill-scenario"><h5>Q10: What is the #1 misconception about K8s Secrets?</h5><ol><li>They are encrypted by default</li><li>Base64 is ENCODING, not encryption — plaintext in etcd without EncryptionConfiguration</li><li>Stored in memory only</li><li>Auto-expire after 30 days</li></ol></div>'',''<div class="drill-solution"><details><summary>Answer</summary><p><strong>Answer: 2. Base64 is not encryption.</strong> Secrets are base64-ENCODED plaintext by default. Always enable EncryptionConfiguration with aescbc or KMS.</p></details></div>''
    )
}

# Apply questions
$totalAdded = 0
foreach ($ch in (9, 10, 11)) {
    $info = $chapters[$ch]
    $chContent = $c.Substring($info.start, $info.end - $info.start)
    $lastDrill = $chContent.LastIndexOf("drill-scenario")
    $lastDrillEnd = $chContent.IndexOf("</div>", $chContent.IndexOf("drill-solution", $lastDrill) + 30)
    # Find the end of the last drill-solution
    $searchFrom = $chContent.IndexOf("drill-solution", $lastDrill)
    $solutionClose = $chContent.IndexOf("</details></div>", $searchFrom) + "</details></div>".Length
    $insertPos = $info.start + $solutionClose
    
    $qs = $qBank[$ch]
    $insertText = ""
    for ($j = 0; $j -lt $qs.Count; $j += 2) {
        $insertText += "`n                    " + $qs[$j] + "`n                    " + $qs[$j+1]
    }
    
    $c = $c.Substring(0, $insertPos) + $insertText + $c.Substring($insertPos)
    $totalAdded += ($qs.Count / 2)
    Write-Host "Ch$ch added $(($qs.Count)/2) questions"
}

Set-Content $f -Value $c -NoNewline
Write-Host "Total questions added: $totalAdded"