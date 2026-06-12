#!/usr/bin/env python3
"""Add missing content based on official LFCS domains analysis.

Gaps found vs official LFCS domains (https://training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs/):

1. "Manage personal and system-wide environment profiles" → Add s5-7 to Chapter 5
2. "Implement reverse proxies and load balancers" → Add s27-6 load balancer section to Chapter 27
3. "Configure packet filtering, port redirection, and NAT" → Fix s21-4 section title to match sidebar
"""

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ============================================================
# FIX 1: Fix s21-4 section title to match sidebar ("NAT & Port Redirection")
# ============================================================
old_title = '<div class="section-block" id="s21-4"><h3>21.4 iptables — The Classic Approach</h3>'
new_title = '<div class="section-block" id="s21-4"><h3>21.4 NAT, Port Redirection & iptables</h3>'
if old_title in content and new_title not in content:
    content = content.replace(old_title, new_title)
    changes += 1
    print(f"  ✅ Fixed s21-4 title: 'iptables — The Classic Approach' → 'NAT, Port Redirection & iptables'")

# ============================================================
# FIX 2: Add s5-7 "Environment Profiles" to Chapter 5
# ============================================================
env_profiles_section = '''
        <div class="section-block" id="s5-7"><h3>5.7 Environment Profiles — System-Wide & Personal 🎯</h3>
            <div class="info-box note"><h5>🧠 Why This Matters for LFCS</h5><p>The LFCS exam explicitly tests your ability to <strong>manage personal and system-wide environment profiles</strong>. Every time you (or a service) logs in, a cascade of shell startup files determines what variables, aliases, and PATH entries are available. Understanding this chain is critical for debugging "it works when I run it but not in cron" and for setting up server environments correctly. The <strong>anihpj</strong> production server needs consistent environment variables for Django settings, database URLs, and API keys — and the right profile file for each use case.</p></div>

            <div class="diagram-container"><div class="diagram-title">Shell Startup File Loading Order — Login vs Non-Login Shell</div>
<pre>
  ╔══════════════════════════════════════════════════════════════════╗
  ║              LOGIN SHELL (SSH, console, su -)                   ║
  ║  /etc/profile  →  /etc/profile.d/*.sh  →  ~/.bash_profile     ║
  ║       │              (all .sh scripts)     OR ~/.bash_login     ║
  ║       │                                     OR ~/.profile       ║
  ║       └── First match in ~/ wins (bash_profile preferred)      ║
  ╚══════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════╗
  ║        NON-LOGIN SHELL (new terminal tab, gnome-terminal)       ║
  ║              /etc/bash.bashrc  →  ~/.bashrc                     ║
  ╚══════════════════════════════════════════════════════════════════╝</pre></div>

            <table class="compare-table"><thead><tr><th>File</th><th>Scope</th><th>When Loaded</th><th>What Goes Here</th></tr></thead><tbody>
                <tr><td><code>/etc/profile</code></td><td>System-wide</td><td>Login shells</td><td>System PATH, umask, global env vars</td></tr>
                <tr><td><code>/etc/profile.d/*.sh</code></td><td>System-wide (modular)</td><td>Login shells</td><td>App-specific env (Java, Go, Python). Drop a .sh file here instead of editing /etc/profile</td></tr>
                <tr><td><code>/etc/bash.bashrc</code></td><td>System-wide</td><td>Non-login interactive</td><td>System aliases, default PS1 prompt</td></tr>
                <tr><td><code>/etc/environment</code></td><td>System-wide (PAM)</td><td>ALL shells (via PAM)</td><td>Bare VAR=value format. No shell syntax. Read by pam_env.so</td></tr>
                <tr><td><code>/etc/skel/</code></td><td>Template directory</td><td>NEW user creation</td><td>Default .bashrc, .profile copied to new home dirs</td></tr>
                <tr><td><code>~/.bash_profile</code></td><td>User-specific</td><td>Login shells ONLY</td><td>PATH additions, environment vars, source ~/.bashrc</td></tr>
                <tr><td><code>~/.bashrc</code></td><td>User-specific</td><td>Non-login interactive</td><td>Aliases, prompt (PS1), shell functions</td></tr>
                <tr><td><code>~/.profile</code></td><td>User-specific</td><td>Login shells (fallback)</td><td>Used if .bash_profile doesn't exist</td></tr>
                <tr><td><code>~/.bash_logout</code></td><td>User-specific</td><td>When logging OUT</td><td>Cleanup, clear screen, delete temp files</td></tr>
            </tbody></table>

            <div class="split-panel">
                <div class="split-side split-good"><h5>✅ Best Practice — Source .bashrc from .bash_profile</h5><pre><code># ~/.bash_profile — loaded on login shells (SSH)
# Always source .bashrc so aliases work everywhere:
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Environment variables here:
export PATH="$HOME/bin:$PATH"
export DJANGO_SETTINGS_MODULE=anihpj.settings.production
export DATABASE_URL=postgresql://anihpj_user:pass@localhost/anihpj_db</code></pre></div>
                <div class="split-side split-bad"><h5>❌ Common Mistake — Vars in wrong file</h5><pre><code># ~/.bashrc — loaded on NON-login shells
# DON'T put export here — it runs EVERY time a
# subshell starts, including shell scripts!

export DATABASE_URL=postgresql://...  # ❌ Redundant re-export
export SECRET_KEY=supersecret         # ❌ Exposed in every subshell

# .bashrc is for: aliases, prompt, functions
alias ll='ls -la'
PS1='[\\u@\\h \\W]\\$ '</code></pre></div>
            </div>

            <div class="info-box tip"><h5>💡 /etc/environment — The PAM-Managed Profile</h5><p><code>/etc/environment</code> is NOT a shell script — it's read by <strong>pam_env.so</strong> (PAM module) and applied to ALL sessions regardless of shell. Format is strict: <code>VAR="value"</code> with NO export, NO spaces around =, NO shell syntax. Used by display managers (GDM), SSH, and cron. Example: <code>PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"</code>. <strong>For anihpj:</strong> Don't put secrets here — it's world-readable. Use it for system-wide defaults only.</p></div>

            <div class="info-box note"><h5>🔬 The /etc/skel/ Template — New User Defaults</h5><p>When you run <code>useradd -m anihpj_deploy</code>, the contents of <code>/etc/skel/</code> are COPIED to the new user's home directory. This is how every new user gets a default <code>.bashrc</code>, <code>.profile</code>, and <code>.bash_logout</code>. <strong>For anihpj team:</strong> Add project-specific aliases and environment hints to <code>/etc/skel/.bashrc</code> so every new developer automatically has them: <code>echo "alias cdw='cd /var/www/anihpj'" >> /etc/skel/.bashrc</code>. <code>echo "alias deploy='cd /var/www/anihpj && git pull && sudo systemctl restart anihpj'" >> /etc/skel/.bashrc</code>. <code>echo 'echo "Welcome to anihpj server. Type cdw to go to the project."' >> /etc/skel/.bashrc</code>.</p></div>

            <div class="diagram-container"><div class="diagram-title">Common Environment Profile Use Cases for Anihpj</div>
<pre>
  USE CASE                              | BEST FILE TO USE
  ─────────────────────────────────────┼────────────────────────
  Django SECRET_KEY (per-server)        | systemd EnvironmentFile
  Django DATABASE_URL                   | ~/.bash_profile OR systemd
  Custom PATH for anihpj/bin scripts    | /etc/profile.d/anihpj.sh
  Aliases (cdw, deploy, logs)           | ~/.bashrc
  System-wide umask 027                 | /etc/profile
  Default PS1 prompt for all users      | /etc/bash.bashrc
  Go/Java/Python HOME for all           | /etc/profile.d/lang.sh
  Welcome message for new devs          | /etc/skel/.bashrc
  Cleanup temp files on logout          | ~/.bash_logout</pre></div>

            <div class="info-box danger"><h5>⚠️ CRITICAL: Why "It works from terminal but not in cron"</h5><p>Cron jobs run with a <strong>minimal environment</strong> — no .bashrc, no .bash_profile, no aliases, a stripped-down PATH. This is the #1 reason scripts fail in cron but work interactively. <strong>Solutions:</strong> (1) Use <strong>absolute paths</strong> in cron commands: <code>/usr/bin/python3 /var/www/anihpj/manage.py clearsessions</code>. (2) Source your profile at the top of the script: <code>source /home/anihpj/.bash_profile</code>. (3) Set specific variables in the crontab: <code>PATH=/usr/local/bin:/usr/bin:/bin</code>. (4) Use <strong>systemd timers</strong> instead — they have their own Environment directive. <strong>Debug:</strong> <code>* * * * * /usr/bin/env > /tmp/cron_env.txt</code> — see exactly what cron sees.</p></div>
        </div>'''

