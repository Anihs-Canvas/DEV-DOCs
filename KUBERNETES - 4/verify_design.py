#!/usr/bin/env python3
"""Verify Backstage.html visual design matches cka.html/CKAD.html"""
import re

for ref_name in ["CKAD.html", "cka.html"]:
    ref = open(ref_name, "r", encoding="utf-8").read()
    bk = open("Backstage.html", "r", encoding="utf-8").read()
    
    # Extract key CSS values for comparison
    def get_css_val(html, prop):
        m = re.search(rf'{prop}:\s*([^;]+);', html)
        return m.group(1).strip() if m else "N/A"
    
    print(f"\n=== {ref_name} vs Backstage.html ===")
    checks = [
        ("Body bg", "background", "#0d1117"),
        ("Body text color", "color", "#e4e4e7"),
        ("Header accent", "border-bottom", "3px solid #326ce5"),
        ("Sidebar width", "width", "340px"),
        ("Sidebar bg", "background", "#161b22"),
        ("H1 color", "color", "#60a5fa"),
        ("Chapter link hover color", "color", "#60a5fa"),
        ("tag bg", "background", "rgba(50, 108, 229, 0.3)"),
        ("Toggle btn gradient", "background", "linear-gradient(135deg, #1e3a5f 0%, #326ce5 100%)"),
    ]
    for name, prop, expected in checks:
        ref_val = get_css_val(ref, prop)
        bk_val = get_css_val(bk, prop)
        match = "MATCH" if expected in ref_val and expected in bk_val else "DIFF"
        print(f"  [{match}] {name}: ref={ref_val[:50]} | bk={bk_val[:50]}")

# Verify key HTML structure patterns
print("\n\n=== HTML STRUCTURE VERIFICATION ===")
patterns = [
    ("Header with gradient", "<header>"),
    ("TOC toggle button", 'class="toc-toggle"'),
    ("Sidebar nav", 'class="toc-sidebar"'),
    ("Part headers collapsible", 'class="part-header" onclick="togglePart(this)"'),
    ("Chapter links with sub-toc", 'class="section-toggle-btn"'),
    ("chapter-intro div", 'class="chapter-intro"'),
    ("learning-objectives div", 'class="learning-objectives"'),
    ("diagram-box with pre", '<pre>'),
    ("info-box note", 'class="info-box'),
    ("exam-question-item", 'exam-question-item'),
    ("Footer 3 columns", 'class="footer-content"'),
    ("JS toggle functions", 'function toggleTOC'),
    ("Body starts toc-open", 'class="toc-open"'),
]
for name, pattern in patterns:
    found = pattern in bk
    print(f"  [{'OK' if found else 'MISSING'}] {name}")

print("\nVisual design verification complete.")
