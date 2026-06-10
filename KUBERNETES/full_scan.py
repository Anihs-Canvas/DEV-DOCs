"""Full-file scan for thin sections and sparse content across ALL chapters."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== FULL FILE AUDIT ===\n")
total_thin = 0
total_sections = 0

for ch in range(1, 21):
    start_tag = f'<div id="ch{ch}">'
    end_tag = f'<div id="ch{ch+1}">' if ch < 20 else None
    
    start = content.find(start_tag)
    if start == -1:
        print(f'Ch {ch}: NOT FOUND')
        continue
    
    if end_tag:
        end = content.find(end_tag, start)
    else:
        end = len(content)
    
    ch_block = content[start:end]
    sections = re.findall(
        r'<div class="section-block" id="(s\d+-\w+)">(.*?)(?=<div class="section-block"|<div class="fce-exam-questions"|<!-- Ch.*?Visual Summary -->)',
        ch_block, re.DOTALL
    )
    
    thin = []
    for sec_id, sec_html in sections:
        total_sections += 1
        visuals = len(re.findall(r'(<table|<pre>|diagram-container|code-block-wrapper|card-grid|compare-table|info-box|scenario-box)', sec_html))
        paras = len(re.findall(r'<p>', sec_html))
        size = len(sec_html)
        
        # Thin if 0 visuals OR very short (<500 chars with only 1 paragraph)
        if visuals == 0 or (visuals <= 1 and paras <= 1 and size < 600):
            thin.append((sec_id, visuals, paras, size))
    
    if thin:
        print(f'Ch {ch:2d}: {len(thin)} thin/light sections')
        for sec_id, v, p, s in thin:
            total_thin += 1
            label = 'THIN' if v == 0 else 'LIGHT'
            print(f'  [{label}] {sec_id}: {v} visuals, {p} paras, {s} chars')
    else:
        print(f'Ch {ch:2d}: CLEAN')

print(f'\n=== SUMMARY ===')
print(f'Total sections: {total_sections}')
print(f'Thin/light remaining: {total_thin}')

# Also check for Q&A that has mismatched enrichments
print('\n=== MISMATCHED Q&A ENRICHMENTS ===')
generic_templates = [
    'Rightsizing Check — kubectl',
    'Namespace with Cost Allocation Labels',
    'Kubecost Quick Start',
    'Proportional Allocation Calculation',
    'Finance Dashboard — Budget Variance',
    'Engineering Dashboard — anihpj',
    'ML Cost — Training vs Inference',
]
for tmpl in generic_templates:
    count = content.count(tmpl)
    if count > 3:
        print(f'  "{tmpl}" appears {count} times — may be over-used')
