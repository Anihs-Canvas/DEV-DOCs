import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "r", encoding="utf-8") as f:
    content = f.read()

# More flexible pattern to catch all question formats
pattern = re.compile(r'<div class="exam-question-item">.*?</details>', re.DOTALL)
blocks = pattern.findall(content)

all_eq = content.count("exam-question-item")
all_ex = content.count("eq-explanation")

missing = []
for b in blocks:
    if "eq-explanation" not in b:
        qm = re.search(r'<div class="eq-question">(.*?)</div>', b, re.DOTALL)
        nm = re.search(r'<div class="eq-number">(Q\d+)</div>', b)
        label = nm.group(1) if nm else "???"
        preview = qm.group(1)[:80] if qm else "???"
        missing.append(f"{label}: {preview}")

print(f"exam-question-item tags: {all_eq}")
print(f"eq-explanation tags: {all_ex}")
print(f"Regex matched blocks: {len(blocks)}")
print(f"Missing in regex: {len(missing)}")
print(f"Missing total (tags - explanations): {all_eq - all_ex}")
if missing:
    for m in missing:
        print(f"  {m}")
else:
    print("  None found by regex pattern")
    print("  The 14 missing explanations may be in special format questions")
    # Check for <details> without closing </details>
    no_close = content.count("<details>") - content.count("</details>")
    print(f"  Unclosed <details> tags: {no_close}")
