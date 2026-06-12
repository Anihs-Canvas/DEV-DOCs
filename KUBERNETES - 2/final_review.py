#!/usr/bin/env python3
"""Final comprehensive review of lfcs.html"""
import re, os

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html'
with open(filepath, 'r', encoding='utf-8') as f:
    c = f.read()

sz = os.path.getsize(filepath)

print('=' * 60)
print('  LFCS.HTML — FINAL COMPREHENSIVE REVIEW')
print('=' * 60)

# Document stats
print('\n📊 DOCUMENT STATS')
print(f'  File size:      {sz//1024:,} KB ({sz:,} bytes)')
print(f'  Total lines:    {c.count(chr(10)):,}')
print(f'  Total chars:    {len(c):,}')
divs = c.count('<div')
pres = c.count('<pre>')
tabs = c.count('<table')
print(f'  <div> blocks:   {divs:,}')
print(f'  <pre> blocks:   {pres:,}')
print(f'  <table> blocks: {tabs:,}')

# Content coverage
print('\n📚 CONTENT COVERAGE')
chs = re.findall(r'Chapter (\d+):', c)
h4s = re.findall(r'<h4>Chapter (\d+)', c)
questions = c.count('exam-question-item')
diagrams = c.count('diagram-container')
explanations = c.count('eq-explanation')
core_understandings = c.count('Core Understanding')
exam_prep_cards = c.count('LFCS Exam Preparation')
visual_summaries = c.count('visual-summary')

print(f'  Chapter headings (h3):  {len(chs)}  (Ch {chs[0] if chs else "?"}-{chs[-1] if chs else "?"})')
print(f'  Practice Q headings:    {len(h4s)} (Ch {h4s[0] if h4s else "?"}-{h4s[-1] if h4s else "?"})')
print(f'  Exam question blocks:   {questions}')
print(f'  Explanation blocks:     {explanations}')
print(f'  Diagram containers:     {diagrams}')
print(f'  Core Understanding:     {core_understandings}')
print(f'  Exam Prep Cards:        {exam_prep_cards}')
print(f'  Visual Summaries:       {visual_summaries}')

# Content per chapter
print('\n📋 PER-CHAPTER AUDIT')
issues = []
for ch in range(1, 46):
    has_ch = f'id="ch{ch}"' in c
    has_h4 = f'Chapter {ch} — LFCS Practice Questions</h4>' in c
    has_intro = f'Chapter {ch}:' in c
    if not has_ch:
        issues.append(f'Ch {ch}: MISSING id="ch{ch}"')
    if not has_h4:
        issues.append(f'Ch {ch}: MISSING practice questions')
    if not has_intro:
        issues.append(f'Ch {ch}: MISSING chapter-intro')
    
    if ch in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]:
        status = '✅' if (has_ch and has_h4 and has_intro) else '❌'
        m = re.search(rf'Chapter {ch} — LFCS Practice Questions</h4>', c)
        if m:
            end = c.find('Chapter ', m.end())
            block = c[m.end():end] if end > 0 else c[m.end():]
            q_count = block.count('exam-question-item')
            exp_count = block.count('eq-explanation')
            d_count = block.count('diagram-container')
            # Get topic
            topic_m = re.search(r'eq-explanation.*?<p><strong>(.*?)</strong>', block, re.DOTALL)
            topic = topic_m.group(1)[:40] if topic_m else '???'
            print(f'  Ch {ch:2d}: {status} {q_count}qs | {exp_count}exps | {d_count}diagrams | Topic: {topic}')

if issues:
    print(f'\n⚠️  ISSUES FOUND ({len(issues)}):')
    for i in issues[:10]:
        print(f'  - {i}')
    if len(issues) > 10:
        print(f'  ... and {len(issues)-10} more')
else:
    print(f'\n✅ No structural issues found')

# Appendices
print('\n📎 APPENDICES')
appendix_anchors = []
for letter in 'ABCDEFGHIJ':
    aid = f'appendix-{letter.lower()}'
    has_content = f'id="{aid}"' in c
    has_sidebar = f'href="#{aid}"' in c
    appendix_anchors.append((letter, has_content, has_sidebar))
    status = '✅' if (has_content and has_sidebar) else '⚠️ CONTENT' if has_content else '⚠️ SIDEBAR' if has_sidebar else '❌ MISSING'
    print(f'  Appendix {letter}: {status}')

# Pre-Chapter 1 sections
print('\n📋 PRE-CHAPTER SECTIONS')
pres = [
    ('master-summary', 'Master Summary & Roadmap'),
    ('exam-logistics-official', 'Official Exam Logistics'),
    ('exam-strategy', 'LFCS Exam Strategy'),
    ('new-topics-2026', 'New 2026 Topics'),
    ('port-analogy', 'Shipping Port Analogy'),
    ('exam-quick-ref', 'Exam Quick Reference'),
    ('last-minute-review', 'Last-Minute Review'),
]
for pid, pname in pres:
    has_content = f'id="{pid}"' in c
    has_sidebar = f'href="#{pid}"' in c
    status = '✅' if (has_content and has_sidebar) else '⚠️'
    print(f'  {pname}: {status}')

# Quality checks
print('\n🔍 QUALITY CHECKS')
placeholders = c.count('Content will be added in the next phase')
generic_exps = c.count('Understanding this concept is critical for the LFCS exam')
print(f'  Placeholders remaining:    {placeholders}')
print(f'  Generic explanations left: {generic_exps}')

# Explanation depth
exp_texts = re.findall(r'eq-exp-label.*?Explanation</div>\s*<p>(.*?)</p>', c, re.DOTALL)
if exp_texts:
    lengths = [len(t) for t in exp_texts]
    print(f'  Explanation count:        {len(exp_texts)}')
    print(f'  Min/Max/Avg length:       {min(lengths)}/{max(lengths)}/{sum(lengths)//len(lengths)} chars')

# Sidebar
sidebar_sections = len(re.findall(r'part-header', c))
print(f'\n📑 SIDEBAR')
print(f'  Part headers:    {sidebar_sections}')
print(f'  Chapter links:   {c.count("chapter-link")}')
print(f'  Sub-toc links:   {c.count("sub-toc")}')

print('\n' + '=' * 60)
print('  REVIEW COMPLETE')
print('=' * 60)
