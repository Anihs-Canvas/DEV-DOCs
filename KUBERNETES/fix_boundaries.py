import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
fixes = 0

# Fix 1: Find all broken div tags where Practice & Lab Sections got inserted between <div and id="chN">
# Pattern: <div \n                <!-- Practice & Lab Sections -->\n...content...\n                    </div>\nid="chN">
pattern = re.compile(
    r'(<div )\n\s*(<!-- Practice & Lab Sections -->\n<div class="cka-exam-questions">.*?</div>\n\s*</div>\n\s*</div>\n\s*</div>\n\s*)\n?(id="ch\d+">)',
    re.DOTALL
)

matches = list(pattern.finditer(html))
print("Found {} broken chapter opening tags".format(len(matches)))

# Remove the misplaced content and fix the div tag
# Process in reverse to preserve positions
for m in reversed(matches):
    before_div = m.group(1)  # '<div '
    misplaced = m.group(2)   # the Q&A content
    after_id = m.group(3)    # 'id="chN">'
    
    # Replace with proper <div id="chN">
    html = html[:m.start()] + '<div ' + after_id + html[m.end():]
    fixes += 1

print("Fixed {} broken chapter divs".format(fixes))

# Fix 2: Ch17 still has visual-summary after cka-exam-questions inside the chapter
# Let's find Ch17 and move its visual-summary before its cka-exam-questions
ch17_start = html.find('id="ch17"')
ch18_start = html.find('id="ch18"')
if ch17_start > 0 and ch18_start > ch17_start:
    ch17_html = html[ch17_start:ch18_start]
    
    # Find visual-summary
    vs_match = re.search(r'<div class="visual-summary">', ch17_html)
    qa_match = re.search(r'<div class="cka-exam-questions">', ch17_html)
    
    if vs_match and qa_match:
        # Check if visual-summary is AFTER cka-exam-questions
        if vs_match.start() > qa_match.start():
            # Extract visual-summary
            vs_start = ch17_start + vs_match.start()
            # Find matching closing </div>
            depth = 1
            pos = vs_match.end()
            while depth > 0 and pos < len(ch17_html):
                no = ch17_html.find('<div', pos)
                nc = ch17_html.find('</div>', pos)
                if nc < 0: break
                if no >= 0 and no < nc:
                    depth += 1
                    pos = no + 4
                else:
                    depth -= 1
                    if depth == 0:
                        vs_end = ch17_start + nc + len('</div>')
                    pos = nc + len('</div>')
            
            if depth == 0:
                vs_text = html[vs_start:vs_end]
                # Remove from current position
                html = html[:vs_start] + html[vs_end:]
                ch18_start -= (vs_end - vs_start)
                # Find cka-exam-questions position again
                qa_start = html.find('<div class="cka-exam-questions">', ch17_start)
                # Insert visual-summary BEFORE Q&A
                html = html[:qa_start] + vs_text + '\n                ' + html[qa_start:]
                fixes += 1
                print("Ch17: Moved visual-summary before Q&A")

if fixes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal fixes applied: {}".format(fixes))
    print("File updated. Lines: {}".format(html.count('\n')))
else:
    print("\nNo fixes needed.")
