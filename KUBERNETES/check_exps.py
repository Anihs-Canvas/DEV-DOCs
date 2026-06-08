import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8').read()
# Find all details blocks - look for the full pattern
blocks = re.findall(r'(class="eq-answer">.+?class="eq-explanation">.+?</div></details>)', html, re.DOTALL)
print(f"Total Q&A details blocks with explanations: {len(blocks)}")

# Also find just explanation blocks
exps = re.findall(r'class="eq-explanation">(.+?)</div></details>', html, re.DOTALL)
print(f"Total explanation blocks: {len(exps)}")

# Show non-generic ones
generic = "This is a key Helm certification concept"
gc = 0
for i, e in enumerate(exps):
    if generic not in e:
        gc += 1
        snippet = e[:250].replace('\n',' ').replace('\r','')
        print(f"Non-generic #{gc} at block {i+1}: {snippet}...")
print(f"\nTotal non-generic: {gc}, Generic: {len(exps)-gc}")
