import re

# Read helm.txt sections
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

# Read helm.html
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all subsection numbers from helm.txt (like 1.1, 1.2, 3.1a, etc.)
txt_sections = set()
for m in re.finditer(r'(\d+\.\d+[a-z]?)\s', txt):
    txt_sections.add(m.group(1))

# Check which exist in HTML as h4 or section headings
missing = []
for sec in sorted(txt_sections, key=lambda s: [int(x) if x.isdigit() else (ord(x[0])*1000) for x in re.split(r'[.a-z]', s) if x]):
    # Look for the section number in HTML headings
    patterns = [
        r'>\s*' + re.escape(sec) + r'\s',
        r'"\s*' + re.escape(sec) + r'\s',
        sec + r'\.',
        sec + r'\s',
    ]
    found = any(re.search(p, html) for p in patterns)
    if not found:
        missing.append(sec)

print("=== Sections in helm.txt but potentially MISSING or THIN in helm.html ===\n")
for sec in missing:
    # Find what section this is from helm.txt
    for line in txt.split('\n'):
        if sec in line and (sec + ' ' in line or sec + '\t' in line or line.strip().startswith(sec)):
            print("{} -> {}".format(sec, line.strip()[:120]))
            break

print("\nTotal txt sections: {}".format(len(txt_sections)))
print("Potentially missing/thin: {}".format(len(missing)))

# Also check which chapters are thinnest
print("\n=== Chapter Line Counts ===\n")
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 20 else 'id="appendix-a"'
    ch_start = html.find(cid)
    ch_end = html.find(ncid, ch_start+1) if ch_start >= 0 else -1
    if ch_start >= 0 and ch_end > 0:
        lines = html[ch_start:ch_end].count('\n')
        # Count distinct section blocks
        sections = len(re.findall(r'class="section-block"', html[ch_start:ch_end]))
        print("Ch{:2d}: {:4d} lines, {:2d} section-blocks".format(ch, lines, sections))
