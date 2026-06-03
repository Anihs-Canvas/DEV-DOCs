with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    <!-- ═══════════════════════════════════════════════════════════
         PART 1: 200 MCQs — CONTENT GOES HERE
         ═══════════════════════════════════════════════════════════ -->

    <section class="chapter-section" id="part1-intro">
        <h2><span>📝 Part 1: 200 Multiple Choice Questions</span><span class="chapter-badge">8 Categories · LF Official</span></h2>
        <div class="chapter-intro">
            <h3>Organized by Linux Foundation Official CCA Exam Categories</h3>
            <p>200 MCQs evenly distributed across all 8 exam categories with answers and detailed explanations. Each question targets a specific CCA knowledge area.</p>
            <div class="chapter-meta">
                <span class="meta-tag">1. Architecture (40 Qs · 20%)</span>
                <span class="meta-tag">2. Network Policy (36 Qs · 18%)</span>
                <span class="meta-tag">3. Service Mesh (32 Qs · 16%)</span>
                <span class="meta-tag">4. Observability (20 Qs · 10%)</span>
                <span class="meta-tag">5. Installation (20 Qs · 10%)</span>
                <span class="meta-tag">6. Cluster Mesh (20 Qs · 10%)</span>
                <span class="meta-tag">7. eBPF (20 Qs · 10%)</span>
                <span class="meta-tag">8. BGP & External (12 Qs · 6%)</span>
            </div>
        </div>
    </section>'''

new = '''    <!-- ═══════════════ PART 1 ═══════════════ -->
    <div class="part-banner part1">
        <h2>📝 Part 1: 200 Multiple Choice Questions</h2>
        <p class="part-subtitle">Organized by Linux Foundation Official CCA Exam Categories — 200 MCQs evenly distributed across all 8 exam categories with answers and detailed explanations.</p>
        <div class="part-stats">
            <div class="part-stat"><span class="ps-num">200</span><span class="ps-label">MCQ Questions</span></div>
            <div class="part-stat"><span class="ps-num">8</span><span class="ps-label">Categories</span></div>
            <div class="part-stat"><span class="ps-num">90 min</span><span class="ps-label">Exam Weight</span></div>
        </div>
    </div>'''

if old in content:
    content = content.replace(old, new)
    with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Part 1 banner replaced successfully!')
else:
    print('Old text not found. Checking...')
    idx = content.find('PART 1: 200 MCQs')
    if idx > 0:
        print(f'Found at position {idx}')
        print(repr(content[idx-50:idx+100]))
