"""Add FCE exam preparation callouts to each chapter before the Q&A section."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Exam prep content per chapter
exam_prep = {
1: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 1</h5>
<p><strong>Most Tested:</strong> CAPEX vs OPEX paradigm shift, 6 FinOps Principles (COBALT), Crawl-Walk-Run maturity stages, stakeholder roles.</p>
<p><strong>Common Trap:</strong> The exam will ask "which maturity stage is this company in?" based on a scenario. Look for keywords: "monthly spreadsheet" = Crawl, "daily dashboards + anomaly alerts" = Walk, "CI/CD cost gates + auto-remediation" = Run.</p>
<p><strong>Memory Aid:</strong> COBALT — Collaboration, Ownership, Business value, Accessibility, Lean operations, Transparency.</p>
</div>''',

2: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 2</h5>
<p><strong>Most Tested:</strong> Pricing models (On-Demand vs RI vs SP vs Spot), CUR/billing data, amortized vs unblended costs, consolidated billing.</p>
<p><strong>Common Trap:</strong> The exam will present a scenario where you need to choose between amortized and unblended costs. Amortized = chargeback/showback/unit economics (smooth, predictable). Unblended = anomaly detection/budget alerts (you want to see the cash spike).</p>
<p><strong>Must-Memorize:</strong> ESR formula (OnDemand - Actual) / OnDemand x 100. RI/SP coverage formula. When to use each pricing model for a given workload type.</p>
</div>''',

3: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 3</h5>
<p><strong>Most Tested:</strong> On-Demand vs RI vs SP vs Spot selection for given workloads, commitment strategies, pricing model trade-offs.</p>
<p><strong>Common Trap:</strong> "Buy RIs for everything" is ALWAYS wrong. The exam expects you to match pricing to workload: SP for steady compute, Spot for fault-tolerant, On-Demand for variable/new. Never recommend RI/SP for overprovisioned resources — rightsize first.</p>
<p><strong>Quick Decision Tree:</strong> Is the workload 24/7 steady? -> SP. Variable/tolerant? -> Spot. New/unpredictable? -> On-Demand. Database? -> RI (only option).</p>
</div>''',

4: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 4</h5>
<p><strong>Most Tested:</strong> RI vs SP comparison, stranded RI risk, staggered purchase strategy, RI marketplace, convertible RI exchange.</p>
<p><strong>Common Trap:</strong> Instance-specific RIs become STRANDED when you modernize instance families (m5->m6i). The exam will test this: "You're migrating from m5 to m6i. You hold m5 RIs. What happens?" Answer: They're stranded — you pay for both old RIs AND new instances. Prevention: use Savings Plans (follow any family) or convertible RIs.</p>
<p><strong>Must-Memorize:</strong> Standard RI = 40-60% discount, locked. Convertible = 30-45%, can exchange. SP Compute = 28-72%, any family. Priority: Rightsize FIRST, then commit.</p>
</div>''',

5: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 5</h5>
<p><strong>Most Tested:</strong> Tagging taxonomy, shared cost allocation methods, showback vs chargeback, K8s-specific allocation challenges.</p>
<p><strong>Common Trap:</strong> The exam will ask "how should this shared cost be allocated?" The answer is almost never "even split." Proportional allocation (based on measurable usage) is preferred. Also: never jump straight to chargeback — trust must be built through showback first.</p>
<p><strong>Must-Memorize:</strong> 10 essential tags, 3 allocation methods (proportional > fixed > direct), showback->chargeback progression, unallocated targets (<10% Walk, <5% Run).</p>
</div>''',

6: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 6</h5>
<p><strong>Most Tested:</strong> KPI target ranges, persona-based dashboards, anomaly detection workflow, forecasting methods.</p>
<p><strong>Common Trap:</strong> You'll be given a KPI value and asked to evaluate it. Know the targets: ESR 30-40% Run, Coverage 60-80% Run, Waste <3% Run, Unallocated <5% Run. A value outside these ranges signals a problem (or wrong maturity stage).</p>
<p><strong>Must-Memorize:</strong> 6 KPIs + target ranges per stage. ESR formula. Coverage formula. Anomaly detection: Detect->Diagnose->Remediate workflow.</p>
</div>''',

7: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 7</h5>
<p><strong>Most Tested:</strong> Optimization ORDER (Rightsize->Reserve->Spot->Autoscale), RI/SP strategies, Spot suitability, K8s autoscaling.</p>
<p><strong>Common Trap:</strong> The exam will ask "what's the FIRST optimization step?" The answer is ALWAYS rightsizing — never buy RIs/SPs for overprovisioned resources. Also: suggesting Spot for production databases is wrong (stateful, latency-sensitive).</p>
<p><strong>Must-Memorize:</strong> Optimization order: RRSMA (Rightsize, Reserve, Spot, Modernize, Autoscale). HPA for traffic spikes, VPA for continuous rightsizing, Karpenter for node consolidation.</p>
</div>''',

8: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 8</h5>
<p><strong>Most Tested:</strong> Storage tiering (S3 lifecycle), database rightsizing, network cost awareness (cross-AZ, NAT Gateway).</p>
<p><strong>Common Trap:</strong> "What's the cheapest storage class?" is a trick — Glacier Deep Archive is cheapest per GB but has 12-48hr retrieval. The exam expects you to match storage class to ACCESS PATTERN, not just pick the cheapest. Also: cross-AZ costs are the #1 hidden expense — $0.01/GB each direction.</p>
<p><strong>Must-Memorize:</strong> S3 Standard ($0.023) -> IA ($0.0125) -> Glacier ($0.004) -> Deep Archive ($0.00099). gp3 is 20% cheaper than gp2. NAT Gateway = $0.045/hr + $0.045/GB.</p>
</div>''',

9: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 9</h5>
<p><strong>Most Tested:</strong> Pod resource requests vs limits, bin packing, VPA/HPA/Karpenter coordination, QoS classes.</p>
<p><strong>Common Trap:</strong> "Set limits = requests" sounds safe but wastes resources (no bursting). "No limits" risks runaway pods. The exam expects balanced configuration: requests = P95+30%, limits = 1.5-2x requests. Also: pod REQUESTS determine node count — a pod requesting 2 CPU but using 0.1 still occupies 2 CPU of node capacity.</p>
<p><strong>Must-Memorize:</strong> QoS classes: Guaranteed (req=limit), Burstable (req<limit), BestEffort (no req/limit — first to be evicted).</p>
</div>''',

10: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 10</h5>
<p><strong>Most Tested:</strong> Spot instance strategies, mixed instance policies, HPA configuration, priority classes, resource quotas.</p>
<p><strong>Common Trap:</strong> HPA target CPU at 50% causes premature scaling (wastes money). Use 70%. Also: maxUnavailable=0 in PDBs blocks Karpenter consolidation and Spot replacement — costing you money. Always allow at least 1 disruption.</p>
<p><strong>Must-Memorize:</strong> HPA min=baseline, max=business ceiling, target=70% CPU. Spot + auto-shutdown = 81% layered savings. Priority classes: high (prod) > medium (staging) > low (dev).</p>
</div>''',

11: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 11</h5>
<p><strong>Most Tested:</strong> Top-down vs bottom-up budgeting, variance analysis, unit economics, ROI calculation.</p>
<p><strong>Common Trap:</strong> The exam will test whether you understand that growing cloud spend is NOT always bad — if unit cost is decreasing while spend increases, that's EFFICIENCY (good scaling). Also: negative ROI doesn't always mean "no" — compliance/strategic projects may proceed despite negative ROI.</p>
<p><strong>Must-Memorize:</strong> ROI = (Savings - Investment) / Investment x 100. Unit Cost = Total Spend / Business Transactions. Budget alerts: 50% Slack, 80% email lead, 90% email director, 100% PagerDuty.</p>
</div>''',

12: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 12</h5>
<p><strong>Most Tested:</strong> 3-layer control framework, Policy-as-Code (SCP, Kyverno, OPA), CI/CD cost gates, auto-remediation.</p>
<p><strong>Common Trap:</strong> The exam asks "which control type should you use?" The answer hierarchy: Preventive > Detective > Corrective. If you CAN block it, block it. If you can't block it, detect it. If you detect it, auto-fix it. Don't suggest detective controls when preventive controls are available.</p>
<p><strong>Must-Memorize:</strong> SCPs apply to OUs/accounts (NOT management account). Kyverno validationFailureAction: Enforce (block) vs Audit (log). Infracost = pre-deployment estimation (shift-left).</p>
</div>''',

13: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 13</h5>
<p><strong>Most Tested:</strong> Tool categories (Cloud-Native, Third-Party, K8s-Specific, IaC), tool selection for given scenarios.</p>
<p><strong>Common Trap:</strong> Recommending an expensive enterprise tool (CloudHealth) for a 10-person startup is wrong. Match tool investment to cloud spend scale: small team = cloud-native + Kubecost (free/$200). Large enterprise = CloudHealth/Cloudability (1-3% of spend).</p>
<p><strong>Must-Memorize:</strong> 4 tool categories + 1 example each. Kubecost (K8s visibility), Infracost (IaC estimation), Karpenter (node autoscaling), Cast AI (autonomous optimization).</p>
</div>''',

14: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 14</h5>
<p><strong>Most Tested:</strong> Exam format, time management, question patterns, 5 key formulas, common traps.</p>
<p><strong>Critical Exam Strategy:</strong> (1) Write the 5 formulas on scratch paper in the first 2 minutes. (2) Use 3-pass strategy: 60min confident, 20min marked, 10min review. (3) NEVER leave a question blank — no penalty for wrong answers. (4) For maturity stage questions, eliminate answers from wrong stages first.</p>
<p><strong>Must-Memorize Cold:</strong> ESR, Coverage, Unit Cost, Amortized Cost, Waste% — formulas AND target ranges for each maturity stage.</p>
</div>''',

15: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 15</h5>
<p><strong>Most Tested:</strong> Hands-on FinOps skills: cost allocation modeling, rightsizing, Spot configuration, policy enforcement.</p>
<p><strong>Lab Exam Strategy:</strong> Complete all 5 labs at least twice. Focus on Lab 5 (full simulation) — it's timed and covers all domains. The hands-on skills directly translate to scenario questions on the exam.</p>
</div>''',

16: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 16</h5>
<p><strong>Domain-Weighted Study Strategy:</strong> Allocate study time proportionally to domain weights. CFM (26%) gets the most time. Optimization (22%) is second. Don't skip any domain — scoring 0% on one almost guarantees failure.</p>
<p><strong>Mock Exam Tips:</strong> Simulate real conditions: 90 minutes, no breaks, no phone. Review wrong answers by domain to identify weak areas. Retake mock exams until consistently scoring >80%.</p>
</div>''',

17: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 17</h5>
<p><strong>Most Tested:</strong> Multi-cloud cost challenges, cloud arbitrage viability, commitment tracking per provider.</p>
<p><strong>Common Trap:</strong> "Should we use cloud arbitrage to save money?" The exam expects you to recognize that arbitrage is mostly impractical for real-time workloads (data gravity, latency, API differences). It's viable only for batch/analytics.</p>
</div>''',

18: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 18</h5>
<p><strong>Most Tested:</strong> SaaS pricing models, managed service TCO, build-vs-buy decisions, SaaS sprawl management.</p>
<p><strong>Common Trap:</strong> Comparing only infrastructure costs in build-vs-buy (ignoring people costs). Always calculate: Self-Managed Total = Cloud Cost + (Engineering Hours x $150/hr). The managed premium almost always wins when people costs are included.</p>
</div>''',

19: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 19</h5>
<p><strong>Most Tested:</strong> Culture change, engineer pushback responses, executive communication, FinOps team structure.</p>
<p><strong>Common Trap:</strong> "How do you respond to 'I'm an engineer, not an accountant!'?" The correct answer reframes cost as an ENGINEERING SIGNAL — like CPU or error rate. NEVER dismiss the engineer's concern. Always acknowledge, then reframe.</p>
</div>''',

20: '''<div class="info-box" style="border-left: 4px solid #f59e0b; background: rgba(245,158,11,0.06);">
<h5>📝 FCE Exam Prep — Chapter 20</h5>
<p><strong>Most Tested:</strong> GPU cost optimization, training vs inference cost dynamics, serverless cost break-even, SaaS license optimization.</p>
<p><strong>Common Trap:</strong> "Is serverless always cheaper?" No — Lambda wins for low/spiky traffic but loses to EC2 RI at high steady volume. The exam expects you to calculate the break-even point based on request volume and execution duration.</p>
</div>''',
}

enriched = 0
for ch_num in range(1, 21):
    prep_html = exam_prep.get(ch_num)
    if not prep_html:
        continue
    
    # Find the chapter's Q&A section
    if ch_num == 15:
        qa_marker = 'Lab-Based Practice Questions'
    elif ch_num == 16:
        qa_marker = 'Domain 1 Questions'
    else:
        qa_marker = f'Chapter {ch_num} — FCE Practice Questions'
    
    qa_pos = content.find(qa_marker)
    if qa_pos == -1:
        print(f'  Ch {ch_num}: Q&A marker not found ({qa_marker[:50]})')
        continue
    
    # Find the fce-exam-questions div opening
    div_pos = content.rfind('<div class="fce-exam-questions"', 0, qa_pos)
    if div_pos == -1:
        print(f'  Ch {ch_num}: fce-exam-questions div not found')
        continue
    
    # Insert exam prep BEFORE the Q&A section
    content = content[:div_pos] + prep_html + '\n' + content[div_pos:]
    enriched += 1
    print(f'  Ch {ch_num}: Exam prep added')

print(f'\nEnriched: {enriched} chapters')
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
