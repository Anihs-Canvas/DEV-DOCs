"""Fix Ch 16 domain headers — inject intro paragraphs + diagrams."""
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'r', encoding='utf-8').read()

domain_intros = {
    's16-1': ('<p>Domain 1 covers foundational concepts. Weight: <strong>20%</strong> (~15 Qs). Master the 6 Principles (COBALT), Crawl-Walk-Run maturity, and stakeholder collaboration.</p>\n<div class="diagram-container"><div class="diagram-title">Domain 1 Quick Reference</div><pre>\n  Weight: 20% (~15 Qs) | COBALT: Collaboration, Ownership, Business, Accessibility, Lean, Transparency\n  Maturity: Crawl (visibility) -> Walk (optimization) -> Run (automation)\n</pre></div>\n'),
    's16-2': ('<p>The heaviest domain at <strong>26%</strong> (~20 Qs). Tests pricing models, CUR, amortization, ESR/coverage formulas, and forecasting. Expect 2-3 calculation questions.</p>\n<div class="diagram-container"><div class="diagram-title">Domain 2 Quick Reference</div><pre>\n  Weight: 26% (~20 Qs) | Formulas: ESR, Coverage, Amortized Cost, Unit Cost\n  Know when to use amortized vs unblended costs in different scenarios.\n</pre></div>\n'),
    's16-3': ('<p>Weight: <strong>14%</strong> (~11 Qs). Tests tagging taxonomy, shared cost allocation, showback vs chargeback, and K8s allocation challenges.</p>\n<div class="diagram-container"><div class="diagram-title">Domain 3 Quick Reference</div><pre>\n  Weight: 14% (~11 Qs) | Allocation: Proportional > Fixed > Direct\n  Chargeback requires: >95% accuracy, team trust, documented methodology\n</pre></div>\n'),
    's16-4': ('<p>Weight: <strong>22%</strong> (~17 Qs). Tests rightsizing, RI/SP strategy, Spot, autoscaling, and K8s optimization. Know the ORDER: Rightsize -> Reserve -> Spot.</p>\n<div class="diagram-container"><div class="diagram-title">Domain 4 Quick Reference</div><pre>\n  Weight: 22% (~17 Qs) | Order: Rightsize -> Reserve -> Spot -> Autoscale\n  K8s: Pod requests drive node count. Rightsize requests first.\n</pre></div>\n'),
    's16-5': ('<p>Weight: <strong>18%</strong> (~14 Qs). Tests Policy-as-Code, CI/CD cost gates, automated remediation, SaaS FinOps, and the 3-layer control framework.</p>\n<div class="diagram-container"><div class="diagram-title">Domain 5 Quick Reference</div><pre>\n  Weight: 18% (~14 Qs) | Controls: Preventive (block) -> Detective (alert) -> Corrective (fix)\n  Tools: SCP, Azure Policy, Kyverno, Infracost, Lambda auto-remediation\n</pre></div>\n'),
}

for sec_id, intro in domain_intros.items():
    id_pos = c.find(f'id="{sec_id}"')
    if id_pos == -1: continue
    # Find the h3 close
    h3_end = c.find('</h3>', id_pos)
    if h3_end == -1: continue
    # Insert content right after </h3>\n
    c = c[:h3_end + 5] + '\n' + intro + c[h3_end + 5:]
    print(f'OK: {sec_id}')

open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'w', encoding='utf-8').write(c)
print('Saved.')
