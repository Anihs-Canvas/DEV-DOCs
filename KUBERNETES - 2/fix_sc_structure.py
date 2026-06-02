with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix diagram placement - it got inserted inside S1's sc-header. Extract and place before S1.
diag_start = c.index('<div class="diagram-container">\n            <div class="diagram-title">🏗️ Part 3 Labs')
diag_end = c.index('</div>\n    \n            <div class="sc-header-content">', diag_start)
diagram_block = c[diag_start:diag_end]
# Remove from wrong location
c = c[:diag_start] + c[diag_end:]

# Insert right before the first scenario-block in part3-cat1
s1_start = c.index('<div class="scenario-block" id="s1">')
c = c[:s1_start] + '\n        ' + diagram_block + '\n    \n    ' + c[s1_start:]

# 2. Replace the old S1 step/body structure with new sc-step format
old_s1_body = '''        <div class="sc-body">

        <h4>📋 Step 1: Deploy the YAML</h4>
        <div class="code-block">
            <div class="code-header">
                <span class="code-lang">YAML — anihpj-deploy.yaml</span>
                <button class="copy-btn" onclick="copyToClipboard(this, 's1-code')">📋 Copy</button>
            </div>
            <pre><code id="s1-code">apiVersion: v1'''

new_s1_body = '''        <div class="sc-body">
        <div class="sc-step">
            <div class="sc-step-num deploy">1</div>
            <div class="sc-step-content">
                <h4 class="deploy">📋 Deploy the YAML</h4>
                <div class="code-block">
            <div class="code-header">
                <span class="code-lang">YAML — anihpj-deploy.yaml</span>
                <button class="copy-btn" onclick="copyToClipboard(this, 's1-code')">📋 Copy</button>
            </div>
            <pre><code id="s1-code">apiVersion: v1'''

c = c.replace(old_s1_body, new_s1_body)

# 3. Replace Step 2 heading and ts-lookat with sc-step
old_step2 = '''<p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>
        <h4>🔍 Step 2: Debug &amp; Troubleshoot</h4>
        <div class="ts-lookat"><p><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj -o wide</code> — all must be Running</p>'''

new_step2 = '''<p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>
        <div class="sc-step">
            <div class="sc-step-num debug">2</div>
            <div class="sc-step-content">
                <h4 class="debug">🔍 Debug &amp; Troubleshoot</h4>
                <div class="ts-lookat"><p style="margin-top:0"><strong>1.</strong> Check pods: <code>kubectl get pods -n anihpj -o wide</code> — all must be Running</p>'''

c = c.replace(old_step2, new_step2)

# 4. Replace Resolution with sc-resolution
old_res = '''<p><strong>6.</strong> Connectivity test: <code>cilium connectivity test</code></p></div>
        <h4>✅ Expected Resolution</h4>
        <p>All pods Running with CiliumEndpoints. Same-node and cross-node pod-to-pod communication works. Hubble shows FORWARDED flows between web→api and api→db. <code>cilium connectivity test</code> passes all checks. This verifies your Cilium CNI is correctly installed and routing pod traffic.</p>
    
        </div>
    </div>'''

new_res = '''<p><strong>6.</strong> Connectivity test: <code>cilium connectivity test</code></p></div>
            </div>
        </div>
        <div class="sc-step">
            <div class="sc-step-num answer">✓</div>
            <div class="sc-step-content">
                <div class="sc-resolution">
                    <h4>✅ Expected Resolution</h4>
                    <p>All pods Running with CiliumEndpoints. Same-node and cross-node pod-to-pod communication works. Hubble shows FORWARDED flows between web→api and api→db. <code>cilium connectivity test</code> passes all checks. This verifies your Cilium CNI is correctly installed and routing pod traffic.</p>
                </div>
            </div>
        </div>
        </div>
    </div>'''

c = c.replace(old_res, new_res)

# 5. Now process S2 through S20 similarly - batch replace the common patterns
# Pattern: Replace all remaining "Step 1: Deploy" headings
import re

# Replace all remaining h4 Step 1 patterns
c = c.replace(
    '<h4>📋 Step 1: Deploy the YAML</h4>',
    '<div class="sc-step"><div class="sc-step-num deploy">1</div><div class="sc-step-content"><h4 class="deploy">📋 Deploy the YAML</h4>'
)

# Replace all remaining h4 Step 2 patterns
c = c.replace(
    '<h4>🔍 Step 2: Debug &amp; Troubleshoot</h4>',
    '</div></div><div class="sc-step"><div class="sc-step-num debug">2</div><div class="sc-step-content"><h4 class="debug">🔍 Debug &amp; Troubleshoot</h4>'
)

# Replace all remaining "Expected Resolution" patterns
c = c.replace(
    '<h4>✅ Expected Resolution</h4>',
    '</div></div><div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution"><h4>✅ Expected Resolution</h4>'
)

# Fix closing: after resolution p, before </div></div> (end of sc-body and scenario-block)
# Need to add the closing divs for sc-resolution and sc-step
# Pattern: resolution text followed by </div> (end sc-body) and </div> (end scenario-block)
old_close = '''Hubble shows FORWARDED flows.'''
new_close = '''Hubble shows FORWARDED flows.</p></div></div></div>'''

c = c.replace(old_close, new_close)

# Also fix the "All pods Running" close pattern
old_close2 = '''Cilium CNI is correctly installed.</p>
        </div>
    </div>
    </div>'''
new_close2 = '''Cilium CNI is correctly installed.</p></div></div></div>
        </div>
    </div>'''

c = c.replace(old_close2, new_close2)

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Fixes applied. Size: {sz} KB | </main>: {c.count("</main>")}')

# Count new elements
print(f'sc-step: {c.count("sc-step")}')
print(f'sc-step-num: {c.count("sc-step-num")}')
print(f'sc-resolution: {c.count("sc-resolution")}')
print(f'diagram-container: {c.count("diagram-container")}')
print(f'scenario-block: {c.count("scenario-block")}')
