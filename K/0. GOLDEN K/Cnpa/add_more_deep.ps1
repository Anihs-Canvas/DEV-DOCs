
$file = 'c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html'
$txt = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# ── Ch12 Deep Content (CI Pipelines deep architecture, insert before <div id="ch13">) ──
$deep12 = @"

            <!-- ═══ DEEP DIVE: CI Pipeline Architecture Beyond "Lint, Test, Build" ═══ -->
            <div class="key-concept">
                <h4>🔬 Deep Dive: A CI Pipeline Is a Distributed System — Treat It Like One</h4>
                <p>Most engineers think of CI pipelines as sequential scripts: lint → test → build → deploy. Platform engineers think of them as <strong>distributed systems with concurrency, failure modes, caching strategies, and SLAs.</strong> A CI pipeline that takes 45 minutes is a platform failure — developers stop pushing code and start batching changes, which INCREASES merge conflicts, which slows everything down further. The CNPA expects you to design CI pipelines as optimized distributed workflows, not linear scripts.</p>
            </div>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">⚡ The Fail-Fast Architecture — Order Matters More Than Speed</h4>
            <p>The most important CI optimization is NOT parallelizing everything. It's ordering stages from CHEAPEST to MOST EXPENSIVE so failures are caught as early as possible:</p>
            <div class="stat-banner">
                <div class="stat-banner-item"><span class="sb-val c-green">~30s</span><span class="sb-lbl">Lint — Cheapest. Catches syntax/style errors.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-blue">~2min</span><span class="sb-lbl">Unit Tests — Catch logic errors, regressions.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-purple">~3min</span><span class="sb-lbl">Build — Docker image creation. Layer cached.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-amber">~1min</span><span class="sb-lbl">Scan — Trivy/Snyk vulnerability detection.</span></div>
                <div class="stat-banner-item"><span class="sb-val c-pink">~30s</span><span class="sb-lbl">Sign & Push — Cosign signature + registry push.</span></div>
            </div>
            <p style="margin-top:16px;">If lint catches an unused import, the developer gets feedback in <strong>30 seconds</strong> instead of waiting 6+ minutes for the full pipeline. This is the fail-fast principle: most pipelines succeed, but when they fail, every second counts. Developer frustration is directly correlated with feedback loop duration — and platform engineering is about reducing developer frustration.</p>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">🔑 Cache Key Design — The Most Underrated CI Skill</h4>
            <p>A poorly designed cache key wastes more compute than no cache at all. A well-designed cache key saves millions of build-minutes per year:</p>
            <div class="split-panel">
                <div class="split-side split-bad"><h5>❌ Bad Cache Keys</h5><p><strong>Date-based:</strong> "cache-2026-06-22" — changes daily even if deps haven't changed. <strong>Branch-based:</strong> "cache-main" — different branches get different caches even with identical deps. <strong>No restore-keys:</strong> Exact match only — any dependency change invalidates the ENTIRE cache, requiring full reinstall.</p></div>
                <div class="split-side split-good"><h5>✅ Good Cache Keys</h5><p><strong>Content-hash:</strong> pip-${{"{{ runner.os }}"}}-${{"{{ hashFiles('requirements.txt') }}"}} — changes ONLY when deps change. <strong>Restore-keys fallback:</strong> pip-${{"{{ runner.os }}"}}- — uses most recent cache for partial matches. <strong>Multi-layer:</strong> Docker layer caching + pip cache + test result cache — each with independent keys.</p></div>
            </div>
            <div class="info-box tip"><h5>💡 CNPA Pattern: Cache Is Infrastructure, Not an Optimization</h5><p>Treat CI caching as PLATFORM INFRASTRUCTURE, not an afterthought. The platform team should provide pre-configured cache keys for every supported language (pip for Python, npm for Node.js, Maven for Java). Developers should never write cache keys — they should inherit them from the platform's golden path templates. This is what "reducing cognitive load" looks like in practice.</p></div>
"@

# ── Ch20 Deep Content (Operators, insert before <section class="chapter-section" id="part5">) ──
$deep20 = @"

            <!-- ═══ DEEP DIVE: Operators — Encoding Human Knowledge into Software ═══ -->
            <div class="key-concept">
                <h4>🔬 Deep Dive: An Operator Is a Senior Engineer Who Never Sleeps</h4>
                <p>The Operator pattern is the ultimate expression of platform engineering: take the knowledge of your BEST engineer — the one who knows exactly how to deploy, configure, heal, scale, backup, and upgrade PostgreSQL — and encode that knowledge into software that runs 24/7. An Operator doesn't get tired, doesn't forget steps, doesn't take vacation, and responds to failures in milliseconds instead of minutes. <strong>If a human must SSH into a machine to fix something, you don't have an Operator.</strong></p>
            </div>

            <h4 style="color:#60a5fa;margin:24px 0 16px;">🏆 Operator Maturity Levels — From Basic Controller to Autonomous Operator</h4>
            <div class="comparison-table"><table>
                <thead><tr><th>Level</th><th>Name</th><th>Capabilities</th><th>Example</th></tr></thead>
                <tbody>
                    <tr><td><strong>Level I</strong></td><td>Basic Install</td><td>Creates resources from CR. No lifecycle management. "Fire and forget."</td><td>A simple controller that creates a Deployment and Service when a CR is created.</td></tr>
                    <tr><td><strong>Level II</strong></td><td>Seamless Upgrades</td><td>Handles version upgrades. Rolling updates. Schema migrations.</td><td>PostgreSQL Operator that upgrades from v14 to v15 with zero downtime.</td></tr>
                    <tr><td><strong>Level III</strong></td><td>Full Lifecycle</td><td>Backup, restore, scaling, reconfiguration, failure recovery. All Day 2 operations automated.</td><td>Strimzi Kafka Operator — handles broker replacement, topic rebalancing, TLS rotation.</td></tr>
                    <tr><td class="winner"><strong>Level IV</strong></td><td>Deep Insights</td><td>Metrics, alerts, auto-tuning, predictive actions. The Operator not only fixes problems but PREVENTS them.</td><td>Prometheus Operator — auto-discovers ServiceMonitors, manages Alertmanager config, handles Thanos integration.</td></tr>
                    <tr><td><strong>Level V</strong></td><td>Autopilot</td><td>Fully autonomous. Human operators only set high-level policies. The Operator handles EVERYTHING.</td><td>Theoretical. No widely-used Operator has reached this level yet. This is the North Star.</td></tr>
                </tbody>
            </table></div>
            <div class="info-box warning"><h5>⚠️ CNPA Exam: What Makes a REAL Operator vs a Simple Controller</h5><p>A simple controller creates resources (Day 0). A production Operator manages the FULL lifecycle (Day 0 + Day 1 + Day 2). The exam will test this distinction: "Is a controller that creates a ConfigMap an Operator?" Answer: <strong>NO.</strong> It's just a controller. An Operator must handle Day 2 operations — healing, scaling, backup, upgrade. If it doesn't reduce human operational burden for ongoing management, it's not an Operator, it's just a CRD with a controller.</p></div>
"@

# Perform replacements
$txt = $txt.Replace('<div id="ch13">', $deep12 + '<div id="ch13">')
$txt = $txt.Replace('<section class="chapter-section" id="part5">', $deep20 + '<section class="chapter-section" id="part5">')

[System.IO.File]::WriteAllText($file, $txt, (New-Object System.Text.UTF8Encoding $false))
Write-Host "Deep content added to Ch12 and Ch20 successfully"
