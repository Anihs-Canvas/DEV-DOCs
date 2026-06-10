"""Final fix: enrich last 8 thin sections in Ch 2 and Ch 20."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = {
    's2-4': '<div class="diagram-container"><div class="diagram-title">Scopes — Product vs Cost Center vs Environment</div><pre>\n  PRODUCT SCOPE: Aligns costs to specific products/features\n  COST CENTER SCOPE: Traditional departmental accounting view\n  ENVIRONMENT SCOPE: Prod vs staging vs dev cost segmentation\n  CUSTOM SCOPE: Any business-relevant grouping (e.g., "customer-facing")\n</pre></div>',
    's2-5': '<div class="diagram-container"><div class="diagram-title">Allied Personas — Supporting the FinOps Ecosystem</div><pre>\n  ITAM: License tracking + BYOL compliance | ITFM: Financial systems integration\n  ITSM: Change management + service catalog | Security: Safe automation guardrails\n  Sustainability: GreenOps alignment (efficiency = lower cost + lower carbon)\n</pre></div>',
    's2-5a': '<div class="diagram-container"><div class="diagram-title">ITAM Role in FinOps</div><pre>\n  ITAM PROVIDES: License inventory -> BYOL tracking -> Hardware lifecycle data\n  FINOPS USES: Accurate license cost allocation + compliance verification\n  COLLABORATION: ITAM data feeds into FinOps for complete technology cost picture\n</pre></div>',
    's2-5b': '<div class="diagram-container"><div class="diagram-title">ITFM Role in FinOps</div><pre>\n  ITFM PROVIDES: General ledger integration + Chargeback models + Financial governance\n  FINOPS FEEDS: Cloud cost data into ITFM systems for unified financial reporting\n  TOGETHER: FinOps generates the data, ITFM structures it for the business\n</pre></div>',
    's2-5c': '<div class="diagram-container"><div class="diagram-title">ITSM Role in FinOps</div><pre>\n  ITSM PROVIDES: Change approval workflows + Service catalog + Incident management\n  FINOPS INTEGRATES: Cost gates in CI/CD pipelines = automated cost-aware change control\n  SYNERGY: Cost spikes treated as incidents = faster detection + resolution\n</pre></div>',
    's2-8': '<div class="diagram-container"><div class="diagram-title">Executive Strategy Alignment — 2026 Framework Addition</div><pre>\n  BRIDGES: FinOps metrics (ESR, Unit Cost, Coverage) -> Boardroom decisions\n  ENABLES: Leaders to compare options, make tradeoffs, govern investments for value\n  FCE TIP: Expect questions about translating FinOps data into business strategy language\n</pre></div>',
    's20-5': '<div class="diagram-container"><div class="diagram-title">AI for FinOps — Use Cases</div><pre>\n  Anomaly Detection: ML models learn normal patterns -> alert on deviations\n  Rightsizing: AI suggests optimal configs (Densify, Cast AI)\n  Forecasting: ML accounts for seasonality + growth trends\n  Agentic FinOps: Autonomous AI adjusts RI/SP coverage, Spot/OD mix continuously\n</pre></div>',
    's20-5a': '<div class="diagram-container"><div class="diagram-title">AI FinOps Use Cases in Practice</div><pre>\n  COST AGENTS: AI continuously optimizes commitments (RI/SP), Spot/OD mix, instance selection\n  NL QUERIES: "Which team exceeded budget?" -> LLM queries cost data in natural language\n  PREDICTIVE: AI forecasts cost impact of architecture changes before deployment\n</pre></div>',
}

enriched = 0
for sec_id, visual in fixes.items():
    idx = c.find(f'id="{sec_id}"')
    if idx == -1: continue
    block_start = c.rfind('<div class="section-block"', 0, idx)
    if block_start == -1: continue
    markers = ['<div class="section-block"', '<div class="fce-exam-questions"', '<div class="visual-summary"']
    end = len(c)
    for m in markers:
        p = c.find(m, block_start + 50)
        if p != -1 and p < end: end = p
    sec = c[block_start:end]
    lc = sec.rfind('</div>')
    if lc > 0:
        c = c[:block_start] + sec[:lc] + '\n' + visual + '\n' + sec[lc:] + c[end:]
        enriched += 1

print(f'Fixed: {enriched} sections')
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('Saved.')
