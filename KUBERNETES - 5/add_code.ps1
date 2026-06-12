
$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = Get-Content $f -Raw
$sz0 = [math]::Round($html.Length/1KB,0)

$sn = @{}
$sn['5'] = @('# 2^(32-24)-2 = 254 usable hosts','# ip route get 10.0.1.50','# ping -M do -s 1472 10.0.1.1','# ip route show 10.0.2.0/24','# ip route show | grep 10.244')
$sn['6'] = @('# ip -6 addr show eth0','# ip -6 addr show | grep fe80','# kubeadm init --pod-network-cidr=10.244.0.0/16,fd00:10:244::/56','# ipv6calc --addr_to_compressed 2001:0db8:...','# tcpdump -i eth0 -nn ip6 and icmp6')
$sn['7'] = @('# traceroute -T -p 443 api.anihpj.com','# ping -M do -s 1400 -c 2 10.0.1.1','# nc -zv 10.0.1.5 8000','# tcpdump -i eth0 -nn icmp','# mtr --tcp -P 443 api.anihpj.com')
$sn['8'] = @('# tcpdump -i eth0 -nn tcp and host 10.0.1.5','# ss -tnp dst 10.0.1.5','# tcpdump -i eth0 tcp[tcpflags] & tcp-syn != 0','# conntrack -L -p tcp','# tcpdump -i eth0 -nn -v tcp and port 8000')
$sn['9'] = @('# sysctl net.ipv4.tcp_congestion_control','# sysctl net.ipv4.tcp_rmem','# ss -ti | grep -i nagle','# sysctl net.ipv4.tcp_sack','# iperf3 -c server -t 10')
$sn['10'] = @('# ss -ulnp','# nc -zuv 10.0.1.5 53','# tcpdump -i eth0 -nn udp port 53','# curl --http3 https://cloudflare.com','# ping -M do -s 1472 8.8.8.8')
$sn['18'] = @('# kubectl get svc,endpoints -n anihpj','# kubectl get pods -n anihpj --show-labels','# iptables -t nat -L KUBE-SERVICES -n -v','# nc -zv NODE_IP 30001','# kubectl expose deployment jobpost --type=NodePort --port=8000')
$sn['19'] = @('# kubectl get ingress -n anihpj','# curl -v -H Host:api.anihpj.com http://IP/api/','# kubectl get secret tls-cert -o yaml','# kubectl get ingressclass','# curl -v https://api.anihpj.com 2>&1')
$sn['20'] = @('# kubectl exec pod -- nslookup svc.ns.svc.cluster.local','# kubectl exec pod -- cat /etc/resolv.conf','# kubectl logs -n kube-system deployment/coredns','# spec.dnsConfig.nameservers:[8.8.8.8]','# kubectl exec pod -- dig +tcp svc')
$sn['21'] = @('# kubectl apply -f default-deny-np.yaml','# kubectl exec pod-a -- nc -zv pod-b-ip 8000','# kubectl get networkpolicies -A','# kubectl describe networkpolicy NAME -n NS','# hubble observe --from-pod src --to-pod dst')
$sn['22'] = @('# kubectl get pod -o jsonpath={.spec.containers[*].name}','# kubectl exec pod -c istio-proxy -- iptables -t nat -L','# istioctl authn tls-check pod-name','# VirtualService route weight: v1=90 v2=10','# kubectl logs pod -c istio-proxy --tail=50')
$sn['23'] = @('# kubectl get gatewayclass','# kubectl get gateway -A','# curl -H Host:api.anihpj.com http://GW_IP/api/','# backendRefs weight: v1=90 v2=10','# ingress2gateway print -f ingress.yaml')

$fixed = 0
foreach ($chKey in '5','6','7','8','9','10','18','19','20','21','22','23') {
    $ch = [int]$chKey
    $cs = $sn[$chKey]
    if (-not $cs) { continue }
    $idx = $html.IndexOf("Chapter $ch ")
    if ($idx -lt 0) { continue }
    $nch = $ch + 1
    $nidx = $html.IndexOf("Chapter $nch ", $idx + 1)
    if ($nidx -lt 0) { $nidx = $idx + 100000 }
    $block = $html.Substring($idx, [Math]::Min($nidx - $idx, 100000))
    $items = [regex]::Matches($block, '(?s)<div class="exam-question-item">(.*?)</details>\s*</div>')
    $chFixed = 0; $si = 0
    foreach ($it in $items) {
        $txt = $it.Value
        if ($txt -match '<pre>') { continue }
        if ($txt -notmatch 'eq-answer-label') { continue }
        $s = $cs[$si % $cs.Count]
        $ae = $txt.LastIndexOf('</div>')
        if ($ae -lt 0) { continue }
        $b = $txt.Substring(0, $ae)
        $a = $txt.Substring($ae)
        $ni = $b + '<pre><code>' + $s + '</code></pre>' + $a
        $html = $html.Replace($txt, $ni)
        $chFixed++; $fixed++; $si++
    }
    Write-Host "Ch $($ch.ToString().PadLeft(2)) : $chFixed added"
}

Set-Content $f $html -NoNewline
$sz1 = [math]::Round($html.Length/1KB,0)
Write-Host "$sz0 -> $sz1 KB | Total: $fixed"
