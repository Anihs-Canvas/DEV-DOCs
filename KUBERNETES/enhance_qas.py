import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# The generic boilerplate to replace
generic = '<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a key Helm certification concept. The performance-based exam tests practical application — understanding <strong>why</strong> is as important as knowing <strong>how</strong>. Review the related chapter section for deeper context, diagrams, and hands-on practice drills.</p></div>'

# For each generic instance, we need to generate a replacement based on the question/answer context
# We'll find each generic and look at the preceding answer text to determine the topic

# Find all generic instances with their surrounding context
pattern = re.compile(
    r'(<span class="eq-number">(Q\d+|S\d+|P\d+)</span>.*?<div class="eq-answer">.*?<span class="eq-answer-label">Answer</span>\s*<p>(.*?)</p>\s*</div>\s*)' +
    re.escape(generic),
    re.DOTALL
)

matches = list(pattern.finditer(html))
print("Found {} generic boilerplates to enhance".format(len(matches)))

# Process in reverse to preserve positions
replacements_made = 0
for m in reversed(matches):
    full_match = m.group(0)
    eq_number = m.group(2)
    answer_text = m.group(3).strip()
    
    # Generate appropriate illustration based on the answer content
    # We'll look for key terms in the answer to determine what illustration to add
    
    illustration = ''
    
    # Detect topic from answer text
    answer_lower = answer_text.lower()
    
    if any(w in answer_lower for w in ['helm install', 'install command']):
        illustration = '<pre>\n# Standard install command:\nhelm install RELEASE ./chart -n NAMESPACE --create-namespace\n\n# Install with values file:\nhelm install RELEASE ./chart -f values.yaml -n NAMESPACE\n\n# Install with --set overrides:\nhelm install RELEASE ./chart --set image.tag=v2.0 -n NAMESPACE\n\n# Install with --atomic (auto-rollback on failure):\nhelm install RELEASE ./chart -n NAMESPACE --atomic --wait --timeout 5m\n</pre>'
    
    elif any(w in answer_lower for w in ['helm upgrade', 'upgrade command']):
        illustration = '<pre>\n# Standard upgrade:\nhelm upgrade RELEASE ./chart -n NAMESPACE\n\n# Upgrade with new values:\nhelm upgrade RELEASE ./chart -f values-new.yaml -n NAMESPACE\n\n# Upgrade-or-install (idempotent):\nhelm upgrade --install RELEASE ./chart -n NAMESPACE\n\n# Upgrade with auto-rollback:\nhelm upgrade RELEASE ./chart -n NAMESPACE --atomic --cleanup-on-fail\n</pre>'
    
    elif any(w in answer_lower for w in ['rollback', 'helm rollback']):
        illustration = '<pre>\n# Rollback to previous revision:\nhelm rollback RELEASE -n NAMESPACE\n\n# Rollback to specific revision:\nhelm rollback RELEASE 3 -n NAMESPACE\n\n# View history first:\nhelm history RELEASE -n NAMESPACE\n# 1  Tue Jan 15 10:00:00 2024  SUPERSEDED  anihpj-0.1.0  1.0.0  Install complete\n# 2  Tue Jan 15 10:30:00 2024  SUPERSEDED  anihpj-0.1.1  1.0.1  Upgrade complete\n# 3  Tue Jan 15 11:00:00 2024  FAILED      anihpj-0.2.0  2.0.0  Upgrade failed\n\n# Rollback creates a NEW revision:\nhelm rollback RELEASE 2 -n NAMESPACE\n# Creates revision 4 with config from revision 2\n</pre>'
    
    elif any(w in answer_lower for w in ['helm list', 'list command']):
        illustration = '<pre>\n# List releases in current namespace:\nhelm list\n\n# List ALL releases across ALL namespaces:\nhelm list -A\n\n# List only failed releases:\nhelm list -A --failed\n\n# List releases sorted by date:\nhelm list -A --date --reverse\n\n# List with specific filter:\nhelm list -n production --filter anihpj\n</pre>'
    
    elif any(w in answer_lower for w in ['chart.yaml', 'chart yaml']):
        illustration = '<pre>\n# Minimal valid Chart.yaml:\napiVersion: v2\nname: mychart\nversion: 0.1.0\ntype: application\n\n# Full Chart.yaml reference:\napiVersion: v2\nname: anihpj\nversion: 0.2.0\nappVersion: "2.1.0"\ndescription: A Helm chart for the anihpj job board application\ntype: application\nkubeVersion: ">=1.25.0-0"\nmaintainers:\n  - name: DevOps Team\n    email: devops@example.com\nicon: https://example.com/anihpj-icon.svg\nkeywords:\n  - django\n  - job-board\n  - python\n</pre>'
    
    elif any(w in answer_lower for w in ['values.yaml', 'values file', 'values yaml']):
        illustration = '<pre>\n# values.yaml with documented defaults:\nreplicaCount: 3\nimage:\n  repository: anihpj        # Docker image repository\n  tag: v2.0.0                # Image tag (pin in production!)\n  pullPolicy: IfNotPresent   # Image pull policy\n\nservice:\n  type: ClusterIP            # ClusterIP | NodePort | LoadBalancer\n  port: 80                   # Service port\n\ningress:\n  enabled: true              # Enable/disable Ingress resource\n  className: nginx           # Ingress class name\n  host: anihpj.example.com   # Ingress hostname\n  tls: true                  # Enable TLS\n\n# Access in templates: {{ .Values.replicaCount }}\n# Override: --set replicaCount=5\n</pre>'
    
    elif any(w in answer_lower for w in ['dependency', 'dependencies', 'subchart']):
        illustration = '<pre>\n# Chart.yaml with dependencies:\ndependencies:\n  - name: postgresql\n    version: "12.x.x"\n    repository: https://charts.bitnami.com/bitnami\n    condition: postgresql.enabled\n  - name: redis\n    version: "~18.0.0"\n    repository: https://charts.bitnami.com/bitnami\n    tags:\n      - cache\n\n# After adding deps, always run:\nhelm dependency update\n# Downloads .tgz to charts/ and creates Chart.lock\n\n# Then install (dependencies auto-included):\nhelm install myapp ./chart -n prod\n</pre>'
    
    elif any(w in answer_lower for w in ['hook', 'helm.sh/hook']):
        illustration = '<pre>\n# Hook annotations on a Job resource:\nmetadata:\n  annotations:\n    "helm.sh/hook": pre-upgrade          # Hook type\n    "helm.sh/hook-weight": "-5"          # Execution order\n    "helm.sh/hook-delete-policy": hook-succeeded\n\n# Available hook types:\n# pre-install, post-install, pre-upgrade, post-upgrade,\n# pre-delete, post-delete, pre-rollback, post-rollback, test\n\n# Weights: Lower numbers execute FIRST\n# Deletion policies: hook-succeeded, hook-failed, before-hook-creation\n</pre>'
    
    elif any(w in answer_lower for w in ['helm lint', 'lint', '--strict']):
        illustration = '<pre>\n# Validate chart structure and syntax:\nhelm lint ./chart --strict\n\n# Common lint checks:\n# - Chart.yaml has required fields (apiVersion, name, version)\n# - values.yaml is valid YAML\n# - Templates parse without errors\n# - Deprecated API versions flagged\n# - Missing required values detected\n\n# Debug workflow:\n# 1. helm lint --strict     (1 second, catches 80%)\n# 2. helm template --debug  (2 seconds, render check)\n# 3. helm install --dry-run (3 seconds, API validation)\n</pre>'
    
    elif any(w in answer_lower for w in ['helm test', 'test pod', 'test hook']):
        illustration = '<pre>\n# Run tests for a release:\nhelm test RELEASE -n NAMESPACE --logs\n\n# Test pod example:\napiVersion: v1\nkind: Pod\nmetadata:\n  name: {{ .Release.Name }}-test\n  annotations:\n    "helm.sh/hook": test\nspec:\n  containers:\n  - name: test\n    image: busybox\n    command: ["wget", "http://{{ .Release.Name }}-svc"]\n  restartPolicy: Never\n\n# Test lifecycle:\n# 1. helm install  → test pods NOT run\n# 2. helm test     → test pods run and report results\n# 3. Tests can be re-run anytime without affecting the release\n</pre>'
    
    elif any(w in answer_lower for w in ['template', 'include', 'define']):
        illustration = '<pre>\n# template vs include - Key Difference:\n\n# template: writes directly to output (NO piping)\n{{ template "mylib.labels" . }}\n\n# include: returns a string (CAN pipe through functions)\n{{ include "mylib.labels" . | nindent 4 }}\n{{ include "mylib.labels" . | quote }}\n\n# Named template definition:\n{{- define "anihpj.labels" -}}\napp.kubernetes.io/name: {{ .Chart.Name }}\napp.kubernetes.io/instance: {{ .Release.Name }}\n{{- end }}\n\n# Usage:\nmetadata:\n  labels:\n    {{- include "anihpj.labels" . | nindent 4 }}\n</pre>'
    
    elif any(w in answer_lower for w in ['oci', 'registry', 'helm push', 'helm pull']):
        illustration = '<pre>\n# OCI Chart Distribution:\n\n# Package the chart:\nhelm package ./anihpj-chart\n# Creates: anihpj-chart-0.1.0.tgz\n\n# Login to OCI registry:\nhelm registry login ghcr.io -u USERNAME\n\n# Push chart to OCI registry:\nhelm push anihpj-chart-0.1.0.tgz oci://ghcr.io/ORG/charts\n\n# Pull chart from OCI registry:\nhelm pull oci://ghcr.io/ORG/charts/anihpj-chart --version 0.1.0\n\n# Install directly from OCI:\nhelm install anihpj oci://ghcr.io/ORG/charts/anihpj-chart --version 0.1.0\n</pre>'
    
    elif any(w in answer_lower for w in ['--dry-run', 'dry run', 'dryrun']):
        illustration = '<pre>\n# Safe deployment workflow:\n\n# Step 1: Lint (1 second):\nhelm lint ./chart --strict\n\n# Step 2: Dry-run (3 seconds, no resources created):\nhelm install test ./chart --dry-run --debug\n\n# Step 3: Template render (local only):\nhelm template test ./chart --debug > rendered.yaml\n\n# Step 4: Review rendered output:\ncat rendered.yaml | less\n\n# Step 5: Actual install (only if all above pass):\nhelm install prod ./chart -f values-prod.yaml -n production --atomic\n</pre>'
    
    elif any(w in answer_lower for w in ['secret', 'sealed secret', 'sops', 'b64enc']):
        illustration = '<pre>\n# SECRETS MANAGEMENT PATTERNS:\n\n# NEVER do this:\n# values.yaml:\n#   password: mySecret123  ← COMMITTED TO GIT! DANGER!\n\n# INSTEAD, use --set at deploy time:\nhelm install app ./chart --set db.password="$DB_PASS" -n prod\n\n# Or use b64enc in templates:\ndata:\n  password: {{ .Values.db.password | b64enc }}\n\n# Or use Sealed Secrets / External Secrets Operator:\n# These encrypt secrets so they can be committed to Git safely\n</pre>'
    
    elif any(w in answer_lower for w in ['release', 'revision', 'version']):
        illustration = '<pre>\n# Release storage (per revision):\nkubectl get secrets -l owner=helm -n NAMESPACE\n# sh.helm.release.v1.anihpj.v1\n# sh.helm.release.v1.anihpj.v2\n# sh.helm.release.v1.anihpj.v3\n\n# Each Secret contains:\n# - Chart metadata (name, version)\n# - Computed values (all overrides merged)\n# - Rendered manifests (the actual YAML applied)\n# - Release info (status, timestamps)\n\n# Inspect a revision:\nkubectl get secret sh.helm.release.v1.anihpj.v2 -n prod -o jsonpath=\'{.data.release}\' | base64 -d | gzip -d | python -m json.tool\n</pre>'
    
    elif any(w in answer_lower for w in ['--atomic', 'atomic', '--wait', '--timeout']):
        illustration = '<pre>\n# Safety flags for production deployments:\n\n# --atomic: Auto-rollback if install/upgrade fails\nhelm install app ./chart --atomic -n production\n\n# --wait: Wait for all resources to be ready\nhelm install app ./chart --wait -n production\n\n# --timeout: Max time to wait (default 5m)\nhelm install app ./chart --timeout 10m -n production\n\n# --cleanup-on-fail: Remove new resources on failure\nhelm install app ./chart --atomic --cleanup-on-fail -n production\n\n# Production golden command:\nhelm upgrade --install app ./chart \\\n  -f values-prod.yaml \\\n  -n production \\\n  --atomic --wait --timeout 10m\n</pre>'
    
    elif any(w in answer_lower for w in ['namespace', '-n ']):
        illustration = '<pre>\n# Namespace best practices:\n\n# Create namespace on install:\nhelm install app ./chart -n myapp --create-namespace\n\n# Deploy same chart to multiple namespaces:\nhelm install app-dev ./chart -f values-dev.yaml -n dev\nhelm install app-stg ./chart -f values-stg.yaml -n staging\nhelm install app-prod ./chart -f values-prod.yaml -n production\n\n# List releases per namespace:\nhelm list -n dev\nhelm list -n staging\nhelm list -n production\n\n# Cross-namespace listing:\nhelm list -A | grep anihpj\n</pre>'
    
    elif any(w in answer_lower for w in ['helm get', 'helm status']):
        illustration = '<pre>\n# Inspect a deployed release:\n\n# Get rendered manifests:\nhelm get manifest RELEASE -n NAMESPACE\n\n# Get user-supplied values:\nhelm get values RELEASE -n NAMESPACE\n\n# Get ALL computed values (user + defaults):\nhelm get values RELEASE -n NAMESPACE --all\n\n# Get hooks:\nhelm get hooks RELEASE -n NAMESPACE\n\n# Get NOTES.txt output:\nhelm get notes RELEASE -n NAMESPACE\n\n# Current status:\nhelm status RELEASE -n NAMESPACE\n</pre>'
    
    elif any(w in answer_lower for w in ['uninstall', 'remove', 'delete']):
        illustration = '<pre>\n# Uninstall a release:\nhelm uninstall RELEASE -n NAMESPACE\n\n# Keep history for potential re-install:\nhelm uninstall RELEASE -n NAMESPACE --keep-history\n# Release status becomes "uninstalled" but history is preserved\n\n# Dry-run uninstall (see what would be deleted):\nhelm uninstall RELEASE -n NAMESPACE --dry-run\n\n# Cleanup workflow:\nhelm list -A --failed  # Find failed releases\nhelm uninstall RELEASE -n NAMESPACE  # Remove them\n</pre>'
    
    elif any(w in answer_lower for w in ['helm repo', 'repository']):
        illustration = '<pre>\n# Repository management:\n\n# Add a repository:\nhelm repo add bitnami https://charts.bitnami.com/bitnami\n\n# List configured repositories:\nhelm repo list\n\n# Update repository indexes:\nhelm repo update\n\n# Search for charts:\nhelm search repo nginx\nhelm search repo bitnami/ --versions\n\n# Remove a repository:\nhelm repo remove bitnami\n</pre>'
    
    elif any(w in answer_lower for w in ['helm create', 'scaffold', 'helm package']):
        illustration = '<pre>\n# Create a new chart scaffold:\nhelm create mychart\n\n# Created structure:\nmychart/\n├── Chart.yaml          # Chart metadata\n├── values.yaml         # Default configuration\n├── charts/             # Dependency charts\n├── templates/          # Template files\n│   ├── deployment.yaml\n│   ├── service.yaml\n│   ├── hpa.yaml\n│   ├── ingress.yaml\n│   ├── serviceaccount.yaml\n│   ├── NOTES.txt       # Post-install message\n│   ├── _helpers.tpl    # Reusable named templates\n│   └── tests/\n│       └── test-connection.yaml\n└── .helmignore         # Files excluded from package\n\n# Package for distribution:\nhelm package ./mychart\n# Creates: mychart-0.1.0.tgz\n</pre>'
    
    elif any(w in answer_lower for w in ['--reuse-values', '--reset-values']):
        illustration = '<pre>\n# --reuse-values vs --reset-values:\n\n# Scenario: First install with custom values\nhelm install app ./chart --set image.tag=v1.0 -n prod\n\n# Later, you want to upgrade only replicas:\n# --reuse-values keeps ALL previous --set values!\nhelm upgrade app ./chart --reuse-values --set replicaCount=5 -n prod\n# Result: image.tag STILL v1.0, replicaCount now 5\n\n# --reset-values discards ALL previous --set values:\nhelm upgrade app ./chart --reset-values -f values-v2.yaml -n prod\n# Result: ONLY values-v2.yaml + chart defaults used\n\n# Neither flag = previous --set values are STILL remembered!\n</pre>'
    
    elif any(w in answer_lower for w in ['--set', 'override', 'precedence']):
        illustration = '<pre>\n# Value Precedence (highest to lowest):\n# 1. --set / --set-string (command line)\n# 2. -f values files (last file wins)\n# 3. Parent chart values (for subcharts)\n# 4. values.yaml (chart defaults)\n# 5. Subchart values.yaml (lowest)\n\n# Example:\nhelm install app ./chart \\\n  -f values-base.yaml \\      # Priority 2b (earlier)\n  -f values-override.yaml \\  # Priority 2a (later, WINS)\n  --set image.tag=hotfix      # Priority 1 (HIGHEST)\n\n# Result: image.tag = "hotfix" (--set always wins)\n</pre>'
    
    else:
        # Generic illustration for any topic
        illustration = '<pre>\n# Key exam commands to remember:\nhelm lint ./chart --strict\nhelm template test ./chart --debug\nhelm install test ./chart --dry-run --debug\nhelm install prod ./chart -f values.yaml -n NAMESPACE --atomic --wait\nhelm list -A\nhelm history RELEASE -n NAMESPACE\nhelm get manifest RELEASE -n NAMESPACE\nhelm rollback RELEASE -n NAMESPACE\nhelm test RELEASE -n NAMESPACE --logs\n</pre>'
    
    # Build the new explanation
    new_explanation = '<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This concept is frequently tested on the Helm certification exam. The illustration below demonstrates the practical application with real commands and examples you can use directly in the exam terminal.</p>\n' + illustration + '\n</div>'
    
    # Replace the generic with the new illustrated explanation
    old_text = generic
    # Find the exact position of this specific generic instance
    gen_pos = html.find(generic, m.start())
    if gen_pos > 0:
        html = html[:gen_pos] + new_explanation + html[gen_pos + len(generic):]
        replacements_made += 1

print("Enhanced {} generic explanations with illustrations".format(replacements_made))

# Save
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)
print("\nSaved. Lines: {}".format(html.count('\n')))
