"""Add edge-case exam content for 95%+ readiness."""
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'r', encoding='utf-8').read()

# Add edge-case scenario content before Ch 14 Q&A
# Compliance exception scenarios, negative ROI judgment calls, multi-cloud edge cases

# Find the Ch 14 Q&A section
qa_pos = c.find('Chapter 14 — FCE Practice Questions')
if qa_pos > 0:
    div_pos = c.rfind('<div class="fce-exam-questions"', 0, qa_pos)
    edge_content = '''<div class="scenario-box positive">
<h5>🎯 Pushing to 95%+ — Edge Cases That Separate Pass from Excellence</h5>
<ul>
<li><strong>Compliance Override:</strong> A project has -50% ROI but is required for SOC2 compliance. Do you proceed? YES — regulatory requirements override financial ROI. The FCE exam tests judgment, not just math.</li>
<li><strong>Spot in Production:</strong> "Should we use Spot for production?" Answer: Yes, but only for STATELESS, HORIZONTALLY-SCALED services with graceful shutdown handling. NEVER for stateful databases or single-point-of-failure services.</li>
<li><strong>Chargeback Without Perfect Data:</strong> "Allocation is only 88% accurate. Can we do chargeback?" No — chargeback requires >95% accuracy. Continue with showback until accuracy improves.</li>
<li><strong>Multi-Cloud for 50 Engineers:</strong> "Should a 50-person startup go multi-cloud?" Almost certainly NO — operational overhead exceeds any theoretical savings or resilience benefits at this scale.</li>
<li><strong>RI vs SP for RDS:</strong> "Should I buy Savings Plans for RDS?" NO — SP covers compute (EC2, Lambda, Fargate) but NOT RDS. RDS requires Reserved Instances specifically.</li>
<li><strong>Enterprise Discount vs SP:</strong> "We have an EDP. Do we still need SP?" YES — EDP is a volume discount ON TOP of SP/RI. They stack. EDP alone is typically 3-5%; SP adds 28-72% on top.</li>
</ul>
</div>
'''
    c = c[:div_pos] + edge_content + '\n' + c[div_pos:]

# Add regulatory/compliance section to Ch 12 (Governance)
gov_pos = c.find('id="s12-5"')
if gov_pos > 0:
    # Find end of s12-5
    next_sec = c.find('<div class="section-block"', gov_pos + 50)
    compliance_content = '''
            <div class="section-block" id="s12-6">
                <h3>12.6 Compliance & Regulatory Considerations for FinOps</h3>
                <p>FinOps automation must operate within regulatory boundaries. Key considerations for the FCE exam:</p>
                <div class="diagram-container"><div class="diagram-title">FinOps + Compliance — The Guardrails</div><pre>
  DATA RESIDENCY: Auto-shutdown scripts must respect data sovereignty (don't move EU data to US)
  AUDIT TRAILS: All automated cost actions must be logged (CloudTrail, Azure Monitor)
  ACCESS CONTROL: Cost tools need least-privilege IAM (read-only for dashboards, write for automation)
  SOC2/HIPAA: Cost optimization cannot compromise security controls (encryption, access logs)
  FEDRAMP: Some US gov workloads CANNOT use Spot or certain regions — FinOps must adapt
</pre></div>
                <p><strong>FCE Exam Tip:</strong> When a scenario involves regulated workloads, the correct answer always prioritizes compliance over cost optimization. "Use Spot to save 60% on this HIPAA workload" is WRONG if it compromises data protection. The exam tests your ability to balance optimization with regulatory requirements.</p>
            </div>
'''
    c = c[:next_sec] + compliance_content + c[next_sec:]

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Edge cases + compliance section added.')
