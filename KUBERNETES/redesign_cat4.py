#!/usr/bin/env python3
"""Redesign Cat4 scenarios (S55-S64) - fix verify h4, fix h4, error-spot indentation"""
import re

with open('cilium-test-prep.html', 'rb') as f:
    c = f.read()

fixes = {
    55: ("Hubble Flows Visible for anihpj",
        'After enabling <code>enable-hubble: "true"</code> in the <code>cilium-config</code> ConfigMap and restarting Cilium agents, the <code>hubble-peer</code> Service registers endpoints from each Cilium agent. Hubble Relay connects to all peers and <strong>aggregates flows from every node</strong>. <code>hubble observe -n anihpj</code> now shows FORWARDED and DROPPED flows with full source/destination pod, verdict, and protocol details.',
        "Enable Hubble in ConfigMap"),
    56: ("anihpj Flows Visible in Hubble",
        'After labeling the namespace with <code>io.cilium/network-policy=true</code> and restarting pods, Cilium creates <strong>CiliumEndpoint CRDs</strong> for all anihpj pods. Hubble now observes and reports all flows in the anihpj namespace. <code>kubectl get cep -n anihpj</code> shows endpoints with valid security identities and IP addresses.',
        "Label Namespace for Cilium Management"),
    57: ("DROPPED Flows Isolated and Identified",
        'Using <code>hubble observe --verdict DROPPED --protocol TCP</code>, only denied connections are displayed. The CNP <code>restrict-db</code> is clearly blocking <strong>api to db:5432</strong> because only <code>tier=web</code> is in the allow list. JSON output with <code>jq</code> reveals <code>policy_match_type: 1</code> confirming L3/L4 policy denial.',
        "Filter Hubble by Verdict"),
    58: ("Structured Flow Analysis with jq",
        'Using <code>hubble observe -o json | jq</code>, flows can be filtered, grouped, and aggregated. <strong>Verdict distribution</strong> (FORWARDED vs DROPPED), <strong>top source pods</strong> by flow count, and <strong>HTTP method/status breakdown</strong> are all available for programmatic analysis. Exported JSON files enable offline analysis and reporting.',
        "Export JSON and Analyze with jq"),
    59: ("Hubble UI Service Map Shows anihpj",
        'After enabling <code>hubble.ui.enabled=true</code> via Helm and deploying the UI, <code>cilium hubble ui</code> opens the Service Map at <code>http://localhost:12000</code>. The dependency graph shows <strong>web, api, and db nodes</strong> with green (FORWARDED) and red (DROPPED) flow lines. Real-time traffic metrics are visible for all anihpj components.',
        "Enable Hubble UI via Helm"),
    60: ("Hubble Relay Connected to All Peers",
        'After enabling Hubble on all Cilium agents and restarting Relay, the <code>hubble-peer</code> Service has endpoints (one per Cilium agent on port 4244). Hubble Relay connects to all peers via gRPC. <code>hubble observe -n anihpj</code> returns <strong>aggregated flows from every node</strong> in the cluster with FORWARDED/DROPPED verdicts.',
        "Enable Hubble on Cilium Agents"),
    61: ("Prometheus Scrapes Hubble Metrics",
        'After enabling <code>hubble.metrics.enabled</code> with HTTP, DNS, TCP, and drop metric types, the <code>hubble-metrics</code> Service exposes port 9965. The ServiceMonitor with <code>release: prometheus</code> label enables Prometheus auto-discovery. Queries for <code>hubble_http_requests_total</code> return request counts by method, path, and status code for anihpj.',
        "Enable Hubble Metrics and ServiceMonitor"),
    62: ("Grafana Dashboard Displays anihpj HTTP Metrics",
        'After importing the Hubble HTTP dashboard as a labeled ConfigMap (<code>grafana_dashboard=1</code>), Grafana auto-discovers it via sidecar provisioning. The dashboard displays <strong>anihpj HTTP request rate (QPS)</strong>, <strong>latency percentiles (p50/p95/p99)</strong>, and <strong>HTTP status code distribution</strong> (200, 404, 500). All panels are powered by Hubble metrics from Prometheus.',
        "Import Hubble Dashboard ConfigMap"),
    63: ("Hubble Metrics Target UP in Prometheus",
        'After adding the <code>release: prometheus</code> label to the hubble-metrics ServiceMonitor and configuring Prometheus to watch the <code>kube-system</code> namespace, the target shows <strong>UP</strong> in Prometheus. Queries for <code>hubble_http_requests_total</code>, <code>hubble_tcp_flags_total</code>, and <code>hubble_drop_total</code> all return valid anihpj data.',
        "Fix ServiceMonitor Label Selector"),
    64: ("Alert Fires When HTTP 500 Rate Exceeds 5%",
        'After creating the <code>PrometheusRule</code> CRD with the error ratio expression, Prometheus evaluates it every evaluation interval. When <code>rate(hubble_http_requests_total{status="500"}[5m]) / rate(hubble_http_requests_total[5m]) > 0.05</code> holds for 5 minutes, the alert transitions from <strong>PENDING to FIRING</strong>. Alertmanager routes the notification based on severity and team labels.',
        "Create PrometheusRule for HTTP 500 Alert"),
}

