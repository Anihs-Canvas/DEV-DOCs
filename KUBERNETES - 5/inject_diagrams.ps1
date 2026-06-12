# encoding: utf8
$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
Write-Host "Loading networking.html..."
$html = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$origSize = [math]::Round($html.Length/1KB,0)
Write-Host "Original size: $origSize KB"

# Build snippet library using ASCII-safe characters
function Get-Snippet {
    param($qtext)
    $q = $qtext.ToLower()
    
    if ($q -match "osi.*model|7.?layer|osi.*layer") {
        return '<pre><code># OSI MODEL - Quick Reference
# Mnemonic: Please Do Not Throw Sausage Pizza Away
# ===============================================
# L7 Application  <-- HTTP, DNS, SSH, SMTP
# L6 Presentation <-- TLS/SSL, JPEG, ASCII
# L5 Session      <-- NetBIOS, RPC, SOCKS
# L4 Transport    <-- TCP, UDP (ports!)
# L3 Network      <-- IP, ICMP (addressing!)
# L2 Data Link    <-- ARP, Ethernet, VLAN
# L1 Physical     <-- Cables, radio, fiber
# ===============================================
# Bottom-up debug: L1 -> L2 -> L3 -> L4 -> L7</code></pre>'
    }
    if ($q -match "encapsul|data.*flow.*layer|russian.*doll|nesting") {
        return '<pre><code># ENCAPSULATION FLOW (Sending Side)
# +----------+
# | L7: Data | "GET /api/jobs HTTP/1.1"
# +----------+  | L4 adds TCP header
# | L4: Seg  | [TCP hdr| L7 data]
# +----------+  | L3 adds IP header
# | L3: Pkt  | [IP hdr| TCP hdr| L7 data]
# +----------+  | L2 adds Ethernet header+trailer
# | L2: Frame| [Eth hdr| IP hdr| TCP hdr| L7 data| FCS]
# +----------+  | L1 converts to bits
# | L1: Bits | 1011001011100101...
# +----------+</code></pre>'
    }
    if ($q -match "tcp.*(handshake|3.way|flag|state|connection)") {
        return '<pre><code># TCP THREE-WAY HANDSHAKE
# Client                    Server
#   |--- SYN (seq=x) ----->|
#   |<-- SYN-ACK ----------| (seq=y, ack=x+1)
#   |--- ACK (ack=y+1) --->|
#   |                        |
# STATE TRANSITIONS:
# CLOSED -> SYN_SENT -> ESTABLISHED (client)
# CLOSED -> SYN_RCVD  -> ESTABLISHED (server)
#
# Check state: ss -tpn state established</code></pre>'
    }
    if ($q -match "\budp\b") {
        return '<pre><code># UDP - Connectionless Transport
# No handshake, no guarantees, low overhead
# +----------------------------------+
# | Src Port (2B) | Dst Port (2B)    |
# | Length  (2B)  | Checksum (2B)    |
# |            DATA ...              |
# +----------------------------------+
# Common UDP services:
# DNS:53, DHCP:67/68, NTP:123, SNMP:161, QUIC:443
# Check: ss -ulpn</code></pre>'
    }
    if ($q -match "\bdns\b|domain.*name|resolv|dig\b|nslookup") {
        return '<pre><code># DNS RESOLUTION CHAIN
# anihpj.com -> ?
# (1) Browser cache -> (2) OS cache (/etc/hosts)
# (3) Recursive resolver (1.1.1.1 / 8.8.8.8)
# (4) Root nameserver -> (5) .com TLD NS
# (6) anihpj.com authoritative NS -> (7) A record!
#
# Debug: dig +trace anihpj.com
#        nslookup anihpj.com</code></pre>'
    }
    if ($q -match "\btls\b|\bssl\b|transport.*layer.*security|certificate|x509") {
        return '<pre><code># TLS 1.3 HANDSHAKE (1-RTT)
# Client                          Server
#   |-- ClientHello ------------->|
#   |   (supported ciphers,        |
#   |    key_share for ECDHE)      |
#   |<-- ServerHello --------------|
#   |   {EncryptedExtensions}      |
#   |   {Certificate}              |
#   |   {CertVerify}               |
#   |   {Finished}                 |
#   |-- {Finished} -------------->|
#   |   [Encrypted channel open!]  |
# Verify: openssl s_client -connect anihpj.com:443</code></pre>'
    }
    if ($q -match "\bhttp\b|rest.*api|web.*server|https?\b") {
        return '<pre><code># HTTP REQUEST/RESPONSE
# REQUEST:
# GET /api/jobs/ HTTP/1.1
# Host: anihpj.com
# Accept: application/json
# Authorization: Bearer <token>
#
# RESPONSE:
# HTTP/1.1 200 OK
# Content-Type: application/json
# Content-Length: 234
#
# {"jobs":[{"id":1,"title":"DevOps"}]}
#
# Test: curl -sv https://anihpj.com/api/jobs/ | jq .</code></pre>'
    }
    if ($q -match "\barp\b|mac.*address|address.*resolution") {
        return '<pre><code># ARP RESOLUTION
# "Who has 192.168.1.5? Tell 192.168.1.10"
# Node A (192.168.1.10) -> Broadcast ff:ff:ff:ff:ff:ff
# Node B (192.168.1.5)  -> Unicast reply with MAC
#
# +---------------------------------+
# | Hardware Type | Protocol Type   |
# | HW Addr Len   | Proto Addr Len  |
# | Operation(1=req,2=reply)        |
# | Sender MAC    | Sender IP       |
# | Target MAC    | Target IP       |
# +---------------------------------+
# Check: ip neigh show; arping -I eth0 192.168.1.5</code></pre>'
    }
    if ($q -match "subnet|cidr|ip.*address|network.*mask|prefix") {
        return '<pre><code># SUBNETTING QUICK REFERENCE
# CIDR  /8  -> Netmask 255.0.0.0     -> 16,777,216 hosts
# CIDR /16  -> Netmask 255.255.0.0   ->     65,536 hosts
# CIDR /24  -> Netmask 255.255.255.0 ->        256 hosts
# CIDR /28  -> Netmask 255.255.255.240->        16 hosts
#
# Network addr = IP & netmask (bitwise AND)
# Broadcast   = Network | ^wildcard
# Host range  = Network+1 ... Broadcast-1
#
# Calculate: ipcalc 192.168.1.0/24</code></pre>'
    }
    if ($q -match "\brout(e|ing)\b|default.*gateway|next.*hop|forwarding") {
        return '<pre><code># ROUTING TABLE
# Destination     Gateway         Genmask         Iface
# 0.0.0.0         192.168.1.1     0.0.0.0         eth0  <- default
# 192.168.1.0     0.0.0.0         255.255.255.0   eth0  <- local
# 10.0.0.0        192.168.1.254   255.0.0.0       eth0  <- static
#
# Longest prefix match wins!
# ip route show | ip route get 8.8.8.8
# traceroute -n 8.8.8.8</code></pre>'
    }
    if ($q -match "\bnat\b|masquerade|snat|dnat|source.*nat|destination.*nat|port.*forward") {
        return '<pre><code># NAT / MASQUERADE
# +--------------------------------------+
# | Internal: 10.0.0.5:45678             |
# |     | SNAT / MASQUERADE              |
# | External: 203.0.113.10:50001         |
# +--------------------------------------+
# Connection tracking table:
# src=10.0.0.5:45678 -> dst=8.8.8.8:53
#   NAT: 10.0.0.5:45678 -> 203.0.113.10:50001
#
# Check: conntrack -L | iptables -t nat -L -nv</code></pre>'
    }
    if ($q -match "\bdhcp\b|dora|dynamic.*host") {
        return '<pre><code># DHCP DORA PROCESS
# Client                    Server
#   |-- DISCOVER (broadcast)->|  "I need an IP!"
#   |<-- OFFER ---------------|  "Here is 192.168.1.100"
#   |-- REQUEST ------------->|  "I will take it"
#   |<-- ACK -----------------|  "It is yours (lease 24h)"
#
# Ports: client 68/udp, server 67/udp
# Capture: tcpdump -i eth0 port 67 or port 68 -v</code></pre>'
    }
    if ($q -match "\bvlan\b|802\.1q|tagged|trunk") {
        return '<pre><code># VLAN TAGGING (802.1Q)
# +-----------+  Trunk  +-----------+
# | SW1       | ======= | SW2       |
# | VLAN 10:HR| VLAN 10 | VLAN 10:HR|
# | VLAN 20:Eng|VLAN 20 | VLAN 20:Eng|
# +-----------+         +-----------+
# Frame: [MAC dst|MAC src|802.1Q(VID=10)|EtherType|Payload|FCS]
#
# Create: ip link add link eth0 name eth0.10 type vlan id 10
# Show:   cat /proc/net/vlan/config</code></pre>'
    }
    if ($q -match "firewall|iptables|nftables|netfilter") {
        return '<pre><code># IPTABLES CHAIN FLOW
# +----------+   +----------+   +----------+
# | PREROUTING|-> | FORWARD  |-> |POSTROUTING|
# |  (DNAT)   |   | (filter) |   | (SNAT)   |
# +----------+   +----------+   +----------+
#       |              ^
# +----------+        LOCAL PROCESS
# |  INPUT   |-> [socket] -> | OUTPUT  |
# | (filter) |             | (filter)|
# +----------+             +----------+
# List: iptables -L -nv --line-numbers</code></pre>'
    }
    if ($q -match "kubernetes|k8s|pod" -and $q -notmatch "service|network.?policy") {
        return '<pre><code># KUBERNETES POD NETWORKING
# +-----------------------------------------+
# | POD (anihpj)                            |
# |  +---------+  +---------+              |
# |  |app:8000 |  |sidecar  |  <- shared NS|
# |  +----+----+  +----+----+              |
# |       +------+------+                   |
# |        +----+----+                      |
# |        |  eth0   | <- veth pair         |
# |        |10.244.1|                      |
# |        +----+----+                      |
# +-------------+---------------------------+
#          +----+----+
#          |  cni0   | <- bridge on node
#          +---------+
# Check: kubectl exec anihpj-pod -- ip addr</code></pre>'
    }
    if ($q -match "service.*kubernetes|cluster.*ip|nodeport|loadbalancer.*k8s|kube.?proxy") {
        return '<pre><code># KUBERNETES SERVICE (ClusterIP)
# +--------------------------------------+
# | Service: anihpj-svc (10.96.0.10:80)  |
# | Endpoints: 10.244.1.5:8000,         |
# |            10.244.2.7:8000          |
# +-------++------------------------------+
#         | kube-proxy (iptables/IPVS)
#    +----+-----------+
#    |                 |
# +--+--+          +--+--+
# |Pod A|          |Pod B|
# +-----+          +-----+
# Traffic flow: Client -> ClusterIP (DNAT) -> PodIP
# Check: kubectl get endpoints anihpj-svc</code></pre>'
    }
    if ($q -match "network.?policy|netpol") {
        return '<pre><code># KUBERNETES NetworkPolicy
# +----------------------------------+
# | podSelector: app=anihpj          |
# | ingress:                         |
# |  - from: podSelector: app=front  |
# |    ports: [8000/TCP]            |
# |  - from: namespaceSelector:      |
# |      name=monitoring             |
# |    ports: [9090/TCP]            |
# | egress:                          |
# |  - to: podSelector: app=postgres |
# |    ports: [5432/TCP]            |
# +----------------------------------+
# Default: ALLOW all unless policy exists
# Apply:  kubectl apply -f netpol.yaml</code></pre>'
    }
    if ($q -match "\bbgp\b|border.*gateway") {
        return '<pre><code># BGP - Border Gateway Protocol
# +----------+  AS 65001  +----------+
# | Router A |============| Router B |
# | 1.1.1.1  |   BGP      | 2.2.2.2  |
# +----------+            +----------+
# States: IDLE -> CONNECT -> OPENSENT -> OPENCONFIRM -> ESTABLISHED
# Check: birdc show protocols; vtysh -c "show ip bgp"</code></pre>'
    }
    if ($q -match "load.?balanc|reverse.?proxy|proxy") {
        return '<pre><code># REVERSE PROXY & LOAD BALANCING
# Client -> [Reverse Proxy:443] -> [Backend:8000]
#           TLS termination       Plain HTTP
#           Rate limiting         App logic
# 
# nginx proxy_pass example:
# location /api/ {
#     proxy_pass http://anihpj-backend:8000;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
# }</code></pre>'
    }
    if ($q -match "docker|container" -and $q -notmatch "kubernetes|k8s|pod") {
        return '<pre><code># DOCKER NETWORKING MODES
# bridge (default): docker0 (172.17.0.0/16)
#   +------+ +------+
#   | C1   | | C2   | <- veth pairs -> docker0 bridge
#   +--+---+ +--+---+
#      +----+---+
#      +----+----+    +----------+
#      | docker0 |----| NAT/eth0 |-> Internet
#      +---------+    +----------+
# host: Container shares host network stack
# none: No networking</code></pre>'
    }
    if ($q -match "mtu|jumbo|fragment|packet.*size") {
        return '<pre><code># MTU AND FRAGMENTATION
# Standard MTU: 1500 bytes (Ethernet)
# Jumbo frames: 9000 bytes (DC/storage)
# VXLAN overhead: 50 bytes -> inner MTU = 1450
# +------------+--------------------+
# | IP Header  | TCP Header | Data |
# |  20 bytes  |  20 bytes  |1460 B|
# +------------+--------------------+
#                   ^ MTU 1500 ^
# Check: ip link show eth0 | grep mtu
# Test:   ping -M do -s 1472 8.8.8.8</code></pre>'
    }
    if ($q -match "bond|lag|lacp|nic.*team|link.*aggregat") {
        return '<pre><code># NIC BONDING / LACP
# +------+ +------+
# | eth0 | | eth1 |  <- physical NICs
# +--+---+ +--+---+
#    +---+----+
#    +---+----+
#    | bond0  |  <- 2 Gbps (active-backup or LACP)
#    +--------+
# Modes:
# 0 balance-rr    1 active-backup
# 4 802.3ad(LACP) 6 balance-alb
# Show: cat /proc/net/bonding/bond0</code></pre>'
    }
    if ($q -match "tcpdump|wireshark|packet.*capture|pcap|sniff") {
        return '<pre><code># PACKET CAPTURE BASICS
# tcpdump -i eth0 -nn -s0 -w capture.pcap
# +------------------------------------+
# | Timestamp | Src IP | Dst IP | ...  |
# | Proto     | SrcPort| DstPort| ...  |
# | Flags     | Seq#   | Ack#   | ...  |
# | Payload (hex + ASCII)              |
# +------------------------------------+
# Filters:
# tcpdump -i any tcp port 443
# tcpdump -i any host 10.244.1.5
# tcpdump -i any net 10.0.0.0/8</code></pre>'
    }
    if ($q -match "overlay|vxlan|geneve|tunnel") {
        return '<pre><code># OVERLAY NETWORK (VXLAN)
# +--------------------------------------+
# | Original Frame                       |
# | [Eth|IP|TCP|Payload]                 |
# +--------------------------------------+
#            | VXLAN Encapsulation
# +--------------------------------------+
# | Outer Eth|Outer IP|UDP|VXLAN|Original|
# | (underlay network)        |   Frame |
# +--------------------------------------+
# VNI (Virtual Network Identifier): 24-bit -> 16M networks
# VTEP: endpoint that encapsulates/decapsulates
# Check: bridge fdb show dev vxlan0</code></pre>'
    }
    if ($q -match "latency|bandwidth|throughput|jitter|packet.?loss|performance") {
        return '<pre><code># NETWORK PERFORMANCE METRICS
# +----------+------------------------------+
# | Bandwidth| Max data rate (bps)          |
# |Throughput| Actual goodput (bps)         |
# | Latency  | RTT (ms) - time one-way/RT  |
# | Jitter   | Latency variation (ms)      |
# |Pkt Loss  | % of packets dropped        |
# +----------+------------------------------+
# Test: iperf3 -c server -t 30       (bandwidth)
#       ping -c 100 server            (latency/loss)
#       mtr -r server                 (per-hop stats)</code></pre>'
    }
    if ($q -match "check.?sum|crc|error.*detect|parity") {
        return '<pre><code># ERROR DETECTION
# CRC (Cyclic Redundancy Check):
# Sender:   Data -> Polynomial division -> CRC32 appended to frame
# Receiver: Data+CRC -> Same division -> Remainder=0 means OK
#
# Checksum (TCP/IP):
# Data split into 16-bit words -> 1s complement sum -> stored
# Receiver recalculates and compares.
#
# Check interface errors: ip -s link show eth0</code></pre>'
    }
    if ($q -match "icmp|ping|echo.*request") {
        return '<pre><code># ICMP - Internet Control Message Protocol
# Types:
# 0  Echo Reply        8  Echo Request
# 3  Dest Unreachable 11  Time Exceeded (TTL=0)
# 5  Redirect         13/14 Timestamp
#
# ping workflow:
# Client -> ICMP Echo Request (type=8)
# Server -> ICMP Echo Reply   (type=0)
#
# Traceroute uses TTL trick:
# Send UDP/TCP with TTL=1,2,3... and watch for
# ICMP Time Exceeded (type=11) from each hop</code></pre>'
    }
    if ($q -match "osi.*tcp.*ip|tcp.*ip.*model|4.?layer|compare.*model") {
        return '<pre><code># TCP/IP vs OSI MODEL
# +------------+-------------------+--------------+
# | TCP/IP     | OSI Layers        | Protocols    |
# +------------+-------------------+--------------+
# |Application | L7 Application    | HTTP,DNS,SSH |
# |            | L6 Presentation   | TLS,ASCII    |
# |            | L5 Session        | NetBIOS,RPC  |
# +------------+-------------------+--------------+
# |Transport   | L4 Transport      | TCP, UDP     |
# +------------+-------------------+--------------+
# |Internet    | L3 Network        | IP, ICMP     |
# +------------+-------------------+--------------+
# |Link        | L2 Data Link      | Ethernet,ARP |
# |            | L1 Physical       | Cables,WiFi  |
# +------------+-------------------+--------------+</code></pre>'
    }
    if ($q -match "osi.*troubleshoot|debug.*bottom|bottom.?up|layer.*approach") {
        return '<pre><code># BOTTOM-UP TROUBLESHOOTING
# L1 - Physical:  ip link show | ethtool eth0
#                 Check: cable, link state, errors
# L2 - Data Link: ip neigh show | arping
#                 Check: ARP, VLAN, switch forwarding
# L3 - Network:   ping | traceroute | ip route
#                 Check: routing, IP reachability
# L4 - Transport: ss -tlnp | nc -zv host port
#                 Check: port open, firewall rules
# L7 - Application: curl -v | dig | openssl s_client
#                 Check: app logic, TLS, DNS</code></pre>'
    }
    if ($q -match "spanning.*tree|stp|loop|broadcast.*storm") {
        return '<pre><code># SPANNING TREE PROTOCOL (STP)
# Prevents L2 loops in switched networks
# +--------+     +--------+
# | Switch1|=====| Switch2|
# +--------+     +--------+
#      ||             ||
#      ++=====++======++
#         Blocked! (STP)
#
# States: Blocking -> Listening -> Learning -> Forwarding
# Root bridge election: lowest Bridge ID wins
# Path cost: lower = better path to root</code></pre>'
    }
    if ($q -match "port.*number|well.?known.*port|iana") {
        return '<pre><code># COMMON PORT NUMBERS
# +------+----------+------------------------+
# | Port | Protocol | Service                |
# +------+----------+------------------------+
# | 20/21| TCP      | FTP                    |
# | 22   | TCP      | SSH                    |
# | 25   | TCP      | SMTP                   |
# | 53   | UDP/TCP  | DNS                    |
# | 67/68| UDP      | DHCP                   |
# | 80   | TCP      | HTTP                   |
# | 123  | UDP      | NTP                    |
# | 443  | TCP      | HTTPS                  |
# | 5432 | TCP      | PostgreSQL             |
# | 6379 | TCP      | Redis                  |
# | 6443 | TCP      | K8s API Server         |
# +------+----------+------------------------+</code></pre>'
    }
    if ($q -match "socket|connection.*state|tcp.*state") {
        return '<pre><code># TCP CONNECTION STATES
# +-----------+--------------------------------+
# | LISTEN    | Waiting for connection         |
# | SYN_SENT  | Sent SYN, awaiting SYN-ACK    |
# | SYN_RCVD  | Received SYN, sent SYN-ACK    |
# | ESTABLISHED| Connection active            |
# | FIN_WAIT1 | Sent FIN                      |
# | FIN_WAIT2 | Received ACK for FIN          |
# | CLOSE_WAIT| Received FIN, waiting for app |
# | TIME_WAIT | Waiting 2*MSL after close     |
# | CLOSED    | No connection                 |
# +-----------+--------------------------------+
# Check: ss -tpn state established</code></pre>'
    }

    if ($q -match "socket|connection.*state|tcp.*state") {
        return '<pre><code># TCP CONNECTION STATES
# +-----------+--------------------------------+
# | LISTEN    | Waiting for connection         |
# | SYN_SENT  | Sent SYN, awaiting SYN-ACK    |
# | SYN_RCVD  | Received SYN, sent SYN-ACK    |
# | ESTABLISHED| Connection active            |
# | FIN_WAIT1 | Sent FIN                      |
# | FIN_WAIT2 | Received ACK for FIN          |
# | CLOSE_WAIT| Received FIN, waiting for app |
# | TIME_WAIT | Waiting 2*MSL after close     |
# | CLOSED    | No connection                 |
# +-----------+--------------------------------+
# Check: ss -tpn state established</code></pre>'
    }
    if ($q -match "physical.*layer|layer.*1|l1\b|copper|fiber|optic|ethernet.*cable|cat[56]|single.?mode|multi.?mode") {
        return '<pre><code># PHYSICAL LAYER (L1) MEDIA TYPES
# Copper (Twisted Pair):
#   Cat5e: 1 Gbps up to 100m
#   Cat6:  1 Gbps/10 Gbps up to 55m
#   Cat6a: 10 Gbps up to 100m
# Fiber:
#   Multi-mode (MMF): Short reach (550m @ 10G)
#     - 850nm, cheaper transceivers
#   Single-mode (SMF): Long reach (40km+)
#     - 1310/1550nm, more expensive
# Check: ethtool eth0 | grep -E "Speed|Duplex|Link"</code></pre>'
    }
    if ($q -match "switch|bridge|mac.*table|forwarding.*table|cam") {
        return '<pre><code># SWITCH MAC ADDRESS TABLE
# +----------+----------------+---------+
# | MAC Addr | Port           | VLAN    |
# +----------+----------------+---------+
# | aa:bb:01 | Gi1/0/1        | 10      |
# | aa:bb:02 | Gi1/0/2        | 10      |
# | aa:bb:03 | Gi1/0/3        | 20      |
# +----------+----------------+---------+
# 3 Fs: Flood (unknown), Forward (known), Filter (same port)
# Linux: bridge fdb show br br0</code></pre>'
    }
    if ($q -match "mtu.*issue|mtu.*black.?hole|pmtu|path.*mtu|do.*not.*fragment") {
        return '<pre><code># PMTU BLACK HOLE DETECTION
# Problem: ICMP "frag needed" blocked by firewall
# Result: TCP handshake OK, but data transfers stall
#
# Test: ping -M do -s 1472 <target>
# If ping works but SSH/HTTP stalls after connect:
# -> PMTU black hole! Lower MTU on interface.
#
# Fix: ip link set dev eth0 mtu 1400
# Or clamp MSS: iptables -A FORWARD -p tcp \
#   --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360</code></pre>'
    }
    if ($q -match "osi.*vs|compare.*osi|difference.*osi|osi.*tcp") {
        return '<pre><code># OSI vs TCP/IP: KEY DIFFERENCES
# +--------------+------------------+------------------+
# | Aspect       | OSI Model        | TCP/IP Model     |
# +--------------+------------------+------------------+
# | Layers       | 7                | 4                |
# | Design       | Committee-first  | Protocol-first   |
# | Adoption     | Teaching tool    | Internet standard |
# | Session/Pres | Separate layers  | In Application   |
# | Strictness   | Strict layering  | Pragmatic        |
# +--------------+------------------+------------------+
# In practice: Use OSI for teaching/troubleshooting
#              Use TCP/IP for implementation</code></pre>'
    }
    if ($q -match "unicast|multicast|broadcast|anycast|mac.*type") {
        return '<pre><code># TRAFFIC TYPES AT L2/L3
# +-----------+---------------------------+------------------+
# | Type      | L2 MAC                    | L3 IP            |
# +-----------+---------------------------+------------------+
# | Unicast   | Specific MAC (aa:bb:cc)  | Specific IP      |
# | Broadcast | ff:ff:ff:ff:ff:ff        | 255.255.255.255  |
# | Multicast | 01:00:5e:xx:xx:xx       | 224.0.0.0/4      |
# | Anycast   | N/A (L3 concept)         | Same IP, many hosts|
# +-----------+---------------------------+------------------+
# ARP uses broadcast; OSPF uses multicast 224.0.0.5</code></pre>'
    }
    if ($q -match "packet.*loss|retransmit|congestion|flow.*control|window.*size|sliding.*window") {
        return '<pre><code># TCP FLOW CONTROL & CONGESTION
# Sliding Window:
#   Window size = bytes receiver can buffer
#   Sender can send up to window without ACK
#   Window shrinks = receiver is slow
#   Window grows   = receiver caught up
#
# Congestion Control Algorithms:
#   Reno, CUBIC (Linux default), BBR (Google)
# Check: ss -tin | grep -E "cwnd|rtt|retrans"
# Test:  iperf3 -c server (watch retransmits)</code></pre>'
    }
    if ($q -match "internet.*protocol|ipv4|ipv6|ip.*header|ip.*packet") {
        return '<pre><code># IP PACKET HEADER (IPv4)
# +-----+-----+-----+-----+-----+-----+-----+-----+
# |Version| IHL |  DSCP/ECN  |    Total Length     |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# |    Identification     |Flags| Fragment Offset  |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# |  TTL   |   Protocol    |    Header Checksum    |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# |              Source IP Address                 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# |           Destination IP Address               |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# TTL: decremented each hop, packet dies at 0
# Protocol: 1=ICMP, 6=TCP, 17=UDP</code></pre>'
    }
    if ($q -match "osi.*tool|which.*tool|tool.*which|match.*tool|diagnostic.*tool") {
        return '<pre><code># NETWORK DIAGNOSTIC TOOLS BY LAYER
# L1: ethtool, ip link, cable tester
# L2: arping, ip neigh, bridge fdb
# L3: ping, traceroute, ip route, mtr
# L4: ss, nc, netstat, lsof -i
# L7: curl, dig, nslookup, telnet, openssl
# Capture: tcpdump -i any -nn -w file.pcap
# Analyze: wireshark, tshark -r file.pcap
# Performance: iperf3, nuttcp</code></pre>'
    }
    if ($q -match "windowing|sliding.*window|flow.*control|tcp.*flow") {
        return '<pre><code># TCP SLIDING WINDOW
# +---+---+---+---+---+---+---+---+---+---+
# | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |...| Bytes
# +---+---+---+---+---+---+---+---+---+---+
#   ^Sent & ACKed    ^Sent,waiting ^Can send  ^Beyond window
#                     for ACK      (window=4)
# Window shifts right as ACKs arrive
# Zero window = receiver buffer full -> sender stops</code></pre>'
    }
    if ($q -match "selective.*ack|sack|tcp.*option|timestamp") {
        return '<pre><code># TCP OPTIONS
# MSS (Maximum Segment Size):
#   Announced during handshake, avoids fragmentation
# SACK (Selective ACK):
#   ACKs specific byte ranges, not just cumulative
#   Enables faster recovery from multiple losses
# Timestamps:
#   RTTM (Round Trip Time Measurement)
#   PAWS (Protection Against Wrapped Sequences)
# Window Scale:
#   Multiplies window size (up to 1GB window)</code></pre>'
    }
    if ($q -match "cni|container.*network.*interface|flannel|calico|weave|cilium") {
        return '<pre><code># KUBERNETES CNI PLUGINS
# +---------+----------+----------------------+
# | Plugin  | Overlay  | Key Feature          |
# +---------+----------+----------------------+
# | Flannel | VXLAN    | Simple, L3-only      |
# | Calico  | BGP/IPIP | NetworkPolicy native |
# | Cilium  | eBPF     | L7 policies, Hubble  |
# | Weave   | VXLAN    | Encryption, mesh     |
# +---------+----------+----------------------+
# CNI spec: ADD/DEL/DELETE/VERSION operations
# Config: /etc/cni/net.d/*.conf</code></pre>'
    }
    if ($q -match "ingress|gateway.*api|external.*access|expose") {
        return '<pre><code># KUBERNETES INGRESS vs GATEWAY API
# Ingress (traditional):
#   Client -> Ingress Controller -> Service -> Pod
#   Rules: host-based + path-based routing
#   Limited to L7 HTTP(S)
#
# Gateway API (new):
#   GatewayClass -> Gateway -> HTTPRoute/TCPRoute
#   Role-based: Infra admin creates Gateway,
#               App dev creates Routes
#   Supports: HTTP, TCP, UDP, TLS, gRPC</code></pre>'
    }
    if ($q -match "private.*ip|public.*ip|rfc.*1918|10\.|172\.16|192\.168") {
        return '<pre><code># PRIVATE IP ADDRESSES (RFC 1918)
# +--------------------+-------------------+
# | Range              | CIDR              |
# +--------------------+-------------------+
# | 10.0.0.0/8         | 10.0.0.0-10.255.255.255 |
# | 172.16.0.0/12     | 172.16.0.0-172.31.255.255|
# | 192.168.0.0/16    | 192.168.0.0-192.168.255.255|
# +--------------------+-------------------+
# These are NOT routable on the public Internet
# Always behind NAT for outbound traffic</code></pre>'
    }
    if ($q -match "osi.*question|exam.*question|certification|cert.*prep") {
        return '<pre><code># EXAM TIP: OSI MODEL
# Most-tested OSI facts:
# 1. Router  = L3 (Network)  - forwards by IP
# 2. Switch  = L2 (Data Link) - forwards by MAC
# 3. Hub     = L1 (Physical)  - repeats bits
# 4. Firewall= L3/L4 (can be L7 too)
# 5. TLS/SSL = L6 (Presentation)
# 6. HTTP    = L7 (Application)
# 7. TCP/UDP = L4 (Transport)
# Remember: Bottom-up debug ALWAYS L1->L7</code></pre>'
    }

    # FALLBACK: Always add something for remaining text-only answers
    return '<pre><code># KEY NETWORKING COMMANDS
# Interface: ip addr show; ip link set eth0 up
# Routing:   ip route show; traceroute -n HOST
# Sockets:   ss -tlnp; ss -ulnp; lsof -i
# DNS:       dig +short DOMAIN; nslookup DOMAIN
# Firewall:  iptables -L -nv; nft list ruleset
# Capture:   tcpdump -i any -nn host IP
# K8s:       kubectl get svc,ep,netpol -A
# Performance: ping -c 10 HOST; iperf3 -c HOST
# TLS:       openssl s_client -connect HOST:443
# HTTP:      curl -sv https://HOST/path
# Debug:     Always bottom-up: L1->L2->L3->L4->L7</code></pre>'
}

