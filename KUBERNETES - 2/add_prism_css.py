#!/usr/bin/env python3
"""Final safe fix: add Prism CSS overrides."""
import os

fp = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

css = '''
        /* Prism.js syntax highlighting */
        pre[class*="language-"] code[class*="language-"],
        pre code[class*="language-"] { color: inherit !important; background: transparent !important; }
        pre.diagram-ascii, pre.diagram-ascii code { color: #c9d1d9 !important; }
        .token.comment,.token.prolog,.token.doctype,.token.cdata { color: #8b949e; }
        .token.punctuation { color: #c9d1d9; }
        .token.property,.token.tag,.token.boolean,.token.number,.token.constant,.token.symbol,.token.deleted { color: #79c0ff; }
        .token.selector,.token.attr-name,.token.string,.token.char,.token.builtin,.token.inserted { color: #a5d6ff; }
        .token.operator,.token.entity,.token.url { color: #d2a8ff; }
        .token.atrule,.token.attr-value,.token.keyword { color: #ff7b72; }
        .token.function,.token.class-name { color: #d2a8ff; }
        .token.regex,.token.important,.token.variable { color: #ffa657; }
'''

last_style = c.rfind('</style>')
insert_pos = c.rfind('\n    ', 0, last_style)
c = c[:insert_pos] + css + '\n' + c[insert_pos:]

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

sz = os.path.getsize(fp)
q = c.count('exam-question-item')
print(f'Done! Size: {sz//1024} KB | Questions: {q}')
print(f'Anchors OK: ch1={"id=\"ch1\"" in c}, ch45={"id=\"ch45\"" in c}')
