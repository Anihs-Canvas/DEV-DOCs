import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# Fix 1: --set overrides
find1 = '<code>--set</code> overrides individual values inline. For nested keys, use dot notation: <code>--set service.port=8080</code>.'
yaml1 = '\n<pre>\n# Value Precedence (highest to lowest):\nhelm install app ./chart \\\n  --set image.tag=hotfix          # 1. HIGHEST - --set wins\n  -f values-prod.yaml             # 2. User values file\n  -f values-base.yaml             # 3. Earlier files lose to later ones\n\n# In values-prod.yaml:  replicaCount: 5    # overrides base\n# In values-base.yaml:  replicaCount: 3    # loses to prod\n#                       image.repository: nginx  # survives (not in prod)\n</pre>'

if find1 in html:
    pos = html.find(find1) + len(find1)
    end_p = html.find('</p>', pos)
    if end_p > 0:
        html = html[:end_p] + yaml1 + html[end_p:]
        changes += 1
        print("✓ Enriched: --set overrides")
else:
    print("✗ --set text not found")

# Fix 2: helm create scaffolds
find2 = '<code>helm create</code> scaffolds a complete chart with Chart.yaml, values.yaml, templates/, and helpers. On the exam, <strong>always use this</strong> — never start from an empty directory. Customize the generated files. Saves 5-10 minutes per chart task.'
yaml2 = '\n<pre>\nhelm create myapp\n# Creates:\nmyapp/\n├── Chart.yaml          # Metadata (apiVersion, name, version)\n├── values.yaml         # Default configuration values\n├── charts/             # Dependency charts go here\n├── templates/\n│   ├── deployment.yaml\n│   ├── service.yaml\n│   ├── hpa.yaml\n│   ├── ingress.yaml\n│   ├── serviceaccount.yaml\n│   ├── NOTES.txt       # Post-install message to users\n│   ├── _helpers.tpl    # Named reusable template blocks\n│   └── tests/\n│       └── test-connection.yaml\n└── .helmignore         # Files excluded from chart package\n\n# Exam tip: helm create + customize = fastest path to a valid chart\n</pre>'

if find2 in html:
    pos = html.find(find2) + len(find2)
    end_p = html.find('</p>', pos)
    if end_p > 0:
        html = html[:end_p] + yaml2 + html[end_p:]
        changes += 1
        print("✓ Enriched: helm create scaffold")
else:
    print("✗ helm create text not found")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nApplied {changes} additional enrichments.")