# Collect all answer blocks first
$blocks = @()
$idx = 0
while ($true) {
    $idx = $html.IndexOf('<div class="eq-answer"><div class="eq-answer-label">Answer</div>', $idx)
    if ($idx -lt 0) { break }
    $blocks += $idx
    $idx++
}
Write-Host "Found $($blocks.Count) total answer blocks"

# Build question->snippet map
$injections = @()  # array of (position, snippet)
$total = $blocks.Count
$checked = 0

for ($i = 0; $i -lt $total; $i++) {
    $start = $blocks[$i]
    
    # Get the answer chunk
    $answerEnd = $html.IndexOf('</div>', $start + 60)
    $chunk = $html.Substring($start, [Math]::Min(3000, $answerEnd - $start + 500))
    
    # Skip if already has code or table
    if ($chunk -match '<pre>' -or $chunk -match '<table') { continue }
    
    # Find the question text (look backwards)
    $searchBack = [Math]::Max(0, $start - 3500)
    $context = $html.Substring($searchBack, $start - $searchBack)
    $eqQuestionMatch = [regex]::Match($context, '(?s)<div class="eq-question">(.*?)</div>', [System.Text.RegularExpressions.RegexOptions]::RightToLeft)
    if (-not $eqQuestionMatch.Success) { continue }
    $questionText = $eqQuestionMatch.Groups[1].Value
    
    $snippet = Get-Snippet $questionText
    if (-not $snippet) { 
        $checked++
        continue 
    }
    
    # Find insertion point: closing </div> of the eq-answer div
    $explStart = $html.IndexOf('<div class="eq-explanation">', $start)
    if ($explStart -lt 0) { continue }
    
    $answerClose = $html.LastIndexOf('</div>', $explStart - 1)
    if ($answerClose -lt $start) { continue }
    
    # Make sure we are inserting in the right place
    $between = $html.Substring($answerClose, $explStart - $answerClose)
    if ($between -match 'eq-explanation') { continue }
    
    $injections += @{ pos = $answerClose; snippet = $snippet }
    $checked++
}

Write-Host "Checked: $checked answers, will inject: $($injections.Count) snippets"

# Apply injections in reverse order to preserve positions
$sorted = $injections | Sort-Object -Property pos -Descending
foreach ($inj in $sorted) {
    $html = $html.Substring(0, $inj.pos) + $inj.snippet + $html.Substring($inj.pos)
}

# Write output
Write-Host "Writing file..."
[System.IO.File]::WriteAllText($f, $html, [System.Text.UTF8Encoding]::new($false))
$newSize = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Host "Size: $origSize -> $newSize KB (delta: $($newSize-$origSize) KB)"
Write-Host "Total injected: $($sorted.Count)"

# Verify
$html2 = [System.IO.File]::ReadAllText($f, [System.Text.UTF8Encoding]::new($false))
$withCode = ([regex]::Matches($html2, '<div class="eq-answer">.*?<pre>', [System.Text.RegularExpressions.RegexOptions]::Singleline)).Count
$totalAnswers = ([regex]::Matches($html2, 'eq-answer-label')).Count
Write-Host "Answers with code now: $withCode / $totalAnswers ($([math]::Round($withCode/$totalAnswers*100,1))%)"
