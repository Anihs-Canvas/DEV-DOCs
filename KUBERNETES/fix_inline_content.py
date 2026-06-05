import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

print("Applying comprehensive formatting fixes to S11-S40...")

# Fix 1: Inline sc-answer opening: <div class="sc-answer" id="sc-sa{N}"><h5>
# Replace with multi-line format
p1 = r'(<div class="sc-answer" id="sc-sa\d+)("><h5>)'
c1 = len(re.findall(p1, h))
h = re.sub(p1, r'\1">\n                \2', h)
print(f"  Fixed {c1} inline sc-answer(s)")

# Fix 2: Inline fix dropdown: <div class="sc-answer" id="sc-s{N}-fix-drop"><div class="code-block"><div class="code-header">
p2 = r'(<div class="sc-answer" id="sc-s\d+-fix-drop")(><div class="code-block"><div class="code-header">)'
c2 = len(re.findall(p2, h))
h = re.sub(p2, r'\1>\n                        <div class="code-block">\n                        <div class="code-header">', h)
print(f"  Fixed {c2} inline fix dropdown(s)")

# Fix 3: Inline cleanup dropdown: <div class="sc-answer" id="sc-s{N}-cleanup-drop"><div class="code-block"><div class="code-header">
p3 = r'(<div class="sc-answer" id="sc-s\d+-cleanup-drop")(><div class="code-block"><div class="code-header">)'
c3 = len(re.findall(p3, h))
h = re.sub(p3, r'\1>\n                        <div class="code-block">\n                        <div class="code-header">', h)
print(f"  Fixed {c3} inline cleanup dropdown(s)")

# Fix 4: </div></div> closing sc-step-content + sc-step on same line
# This is the pattern at end of sc-step blocks. We want:
# OLD:             </div></div>
# NEW:             </div>
#                </div>
# But we need to be careful - only fix this within scenario blocks
p4 = r'(\s{12})</div></div>\n(\s{12})<div class="sc-step'
c4 = len(re.findall(p4, h))
h = re.sub(p4, r'\1</div>\n            </div>\n\2<div class="sc-step', h)
print(f"  Fixed {c4} inline sc-step closings")

# Also fix the LAST sc-step closing before sc-body closing
p4b = r'(\s{12})</div></div>\n(\s{8})</div>\n(\s{4})</div>'
c4b = len(re.findall(p4b, h))
h = re.sub(p4b, r'\1</div>\n            </div>\n\2</div>\n\3</div>', h)
print(f"  Fixed {c4b} final sc-step closings")

# Fix 5: Inline tenet-flow opening (after h5)
# OLD: <h5>...THOUGHT PROCESS</h5><div class="tenet-flow">
# NEW: <h5>...THOUGHT PROCESS</h5>\n                <div class="tenet-flow">
# But only for the Diagnostic Tenet heading
p5 = r'(<h5>🧠 Diagnostic Tenet \(Thought Process\)</h5>)(<div class="tenet-flow">)'
c5 = len(re.findall(p5, h))
h = re.sub(p5, r'\1\n                \2', h)
print(f"  Fixed {c5} inline tenet-flow openings")

# Fix 6: Inline sc-step opening (sc-step and sc-step-content on same line with sc-step-num)
# OLD: <div class="sc-step"><div class="sc-step-num ...
# This one is tricky. Let me check if it's really an issue.
# Actually, looking at S1: <div class="sc-step"><div class="sc-step-num deploy">1</div><div class="sc-step-content">
# This is the SAME in S1! So this is fine, leave it.

# Fix 7: Inline pre/code closing with </div> for code-block
# OLD: </code></pre></div>
# This is actually fine in S1 too. Let me check...

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("\nDone! Running verification...")
