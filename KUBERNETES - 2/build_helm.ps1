$f = "helm.html"

# CSS from CKA/CKAD pattern
$css = @'
    <style>
        * { box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, "Noto Sans", sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #e4e4e7; background: #0d1117; }
        *::-webkit-scrollbar { width: 12px; height: 12px; }
        *::-webkit-scrollbar-track { background: #21262d; }
        *::-webkit-scrollbar-thumb { background: #484f58; border-radius: 6px; border: 2px solid #21262d; }
        *::-webkit-scrollbar-thumb:hover { background: #6e7681; }
        * { scrollbar-width: thin; scrollbar-color: #484f58 #21262d; }

        header { background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 60%, #0a1929 100%); color: #e4e4e7; padding: 50px 20px; text-align: center; box-shadow: 0 6px 18px rgba(0,0,0,0.4); border-bottom: 3px solid #326ce5; position: relative; overflow: hidden; }
        header::before { content: "⚓"; position: absolute; font-size: 300px; opacity: 0.03; right: -50px; top: -80px; }
        header h1 { margin: 0 0 16px 0; font-size: 2.6em; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 50%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        header .subtitle { margin: 0 0 8px 0; font-size: 1.3em; opacity: 0.9; color: #93c5fd; }
        header .description { margin: 0 0 24px 0; font-size: 1.05em; opacity: 0.8; max-width: 800px; margin-left: auto; margin-right: auto; }
        .header-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
        .tag { display: inline-block; background: rgba(50,108,229,0.3); color: #93c5fd; border: 1px solid rgba(50,108,229,0.5); border-radius: 20px; padding: 6px 16px; font-size: 13px; font-weight: 500; }
        .tag.beginner { background: rgba(34,197,94,0.2); border-color: rgba(34,197,94,0.5); color: #4ade80; }
        .tag.intermediate { background: rgba(234,179,8,0.2); border-color: rgba(234,179,8,0.5); color: #facc15; }

        html { scroll-behavior: smooth; }
        .toc-sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: 340px; background: #161b22; border-right: 1px solid #30363d; box-shadow: 0 0 24px rgba(0,0,0,0.4); padding: 16px 0; overflow-y: auto; transform: translateX(-100%); transition: transform 250ms ease; z-index: 1000; }
        .sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 0 16px 16px; border-bottom: 1px solid #30363d; margin-bottom: 12px; }
        .sidebar-header h2 { margin: 0; font-size: 18px; color: #60a5fa; font-weight: 700; }
        .sidebar-controls { display: flex; gap: 6px; }
        .expand-collapse-btn { background: #1e3a5f; color: #93c5fd; border: 1px solid #326ce5; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 14px; transition: all 0.2s ease; }
        .expand-collapse-btn:hover { background: #326ce5; color: white; }
        .toc-list { list-style: none; padding: 0 12px; margin: 0; }
        .toc-list li { margin-bottom: 4px; }
        .part-header { background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 100%); border: 1px solid #326ce5; border-radius: 8px; padding: 10px 14px; margin: 16px 0 8px 0; cursor: pointer; transition: all 0.2s ease; }
        .part-header:first-child { margin-top: 0; }
        .part-header:hover { background: linear-gradient(135deg, #326ce5 0%, #1e3a5f 100%); }
        .part-header .part-title { color: #93c5fd; font-weight: 600; font-size: 14px; display: flex; align-items: center; justify-content: space-between; }
        .part-header .part-badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(50,108,229,0.3); }
        .part-badge.beginner { background: rgba(34,197,94,0.3); color: #4ade80; }
        .part-badge.intermediate { background: rgba(234,179,8,0.3); color: #facc15; }
        .part-badge.advanced { background: rgba(239,68,68,0.3); color: #f87171; }
        .chapter-list { list-style: none; padding-left: 12px; margin: 8px 0; display: none; }
        .chapter-list.visible { display: block; }
        .chapter-item { margin: 4px 0; }
        .chapter-link { display: flex; align-items: center; justify-content: flex-start; padding: 8px 12px; text-align: left; color: #e4e4e7; text-decoration: none; border-radius: 6px; font-size: 13px; transition: all 0.2s ease; border-left: 3px solid transparent; }
        .chapter-link:hover { background: #21262d; border-left-color: #326ce5; color: #60a5fa; }
        .chapter-link.active { background: #1e3a5f; border-left-color: #326ce5; color: #60a5fa; font-weight: 600; }
        .chapter-number { font-size: 11px; color: #a1a1aa; margin-right: 8px; min-width: 28px; }
        .chapter-row { display: flex; align-items: center; justify-content: space-between; gap: 4px; }
        .chapter-row .chapter-link { flex: 1; }
        .section-toggle-btn { background: none; border: none; color: #a1a1aa; cursor: pointer; font-size: 12px; padding: 2px 6px; border-radius: 4px; }
        .section-toggle-btn:hover { background: #30363d; color: #60a5fa; }
        .sub-toc { list-style: none; padding-left: 20px; margin: 4px 0; display: none; }
        .sub-toc.visible { display: block; }
        .sub-toc li { margin: 2px 0; }
        .sub-toc a { color: #a1a1aa; text-decoration: none; font-size: 12px; padding: 4px 8px; display: block; border-radius: 4px; }
        .sub-toc a:hover { color: #60a5fa; background: #21262d; }
        .toc-toggle { position: fixed; top: 18px; left: 18px; background: linear-gradient(135deg, #1e3a5f 0%, #326ce5 100%); color: #ffffff; border: 1px solid #326ce5; border-radius: 8px; padding: 12px 18px; cursor: pointer; z-index: 1100; font-size: 15px; font-weight: 600; box-shadow: 0 4px 12px rgba(50,108,229,0.3); transition: all 0.2s ease; }
        .toc-toggle:hover { background: linear-gradient(135deg, #326ce5 0%, #1e3a5f 100%); transform: scale(1.05); box-shadow: 0 6px 16px rgba(50,108,229,0.4); }
        body.toc-open .toc-sidebar { transform: translateX(0); }
        @media (min-width: 1000px) { body.toc-open header, body.toc-open main, body.toc-open footer { margin-left: 340px; transition: margin-left 250ms ease; } }

        main { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
        main h2 { color: #60a5fa; border-bottom: 3px solid #326ce5; padding-bottom: 12px; margin: 48px 0 24px 0; font-size: 1.8em; }
        main h3 { color: #93c5fd; margin: 32px 0 16px 0; font-size: 1.3em; }
        main h4 { color: #e4e4e7; margin: 24px 0 12px 0; font-size: 1.1em; }
        main p { margin: 12px 0; }
        main code { background: rgba(50,108,229,0.15); color: #93c5fd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        main pre { background: #0d1117; border: 1px solid #1e3a5f; border-radius: 8px; padding: 16px; overflow-x: auto; }
        main pre code { background: none; padding: 0; }
        .intro-callout { background: linear-gradient(135deg, #1a2e1a 0%, #1e3a5f 100%); border: 1px solid #326ce5; border-radius: 12px; padding: 24px 30px; margin: 0 0 40px 0; text-align: center; }
        .intro-callout p { margin: 0; font-size: 1.15em; line-height: 1.7; }
        .intro-callout strong { color: #60a5fa; }

        .visual-summary { background: linear-gradient(135deg, rgba(50,108,229,0.08) 0%, rgba(59,130,246,0.05) 100%); border: 1px solid rgba(50,108,229,0.25); border-radius: 16px; padding: 28px; margin: 32px 0; position: relative; }
        .visual-summary::before { content: '📊 VISUAL SUMMARY'; display: block; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; color: #60a5fa; margin-bottom: 16px; text-transform: uppercase; }
        .visual-summary h4 { color: #93c5fd; margin: 0 0 16px 0; }
        .vs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
        .vs-item { background: rgba(13,17,23,0.6); border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px; text-align: center; transition: transform 0.2s, border-color 0.2s; }
        .vs-item:hover { border-color: #326ce5; transform: translateY(-2px); }
        .vs-item .vs-icon { font-size: 1.8em; margin-bottom: 6px; }
        .vs-item .vs-label { color: #93c5fd; font-size: 0.82em; font-weight: 600; display: block; margin-bottom: 4px; }
        .vs-item .vs-detail { color: #8b949e; font-size: 0.75em; line-height: 1.4; }

        .flow-diagram { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 8px; margin: 24px 0; padding: 20px; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; }
        .flow-step { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 14px 18px; text-align: center; min-width: 110px; }
        .flow-step:hover { border-color: #326ce5; transform: translateY(-2px); }
        .flow-step .step-icon { font-size: 1.5em; margin-bottom: 4px; }
        .flow-step .step-label { color: #93c5fd; font-size: 0.78em; display: block; font-weight: 600; }
        .flow-step .step-detail { color: #8b949e; font-size: 0.72em; display: block; }
        .flow-arrow { color: #326ce5; font-size: 1.3em; font-weight: bold; }

        .decision-tree { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 24px; margin: 24px 0; }
        .decision-node { background: #21262d; border: 1px solid #30363d; border-radius: 10px; padding: 14px 20px; margin: 10px auto; max-width: 500px; text-align: center; color: #c9d1d9; font-size: 0.92em; }
        .decision-node.question { background: #1e3a5f; border-color: #326ce5; color: #93c5fd; font-weight: 600; }
        .diagram-title { font-size: 1em; font-weight: 600; text-align: center; }

        .process-steps { display: flex; align-items: flex-start; gap: 0; margin: 28px 0; padding: 24px 16px; background: linear-gradient(135deg, #0d1117 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 14px; overflow-x: auto; position: relative; }
        .process-steps::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #326ce5, #6366f1, #ec4899, #f59e0b, #22c55e); border-radius: 14px 14px 0 0; }
        .process-step-item { flex: 1; min-width: 130px; text-align: center; position: relative; padding: 0 8px; }
        .process-step-item:not(:last-child)::after { content: '→'; position: absolute; right: -8px; top: 18px; color: #326ce5; font-size: 1.3em; font-weight: bold; z-index: 1; }
        .step-number { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #326ce5 0%, #2563eb 100%); color: #fff; font-weight: 700; font-size: 0.9em; margin-bottom: 8px; }
        .process-step-item.active .step-number { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); box-shadow: 0 0 12px rgba(34,197,94,0.3); }
        .process-step-item h5 { color: #e4e4e7; font-size: 0.85em; margin: 4px 0; }
        .process-step-item p { color: #8b949e; font-size: 0.75em; line-height: 1.4; margin: 0; }

        .info-box { border-radius: 12px; padding: 16px 20px; margin: 20px 0; border-left: 4px solid; }
        .info-box h5 { margin: 0 0 8px 0; font-size: 0.95em; }
        .info-box p { margin: 0; font-size: 0.9em; }
        .info-box.note { background: rgba(50,108,229,0.08); border-color: #326ce5; border-left-color: #326ce5; }
        .info-box.note h5 { color: #60a5fa; }
        .info-box.warning { background: rgba(234,179,8,0.08); border-color: rgba(234,179,8,0.3); border-left-color: #d2991d; }
        .info-box.warning h5 { color: #facc15; }
        .info-box.tip { background: rgba(34,197,94,0.08); border-color: rgba(34,197,94,0.3); border-left-color: #238636; }
        .info-box.tip h5 { color: #4ade80; }
        .info-box.danger { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.3); border-left-color: #da3633; }
        .info-box.danger h5 { color: #f87171; }

        .split-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin: 24px 0; border-radius: 14px; overflow: hidden; border: 1px solid #1e3a5f; }
        @media (max-width: 768px) { .split-panel { grid-template-columns: 1fr; } }
        .split-side { padding: 24px; }
        .split-side.split-bad { background: linear-gradient(135deg, #2d1a1a 0%, #1a1010 100%); border-right: 2px solid #30363d; }
        .split-side.split-good { background: linear-gradient(135deg, #1a2d1a 0%, #101a10 100%); }
        .split-side h5 { margin: 0 0 12px 0; font-size: 1em; }
        .split-side.split-bad h5 { color: #f87171; }
        .split-side.split-good h5 { color: #4ade80; }
        .split-side p, .split-side ul { color: #c9d1d9; font-size: 0.88em; line-height: 1.7; }
        .split-side ul { padding-left: 20px; margin: 8px 0; }

        .compare-table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 24px 0; font-size: 0.9em; border-radius: 12px; overflow: hidden; border: 1px solid #1e3a5f; }
        .compare-table th { background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%); color: #93c5fd; padding: 12px 16px; text-align: left; font-weight: 700; border-bottom: 2px solid #326ce5; }
        .compare-table td { padding: 10px 16px; border-bottom: 1px solid #1c2333; color: #c9d1d9; }
        .compare-table tr:last-child td { border-bottom: none; }
        .compare-table tr:hover td { background: rgba(50,108,229,0.05); }

        .card-grid { display: grid; gap: 16px; margin: 24px 0; }
        .card-grid.cols-2 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
        .card-grid.cols-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

        .code-block-wrapper { margin: 20px 0; border: 1px solid #1e3a5f; border-radius: 12px; overflow: hidden; }
        .code-block-header { background: #161b22; padding: 10px 16px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1e3a5f; font-size: 0.85em; color: #8b949e; }
        .code-dot { width: 12px; height: 12px; border-radius: 50%; }
        .code-dot.red { background: #ff5f56; }
        .code-dot.yellow { background: #ffbd2e; }
        .code-dot.green { background: #27ca40; }
        .code-lang { color: #8b949e; font-size: 0.8em; margin-left: auto; }
        .code-block-wrapper pre { margin: 0; border: none; border-radius: 0; background: #0d1117; }

        .toc-section { margin: 50px 0; }
        .toc-section h2 { color: #60a5fa; font-size: 1.8em; text-align: center; margin-bottom: 30px; position: relative; border-bottom: none; }
        .toc-section h2::after { content: ''; display: block; width: 80px; height: 3px; background: #326ce5; margin: 12px auto 0; border-radius: 2px; }
        .toc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
        .toc-card { background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border: 1px solid #30363d; border-radius: 16px; overflow: hidden; transition: all 0.3s ease; cursor: pointer; position: relative; }
        .toc-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #326ce5, #60a5fa); opacity: 0; transition: opacity 0.3s ease; z-index: 1; }
        .toc-card:hover { background: linear-gradient(135deg, #1e3a5f 0%, #21262d 100%); border-color: #326ce5; transform: translateY(-6px); box-shadow: 0 12px 30px rgba(50,108,229,0.2); }
        .toc-card:hover::before { opacity: 1; }
        .toc-card a { text-decoration: none; color: inherit; display: block; padding: 24px; }
        .toc-card .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .toc-card .card-icon { font-size: 1.4em; }
        .toc-card .card-part-badge { font-size: 0.72em; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
        .toc-card .card-part-badge.beginner { background: rgba(34,197,94,0.2); color: #4ade80; }
        .toc-card .card-part-badge.intermediate { background: rgba(234,179,8,0.2); color: #facc15; }
        .toc-card .card-part-badge.advanced { background: rgba(239,68,68,0.2); color: #f87171; }
        .toc-card h3 { margin: 0 0 4px 0; font-size: 1.05em; color: #93c5fd; }
        .toc-card .card-subtitle { color: #93c5fd; font-size: 0.95em; margin-bottom: 12px; }
        .toc-card p { color: #a1a1aa; font-size: 0.9em; line-height: 1.6; margin: 0 0 16px 0; }
        .toc-card .card-chapters { display: flex; gap: 6px; }
        .toc-card .chapter-tag { background: rgba(50,108,229,0.2); color: #93c5fd; padding: 4px 10px; border-radius: 6px; font-size: 11px; border: 1px solid rgba(50,108,229,0.3); }

        .appendix-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }
        .appendix-card { background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border: 1px solid #30363d; border-radius: 12px; padding: 20px; transition: all 0.3s ease; position: relative; overflow: hidden; }
        .appendix-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #326ce5, #60a5fa); opacity: 0; transition: opacity 0.3s ease; }
        .appendix-card:hover { border-color: #326ce5; background: #1e3a5f; transform: translateY(-4px); box-shadow: 0 8px 24px rgba(50,108,229,0.2); }
        .appendix-card:hover::before { opacity: 1; }
        .appendix-card a { text-decoration: none; color: inherit; display: block; padding: 16px; }
        .appendix-card h4 { margin: 0 0 4px 0; font-size: 0.92em; color: #93c5fd; }
        .appendix-card p { margin: 0; font-size: 0.78em; color: #8b949e; line-height: 1.4; }

        .chapter-section { margin: 40px 0; }
        .chapter-section > h2 { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; color: #60a5fa; font-size: 1.8em; border-bottom: 3px solid #326ce5; padding-bottom: 12px; margin-bottom: 30px; }
        .chapter-badge { font-size: 0.45em; background: rgba(50,108,229,0.2); color: #93c5fd; padding: 4px 10px; border-radius: 8px; font-weight: 500; }
        .chapter-intro { background: linear-gradient(135deg, #1e3a5f 0%, #161b22 100%); border: 1px solid #326ce5; border-radius: 16px; padding: 32px; margin: 24px 0 40px 0; position: relative; box-shadow: 0 4px 24px rgba(50,108,229,0.1); }
        .chapter-intro::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #326ce5, #60a5fa, #93c5fd, #60a5fa, #326ce5); border-radius: 16px 16px 0 0; }
        .chapter-intro h3 { color: #60a5fa; font-size: 1.5em; margin: 0 0 12px 0; }
        .chapter-intro p { color: #c9d1d9; font-size: 1.02em; line-height: 1.7; margin: 0; }
        .chapter-meta { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
        .meta-tag { display: inline-flex; align-items: center; gap: 6px; background: rgba(50,108,229,0.12); border: 1px solid rgba(50,108,229,0.25); color: #93c5fd; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; backdrop-filter: blur(4px); transition: all 0.2s ease; }
        .meta-tag:hover { background: rgba(50,108,229,0.2); border-color: rgba(50,108,229,0.5); }
        .section-block { margin: 24px 0; padding: 20px; background: rgba(13,17,23,0.5); border: 1px solid #1c2333; border-radius: 10px; }
        .learning-objectives { background: linear-gradient(135deg, rgba(34,197,94,0.08) 0%, rgba(16,185,129,0.04) 100%); border: 1px solid rgba(34,197,94,0.25); border-radius: 12px; padding: 20px 24px; margin: -20px 0 24px 0; }
        .learning-objectives h4 { color: #4ade80; margin: 0 0 10px 0; font-size: 1.05em; }
        .learning-objectives ul { margin: 0; padding-left: 20px; color: #c9d1d9; line-height: 1.8; }
        .learning-objectives li { margin: 4px 0; }

        .drill-solution { background: linear-gradient(135deg, rgba(34,197,94,0.06) 0%, rgba(50,108,229,0.04) 100%); border: 1px solid rgba(50,108,229,0.25); border-left: 4px solid #22c55e; border-radius: 10px; padding: 16px 20px; margin-top: 14px; }
        .drill-solution summary { color: #4ade80; cursor: pointer; font-weight: 600; font-size: 0.95em; padding: 4px 0; }
        .drill-solution summary:hover { color: #86efac; }
        .drill-solution p { color: #c9d1d9; font-size: 0.9em; line-height: 1.8; margin: 8px 0 0 0; }
        .drill-solution strong { color: #60a5fa; }
        .drill-solution pre { margin: 10px 0 0; background: #0a0e14; border-radius: 8px; padding: 14px 18px; overflow-x: auto; }
        .drill-solution code { font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 13px; line-height: 1.6; color: #c9d1d9; }

        .architecture-layers { margin: 28px 0; border-radius: 14px; overflow: hidden; border: 1px solid #1e3a5f; }
        .arch-layer { padding: 18px 24px; display: flex; align-items: center; gap: 16px; border-bottom: 1px solid rgba(30,26,46,0.5); transition: background 0.2s; }
        .arch-layer:hover { background: rgba(50,108,229,0.05); }
        .arch-layer:last-child { border-bottom: none; }
        .arch-layer .layer-icon { font-size: 1.5em; min-width: 40px; text-align: center; }
        .arch-layer .layer-name { color: #e4e4e7; font-weight: 600; font-size: 0.95em; min-width: 140px; }
        .arch-layer .layer-desc { color: #8b949e; font-size: 0.85em; flex: 1; }
        .arch-layer .layer-examples { display: flex; gap: 6px; flex-wrap: wrap; }
        .arch-layer .layer-examples span { background: rgba(0,0,0,0.3); color: #a1a1aa; padding: 2px 8px; border-radius: 6px; font-size: 0.75em; }

        .relationship-map { background: linear-gradient(135deg, #0d1117 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 14px; padding: 28px; margin: 28px 0; position: relative; }
        .relationship-map h4 { color: #93c5fd; text-align: center; margin: 0 0 20px 0; }
        .rel-center { text-align: center; margin-bottom: 20px; }
        .rel-hub { display: inline-flex; align-items: center; justify-content: center; width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #326ce5, #2563eb); color: white; font-weight: 700; font-size: 0.9em; text-align: center; box-shadow: 0 0 30px rgba(50,108,229,0.3); }
        .rel-spokes { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
        .rel-spoke { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 14px; text-align: center; transition: border-color 0.2s; }
        .rel-spoke:hover { border-color: #326ce5; }
        .rel-spoke .spoke-icon { font-size: 1.4em; margin-bottom: 4px; }
        .rel-spoke h5 { color: #e4e4e7; margin: 4px 0; font-size: 0.88em; }
        .rel-spoke p { color: #8b949e; font-size: 0.78em; margin: 0; line-height: 1.4; }

        .summary-hero { text-align: center; padding: 20px; }
        .summary-hero .hero-icon { font-size: 3em; display: block; margin-bottom: 12px; }
        .summary-hero h2 { border: none; margin: 0 0 8px 0; }
        .summary-hero .hero-subtitle { color: #60a5fa; font-size: 1.05em; margin: 0 0 8px 0; }
        .summary-hero .hero-desc { color: #8b949e; font-size: 0.9em; max-width: 700px; margin: 0 auto; line-height: 1.6; }
        .summary-stats-bar { display: flex; flex-wrap: wrap; justify-content: center; gap: 16px; margin: 20px 0; }
        .summary-stat-card { background: #161b22; border: 1px solid #1e3a5f; border-radius: 10px; padding: 14px 18px; text-align: center; min-width: 90px; }
        .summary-stat-card .stat-icon { font-size: 1.2em; display: block; margin-bottom: 4px; }
        .summary-stat-card .stat-number { font-size: 1.5em; font-weight: 800; display: block; }
        .summary-stat-card .stat-number.blue { color: #60a5fa; }
        .summary-stat-card .stat-number.green { color: #4ade80; }
        .summary-stat-card .stat-number.purple { color: #60a5fa; }
        .summary-stat-card .stat-number.orange { color: #fb923c; }
        .summary-stat-card .stat-text { color: #8b949e; font-size: 0.75em; display: block; margin-top: 2px; }

        footer { text-align: center; padding: 40px 20px; color: #8b949e; font-size: 0.85em; border-top: 1px solid #1e3a5f; margin-top: 60px; }
        footer a { color: #60a5fa; text-decoration: none; }
        footer a:hover { text-decoration: underline; }

        pre[class*="language-"], code[class*="language-"] { background: transparent !important; text-shadow: none !important; }
        .token.comment { color: #6e7681 !important; }
        .token.punctuation { color: #c9d1d9 !important; }
    </style>
</head>
<body class="toc-open">
    <button id="tocToggle" class="toc-toggle" aria-controls="tocSidebar" aria-expanded="true" title="Toggle TOC">☰ Contents</button>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                         SIDEBAR — TOC                          -->
<!-- ═══════════════════════════════════════════════════════════════ -->
    <nav id="tocSidebar" class="toc-sidebar" aria-label="Table of Contents">
        <div class="sidebar-header">
            <h2>⚓ Helm Guide</h2>
            <div class="sidebar-controls">
                <button class="expand-collapse-btn" onclick="expandAllParts()" title="Expand All">⊞</button>
                <button class="expand-collapse-btn" onclick="collapseAllParts()" title="Collapse All">⊟</button>
            </div>
        </div>
        <ul class="toc-list">
            <!-- OVERVIEW & ROADMAP -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>🏠 Overview & Roadmap</span><span class="part-badge beginner">📋 Guide</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#front-toc" class="chapter-link"><span class="chapter-number">📚</span>Complete Table of Contents</a></div></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#front-appendices" class="chapter-link"><span class="chapter-number">📎</span>Appendices Quick Reference</a></div></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#master-summary" class="chapter-link"><span class="chapter-number">🗺️</span>Master Summary & Roadmap</a></div></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#quick-ref" class="chapter-link"><span class="chapter-number">⚡</span>Helm CLI Quick Reference</a></div></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#helm-mistakes" class="chapter-link"><span class="chapter-number">⚠️</span>Top 10 Helm Mistakes</a></div></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#helm-strategy" class="chapter-link"><span class="chapter-number">🎯</span>Helm Best Practices</a></div></li>
                </ul>
            </li>
            <!-- PART 1 -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>📚 Part 1: Helm Fundamentals</span><span class="part-badge beginner">🟢 Beginner</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch1" class="chapter-link"><span class="chapter-number">Ch 1</span>What is Helm?</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s1-1">1.1 The Problem Before Helm</a></li><li><a href="#s1-2">1.2 What is Helm?</a></li><li><a href="#s1-3">1.3 Helm vs kubectl</a></li><li><a href="#s1-4">1.4 Cloud Native Ecosystem</a></li><li><a href="#s1-5">1.5 Quick Start</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch2" class="chapter-link"><span class="chapter-number">Ch 2</span>Helm Architecture</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s2-1">2.1 Helm 3 (Tiller-less)</a></li><li><a href="#s2-2">2.2 Core Concepts</a></li><li><a href="#s2-3">2.3 Client Workflow</a></li><li><a href="#s2-4">2.4 Release Lifecycle</a></li><li><a href="#s2-5">2.5 Release Storage</a></li><li><a href="#s2-6">2.6 First anihpj Release</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch3" class="chapter-link"><span class="chapter-number">Ch 3</span>Installing & Configuring</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s3-1">3.1 Installing Helm</a></li><li><a href="#s3-2">3.2 Configuration</a></li><li><a href="#s3-3">3.3 Chart Repositories</a></li><li><a href="#s3-4">3.4 Own Chart Repository</a></li><li><a href="#s3-5">3.5 Provenance & Signing</a></li></ul></li>
                </ul>
            </li>
            <!-- PART 2 -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>📦 Part 2: Chart Development</span><span class="part-badge intermediate">🟡 Intermediate</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch4" class="chapter-link"><span class="chapter-number">Ch 4</span>Chart Structure</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s4-1">4.1 Directory Tree</a></li><li><a href="#s4-2">4.2 Chart.yaml</a></li><li><a href="#s4-3">4.3 Your First Chart</a></li><li><a href="#s4-4">4.4 .helmignore</a></li><li><a href="#s4-5">4.5 Packaging</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch5" class="chapter-link"><span class="chapter-number">Ch 5</span>Templates</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s5-1">5.1 Go Template Basics</a></li><li><a href="#s5-2">5.2 Built-in Objects</a></li><li><a href="#s5-3">5.3 Values Files</a></li><li><a href="#s5-4">5.4 Functions & Pipelines</a></li><li><a href="#s5-5">5.5 Flow Control</a></li><li><a href="#s5-6">5.6 Named Templates</a></li><li><a href="#s5-7">5.7 Debugging</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch6" class="chapter-link"><span class="chapter-number">Ch 6</span>Building the anihpj Chart</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s6-1">6.1 Chart Planning</a></li><li><a href="#s6-2">6.2 Scaffolding</a></li><li><a href="#s6-3">6.3 Deployment Template</a></li><li><a href="#s6-4">6.4 Services & Ingress</a></li><li><a href="#s6-5">6.5 ConfigMaps & Secrets</a></li><li><a href="#s6-6">6.6 values.yaml</a></li><li><a href="#s6-7">6.7 Testing</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch7" class="chapter-link"><span class="chapter-number">Ch 7</span>Dependencies & Subcharts</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s7-1">7.1 Chart Dependencies</a></li><li><a href="#s7-2">7.2 Managing Deps</a></li><li><a href="#s7-3">7.3 Subcharts</a></li><li><a href="#s7-4">7.4 PostgreSQL for anihpj</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch8" class="chapter-link"><span class="chapter-number">Ch 8</span>Hooks, Tests & Lifecycle</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s8-1">8.1 Chart Hooks</a></li><li><a href="#s8-2">8.2 anihpj Hooks</a></li><li><a href="#s8-3">8.3 Chart Tests</a></li><li><a href="#s8-4">8.4 anihpj Tests</a></li></ul></li>
                </ul>
            </li>
            <!-- PART 3 -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>🔧 Part 3: Advanced Patterns</span><span class="part-badge advanced">🔴 Advanced</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch9" class="chapter-link"><span class="chapter-number">Ch 9</span>Values Management</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s9-1">9.1 Value Sources</a></li><li><a href="#s9-2">9.2 Schema Validation</a></li><li><a href="#s9-3">9.3 Environment Configs</a></li><li><a href="#s9-4">9.4 Advanced Templates</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch10" class="chapter-link"><span class="chapter-number">Ch 10</span>Library Charts</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s10-1">10.1 What Are Library Charts?</a></li><li><a href="#s10-2">10.2 anihpj Library Chart</a></li><li><a href="#s10-3">10.3 Using Library Charts</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch11" class="chapter-link"><span class="chapter-number">Ch 11</span>Helm + GitOps</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s11-1">11.1 Helm + ArgoCD</a></li><li><a href="#s11-2">11.2 Helm + FluxCD</a></li><li><a href="#s11-3">11.3 CI/CD Pipelines</a></li><li><a href="#s11-4">11.4 anihpj Full Pipeline</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch12" class="chapter-link"><span class="chapter-number">Ch 12</span>Helmfile</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s12-1">12.1 What is Helmfile?</a></li><li><a href="#s12-2">12.2 Structure</a></li><li><a href="#s12-3">12.3 anihpj Helmfile</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch13" class="chapter-link"><span class="chapter-number">Ch 13</span>OCI Registries</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s13-1">13.1 OCI Support</a></li><li><a href="#s13-2">13.2 Push & Pull via OCI</a></li><li><a href="#s13-3">13.3 OCI vs Classic</a></li><li><a href="#s13-4">13.4 anihpj Distribution</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch14" class="chapter-link"><span class="chapter-number">Ch 14</span>Security & Best Practices</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s14-1">14.1 Chart Security</a></li><li><a href="#s14-2">14.2 K8s Security</a></li><li><a href="#s14-3">14.3 Provenance</a></li><li><a href="#s14-4">14.4 Production Practices</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch15" class="chapter-link"><span class="chapter-number">Ch 15</span>Troubleshooting</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s15-1">15.1 Install Errors</a></li><li><a href="#s15-2">15.2 Debugging Templates</a></li><li><a href="#s15-3">15.3 Release Issues</a></li><li><a href="#s15-4">15.4 anihpj Scenarios</a></li></ul></li>
                </ul>
            </li>
            <!-- PART 4 -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>🚀 Part 4: Production & Beyond</span><span class="part-badge advanced">🔴 Advanced</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch16" class="chapter-link"><span class="chapter-number">Ch 16</span>Helm at Scale</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s16-1">16.1 Multi-Cluster</a></li><li><a href="#s16-2">16.2 Multi-Tenant</a></li><li><a href="#s16-3">16.3 Service Mesh</a></li><li><a href="#s16-4">16.4 Monitoring</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch17" class="chapter-link"><span class="chapter-number">Ch 17</span>Migrating to Helm</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s17-1">17.1 Assessment</a></li><li><a href="#s17-2">17.2 Migration Strategy</a></li><li><a href="#s17-3">17.3 Zero-Downtime</a></li><li><a href="#s17-4">17.4 anihpj Migration</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#ch18" class="chapter-link"><span class="chapter-number">Ch 18</span>Ecosystem & Community</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#s18-1">18.1 Plugins</a></li><li><a href="#s18-2">18.2 Community Charts</a></li><li><a href="#s18-3">18.3 Artifact Hub</a></li><li><a href="#s18-4">18.4 Contributing</a></li></ul></li>
                </ul>
            </li>
            <!-- APPENDICES -->
            <li>
                <div class="part-header" onclick="togglePart(this)"><div class="part-title"><span>📎 Appendices</span><span class="part-badge">🏆 Reference</span></div></div>
                <ul class="chapter-list visible">
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-a" class="chapter-link"><span class="chapter-number">A</span>CLI Command Reference</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#sa-1">A.1 Chart Management</a></li><li><a href="#sa-2">A.2 Release Lifecycle</a></li><li><a href="#sa-3">A.3 Repositories & OCI</a></li><li><a href="#sa-4">A.4 Debugging & Plugins</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-b" class="chapter-link"><span class="chapter-number">B</span>Complete anihpj Chart</a><button class="section-toggle-btn" onclick="toggleSections(this)">▶</button></div><ul class="sub-toc visible"><li><a href="#sb-1">B.1 Chart.yaml</a></li><li><a href="#sb-2">B.2 values.yaml</a></li><li><a href="#sb-3">B.3 deployment.yaml</a></li><li><a href="#sb-4">B.4 service.yaml</a></li><li><a href="#sb-5">B.5 ingress.yaml</a></li><li><a href="#sb-6">B.6 _helpers.tpl</a></li><li><a href="#sb-7">B.7 NOTES.txt</a></li></ul></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-c" class="chapter-link"><span class="chapter-number">C</span>Quick Reference Cards</a></li></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-d" class="chapter-link"><span class="chapter-number">D</span>Common Errors & Solutions</a></li></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-e" class="chapter-link"><span class="chapter-number">E</span>Helm Glossary</a></li></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-f" class="chapter-link"><span class="chapter-number">F</span>10-Week Study Plan</a></li></li>
                    <li class="chapter-item"><div class="chapter-row"><a href="#appendix-g" class="chapter-link"><span class="chapter-number">G</span>Practice Exam (30 Qs)</a></li></li>
                </ul>
            </li>
        </ul>
    </nav>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                          HEADER                                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->
    <header>
        <h1>⚓ Helm — The Kubernetes Package Manager</h1>
        <p class="subtitle">Complete Learning Guide — From Zero to Production-Ready Helm Charts</p>
        <p class="description">Master Helm from first principles: charts, templates, releases, hooks, GitOps integration, OCI registries, and production best practices — all using the <strong>anihpj/jobpost</strong> Django project as your hands-on example.</p>
        <div class="header-tags">
            <span class="tag">⚓ Helm v3</span>
            <span class="tag beginner">🟢 Beginner-Friendly</span>
            <span class="tag">☸️ Kubernetes</span>
            <span class="tag">📦 Charts</span>
            <span class="tag">📋 18 Chapters</span>
            <span class="tag">📎 7 Appendices</span>
        </div>
    </header>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                        MAIN CONTENT                            -->
<!-- ═══════════════════════════════════════════════════════════════ -->
    <main>
        <div class="intro-callout">
            <p><strong>⚓ Welcome!</strong> This guide takes you from complete beginner to Helm expert. Every concept is explained with real examples using the <strong>anihpj/jobpost</strong> Django project — you'll build, package, deploy, and distribute production-ready Helm charts. By the end, you'll confidently manage any Kubernetes application with Helm.</p>
        </div>

<!-- ═══ MAIN TOC GRID ═══ -->
        <section class="toc-section" id="front-toc">
            <h2>📚 Complete Table of Contents</h2>
            <div class="toc-grid">
                <div class="toc-card"><a href="#part1"><div class="card-header"><span class="card-icon">📚</span><span class="card-part-badge beginner">🟢 Beginner</span></div><h3>Part 1: Helm Fundamentals</h3><p class="card-subtitle">Chapters 1-3 · ~4 hours</p><p>What is Helm? Architecture, installation, first release. The "YAML Hell" problem solved.</p><div class="card-chapters"><span class="chapter-tag">Ch 1-3</span><span class="chapter-tag">~4 hrs</span></div></a></div>
                <div class="toc-card"><a href="#part2"><div class="card-header"><span class="card-icon">📦</span><span class="card-part-badge intermediate">🟡 Intermediate</span></div><h3>Part 2: Chart Development</h3><p class="card-subtitle">Chapters 4-8 · ~6 hours</p><p>Chart structure, Go templates, building the anihpj chart from scratch, dependencies, hooks and tests.</p><div class="card-chapters"><span class="chapter-tag">Ch 4-8</span><span class="chapter-tag">~6 hrs</span></div></a></div>
                <div class="toc-card"><a href="#part3"><div class="card-header"><span class="card-icon">🔧</span><span class="card-part-badge advanced">🔴 Advanced</span></div><h3>Part 3: Advanced Patterns</h3><p class="card-subtitle">Chapters 9-15 · ~5 hours</p><p>Values management, library charts, GitOps + ArgoCD, Helmfile, OCI registries, security, troubleshooting.</p><div class="card-chapters"><span class="chapter-tag">Ch 9-15</span><span class="chapter-tag">~5 hrs</span></div></a></div>
                <div class="toc-card"><a href="#part4"><div class="card-header"><span class="card-icon">🚀</span><span class="card-part-badge advanced">🔴 Advanced</span></div><h3>Part 4: Production & Beyond</h3><p class="card-subtitle">Chapters 16-18 · ~3 hours</p><p>Multi-cluster, migration, ecosystem plugins, community charts, Artifact Hub, contributing.</p><div class="card-chapters"><span class="chapter-tag">Ch 16-18</span><span class="chapter-tag">~3 hrs</span></div></a></div>
            </div>
        </section>

<!-- ═══ APPENDIX GRID ═══ -->
        <section class="toc-section" id="front-appendices">
            <h2>📎 Appendices — Quick Reference</h2>
            <div class="appendix-grid">
                <div class="appendix-card"><a href="#appendix-a"><h4>📋 Appendix A: CLI Command Reference</h4><p>Every Helm command organized by category</p></a></div>
                <div class="appendix-card"><a href="#appendix-b"><h4>📦 Appendix B: Complete anihpj Chart</h4><p>Full production-ready Helm chart with all templates</p></a></div>
                <div class="appendix-card"><a href="#appendix-c"><h4>📊 Appendix C: Quick Reference Cards</h4><p>Values precedence, template functions, hooks reference</p></a></div>
                <div class="appendix-card"><a href="#appendix-d"><h4>🔧 Appendix D: Common Errors</h4><p>Error → Cause → Fix quick reference</p></a></div>
                <div class="appendix-card"><a href="#appendix-e"><h4>📖 Appendix E: Glossary</h4><p>50+ Helm terms defined</p></a></div>
                <div class="appendix-card"><a href="#appendix-f"><h4>📅 Appendix F: 10-Week Study Plan</h4><p>Week-by-week from zero to Helm expert</p></a></div>
                <div class="appendix-card"><a href="#appendix-g"><h4>🧪 Appendix G: Practice Exam</h4><p>30 questions with full answer key</p></a></div>
            </div>
        </section>

<!-- ═══ MASTER SUMMARY ═══ -->
        <section id="master-summary">
            <div class="summary-hero">
                <span class="hero-icon">🗺️</span>
                <h2>Master Summary & Implementation Roadmap</h2>
                <p class="hero-subtitle">Your Complete Helm Journey — From Zero to Production-Ready Charts</p>
                <p class="hero-desc">This guide takes you from complete beginner to Helm expert with <strong>4 Parts</strong>, <strong>18 Chapters</strong>, <strong>7 Appendices</strong>, and <strong>30 Practice Questions</strong> — all using the <strong>anihpj/jobpost</strong> Django project.</p>
            </div>
            <div class="summary-stats-bar">
                <div class="summary-stat-card"><span class="stat-icon">📚</span><span class="stat-number purple">4</span><span class="stat-text">Learning Parts</span></div>
                <div class="summary-stat-card"><span class="stat-icon">📖</span><span class="stat-number green">18</span><span class="stat-text">Chapters</span></div>
                <div class="summary-stat-card"><span class="stat-icon">📎</span><span class="stat-number blue">7</span><span class="stat-text">Appendices</span></div>
                <div class="summary-stat-card"><span class="stat-icon">🧪</span><span class="stat-number orange">30+</span><span class="stat-text">Practice Questions</span></div>
                <div class="summary-stat-card"><span class="stat-icon">⏱️</span><span class="stat-number green">~18</span><span class="stat-text">Hours Total</span></div>
                <div class="summary-stat-card"><span class="stat-icon">🚀</span><span class="stat-number purple">1</span><span class="stat-text">Real Project</span></div>
            </div>
        </section>

<!-- ═══ HELM CLI QUICK REFERENCE ═══ -->
        <section class="chapter-section" id="quick-ref">
            <h2><span>⚡ Helm CLI Quick Reference</span><span class="chapter-badge">Must Know</span></h2>
            <p style="color:#8b949e;margin-bottom:20px;">Every Helm command you'll use daily — organized by category.</p>
            <div class="compare-table"><table><thead><tr><th colspan="2">📦 Chart Management</th></tr></thead><tbody>
                <tr><td><strong>helm create mychart</strong></td><td>Scaffold a new chart directory</td></tr>
                <tr><td><strong>helm lint ./mychart</strong></td><td>Validate chart structure and templates</td></tr>
                <tr><td><strong>helm package ./mychart</strong></td><td>Create versioned .tgz archive</td></tr>
                <tr><td><strong>helm template ./mychart</strong></td><td>Render templates locally (no cluster needed)</td></tr>
            </tbody></table></div>
            <div class="compare-table" style="margin-top:24px;"><table><thead><tr><th colspan="2">🚀 Release Lifecycle</th></tr></thead><tbody>
                <tr><td><strong>helm install myapp ./chart</strong></td><td>Deploy a new release</td></tr>
                <tr><td><strong>helm list -A</strong></td><td>List all releases across namespaces</td></tr>
                <tr><td><strong>helm upgrade myapp ./chart</strong></td><td>Upgrade to new chart version / values</td></tr>
                <tr><td><strong>helm rollback myapp 1</strong></td><td>Roll back to revision 1</td></tr>
                <tr><td><strong>helm uninstall myapp</strong></td><td>Remove the release</td></tr>
                <tr><td><strong>helm history myapp</strong></td><td>Show all revisions with status</td></tr>
            </tbody></table></div>
            <div class="compare-table" style="margin-top:24px;"><table><thead><tr><th colspan="2">🔍 Debugging & Inspection</th></tr></thead><tbody>
                <tr><td><strong>helm get manifest myapp</strong></td><td>See exactly what was deployed</td></tr>
                <tr><td><strong>helm get values myapp --all</strong></td><td>See all resolved values</td></tr>
                <tr><td><strong>helm install --dry-run --debug</strong></td><td>Full simulation without applying</td></tr>
                <tr><td><strong>helm template --debug</strong></td><td>Debug template rendering locally</td></tr>
            </tbody></table></div>
        </section>

<!-- ═══ TOP 10 HELM MISTAKES ═══ -->
        <section class="chapter-section" id="helm-mistakes">
            <h2><span>⚠️ Top 10 Helm Mistakes & How to Avoid Them</span><span class="chapter-badge">Critical</span></h2>
            <div class="split-panel">
                <div class="split-side split-bad"><h5>❌ Common Mistakes</h5><ul><li>Hardcoding values in templates instead of using .Values</li><li>Committing secrets in values.yaml to Git</li><li>Not pinning chart versions (using "latest")</li><li>Skipping helm lint before packaging</li><li>Not using --dry-run before applying</li><li>Forgetting helm dependency update</li><li>Using --force on upgrades without --atomic</li><li>Not setting resource limits in templates</li><li>Confusing .Values and .Release</li><li>Not using _helpers.tpl for repeated logic</li></ul></div>
                <div class="split-side split-good"><h5>✅ Correct Approach</h5><ul><li>Reference via {{ .Values.key }} always</li><li>Use .helmignore + External Secrets Operator</li><li>Always specify --version 1.2.3</li><li>helm lint ./chart in CI pipeline</li><li>Always dry-run before production changes</li><li>Run after editing Chart.yaml dependencies</li><li>Use --atomic for auto-rollback on failure</li><li>Template requests/limits in values.yaml</li><li>.Values = config, .Release = runtime info</li><li>DRY principle: reusable named templates</li></ul></div>
            </div>
        </section>

<!-- ═══ CONTENT PLACEHOLDERS ═══ -->
        <section class="chapter-section" id="part1"><h2><span>📚 Part 1: Helm Fundamentals</span><span class="chapter-badge">Ch 1-3</span></h2>
            <div id="ch1"><div class="chapter-intro"><h3>Chapter 1: What is Helm?</h3><p>Content coming soon — detailed chapter with diagrams, code examples, and practice questions.</p><div class="chapter-meta"><span class="meta-tag">🟢 Beginner</span><span class="meta-tag">⏱️ ~1.5 hours</span></div></div></div>
            <div id="ch2"><div class="chapter-intro"><h3>Chapter 2: Helm Architecture</h3><p>Content coming soon.</p><div class="chapter-meta"><span class="meta-tag">🟢 Beginner</span><span class="meta-tag">⏱️ ~1.5 hours</span></div></div></div>
            <div id="ch3"><div class="chapter-intro"><h3>Chapter 3: Installing & Configuring Helm</h3><p>Content coming soon.</p><div class="chapter-meta"><span class="meta-tag">🟢 Beginner</span><span class="meta-tag">⏱️ ~1 hour</span></div></div></div>
        </section>
        <section class="chapter-section" id="part2"><h2><span>📦 Part 2: Chart Development</span><span class="chapter-badge">Ch 4-8</span></h2>
            <div id="ch4"><div class="chapter-intro"><h3>Chapter 4: Chart Structure</h3><p>Content coming soon.</p></div></div>
            <div id="ch5"><div class="chapter-intro"><h3>Chapter 5: Templates</h3><p>Content coming soon.</p></div></div>
            <div id="ch6"><div class="chapter-intro"><h3>Chapter 6: Building the anihpj Chart</h3><p>Content coming soon.</p></div></div>
            <div id="ch7"><div class="chapter-intro"><h3>Chapter 7: Dependencies & Subcharts</h3><p>Content coming soon.</p></div></div>
            <div id="ch8"><div class="chapter-intro"><h3>Chapter 8: Hooks, Tests & Lifecycle</h3><p>Content coming soon.</p></div></div>
        </section>
        <section class="chapter-section" id="part3"><h2><span>🔧 Part 3: Advanced Patterns</span><span class="chapter-badge">Ch 9-15</span></h2>
            <div id="ch9"><div class="chapter-intro"><h3>Chapter 9: Values Management</h3><p>Content coming soon.</p></div></div>
            <div id="ch10"><div class="chapter-intro"><h3>Chapter 10: Library Charts</h3><p>Content coming soon.</p></div></div>
            <div id="ch11"><div class="chapter-intro"><h3>Chapter 11: Helm + GitOps</h3><p>Content coming soon.</p></div></div>
            <div id="ch12"><div class="chapter-intro"><h3>Chapter 12: Helmfile</h3><p>Content coming soon.</p></div></div>
            <div id="ch13"><div class="chapter-intro"><h3>Chapter 13: OCI Registries</h3><p>Content coming soon.</p></div></div>
            <div id="ch14"><div class="chapter-intro"><h3>Chapter 14: Security & Best Practices</h3><p>Content coming soon.</p></div></div>
            <div id="ch15"><div class="chapter-intro"><h3>Chapter 15: Troubleshooting</h3><p>Content coming soon.</p></div></div>
        </section>
        <section class="chapter-section" id="part4"><h2><span>🚀 Part 4: Production & Beyond</span><span class="chapter-badge">Ch 16-18</span></h2>
            <div id="ch16"><div class="chapter-intro"><h3>Chapter 16: Helm at Scale</h3><p>Content coming soon.</p></div></div>
            <div id="ch17"><div class="chapter-intro"><h3>Chapter 17: Migrating to Helm</h3><p>Content coming soon.</p></div></div>
            <div id="ch18"><div class="chapter-intro"><h3>Chapter 18: Ecosystem & Community</h3><p>Content coming soon.</p></div></div>
        </section>
        <!-- APPENDIX PLACEHOLDERS -->
        <section class="chapter-section" id="appendix-a"><h2><span>📎 Appendix A: CLI Command Reference</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-b"><h2><span>📎 Appendix B: Complete anihpj Chart</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-c"><h2><span>📎 Appendix C: Quick Reference Cards</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-d"><h2><span>📎 Appendix D: Common Errors</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-e"><h2><span>📎 Appendix E: Glossary</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-f"><h2><span>📎 Appendix F: 10-Week Study Plan</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
        <section class="chapter-section" id="appendix-g"><h2><span>📎 Appendix G: Practice Exam</span><span class="chapter-badge">Reference</span></h2><p style="color:#8b949e;">Content coming soon.</p></section>
    </main>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                          FOOTER                                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->
    <footer>
        <p>⚓ <strong>Helm — The Kubernetes Package Manager</strong> | Complete Learning Guide</p>
        <p>Built with the anihpj/jobpost Django project as a hands-on example throughout</p>
        <p style="margin-top:12px;">4 Parts · 18 Chapters · 7 Appendices · 30+ Practice Questions · ~18 Hours</p>
        <p style="margin-top:8px;font-size:0.8em;">Helm is a <a href="https://www.cncf.io" target="_blank">CNCF</a> graduated project. Official docs: <a href="https://helm.sh/docs/" target="_blank">helm.sh/docs</a></p>
    </footer>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                        JAVASCRIPT                               -->
<!-- ═══════════════════════════════════════════════════════════════ -->
    <script>
        const tocToggle = document.getElementById('tocToggle');
        const tocSidebar = document.getElementById('tocSidebar');
        tocToggle.addEventListener('click', () => { document.body.classList.toggle('toc-open'); });
        function togglePart(header) { const list = header.nextElementSibling; if (list) list.classList.toggle('visible'); }
        function toggleSections(btn) { const sub = btn.closest('.chapter-item').querySelector('.sub-toc'); if (sub) { sub.classList.toggle('visible'); btn.textContent = sub.classList.contains('visible') ? '▼' : '▶'; } }
        function expandAllParts() { document.querySelectorAll('.chapter-list').forEach(l => l.classList.add('visible')); }
        function collapseAllParts() { document.querySelectorAll('.chapter-list').forEach(l => l.classList.remove('visible')); }
        document.querySelectorAll('.chapter-link').forEach(link => { link.addEventListener('click', function() { if (window.innerWidth < 1000) document.body.classList.remove('toc-open'); }); });
        document.querySelectorAll('.toc-card a, .appendix-card a').forEach(link => { link.addEventListener('click', function(e) { e.preventDefault(); const t = document.querySelector(this.getAttribute('href')); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }); });
    </script>
</body>
</html>
'@

[System.IO.File]::WriteAllText((Resolve-Path $f), $css)
Write-Host "helm.html created: $([math]::Round((Get-Item $f).Length/1024,1))KB"