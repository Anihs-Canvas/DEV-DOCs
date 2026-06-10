#!/usr/bin/env python3
"""
Comprehensive fix: Replace all 19 mismatched templates in finOps_eng.html
- 8 "Rightsizing Check — kubectl top + describe" in non-K8s chapters → cloud-agnostic
- 11 "Kubecost Quick Start & Cost Query" in non-K8s chapters → FinOps tools
Uses EXACT string matching confirmed from the file.
"""

import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html"

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

rs_count = 0
kc_count = 0

# ── RIGHTSIZING CHECK replacement ──
# Exact block confirmed from file (line 8008)
old_rs = (
    '<div class="code-block-wrapper"><div class="code-block-header">'
    '<span class="code-dot red"></span><span class="code-dot yellow"></span>'
    '<span class="code-dot green"></span>'
    '<span class="code-lang">Rightsizing Check — kubectl top + describe</span></div>'
    '<pre><code class="language-bash"># Check actual resource usage (metrics-server required)\n'
    'kubectl top pods -n jobpost-prod\n\n'
    '# Check requested vs actual (VPA Recommender)\n'
    'kubectl get vpa anihpj-web-vpa -n jobpost-prod -o yaml\n'
    '# Look for: recommendation.target.cpu, recommendation.target.memory\n\n'
    '# AWS Compute Optimizer (EC2-level rightsizing)\n'
    'aws compute-optimizer get-ec2-instance-recommendations'
    '   --instance-arns arn:aws:ec2:us-east-1:123456789:instance/i-0a3f'
    '</code></pre></div>'
)

new_rs = (
    '<div class="code-block-wrapper"><div class="code-block-header">'
    '<span class="code-dot red"></span><span class="code-dot yellow"></span>'
    '<span class="code-dot green"></span>'
    '<span class="code-lang">Rightsizing Check — Multi-Cloud Quick Audit</span></div>'
    '<pre><code class="language-bash"># AWS: Find underutilized EC2 instances (CPU < 20% over 14 days)'
    '\naws compute-optimizer get-ec2-instance-recommendations \\\n'
    '  --filters "[{\\"name\\":\\"Finding\\",\\"values\\":[\\"Overprovisioned\\"]}]"'
    '\n\n# Azure: List VM resize recommendations'
    '\naz advisor recommendation list --category Cost --query "[?impactedField==\'Microsoft.Compute/virtualMachines\']"'
    '\n\n# GCP: Get rightsizing recommendations'
    '\ngcloud recommender recommendations list --recommender=google.compute.instance.MachineTypeRecommender \\\n'
    '  --project=anihpj --location=us-central1-a'
    '\n\n# K8s: Check pod resource usage (metrics-server required)'
    '\nkubectl top pods -n jobpost-prod</code></pre></div>'
)

while old_rs in content:
    content = content.replace(old_rs, new_rs, 1)
    rs_count += 1

print(f"Replaced {rs_count} Rightsizing Check blocks")

# ── KUBECOST QUICK START replacement ──
old_kc = (
    '<div class="code-block-wrapper"><div class="code-block-header">'
    '<span class="code-dot red"></span><span class="code-dot yellow"></span>'
    '<span class="code-dot green"></span>'
    '<span class="code-lang">Kubecost Quick Start & Cost Query</span></div>'
    '<pre><code class="language-bash"># Install Kubecost\n'
    'helm repo add kubecost https://kubecost.github.io/cost-analyzer/\n'
    'helm install kubecost kubecost/cost-analyzer -n kubecost --create-namespace\n\n'
    '# Query costs by namespace\n'
    'kubectl port-forward svc/kubecost-cost-analyzer 9090 -n kubecost\n'
    'curl -G http://localhost:9090/model/costData \\\n'
    '  --data-urlencode \'window=month\' \\\n'
    '  --data-urlencode \'aggregate=namespace\''
    '</code></pre></div>'
)

new_kc = (
    '<div class="code-block-wrapper"><div class="code-block-header">'
    '<span class="code-dot red"></span><span class="code-dot yellow"></span>'
    '<span class="code-dot green"></span>'
    '<span class="code-lang">FinOps Cost Visibility — Multi-Cloud Quick Start</span></div>'
    '<pre><code class="language-bash"># AWS: Enable Cost Explorer + create budget alert'
    '\naws ce update-cost-allocation-tags-status \\\n'
    '  --cost-allocation-tags-status "TagKeys=[Environment,Team,Application,CostCenter]"'
    '\naws budgets create-budget --account-id 123456789 \\\n'
    '  --budget \'{"BudgetName":"monthly","BudgetLimit":{"Amount":"15000","Unit":"USD"},"TimeUnit":"MONTHLY"}\''
    '\n\n# Azure: Enable cost export + set budget'
    '\naz costmanagement export create --name "monthly-export" \\\n'
    '  --type ActualCost --timeframe MonthToDate --storage-container "cost-data"'
    '\n\n# GCP: Export billing to BigQuery'
    '\ngcloud beta billing budgets create --billing-account=XXXXXX-XXXXXX-XXXXXX \\\n'
    '  --display-name="monthly-budget" --budget-amount=15000USD'
    '\n\n# K8s (optional): Install Kubecost for pod-level visibility'
    '\nhelm repo add kubecost https://kubecost.github.io/cost-analyzer/'
    '\nhelm install kubecost kubecost/cost-analyzer -n kubecost --create-namespace'
    '</code></pre></div>'
)

while old_kc in content:
    content = content.replace(old_kc, new_kc, 1)
    kc_count += 1

print(f"Replaced {kc_count} Kubecost Quick Start blocks")

# Write back
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n=== Summary ===")
print(f"Rightsizing Check: {rs_count} replaced")
print(f"Kubecost Quick Start: {kc_count} replaced")
print(f"Total fixes: {rs_count + kc_count}")

# Verify
with open(FILE, 'r', encoding='utf-8') as f:
    final = f.read()

rs_remaining = final.count('Rightsizing Check — kubectl top + describe')
kc_remaining = final.count('Kubecost Quick Start & Cost Query')
print(f"\n=== Verification ===")
print(f"Rightsizing Check remaining: {rs_remaining}")
print(f"Kubecost Quick Start remaining: {kc_remaining}")
print("ALL CLEAN!" if rs_remaining == 0 and kc_remaining == 0 else f"Still have {rs_remaining + kc_remaining} left")
