import re
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Check which scenarios exist
for s in range(1, 41):
    sid = f'id="sc-s{s}"'
    if sid not in h:
        print(f"MISSING: S{s}")
    else:
        # Count tenet-steps and cmd-outputs
        idx = h.index(sid)
        next_s = h.find(f'id="sc-s{s+1}"', idx+1)
        if next_s == -1:
            next_s = h.find('<footer', idx)
        block = h[idx:next_s]
        ts = block.count('tenet-step')
        cmd = block.count('cmd-output')
        if s == 1:
            print(f"S1 (REF): tenet={ts}, cmd={cmd}")
        elif s >= 11:
            print(f"S{s}: tenet={ts}, cmd={cmd}")
