#!/usr/bin/env python3
"""Enrich finOps_eng.html Q&A blocks with YAML, tables, and diagrams based on topic keywords."""

import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'

with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Track enrichment count
enriched_count = 0

def inject_after_answer(block, visual_html):
    """Inject visual HTML right before the closing eq-answer div but after the <p> content."""
    # Find the last </p> before </div> in the answer section
    # Pattern: answer div with its content, then inject before </div></details> or before eq-explanation
    # We'll inject right after the answer's closing </div> and before </details> or eq-explanation
    # Actually let's inject right before </div> of eq-answer
    if 'eq-explanation' in block:
        # Inject before eq-explanation div
        return block.replace('<div class="eq-explanation">', visual_html + '\n<div class="eq-explanation">', 1)
    else:
        # Inject before </details>
        return block.replace('</details>', visual_html + '\n</details>', 1)

def has_visual(block):
    """Check if block already has visual elements."""
    return bool(re.search(r'(<pre>|<table|<div class="diagram-container"|<div class="code-block-wrapper"|<div class="compare-table")', block))

# Chapter-specific enrichment templates
templates = {
    # Ch 1: FinOps Fundamentals
    'principles|finops principles|six principles': '''
<div class="diagram-container"><div class="diagram-title">🧭 The 6 FinOps Principles (COBALT)</div><pre>
  C — Collaboration    : Finance + Engineering + Business = One Team
  O — Ownership        : Everyone owns their cloud spend
  B — Business Value   : Decisions driven by business ROI, not cost alone
  A — Accessibility    : Timely, accessible cost data for all
  L — Lean Operations  : Eliminate waste continuously
  T — Transparency     : Costs visible to everyone, no hidden budgets

  MEMORY AID: "COBALT" — like the metal, strong and essential.
</pre></div>''',
    'crawl.*walk.*run|maturity model': '''
<div class="diagram-container"><div class="diagram-title">📈 FinOps Maturity Model — Crawl → Walk → Run</div><pre>
  CRAWL (0-6 months)          WALK (6-18 months)          RUN (18+ months)
  ┌────────────────────┐  ┌────────────────────────┐  ┌──────────────────────┐
  │ • See the bill      │  │ • Track by team/app     │  │ • Real-time visibility│
  │ • Monthly review    │  │ • Weekly review         │  │ • Automated actions   │
  │ • Manual tagging    │  │ • Tag enforcement       │  │ • CI/CD cost gates    │
  │ • 0-15% ESR        │  │ • 20-30% ESR            │  │ • 30-40% ESR          │
  │ • Awareness only    │  │ • Showback active       │  │ • Full chargeback     │
  └────────────────────┘  └────────────────────────┘  └──────────────────────┘
       "What did we spend?"      "How can we optimize?"       "Optimization is automatic"
</pre></div>''',
    'unit economics|cost per transaction|unit cost': '''
<div class="diagram-container"><div class="diagram-title">📐 Unit Economics Formula & Example</div><pre>
  UNIT COST = Total Cloud Spend / Number of Business Transactions

  anihpj EXAMPLES:
  ┌──────────────────────────────────────────────────────────────────┐
  │ Metric                      Formula                     Value    │
  │ ──────                      ───────                     ─────    │
  │ Cost per job posting        $14,200 / 4,730,000        $0.0030  │
  │ Cost per job application    $14,200 / 34,800,000       $0.00041 │
  │ Cost per active employer    $14,200 / 1,200            $11.83   │
  └──────────────────────────────────────────────────────────────────┘

  KEY INSIGHT: If unit cost rises, you're getting LESS business value
  per cloud dollar → investigate immediately.
</pre></div>''',
    
    # Ch 2: Cloud Financial Management  
    'pricing model.*on.demand|on.demand.*reserved|savings plan': '''
<div class="compare-table"><table><thead><tr><th>Model</th><th>Commitment</th><th>Discount</th><th>Flexibility</th><th>Best For</th></tr></thead><tbody>
<tr><td><strong>On-Demand</strong></td><td>None</td><td>0%</td><td>⭐⭐⭐⭐⭐</td><td>Variable/unpredictable workloads</td></tr>
<tr><td><strong>Reserved Instances</strong></td><td>1-3 years, instance-specific</td><td>30-72%</td><td>⭐⭐</td><td>Steady-state production</td></tr>
<tr><td><strong>Savings Plans</strong></td><td>1-3 years, $/hr</td><td>28-72%</td><td>⭐⭐⭐⭐</td><td>Any compute (EC2, Fargate, Lambda)</td></tr>
<tr><td><strong>Spot Instances</strong></td><td>None</td><td>60-90%</td><td>⭐</td><td>Fault-tolerant, stateless</td></tr>
</tbody></table></div>''',
    'esr|effective savings rate': '''
<div class="diagram-container"><div class="diagram-title">💰 ESR Calculation Visualized</div><pre>
  ESR = (On-Demand Equivalent - Actual Cost) / On-Demand Equivalent × 100

  EXAMPLE: On-Demand would cost $14,200. Actual bill is $9,230.
  ESR = ($14,200 - $9,230) / $14,200 × 100 = 35%

  TARGETS BY MATURITY:
  Crawl: 0-15%     Walk: 20-30%     Run: 30-40%
  ⚠️ Above 50% may indicate over-commitment (stranded RI risk)
</pre></div>''',
    
    # Ch 3/4: Optimization 
    'rightsizing|right.size|overprovision': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Rightsizing Check — kubectl top + describe</span></div><pre><code class="language-bash"># Check actual resource usage (metrics-server required)
kubectl top pods -n jobpost-prod

# Check requested vs actual (VPA Recommender)
kubectl get vpa anihpj-web-vpa -n jobpost-prod -o yaml
# Look for: recommendation.target.cpu, recommendation.target.memory

# AWS Compute Optimizer (EC2-level rightsizing)
aws compute-optimizer get-ec2-instance-recommendations \
  --instance-arns arn:aws:ec2:us-east-1:123456789:instance/i-0a3f</code></pre></div>''',
    
    # Ch 7-8: K8s compute/storage  
    'hpa|horizontal pod autoscaler|autoscal': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">HPA Configuration — anihpj-web</span></div><pre><code class="language-yaml">apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: anihpj-web-hpa
  namespace: jobpost-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: anihpj-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70    # Scale up at 70% CPU
    - type: Resource
      resource:
        name: memory
        target:
          averageUtilization: 80</code></pre></div>''',
    
    'spot instance|spot.*workload': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">K8s Spot Tolerance + Node Affinity</span></div><pre><code class="language-yaml">apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj-dev
spec:
  template:
    spec:
      tolerations:
        - key: "spot"
          operator: "Equal"
          value: "true"
          effect: "PreferNoSchedule"
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: karpenter.sh/capacity-type
                    operator: In
                    values: ["spot"]</code></pre></div>''',
    
    'kyverno|policy.*tag|policy.*compliance|opa': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Kyverno Policy — Enforce Cost Labels</span></div><pre><code class="language-yaml">apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-cost-allocation-labels
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-namespace-labels
      match:
        resources:
          kinds: [Namespace]
      validate:
        message: "All namespaces must have team and cost-center labels"
        pattern:
          metadata:
            labels:
              team: "?*"
              cost-center: "?*"</code></pre></div>''',

    'kubecost|opencost': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Kubecost — Install & Query Costs</span></div><pre><code class="language-bash"># Install Kubecost (Helm)
helm upgrade --install kubecost kubecost/cost-analyzer \
  --namespace kubecost --create-namespace

# Query cost by namespace (API)
kubectl port-forward svc/kubecost-cost-analyzer 9090:9090 -n kubecost
curl http://localhost:9090/model/costData \
  -d 'window=last7d&aggregate=namespace'

# Kubecost CLI — cost by team label
kubectl cost namespace --show-all-resources</code></pre></div>''',

    # Additional templates for remaining chapters
    'storage.*class|s3.*tier|lifecycle.*policy|glacier|ebs.*volume': '''
<div class="diagram-container"><div class="diagram-title">💾 Storage Tiering — Hot → Cold → Archive</div><pre>
  DATA TEMPERATURE     AWS S3 CLASS           COST/GB    ACCESS TIME
  ────────────────     ────────────           ───────    ───────────
  🔥 Hot (daily)       S3 Standard            $0.023     Instant
  🌤️ Warm (monthly)    S3 Infrequent Access   $0.0125    Instant
  ❄️ Cold (quarterly)  S3 Glacier             $0.004     Minutes-Hours
  🧊 Frozen (yearly)   S3 Glacier Deep Archive$0.00099   12-48 Hours

  5TB SAVINGS: Hot=$115/mo → Glacier=$20/mo = 83% reduction
</pre></div>''',

    'cross.az|data transfer|nat gateway|network.*cost': '''
<div class="diagram-container"><div class="diagram-title">🌐 Hidden Network Costs — Cross-AZ & NAT Gateway</div><pre>
  HIDDEN COST #1: Cross-AZ Data Transfer
  ┌────────────────────────────────────────────────────┐
  │ Pod-A (us-east-1a) ←→ Pod-B (us-east-1b)          │
  │ Each direction: $0.01/GB → $0.02/GB round-trip    │
  │ 500 GB/month between AZs = $120/year wasted       │
  │ FIX: Pod affinity to same AZ, topology spread     │
  └────────────────────────────────────────────────────┘

  HIDDEN COST #2: NAT Gateway
  ┌────────────────────────────────────────────────────┐
  │ $0.045/hour ($32.85/month) + $0.045/GB processed  │
  │ 100GB/month through NAT GW = $32.85 + $4.50       │
  │ FIX: VPC Endpoints for S3/DynamoDB (free)         │
  └────────────────────────────────────────────────────┘
</pre></div>''',

    'budget|forecast|billing.*alert': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">AWS Budget Alert Configuration</span></div><pre><code class="language-bash"># Create monthly budget with 3 alert thresholds
aws budgets create-budget \
  --account-id 123456789 \
  --budget '{"BudgetName":"anihpj-monthly","BudgetLimit":{"Amount":"15000","Unit":"USD"},"TimeUnit":"MONTHLY"}'

aws budgets create-notification \
  --account-id 123456789 \
  --budget-name anihpj-monthly \
  --notification '{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":50}' \
  --subscribers '[{"SubscriptionType":"SNS","Address":"arn:aws:sns:us-east-1:123456789:finops-alerts"}]'</code></pre></div>''',

    'reserved instance.*exchange|convertible|stranded|ri.*portfolio': '''
<div class="diagram-container"><div class="diagram-title">📋 RI Portfolio Management — Avoid Stranded Commitments</div><pre>
  RI TYPES:
  ┌──────────────┬────────────┬────────────┬──────────────────────┐
  │ Type         │ Discount   │ Flexibility│ Stranded Risk        │
  ├──────────────┼────────────┼────────────┼──────────────────────┤
  │ Standard RI  │ 30-72%     │ LOW        │ HIGH (locked to fam) │
  │ Convertible  │ 20-54%     │ MEDIUM     │ MED (can exchange)   │
  │ Savings Plan │ 28-72%     │ HIGH       │ LOW (any family)     │
  └──────────────┴────────────┴────────────┴──────────────────────┘

  RECOMMENDATION: Prefer Savings Plans over RIs for compute.
  Only use RIs for: RDS (no SP option), specific instance needs.
</pre></div>''',

    'tag.*enforce|tag.*policy|scp.*tag': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">AWS SCP — Deny EC2 Without Required Tags</span></div><pre><code class="language-json">{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyEC2WithoutTags",
    "Effect": "Deny",
    "Action": ["ec2:RunInstances"],
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "Null": {
        "aws:RequestTag/Environment": "true",
        "aws:RequestTag/Team": "true",
        "aws:RequestTag/CostCenter": "true"
      }
    }
  }]
}</code></pre></div>''',

    'database.*optim|rds.*cost|db.*rightsiz': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">RDS Cost Optimization Checklist</span></div><pre><code class="language-bash"># 1. Rightsize: Check actual DB metrics vs provisioned
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=anihpj-postgres

# 2. RI purchase: RDS RIs save 30-60% (only RI, not SP)
aws rds describe-reserved-db-instances-offerings \
  --db-instance-class db.t3.medium --product-description postgresql

# 3. Storage: Switch to gp3 from gp2 (20% cheaper, better perf)
aws rds modify-db-instance --db-instance-identifier anihpj-postgres \
  --storage-type gp3 --allocated-storage 100</code></pre></div>''',

    'chargeback|showback.*vs|chargeback.*showback': '''
<div class="compare-table"><table><thead><tr><th>Aspect</th><th>Showback</th><th>Chargeback</th></tr></thead><tbody>
<tr><td>Budget impact</td><td>None (informational only)</td><td>Actual budget deduction</td></tr>
<tr><td>Maturity stage</td><td>Crawl → early Walk</td><td>Late Walk → Run</td></tr>
<tr><td>Accuracy needed</td><td>80%+</td><td>95%+</td></tr>
<tr><td>Trust required</td><td>Moderate</td><td>High</td></tr>
<tr><td>Behavior change speed</td><td>Slow (awareness)</td><td>Fast (accountability)</td></tr>
</tbody></table></div>''',

    'finops team|finops practitioner|stakeholder|persona': '''
<div class="diagram-container"><div class="diagram-title">👥 FinOps Stakeholders & Personas</div><pre>
  FINOPS PRACTITIONER (You!)
  ┌────────────────────────────────────────────────────────┐
  │ Bridges Finance + Engineering + Business               │
  │ ↓                                                      │
  │ ┌──────────┬──────────────────┬──────────────────────┐ │
  │ │FINANCE   │ ENGINEERING      │ BUSINESS/EXECUTIVE   │ │
  │ │          │                  │                       │ │
  │ │• Budget  │ • Rightsizing    │ • Unit economics     │ │
  │ │• Forecast│ • Spot adoption  │ • Cloud as % revenue │ │
  │ │• Chargeb │ • Tag compliance │ • Strategic growth   │ │
  │ │• Amortize│ • K8s efficiency │ • Make vs Buy cloud  │ │
  │ └──────────┴──────────────────┴──────────────────────┘ │
  └────────────────────────────────────────────────────────┘
</pre></div>''',

    'cur|cost.*usage.*report|billing.*data': '''
<div class="diagram-container"><div class="diagram-title">📊 CUR — Cost & Usage Report Pipeline</div><pre>
  AWS RESOURCES          CUR (S3)               DASHBOARD/ANALYSIS
  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────┐
  │ EC2 (tags)   │──▶│ Hourly CSV   │──▶│ • Cost Explorer (quick) │
  │ RDS (tags)   │   │ with:         │   │ • Athena (SQL queries)  │
  │ S3 (tags)    │   │ • Resource ID │   │ • QuickSight (BI)      │
  │ Lambda (tags)│   │ • All tags    │   │ • 3rd party (CloudHlth)│
  └──────────────┘   │ • Cost/line   │   └─────────────────────────┘
                      │ • 24hr delay  │
                      └──────────────┘

  KEY FACT: CUR is the SOURCE OF TRUTH for all cost data.
  Dashboard tools (Cost Explorer, etc.) read from CUR.
</pre></div>''',

    'multicloud|multi.cloud|arbitrage': '''
<div class="compare-table"><table><thead><tr><th>Strategy</th><th>Approach</th><th>Complexity</th><th>Cost Impact</th></tr></thead><tbody>
<tr><td><strong>Multi-Cloud</strong></td><td>Run workloads on 2+ cloud providers</td><td>⭐⭐⭐⭐⭐</td><td>10-30% premium (unless arbitrage)</td></tr>
<tr><td><strong>Cloud Arbitrage</strong></td><td>Shift workloads to cheapest provider in real-time</td><td>⭐⭐⭐⭐⭐</td><td>Theoretical 20-40% savings</td></tr>
<tr><td><strong>Hybrid Cloud</strong></td><td>Mix on-prem + cloud</td><td>⭐⭐⭐⭐</td><td>Varies by workload</td></tr>
</tbody></table></div>''',

    'serverless|lambda.*cheaper|lambda.*expensive': '''
<div class="diagram-container"><div class="diagram-title">⚡ Serverless vs Provisioned — Cost Break-Even</div><pre>
  LAMBDA COST MODEL:
  ┌────────────────────────────────────────────────────────┐
  │ $0.20 per 1M requests + $0.0000166667 per GB-second    │
  │                                                         │
  │ EXAMPLE: 1M requests/day, 512MB, 200ms avg              │
  │ Compute: 1M × 0.2s × 0.5GB × $0.00001667 = $1.67/day  │
  │ Requests: 1M × $0.20/M = $0.20/day                     │
  │ Total: ~$56/month                                       │
  │                                                         │
  │ EC2 equivalent (t3.micro, $0.0104/hr): $7.50/month     │
  │                                                         │
  │ WHEN LAMBDA WINS: Low/medium traffic, spiky patterns    │
  │ WHEN EC2 WINS: High/steady traffic (>500K req/hr)      │
  └────────────────────────────────────────────────────────┘
</pre></div>''',

    'exam.*format|exam.*strategy|pass.*strategy|time management|retake|never leave.*blank': '''
<div class="diagram-container"><div class="diagram-title">📝 FCE Exam Quick Reference Card</div><pre>
  FORMAT:                STRATEGY:
  ┌──────────────────┐   ┌─────────────────────────────────┐
  │ 90 minutes       │   │ PASS 1 (60 min): Confident Qs    │
  │ 76 questions     │   │   Mark uncertain, keep moving     │
  │ Multiple choice  │   │                                  │
  │ 70-75% to pass   │   │ PASS 2 (20 min): Marked Qs        │
  │ No penalty/guess │   │   Eliminate 2 wrong, guess       │
  │ Online proctored │   │                                  │
  └──────────────────┘   │ PASS 3 (10 min): Review all      │
                          │   Ensure nothing left blank     │
  5 KEY FORMULAS:         └─────────────────────────────────┘
  ESR = (OnDemand-Actual)/OnDemand × 100
  Coverage = RI+SP/Total × 100
  Unit Cost = Spend/Txns
  Amortized = Payment/Months
  Waste% = Waste/Total × 100
</pre></div>''',

    'saas.*licens|unused.*license|license.*optim': '''
<div class="diagram-container"><div class="diagram-title">📋 SaaS License Optimization Workflow</div><pre>
  AUDIT → RIGHT-SIZE → NEGOTIATE → MONITOR
  ─────   ──────────   ─────────   ───────
  ┌──────────────────────────────────────────────────────┐
  │ 1. Pull SaaS admin console → active vs licensed users│
  │ 2. 30% unused = 30% savings by downgrading tiers     │
  │ 3. Negotiate: commit annual for 20-40% discount      │
  │ 4. SSO integration: auto-deprovision leavers         │
  │ 5. Monthly audit: identify creeping license growth   │
  └──────────────────────────────────────────────────────┘
</pre></div>''',

    'tco|on.prem.*vs.*cloud|on.premises|total cost of ownership': '''
<div class="compare-table"><table><thead><tr><th>Cost Category</th><th>On-Premises</th><th>Cloud (AWS)</th></tr></thead><tbody>
<tr><td>Hardware (servers, racks)</td><td>$45,000 upfront + $5K/yr maintenance</td><td>$0 (pay-per-use)</td></tr>
<tr><td>Staffing (sysadmin, DBA)</td><td>$120,000/yr (1 FTE)</td><td>$30,000/yr (0.25 FTE)</td></tr>
<tr><td>Power/Cooling/Facility</td><td>$12,000/yr</td><td>$0</td></tr>
<tr><td>Compute (EC2 equiv)</td><td>$0 (owned)</td><td>$24,000/yr (RI)</td></tr>
<tr><td>Networking</td><td>$6,000/yr</td><td>$3,600/yr</td></tr>
<tr><td><strong>3-Year TCO</strong></td><td><strong>$231,000</strong></td><td><strong>$82,800</strong></td></tr>
</tbody></table></div>''',

    'consolidated bill|aws organization.*account|management account': '''
<div class="diagram-container"><div class="diagram-title">🏢 AWS Organizations — Consolidated Billing</div><pre>
  MANAGEMENT ACCOUNT (Payer)
  ┌──────────────────────────────────────────────────────┐
  │ • Receives ONE bill for ALL accounts                 │
  │ • RI/SP discounts shared across all accounts         │
  │ • SCPs applied here → cascade to all member accounts │
  │ • Consolidated: volume discounts apply               │
  └──────────────────────────────────────────────────────┘
           │
           ├──▶ Member Account 1 (jobpost-prod)    $5,420
           ├──▶ Member Account 2 (jobpost-staging)  $2,100
           ├──▶ Member Account 3 (search-prod)      $3,100
           ├──▶ ... (up to thousands of accounts)
           └──▶ Member Account 50

  KEY: Tags+Cost Explorer show per-account breakdown even
  though billing is consolidated to one payer account.
</pre></div>''',

    'ml.*cost|training.*cost|inference.*cost|ai.*cost': '''
<div class="diagram-container"><div class="diagram-title">🤖 ML Cost — Training vs Inference</div><pre>
  TRAINING (one-time):                  INFERENCE (ongoing):
  ┌─────────────────────────┐        ┌──────────────────────────────┐
  │ • GPU instances (p4d)   │        │ • CPU or GPU depending on     │
  │ • $32/hr × 100 hrs      │        │   model size                  │
  │ • $3,200 per training   │        │ • $0.0004 per prediction     │
  │ • Run weekly: $166K/yr  │        │ • 1M predictions/day = $400  │
  └─────────────────────────┘        │ • $146,000/year              │
                                      └──────────────────────────────┘

  LONG-TERM: Inference dominates (recurring), but training
  has higher per-hour cost. Optimize BOTH.
</pre></div>''',

    'cds|cloudfront|cdn.*cost|cdn.*affect': '''
<div class="diagram-container"><div class="diagram-title">🌐 CDN Cost Impact — S3 Direct vs CloudFront</div><pre>
  WITHOUT CDN (S3 direct):              WITH CDN (CloudFront):
  ┌────────────────────────┐         ┌──────────────────────────┐
  │ 2TB × $0.09/GB (xfer)  │         │ 2TB × $0.085/GB (CF)    │
  │ = $187.20/month        │         │ = $173.40/month          │
  │                         │         │ + Cache hit ratio: 80%   │
  │ Latency: 50-200ms      │         │ → Only 400GB hits origin │
  │ Origin load: 100%      │         │ → S3 cost: $36/month     │
  └────────────────────────┘         │ TOTAL: ~$209/month        │
                                      │ Latency: 5-20ms          │
  CDN costs slightly MORE but         │ Origin load: 20%         │
  delivers far better UX.             └──────────────────────────┘
</pre></div>''',

    'daemonset.*cost|daemon.*set.*alloc': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">DaemonSet Cost Handling</span></div><pre><code class="language-yaml"># DaemonSets run one pod per node — treated as PLATFORM cost
