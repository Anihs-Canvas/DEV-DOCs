with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix S1 Step 2 - find exact pattern
# S1 Step 2 has: </div>\n        <p class="sc-kubectl">...apply...</p>\n        <h4>🔍 Step 2
old_s1_s2 = '</div>\n        <p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>\n        <h4>🔍 Step 2: Debug &amp; Troubleshoot</h4>\n        <div class="ts-lookat"><p><strong>1.</strong> Check pods:'

new_s1_s2 = '</div>\n        <p class="sc-kubectl"><strong>▶️ Apply:</strong> <code>kubectl apply -f anihpj-deploy.yaml</code></p>\n        <div class="sc-step">\n            <div class="sc-step-num debug">2</div>\n            <div class="sc-step-content">\n                <h4 class="debug">🔍 Debug &amp; Troubleshoot</h4>\n                <div class="ts-lookat"><p style="margin-top:0"><strong>1.</strong> Check pods:'

if old_s1_s2 in c:
    c = c.replace(old_s1_s2, new_s1_s2)
    print('Fixed S1 Step 2')
else:
    print('Checking alternative pattern...')
    # Try finding just the h4
    idx = c.find('<h4>🔍 Step 2: Debug &amp; Troubleshoot</h4>')
    if idx != -1:
        # Show context
        ctx = c[idx-100:idx+100]
        print('Context around S1 Step2 h4:')
        for i, line in enumerate(ctx.split('\n')):
            print(f'  {i}: {line[:120]}')

# Fix S1 duplicate sc-resolution div
dup = '<div class="sc-resolution">\n                    <div class="sc-resolution">'
fixed = '<div class="sc-resolution">'
if dup in c:
    c = c.replace(dup, fixed)
    print('Fixed duplicate sc-resolution')
else:
    print('No duplicate sc-resolution found')

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Size: {sz} KB')
