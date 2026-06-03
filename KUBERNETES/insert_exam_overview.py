#!/usr/bin/env python3
"""Insert exam-overview section before Part 1"""
with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html", "r", encoding="utf-8") as f:
    content = f.read()

exam_overview = """    <!-- ═══════════════ EXAM OVERVIEW ═══════════════ -->
    <section class="chapter-section" id="exam-overview">
        <h2><span>🎯 Cilium CCA Exam Overview</span><span class="chapter-badge">Certification Guide</span></h2>
        <div class="chapter-intro"><p>Everything you need to know about the <strong>Cilium Certified Associate (CCA)</strong> exam — format, domains, scoring, preparation strategy, and exam-day tips.</p></div>
        <div class="section-block">
            <h3>Exam Format</h3>
            <table style="width:100%;border-collapse:collapse;margin:12px 0;">
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Duration</td><td style="padding:8px 12px;border:1px solid #30363d;">90 minutes</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Questions</td><td style="padding:8px 12px;border:1px solid #30363d;">~60 multiple-choice &amp; multiple-select</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Passing Score</td><td style="padding:8px 12px;border:1px solid #30363d;">~65-70% (varies by exam version)</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Delivery</td><td style="padding:8px 12px;border:1px solid #30363d;">Online proctored OR testing center</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Prerequisites</td><td style="padding:8px 12px;border:1px solid #30363d;">CKA recommended but NOT required</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Cost</td><td style="padding:8px 12px;border:1px solid #30363d;">~$250 USD (check cilium.io for current pricing)</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">Validity</td><td style="padding:8px 12px;border:1px solid #30363d;">2 years</td></tr>
            </table>
            <h3>Exam Domains (Weight Distribution)</h3>
            <table style="width:100%;border-collapse:collapse;margin:12px 0;">
                <tr style="background:#1c2128;"><th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">#</th><th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">Domain</th><th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">Weight</th></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;">1</td><td style="padding:8px 12px;border:1px solid #30363d;">Architecture</td><td style="padding:8px 12px;border:1px solid #30363d;">20%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;">2</td><td style="padding:8px 12px;border:1px solid #30363d;">Network Policy</td><td style="padding:8px 12px;border:1px solid #30363d;">18%</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;">3</td><td style="padding:8px 12px;border:1px solid #30363d;">Service Mesh</td><td style="padding:8px 12px;border:1px solid #30363d;">16%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;">4</td><td style="padding:8px 12px;border:1px solid #30363d;">Observability</td><td style="padding:8px 12px;border:1px solid #30363d;">10%</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;">5</td><td style="padding:8px 12px;border:1px solid #30363d;">Installation &amp; Configuration</td><td style="padding:8px 12px;border:1px solid #30363d;">10%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;">6</td><td style="padding:8px 12px;border:1px solid #30363d;">Cluster Mesh</td><td style="padding:8px 12px;border:1px solid #30363d;">10%</td></tr>
                <tr><td style="padding:8px 12px;border:1px solid #30363d;">7</td><td style="padding:8px 12px;border:1px solid #30363d;">eBPF</td><td style="padding:8px 12px;border:1px solid #30363d;">10%</td></tr>
                <tr style="background:#1c2128;"><td style="padding:8px 12px;border:1px solid #30363d;">8</td><td style="padding:8px 12px;border:1px solid #30363d;">BGP &amp; External Networking</td><td style="padding:8px 12px;border:1px solid #30363d;">6%</td></tr>
            </table>
            <h3>How to Use This Study Guide</h3>
            <div style="margin:12px 0;padding:12px;background:#1c2128;border-radius:8px;border-left:3px solid var(--accent);">
                <p><strong>📚 Recommended Study Path (4-6 weeks):</strong></p>
                <ol style="margin:8px 0 8px 20px;line-height:1.8;">
                    <li><strong>Week 1-2:</strong> Work through Part 1 MCQs (200 questions) domain by domain. Read ALL explanations — even for questions you got right.</li>
                    <li><strong>Week 3:</strong> Complete Part 2 Troubleshooting Issues (100 issues). Focus on the "Most Likely Causes" — these are the exam's scenario-based questions.</li>
                    <li><strong>Week 4:</strong> Hands-on practice with Part 3 Lab Scenarios (S1-S100). Deploy anihpj, inject bugs, fix them. Nothing beats real Cilium debugging experience.</li>
                    <li><strong>Week 5:</strong> Review Appendices. Memorize the Top 50 Commands (Appendix B). Review decision trees (Appendix E) for rapid troubleshooting.</li>
                    <li><strong>Week 6:</strong> Take full practice exams (200 MCQs timed). Score 80%+ consistently before scheduling your exam.</li>
                </ol>
            </div>
            <h3>Exam-Day Tips</h3>
            <ul style="margin:8px 0 8px 20px;line-height:1.8;">
                <li><strong>⌛ Time Management:</strong> 90 minutes for ~60 questions = ~1.5 min per question. Flag tough ones and return later. Don't get stuck.</li>
                <li><strong>🔑 Key Topics to Master:</strong> CiliumNetworkPolicy syntax (L3/L4/L7), Hubble observe commands, KPR modes, Cluster Mesh prerequisites, eBPF hook points, BGP peering config.</li>
                <li><strong>⚠️ Common Pitfalls:</strong> Confusing CiliumNetworkPolicy with Kubernetes NetworkPolicy syntax. Forgetting that L7 policies disable socket LB. Assuming Cluster Mesh auto-encrypts cross-cluster traffic.</li>
                <li><strong>💻 Hands-On Is Essential:</strong> The CCA tests practical knowledge. You should be able to: deploy Cilium, write a CNP, debug with Hubble, run connectivity test, and interpret cilium status output — all from memory.</li>
                <li><strong>📋 Pre-Exam Checklist:</strong> Stable internet (if online), quiet room, government ID ready, system compatibility test completed 24h before.</li>
            </ul>
        </div>
    </section>
"""

# Find the PART 1 banner comment block
marker = "PART 1: 200 MCQs — CONTENT GOES HERE"
idx = content.find(marker)
if idx > 0:
    # Find the start of this comment line (the <!--)
    comment_start = content.rfind("    <!--", 0, idx)
    if comment_start > 0:
        content = content[:comment_start] + exam_overview + "\n\n" + content[comment_start:]
        print("✅ exam-overview inserted before Part 1")
    else:
        print("Could not find comment block start")
else:
    print("❌ Part 1 marker not found!")

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html", "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 Done!")
