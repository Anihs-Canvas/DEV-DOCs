import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# Find ALL details blocks with >1 explanation and remove the second one
# Pattern: first explanation </div> followed by second explanation div
# The second explanation always starts with <div class="eq-explanation"> without indentation

# More aggressive: find any consecutive eq-explanation divs and remove the second
pattern = re.compile(
    r'(class="eq-explanation">.*?</div>)\s*(<div class="eq-explanation"><span class="eq-exp-label">Explanation</span>)',
    re.DOTALL
)

matches = list(pattern.finditer(h))
print("Found {} duplicates".format(len(matches)))

for m in reversed(matches):
    # Remove from start of second explanation to its closing </div>
    start = m.start(2)
    # Find matching </div> - count divs
    pos = start
    depth = 1
    while depth > 0 and pos < len(h):
        no = h.find('<div', pos)
        nc = h.find('</div>', pos)
        if nc < 0: break
        if no >= 0 and no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            pos = nc + 6
    if depth == 0:
        h = h[:start] + h[pos:]

# Clean blank lines
h = re.sub(r'\n\s*\n\s*\n', '\n\n', h)

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','w',encoding='utf-8') as f:
    f.write(h)

print("Cleaned. Lines: {}".format(h.count('\n')))

# Verify
h2 = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
details = re.findall(r'<details>.*?</details>', h2, re.DOTALL)
doubles = [d for d in details if d.count('class="eq-explanation"') > 1]
print("Remaining doubles: {}".format(len(doubles)))
