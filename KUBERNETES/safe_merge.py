import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# ONLY remove boilerplate duplicates that say "This concept is frequently tested on the Helm certification exam"
# This is the SAFE pattern - it only matches the specific boilerplate text we added
pattern = re.compile(
    r'</div>\s*<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This concept is frequently tested on the Helm certification exam\. The illustration below demonstrates the practical application with real commands and examples you can use directly in the exam terminal\.</p>\n<pre>.*?</pre>\n</div>',
    re.DOTALL
)

matches = list(pattern.finditer(h))
print("Found {} boilerplate duplicates to remove".format(len(matches)))

for m in reversed(matches):
    h = h[:m.start()] + h[m.end():]

# Also remove remaining "This is a key Helm certification concept" if any
h = h.replace(
    '<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a key Helm certification concept. The performance-based exam tests practical application — understanding <strong>why</strong> is as important as knowing <strong>how</strong>. Review the related chapter section for deeper context, diagrams, and hands-on practice drills.</p></div>',
    ''
)

# Clean up triple blank lines
h = re.sub(r'\n\s*\n\s*\n\s*\n', '\n\n\n', h)

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','w',encoding='utf-8') as f:
    f.write(h)

# Verify
details = re.findall(r'<details>.*?</details>', h, re.DOTALL)
doubles = sum(1 for d in details if d.count('class="eq-explanation"') > 1)
gb = h.count('This is a key Helm certification concept')
qas = len(re.findall(r'class="exam-question-item"', h))
print("Remaining doubles: {}".format(doubles))
print("Generic boilerplates: {}".format(gb))
print("Total Q&As: {}".format(qas))
print("Lines: {}".format(h.count('\n')))