# NOT allocated to individual teams

# Example: logging-agent DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: logging-agent
  namespace: kube-system
spec:
  template:
    metadata:
      labels:
        cost-allocation: platform  # Kubecost ignores or buckets as shared

# In Kubecost: DaemonSet costs appear under "Platform/Shared"
# Split proportionally across all teams using that node</code></pre></div>''',

    'kubernetes control plane.*cost|eks.*aks.*gke.*compar': '''
<div class="compare-table"><table><thead><tr><th>Provider</th><th>Control Plane Cost</th><th>Key Difference</th></tr></thead><tbody>
<tr><td><strong>AWS EKS</strong></td><td>$0.10/hr = $73/month</td><td>Charges for control plane, free on Fargate-only</td></tr>
<tr><td><strong>Azure AKS</strong></td><td>FREE</td><td>Control plane is free, pay only for worker nodes</td></tr>
<tr><td><strong>GCP GKE</strong></td><td>FREE (1 zonal cluster)</td><td>Free for 1 zonal cluster, pay for >1 or regional</td></tr>
</tbody></table></div>''',

    'pioneer.*finops|netflix.*atlassian|early.*adopter|faced.*challeng': '''
<div class="diagram-container"><div class="diagram-title">🏢 FinOps Origin Story — Why It Was Born</div><pre>
  THE PROBLEM (2012-2015):
  ┌────────────────────────────────────────────────────────────┐
  │ Netflix:  Cloud bill growing 10× YoY, no ownership         │
  │ Atlassian: Engineers spinning up $50K/month of resources   │
  │ Spotify:   No way to map cloud costs to product teams      │
  │                                                            │
  │ COMMON CHALLENGE:                                          │
  │ "Cloud moved CAPEX → OPEX, but NOBODY owned the OPEX."    │
  │ Finance didn't understand cloud pricing.                   │
  │ Engineers didn't care about cost (no accountability).       │
  │ Business couldn't map cost to value.                        │
  └────────────────────────────────────────────────────────────┘

  THE SOLUTION: FinOps — shared ownership model where Finance,
  Engineering, and Business collaborate on cloud spend.
</pre></div>''',

    'larger than xlarge|prevent.*instance.*size|instance.*larger|scp.*prevent': '''
<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">AWS SCP — Block Instances Larger Than xlarge</span></div><pre><code class="language-json">{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyLargeInstances",
    "Effect": "Deny",
    "Action": ["ec2:RunInstances"],
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "StringNotLike": {
        "ec2:InstanceType": [
          "*.nano", "*.micro", "*.small",
          "*.medium", "*.large", "*.xlarge"
        ]
      }
    }
  }]
}
// SCPs apply to: AWS Account, OU, or Root
// They do NOT apply to the Management Account itself
//   (unless you explicitly attach it)</code></pre></div>''',

    'dev.*environment.*runs.*24/7|auto.*shutdown|auto.*remediation.*dev|scale.*to.*0.*night': '''
<div class="diagram-container"><div class="diagram-title">⏰ Auto-Shutdown Architecture for Dev Environments</div><pre>
  WITHOUT AUTO-SHUTDOWN:                  WITH AUTO-SHUTDOWN:
  ┌────────────────────────┐         ┌──────────────────────────┐
  │ Dev: 24/7 × 730 hrs    │         │ Dev: 8AM-8PM × 390 hrs   │
  │ $800/month             │         │ $427/month (Spot)        │
  │ On-Demand rate         │         │                           │
  └────────────────────────┘         │ SAVED: $373/month (47%)  │
                                      └──────────────────────────┘

  IMPLEMENTATION:
  ┌──────────────────────────────────────────────────────────────┐
  │ 1. Lambda (CloudWatch cron: 0 20 * * ? *) — scale to 0      │
  │ 2. Lambda (CloudWatch cron: 0 7 * * ? *)  — scale to 2      │
  │ 3. Kyverno CleanupPolicy: delete test namespaces >7d idle   │
  │ 4. Override: team can add label "skip-shutdown: true"        │
  └──────────────────────────────────────────────────────────────┘
</pre></div>''',

    'eks control plane.*namespace.*allocation|shared.*eks.*split|proportional.*eks': '''
<div class="diagram-container"><div class="diagram-title">📐 EKS Control Plane Proportional Allocation</div><pre>
  SHARED COST: EKS Control Plane = $73/month
  ALLOCATION KEY: % of total pod count per namespace

  ┌────────────────────┬───────────┬──────────────────────────┐
  │ Namespace          │ Pod Count │ Allocation               │
  ├────────────────────┼───────────┼──────────────────────────┤
  │ jobpost-prod (60%) │    120    │ $73 × 0.60 = $43.80/mo  │
  │ jobpost-stag (25%) │     50    │ $73 × 0.25 = $18.25/mo  │
  │ kube-system (15%)  │     30    │ $73 × 0.15 = $10.95/mo  │
  ├────────────────────┼───────────┼──────────────────────────┤
  │ TOTAL              │    200    │ $73.00 ✓                 │
  └────────────────────┴───────────┴──────────────────────────┘

  ALTERNATIVE KEYS: CPU usage %, memory usage %, or even split.
  Rule: pick ONE method, document it, apply consistently.
</pre></div>''',
}

# Process the file
# Find all exam-question-item blocks that need enrichment
question_pattern = re.compile(r'(<div class="exam-question-item">.*?</details>)', re.DOTALL)

def enrich_block(match):
    global enriched_count
    block = match.group(1)
    
    # Skip if already has visual enrichment
    if has_visual(block):
        return block
    
    # Check which template matches
    block_lower = block.lower()
    for keyword_pattern, visual_html in templates.items():
        if re.search(keyword_pattern, block_lower):
            enriched_count += 1
            # Inject the visual before </details>
            return block.replace('</details>', visual_html + '\n</details>', 1)
    
    return block

# Apply enrichment
new_content = question_pattern.sub(enrich_block, content)

print(f'Enriched {enriched_count} Q&A blocks with visual elements')

# Write back
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('File updated successfully.')
