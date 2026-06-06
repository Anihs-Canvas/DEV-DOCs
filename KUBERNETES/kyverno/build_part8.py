"""Build Part 8 — Complete Cluster Bootstrap Walkthrough"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 8: BOOTSTRAP WALKTHROUGH -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-8">
        <h2>🚀 <span class="section-num">Part 8</span> — Complete Cluster Bootstrap Walkthrough</h2>
        <div class="section-intro">
            <p>This is the <strong>Day 1 playbook</strong> — every command needed to go from 10 bare Ubuntu 24.04 VMs to a fully operational Kubernetes cluster running the anihpj web application. Every command is <strong>copy-paste ready</strong>, tested on the anihpj cluster, and follows the exact sequence: <em>prerequisites → init → join CP nodes → join workers → install CNI → deploy applications</em>.</p>
            <p>The entire bootstrap takes approximately <strong>20-30 minutes</strong> for all 10 nodes.</p>
        </div>

        <!-- 8.1 PRE-REQUISITES -->
        <h3 id="part-8-1">8.1 Pre-requisites — All 10 Nodes</h3>
        <div class="api-block">
            <p>Run this script as <strong>root</strong> on EVERY node (cp-01..03, wk-01..05, fe-01..02) BEFORE running kubeadm init/join. This configures the Linux kernel, installs containerd, and installs the Kubernetes binaries:</p>

            <h4>Part A: Kernel Modules & System Configuration</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔧 Kernel & System Prep — Run on ALL nodes</div>
                <pre><code class="language-bash">#!/bin/bash
# Run as root on EVERY node before kubeadm init/join

# ── Load required kernel modules ──
cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
modprobe overlay
modprobe br_netfilter</code></pre>
            </div>
            <div class="info">
                <strong>💡 Why these modules?</strong> <code class="inline">overlay</code> is the kernel module that enables the OverlayFS filesystem — required by containerd for container image layers. <code class="inline">br_netfilter</code> enables iptables to see bridged traffic — without it, Pod-to-Pod network policies (NetworkPolicy) won't work because iptables rules are bypassed on bridge interfaces.
            </div>

            <div class="diagram-box">
                <div class="diagram-title">📡 Kernel Networking Parameters</div>
                <pre><code class="language-bash"># ── Set kernel networking parameters ──
cat <<EOF | tee /etc/sysctl.d/99-kubernetes.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sysctl --system

# ── Disable swap (REQUIRED by Kubernetes) ──
swapoff -a
sed -i '/swap/d' /etc/fstab</code></pre>
            </div>
            <div class="info">
                <strong>💡 Why these sysctls?</strong> <code class="inline">bridge-nf-call-iptables</code> ensures that packets traversing Linux bridges (used by containers) pass through iptables. Without this, kube-proxy's iptables rules would be invisible to Pod traffic. <code class="inline">ip_forward</code> enables the node to forward packets between Pods. <strong>Swap must be OFF</strong> because Kubernetes' QoS model assumes guaranteed memory — if a Pod is swapped to disk, the kubelet can't accurately track its memory usage and QoS guarantees break.
            </div>

            <h4>Part B: Install Container Runtime (containerd)</h4>
            <div class="diagram-box">
                <div class="diagram-title">📦 Install & Configure containerd</div>
                <pre><code class="language-bash"># ── Install containerd ──
apt-get update && apt-get install -y containerd
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml

# CRITICAL: Use systemd as the cgroup driver (matches kubelet default)
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd</code></pre>
            </div>
            <div class="highlight-box">
                <strong>🧠 The cgroup driver mismatch is the #1 bootstrap failure:</strong> containerd defaults to <code class="inline">cgroupfs</code> driver, but kubelet defaults to <code class="inline">systemd</code>. If they mismatch, the kubelet can't properly enforce resource limits, and you'll see errors like <code class="inline">"Failed to create pod sandbox"</code>. ALWAYS set containerd to <code class="inline">systemd</code> to match kubelet.
            </div>

            <h4>Part C: Install Kubernetes Binaries</h4>
            <div class="diagram-box">
                <div class="diagram-title">📦 Install kubeadm, kubelet, kubectl</div>
                <pre><code class="language-bash"># ── Install Kubernetes packages ──
apt-get update && apt-get install -y apt-transport-https ca-certificates curl gpg

# Add the Kubernetes package repository
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | \
  gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | \
  tee /etc/apt/sources.list.d/kubernetes.list

# Install and pin versions (prevent accidental upgrades)
apt-get update && apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# Enable kubelet (it will fail until kubeadm init/join — that's OK!)
systemctl enable kubelet</code></pre>
            </div>
            <div class="info">
                <strong>💡 Why <code class="inline">apt-mark hold</code>?</strong> This prevents unattended-upgrades from accidentally upgrading Kubernetes packages. Kubernetes upgrades must be done deliberately, in a specific order, one node at a time — an automatic upgrade could break the cluster. The kubelet is enabled here but will crash-loop until <code class="inline">kubeadm init</code> or <code class="inline">kubeadm join</code> creates the required configuration files — this is expected behavior.
            </div>
        </div>

        <!-- 8.2 INITIALIZE -->
        <h3 id="part-8-2">8.2 Initialize the Cluster — cp-01 ONLY</h3>
        <div class="api-block">
            <p>After prerequisites are done on all nodes, <strong>bootstrap the cluster</strong> from cp-01:</p>

            <div class="warning">
                <strong>⚠️ CRITICAL: Save the init output!</strong> The <code class="inline">kubeadm init</code> output contains the <strong>join command and certificate key</strong> needed for other nodes. Without it, you can't join the remaining CP nodes. Copy it to a secure location immediately.
            </div>

            <div class="diagram-box">
                <div class="diagram-title">🚀 kubeadm init — Bootstrap the Cluster</div>
                <pre><code class="language-bash"># Create kubeadm configuration (see Part 1.2 for full config):
cat <<EOF > ~/kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.31.0
controlPlaneEndpoint: "10.0.0.100:6443"
networking:
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
apiServer:
  certSANs:
  - "10.0.0.100"
  - "anihpj.io"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "10.0.0.10"
nodeRegistration:
  criSocket: "unix:///run/containerd/containerd.sock"
EOF

# Run init (--upload-certs shares certs with joining CP nodes):
kubeadm init --config=~/kubeadm-config.yaml --upload-certs

# SAVE THIS OUTPUT! It contains:
#   - Worker join command: kubeadm join 10.0.0.100:6443 --token ... --discovery-token-ca-cert-hash ...
#   - CP join command:     kubeadm join 10.0.0.100:6443 --token ... --control-plane --certificate-key ...
#   - Certificate key:     (needed for cp-02 and cp-03)</code></pre>
            </div>

            <h4>Post-Init: Configure kubectl on cp-01</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔑 Set Up kubectl for the Admin User</div>
                <pre><code class="language-bash"># Set up kubectl to talk to the new cluster:
mkdir -p $HOME/.kube
cp /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# Verify — the node shows as NotReady until CNI is installed:
kubectl get nodes
# NAME    STATUS     ROLES           AGE   VERSION
# cp-01   NotReady   control-plane   30s   v1.31.0</code></pre>
            </div>
            <div class="info">
                <strong>💡 Why NotReady?</strong> The node shows <code class="inline">NotReady</code> because no CNI (Container Network Interface) plugin is installed yet. The kubelet can't assign Pod IPs without a network plugin. This is fixed in Step 8.5 when Calico is installed. The control plane components (apiserver, etcd, scheduler, controller-manager) ARE running — they use the host network, not the Pod network.
            </div>
        </div>

        <!-- 8.3 JOIN CP NODES -->
        <h3 id="part-8-3">8.3 Join Other Control Plane Nodes — cp-02, cp-03</h3>
        <div class="api-block">
            <p>After cp-01 is initialized, join the remaining control plane nodes using the <strong>certificate key</strong> from the init output:</p>

            <div class="diagram-box">
                <div class="diagram-title">🔗 Join cp-02 and cp-03 as Control Plane Nodes</div>
                <pre><code class="language-bash"># On cp-02 AND cp-03 (run the SAME command on each):
kubeadm join 10.0.0.100:6443 \
  --token abc123.0123456789abcdef \
  --discovery-token-ca-cert-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef \
  --control-plane \
  --certificate-key a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2

# The --control-plane flag tells kubeadm to:
#   1. Download the etcd certs and join the etcd cluster
#   2. Download the control plane certs (apiserver, scheduler, controller-manager)
#   3. Start static Pods for apiserver, scheduler, controller-manager, etcd
#   4. The --certificate-key decrypts the certificate bundle uploaded by --upload-certs</code></pre>
            </div>

            <div class="highlight-box">
                <strong>🧠 How --upload-certs and --certificate-key work:</strong> During <code class="inline">kubeadm init --upload-certs</code>, kubeadm encrypts ALL control plane certificates (apiserver, etcd, front-proxy, CA) into a Secret in the <code class="inline">kube-system</code> namespace. The <code class="inline">--certificate-key</code> is the decryption key. Joining CP nodes use this key to decrypt the Secret and get copies of the same certificates used by cp-01. Without this mechanism, you'd need to manually copy certificates between CP nodes — <code class="inline">--upload-certs</code> automates it.
            </div>

            <p>After joining, set up kubectl on cp-02 and cp-03 (optional but recommended):</p>
            <div class="diagram-box">
                <div class="diagram-title">🔑 Set Up kubectl on cp-02 and cp-03</div>
                <pre><code class="language-bash">mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config</code></pre>
            </div>
        </div>

        <!-- 8.4 JOIN WORKERS -->
        <h3 id="part-8-4">8.4 Join Worker Nodes — wk-01 through wk-05</h3>
        <div class="api-block">
            <p>Workers join using a simpler command (no <code class="inline">--control-plane</code> or <code class="inline">--certificate-key</code>):</p>

            <div class="diagram-box">
                <div class="diagram-title">🔗 Join All 5 Worker Nodes</div>
                <pre><code class="language-bash"># On EACH worker node (wk-01 through wk-05):
kubeadm join 10.0.0.100:6443 \
  --token abc123.0123456789abcdef \
  --discovery-token-ca-cert-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef

# What happens during join:
#   1. kubeadm connects to the API server using the bootstrap token
#   2. API server validates the token and returns the cluster CA cert
#   3. kubeadm generates a kubelet certificate signed by the cluster CA
#   4. kubeadm creates /etc/kubernetes/kubelet.conf (kubelet config)
#   5. kubelet starts and registers this node with the API server</code></pre>
            </div>

            <div class="diagram-box">
                <div class="diagram-title">⚡ Bulk Join — All Workers at Once</div>
                <pre><code class="language-bash"># Generate join command on cp-01 (valid for 24 hours):
kubeadm token create --print-join-command
# Output: kubeadm join 10.0.0.100:6443 --token newtoken.abcdefghijk --discovery-token-ca-cert-hash sha256:...

# Run this output command on each worker. Workers can join in PARALLEL
# (unlike CP nodes which must join sequentially for etcd safety).
# Pro tip: use a terminal multiplexer or SSH loop:
for ip in 10.0.4.21 10.0.4.22 10.0.4.23 10.0.4.24 10.0.4.25; do
  ssh root@$ip "kubeadm join 10.0.0.100:6443 --token &lt;token&gt; --discovery-token-ca-cert-hash sha256:&lt;hash&gt;"
done</code></pre>
            </div>
        </div>

        <!-- 8.5 INSTALL CNI -->
        <h3 id="part-8-5">8.5 Install CNI — Calico v3.28</h3>
        <div class="api-block">
            <p>The cluster is functional but <strong>not usable</strong> until a CNI plugin is installed. Without CNI, Pods can't get IP addresses and CoreDNS will stay Pending forever:</p>

            <div class="diagram-box">
                <div class="diagram-title">🌐 Install Calico CNI</div>
                <pre><code class="language-bash"># On cp-01 (or any node with kubectl configured):
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/calico.yaml

# Watch the magic happen:
kubectl get nodes -w
# cp-01   NotReady → Ready   (10-30 seconds)
# cp-02   NotReady → Ready
# cp-03   NotReady → Ready
# wk-01   NotReady → Ready
# ...all nodes transition to Ready...

# Verify CoreDNS is now running (was Pending before CNI):
kubectl get pods -n kube-system | grep coredns
# coredns-6d4b75cb6d-8j9xz   1/1   Running   0   2m
# coredns-6d4b75cb6d-9k0yz   1/1   Running   0   2m</code></pre>
            </div>

            <div class="highlight-box">
                <strong>🧠 What Calico actually does when applied:</strong>
                <ol style="margin-top:6px;">
                    <li>Creates a <code class="inline">DaemonSet</code> that runs a <code class="inline">calico-node</code> Pod on every node</li>
                    <li>Each calico-node Pod programs the node's routing table with Pod CIDR routes</li>
                    <li>Starts the <strong>bird</strong> BGP daemon to exchange routes between nodes</li>
                    <li>Creates iptables rules for NetworkPolicy enforcement</li>
                    <li>Assigns Pod IPs from the node's /26 subnet (part of 10.244.0.0/16)</li>
                    <li>CoreDNS Pods finally get IPs → DNS resolution starts working cluster-wide</li>
                </ol>
            </div>
        </div>

        <!-- 8.6 DEPLOY ANIHPJ APPLICATIONS -->
        <h3 id="part-8-6">8.6 Deploy the anihpj Application Stack</h3>
        <div class="api-block">
            <p>With the cluster operational, deploy the anihpj web application:</p>

            <h4>Step 1: Create Namespace</h4>
            <div class="diagram-box">
                <div class="diagram-title">📁 Create the anihpj-prod Namespace</div>
                <pre><code class="language-bash">kubectl create namespace anihpj-prod</code></pre>
            </div>

            <h4>Step 2: Deploy the Webapp Deployment</h4>
            <div class="diagram-box">
                <div class="diagram-title">🚀 webapp Deployment — 3 Replicas with Health Probes</div>
                <pre><code class="language-yaml">kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  namespace: anihpj-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: registry.anihpj.io/webapp:v1.2.3
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
EOF</code></pre>
            </div>

            <div class="info">
                <strong>💡 Why two probes?</strong> The <strong>liveness probe</strong> tells Kubernetes "restart me if I'm stuck" — if <code class="inline">/healthz</code> fails, the container is killed and restarted. The <strong>readiness probe</strong> tells Kubernetes "I'm ready to receive traffic" — if <code class="inline">/readyz</code> fails, the Pod is removed from the Service's endpoints but NOT restarted. This distinction prevents traffic from being sent to Pods that are temporarily overloaded or still initializing.
            </div>

            <h4>Step 3: Expose as a Service</h4>
            <div class="diagram-box">
                <div class="diagram-title">🌐 Create ClusterIP Service</div>
                <pre><code class="language-bash">kubectl expose deployment webapp -n anihpj-prod \
  --port=8080 --target-port=8080 --name=webapp-svc

# Verify:
kubectl get svc -n anihpj-prod
# NAME         TYPE        CLUSTER-IP      PORT(S)    AGE
# webapp-svc   ClusterIP   10.96.50.100    8080/TCP   10s</code></pre>
            </div>

            <h4>Step 4: Create Ingress (External Access)</h4>
            <div class="diagram-box">
                <div class="diagram-title">🌍 Ingress — TLS + Host-Based Routing</div>
                <pre><code class="language-yaml">kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp-ingress
  namespace: anihpj-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - anihpj.io
    secretName: anihpj-tls
  rules:
  - host: anihpj.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp-svc
            port:
              number: 8080
EOF</code></pre>
            </div>

            <h4>Step 5: Verify Everything</h4>
            <div class="diagram-box">
                <div class="diagram-title">✅ Final Verification</div>
                <pre><code class="language-bash"># Check all resources in the namespace:
kubectl get all -n anihpj-prod
# NAME                          READY   STATUS    RESTARTS   AGE
# pod/webapp-7d8f9c6b5-xk2lm   1/1     Running   0          30s
# pod/webapp-7d8f9c6b5-8j9xz   1/1     Running   0          30s
# pod/webapp-7d8f9c6b5-3k4mn   1/1     Running   0          30s
#
# NAME                 TYPE        CLUSTER-IP      PORT(S)    AGE
# service/webapp-svc   ClusterIP   10.96.50.100    8080/TCP   20s
#
# NAME                                     CLASS   HOSTS       ADDRESS   PORTS
# ingress.networking.k8s.io/webapp-ingress nginx   anihpj.io             80, 443

# Test external access (through the load balancer → nginx → service → pod):
curl -k https://anihpj.io/api/jobs
# {"jobs": [...]}  ← Application is live!</code></pre>
            </div>

            <h4>Bootstrap Summary — Full Sequence</h4>
            <table>
                <tr><th style="width:40px;">#</th><th>Step</th><th>Nodes</th><th>Duration</th><th>Key Command</th></tr>
                <tr><td>1</td><td>Prerequisites</td><td>All 10</td><td>~5 min (parallel)</td><td>Bash script (8.1 — kernel, containerd, kubeadm)</td></tr>
                <tr><td>2</td><td>Init Cluster</td><td>cp-01</td><td>~3 min</td><td><code class="inline">kubeadm init --config=... --upload-certs</code></td></tr>
                <tr><td>3</td><td>Join CP Nodes</td><td>cp-02, cp-03</td><td>~2 min each</td><td><code class="inline">kubeadm join ... --control-plane --certificate-key ...</code></td></tr>
                <tr><td>4</td><td>Join Workers</td><td>wk-01..05</td><td>~2 min (parallel)</td><td><code class="inline">kubeadm join ... --token ...</code></td></tr>
                <tr><td>5</td><td>Install CNI</td><td>All nodes</td><td>~2 min</td><td><code class="inline">kubectl apply -f calico.yaml</code></td></tr>
                <tr><td>6</td><td>Deploy Apps</td><td>cp-01</td><td>~2 min</td><td><code class="inline">kubectl apply -f webapp.yaml</code></td></tr>
                <tr><td colspan="2"><strong>Total</strong></td><td><strong>10 nodes</strong></td><td><strong>~20-30 min</strong></td><td></td></tr>
            </table>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-8">
        <h2>🚀 <span class="section-num">Part 8</span> — Complete Cluster Bootstrap Walkthrough</h2>
        <div class="section-intro"><p>Copy-paste shell scripts: prerequisites → kubeadm init → join CP → join workers → install Calico → deploy anihpj applications.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 8: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, Code blocks: {content.count("<pre><code")}, Diagrams: {content.count("diagram-box")}')
print(f'Highlights: {content.count("highlight-box")}, Warnings: {content.count("warning")}, Infos: {content.count("class=\"info\"")}')
