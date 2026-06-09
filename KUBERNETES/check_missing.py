import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# Find Q&A blocks missing explanations
details = re.findall(r'(<details>.*?</details>)', h, re.DOTALL)
missing = []
for d in details:
    exp_count = d.count('class="eq-explanation"')
    if exp_count == 0:
        q_match = re.search(r'class="eq-question">(.*?)</div>', d)
        q_text = q_match.group(1)[:80] if q_match else "???"
        missing.append(q_text)

print("Q&A blocks with NO explanation:", len(missing))
for i, q in enumerate(missing[:10]):
    print("  {}: {}".format(i+1, q))

# Check first few blocks that have explanations
with_exp = []
for d in details:
    if d.count('class="eq-explanation"') >= 1:
        exp_match = re.search(r'class="eq-explanation">.*?<p>(.*?)</p>', d, re.DOTALL)
        if exp_match:
            with_exp.append(exp_match.group(1)[:80])

print("\nBlocks WITH explanation:", len(with_exp))
for i, e in enumerate(with_exp[:5]):
    print("  {}: {}".format(i+1, e))
