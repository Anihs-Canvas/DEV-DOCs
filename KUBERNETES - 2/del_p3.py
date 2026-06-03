import re

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original size: {len(content):,} chars')

# === STEP 1: Remove Part 3 SIDEBAR ===
sidebar_start = content.find('<!-- PART 3: 100 SCENARIOS -->')
appendices_sidebar = content.find('<!-- APPENDICES -->', sidebar_start)

if sidebar_start > 0 and appendices_sidebar > sidebar_start:
    search_region = content[sidebar_start:appendices_sidebar]
    last_ul = search_region.rfind('</ul>')
    if last_ul > 0:
        part3_sidebar_end = sidebar_start + last_ul + len('</ul>')
        content = content[:sidebar_start] + content[part3_sidebar_end:]
        print(f'Removed Part 3 sidebar ({part3_sidebar_end - sidebar_start:,} chars)')
    else:
        print('ERROR: Could not find closing </ul> for sidebar Part 3')
else:
    print(f'ERROR: sidebar_start={sidebar_start}, appendices_sidebar={appendices_sidebar}')

# === STEP 2: Remove Part 3 CONTENT ===
# Find the stray </section> before part3-cat1
stray_section = content.find('</section>\n\n    <section class="chapter-section" id="part3-cat1">')
if stray_section < 0:
    stray_section = content.find('<section class="chapter-section" id="part3-cat1">')

end_marker = content.find('More Part 3 scenarios will be populated here.')

if stray_section > 0 and end_marker > stray_section:
    end_p = content.find('</p>', end_marker)
    if end_p > 0:
        end_pos = content.find('\n', end_p)
        if end_pos < 0:
            end_pos = end_p + 4
        else:
            end_pos = end_pos + 1
        
        # Include stray </section> if present
        pre_stray = content.rfind('</section>', 0, stray_section)
        if pre_stray > 0 and 'ts-sm1' in content[pre_stray-100:stray_section]:
            actual_start = pre_stray
        else:
            actual_start = stray_section
        
        content = content[:actual_start] + '\n' + content[end_pos:]
        print(f'Removed Part 3 content ({end_pos - actual_start:,} chars)')
    else:
        print('ERROR: Could not find closing </p> after end marker')
else:
    print(f'ERROR: stray_section={stray_section}, end_marker={end_marker}')

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Final size: {len(content):,} chars')
print('Done!')
