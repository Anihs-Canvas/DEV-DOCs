#!/usr/bin/env python3
"""Rewrite k8s-cluster-structure.html with collapsible sidebar, better visuals"""

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kubernetes Cluster Structure — anihpj-prod | kubeadm v1.31 | Complete Reference</title>
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css"></noscript>
    <style>
        :root {
            --k8s-blue: #326ce5; --k8s-blue-light: #4a8eff; --k8s-blue-dark: #2457b3;
            --k8s-accent: #7b68ee; --k8s-teal: #2dd4bf;
            --dark-bg: #0d1117; --slate-bg: #161b22; --slate-light: #21262d;
            --card-bg: rgba(22,27,34,0.9);
            --text-primary: #e6edf3; --text-secondary: #8b949e; --text-muted: #6e7681;
            --border-color: #30363d; --code-bg: #0d1117;
            --success: #3fb950; --warning: #d29922; --error: #f85149;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6; color: var(--text-primary);
            background: var(--dark-bg); min-height: 100vh;
        }

        a { color: var(--k8s-blue-light); text-decoration: none; transition: color 0.2s; }
        a:hover { color: var(--k8s-accent); }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--dark-bg); }
        ::-webkit-scrollbar-thumb { background: var(--k8s-blue-dark); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--k8s-blue); }

        code.inline {
            background: var(--code-bg); border: 1px solid var(--border-color);
            padding: 2px 7px; border-radius: 4px; font-size: 0.9em;
            color: var(--k8s-teal); font-family: 'JetBrains Mono','Fira Code','Consolas',monospace;
        }

        /* ══ HEADER ══ */
        header {
            position: fixed; top: 0; left: 0; right: 0; z-index: 200;
            background: rgba(13,17,23,0.97); backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 24px; display: flex; align-items: center; justify-content: space-between;
            height: 56px;
        }
        header .logo { display: flex; align-items: center; gap: 10px; }
        header .logo-icon { font-size: 26px; }
        header .logo-text { font-size: 19px; font-weight: 700; color: var(--text-primary); }
        header .logo-text span { color: var(--k8s-blue-light); }
        header .header-meta { font-size: 12px; color: var(--text-secondary); display: flex; gap: 16px; }

        /* ══ SIDEBAR ══ */
        #sidebar {
            position: fixed; top: 56px; left: 0; bottom: 0; width: 310px; z-index: 150;
            background: var(--slate-bg); border-right: 1px solid var(--border-color);
            overflow-y: auto; overflow-x: hidden;
            transition: transform 0.3s ease;
        }
        #sidebar.collapsed { transform: translateX(-100%); }

        #sidebar .sidebar-top {
            padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--border-color);
        }
        #sidebar .sidebar-top .title {
            font-size: 12px; font-weight: 700; color: var(--k8s-blue-light);
            text-transform: uppercase; letter-spacing: 1.5px;
        }
        #sidebar .sidebar-top .btn-group { display: flex; gap: 4px; }
        #sidebar .sidebar-top button {
            background: var(--slate-light); border: 1px solid var(--border-color);
            color: var(--text-secondary); padding: 3px 8px; border-radius: 4px;
            cursor: pointer; font-size: 11px; transition: all 0.15s;
        }
        #sidebar .sidebar-top button:hover { color: var(--text-primary); border-color: var(--k8s-blue); }

        #sidebar nav { padding: 4px 0 40px 0; }

        #sidebar nav .nav-section {
            display: flex; align-items: center; padding: 7px 16px; cursor: pointer;
            color: var(--text-primary); font-size: 13px; font-weight: 700;
            border-left: 3px solid transparent; transition: all 0.15s;
            user-select: none;
        }
        #sidebar nav .nav-section:hover { background: rgba(50,108,229,0.08); border-left-color: var(--k8s-blue); }
        #sidebar nav .nav-section .arrow {
            font-size: 10px; margin-right: 6px; transition: transform 0.2s;
            color: var(--text-muted); min-width: 12px;
        }
        #sidebar nav .nav-section.open .arrow { transform: rotate(90deg); }

        #sidebar nav .sub-items {
            max-height: 0; overflow: hidden; transition: max-height 0.35s ease;
        }
        #sidebar nav .sub-items.open { max-height: 1500px; }

        #sidebar nav .sub-items a {
            display: block; padding: 4px 16px 4px 40px; font-size: 12px;
            color: var(--text-secondary); border-left: 3px solid transparent;
            transition: all 0.15s;
        }
        #sidebar nav .sub-items a:hover {
            color: var(--text-primary); background: rgba(50,108,229,0.06);
            border-left-color: var(--k8s-blue-light); text-decoration: none;
        }
        #sidebar nav .sub-items a.active {
            color: var(--k8s-blue-light); background: rgba(50,108,229,0.1);
            border-left-color: var(--k8s-blue-light);
        }

        /* ══ SIDEBAR TOGGLE ══ */
        #sidebar-toggle {
            position: fixed; top: 66px; left: 310px; z-index: 160;
            background: var(--slate-light); border: 1px solid var(--border-color);
            color: var(--text-secondary); width: 24px; height: 40px; border-radius: 0 6px 6px 0;
            cursor: pointer; font-size: 11px; display: flex; align-items: center;
            justify-content: center; transition: left 0.3s ease;
        }
        #sidebar.collapsed ~ #sidebar-toggle { left: 0; }

        /* ══ MAIN ══ */
        main {
            margin-left: 310px; margin-top: 56px;
            padding: 28px 36px; max-width: 1100px; min-height: calc(100vh - 56px);
            transition: margin-left 0.3s ease;
        }
        #sidebar.collapsed ~ main { margin-left: 0; max-width: 100%; }

        h1 { font-size: 30px; font-weight: 800; margin-bottom: 6px; color: var(--text-primary); }
        h1 span { color: var(--k8s-blue-light); }
        h2 { font-size: 22px; font-weight: 700; margin: 40px 0 16px; color: var(--text-primary); border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
        h2 .section-num { color: var(--k8s-blue-light); }
        h3 { font-size: 17px; font-weight: 700; margin: 28px 0 10px; color: var(--k8s-blue-light); }
        h4 { font-size: 14px; font-weight: 700; margin: 18px 0 8px; color: var(--text-primary); }

        /* ══ BADGES ══ */
        .badge {
            display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 11px; font-weight: 600; margin: 2px;
        }
        .b-cp { background: rgba(123,104,238,0.2); color: #a78bfa; }
        .b-wk { background: rgba(50,108,229,0.2); color: #60a5fa; }
        .b-etcd { background: rgba(45,212,191,0.2); color: #2dd4bf; }
        .b-kubeadm { background: rgba(251,146,60,0.2); color: #fb923c; }
        .b-calico { background: rgba(96,165,250,0.2); color: #60a5fa; }
        .b-ctrd { background: rgba(251,191,36,0.2); color: #fbbf24; }
        .b-nginx { background: rgba(34,197,94,0.2); color: #22c55e; }

        /* ══ CARDS ══ */
        .card-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 12px; margin: 20px 0;
        }
        .card {
            background: var(--slate-light); border: 1px solid var(--border-color);
            border-radius: 10px; padding: 16px; transition: all 0.2s;
            cursor: pointer; display: block;
        }
        a.card-link { text-decoration: none; }
        .card:hover { border-color: var(--k8s-blue); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.35); }
        .card .card-icon { font-size: 22px; margin-bottom: 6px; }
        .card h4 { margin: 0 0 5px; font-size: 14px; color: var(--k8s-blue-light); }
        .card p { margin: 0; font-size: 11px; color: var(--text-secondary); line-height: 1.5; }

        /* ══ TABLES ══ */
        table {
            width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px;
            background: var(--slate-light); border-radius: 8px; overflow: hidden;
            border: 1px solid var(--border-color);
        }
        th { background: var(--slate-bg); color: var(--k8s-blue-light); font-weight: 700; text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--border-color); }
        td { padding: 8px 14px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(50,108,229,0.05); }

        /* ══ CODE ══ */
        pre {
            background: var(--code-bg); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 14px; overflow-x: auto;
            font-size: 13px; line-height: 1.5; margin: 12px 0;
        }
        pre code { font-family: 'JetBrains Mono','Fira Code','Consolas',monospace; }
        .ascii-block {
            background: var(--code-bg); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono','Fira Code','Consolas',monospace;
            font-size: 10.5px; line-height: 1.2; overflow-x: auto; white-space: pre;
            color: var(--text-primary); margin: 14px 0;
        }

        /* ══ SECTIONS ══ */
        .section { margin-bottom: 36px; }
        .section-intro {
            background: rgba(50,108,229,0.05); border: 1px solid var(--border-color);
            border-left: 3px solid var(--k8s-blue); border-radius: 0 8px 8px 0;
            padding: 14px 18px; margin-bottom: 20px;
        }
        .section-intro p { margin: 0 0 6px; font-size: 13px; }
        .section-intro p:last-child { margin-bottom: 0; }
        .api-block {
            background: var(--slate-light); border: 1px solid var(--border-color);
            border-radius: 10px; padding: 22px; margin-bottom: 20px;
        }

        /* ══ INFO BOXES ══ */
        .info { background: rgba(50,108,229,0.08); border: 1px solid rgba(50,108,229,0.25); border-radius: 8px; padding: 11px 15px; margin: 10px 0; font-size: 13px; }
        .warning { background: rgba(210,153,34,0.08); border: 1px solid rgba(210,153,34,0.25); border-radius: 8px; padding: 11px 15px; margin: 10px 0; font-size: 13px; }
        .success { background: rgba(63,185,80,0.08); border: 1px solid rgba(63,185,80,0.25); border-radius: 8px; padding: 11px 15px; margin: 10px 0; font-size: 13px; }
        .error { background: rgba(248,81,73,0.08); border: 1px solid rgba(248,81,73,0.25); border-radius: 8px; padding: 11px 15px; margin: 10px 0; font-size: 13px; }

        /* ══ DIAGRAM BOX ══ */
        .diagram-box {
            background: var(--code-bg); border: 2px solid var(--k8s-blue-dark);
            border-radius: 10px; padding: 18px; margin: 18px 0; overflow-x: auto;
        }
        .diagram-title {
            font-size: 12px; font-weight: 700; color: var(--k8s-blue-light);
            margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;
        }

        /* ══ HERO BANNER ══ */
        .hero-banner {
            background: linear-gradient(135deg, rgba(50,108,229,0.1), rgba(123,104,238,0.08));
            border: 1px solid var(--border-color); border-radius: 14px;
            padding: 28px 32px; margin-bottom: 28px;
        }
        .hero-banner h1 { font-size: 32px; margin-bottom: 4px; }
        .hero-banner .subtitle { font-size: 15px; color: var(--text-secondary); margin-bottom: 14px; }
        .hero-banner .stat-row { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
        .hero-banner .stat-item {
            background: var(--slate-light); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 10px 16px; text-align: center; min-width: 90px;
        }
        .hero-banner .stat-item .val { font-size: 22px; font-weight: 800; color: var(--k8s-blue-light); }
        .hero-banner .stat-item .lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* ══ FOOTER ══ */
        footer {
            text-align: center; padding: 32px 20px; border-top: 1px solid var(--border-color);
            margin-top: 50px; margin-left: 310px; transition: margin-left 0.3s;
        }
        #sidebar.collapsed ~ footer { margin-left: 0; }
        footer p { color: var(--text-muted); font-size: 12px; margin: 3px 0; }
        footer a { color: var(--k8s-blue-light); }

        /* ══ RESPONSIVE ══ */
        @media (max-width: 900px) {
            #sidebar { transform: translateX(-100%); }
            main { margin-left: 0; padding: 16px; }
            footer { margin-left: 0; }
            .card-grid { grid-template-columns: 1fr; }
            .hero-banner .stat-row { justify-content: center; }
        }
    </style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- HEADER -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<header>
    <div class="logo">
        <span class="logo-icon">☸</span>
        <span class="logo-text">anihpj <span>Cluster Structure</span></span>
    </div>
    <div class="header-meta">
        <span>🔧 kubeadm v1.31</span>
        <span>🖥 3 CP · 5 Worker · 2 FE</span>
        <span>🐳 containerd · Calico</span>
        <span>🐧 Ubuntu 24.04</span>
    </div>
</header>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- SIDEBAR -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<aside id="sidebar">
    <div class="sidebar-top">
        <span class="title">📑 Navigation</span>
        <div class="btn-group">
            <button onclick="expandAll()" title="Expand All">⊞ All</button>
            <button onclick="collapseAll()" title="Collapse All">⊟ All</button>
        </div>
    </div>
    <nav>
        <div class="nav-section open" onclick="toggleSub(this)" data-target="sub-0"><span class="arrow">▶</span> ☸ Part 0 — Cluster Inventory</div>
        <div class="sub-items open" id="sub-0">
            <a href="#part-0">Overview</a>
            <a href="#part-0-1">0.1 Node Specs Table</a>
            <a href="#part-0-2">0.2 Cluster Capacity</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-1"><span class="arrow">▶</span> 🔧 Part 1 — kubeadm Deep Dive</div>
        <div class="sub-items" id="sub-1">
            <a href="#part-1">Overview</a>
            <a href="#part-1-1">1.1 What is kubeadm?</a>
            <a href="#part-1-1a">1.1a Bootstrap Timeline</a>
            <a href="#part-1-2">1.2 kubeadm Config File</a>
            <a href="#part-1-3">1.3 kubeadm Phases</a>
            <a href="#part-1-3a">1.3a Phase Dependency Tree</a>
            <a href="#part-1-4">1.4 Certificate Management</a>
            <a href="#part-1-4a">1.4a Certificate Trust Chain</a>
            <a href="#part-1-5">1.5 kubeadm Join</a>
            <a href="#part-1-5a">1.5a Join Sequence (Worker)</a>
            <a href="#part-1-5b">1.5b Join Sequence (CP)</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-2"><span class="arrow">▶</span> 📁 Part 2 — Directory Tree</div>
        <div class="sub-items" id="sub-2">
            <a href="#part-2">Overview</a>
            <a href="#part-2-1">2.1 CP Node Filesystem</a>
            <a href="#part-2-2">2.2 Worker Node Filesystem</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-3"><span class="arrow">▶</span> 🔍 Part 3 — Node Runtime</div>
        <div class="sub-items" id="sub-3">
            <a href="#part-3">Overview</a>
            <a href="#part-3-1">3.1 Process Tree (Worker)</a>
            <a href="#part-3-2">3.2 CP Node Differences</a>
            <a href="#part-3-3">3.3 Pod Lifecycle State Machine</a>
            <a href="#part-3-4">3.4 Container Runtime Architecture</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-4"><span class="arrow">▶</span> 📋 Part 4 — Directory Reference</div>
        <div class="sub-items" id="sub-4">
            <a href="#part-4">Overview</a>
            <a href="#part-4-1">4.1 Filesystem Heat Map</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-5"><span class="arrow">▶</span> 🌐 Part 5 — Network Flow</div>
        <div class="sub-items" id="sub-5">
            <a href="#part-5">Overview</a>
            <a href="#part-5-1">5.1 External Request Flow</a>
            <a href="#part-5-2">5.2 Pod-to-Pod (Same Node)</a>
            <a href="#part-5-3">5.3 Pod-to-Pod (Cross-Node)</a>
            <a href="#part-5-4">5.4 Service to Pod (iptables)</a>
            <a href="#part-5-5">5.5 kube-proxy iptables Chain</a>
            <a href="#part-5-6">5.6 CNI Plugin Chain</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-6"><span class="arrow">▶</span> 🧠 Part 6 — etcd: The Brain</div>
        <div class="sub-items" id="sub-6">
            <a href="#part-6">Overview</a>
            <a href="#part-6-1">6.1 What is etcd?</a>
            <a href="#part-6-2">6.2 Raft Consensus</a>
            <a href="#part-6-3">6.3 Data Model</a>
            <a href="#part-6-4">6.4 API Server ↔ etcd</a>
            <a href="#part-6-5">6.5 MVCC & Revisions</a>
            <a href="#part-6-6">6.6 etcd Topology</a>
            <a href="#part-6-7">6.7 Performance</a>
            <a href="#part-6-8">6.8 Backup, Restore, Defrag</a>
            <a href="#part-6-9">6.9 Security</a>
            <a href="#part-6-10">6.10 Troubleshooting</a>
            <a href="#part-6-11">6.11 etcdctl Reference</a>
            <a href="#part-6-12">6.12 Component Map</a>
            <a href="#part-6-13">6.13 Disaster Scenarios</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-7"><span class="arrow">▶</span> 🔄 Part 7 — Day 2 Operations</div>
        <div class="sub-items" id="sub-7">
            <a href="#part-7">Overview</a>
            <a href="#part-7-1">7.1 Upgrading with kubeadm</a>
            <a href="#part-7-2">7.2 Adding New Nodes</a>
            <a href="#part-7-3">7.3 Renewing Certificates</a>
            <a href="#part-7-4">7.4 Troubleshooting</a>
            <a href="#part-7-5">7.5 Upgrade Timeline</a>
            <a href="#part-7-6">7.6 Certificate Lifecycle</a>
            <a href="#part-7-7">7.7 Decision Tree</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-8"><span class="arrow">▶</span> 🚀 Part 8 — Bootstrap Walkthrough</div>
        <div class="sub-items" id="sub-8">
            <a href="#part-8">Overview</a>
            <a href="#part-8-1">8.1 Prerequisites</a>
            <a href="#part-8-2">8.2 Init Cluster (cp-01)</a>
            <a href="#part-8-3">8.3 Join CP Nodes</a>
            <a href="#part-8-4">8.4 Join Workers</a>
            <a href="#part-8-5">8.5 Install Calico</a>
            <a href="#part-8-6">8.6 Deploy Apps</a>
        </div>

        <div class="nav-section" onclick="toggleSub(this)" data-target="sub-9"><span class="arrow">▶</span> ⚡ Part 9 — Cheat Sheet</div>
        <div class="sub-items" id="sub-9">
            <a href="#part-9">Overview</a>
        </div>
    </nav>
</aside>

<!-- SIDEBAR TOGGLE -->
<button id="sidebar-toggle" onclick="toggleSidebarCollapse()" title="Toggle Sidebar">◀</button>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- MAIN CONTENT -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<main>

    <!-- HERO BANNER -->
    <div class="hero-banner">
        <h1>☸ anihpj <span>Kubernetes Cluster Structure</span></h1>
        <p class="subtitle">Complete under-the-hood reference — every directory, component, and workflow in the anihpj-prod cluster</p>
        <p style="margin-bottom:6px;">
            <span class="badge b-kubeadm">kubeadm v1.31.0</span>
            <span class="badge b-cp">3 Control Plane</span>
            <span class="badge b-wk">5 Worker Nodes</span>
            <span class="badge b-etcd">etcd v3.5</span>
            <span class="badge b-calico">Calico v3.28</span>
            <span class="badge b-ctrd">containerd v1.7</span>
            <span class="badge b-nginx">nginx v1.27</span>
        </p>
        <div class="stat-row">
            <div class="stat-item"><div class="val">10</div><div class="lbl">Total Nodes</div></div>
            <div class="stat-item"><div class="val">54</div><div class="lbl">vCPUs</div></div>
            <div class="stat-item"><div class="val">212 GB</div><div class="lbl">Total RAM</div></div>
            <div class="stat-item"><div class="val">2.3 TB</div><div class="lbl">SSD Storage</div></div>
            <div class="stat-item"><div class="val">1,100</div><div class="lbl">Max Pods</div></div>
            <div class="stat-item"><div class="val">10.244.0.0/16</div><div class="lbl">Pod CIDR</div></div>
        </div>
    </div>

    <!-- INTRODUCTION -->
    <section class="section" id="introduction">
        <h2>📖 <span class="section-num">Introduction</span> — What This Document Covers</h2>
        <div class="section-intro">
            <p>This is the <strong>complete reference</strong> for the <code class="inline">anihpj-prod</code> Kubernetes cluster. It covers every aspect — from hardware specs to container runtime internals, from the kubeadm bootstrap process to the etcd Raft consensus that stores all cluster state.</p>
            <p>Built with <code class="inline">kubeadm v1.31.0</code> on <strong>Ubuntu 24.04 LTS</strong> across 10 nodes, using <strong>containerd</strong> as the container runtime and <strong>Calico</strong> for BGP-based Pod networking with no overlay.</p>
        </div>

        <!-- TOC CARDS -->
        <div class="card-grid">
            <a href="#part-0" class="card-link"><div class="card"><div class="card-icon">☸</div><h4>Part 0 — Cluster Inventory</h4><p>All 10 nodes: IPs, specs, roles, resource budget.</p></div></a>
            <a href="#part-1" class="card-link"><div class="card"><div class="card-icon">🔧</div><h4>Part 1 — kubeadm Deep Dive</h4><p>Phases, certs, bootstrap tokens, join sequences.</p></div></a>
            <a href="#part-2" class="card-link"><div class="card"><div class="card-icon">📁</div><h4>Part 2 — Directory Tree</h4><p>Complete filesystem for CP and worker nodes.</p></div></a>
            <a href="#part-3" class="card-link"><div class="card"><div class="card-icon">🔍</div><h4>Part 3 — Node Runtime</h4><p>Process trees, configs, Pod lifecycle, runtime arch.</p></div></a>
            <a href="#part-4" class="card-link"><div class="card"><div class="card-icon">📋</div><h4>Part 4 — Directory Reference</h4><p>Quick lookup + filesystem heat map per node type.</p></div></a>
            <a href="#part-5" class="card-link"><div class="card"><div class="card-icon">🌐</div><h4>Part 5 — Network Flow</h4><p>Request-to-Pod path, Pod routing, kube-proxy, CNI.</p></div></a>
            <a href="#part-6" class="card-link"><div class="card"><div class="card-icon">🧠</div><h4>Part 6 — etcd: The Brain</h4><p>Raft, MVCC, backup/restore, security, disaster recovery.</p></div></a>
            <a href="#part-7" class="card-link"><div class="card"><div class="card-icon">🔄</div><h4>Part 7 — Day 2 Operations</h4><p>Upgrades, node adds, cert renewal, troubleshooting.</p></div></a>
            <a href="#part-8" class="card-link"><div class="card"><div class="card-icon">🚀</div><h4>Part 8 — Bootstrap Walkthrough</h4><p>Copy-paste scripts: bare metal → running cluster.</p></div></a>
            <a href="#part-9" class="card-link"><div class="card"><div class="card-icon">⚡</div><h4>Part 9 — Cheat Sheet</h4><p>Daily ops: health checks, etcdctl, diagnostics, reset.</p></div></a>
        </div>

        <!-- CLUSTER TOPOLOGY -->
        <div class="diagram-box">
            <div class="diagram-title">🏗 Cluster Topology — 3 CP + 5 Worker + 2 Frontend</div>
            <div class="ascii-block">┌──────────────────────────────────────────────────────────────────────────────┐
│                         ANIHPJ CLUSTER TOPOLOGY                               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                    CONTROL PLANE (3 nodes)                          │    │
│   │  ┌──────────┐     ┌──────────┐     ┌──────────┐                    │    │
│   │  │  cp-01   │◄───►│  cp-02   │◄───►│  cp-03   │   etcd Raft       │    │
│   │  │10.0.0.10 │     │10.0.0.11 │     │10.0.0.12 │   + API server     │    │
│   │  │ Leader   │     │ Follower │     │ Follower │   + scheduler      │    │
│   │  └────┬─────┘     └────┬─────┘     └────┬─────┘   + ctrl-mgr       │    │
│   │       │                │                │                           │    │
│   └───────┼────────────────┼────────────────┼───────────────────────────┘    │
│           │                │                │                                  │
│   ┌───────┼────────────────┼────────────────┼───────────────────────────┐    │
│   │       │          WORKER NODES (5 nodes) │                            │    │
│   │  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌──────────┐ ┌──────────┐  │    │
│   │  │  wk-01   │ │  wk-02   │ │  wk-03   │ │  wk-04   │ │  wk-05   │  │    │
│   │  │10.0.4.21 │ │10.0.4.22 │ │10.0.4.23 │ │10.0.4.24 │ │10.0.4.25 │  │    │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                    FRONTEND NODES (2 nodes)                         │    │
│   │  ┌──────────┐     ┌──────────┐                                      │    │
│   │  │  fe-01   │     │  fe-02   │    Nginx Ingress + TLS termination   │    │
│   │  │10.0.5.10 │     │10.0.5.11 │                                      │    │
│   │  └──────────┘     └──────────┘                                      │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘</div>
        </div>

        <!-- KEY STATS -->
        <table>
            <tr><th style="width:220px;">Metric</th><th>Value</th></tr>
            <tr><td>Cluster Name</td><td><code class="inline">anihpj-prod</code></td></tr>
            <tr><td>Kubernetes Version</td><td>v1.31.0 (kubeadm bootstrapped)</td></tr>
            <tr><td>Total Nodes</td><td>10 — 3 Control Plane + 5 Worker + 2 Frontend</td></tr>
            <tr><td>Total vCPUs</td><td>54 cores across all nodes</td></tr>
            <tr><td>Total RAM</td><td>212 GB across all nodes</td></tr>
            <tr><td>Total Disk</td><td>2.3 TB SSD (all nodes)</td></tr>
            <tr><td>Pod CIDR</td><td>10.244.0.0/16 (Calico default)</td></tr>
            <tr><td>Service CIDR</td><td>10.96.0.0/12</td></tr>
            <tr><td>API Server VIP</td><td>10.0.0.100:6443 (HAProxy load-balanced)</td></tr>
            <tr><td>Container Runtime</td><td>containerd v1.7 (CRI, systemd cgroup driver)</td></tr>
            <tr><td>CNI Plugin</td><td>Calico v3.28 (BGP routing, no overlay)</td></tr>
            <tr><td>Max Pods</td><td>1,100 (110 per node × 10 nodes)</td></tr>
            <tr><td>Operating System</td><td>Ubuntu 24.04 LTS (kernel 6.8)</td></tr>
        </table>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PLACEHOLDER SECTIONS -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-0">
        <h2>☸ <span class="section-num">Part 0</span> — Cluster Inventory: All Nodes at a Glance</h2>
        <div class="section-intro"><p>Complete hardware and software inventory for all 10 nodes. 3 CP nodes run co-located etcd, API server, scheduler, and controller manager. 5 workers run application Pods. 2 frontend nodes terminate TLS via Nginx.</p></div>
    </section>
    <section class="section" id="part-1">
        <h2>🔧 <span class="section-num">Part 1</span> — kubeadm Deep Dive: How the Cluster Is Built</h2>
        <div class="section-intro"><p>kubeadm generates certificates, writes static Pod manifests, starts etcd and control plane components, and manages the join process. Covers every phase, certificate, and join sequence.</p></div>
    </section>
    <section class="section" id="part-2">
        <h2>📁 <span class="section-num">Part 2</span> — Cluster-Level Directory Tree</h2>
        <div class="section-intro"><p>Complete filesystem layout for control plane and worker nodes — every file and directory created by kubeadm, with additions for anihpj applications.</p></div>
    </section>
    <section class="section" id="part-3">
        <h2>🔍 <span class="section-num">Part 3</span> — Inside a Single Node: Runtime Deep Dive</h2>
        <div class="section-intro"><p>Process trees, kubelet/containerd configs, Pod lifecycle state machine, and container runtime architecture — what actually runs on a node.</p></div>
    </section>
    <section class="section" id="part-4">
        <h2>📋 <span class="section-num">Part 4</span> — Key Directory Quick Reference</h2>
        <div class="section-intro"><p>Quick lookup table + filesystem heat map showing what lives where on each node type.</p></div>
    </section>
    <section class="section" id="part-5">
        <h2>🌐 <span class="section-num">Part 5</span> — Network Flow: How a Request Reaches a Pod</h2>
        <div class="section-intro"><p>End-to-end: external request → LB → Nginx → kube-proxy iptables → Pod. Includes Pod routing, Service DNAT, and CNI plugin chains.</p></div>
    </section>
    <section class="section" id="part-6">
        <h2>🧠 <span class="section-num">Part 6</span> — etcd: The Brain of the Cluster</h2>
        <div class="section-intro"><p>Raft consensus, data model, MVCC, performance, backup/restore, security, troubleshooting, and disaster recovery scenarios.</p></div>
    </section>
    <section class="section" id="part-7">
        <h2>🔄 <span class="section-num">Part 7</span> — kubeadm Day 2 Operations</h2>
        <div class="section-intro"><p>Upgrading the cluster, adding new nodes, renewing certificates, troubleshooting common issues, and maintenance timelines.</p></div>
    </section>
    <section class="section" id="part-8">
        <h2>🚀 <span class="section-num">Part 8</span> — Complete Cluster Bootstrap Walkthrough</h2>
        <div class="section-intro"><p>Copy-paste shell scripts: prerequisites → kubeadm init → join CP → join workers → install Calico → deploy anihpj applications.</p></div>
    </section>
    <section class="section" id="part-9">
        <h2>⚡ <span class="section-num">Part 9</span> — Day 2 Maintenance Cheat Sheet</h2>
        <div class="section-intro"><p>Quick reference: cluster health, etcd operations, certificate management, node maintenance, diagnostics, and cluster reset.</p></div>
    </section>
</main>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- FOOTER -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<footer>
    <h3>☸ anihpj Kubernetes Cluster Structure</h3>
    <p>Complete reference for the anihpj-prod cluster — kubeadm v1.31.0 on Ubuntu 24.04 LTS</p>
    <p style="margin-top:8px;">
        <a href="https://kubernetes.io/docs/" target="_blank" rel="noopener">Kubernetes Docs</a> ·
        <a href="https://kubeadm.io" target="_blank" rel="noopener">kubeadm</a> ·
        <a href="https://etcd.io" target="_blank" rel="noopener">etcd</a> ·
        <a href="https://containerd.io" target="_blank" rel="noopener">containerd</a> ·
        <a href="https://docs.tigera.io/calico" target="_blank" rel="noopener">Calico</a> ·
        <a href="https://nginx.org" target="_blank" rel="noopener">Nginx</a>
    </p>
    <p style="margin-top:10px;color:var(--text-muted);">Last updated: 2026-06-06 · anihpj infrastructure team</p>
</footer>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- SCRIPTS -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>
<script>
    function toggleSidebarCollapse() {
        var sb = document.getElementById('sidebar');
        var btn = document.getElementById('sidebar-toggle');
        sb.classList.toggle('collapsed');
        btn.textContent = sb.classList.contains('collapsed') ? '▶' : '◀';
    }

    function toggleSub(el) {
        var targetId = el.getAttribute('data-target');
        var sub = document.getElementById(targetId);
        if (!sub) return;
        el.classList.toggle('open');
        sub.classList.toggle('open');
    }

    function expandAll() {
        document.querySelectorAll('.nav-section').forEach(function(el) { el.classList.add('open'); });
        document.querySelectorAll('.sub-items').forEach(function(el) { el.classList.add('open'); });
    }

    function collapseAll() {
        document.querySelectorAll('.nav-section').forEach(function(el) { el.classList.remove('open'); });
        document.querySelectorAll('.sub-items').forEach(function(el) { el.classList.remove('open'); });
    }

    // Active section highlighting via IntersectionObserver
    (function() {
        var sections = document.querySelectorAll('.section[id]');
        var links = document.querySelectorAll('#sidebar .sub-items a');
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var id = entry.target.getAttribute('id');
                    links.forEach(function(l) {
                        l.classList.remove('active');
                        if (l.getAttribute('href') === '#' + id) l.classList.add('active');
                    });
                }
            });
        }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 });
        sections.forEach(function(s) { observer.observe(s); });
    })();
</script>
</body>
</html>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)

lines = html.count('\n')
print(f'Written: {lines} lines')
print(f'Collapsible sections: {html.count("nav-section")}')
print(f'Sub-menus: {html.count("sub-items open")}')
print(f'TOC cards: 10')
print('Done.')
