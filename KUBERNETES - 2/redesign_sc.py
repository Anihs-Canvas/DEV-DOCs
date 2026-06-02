with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Full scenario CSS redesign - replace the entire scenario section
old_sc_css = '''        /* ═══════════════ SCENARIO STYLES ═══════════════ */
        .scenario-block { background: var(--gradient-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 0; margin-bottom: 28px; overflow: hidden; box-shadow: var(--shadow); transition: var(--transition); position: relative; animation: fadeInUp 0.5s ease both; }
        .scenario-block:hover { border-color: rgba(88,166,255,0.4); box-shadow: var(--shadow-glow), var(--shadow-lg); transform: translateY(-2px); }
        .scenario-block::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 80% 0%, rgba(163,113,247,0.04) 0%, transparent 60%); pointer-events: none; z-index: 0; }
        .scenario-block > * { position: relative; z-index: 1; }
        .sc-header { display: flex; align-items: flex-start; gap: 14px; padding: 20px 24px 16px 24px; border-bottom: 1px solid var(--border); background: linear-gradient(135deg, rgba(22,27,34,0.9) 0%, rgba(13,17,23,0.95) 100%); position: relative; }
        .sc-header::after { content: ''; position: absolute; bottom: -1px; left: 24px; right: 24px; height: 1px; background: linear-gradient(90deg, transparent, var(--accent-purple), transparent); opacity: 0.3; }
        .sc-badge { flex-shrink: 0; width: 48px; height: 48px; border-radius: 14px; background: var(--gradient-3); background-size: 200% 200%; animation: gradientShift 4s ease infinite; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: #fff; box-shadow: 0 4px 16px rgba(163,113,247,0.35); transition: var(--transition); }
        .scenario-block:hover .sc-badge { box-shadow: 0 6px 24px rgba(163,113,247,0.5); transform: scale(1.05); }
        .sc-header-content { flex: 1; }
        .scenario-block .sc-num { font-size: 10px; color: var(--accent-purple); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; font-weight: 700; }
        .scenario-block h4 { font-size: 19px; font-weight: 700; margin: 0 0 4px 0; color: var(--text); line-height: 1.3; }
        .scenario-block .sc-desc { margin: 8px 0 0 0; font-size: 14px; color: var(--text-secondary); line-height: 1.6; padding: 10px 14px; background: rgba(163,113,247,0.04); border-radius: 8px; border: 1px dashed rgba(163,113,247,0.2); }
        .scenario-block .sc-desc strong { color: var(--accent-purple); }
        .sc-body { padding: 20px 24px; }
        .sc-body h4 { font-size: 16px; color: var(--accent); margin: 20px 0 10px 0; padding: 0; display: flex; align-items: center; gap: 8px; }
        .sc-body h4:first-child { margin-top: 0; }
        .sc-kubectl { margin: 8px 0 16px 0; font-size: 13px; }
        .sc-kubectl code { background: rgba(63,185,80,0.1); color: var(--accent-green); padding: 6px 14px; border-radius: 6px; font-size: 13px; display: inline-block; border: 1px solid rgba(63,185,80,0.2); }
        .copy-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-secondary); border-radius: 8px; cursor: pointer; font-size: 12px; transition: var(--transition); margin: 4px 0; font-weight: 600; }
        .copy-btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(88,166,255,0.08); }
        .copy-btn.copied { border-color: var(--accent-green); color: var(--accent-green); background: rgba(63,185,80,0.1); }'''

