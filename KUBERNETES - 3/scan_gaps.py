import re

with open('Backstage.html', 'r', encoding='utf-8') as f:
    content = f.read()

sections = re.findall(
    r'<div class="section-block" id="(s\d+-\d+[a-z]?)">(.*?)(?=<div class="section-block"|<div class="cba-exam-questions"|</div>\s*</div>\s*<!--)',
    content, re.DOTALL)

visual_patterns = [
    r'class="(?:diagram-container|card-grid|info-box|compare-table|info-card|arch-layer|process-steps|visual-summary)"',
    r'class="(?:case-study-grid|case-card|evolution-strip|evo-item|timeline-vertical|timeline-item|arch-layers|layer-)"',
    r'<pre><code',
    r'<table',
    r'<img ',
]

zero_vis = []
for sec_id, sec_content in sections:
    visuals = sum(len(re.findall(p, sec_content)) for p in visual_patterns)
    clean = re.sub(r'<[^>]+>', '', sec_content)
    clean = re.sub(r'\s+', ' ', clean).strip()
    chars = len(clean)
    h3 = re.search(r'<h3>(.*?)</h3>', sec_content)
    title = h3.group(1) if h3 else '(no title)'
    
    if chars < 1500 and visuals == 0:
        zero_vis.append((sec_id, chars, title))

print(f"TRUE zero-visual sections: {len(zero_vis)}\n")
for sid, c, t in zero_vis:
    print(f"  {sid}: {c:>5} chars | {t}")
