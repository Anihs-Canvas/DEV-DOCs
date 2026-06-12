#!/usr/bin/env python3
"""Quick audit of restored lfcs.html"""
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html', 'r', encoding='utf-8').read()
print(f'Size: {len(c)//1024} KB')
print(f'Chapters: {c.count("chapter-intro")}')
print(f'Practice Qs: {c.count("exam-question-item")}')
print(f'Diagrams: {c.count("diagram-container")}')
print(f'Core Understanding: {c.count("Core Understanding")}')
print(f'Generic exps: {c.count("Understanding this concept is critical")}')
checks = {
    'master-summary': 'id="master-summary"',
    'exam-strategy': 'id="exam-strategy"',
    'port-analogy': 'id="port-analogy"',
    's5-7 env profiles': 'id="s5-7"',
    's27-6 load balancer': 'id="s27-6"',
    's19-5 IPv6': 'id="s19-5"',
    's23-6 virtual FS': 'id="s23-6"',
    'Prism JS': 'prism.min.js',
    'exam-logistics': 'id="exam-logistics-official"',
    'new-topics-2026': 'id="new-topics-2026"',
}
for name, pattern in checks.items():
    print(f'{name}: {"YES" if pattern in c else "MISSING"}')
print(f'Placeholders: {c.count("Content will be added in the next phase")}')
