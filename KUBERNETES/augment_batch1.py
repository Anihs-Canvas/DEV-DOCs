import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

def insert_before_qa(ch_start, ch_end, new_content, label):
    global html, changes
    chapter = html[ch_start:ch_end]
    qa_pos = chapter.rfind('class="cka-exam-questions"')
    drill_pos = chapter.rfind('class="ckad-practice-drill"')
    insert_marker = max(qa_pos, drill_pos)
    if insert_marker < 0:
        print("  {}: No Q&A section".format(label))
        return False
    pre = chapter[:insert_marker]
    cmt = pre.rfind('<!--')
    if cmt > insert_marker - 500 and 'Practice' in chapter[cmt:cmt+100]:
        insert_marker = cmt
    abs_insert = ch_start + insert_marker
    html = html[:abs_insert] + new_content + '\n' + html[abs_insert:]
    changes += 1
    print("  {}: Added content".format(label))
    return True

chapter_starts = {}
for ch in range(1, 21):
    pos = html.find('id="ch{}"'.format(ch))
    if pos >= 0:
        chapter_starts[ch] = pos

# ============================================================
# CHAPTER 2: Installing Helm - Add OS-specific installs, verification, plugin ecosystem
# ============================================================
ch2_s = chapter_starts.get(2, -1)
ch3_s = chapter_starts.get(3, -1)
if ch2_s > 0 and ch3_s > ch2_s:
    content = '''
                <div class="section-block">
                    <h4>2.7 Installing Helm Across Platforms - Complete Guide</h4>
                    <div class="card-grid three-col">
                        <div class="info-card"><div class="card-icon">🐧</div><h5>Linux (APT/YUM)</h5><pre>
# Debian/Ubuntu:
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# RHEL/CentOS/Fedora:
sudo dnf install helm
</pre></div>
                        <div class="info-card"><div class="card-icon">🪟</div><h5>Windows</h5><pre>
# Chocolatey:
choco install kubernetes-helm

# Scoop:
scoop install helm

# Direct download (.zip):
# Extract helm.exe to PATH
# Verify: helm version
</pre></div>
                        <div class="info-card"><div class="card-icon">🍎</div><h5>macOS</h5><pre>
# Homebrew:
brew install helm

# MacPorts:
sudo port install helm
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>2.8 Essential Helm Plugins for Exam & Production</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Plugin</th><th>Install Command</th><th>Purpose</th><th>Exam Relevance</th></tr></thead>
                        <tbody>
                            <tr><td><strong>helm-diff</strong></td><td><code>helm plugin install https://github.com/databus23/helm-diff</code></td><td>Shows diff between release and new chart</td><td>⭐⭐⭐ Detect changes before upgrade</td></tr>
                            <tr><td><strong>helm-secrets</strong></td><td><code>helm plugin install https://github.com/jkroepke/helm-secrets</code></td><td>Encrypt/decrypt values files with SOPS</td><td>⭐⭐ Security best practices</td></tr>
                            <tr><td><strong>helm-mapkubeapis</strong></td><td><code>helm plugin install https://github.com/helm/helm-mapkubeapis</code></td><td>Map deprecated APIs to supported versions</td><td>⭐⭐⭐ K8s version upgrades</td></tr>
                            <tr><td><strong>helm-unittest</strong></td><td><code>helm plugin install https://github.com/helm-unittest/helm-unittest</code></td><td>Unit tests for Helm templates</td><td>⭐⭐ CI/CD testing</td></tr>
                        </tbody>
                    </table></div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">💡</div><div class="ckad-tip-content"><strong>Exam Tip:</strong> While plugins aren't heavily tested, knowing helm-diff exists is useful for troubleshooting questions. You can always suggest "install helm-diff plugin" as a solution for detecting configuration drift.</div></div>
                </div>
                <div class="section-block">
                    <h4>2.9 Helm Environment Deep Dive</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Key Environment Variables</h5>
                            <div class="compare-table"><table>
                                <tr><th>Variable</th><th>Purpose</th><th>Default</th></tr>
                                <tr><td><code>HELM_HOME</code></td><td>Helm config/cache location</td><td><code>~/.config/helm</code></td></tr>
                                <tr><td><code>HELM_CACHE_HOME</code></td><td>Chart cache</td><td><code>$HELM_HOME/cache</code></td></tr>
                                <tr><td><code>HELM_CONFIG_HOME</code></td><td>Config files</td><td><code>$HELM_HOME/config</code></td></tr>
                                <tr><td><code>HELM_DATA_HOME</code></td><td>Data/plugins</td><td><code>$HELM_HOME/data</code></td></tr>
                                <tr><td><code>HELM_DRIVER</code></td><td>Storage backend</td><td><code>secret</code></td></tr>
                                <tr><td><code>HELM_KUBECONTEXT</code></td><td>Override kube context</td><td>Current context</td></tr>
                                <tr><td><code>KUBECONFIG</code></td><td>Kubeconfig path</td><td><code>~/.kube/config</code></td></tr>
                            </table></div>
                        </div>
                        <div class="split-side">
                            <h5>Registry Configuration</h5>
<pre>
# ~/.config/helm/registry/config.json
{
  "auths": {
    "ghcr.io": {
      "auth": "base64encodedtoken"
    },
    "myregistry.io": {
      "auth": "base64encodedtoken"
    }
  }
}

# Login command:
helm registry login ghcr.io -u USER -p TOKEN
helm registry logout ghcr.io
</pre>
                        </div>
                    </div>
                </div>
'''
    insert_before_qa(ch2_s, ch3_s, content, "Ch2: Installation & Plugins")

