
$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = Get-Content $f -Raw
$sz0 = [math]::Round($html.Length/1KB,0)

# Define explanations per chapter (compact format: index 0 = Q1, index 9 = Q10)
$E = @{}
$E[7]  = @('ICMP is L3 control protocol carrying diagnostic info. Key types: 0/8=ping, 3=unreachable, 11=time exceeded. Every SRE uses ICMP daily via ping and traceroute.','Classic exam scenario: ping works but curl fails = ICMP allowed, TCP blocked. Always verify with actual protocol (nc -zv for TCP, dig for DNS, curl for HTTPS).','Traceroute genius: exploits TTL expiration (RFC 1812 mandates ICMP Time Exceeded). *** means router suppresses ICMP or firewall blocks. Use TCP SYN traceroute to bypass.','PMTU black holes: SSH works but HTTPS POST hangs. Fix: lower MTU or TCP MSS clamping. Cloud security groups default-deny ICMP, making this common in AWS/GCP.','Blocking ALL ICMP breaks PMTUD and diagnostics. Best practice: allow Type 3 and 11 from trusted sources. Block Type 8 from untrusted. Cloud SG must explicitly add ICMP rules.','IPv6 depends on ICMPv6 for NDP (ARP replacement), router discovery, DAD. Blocking ICMPv6 breaks IPv6 entirely. IPv6 firewall rules must be more nuanced than IPv4.','ICMP Redirect attack: attacker sends spoofed redirect to hijack traffic (MITM). Always verify accept_redirects=0 on production. One of the oldest network attack vectors.','mtr false positive rule: loss at hop N not carrying to hop N+1 = router rate-limiting ICMP, not real packet loss. Only persistent loss through all hops is real.','ICMP Port Unreachable = no UDP listener. TCP RST = no TCP connection. Different protocols, different layers. Key distinction for accurate diagnosis.','Overlay networks hide physical hops (VXLAN/IP-in-IP encapsulation). Debug underlay first (node-to-node trace), then verify overlay (pod-to-pod). Expected behavior.')
$E[8]  = @('TCP 3-way handshake: SYN→SYN-ACK→ACK establishes state on both ends. After handshake, both in ESTABLISHED. Sequence numbers track bytes; ACK numbers track received bytes.','Each flag: SYN=start, ACK=acknowledge, FIN=close, RST=reset. PSH=push to app immediately, URG=urgent pointer. RST when no listener on target port is connection refused.','TCP connection uniquely identified by 4-tuple (src_ip, src_port, dst_ip, dst_port). Kernel uses this for conntrack tracking. Same client can have multiple connections via different source ports.','TCP options: MSS (max segment size, typically MTU-40), Window Scale (multiply by 2^n), SACK (better loss recovery), Timestamps (RTT measurement). Negotiated during handshake.','CLOSE_WAIT = remote sent FIN, kernel ACKed, but app has NOT called close(). #1 app bug indicator. Stays forever until process exits. Unlike TIME_WAIT, no timeout.','TIME_WAIT is normal cleanup: active closer waits 2*MSL (60s) to ensure remote got final ACK. High TIME_WAIT = many short-lived outbound connections. Mitigate with connection pooling.','State diagram: ESTABLISHED→(recv FIN)→CLOSE_WAIT→(app close)→LAST_ACK→(recv ACK)→CLOSED. Missing close() = stuck in CLOSE_WAIT permanently.','RST aborts connection immediately. Causes: no listener, firewall inject, app crash. Connection refused (got RST) vs Connection timeout (no response) tells you if port is open.','TCP reliable: every byte acknowledged. If ACK not received within RTO (retransmission timeout), segment retransmitted. RTO doubles with each retransmission (exponential backoff).','TCP connection-oriented and reliable at cost of latency/overhead. Three-way handshake = 1 RTT before data. For low-latency, consider QUIC (0-RTT) or TCP Fast Open.')
$E[9]  = @('TCP congestion control: Reno, CUBIC (Linux default), BBR (Google). CWND starts small, grows with ACKs. Slow start: CWND doubles each RTT until threshold then linear growth.','Flow control via receive window (rwnd). Zero window = receiver buffer full, app not reading. Window scaling (RFC 7323) enables >64KB windows for high-BDP paths.','Nagels algorithm combines small writes. Disable with TCP_NODELAY for low-latency. Delayed ACK waits 200ms. Together can cause 200ms+ delays for small request-response.','SACK lets receiver report exactly which segments arrived. Without SACK, one loss causes retransmission of everything after. Critical for high-BDP paths with occasional loss.','BBR uses bandwidth+RTT measurements, not loss. Better for paths with some packet loss. Unlike CUBIC (loss-based), BBR does not interpret loss as congestion.','BDP = bandwidth x RTT. Optimal window size. 10Gbps 50ms RTT needs 62.5MB window. Without window scaling (max 64KB), high-speed links severely underutilized.','TCP buffer auto-tuning: kernel dynamically adjusts socket buffers. Check /proc/sys/net/ipv4/tcp_rmem if throughput unexpectedly low on high-speed links.','SYN cookies: encode connection info in SYN-ACK sequence number. No state allocated until handshake completes. Protects against SYN floods. Auto-enabled under attack.','TCP Fast Open (TFO): data in SYN packet saves one RTT. Need client+server support. Enable: sysctl net.ipv4.tcp_fastopen=3. Big improvement for short connections.','TCP pacing smooths bursts, preventing microbursts that overflow switch buffers. Without pacing, full window sent at line rate causes jitter and packet loss.')
$E[10] = @('UDP connectionless: no handshake, no state, no ACKs. Each datagram independent. Fast but unreliable — app handles loss, ordering, duplication.','UDP ideal for DNS (small queries), real-time media, gaming (low latency), QUIC/HTTP3. Not for file transfers or DB queries that need reliability.','UDP header 8 bytes: src port(2), dst port(2), length(2), checksum(2). Compare TCP 20-60 bytes. No sequence numbers, no ACKs, no window. Minimal overhead.','UDP checksum optional IPv4, mandatory IPv6. NICs offload calculation. Wrong checksums in tcpdump? Disable offloading: ethtool -K eth0 tx off rx off.','QUIC builds TCP-like reliability on UDP: 0-RTT, stream multiplexing without HOLB, connection migration. HTTP/3 runs on QUIC. Becoming default web protocol.','UDP fragmentation: if datagram exceeds path MTU, IP fragments. Fragile and often blocked. Unlike TCP which segments to fit MTU properly.','DNS uses UDP 53 primarily, TCP fallback for >512 byte responses or zone transfers. UDP preferred for low-overhead query-response.','UDP conntrack: timeout-based (no state machine). Default 30s vs TCP ESTABLISHED 5 days. If no packets for timeout period, entry removed.','UDP no built-in congestion control. Apps using UDP for bulk transfer (QUIC) must implement their own congestion control for fairness.','K8s CoreDNS uses UDP 53. NetworkPolicy must allow both UDP and TCP 53. UDP-only DNS silently fails if response >512 bytes and TCP blocked.')

