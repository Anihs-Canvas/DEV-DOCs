"""Bulk-enrich thin section-block content with relevant visual elements."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

enriched = 0

# Template map: keyword_pattern -> visual HTML to inject after the paragraph
templates = [
    # ---- Ch 5: Cost Allocation ----
    ('K8s.*cost.*challeng|shared.*node|shared.*cluster',
     '''<div class="diagram-container"><div class="diagram-title">Shared-Node K8s Cost Challenge</div><pre>
  VM MODEL (Simple):                    K8s MODEL (Complex):
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510          \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 VM-1 \u2192 Team A \u2192 $100    \u2502          \u2502 Node-1 ($138):          \u2502
  \u2502 VM-2 \u2192 Team B \u2192 $100    \u2502          \u2502   Pod-A(Team-A) 40%=$55 \u2502
  \u2502 VM-3 \u2192 Team C \u2192 $100    \u2502          \u2502   Pod-B(Team-B) 30%=$41 \u2502
  \u2502 Direct 1:1 mapping      \u2502          \u2502   Pod-C(Team-C) 20%=$28 \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518          \u2502   Idle         10%=$14 \u2502
                                   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  TOOL NEEDED: Kubecost to map pod\u2192node\u2192team\u2192cost
</pre></div>'''),

    ('namespace.*allocation|namespace.*based|namespace.*cost boundary',
     '''<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Namespace with Cost Allocation Labels</span></div><pre><code class="language-yaml">apiVersion: v1
kind: Namespace
metadata:
  name: jobpost-prod
  labels:
    team: jobpost-team
    cost-center: "1500-IT-ENG"
    environment: prod
    application: anihpj</code></pre></div>'''),

    ('label.*allocation|annotation.*allocation|k8s label',
     '''<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Pod with Cost Labels for Granular Tracking</span></div><pre><code class="language-yaml">apiVersion: v1
kind: Pod
metadata:
  name: anihpj-web-7d4f
  labels:
    component: web
    team: jobpost-team
    cost-tier: production
    version: v2.1</code></pre></div>'''),

    ('kubecost.*opencost|opencost|kubecost',
     '''<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Kubecost Quick Start & Cost Query</span></div><pre><code class="language-bash"># Install Kubecost
helm repo add kubecost https://kubecost.github.io/cost-analyzer/
helm install kubecost kubecost/cost-analyzer -n kubecost --create-namespace

# Query costs by namespace
kubectl port-forward svc/kubecost-cost-analyzer 9090 -n kubecost
curl -G http://localhost:9090/model/costData \\
  --data-urlencode 'window=month' \\
  --data-urlencode 'aggregate=namespace'</code></pre></div>'''),

    ('proportional.*usage|proportional.*split|based on usage',
     '''<div class="diagram-container"><div class="diagram-title">Proportional Allocation Calculation</div><pre>
  SHARED COST: $73/month (EKS Control Plane)
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u252c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u252c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Team    \u2502 Pods  \u2502 Allocation = $73 x Pod%        \u2502
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u253c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u253c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
  \u2502 Team A  \u2502 40%  \u2502 $73 x 0.40 = $29.20/mo       \u2502
  \u2502 Team B  \u2502 30%  \u2502 $73 x 0.30 = $21.90/mo       \u2502
  \u2502 Team C  \u2502 20%  \u2502 $73 x 0.20 = $14.60/mo       \u2502
  \u2502 Team D  \u2502 10%  \u2502 $73 x 0.10 =  $7.30/mo       \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
</pre></div>'''),

    ('fixed.*even.*split|split equally',
     '''<div class="diagram-container"><div class="diagram-title">Fixed vs Proportional Allocation Comparison</div><pre>
  $500 Monitoring Tool — 5 Teams:
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u252c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 FIXED SPLIT        \u2502 Amount  \u2502
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u253c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
  \u2502 Each team pays      \u2502 $100    \u2502
  \u2502 Simple but unfair   \u2502 (500/5) \u2502
  \u2502 for unequal usage   \u2502         \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  Use only when all teams benefit equally.
</pre></div>'''),

    ('unallocated.*bucket|unallocated.*problem|untagged',
     '''<div class="diagram-container"><div class="diagram-title">Unallocated Cost Reduction Targets</div><pre>
  MATURITY TARGETS:
  Crawl: <20% unallocated  \u2502  Walk: <10%  \u2502  Run: <5%  \u2502  Elite: <2%

  REDUCTION ACTIONS:
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u252c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 1. Audit untagged  \u2502 Tag retroactively via AWS Tag Editor    \u2502
  \u2502 2. Enforce tags    \u2502 SCP + Kyverno policies at creation time  \u2502
  \u2502 3. Document splits \u2502 For truly shared costs, be consistent    \u2502
  \u2502 4. Monitor monthly \u2502 Track % unallocated as a KPI           \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
</pre></div>'''),

    ('showback.*inform|showback.*without.*bill',
     '''<div class="diagram-container"><div class="diagram-title">Showback Flow — Inform Without Billing</div><pre>
  Cloud Costs \u2192 Allocation Engine \u2192 Dashboard \u2192 Team Views
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 AWS CUR  \u2502\u2500\u2500\u2500\u2516\u2502 Kubecost \u2502\u2500\u2500\u2500\u2516\u2502 "FYI:    \u2502
  \u2502 (raw)    \u2502   \u2502 (mapped)\u2502   \u2502  Your team\u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2502  cost:   \u2502
                                  \u2502  $5,420" \u2502
                                  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  NO budget hit \u2714  Builds awareness \u2714  Zero resistance \u2714
</pre></div>'''),

    ('chargeback.*bill|actually.*bill|chargeback.*deduct',
     '''<div class="diagram-container"><div class="diagram-title">Chargeback Flow — Actually Bill Teams</div><pre>
  Cloud Costs \u2192 Allocation \u2192 Team Budget \u2192 Auto-Deduction
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 $5,420  \u2502\u2500\u2500\u2500\u2516\u2502 jobpost- \u2502\u2500\u2500\u2500\u2516\u2502 Budget:  \u2502
  \u2502 spend   \u2502   \u2502 team    \u2502   \u2502 $5,500  \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2502 -$5,420\u2502
                                  \u2502 =$80   \u2502
                                  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  PREREQ: >95% allocation accuracy, team trust, documented methodology
</pre></div>'''),

    ('maturity.*stage|choosing.*model|maturity.*matter',
     '''<div class="compare-table"><table><thead><tr><th>Stage</th><th>Model</th><th>Accuracy Needed</th><th>Key Activity</th></tr></thead><tbody>
<tr><td>Crawl (0-6mo)</td><td>Showback only</td><td>80%+</td><td>Build visibility, monthly reports</td></tr>
<tr><td>Walk (6-18mo)</td><td>Hybrid (Show+Charge)</td><td>90%+</td><td>Tag enforcement, anomaly detection</td></tr>
<tr><td>Run (18mo+)</td><td>Full Chargeback</td><td>95%+</td><td>Automated cost gates, CI/CD integration</td></tr>
</tbody></table></div>'''),

    # ---- Ch 6: Dashboards & KPIs ----
    ('good.*dashboard|makes a good.*dashboard',
     '''<div class="diagram-container"><div class="diagram-title">Dashboard Design Principles</div><pre>
  \u2714 PERSONA-SPECIFIC    \u2714 ACTIONABLE         \u2714 TIMELY          \u2714 CONTEXTUAL
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Exec: 6 KPIs  \u2502 \u2502 Shows what    \u2502 \u2502 Daily refresh\u2502 \u2502 Trends, not  \u2502
  \u2502 Eng: per-pod  \u2502 \u2502 to DO about   \u2502 \u2502 at minimum   \u2502 \u2502 just numbers \u2502
  \u2502 Finance:budget\u2502 \u2502 the numbers    \u2502 \u2502 (Walk stage)  \u2502 \u2502 MoM, QoQ     \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
</pre></div>'''),

    ('engineering dashboard|per.service.*cost|per.team.*cost',
     '''<div class="diagram-container"><div class="diagram-title">Engineering Dashboard — anihpj Per-Deployment View</div><pre>
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Deployment        Monthly    Daily Trend    Recommendation     \u2502
  \u2502 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2502
  \u2502 anihpj-web        $890      \u25b25%         Rightsize 2CPU\u21920.5   \u2502
  \u2502 anihpj-worker     $340      \u2192 steady      Set resource limits  \u2502
  \u2502 postgres-prod     $69       \u2192 steady      Review RI purchase   \u2502
  \u2502 redis-cache       $28       \u2192 steady      Consider Spot       \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
</pre></div>'''),

    ('finance dashboard|budget.*actual|budget.*forecast',
     '''<div class="diagram-container"><div class="diagram-title">Finance Dashboard — Budget Variance Report</div><pre>
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Budget: $15,000    Actual (MTD): $10,200     Days: 20/30 (67%)\u2502
  \u2502 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2502
  \u2502 jobpost-team:    $5,420/$5,500  \u2714 ON TRACK           \u2502
  \u2502 search-team:     $3,100/$4,000  \u2714 UNDER              \u2502
  \u2502 platform-team:   $4,200/$3,500  \u26a0 OVER ($700)       \u2502
  \u2502 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \u2502
  \u2502 FORECAST (month-end): $15,300 (102% of budget)        \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
</pre></div>'''),

    # ---- Ch 7: Optimization ----
    ('rightsizing.*don.*pay|rightsizing.*#1|overprovision.*problem',
     '''<div class="diagram-container"><div class="diagram-title">The Overprovisioning Tax — Visualized</div><pre>
  PROVISIONED:  \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 100% ($150/mo)
  ACTUAL USE:  \u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591 18%  ($27 of value)
  WASTED:      \u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591 82%  ($123 burned/mo)
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  anihpj: 12 overprovisioned nodes x $123 = $1,476/month wasted
</pre></div>'''),

    ('cpu.*memory.*analysis|finding.*overprovision|p95.*utilization',
     '''<div class="code-block-wrapper"><div class="code-block-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">Find Overprovisioned Resources</span></div><pre><code class="language-bash"># Check actual pod resource usage
kubectl top pods -n jobpost-prod --containers

# Check VPA recommendations (Off mode — no auto-changes)
kubectl get vpa -n jobpost-prod -o json | \\
  jq '.items[].status.recommendation'

# AWS Compute Optimizer — instance-level recommendations
aws compute-optimizer get-ec2-instance-recommendations</code></pre></div>'''),

    ('rightsizing process|measure.*analyze.*right.size.*validate',
     '''<div class="diagram-container"><div class="diagram-title">The Rightsizing Process — 4 Steps</div><pre>
  MEASURE           ANALYZE           RIGHT-SIZE        VALIDATE
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 14 days\u2502\u2500\u2500\u2516\u2502 P95 of   \u2502\u2500\u2500\u2516\u2502 Reduce  \u2502\u2500\u2500\u2516\u2502 Monitor \u2502
  \u2502 of data\u2502   \u2502 actual  \u2502   \u2502 request\u2502   \u2502 48-72h\u2502
  \u2502 (VPA)  \u2502   \u2502 usage   \u2502   \u2502 +30-50%\u2502   \u2502 for    \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518   \u2502 safety \u2502
                                        \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  NEVER: Guess. ALWAYS: Use 14+ days of actual P95 data.
</pre></div>'''),

    ('just in case.*anti.pattern|psychology.*overprovision',
     '''<div class="diagram-container"><div class="diagram-title">The "Just in Case" Anti-Pattern</div><pre>
  ENGINEER THINKS:           REALITY:
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 "What if we get    \u2502    \u2502 Actual usage:     \u2502
  \u2502  SLASHED on HN?"   \u2502    \u2502 12-18% of request \u2502
  \u2502                    \u2502    \u2502                    \u2502
  \u2502 Request: 4 CPU     \u2502    \u2502 Need: 0.5 CPU      \u2502
  \u2502 (just in case!)    \u2502    \u2502 8x overprovisioned\u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  FIX: Use HPA for spikes, not overprovisioning.
</pre></div>'''),

    ('standard ri.*convertible|standard.*vs.*convertible',
     '''<div class="compare-table"><table><thead><tr><th>Feature</th><th>Standard RI</th><th>Convertible RI</th></tr></thead><tbody>
<tr><td>Discount</td><td>40-60%</td><td>30-45%</td></tr>
<tr><td>Instance flexibility</td><td>Locked to family</td><td>Can exchange families</td></tr>
<tr><td>Marketplace resale</td><td>Yes</td><td>No</td></tr>
<tr><td>Best for</td><td>Stable, known workloads</td><td>Planned migrations</td></tr></tbody></table></div>'''),

    ('staggered.*purchase|reservation.*portfolio|don.*buy.*all',
     '''<div class="diagram-container"><div class="diagram-title">Staggered RI/SP Purchase Strategy</div><pre>
  Month 0:  Buy 33% of baseline (1yr)     Coverage: 33%
  Month 4:  Buy 33% of baseline (1yr)     Coverage: 66%
  Month 8:  Buy 34% of baseline (1yr)     Coverage: 100%
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  At Month 12: First batch expires, re-evaluate before renewing.

  WHY: Avoids locking in for overprovisioned baselines.
  Allows rightsizing between batches. Reduces stranded risk.
</pre></div>'''),

    ('spot.*how.*work|2.minute.*warning|rebalancing',
     '''<div class="diagram-container"><div class="diagram-title">Spot Instance Lifecycle — 2-Minute Warning</div><pre>
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510     \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510     \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 RUNNING (60-90%  \u2502\u2500\u2500\u2500\u2516\u2502 2-MIN WARNING \u2502\u2500\u2500\u2500\u2516\u2502 TERMINATED    \u2502
  \u2502 off On-Demand)   \u2502   \u2502 Spot reclaims \u2502   \u2502 Graceful      \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518     \u2502 instance   \u2502     \u2502 shutdown      \u2502
                        \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518     \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  BEST FOR: Stateless workloads, batch jobs, CI/CD, dev/staging.
  NOT FOR: Stateful databases, latency-sensitive production.
</pre></div>'''),
]

def should_enrich(section_id, section_html):
    """Check if a section is thin (needs enrichment)."""
    # Skip if already has visual elements
    visuals = ['<table', '<pre>', 'diagram-container', 'code-block-wrapper', 
               'card-grid', 'compare-table', 'info-box', 'scenario-box']
    existing = sum(1 for v in visuals if v in section_html)
    if existing > 1:
        return False
    # Must have at least one paragraph
    if '<p>' not in section_html:
        return False
    return True

# Process each thin section
sections = re.finditer(
    r'(<div class="section-block" id="([^"]+)">)(.*?)(?=<div class="section-block"|<div class="fce-exam-questions"|<!-- Ch.*?Visual Summary -->)',
    content, re.DOTALL
)

# Build a list of replacements
replacements = []
for m in sections:
    full_match = m.group(0)
    sec_id = m.group(2)
    sec_content = m.group(3)
    
    if not should_enrich(sec_id, sec_content):
        continue
    
    # Find best matching template
    for pattern, visual_html in templates:
        if re.search(pattern, sec_content, re.IGNORECASE):
            # Inject visual after first paragraph
            first_p_end = sec_content.find('</p>')
            if first_p_end > 0:
                new_content = sec_content[:first_p_end+4] + '\n' + visual_html + sec_content[first_p_end+4:]
                replacements.append((full_match, m.group(1) + new_content))
                enriched += 1
            break

print(f'Found {enriched} sections to enrich')
for old, new in replacements:
    if old in content:
        content = content.replace(old, new, 1)
    else:
        print(f'  WARNING: Could not find match for section')

with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Applied {enriched} enrichments. File saved.')
