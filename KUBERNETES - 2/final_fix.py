with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix S1 indentation
c = c.replace(
    '            <div class="scenario-block" id="s1">\n        <div class="sc-header">\n            <div class="sc-badge">S1</div>\n            <div class="sc-header-content">',
    '    <div class="scenario-block" id="s1">\n        <div class="sc-header">\n            <div class="sc-badge">S1</div>\n            <div class="sc-header-content">'
)

# Add diagram before S1
diagram = '''
        <div class="diagram-container">
            <div class="diagram-title">🏗️ Part 3 Labs — Architecture Troubleshooting Workflow</div>
            <pre>
  ┌──────────────────────────────────────────────────────────────────┐
  │           ARCHITECTURE LAB SCENARIOS — LEARNING PATH              │
  │                                                                  │
  │  S1-S5:    CORE NETWORKING                                       │
  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐       │
  │  │ Deploy   │ Cross-   │ Service  │ DNS      │ Agent    │       │
  │  │ anihpj   │ Node     │ Selector │ Failure  │ Crash    │       │
  │  │ on Cilium│ Failure  │ Mismatch │ (CNP)    │ Loop     │       │
  │  └──────────┴──────────┴──────────┴──────────┴──────────┘       │
  │                                                                  │
  │  S6-S10:   IDENTITY &amp; SECURITY                                  │
  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐       │
  │  │ Identity │ Endpoint │ WireGuard│ Host FW  │ Verify   │       │
  │  │ Mismatch │ Create   │ Not      │ Lockout  │ Encrypt  │       │
  │  │          │ Failure  │ Active   │ Recovery │ (Hubble) │       │
  │  └──────────┴──────────┴──────────┴──────────┴──────────┘       │
  │                                                                  │
  │  S11-S20:  ADVANCED TROUBLESHOOTING                              │
  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐       │
  │  │ Mixed OS │ Operator │ IPAM     │ TLS Cert │ Identity │       │
  │  │ Nodes    │ Down     │ Exhaust  │ SAN      │ GC Bug   │       │
  │  ├──────────┼──────────┼──────────┼──────────┼──────────┤       │
  │  │ API      │ MTU      │ Health   │ ConfigMap│ NodePort │       │
  │  │ Server   │ Blackhole│ Endpoint │ Restart  │ External │       │
  │  └──────────┴──────────┴──────────┴──────────┴──────────┘       │
  │                                                                  │
  │  FORMAT: YAML → Apply → Debug → Command Output → Resolution      │
  └──────────────────────────────────────────────────────────────────┘
            </pre>
        </div>
'''

s1_marker = '    <div class="scenario-block" id="s1">'
s1_pos = c.find(s1_marker)
if s1_pos != -1:
    c = c[:s1_pos] + diagram + '\n' + c[s1_pos:]
    print('Diagram added before S1')

# Also fix sc-body indentation in S1
c = c.replace(
    '</div>\n<div class="sc-body">\n        <div class="sc-step">',
    '</div>\n        <div class="sc-body">\n        <div class="sc-step">'
)

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
print(f'Size: {round(os.path.getsize("cilium-test-prep.html")/1024,1)} KB')
print(f'diagram-container HTML: {c.count("diagram-title")}')
