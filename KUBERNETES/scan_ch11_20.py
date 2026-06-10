"""Scan chapters 11-20 for thin sections needing enrichment."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

for ch in range(11, 21):
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
    
    thin_sections = []
    for sec_id, sec_html in sections:
        visuals = len(re.findall(r'(<table|<pre>|diagram-container|code-block-wrapper|card-grid|compare-table|info-box|scenario-box)', sec_html))
        paras = len(re.findall(r'<p>', sec_html))
        if visuals == 0 and paras >= 1:
            h_match = re.search(r'<h[34][^>]*>(.*?)</h[34]>', sec_html)
            heading = h_match.group(1) if h_match else sec_id
            # Get section size
            size = len(sec_html)
            thin_sections.append((sec_id, heading, size, paras))
    
    if thin_sections:
        print(f'\n=== Ch {ch}: {len(thin_sections)} thin sections ===')
        for sec_id, heading, size, paras in thin_sections:
            print(f'  [{sec_id}] {heading}')
            print(f'       Size: {size} chars, Parags: {paras}')
    else:
        print(f'Ch {ch}: CLEAN — no thin sections')