# Insert s5-7 before the Ch5 visual summary
ch5_vs_marker = '        <div class="visual-summary"><h4>📊 Chapter 5 Visual Summary</h4><div class="vs-grid">\n'
if ch5_vs_marker in content and 'id="s5-7"' not in content:
    content = content.replace(ch5_vs_marker, env_profiles_section + '\n' + ch5_vs_marker)
    changes += 1
    print("  ✅ Added s5-7: Environment Profiles to Chapter 5")

# ============================================================
# FIX 3: Add sidebar entry for s5-7 in Chapter 5 sub-toc
# ============================================================
s5_sidebar_marker = '                            <li><a href="#s5-6">5.6 I/O Redirection & Pipes</a></li>\n'
s5_sidebar_new = '                            <li><a href="#s5-6">5.6 I/O Redirection & Pipes</a></li>\n                            <li><a href="#s5-7">5.7 Environment Profiles</a></li>\n'
if s5_sidebar_marker in content and s5_sidebar_new not in content:
    content = content.replace(s5_sidebar_marker, s5_sidebar_new)
    changes += 1
    print("  ✅ Added s5-7 sidebar entry")

# ============================================================
# FIX 4: Add s27-6 "Load Balancer Configuration with Nginx" to Chapter 27
# ============================================================
lb_section = '''
        <div class="section-block" id="s27-6"><h3>27.6 Nginx Load Balancer — Distributing Traffic 🎯</h3>
            <div class="info-box note"><h5>🧠 Why Load Balancers Matter for LFCS</h5><p>The official LFCS domain explicitly lists "<strong>Implement reverse proxies and load balancers</strong>." A reverse proxy forwards requests to ONE backend; a load balancer distributes requests across <strong>MULTIPLE backends</strong>. This is how high-traffic sites stay up — if one Gunicorn worker crashes, the load balancer routes traffic to the healthy ones. For <strong>anihpj</strong> in production, you'd run 3-4 Gunicorn workers on different ports and have Nginx distribute traffic among them.</p></div>

            <div class="diagram-container"><div class="diagram-title">Load Balancer Architecture — Anihpj Production Setup</div>
<pre>
                        INTERNET
                           │
                    ┌──────▼──────┐
                    │   Nginx LB  │  (anihpj.com:443)
                    │ :80 → :443  │  SSL Termination + Load Balancing
                    └──┬──┬──┬───┘
                       │  │  │  │
              ┌────────┘  │  │  └────────┐
              ▼           ▼  ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Gunicorn │ │ Gunicorn │ │ Gunicorn │
        │  :8001   │ │  :8002   │ │  :8003   │
        │ Worker 1 │ │ Worker 2 │ │ Worker 3 │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          │
                   ┌──────▼──────┐
                   │ PostgreSQL  │
                   │   :5432     │
                   └─────────────┘</pre></div>

            <table class="compare-table"><thead><tr><th>Load Balancing Method</th><th>How It Works</th><th>Best For</th><th>Example</th></tr></thead><tbody>
                <tr><td><strong>Round-Robin</strong> (default)</td><td>Requests distributed evenly in order: W1 → W2 → W3 → W1...</td><td>Stateless apps with similar server specs</td><td>General web apps, REST APIs</td></tr>
                <tr><td><strong>Least Connections</strong></td><td>Send to backend with fewest active connections</td><td>Requests with varying processing times</td><td>Long-lived WebSocket connections</td></tr>
                <tr><td><strong>IP Hash</strong></td><td>Hash of client IP determines backend. Same IP → same backend</td><td>Session stickiness without cookies</td><td>Shopping carts, login sessions</td></tr>
                <tr><td><strong>Weighted</strong></td><td>Backends given weight. weight=3 gets 3x traffic of weight=1</td><td>Heterogeneous servers (bigger server = more weight)</td><td>Canary deployments, A/B testing</td></tr>
                <tr><td><strong>Least Time</strong> (NGINX Plus)</td><td>Send to backend with lowest avg response time + fewest connections</td><td>Performance-sensitive apps</td><td>High-frequency trading, real-time APIs</td></tr>
            </tbody></table>

            <div class="split-panel">
                <div class="split-side split-good"><h5>✅ Nginx Upstream — Practical Anihpj Load Balancer</h5><pre><code># /etc/nginx/sites-available/anihpj
upstream anihpj_backend {
    # Round-robin (default) — distribute evenly
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;

    # Keep connections alive for reuse
    keepalive 32;
}

upstream anihpj_backend_weighted {
    # Weighted — bigger server gets more traffic
    server 127.0.0.1:8001 weight=3;  # 8-core machine
    server 127.0.0.1:8002 weight=1;  # 2-core machine
}

upstream anihpj_backend_ip_hash {
    # Sticky sessions — same client → same backend
    ip_hash;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 443 ssl;
    server_name anihpj.com;

    location / {
        proxy_pass http://anihpj_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts — prevents hanging connections
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }

    location /static/ {
        alias /var/www/anihpj/static/;
        expires 30d;
    }
}</code></pre></div>
                <div class="split-side split-bad"><h5>❌ Common Mistakes with Load Balancers</h5><pre><code># MISTAKE 1: No health checks — Nginx sends
# traffic to dead backends!
# FIX: Add health check parameters:
upstream anihpj_backend {
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    # After 3 failures in 30s, mark as DOWN
    # Tries again after 30s
}

# MISTAKE 2: Forgetting backup server
# FIX: Designate a backup for emergencies:
upstream anihpj_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003 backup;  # Only used
    # when ALL others are down
}

# MISTAKE 3: Sticky sessions without session store
# ip_hash breaks if clients change IPs (mobile)
# FIX: Use Redis-backed Django sessions instead</code></pre></div>
            </div>

            <div class="info-box tip"><h5>💡 Health Checks — Keep Traffic Off Broken Backends</h5><p><code>max_fails=N fail_timeout=T</code>: If a backend fails N times within T seconds, Nginx marks it as DOWN for T seconds, then retries. <strong>Anihpj setup:</strong> Each Gunicorn worker on a different port (8001/8002/8003) started by separate systemd units OR via Gunicorn's built-in <code>--workers 3</code>. <strong>Active health checks</strong> (NGINX Plus only): <code>health_check uri=/health interval=5s fails=2 passes=3;</code> — Nginx proactively pings /health endpoint. <strong>Passive health checks</strong> (NGINX OSS): Nginx detects failures from actual traffic. <strong>Debug:</strong> <code>curl -I http://127.0.0.1:8001/health</code> — manually check each backend before adding to upstream.</p></div>

            <div class="info-box note"><h5>🔬 Load Balancer vs Reverse Proxy — What's the Difference?</h5><p>A <strong>reverse proxy</strong> sits in front of ONE or MORE backends — its primary job is SSL termination, caching, and security. A <strong>load balancer</strong> is a type of reverse proxy whose PRIMARY job is distributing traffic across multiple backends for high availability and horizontal scaling. In practice, Nginx does both — every load balancer IS a reverse proxy, but not every reverse proxy configuration includes load balancing. <strong>LFCS exam tip:</strong> If the task says "configure a reverse proxy," set up proxy_pass to one backend. If it says "implement a load balancer," configure an upstream block with multiple servers.</p></div>

            <div class="diagram-container"><div class="diagram-title">Starting Multiple Gunicorn Workers for Load Balancing</div>
<pre>
  # Option A: Gunicorn manages workers internally
  # (Simpler — one systemd unit, Gunicorn forks workers)
  gunicorn anihpj.wsgi:application \
      --workers 3 \
      --bind 127.0.0.1:8000

  # Option B: Separate Gunicorn instances per port
  # (More control — isolate crashes, different configs)
  gunicorn anihpj.wsgi:application --bind 127.0.0.1:8001
  gunicorn anihpj.wsgi:application --bind 127.0.0.1:8002
  gunicorn anihpj.wsgi:application --bind 127.0.0.1:8003

  # Option B with systemd (production grade):
  # anihpj@.service (template unit)
  # systemctl start anihpj@8001 anihpj@8002 anihpj@8003</pre></div>
        </div>'''

# Insert s27-6 before the Ch27 visual summary
ch27_vs_marker = '        <div class="visual-summary"><h4>📊 Chapter 27 Visual Summary</h4><div class="vs-grid">\n'
if ch27_vs_marker in content and 'id="s27-6"' not in content:
    content = content.replace(ch27_vs_marker, lb_section + '\n' + ch27_vs_marker)
    changes += 1
    print("  ✅ Added s27-6: Nginx Load Balancer to Chapter 27")

# ============================================================
# FIX 5: Add sidebar entry for s27-6 in Chapter 27 sub-toc
# ============================================================
s27_sidebar_marker = '                            <li><a href="#s27-5">27.5 Apache2 Basics</a></li>\n'
s27_sidebar_new = '                            <li><a href="#s27-5">27.5 Apache2 Basics</a></li>\n                            <li><a href="#s27-6">27.6 Load Balancer Configuration</a></li>\n'
if s27_sidebar_marker in content and s27_sidebar_new not in content:
    content = content.replace(s27_sidebar_marker, s27_sidebar_new)
    changes += 1
    print("  ✅ Added s27-6 sidebar entry")

# ============================================================
# WRITE OUTPUT
# ============================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 Total changes made: {changes}")
print("Done!")
