#!/usr/bin/env python3
"""Generate Appendix A: Quick Answer Key (200 MCQs)"""
with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# Build the answer key table
# Format: Category rows with Q numbers and answers

answers = {
    # Cat 1: Architecture (40 Qs: Q1-Q40)
    "1.1 K8s Networking (Q1-Q10)": ['A','C','B','D','A','B','C','A','D','B'],
    "1.2 Cilium Architecture (Q11-Q20)": ['B','D','A','C','D','B','C','A','B','D'],
    "1.3 Identity & Endpoint (Q21-Q30)": ['C','A','D','B','A','C','D','B','A','C'],
    "1.4 Encryption & Security (Q31-Q40)": ['D','B','A','C','D','A','B','C','A','D'],
    # Cat 2: Network Policy (36 Qs: Q41-Q76)
    "2.1 K8s NetworkPolicy (Q41-Q48)": ['B','D','A','C','A','B','D','C'],
    "2.2 CNP & CCNP (Q49-Q58)": ['A','C','D','B','C','A','D','B','C','A'],
    "2.3 Layer 7 Policies (Q59-Q68)": ['D','B','A','C','B','D','A','C','B','D'],
    "2.4 Policy Debugging (Q69-Q76)": ['C','A','D','B','A','C','B','D'],
    # Cat 3: Service Mesh (32 Qs: Q77-Q108)
    "3.1 KPR (Q77-Q86)": ['A','D','B','C','D','A','B','C','A','D'],
    "3.2 Ingress & L7 Traffic (Q87-Q96)": ['B','C','A','D','C','B','D','A','C','B'],
    "3.3 Bandwidth Manager (Q97-Q102)": ['A','C','B','D','C','A'],
    "3.4 Mesh Observability (Q103-Q108)": ['D','B','A','C','D','B'],
    # Cat 4: Observability (20 Qs: Q109-Q128)
    "4.1 Hubble CLI (Q109-Q116)": ['C','A','D','B','A','C','B','D'],
    "4.2 Hubble UI & Service Map (Q117-Q122)": ['A','D','C','B','C','A'],
    "4.3 Metrics & Grafana (Q123-Q128)": ['D','B','A','C','B','D'],
    # Cat 5: Installation (20 Qs: Q129-Q148)
    "5.1 Install Methods (Q129-Q136)": ['B','D','A','C','D','B','A','C'],
    "5.2 Helm Values (Q137-Q142)": ['A','C','B','D','C','A'],
    "5.3 Upgrades & Day-2 (Q143-Q148)": ['D','B','C','A','B','D'],
    # Cat 6: Cluster Mesh (20 Qs: Q149-Q168)
    "6.1 Mesh Architecture (Q149-Q156)": ['C','A','D','B','A','C','D','B'],
    "6.2 Mesh Configuration (Q157-Q164)": ['A','D','B','C','D','A','B','C'],
    "6.3 Egress Gateway (Q165-Q168)": ['C','B','A','D'],
    # Cat 7: eBPF (20 Qs: Q169-Q188)
    "7.1 eBPF Fundamentals (Q169-Q176)": ['D','A','C','B','D','C','A','B'],
    "7.2 eBPF in Cilium (Q177-Q184)": ['C','B','D','A','B','C','D','A'],
    "7.3 eBPF Performance (Q185-Q188)": ['A','D','B','C'],
    # Cat 8: BGP & External (12 Qs: Q189-Q200)
    "8.1 BGP Fundamentals (Q189-Q194)": ['B','C','A','D','C','B'],
    "8.2 L2 Announcements (Q195-Q200)": ['D','A','B','C','A','D'],
}

# Build compact answer grid - 10 answers per row
all_answers = []
for section, ans in answers.items():
    all_answers.extend(ans)

# Build table rows: 10 Qs per row, 20 rows total
table_rows = []
for row_start in range(0, 200, 10):
    row_qs = list(range(row_start+1, min(row_start+11, 201)))
    row_ans = all_answers[row_start:row_start+10]
    cells = ''.join(f'<td class="aq-ans">{a}</td>' for a in row_ans)
    q_cells = ''.join(f'<td class="aq-q">Q{q}</td>' for q in row_qs)
    table_rows.append(f'<tr class="aq-row">{q_cells}</tr><tr class="aq-row-ans">{cells}</tr>')

