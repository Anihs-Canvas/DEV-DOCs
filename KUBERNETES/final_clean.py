import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# Find ALL details blocks
pattern = re.compile(r'(<details>.*?</details>)', re.DOTALL)
details = list(pattern.finditer(h))

fixed = 0
for m in reversed(details):
    block = m.group(1)
    # Count eq-explanation divs
    exp_count = block.count('class="eq-explanation"')
    if exp_count <= 1:
        continue
    
    # Find all eq-explanation starting positions within this block
    exp_starts = []
    search_from = 0
    while True:
        pos = block.find('class="eq-explanation"', search_from)
        if pos < 0:
            break
        exp_starts.append(pos)
        search_from = pos + 1
    
    # Keep only the FIRST explanation, remove the rest
    # Build new block: from start to end of first exp, then skip to after the last exp
    first_start = m.start() + exp_starts[0]
    # Find end of first explanation
    pos = first_start
    depth = 1
    first_end = -1
    while depth > 0 and pos < len(h):
        no = h.find('<div', pos)
        nc = h.find('</div>', pos)
        if nc < 0: break
        if 0 <= no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            if depth == 0:
                first_end = nc + 6
            pos = nc + 6
    
    if first_end < 0:
        continue
    
    # Find end of last explanation
    last_start = m.start() + exp_starts[-1]
    pos = last_start
    depth = 1
    last_end = -1
    while depth > 0 and pos < len(h):
        no = h.find('<div', pos)
        nc = h.find('</div>', pos)
        if nc < 0: break
        if 0 <= no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            if depth == 0:
                last_end = nc + 6
            pos = nc + 6
    
    if last_end < 0:
        continue
    
    # Remove everything between first_end and last_end (the duplicate explanations)
    h = h[:first_end] + h[last_end:]
    fixed += 1

h = re.sub(r'\n\s*\n\s*\n', '\n\n', h)

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','w',encoding='utf-8') as f:
    f.write(h)

print("Fixed {} blocks".format(fixed))
print("Lines: {}".format(h.count('\n')))

# Final check
details2 = re.findall(r'<details>.*?</details>', h, re.DOTALL)
doubles = [d for d in details2 if d.count('class="eq-explanation"') > 1]
print("Remaining doubles: {}".format(len(doubles)))
