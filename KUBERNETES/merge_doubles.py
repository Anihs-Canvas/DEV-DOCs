import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# Pattern: a real eq-explanation followed by a "This concept is frequently tested" duplicate
# The second one is always on the same line (no newline between) and starts right after </div>
pattern = re.compile(
    r'(</div>)\s*(<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This concept is frequently tested on the Helm certification exam)',
    re.DOTALL
)

matches = list(pattern.finditer(h))
print("Found {} duplications to merge".format(len(matches)))

# Remove the second explanation - just keep the closing </div> from the first
for m in reversed(matches):
    # m.group(1) is the first </div>, m.group(2) starts the boilerplate
    end_pos = m.end()
    # Find the closing </div> for this boilerplate explanation
    closing = h.find('</div>', m.start(2))
    if closing < 0:
        continue
    closing += 6  # include the </div>
    # Remove the boilerplate explanation div entirely
    h = h[:m.start(2)] + h[closing:]

# Also clean up any blank lines created
h = re.sub(r'\n\s*\n\s*\n', '\n\n', h)

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','w',encoding='utf-8') as f:
    f.write(h)

print("Cleaned. Lines: {}".format(h.count('\n')))

# Verify
h2 = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
details2 = re.findall(r'<details>.*?</details>', h2, re.DOTALL)
double2 = [d for d in details2 if d.count('class="eq-explanation"') > 1]
print("Remaining double explanations: {}".format(len(double2)))
