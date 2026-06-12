#!/usr/bin/env python3
"""Analyze which chapters have generic explanations."""
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html', 'r', encoding='utf-8') as f:
    content = f.read()

generic = '<strong>💡 Explanation:</strong> Understanding this concept is critical for the LFCS exam.'

# Find all chapters and count generic vs unique explanations per chapter
chapter_pattern = r'<div class="chapter-intro"><h3>Chapter (\d+):'
chapters = re.findall(chapter_pattern, content)

# For each chapter, find its questions and explanations
for ch_num in chapters:
    # Find the chapter block
    ch_match = re.search(rf'Chapter {ch_num} — LFCS Practice Questions</h4>(.*?)(?=<div class="chapter-intro">|$)', content, re.DOTALL)
    if not ch_match:
        continue
    
    ch_block = ch_match.group(1)
    questions = len(re.findall(r'<div class="exam-question-item">', ch_block))
    generics = len(re.findall(re.escape(generic), ch_block))
    
    if questions > 0:
        status = '⚠️ ALL GENERIC' if generics == questions else f'{generics}/{questions} generic' if generics > 0 else '✅ ALL UNIQUE'
        print(f'Ch {ch_num}: {questions} qs — {status}')
