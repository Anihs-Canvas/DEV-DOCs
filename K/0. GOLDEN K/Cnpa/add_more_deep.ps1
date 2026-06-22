
$file = 'c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html'
$txt = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

$deep12 = @'

            <!-- ═══ DEEP DIVE: CI Pipeline Architecture ═══ -->
            <div class="key-concept">
                <h4>🔬 Deep Dive: A CI Pipeline Is a Distributed System — Treat It Like One</h4>
                <p>Most engineers think of CI pipelines as sequential scripts: lint, test, build, deploy. Platform engineers think of them as <strong>distributed systems with concurrency, failure modes, caching strategies, and SLAs.</strong> A CI pipeline that takes 45 minutes is a platform failure — developers stop pushing code and start batching changes, which INCREASES merge conflicts. The CNPA expects you to design CI pipelines as optimized distributed workflows.</p>
            </div>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">⚡ The Fail-Fast Architecture — Order Matters More Than Parallelization</h4>
            <div class="stat-banner">
                <div class="stat-banner-item"><span class="sb-val c-green">~30s</span><span class="sb-lbl">Lint — Cheapest stage. Catches syntax errors.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-blue">~2min</span><span class="sb-lbl">Unit Tests — Catch logic errors, regressions.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-purple">~3min</span><span class="sb-lbl">Build — Docker image. Layer cached.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-amber">~1min</span><span class="sb-lbl">Scan — Trivy vulnerability scan.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-pink">~30s</span><span class="sb-lbl">Sign and Push to registry.</span></div>
            </div>
            <p style="margin-top:16px;">If lint catches an unused import, the developer gets feedback in <strong>30 seconds</strong> instead of waiting 6+ minutes for the full pipeline. Developer frustration is directly correlated with feedback loop duration — and platform engineering is about reducing developer frustration. <strong>The CNPA answer is always: run the cheapest checks first.</strong></p>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">🔑 Cache Key Design — The Most Underrated CI Skill</h4>
            <div class="split-panel">
                <div class="split-side split-bad"><h5>❌ Bad Cache Keys</h5><p><strong>Date-based:</strong> changes daily even if deps have not changed. <strong>Branch-based:</strong> different branches get different caches with identical deps. <strong>No restore-keys:</strong> any dep change invalidates the ENTIRE cache.</p></div>
                <div class="split-side split-good"><h5>✅ Good Cache Keys</h5><p><strong>Content-hash:</strong> key changes ONLY when deps change. <strong>Restore-keys fallback:</strong> uses most recent cache for partial matches. <strong>Multi-layer:</strong> Docker layer + pip cache + test cache — independent keys for each.</p></div>
            </div>
            <div class="info-box tip"><h5>💡 Cache Is Platform Infrastructure</h5><p>The platform team should provide pre-configured cache keys for every supported language. Developers should never write cache keys — they inherit them from golden path templates. This is cognitive load reduction in practice.</p></div>
'@

$deep20 = @'

            <!-- ═══ DEEP DIVE: Operators Encode Human Knowledge ═══ -->
            <div class="key-concept">
                <h4>🔬 Deep Dive: An Operator Is a Senior Engineer Who Never Sleeps</h4>
                <p>The Operator pattern is the ultimate expression of platform engineering: take the knowledge of your BEST engineer — the one who knows exactly how to deploy, configure, heal, scale, backup, and upgrade PostgreSQL — and encode that knowledge into software that runs 24/7. An Operator does not get tired, does not forget steps, and responds to failures in milliseconds. <strong>If a human must SSH into a machine to fix something, you do not have an Operator.</strong></p>
            </div>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">🏆 Operator Maturity Levels</h4>
            <div class="comparison-table"><table>
                <thead><tr><th>Level</th><th>Name</th><th>Capabilities</th><th>Example</th></tr></thead>
                <tbody>
                    <tr><td><strong>Level I</strong></td><td>Basic Install</td><td>Creates resources from CR. No lifecycle mgmt.</td><td>Simple controller: create Deployment when CR created.</td></tr>
                    <tr><td><strong>Level II</strong></td><td>Seamless Upgrades</td><td>Version upgrades, rolling updates, schema migrations.</td><td>PostgreSQL Operator: v14 to v15 with zero downtime.</td></tr>
                    <tr><td><strong>Level III</strong></td><td>Full Lifecycle</td><td>Backup, restore, scaling, failure recovery. All Day 2 automated.</td><td>Strimzi Kafka: broker replacement, TLS rotation.</td></tr>
                    <tr><td class="winner"><strong>Level IV</strong></td><td>Deep Insights</td><td>Metrics, alerts, auto-tuning, predictive actions. PREVENTS problems.</td><td>Prometheus Operator: auto-discovers ServiceMonitors.</td></tr>
                    <tr><td><strong>Level V</strong></td><td>Autopilot</td><td>Fully autonomous. Humans set high-level policies only.</td><td>Theoretical. The North Star for Operator development.</td></tr>
                </tbody>
            </table></div>
            <div class="info-box warning"><h5>⚠️ CNPA Exam: Controller vs REAL Operator</h5><p>A simple controller creates resources (Day 0). A production Operator manages the FULL lifecycle (Day 0+1+2). The exam asks: "Is a controller that creates a ConfigMap an Operator?" Answer: NO — it is just a controller. An Operator MUST handle Day 2 operations (healing, scaling, backup, upgrade) to qualify.</p></div>
'@

$txt = $txt.Replace('<div id="ch13">', $deep12 + '<div id="ch13">')
$txt = $txt.Replace('<section class="chapter-section" id="part5">', $deep20 + '<section class="chapter-section" id="part5">')

[System.IO.File]::WriteAllText($file, $txt, (New-Object System.Text.UTF8Encoding $false))
Write-Host "Deep content added to Ch12 and Ch20"