def fix_scenario(chunk, short_verify, verify_detail, short_fix):
    # 1. Fix verify h4 (too long to short title)
    m = re.search(rb'(<h4>\xe2\x9c\x85 Verify \xe2\x80\x94 ).+?(</h4>)', chunk)
    if m:
        new_h4 = '\u2705 Verify \u2014 '.encode() + short_verify.encode() + b'</h4>'
        chunk = chunk[:m.start()] + b'<h4>' + new_h4 + chunk[m.end():]
    
    # 2. Fix verify p (generic to specific)
    m = re.search(rb'(<div class="sc-resolution">.*?</h4>\s*)<p>.*?</p>', chunk, re.DOTALL)
    if m:
        new_p = b'<p>' + verify_detail.encode() + b'</p>'
        chunk = chunk[:m.start(1)] + m.group(1) + new_p + chunk[m.end():]
    
    # 3. Fix fix h4
    m = re.search(rb'<h4 style="color: #3fb950;">\xf0\x9f\x94\xa7 Fix \xe2\x80\x94 .+?</h4>', chunk)
    if m:
        new_fix_h4 = '<h4 style="color: #3fb950;">🔧 Fix — '.encode() + short_fix.encode() + b'</h4>'
        chunk = chunk[:m.start()] + new_fix_h4 + chunk[m.end():]
    
    # 4. Fix code header
    chunk = chunk.replace(
        b'BASH - copy &amp; paste into terminal',
        b'BASH - copy &amp; paste into Ubuntu terminal'
    )
    
    # 5. Fix error-spot lookat-item indentation
    es_idx = chunk.find(b'error-spot')
    if es_idx >= 0:
        es_end = chunk.find(b'debug-find', es_idx)
        if es_end > 0:
            before = chunk[:es_idx]
            es_section = chunk[es_idx:es_end]
            after = chunk[es_end:]
            
            # Add newlines between consecutive lookat-items in error-spot
            es_section = es_section.replace(
                b'</div><div class="lookat-item">',
                b'</div>\n                    <div class="lookat-item">'
            )
            # Fix first one after h4
            es_section = es_section.replace(
                b'</h4><div class="lookat-item">',
                b'</h4>\n                    <div class="lookat-item">'
            )
            
            chunk = before + es_section + after
    
    return chunk

for n in range(55, 65):
    bs = c.find(f'id="sc-s{n}"'.encode())
    if bs < 0:
        print(f'S{n}: NOT FOUND')
        continue
    bs = max(0, bs - 30)
    
    be = c.find(f'id="sc-s{n+1}"'.encode()) if n < 65 else -1
    if be < 0:
        be = c.find(b'id="appendices"', bs + 100)
    if be < 0:
        print(f'S{n}: END NOT FOUND')
        continue
    
    chunk = c[bs:be]
    short_v, detail_p, short_f = fixes[n]
    new_chunk = fix_scenario(chunk, short_v, detail_p, short_f)
    c = c[:bs] + new_chunk + c[be:]
    print(f'S{n}: REDESIGNED')

with open('cilium-test-prep.html', 'wb') as f:
    f.write(c)

print(f'\nDone! {len(c)} bytes')
