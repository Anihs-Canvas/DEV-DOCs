#!/usr/bin/env python3
"""Rebuild the sidebar HTML in cilium-test-prep.html to match CKA.html style."""

import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_header_start = '<!-- ═══════════════════════════════ HEADER ═══════════════════════════════ -->'
old_sidebar_end = '</nav>\n\n<!-- ═══════════════════════════════ MAIN CONTENT ═══════════════════════════════ -->'

idx_start = content.find(old_header_start)
idx_end = content.find(old_sidebar_end)

if idx_start == -1 or idx_end == -1:
    print('ERROR: Could not find markers')
    print('idx_start:', idx_start)
    print('idx_end:', idx_end)
    exit(1)

new_html = r'''<!-- ═══════════════ TOGGLE BUTTON ═══════════════ -->
<button id="tocToggle" class="toc-toggle" aria-controls="tocSidebar" aria-expanded="false" title="Toggle table of contents">
    ☰ Contents
</button>

<!-- ═══════════════ SIDEBAR NAVIGATION ═══════════════ -->
<nav id="tocSidebar" class="toc-sidebar" aria-label="Table of contents">
    <div class="sidebar-header">
        <h2>🐝 CCA Study Guide</h2>
        <div class="sidebar-controls">
            <button class="expand-collapse-btn" onclick="expandAllParts()" title="Expand All">⊞</button>
            <button class="expand-collapse-btn" onclick="collapseAllParts()" title="Collapse All">⊟</button>
        </div>
    </div>

    <ul class="toc-list">
        <!-- PRE-CHAPTER: OVERVIEW -->
        <li>
            <div class="part-header" onclick="togglePart(this)">
                <div class="part-title">
                    <span>🗺️ Guide Overview</span>
                    <span class="part-badge">START HERE</span>
                </div>
            </div>
            <ul class="chapter-list">
                <li class="chapter-item">
                    <a href="#master-summary" class="chapter-link"><span class="chapter-number">🏠</span>Master Summary</a>
                </li>
                <li class="chapter-item">
                    <a href="#exam-overview" class="chapter-link"><span class="chapter-number">📊</span>Exam Overview &amp; Strategy</a>
                </li>
            </ul>
        </li>

        <!-- PART 1: 200 MCQs -->
        <li>
            <div class="part-header" onclick="togglePart(this)">
                <div class="part-title">
                    <span>📝 Part 1: 200 MCQs</span>
                    <span class="part-badge beginner">Q1–Q200</span>
                </div>
            </div>
            <ul class="chapter-list">
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat1" class="chapter-link"><span class="chapter-number">1</span>Architecture (20%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat1-1">1.1 K8s Networking (Q1–Q10)</a></li>
                        <li><a href="#cat1-2">1.2 Cilium Components (Q11–Q20)</a></li>
                        <li><a href="#cat1-3">1.3 Identity &amp; Endpoints (Q21–Q30)</a></li>
                        <li><a href="#cat1-4">1.4 Encryption &amp; Security (Q31–Q40)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat2" class="chapter-link"><span class="chapter-number">2</span>Network Policy (18%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat2-1">2.1 K8s NetworkPolicy (Q41–Q48)</a></li>
                        <li><a href="#cat2-2">2.2 CNP &amp; CCNP (Q49–Q58)</a></li>
                        <li><a href="#cat2-3">2.3 L7 Policies (Q59–Q68)</a></li>
                        <li><a href="#cat2-4">2.4 Policy Debugging (Q69–Q76)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat3" class="chapter-link"><span class="chapter-number">3</span>Service Mesh (16%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat3-1">3.1 KPR &amp; Maglev (Q77–Q86)</a></li>
                        <li><a href="#cat3-2">3.2 Ingress &amp; Gateway (Q87–Q96)</a></li>
                        <li><a href="#cat3-3">3.3 Bandwidth &amp; BBR (Q97–Q102)</a></li>
                        <li><a href="#cat3-4">3.4 Sidecar-free Mesh (Q103–Q108)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat4" class="chapter-link"><span class="chapter-number">4</span>Observability (10%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat4-1">4.1 Hubble CLI &amp; Flows (Q109–Q116)</a></li>
                        <li><a href="#cat4-2">4.2 Hubble UI &amp; Map (Q117–Q122)</a></li>
                        <li><a href="#cat4-3">4.3 Metrics &amp; Grafana (Q123–Q128)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat5" class="chapter-link"><span class="chapter-number">5</span>Installation (10%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat5-1">5.1 Methods &amp; Reqs (Q129–Q136)</a></li>
                        <li><a href="#cat5-2">5.2 Helm &amp; Config (Q137–Q142)</a></li>
                        <li><a href="#cat5-3">5.3 Upgrades &amp; Ops (Q143–Q148)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat6" class="chapter-link"><span class="chapter-number">6</span>Cluster Mesh (10%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat6-1">6.1 CM Architecture (Q149–Q156)</a></li>
                        <li><a href="#cat6-2">6.2 CM Configuration (Q157–Q164)</a></li>
                        <li><a href="#cat6-3">6.3 Egress Gateway (Q165–Q168)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat7" class="chapter-link"><span class="chapter-number">7</span>eBPF (10%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat7-1">7.1 eBPF Fundamentals (Q169–Q176)</a></li>
                        <li><a href="#cat7-2">7.2 eBPF in Cilium (Q177–Q184)</a></li>
                        <li><a href="#cat7-3">7.3 BPF Perf &amp; Debug (Q185–Q188)</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#cat8" class="chapter-link"><span class="chapter-number">8</span>BGP &amp; External (6%)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#cat8-1">8.1 BGP in Cilium (Q189–Q194)</a></li>
                        <li><a href="#cat8-2">8.2 L2 Announcements (Q195–Q200)</a></li>
                    </ul>
                </li>
            </ul>
        </li>

        <!-- PART 2: 100 TROUBLESHOOTING -->
        <li>
            <div class="part-header" onclick="togglePart(this)">
                <div class="part-title">
                    <span>🔧 Part 2: 100 Issues</span>
                    <span class="part-badge intermediate">T1–T100</span>
                </div>
            </div>
            <ul class="chapter-list">
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat1" class="chapter-link"><span class="chapter-number">1</span>Architecture (20)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-a1">A1–A5: Pod-to-Pod Failures</a></li>
                        <li><a href="#ts-a2">A6–A10: Service Issues</a></li>
                        <li><a href="#ts-a3">A11–A15: Identity Issues</a></li>
                        <li><a href="#ts-a4">A16–A18: Agent Problems</a></li>
                        <li><a href="#ts-a5">A19–A20: Endpoint Failures</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat2" class="chapter-link"><span class="chapter-number">2</span>Network Policy (18)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-p1">P1–P5: CNP Not Enforcing</a></li>
                        <li><a href="#ts-p2">P6–P10: L7 Policy Issues</a></li>
                        <li><a href="#ts-p3">P11–P13: Audit Mode</a></li>
                        <li><a href="#ts-p4">P14–P16: Host Firewall</a></li>
                        <li><a href="#ts-p5">P17–P18: CIDRGroup</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat3" class="chapter-link"><span class="chapter-number">3</span>Service Mesh (16)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-sm1">SM1–SM5: KPR Problems</a></li>
                        <li><a href="#ts-sm2">SM6–SM10: Ingress Issues</a></li>
                        <li><a href="#ts-sm3">SM11–SM13: Bandwidth Mgr</a></li>
                        <li><a href="#ts-sm4">SM14–SM16: BBR Problems</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat4" class="chapter-link"><span class="chapter-number">4</span>Observability (10)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-o1">O1–O3: No Hubble Flows</a></li>
                        <li><a href="#ts-o2">O4–O6: Relay Problems</a></li>
                        <li><a href="#ts-o3">O7–O8: UI Issues</a></li>
                        <li><a href="#ts-o4">O9–O10: Metrics Issues</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat5" class="chapter-link"><span class="chapter-number">5</span>Installation (10)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-ic1">IC1–IC3: Install Fails</a></li>
                        <li><a href="#ts-ic2">IC4–IC6: CNI Migration</a></li>
                        <li><a href="#ts-ic3">IC7–IC8: Upgrade Fails</a></li>
                        <li><a href="#ts-ic4">IC9–IC10: Helm/Config</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat6" class="chapter-link"><span class="chapter-number">6</span>Cluster Mesh (10)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-cm1">CM1–CM3: Not Connecting</a></li>
                        <li><a href="#ts-cm2">CM4–CM6: Service Discovery</a></li>
                        <li><a href="#ts-cm3">CM7–CM8: Identity Sync</a></li>
                        <li><a href="#ts-cm4">CM9–CM10: Egress GW</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat7" class="chapter-link"><span class="chapter-number">7</span>eBPF (10)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-eb1">EB1–EB3: Prog Load Fail</a></li>
                        <li><a href="#ts-eb2">EB4–EB6: BPF Map Issues</a></li>
                        <li><a href="#ts-eb3">EB7–EB8: Kernel Compat</a></li>
                        <li><a href="#ts-eb4">EB9–EB10: Perf Degradation</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-cat8" class="chapter-link"><span class="chapter-number">8</span>BGP &amp; External (6)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#ts-bg1">BG1–BG3: BGP Peering</a></li>
                        <li><a href="#ts-bg2">BG4–BG5: LB IPAM</a></li>
                        <li><a href="#ts-bg3">BG6: L2 Announcements</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#ts-dt" class="chapter-link"><span class="chapter-number">📊</span>Decision Trees (15)</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#dt1">DT-1: Pod Can&apos;t Reach Pod</a></li>
                        <li><a href="#dt2">DT-2: DNS Not Resolving</a></li>
                        <li><a href="#dt3">DT-3: Policy Blocking Traffic</a></li>
                        <li><a href="#dt4">DT-4: No Hubble Flows</a></li>
                        <li><a href="#dt5">DT-5: Agent Not Starting</a></li>
                        <li><a href="#dt6">DT-6: KPR Not Working</a></li>
                        <li><a href="#dt7">DT-7: CM Not Connecting</a></li>
                        <li><a href="#dt8">DT-8: eBPF Load Fails</a></li>
                        <li><a href="#dt9">DT-9: BGP Peering Down</a></li>
                        <li><a href="#dt10">DT-10: Install Fails</a></li>
                        <li><a href="#dt11">DT-11: L7 Not Enforcing</a></li>
                        <li><a href="#dt12">DT-12: Hubble UI Down</a></li>
                        <li><a href="#dt13">DT-13: Encryption Broken</a></li>
                        <li><a href="#dt14">DT-14: Bandwidth Not Limiting</a></li>
                        <li><a href="#dt15">DT-15: High Latency</a></li>
                    </ul>
                </li>
            </ul>
        </li>

        <!-- PART 3: 100 LAB SCENARIOS -->
        <li>
            <div class="part-header" onclick="togglePart(this)">
                <div class="part-title">
                    <span>🧪 Part 3: 100 Lab Scenarios</span>
                    <span class="part-badge advanced">S1–S100</span>
                </div>
            </div>
            <ul class="chapter-list">
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat1" class="chapter-link"><span class="chapter-number">1</span>Architecture</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s1">S1–S5: Core Networking</a></li>
                        <li><a href="#sc-s6">S6–S10: Identity &amp; Security</a></li>
                        <li><a href="#sc-s11">S11–S15: Encryption &amp; Auth</a></li>
                        <li><a href="#sc-s16">S16–S20: Node &amp; Agent Ops</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat2" class="chapter-link"><span class="chapter-number">2</span>Network Policy</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s21">S21–S26: L3/L4 CNP &amp; DNS</a></li>
                        <li><a href="#sc-s27">S27–S32: CIDR, Host FW &amp; Trace</a></li>
                        <li><a href="#sc-s33">S33–S38: Deny-All, L7 Hardening</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat3" class="chapter-link"><span class="chapter-number">3</span>Service Mesh</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s39">S39–S44: KPR, Maglev &amp; Ingress</a></li>
                        <li><a href="#sc-s45">S45–S49: Retry, BW Mgr &amp; mTLS</a></li>
                        <li><a href="#sc-s50">S50–S54: Envoy, Gateway &amp; Affinity</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat4" class="chapter-link"><span class="chapter-number">4</span>Observability</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s55">S55–S58: Hubble CLI &amp; Flows</a></li>
                        <li><a href="#sc-s59">S59–S60: Hubble UI &amp; Map</a></li>
                        <li><a href="#sc-s61">S61–S64: Metrics &amp; Grafana</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat5" class="chapter-link"><span class="chapter-number">5</span>Installation</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s65">S65–S68: Helm &amp; Config</a></li>
                        <li><a href="#sc-s69">S69–S70: System Requirements</a></li>
                        <li><a href="#sc-s71">S71–S74: Migration &amp; Upgrade</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat6" class="chapter-link"><span class="chapter-number">6</span>Cluster Mesh</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s75">S75–S77: Mesh Setup &amp; Global Svc</a></li>
                        <li><a href="#sc-s78">S78–S80: Cross-Cluster Pod &amp; Policy</a></li>
                        <li><a href="#sc-s81">S81–S84: Egress Gateway &amp; Perf</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat7" class="chapter-link"><span class="chapter-number">7</span>eBPF &amp; Kernel</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s85">S85–S88: Kernel &amp; BPF Basics</a></li>
                        <li><a href="#sc-s89">S89–S94: Datapath Tracing</a></li>
                    </ul>
                </li>
                <li class="chapter-item">
                    <div class="chapter-row">
                        <a href="#sc-cat8" class="chapter-link"><span class="chapter-number">8</span>BGP &amp; External</a>
                        <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>
                    </div>
                    <ul class="sub-toc">
                        <li><a href="#sc-s95">S95–S97: BGP Peering &amp; LB IPAM</a></li>
                        <li><a href="#sc-s98">S98–S100: L2 Announcements &amp; ARP</a></li>
                    </ul>
                </li>
            </ul>
        </li>

        <!-- APPENDICES -->
        <li>
            <div class="part-header" onclick="togglePart(this)">
                <div class="part-title">
                    <span>📎 Appendices</span>
                </div>
            </div>
            <ul class="chapter-list">
                <li class="chapter-item"><a href="#apx-a" class="chapter-link"><span class="chapter-number">A</span>Answer Key (200 Qs)</a></li>
                <li class="chapter-item"><a href="#apx-b" class="chapter-link"><span class="chapter-number">B</span>Top 50 Commands</a></li>
                <li class="chapter-item"><a href="#apx-c" class="chapter-link"><span class="chapter-number">C</span>anihpj File Structure</a></li>
                <li class="chapter-item"><a href="#apx-d" class="chapter-link"><span class="chapter-number">D</span>Dockerfile &amp; Deploy</a></li>
                <li class="chapter-item"><a href="#apx-e" class="chapter-link"><span class="chapter-number">E</span>15 Decision Trees</a></li>
            </ul>
        </li>
    </ul>
</nav>

<!-- ═══════════════════════════════ MAIN CONTENT ═══════════════════════════════ -->'''

content = content[:idx_start] + new_html + content[idx_end + len(old_sidebar_end):]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('HTML sidebar replaced successfully!')
print(f'New file length: {len(content)} chars')
