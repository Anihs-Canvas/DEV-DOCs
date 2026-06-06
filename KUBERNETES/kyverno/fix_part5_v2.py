"""Fix 5.5 — corrected whitespace match"""

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old_55_end = '''└─────────────────────────────────────────────────────────────────────┘</div>
            </div>
            <div class="info">
                <strong>💡 IPVS Mode Alternative:</strong>'''

new_55_end = '''└─────────────────────────────────────────────────────────────────────┘</div>
            </div>

            <div class="highlight-box">
                <strong>🧠 Why Probability Mode? The Math Behind iptables Load Balancing:</strong> iptables rules are evaluated sequentially — there is no hash table or round-robin counter. To achieve statistically even distribution across 3 endpoints, kube-proxy writes rules with carefully calculated probabilities:
                <ul style="margin-top:8px;">
                    <li><strong>Endpoint 1 (wk-03):</strong> probability 0.33333333 — 1/3 of traffic matches and gets DNAT'd to <code class="inline">10.244.3.45:8080</code></li>
                    <li><strong>Endpoint 2 (wk-04):</strong> probability 0.50000000 — of the remaining 66.7%, half (33.3%) goes to <code class="inline">10.244.4.72:8080</code></li>
                    <li><strong>Endpoint 3 (wk-05):</strong> probability 1.00000000 — all remaining traffic (33.3%) goes to <code class="inline">10.244.5.18:8080</code></li>
                </ul>
                This gives statistically even load distribution <strong>without needing a separate load balancer process</strong>. The trade-off: every packet evaluates O(n) iptables rules where n = number of endpoints.
            </div>

            <div class="warning">
                <strong>⚠️ iptables Scalability Ceiling:</strong> For 100 Services with 5 endpoints each: <strong>~6,000 iptables rules</strong>. For 5,000 Services: <strong>hundreds of thousands</strong> of rules. iptables evaluates rules sequentially (O(n)), so adding a new Service gets progressively slower. This is why iptables mode doesn't scale past <strong>~5,000 Services</strong> — IPVS mode uses a kernel hash table instead, which is O(1) vs O(n). For the anihpj cluster (well under 1,000 Services), iptables mode is perfectly fine.
            </div>

            <div class="info">
                <strong>💡 IPVS Mode Alternative:</strong>'''

if old_55_end in html:
    html = html.replace(old_55_end, new_55_end)
    print("FIX 5.5: Probability bullet points + scalability numbers inserted SUCCESSFULLY")
else:
    print("FIX 5.5: String NOT FOUND — checking for partial match...")
    # fallback: try to find just the closing ascii block
    fallback = '└─────────────────────────────────────────────────────────────────────┘</div>'
    idx = html.find(fallback)
    if idx > 0:
        print(f"Fallback: found at index {idx}")
        # Show context
        print("Context around match:")
        print(repr(html[idx+len(fallback):idx+len(fallback)+150]))
    else:
        print("Fallback also failed")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nFinal: {html.count(chr(10))} lines')
