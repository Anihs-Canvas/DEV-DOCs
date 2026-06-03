import re

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Part 3 content boundaries
# Start: the stray </section> before part3-cat1 OR the part3-cat1 section itself
# End: the "More Part 3 scenarios" paragraph

# Find the start
start_pattern = r'</section>\n\n    <section class="chapter-section" id="part3-cat1">'
m_start = re.search(start_pattern, content)
if not m_start:
    # Try without the stray </section>
    start_pattern = r'<section class="chapter-section" id="part3-cat1">'
    m_start = re.search(start_pattern, content)

# Find the end
end_pattern = r'<p style="text-align:center;color:var\(--text-muted\);padding:40px;">\s*\n\s*🧪 <strong>More Part 3 scenarios will be populated here\.</strong>\s*\n\s*</p>'
m_end = re.search(end_pattern, content)

if m_start and m_end:
    start_pos = m_start.start()
    end_pos = m_end.end()
    
    # Remove everything between start and end
    new_content = content[:start_pos] + content[end_pos:]
    
    with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    removed_len = end_pos - start_pos
    print(f'Removed {removed_len:,} chars from Part 3 content')
    print(f'Start: "{content[start_pos:start_pos+60]}..."')
    print(f'End:   "...{content[end_pos-60:end_pos]}"')
else:
    print(f'Start found: {m_start is not None}')
    print(f'End found: {m_end is not None}')
    if m_start:
        print(f'Start at: {m_start.start()}')
        print(f'Context: {content[m_start.start():m_start.start()+100]}')
    if m_end:
        print(f'End at: {m_end.start()}')
