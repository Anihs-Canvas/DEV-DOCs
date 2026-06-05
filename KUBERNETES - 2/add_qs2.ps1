$f = "KCSA.html"
$c = [System.IO.File]::ReadAllText((Resolve-Path $f))

# Function to get chapter content boundaries
function Get-Chapter($num) {
    $startTag = "id=`"ch$num`""
    $endTag = if ($num -eq 25) { "id=`"appendix-a`"" } else { "id=`"ch$($num+1)`"" }
    $s = $c.IndexOf($startTag)
    $e = $c.IndexOf($endTag, $s)
    if ($s -lt 0 -or $e -le $s) { return $null }
    return @{ start = $s; end = $e; text = $c.Substring($s, $e - $s) }
}

# Function to find last drill-solution closing in chapter text
function Find-InsertPoint($chText, $chStart) {
    $lastSolutionClose = $chText.LastIndexOf("</details></div>")
    if ($lastSolutionClose -lt 0) { return -1 }
    return $chStart + $lastSolutionClose + "</details></div>".Length
}

# Add questions for a chapter using positional insertion
function Add-ChapterQs($chNum, $qPairs) {
    $ch = Get-Chapter $chNum
    if ($null -eq $ch) { Write-Host "Ch$chNum`: CHAPTER NOT FOUND"; return }
    $insertAt = Find-InsertPoint $ch.text $ch.start
    if ($insertAt -lt 0) { Write-Host "Ch$chNum`: NO DRILL SECTION"; return }
    
    $insertText = ""
    foreach ($pair in $qPairs) {
        $insertText += "`n" + $pair[0] + "`n" + $pair[1]
    }
    
    $script:c = $c.Substring(0, $insertAt) + $insertText + $c.Substring($insertAt)
    Write-Host "Ch$chNum`: added $($qPairs.Count) Qs at pos $insertAt"
}

Write-Host "Starting insertion..."
$totalAdded = 0

# Ch9: +1 (9->10)
$q = @()
$q += ,@('                    <div class="drill-scenario"><h5>Q10: What is the correct evolution of pod security in Kubernetes?</h5><ol><li>PSA to PSP to OPA</li><li>PSP (deprecated v1.21) to PSA (built-in v1.23) to OPA/Kyverno for custom policies</li><li>RBAC to NetworkPolicy to PSS</li><li>OPA to Kyverno to PSP</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. PSP->PSA->OPA/Kyverno.</strong> PodSecurityPolicy was deprecated in v1.21 and removed in v1.25. Pod Security Admission (PSA) is the built-in replacement. OPA/Gatekeeper and Kyverno are external policy engines for custom policies beyond PSA.</p></details></div>')
Add-ChapterQs 9 $q

# Ch10: +6 (4->10)
$q = @()
$q += ,@('                    <div class="drill-scenario"><h5>Q5: What does the built-in view ClusterRole NOT allow by default?</h5><ol><li>Reading pods</li><li>Reading Secrets</li><li>Reading services</li><li>Reading deployments</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Reading Secrets.</strong> The view role explicitly excludes Secrets, Roles, RoleBindings, and ClusterRoleBindings. You must create a separate Role for Secret access.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q6: Why are projected volume tokens better than legacy SA tokens?</h5><ol><li>They are the same thing</li><li>Projected tokens are time-bound (1hr), audience-scoped, and automatically rotated by kubelet</li><li>Legacy tokens are more secure</li><li>Projected tokens are deprecated</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Time-bound and auto-rotated.</strong> TokenRequest API generates tokens with expiration, audience binding, and automatic rotation. Legacy SA tokens (stored as Secrets) have no expiry and survive forever.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q7: Can a RoleBinding reference a ClusterRole? What happens?</h5><ol><li>No — only Roles can be bound via RoleBinding</li><li>Yes — grants the ClusterRole permissions but limited to the binding namespace</li><li>Only via ClusterRoleBinding</li><li>This creates a cluster-admin binding</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Yes, namespace-limited.</strong> A RoleBinding referencing a ClusterRole grants that role permissions ONLY within the binding namespace. This lets namespace admins get limited cluster-scoped access (like node listing) without cluster-wide power.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q8: Why is OIDC superior to static token files for production?</h5><ol><li>OIDC is faster</li><li>OIDC provides short-lived tokens, MFA support, centralized revocation, and identity federation</li><li>Static tokens are more secure</li><li>OIDC works without certificates</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Short-lived tokens + MFA + revocation.</strong> OIDC JWTs expire in ~1 hour, support MFA at the IDP, and can be centrally revoked. Static tokens in CSV files never expire and require API server restart to change.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q9: How do aggregated ClusterRoles work?</h5><ol><li>They improve RBAC performance</li><li>They compose multiple ClusterRoles using label selectors — admin/edit/view roles use this to auto-include CRD permissions</li><li>They are a deprecated feature</li><li>They aggregate network policies</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Label-based composition.</strong> Aggregated ClusterRoles use aggregationRule.clusterRoleSelectors to combine other ClusterRoles matching labels. When you create a CRD with a properly labeled ClusterRole, it automatically joins admin/edit/view.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q10: What is the fundamental RBAC security principle?</h5><ol><li>Maximum privilege for operational efficiency</li><li>Least privilege — grant only the minimum permissions needed</li><li>Always use cluster-admin for simplicity</li><li>Disable RBAC and use network security instead</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Least privilege.</strong> Grant minimum permissions. Use namespace Roles. Bind OIDC groups (not individual users). Audit monthly. Never use cluster-admin for daily operations.</p></details></div>')
Add-ChapterQs 10 $q

