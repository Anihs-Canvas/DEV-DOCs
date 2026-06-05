import re
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Check S1 itself
s1_start = h.index('id="sc-s1"')
s1_end = h.index('id="sc-s2"')
s1 = h[s1_start:s1_end]

s1_ts = s1.count('tenet-step')
s1_cmd = s1.count('cmd-output')
s1_ft = s1.count('sc-fix-toggle')

print("=== S1 REFERENCE ===")
print(f"  tenet-steps: {s1_ts}")
print(f"  cmd-outputs: {s1_cmd}")
print(f"  fix-toggles: {s1_ft}")
print()

# Check S11-S40 for REAL content issues
print("=== REAL CONTENT ISSUES (S11-S40) ===")
real_issues = []
for s in range(11, 41):
    sid = f'id="sc-s{s}"'
    idx = h.index(sid)
    next_s = h.find(f'id="sc-s{s+1}"', idx+1)
    if next_s == -1:
        next_s = h.find('<footer', idx)
    block = h[idx:next_s]
    
    sc_issues = []
    
    ts = block.count('tenet-step')
    cmd = block.count('cmd-output')
    ft = block.count('sc-fix-toggle')
    at = block.count('sc-answer-toggle')
    res = block.count('sc-resolution')
    
    if at < 1:
        sc_issues.append("NO answer-toggle")
    if ts < s1_ts - 1:
        sc_issues.append(f"tenet-steps={ts} (S1={s1_ts})")
    if cmd < 3:
        sc_issues.append(f"cmd-outputs={cmd} (S1={s1_cmd})")
    if ft < 2:
        sc_issues.append(f"fix-toggles={ft} (needs fix+cleanup)")
    if res < 1:
        sc_issues.append("NO resolution")
    
    # Check for proper BEFORE/AFTER headers
    if 'BEFORE fix' not in block:
        sc_issues.append("NO 'BEFORE fix' header")
    if 'AFTER Fix' not in block:
        sc_issues.append("NO 'AFTER Fix' header")
    
    if sc_issues:
        real_issues.append(f"S{s}: {', '.join(sc_issues)}")

for i in real_issues:
    print(f"  ❌ {i}")

if not real_issues:
    print("  ✅ ALL 30 scenarios have complete content!")
print(f"\nScenarios with issues: {len(real_issues)}/30")
