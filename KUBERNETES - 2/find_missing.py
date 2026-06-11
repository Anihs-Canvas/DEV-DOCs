import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(r'<div class="exam-question-item">.*?</details>\s*</div>', re.DOTALL)
blocks = pattern.findall(content)

missing = []
for b in blocks:
    if "eq-explanation" not in b:
        qm = re.search(r'<div class="eq-question">(.*?)</div>', b, re.DOTALL)
        nm = re.search(r'<div class="eq-number">(Q\d+)</div>', b)
        label = nm.group(1) if nm else "???"
        preview = qm.group(1)[:80] if qm else "???"
        missing.append(f"{label}: {preview}")

print(f"Total question blocks: {len(blocks)}")
print(f"Missing explanations: {len(missing)}")
for m in missing:
    print(f"  {m}")