# Batch insert explanations using a simple approach:
# For each chapter, find all </div></details></div> and replace with explanation version
foreach ($ch in 7,8,9,10) {
    $marker = "CH${ch}_FIX_MARKER"
    if ($html -notmatch $marker) { Write-Host "Ch $ch: NO MARKER"; continue }
    $exps = $E[$ch]
    if (-not $exps) { Write-Host "Ch $ch: no explanations"; continue }
    
    # Replace marker with numbered placeholder, then replace placeholders with content
    $block = $marker
    for ($q=1; $q -le 10; $q++) {
        $block += "`nEXP_${ch}_Q${q}_PLACEHOLDER"
    }
    $html = $html -replace $marker, $block
    Write-Host "Ch $ch: placeholders inserted"
    
    # Now replace each placeholder with explanation content
    for ($q=1; $q -le 10; $q++) {
        $placeholder = "EXP_${ch}_Q${q}_PLACEHOLDER"
        $expText = $exps[$q-1]
        $explContent = "</div><div class=`"eq-explanation`"><div class=`"eq-exp-label`">Explanation</div><p>$expText</p></div></details></div>"
        $html = $html -replace $placeholder, $explContent
    }
    Write-Host "Ch $ch: explanations added"
}

Set-Content $f $html -NoNewline
$sz1 = [math]::Round($html.Length/1KB,0)
Write-Host "Done. $sz0 -> $sz1 KB"
