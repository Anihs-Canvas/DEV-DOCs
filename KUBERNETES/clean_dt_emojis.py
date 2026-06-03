#!/usr/bin/env python3
import re
with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html", "r", encoding="utf-8") as f:
    c = f.read()

# Remove duplicated emoji from dt-yes/dt-no text spans
# Pattern: dt-icon already has ✅/❌, text span also has it
c = re.sub(
    r'(<div class="dt-yes"><span class="dt-icon">✅</span> <span>)✅ ',
    r'\1',
    c
)
c = re.sub(
    r'(<div class="dt-no"><span class="dt-icon">❌</span> <span>)❌ ',
    r'\1',
    c
)

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html", "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Cleaned duplicate emojis")
