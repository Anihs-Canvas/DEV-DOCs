import re

with open('linux_cli.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add CSS for output notes
content = content.replace(
    '        .example h5 { margin: 0 0 16px 0; color: var(--primary-light); font-size: 1.1em; font-weight: 600; }',
    '        .example h5 { margin: 0 0 16px 0; color: var(--primary-light); font-size: 1.1em; font-weight: 600; }\n        .output-note { color: var(--text-secondary); font-size: 0.9em; margin: 8px 0 0 0; border-left: 3px solid var(--border-color); padding-left: 12px; }'
)

explanations = {
    # ── ls examples ──
    'anihpj  api  docker-compose.yml  Dockerfile  Dockerfile.dev  jobpost  k8s  Makefile  manage.py  README.md  requirements.txt  scripts':
        'The root directory contains 5 project folders (anihpj, api, jobpost, k8s, scripts), Docker files, and configuration files. Everything is present — the deployment structure is intact and ready for the morning workflow.',

    'total 32\ndrwxr-xr-x  6 anihpj developers 4096 Jun  3 08:30 .\ndrwxr-xr-x 12 anihpj developers 4096 Jun  3 08:30 ..\ndrwxr-xr-x  2 anihpj developers 4096 Jun  2 10:20 base\ndrwxr-xr-x  2 anihpj developers 4096 Jun  2 10:20 cilium\ndrwxr-xr-x  2 anihpj developers 4096 Jun  2 10:20 ingress\ndrwxr-xr-x  2 anihpj developers 4096 Jun  2 10:20 monitoring':
        'The <code>k8s/</code> directory contains four subdirectories, not flat YAML files. Each subdirectory starts with <code>d</code> (directory), has <code>rwxr-xr-x</code> (755) permissions, and is owned by anihpj:developers. Ready for <code>kubectl apply -k</code>.',

    'total 56K\n-rw-r--r-- 1 anihpj developers 1.9K Jun  2 10:15 web-deployment.yaml\n-rw-r--r-- 1 anihpj developers 1.5K Jun  2 10:16 api-deployment.yaml\n-rw-r--r-- 1 anihpj developers 1.4K Jun  2 10:18 db-statefulset.yaml\n-rw-r--r-- 1 anihpj developers  320 Jun  2 10:20 configmap.yaml\n-rw-r--r-- 1 anihpj developers  890 Jun  2 10:20 web-service.yaml\n-rw-r--r-- 1 anihpj developers  678 Jun  2 10:20 api-service.yaml\n-rw-r--r-- 1 anihpj developers  567 Jun  2 10:20 db-service.yaml\n-rw-r--r-- 1 anihpj developers   92 Jun  2 10:20 namespace.yaml\n-rw------- 1 anihpj developers  234 Jun  2 10:20 secrets.yaml':
        'Nine YAML manifests with human-readable sizes (<code>-h</code>). secrets.yaml has restricted permissions (<code>rw-------</code> / 600) — only the owner can read or write. All other files use standard 644 (<code>rw-r--r--</code>), confirming good security hygiene.',

    'total 1240\n-rw-r--r-- 1 anihpj anihpj 524288 Jun  3 14:23 error.log\n-rw-r--r-- 1 anihpj anihpj 196542 Jun  3 14:23 app.log\n-rw-r--r-- 1 anihpj anihpj  89432 Jun  3 14:20 access.log':
        'Sorted by modification time (<code>-t</code>), newest first. error.log (524KB) and app.log were both modified at 14:23 — right when the incident occurred. The large file sizes confirm heavy activity during the incident window.',

    '__init__.py\nviews.py\nurls.py\nserializers.py':
        'Four Python files in the API app. The recursive search (<code>-R</code>) found them inside <code>/lpj/api/</code>, and <code>grep</code> filtered for <code>.py</code> files only. This confirms the API app has the expected structure.',

    # ── cd examples ──
    '/lpj':
        'Carol is now at the project root. Using <code>cd</code> with an absolute path (<code>/lpj</code>) guarantees she lands in the correct directory regardless of where she started.',

    '/lpj/jobpost/static/jobpost':
        'Alice navigated from templates to static using a relative path. <code>../..</code> went up two levels (templates/jobpost → jobpost), then <code>static/jobpost</code> descended into the target. Relative paths save typing when you are already near the target.',

    '/lpj/api':
        'Bob used <code>cd -</code> to return to his previous directory in one keystroke. The shell stores the last directory in <code>$OLDPWD</code> — <code>cd -</code> is shorthand for <code>cd $OLDPWD</code>.',

    '/home/dave':
        'Dave jumped from deep inside <code>/lpj/k8s/base</code> all the way to his home directory with just <code>cd ~</code>. No matter how deep you are, <code>cd</code> (no args) or <code>cd ~</code> always takes you home.',

    '/lpj/k8s/cilium:\n-rw-r--r-- 1 carol developers 2147 Jun  1 00:00 cnp-baseline.yaml\n-rw-r--r-- 1 carol developers 1704 Jun  1 00:00 cnp-l7.yaml\n-rw-r--r-- 1 carol developers 1094 Jun  1 00:00 cnp-dns.yaml\n-rw-r--r-- 1 carol developers 4599 May 15 14:22 ccnp-host-firewall.yaml\n-rw-r--r-- 1 carol developers 1234 May 15 14:22 cidrgroup-vpn.yaml\n\n/lpj/api:\n-rw-r--r-- 1 bob developers   1542 Jun  3 12:00 __init__.py\n-rw-r--r-- 1 bob developers   3847 Jun  3 12:00 views.py\n-rw-r--r-- 1 bob developers   2145 Jun  3 12:00 urls.py\n-rw-r--r-- 1 bob developers   4096 Jun  3 12:00 serializers.py':
        'Eve navigated deep into <code>k8s/cilium/</code> to audit 5 network policy files — all owned by carol with standard 644 permissions. Then she jumped to <code>/lpj/api/</code> where 4 Python files are owned by bob. All permissions are consistent.',

    # ── pwd examples ──
    '/lpj/k8s':
        '<code>pwd</code> confirms Carol is in the correct directory before running a destructive cleanup script. Always verify with <code>pwd</code> before <code>rm</code> — it is the cheapest insurance against disaster.',
    'Script running from: /lpj/scripts':
        'The script captured its own location using <code>SCRIPT_DIR="$(pwd)"</code>. This pattern is essential for scripts that need to find files relative to their own location, regardless of where they are invoked from.',
    'Logical: /lpj/k8s\nPhysical: /mnt/data/lpj/k8s':
        'The logical path (<code>pwd -L</code>) shows the symlink, while the physical path (<code>pwd -P</code>) reveals the real disk location. Dave now knows the data actually lives on <code>/mnt/data/</code>, not <code>/lpj/</code>.',
    '[2026-06-03 15:42:00] Running tests from /lpj/jobpost':
        'A timestamped log message confirms the test runner started from <code>/lpj/jobpost</code>. Embedding <code>$(pwd)</code> in log messages creates an audit trail — you can always trace where a command was executed.',
    '/lpj/api\n-rw-r--r-- 1 bob bob   1542 Jun  3 12:00 __init__.py\n-rw-r--r-- 1 bob bob   3847 Jun  3 12:00 views.py\n-rw-r--r-- 1 bob bob   2145 Jun  3 12:00 urls.py\n-rw-r--r-- 1 bob bob   4096 Jun  3 12:00 serializers.py':
        'Bob combined <code>pwd</code> with <code>ls -l</code> in one line — first confirming his location (<code>/lpj/api</code>), then listing the contents. The files are all owned by bob with 644 permissions, confirming they are ready for editing.',
}

# Apply replacements
count = 0
for output_text, explanation in explanations.items():
    old = '<div class="example-output">' + output_text + '</div>'
    new = '<div class="example-output">' + output_text + '</div>\n                    <p class="output-note"><strong>📝 What happened:</strong> ' + explanation + '</p>'
    if old in content:
        content = content.replace(old, new)
        count += 1
    else:
        print(f'MISS ({count}): {output_text[:50]}...')

with open('linux_cli.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone. Added {count} explanations.')
