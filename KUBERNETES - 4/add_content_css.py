#!/usr/bin/env python3
"""Compare CKAD.html CSS classes vs Backstage.html and add missing ones"""
import re

ckad = open("CKAD.html", "r", encoding="utf-8").read()
backstage = open("Backstage.html", "r", encoding="utf-8").read()

ckad_css = re.search(r"<style>(.*?)</style>", ckad, re.DOTALL).group(1)
bs_css = re.search(r"<style>(.*?)</style>", backstage, re.DOTALL).group(1)

# Find all class definitions in CKAD (with their full CSS blocks)
ckad_classes = {}
for m in re.finditer(r'(\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{[^}]+\})', ckad_css):
    cls = m.group(2)
    block = m.group(1)
    if cls not in ckad_classes:
        ckad_classes[cls] = block

# Find all class definitions already in Backstage
bs_class_names = set(re.findall(r'\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{', bs_css))

# Content-specific classes we should add (filter out K8s-specific)
content_classes = [
    # Q&A / Exam patterns
    'ckad-exam-questions', 'exam-question-item', 'eq-number', 'eq-question',
    'eq-answer', 'eq-answer-label', 'eq-explanation', 'eq-exp-label',
    # Info patterns
    'ckad-exam-tip', 'ckad-gotcha', 'ckad-speed-tip', 'ckad-verify',
    'ckad-practice-drill', 'ckad-yaml-skeleton', 'ckad-imperative-ref',
    # Gotcha patterns
    'gotcha-correct', 'gotcha-wrong',
    # CTA
    'cta-section', 'cta-paths', 'cta-path', 'cta-link', 'cta-icon',
    # Summary
    'chapter-summary-grid', 'ch-summary-card', 'ch-num', 'ch-topic-tag', 'ch-topics',
    # Card variants
    'card-control', 'card-critical', 'card-network', 'card-user', 'card-worker',
    'card-icon-lg', 'card-part-badge', 'card-subtitle', 'center-card',
    # Step colors
    'step-blue', 'step-green', 'step-orange', 'step-pink', 'step-purple', 'step-red', 'step-teal',
    # Badges
    'badge', 'badge-beginner', 'badge-intermediate', 'badge-advanced',
    'badge-exam', 'badge-observe', 'badge-part', 'badge-security',
    # Tags
    'tag-create', 'tag-delete', 'tag-update',
    # Visual
    'hero-desc', 'hero-icon', 'hero-subtitle', 'mini-icon',
    'item-desc', 'item-icon', 'item-name',
    # Drill
    'drill-scenario', 'drill-solution', 'drill-hint', 'drill-timer',
    # Decision
    'decision-tree', 'decision-node', 'decision-branch-label', 'decision-branches',
    # Relevance
    'ckad-chapter-relevance', 'relevance-domains', 'relevance-label',
    'ckad-domain-badge', 'ckad-weight', 'ckad-domain-name', 'ckad-domain-pct',
    'ckad-domain-row', 'ckad-domains', 'ckad-bar-wrap', 'ckad-bar-fill',
    'ckad-coverage',
    # Misc
    'positive', 'winner', 'diagram-container', 'diagram-title',
    'conn-line', 'has-children', 'sub-sub-toggle',
    'vs-grid', 'vs-item', 'vs-icon', 'vs-label', 'vs-detail',
    'tl-tag', 'tl-active', 'tl-danger', 'tl-warning',
]

missing_css = []
for cls in content_classes:
    if cls in ckad_classes and cls not in bs_class_names:
        missing_css.append(ckad_classes[cls])
        # Also add any combined selectors
        for m in re.finditer(rf'([^}}]*\.{cls}[^{{]*\{{[^}}]+\}})', ckad_css):
            block = m.group(1).strip()
            if block not in missing_css:
                missing_css.append(block)

print(f"Adding {len(missing_css)} CSS blocks for content classes")

if missing_css:
    insertion = "\n\n        /* ============================================\n           CONTENT PATTERNS (from CKAD.html)\n           ============================================ */\n"
    for block in missing_css:
        insertion += "        " + block + "\n"
    
    insert_pos = backstage.find("    </style>")
    if insert_pos > 0:
        new_backstage = backstage[:insert_pos] + insertion + backstage[insert_pos:]
        with open("Backstage.html", "w", encoding="utf-8") as f:
            f.write(new_backstage)
        
        import os
        size_kb = os.path.getsize("Backstage.html") / 1024
        lines = new_backstage.count('\n')
        print(f"Updated Backstage.html: {size_kb:.1f} KB, {lines} lines")
