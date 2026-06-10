"""Find and fix mismatched Q&A templates + add 95%+ content."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    c = f.read()

fixed = 0

# 1. Replace over-used "Rightsizing Check — kubectl" in non-K8s chapters (1-6, 11, 13-14, 17-20)
rw = 'Rightsizing Check — kubectl top + describe'
# Find all occurrences
positions = []
idx = 0
while True:
    idx = c.find(rw, idx)
    if idx == -1: break
    positions.append(idx)
    idx += 1

print(f'Found {len(positions)} "Rightsizing Check" blocks')

# For each, determine which chapter it's in and replace with chapter-relevant content
chapter_replacements = {
    1: '<div class="diagram-container"><div class="diagram-title">FinOps Principles — COBALT</div><pre>\n  C — Collaboration: Finance + Engineering + Business = One Team\n  O — Ownership: Everyone owns their technology spend\n  B — Business Value: Decisions driven by business ROI\n  A — Accessibility: Timely, accessible cost data for all\n  L — Lean Operations: Eliminate waste continuously\n  T — Transparency: Costs visible to everyone\n</pre></div>',
    2: '<div class="diagram-container"><div class="diagram-title">FinOps Lifecycle — Inform → Optimize → Operate</div><pre>\n  INFORM: Visibility, dashboards, allocation → "See the bill"\n  OPTIMIZE: Rightsize, reserve, spot → "Reduce the bill"\n  OPERATE: Governance, automation, culture → "Prevent waste"\n</pre></div>',
    3: '<div class="compare-table"><table><thead><tr><th>Model</th><th>Discount</th><th>Commitment</th><th>Best For</th></tr></thead><tbody><tr><td>On-Demand</td><td>0%</td><td>None</td><td>Variable/new</td></tr><tr><td>RI Standard</td><td>40-60%</td><td>1-3yr</td><td>Stable prod</td></tr><tr><td>RI Convertible</td><td>30-45%</td><td>1-3yr</td><td>Planned migration</td></tr><tr><td>Savings Plan</td><td>28-72%</td><td>1-3yr $/hr</td><td>Any compute</td></tr><tr><td>Spot</td><td>60-90%</td><td>None</td><td>Fault-tolerant</td></tr></tbody></table></div>',
    4: '<div class="diagram-container"><div class="diagram-title">RI/SP Strategy — Rightsize First, Then Commit</div><pre>\n  STEP 1: Rightsize (VPA + Compute Optimizer) — never commit to overprovisioned waste\n  STEP 2: Stagger purchases (33% every 4 months) — avoid stranded commitments\n  STEP 3: Prefer SP over RI for compute — follows any family, any region\n  STEP 4: Track expiration dates — prevent surprise On-Demand bill spikes\n</pre></div>',
    5: '<div class="diagram-container"><div class="diagram-title">Tagging + Allocation Strategy</div><pre>\n  10 ESSENTIAL TAGS: Environment, Application, Component, Team, CostCenter, Owner,\n  DataClassification, Compliance, ProvisionedBy, AutoShutdown\n  ALLOCATION: Proportional (usage-based) > Fixed (even split) > Direct (dedicated)\n  SHOWBACK: Inform without billing (Crawl) | CHARGEBACK: Bill teams (Run)\n</pre></div>',
    6: '<div class="diagram-container"><div class="diagram-title">6 Key FinOps KPIs</div><pre>\n  Total Spend: Sum of all costs | Unit Cost: Spend / Transactions\n  ESR: (OnDemand-Actual)/OnDemand% | Coverage: RI+SP/Total%\n  Waste%: Waste/Total% | Unallocated%: Untagged/Total%\n  TARGETS: Walk: ESR 20-30%, Cov 60%, Waste<10%, Unalloc<10%\n</pre></div>',
    11: '<div class="diagram-container"><div class="diagram-title">Budgeting + Unit Economics</div><pre>\n  TOP-DOWN: Leadership sets cap -> allocate down | BOTTOM-UP: Teams estimate -> aggregate up\n  HYBRID BEST: Bottom-up detail + top-down validation\n  UNIT COST: $14,200 / 4.73M = $0.003/posting | ROI = (Savings - Investment) / Investment x 100\n</pre></div>',
    13: '<div class="compare-table"><table><thead><tr><th>Category</th><th>Tools</th><th>Cost</th></tr></thead><tbody><tr><td>Cloud-Native</td><td>Cost Explorer, Azure CM</td><td>Free</td></tr><tr><td>Third-Party</td><td>CloudHealth, Vantage</td><td>1-3%/$50</td></tr><tr><td>K8s-Specific</td><td>Kubecost, Cast AI</td><td>Free/$$$</td></tr><tr><td>IaC Estimation</td><td>Infracost</td><td>Free</td></tr></tbody></table></div>',
    14: '<div class="diagram-container"><div class="diagram-title">Exam Strategy Quick Card</div><pre>\n  90 min | 76 Qs | ~70 sec/Q | 3-pass: 60min confident, 20min marked, 10min review\n  NEVER leave blank (no penalty) | Write 5 formulas first | Eliminate 2 wrong = 50% guess\n</pre></div>',
    17: '<div class="diagram-container"><div class="diagram-title">Multi-Cloud Decision Framework</div><pre>\n  GO MULTI-CLOUD: Acquisition, compliance (data residency), best-of-breed, negotiation leverage\n  STAY SINGLE-CLOUD: <200 engineers, no compliance need, simplicity > theoretical savings\n  anihpj (15 eng): Stay single-cloud AWS. Multi-cloud overhead exceeds savings.\n</pre></div>',
    18: '<div class="diagram-container"><div class="diagram-title">Build vs Buy — Total Cost Comparison</div><pre>\n  BUY (Managed): Infrastructure cost + $0 ops = LOWER total\n  BUILD (Self-Managed): Infrastructure cost + Engineer hrs x $150/hr\n  RULE: If self-managed requires >30 min/month, managed wins on total cost.\n</pre></div>',
    19: '<div class="diagram-container"><div class="diagram-title">FinOps Culture Building Blocks</div><pre>\n  VISIBILITY: Dashboards + Slack bots -> everyone sees costs\n  CELEBRATION: Cost wins celebrated like feature launches\n  TRAINING: 30min onboarding + monthly 15min wins + quarterly 45min deep-dives\n  INCENTIVES: Reward unit cost improvement, not absolute cost reduction\n</pre></div>',
    20: '<div class="diagram-container"><div class="diagram-title">AI/ML + Serverless Cost Optimization</div><pre>\n  TRAINING: Spot GPUs (60-70% savings) | INFERENCE: Inferentia/Trainium (40% savings)\n  LAMBDA WINS: Low traffic, spiky, event-driven | EC2 WINS: Steady 24/7, RI-eligible\n  BREAK-EVEN: ~500K req/hr. Below = Lambda cheaper. Above = EC2 RI cheaper.\n</pre></div>',
}

# Fix each mismatched template
for ch_num, replacement in chapter_replacements.items():
    # Find occurrences within this chapter
    ch_start = c.find(f'<div id="ch{ch_num}">')
    if ch_start == -1: continue
    ch_end_tag = f'<div id="ch{ch_num+1}">' if ch_num < 20 else None
    ch_end = c.find(ch_end_tag, ch_start) if ch_end_tag else len(c)
    
    # Find all "Rightsizing Check" blocks in this chapter
    search_pos = ch_start
    while True:
        pos = c.find('Rightsizing Check — kubectl', search_pos)
        if pos == -1 or pos >= ch_end: break
        
        # Find the full code-block-wrapper to replace
        block_start = c.rfind('<div class="code-block-wrapper">', 0, pos)
        block_end = c.find('</code></pre></div>', pos) + len('</code></pre></div>')
        
        if block_start >= ch_start and block_end <= ch_end:
            c = c[:block_start] + replacement + c[block_end:]
            fixed += 1
        
        search_pos = pos + 100

# 2. Also replace Kubecost blocks in non-K8s chapters
for ch_num in [1,2,3,4,5,6,11,13,14,17,18,19,20]:
    ch_start = c.find(f'<div id="ch{ch_num}">')
    if ch_start == -1: continue
    ch_end_tag = f'<div id="ch{ch_num+1}">' if ch_num < 20 else None
    ch_end = c.find(ch_end_tag, ch_start) if ch_end_tag else len(c)
    
    search_pos = ch_start
    while True:
        pos = c.find('Kubecost Quick Start', search_pos)
        if pos == -1 or pos >= ch_end: break
        
        block_start = c.rfind('<div class="code-block-wrapper">', 0, pos)
        block_end = c.find('</code></pre></div>', pos) + len('</code></pre></div>')
        
        if block_start >= ch_start and block_end <= ch_end:
            replacement = chapter_replacements.get(ch_num, '<div class="diagram-container"><div class="diagram-title">Key Concept</div><pre>\n  See chapter content above for detailed explanations and examples.\n</pre></div>')
            c = c[:block_start] + replacement + c[block_end:]
            fixed += 1
        
        search_pos = pos + 100

print(f'Fixed {fixed} mismatched templates')

with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('Saved.')
