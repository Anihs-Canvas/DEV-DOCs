#!/usr/bin/env python3
"""Extract ALL structural patterns from CKAD.html and cka.html"""
import re

for fname in ["CKAD.html", "cka.html"]:
    html = open(fname, "r", encoding="utf-8").read()
    print(f"\n{'='*80}")
    print(f"  {fname} — STRUCTURAL ANALYSIS")
    print(f"{'='*80}")
    print(f"  Size: {len(html)/1024:.0f} KB, Lines: {html.count(chr(10))}")
    
    # 1. Header structure
    h_match = re.search(r'<header>(.*?)</header>', html, re.DOTALL)
    if h_match:
        h = h_match.group(1)
        h1 = re.search(r'<h1>(.*?)</h1>', h)
        sub = re.search(r'class="subtitle">(.*?)</p>', h)
        desc = re.search(r'class="description">(.*?)</p>', h)
        tags = re.findall(r'<span class="tag[^"]*">([^<]+)</span>', h)
        print(f"\n  HEADER:")
        print(f"    h1: {h1.group(1)[:80] if h1 else 'N/A'}")
        print(f"    subtitle: {sub.group(1)[:80] if sub else 'N/A'}")
        print(f"    description: {desc.group(1)[:80] if desc else 'N/A'}")
        print(f"    tags ({len(tags)}): {', '.join(tags)}")
    
    # 2. Sidebar structure
    sb_start = html.find('<nav class="toc-sidebar"')
    sb_end = html.find('</nav>', sb_start) + 6
    sidebar = html[sb_start:sb_end]
    parts = re.findall(r'<span class="part-title"><span>([^<]+)</span>', sidebar)
    chapters = re.findall(r'class="chapter-link"[^>]*>([^<]+)</a>', sidebar)
    sub_tocs = re.findall(r'class="sub-toc">(.*?)</ul>', sidebar, re.DOTALL)
    print(f"\n  SIDEBAR:")
    print(f"    Parts: {len(parts)}")
    for p in parts:
        print(f"      - {p[:60]}")
    print(f"    Chapter links: {len(chapters)}")
    print(f"    Sub-toc groups: {len(sub_tocs)}")
    
    # 3. Main content - find all chapter sections
    ch_sections = re.findall(r'<section id="ch(\d+)"', html)
    app_sections = re.findall(r'<section id="app-([a-h])"', html)
    front_sections = re.findall(r'<section id="(front-[^"]+)"', html)
    master = 'id="master-summary"' in html
    
    print(f"\n  MAIN CONTENT SECTIONS:")
    print(f"    Chapters (ch1-chX): {len(ch_sections)}")
    print(f"    Appendices (app-a to app-h): {len(app_sections)}")
    print(f"    Front-matter sections: {front_sections}")
    print(f"    Master summary: {master}")
    
    # 4. Content block types used
    block_types = {}
    for pattern_name, pattern in [
        ("chapter-intro", r'<div class="chapter-intro"'),
        ("learning-objectives", r'<div class="learning-objectives"'),
        ("diagram-box", r'<div class="diagram-box'),
        ("info-box", r'<div class="info-box'),
        ("info-table", r'<table class="info-table"'),
        ("card-grid", r'<div class="card-grid"'),
        ("info-card", r'<div class="info-card"'),
        ("split-panel", r'<div class="split-panel"'),
        ("scenario-box", r'<div class="scenario-box"'),
        ("summary-box", r'<div class="summary-box"'),
        ("code-block-wrapper", r'<div class="code-block-wrapper"'),
        ("prereq-box", r'<div class="prereq-box"'),
        ("exam-question-item", r'<div class="exam-question-item"'),
        ("drill-scenario", r'<div class="drill-scenario"'),
        ("note", r'<div class="note"'),
        ("tip", r'<div class="tip"'),
        ("warning", r'<div class="warning"'),
        ("danger", r'<div class="danger"'),
        ("callout-enhanced", r'<div class="callout-enhanced"'),
        ("highlight-box", r'<div class="highlight-box"'),
        ("skeleton-note", r'<div class="skeleton-note"'),
        ("icon-feature", r'<div class="icon-feature"'),
        ("timeline-item", r'<div class="timeline-item"'),
        ("process-steps", r'<div class="process-steps"'),
        ("cta-section", r'<div class="cta-section"'),
        ("visual-summary", r'<div class="visual-summary"'),
        ("prereq-grid", r'<div class="prereq-grid"'),
        ("relationship-map", r'<div class="relationship-map"'),
    ]:
        count = len(re.findall(pattern, html))
        if count > 0:
            block_types[pattern_name] = count
    
    print(f"\n  CONTENT BLOCKS USED:")
    for name, count in sorted(block_types.items(), key=lambda x: -x[1]):
        print(f"    {name}: {count}x")
    
    # 5. Practice questions pattern
    q_count = len(re.findall(r'Q\d+:', html))
    lab_count = len(re.findall(r'Lab:', html))
    print(f"\n  PRACTICE QUESTIONS:")
    print(f"    Total Q#: references: {q_count}")
    print(f"    Lab: references: {lab_count}")
    
    # 6. Footer structure
    ft_match = re.search(r'<footer>(.*?)</footer>', html, re.DOTALL)
    if ft_match:
        ft = ft_match.group(1)
        ft_sections = re.findall(r'<h3>([^<]+)</h3>', ft)
        print(f"\n  FOOTER SECTIONS: {len(ft_sections)}")
        for fs in ft_sections:
            print(f"    - {fs[:60]}")
    
    # 7. Section block structure (h3/h4 pattern)
    h3_count = len(re.findall(r'<h3[^>]*>', html[html.find('<main>'):html.find('<footer>')]))
    h4_count = len(re.findall(r'<h4[^>]*>', html[html.find('<main>'):html.find('<footer>')]))
    section_blocks = len(re.findall(r'class="section-block"', html))
    print(f"\n  CONTENT STRUCTURE (main area):")
    print(f"    h3 tags: {h3_count}")
    print(f"    h4 tags: {h4_count}")
    print(f"    section-block divs: {section_blocks}")
    
    # 8. Pre/code usage
    pre_count = len(re.findall(r'<pre>', html[html.find('<main>'):]))
    code_count = len(re.findall(r'<code>', html[html.find('<main>'):]))
    print(f"\n  CODE USAGE (main area):")
    print(f"    <pre> blocks: {pre_count}")
    print(f"    <code> inline: {code_count}")
    
    print()
