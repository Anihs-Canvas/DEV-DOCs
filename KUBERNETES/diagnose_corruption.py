import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Find the S23 block
s23_idx = h.index('id="sc-s23"')
s23_block_start = h.rfind('<div class="scenario-block"', 0, s23_idx)

# Find S29
s29_idx = h.index('id="sc-s29"')
s29_block_start = h.rfind('<div class="scenario-block"', 0, s29_idx)

# The corrupted S23 block is from s23_block_start to s29_block_start
corrupt_block = h[s23_block_start:s29_block_start]
print(f"Corrupt S23 block: {len(corrupt_block)} chars")

# Search for embedded scenario headers
for s in [24, 25, 26, 27, 28]:
    pattern = f'<div class="scenario-block" id="sc-s{s}"'
    if pattern in corrupt_block:
        idx = corrupt_block.index(pattern)
        print(f"Found S{s} at offset {idx} within S23 block")
    else:
        print(f"S{s} not found in corrupt block")
