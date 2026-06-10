"""Surgical fix for remaining mismatched templates."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    c = f.read()

# Map of what each chapter's QA code blocks should contain
ch_visuals = {
    1: '<div class="diagram-container"><div class="diagram-title">FinOps Principles — COBALT</div><pre>\n  C — Collaboration: Finance + Engineering + Business = One Team\n  O — Ownership: Everyone owns their technology spend\n  B — Business Value: Decisions driven by business ROI\n  A — Accessibility: Timely, accessible cost data for all\n  L — Lean Operations: Eliminate waste continuously\n  T — Transparency: Costs visible to everyone\n</pre></div>',
    2: '<div class="diagram-container"><div class="diagram-title">FinOps Lifecycle — Inform → Optimize → Operate</div><pre>\n  INFORM: Visibility, dashboards, allocation → "See the bill"\n  OPTIMIZE: Rightsize, reserve, spot → "Reduce the bill"\n  OPERATE: Governance, automation, culture → "Prevent waste"\n</pre></div>',
    11: '<div class="diagram-container"><div class="diagram-title">Budgeting + Unit Economics</div><pre>\n  TOP-DOWN: Leadership sets cap → allocate down | BOTTOM-UP: Teams estimate → aggregate up\n  HYBRID BEST: Bottom-up detail + top-down validation\n  UNIT COST: $14,200 / 4.73M = $0.003/posting | ROI = (Savings - Investment) / Investment × 100\n</pre></div>',
    13: '<div class="compare-table"><table><thead><tr><th>Category</th><th>Tools</th><th>Cost</th></tr></thead><tbody><tr><td>Cloud-Native</td><td>Cost Explorer, Azure CM</td><td>Free</td></tr><tr><td>Third-Party</td><td>CloudHealth, Vantage</td><td>1-3%/$50</td></tr><tr><td>K8s-Specific</td><td>Kubecost, Cast AI</td><td>Free/$$$</td></tr><tr><td>IaC Estimation</td><td>Infracost</td><td>Free</td></tr></tbody></table></div>',
    14: '<div class="diagram-container"><div class="diagram-title">Exam Strategy Quick Card</div><pre>\n  90 min | 76 Qs | ~70 sec/Q | 3-pass: 60min confident, 20min marked, 10min review\n  NEVER leave blank (no penalty) | Write 5 formulas first | Eliminate 2 wrong = 50% guess\n</pre></div>',
    17: '<div class="diagram-container"><div class="diagram-title">Multi-Cloud Decision Framework</div><pre>\n  GO MULTI-CLOUD: Acquisition, compliance (data residency), best-of-breed, negotiation leverage\n  STAY SINGLE-CLOUD: <200 engineers, no compliance need, simplicity > theoretical savings\n  anihpj (15 eng): Stay single-cloud AWS. Multi-cloud overhead exceeds savings.\n</pre></div>',
    18: '<div class="diagram-container"><div class="diagram-title">Build vs Buy — Total Cost Comparison</div><pre>\n  BUY (Managed): Infrastructure cost + $0 ops = LOWER total\n  BUILD (Self-Managed): Infrastructure cost + Engineer hrs × $150/hr\n  RULE: If self-managed requires >30 min/month, managed wins on total cost.\n</pre></div>',
    19: '<div class="diagram-container"><div class="diagram-title">FinOps Culture Building Blocks</div><pre>\n  VISIBILITY: Dashboards + Slack bots → everyone sees costs\n  CELEBRATION: Cost wins celebrated like feature launches\n  TRAINING: 30min onboarding + monthly 15min wins + quarterly 45min deep-dives\n  INCENTIVES: Reward unit cost improvement, not absolute cost reduction\n</pre></div>',
    20: '<div class="diagram-container"><div class="diagram-title">AI/ML + Serverless Cost Optimization</div><pre>\n  TRAINING: Spot GPUs (60-70% savings) | INFERENCE: Inferentia/Trainium (40% savings)\n  LAMBDA WINS: Low traffic, spiky, event-driven | EC2 WINS: Steady 24/7, RI-eligible\n  BREAK-EVEN: ~500K req/hr. Below = Lambda cheaper. Above = EC2 RI cheaper.\n</pre></div>',
}

fixed = 0

# Find chapters and their content boundaries
for ch_num, replacement_html in ch_visuals.items():
    # Find chapter start
    ch_start_tag = f'<div id="ch{ch_num}">'
    ch_start = c.find(ch_start_tag)
    if ch_start == -1:
        print(f'Chapter {ch_num} not found, skipping')
        continue
    
    # Find next chapter (or end marker) to bound content
    next_ch = c.find(f'<div id="ch{ch_num+1}">', ch_start) if ch_num < 20 else len(c)
    if next_ch == -1:
        next_ch = len(c)
    
    chapter_slice = c[ch_start:next_ch]
    
    # Replace Rightsizing Check blocks in this chapter
    for template_title in ['Rightsizing Check — kubectl', 'Kubecost Quick Start']:
        pos = 0
        while True:
            idx = chapter_slice.find(template_title, pos)
            if idx == -1:
                break
            
            # Find the full code-block-wrapper
            full_start = chapter_slice.rfind('<div class="code-block-wrapper">', 0, idx)
            if full_start == -1:
                pos = idx + len(template_title)
                continue
            
            full_end = chapter_slice.find('</code></pre></div>', idx)
            if full_end == -1:
                pos = idx + len(template_title)
                continue
            full_end += len('</code></pre></div>')
            
            # Calculate absolute positions
            abs_start = ch_start + full_start
            abs_end = ch_start + full_end
            
            # Replace
            c = c[:abs_start] + replacement_html + c[abs_end:]
            fixed += 1
            
            # Recalculate chapter boundaries since content shifted
            ch_start = c.find(ch_start_tag)
            next_ch = c.find(f'<div id="ch{ch_num+1}">', ch_start) if ch_num < 20 else len(c)
            if next_ch == -1:
                next_ch = len(c)
            chapter_slice = c[ch_start:next_ch]
            
            pos = idx + len(replacement_html)  # move past replaced content

print(f'Fixed {fixed} remaining templates')

# Final count
rw_left = c.count('Rightsizing Check — kubectl')
kc_left = c.count('Kubecost Quick Start')
print(f'Rightsizing Check remaining: {rw_left}')
print(f'Kubecost Quick Start remaining: {kc_left}')

with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('Saved.')
