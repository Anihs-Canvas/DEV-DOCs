import re
FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = {
    's13-2c': '<div class="diagram-container"><div class="diagram-title">Third-Party Tool Quick Reference</div><pre>\n  Flexera: Migration + license optimization | Densify: ML resource optimization\n  Harness CCM: Engineering-led, CI/CD integrated | Vantage.sh: Startups, simple UX\n</pre></div>',
    's13-2d': '<div class="diagram-container"><div class="diagram-title">Densify vs Cloud-Native Recommendations</div><pre>\n  Cloud-Native: Free, single-cloud, basic recos\n  Densify: ML-based, multi-platform (K8s+VMware+AWS+Azure), advanced analytics\n  UPGRADE WHEN: Native recos are too generic or you need K8s + VM together.\n</pre></div>',
    's13-2e': '<div class="diagram-container"><div class="diagram-title">Harness CCM Features</div><pre>\n  Auto-Stopping: Pause idle non-prod resources (60-80% savings)\n  Cost per Feature: Map costs to microservices, features, teams\n  CI/CD Integration: Cost estimates in PR comments\n  BEST FOR: Engineering-led FinOps integrated into developer workflow.\n</pre></div>',
}

for sec_id, visual in fixes.items():
    start = c.find(f'id="{sec_id}"')
    if start == -1: continue
    block_start = c.rfind('<div class="section-block"', 0, start)
    if block_start == -1: continue
    markers = ['<div class="section-block"', '<div class="fce-exam-questions"', '<div class="visual-summary"']
    end = len(c)
    for m in markers:
        p = c.find(m, block_start + 50)
        if p != -1 and p < end: end = p
    sec = c[block_start:end]
    lc = sec.rfind('</div>')
    if lc > 0:
        new_sec = sec[:lc] + '\n' + visual + '\n' + sec[lc:]
        c = c[:block_start] + new_sec + c[end:]
        print(f'OK: {sec_id}')

with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('Saved.')
