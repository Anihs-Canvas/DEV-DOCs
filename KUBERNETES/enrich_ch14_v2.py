"""Inject diagrams into thin sections by finding section IDs and appending content."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Visual content per thin section ID
visuals = {
    's14-1': '<div class="diagram-container"><div class="diagram-title">FCE Exam at a Glance</div><pre>\n  90 MIN | 76 Qs | MULTIPLE CHOICE | 70-75% TO PASS | NO PENALTY FOR GUESSING\n  Online proctored | Results immediate | ~70 sec/question\n</pre></div>',
    's14-1a': '<div class="diagram-container"><div class="diagram-title">Question Types & Strategy</div><pre>\n  ~50 Single-answer (45-60s) | ~15 Multi-select (90s) | ~11 Scenario (2-3 min)\n  Use 3-pass strategy: Confident -> Marked -> Final review\n</pre></div>',
    's14-3a': '<div class="diagram-container"><div class="diagram-title">ESR = (OnDemand - Actual) / OnDemand x 100</div><pre>\n  anihpj: ($10,000 - $6,500) / $10,000 = 35%\n  Crawl 0-15% | Walk 20-30% | Run 30-40% | Above 50% = stranded RI risk\n</pre></div>',
    's14-3b': '<div class="diagram-container"><div class="diagram-title">Coverage = (RI + SP) / Total Compute x 100</div><pre>\n  anihpj: $4,200 / $6,500 = 64.6% | Crawl 0-20% | Walk 40-60% | Run 60-80%\n  Below 40% = overpaying | Above 90% = stranded risk + no flexibility\n</pre></div>',
    's14-3c': '<div class="compare-table"><table><thead><tr><th>Metric</th><th>Formula</th><th>anihpj</th></tr></thead><tbody><tr><td>Cost/Posting</td><td>$14.2K / 4.73M</td><td>$0.0030</td></tr><tr><td>Cost/App</td><td>$14.2K / 34.8M</td><td>$0.00041</td></tr><tr><td>Waste%</td><td>Waste/Total x100</td><td><5%</td></tr></tbody></table></div>',
    's14-3d': '<div class="diagram-container"><div class="diagram-title">Amortized Cost = Total Payment / Months</div><pre>\n  $10K RI All Upfront / 12mo = $833.33/mo amortized\n  USE amortized for: chargeback, unit economics\n  USE unblended for: budget alerts, anomaly detection (see cash spike)\n</pre></div>',
    's14-4': '<div class="diagram-container"><div class="diagram-title">3-Pass Strategy for 90-Minute Exam</div><pre>\n  PASS 1 (60min): Answer confident Qs. >90s -> MARK AND MOVE.\n  PASS 2 (20min): Return to marked. Eliminate 2 wrong -> 50% guess.\n  PASS 3 (10min): Final review. Check calculations. NEVER leave blank.\n</pre></div>',
    's14-5': '<div class="compare-table"><table><thead><tr><th>Question Pattern</th><th>Strategy</th></tr></thead><tbody><tr><td>Maturity Stage</td><td>Eliminate answers from wrong stage</td></tr><tr><td>Optimization Order</td><td>Always: Rightsize -> Reserve -> Spot</td></tr><tr><td>Calculation</td><td>Write formula on scratch paper first</td></tr><tr><td>Tool Selection</td><td>Match tool cost to cloud spend scale</td></tr></tbody></table></div>',
    's14-7': '<div class="diagram-container"><div class="diagram-title">Day-Before + Exam-Day Checklist</div><pre>\n  DAY BEFORE: Review 5 formulas + 6 Principles | Sleep 8hrs | NO cramming\n  EXAM DAY: Wake 2hrs before | Light breakfast | System check 30min before | Clear desk\n</pre></div>',
    's15-3': '<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Lab 3 Commands</span></div><pre><code class="language-bash">kubectl apply -f vpa-v0.14.0.yaml\nkubectl get vpa -n jobpost-prod -o yaml | grep recommendation\nkubectl patch deploy anihpj-web -p \'{"spec":{"template":{"spec":{"containers":[{"name":"web","resources":{"requests":{"cpu":"500m","memory":"512Mi"}}}}]}}\'</code></pre></div>',
    's15-4': '<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Lab 4 Karpenter Config</span></div><pre><code class="language-yaml">apiVersion: karpenter.sh/v1beta1\nkind: NodePool\nmetadata:\n  name: dev-spot\nspec:\n  template:\n    spec:\n      taints:\n        - key: spot\n          value: "true"\n          effect: PreferNoSchedule\n      requirements:\n        - key: karpenter.sh/capacity-type\n          operator: In\n          values: [spot, on-demand]\n  disruption:\n    consolidationPolicy: WhenUnderutilized</code></pre></div>',
    's17-1': '<div class="diagram-container"><div class="diagram-title">5 Reasons Organizations Go Multi-Cloud</div><pre>\n  1. Acquisition (bought company on different cloud)\n  2. Compliance (data residency laws require specific regions)\n  3. Best-of-Breed (AWS compute + Azure AD + GCP BigQuery)\n  4. Negotiation Leverage (2+ providers = pricing power)\n  5. Resilience/DR (avoid single-provider dependency)\n</pre></div>',
    's17-2': '<div class="compare-table"><table><thead><tr><th>Challenge</th><th>Solution</th></tr></thead><tbody><tr><td>Different billing models</td><td>Normalize to common unit ($/vCPU-hr)</td></tr><tr><td>Separate consoles</td><td>Third-party tool (CloudHealth, Vantage)</td></tr><tr><td>Different discount programs</td><td>Track coverage per cloud separately</td></tr><tr><td>Cross-cloud data egress</td><td>Minimize cross-cloud data movement</td></tr></tbody></table></div>',
    's17-4': '<div class="diagram-container"><div class="diagram-title">Cloud Arbitrage — Theory vs Reality</div><pre>\n  THEORY: Shift to cheapest provider in real-time -> 30%+ savings\n  REALITY: Data gravity + API differences + latency = impractical for real-time\n  VIABLE FOR: Batch/analytics workloads only\n</pre></div>',
    's17-5': '<div class="diagram-container"><div class="diagram-title">Multi-Cloud Commitment Tracking</div><pre>\n  AWS: Savings Plans (60-80% target) | Azure: Reserved Instances | GCP: CUDs\n  RULE: Track per cloud. Each has unique discount mechanics.\n</pre></div>',
    's17-6': '<div class="diagram-container"><div class="diagram-title">anihpj Multi-Cloud: AWS Primary + Azure DR</div><pre>\n  PRIMARY AWS: $14,200/mo (EKS+RDS+S3+CDN)\n  DR Azure: $3,800/mo (AKS standby + DB replica + Blob)\n  TOTAL: $18,000/mo. DR adds 27% baseline cost.\n</pre></div>',
    's19-4': '<div class="diagram-container"><div class="diagram-title">Translate Cloud Metrics to Business Impact</div><pre>\n  "ESR 35%" -> "Saving $2,100/month on compute"\n  "Unit cost down 14%" -> "Each posting costs $0.0030 vs $0.0035"\n  GOLDEN RULE: Never present metrics without business context.\n</pre></div>',
    's19-5': '<div class="diagram-container"><div class="diagram-title">Pushback -> Response Playbook</div><pre>\n  "Not an accountant!" -> "Cost is an engineering signal, like CPU. A spike = something wrong."\n  "Optimization slows me down" -> "30 min rightsizing = $828/mo savings for your team."\n  "Data is inaccurate" -> "Let us review together. Show me what looks wrong."\n</pre></div>',
    's19-6': '<div class="diagram-container"><div class="diagram-title">FinOps Team Scaling by Org Size</div><pre>\n  1-50 eng: 0.2 FTE (20% role) | 50-200: 1 FTE | 200-500: 2-3 FTE\n  500-1000: 4-6 FTE | 1000+: 6-10+ (FinOps CoE)\n  anihpj (15): Part-time. Hire first dedicated FinOps Practitioner at ~50 engineers.\n</pre></div>',
    's20-1a': '<div class="compare-table"><table><thead><tr><th>GPU</th><th>Instance</th><th>$/hr</th><th>Best For</th></tr></thead><tbody><tr><td>A100</td><td>p4d.24xl</td><td>$32.77</td><td>Large model training</td></tr><tr><td>H100</td><td>p5.48xl</td><td>$98.32</td><td>LLM training</td></tr><tr><td>Inferentia2</td><td>inf2.48xl</td><td>$12.98</td><td>Cost-effective inference</td></tr></tbody></table></div>',
    's20-1b': '<div class="diagram-container"><div class="diagram-title">Training vs Inference Cost Dynamics</div><pre>\n  TRAINING: p4d x 100hrs x $32.77 = $13,108/mo (monthly retrain)\n  INFERENCE: 34.8M apps/mo x $0.0004 = $13,920/mo\n  Year 1: Training dominates. Year 3+: Inference FAR exceeds training.\n</pre></div>',
    's20-1c': '<div class="diagram-container"><div class="diagram-title">anihpj Resume Scoring ML Costs</div><pre>\n  Training: g5.2xl x 8hrs x $1.21/hr = $9.68/run\n  Inference: 34.8M apps x $0.0002 = $6,960/mo\n  TOTAL: ~$6,970/mo | Optimize: Inf2 reduces inference cost 40%\n</pre></div>',
    's20-3': '<div class="diagram-container"><div class="diagram-title">Data Pipeline Cost Optimization</div><pre>\n  Compute: Spot for batch ETL | Storage: Lifecycle to glacier | Query: Partition + compress\n  KEY: Analytics costs grow with DATA VOLUME, not user traffic.\n</pre></div>',
    's20-4': '<div class="diagram-container"><div class="diagram-title">Serverless — When Lambda Wins vs Loses</div><pre>\n  WINS: Low traffic (<500K req/hr) | Spiky | Event-driven | Prototypes\n  LOSES: High steady traffic | 24/7 predictable | Long-running | GPU needed\n  anihpj: Lambda for image resizing. EC2 for web API (steady 24/7).\n</pre></div>',
}

enriched = 0
for sec_id, visual in visuals.items():
    pattern = f'id="{sec_id}"'
    idx = content.find(pattern)
    if idx == -1:
        print(f'  SKIP: {sec_id}')
        continue
    
    # Find section-block opening
    block_start = content.rfind('<div class="section-block"', 0, idx)
    if block_start == -1:
        continue
    
    # Find next section-block or other marker after this one
    markers = ['<div class="section-block"', '<div class="fce-exam-questions"', '<div class="visual-summary"']
    end = len(content)
    for m in markers:
        pos = content.find(m, block_start + 50)
        if pos != -1 and pos < end:
            end = pos
    
    section_text = content[block_start:end]
    last_close = section_text.rfind('</div>')
    if last_close > 0:
        new_section = section_text[:last_close] + '\n' + visual + '\n' + section_text[last_close:]
        content = content[:block_start] + new_section + content[end:]
        enriched += 1
        print(f'  OK: {sec_id}')

print(f'\nEnriched: {enriched}')
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
