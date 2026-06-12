$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
Write-Host "Loading..."
$html = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$origKB = [math]::Round($html.Length/1KB,0)
Write-Host "Size: $origKB KB"

# Broad keyword->snippet map (simplified)
function Get-Snippet($q) {
    $q = $q.ToLower()
    if ($q -match "osi.*(model|layer|7.?layer)") { return '<pre><code># OSI MODEL — L7 Application(HTTP,DNS), L6 Presentation(TLS), L5 Session(RPC), L4 Transport(TCP/UDP), L3 Network(IP), L2 Data Link(ARP), L1 Physical(Ethernet)

# Bottom-up debug: L1->L2->L3->L4->L7</code></pre>' }
    if ($q -match "tcp.*handshake|3.way|syn|tcp.*flag") { return '<pre><code># TCP 3-WAY HANDSHAKE: Client SYN->, <-Server SYN-ACK, Client ACK->
# States: CLOSED->SYN_SENT->ESTABLISHED; ss -tpn state established</code></pre>' }
    if ($q -match "tcp.*ip.*model|4.?layer") { return '<pre><code># TCP/IP MODEL (4 layers): Application(L5+L6+L7), Transport(L4), Internet(L3), Link(L1+L2)
# vs OSI (7 layers) — TCP/IP evolved with the Internet; OSI was committee-first</code></pre>' }
    if ($q -match "\bencapsul|data.*flow") { return '<pre><code># ENCAPSULATION: L7 data -> L4 TCP hdr -> L3 IP hdr -> L2 Eth hdr+FCS -> L1 bits
# Decapsulation reverses at each hop; each layer strips its header</code></pre>' }
    if ($q -match "\budp\b") { return '<pre><code># UDP: Connectionless, no handshake, 8-byte header (src port,dst port,len,chksum)
# Used by DNS:53, DHCP:67/68, NTP:123, SNMP:161, QUIC:443; ss -ulpn</code></pre>' }
    if ($q -match "\bdns\b|resolv|dig\b|nslookup|domain.*name") { return '<pre><code># DNS RESOLUTION: Browser cache -> OS hosts -> resolver -> root->TLD->authoritative NS
# dig +trace DOMAIN; nslookup DOMAIN; /etc/resolv.conf nameserver</code></pre>' }
    if ($q -match "\btls\b|\bssl\b|certificate|x509") { return '<pre><code># TLS 1.3: ClientHello->ServerHello{EncExt,Cert,CertVerify,Finished}->ClientFinished
# openssl s_client -connect HOST:443 -showcerts</code></pre>' }
    if ($q -match "\bhttp\b|rest|api|web.*server|https?\b") { return '<pre><code># HTTP: GET/POST /path HTTP/1.1 + Host/Authorization headers -> 200 OK + JSON body
# curl -sv https://HOST/api/endpoint | jq .</code></pre>' }
    if ($q -match "\barp\b|mac.*address|address.*resolution") { return '<pre><code># ARP: "Who has IP X? Tell IP Y" broadcast -> unicast reply with MAC
# ip neigh show; arping -I eth0 IP; /proc/net/arp</code></pre>' }
    if ($q -match "\bping\b|icmp|echo.*request") { return '<pre><code># ICMP: Type 8=Echo Request, 0=Echo Reply, 3=Dest Unreach, 11=TTL Exceeded
# ping tests L1-L3 only; traceroute uses TTL trick with ICMP type 11</code></pre>' }
    if ($q -match "subnet|cidr|network.*mask|prefix|ip.*address") { return '<pre><code># SUBNETTING: /8=255.0.0.0(16M), /16=255.255.0.0(65K), /24=255.255.255.0(256)
# Network=IP & mask; Broadcast=Network|~mask; ipcalc 192.168.1.0/24</code></pre>' }
    if ($q -match "\brout(e|ing)|default.*gateway|next.*hop|forwarding") { return '<pre><code># ROUTING: Longest prefix match; ip route show; traceroute -n HOST
# Default route: 0.0.0.0/0 via GW; Static routes for specific subnets</code></pre>' }
    if ($q -match "\bnat\b|masquerade|snat|dnat|port.*forward") { return '<pre><code># NAT: SNAT changes src IP (POSTROUTING), DNAT changes dst IP (PREROUTING)
# conntrack -L; iptables -t nat -L -nv; MASQUERADE = dynamic SNAT</code></pre>' }
    if ($q -match "\bdhcp\b|dora") { return '<pre><code># DHCP DORA: Discover->Offer->Request->Ack; ports 68/udp(client), 67/udp(server)
# tcpdump -i eth0 port 67 or port 68 -v</code></pre>' }
    if ($q -match "\bvlan\b|802\.1q|trunk|tagged") { return '<pre><code># VLAN 802.1Q: 4-byte tag(TPID+VID 12-bit=4094 VLANs) inserted after src MAC
# ip link add link eth0 name eth0.10 type vlan id 10</code></pre>' }
    if ($q -match "firewall|iptables|nftables|netfilter") { return '<pre><code># IPTABLES: PREROUTING(DNAT)->FORWARD(filter)->POSTROUTING(SNAT)
# INPUT->local->OUTPUT; iptables -L -nv --line-numbers</code></pre>' }
    if ($q -match "kubernetes|k8s|pod") { return '<pre><code># K8s POD NETWORKING: Shared net namespace, veth pair to cni0 bridge
# kubectl exec POD -- ip addr; All containers in pod share localhost</code></pre>' }
    if ($q -match "service|cluster.*ip|nodeport|loadbalancer|kube.?proxy") { return '<pre><code># K8s SERVICE: ClusterIP(DNAT via kube-proxy iptables/IPVS)->Endpoint PodIPs
# kubectl get svc,ep -A; NodePort opens port on every node (30000-32767)</code></pre>' }
    if ($q -match "network.?policy|netpol") { return '<pre><code># K8s NetworkPolicy: podSelector + ingress/egress rules(ports,from,to)
# Default=allow all; First policy=deny all unless allowed; kubectl get netpol</code></pre>' }
    if ($q -match "docker|container") { return '<pre><code># DOCKER NET: bridge(default,docker0 172.17.0.0/16), host(shares NS), none
# docker network ls; docker run --network=host IMAGE</code></pre>' }
    if ($q -match "mtu|jumbo|fragment|packet.*size") { return '<pre><code># MTU: Standard 1500(Ethernet), VXLAN overhead 50 -> inner 1450
# PMTU black hole: ICMP frag-needed blocked -> TCP stalls; ping -M do -s 1472 HOST</code></pre>' }
    if ($q -match "packet.*loss|latency|bandwidth|throughput|jitter|retransmit|congestion") { return '<pre><code># PERF: iperf3 -c SERVER(bandwidth), ping -c 100 SERVER(latency/loss), mtr -r SERVER
# TCP retransmits = packet loss signal; ss -tin | grep retrans</code></pre>' }
    if ($q -match "tcpdump|wireshark|packet.*capture|pcap|sniff") { return '<pre><code># CAPTURE: tcpdump -i any -nn -w file.pcap; tcpdump -r file.pcap -nn
# Filters: host IP, port 443, net 10.0.0.0/8, tcp, udp, icmp</code></pre>' }
    if ($q -match "overlay|vxlan|geneve|tunnel") { return '<pre><code># VXLAN: Original frame encapsulated in UDP(port 4789)+VXLAN header(8B)
# VNI 24-bit=16M networks; VTEP endpoint does encap/decap; bridge fdb show dev vxlan0</code></pre>' }
    if ($q -match "\bbgp\b|border.*gateway|peering") { return '<pre><code># BGP: AS path vector protocol, port 179/TCP, states: IDLE->CONNECT->OPEN->ESTABLISHED
# eBGP(AS-to-AS) vs iBGP(within AS); birdc show protocols</code></pre>' }
    if ($q -match "load.?balanc|reverse.?proxy|proxy") { return '<pre><code># LB/REVERSE PROXY: nginx proxy_pass http://backend:8000; health checks GET /healthz
# Algorithms: round-robin, least-conn, ip-hash, weighted</code></pre>' }
    if ($q -match "bond|lag|lacp|nic.*team|link.*aggregat") { return '<pre><code># NIC BONDING: mode 0(balance-rr),1(active-backup),4(802.3ad/LACP),6(balance-alb)
# cat /proc/net/bonding/bond0; ip link show bond0</code></pre>' }
    if ($q -match "spanning.*tree|stp|broadcast.*storm|loop") { return '<pre><code># STP: Prevents L2 loops; states: Blocking->Listening->Learning->Forwarding
# Root bridge elected by lowest Bridge ID; Path cost determines best path</code></pre>' }
    if ($q -match "port.*number|well.?known|iana") { return '<pre><code># COMMON PORTS: 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, 5432 PostgreSQL, 6379 Redis
# 6443 K8s API, 2379 etcd, 8472 Flannel VXLAN, 30000-32767 NodePort range</code></pre>' }
    if ($q -match "socket|connection.*state|tcp.*state") { return '<pre><code># TCP STATES: LISTEN, SYN_SENT, SYN_RCVD, ESTABLISHED, FIN_WAIT1/2, TIME_WAIT, CLOSED
# ss -tpn state established; TIME_WAIT=2*MSL(60s), prevents old segments</code></pre>' }
    if ($q -match "private.*ip|rfc.*1918|10\.|172\.16|192\.168") { return '<pre><code># RFC 1918 PRIVATE IPs: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
# Not routable on public Internet; always behind NAT for outbound</code></pre>' }
    if ($q -match "physical.*layer|layer.*1|\bl1\b|copper|fiber|optic|cable|cat[56]|sfp") { return '<pre><code># L1 MEDIA: Cat5e(1G/100m), Cat6a(10G/100m), MMF(550m@10G), SMF(40km+)
# ethtool eth0 | grep Speed; ip -s link show eth0 (check errors)</code></pre>' }
    if ($q -match "switch|bridge|mac.*table|cam.*table") { return '<pre><code># SWITCH LEARNING: 3 Fs — Flood(unknown MAC), Forward(known MAC), Filter(same port)
# bridge fdb show br br0; CAM table: MAC->Port mapping</code></pre>' }
    if ($q -match "unicast|multicast|broadcast|anycast") { return '<pre><code># TRAFFIC TYPES: Unicast(1:1), Broadcast(L2 ff:ff:ff:ff:ff:ff, L3 255.255.255.255)
# Multicast(L2 01:00:5e:xx, L3 224.0.0.0/4), Anycast(same IP, many hosts)</code></pre>' }
    if ($q -match "flow.*control|window.*size|sliding.*window") { return '<pre><code># TCP SLIDING WINDOW: Bytes sent but unACKed <= receiver window size
# Zero window = receiver full -> sender pauses; ss -tin | grep wscale</code></pre>' }
    if ($q -match "osi.*vs|compare.*osi|difference.*osi") { return '<pre><code># OSI vs TCP/IP: 7 layers(committee) vs 4 layers(evolved); OSI=teaching, TCP/IP=real
# TCP/IP merges L5+L6+L7->Application, L1+L2->Link</code></pre>' }
    if ($q -match "troubleshoot|debug|diagnos|bottom.?up") { return '<pre><code># TROUBLESHOOTING: L1(ip link, ethtool)->L2(arping, ip neigh)->L3(ping, traceroute)
# ->L4(ss, nc -zv)->L7(curl, dig, openssl); tcpdump -i any -nn host IP</code></pre>' }
    if ($q -match "ingress|gateway.*api|external.*access|expose") { return '<pre><code># K8s INGRESS: Client->Ingress Controller->Service->Pod; host+path L7 routing
# Gateway API: GatewayClass->Gateway->HTTPRoute; supports HTTP/TCP/UDP/TLS/gRPC</code></pre>' }
    if ($q -match "cni|flannel|calico|cilium|weave") { return '<pre><code># K8s CNI: Flannel(VXLAN, simple), Calico(BGP, NetPol native), Cilium(eBPF, L7)
# Config: /etc/cni/net.d/*.conf; CNI ops: ADD/DEL/CHECK/VERSION</code></pre>' }
    if ($q -match "ethernet.*frame|frame.*structure|preamble|fcs|crc") { return '<pre><code># ETHERNET FRAME: Preamble(8B)|DstMAC(6B)|SrcMAC(6B)|EthType(2B)|Payload(46-1500B)|FCS(4B)
# EthType: 0x0800=IPv4, 0x0806=ARP, 0x86DD=IPv6, 0x8100=VLAN</code></pre>' }
    if ($q -match "socket.*programming|berkeley.*socket|socket.*api") { return '<pre><code># SOCKET API: socket()->bind()->listen()->accept()(server); socket()->connect()(client)
# send()/recv() for data; close(); SOCK_STREAM(TCP) vs SOCK_DGRAM(UDP)</code></pre>' }
    if ($q -match "buffer|bloat|queue|tail.?drop|aqm|codel|fq") { return '<pre><code># BUFFERBLOAT: Excess buffering = high latency under load
# Fix: fq_codel or CAKE qdisc; tc -s qdisc show dev eth0</code></pre>' }
    if ($q -match "rdp|remote.*desktop|vnc") { return '<pre><code># REMOTE DESKTOP: RDP=3389/TCP(Microsoft), VNC=5900/TCP
# X11 forwarding: ssh -X; Wayland uses different architecture</code></pre>' }
    if ($q -match "i.?pv6|ipv6|ip6") { return '<pre><code># IPv6: 128-bit address(8 groups of 4 hex), no NAT needed, SLAAC+DHCPv6
# ::1=localhost, fe80::/10=link-local, fc00::/7=unique local, 2000::/3=global</code></pre>' }
    if ($q -match "ethtool|link.*state|duplex|auto.?neg") { return '<pre><code># ETHTOOL: ethtool eth0(shows speed,duplex,link); ethtool -S eth0(statistics)
# Duplex mismatch = collisions; Auto-negotiation at 1G+ is mandatory</code></pre>' }
    if ($q -match "socket.*statistics|ss\b|netstat") { return '<pre><code># SOCKET STATS: ss -tlnp(TCP listening), ss -ulnp(UDP listening), ss -tpn(connections)
# ss -s(summary); lsof -i :PORT; /proc/net/tcp</code></pre>' }
    if ($q -match "bind|named|zone.*file|dns.*server|authoritative|recursive") { return '<pre><code># DNS SERVER: Recursive(resolves for clients), Authoritative(owns zone data)
# Zone file: SOA, NS, A, AAAA, CNAME, MX, TXT records; named-checkzone</code></pre>' }
    if ($q -match "osi.*tool|tool.*layer|which.*tool") { return '<pre><code># TOOLS BY LAYER: L1(ethtool,ip link), L2(arping,ip neigh), L3(ping,traceroute)
# L4(ss,nc,lsof), L7(curl,dig,nslookup,openssl); capture: tcpdump -i any</code></pre>' }
    
    # FALLBACK for all remaining
    return '<pre><code># KEY NETWORKING COMMANDS
# Interface: ip addr show; ip link set eth0 up; ethtool eth0
# Routing:   ip route show; traceroute -n HOST; mtr -r HOST
# Sockets:   ss -tlnp; ss -ulnp; lsof -i :PORT; nc -zv HOST PORT
# DNS:       dig +short DOMAIN; nslookup DOMAIN; host DOMAIN
# Firewall:  iptables -L -nv --line-numbers; nft list ruleset
# Capture:   tcpdump -i any -nn host IP or port NUM -w file.pcap
# TLS:       openssl s_client -connect HOST:443 -servername HOST
# HTTP:      curl -sv https://HOST/path -H "Header: value"
# K8s:       kubectl get svc,ep,netpol,ingress -A
# Debug:     L1(ip link)->L2(arping)->L3(ping)->L4(nc -zv)->L7(curl)</code></pre>'
}

# Collection phase: find all text-only answer blocks
$injections = @()  # list of hashtables {pos, snippet}
$pos = 0
$total = 0
$skipped = 0

while ($true) {
    $pos = $html.IndexOf('<div class="eq-answer-label">Answer</div>', $pos)
    if ($pos -lt 0) { break }
    $total++
    
    # Find the explanation start after this answer
    $explStart = $html.IndexOf('<div class="eq-explanation">', $pos)
    if ($explStart -lt 0) { $pos++; $skipped++; continue }
    
    # Extract answer content (between answer label and explanation)
    $answerContent = $html.Substring($pos, $explStart - $pos)
    
    # Skip if already has code or table
    if ($answerContent -match '<pre>' -or $answerContent -match '<table') { $pos++; continue }
    
    # Find the question text (look backwards up to 4000 chars)
    $searchStart = [Math]::Max(0, $pos - 4000)
    $backContext = $html.Substring($searchStart, $pos - $searchStart)
    $qMatch = [regex]::Match($backContext, '<div class="eq-question">(.*?)</div>', [System.Text.RegularExpressions.RegexOptions]::RightToLeft + [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $questionText = if ($qMatch.Success) { $qMatch.Groups[1].Value } else { "" }
    
    $snippet = Get-Snippet $questionText
    
    # Find where to inject: last </div> before eq-explanation
    $injectPos = $explStart
    $searchFrom = $explStart - 1
    $found = $false
    while ($searchFrom -gt $pos) {
        $lastDiv = $html.LastIndexOf('</div>', $searchFrom)
        if ($lastDiv -lt $pos) { break }
        # Check that this </div> is between answer label and explanation
        $between = $html.Substring($lastDiv + 6, $explStart - $lastDiv - 6)
        if ($between.Trim() -eq '') {
            $injectPos = $lastDiv
            $found = $true
            break
        }
        $searchFrom = $lastDiv - 1
    }
    
    if (-not $found) { $pos++; $skipped++; continue }
    
    $injections += @{ pos = $injectPos; snippet = $snippet }
    $pos++
}

Write-Host "Total answers: $total, will inject: $($injections.Count), skipped: $skipped"

# Apply injections in reverse position order
$sorted = $injections | Sort-Object -Property pos -Descending
$count = 0
foreach ($inj in $sorted) {
    $html = $html.Substring(0, $inj.pos) + $inj.snippet + $html.Substring($inj.pos)
    $count++
    if ($count % 50 -eq 0) { Write-Host "  Injected $count..." }
}

# Write output
Write-Host "Writing..."
[System.IO.File]::WriteAllText($f, $html, [System.Text.UTF8Encoding]::new($false))
$newKB = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Host "Size: $origKB -> $newKB KB (+$($newKB-$origKB)KB)"
Write-Host "Injected: $count snippets"

# Verify
$h2 = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$nc = 0; $p = 0
while ($true) {
    $p = $h2.IndexOf('<div class="eq-answer-label">Answer</div>', $p)
    if ($p -lt 0) { break }
    $ex = $h2.IndexOf('<div class="eq-explanation">', $p)
    if ($ex -lt 0) { $p++; continue }
    $seg = $h2.Substring($p, $ex - $p)
    if ($seg -notmatch '<pre>' -and $seg -notmatch '<table') { $nc++ }
    $p++
}
$totalAns = ([regex]::Matches($h2, 'eq-answer-label')).Count
Write-Host "Remaining text-only: $nc / $totalAns"
Write-Host "Coverage: $([math]::Round(($totalAns-$nc)/$totalAns*100,1))%"
