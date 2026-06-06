"""Scale down cluster specs to realistic demo/learning sizes"""
import re

fp_html = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
fp_txt = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.txt'

for fp in [fp_html, fp_txt]:
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()

    replacements = [
        # Hero / totals
        ('54 cores', '22 cores'),
        ('212 GB', '88 GB'),
        ('2.3 TB', '0.8 TB'),
        ('54 vCPUs', '22 vCPUs'),
        ('212 GB across all nodes', '88 GB across all nodes'),
        ('2.3 TB SSD (all nodes)', '0.8 TB SSD (all nodes'),
        ('54 cores across all nodes', '22 cores across all nodes'),
        # CP node specs (100 GB SSD -> 60 GB, 16 GB -> 8 GB, 4 vCPU -> 2 vCPU)
        ('<span class="spec-val">4 vCPU</span>', '<span class="spec-val">2 vCPU</span>'),
        ('<span class="spec-val">16 GB</span>', '<span class="spec-val">8 GB</span>'),
        ('<span class="spec-val">100 GB SSD</span>', '<span class="spec-val">60 GB SSD</span>'),
        # Std worker specs (200 GB SSD -> 80 GB)
        ('<span class="spec-val">200 GB SSD</span>', '<span class="spec-val">80 GB SSD</span>'),
        # High-cap worker specs (8 vCPU -> 4, 32 GB -> 16, 500 GB -> 160)
        ('<span class="spec-val">8 vCPU ⚡</span>', '<span class="spec-val">4 vCPU ⚡</span>'),
        ('<span class="spec-val">32 GB ⚡</span>', '<span class="spec-val">16 GB ⚡</span>'),
        ('<span class="spec-val">500 GB SSD</span>', '<span class="spec-val">160 GB SSD</span>'),
        # Frontend specs (2 vCPU -> 1, 8 GB -> 4, 80 GB -> 30)
        ('<span class="spec-val">2 vCPU</span>', '<span class="spec-val">1 vCPU</span>'),
        # Handle the 2 vCPU -> 1 vCPU but NOT the one we just changed from 4 vCPU -> 2 vCPU
        # Actually we need to be more careful. Let me do frontend specifically
    ]

    for old, new in replacements:
        c = c.replace(old, new)

    # Now handle the tricky ones with context
    # Frontend: 8 GB -> 4 GB (but only in frontend cards, not CP/worker)
    c = c.replace('>fe-01</span><span class="node-ip">10.0.5.10</span>',
                   '>fe-01</span><span class="node-ip">10.0.5.10</span>')
    
    # More targeted: find frontend sections and fix them
    # fe-01 card RAM
    fe01_start = c.find('fe-01</span><span class="node-ip">10.0.5.10</span>')
    if fe01_start > 0:
        fe_context = c[fe01_start:fe01_start+500]
        # Replace 8 GB in this section
        old_fe_ram = 'RAM:</span> <span class="spec-val">8 GB</span>'
        new_fe_ram = 'RAM:</span> <span class="spec-val">4 GB</span>'
        c = c.replace(old_fe_ram, new_fe_ram, 1)
        c = c.replace(old_fe_ram, new_fe_ram, 1)  # fe-02
    
    old_fe_disk = '<span class="spec-val">80 GB SSD</span>'
    new_fe_disk = '<span class="spec-val">30 GB SSD</span>'
    # Only replace the frontend ones - find by counting
    # After previous replacements, "80 GB SSD" should only appear in frontend
    count = c.count(old_fe_disk)
    if count <= 2:
        c = c.replace(old_fe_disk, new_fe_disk)
    
    # Allocatable table values  
    # ~3.25 CPU per CP/node -> ~1.25
    c = c.replace('~3.25 cores each', '~1.25 cores each')
    c = c.replace('~7.25 cores each', '~3.25 cores each')
    c = c.replace('~14.5 GB each', '~6.5 GB each')
    c = c.replace('~30.5 GB each', '~14.5 GB each')
    c = c.replace('~40.5 cores', '~14 cores')
    c = c.replace('~179 GB', '~56 GB')
    c = c.replace('~85 GB', '~49 GB')  # ephemeral CP
    c = c.replace('~185 GB', '~69 GB')  # ephemeral std worker
    c = c.replace('~485 GB', '~149 GB')  # ephemeral high-cap
    
    # Resource bar percentages
    c = c.replace('~40.5 / 54 cores (75%)', '~14 / 22 cores (64%)')
    c = c.replace('width:75%', 'width:64%')
    c = c.replace('~179 / 212 GB (84%)', '~56 / 88 GB (64%)')
    c = c.replace('width:84%', 'width:64%')
    
    # Text descriptions in highlight boxes
    c = c.replace('~7.25 vCPUs and ~30.5 GB RAM', '~3.25 vCPUs and ~14.5 GB RAM')
    c = c.replace('3.25 vCPUs and ~6.5 GB', '~1.25 vCPUs and ~6.5 GB')
    c = c.replace('~3.25 vCPUs and ~14.5 GB', '~1.25 vCPUs and ~6.5 GB')

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(c)

    print(f'Updated: {fp}')

# Verify
for fp in [fp_html, fp_txt]:
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    print(f'\n{fp.split(chr(92))[-1]}:')
    print(f'  Lines: {c.count(chr(10))}')
    # Count remaining old values that shouldn't be there
    issues = []
    for old_val in ['54 cores', '212 GB', '2.3 TB']:
        if old_val in c:
            issues.append(f'  STILL HAS: {old_val}')
            # Show context
            idx = c.find(old_val)
            print(f'    at position {idx}: ...{c[max(0,idx-30):idx+30]}...')
    if not issues:
        print('  ✓ All old values replaced')
    else:
        for i in issues:
            print(i)
