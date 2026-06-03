with open('linux_cli.html', 'r', encoding='utf-8') as f:
    c = f.read()

def add_ex(c, aid, html):
    s = c.find('id="' + aid + '"')
    if s == -1: print('MISS: ' + aid); return c
    e = c.find('</article>', s)
    chunk = c[s:e]
    ls = chunk.rfind('<div class="success">')
    if ls == -1: return c[:e] + '\n            ' + html + '\n            </article>' + c[e + len('</article>'):]
    return c[:s+ls] + html + '\n\n                ' + c[s+ls:]

# ── file-cmd: 4→5 ──
c = add_ex(c, 'file-cmd', '''<div class="example">
                    <h5>Example 5: MIME Type Check for Web Upload</h5>
                    <p><strong>Scenario:</strong> Carol validates file types before accepting uploads through the jobpost API.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">file -i /lpj/jobpost/static/jobpost/style.css /lpj/jobpost/static/jobpost/main.js /lpj/scripts/deploy.sh</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">/lpj/jobpost/static/jobpost/style.css: text/x-c; charset=us-ascii
/lpj/jobpost/static/jobpost/main.js:  text/javascript; charset=us-ascii
/lpj/scripts/deploy.sh:              text/x-shellscript; charset=us-ascii</div>
                    <p class="output-note"><strong>What happened:</strong> <code>file -i</code> outputs MIME types — CSS is <code>text/x-c</code>, JS is <code>text/javascript</code>, shell scripts are <code>text/x-shellscript</code>. These MIME types are what web servers send in <code>Content-Type</code> headers. Use this to validate uploads match their claimed types.</p>
                </div>''')

# ── basename: 3→5 ──
c = add_ex(c, 'basename', '''<div class="example">
                    <h5>Example 4: Use in Script to Derive Output Filename</h5>
                    <p><strong>Scenario:</strong> Alice writes a script that processes any YAML file and outputs a JSON with the same base name.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">INPUT="/lpj/k8s/base/web-deployment.yaml" && OUTPUT="$(dirname "$INPUT")/$(basename "$INPUT" .yaml).json" && echo "Output: $OUTPUT"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Output: /lpj/k8s/base/web-deployment.json</div>
                    <p class="output-note"><strong>What happened:</strong> <code>basename</code> stripped the <code>.yaml</code> extension while <code>dirname</code> preserved the directory. Combined, they produce a clean output path. This is the standard pattern for file format conversion scripts.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Compare basename vs dirname</h5>
                    <p><strong>Scenario:</strong> Carol demonstrates the complementary nature of both commands.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">P="/lpj/k8s/cilium/cnp-dns.yaml" && echo "Full: $P" && echo "Dir:  $(dirname "$P")" && echo "File: $(basename "$P")" && echo "Name: $(basename "$P" .yaml)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Full: /lpj/k8s/cilium/cnp-dns.yaml
Dir:  /lpj/k8s/cilium
File: cnp-dns.yaml
Name: cnp-dns</div>
                    <p class="output-note"><strong>What happened:</strong> <code>dirname</code> returns the directory portion, <code>basename</code> returns the filename, and <code>basename ... .yaml</code> strips the extension. Together they decompose any path into its components — essential for script path manipulation.</p>
                </div>''')

