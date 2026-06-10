"""Analyze content depth per chapter — find chapters with minimal explanatory text."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== CONTENT DEPTH ANALYSIS ===\n")
for ch in range(1, 21):
    start = content.find(f'<div id="ch{ch}">')
    if start == -1: continue
    end_tag = f'<div id="ch{ch+1}">' if ch < 20 else None
    end = content.find(end_tag, start) if end_tag else len(content)
    ch_block = content[start:end]
    
    # Count content metrics
    paras = len(re.findall(r'<p>', ch_block))
    sections = len(re.findall(r'<div class="section-block"', ch_block))
    diagrams = len(re.findall(r'diagram-container', ch_block))
    code_blocks = len(re.findall(r'code-block-wrapper', ch_block))
    tables = len(re.findall(r'<table', ch_block))
    cards = len(re.findall(r'card-grid', ch_block))
    questions = len(re.findall(r'exam-question-item', ch_block))
    total_visuals = diagrams + code_blocks + tables + cards
    
    # Calculate "explanation density" — average chars of <p> text
    p_texts = re.findall(r'<p>(.*?)</p>', ch_block, re.DOTALL)
    avg_p_len = sum(len(re.sub(r'<[^>]+>', '', t).strip()) for t in p_texts) / len(p_texts) if p_texts else 0
    
    # Score: higher = better coverage
    score = paras * 2 + total_visuals * 5 + questions * 3
    
    depth = 'DEEP' if score > 100 else 'GOOD' if score > 60 else 'MODERATE' if score > 30 else 'SHALLOW'
    print(f'Ch {ch:2d}: {paras:3d} Ps, {total_visuals:2d} Vis, {sections:2d} Secs, {questions:2d} Qs, avgP={avg_p_len:.0f}ch | Score={score} [{depth}]')

# Also check the .txt for content that may be missing in .html
print("\n=== .TXT CONTENT CROSS-REFERENCE ===")
txt_path = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.txt'
with open(txt_path, 'r', encoding='utf-8') as f:
    txt = f.read()

# Find section markers in .txt and check if they exist in .html
txt_sections = re.findall(r'(?:^|\n)(#{1,4}\s+.*?)(?=\n#{1,4}\s+|\Z)', txt, re.MULTILINE)
missing = 0
for sec in txt_sections[:50]:  # Check first 50
    # Extract key terms
    terms = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}', sec)
    for term in terms[:2]:
        if len(term) > 15 and term.lower() not in content.lower():
            missing += 1
            if missing <= 10:
                print(f'  MAYBE MISSING: "{term}" from .txt not found in .html')
