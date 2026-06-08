import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8').read()

# Find all details blocks with their full content
pattern = r'<details>\s*<summary>Answer & Explanation</summary>(.*?)</details>'
matches = re.findall(pattern, html, re.DOTALL)
print(f"Total Q&A details blocks: {len(matches)}")

# For each block, find eq-explanation divs
for i, m in enumerate(matches[:3]):
    exps_in_block = re.findall(r'class="eq-explanation">(.+?)</div>\s*(?:<div class="eq-explanation">|</details>)', m, re.DOTALL)
    print(f"\nBlock {i+1}: {len(exps_in_block)} explanation divs")
    for j, e in enumerate(exps_in_block):
        print(f"  Exp {j+1}: {e[:150]}...")
