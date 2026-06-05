import re, os
os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')
with open('cka_test_prep.html','r',encoding='utf-8') as f: h=f.read()
print(f'File: {len(h)} bytes')

# Find all scenario IDs
ids = re.findall(r'id="(sc-s\d+)"', h)
nums = sorted(set(int(x.split('-s')[1]) for x in ids))
print(f'Scenarios: {nums}')
print(f'Count: {len(nums)}')

# Check S11-S20 for key structural elements
for s in range(11, 21):
    sid = f'sc-s{s}'
    if sid not in ids:
        print(f'  S{s}: MISSING')
        continue
    
    # Check each element
    checks = []
    # deploy step
    if f'id="{sid}-code"' in h: checks.append('deploy')
    # error-spot
    if f'id="{sid}"' in h: checks.append('')
    # Actually count elements between this scenario and next
    start = h.find(f'id="{sid}"')
    next_start = h.find('id="sc-s', start + len(sid) + 10)
    if next_start == -1: next_start = len(h)
    section = h[start:next_start]
    
    has_error = 'sc-step error-spot' in section
    has_debug = 'sc-step debug-find' in section
    has_answer_toggle = 'sc-answer-toggle' in section
    has_fix = 'sc-s'+str(s)+'-fix-drop' in section
    has_cleanup = 'sc-s'+str(s)+'-cleanup-drop' in section
    has_verify = 'sc-step-num answer' in section
    
    status = []
    if has_error: status.append('error-spot')
    if has_debug: status.append('debug')
    if has_answer_toggle: status.append('answer')
    if has_fix: status.append('fix')
    if has_cleanup: status.append('cleanup')
    if has_verify: status.append('verify')
    
    missing = []
    if not has_error: missing.append('error-spot')
    if not has_debug: missing.append('debug')
    if not has_answer_toggle: missing.append('answer')
    if not has_fix: missing.append('fix')
    if not has_cleanup: missing.append('cleanup')
    if not has_verify: missing.append('verify')
    
    if missing:
        print(f'  S{s}: ❌ Missing: {missing}')
    else:
        print(f'  S{s}: ✅ All 6 elements present')