# ============================================================
# CHAPTER 3: Charts - Add Chart.yaml deep dive, chart types comparison, dependency patterns
# ============================================================
ch3_s = chapter_starts.get(3, -1)
ch4_s = chapter_starts.get(4, -1)
if ch3_s > 0 and ch4_s > ch3_s:
    content = '''
                <div class="section-block">
                    <h4>3.7 Chart.yaml - Every Field Explained</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Field</th><th>Required?</th><th>Type</th><th>Description</th></tr></thead>
                        <tbody>
                            <tr><td><code>apiVersion</code></td><td><span class="badge badge-red">YES</span></td><td>string</td><td>Chart API version. Must be <code>v2</code> for Helm 3. <code>v1</code> was Helm 2.</td></tr>
                            <tr><td><code>name</code></td><td><span class="badge badge-red">YES</span></td><td>string</td><td>Chart name. Must match directory name. Lowercase + hyphens only.</td></tr>
                            <tr><td><code>version</code></td><td><span class="badge badge-red">YES</span></td><td>semver</td><td>Chart version. Must follow SemVer 2. Increment on every change.</td></tr>
                            <tr><td><code>kubeVersion</code></td><td>No</td><td>semver range</td><td>K8s version constraint. <code>>=1.25.0</code> blocks old clusters.</td></tr>
                            <tr><td><code>description</code></td><td>No</td><td>string</td><td>Single-line description shown in <code>helm search</code>.</td></tr>
                            <tr><td><code>type</code></td><td>No</td><td>string</td><td><code>application</code> (default, deployable) or <code>library</code> (template-only).</td></tr>
                            <tr><td><code>appVersion</code></td><td>No</td><td>string</td><td>Version of the app being deployed. Informational only.</td></tr>
                            <tr><td><code>dependencies</code></td><td>No</td><td>array</td><td>List of subchart dependencies with version constraints.</td></tr>
                            <tr><td><code>maintainers</code></td><td>No</td><td>array</td><td>Name + email of chart maintainers.</td></tr>
                            <tr><td><code>icon</code></td><td>No</td><td>URL</td><td>Icon URL shown in Artifact Hub. SVG or PNG.</td></tr>
                            <tr><td><code>annotations</code></td><td>No</td><td>map</td><td>Arbitrary metadata. Used by Artifact Hub for categories.</td></tr>
                            <tr><td><code>keywords</code></td><td>No</td><td>array</td><td>Search keywords. Used by <code>helm search</code> and Artifact Hub.</td></tr>
                        </tbody>
                    </table></div>
                </div>
                <div class="section-block">
                    <h4>3.8 Chart Types - Application vs Library (Side-by-Side)</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>📦 Application Chart</h5>
                            <div class="info-box tip"><p>Deployable. Contains templates that produce K8s resources. This is what you install with <code>helm install</code>.</p></div>
<pre>
# Chart.yaml
apiVersion: v2
name: anihpj
type: application
version: 0.1.0

# Contains:
templates/
  deployment.yaml  ✅ Creates resources
  service.yaml     ✅ Creates resources
  NOTES.txt        ✅ Post-install message
</pre>
                        </div>
                        <div class="split-side">
                            <h5>📚 Library Chart</h5>
                            <div class="info-box"><p>NOT deployable. Contains only named templates (<code>define</code> blocks). Imported by other charts via dependencies.</p></div>
<pre>
# Chart.yaml
apiVersion: v2
name: anihpj-common
type: library
version: 0.1.0

# Contains:
templates/
  _labels.tpl      {{ define "anihpj.labels" }}
  _security.tpl    {{ define "anihpj.security" }}
  # NO deployment.yaml, service.yaml etc.
</pre>
                        </div>
                    </div>
                    <div class="ckad-gotcha"><div class="ckad-gotcha-icon">⚠️</div><div class="ckad-gotcha-content"><strong>Library Chart Gotcha:</strong> Running <code>helm install</code> on a library chart produces an error. Library charts are imported with <code>{{ include "name" . }}</code> in another chart's templates. They cannot be installed standalone.</div></div>
                </div>
                <div class="section-block">
                    <h4>3.9 Chart Versioning Best Practices</h4>
                    <div class="process-steps">
                        <div class="ps-step"><div class="ps-num">1</div><div class="ps-content"><h5>SemVer for Charts</h5><p>Chart version follows MAJOR.MINOR.PATCH. Increment MAJOR for breaking template changes, MINOR for new features, PATCH for bug fixes. <code>appVersion</code> tracks the application version independently.</p></div></div>
                        <div class="ps-step"><div class="ps-num">2</div><div class="ps-content"><h5>kubeVersion Constraints</h5><p>Use <code>kubeVersion: ">=1.25.0-0"</code> to prevent installation on unsupported clusters. The <code>-0</code> suffix allows pre-release versions. <code>semverCompare</code> in templates provides runtime checks.</p></div></div>
                        <div class="ps-step"><div class="ps-num">3</div><div class="ps-content"><h5>Deprecation Strategy</h5><p>Set <code>deprecated: true</code> in Chart.yaml when a chart is no longer maintained. Users see a warning on install. Remove the chart entirely after a deprecation period.</p></div></div>
                    </div>
                </div>
'''
    insert_before_qa(ch3_s, ch4_s, content, "Ch3: Chart.yaml & Types")

