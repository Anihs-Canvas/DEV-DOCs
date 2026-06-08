import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8').read()

# Find all exam-question-items
items = re.findall(r'<div class="exam-question-item">(.*?)</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
print(f"Total exam-question-items: {len(items)}")

# Find explanations inside details
count = 0
for i, item in enumerate(items):
    # Find explanation within details
    m = re.search(r'class="eq-explanation">\s*<span class="eq-exp-label">Explanation</span>\s*<p>(.+?)</p>', item, re.DOTALL)
    if m:
        text = m.group(1).strip()
        # Skip generic
        if "This is a key Helm certification concept" not in text:
            count += 1
            # Show first 80 chars
            print(f"[{i+1}] {text[:120]}...")
print(f"\nTotal non-generic explanations: {count}")
