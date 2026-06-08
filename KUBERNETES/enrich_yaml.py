import re
import sys

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

original = html
changes = 0

# Define enrichment map: (unique_text_to_find, yaml_block_to_append_before_closing_p)
enrichments = [
    # 1. Hooks test explanation
    (
        'Test hooks are annotated with <code>"helm.sh/hook": test</code>. They run on demand, not automatically. This separates validation from deployment',
        '\n<pre>\n# Test hook pod template:\nmetadata:\n  annotations:\n    "helm.sh/hook": test           # Only runs with helm test\n    "helm.sh/hook-delete-policy": before-hook-creation\nspec:\n  containers:\n  - name: test\n    command: ["curl", "http://myapp-service/smoke"]\n  restartPolicy: Never\n\n# Test command: helm test my-release -n prod --logs\n</pre>'
    ),
    # 2. Release secrets
    (
        'Each release revision creates one Secret: <code>sh.helm.release.v1.&lt;name&gt;.v&lt;rev&gt;</code>. These Secrets contain the chart, values (including secrets!), and rendered manifests.',
        '\n<pre>\n# View release secrets:\nkubectl get secrets -l owner=helm -n prod\n# NAME                               TYPE     DATA\n# sh.helm.release.v1.anihpj.v1     helm.sh/release.v1   1\n# sh.helm.release.v1.anihpj.v2     helm.sh/release.v1   1\n\n# Inspect revision:\nkubectl get secret sh.helm.release.v1.anihpj.v2 -n prod -o jsonpath=\'{.data.release}\' | base64 -d | gzip -d | jq .\n# Output: {\"name\":\"anihpj\",\"chart\":{...},\"config\":{...},\"manifest\":\"---\\napiVersion: apps/v1...\"}\n</pre>'
    ),
    # 3. --set overrides
    (
        '<code>--set</code> overrides individual values inline. For nested keys, use dot notation: <code>--set service.port=8080</code>. These take highest precedence over ALL other value sources.',
        '\n<pre>\n# Value Precedence (highest to lowest):\nhelm install app ./chart \\\n  --set image.tag=hotfix          # 1. HIGHEST - --set wins\n  -f values-prod.yaml             # 2. User values file\n  -f values-base.yaml             # 3. Earlier files lose to later ones\n\n# In values-prod.yaml:\nreplicaCount: 5        # overrides base\n# In values-base.yaml:\nreplicaCount: 3        # loses to prod\nimage:\n  repository: nginx    # survives if not in prod\n</pre>'
    ),
    # 4. Minimal Chart.yaml
    (
        'The exam may ask you to create a minimal valid Chart.yaml. The absolute minimum is apiVersion, name, and version. However, always include <code>type: application</code> for clarity.',
        '\n<pre>\n# Minimal valid Chart.yaml:\napiVersion: v2\nname: myapp\nversion: 0.1.0\ntype: application\n\n# Full-featured example:\napiVersion: v2\nname: anihpj\nversion: 0.2.0\nappVersion: "2.1.0"\nicon: https://example.com/icon.svg\ntype: application\nmaintainers:\n  - name: DevOps Team\n    email: devops@anihpj.com\n</pre>'
    ),
    # 5. upgrade --install golden command
    (
        'This is the "golden command" — installs if new, upgrades if exists, auto-rolls back on failure.',
        '\n<pre>\n# Gold Standard Exam Command:\nhelm upgrade --install anihpj ./chart \\\n  --namespace prod \\\n  --create-namespace \\\n  --values values-prod.yaml \\\n  --set image.tag=v2.0 \\\n  --atomic \\\n  --timeout 5m \\\n  --wait \\\n  --debug     # Always add --debug on exam!\n\n# --atomic:    Auto rollback on failure\n# --wait:      Wait for all pods ready\n# --debug:     Shows rendered templates\n# --timeout:   Prevents hanging\n</pre>'
    ),
    # 6. Helm create scaffold
    (
        '<code>helm create</code> scaffolds a complete chart with Chart.yaml, values.yaml, templates/, and helpers. On the exam, this saves 10-15 minutes.',
        '\n<pre>\nhelm create myapp\n# Creates:\nmyapp/\n├── Chart.yaml          # Metadata\n├── values.yaml         # Defaults\n├── charts/             # Dependencies\n├── templates/\n│   ├── deployment.yaml\n│   ├── service.yaml\n│   ├── hpa.yaml\n│   ├── ingress.yaml\n│   ├── serviceaccount.yaml\n│   ├── NOTES.txt       # Post-install message\n│   ├── _helpers.tpl    # Named templates\n│   └── tests/\n│       └── test-connection.yaml\n└── .helmignore         # Exclude patterns\n\n# Exam: helm create + customize = fastest path\n</pre>'
    ),
    # 7. Release history secrets
    (
        'This Secret contains the chart metadata, values used, and the rendered manifests. This is how Helm tracks release history and enables rollbacks.',
        '\n<pre>\n# Secret structure:\napiVersion: v1\nkind: Secret\nmetadata:\n  name: sh.helm.release.v1.anihpj.v3\n  labels:\n    owner: helm\n    name: anihpj\n    version: "3"\ntype: helm.sh/release.v1\ndata:\n  release: &lt;gzipped+base64 JSON&gt;\n\n# JSON payload: {\"name\":\"anihpj\",\"info\":{\"status\":\"deployed\"},\n#   \"chart\":{...},\"config\":{...},\"manifest\":\"...\",\"version\":3}\n</pre>'
    ),
    # 8. Helm lint debugging workflow
    (
        '<code>helm lint ./chart --strict</code>. Catches 80%',
        '\n<pre>\n# Debugging Pyramid (fastest → most thorough):\nhelm lint ./chart --strict           # 1s  - syntax/structural errors\nhelm template ./chart --debug        # 2s  - rendering errors\nhelm install test ./chart --dry-run --debug  # 3s - API validation\nhelm install prod ./chart -f values.yaml --atomic --wait  # REAL\n\n# Always run lint first on the exam!\n</pre>'
    ),
]

for find_text, yaml_block in enrichments:
    if find_text in html:
        # Find the closing </p> after this text
        pos = html.find(find_text)
        if pos > 0:
            end_p = html.find('</p>', pos + len(find_text))
            if end_p > 0:
                # Insert YAML block before </p>
                html = html[:end_p] + yaml_block + html[end_p:]
                changes += 1
                print(f"✓ Enriched: {find_text[:60]}...")
            else:
                print(f"✗ No </p> found for: {find_text[:60]}...")
        else:
            print(f"✗ Position error for: {find_text[:60]}")
    else:
        print(f"✗ NOT FOUND: {find_text[:60]}...")

# Check for remaining generic boilerplate duplicates
boilerplate = '<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a key Helm certification concept.'
count = html.count(boilerplate)
print(f"\nGeneric boilerplate blocks remaining: {count}")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nApplied {changes} enrichments. File updated.")
else:
    print("\nNo changes made.")