# Ch11: +5 (5->10)
$q = @()
$q += ,@('                    <div class="drill-scenario"><h5>Q6: What is the key difference between Sealed Secrets and External Secrets Operator?</h5><ol><li>No functional difference</li><li>Sealed Secrets uses asymmetric encryption with NO external dependencies; ESO syncs from cloud secret managers</li><li>Sealed Secrets is deprecated</li><li>ESO requires no cloud services</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Self-contained vs cloud-synced.</strong> Sealed Secrets encrypts with public key, decrypts with cluster private key — zero external deps. ESO syncs from AWS/Azure/GCP secret managers into K8s Secrets automatically.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q7: Why mount Secrets as files rather than environment variables?</h5><ol><li>Files load faster</li><li>Environment variables leak via kubectl exec -- env, crash dumps, and debug endpoints. tmpfs mounts are memory-only</li><li>Kubernetes requires file mounts per specification</li><li>Files can store larger values</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Reduced exposure surface.</strong> Env vars appear in process listings (/proc), crash reports, debug pages, and kubectl exec output. tmpfs-mounted Secret files exist only in the pod memory namespace.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q8: What makes SOPS suitable for GitOps workflows?</h5><ol><li>It encrypts entire repositories</li><li>It encrypts individual YAML/JSON values while preserving structure — FluxCD decrypts natively at reconciliation</li><li>It signs container images</li><li>It manages network traffic encryption</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Selective value encryption.</strong> SOPS encrypts specific values in YAML/JSON files. YAML structure stays readable. FluxCD natively decrypts SOPS at sync time. Supports GPG, Age, or cloud KMS keys.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q9: Which Kubernetes Secret type holds TLS certificates?</h5><ol><li>Opaque</li><li>kubernetes.io/tls (requires tls.crt and tls.key)</li><li>kubernetes.io/dockerconfigjson</li><li>kubernetes.io/basic-auth</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. kubernetes.io/tls.</strong> TLS secrets need tls.crt and tls.key data keys. cert-manager auto-creates and renews these from ACME (Let''s Encrypt) certificates.</p></details></div>')
$q += ,@('                    <div class="drill-scenario"><h5>Q10: What is the most dangerous misconception about Kubernetes Secrets?</h5><ol><li>They are encrypted by default</li><li>Base64 is ENCODING, not encryption — Secrets are plaintext in etcd unless EncryptionConfiguration is configured</li><li>Secrets are stored only in memory</li><li>Secrets automatically expire after 30 days</li></ol></div>',
           '                    <div class="drill-solution"><details><summary>✅ Answer</summary><p><strong>Answer: 2. Base64 is not encryption.</strong> Default Secrets are base64-ENCODED plaintext. Anyone with etcd access can decode all secrets. Always enable EncryptionConfiguration with aescbc, aesgcm, or KMS provider for true encryption at rest.</p></details></div>')
Add-ChapterQs 11 $q

# Save
[System.IO.File]::WriteAllText((Resolve-Path $f), $c)
Write-Host "File saved. Size: $([math]::Round($c.Length/1024,1))KB"