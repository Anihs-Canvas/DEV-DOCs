$f = "helm.html"
$c = [System.IO.File]::ReadAllText((Resolve-Path $f), [System.Text.Encoding]::UTF8)

# Fix encoding: replace garbled chars with HTML entities
$c = $c.Replace('âš"', '&#x2693;')      # ⚓ anchor
$c = $c.Replace('ðŸ"Š', '&#x1F4CA;')   # 📊 chart
$c = $c.Replace('â†', '&#x2192;')       # → arrow
$c = $c.Replace('ðŸ"—', '&#x1F4CB;')   # 📋 clipboard  
$c = $c.Replace('ðŸ"', '&#x1F4E6;')    # 📦 package
$c = $c.Replace('ðŸ"—', '&#x1F517;')   # 🔗 link
$c = $c.Replace('ðŸ"§', '&#x1F527;')   # 🔧 wrench
$c = $c.Replace('ðŸš€', '&#x1F680;')   # 🚀 rocket
$c = $c.Replace('ðŸ"—', '&#x1F4C5;')   # 📅 calendar
$c = $c.Replace('ðŸ§ª', '&#x1F9EA;')   # 🧪 test tube
$c = $c.Replace('ðŸ"—', '&#x1F4D6;')   # 📖 book
$c = $c.Replace('ðŸ"—', '&#x1F5FA;')   # 🗺️ map (approximate)

# Clean up any remaining multi-byte garbled sequences  
$c = $c -replace 'â€', '-'  # em dash
$c = $c -replace 'â€"', '—'  # em dash

Write-Host "Fixed encoding issues"

# Find the CSS closing style tag position to insert new CSS before
$styleClose = $c.IndexOf('</style>')
if ($styleClose -lt 0) { Write-Host "ERROR: </style> not found"; exit 1 }

