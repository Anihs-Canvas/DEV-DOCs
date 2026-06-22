
$file = 'c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html'
$txt = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

$execSummary = @'

    <!-- ══════════════════════════════════════════════════════
         EXECUTIVE SUMMARY & IMPLEMENTATION GUIDE
         ══════════════════════════════════════════════════════ -->

    <!-- Master Overview Hero -->
    <div class="hero-banner">
        <h2>CNPA Complete Study Guide -- Executive Summary</h2>
        <p class="hero-desc">This guide provides <strong>100% coverage of all 6 CNPA exam domains</strong> through 26 chapters, 260+ practice questions, 10 appendices, and hands-on learning with the anihpj/jobpost Django application. Below: what you will learn, how to use this guide, and the implementation roadmap to CNPA certification.</p>
        <div class="hero-stats">
            <div class="hero-stat"><span class="stat-val">26</span><span class="stat-lbl">Chapters</span></div>
            <div class="hero-stat"><span class="stat-val">260+</span><span class="stat-lbl">Practice Qs</span></div>
            <div class="hero-stat"><span class="stat-val">6</span><span class="stat-lbl">Exam Domains</span></div>
            <div class="hero-stat"><span class="stat-val">10</span><span class="stat-lbl">Appendices</span></div>
            <div class="hero-stat accent"><span class="stat-val">100%</span><span class="stat-lbl">Exam Coverage</span></div>
        </div>
    </div>

    <!-- Domain Coverage -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">CNPA Exam Domain Coverage at a Glance</h2>
    <div class="stat-banner">
        <div class="stat-banner-item"><span class="sb-val c-green">36%</span><span class="sb-lbl">Domain 1: Core Fundamentals (Ch 1-6)</span></div>
        <div class="stat-banner-item"><span class="sb-val c-blue">20%</span><span class="sb-lbl">Domain 2: Observability & Security (Ch 7-11)</span></div>
        <div class="stat-banner-item"><span class="sb-val c-purple">16%</span><span class="sb-lbl">Domain 3: Continuous Delivery (Ch 12-16)</span></div>
        <div class="stat-banner-item"><span class="sb-val c-amber">12%</span><span class="sb-lbl">Domain 4: APIs & Provisioning (Ch 17-20)</span></div>
        <div class="stat-banner-item"><span class="sb-val c-pink">8%</span><span class="sb-lbl">Domain 5: IDPs & DevEx (Ch 21-24)</span></div>
        <div class="stat-banner-item"><span class="sb-val c-red">8%</span><span class="sb-lbl">Domain 6: Measuring (Ch 25-26)</span></div>
    </div>

    <!-- What You Will Learn -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">What You Will Learn -- Domain-by-Domain</h2>
    <div class="glow-card-grid">
        <div class="glow-card green"><span class="glow-icon">📚</span><h5>Domain 1: Core Fundamentals (36%)</h5><p><strong>Ch 1-6.</strong> Platform engineering principles, declarative resource management, DevOps (CAMS), app environments, platform architecture, CI fundamentals, CD & GitOps overview. <strong>Learn:</strong> Why platforms exist and how to design them.</p></div>
        <div class="glow-card blue"><span class="glow-icon">🔐</span><h5>Domain 2: Observability & Security (20%)</h5><p><strong>Ch 7-11.</strong> Metrics/Logs/Traces, mTLS/cert-manager, Policy engines (Kyverno/OPA), K8s security, CI/CD security. <strong>Learn:</strong> How to make your platform observable and secure by default.</p></div>
        <div class="glow-card purple"><span class="glow-icon">🚀</span><h5>Domain 3: Continuous Delivery (16%)</h5><p><strong>Ch 12-16.</strong> CI pipeline architecture, incident response, deployment strategies, GitOps with ArgoCD, progressive delivery. <strong>Learn:</strong> How to ship code to production safely and automatically.</p></div>
        <div class="glow-card amber"><span class="glow-icon">🔌</span><h5>Domain 4: APIs & Provisioning (12%)</h5><p><strong>Ch 17-20.</strong> K8s reconciliation loop, CRDs, Crossplane/Terraform, Operator pattern. <strong>Learn:</strong> How to extend Kubernetes with your own APIs and automate infrastructure.</p></div>
        <div class="glow-card pink"><span class="glow-icon">🎭</span><h5>Domain 5: IDPs & DevEx (8%)</h5><p><strong>Ch 21-24.</strong> Internal Developer Platforms, service catalogs, Backstage portal, AI/ML automation. <strong>Learn:</strong> How to build the unified developer experience.</p></div>
        <div class="glow-card green"><span class="glow-icon">📊</span><h5>Domain 6: Measuring Your Platform (8%)</h5><p><strong>Ch 25-26.</strong> Efficiency metrics, SPACE framework, DORA metrics. <strong>Learn:</strong> How to prove your platform is working with data, not opinions.</p></div>
    </div>

    <!-- Implementation Guide -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">How to Implement This Study Guide</h2>
    <div class="key-concept"><h4>Three Usage Modes: Study, Build, Reference</h4><p>(1) <strong>Structured exam prep</strong> -- follow the 8-week plan below. (2) <strong>Hands-on platform building</strong> -- apply concepts to the anihpj/jobpost Django project. (3) <strong>On-the-job reference</strong> -- YAML skeleton cards, command tables, and exam trap callouts serve as quick job aids.</p></div>

    <div class="num-flow">
        <div class="num-step"><div class="num-circle c1">1</div><h5>READ</h5><p>Chapter intro + objectives</p></div>
        <div class="num-step"><div class="num-circle c2">2</div><h5>STUDY</h5><p>Diagrams, tables, deep dives</p></div>
        <div class="num-step"><div class="num-circle c3">3</div><h5>PRACTICE</h5><p>10 CNPA-style MCQs</p></div>
        <div class="num-step"><div class="num-circle c4">4</div><h5>BUILD</h5><p>Apply to anihpj/jobpost</p></div>
        <div class="num-step"><div class="num-circle c5">5</div><h5>REVIEW</h5><p>Visual summary grid</p></div>
        <div class="num-step"><div class="num-circle c6">6</div><h5>REFERENCE</h5><p>YAML cards for work</p></div>
    </div>

    <!-- Chapter Structure -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">How Each Chapter Is Structured</h2>
    <div class="layer-stack">
        <div class="layer-item l1"><span class="layer-num">1</span><div class="layer-content"><h5>Chapter Introduction</h5><p>Why this topic matters, connections, estimated study time.</p></div></div>
        <div class="layer-item l2"><span class="layer-num">2</span><div class="layer-content"><h5>Learning Objectives + Exam Quick Reference Cards</h5><p>What you will learn plus YAML skeleton cards and command reference tables.</p></div></div>
        <div class="layer-item l3"><span class="layer-num">3</span><div class="layer-content"><h5>Deep Content Sections (3-9 per chapter)</h5><p>Diagrams, comparison tables, split-panels, code blocks, scenario boxes with anihpj/jobpost.</p></div></div>
        <div class="layer-item l4"><span class="layer-num">4</span><div class="layer-content"><h5>Deep Dive + Practice Lab (10 MCQs)</h5><p>Beyond-the-exam WHY explanations plus CNPA-style questions with detailed answer analysis.</p></div></div>
        <div class="layer-item l5"><span class="layer-num">5</span><div class="layer-content"><h5>Visual Summary + Cross-Chapter Connections</h5><p>6 key takeaways in a card grid. How this chapter connects to other CNPA domains.</p></div></div>
    </div>

    <!-- 8-Week Plan -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">8-Week Implementation Plan</h2>
    <div class="comparison-table"><table>
        <thead><tr><th>Week</th><th>Focus</th><th>Chapters</th><th>Hours</th><th>Key Milestone</th></tr></thead>
        <tbody>
            <tr><td><strong>Week 1</strong></td><td>Pre-Learning + Domain 1 Start</td><td>F.1-F.6, Ch 1-2</td><td>~8h</td><td>Why platforms exist. Declarative vs imperative mastery.</td></tr>
            <tr><td><strong>Week 2</strong></td><td>Domain 1 Complete</td><td>Ch 3-6</td><td>~8h</td><td>DevOps, environments, architecture, CI, CD+GitOps overview.</td></tr>
            <tr><td><strong>Week 3</strong></td><td>Domain 2 Part 1</td><td>Ch 7-9</td><td>~8h</td><td>Observability pillars. Policy engines. Secure communication.</td></tr>
            <tr><td><strong>Week 4</strong></td><td>Domain 2 Part 2</td><td>Ch 10-11</td><td>~6h</td><td>K8s security essentials. CI/CD pipeline security.</td></tr>
            <tr><td><strong>Week 5</strong></td><td>Domain 3</td><td>Ch 12-16</td><td>~10h</td><td>CI deep dive, incidents, deployment strategies, GitOps.</td></tr>
            <tr><td><strong>Week 6</strong></td><td>Domain 4</td><td>Ch 17-20</td><td>~8h</td><td>Reconciliation, CRDs, Crossplane, Operators.</td></tr>
            <tr><td><strong>Week 7</strong></td><td>Domain 5</td><td>Ch 21-24</td><td>~6h</td><td>IDPs, Backstage, service catalogs, AI/ML automation.</td></tr>
            <tr><td><strong>Week 8</strong></td><td>Domain 6 + Review</td><td>Ch 25-26, All MCQs</td><td>~6h</td><td>DORA metrics, platform measurement. Review all questions.</td></tr>
        </tbody>
    </table></div>
    <p style="color:#8b949e;text-align:center;font-size:0.85em;margin-top:8px;"><strong>Total: ~60 hours.</strong> Beginners: 10-12 weeks. Experienced K8s users: 4-6 weeks.</p>

    <!-- anihpj Project -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">The anihpj/jobpost Project -- Your Hands-On Lab</h2>
    <div class="split-panel">
        <div class="split-side split-good"><h5>What You Will Build</h5><p>Deploy a real Django job posting platform:</p><ul><li>Multi-stage Docker builds</li><li>Kubernetes declarative deployment</li><li>GitHub Actions CI/CD</li><li>ArgoCD GitOps</li><li>Prometheus/Grafana/Loki observability</li><li>Kyverno security policies</li><li>Crossplane infrastructure</li><li>Backstage IDP portal</li></ul></div>
        <div class="split-side split-good"><h5>Workspace Structure</h5><p><code>anihpj/</code> directory:</p><ul><li><code>manage.py</code> -- Django commands</li><li><code>anihpj/settings.py</code> -- Config</li><li><code>jobpost/models.py</code> -- Data models</li><li><code>jobpost/views.py</code> -- Request logic</li><li><code>Dockerfile</code> -- Multi-stage build</li><li><code>requirements.txt</code> -- Dependencies</li></ul><p style="margin-top:12px;"><code>db.sqlite3</code> has pre-loaded sample data.</p></div>
    </div>

    <!-- Differentiators -->
    <h2 style="color:#60a5fa;text-align:center;margin:40px 0 20px;font-size:1.6em;">What Makes This Guide Different</h2>
    <div class="card-grid cols-2">
        <div class="info-card highlight"><div class="card-icon-lg">🏭</div><h5>Platform-as-Product Mindset</h5><p>CNCF White Paper philosophy throughout. Platforms are products, not projects.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">🐍</div><h5>One Project, End-to-End</h5><p>Follow anihpj/jobpost through every phase for a coherent mental model.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">⚠️</div><h5>Exam Trap Callouts</h5><p>Wrong answers that look right. Know the traps, avoid points loss.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">📋</div><h5>YAML & Command Cards</h5><p>Quick-reference for CNPA-tested YAML skeletons and imperative commands.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">🔬</div><h5>Deep Dive Sections</h5><p>Beyond-the-exam WHY explanations for true understanding.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">🔗</div><h5>Cross-Domain Connections</h5><p>Every chapter maps to other CNPA domains for integrative thinking.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">📊</div><h5>Rich Visual Design</h5><p>Diagrams, tables, glow cards, stat banners, layer stacks -- visual learning.</p></div>
        <div class="info-card highlight"><div class="card-icon-lg">✅</div><h5>260+ Practice Questions</h5><p>10 CNPA-style MCQs per chapter with detailed answer explanations.</p></div>
    </div>

    <!-- Quick Start -->
    <div class="key-concept"><h4>Quick Start -- How to Begin RIGHT NOW</h4><p><strong>5 min:</strong> Read this summary. <strong>30 min:</strong> Read Pre-Learning F.1-F.3. <strong>2 hours:</strong> Complete Chapter 1. <strong>Exam-focused:</strong> Jump to Exam Strategy. <strong>Building a platform:</strong> Start with Ch 5 (Architecture) + Ch 21 (IDPs).</p></div>

'@

# Use intro-callout as unique marker
$marker = '<div class="intro-callout">'
$txt = $txt.Replace($marker, $execSummary + '    ' + $marker)

$ok = $txt.Contains('Executive Summary')
Write-Host "Inserted: $ok"
[System.IO.File]::WriteAllText($file, $txt, (New-Object System.Text.UTF8Encoding $false))
