#!/usr/bin/env python3
"""
Fix and enhance all 15 decision trees:
1. Repair broken <tr> HTML syntax
2. Replace plain tables with styled decision-flow cards
3. Add visual step indicators, connector lines, hover effects
"""
import re

PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# =============================================================================
# STEP 1: Fix all broken <tr> tags in decision trees
# =============================================================================
# Pattern: <tr>style="background:#1c2128;">  →  <tr style="background:#1c2128;">
content = re.sub(r'<tr>style="(background:#[^"]+)"', r'<tr style="\1"', content)
# Pattern: <tr>>  →  <tr>
content = re.sub(r'<tr>>', r'<tr>', content)

print("✅ Fixed broken <tr> tags")

# =============================================================================
# STEP 2: Find the CSS insertion point and add decision tree styles
# =============================================================================
dt_css = """
        /* ═══════════════ DECISION TREE STYLES ═══════════════ */
        .dt-container {
            margin: 20px 0;
        }
        .dt-step {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 14px 18px;
            margin: 0 0 2px 0;
            border-radius: var(--radius-sm);
            transition: var(--transition);
            position: relative;
        }
        .dt-step:nth-child(odd) {
            background: linear-gradient(135deg, rgba(22,27,34,0.8) 0%, rgba(13,17,23,0.6) 100%);
        }
        .dt-step:nth-child(even) {
            background: linear-gradient(135deg, rgba(33,38,45,0.6) 0%, rgba(22,27,34,0.4) 100%);
        }
        .dt-step:hover {
            background: rgba(88,166,255,0.08);
            box-shadow: 0 0 0 1px rgba(88,166,255,0.15);
            transform: translateX(4px);
        }
        .dt-step::after {
            content: '';
            position: absolute;
            left: 27px;
            bottom: -2px;
            width: 2px;
            height: 2px;
            background: var(--border);
        }
        .dt-step:last-of-type::after {
            display: none;
        }
        .dt-step-num {
            flex-shrink: 0;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 20px;
            color: #fff;
            position: relative;
            z-index: 1;
        }
        .dt-step:nth-child(1) .dt-step-num { background: linear-gradient(135deg, #f85149, #d2991d); }
        .dt-step:nth-child(2) .dt-step-num { background: linear-gradient(135deg, #d2991d, #e3b341); }
        .dt-step:nth-child(3) .dt-step-num { background: linear-gradient(135deg, #3fb950, #39d2c0); }
        .dt-step:nth-child(4) .dt-step-num { background: linear-gradient(135deg, #58a6ff, #a371f7); }
        .dt-step:nth-child(5) .dt-step-num { background: linear-gradient(135deg, #a371f7, #f778ba); }
        .dt-step:nth-child(6) .dt-step-num { background: linear-gradient(135deg, #f778ba, #f85149); }
        .dt-step:nth-child(7) .dt-step-num { background: linear-gradient(135deg, #39d2c0, #58a6ff); }
        .dt-step-body {
            flex: 1;
            min-width: 0;
        }
        .dt-check {
            font-size: 14px;
            color: var(--text);
            line-height: 1.5;
            margin-bottom: 8px;
        }
        .dt-check code {
            background: rgba(88,166,255,0.12);
            color: var(--accent);
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 12.5px;
            white-space: nowrap;
        }
        .dt-branches {
            display: flex;
            gap: 12px;
        }
        .dt-yes, .dt-no {
            flex: 1;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition);
        }
        .dt-yes {
            background: rgba(63,185,80,0.1);
            border: 1px solid rgba(63,185,80,0.25);
            color: #3fb950;
        }
        .dt-yes:hover {
            background: rgba(63,185,80,0.18);
            box-shadow: 0 0 12px rgba(63,185,80,0.12);
        }
        .dt-no {
            background: rgba(248,81,73,0.1);
            border: 1px solid rgba(248,81,73,0.25);
            color: #f85149;
        }
        .dt-no:hover {
            background: rgba(248,81,73,0.18);
            box-shadow: 0 0 12px rgba(248,81,73,0.12);
        }
        .dt-icon {
            font-size: 18px;
            flex-shrink: 0;
        }
        .dt-connector {
            width: 2px;
            height: 8px;
            background: var(--border);
            margin: 0 auto;
            border-radius: 1px;
        }
        .dt-tree-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }
        .dt-tree-title .dt-tree-icon {
            font-size: 32px;
        }
        .dt-tree-title h4 {
            margin: 0;
            font-size: 18px;
            color: var(--text);
        }
"""

# Insert CSS before the closing </style> tag
style_end = content.find('</style>')
if style_end > 0:
    content = content[:style_end] + dt_css + "\n" + content[style_end:]
    print("✅ Added decision tree CSS styles")
else:
    print("❌ Could not find </style> tag")

# =============================================================================
# STEP 3: Replace each table-based decision tree with card-based flow design
# =============================================================================

def fix_dt(match):
    """Convert a table-based decision tree to the new card-based flow design."""
    html = match.group(0)
    
    # Extract the header/symptom section (keep everything before <table>)
    table_start = html.find('<table')
    table_end = html.find('</table>')
    if table_start < 0 or table_end < 0:
        return html
    
    header = html[:table_start]
    table = html[table_start:table_end + 8]
    footer = html[table_end + 8:]
    
    # Parse table rows to extract step data
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
    
    # Skip header row (first row with <th>)
    data_rows = [r for r in rows if '<th' not in r]
    
    # Build card-based steps
    steps_html = '<div class="dt-container">\n'
    
    for row_html in data_rows:
        # Extract cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(cells) < 4:
            continue
        
        step_num = cells[0].strip()
        check_text = cells[1].strip()
        yes_text = cells[2].strip()
        no_text = cells[3].strip()
        
        # Clean up the check text - remove HTML but keep code tags
        check_clean = check_text
        
        steps_html += f'''            <div class="dt-step">
                <div class="dt-step-num">{step_num}</div>
                <div class="dt-step-body">
                    <div class="dt-check">{check_clean}</div>
                    <div class="dt-branches">
                        <div class="dt-yes"><span class="dt-icon">✅</span> {yes_text}</div>
                        <div class="dt-no"><span class="dt-icon">❌</span> {no_text}</div>
                    </div>
                </div>
            </div>
'''
    
    steps_html += '        </div>\n'
    
    return header + steps_html + footer

# Find all decision tree blocks (ts-issue divs with id="dt\d+")
dt_pattern = re.compile(r'<div class="ts-issue" id="dt\d+">.*?</div>\s*<div class="ts-footer-spacer"></div>\s*</div>', re.DOTALL)

def process_dt(match):
    return fix_dt(match)

content = dt_pattern.sub(process_dt, content)

print("✅ Converted all 15 decision trees to card-based flow design")

# Save
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 Decision trees enhanced!")