# ============================================================
# CHAPTER 4: Values & Configuration - Add schema examples, best practices, env patterns
# ============================================================
ch4_s = chapter_starts.get(4, -1)
ch5_s = chapter_starts.get(5, -1)
if ch4_s > 0 and ch5_s > ch4_s:
    content = '''
                <div class="section-block">
                    <h4>4.7 Values File Patterns - Dev vs Staging vs Production</h4>
                    <div class="card-grid three-col">
                        <div class="info-card"><div class="card-icon">🛠️</div><h5>values-dev.yaml</h5><pre>
replicaCount: 1
image:
  tag: latest
  pullPolicy: Always
ingress:
  enabled: false
resources:
  limits:
    cpu: 200m
    memory: 256Mi
debug: true
logging:
  level: DEBUG
</pre></div>
                        <div class="info-card"><div class="card-icon">🧪</div><h5>values-staging.yaml</h5><pre>
replicaCount: 2
image:
  tag: v2.1.0-rc3
  pullPolicy: IfNotPresent
ingress:
  enabled: true
  host: staging.anihpj.io
resources:
  limits:
    cpu: 500m
    memory: 512Mi
debug: false
logging:
  level: INFO
</pre></div>
                        <div class="info-card"><div class="card-icon">🏭</div><h5>values-prod.yaml</h5><pre>
replicaCount: 3
image:
  tag: v2.0.0
  pullPolicy: IfNotPresent
ingress:
  enabled: true
  host: anihpj.io
  tls: true
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
debug: false
logging:
  level: WARN
</pre></div>
                    </div>
                </div>
                <div class="section-block">
                    <h4>4.8 Understanding the Deep Merge</h4>
                    <div class="diagram-container">
                        <div class="diagram-title">How Multiple Values Files Merge</div>
<pre>
VALUES MERGE VISUALIZATION
═══════════════════════════════════════════════════════════
values.yaml        + values-staging.yaml    = MERGED RESULT
───────────────────────────────────────────────────────────
replicaCount: 1      replicaCount: 2          replicaCount: 2  ← override
image:                image:                   image:
  repo: nginx           tag: latest              repo: nginx    ← preserved!
  tag: v2.0                                     tag: latest    ← overridden

KEY RULES:
1. Non-conflicting keys are PRESERVED (repo: nginx survived)
2. Conflicting keys use LAST file's value (tag: latest wins)
3. Nested objects are merged DEEP (not wholesale replaced)
4. Lists are REPLACED entirely (NOT appended)
5. Null values in later files DO NOT remove earlier values
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>4.9 values.schema.json - Practical Examples</h4>
                    <div class="split-panel">
                        <div class="split-side">
                            <h5>Basic Constraints</h5>
<pre>
{
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50
    },
    "service": {
      "type": "object",
      "required": ["type", "port"],
      "properties": {
        "type": {
          "enum": ["ClusterIP","NodePort","LoadBalancer"]
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    }
  }
}
</pre>
                        </div>
                        <div class="split-side">
                            <h5>Conditional Validation</h5>
<pre>
{
  "properties": {
    "ingress": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "tls": {"type": "boolean"},
        "host": {"type": "string"}
      },
      "allOf": [{
        "if": {
          "properties": {"tls": {"const": true}}
        },
        "then": {
          "required": ["host"]
        }
      }]
    }
  }
}
# If TLS is enabled, host MUST be provided
</pre>
                        </div>
                    </div>
                </div>
'''
    insert_before_qa(ch4_s, ch5_s, content, "Ch4: Values Patterns & Schema")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nTotal enrichments: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
