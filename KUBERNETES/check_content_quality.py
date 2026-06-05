import re
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Extract S1 as reference
s1_start = h.index('id="sc-s1"')
s1_end = h.index('id="sc-s2"')
s1 = h[s1_start:s1_end]

# Count structural elements in S1
s1_answer_toggle = s1.count('sc-answer-toggle')
s1_tenet_steps = s1.count('tenet-step')
s1_cmd_outputs = s1.count('cmd-output')
s1_before = s1.count('BEFORE fix')
s1_after = s1.count('AFTER Fix')
s1_fix_toggle = s1.count('sc-fix-toggle')
s1_code_blocks = s1.count('code-block')
s1_code_headers = s1.count('code-header')

print("=== S1 REFERENCE COUNTS ===")
print(f"  answer-toggle: {s1_answer_toggle}")
print(f"  tenet-steps: {s1_tenet_steps}")
print(f"  cmd-outputs: {s1_cmd_outputs}")
print(f"  BEFORE fix: {s1_before}")
print(f"  AFTER Fix: {s1_after}")
print(f"  fix-toggle: {s1_fix_toggle}")
print(f"  code-blocks: {s1_code_blocks}")
print(f"  code-headers: {s1_code_headers}")
print()

# Check each scenario S11-S40
print("=== S11-S40 COMPARISON ===")
issues = []
for s in range(11, 41):
    sid = f'id="sc-s{s}"'
    if sid not in h:
        issues.append(f"S{s}: MISSING")
        continue
    
    idx = h.index(sid)
    next_s = h.find(f'id="sc-s{s+1}"', idx+1)
    if next_s == -1:
        next_s = h.find('<footer', idx)
    block = h[idx:next_s]
    
    sc_issues = []
    
    # Check answer section
    at_count = block.count('sc-answer-toggle')
    ts_count = block.count('tenet-step')
    cmd_count = block.count('cmd-output')
    before_count = block.count('BEFORE fix')
    after_count = block.count('AFTER Fix')
    ft_count = block.count('sc-fix-toggle')
    cb_count = block.count('code-block')
    ch_count = block.count('code-header')
    
    if at_count < 1:
        sc_issues.append("NO answer-toggle")
    if ts_count < 3:
        sc_issues.append(f"tenet-steps={ts_count} (ref=5)")
    if cmd_count < 3:
        sc_issues.append(f"cmd-outputs={cmd_count} (ref=5)")
    if before_count < 1:
        sc_issues.append("NO 'BEFORE fix' label")
    if after_count < 1:
        sc_issues.append("NO 'AFTER Fix' label")
    if ft_count < 2:
        sc_issues.append(f"fix-toggle={ft_count} (ref=2, needs fix+cleanup)")
    if cb_count < 2:
        sc_issues.append(f"code-blocks={cb_count} (ref=4+)")
    
    # Check for inline/compact formatting
    # Inline sc-answer
    inline_answer = re.findall(r'<div class="sc-answer" id="sc-sa\d+"><h5>', block)
    if inline_answer:
        sc_issues.append(f"{len(inline_answer)} INLINE answer(s)")
    
    # Inline fix dropdown
    inline_fix = re.findall(r'<div class="sc-answer" id="sc-s\d+-fix-drop"><div class="code-block"><div class="code-header">', block)
    if inline_fix:
        sc_issues.append(f"{len(inline_fix)} INLINE fix dropdown(s)")
    
    # Inline cleanup dropdown
    inline_cleanup = re.findall(r'<div class="sc-answer" id="sc-s\d+-cleanup-drop"><div class="code-block"><div class="code-header">', block)
    if inline_cleanup:
        sc_issues.append(f"{len(inline_cleanup)} INLINE cleanup dropdown(s)")
    
    # Inline sc-step content (missing proper indentation)
    inline_step = re.findall(r'<div class="sc-step-content">\s*<h4', block)
    if inline_step:
        sc_issues.append(f"{len(inline_step)} INLINE step-content(s)")
    
    if sc_issues:
        issues.append(f"S{s}: {', '.join(sc_issues)}")
    else:
        print(f"  S{s}: ✅ MATCHES S1")

print()
for i in issues:
    print(f"  ❌ {i}")
print(f"\nTotal with issues: {len(issues)}/30")
