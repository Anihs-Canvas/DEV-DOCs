"""Fix remaining Ch 18 mismatched Q&A enrichments using exact file content."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

m18_start = content.find('id="ch18"')
m19_start = content.find('id="ch19"')
ch18 = content[m18_start:m19_start]

# Fix Q2
old_q2 = """<div class="diagram-container"><div class="diagram-title">\u2011\u20e3 FinOps Stakeholders & Personas</div><pre>
  FINOPS PRACTITIONER (You!)
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Bridges Finance + Engineering + Business               \u2502"""

# Search for it in Ch 18
if "FinOps Stakeholders" in ch18:
    # Find exact boundaries
    pos = ch18.find("FinOps Stakeholders")
    # Find the diagram div start
    start = ch18.rfind('<div class="diagram-container">', 0, pos)
    # Find end marker
    end = ch18.find('</details></div>', pos)
    end = ch18.find('</pre></div>', pos) + len('</pre></div>')
    
    new_q2 = """<div class="diagram-container"><div class="diagram-title">IAAS Visibility vs SaaS Blind Spot</div><pre>
  IAAS COSTS (Visible):                   SAAS COSTS (Invisible):
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510    \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 AWS CUR \u2192 Cost Explorer      \u2502    \u2502 Salesforce: $150/mo (card)   \u2502
  \u2502 Every EC2 instance tracked    \u2502    \u2502 Datadog: $800/mo (invoice)   \u2502
  \u2502 Tagged, allocated, daily      \u2502    \u2502 Slack: $640/mo (80 users)    \u2502
  \u2502 Anomaly detection active      \u2502    \u2502 NO cloud bill visibility     \u2502
  \u2502                               \u2502    \u2502 Found via expense reports    \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518    \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518

  SOLUTION: SMP tools (Zylo, BetterCloud) + SSO logs feed into
  unified Total Technology Cost dashboard.
</pre></div>"""
    content = content[:m18_start] + ch18[:start] + new_q2 + ch18[end:] + content[m19_start:]
    print('Q2 fixed')
else:
    print('Q2: "FinOps Stakeholders" not found')

# Re-extract
ch18 = content[m18_start:m19_start]

# Fix Q5: ML Cost diagram
if "ML Cost — Training vs Inference" in ch18:
    pos = ch18.find("ML Cost — Training vs Inference")
    start = ch18.rfind('<div class="diagram-container">', 0, pos)
    end = ch18.find('</pre></div>', pos) + len('</pre></div>')
    
    new_q5 = """<div class="diagram-container"><div class="diagram-title">Managed vs Self-Managed Decision Framework</div><pre>
  MANAGED WINS WHEN:                      SELF-MANAGE WINS WHEN:
  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
  \u2502 Premium < 2 hrs engineering  \u2502  \u2502 Premium >$500/mo per unit   \u2502
  \u2502 Team < 500 engineers         \u2502  \u2502 1,000+ instances (scale)    \u2502
  \u2502 No specialized in-house skill\u2502  \u2502 Dedicated DB/Redis team     \u2502
  \u2502 Standard configuration needs \u2502  \u2502 Custom requirements needed  \u2502
  \u2502 Compliance handled by vendor \u2502  \u2502 Full control required       \u2502
  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518

  DECISION FORMULA:
  Self-Managed Total = Cloud Cost + (Engineer Hours x $150/hr)
  IF Self-Managed > Managed Cost -> USE MANAGED
</pre></div>"""
    content = content[:m18_start] + ch18[:start] + new_q5 + ch18[end:] + content[m19_start:]
    print('Q5 fixed')
else:
    print('Q5: "ML Cost" not found')

# Re-extract
ch18 = content[m18_start:m19_start]

# Fix Q7: Kubecost block
if "Kubecost — Install" in ch18:
    pos = ch18.find("Kubecost — Install")
    start = ch18.rfind('<div class="code-block-wrapper">', 0, pos)
    end = ch18.find('</code></pre></div>', pos) + len('</code></pre></div>')
    
    new_q7 = """<div class="compare-table"><table><thead><tr><th>Category</th><th>What It Does</th><th>Example Tools</th><th>Cloud Parallel</th></tr></thead><tbody><tr><td><strong>SaaS Mgmt Platform</strong></td><td>Discover, manage, optimize SaaS</td><td>Zylo, BetterCloud, Torii</td><td>CloudHealth, Kubecost</td></tr><tr><td><strong>Procurement</strong></td><td>Negotiate, purchase, renew</td><td>Vendr, Tropic</td><td>RI/SP marketplace</td></tr><tr><td><strong>Expense Mgmt</strong></td><td>Track spend via cards</td><td>Ramp, Brex</td><td>AWS Budgets</td></tr><tr><td><strong>SSO/Identity</strong></td><td>Discovery source</td><td>Okta, Azure AD</td><td>CloudTrail</td></tr></tbody></table></div>"""
    content = content[:m18_start] + ch18[:start] + new_q7 + ch18[end:] + content[m19_start:]
    print('Q7 fixed')
else:
    print('Q7: "Kubecost" not found')

with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved.')
