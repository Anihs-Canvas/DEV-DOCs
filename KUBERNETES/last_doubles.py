import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
details = re.findall(r'<details>.*?</details>', h, re.DOTALL)
doubles = [d for d in details if d.count('class="eq-explanation"') > 1]

for i, d in enumerate(doubles):
    # Find the exact positions of eq-explanation divs
    positions = [(m.start(), m.end()) for m in re.finditer(r'class="eq-explanation"', d)]
    print("\nDouble #{}: {} explanations".format(i+1, len(positions)))
    for j, (s, e) in enumerate(positions):
        # Show the surrounding context
        ctx_start = max(0, s-5)
        ctx = d[ctx_start:e+150].replace('\n','\\n')
        print("  {}: ...{}".format(j+1, ctx[:200]))
