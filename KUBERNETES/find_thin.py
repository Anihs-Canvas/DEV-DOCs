"""Scan finOps_eng.html for thin sections — content blocks without visual enrichment."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all section-block divs
sections = re.findall(
    r'<div class="section-block" id="([^"]+)">(.*?)(?=<div class="section-block"|<!-- Ch.*?Visual Summary -->|<div class="fce-exam-questions"|<div class="info-box|<div class="card-grid|<div class="diagram-container|<div class="code-block-wrapper|<div class="compare-table|<div class="scenario-box)',
    content, re.DOTALL
)

# Also check non-section-block content between chapter intro and first section
chapters = re.findall(
    r'(<div id="ch\d+">.*?)(?=<div id="ch\d+">|$)',
    content, re.DOTALL
)

print("=== THIN SECTIONS AUDIT ===\n")
thin_count = 0

for sec_id, sec_content in sections:
    # Count visual elements
    has_table = bool(re.search(r'<table', sec_content))
    has_pre = bool(re.search(r'<pre>', sec_content))
    has_diagram = bool(re.search(r'diagram-container', sec_content))
    has_code_block = bool(re.search(r'code-block-wrapper', sec_content))
    has_card = bool(re.search(r'card-grid', sec_content))
    has_compare = bool(re.search(r'compare-table', sec_content))
    has_info = bool(re.search(r'info-box', sec_content))
    has_scenario = bool(re.search(r'scenario-box', sec_content))
    
    # Count paragraphs vs visual elements
    p_count = len(re.findall(r'<p>', sec_content))
    visual_count = sum([has_table, has_pre, has_diagram, has_code_block, has_card, has_compare, has_info, has_scenario])
    
    # A section is "thin" if it has 0-1 visual elements and multiple paragraphs
    if visual_count <= 1 and p_count >= 1:
        # Get the heading
        h_match = re.search(r'<h[34][^>]*>(.*?)</h[34]>', sec_content)
        heading = h_match.group(1) if h_match else sec_id
        
        # Get first 120 chars of text for context
        text = re.sub(r'<[^>]+>', ' ', sec_content[:200]).strip()[:120]
        
        thin_count += 1
        status = "🔴 THIN" if visual_count == 0 else "🟡 LIGHT"
        print(f'{status} [{sec_id}] {heading}')
        print(f'       Visuals: {visual_count}, Parags: {p_count}')
        print(f'       Preview: {text}...')
        print()

print(f'\nTotal thin sections found: {thin_count}')

# Also check for thin chapter intros (no visual after learning objectives)
print("\n=== CHAPTER INTROS WITHOUT ENRICHMENT ===")
for ch_num in range(1, 21):
    m = re.search(rf'id="ch{ch_num}".*?(?=id="ch{ch_num+1}"|$)', content, re.DOTALL)
    if m:
        ch_block = m.group(1)
        # Check content between learning-objectives and first section-block
        lo_end = ch_block.find('</ul></div>')  # end of learning objectives
        if lo_end > 0:
            # Content between LOs and first section
            after_lo = ch_block[lo_end:]
            # Skip FCE relevance and exam tips (those are fine)
            # Check if there's substantial paragraph content without visuals
            first_section = after_lo.find('<div class="section-block"')
            if first_section > 0:
                gap = after_lo[:first_section]
                visuals_in_gap = len(re.findall(r'(<table|<pre>|diagram-container|code-block-wrapper|card-grid|compare-table|info-box|scenario-box)', gap))
                if visuals_in_gap == 0 and len(gap) > 200:
                    print(f'  Ch {ch_num}: Intro gap without visuals ({len(gap)} chars)')