new_sc_css = '''        /* ═══════════════ SCENARIO STYLES ═══════════════ */
        .scenario-block { background: var(--gradient-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 0; margin-bottom: 32px; overflow: hidden; box-shadow: var(--shadow); transition: var(--transition); position: relative; animation: fadeInUp 0.5s ease both; }
        .scenario-block:hover { border-color: rgba(163,113,247,0.5); box-shadow: var(--glow-purple), var(--shadow-lg); transform: translateY(-2px); }
        .scenario-block::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, var(--accent-purple), var(--accent), var(--accent-green)); z-index: 2; }
        .scenario-block::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 70% 0%, rgba(163,113,247,0.05) 0%, transparent 50%); pointer-events: none; z-index: 0; }
        .scenario-block > * { position: relative; z-index: 1; }
        
        .sc-header { display: flex; align-items: flex-start; gap: 16px; padding: 24px 28px 18px 28px; border-bottom: 1px solid var(--border); background: linear-gradient(180deg, rgba(163,113,247,0.06) 0%, rgba(22,27,34,0.9) 100%); position: relative; }
        .sc-header::after { content: ''; position: absolute; bottom: -1px; left: 28px; right: 28px; height: 1px; background: linear-gradient(90deg, transparent, rgba(163,113,247,0.4), var(--accent), rgba(63,185,80,0.4), transparent); opacity: 0.5; }
        
        .sc-badge { flex-shrink: 0; width: 52px; height: 52px; border-radius: 16px; background: linear-gradient(135deg, #a371f7 0%, #58a6ff 100%); background-size: 200% 200%; animation: gradientShift 4s ease infinite; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; color: #fff; box-shadow: 0 4px 20px rgba(163,113,247,0.4); transition: var(--transition); }
        .scenario-block:hover .sc-badge { box-shadow: 0 8px 30px rgba(163,113,247,0.6); transform: scale(1.08); }
        
        .sc-header-content { flex: 1; }
        .scenario-block .sc-num { font-size: 11px; color: var(--accent-purple); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        .scenario-block .sc-num .sc-status { font-size: 10px; padding: 2px 10px; border-radius: 10px; font-weight: 600; letter-spacing: 1px; }
        .scenario-block .sc-num .sc-status.deploy { background: rgba(88,166,255,0.12); color: var(--accent); }
        .scenario-block .sc-num .sc-status.debug { background: rgba(210,153,29,0.12); color: var(--accent-orange); }
        .scenario-block .sc-num .sc-status.resolve { background: rgba(63,185,80,0.12); color: var(--accent-green); }
        .scenario-block h4 { font-size: 20px; font-weight: 700; margin: 0 0 6px 0; color: var(--text); line-height: 1.35; }
        .scenario-block .sc-desc { margin: 10px 0 0 0; font-size: 14px; color: var(--text-secondary); line-height: 1.7; padding: 12px 16px; background: rgba(163,113,247,0.03); border-radius: 10px; border: 1px solid rgba(163,113,247,0.12); border-left: 3px solid rgba(163,113,247,0.4); }
        .scenario-block .sc-desc strong { color: var(--accent-purple); }
        
        .sc-body { padding: 24px 28px; }
        .sc-step { display: flex; gap: 14px; margin: 24px 0; align-items: flex-start; }
        .sc-step-num { flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: #fff; margin-top: 2px; }
        .sc-step-num.deploy { background: linear-gradient(135deg, #58a6ff, #3fb950); }
        .sc-step-num.debug { background: linear-gradient(135deg, #d2991d, #f85149); }
        .sc-step-num.answer { background: linear-gradient(135deg, #a371f7, #58a6ff); }
        .sc-step-content { flex: 1; }
        .sc-step-content h4 { font-size: 17px; font-weight: 700; color: var(--text); margin: 0 0 8px 0; padding: 0; display: flex; align-items: center; gap: 8px; }
        .sc-step-content h4.deploy { color: #58a6ff; }
        .sc-step-content h4.debug { color: #d2991d; }
        .sc-step-content h4.answer { color: #a371f7; }
        
        .sc-resolution { margin: 20px 0 0 0; padding: 16px 20px; background: linear-gradient(135deg, rgba(63,185,80,0.05) 0%, rgba(63,185,80,0.01) 100%); border: 1px solid rgba(63,185,80,0.2); border-radius: 10px; position: relative; }
        .sc-resolution h4 { color: var(--accent-green) !important; margin: 0 0 8px 0 !important; padding: 0 !important; }
        .sc-resolution::before { content: '✅'; position: absolute; right: 18px; top: 14px; font-size: 22px; opacity: 0.2; }
        
        .sc-kubectl { margin: 10px 0 18px 0; font-size: 14px; }
        .sc-kubectl code { background: rgba(63,185,80,0.1); color: var(--accent-green); padding: 8px 16px; border-radius: 8px; font-size: 13px; display: inline-block; border: 1px solid rgba(63,185,80,0.25); font-family: 'JetBrains Mono', 'Fira Code', monospace; }
        
        .copy-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-secondary); border-radius: 8px; cursor: pointer; font-size: 12px; transition: var(--transition); margin: 4px 0; font-weight: 600; }
        .copy-btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(88,166,255,0.08); box-shadow: var(--glow-blue); }
        .copy-btn.copied { border-color: var(--accent-green); color: var(--accent-green); background: rgba(63,185,80,0.1); }'''

c = c.replace(old_sc_css, new_sc_css)

# Add a category diagram for Part 3 Cat 1
cat1_p3_diag = '''
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
  │  S6-S10:   IDENTITY & SECURITY                                   │
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
        </div>'''

# Insert after Cat 1 chapter-intro
cat1_marker = 'id="part3-cat1"'
idx = c.find(cat1_marker)
intro_start = c.find('<div class="chapter-intro">', idx)
intro_end = c.find('</div>', intro_start)
intro_end = c.find('</div>', intro_end + 6)
c = c[:intro_end + 6] + '\n' + cat1_p3_diag + '\n    ' + c[intro_end + 6:]

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Redesigned. Size: {sz} KB | </main>: {c.count("</main>")}')
print(f'scenario-block: {c.count("scenario-block")}')