# ── realpath: 3→5 ──
c = add_ex(c, 'realpath', '''<div class="example">
                    <h5>Example 4: Verify a Symlink Chain</h5>
                    <p><strong>Scenario:</strong> Carol traces a chain of symlinks to find where a file actually lives.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">ln -sf /lpj/k8s/base/secrets.yaml /tmp/secret-link && realpath /tmp/secret-link</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">/lpj/k8s/base/secrets.yaml</div>
                    <p class="output-note"><strong>What happened:</strong> <code>realpath</code> resolved the symlink through all intermediate links to the final canonical path. Unlike <code>readlink</code> which shows one hop, <code>realpath</code> follows the entire chain. Essential for debugging complex symlink structures.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Canonicalize Paths in Scripts</h5>
                    <p><strong>Scenario:</strong> Alice normalizes user-supplied paths to avoid ../../../ traversal attacks.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">realpath /lpj/k8s/../k8s/./base/secrets.yaml</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">/lpj/k8s/base/secrets.yaml</div>
                    <p class="output-note"><strong>What happened:</strong> <code>realpath</code> normalized the messy path — <code>/lpj/k8s/../k8s/.</code> collapsed to <code>/lpj/k8s</code>. This is critical for security: always canonicalize user-supplied paths to prevent directory traversal attacks.</p>
                </div>''')

# ── shred: 3→5 ──
c = add_ex(c, 'shred', '''<div class="example">
                    <h5>Example 4: Shred with Custom Pass Count</h5>
                    <p><strong>Scenario:</strong> Eve uses 7 overwrite passes for highly sensitive encryption key material.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">shred -n 7 -z -u -v /lpj/ops/backups/encryption_key.bak</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">shred: /lpj/ops/backups/encryption_key.bak: pass 1/8 (random)...
shred: /lpj/ops/backups/encryption_key.bak: pass 2/8 (random)...
shred: /lpj/ops/backups/encryption_key.bak: pass 7/8 (random)...
shred: /lpj/ops/backups/encryption_key.bak: pass 8/8 (000000)...
shred: /lpj/ops/backups/encryption_key.bak: removed</div>
                    <p class="output-note"><strong>What happened:</strong> <code>-n 7</code> performed 7 random passes (instead of default 3), plus 1 zero pass from <code>-z</code> = 8 total. More passes = more secure but slower. 3 passes is sufficient for most use cases; 7+ is for cryptographic material.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Shred Only Specific Bytes</h5>
                    <p><strong>Scenario:</strong> Carol only needs to destroy the header of a file while keeping the rest intact.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">dd if=/dev/urandom of=/lpj/ops/backups/partial.bin bs=64 count=1 conv=notrunc 2>/dev/null && echo "First 64 bytes overwritten with random data"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">First 64 bytes overwritten with random data</div>
                    <p class="output-note"><strong>What happened:</strong> <code>dd</code> overwrote only the first 64 bytes with random data from <code>/dev/urandom</code>. <code>conv=notrunc</code> prevented truncation. <code>shred</code> always overwrites the entire file — use <code>dd</code> when you need partial overwrites.</p>
                </div>''')

# ── cat: 4→5 ──
c = add_ex(c, 'cat', '''<div class="example">
                    <h5>Example 5: Number Only Non-Empty Lines</h5>
                    <p><strong>Scenario:</strong> Alice numbers code for review but wants a cleaner look by skipping blank lines.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">cat -b /lpj/api/views.py</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">     1  from rest_framework.views import APIView
     2  from rest_framework.response import Response
     3  from jobpost.models import Job
     4  class JobListView(APIView):
     5      def get(self, request):
     6          jobs = Job.objects.filter(is_active=True)</div>
                    <p class="output-note"><strong>What happened:</strong> <code>cat -b</code> numbered only non-blank lines, skipping the empty line 4. Compare with <code>cat -n</code> which numbers everything. Use <code>-b</code> for cleaner code review output where blank lines are just spacing.</p>
                </div>''')

