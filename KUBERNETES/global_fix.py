"""Global fix for remaining mismatched templates in section content."""
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'r', encoding='utf-8').read()

# Just replace the code-block titles directly - they're in section content, not QA
fixes = 0

# Replace Rightsizing Check blocks
old_rw = '<span class="code-lang">Rightsizing Check — kubectl top + describe</span><pre><code class="language-bash"># Check actual resource usage (metrics-server required)\nkubectl top pods -n jobpost-prod\n\n# Check requested vs actual (VPA Recommender)\nkubectl get vpa anihpj-web-vpa -n jobpost-prod -o yaml\n# Look for: recommendation.target.cpu, recommendation.target.memory\n\n# AWS Compute Optimizer (EC2-level rightsizing)\naws compute-optimizer get-ec2-instance-recommendations   --instance-arns arn:aws:ec2:us-east-1:123456789:instance/i-0a3f</code></pre></div>'

new_rw = '<div class="diagram-container"><div class="diagram-title">Rightsizing Strategy — Measure, Analyze, Optimize</div><pre>\n  STEP 1: MEASURE — 14-30 days of P95 CPU/Memory usage (VPA Recommender, Compute Optimizer)\n  STEP 2: ANALYZE — Compare P95 actual vs provisioned. Identify overprovisioned resources.\n  STEP 3: RIGHT-SIZE — Reduce requests to P95 + 25% buffer. Limits = 2× requests.\n  STEP 4: VALIDATE — Monitor for 1 week in staging before production rollout.\n\n  anihpj EXAMPLE: Web pod request 2 CPU → 0.4 CPU (P95=0.3, +25% buffer)\n  7 pods fit per node instead of 2 → 67% fewer nodes → $828/month savings\n</pre></div>'

count_rw = c.count(old_rw)
c = c.replace(old_rw, new_rw)
fixes += count_rw
print(f'Replaced {count_rw} Rightsizing Check blocks')

# Replace Kubecost Quick Start blocks
old_kc = '<span class="code-lang">Kubecost Quick Start &amp; Cost Query</span><pre><code class="language-bash"># Install Kubecost\nhelm repo add kubecost https://kubecost.github.io/cost-analyzer/\nhelm install kubecost kubecost/cost-analyzer -n kubecost --create-namespace\n\n# Query costs by namespace\nkubectl port-forward svc/kubecost-cost-analyzer 9090 -n kubecost\ncurl -G http://localhost:9090/model/costData \\\n  --data-urlencode \'window=month\' \\\n  --data-urlencode \'aggregate=namespace\'</code></pre></div>'

new_kc = '<div class="diagram-container"><div class="diagram-title">Kubecost — Real-Time K8s Cost Visibility</div><pre>\n  INSTALL: helm upgrade --install kubecost kubecost/cost-analyzer --namespace kubecost --create-namespace\n  DASHBOARD: kubectl port-forward svc/kubecost-cost-analyzer 9090 -n kubecost → http://localhost:9090\n  FEATURES: Cost by namespace, deployment, pod, label. Savings insights. Rightsizing recommendations.\n  COST: Free for single-cluster. Enterprise: additional features, SSO, multi-cluster support.\n  anihpj: Kubecost identified $3,200/month of optimization opportunities on first install.\n</pre></div>'

count_kc = c.count(old_kc)
c = c.replace(old_kc, new_kc)
fixes += count_kc
print(f'Replaced {count_kc} Kubecost Quick Start blocks')

# Also handle unescaped ampersand version
old_kc2 = old_kc.replace('&amp;', '&')
count_kc2 = c.count(old_kc2)
c = c.replace(old_kc2, new_kc)
fixes += count_kc2
print(f'Replaced {count_kc2} unescaped Kubecost blocks')

print(f'Total fixes: {fixes}')

# Final verification
print(f'Rightsizing Check remaining: {c.count("Rightsizing Check — kubectl")}')
print(f'Kubecost Quick Start remaining: {c.count("Kubecost Quick Start")}')

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Saved.')
