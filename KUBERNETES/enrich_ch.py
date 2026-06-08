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
    # Find comment before Q&A
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
# CHAPTER 1: CNCF Ecosystem, Real-World Users, Helm vs Alternatives
# ============================================================
ch1_s = chapter_starts.get(1, -1)
ch2_s = chapter_starts.get(2, -1)
if ch1_s > 0 and ch2_s > ch1_s:
    content = '''
                <div class="section-block">
                    <h4>1.7a Helm in the CNCF Ecosystem</h4>
                    <p>Helm is a <strong>CNCF Graduated project</strong> (since April 2020), placing it alongside Kubernetes, Prometheus, Envoy, and etcd in the foundation's highest maturity tier. This status means Helm has proven its stability, adoption, and governance at enterprise scale.</p>
                    <div class="compare-table"><table>
                        <thead><tr><th>CNCF Status</th><th>Projects</th><th>What It Means</th></tr></thead>
                        <tbody>
                            <tr><td><span class="badge badge-gold">Graduated</span></td><td>Kubernetes, Helm, Prometheus, Envoy, etcd, CoreDNS, containerd, Jaeger, Harbor, Rook, Argo</td><td>Production-ready at massive scale; strong governance; used by thousands of orgs</td></tr>
                            <tr><td><span class="badge badge-silver">Incubating</span></td><td>Backstage, Crossplane, Dapr, Knative, OpenTelemetry, Operator Framework, Thanos</td><td>Growing adoption; maturing governance; on path to graduation</td></tr>
                            <tr><td><span class="badge badge-bronze">Sandbox</span></td><td>200+ projects (Kyverno, KubeVirt, Parsec, etc.)</td><td>Experimental; early-stage innovation</td></tr>
                        </tbody>
                    </table></div>
                    <div class="diagram-container">
                        <div class="diagram-title">Helm's Position in the Cloud Native Stack</div>
<pre>
CLOUD NATIVE LANDSCAPE
=====================================================
 App Definition      Orchestration      Provisioning
+-----------------+ +----------------+ +---------------+
| HELM            | | Kubernetes     | | Terraform     |
| Kustomize       | | Argo CD        | | Crossplane    |
| Docker Compose  | | Flux           | | Pulumi        |
+-----------------+ +----------------+ +---------------+

 Observability      Service Mesh       Security
+-----------------+ +----------------+ +---------------+
| Prometheus      | | Istio          | | Falco         |
| Grafana         | | Linkerd        | | Kyverno       |
| OpenTelemetry   | | Consul         | | OPA/Gatekeeper|
+-----------------+ +----------------+ +---------------+

Helm = The bridge from "I have YAML" to "I have 
       a deployable, shareable application"
</pre>
                    </div>
                </div>
                <div class="section-block">
                    <h4>1.7b Real-World Helm Adoption</h4>
                    <div class="card-grid three-col">
                        <div class="info-card"><div class="card-icon">MAJOR</div><h5>Enterprise Giants</h5><p>Microsoft, Google, AWS, IBM, SAP, Adobe, Salesforce, VMware all use Helm internally and publish official charts.</p></div>
                        <div class="info-card"><div class="card-icon">STARTUP</div><h5>Cloud-Native Leaders</h5><p>Datadog, GitLab, HashiCorp, MongoDB, Confluent, Elastic distribute software via Helm charts on Artifact Hub.</p></div>
                        <div class="info-card"><div class="card-icon">PLATFORM</div><h5>Platform Teams</h5><p>Thousands of organizations build standardized "golden path" Helm charts for internal application deployment.</p></div>
                    </div>
                    <div class="info-box tip">
                        <h5>Helm by the Numbers (2024-2025)</h5>
                        <ul>
                            <li><strong>10,000+ charts</strong> on Artifact Hub - the de facto standard for K8s packaging</li>
                            <li><strong>70%+ of K8s users</strong> report using Helm (CNCF Survey 2024)</li>
                            <li><strong>OCI support (Helm 3.8+)</strong> means charts live alongside container images</li>
                            <li><strong>All major cloud providers</strong> (EKS, AKS, GKE) have native Helm integration</li>
                        </ul>
                    </div>
                </div>
                <div class="section-block">
                    <h4>1.7c Helm vs Alternatives - Decision Matrix</h4>
                    <div class="compare-table"><table>
                        <thead><tr><th>Feature</th><th>Helm</th><th>Kustomize</th><th>Kubectl</th><th>Operators</th><th>Argo CD</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Templating</strong></td><td><span class="badge badge-green">Go Templates</span></td><td><span class="badge badge-red">None</span></td><td><span class="badge badge-red">None</span></td><td><span class="badge badge-yellow">Custom</span></td><td><span class="badge badge-green">Via Helm/Kustomize</span></td></tr>
                            <tr><td><strong>Versioning</strong></td><td><span class="badge badge-green">SemVer</span></td><td><span class="badge badge-yellow">Git-based</span></td><td><span class="badge badge-red">None</span></td><td><span class="badge badge-green">OLM SemVer</span></td><td><span class="badge badge-green">Git commits</span></td></tr>
                            <tr><td><strong>Sharing/Packaging</strong></td><td><span class="badge badge-green">Chart repos</span></td><td><span class="badge badge-red">No built-in</span></td><td><span class="badge badge-red">N/A</span></td><td><span class="badge badge-green">OLM catalog</span></td><td><span class="badge badge-red">Git only</span></td></tr>
                            <tr><td><strong>Dependencies</strong></td><td><span class="badge badge-green">Built-in</span></td><td><span class="badge badge-red">Manual</span></td><td><span class="badge badge-red">N/A</span></td><td><span class="badge badge-green">OLM deps</span></td><td><span class="badge badge-yellow">App of Apps</span></td></tr>
                            <tr><td><strong>Lifecycle Hooks</strong></td><td><span class="badge badge-green">pre/post hooks</span></td><td><span class="badge badge-red">None</span></td><td><span class="badge badge-red">None</span></td><td><span class="badge badge-green">Reconciler</span></td><td><span class="badge badge-green">Sync hooks</span></td></tr>
                            <tr><td><strong>Rollback</strong></td><td><span class="badge badge-green">helm rollback</span></td><td><span class="badge badge-yellow">Git revert</span></td><td><span class="badge badge-yellow">kubectl rollout undo</span></td><td><span class="badge badge-green">OLM upgrades</span></td><td><span class="badge badge-green">Auto-sync</span></td></tr>
                            <tr><td><strong>Best For</strong></td><td>Packaging + sharing apps</td><td>Env-specific overlays</td><td>Quick one-offs</td><td>Stateful day-2 ops</td><td>GitOps delivery</td></tr>
                        </tbody>
                    </table></div>
                    <div class="ckad-exam-tip"><div class="ckad-tip-icon">EXAM</div><div class="ckad-tip-content"><strong>Exam Insight:</strong> The exam may ask you when to use Helm vs Kustomize. <strong>Helm = packaging + sharing</strong> (you want others to install your app). <strong>Kustomize = environment overlays</strong> (dev/staging/prod variants without templating). They can also be used <strong>together</strong> via post-renderers (Ch19).</div></div>
                </div>
'''
    insert_before_qa(ch1_s, ch2_s, content, "Ch1: Ecosystem & Comparisons")

if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nEnrichments applied: {}".format(changes))
    print("Lines: {}".format(html.count('\n')))
