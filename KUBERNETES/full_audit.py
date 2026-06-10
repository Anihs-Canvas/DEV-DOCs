import re
c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html','r',encoding='utf-8').read()

# Chapter by chapter Q count
print('=== CHAPTER Q&A BREAKDOWN ===')
total_q = 0; total_exp = 0; total_vis = 0
for ch in range(1,21):
    if ch == 15:
        pat = rf'id="ch15".*?(id="ch16"|$)'
    else:
        pat = rf'id="ch{ch}".*?(id="ch{ch+1}"|</section>|$)'
    m = re.search(pat, c, re.DOTALL)
    if m:
        block = m.group(1)
        qs = len(re.findall(r'eq-answer-label', block))
        ex = len(re.findall(r'eq-explanation', block))
        items = re.findall(r'<div class="exam-question-item">.*?</details>', block, re.DOTALL)
        vis = sum(1 for i in items if '<pre>' in i or '<table' in i or 'diagram-container' in i or 'code-block-wrapper' in i)
        total_q += qs; total_exp += ex; total_vis += vis
        status = 'OK' if qs >= 10 and ex >= qs else 'ISSUE'
        print(f'  Ch {ch:2d}: {qs:2d} Qs, {ex:2d} Exp, {vis:2d} Vis [{status}]')
    else:
        print(f'  Ch {ch:2d}: NOT FOUND')

print(f'\nTOTAL: {total_q} answers, {total_exp} explanations, {total_vis} with visuals')
print(f'Coverage: {total_exp/total_q*100:.1f}%' if total_q else 'N/A')
print(f'Visuals: {total_vis/total_q*100:.1f}%' if total_q else 'N/A')

# Sidebar link check
sidebar_hrefs = set(re.findall(r'href="#([^"]+)"', c))
body_ids = set(re.findall(r' id="([^"]+)"', c))
broken = sidebar_hrefs - body_ids
print(f'\n=== SIDEBAR CHECK ===')
print(f'Sidebar links: {len(sidebar_hrefs)}')
print(f'Body IDs: {len(body_ids)}')
print(f'Broken links: {len(broken)}')
if broken:
    for b in sorted(broken)[:10]:
        print(f'  BROKEN: #{b}')

# HTML integrity
print(f'\n=== HTML INTEGRITY ===')
print(f'</main>: {c.count("</main>")}')
print(f'<section>: {c.count("<section")}')
print(f'</section>: {c.count("</section")}')
print(f'<details>: {c.count("<details>")}')
print(f'</details>: {c.count("</details>")}')
print(f'File size: {len(c):,} chars')
