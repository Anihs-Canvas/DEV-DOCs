"""Enrich argo.html explanations with skeletal ASCII diagrams."""
import re

with open('argo.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── Compact diagram templates ──
def diagram(title, art):
    return f'<div class="diagram-container" style="margin:12px 0;padding:14px 18px;"><div class="diagram-title">🔍 {title}</div><pre>{art}</pre></div>'

DIAGRAMS = {
    "gitops": diagram("GITOPS PRINCIPLES",
        "┌──────────┐   watch   ┌──────────┐   sync   ┌──────────┐\n│ Git Repo │─────────▶│ Argo CD  │─────────▶│ Cluster  │\n│ (Truth)  │          │ (Agent)  │          │ (Actual) │\n└──────────┘          └──────────┘          └──────────┘\n     ▲                                           │\n     └──────── git revert = rollback ────────────┘"),
    "push-pull": diagram("PUSH vs PULL",
        "PUSH:  CI Server ──kubectl──▶ Cluster  ⚠️ external creds\nPULL:  Git ◀── CI ──▶ Git ──▶ ArgoCD ──▶ Cluster ✅ safe"),
    "argo-projects": diagram("4 ARGO PROJECTS",
        "┌────────────┬────────────────────────────────┐\n│ Argo CD    │ GitOps Continuous Delivery      │\n│ Workflows  │ DAG/Steps Pipeline Engine       │\n│ Rollouts   │ Canary & Blue-Green Deploy      │\n│ Events     │ 20+ Event-Driven Triggers       │\n└────────────┴────────────────────────────────┘"),
    "k8s": diagram("K8s CONTROL PLANE",
        "┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐\n│API Server│  │   etcd   │  │ Scheduler │  │Controller-Mgr│\n└────┬─────┘  └──────────┘  └─────┬─────┘  └──────┬─────┘\n     └──────────────┬───────────────┬──────────────┘\n                    ▼\n              All via API Server"),
    "reconcile": diagram("RECONCILE LOOP",
        "┌──────────┐    ┌──────────┐    ┌──────────┐\n│ OBSERVE  │───▶│   DIFF   │───▶│   ACT    │\n│(current) │    │(compare) │    │(fix it)  │\n└──────────┘    └──────────┘    └────┬─────┘\n       ◀─────────────────────────────┘"),
    "crd": diagram("CRDs EXTEND K8s",
        "K8s Built-in: Pod | Service | Deployment | ConfigMap\n    +\nArgo CRDs: Application | Workflow | Rollout | Sensor\n    =\nK8s now understands GitOps resources!"),
    "docker": diagram("DOCKER LAYERS",
        "Layer 5: App Code      ← changes often (small)\nLayer 4: pip install     \nLayer 3: apt-get deps    \nLayer 2: Python 3.11     \nLayer 1: Ubuntu Base     ← rarely changes (big)"),
    "labels": diagram("LABELS CONNECT RESOURCES",
        "Service (selector: app=jobpost)\n   │\n   ├──▶ Pod-1 (labels: app=jobpost)\n   ├──▶ Pod-2 (labels: app=jobpost)\n   └──▶ Pod-3 (labels: app=jobpost)"),
    "namespace": diagram("NAMESPACES",
        "┌──── anihpj ────┐  ┌──── argocd ────┐\n│ Pods │ Svc │ CM│  │ArgoCD│Redis│Repo│\n└────────────────┘  └────────────────┘\nVirtual clusters in one physical cluster"),
    "yaml": diagram("YAML RULES",
        "✅ CORRECT:           ❌ WRONG:\nspec:                 spec:\n  containers:         \tcontainers:  ← TABS!\n    - name: app           - name: app\n      image: nginx          image: nginx\n2 SPACES per level. NEVER tabs."),
    "git": diagram("GIT BRANCHING",
        "main    ──●────●────●──  (production)\n          \    \nstaging   ──●────●────●  (auto-sync)\nfeature   ──●──●──●      (short-lived)"),
    "application": diagram("ARGO CD APPLICATION",
        "Application = Source + Destination + Sync Policy\n┌──────────┐     ┌──────────────┐     ┌──────────┐\n│ Git Repo │────▶│ Argo CD App  │────▶│ Cluster  │\n│ (source) │     │  (bridge)    │     │ (target) │\n└──────────┘     └──────────────┘     └──────────┘"),
    "sync": diagram("SYNC POLICIES",
        "Manual:    Git → (wait) → Click Sync\nAuto:      Git → ArgoCD auto-syncs\nSelf-Heal: ANY drift auto-corrected"),
    "health": diagram("SYNC vs HEALTH",
        "Sync:   Synced ✅ | OutOfSync ⚠️\nHealth: Healthy ✅ | Progressing ⏳ | Degraded ❌\nCan be Synced+Degraded OR OutOfSync+Healthy"),
    "workflow": diagram("WORKFLOW ANATOMY",
        "Entrypoint → Step A → Step B → Step C\n                 │          │\n                 └──▶ Step D ◀──┘\nEach step = 1 K8s Pod | Artifacts via S3/MinIO"),
    "dag-steps": diagram("DAG vs STEPS",
        "Steps: [A,B](∥) → [C](seq) → [D,E](∥)\nDAG:   A ──┐       B ──┐\n          ├──▶ C ──▶ D\n       no dep          ┘"),
    "template": diagram("TEMPLATE TYPES",
        "Container │ Script │ Resource │ Steps │ DAG\nSuspend    │ HTTP   │ Plugin   │ templateRef\nEach solves a different use case"),
    "artifact": diagram("ARTIFACT PASSING",
        "Step A ──upload──▶ [MinIO/S3] ──download──▶ Step B\noutputs.artifacts:              inputs.artifacts:\n  - name: data                   - name: data\n    path: /tmp/data.json           from: {{steps.A...}}"),
    "parameter": diagram("PARAMETER FLOW",
        "argo submit -p key=value\n       │\n       ▼\nWorkflow: {{workflow.parameters.key}}\n       │\nStep A → outputs.parameters.result\n       │\nStep B: {{steps.A.outputs.parameters.result}}"),
    "loop": diagram("LOOP TYPES",
        "withSequence: [0][1][2] (numeric range)\nwithItems: [dev,stg,prod] (static list)\nwithParam: dynamic from step output ⭐"),
    "retry": diagram("RETRY + BACKOFF",
        "Attempt 1 ❌ → 10s → Attempt 2 ❌ → 20s → Attempt 3 ✅\nbackoff: duration:10s factor:2 maxDuration:1h\nonExit: ALWAYS runs (cleanup/notify)"),
    "cron": diagram("CRONWORKFLOW",
        "schedule: '0 2 * * *' (daily 2 AM)\nconcurrencyPolicy:\n  Forbid  = skip if prev running\n  Replace = kill old, start new\n  Allow   = run in parallel"),
    "canary": diagram("CANARY DEPLOYMENT",
        "Stable v1 (90%) ──▶ Users\nCanary v2 (10%) ──▶ Users\nSteps: 10%→pause→50%→pause→100%\nAnalysis at each step: Fail → Auto Rollback"),
    "blue-green": diagram("BLUE-GREEN",
        "BEFORE: Blue(v1) 100% | Green(v2) idle\nAFTER:  Blue(v1) idle  | Green(v2) 100%\nInstant rollback: switch Service back"),
    "rollout": diagram("ROLLOUT ANATOMY",
        "┌──────── Rollout ─────────┐\n│ Stable RS(v1) │ Canary RS(v2) │\n│ Stable Svc    │ Canary Svc    │\n└────────────────────────────┘\nController manages both RS + both Svcs"),
    "analysis": diagram("ANALYSIS TEMPLATE",
        "Metrics: Prometheus | Datadog | Web | Job\n┌──────────────────────────────┐\n│ error-rate<1% AND p95<500ms │ → PASS\n│           FAIL → Rollback    │\n└──────────────────────────────┘"),
    "events": diagram("ARGO EVENTS",
        "EventSource ──▶ EventBus(NATS) ──▶ Sensor ──▶ Trigger\n(GitHub/S3)      (pub/sub)         (filter)     (Workflow)\n20+ EventSources available"),
    "sensor": diagram("SENSOR DEPENDENCIES",
        "Group 1 (AND): [GitHub Push + S3 Upload]\nGroup 2 (OR):  [Webhook]\nFilter: body.ref == 'refs/heads/main'"),
    "ci-cd": diagram("CI/CD PIPELINE",
        "Git Push → Events → Workflows(CI) → ArgoCD → Rollouts\n                              │            │         │\n                         test+build     sync    canary+analysis"),
    "repo": diagram("GITOPS REPO",
        "gitops-repo/\n├── apps/anihpj/\n│   ├── base/        (common YAML)\n│   └── overlays/    (dev|staging|prod)\n└── clusters/prod/argocd-apps/\n    └── anihpj-app.yaml"),
    "security": diagram("SECURITY LAYERS",
        "RBAC → NetworkPolicy → SSO/OIDC →\nSecrets Encryption → Audit → Monitoring\nDefense in depth: multiple protective layers"),
    "rbac": diagram("RBAC CHAIN",
        "Subject ──▶ Role ──▶ RoleBinding\n(User/SA)   (verbs)  (assignment)\n'Alice CAN get pods in namespace anihpj'"),
    "secret": diagram("GITOPS SECRETS",
        "❌ NEVER plaintext in Git\n✅ Sealed Secrets (encrypt before commit)\n✅ External Secrets Operator (fetch from vault)\n✅ SOPS (KMS-encrypted, ArgoCD decrypts)"),
    "user": diagram("ARGO CD AUTH",
        "Local: accounts.alice: apiKey, login (bcrypt)\nSSO:   Google, GitHub, Okta, AzureAD via Dex\nRBAC:  g, alice, role:admin\n       p, role:admin, applications, *, *, allow"),
    "notification": diagram("NOTIFICATIONS",
        "Triggers:              Services:\non-sync-succeeded ────▶ Slack/Email/Teams\non-sync-failed    ────▶ PagerDuty/Opsgenie\non-health-degraded───▶ Webhook/Graphana"),
    "migration": diagram("DB MIGRATION",
        "1. Backup (pg_dump → S3)\n2. Migrate (manage.py migrate)\n3. Verify (check migration table)\n4. THEN deploy new app\n⚠️ Migration must be BACKWARD compatible"),
    "multi-env": diagram("MULTI-ENVIRONMENT",
        "DEV(auto-sync) → STAGING(auto) → PROD(manual)\nEach env = separate ArgoCD Application\nSame GitOps repo, different path/branch"),
    "monitoring": diagram("MONITORING",
        "Argo Metrics → Prometheus → Grafana → Alerts\nKey: sync failures, workflow errors, stuck rollouts\nAll 4 controllers expose Prometheus natively"),
    "resources": diagram("RESOURCE LIMITS",
        "requests = guaranteed minimum\nlimits   = maximum cap\nArgoCD: Repo Server 512Mi-1Gi, Controller 1-2Gi\nMonitor actual usage → adjust limits"),
    "image": diagram("IMAGE FLOW",
        "Dockerfile → Build → Registry → Pod\nUse specific tags (v2.1), NEVER :latest\nImagePullPolicy: Always | IfNotPresent | Never"),
    "configmap": diagram("CONFIGMAP vs SECRET",
        "ConfigMap: plaintext (DB_URL, LOG_LEVEL)\nSecret:    sensitive (passwords, keys)\nMount as env vars or volumes in pods"),
    "drift": diagram("DRIFT DETECTION",
        "Git(desired) vs Cluster(actual) = Diff\nDiff → OutOfSync → ArgoCD alerts/auto-fixes\nSelf-heal: ANY manual change auto-reverted"),
    "backup": diagram("BACKUP STRATEGY",
        "1. Git repo IS the backup (source of truth)\n2. argocd admin export (cluster creds)\n3. CronWorkflow for scheduled backups\n4. Test restore quarterly"),
    "troubleshoot": diagram("TROUBLESHOOTING",
        "1. Check logs: kubectl logs / argo logs\n2. Check status: kubectl describe / argo get\n3. Check events: kubectl get events\n4. Follow the chain: Events→WF→CD→Rollouts"),
    "promotion": diagram("PROMOTION FLOW",
        "Dev → Stage → Prod\nEach promotion = merge to env branch\nRBAC prevents unauthorized prod deploys\ngit revert = instant rollback at any stage"),
    "upgrade": diagram("UPGRADE STRATEGY",
        "1. Read upgrade guide\n2. Test in staging first\n3. Backup before upgrading\n4. Upgrade ONE minor version at a time\n5. Monitor syncs during upgrade"),
    "app-of-apps": diagram("APP OF APPS",
        "Parent App (root)\n├── Child A (anihpj backend)\n├── Child B (postgres operator)\n└── Child C (redis cluster)\nOne apply = entire environment"),
    "hooks": diagram("SYNC HOOKS",
        "PreSync ──▶ Sync ──▶ PostSync\n(backup)    (apply)   (smoke test)\nHook types: Pod, Job, Workflow"),
  }

def classify(question):
    q = question.lower()
    if "gitops" in q and "principle" in q: return "gitops"
    if "pull-based" in q or "push-based" in q or "push vs" in q: return "push-pull"
    if "roll back" in q or "git revert" in q: return "gitops"
    if "cncf" in q and ("graduated" in q or "maturity" in q): return "argo-projects"
    if "argo cd" in q and ("application" in q or "appproject" in q) and "app of apps" not in q: return "application"
    if "app of apps" in q: return "app-of-apps"
    if "health" in q and ("status" in q or "sync" in q) and "hook" not in q: return "health"
    if "sync" in q and "hook" in q: return "hooks"
    if "sync" in q and ("policy" in q or "auto" in q or "self-heal" in q or "manual" in q): return "sync"
    if "source" in q and ("type" in q or "git" in q or "helm" in q or "kustomize" in q): return "application"
    if "api server" in q or ("controller" in q and "application controller" in q): return "k8s"
    if "kubelet" in q or "control plane" in q or "worker node" in q: return "k8s"
    if "etcd" in q: return "k8s"
    if "reconciliation" in q or "reconcile" in q: return "reconcile"
    if "crd" in q or "custom resource" in q: return "crd"
    if "docker" in q or "image layer" in q or "dockerfile" in q: return "docker"
    if "label" in q and ("selector" in q or "match" in q or "annotation" in q): return "labels"
    if "annotation" in q: return "labels"
    if "namespace" in q: return "namespace"
    if "yaml" in q and ("indent" in q or "strict" in q or "format" in q): return "yaml"
    if "git" in q and ("branch" in q or "commit" in q): return "git"
    if "drift" in q: return "drift"
    if ("job" in q and "workflow" in q) or "k8s job" in q: return "workflow"
    if "dag" in q and "steps" in q: return "dag-steps"
    if "template" in q and ("type" in q or "container" in q or "script" in q or "resource" in q or "suspend" in q or "templateref" in q): return "template"
    if "template" in q and "reference" in q: return "template"
    if "artifact" in q: return "artifact"
    if "parameter" in q and ("pass" in q or "submit" in q or "output" in q or "input" in q): return "parameter"
    if "withitems" in q or "withsequence" in q or "withparam" in q or "loop" in q: return "loop"
    if "retry" in q or "backoff" in q: return "retry"
    if "cronworkflow" in q or "schedule" in q and "cron" in q: return "cron"
    if "canary" in q and ("step" in q or "weight" in q or "traffic" in q or "percentage" in q): return "canary"
    if "blue-green" in q or "blue green" in q: return "blue-green"
    if "analysis" in q and ("metric" in q or "template" in q or "prometheus" in q or "health" in q): return "analysis"
    if "rollout" in q and ("spec" in q or "controller" in q or "service" in q or "replicaset" in q or "install" in q): return "rollout"
    if "event" in q and ("source" in q or "sensor" in q or "eventbus" in q or "nats" in q or "architecture" in q): return "events"
    if "dependency" in q or ("filter" in q and "sensor" in q): return "sensor"
    if "ci/cd" in q or "end-to-end" in q or ("pipeline" in q and "workflow" in q): return "ci-cd"
    if "gitops repo" in q: return "repo"
    if "security" in q or "hardening" in q or "network policy" in q: return "security"
    if "rbac" in q: return "rbac"
    if "secret" in q and ("gitops" in q or "encrypt" in q or "sops" in q or "sealed" in q or "vault" in q): return "secret"
    if "sso" in q or "oidc" in q or "user" in q and ("management" in q or "dex" in q or "login" in q): return "user"
    if "notification" in q or ("slack" in q and "notif" in q): return "notification"
    if "migration" in q or "db migration" in q: return "migration"
    if "multi-environment" in q or ("promotion" in q and ("dev" in q or "staging" in q)): return "multi-env"
    if "monitoring" in q or ("prometheus" in q and ("alert" in q or "grafana" in q)): return "monitoring"
    if "resource" in q and ("limit" in q or "cpu" in q or "memory" in q): return "resources"
    if "image" in q and ("tag" in q or "registry" in q or "pull" in q or "container" in q): return "image"
    if "configmap" in q or ("secret" in q and "volume" in q): return "configmap"
    if "plugin" in q: return "application"
    if "backup" in q or "disaster" in q: return "backup"
    if "troubleshoot" in q or "debug" in q or "debugging" in q: return "troubleshoot"
    if "promotion" in q or "promote" in q: return "promotion"
    if "upgrade" in q: return "upgrade"
    if "workflow" in q: return "workflow"
    if "rollout" in q: return "rollout"
    if "canary" in q: return "canary"
    if "event" in q: return "events"
    if "argo cd" in q: return "application"
    return "gitops"

count = 0

def enrich(match):
    global count
    item = match.group(0)
    qm = re.search(r'<div class="eq-question">(.*?)</div>', item, re.DOTALL)
    if not qm:
        return item
    qtext = qm.group(1).strip()
    key = classify(qtext)
    d = DIAGRAMS.get(key, DIAGRAMS["gitops"])
    
    if 'diagram-container' in item:
        return item
    
    # Insert diagram before explanation closing div
    old = '</div>\n                        </details>'
    new = d + '\n                            </div>\n                        </details>'
    count += 1
    return item.replace(old, new)

# Match each exam-question-item block
content = re.sub(
    r'<div class="exam-question-item">.*?</details>\s*</div>',
    enrich,
    content,
    flags=re.DOTALL
)

print(f"Diagrams added: {count}")

with open('argo.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
