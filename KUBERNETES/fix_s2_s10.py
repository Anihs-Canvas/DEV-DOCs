import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'r', encoding='utf-8') as f:
    html = f.read()

def fix_scenario(html, n, app_story_text, file_tree_text):
    """Fix one scenario: extract embedded FS + APP from code block into proper divs"""
    
    # Find the scenario block
    start = html.find('id="sc-s{}"'.format(n))
    if start < 0:
        return html
    
    # Find the deploy h4
    deploy_h4 = html.find('<h4 class="deploy"', start)
    deploy_h4_end = html.find('</h4>', deploy_h4) + 5
    
    # Find the <p style> tag after h4
    p_start = html.find('<p style=', deploy_h4_end)
    p_end = html.find('</p>', p_start) + 4 if p_start > 0 else deploy_h4_end
    
    # Find the code-block after that
    code_block = html.find('<div class="code-block">', p_end)
    
    # Find the pre/code start
    pre_start = html.find('<pre><code id="sc-s{}-code">'.format(n), code_block)
    
    # Find the end of the code block
    code_end_marker = '</code></pre>'
    code_content_end = html.find(code_end_marker, pre_start)
    
    # Find the closing of code-block div
    code_div_end = html.find('</div>', code_content_end) + 6
    
    # Now extract the actual code content between the pre/code tags
    code_start = html.find('>', pre_start) + 1
    code_end = code_content_end
    
    code_text = html[code_start:code_end]
    
    # Remove FILE STRUCTURE lines from code
    code_text = re.sub(r'<span class="token comment"># =+\n</span>\n<span class="token comment"># FILE STRUCTURE.*?</span>\n(?:<span class="token comment"># .*?</span>\n)*?<span class="token comment"># =+\n</span>\n?', '', code_text, flags=re.DOTALL)
    if not file_tree_text:
        # If no specific tree, remove the first comment block
        code_text = re.sub(r'<span class="token comment"># =+\n</span>\n<span class="token comment"># FILE STRUCTURE.*?</span>\n(?:<span class="token comment"># .*?</span>\n)*?<span class="token comment"># =+\n</span>\n?', '', code_text, count=1, flags=re.DOTALL)
    
    # Remove APP STORY lines from code
    code_text = re.sub(r'<span class="token comment"># The APP STORY:\n</span>(?:<span class="token comment"># .*?\n</span>)*', '', code_text, flags=re.DOTALL)
    
    # Reconstruct the section
    deploy_part = html[deploy_h4:deploy_h4_end]
    
    # Build new content
    new_section = deploy_part + '\n'
    
    if app_story_text:
        new_section += '                    <div class="app-story"><strong>📖 APP STORY:</strong> ' + app_story_text + '</div>\n'
    
    if file_tree_text:
        new_section += '                    <div class="file-structure">\n'
        new_section += '                        <strong>📁 FILE STRUCTURE for anihpj/jobpost (S{}):</strong>\n'.format(n)
        new_section += '                        <pre>' + file_tree_text + '</pre>\n'
        new_section += '                    </div>\n'
    
    # Add back the code block with cleaned code
    code_header_end = html.find('</div>', html.find('<div class="code-header">', p_end)) + 6
    new_section += html[code_block:code_header_end] + '\n'
    new_section += '                        <pre><code id="sc-s{}-code">'.format(n) + code_text + '</code></pre>\n'
    new_section += '                    </div>\n'
    
    # Replace old content
    old_content = html[deploy_h4:code_div_end]
    html = html[:deploy_h4] + new_section + html[code_div_end:]
    
    return html

# Fix S3
html = fix_scenario(html, 3,
    'anihpj/jobpost launched 6 months ago with a 5Gi database. Now there are 50,000 job listings, 10,000 users, 200,000 applications. The DB is at 92% capacity — INSERTs are failing! <strong>DevOps patches PVC to 20Gi — but nothing happens. The StorageClass has allowVolumeExpansion: false. Lesson: Always set allowVolumeExpansion: true on production SCs!</strong>',
    'anihpj/\n├── 00-namespace.yaml               ← kubectl create ns anihpj\n├── 01-storageclass.yaml            ← SC with allowVolumeExpansion: false (BUG!)\n├── 02-persistentvolume.yaml        ← 20Gi PV (hostPath)\n├── 03-postgres-pvc.yaml            ← PVC 5Gi (too small for growing data)\n├── 04-postgres-statefulset.yaml    ← StatefulSet with volumeClaimTemplates\n└── 05-postgres-service.yaml        ← ClusterIP Service (port 5432)')

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('S2 and S3 fixed')
