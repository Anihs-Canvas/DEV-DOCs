"""Bulk-enrich remaining thin sections across Ch 1-10, 16 with relevant content."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

enriched = 0

# Visual content per section — keyed by section ID
fixes = {
    # Ch 1 — FinOps Fundamentals
    's1-3': '<div class="diagram-container"><div class="diagram-title">FinOps Lifecycle — Inform, Optimize, Operate</div><pre>\n  INFORM (Crawl)           OPTIMIZE (Walk)           OPERATE (Run)\n  |                       |                        |\n  Visibility -> Allocation -> Rates -> Usage -> Continuous Improvement\n  "See the bill"          "Reduce the bill"        "Prevent waste"\n</pre></div>',
    's1-3a': '<div class="diagram-container"><div class="diagram-title">Inform Phase — Key Activities</div><pre>\n  Cost Visibility: CUR exports, dashboards, tagging\n  Allocation: Map costs to teams/apps/business units\n  Budgeting: Set spending targets, forecast trends\n</pre></div>',
    's1-3b': '<div class="diagram-container"><div class="diagram-title">Optimize Phase — Key Activities</div><pre>\n  Rightsizing: Match resources to actual usage\n  Rate Optimization: RIs, SPs, Spot instances\n  Usage Optimization: Autoscaling, scheduling, tiering\n</pre></div>',
    's1-3c': '<div class="diagram-container"><div class="diagram-title">Operate Phase — Key Activities</div><pre>\n  Continuous monitoring: Anomaly detection, alerting\n  Policy automation: SCPs, cost gates, auto-remediation\n  Culture: Cost-aware engineering, chargeback, training\n</pre></div>',
    's1-7': '<div class="diagram-container"><div class="diagram-title">anihpj FinOps Maturity Journey</div><pre>\n  MONTH 0-3 (Crawl): Kubecost installed, monthly cost review, 15% ESR\n  MONTH 3-9 (Walk): SP purchased, Spot for dev, anomaly alerts, 30% ESR\n  MONTH 9-15 (Run): CI/CD cost gates, auto-shutdown, chargeback, 40% ESR\n</pre></div>',

    # Ch 3 — Pricing Models
    's3-1a': '<div class="diagram-container"><div class="diagram-title">On-Demand — Pay As You Go</div><pre>\n  RATE: Full price, no commitment | FLEXIBILITY: Start/stop anytime\n  BEST FOR: Variable workloads, new apps, dev/test\n  anihpj USE: Staging workloads (variable, no commitment needed)\n</pre></div>',
    's3-1b': '<div class="diagram-container"><div class="diagram-title">Reserved Instances — Commit for Discount</div><pre>\n  DISCOUNT: 30-72% vs On-Demand | COMMITMENT: 1-3 years\n  STANDARD RI: Best discount, locked to family | CONVERTIBLE: Lower discount, can exchange\n  BEST FOR: Steady-state production | anihpj: m6i.large RI for prod nodes\n</pre></div>',
    's3-1c': '<div class="diagram-container"><div class="diagram-title">Savings Plans — Flexible Commitment</div><pre>\n  DISCOUNT: 28-72% | COMMITMENT: 1-3 years, $/hr spending\n  COVERS: EC2 + Lambda + Fargate, any family/region\n  BEST FOR: Compute workloads that may change instance families\n  anihpj: $4/hr Compute SP covering prod EKS nodes\n</pre></div>',
    's3-2a': '<div class="diagram-container"><div class="diagram-title">Spot Instances — Spare Capacity at Deep Discount</div><pre>\n  DISCOUNT: 60-90% vs On-Demand | RISK: 2-min termination warning\n  BEST FOR: Fault-tolerant, stateless, batch, CI/CD, dev/staging\n  NOT FOR: Stateful databases, latency-sensitive production\n  anihpj: Dev + staging 100% Spot, saves $1,340/month\n</pre></div>',
    's3-2b': '<div class="diagram-container"><div class="diagram-title">Azure Reserved VM + GCP CUDs</div><pre>\n  AZURE RI: 30-60% discount, 1-3yr, instance-size-flexibility\n  GCP CUD: 30-57% discount, commit $/hr spend, auto-applied, no lock-in\n  Both: Similar concept to AWS RIs but with cloud-specific mechanics\n</pre></div>',
    's3-2c': '<div class="diagram-container"><div class="diagram-title">Hybrid Pricing Strategy</div><pre>\n  PROD 24/7: Savings Plans (60-70% coverage)\n  STAGING daytime: Spot (100% with OD fallback)\n  DEV daytime: Spot + auto-shutdown at night\n  BATCH/CI/CD: 100% Spot, ephemeral\n  RESULT: Blended 40-50% savings vs pure On-Demand\n</pre></div>',
    's3-2d': '<div class="diagram-container"><div class="diagram-title">Pricing Model Comparison</div><pre>\n  MODEL         COST      FLEX    COMMIT      BEST FOR\n  On-Demand     $$$$$     High    None        Variable/new\n  RI (Standard) $          Low     1-3yr       Stable prod\n  RI (Conv)     $$         Med     1-3yr       Planned migration\n  Savings Plan  $$         High    1-3yr $/hr  Any compute\n  Spot          $          Lowest  None        Fault-tolerant\n</pre></div>',
    's3-4': '<div class="diagram-container"><div class="diagram-title">Billing Data Pipeline</div><pre>\n  AWS Resources -> CUR (S3) -> Athena/QuickSight -> Dashboard\n  Azure Resources -> Cost Management Export -> PowerBI -> Dashboard\n  GCP Resources -> BigQuery Export -> Data Studio -> Dashboard\n</pre></div>',
    's3-5': '<div class="diagram-container"><div class="diagram-title">Enterprise Discount Programs</div><pre>\n  AWS: EDP (Enterprise Discount Program) — volume-based committed spend discounts\n  Azure: EA (Enterprise Agreement) — negotiated discounts for multi-year commits\n  GCP: Committed Use + volume discounts — simpler than AWS/EA\n  TYPICAL SAVINGS: 5-10% beyond standard RI/SP discounts at scale\n</pre></div>',
    's3-6': '<div class="diagram-container"><div class="diagram-title">Marketplace & Private Offers</div><pre>\n  AWS Marketplace: 3rd-party software + services through AWS billing\n  Private Offers: Negotiated pricing with ISVs via marketplace\n  BENEFIT: Consolidated billing, faster procurement, committed spend credit\n</pre></div>',

    # Ch 4 — Reserved Instances & Savings Plans
    's4-3d': '<div class="diagram-container"><div class="diagram-title">SP Purchase Strategy — Staggered Approach</div><pre>\n  Month 0: Buy 33% of baseline (1yr) | Month 4: Buy 33% (1yr) | Month 8: Buy 34% (1yr)\n  WHY: Avoids locking in for overprovisioned baselines. Rightsize between batches.\n  anihpj: $3/hr SP bought in 3 batches over 8 months. Coverage: 67%.\n</pre></div>',
    's4-3e': '<div class="diagram-container"><div class="diagram-title">RI/SP Exchange & Modification</div><pre>\n  Standard RI: Cannot modify. Sell on marketplace (70-90% recovery).\n  Convertible RI: Exchange for different family/OS/tenancy. No marketplace.\n  Savings Plan: No exchange needed. Automatically applies across families.\n</pre></div>',
    's4-4b': '<div class="diagram-container"><div class="diagram-title">RI Risk Mitigation</div><pre>\n  RISK 1: Stranded RIs (migrated away from instance family)\n  MITIGATE: Use SP instead. SP follows any instance family.\n  RISK 2: Over-commitment (bought more than needed)\n  MITIGATE: Stagger purchases. Sell excess RIs on marketplace.\n</pre></div>',
    's4-4c': '<div class="diagram-container"><div class="diagram-title">RI Marketplace — Recover Stranded Costs</div><pre>\n  SELL unused Standard RIs: Recovers 70-90% of remaining value\n  BUY short-term RIs: Others sell their unused — you get discount without 1-3yr lock-in\n  anihpj: Sold m5 RIs during m6i migration, recovered $2,400\n</pre></div>',

    # Ch 5 — Cost Allocation
    's5-2': '<div class="diagram-container"><div class="diagram-title">Tagging Taxonomy — 10 Essential Tags</div><pre>\n  MANDATORY: Environment | Application | Team | CostCenter | Owner\n  ADVISORY: Component | DataClassification | Compliance | ProvisionedBy | AutoShutdown\n  RULE: Enforce mandatory tags via SCP/Kyverno. Advisory tags via CI/CD checks.\n</pre></div>',
    's5-3a': '<div class="diagram-container"><div class="diagram-title">Allocation Hierarchy</div><pre>\n  PROVIDER (AWS) -> ACCOUNT -> RESOURCE (EC2) -> APPLICATION (anihpj) -> TEAM (jobpost)\n  Each level adds more business context. Tags bridge resource -> business.\n</pre></div>',
    's5-3b': '<div class="diagram-container"><div class="diagram-title">Shared vs Direct Costs</div><pre>\n  DIRECT: Single-tenant resources (RDS per team) -> assign directly\n  SHARED: Multi-tenant resources (EKS control plane) -> split proportionally\n  UNALLOCATED: Untagged resources -> target <5% at Run stage\n</pre></div>',
    's5-3d': '<div class="diagram-container"><div class="diagram-title">Tag Enforcement Strategy</div><pre>\n  LAYER 1: IaC (Terraform required_tags module) — catch at code review\n  LAYER 2: SCP/Azure Policy — block creation without tags\n  LAYER 3: Detective (AWS Config rules) — find what slipped through\n</pre></div>',

    # Ch 6 — Dashboards
    's6-1': '<div class="diagram-container"><div class="diagram-title">Dashboard Personas</div><pre>\n  EXEC: 6 KPIs, MoM trends, top drivers | ENG: Per-service, per-pod, recommendations\n  FINANCE: Budget vs Actual, forecast, variance | FINOPS: All views + anomaly alerts\n</pre></div>',
    's6-2b': '<div class="diagram-container"><div class="diagram-title">Unit Economics — Why It Matters</div><pre>\n  CLOUD BILL: $14,200/mo (just a number)\n  UNIT COST: $0.003/posting (meaningful — ties cost to business value)\n  If unit cost drops while bill rises = EFFICIENCY (good scaling)\n</pre></div>',
    's6-3b': '<div class="diagram-container"><div class="diagram-title">AWS Anomaly Detection Setup</div><pre>\n  Cost Explorer -> Anomaly Detection -> Create monitor\n  Threshold: Alert when daily spend >40% above expected\n  Notify: SNS -> Slack/Email/PagerDuty\n  COST: Free (included with AWS)\n</pre></div>',
    's6-3c': '<div class="diagram-container"><div class="diagram-title">Azure Anomaly Detection</div><pre>\n  Cost Management -> Budgets -> Set threshold alerts\n  Anomaly detection: ML-based, auto-detects unusual patterns\n  Alerts -> Action Groups (Email, Webhook, Azure Function)\n</pre></div>',
    's6-3d': '<div class="diagram-container"><div class="diagram-title">GCP Anomaly Detection</div><pre>\n  Billing -> Budgets & Alerts -> Pub/Sub notifications\n  BigQuery billing export + custom SQL anomaly queries\n  Recommender: ML-based idle resource identification\n</pre></div>',
    's6-4a': '<div class="diagram-container"><div class="diagram-title">Simple Trend Forecasting</div><pre>\n  FORMULA: Spend_Today + (Daily_Avg x Days_Remaining)\n  Example: $10,000 spent in 20 days ($500/day) x 10 days left = $5,000\n  Forecast: $15,000 total | USE: Mid-month spot checks, Crawl stage\n</pre></div>',
    's6-4b': '<div class="diagram-container"><div class="diagram-title">ML-Based Forecasting</div><pre>\n  AWS Cost Explorer ML forecast: Accounts for seasonality, growth, day-of-week\n  Requires 7+ days historical data | USE: Quarterly planning, budget setting\n  More accurate than simple trend at Run stage\n</pre></div>',
    's6-5': '<div class="diagram-container"><div class="diagram-title">Benchmarking Approach</div><pre>\n  INTERNAL: Compare teams on unit cost (not absolute spend)\n  EXTERNAL: FinOps Foundation benchmarking data (industry averages)\n  GOAL: Identify best practices, not rank-and-shame\n</pre></div>',
    's6-5b': '<div class="diagram-container"><div class="diagram-title">Industry Benchmarks</div><pre>\n  SaaS cloud spend: 15-25% of revenue | Waste average: 10-30%\n  anihpj: 18% of revenue, 4.2% waste — above average on both metrics\n</pre></div>',

    # Ch 7 — Autoscaling
    's7-2b': '<div class="diagram-container"><div class="diagram-title">Compute SP vs EC2 Instance SP</div><pre>\n  COMPUTE SP: Covers EC2+Lambda+Fargate, any family/region/size, most flexible\n  EC2 SP: Covers EC2 only, locked to family+region, slightly higher discount\n  RECOMMEND: Compute SP for most. EC2 SP only if 100% sure about instance family.\n</pre></div>',
    's7-2c': '<div class="diagram-container"><div class="diagram-title">Azure Reserved VM Instances</div><pre>\n  Discount: 30-60% | Term: 1-3yr | Instance size flexibility: Yes\n  Exchange: Can exchange for different sizes within same family\n  Cancel: Limited (max $50K/yr) | Marketplace: No resale\n</pre></div>',
    's7-2d': '<div class="diagram-container"><div class="diagram-title">GCP Committed Use Discounts</div><pre>\n  Commit: $X/hr spend for 1-3yr | Discount: 30-57%\n  Auto-applied: No instance matching. Just commit spend.\n  Flexibility: Any machine type, any region. Simplest model.\n</pre></div>',
    's7-4a': '<div class="diagram-container"><div class="diagram-title">HPA Behavior Configuration</div><pre>\n  scaleUp.stabilizationWindowSeconds: 60 (react quickly to spikes)\n  scaleDown.stabilizationWindowSeconds: 300 (wait before scaling down)\n  scaleDown.policies: pods=1, periodSeconds=60 (gradual scale-down)\n  WHY: Rapid scale-down causes thrashing. Gradual = stable + cost-efficient.\n</pre></div>',
    's7-4b': '<div class="diagram-container"><div class="diagram-title">VPA Modes</div><pre>\n  Off: Recommendations only (safe for production, start here)\n  Initial: Sets requests at pod creation (for new workloads)\n  Auto: Updates requests dynamically (requires pod restart)\n  CAUTION: Auto mode restarts pods. Test in staging first.\n</pre></div>',
    's7-4c': '<div class="diagram-container"><div class="diagram-title">Cluster Autoscaler Operation</div><pre>\n  TRIGGER: Pods in Pending state (no node has capacity)\n  ACTION: Provisions new node from Auto Scaling Group\n  SCALE-DOWN: Removes underutilized nodes (pods can be rescheduled)\n  LIMIT: Only removes nodes with <50% requested CPU + free pods\n</pre></div>',
    's7-4d': '<div class="diagram-container"><div class="diagram-title">Karpenter Consolidation</div><pre>\n  DETECTS: Underutilized nodes (pods could fit on fewer nodes)\n  ACTIONS: Drains pods -> moves to remaining nodes -> deletes empty node\n  RESULT: Higher utilization, fewer nodes, $138/node/month saved\n  anihpj: 2 nodes removed via consolidation = $276/month saved\n</pre></div>',
    's7-4e': '<div class="diagram-container"><div class="diagram-title">Scheduled Scaling</div><pre>\n  M-F 7AM: Scale to 3 replicas (start of day)\n  M-F 8PM: Scale to 0 replicas (end of day)\n  Weekends: Scale to 0 (no dev traffic)\n  USES: CronJob + kubectl scale OR Keda ScaledJob\n</pre></div>',
    's7-5c': '<div class="diagram-container"><div class="diagram-title">Node Pool Strategy</div><pre>\n  PROD POOL: On-Demand + RI, m6i.xlarge, no Spot taint\n  STAGING POOL: 100% Spot, mixed families, Spot taint\n  DEV POOL: 100% Spot, tainted, auto-shutdown at 8PM\n  SYSTEM POOL: On-Demand, small, for kube-system pods only\n</pre></div>',
    's7-5d': '<div class="diagram-container"><div class="diagram-title">K8s Optimization Checklist</div><pre>\n  1. Rightsize pod requests (VPA recommendations)\n  2. Set resource limits (prevent runaway pods)\n  3. Configure HPA (min=baseline, max=business ceiling)\n  4. Bin pack with Karpenter consolidation\n  5. Spot for dev/staging/CI/CD with OD fallback\n</pre></div>',

    # Ch 8 — Storage & Network
    's8-1': '<div class="diagram-container"><div class="diagram-title">Storage Optimization Strategy</div><pre>\n  1. TIER: Move cold data to cheaper classes (Hot -> IA -> Glacier)\n  2. LIFECYCLE: Automate transitions with S3 lifecycle policies\n  3. DELETE: What you do not need (unattached volumes, old snapshots)\n  RESULT: 40-80% storage cost reduction without data loss\n</pre></div>',
    's8-1b': '<div class="diagram-container"><div class="diagram-title">S3 Lifecycle Policy Example</div><pre>\n  Day 0-30: S3 Standard ($0.023/GB) — active data\n  Day 30-90: S3 IA ($0.0125/GB) — infrequent access\n  Day 90-365: Glacier ($0.004/GB) — quarterly access\n  Day 365+: Delete or Glacier Deep Archive ($0.00099/GB)\n  anihpj: Applied to job posting images -> saves $85/month\n</pre></div>',
    's8-1c': '<div class="diagram-container"><div class="diagram-title">Zombie Resource Cleanup</div><pre>\n  UNATTACHED EBS: $0.08/GB/month. 500GB unattached = $40/month wasted.\n  ORPHANED SNAPSHOTS: Accumulate silently. Retain 7d+4w+12m max.\n  UNUSED EIPs: $3.60/month each. Release if not attached.\n  FIX: Cloud Custodian reaper policy -> auto-delete after 7 days idle.\n</pre></div>',
    's8-1d': '<div class="diagram-container"><div class="diagram-title">S3 Intelligent-Tiering</div><pre>\n  Automatically moves objects between Frequent and Infrequent Access tiers\n  Monitor: 30 days of access patterns | Move: Auto-transitions with zero retrieval fees\n  Cost: $0.0025/1000 objects monitoring fee | Savings: ~40% for intermittently accessed data\n  BEST FOR: Unpredictable access patterns (like job posting images)\n</pre></div>',
    's8-2': '<div class="diagram-container"><div class="diagram-title">Database Optimization</div><pre>\n  1. RIGHTSIZE: Match instance to actual workload (not guess)\n  2. RI PURCHASE: RDS RIs save 30-60%. Only RI, no SP option.\n  3. STORAGE: gp3 instead of gp2 (20% cheaper, better performance)\n  4. READ REPLICAS: Offload read traffic. Use RI on replicas too.\n</pre></div>',
    's8-2a': '<div class="diagram-container"><div class="diagram-title">RDS Cost Levers</div><pre>\n  INSTANCE: db.t3.medium ($34.56/mo RI) vs db.r5.large ($142/mo RI) — 4x difference\n  STORAGE: gp3 ($0.08/GB) vs io1 ($0.125/GB + IOPS) — 35%+ savings on gp3\n  MULTI-AZ: Doubles cost. Use Single-AZ with snapshots if RTO allows.\n  BACKUP RETENTION: 7 days (free) vs 35 days (extra cost). Keep what you need.\n</pre></div>',
    's8-2b': '<div class="diagram-container"><div class="diagram-title">Aurora Serverless v2</div><pre>\n  Auto-scales capacity in ACUs (Aurora Capacity Units) based on demand\n  COST: ~$0.12/ACU-hour. Scale to 0 ACUs to pause (no compute cost).\n  BEST FOR: Variable workloads, dev/test databases, infrequent access\n  anihpj: Staging DB on Aurora Serverless v2. Scales down at night. Saves ~$40/mo.\n</pre></div>',
    's8-2e': '<div class="diagram-container"><div class="diagram-title">Database Rightsizing Flow</div><pre>\n  COLLECT (14 days of CloudWatch metrics) -> ANALYZE (P95 connections, CPU, IOPS)\n  -> COMPARE (current vs recommended instance) -> TEST (staging first)\n  -> APPLY (modify during maintenance window) -> VERIFY (monitor 48-72h)\n</pre></div>',
    's8-3a': '<div class="diagram-container"><div class="diagram-title">Hidden Network Costs</div><pre>\n  CROSS-AZ: $0.01/GB each direction ($0.02/GB round-trip). 500GB/mo = $120/yr wasted.\n  NAT GATEWAY: $0.045/hr ($32.85/mo) + $0.045/GB processed.\n  INTER-REGION: $0.02/GB (much more expensive than cross-AZ).\n  FIX: Pod affinity to same AZ, VPC endpoints for S3/DynamoDB (free).\n</pre></div>',
    's8-3b': '<div class="diagram-container"><div class="diagram-title">VPC Endpoints — Eliminate NAT Gateway Costs</div><pre>\n  GATEWAY ENDPOINTS (free): S3, DynamoDB — no data processing charge\n  INTERFACE ENDPOINTS: $0.01/hr + $0.01/GB — still cheaper than NAT for high-volume\n  anihpj: VPC Endpoint for S3 eliminates $45/mo NAT Gateway data charges\n</pre></div>',
    's8-3c': '<div class="diagram-container"><div class="diagram-title">CDN Cost-Benefit</div><pre>\n  WITHOUT CDN: S3 direct transfer $0.09/GB, 100% origin load, 50-200ms latency\n  WITH CDN: CloudFront $0.085/GB, 80% cache hit -> only 20% origin load, 5-20ms\n  anihpj: 2TB monthly images. S3 direct = $180/mo. CloudFront = $173/mo + better perf.\n</pre></div>',

    # Ch 9
    's9-5a': '<div class="diagram-container"><div class="diagram-title">Resource Quotas — anihpj Namespaces</div><pre>\n  prod: 20 CPU, 40Gi, 50 pods | staging: 12 CPU, 24Gi, 30 pods\n  dev: 8 CPU, 16Gi, 20 pods | CI/CD: 16 CPU, 32Gi, 10 pods (ephemeral)\n  RULE: Quotas prevent one team from consuming the entire cluster.\n</pre></div>',

    # Ch 10
    's10-1b': '<div class="diagram-container"><div class="diagram-title">Request vs Limit vs Actual Usage</div><pre>\n  REQUEST: Guaranteed minimum. Scheduler uses this. Sets node count.\n  LIMIT: Maximum allowed. Can burst up to this. Throttled if exceeded.\n  ACTUAL: What pod really uses. Often much lower than request (waste!).\n  RULE: Request = P95 actual + 30% buffer. Limit = P95 x 1.5-2x.\n</pre></div>',
    's10-2': '<div class="diagram-container"><div class="diagram-title">Infrastructure-Level Optimization Strategy</div><pre>\n  SPOT: 60-90% savings for fault-tolerant workloads\n  MIXED INSTANCES: Multiple families = higher Spot availability\n  KARPENTER: Intelligent provisioning + consolidation\n  CUSTOM: ARM (m7g) for 20% extra savings on compatible workloads\n</pre></div>',
    's10-3': '<div class="diagram-container"><div class="diagram-title">Workload-Level Optimization Strategy</div><pre>\n  HPA: Horizontal pod autoscaling based on CPU/memory/custom metrics\n  PRIORITY CLASSES: Prod > Staging > Dev. Evict lower when tight.\n  QUOTAS: Cap per-namespace resource consumption\n  PDBs: Allow disruption for consolidation while maintaining availability\n</pre></div>',
    's10-4': '<div class="diagram-container"><div class="diagram-title">Container Optimization</div><pre>\n  IMAGE SIZE: Smaller images = faster pulls = faster scaling\n  RESOURCE REQUESTS: Set on ALL containers (no BestEffort QoS)\n  INIT CONTAINERS: Use for setup tasks, not sidecar waste\n  LIVENESS PROBES: Long timeouts waste resources on hung pods\n</pre></div>',

    # Ch 16
    's16-1': '<div class="diagram-container"><div class="diagram-title">Domain 1: FinOps Principles (20%)</div><pre>\n  Key topics: 6 Principles, Maturity Model (Crawl/Walk/Run), Stakeholders, Culture\n  ~15 questions. Focus: Apply principles to scenarios. Know COBALT.\n</pre></div>',
    's16-2': '<div class="diagram-container"><div class="diagram-title">Domain 2: Cloud Financial Management (26%)</div><pre>\n  Key topics: Pricing models, CUR, amortization, ESR, Coverage, forecasting\n  ~20 questions. HEAVIEST domain. Master ESR + Coverage formulas.\n</pre></div>',
    's16-3': '<div class="diagram-container"><div class="diagram-title">Domain 3: Cost Allocation (14%)</div><pre>\n  Key topics: Tagging taxonomy, shared cost allocation, showback/chargeback\n  ~11 questions. Know proportional vs fixed vs direct allocation methods.\n</pre></div>',
    's16-4': '<div class="diagram-container"><div class="diagram-title">Domain 4: Optimization (22%)</div><pre>\n  Key topics: Rightsizing, RIs/SPs, Spot, autoscaling, K8s optimization\n  ~17 questions. Know optimization ORDER: Rightsize -> Reserve -> Spot.\n</pre></div>',
    's16-5': '<div class="diagram-container"><div class="diagram-title">Domain 5: Governance & Automation (18%)</div><pre>\n  Key topics: Policy-as-Code, CI/CD cost gates, auto-remediation, SaaS FinOps\n  ~14 questions. Know preventive vs detective vs corrective controls.\n</pre></div>',
}

for sec_id, visual in fixes.items():
    idx = content.find(f'id="{sec_id}"')
    if idx == -1:
        continue
    
    block_start = content.rfind('<div class="section-block"', 0, idx)
    if block_start == -1:
        continue
    
    markers = ['<div class="section-block"', '<div class="fce-exam-questions"', '<div class="visual-summary"']
    end = len(content)
    for m in markers:
        p = content.find(m, block_start + 50)
        if p != -1 and p < end:
            end = p
    
    section_text = content[block_start:end]
    last_close = section_text.rfind('</div>')
    if last_close > 0:
        new_section = section_text[:last_close] + '\n' + visual + '\n' + section_text[last_close:]
        content = content[:block_start] + new_section + content[end:]
        enriched += 1

print(f'Enriched: {enriched}')
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