$newCSS = @'

        /* ═══ ADDITIONAL CKA/CKAD PATTERN CSS ═══ */
        .cka-exam-tip { background: linear-gradient(135deg, rgba(234,179,8,0.08) 0%, rgba(245,158,11,0.04) 100%); border: 1px solid rgba(234,179,8,0.3); border-radius: 10px; padding: 16px 20px; margin: 20px 0; }
        .cka-exam-tip::before { content: '🎯 HELM EXAM TIP'; display: block; font-size: 11px; font-weight: 700; letter-spacing: 1px; color: #facc15; margin-bottom: 8px; }
        .cka-exam-tip p { margin: 0; color: #e4e4e7; font-size: 0.9em; }

        .exam-question-item { background: rgba(15,23,42,0.5); border: 1px solid rgba(99,102,241,0.15); border-radius: 10px; padding: 1.2rem; margin: 1rem 0; }
        .exam-question-item .eq-number { display: inline-block; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-weight: 700; font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; margin-bottom: 8px; }
        .exam-question-item .eq-question { color: #e2e8f0; font-size: 0.88rem; line-height: 1.7; margin: 0.5rem 0; }
        .exam-question-item .eq-question code { background: #1e293b; color: #93c5fd; padding: 2px 6px; border-radius: 4px; font-size: 0.82rem; }
        .eq-answer { margin-top: 0.8rem; padding: 1rem; background: rgba(34,197,94,0.04); border-left: 3px solid #22c55e; border-radius: 0 8px 8px 0; }
        .eq-answer .eq-answer-label { color: #4ade80; font-weight: 700; font-size: 0.78rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
        .eq-answer pre { background: #0d1117; border: 1px solid rgba(99,102,241,0.15); border-radius: 6px; padding: 0.8rem; margin: 0.5rem 0; overflow-x: auto; }
        .eq-explanation { margin-top: 0.8rem; padding: 0.8rem; background: rgba(251,146,60,0.04); border-left: 3px solid #f97316; border-radius: 0 8px 8px 0; }
        .eq-explanation .eq-exp-label { color: #fb923c; font-weight: 700; font-size: 0.78rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
        .eq-explanation p { color: #d4d4d8; font-size: 0.84rem; line-height: 1.7; margin: 0.3rem 0; }
        .eq-explanation code { background: #1e293b; color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }

        .anatomy-card { background: #0d1117; border: 1px solid #1e3a5f; border-radius: 14px; margin: 24px 0; overflow: hidden; }
        .anatomy-card .anatomy-header { background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%); padding: 14px 20px; display: flex; align-items: center; gap: 10px; }
        .anatomy-card .anatomy-header h4 { color: #93c5fd; margin: 0; font-size: 1em; }
        .anatomy-card .anatomy-body { padding: 20px; }
        .anatomy-row { display: flex; align-items: flex-start; gap: 16px; padding: 12px 0; border-bottom: 1px solid #1c2333; }
        .anatomy-row:last-child { border-bottom: none; }
        .anatomy-label { min-width: 120px; color: #60a5fa; font-weight: 600; font-size: 0.9em; display: flex; align-items: center; gap: 6px; }
        .anatomy-label .anat-icon { font-size: 1.2em; }
        .anatomy-value { flex: 1; color: #c9d1d9; font-size: 0.88em; line-height: 1.6; }
        .anatomy-value code { background: rgba(50,108,229,0.15); color: #7ee787; padding: 1px 5px; border-radius: 4px; font-size: 0.9em; }

        .timeline-vertical { margin: 24px 0; padding: 0 0 0 24px; border-left: 3px solid #1e3a5f; position: relative; }
        .timeline-item { position: relative; padding: 0 0 24px 24px; }
        .timeline-item:last-child { padding-bottom: 0; }
        .timeline-item::before { content: ''; position: absolute; left: -30px; top: 4px; width: 14px; height: 14px; border-radius: 50%; background: #326ce5; border: 3px solid #0d1117; }
        .timeline-item.tl-active::before { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.4); }
        .timeline-item h5 { color: #e4e4e7; margin: 0 0 4px 0; font-size: 0.92em; }
        .timeline-item p { color: #8b949e; font-size: 0.85em; margin: 0; line-height: 1.5; }

        .scenario-box { background: linear-gradient(135deg, rgba(239,68,68,0.06) 0%, rgba(245,158,11,0.03) 100%); border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; padding: 20px; margin: 20px 0; }
        .scenario-box h5 { color: #f87171; margin: 0 0 8px 0; }
        .scenario-box.positive { border-color: rgba(34,197,94,0.3); background: linear-gradient(135deg, rgba(34,197,94,0.06) 0%, rgba(16,185,129,0.03) 100%); }
        .scenario-box.positive h5 { color: #4ade80; }

        .evolution-strip { display: flex; gap: 8px; margin: 24px 0; flex-wrap: wrap; }
        .evo-item { flex: 1; min-width: 120px; background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; text-align: center; }
        .evo-item:hover { border-color: #326ce5; }
        .evo-item .evo-icon { font-size: 1.5em; margin-bottom: 6px; }
        .evo-item h5 { color: #e4e4e7; margin: 0 0 4px 0; font-size: 0.85em; }
        .evo-item p { color: #8b949e; font-size: 0.75em; margin: 0; }

        .ba-comparison { margin: 24px 0; }
        .ba-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        @media (max-width: 768px) { .ba-panels { grid-template-columns: 1fr; } }
        .ba-before { background: linear-gradient(135deg, #2d1a1a 0%, #1a1010 100%); border: 1px solid #da3633; border-radius: 12px; padding: 20px; }
        .ba-before h5 { color: #f87171; margin: 0 0 10px 0; }
        .ba-after { background: linear-gradient(135deg, #1a2d1a 0%, #101a10 100%); border: 1px solid #238636; border-radius: 12px; padding: 20px; }
        .ba-after h5 { color: #4ade80; margin: 0 0 10px 0; }

        .metric-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 24px 0; }
        .metric-card { background: linear-gradient(145deg, #161b22 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 18px; text-align: center; }
        .metric-card:hover { border-color: #326ce5; transform: translateY(-2px); }
        .metric-card .metric-value { color: #60a5fa; font-size: 1.8em; font-weight: 800; line-height: 1; margin-bottom: 4px; }
        .metric-card .metric-label { color: #8b949e; font-size: 0.78em; text-transform: uppercase; letter-spacing: 0.5px; }

        .roadmap-track { position: relative; padding: 0; }
        .roadmap-track::before { content: ''; position: absolute; top: 0; bottom: 0; left: 32px; width: 4px; background: linear-gradient(to bottom, #22c55e, #326ce5, #eab308, #8b5cf6, #ef4444); border-radius: 4px; }
        .roadmap-phase { position: relative; margin-bottom: 40px; padding-left: 72px; }
        .roadmap-phase .phase-marker { position: absolute; left: 16px; top: 0; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1em; font-weight: 800; color: #fff; z-index: 2; box-shadow: 0 0 16px rgba(0,0,0,0.4); }

        .lifecycle-flow { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 4px; margin: 24px 0; padding: 20px; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; }
        .lf-stage { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 14px 16px; text-align: center; min-width: 100px; }

        .port-scene { background: linear-gradient(180deg, #0a1628 0%, #0d2137 60%, #0f2b4a 100%); border: 2px solid #1a4a6e; border-radius: 16px; padding: 32px; margin: 28px 0; position: relative; overflow: hidden; }
        .port-scene .port-scene-title { text-align: center; color: #60a5fa; font-size: 1.25em; font-weight: 700; margin-bottom: 8px; letter-spacing: 1.5px; }
        .port-scene .port-scene-subtitle { text-align: center; color: #8b949e; font-size: 0.88em; margin-bottom: 28px; }
        .port-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 14px; }
        .port-card { background: linear-gradient(145deg, #111827 0%, #0d1117 100%); border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px 14px; position: relative; transition: border-color 0.2s, box-shadow 0.2s; }
        .port-card:hover { border-color: #326ce5; box-shadow: 0 4px 16px rgba(50,108,229,0.15); }
        .port-card .port-icon { font-size: 1.6em; margin-bottom: 4px; display: block; }
        .port-card h5 { color: #e4e4e7; margin: 4px 0; font-size: 0.95em; font-weight: 700; }
        .port-card p { color: #8b949e; font-size: 0.82em; margin: 0; line-height: 1.5; }

        .icon-feature-list { margin: 20px 0; }
        .icon-feature { display: flex; align-items: flex-start; gap: 14px; padding: 14px 0; border-bottom: 1px solid #1c2333; }
        .icon-feature:last-child { border-bottom: none; }
        .icon-feature .if-icon { font-size: 1.4em; min-width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: rgba(50,108,229,0.1); border-radius: 8px; }
        .icon-feature .if-content h5 { color: #e4e4e7; margin: 0 0 2px 0; font-size: 0.92em; }
        .icon-feature .if-content p { color: #8b949e; font-size: 0.85em; margin: 0; line-height: 1.5; }

        .prereq-box { background: linear-gradient(135deg, rgba(139,92,246,0.08), rgba(50,108,229,0.06)); border: 1px solid rgba(139,92,246,0.25); border-radius: 16px; padding: 28px; margin: 32px 0; }
        .prereq-box h4 { color: #c4b5fd; margin: 0 0 16px; font-size: 1.1em; }
        .prereq-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
        .prereq-item { display: flex; align-items: center; gap: 10px; background: rgba(13,17,23,0.6); border: 1px solid #21262d; border-radius: 10px; padding: 12px 14px; }
        .prereq-item .prereq-icon { font-size: 1.3em; }
        .prereq-item .prereq-text { color: #c9d1d9; font-size: 0.85em; }
        .prereq-item .prereq-text strong { color: #e4e4e7; }

        .cta-section { background: linear-gradient(135deg, #0a1628 0%, #0d2137 40%, #121a2d 100%); border: 2px solid #1e3a5f; border-radius: 20px; padding: 40px 32px; margin: 40px 0; text-align: center; position: relative; overflow: hidden; }
        .cta-section::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #22c55e, #326ce5, #8b5cf6, #ec4899); }
        .cta-section h3 { color: #60a5fa; font-size: 1.6em; margin: 0 0 10px; }
        .cta-section p { color: #8b949e; font-size: 0.95em; max-width: 600px; margin: 0 auto 28px; line-height: 1.65; }
        .cta-paths { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
        .cta-path { background: rgba(13,17,23,0.7); border: 1px solid #21262d; border-radius: 14px; padding: 22px 18px; text-align: center; transition: all 0.3s ease; }
        .cta-path:hover { border-color: #326ce5; transform: translateY(-4px); box-shadow: 0 8px 28px rgba(50,108,229,0.15); }
        .cta-path .cta-icon { font-size: 2em; display: block; margin-bottom: 10px; }
        .cta-path h5 { color: #e4e4e7; font-size: 0.95em; margin: 0 0 6px; }

        .header-tags .tag.helm { background: rgba(50,108,229,0.3); color: #93c5fd; border: 1px solid rgba(50,108,229,0.5); }

        .helm-exam-questions { background: linear-gradient(135deg, rgba(99,102,241,0.06) 0%, rgba(139,92,246,0.04) 100%); border: 1px solid rgba(99,102,241,0.2); border-radius: 14px; padding: 1.8rem; margin: 2rem 0; }
        .helm-exam-questions::before { content: '📝 HELM PRACTICE QUESTIONS'; display: block; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #818cf8; margin-bottom: 16px; }
        .helm-exam-questions h4 { color: #a5b4fc; font-size: 1.1rem; margin: 0 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(99,102,241,0.2); }

'@

$c = $c.Substring(0, $styleClose) + $newCSS + $c.Substring($styleClose)

[System.IO.File]::WriteAllText((Resolve-Path $f), $c, [System.Text.Encoding]::UTF8)
Write-Host "helm.html updated: $([math]::Round($c.Length/1024,1))KB"