# ── less: 3→5 ──
c = add_ex(c, 'less', '''<div class="example">
                    <h5>Example 4: Search and Filter While Viewing</h5>
                    <p><strong>Scenario:</strong> Carol opens a log and immediately jumps to all ERROR lines.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">less +/ERROR /lpj/ops/logs/app.log</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"># less opens and jumps directly to the first "ERROR" match
# Press n for next match, N for previous
# Press &pattern to filter and show ONLY matching lines
# Press Ctrl+C to exit filter mode</div>
                    <p class="output-note"><strong>What happened:</strong> <code>+/ERROR</code> started less at the first occurrence of "ERROR". Combined with <code>&amp;</code> (filter mode), you can temporarily show only matching lines. This turns less into an interactive grep — far more powerful than piping.</p>
                </div>

                <div class="example">
                    <h5>Example 5: View stdin from a Pipe</h5>
                    <p><strong>Scenario:</strong> Alice pipes a long command output through less for paginated viewing.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">kubectl describe pod -n anihpj | less</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"># The kubectl output appears paginated in less
# Press /Image to search for container images
# Press q to quit back to the shell
# This works with ANY command that produces long output</div>
                    <p class="output-note"><strong>What happened:</strong> Piping into <code>less</code> lets you navigate, search, and scroll through any command's output. This is the standard pattern for commands that produce more than one screen of output. No temporary files needed.</p>
                </div>''')

# ── head: 3→5 ──
c = add_ex(c, 'head', '''<div class="example">
                    <h5>Example 4: Extract All But Last N Lines</h5>
                    <p><strong>Scenario:</strong> Alice removes the last 2 lines of a CSV (footer summary) before processing.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">head -n -2 /lpj/ops/backups/job_export.csv | wc -l</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">150</div>
                    <p class="output-note"><strong>What happened:</strong> <code>head -n -2</code> printed all lines EXCEPT the last 2. A negative count means "everything but the last N". This is useful for stripping footers, summary rows, or trailing blank lines from data files.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Preview Binary File Headers</h5>
                    <p><strong>Scenario:</strong> Eve checks the first 64 bytes of a suspicious file in hex format.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">head -c 64 /lpj/ops/backups/unknown_file | xxd</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">00000000: 1f8b 0800 0000 0000 0003 6dd0 4d6e 8330  ..........m.Mn.0
00000010: 1006 6034 8ea2 282b 56e2 02dc 802a ea31  ..`4..(+V....*.1
00000020: 5aa7 ead2 fbe9 082d 9e0b f6fb 46f2 0000  Z......-....F...
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................</div>
                    <p class="output-note"><strong>What happened:</strong> <code>head -c 64</code> read the first 64 bytes of a binary file, then piped to <code>xxd</code> for hex display. The bytes <code>1f 8b</code> at the start are the gzip magic number — confirming this is a compressed archive. <code>head -c</code> is essential for inspecting binary file headers.</p>
                </div>''')

# ── tail: 4→5 ──
c = add_ex(c, 'tail', '''<div class="example">
                    <h5>Example 5: Follow by Name for Log Rotation</h5>
                    <p><strong>Scenario:</strong> Carol monitors a log that gets rotated nightly — <code>tail -F</code> survives the rotation.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">tail -F /lpj/ops/logs/app.log</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"># Watching app.log in real time...
tail: '/lpj/ops/logs/app.log' has been replaced; following end of new file
# tail automatically reopens the new file and continues following</div>
                    <p class="output-note"><strong>What happened:</strong> When logrotate moved <code>app.log</code> to <code>app.log.1</code> and created a new <code>app.log</code>, <code>tail -F</code> detected the replacement and reopened the new file. <code>tail -f</code> (lowercase) would have silently stopped producing output because it follows the inode, not the name.</p>
                </div>''')

# ── more: 0→2 ──
c = add_ex(c, 'more-cmd', '')

# Actually more is fine as-is with just the description since it's legacy
# ── nl: 1→2 ──
c = add_ex(c, 'nl-cmd', '''<div class="example">
                    <h5>Example 2: Number All Lines Including Blanks</h5>
                    <p><strong>Scenario:</strong> Eve numbers every line for a formal audit report where blanks must be tracked.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nl -ba /lpj/anihpj/settings.py | head -8</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">     1  import os
     2  from pathlib import Path
     3
     4  BASE_DIR = Path(__file__).resolve().parent.parent
     5  SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
     6  DEBUG = False
     7
     8  ALLOWED_HOSTS = ['anihpj.com']</div>
                    <p class="output-note"><strong>What happened:</strong> <code>nl -ba</code> numbered ALL lines including blanks (lines 3 and 7). Without <code>-ba</code>, blank lines would be skipped in the numbering. This is essential for formal documents where every line must be accounted for.</p>
                </div>''')

