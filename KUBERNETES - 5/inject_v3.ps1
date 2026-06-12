$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
Write-Host "Loading networking.html..."
$html = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$origKB = [math]::Round($html.Length/1KB,0)
Write-Host "Size: $origKB KB"

function Get-Snippet($q) {
    $q = $q.ToLower()
    if ($q -match "osi.*(model|layer|7.?layer)") { return '<pre><code># OSI MODEL: L7 Application(HTTP,DNS), L6 Presentation(TLS), L5 Session(RPC)
# L4 Transport(TCP/UDP), L3 Network(IP), L2 Data Link(ARP), L1 Physical(Ethernet)
# Debug bottom-up: L1->L2->L3->L4->L7</code></pre>' }
    if ($q -match "tcp.*handshake|3.way|syn|tcp.*flag") { return '<pre><code># TCP 3-WAY: Client SYN(x)->Server, <-Server SYN-ACK(y,ack=x+1), Client ACK(ack=y+1)->
# States: CLOSED->SYN_SENT->ESTABLISHED (client), CLOSED->SYN_RCVD->ESTABLISHED (server)
# ss -tpn state established</code></pre>' }
    if ($q -match "tcp.*ip.*model|4.?layer") { return '<pre><code># TCP/IP MODEL (4 layers): Application(L5+L6+L7), Transport(TCP/UDP), Internet(IP), Link(L1+L2)
# vs OSI (7 layers): TCP/IP evolved with ARPANET; OSI was designed by committee</code></pre>' }
    if ($q -match "\bencapsul|data.*flow") { return '<pre><code># ENCAPSULATION: L7 data -> L4+TCP hdr -> L3+IP hdr -> L2+Eth hdr+FCS -> L1 bits
# Decapsulation reverses at destination: each layer strips its header</code></pre>' }
    if ($q -match "\budp\b") { return '<pre><code># UDP: Connectionless, no handshake, 8B header(srcPort|dstPort|Len|Checksum)
# DNS:53, DHCP:67/68, NTP:123, SNMP:161, QUIC:443; ss -ulpn</code></pre>' }
    if ($q -match "\bdns\b|resolv|dig\b|nslookup|domain.*name") { return '<pre><code># DNS CHAIN: BrowserCache->OS(/etc/hosts)->resolver(1.1.1.1)->root->TLD->authoritative NS
# Record types: A(IPv4), AAAA(IPv6), CNAME(alias), MX(mail), TXT, NS, SOA
# dig +trace DOMAIN; nslookup DOMAIN; resolvectl status</code></pre>' }
    if ($q -match "\btls\b|\bssl\b|certificate|x509") { return '<pre><code># TLS 1.3: ClientHello->ServerHello{EncExt,Cert,CertVerify,Finished}->ClientFinished
# 1-RTT handshake (vs TLS 1.2=2-RTT); openssl s_client -connect HOST:443 -showcerts</code></pre>' }
    if ($q -match "\bhttp\b|rest|api|web.*server|https?\b") { return '<pre><code># HTTP: REQUEST=GET/POST /path HTTP/1.1\nHost+Auth headers\nRESPONSE=200 OK + JSON/HTML
# curl -sv https://HOST/api -H "Authorization: Bearer TOKEN" | jq .
# Status: 2xx=OK, 3xx=redirect, 4xx=client err, 5xx=server err</code></pre>' }
    if ($q -match "\barp\b|mac.*address|address.*resolution") { return '<pre><code># ARP: Broadcast "Who has IP X? Tell IP Y" -> Unicast reply with MAC
# ARP table: ip neigh show; /proc/net/arp; arping -I eth0 IP
# Gratuitous ARP: announces own IP-MAC mapping (used for IP conflict detection)</code></pre>' }
    if ($q -match "\bping\b|icmp|echo.*request") { return '<pre><code># ICMP: Type8=EchoReq, 0=EchoReply, 3=DestUnreach, 11=TTLexceeded
# ping tests L1-L3 only (does NOT test TCP ports!); mtr combines ping+traceroute
# traceroute: sends packets with TTL=1,2,3... reads ICMP Time Exceeded replies</code></pre>' }
    if ($q -match "subnet|cidr|network.*mask|prefix|ip.*address") { return '<pre><code># SUBNETTING: /8=255.0.0.0(16M hosts), /16=255.255.0.0(65K), /24=255.255.255.0(256)
# Network=IP&mask; Broadcast=Network|~mask; Hosts=2^(32-prefix)-2
# ipcalc 192.168.1.0/24; sipcalc eth0</code></pre>' }
    if ($q -match "\brout(e|ing)|default.*gateway|next.*hop|forwarding") { return '<pre><code># ROUTING: Longest prefix match wins; ip route show; ip route get 8.8.8.8
# Default route=0.0.0.0/0 via GW; Static routes for specific subnets
# traceroute -n HOST; birdc show route (for BGP/OSPF)</code></pre>' }
    if ($q -match "\bnat\b|masquerade|snat|dnat|port.*forward") { return '<pre><code># NAT: SNAT changes src IP(POSTROUTING/MASQUERADE), DNAT changes dst IP(PREROUTING)
# conntrack -L; iptables -t nat -L -nv; /proc/net/nf_conntrack</code></pre>' }
    if ($q -match "\bdhcp\b|dora") { return '<pre><code># DHCP DORA: Discover(bcast)->Offer(unicast)->Request(bcast)->Ack(unicast)
# Client=68/udp, Server=67/udp; tcpdump -i eth0 port 67 or port 68 -v</code></pre>' }
    if ($q -match "\bvlan\b|802\.1q|trunk|tagged") { return '<pre><code># VLAN 802.1Q: 4B tag inserted after src MAC(TPID 0x8100 + PCP/DEI/VID 12-bit=4094 VLANs)
# Access port=untagged(one VLAN); Trunk port=tagged(multiple VLANs)
# Linux: ip link add link eth0 name eth0.10 type vlan id 10</code></pre>' }
    if ($q -match "firewall|iptables|nftables|netfilter") { return '<pre><code># IPTABLES FLOW: PREROUTING(DNAT)->FORWARD(filter)->POSTROUTING(SNAT)
# INPUT(filter)->local process->OUTPUT(filter); iptables -L -nv --line-numbers</code></pre>' }
    if ($q -match "kubernetes|k8s|pod") { return '<pre><code># K8s POD NET: Shared net namespace(same IP+ports), veth pair to cni0 bridge on node
# kubectl exec POD -- ip addr; All containers in pod share localhost:PORT</code></pre>' }
    if ($q -match "service|cluster.*ip|nodeport|loadbalancer|kube.?proxy") { return '<pre><code># K8s SERVICE: ClusterIP(virtual IP, DNAT via kube-proxy iptables/IPVS)->Endpoint PodIPs
# NodePort(30000-32767 on every node); LoadBalancer(cloud LB); kubectl get svc,ep</code></pre>' }
    if ($q -match "network.?policy|netpol") { return '<pre><code># K8s NetworkPolicy: podSelector+policyTypes(Ingress/Egress)+rules(from,to,ports)
# Default=allow all; First policy=implicit deny; kubectl get netpol -A</code></pre>' }
    if ($q -match "docker|container") { return '<pre><code># DOCKER NET: bridge(docker0 172.17.0.0/16, veth pairs), host(shares host NS), none
# Overlay(VXLAN for Swarm); docker network ls; docker run --network=host IMG</code></pre>' }
    if ($q -match "mtu|jumbo|fragment|packet.*size") { return '<pre><code># MTU: Ethernet=1500, Jumbo=9000, VXLAN overhead=50->inner MTU=1450
# PMTU black hole: ICMP frag-needed blocked->TCP stalls; ping -M do -s 1472 HOST</code></pre>' }
    if ($q -match "packet.*loss|latency|bandwidth|throughput|jitter|retransmit|congestion") { return '<pre><code># NET PERF: iperf3 -c SERVER(bandwidth), ping -c 100 SERVER(latency/loss)
# ss -tin | grep retrans(retransmits=packet loss); mtr -r SERVER(per-hop stats)</code></pre>' }
    if ($q -match "tcpdump|wireshark|packet.*capture|pcap|sniff") { return '<pre><code># PACKET CAPTURE: tcpdump -i any -nn -w file.pcap; tcpdump -r file.pcap -nn host IP
# BPF filters: host IP, port NUM, net 10.0.0.0/8, tcp, udp, icmp, not port 22</code></pre>' }
    if ($q -match "overlay|vxlan|geneve|tunnel") { return '<pre><code># VXLAN OVERLAY: Original L2 frame in UDP(port 4789)+VXLAN hdr(8B:Flags+VNI 24-bit+Reserved)
# VNI=16M networks; VTEP does encap/decap; bridge fdb show dev vxlan0</code></pre>' }
    if ($q -match "\bbgp\b|border.*gateway|peering") { return '<pre><code># BGP: Path-vector, TCP/179, AS-to-AS(eBGP) or within AS(iBGP)
# States: IDLE->CONNECT->ACTIVE->OPENSENT->OPENCONFIRM->ESTABLISHED
# Attributes: AS_PATH(loop prevention), NEXT_HOP, LOCAL_PREF, MED</code></pre>' }
    if ($q -match "load.?balanc|proxy") { return '<pre><code># LB/PROXY: nginx proxy_pass http://backend:8000; proxy_set_header Host/X-Real-IP
# Algorithms: round-robin, least_conn, ip_hash, random; health_check GET /healthz</code></pre>' }
    if ($q -match "bond|lag|lacp|nic.*team") { return '<pre><code># NIC BONDING: mode0(balance-rr),1(active-backup),2(balance-xor),4(802.3ad/LACP)
# cat /proc/net/bonding/bond0; ip link show bond0</code></pre>' }
    if ($q -match "stp|spanning.*tree|broadcast.*storm|loop") { return '<pre><code># STP(802.1D): Prevents L2 loops; States: Blocking->Listening->Learning->Forwarding
# Root bridge=lowest Bridge ID; Path cost; RSTP(802.1w)=rapid convergence</code></pre>' }
    if ($q -match "port.*number|well.?known|iana") { return '<pre><code># PORTS: 20/21 FTP, 22 SSH, 25 SMTP, 53 DNS, 67/68 DHCP, 80 HTTP, 443 HTTPS
# 5432 PostgreSQL, 6379 Redis, 6443 K8s API, 2379 etcd, 30000-32767 NodePort</code></pre>' }
    if ($q -match "socket|connection.*state|tcp.*state") { return '<pre><code># TCP STATES: LISTEN->SYN_RCVD->ESTABLISHED; FIN_WAIT1->FIN_WAIT2->TIME_WAIT->CLOSED
# TIME_WAIT=2*MSL(60s default); CLOSE_WAIT=app didnt call close(); ss -tpn</code></pre>' }
    if ($q -match "private.*ip|rfc.*1918|10\.|172\.16|192\.168") { return '<pre><code># RFC1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 — NOT routable on Internet
# Carrier-Grade NAT: 100.64.0.0/10(RFC6598); Link-local: 169.254.0.0/16</code></pre>' }
    if ($q -match "physical.*layer|layer.*1|\bl1\b|copper|fiber|optic|cable|cat[56]|sfp") { return '<pre><code># L1 MEDIA: Cat5e(1G/100m), Cat6a(10G/100m), MMF(OM3/OM4,550m), SMF(OS2,40km+)
# ethtool eth0; ip -s link show eth0(check errors/drops/overruns)</code></pre>' }
    if ($q -match "switch|bridge|mac.*table|cam") { return '<pre><code># L2 SWITCH: 3Fs=Flood(unknown),Forward(known),Filter(same port); CAM table MAC->Port
# Managed=VLANS/SNMP/STP; Unmanaged=plug&play; bridge fdb show br br0</code></pre>' }
    if ($q -match "unicast|multicast|broadcast|anycast") { return '<pre><code># TRAFFIC: Unicast(1:1), Broadcast(L2 ff:ff:ff:ff:ff:ff, L3 255.255.255.255)
# Multicast(L2 01:00:5E:xx, L3 224.0.0.0/4), Anycast(same IP many hosts, L3)</code></pre>' }
    if ($q -match "flow.*control|window.*size|sliding.*window") { return '<pre><code># TCP WINDOW: Bytes in flight <= min(cwnd, rwnd); rwnd=receiver buffer space
# Zero window=receiver full->sender pauses; Window scale option multiplies by 2^N
# ss -tin | grep -E "cwnd|rwnd|wscale|retrans"</code></pre>' }
    if ($q -match "osi.*vs|compare.*osi|difference.*osi") { return '<pre><code># OSI(7 layers, committee, teaching) vs TCP/IP(4 layers, evolved, real Internet)
# OSI L5+L6+L7->TCP/IP Application; OSI L1+L2->TCP/IP Link</code></pre>' }
    if ($q -match "troubleshoot|debug|diagnos|bottom.?up") { return '<pre><code># TROUBLESHOOT: L1(ethtool,ip link)->L2(arping,ip neigh)->L3(ping,traceroute)
# ->L4(ss,nc -zv)->L7(curl,dig,openssl); TCPdump: tcpdump -i any -nn host IP</code></pre>' }
    if ($q -match "ingress|gateway.*api|external.*access|expose") { return '<pre><code># K8s INGRESS: Client->IngressCtrl->Service->Pod; host+path L7 rules, TLS termination
# Gateway API: GatewayClass->Gateway->HTTPRoute/TCPRoute; role separation</code></pre>' }
    if ($q -match "cni|flannel|calico|cilium|weave") { return '<pre><code># K8s CNI: Flannel(VXLAN/host-gw), Calico(BGP/IPIP,native NetPol), Cilium(eBPF,L7)
# CNI spec: ADD/DEL/CHECK/VERSION; Config: /etc/cni/net.d/*.conf</code></pre>' }
    if ($q -match "ethernet.*frame|frame.*struct|preamble|fcs|crc") { return '<pre><code># ETH FRAME: Preamble(8B)|DstMAC(6B)|SrcMAC(6B)|802.1Q(4B,opt)|EthType(2B)|Payload(46-1500B)|FCS(4B)
# EthType: 0x0800=IPv4,0x0806=ARP,0x86DD=IPv6,0x8100=VLAN; FCS=CRC32 check</code></pre>' }
    if ($q -match "i.?pv6|ipv6|ip6") { return '<pre><code># IPv6: 128-bit(8x4hex), no NAT, SLAAC+DHCPv6, ::1=localhost
# fe80::/10=link-local, fc00::/7=unique-local, 2000::/3=global unicast
# ip -6 addr show; ping6 fe80::1%eth0; traceroute6</code></pre>' }
    if ($q -match "ethtool|link.*state|duplex|auto.?neg") { return '<pre><code># ETHTOOL: ethtool eth0(speed,duplex,link,auto-neg); ethtool -S eth0(stats)
# ethtool -k eth0(offload features: TSO,GSO,GRO,LRO); ethtool -g eth0(ring buffer)</code></pre>' }
    if ($q -match "ss\b|netstat|socket.*statistic") { return '<pre><code># SOCKET STATS: ss -tlnp(TCP listening), -ulnp(UDP listening), -tpn(all connections)
# ss -s(summary); lsof -i :PORT; cat /proc/net/tcp /proc/net/udp</code></pre>' }
    if ($q -match "buffer|bloat|queue|aqm|fq|codel") { return '<pre><code># BUFFERBLOAT: Excess buffering causes latency spike under load
# Fix: fq_codel or CAKE qdisc; tc qdisc replace dev eth0 root fq_codel</code></pre>' }
    if ($q -match "check.?sum|crc|error.*detect|parity") { return '<pre><code># ERROR DETECTION: CRC32=Ethernet FCS; IP header checksum(1s complement of 16-bit sums)
# TCP checksum covers pseudo-header+segment; UDP checksum is optional in IPv4
# ip -s link show eth0 (shows RX/TX errors, dropped, overruns)</code></pre>' }
    if ($q -match "tool.*layer|layer.*tool|which.*tool") { return '<pre><code># TOOLS BY LAYER: L1(ethtool,ip link), L2(arping,ip neigh,brctl), L3(ping,traceroute,ip route)
# L4(ss,nc,lsof -i), L7(curl,dig,nslookup,openssl s_client); All layers: tcpdump</code></pre>' }
    if ($q -match "windowing|sliding.*window|tcp.*flow") { return '<pre><code># TCP WINDOW: Sliding window allows multiple unACKed segments; Flow control prevents overflow
# AdvertisedWindow shrinks/grows based on receiver buffer; ZeroWindowProbe keeps alive
# ss -tin | grep -E "cwnd|ssthresh|rtt|retrans|wscale"</code></pre>' }
    if ($q -match "socket.*programming|berkeley.*socket|socket.*api") { return '<pre><code># SOCKET API: socket()->bind()->listen()->accept()(server), socket()->connect()(client)
# send()/recv()/close(); SOCK_STREAM(TCP), SOCK_DGRAM(UDP), SOCK_RAW</code></pre>' }
    if ($q -match "rdp|remote.*desktop|vnc") { return '<pre><code># REMOTE ACCESS: RDP=3389/TCP(Windows), VNC=5900/TCP, SSH X11 forwarding=ssh -X
# Apache Guacamole=HTML5 gateway for RDP/VNC/SSH; NoMachine NX protocol</code></pre>' }
    if ($q -match "dns.*server|bind|named|zone.*file|authoritative|recursive") { return '<pre><code># DNS SERVER: Recursive=caches+forwards queries; Authoritative=owns zone SOA record
# Zone file: $TTL, SOA, NS, A, AAAA, CNAME, MX, TXT, SRV; named-checkzone ZONE FILE</code></pre>' }
    if ($q -match "selective.*ack|sack|tcp.*option|timestamp") { return '<pre><code># TCP OPTIONS: MSS(max segment size, avoids fragmentation), SACK(selective ACK, better loss recovery)
# Timestamps(RTTM+PAWS), Window Scale(multiplies window up to 1GB), NOP(padding)</code></pre>' }
    if ($q -match "connection.*refused|connection.*timeout|no.*route") { return '<pre><code># TCP ERRORS: Connection refused=RST(no listener on port); Timeout=SYN dropped(firewall/DOWN)
# No route to host=ICMP unreachable(gateway cant forward); ss -tlnp(check listener)</code></pre>' }
    if ($q -match "multiplex|spdy|http.?2|http.?3|quic|grpc") { return '<pre><code># HTTP EVOLUTION: HTTP/1.1(text,keep-alive), HTTP/2(binary,multiplex,HPACK), HTTP/3(QUIC/UDP)
# gRPC uses HTTP/2; QUIC=UDP 443, 0-RTT handshake, built-in TLS 1.3</code></pre>' }
    if ($q -match "osi.*question|exam.*question|certification|cert.*prep|exam.*tip") { return '<pre><code># EXAM TIPS: Router=L3(by IP), Switch=L2(by MAC), Hub=L1(repeat bits), Firewall=L3/L4/L7
# TLS/SSL=L6, HTTP/DNS/SSH=L7, TCP/UDP=L4; Bottom-up debug ALWAYS L1->L7</code></pre>' }

    # FALLBACK: relevant command reference
    return '<pre><code># NETWORKING COMMANDS REFERENCE
# Check interface: ip addr show; ip link set eth0 up; ethtool eth0
# Check routing:   ip route show; ip route get 8.8.8.8; traceroute -n HOST
# Check ports:     ss -tlnp; ss -ulnp; nc -zv HOST PORT; lsof -i :PORT
# Check DNS:       dig +short DOMAIN; nslookup DOMAIN; host DOMAIN
# Check firewall:  iptables -L -nv --line-numbers; nft list ruleset
# Capture traffic: tcpdump -i any -nn host IP -w capture.pcap
# Check TLS:       openssl s_client -connect HOST:443 -servername HOST
# Test HTTP:       curl -sv https://HOST/path -H "Header: value"
# K8s networking:  kubectl get svc,ep,netpol,ingress -A
# Debug order:     L1(ethtool)->L2(arping)->L3(ping)->L4(nc)->L7(curl)</code></pre>'
}

# Phase 1: Collect all text-only answers and their injection points
# Strategy: insert snippet right BEFORE <div class="eq-explanation"> (safe, no div nesting issues)
$injections = @()
$pos = 0
$total = 0
$skipped = 0

while ($true) {
    $pos = $html.IndexOf('<div class="eq-answer-label">Answer</div>', $pos)
    if ($pos -lt 0) { break }
    $total++
    
    # Find explanation start
    $explStart = $html.IndexOf('<div class="eq-explanation">', $pos)
    if ($explStart -lt 0) { $pos++; $skipped++; continue }
    
    # Check if answer already has code/table
    $answerSeg = $html.Substring($pos, $explStart - $pos)
    if ($answerSeg -match '<pre>' -or $answerSeg -match '<table') { $pos++; continue }
    
    # Extract question text (look backwards)
    $searchBack = [Math]::Max(0, $pos - 4000)
    $backCtx = $html.Substring($searchBack, $pos - $searchBack)
    $qMatch = [regex]::Match($backCtx, '<div class="eq-question">(.*?)</div>', [System.Text.RegularExpressions.RegexOptions]::RightToLeft + [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $qText = if ($qMatch.Success) { $qMatch.Groups[1].Value } else { "" }
    
    $snippet = Get-Snippet $qText
    
    # Insert right before the explanation div
    $injections += @{ pos = $explStart; snippet = $snippet }
    $pos = $explStart + 1  # advance past this insertion point
}

Write-Host "Total answers: $total, to inject: $($injections.Count), skipped: $skipped"

# Phase 2: Apply injections in reverse order
$sorted = $injections | Sort-Object -Property pos -Descending
$cnt = 0
foreach ($inj in $sorted) {
    $html = $html.Substring(0, $inj.pos) + $inj.snippet + $html.Substring($inj.pos)
    $cnt++
    if ($cnt % 50 -eq 0) { Write-Host "  Injected $cnt..." }
}

Write-Host "Writing file..."
[System.IO.File]::WriteAllText($f, $html, [System.Text.UTF8Encoding]::new($false))
$newKB = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Host "Size: $origKB -> $newKB KB (+$($newKB-$origKB)KB)"
Write-Host "Injected: $cnt snippets"

# Verify
$h2 = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$totalAns = ([regex]::Matches($h2, 'eq-answer-label')).Count
$totalPre = ([regex]::Matches($h2, '<pre>')).Count
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
Write-Host "Answers with code in answer div: $($totalAns-$nc) / $totalAns"
Write-Host "Answers with code before explanation: $cnt"
Write-Host "Total <pre> blocks in file: $totalPre"