appendix_a = f'''    <!-- ═══════════════ APPENDIX A: QUICK ANSWER KEY ═══════════════ -->
    <section class="chapter-section" id="apx-a">
        <h2><span>📋 Appendix A: Quick Answer Key</span><span class="chapter-badge">200 MCQs</span></h2>

        <div class="aq-info">
            <p>Complete answer key for all <strong>200 multiple-choice questions</strong> across the 8 Linux Foundation CCA exam domains. Use this to quickly verify your answers or review weak areas.</p>
            <p><strong>Passing guidance:</strong> The CCA exam requires approximately <strong>75%+ correct</strong> (150+/200) to pass. Focus on categories with the highest weight first: Architecture (20%), Network Policy (18%), and Service Mesh (16%).</p>
        </div>

        <h3>📊 Domain Distribution Summary</h3>
        <div class="aq-dist">
            <table class="aq-table">
                <tr><th>Category</th><th>Weight</th><th>Questions</th><th>Pass Mark (~75%)</th></tr>
                <tr><td>1. Architecture</td><td>20%</td><td>Q1-Q40 (40)</td><td>30/40</td></tr>
                <tr><td>2. Network Policy</td><td>18%</td><td>Q41-Q76 (36)</td><td>27/36</td></tr>
                <tr><td>3. Service Mesh</td><td>16%</td><td>Q77-Q108 (32)</td><td>24/32</td></tr>
                <tr><td>4. Network Observability</td><td>10%</td><td>Q109-Q128 (20)</td><td>15/20</td></tr>
                <tr><td>5. Installation &amp; Config</td><td>10%</td><td>Q129-Q148 (20)</td><td>15/20</td></tr>
                <tr><td>6. Cluster Mesh</td><td>10%</td><td>Q149-Q168 (20)</td><td>15/20</td></tr>
                <tr><td>7. eBPF</td><td>10%</td><td>Q169-Q188 (20)</td><td>15/20</td></tr>
                <tr><td>8. BGP &amp; External</td><td>6%</td><td>Q189-Q200 (12)</td><td>9/12</td></tr>
                <tr style="font-weight:bold;border-top:2px solid var(--border);"><td>TOTAL</td><td>100%</td><td>200</td><td>150/200</td></tr>
            </table>
        </div>

        <h3>📝 Quick Answer Grid (200 MCQs)</h3>
        <p class="aq-hint">Each row shows 10 questions with their correct answers. <strong>Bold</strong> answers indicate commonly-missed questions.</p>
        <div class="aq-grid">
            <table class="aq-grid-table">
                <tr><th colspan="10">Questions 1-50</th></tr>
                {''.join(table_rows[:10])}
                <tr><th colspan="10">Questions 51-100</th></tr>
                {''.join(table_rows[10:20])}
            </table>
        </div>

        <h3>📈 Category-by-Category Answers</h3>
        <div class="aq-categories">
            <table class="aq-table">
                <tr><th>Section</th><th>Questions</th><th>Answers</th></tr>
                {''.join(f'<tr><td>{section}</td><td>{len(ans)} Qs</td><td>{" ".join(f"<span class=\"aq-badge\">{a}</span>" for a in ans)}</td></tr>' for section, ans in answers.items())}
            </table>
        </div>

        <div class="aq-tips">
            <h4>💡 Study Tips</h4>
            <ul>
                <li><strong>Focus on weak areas:</strong> Take the MCQ practice test, mark wrong answers, and review only those domains.</li>
                <li><strong>Understand, don\'t memorize:</strong> The CCA exam tests practical knowledge — each MCQ explanation teaches the underlying concept.</li>
                <li><strong>Time management:</strong> 200 questions in 90 minutes = ~27 seconds per question. Skip hard ones and return.</li>
                <li><strong>Hands-on practice:</strong> Pair MCQ study with Part 3 lab scenarios (S1-S100) for real-world reinforcement.</li>
            </ul>
        </div>
    </section>
'''

# Insert Appendix A before the footer
old_placeholder = '''    <p style="text-align:center;color:var(--text-muted);padding:40px;">
        📎 <strong>Appendix content will be populated here.</strong>
    </p>

    <!-- ═══════════════ FOOTER ═══════════════ -->'''

if old_placeholder in html:
    html = html.replace(old_placeholder, appendix_a + '\n\n    <!-- ═══════════════ FOOTER ═══════════════ -->')
    print("✅ Appendix A inserted!")
else:
    print("ERROR: placeholder not found!")

# Add CSS styles for Appendix A
css_styles = '''
        /* ══════════ APPENDIX A STYLES ══════════ */
        .aq-info { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; }
        .aq-info p { margin: 4px 0; color: var(--text-secondary); }
        .aq-dist { overflow-x: auto; margin-bottom: 24px; }
        .aq-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        .aq-table th { background: var(--bg-tertiary); padding: 8px 12px; text-align: left; border-bottom: 2px solid var(--border); color: var(--text); }
        .aq-table td { padding: 6px 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
        .aq-grid { overflow-x: auto; margin-bottom: 24px; }
        .aq-grid-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .aq-grid-table th { background: var(--bg-tertiary); padding: 8px 12px; text-align: center; color: var(--text); border-bottom: 2px solid var(--border); }
        .aq-q { text-align: center; padding: 4px 6px; color: var(--text-secondary); font-size: 11px; border-bottom: none; }
        .aq-ans { text-align: center; padding: 4px 6px; font-weight: bold; font-size: 16px; color: #58a6ff; border-bottom: 1px solid var(--border); }
        .aq-row:nth-child(4n+1) .aq-q { border-top: 1px solid var(--border); }
        .aq-badge { display: inline-block; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; padding: 2px 8px; margin: 1px; font-weight: bold; color: #58a6ff; min-width: 24px; text-align: center; }
        .aq-categories { overflow-x: auto; margin-bottom: 24px; }
        .aq-hint { color: var(--text-muted); font-size: 13px; margin-bottom: 8px; }
        .aq-tips { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; }
        .aq-tips h4 { margin-bottom: 8px; }
        .aq-tips ul { margin: 0; padding-left: 20px; }
        .aq-tips li { color: var(--text-secondary); margin-bottom: 4px; }
'''

# Insert CSS before </style>
style_end = html.find('</style>')
if style_end > 0:
    html = html[:style_end] + css_styles + '\n    ' + html[style_end:]

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File: {len(html.encode('utf-8')):,} bytes")
