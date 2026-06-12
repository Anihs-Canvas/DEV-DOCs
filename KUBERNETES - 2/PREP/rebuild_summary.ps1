$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\PREP\argocd_test_Prep.html"
$c = [System.IO.File]::ReadAllText($f)

$startMarker = 'MASTER SUMMARY & IMPLEMENTATION ROADMAP'
$endMarker = 'EXAM OVERVIEW'

$start = $c.IndexOf($startMarker)
$end = $c.IndexOf($endMarker, $start)

# Find the actual section boundaries
$sectionStart = $c.LastIndexOf('<section', $start) - 5  # include the comment before
$sectionEnd = $c.IndexOf('<!-- ═══════════════ EXAM OVERVIEW', $start)

"Section: $sectionStart to $sectionEnd ($($sectionEnd - $sectionStart) chars)"

$newSummary = @'
    <!-- ═══════════════ MASTER SUMMARY — 200 CAPA MCQs ═══════════════ -->
    <section class="chapter-section" id="master-summary">
        <h2><span>🏠 Master Summary — 200 CAPA MCQs</span><span class="chapter-badge">START HERE</span></h2>

        <div class="chapter-intro" style="border-left:4px solid #58a6ff;">
            <h3>🎯 What This Document Is</h3>
            <p>Your <strong>complete CAPA (Certified Argo Project Associate) exam preparation system</strong>. 200 MCQs spanning all 4 CNCF Argo domains, each with detailed explanations, ASCII diagrams, and real-world context from the <strong>anihpj/jobpost</strong> Django application running on a 6-cluster Kubernetes lab. Every question builds <strong>progressive mastery</strong>: foundational concepts (Q1-Q100) → advanced production patterns (Q101-Q200).</p>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #d2991d;">
            <h3>📊 CAPA Domain Distribution</h3>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0;">
                <div style="background:linear-gradient(180deg,rgba(88,166,255,0.08),rgba(88,166,255,0.02));border:1px solid rgba(88,166,255,0.2);border-radius:12px;padding:18px;text-align:center;">
                    <div style="font-size:32px;">⚙️</div>
                    <div style="font-size:28px;font-weight:800;color:#58a6ff;">72 Qs</div>
                    <div style="font-size:12px;color:#8b949e;">Argo Workflows</div>
                    <div style="font-size:10px;color:#58a6ff;">Q1-Q36 · Q101-Q136</div>
                    <div style="width:100%;height:6px;background:rgba(88,166,255,0.1);border-radius:3px;margin-top:8px;"><div style="width:36%;height:100%;background:#58a6ff;border-radius:3px;"></div></div>
                    <div style="font-size:11px;color:#58a6ff;margin-top:4px;">36% 🔴 HIGHEST</div>
                </div>
                <div style="background:linear-gradient(180deg,rgba(63,185,80,0.08),rgba(63,185,80,0.02));border:1px solid rgba(63,185,80,0.2);border-radius:12px;padding:18px;text-align:center;">
                    <div style="font-size:32px;">🚢</div>
                    <div style="font-size:28px;font-weight:800;color:#3fb950;">68 Qs</div>
                    <div style="font-size:12px;color:#8b949e;">Argo CD</div>
                    <div style="font-size:10px;color:#3fb950;">Q37-Q70 · Q137-Q170</div>
                    <div style="width:100%;height:6px;background:rgba(63,185,80,0.1);border-radius:3px;margin-top:8px;"><div style="width:34%;height:100%;background:#3fb950;border-radius:3px;"></div></div>
                    <div style="font-size:11px;color:#3fb950;margin-top:4px;">34% 🔴 HIGH</div>
                </div>
                <div style="background:linear-gradient(180deg,rgba(210,153,29,0.08),rgba(210,153,29,0.02));border:1px solid rgba(210,153,29,0.2);border-radius:12px;padding:18px;text-align:center;">
                    <div style="font-size:32px;">📈</div>
                    <div style="font-size:28px;font-weight:800;color:#d2991d;">36 Qs</div>
                    <div style="font-size:12px;color:#8b949e;">Argo Rollouts</div>
                    <div style="font-size:10px;color:#d2991d;">Q71-Q88 · Q171-Q188</div>
                    <div style="width:100%;height:6px;background:rgba(210,153,29,0.1);border-radius:3px;margin-top:8px;"><div style="width:18%;height:100%;background:#d2991d;border-radius:3px;"></div></div>
                    <div style="font-size:11px;color:#d2991d;margin-top:4px;">18% 🟡 MEDIUM</div>
                </div>
                <div style="background:linear-gradient(180deg,rgba(163,113,247,0.08),rgba(163,113,247,0.02));border:1px solid rgba(163,113,247,0.2);border-radius:12px;padding:18px;text-align:center;">
                    <div style="font-size:32px;">⚡</div>
                    <div style="font-size:28px;font-weight:800;color:#a371f7;">24 Qs</div>
                    <div style="font-size:12px;color:#8b949e;">Argo Events</div>
                    <div style="font-size:10px;color:#a371f7;">Q89-Q100 · Q189-Q200</div>
                    <div style="width:100%;height:6px;background:rgba(163,113,247,0.1);border-radius:3px;margin-top:8px;"><div style="width:12%;height:100%;background:#a371f7;border-radius:3px;"></div></div>
                    <div style="font-size:11px;color:#a371f7;margin-top:4px;">12% 🟢 LOWER</div>
                </div>
            </div>
            <pre style="font-size:13px;line-height:1.8;color:#c9d1d9;background:transparent;margin:12px 0 0;">
  ⚙️ Workflows + 🚢 Argo CD = <strong style="color:#58a6ff;">70% of your CAPA score</strong>
  → Prioritize these two. Master them and you need ~50% on Rollouts + Events to pass.</pre>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #a371f7;">
            <h3>🗺️ Progressive Learning Path</h3>
            <div class="tenet-flow" style="margin:16px 0;">
                <div class="tenet-step" style="flex:1;min-width:110px;background:rgba(88,166,255,0.08);border-color:rgba(88,166,255,0.2);">
                    <div class="step-num" style="color:#58a6ff;font-size:20px;">📝</div>
                    <div class="step-label" style="font-size:11px;"><strong>Foundation</strong><br>Q1-Q100<br><small>All 4 domains<br>Core concepts</small></div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:110px;background:rgba(210,153,29,0.08);border-color:rgba(210,153,29,0.2);">
                    <div class="step-num" style="color:#d2991d;font-size:20px;">📖</div>
                    <div class="step-label" style="font-size:11px;"><strong>Read Explanations</strong><br>Every answer<br><small>Diagrams · CLI ·<br>Architecture</small></div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:110px;background:rgba(163,113,247,0.08);border-color:rgba(163,113,247,0.2);">
                    <div class="step-num" style="color:#a371f7;font-size:20px;">🚀</div>
                    <div class="step-label" style="font-size:11px;"><strong>Advanced</strong><br>Q101-Q200<br><small>Production patterns<br>Multi-cluster</small></div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:110px;background:rgba(63,185,80,0.08);border-color:rgba(63,185,80,0.2);">
                    <div class="step-num" style="color:#3fb950;font-size:20px;">✅</div>
                    <div class="step-label" style="font-size:11px;"><strong>Mastery</strong><br>Re-test weak spots<br><small>Target 85%+<br>across all domains</small></div>
                </div>
            </div>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #3fb950;">
            <h3>📅 3-Week Implementation Plan</h3>
            <div class="tenet-flow" style="margin:16px 0;">
                <div class="tenet-step" style="flex:1;min-width:130px;background:rgba(88,166,255,0.08);border-color:rgba(88,166,255,0.2);">
                    <div class="step-num" style="color:#58a6ff;">📅 Week 1</div>
                    <div class="step-label" style="font-size:11px;"><strong>Foundation</strong><br>Pre-Learning F.1-F.5<br>Q1-Q70: Workflows + CD<br><small>Goal: 80%+</small></div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:130px;background:rgba(210,153,29,0.08);border-color:rgba(210,153,29,0.2);">
                    <div class="step-num" style="color:#d2991d;">📅 Week 2</div>
                    <div class="step-label" style="font-size:11px;"><strong>Deep Dive</strong><br>Q71-Q100: Rollouts+Events<br>Q101-Q170: Advanced WF+CD<br><small>Goal: Master GitOps</small></div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:130px;background:rgba(163,113,247,0.08);border-color:rgba(163,113,247,0.2);">
                    <div class="step-num" style="color:#a371f7;">📅 Week 3</div>
                    <div class="step-label" style="font-size:11px;"><strong>Mastery</strong><br>Q171-Q200: Prod Patterns<br>Full timed mock (200 Qs)<br><small>Goal: Exam-ready</small></div>
                </div>
            </div>
            <div class="dt-checklist" style="margin:12px 0 0;background:rgba(63,185,80,0.04);border:1px solid rgba(63,185,80,0.15);">
                <div class="dt-checklist-title" style="color:#3fb950;background:rgba(63,185,80,0.06);">✅ Daily Checklist</div>
                <ul class="dt-checklist-items">
                    <li class="dt-check-item"><strong>Morning (30 min):</strong> Answer 10-15 MCQs. Read ALL explanations — even for correct answers.</li>
                    <li class="dt-check-item"><strong>Afternoon (30 min):</strong> Re-read diagrams and CLI patterns. Type commands from memory on your lab.</li>
                    <li class="dt-check-item"><strong>Evening (45 min):</strong> Practice on your 6-cluster lab with <code>ksw</code>. Deploy workflows, create Applications.</li>
                    <li class="dt-check-item"><strong>Weekend (2 hrs):</strong> Full review. 50+ MCQs back-to-back. Focus on weak areas.</li>
                </ul>
            </div>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #f85149;margin-top:24px;">
            <h3>🏆 Before vs After — Skills You'll Master</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0;">
                <div style="background:rgba(248,81,73,0.05);border:1px solid rgba(248,81,73,0.2);border-radius:10px;padding:16px;">
                    <h4 style="color:#f85149;margin:0 0 10px;font-size:14px;">❌ BEFORE — Common Gaps</h4>
                    <ul style="list-style:none;padding:0;margin:0;font-size:13px;line-height:1.8;color:#b0b8c4;">
                        <li>❌ "What's a Workflow Template vs a Step?"</li>
                        <li>❌ "Why does Argo CD show OutOfSync?"</li>
                        <li>❌ "How do I pass artifacts between steps?"</li>
                        <li>❌ "Blue/Green vs Canary — which when?"</li>
                        <li>❌ "How do EventSources and Sensors connect?"</li>
                        <li>❌ "Multi-cluster GitOps with one Argo CD?"</li>
                    </ul>
                </div>
                <div style="background:rgba(63,185,80,0.05);border:1px solid rgba(63,185,80,0.2);border-radius:10px;padding:16px;">
                    <h4 style="color:#3fb950;margin:0 0 10px;font-size:14px;">✅ AFTER — What You'll Know</h4>
                    <ul style="list-style:none;padding:0;margin:0;font-size:13px;line-height:1.8;color:#b0b8c4;">
                        <li>✅ Design DAG workflows with artifact passing</li>
                        <li>✅ Configure GitOps: auto-sync, self-heal, prune</li>
                        <li>✅ Canary + Prometheus analysis + auto-rollback</li>
                        <li>✅ Event-driven pipelines: S3→Sensor→Workflow</li>
                        <li>✅ ApplicationSets across 6 clusters</li>
                        <li>✅ RBAC, Dex SSO, security best practices</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #58a6ff;margin-top:24px;">
            <h3>⚔️ Exam Day Strategy — 2 Hours, 200 MCQs</h3>
            <div class="tenet-flow" style="margin:16px 0;">
                <div class="tenet-step" style="flex:1;min-width:90px;background:rgba(88,166,255,0.08);border-color:rgba(88,166,255,0.2);">
                    <div class="step-num" style="color:#58a6ff;">⏱️ 0-5m</div>
                    <div class="step-label" style="font-size:11px;"><strong>Scan</strong><br>Skim all Qs<br>Flag hard ones</div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:90px;background:rgba(210,153,29,0.08);border-color:rgba(210,153,29,0.2);">
                    <div class="step-num" style="color:#d2991d;">⏱️ 5-100m</div>
                    <div class="step-label" style="font-size:11px;"><strong>Execute</strong><br>Easy first<br>~30s per Q</div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:90px;background:rgba(163,113,247,0.08);border-color:rgba(163,113,247,0.2);">
                    <div class="step-num" style="color:#a371f7;">⏱️ 100-115m</div>
                    <div class="step-label" style="font-size:11px;"><strong>Tackle Hard</strong><br>Flagged Qs<br>Eliminate wrong</div>
                </div>
                <div class="tenet-step" style="flex:1;min-width:90px;background:rgba(63,185,80,0.08);border-color:rgba(63,185,80,0.2);">
                    <div class="step-num" style="color:#3fb950;">⏱️ 115-120m</div>
                    <div class="step-label" style="font-size:11px;"><strong>Verify</strong><br>All answered<br>No blanks</div>
                </div>
            </div>
            <div class="dt-checklist" style="margin:12px 0 0;background:rgba(88,166,255,0.04);border:1px solid rgba(88,166,255,0.15);">
                <div class="dt-checklist-title" style="color:#58a6ff;background:rgba(88,166,255,0.06);">🚨 Critical Do's & Don'ts</div>
                <ul class="dt-checklist-items">
                    <li class="dt-check-item"><strong>✅ DO:</strong> Read EVERY option. CAPA questions have "mostly correct" distractors.</li>
                    <li class="dt-check-item"><strong>✅ DO:</strong> Prioritize Workflows (36%) + Argo CD (34%) = 70% of your score.</li>
                    <li class="dt-check-item"><strong>✅ DO:</strong> Eliminate wrong answers. Contradictions to GitOps/declarative philosophy are red flags.</li>
                    <li class="dt-check-item"><strong>❌ DON'T:</strong> Spend >1 min per question. Flag and return.</li>
                    <li class="dt-check-item"><strong>❌ DON'T:</strong> Leave any question blank. No penalty for wrong answers — always guess.</li>
                </ul>
            </div>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #d2991d;margin-top:24px;">
            <h3>📦 Content Inventory — 200 MCQs Across 28 Sub-Sections</h3>
            <pre style="font-size:11px;line-height:1.7;color:#c9d1d9;background:transparent;margin:8px 0 0;white-space:pre-wrap;">
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  ⚙️  ARGO WORKFLOWS (36% — 72 Qs · 8 Sections)                              │
  │  1.1 Basics (Q1-Q10)   1.3 Artifacts (Q19-Q24)  1.5 Spec (Q31-Q36)          │
  │  1.2 Templates (Q11-Q18) 1.4 DAG (Q25-Q30)      1.6 Advanced (Q101-Q112)    │
  │  1.7 Real-World (Q113-Q124)    1.8 Data/ETL (Q125-Q136)                      │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  🚢 ARGO CD (34% — 68 Qs · 10 Sections)                                     │
  │  2.1 Fundamentals (Q37-Q44)  2.4 Helm/Kustomize (Q61-Q65)  2.7 RBAC (Q145-Q152)│
  │  2.2 Sync (Q45-Q52)          2.5 Reconciliation (Q66-Q70)  2.8 Adv Sync (Q153-Q160)│
  │  2.3 App CRD (Q53-Q60)       2.6 Multi-Cluster (Q137-Q144) 2.9 Adv Apps (Q161-Q166)│
  │                                                             2.10 Production (Q167-Q170)│
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  📈 ARGO ROLLOUTS (18% — 36 Qs · 6 Sections)                                │
  │  3.1 Fundamentals (Q71-Q76)  3.3 Analysis (Q83-Q88)    3.5 Real-World (Q177-Q182)│
  │  3.2 Strategies (Q77-Q82)    3.4 Adv Canary (Q171-Q176) 3.6 Prod Analysis (Q183-Q188)│
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  ⚡ ARGO EVENTS (12% — 24 Qs · 4 Sections)                                  │
  │  4.1 Fundamentals (Q89-Q94)  4.2 Components (Q95-Q100)                       │
  │  4.3 Adv Patterns (Q189-Q194) 4.4 Production (Q195-Q200)                     │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  🖥️  Built around anihpj/jobpost on a 6-cluster Kubernetes lab              │
  │  📊 200+ ASCII diagrams · 800 options · Progressive difficulty              │
  └──────────────────────────────────────────────────────────────────────────────┘</pre>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #a371f7;margin-top:24px;">
            <h3>🏗️ anihpj/jobpost — Production Architecture (How To Implement)</h3>
            <p style="font-size:13px;color:#8b949e;">Every question references this real Django application. The 6-cluster lab mirrors actual CAPA exam conditions:</p>
            <pre style="font-size:11px;line-height:1.6;color:#c9d1d9;background:transparent;margin:12px 0 0;">
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │                     ANIHPJ/JOBPOST — ARGO STACK ARCHITECTURE                 │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │                                                                              │
  │  ┌── CI/CD ──────────────────────────────────────────────────────────────┐  │
  │  │  GitHub Push ──▶ Argo Events (Webhook) ──▶ Argo Workflows ──▶ ECR     │  │
  │  │  (main branch)    EventSource→Sensor       lint→test→build→push       │  │
  │  └───────────────────────────────────────────────────────────────────────┘  │
  │                                    │                                         │
  │                                    ▼                                         │
  │  ┌── GITOPS DELIVERY ────────────────────────────────────────────────────┐  │
  │  │  Argo CD (mgmt cluster) syncs ApplicationSets to all 6 clusters:       │  │
  │  │  kind-cl1(dev) · kubeadm(staging) · kind-cl2(prod-us) · kind-cl3(eu)  │  │
  │  │  minikube(prod-asia) · mgmt(self-managed)                              │  │
  │  └───────────────────────────────────────────────────────────────────────┘  │
  │                                    │                                         │
  │                                    ▼                                         │
  │  ┌── PROGRESSIVE DELIVERY ───────────────────────────────────────────────┐  │
  │  │  Argo Rollouts: Canary 10%→25%→50%→100% + Prometheus analysis         │  │
  │  │  Auto-rollback if error rate > 2% or p99 latency > 500ms              │  │
  │  └───────────────────────────────────────────────────────────────────────┘  │
  │                                                                              │
  │  STACK: Django+Gunicorn · PostgreSQL 15 · Redis · Celery                     │
  │  IMAGE: Multi-stage distroless (Python 3.12) · REGISTRY: AWS ECR             │
  │  SECRETS: AWS Secrets Manager + External Secrets Operator (ESO)              │
  └──────────────────────────────────────────────────────────────────────────────┘</pre>
        </div>

        <div class="chapter-intro" style="border-left:4px solid #3fb950;margin-top:24px;">
            <h3>🧭 Quick Navigation — Jump To Any Domain</h3>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0;">
                <a href="#cat1" style="text-decoration:none;"><div style="background:linear-gradient(145deg,rgba(88,166,255,0.08),rgba(88,166,255,0.02));border:1px solid rgba(88,166,255,0.2);border-radius:12px;padding:14px;text-align:center;"><div style="font-size:24px;">⚙️</div><div style="font-size:13px;font-weight:700;color:#58a6ff;">Argo Workflows</div><div style="font-size:10px;color:#8b949e;">72 Qs · 8 Sections</div></div></a>
                <a href="#cat2" style="text-decoration:none;"><div style="background:linear-gradient(145deg,rgba(63,185,80,0.08),rgba(63,185,80,0.02));border:1px solid rgba(63,185,80,0.2);border-radius:12px;padding:14px;text-align:center;"><div style="font-size:24px;">🚢</div><div style="font-size:13px;font-weight:700;color:#3fb950;">Argo CD</div><div style="font-size:10px;color:#8b949e;">68 Qs · 10 Sections</div></div></a>
                <a href="#cat3" style="text-decoration:none;"><div style="background:linear-gradient(145deg,rgba(210,153,29,0.08),rgba(210,153,29,0.02));border:1px solid rgba(210,153,29,0.2);border-radius:12px;padding:14px;text-align:center;"><div style="font-size:24px;">📈</div><div style="font-size:13px;font-weight:700;color:#d2991d;">Argo Rollouts</div><div style="font-size:10px;color:#8b949e;">36 Qs · 6 Sections</div></div></a>
                <a href="#cat4" style="text-decoration:none;"><div style="background:linear-gradient(145deg,rgba(163,113,247,0.08),rgba(163,113,247,0.02));border:1px solid rgba(163,113,247,0.2);border-radius:12px;padding:14px;text-align:center;"><div style="font-size:24px;">⚡</div><div style="font-size:13px;font-weight:700;color:#a371f7;">Argo Events</div><div style="font-size:10px;color:#8b949e;">24 Qs · 4 Sections</div></div></a>
            </div>
        </div>
    </section>

    <!-- ═══════════════ EXAM OVERVIEW ═══════════════ -->
'@

$new = $c.Substring(0, $sectionStart) + $newSummary + $c.Substring($sectionEnd + 64)
[System.IO.File]::WriteAllText($f, $new)
"Done. Old: $($c.Length) New: $($new.Length)"
