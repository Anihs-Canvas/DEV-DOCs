with open('linux_cli.html', 'r', encoding='utf-8') as f:
    content = f.read()

explanations = {
    # ── tree examples ──
    '/lpj\n├── anihpj\n├── api\n├── jobpost\n│   ├── migrations\n│   ├── static\n│   └── templates\n├── k8s\n│   ├── base\n│   ├── cilium\n│   ├── ingress\n│   └── monitoring\n├── scripts\n├── Dockerfile\n├── Dockerfile.dev\n├── docker-compose.yml\n├── manage.py\n└── requirements.txt\n\n10 directories':
        'A clean 2-level overview of the entire project. Directories (with trailing slashes) show structure; root-level files confirm Docker and Django tooling. This is the output you would paste into <code>README.md</code> to onboard a new team member.',

    '/lpj/k8s\n├── [-rw-r--r-- carol   ]  configmap.yaml\n├── [-rw------- carol   ]  secrets.yaml\n├── [-rw-r--r-- carol   ]  deployment-api.yaml\n├── [-rw-r--r-- carol   ]  deployment-worker.yaml\n├── [-rw-r--r-- carol   ]  hpa.yaml\n├── [-rw-r--r-- carol   ]  ingress.yaml\n├── [-rw-r--r-- carol   ]  kustomization.yaml\n├── [-rw-r--r-- carol   ]  namespace.yaml\n├── [-rw-r--r-- carol   ]  cnp-baseline.yaml\n├── [-rw-r--r-- carol   ]  pdb.yaml\n├── [-rw-r--r-- carol   ]  service.yaml\n└── [-rw-r--r-- carol   ]  servicemonitor.yaml':
        'The <code>-pu</code> flags show file permissions and owner for each file. All files are owned by carol with standard 644 permissions (<code>rw-r--r--</code>), which is correct for K8s manifests.',

    '.\n├── [4.0K]  Dockerfile\n├── [1.2K]  Manage.py\n├── [ 12K]  requirements.txt\n├── [4.0K]  jobpost/\n├── [4.0K]  static/\n├── [4.0K]  templates/\n├── [4.0K]  tests/\n└── [4.0K]  media/':
        'The <code>-h</code> flag shows human-readable file sizes. requirements.txt is the largest at 12K — expected for a Python project with many dependencies. All directories consume 4.0K (the minimum block size).',

    '/lpj/config\n├── .env\n├── .env.example\n├── env/\n│   └── production.env\n├── gunicorn/\n│   └── gunicorn.conf.py\n├── nginx/\n│   ├── nginx.conf\n│   └── sites-enabled/\n│       └── anihpj.com\n├── postgres/\n│   ├── pg_hba.conf\n│   └── postgresql.conf\n├── redis/\n│   └── redis.conf\n└── ssl/\n    ├── anihpj.com.crt\n    ├── anihpj.com.csr\n    ├── anihpj.com.key\n    └── ca-bundle.crt':
        'The <code>-a</code> flag reveals hidden files (<code>.env</code>, <code>.env.example</code>) that are invisible to a normal tree. These dotfiles often contain sensitive configuration — always use <code>-a</code> during security audits.',

    '[{"type":"directory","name":"/lpj","contents":[\n    {"type":"directory","name":"anihpj","contents":[]},\n    {"type":"directory","name":"api","contents":[]},\n    {"type":"directory","name":"jobpost","contents":[\n      {"type":"directory","name":"migrations","contents":[]},\n      {"type":"directory","name":"static","contents":[]},\n      {"type":"directory","name":"templates","contents":[]}\n    ]},\n    {"type":"directory","name":"k8s","contents":[\n      {"type":"directory","name":"base","contents":[]},\n      {"type":"directory","name":"cilium","contents":[]},\n      {"type":"directory","name":"ingress","contents":[]},\n      {"type":"directory","name":"monitoring","contents":[]}\n    ]},\n    {"type":"directory","name":"scripts","contents":[]},\n    ...\n]}]':
        'The <code>-J</code> flag outputs parseable JSON. This can be piped into <code>jq</code> for filtering or consumed by documentation generators. Notice how nested directories use the <code>"contents"</code> array — a clean recursive structure.',

    # ── find examples ──
    '/lpj/jobpost/jobpost/views.py\n/lpj/jobpost/jobpost/models.py\n/lpj/jobpost/jobpost/urls.py':
        'Three Python files were modified in the last 24 hours (<code>-mtime -1</code>). These are the exact files Alice needs to review for her git commit — <code>find</code> did the detective work of identifying changed files.',

    '/lpj/jobpost/app.log.2026-04-01\n/lpj/jobpost/error.log.2026-04-15\n/lpj/k8s/.../access.log.2026-05-01\n3 files deleted':
        'Three log files older than 30 days were found and deleted. The <code>-print</code> flag confirmed which files were removed — always use this before running <code>-delete</code> in production. 3 files freed up disk space.',

    '-rw-rw-rw- 1 alice alice 1245 May 20 10:00 /lpj/anihpj/.env.example\n-rw-rw-rw- 1 root  root  4502 Jan 15  2026 /lpj/jobpost/test_legacy.py':
        'Two files have world-writable permissions (<code>rw-rw-rw-</code> / 666) — a serious security risk. Anyone can modify them. <code>.env.example</code> owned by alice should be 644, and <code>test_legacy.py</code> owned by root indicates a misconfiguration.',

    '-rw-r--r-- 1 anihpj anihpj 234M Jun  1 02:00 /lpj/k8s/backups/daily/jobpost_db_2026-06-01.dump\n-rw-r--r-- 1 anihpj anihpj 156M Jun  3 15:00 /lpj/k8s/ingress/access.log\n-rw-r--r-- 1 anihpj anihpj  89M Jun  3 14:55 /lpj/jobpost/app.log':
        'Three files over 50MB found, sorted largest-first. The database dump at 234MB is the biggest consumer — this is normal for a daily backup. The access.log (156MB) might need rotation. Total identified: ~479MB that could be archived.',

    '# No output on success — verify with:\n# find /lpj/jobpost -name "*.pyc"\n# (should return nothing)':
        'No output means all <code>.pyc</code> files were successfully renamed (or deleted). The verification command confirms zero matches remain. <code>find -exec</code> combined with <code>sh -c</code> gives you full shell power on each matched file.',

    '/lpj/jobpost/migrations/__pycache__\n/lpj/jobpost/src/old_components':
        'Two empty directories found. <code>__pycache__</code> is a Python artifact that can safely be deleted. <code>old_components</code> is likely leftover from a refactor — empty directories are harmless but indicate incomplete cleanup.',

    '524289  4 -rw-r--r-- 1 alice alice 2145 May 12 14:23 /lpj/anihpj/settings.py\n524290  8 -rw-r--r-- 1 carol carol 8192 May  8 09:00 /lpj/k8s/web-deployment.yaml':
        'Two files modified during the May 1-15 incident window. settings.py (alice, May 12) and web-deployment.yaml (carol, May 8). The <code>-ls</code> action includes inode numbers and sizes — useful for correlating with filesystem audit logs.',

    # ── locate examples ──
    '/lpj/jobpost/jobpost/settings.py\n/usr/lib/python3/dist-packages/django/conf/global_settings.py':
        'Two settings.py files found — one in the anihpj project and the Django framework default. <code>locate</code> searches the entire filesystem instantly because it queries a pre-built database, not the disk.',

    '/lpj/jobpost\n/lpj/jobpost/jobpost\n/lpj/docker/jobpost\n/lpj/docs/jobpost-deploy-guide.md\n/lpj/helm/jobpost\n... (15 results shown)':
        '15 results capped by <code>-l 15</code>. Case-insensitive search found matches regardless of capitalization. Without <code>-l</code>, locate might return hundreds of results — always limit output when scanning large systems.',

    '47':
        '<code>locate -c</code> counts matches instead of listing them. 47 configuration files exist under <code>/lpj/config/</code>. This is useful for quick audits — "how many YAML files do we have?" — without flooding the terminal.',

    '/lpj/k8s/web-deployment.yaml\n/lpj/k8s/api-deployment.yaml':
        'Only files that currently exist on disk are shown (<code>-e</code> flag). If a deployment had been deleted since the last <code>updatedb</code>, it would not appear here. Always use <code>-e</code> when you need accurate results.',

    '/lpj/scripts/new-deploy.sh\n/lpj/docs/new-deploy-guide.md':
        'After running <code>sudo updatedb</code>, the freshly created files are immediately findable. Without <code>updatedb</code>, new files would be invisible to locate until the nightly cron job rebuilds the database.',

    # ── which examples ──
    '/lpj/venv/bin/python3':
        'The Python interpreter is coming from the project virtual environment (<code>/lpj/venv/</code>), not the system Python. This confirms the virtualenv is activated and all <code>pip install</code> packages will be isolated.',

    '/lpj/venv/bin/python3\n/usr/local/bin/python3\n/usr/bin/python3':
        'Three Python installations exist on this system. The virtualenv version takes priority (listed first). <code>/usr/local/bin/python3</code> is a manual install, and <code>/usr/bin/python3</code> is the system default. Use <code>-a</code> to see the full chain.',

    '/usr/bin/docker\n/usr/local/bin/kubectl\n/usr/local/bin/helm\nMISSING TOOLS!':
        'Docker, kubectl, and helm are all found — but <code>argocd</code> is missing. The script detected this and printed "MISSING TOOLS!". This pattern (<code>which cmd1 cmd2 || echo "MISSING"</code>) is standard for pre-flight checks.',

    '/usr/bin/node\n/usr/bin/npm\n/usr/local/bin/npx\nAll tools found':
        'Node, npm, and npx are all available. <code>which</code> returned exit code 0 for all three, so the "All tools found" message printed. This is a reliable way to gate CI pipeline steps — if any tool is missing, fail early.',

    'terraform not installed':
        'The <code>if which terraform; then ... fi</code> pattern silently checks for a tool. Since terraform is not in <code>$PATH</code>, <code>which</code> returns exit code 1, and the else branch prints "not installed".',

    # ── whereis examples ──
    'gunicorn: /usr/local/bin/gunicorn /usr/share/man/man1/gunicorn.1.gz':
        '<code>whereis</code> found both the binary (<code>/usr/local/bin/gunicorn</code>) and its man page. This is more information than <code>which gunicorn</code> would give — <code>whereis</code> searches standard system directories beyond just <code>$PATH</code>.',

    'nginx: /usr/sbin/nginx /usr/lib/nginx /etc/nginx /usr/share/nginx':
        'Only binaries shown (<code>-b</code>). Nginx has four binary-related locations — the daemon itself, its library directory, its config directory, and shared data. This tells you where to look when troubleshooting nginx.',

    'postgres: /usr/share/man/man1/postgres.1.gz':
        'Only the man page found (<code>-m</code>). This means the PostgreSQL client is installed (hence the man page), but the server binary might be elsewhere. Man pages are great for discovering installed-but-not-active tools.',

    'docker: /usr/bin/docker /usr/libexec/docker /etc/docker /usr/share/man/man1/docker.1.gz\nkubectl: /usr/local/bin/kubectl\nhelm: /usr/local/bin/helm':
        'Three tools queried in one command. Docker has the richest footprint (binary + libexec + config + man). kubectl and helm are single-binary installs. This overview tells Carol her toolchain is fully installed.',

    '=== which ===\n/usr/sbin/nginx\n=== whereis ===\nnginx: /usr/sbin/nginx /usr/lib/nginx /etc/nginx /usr/share/nginx /usr/share/man/man8/nginx.8.gz':
        'Side-by-side comparison: <code>which</code> returns only the binary path; <code>whereis</code> returns binaries, config directories, and man pages. Use <code>which</code> for "what runs?", <code>whereis</code> for "where is everything related to this command?"',

    # ── type examples ──
    'cd is a shell builtin\necho is a shell builtin\nalias is a shell builtin\nsource is a shell builtin\nexport is a shell builtin\npwd is a shell builtin':
        'Six commands are all shell builtins — they are part of bash itself, not separate binaries. This means they have no man pages and <code>which</code> won\'t find them. Use <code>help &lt;cmd&gt;</code> for documentation.',

    'ls is aliased to `ls --color=auto -h\'':
        'The <code>ls</code> command is not running the raw binary — it is aliased with <code>--color=auto -h</code>. This explains why <code>ls</code> always shows colors and human-readable sizes. Aliases can shadow the original command — <code>type</code> reveals the truth.',
    'grep is a function\ngrep ()\n{\n    /usr/bin/grep --color=auto "$@"\n}\ngrep is /usr/bin/grep':
        'A function AND a binary both named grep exist. The function (defined first) takes priority — it wraps the binary with <code>--color=auto</code>. <code>type -a</code> shows the full resolution chain: function → binary.',

    'kubectl ready':
        'The <code>type -t</code> flag outputs a single word — "file" means an external binary was found. Redirecting to <code>/dev/null</code> suppresses that word, and the exit code drives the conditional. This pattern is cleaner than <code>which</code> for scripts.',

    'Exit: 1\ncd is a shell builtin\nExit: 0':
        '<code>which cd</code> failed (exit 1) because cd is not an external binary. <code>type cd</code> succeeded (exit 0) and correctly identified it as a shell builtin. This is the definitive demonstration: <code>type</code> sees what the shell sees.',

    # ── dirs examples ──
    ' 0  /lpj/k8s/ingress\n 1  /lpj/jobpost/templates\n 2  /lpj/jobpost\n 3  /lpj':
        'Four entries in the stack, numbered 0-3. Index 0 is the current directory (<code>/lpj/k8s/ingress</code>). Index 3 is the project root — the first directory pushed. The stack grows leftward; popping will return to index 1.',

    '/lpj/k8s/ingress\n/lpj/jobpost/templates\n/lpj/jobpost\n/lpj':
        'One entry per line (<code>-p</code>) — ideal for shell scripts that need to iterate over the stack with <code>while read dir; do ...; done</code>. No index numbers, just clean paths.',

    ' 0  /lpj':
        'After <code>dirs -c</code>, the stack has only one entry — the current directory. A clean stack is a fresh start for the next task. This is good practice after finishing a complex navigation session.',

    # ── pushd examples ──
    ' 0  /lpj/api\n 1  /lpj/ops/logs\n 2  /lpj':
        'The stack shows the push order: api was pushed last (index 0), logs before that (index 1), and root was the starting point (index 2). Pop will return to logs, then root.',
    '/lpj/jobpost /lpj /lpj/k8s/ingress /lpj/jobpost/templates':
        '<code>pushd +2</code> rotated the stack — the entry at index 2 (<code>/lpj/k8s/ingress</code>) moved to the top. The other entries shifted right. This lets you jump to any directory in the stack without losing the trail.',
    'Deployed, back in /lpj':
        'The script changed to <code>/lpj/k8s/base</code>, deployed, then popped back. The final <code>pwd</code> confirms the return. Using <code>pushd/popd</code> in scripts prevents accidental directory drift — you always return to where you started.',

    # ── popd examples ──
    '/lpj/k8s/ingress\n/lpj':
        'Two pops returned Carol from <code>/lpj/anihpj</code> through <code>/lpj/k8s/ingress</code> back to root. <code>pwd</code> after each pop confirmed the trail. The stack is now empty — all pushed directories have been visited.',
    '/lpj/anihpj\n 0  /lpj/anihpj\n 1  /lpj':
        '<code>popd -n</code> removed the top entry from the stack without changing directories. Dave stayed in <code>/lpj/anihpj</code> but the stack shrank from 3 to 2 entries. Useful for cleaning the stack while staying put.',
    'Stack is empty — already at root':
        'Trying to <code>popd</code> an empty stack produces an error (exit code 1). The <code>||</code> operator caught it and printed a friendly message. Always handle empty stacks in scripts to avoid unexpected failures.',
}

count = 0
for output_text, explanation in explanations.items():
    old = '<div class="example-output">' + output_text + '</div>'
    new = '<div class="example-output">' + output_text + '</div>\n                    <p class="output-note"><strong>📝 What happened:</strong> ' + explanation + '</p>'
    if old in content:
        content = content.replace(old, new)
        count += 1
    else:
        # Try with different line endings
        alt = output_text.replace('\n', '\r\n')
        old_alt = '<div class="example-output">' + alt + '</div>'
        if old_alt in content:
            content = content.replace(old_alt, new)
            count += 1
        else:
            print(f'MISS: {output_text[:70]}...')

with open('linux_cli.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone. Added {count} explanations.')