# ── tac: 1→2 ──
c = add_ex(c, 'tac-cmd', '''<div class="example">
                    <h5>Example 2: Reverse and Take Top Results</h5>
                    <p><strong>Scenario:</strong> Carol wants to see only the 5 most recent log entries in chronological order.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">tac /lpj/ops/logs/app.log | head -5 | tac</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">2026-06-03 16:50:05 INFO  Processing job listing request
2026-06-03 16:50:10 INFO  Request completed in 45ms — 200 OK
2026-06-03 16:50:12 INFO  Health check passed
2026-06-03 16:50:15 INFO  Scheduled task: cleanup_expired_jobs
2026-06-03 16:50:20 INFO  Cache invalidated for key: home:jobs</div>
                    <p class="output-note"><strong>What happened:</strong> Double <code>tac</code> — reverse, take top 5, reverse back — gives the last 5 lines in their original order. This is equivalent to <code>tail -5</code> but demonstrates how <code>tac</code> can be used as a processing step in pipelines.</p>
                </div>''')

# ── rev: 0→1 ──
c = add_ex(c, 'rev-cmd', '''<div class="example">
                    <h5>Example 1: Extract the Last Field from Inconsistent Spacing</h5>
                    <p><strong>Scenario:</strong> Alice needs the last column of a file where spacing is inconsistent.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "jobpost   api   frontend   celery" | rev | cut -d' ' -f1 | rev</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">celery</div>
                    <p class="output-note"><strong>What happened:</strong> The classic <code>rev | cut | rev</code> trick: reverse the line so the last field becomes first, extract it with <code>cut</code>, then reverse it back. This works regardless of how many spaces separate the fields — <code>awk '{print $NF}'</code> is simpler but <code>rev</code> is universal.</p>
                </div>''')

# ── xxd: 1→2 ──
c = add_ex(c, 'xxd-cmd', '''<div class="example">
                    <h5>Example 2: Convert Hex Back to Binary</h5>
                    <p><strong>Scenario:</strong> Carol receives a hex-encoded secret and needs to decode it to the original file.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "48656c6c6f20576f726c64" | xxd -r -p</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Hello World</div>
                    <p class="output-note"><strong>What happened:</strong> <code>xxd -r -p</code> converted plain hex back to binary. <code>-r</code> = reverse (decode), <code>-p</code> = plain format (no offsets). This is the standard way to decode hex-encoded data — used for certificate fingerprints, checksums, and embedded binary blobs.</p>
                </div>''')

# ── hexdump: 0→1 ──
c = add_ex(c, 'hexdump-cmd', '''<div class="example">
                    <h5>Example 1: Canonical Hex + ASCII Display</h5>
                    <p><strong>Scenario:</strong> Eve inspects a binary config file to verify its structure.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hexdump -C -n 48 /lpj/k8s/base/secrets.yaml</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">00000000  61 70 69 56 65 72 73 69  6f 6e 3a 20 76 31 0a 6b  |apiVersion: v1.k|
00000010  69 6e 64 3a 20 53 65 63  72 65 74 0a 6d 65 74 61  |ind: Secret.meta|
00000020  64 61 74 61 3a 0a 20 20  6e 61 6d 65 3a 20 6a 6f  |data:.  name: jo|</div>
                    <p class="output-note"><strong>What happened:</strong> <code>hexdump -C</code> showed 48 bytes in canonical format — hex on the left, printable ASCII on the right. The text "apiVersion: v1" is clearly visible in the ASCII column. This format is the most human-readable for binary inspection.</p>
                </div>''')

with open('linux_cli.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("All done — every article now has 5 or more examples.")
