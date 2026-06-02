with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# S1 is missing its opening tags. Find where the raw YAML code starts for S1.
# The YAML starts with: kind: Namespace\nmetadata:\n  name: anihpj
s1_yaml_start = c.find('kind: Namespace\nmetadata:\n  name: anihpj')
if s1_yaml_start == -1:
    print('ERROR: Cannot find S1 YAML start')
else:
    # Go back to find the <pre><code id="s1-code"> tag
    code_start = c.rfind('<pre><code id="s1-code">', 0, s1_yaml_start)
    if code_start == -1:
        print('ERROR: Cannot find s1-code')
    else:
        # The code-block div starts before that
        cb_start = c.rfind('<div class="code-block">', 0, code_start)
        # The sc-step-content h4 deploy should be even before
        h4_deploy = c.rfind('<h4 class="deploy">📋 Deploy the YAML</h4>', 0, cb_start)
        
        if h4_deploy != -1:
            # The sc-step-content div should be right before h4
            sc_step_content = c.rfind('<div class="sc-step-content">', 0, h4_deploy)
            if sc_step_content != -1:
                # Before that: <div class="sc-step-num deploy">1</div>
                # Before that: <div class="sc-step">
                # Before that: <div class="sc-body">
                
                # Found the start of sc-body content. We need to prepend the header.
                body_start = c.rfind('<div class="sc-body">', 0, sc_step_content)
                
                s1_header = '''    <div class="scenario-block" id="s1">
        <div class="sc-header">
            <div class="sc-badge">S1</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S1 — Category 1: Architecture</div>
                <h4>🚀 Deploy anihpj on Cilium — Verify Pod-to-Pod Connectivity</h4>
                <div class="sc-desc"><strong>📦 What This App Does:</strong> anihpj is a Django job posting platform with three tiers: web (Django+Gunicorn on :8000), api (Django REST on :8080), and db (PostgreSQL on :5432). This lab deploys all three on a Cilium cluster and verifies pod-to-pod communication using Hubble.</div>
            </div>
        </div>
'''
                c = c[:body_start] + s1_header + c[body_start:]
                print('Reconstructed S1 header')
            else:
                print('ERROR: sc-step-content not found')
        else:
            print('ERROR: h4 deploy not found')

# Fix S1 Step 2 (old format without sc-step wrapper)
# Pattern: after sc-kubectl, directly <h4>🔍 Step 2
old_s1_step2 = '<p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>\n        <h4>🔍 Step 2: Debug &amp; Troubleshoot</h4>\n        <div class="ts-lookat"><p><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj -o wide</code> — all must be Running</p>'

new_s1_step2 = '<p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>\n        <div class="sc-step">\n            <div class="sc-step-num debug">2</div>\n            <div class="sc-step-content">\n                <h4 class="debug">🔍 Debug &amp; Troubleshoot</h4>\n                <div class="ts-lookat"><p style="margin-top:0"><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj -o wide</code> — all must be Running</p>'

if old_s1_step2 in c:
    c = c.replace(old_s1_step2, new_s1_step2)
    print('Fixed S1 Step 2')
else:
    print('S1 Step 2 not found (may already be fixed)')

# Fix S1 resolution duplicate:
# Broken: </div></div><div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution">
# Should just be: <div class="sc-resolution">
broken_res = '</div></div><div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution">'
fixed_res = '<div class="sc-resolution">'
if broken_res in c:
    c = c.replace(broken_res, fixed_res)
    print('Fixed S1 resolution duplicate')
else:
    print('S1 resolution duplicate not found')

# Also fix the trailing structure: after resolution p, close sc-resolution, sc-step-content, sc-step, sc-body, scenario-block
# Pattern: ...Cilium CNI is correctly installed and routing pod traffic.</p>\n                </div>\n            </div>\n        </div>\n        </div>\n    </div>
# This should close properly. Let me check if S2 starts correctly after.

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Size: {sz} KB | </main>: {c.count("</main>")}')
print(f'scenario-block: {c.count("scenario-block")} | sc-step: {c.count("sc-step")}')
