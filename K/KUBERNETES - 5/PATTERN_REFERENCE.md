# COMPREHENSIVE PATTERN REFERENCE: cka.html & NVIDIA_ast.html

## FILE OVERVIEW
| Property | cka.html | NVIDIA_ast.html |
|---|---|---|
| Size | ~3.7 MB | ~1.5 MB |
| Theme | Kubernetes CKA Certification | NVIDIA Accelerated Computing (NCA-AIIO) |
| Chapters | 40 chapters + 9 appendices | ~17 chapters + front matter + exam amplification |
| Parts | 11 Parts | 4 Parts |
| Color accent | Blue (#326ce5, #60a5fa) | NVIDIA Green (#76b900) / Blue (#326ce5) |

---

## 1. SIDEBAR / TOC PATTERN

### 1.1 Overall Structure
The sidebar is a fixed-position `<nav>` element that slides in/out using CSS `transform: translateX(-100%)` → `translateX(0)`.

```
HTML document
├── <button id="tocToggle" class="toc-toggle">  ← fixed toggle button, z-index: 1100
├── <nav id="tocSidebar" class="toc-sidebar">    ← fixed sidebar, z-index: 1000
├── <header>
├── <main>
└── <footer>
```

### 1.2 Key CSS Classes for Sidebar/Navigation

| Class | Purpose |
|---|---|
| `.toc-sidebar` | Fixed sidebar nav. 340px wide, `#161b22` bg, `transform: translateX(-100%)`, `transition: transform 250ms ease` |
| `.toc-toggle` | Fixed toggle button (☰ Contents). top:18px, left:18px, z-index:1100 |
| `.sidebar-header` | Flex row with title + expand/collapse buttons |
| `.sidebar-controls` | Container for ⊞/⊟ buttons |
| `.expand-collapse-btn` | Small blue button for Expand All / Collapse All |
| `.toc-list` | Root `<ul>` with `list-style: none`, `padding: 0 12px` |
| `.part-header` | Clickable part divider. Gradient bg, cursor:pointer, rounded 8px |
| `.part-title` | Flex row inside part-header: name + badge |
| `.part-badge` | Small pill: `.beginner` (green), `.intermediate` (yellow), `.advanced` (red) |
| `.chapter-list` | `<ul>` under part-header. **`display: none`** by default |
| `.chapter-list.visible` | **`display: block`** — toggled by JS |
| `.chapter-item` | `<li>` wrapper for each chapter |
| `.chapter-row` | Flex row: `.chapter-link` + `.section-toggle-btn` |
| `.chapter-link` | `<a>` with left border highlight. `.active` variant for scroll tracking |
| `.chapter-number` | Small gray span for "Ch 1", "Ch 2" numbering |
| `.section-toggle-btn` | ▶ button to expand/collapse sub-sections |
| `.sub-toc` | `<ul>` for sub-sections. **`display: none`** by default |
| `.sub-toc.visible` | **`display: block`** — toggled by JS |
| `.has-children` | Applied to `<li>` items that contain 3rd-level nesting |
| `.sub-sub-toggle` | ▸ button for 3rd-level expand/collapse |
| `.sub-sub-toc` | `<ul>` for 3rd-level nesting. **`display: none`** by default |
| `.sub-sub-toc.visible` | **`display: block`** |

### 1.3 3-Level Nesting (Part → Chapter → Sub-Section → Sub-Sub-Section)

```
.toc-list
  └── <li>                          ← Each Part is an <li>
        ├── <div class="part-header" onclick="togglePart(this)">
        │     └── <div class="part-title">
        │           ├── <span>Part Name</span>
        │           └── <span class="part-badge beginner">BEGINNER</span>
        │
        └── <ul class="chapter-list">    ← LEVEL 1: Chapters (default: hidden)
              └── <li class="chapter-item">
                    ├── <div class="chapter-row">
                    │     ├── <a href="#ch1" class="chapter-link">
                    │     │     <span class="chapter-number">Ch 1</span>Title
                    │     │   </a>
                    │     └── <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    │
                    └── <ul class="sub-toc">    ← LEVEL 2: Sub-sections (default: hidden)
                          ├── <li><a href="#s1-1">1.1 Title</a></li>
                          ├── <li class="has-children">
                          │     <a href="#s2-3">2.3 Title</a>
                          │     <button class="sub-sub-toggle" onclick="toggleSubSub(this)">▸</button>
                          │     <ul class="sub-sub-toc">    ← LEVEL 3: Sub-sub-sections
                          │       <li><a href="#s2-3a">Detail A</a></li>
                          │       <li><a href="#s2-3b">Detail B</a></li>
                          │     </ul>
                          │   </li>
                          └── <li><a href="#s1-5">1.5 Title</a></li>
                        </ul>
```

### 1.4 Collapse/Expand Pattern

- **All `.chapter-list` elements** start with `display: none`
- **All `.sub-toc` elements** start with `display: none`
- **All `.sub-sub-toc` elements** start with `display: none`
- Clicking `.part-header` → toggles `chapter-list.visible` on the immediate next sibling `<ul>`
- Clicking `.section-toggle-btn` → toggles `.sub-toc.visible` on the nearest `.sub-toc` within the same `.chapter-item`
- Clicking `.sub-sub-toggle` → toggles `.sub-sub-toc.visible` + changes button text ▸↔▾
- Expand All / Collapse All buttons → add/remove `visible` class on ALL `.chapter-list` elements

### 1.5 Body Class Pattern for Sidebar State
- `<body class="toc-open">` — sidebar is visible (starts open by default)
- When sidebar closed: `document.body.classList.toggle('toc-open')` removes the class
- CSS: `body.toc-open .toc-sidebar { transform: translateX(0); }`
- CSS media query (≥1000px): `body.toc-open header, body.toc-open main, body.toc-open footer { margin-left: 340px; }`

---

## 2. CONTENT SECTION PATTERN

### 2.1 Chapter Wrapper Structure

```html
<section class="chapter-section" id="part1">          ← Chapter group (semantic section)
  <h2>
    <span>🟢 Part 1: Foundation</span>                ← Part title
    <span class="chapter-badge">Chapters 1-4</span>    ← Badge pill
  </h2>

  <div id="ch1">                                       ← Individual chapter anchor
    <div class="chapter-intro">                        ← Chapter intro card
      <h3>Chapter 1: Title</h3>
      <p>Description...</p>
      <div class="chapter-meta">
        <span class="meta-tag">🟢 Beginner</span>
        <span class="meta-tag">⏱️ ~1.5 hours</span>
        <span class="meta-tag">📖 Concepts</span>
      </div>
    </div>

    <div class="learning-objectives">                  ← Green-tinted learning goals
      <h4>🎯 What You'll Learn</h4>
      <ul>
        <li>✅ Goal 1</li>
        <li>✅ Goal 2</li>
      </ul>
    </div>

    <div class="section-block" id="s1-1">              ← Individual section (sub-section)
      <h3>1.1 Section Title</h3>
      <p>Content...</p>
      <!-- Various component boxes go here -->
    </div>

    <div class="section-block" id="s1-2">
      <h3>1.2 Another Section</h3>
      ...
    </div>
  </div>
</section>
```

### 2.2 Key Content Component Classes

| Class | Used In | Purpose |
|---|---|---|
| `.chapter-section` | Both | Top-level `<section>` wrapper. `margin: 60px 0`, `border-top: 2px solid #30363d` |
| `.chapter-intro` | Both | Blue-gradient intro card with top accent bar. Contains title, description, meta tags |
| `.chapter-meta` | Both | Flex row of `.meta-tag` pills inside chapter-intro |
| `.meta-tag` | Both | Small pill with icon: "🟢 Beginner", "⏱️ ~1.5 hours" |
| `.learning-objectives` | Both | Green-gradient box with ✅ bullet points. `::before` has green gradient bar |
| `.section-block` | Both | Main content section unit. `margin: 50px 0`, `h3` has gradient bottom border |
| `.content-placeholder` | NVIDIA | Dashed-border placeholder for unwritten content |
| `.info-box` | Both | Callout box with 4 variants: `.note` (blue), `.warning` (yellow), `.tip` (green), `.danger` (red) |
| `.diagram-container` | Both | Dark container for ASCII diagrams. Top accent bar, `overflow-x: auto` |
| `.diagram-box` | Both | Inner dashed-border box within diagram-container |
| `.diagram-title` | Both | Small uppercase centered label inside diagram-container |
| `.card-grid` | Both | Responsive grid: `.cols-2`, `.cols-4` variants |
| `.info-card` | Both | Card with hover effect (top blue line appears). `.highlight` variant for emphasis |
| `.evolution-strip` | Both | Horizontal timeline of `.evo-item` cards |
| `.evo-item` | Both | Timeline card. `.active` variant has blue border + glow |
| `.compare-table` | Both | Styled comparison table with gradient headers, `.winner` class for green text |
| `.scenario-box` | Both | Pain-point box (red-tinted) or `.positive` (green-tinted) |
| `.flow-diagram` | Both | Flex row of `.flow-step` cards connected by `.flow-arrow` |
| `.decision-tree` | Both | Contains `.decision-node` elements: `.question`, `.yes`, `.no` |
| `.code-block-wrapper` | Both | Code block with macOS-style header (red/yellow/green dots) + language label |
| `.code-block-header` | Both | Header bar of code block with `.code-dot.red/.yellow/.green` |
| `.process-steps` | Both | Horizontal numbered steps with rainbow top bar |
| `.process-step-item` | Both | Individual step. `.active` has green number circle. `::after` adds → arrow |
| `.step-number` | Both | Blue numbered circle (36×36px). `.active` variant is green |
| `.visual-summary` | Both | Chapter recap with "📊 VISUAL SUMMARY" header. Contains `.vs-grid` |
| `.vs-grid` | Both | Responsive grid of `.vs-item` cards |
| `.vs-item` | Both | Small icon + label + detail card |
| `.arch-layers` | Both | Stacked layers visualization. Contains `.arch-layer` items |
| `.arch-layer` | Both | A single layer row. Variants: `.layer-app` (green), `.layer-k8s` (blue), `.layer-infra` (purple), `.layer-hw` (yellow), `.layer-cuda` (blue), `.layer-gpu` (light blue), `.layer-inference` (orange), `.layer-framework` (pink), `.layer-hardware` (purple) |
| `.arch-foundation` | NVIDIA | Special thicker bottom layer variant |
| `.split-panel` | Both | 2-column grid: `.split-bad` (red left) vs `.split-good` (green right) |
| `.metric-row` | Both | Responsive grid of `.metric-card` elements |
| `.metric-card` | Both | Stat card with large number. Variants: `.metric-blue`, `.metric-green`, `.metric-purple`, `.metric-orange`, `.metric-red` |
| `.timeline-vertical` | Both | Left-bordered timeline with `.timeline-item` nodes. Variants: `.tl-active` (green dot), `.tl-warning` (yellow), `.tl-danger` (red) |
| `.stat-bar-group` | Both | Group of `.stat-bar-item` rows |
| `.stat-bar-item` | Both | Row: label + bar track + fill |
| `.stat-bar-fill` | Both | Colored fill bar. Variants: `.green`, `.blue`, `.purple`, `.orange`, `.red` |
| `.summary-box` | Both | Blue-gradient chapter summary with icon-grid |
| `.anatomy-card` | CKA | Labeled breakdown card with `.anatomy-header` + `.anatomy-body` + `.anatomy-row` |
| `.relationship-map` | CKA | Hub-and-spoke concept map: `.rel-center` → `.rel-hub` + `.rel-spokes` |
| `.obj-relationship` | CKA | K8s object tree diagram with `.obj-tree` → `.obj-level` → `.obj-node` |
| `.ba-comparison` | CKA | Before/After split: `.ba-grid` → `.ba-side.ba-before` / `.ba-side.ba-after` |
| `.case-study-grid` | Both | Grid of `.case-card` elements |
| `.eco-card` / `.ecosystem-grid` | Both | Ecosystem orbit cards. `.center-card` variant |
| `.intro-callout` | Both | Blue-gradient intro paragraph at the top of the main page |
| `.toc-section` | Both | Main-page TOC grid section with `.toc-grid` → `.toc-card` |
| `.appendix-grid` | Both | Grid of `.appendix-card` elements |
| `.prereq-box` / `.prereq-grid` | CKA | Exam prerequisite/checklist grid with icon+text items |
| `.highlight-box` | CKA | Blue left-border callout box |
| `.callout-enhanced` | CKA | Enhanced callout: `.tip` (green), `.warning` (yellow), `.danger` (red), `.note` (blue) |

---

## 3. EXAM QUESTIONS PATTERN

### 3.1 CKA Exam Question Pattern (cka.html)

**Key container:** `.cka-exam-questions`

```html
<div class="cka-exam-questions">
  <h4>📝 CKA Practice Questions — Chapter X</h4>
  
  <div class="exam-question-item">
    <span class="eq-number">Q1</span>
    <p class="eq-question">Question text with <code>code</code> references...</p>
    <details>
      <summary>Click to reveal answer</summary>
      <div class="eq-answer">
        <div class="eq-answer-label">✅ ANSWER</div>
        <p>Answer text...</p>
        <pre><code>command example</code></pre>
      </div>
      <div class="eq-explanation">
        <div class="eq-exp-label">💡 EXPLANATION</div>
        <p>Explanation text with <code>code</code>...</p>
      </div>
    </details>
  </div>
  <!-- More .exam-question-item blocks... -->
</div>
```

**CKA colors:**
- `.eka-exam-questions` — indigo/purple accent (#6366f1, #8b5cf6)
- `.eq-number` — indigo→purple gradient badge
- `.eq-answer` — green left border (#22c55e)
- `.eq-explanation` — orange left border (#f97316)
- `summary` — indigo accent with ▶/▼ toggle
- `summary:hover` — lighter indigo

### 3.2 NVIDIA Exam Question Pattern (NVIDIA_ast.html)

**Key container:** `.nvidia-exam-questions`

```html
<div class="nvidia-exam-questions">
  <h4>📝 NVIDIA Certification Practice Questions — Chapter X</h4>
  
  <div class="exam-question-item">
    <span class="eq-number">Q1</span>
    <p class="eq-question">Question text...</p>
    <details>
      <summary>Click to reveal answer</summary>
      <div class="eq-answer">
        <div class="eq-answer-label">✅ ANSWER</div>
        <p>Answer text...</p>
      </div>
      <div class="eq-explanation">
        <div class="eq-exp-label">💡 EXPLANATION</div>
        <pre>ASCII diagram or detailed explanation</pre>
        <p>Explanation text...</p>
      </div>
    </details>
  </div>
</div>
```

**NVIDIA colors:**
- `.nvidia-exam-questions` — green accent (#76b900 / #326ce5)
- `.eq-number` — blue gradient (#326ce5 → #2563eb)
- `.eq-answer` — green left border (#22c55e)
- `.eq-explanation` — orange left border (#f97316)
- `summary` — green tint with ▶/▼ toggle
- `summary:hover` — shifts to blue

### 3.3 CKA Practice Drill Pattern (CKA-specific)

**Key container:** `.cka-practice-drill`

More elaborate than exam questions — includes timer, scenario, hints, and foldable solution:
```html
<div class="cka-practice-drill">
  <span class="drill-timer">⏱️ 5 min</span>
  <div class="drill-scenario">
    <h5>Scenario</h5>
    <p>Description...</p>
    <ol><li>Task 1</li><li>Task 2</li></ol>
  </div>
  <div class="drill-hint">💡 Hint: ...</div>
  <details class="drill-solution">
    <summary>Click to reveal solution</summary>
    <pre><code>solution commands</code></pre>
  </details>
</div>
```

### 3.4 Key Differences Between CKA and NVIDIA Exam Question Patterns

| Aspect | CKA (cka-exam-questions) | NVIDIA (nvidia-exam-questions) |
|---|---|---|
| Accent color | Indigo/purple (#6366f1) | Green/blue (#76b900/#326ce5) |
| Container `::before` | "📝 CKA PRACTICE QUESTIONS — EXAM SIMULATION" | "📝 NVIDIA PRACTICE QUESTIONS — EXAM SIMULATION" |
| eq-number gradient | #6366f1 → #8b5cf6 (purple) | #326ce5 → #2563eb (blue) |
| Summary color | #818cf8 (indigo) | #93c5fd (blue) |
| Summary hover | #a5b4fc | #326ce5 |
| Answer code color | #a5b4fc | #93c5fd |
| Explanation code color | #fbbf24 | #fbbf24 |
| Practice Drills | ✅ Has `.cka-practice-drill` | ❌ No equivalent |
| Explanations use ASCII art | Less common | Very common (ASCII diagrams in explanations) |
| CKS question variant | ✅ `.cks-exam-questions` (red accent) | ❌ No equivalent |

### 3.5 CKS Exam Questions (cka.html only)

```html
<div class="cks-exam-questions">
  <!-- Same .exam-question-item structure as CKA -->
  <!-- BUT: red accent (#dc2626), eq-number gradient: #dc2626 → #f97316 -->
</div>
```

Also has `.cks-security-section` for CKS content blocks (red-tinted container).

---

## 4. COMPLETE CSS COMPONENT CLASS REFERENCE

### 4.1 Exam/Certification Callout Classes

| Class | File | Purpose | Color | Icon |
|---|---|---|---|---|
| `.cka-exam-tip` | CKA | Exam strategy tips | Purple (#8b5cf6) | 🎓 CKA EXAM TIP |
| `.cka-speed-tip` | CKA | Time-saving imperative commands | Orange (#f59e0b) | ⚡ SPEED TIP |
| `.cka-gotcha` | CKA | Common exam mistakes/warnings | Red (#ef4444) | ⚠️ EXAM GOTCHA |
| `.cka-verify` | CKA | Post-task verification checklist | Green (#22c55e) | ✅ VERIFY YOUR ANSWER |
| `.cka-practice-drill` | CKA | Hands-on timed exercises | Green (#10b981) | 🏋️ CKA PRACTICE DRILL |
| `.cka-exam-questions` | CKA | End-of-chapter exam simulation Q&A | Indigo (#6366f1) | 📝 CKA PRACTICE QUESTIONS |
| `.cks-exam-questions` | CKA | CKS security exam simulation Q&A | Red (#dc2626) | 🔐 CKS PRACTICE QUESTIONS |
| `.cks-security-section` | CKA | CKS security content blocks | Red (#dc2626) | 🛡️ CKS — SECURITY SPECIALIST |
| `.cka-chapter-relevance` | CKA | Domain weight indicator per chapter | Purple (#8b5cf6) | 🎓 CKA Relevance |
| `.cka-weight-bar` | CKA | Domain weight progress bar | Purple gradient | N/A |
| `.cka-imperative-ref` | CKA | Imperative command cheat sheet | Cyan (#00d2ff) | ⚡ IMPERATIVE COMMANDS |
| `.cka-yaml-skeleton` | CKA | YAML template to memorize | Orange (#f0883e) | 📋 EXAM YAML SKELETON |
| `.cka-kubectl-path` | CKA | kubectl explain path reference | Indigo (#818cf8) | 🔍 KUBECTL EXPLAIN |
| `.nvidia-exam-tip` | NVIDIA | Exam strategy tips | Green (#76b900) | 🎓 NVIDIA EXAM TIP |
| `.nvidia-speed-tip` | NVIDIA | Time-saving tips | Orange (#f59e0b) | ⚡ SPEED TIP |
| `.nvidia-gotcha` | NVIDIA | Common exam mistakes | Red (#ef4444) | ⚠️ EXAM GOTCHA |
| `.nvidia-verify` | NVIDIA | Verification checklist | Green (#22c55e) | ✅ VERIFY YOUR ANSWER |
| `.nvidia-exam-questions` | NVIDIA | End-of-chapter exam simulation Q&A | Green/Blue | 📝 NVIDIA PRACTICE QUESTIONS |

### 4.2 Exam Question Item Internal Classes (shared by CKA, CKS, NVIDIA)

| Class | Purpose |
|---|---|
| `.exam-question-item` | Individual question card |
| `.eq-number` | Question number badge (Q1, Q2...) |
| `.eq-question` | Question text paragraph |
| `.eq-answer` | Answer reveal box (green left border) |
| `.eq-answer-label` | "✅ ANSWER" label |
| `.eq-explanation` | Explanation box (orange left border) |
| `.eq-exp-label` | "💡 EXPLANATION" label |

### 4.3 Content Block Classes (shared across both files)

| Class | Purpose |
|---|---|
| `.section-block` | Main content section unit with gradient-bottom-border h3 |
| `.chapter-section` | Chapter-level wrapper with top border separator |
| `.chapter-intro` | Chapter introduction card with gradient background |
| `.chapter-meta` / `.meta-tag` | Chapter metadata pills |
| `.learning-objectives` | Green learning goals box |
| `.chapter-badge` | Chapter number pill in section h2 |
| `.content-placeholder` | Dashed placeholder for unwritten content |
| `.intro-callout` | Main page intro paragraph |

### 4.4 Callout/Info Box Classes

| Class | Purpose | Color |
|---|---|---|
| `.info-box.note` | General note/info | Blue (#326ce5) |
| `.info-box.warning` | Warning callout | Yellow (#eab308) |
| `.info-box.tip` | Pro tip | Green (#22c55e) |
| `.info-box.danger` | Danger/warning | Red (#ef4444) |
| `.callout-enhanced.tip` | Enhanced tip | Green |
| `.callout-enhanced.warning` | Enhanced warning | Yellow |
| `.callout-enhanced.danger` | Enhanced danger | Red |
| `.callout-enhanced.note` | Enhanced note | Blue |
| `.highlight-box` | Blue left-border highlight | Blue |
| `.summary-box` | Blue-gradient summary | Blue |

### 4.5 Diagram/Visual Classes

| Class | Purpose |
|---|---|
| `.diagram-container` | Dark themed container for ASCII diagrams |
| `.diagram-box` | Inner dashed-border box for ASCII art |
| `.diagram-title` | Centered uppercase label |
| `.arch-layers` | Stacked architecture layers container |
| `.arch-layer` | Single architecture layer row |
| `.arch-layer.layer-app` | Application layer (green left border) |
| `.arch-layer.layer-k8s` | Kubernetes/orchestration layer (blue) |
| `.arch-layer.layer-infra` | Infrastructure layer (purple) |
| `.arch-layer.layer-hw` | Hardware layer (yellow) |
| `.arch-layer.layer-cuda` | CUDA layer (blue) |
| `.arch-layer.layer-gpu` | GPU layer (light blue) |
| `.arch-layer.layer-inference` | Inference layer (orange) |
| `.arch-layer.layer-framework` | Framework layer (pink) |
| `.arch-layer.layer-hardware` | Hardware layer (purple) |
| `.arch-foundation` | Foundation/base layer (thicker) |

### 4.6 Card/Grid Classes

| Class | Purpose |
|---|---|
| `.card-grid` | Responsive card grid (auto-fit, minmax 240px) |
| `.card-grid.cols-2` | 2-column variant (minmax 320px) |
| `.card-grid.cols-4` | 4-column variant (minmax 200px) |
| `.info-card` | Standard info card with hover effect |
| `.info-card.highlight` | Highlighted/emphasized card |
| `.toc-grid` | Main-page TOC grid |
| `.toc-card` | Main-page TOC card with hover lift |
| `.appendix-grid` | Appendix card grid |
| `.appendix-card` | Appendix card |
| `.case-study-grid` | Company case study card grid |
| `.case-card` | Individual case study card |
| `.ecosystem-grid` | Ecosystem orbit grid |
| `.eco-card` | Ecosystem card. `.center-card` variant |
| `.metric-row` | Metric cards row |
| `.metric-card` | Stat metric card |
| `.metric-card.metric-blue` | Blue metric value |
| `.metric-card.metric-green` | Green metric value |
| `.metric-card.metric-purple` | Purple metric value |
| `.metric-card.metric-orange` | Orange metric value |
| `.metric-card.metric-red` | Red metric value |

### 4.7 Timeline/Evolution Classes

| Class | Purpose |
|---|---|
| `.evolution-strip` | Horizontal evolution timeline grid |
| `.evo-item` | Timeline card. `.active` variant |
| `.timeline-vertical` | Vertical timeline with left border |
| `.timeline-item` | Timeline node. `.tl-active`, `.tl-warning`, `.tl-danger` |
| `.tl-tag.tag-create` | Green tag on timeline |
| `.tl-tag.tag-update` | Blue tag on timeline |
| `.tl-tag.tag-delete` | Red tag on timeline |

### 4.8 Comparison/Split Classes

| Class | Purpose |
|---|---|
| `.split-panel` | 2-column side-by-side comparison |
| `.split-side.split-bad` | Red-tinted left side (before/wrong) |
| `.split-side.split-good` | Green-tinted right side (after/correct) |
| `.compare-table` | Styled comparison table |
| `.compare-table .winner` | Green-bold winning cell |
| `.scenario-box` | Red-tinted pain-point scenario |
| `.scenario-box.positive` | Green-tinted positive scenario |
| `.ba-comparison` | Before/After comparison wrapper |
| `.ba-grid` | Before/After 2-column grid |
| `.ba-side.ba-before` | Red "before" column |
| `.ba-side.ba-after` | Green "after" column |
| `.flow-diagram` | Horizontal flow/pipeline diagram |
| `.flow-step` | Individual flow step card |
| `.flow-arrow` | Arrow connector between steps |
| `.decision-tree` | Decision tree container |
| `.decision-node.question` | Blue question node |
| `.decision-node.yes` | Green yes/true path |
| `.decision-node.no` | Red no/false path |

### 4.9 Process/Step Classes

| Class | Purpose |
|---|---|
| `.process-steps` | Horizontal numbered process flow |
| `.process-step-item` | Individual step. `.active` variant |
| `.step-number` | Numbered circle (36px) |

### 4.10 Visual Summary Classes

| Class | Purpose |
|---|---|
| `.visual-summary` | Chapter recap container with "📊 VISUAL SUMMARY" header |
| `.vs-grid` | Grid of summary items |
| `.vs-item` | Individual summary item (icon + label + detail) |

### 4.11 Code Block Classes

| Class | Purpose |
|---|---|
| `.code-block-wrapper` | Full code block with header |
| `.code-block-header` | macOS-style header bar |
| `.code-dot.red` | Red window dot |
| `.code-dot.yellow` | Yellow window dot |
| `.code-dot.green` | Green window dot |
| `.code-lang` | Language label in header |

### 4.12 Relationship/Architecture Diagram Classes (CKA-specific)

| Class | Purpose |
|---|---|
| `.obj-relationship` | K8s object relationship diagram container |
| `.obj-tree` | Flex column tree layout |
| `.obj-level` | Horizontal row of nodes at same depth |
| `.obj-node` | Individual object node |
| `.obj-node.obj-primary` | Blue-bordered primary node |
| `.obj-node.obj-green` | Green-bordered node |
| `.obj-node.obj-purple` | Purple-bordered node |
| `.obj-node.obj-orange` | Orange-bordered node |
| `.obj-node.obj-pink` | Pink-bordered node |
| `.obj-connector-down` | Vertical connector between levels |
| `.relationship-map` | Hub-and-spoke concept relationship map |
| `.rel-center` | Center hub container |
| `.rel-hub` | Center circle hub |
| `.rel-spokes` | Grid of spoke items |
| `.rel-spoke` | Individual spoke node |
| `.anatomy-card` | Component breakdown card |
| `.anatomy-header` | Header of anatomy card |
| `.anatomy-body` | Body of anatomy card |
| `.anatomy-row` | Row: label + value |
| `.anatomy-label` | Label column with icon |
| `.anatomy-value` | Value column with code |

### 4.13 Stat/Progress Bar Classes

| Class | Purpose |
|---|---|
| `.stat-bar-group` | Group of stat bars |
| `.stat-bar-item` | Individual bar row |
| `.stat-bar-label` | Bar label text |
| `.stat-bar` | Bar track background |
| `.stat-bar-fill` | Colored fill. `.green`, `.blue`, `.purple`, `.orange`, `.red` |
| `.cka-weight-bar` | CKA domain weight bar |
| `.cka-weight-bar .weight-fill` | Purple gradient fill |

### 4.14 Header/Tag/Badge Classes

| Class | Purpose |
|---|---|
| `.tag` | Header tag pill |
| `.tag.beginner` | Green beginner tag |
| `.tag.nvidia-blue` | NVIDIA-specific green-tinted tag |
| `.badge` | Inline badge/pill |
| `.badge-part` | Blue part badge |
| `.badge-beginner` | Green beginner badge |
| `.badge-intermediate` | Yellow intermediate badge |
| `.badge-advanced` | Red advanced badge |
| `.badge-exam` | Purple pulsing exam badge |
| `.badge-security` | Red security badge |
| `.badge-observe` | Cyan observability badge |
| `.badge-appendix` | Purple appendix badge |
| `.badge-reference` | Blue reference badge |
| `.badge-concept` | Cyan concept badge |
| `.badge-command` | Emerald command badge |
| `.part-badge` | Sidebar part level badge |
| `.part-badge.beginner` | Green (🟢) |
| `.part-badge.intermediate` | Yellow (🟡) |
| `.part-badge.advanced` | Red (🔴) |
| `.card-part-badge` | TOC card badge |
| `.chapter-tag` | TOC card chapter pill |
| `.header-tags` | Flex wrapper for header tags |

### 4.15 Master Summary / Hero Classes (CKA-specific)

| Class | Purpose |
|---|---|
| `.master-summary` | Master summary container |
| `.summary-hero` | Hero banner with animated gradient border |
| `.summary-stats-bar` | Stats grid at top |
| `.summary-stat-card` | Individual stat card |
| `.summary-stat-card .stat-number.blue/.green/.purple/.orange/.pink/.yellow` | Colored stat numbers |
| `.journey-section` | Learning journey section |
| `.roadmap-track` | Vertical roadmap with colored left-border gradient |
| `.ps-project` | Project showcase card |
| `.ps-header` | Project showcase header |
| `.ps-logo` | Project logo square |
| `.ps-body` | Project showcase body |
| `.ps-stack` | Tech stack tag row |
| `.ps-components` | Component grid |
| `.prereq-box` | Exam prerequisite box |
| `.prereq-grid` | Grid inside prereq box |
| `.prereq-item` | Individual prereq item |

### 4.16 Footer Classes

| Class | Purpose |
|---|---|
| `footer` | Full-width footer with gradient bg |
| `.footer-content` | 3-column grid footer |
| `.footer-section` | Individual footer column |
| `.footer-bottom` | Bottom copyright bar |
| `.project-info` | Project attribution text |
| `.nvidia-icon` | NVIDIA icon in footer |

---

## 5. SIDEBAR JAVASCRIPT

### 5.1 Complete JS Code (identical in both files, with minor var naming differences)

```javascript
// Toggle sidebar open/close via body class
document.getElementById('tocToggle').addEventListener('click', function() {
    document.body.classList.toggle('toc-open');
    const isOpen = document.body.classList.contains('toc-open');
    this.setAttribute('aria-expanded', isOpen);
});

// Toggle individual part expansion (chapter-list visibility)
function togglePart(header) {
    const chapterList = header.nextElementSibling;
    chapterList.classList.toggle('visible');
}

// Toggle 3rd-level sub-sections
function toggleSubSub(btn) {
    const subSubToc = btn.parentElement.querySelector('.sub-sub-toc');
    if (subSubToc) {
        subSubToc.classList.toggle('visible');
        btn.textContent = subSubToc.classList.contains('visible') ? '▾' : '▸';
    }
}

// Toggle 2nd-level sub-sections (within a chapter)
function toggleSections(btn) {
    const subToc = btn.closest('.chapter-item').querySelector('.sub-toc');
    if (subToc) {
        subToc.classList.toggle('visible');
        btn.textContent = subToc.classList.contains('visible') ? '▼' : '▶';
    }
}

// Expand all parts (show all chapter-lists)
function expandAllParts() {
    document.querySelectorAll('.chapter-list').forEach(list => list.classList.add('visible'));
}

// Collapse all parts (hide all chapter-lists)
function collapseAllParts() {
    document.querySelectorAll('.chapter-list').forEach(list => list.classList.remove('visible'));
}

// Scroll spy: highlight active chapter-link based on scroll position
function highlightActiveSection() {
    const sections = document.querySelectorAll('.chapter-section');
    const navLinks = document.querySelectorAll('.chapter-link');
    let current = '';
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= 150) { current = section.id; }
    });
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === '#' + current) { link.classList.add('active'); }
    });
}
window.addEventListener('scroll', highlightActiveSection);

// Mobile: auto-close sidebar when clicking a chapter link
document.querySelectorAll('.chapter-link').forEach(link => {
    link.addEventListener('click', function() {
        if (window.innerWidth < 1000) { document.body.classList.remove('toc-open'); }
    });
});

// Smooth scroll for TOC cards and appendix cards
document.querySelectorAll('.toc-card a, .appendix-card a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const target = document.querySelector(targetId);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
```

### 5.2 JS Behavior Summary

| Function | Trigger | Action |
|---|---|---|
| Toggle button click | User clicks ☰ Contents | Toggles `body.toc-open` class → sidebar slides in/out. On desktop (≥1000px), main content margin adjusts |
| `togglePart(header)` | User clicks `.part-header` | Toggles `.visible` on next `<ul class="chapter-list">` |
| `toggleSections(btn)` | User clicks `▶` button | Toggles `.visible` on nearest `.sub-toc`, changes button text ▶↔▼ |
| `toggleSubSub(btn)` | User clicks `▸` button | Toggles `.visible` on `.sub-sub-toc`, changes button text ▸↔▾ |
| `expandAllParts()` | User clicks ⊞ button | Adds `.visible` to ALL `.chapter-list` elements |
| `collapseAllParts()` | User clicks ⊟ button | Removes `.visible` from ALL `.chapter-list` elements |
| `highlightActiveSection()` | `window scroll` event | Adds `.active` to the `.chapter-link` whose target `.chapter-section` is in view (top ≤ 150px) |
| Chapter link click (mobile) | User clicks any `.chapter-link` on <1000px screen | Removes `body.toc-open` (closes sidebar) |
| TOC/appendix card click | User clicks TOC card or appendix card link | Smooth scrolls to target anchor |

---

## 6. HTML STRUCTURE PATTERNS (HEADER / FOOTER / BODY LAYOUT)

### 6.1 Document Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Title</title>
    <!-- Prism.js CSS preload -->
    <link rel="preload" href="prism-tomorrow.min.css" as="style" onload="...">
    <noscript><link rel="stylesheet" href="prism-tomorrow.min.css"></noscript>
    <style>
        /* ALL CSS IS INLINE in <style> tag — no external stylesheets */
        /* Sections marked with ═══ comment banners */
    </style>
</head>
<body class="toc-open">
    <!-- 1. Toggle Button -->
    <!-- 2. Sidebar Navigation -->
    <!-- 3. Header -->
    <!-- 4. Main Content -->
    <!-- 5. Footer -->
    <!-- 6. JavaScript (<script> at end of body) -->
</body>
</html>
```

### 6.2 Header Pattern

```html
<header>
    <h1>☸️ Page Title with Gradient Text</h1>              <!-- h1 has gradient -webkit-background-clip text -->
    <p class="subtitle">Subtitle with <strong>emphasis</strong></p>
    <p class="description">Longer description text...</p>
    <div class="header-tags">
        <span class="tag beginner">🟢 Beginner Friendly</span>
        <span class="tag">☸️ Topic Tag</span>
        <span class="tag">📚 Chapter Count</span>
        <!-- More .tag elements -->
    </div>
</header>
```

**Header CSS:** `background: linear-gradient(135deg, #1e3a5f, #0f2744, #0a1929)`, `border-bottom: 3px solid #326ce5`, `::before` pseudo-element with large watermark character (☸ for CKA, 🔺 for NVIDIA) at 0.03 opacity.

### 6.3 Main Content Shell

```html
<main>
    <!-- Optional: Intro Callout -->
    <div class="intro-callout">
        <p>Welcome text with <strong>highlighted</strong> terms.</p>
    </div>

    <!-- Optional: On main page — TOC Grid Sections -->
    <div class="toc-section">
        <h2>Section Title</h2>
        <div class="toc-grid">
            <div class="toc-card">
                <a href="#anchor">
                    <div class="card-header">
                        <span class="card-part-badge beginner">BEGINNER</span>
                        <span class="card-icon">📚</span>
                    </div>
                    <h3>Card Title</h3>
                    <p class="card-subtitle">Subtitle</p>
                    <p>Description...</p>
                    <div class="card-chapters">
                        <span class="chapter-tag">Ch 1</span>
                        <span class="chapter-tag">Ch 2</span>
                    </div>
                </a>
            </div>
            <!-- More .toc-card elements -->
        </div>
    </div>

    <!-- Content Chapters -->
    <section class="chapter-section" id="part1">
        <h2><span>🟢 Part Title</span><span class="chapter-badge">Ch X-Y</span></h2>
        
        <div id="ch1">
            <div class="chapter-intro">...</div>
            <div class="learning-objectives">...</div>
            <div class="section-block" id="s1-1">...</div>
            <div class="section-block" id="s1-2">...</div>
        </div>
    </section>
</main>
```

### 6.4 Footer Pattern

```html
<footer>
    <div class="footer-content">
        <div class="footer-section">
            <h3>Column 1 Title</h3>
            <p>Description text...</p>
        </div>
        <div class="footer-section">
            <h3>Column 2 Title</h3>
            <ul>
                <li><a href="#link">Link</a></li>
            </ul>
        </div>
        <div class="footer-section">
            <h3>Column 3 Title</h3>
            <p>More content...</p>
        </div>
    </div>
    <div class="footer-bottom">
        <p>© 2026 Copyright</p>
        <p class="project-info">Built with 💙 using anihpj/jobpost Django Project | June 2026</p>
        <!-- NVIDIA variant adds: <span class="nvidia-icon">🔺</span> -->
    </div>
</footer>
```

---

## 7. COLOR PALETTE REFERENCE

### 7.1 Shared Dark Theme (both files)
| Token | Hex | Usage |
|---|---|---|
| Page bg | `#0d1117` | Body/main/background |
| Card bg | `#161b22` | Cards, sidebar |
| Card bg alt | `#111827` | Gradient cards |
| Border | `#30363d` | Default borders |
| Border accent | `#1e3a5f` | Blue borders, diagram borders |
| Text primary | `#e4e4e7` | Main text |
| Text secondary | `#c9d1d9` | Body text |
| Text muted | `#a1a1aa` / `#8b949e` | Muted/secondary text |
| Text dim | `#6b7280` | Very dim text |
| Header gradient | `#1e3a5f → #0f2744 → #0a1929` | Header background |
| Footer gradient | `#0f2744 → #0a1929` | Footer background |

### 7.2 Accent Colors
| Color | Hex | CKA usage | NVIDIA usage |
|---|---|---|---|
| Primary blue | `#326ce5` | ✓ | ✓ (shared) |
| Light blue | `#60a5fa` / `#93c5fd` | ✓ (h1, links, headings) | ✓ (headings) |
| Green | `#22c55e` / `#4ade80` | ✓ (tips, success) | ✓ (tips, success) |
| Yellow | `#eab308` / `#facc15` | ✓ (warnings) | ✓ (warnings) |
| Red | `#ef4444` / `#f87171` | ✓ (danger, gotchas) | ✓ (danger, gotchas) |
| Purple | `#8b5cf6` / `#a78bfa` | ✓ (CKA exam tips) | ✓ (minor) |
| Orange | `#f59e0b` / `#fb923c` | ✓ (speed tips) | ✓ (speed tips) |
| Indigo | `#6366f1` / `#818cf8` | ✓ (CKA questions, kubectl) | — |
| Cyan | `#00d2ff` | ✓ (imperative ref) | — |
| NVIDIA green | `#76b900` | — | ✓ (tags, badges, borders) |

---

## 8. KEY PATTERN DIFFERENCES BETWEEN FILES

| Pattern | cka.html | NVIDIA_ast.html |
|---|---|---|
| Sidebar width | 340px | 340px (identical) |
| Sidebar title | "☸️ CKA Study Guide" | "🔺 NVIDIA Study Guide" |
| Header watermark | ☸ | 🔺 |
| h1 gradient | `#60a5fa → #93c5fd → #60a5fa` | `#326ce5 → #93c5fd → #326ce5` |
| Exam tip prefix | `cka-*` (.cka-exam-tip, .cka-gotcha, .cka-verify, etc.) | `nvidia-*` (.nvidia-exam-tip, .nvidia-gotcha, .nvidia-verify, etc.) |
| Practice drills | ✅ `.cka-practice-drill` with timer/scenario/hint/solution | ❌ None |
| Imperative command ref | ✅ `.cka-imperative-ref` (cyan) | ❌ None |
| YAML skeleton | ✅ `.cka-yaml-skeleton` (orange) | ❌ None |
| kubectl explain path | ✅ `.cka-kubectl-path` (indigo) | ❌ None |
| CKS content | ✅ `.cks-security-section`, `.cks-exam-questions` | ❌ None |
| Domain weight bars | ✅ `.cka-weight-bar` | ❌ None |
| Master summary hero | ✅ `.summary-hero` with animated gradient | ❌ None (simpler structure) |
| Learning journey roadmap | ✅ `.roadmap-track` with colored vertical line | ❌ None |
| Object relationship diagram | ✅ `.obj-relationship` tree structure | ❌ None |
| Before/After comparison | ✅ `.ba-comparison` split panel | Uses `.split-panel` instead |
| Evolution strip | ✅ `.evolution-strip` | ✅ `.evolution-strip` (shared) |
| Process steps | ✅ `.process-steps` | ✅ `.process-steps` (shared) |
| Visual summary | ✅ `.visual-summary` | ✅ `.visual-summary` (shared) |
| Architecture layers | ✅ `.arch-layers` (simpler) | ✅ `.arch-layers` (more layer variants) |
| 3rd-level sidebar nesting | ✅ `.sub-sub-toc` | ✅ `.sub-sub-toc` (more usage) |
| Chapter count | 40 chapters + 9 appendices | ~17 chapters + front matter |
| Exam question accent | Indigo/purple (#6366f1) | Blue (#326ce5) |
| Explanations with ASCII art | Less common | Very common |
| Content placeholder | ❌ | ✅ `.content-placeholder` |
| Project showcase | ✅ `.ps-project` (anihpj Django) | ❌ |
