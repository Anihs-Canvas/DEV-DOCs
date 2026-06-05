with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Print headers for affected scenarios
for s in [18, 19, 20, 23, 30, 31, 36, 37, 38, 39, 40]:
    sid = f'id="sc-s{s}"'
    idx = h.index(sid)
    # Find the h4 and sc-desc
    chunk = h[idx:idx+600]
    
    # Extract h4
    h4_match = __import__('re').search(r'<h4>(.*?)</h4>', chunk)
    # Extract sc-desc  
    desc_match = __import__('re').search(r'<div class="sc-desc">(.*?)</div>', chunk, __import__('re').DOTALL)
    # Extract tenet-flow content
    ts_match = __import__('re').search(r'<h5>🧠 Diagnostic Tenet.*?</h5>(.*?)<h5>📟', chunk, __import__('re').DOTALL)
    
    h4_text = h4_match.group(1) if h4_match else "?"
    desc_text = desc_match.group(1).strip() if desc_match else "?"
    ts_count = chunk.count('tenet-step')
    cmd_count = chunk.count('cmd-output')
    
    # Count tenet-steps in full block
    next_s = h.find(f'id="sc-s{s+1}"', idx+1)
    if next_s == -1:
        next_s = h.find('<footer', idx)
    block = h[idx:next_s]
    full_ts = block.count('tenet-step')
    full_cmd = block.count('cmd-output')
    
    print(f"S{s}: {h4_text}")
    print(f"  tenet-steps={full_ts}, cmd-outputs={full_cmd}")
    print()
