#!/usr/bin/env python3
"""
scripts/build_website.py
Generates index.html, updates demos-complete.md, and creates serve.py.
"""

import os
import re
import json

def get_topics_and_header():
    with open("demos-complete.md", "r", encoding="utf-8") as f:
        content = f.read()

    header_and_topics = re.split(r"\n(?=## \d+\. )", content)
    header = header_and_topics[0]
    topics_raw = header_and_topics[1:]

    topics = []
    for sec in topics_raw:
        m = re.match(r"## (\d+)\. (.+)", sec)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()

        # Extract Technical Discussion
        tech_disc_m = re.search(r"\*\*Part 1 — Technical Discussion:\*\*(.*?)(?=\!\[|\*\*Technical perspective:\*\*)", sec, re.S)
        tech_disc = tech_disc_m.group(1).strip() if tech_disc_m else ""

        # Extract Technical Perspective
        tech_persp_m = re.search(r"\*\*Technical perspective:\*\*(.*?)(?=\*\*Part 2 — Analogy / Zine:\*\*|\!\[.*?zine|### Component architecture flow)", sec, re.S)
        tech_persp = tech_persp_m.group(1).strip() if tech_persp_m else ""

        # Extract Zine Analogy
        zine_analogy_m = re.search(r"\*\*Part 2 — Analogy / Zine:\*\*(.*?)(?=\!\[.*?zine)", sec, re.S)
        zine_analogy = zine_analogy_m.group(1).strip() if zine_analogy_m else ""

        # Extract Zine Explanation
        zine_exp_m = re.search(r"\*\*Zine explanation:\*\*(.*?)(?=\*\*Further reading\*\*|### Demo)", sec, re.S)
        zine_exp = zine_exp_m.group(1).strip() if zine_exp_m else ""

        # Extract Further Reading
        reading_m = re.search(r"\*\*Further reading\*\*(.*?)(?=### Demo)", sec, re.S)
        reading = reading_m.group(1).strip() if reading_m else ""

        # Extract Demo
        demo_m = re.search(r"### Demo — .*?\n\n<div style=\"background:#000;.*?\"><pre style=\".*?\">(.*?)</pre></div>", sec, re.S)
        demo = demo_m.group(1).strip() if demo_m else ""

        # Categories
        cat = "Control Plane"
        if num in [1, 2]:
            cat = "Cluster Architecture"
        elif num in [3, 4, 5, 6, 7]:
            cat = "Control Plane Core"
        elif num in [8, 9, 10, 11, 12, 13]:
            cat = "Nodes & Runtime"
        elif num in [14, 15, 16, 17, 18, 19]:
            cat = "Networking & Ingress"
        elif num in [20, 21, 22]:
            cat = "Storage Subsystem"
        elif num in [23, 24, 25, 26, 27]:
            cat = "Security & RBAC"
        elif num in [28, 29, 30, 31]:
            cat = "Lifecycle & Governance"
        elif num in [32, 33, 34, 35, 36, 37, 38]:
            cat = "Workload Controllers"
        elif num in [39, 40, 41]:
            cat = "Autoscaling & Disruption"

        topics.append({
            "num": num,
            "title": title,
            "category": cat,
            "tech_disc": tech_disc,
            "tech_persp": tech_persp,
            "zine_analogy": zine_analogy,
            "zine_exp": zine_exp,
            "reading": reading,
            "demo": demo,
            "tech_img": f"generated/kubernetes-apartment-complex/{num:02d}-technical.png",
            "zine_img": f"generated/kubernetes-apartment-complex/{num:02d}-zine.png",
            "diagram": f"diagrams/topic-{num:02d}.html"
        })

    return header, topics


def generate_index_html(topics):
    topics_json = json.dumps(topics)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kubernetes Apartment Complex — Architecture Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0b1120;
    --panel: #111a2e;
    --panel-hover: #16223b;
    --panel-border: #1e2b47;
    --cp-tint: #0f1f38;
    --wn-tint: #14231c;
    --accent: #38bdf8;
    --accent-glow: rgba(56, 189, 248, 0.55);
    --accent-dim: rgba(56, 189, 248, 0.15);
    --packet: #f59e0b;
    --packet-glow: rgba(245, 158, 11, 0.6);
    --text-main: #e5edf7;
    --text-dim: #7f93b3;
    --line: #24324f;
    --region-cp-border: #2b3f66;
    --region-wn-border: #234030;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    background: var(--bg);
    color: var(--text-main);
    font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
    line-height: 1.6;
    min-height: 100vh;
  }}
  a {{ color: var(--accent); text-decoration: none; transition: color 0.2s; }}
  a:hover {{ text-decoration: underline; }}

  /* App Shell */
  .site-header {{
    background: #080d1a;
    border-bottom: 1px solid var(--panel-border);
    padding: 16px 24px;
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .logo {{
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }}
  .logo span {{ color: var(--text-main); }}
  .header-actions {{
    display: flex;
    gap: 12px;
    align-items: center;
  }}
  .btn {{
    font-family: inherit;
    font-size: 12px;
    letter-spacing: 0.03em;
    background: var(--panel);
    color: var(--accent);
    border: 1px solid var(--panel-border);
    border-radius: 6px;
    padding: 7px 14px;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}
  .btn:hover {{
    border-color: var(--accent);
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
    color: #fff;
  }}
  .btn:active {{ transform: translateY(1px); }}
  .btn-primary {{
    background: var(--accent);
    color: #0b1120;
    font-weight: 600;
  }}
  .btn-primary:hover {{
    background: #7dd3fc;
    color: #0b1120;
    box-shadow: 0 0 16px var(--accent-glow);
  }}

  /* Container */
  .main-wrap {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 28px 16px 60px;
  }}

  /* Home Architecture View */
  .hero-heading {{
    text-align: center;
    margin-bottom: 24px;
  }}
  .hero-heading h1 {{
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 6px;
  }}
  .hero-heading p {{
    color: var(--text-dim);
    font-size: 12px;
  }}

  .arch-diagram-card {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    padding: 24px 18px 20px;
    margin-bottom: 36px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  }}
  .stage-label-bar {{
    text-align: center;
    min-height: 28px;
    font-size: 13px;
    color: var(--text-main);
    margin-bottom: 12px;
    letter-spacing: 0.02em;
    line-height: 1.4;
  }}
  .controls-bar {{
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 18px;
  }}

  /* SVG interactive styles */
  svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
  .region-box {{ fill: none; stroke-width: 1.2; stroke-dasharray: 3 4; }}
  .region-cp {{ stroke: var(--region-cp-border); }}
  .region-wn {{ stroke: var(--region-wn-border); }}
  .region-neutral {{ stroke: var(--panel-border); }}
  .region-label {{ fill: var(--text-dim); font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; }}

  .node-box {{
    stroke-width: 1.2;
    transition: stroke 0.25s ease, filter 0.25s ease, fill 0.25s ease;
    cursor: pointer;
  }}
  .node-box.cp {{ fill: var(--cp-tint); stroke: var(--panel-border); }}
  .node-box.wn {{ fill: var(--wn-tint); stroke: var(--panel-border); }}
  .node-box.client {{ fill: #132238; stroke: var(--panel-border); }}
  .node-box.neutral {{ fill: var(--panel); stroke: var(--panel-border); }}
  
  .interactive-node:hover .node-box {{
    stroke: var(--accent);
    filter: drop-shadow(0 0 10px var(--accent-glow));
  }}
  .interactive-node:hover .node-title {{
    fill: var(--accent);
  }}
  .node-box.active {{
    stroke: var(--accent) !important;
    filter: drop-shadow(0 0 10px var(--accent-glow)) !important;
  }}
  .node-title {{ fill: var(--text-main); font-size: 12px; font-weight: 600; transition: fill 0.25s ease; cursor: pointer; }}
  .node-title.active {{ fill: var(--accent); }}
  .node-sub {{ fill: var(--text-dim); font-size: 9.5px; cursor: pointer; }}
  .node-tag {{ fill: var(--accent); font-size: 8.5px; font-weight: 600; opacity: 0.85; }}

  .connector {{ stroke: var(--line); stroke-width: 1.4; fill: none; transition: stroke 0.3s ease; }}
  .connector.active {{ stroke: var(--accent); }}
  .connector-dash {{
    stroke-dasharray: 4 5; animation: dash-flow 0.9s linear infinite;
    opacity: 0; transition: opacity 0.25s ease;
  }}
  .connector-dash.on {{ opacity: 1; }}
  @keyframes dash-flow {{ to {{ stroke-dashoffset: -18; }} }}

  .packet {{
    fill: var(--packet); filter: drop-shadow(0 0 8px var(--packet-glow));
    opacity: 0; transition: opacity 0.2s ease, cx 0.55s cubic-bezier(.4,0,.2,1), cy 0.55s cubic-bezier(.4,0,.2,1);
  }}
  .packet.on {{ opacity: 1; }}

  /* Topics Directory */
  .section-title {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .filter-controls {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .search-input {{
    flex: 1;
    min-width: 260px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--text-main);
    font-family: inherit;
    font-size: 12px;
    padding: 9px 14px;
    border-radius: 6px;
    outline: none;
    transition: border-color 0.2s;
  }}
  .search-input:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
  }}
  .cat-pill {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--text-dim);
    font-size: 11px;
    padding: 6px 12px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .cat-pill:hover, .cat-pill.active {{
    background: var(--accent-dim);
    border-color: var(--accent);
    color: var(--accent);
  }}

  .topics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }}
  .topic-card {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .topic-card:hover {{
    border-color: var(--accent);
    box-shadow: 0 4px 18px rgba(0,0,0,0.3);
    transform: translateY(-2px);
  }}
  .topic-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
  }}
  .topic-badge {{
    font-size: 10px;
    font-weight: 700;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.05em;
  }}
  .topic-cat {{
    font-size: 10px;
    color: var(--text-dim);
  }}
  .topic-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 8px;
  }}
  .topic-desc {{
    font-size: 11px;
    color: var(--text-dim);
    line-height: 1.5;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .topic-footer {{
    font-size: 11px;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  /* Topic View */
  .topic-view-wrap {{ display: none; }}
  .topic-nav-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 24px;
  }}
  .topic-crumb {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .topic-heading-block {{
    margin-bottom: 28px;
  }}
  .topic-heading-block h1 {{
    font-size: 20px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.04em;
    margin-bottom: 6px;
  }}
  .topic-heading-block .meta {{
    font-size: 12px;
    color: var(--text-dim);
  }}

  /* 5-Part Layout in Topic View */
  .part-section {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 22px 20px;
    margin-bottom: 28px;
  }}
  .part-header {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid var(--panel-border);
    padding-bottom: 8px;
  }}
  .part-text {{
    font-size: 12.5px;
    color: var(--text-main);
    line-height: 1.7;
    margin-bottom: 16px;
  }}
  .part-persp {{
    font-size: 12px;
    color: var(--text-dim);
    line-height: 1.65;
    background: #0d1527;
    border-left: 3px solid var(--accent);
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-top: 14px;
  }}
  .illustration-wrap {{
    text-align: center;
    margin: 18px 0;
    background: #080d1a;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid var(--panel-border);
  }}
  .illustration-wrap img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    display: block;
    margin: 0 auto;
  }}
  .diagram-iframe-wrap {{
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    background: #080d1a;
    border: 1px solid var(--panel-border);
  }}
  .diagram-iframe {{
    width: 100%;
    height: 580px;
    border: none;
    display: block;
  }}
  .demo-block {{
    background: #000 !important;
    color: #fff !important;
    border-radius: 8px;
    padding: 1.2rem;
    overflow: auto;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    font-size: 12px;
    line-height: 1.55;
    border: 1px solid #222;
  }}
  .demo-block pre {{
    background: transparent;
    color: #fff;
    margin: 0;
    white-space: pre-wrap;
    font-family: inherit;
  }}

  /* Footer */
  .site-footer {{
    text-align: center;
    color: var(--text-dim);
    font-size: 11px;
    padding: 40px 16px 20px;
    border-top: 1px solid var(--panel-border);
    margin-top: 60px;
  }}
</style>
</head>
<body>

  <!-- Top Navigation Header -->
  <header class="site-header">
    <div class="logo" onclick="showHome()">
      <span>⬡</span> KUBERNETES <span>APARTMENT COMPLEX</span>
    </div>
    <div class="header-actions">
      <button class="btn" onclick="showHome()">🗺 Architecture Map</button>
      <a href="demos-complete.md" class="btn" target="_blank">📄 View Markdown</a>
    </div>
  </header>

  <main class="main-wrap">

    <!-- VIEW 1: HOME PAGE (Interactive Architecture Diagram + Topics Index) -->
    <div id="homeView">
      <div class="hero-heading">
        <h1>Kubernetes Architecture Overview</h1>
        <p>Dan Koe style minimalist system design · Click any component box to explore the topic</p>
      </div>

      <!-- Master Architecture SVG Diagram -->
      <div class="arch-diagram-card">
        <div class="stage-label-bar" id="masterStageLabel">Click any component below to jump to its topic, or press Play to trace cluster request flow</div>
        
        <div class="controls-bar">
          <button class="btn btn-primary" id="masterPlayBtn" onclick="playMasterFlow()">▶ Play End-to-End Flow</button>
          <button class="btn" onclick="resetMasterFlow()">↺ Reset</button>
        </div>

        <svg viewBox="0 0 1000 680" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Kubernetes full architecture diagram">
          <!-- Control Plane Region -->
          <rect class="region-box region-cp" x="30" y="80" width="450" height="420" rx="14"/>
          <text class="region-label" x="50" y="102">Control Plane (Brain / Leasing Office)</text>

          <!-- Worker Node Region -->
          <rect class="region-box region-wn" x="520" y="80" width="450" height="420" rx="14"/>
          <text class="region-label" x="540" y="102">Worker Nodes (Execution / Buildings)</text>

          <!-- Networking Layer Region -->
          <rect class="region-box region-neutral" x="30" y="520" width="940" height="130" rx="14"/>
          <text class="region-label" x="50" y="542">Networking, Ingress &amp; Discovery Layer</text>

          <!-- Client (Topic 1) -->
          <g class="interactive-node" id="mClient" onclick="goToTopic(1)">
            <rect class="node-box client" x="390" y="14" width="220" height="50" rx="10"/>
            <text class="node-title" x="500" y="36" text-anchor="middle">kubectl / Client</text>
            <text class="node-sub" x="500" y="52" text-anchor="middle">Topic 01: The Cluster</text>
          </g>

          <!-- Control Plane Components -->
          <g class="interactive-node" id="mApi" onclick="goToTopic(3)">
            <rect class="node-box cp" x="50" y="120" width="410" height="54" rx="10"/>
            <text class="node-title" x="255" y="142" text-anchor="middle">kube-apiserver</text>
            <text class="node-sub" x="255" y="160" text-anchor="middle">Topic 03 · AuthN / AuthZ / Admission Pipeline</text>
          </g>

          <g class="interactive-node" id="mEtcd" onclick="goToTopic(4)">
            <rect class="node-box cp" x="50" y="196" width="195" height="56" rx="10"/>
            <text class="node-title" x="147" y="220" text-anchor="middle">etcd</text>
            <text class="node-sub" x="147" y="238" text-anchor="middle">Topic 04 · State Store</text>
          </g>

          <g class="interactive-node" id="mSched" onclick="goToTopic(5)">
            <rect class="node-box cp" x="265" y="196" width="195" height="56" rx="10"/>
            <text class="node-title" x="362" y="220" text-anchor="middle">kube-scheduler</text>
            <text class="node-sub" x="362" y="238" text-anchor="middle">Topic 05 · Filtering &amp; Scoring</text>
          </g>

          <g class="interactive-node" id="mCtrl" onclick="goToTopic(6)">
            <rect class="node-box cp" x="50" y="274" width="195" height="56" rx="10"/>
            <text class="node-title" x="147" y="298" text-anchor="middle">kube-controller-mgr</text>
            <text class="node-sub" x="147" y="316" text-anchor="middle">Topic 06 · Reconciliation</text>
          </g>

          <g class="interactive-node" id="mCcm" onclick="goToTopic(7)">
            <rect class="node-box cp" x="265" y="274" width="195" height="56" rx="10"/>
            <text class="node-title" x="362" y="298" text-anchor="middle">cloud-controller-mgr</text>
            <text class="node-sub" x="362" y="316" text-anchor="middle">Topic 07 · Cloud APIs</text>
          </g>

          <g class="interactive-node" id="mWorkload" onclick="goToTopic(33)">
            <rect class="node-box cp" x="50" y="352" width="410" height="54" rx="10"/>
            <text class="node-title" x="255" y="374" text-anchor="middle">Workload Controllers</text>
            <text class="node-sub" x="255" y="392" text-anchor="middle">Topics 32-38 · Deployments, StatefulSets, DaemonSets, Jobs</text>
          </g>

          <g class="interactive-node" id="mRbac" onclick="goToTopic(23)">
            <rect class="node-box cp" x="50" y="426" width="410" height="54" rx="10"/>
            <text class="node-title" x="255" y="448" text-anchor="middle">RBAC &amp; Governance</text>
            <text class="node-sub" x="255" y="466" text-anchor="middle">Topics 23-31 · Roles, Quotas, GC, ServiceAccounts</text>
          </g>

          <!-- Worker Node Components -->
          <g class="interactive-node" id="mKubelet" onclick="goToTopic(9)">
            <rect class="node-box wn" x="540" y="120" width="195" height="54" rx="10"/>
            <text class="node-title" x="637" y="142" text-anchor="middle">kubelet</text>
            <text class="node-sub" x="637" y="160" text-anchor="middle">Topic 09 · Node Agent</text>
          </g>

          <g class="interactive-node" id="mCri" onclick="goToTopic(11)">
            <rect class="node-box wn" x="755" y="120" width="195" height="54" rx="10"/>
            <text class="node-title" x="852" y="142" text-anchor="middle">containerd (CRI)</text>
            <text class="node-sub" x="852" y="160" text-anchor="middle">Topic 11 · Container Runtime</text>
          </g>

          <g class="interactive-node" id="mProxy" onclick="goToTopic(10)">
            <rect class="node-box wn" x="540" y="196" width="195" height="56" rx="10"/>
            <text class="node-title" x="637" y="220" text-anchor="middle">kube-proxy</text>
            <text class="node-sub" x="637" y="238" text-anchor="middle">Topic 10 · Datapath</text>
          </g>

          <g class="interactive-node" id="mCni" onclick="goToTopic(14)">
            <rect class="node-box wn" x="755" y="196" width="195" height="56" rx="10"/>
            <text class="node-title" x="852" y="220" text-anchor="middle">CNI Plugin</text>
            <text class="node-sub" x="852" y="238" text-anchor="middle">Topic 14 · Pod Network</text>
          </g>

          <g class="interactive-node" id="mPods" onclick="goToTopic(12)">
            <rect class="node-box wn" x="540" y="274" width="410" height="56" rx="10"/>
            <text class="node-title" x="745" y="298" text-anchor="middle">Pods, Sidecars &amp; Init Containers</text>
            <text class="node-sub" x="745" y="316" text-anchor="middle">Topics 08, 12, 13 · Application Runtime Sandboxes</text>
          </g>

          <g class="interactive-node" id="mStorage" onclick="goToTopic(20)">
            <rect class="node-box wn" x="540" y="352" width="410" height="54" rx="10"/>
            <text class="node-title" x="745" y="374" text-anchor="middle">Storage Subsystem (PV / PVC / CSI)</text>
            <text class="node-sub" x="745" y="392" text-anchor="middle">Topics 20-22 · PersistentVolumes &amp; Dynamic StorageClasses</text>
          </g>

          <g class="interactive-node" id="mAutoscale" onclick="goToTopic(39)">
            <rect class="node-box wn" x="540" y="426" width="410" height="54" rx="10"/>
            <text class="node-title" x="745" y="448" text-anchor="middle">Autoscaling &amp; Disruptions (HPA / VPA / PDB)</text>
            <text class="node-sub" x="745" y="466" text-anchor="middle">Topics 39-41 · Metric-driven Scaling &amp; Maintenance Gates</text>
          </g>

          <!-- Bottom Layer: Ingress, Services, CoreDNS -->
          <g class="interactive-node" id="mIngress" onclick="goToTopic(18)">
            <rect class="node-box neutral" x="50" y="560" width="280" height="64" rx="10"/>
            <text class="node-title" x="190" y="586" text-anchor="middle">Ingress Controller</text>
            <text class="node-sub" x="190" y="606" text-anchor="middle">Topic 18 · Layer 7 HTTP &amp; TLS</text>
          </g>

          <g class="interactive-node" id="mServices" onclick="goToTopic(16)">
            <rect class="node-box neutral" x="360" y="560" width="280" height="64" rx="10"/>
            <text class="node-title" x="500" y="586" text-anchor="middle">Services &amp; Endpoints</text>
            <text class="node-sub" x="500" y="606" text-anchor="middle">Topics 16, 17 · ClusterIP &amp; EndpointSlices</text>
          </g>

          <g class="interactive-node" id="mCoreDns" onclick="goToTopic(15)">
            <rect class="node-box neutral" x="670" y="560" width="280" height="64" rx="10"/>
            <text class="node-title" x="810" y="586" text-anchor="middle">CoreDNS &amp; Policy</text>
            <text class="node-sub" x="810" y="606" text-anchor="middle">Topics 15, 19 · Discovery &amp; NetworkPolicy</text>
          </g>

          <!-- Connectors -->
          <path class="connector" id="mc0" d="M500 64 L500 90 L255 90 L255 120" fill="none"/>
          <path class="connector connector-dash" id="mc0d" d="M500 64 L500 90 L255 90 L255 120" fill="none"/>

          <line class="connector" id="mc1" x1="147" y1="174" x2="147" y2="196"/>
          <line class="connector connector-dash" id="mc1d" x1="147" y1="174" x2="147" y2="196"/>

          <line class="connector" id="mc2" x1="362" y1="174" x2="362" y2="196"/>
          <line class="connector connector-dash" id="mc2d" x1="362" y1="174" x2="362" y2="196"/>

          <path class="connector" id="mc3" d="M460 147 L540 147" fill="none"/>
          <path class="connector connector-dash" id="mc3d" d="M460 147 L540 147" fill="none"/>

          <line class="connector" id="mc4" x1="735" y1="147" x2="755" y2="147"/>
          <line class="connector connector-dash" id="mc4d" x1="735" y1="147" x2="755" y2="147"/>

          <path class="connector" id="mc5" d="M852 174 L852 274" fill="none"/>
          <path class="connector connector-dash" id="mc5d" d="M852 174 L852 274" fill="none"/>

          <path class="connector" id="mc6" d="M745 330 L745 530 L500 530 L500 560" fill="none"/>
          <path class="connector connector-dash" id="mc6d" d="M745 330 L745 530 L500 530 L500 560" fill="none"/>

          <circle class="packet" id="masterPacket" cx="500" cy="39" r="7"/>
        </svg>
      </div>

      <!-- Topics Directory & Search Filter -->
      <div class="section-title">
        <span>Topic Reference Catalog (41 Topics)</span>
        <span style="font-size: 11px; color: var(--text-dim); font-weight: normal;">Search or filter by category</span>
      </div>

      <div class="filter-controls">
        <input type="text" id="topicSearch" class="search-input" placeholder="Search topic by name, component, or keyword..." oninput="filterTopics()">
        <div class="cat-pill active" onclick="setCategoryFilter('All', this)">All (41)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Cluster Architecture', this)">Cluster (2)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Control Plane Core', this)">Control Plane (5)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Nodes & Runtime', this)">Nodes (6)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Networking & Ingress', this)">Networking (6)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Storage Subsystem', this)">Storage (3)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Security & RBAC', this)">RBAC (5)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Workload Controllers', this)">Workloads (7)</div>
        <div class="cat-pill" onclick="setCategoryFilter('Autoscaling & Disruption', this)">Autoscaling (3)</div>
      </div>

      <div class="topics-grid" id="topicsGrid">
        <!-- Dynamically populated via JS -->
      </div>
    </div>

    <!-- VIEW 2: TOPIC VIEW (5 Parts) -->
    <div id="topicView" class="topic-view-wrap">
      <div class="topic-nav-bar">
        <div class="topic-crumb">
          <button class="btn" onclick="showHome()">← Architecture Map</button>
          <span class="topic-badge" id="topicBadge">Topic 01</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn" id="prevTopicBtn" onclick="navigateTopic(-1)">← Prev</button>
          <button class="btn" id="nextTopicBtn" onclick="navigateTopic(1)">Next →</button>
        </div>
      </div>

      <div class="topic-heading-block">
        <h1 id="topicTitle">Topic Title</h1>
        <div class="meta" id="topicMeta">Category · Minimalist Tech Deep-Dive</div>
      </div>

      <!-- PART 1: Technical Perspective & Technical Illustration -->
      <section class="part-section">
        <div class="part-header">Part 1 — Technical Discussion &amp; Illustration</div>
        <div class="part-text" id="topicTechDisc">Technical discussion text...</div>
        <div class="illustration-wrap">
          <img id="topicTechImg" src="" alt="Technical illustration" loading="lazy">
        </div>
        <div class="part-persp" id="topicTechPersp">Technical perspective analysis...</div>
      </section>

      <!-- PART 2: Embedded Component Architecture Diagram -->
      <section class="part-section">
        <div class="part-header">Part 2 — Interactive Component Flow Diagram</div>
        <p class="part-text" style="color: var(--text-dim); font-size: 11.5px; margin-bottom: 12px;">
          Dan Koe style system-design animation · Play to trace request packet hops across component boundaries
        </p>
        <div class="diagram-iframe-wrap">
          <iframe id="topicDiagramIframe" class="diagram-iframe" src="" title="Component Diagram"></iframe>
        </div>
        <div style="margin-top: 10px; text-align: right;">
          <a id="topicDiagramLink" href="" target="_blank" style="font-size: 11px;">▶ Open diagram in standalone full window</a>
        </div>
      </section>

      <!-- PART 3: Zine Analogy & Illustration -->
      <section class="part-section">
        <div class="part-header">Part 3 — Apartment Complex Zine Metaphor</div>
        <div class="part-text" id="topicZineAnalogy" style="font-style: italic;">Zine analogy...</div>
        <div class="illustration-wrap">
          <img id="topicZineImg" src="" alt="Apartment Complex Zine illustration" loading="lazy">
        </div>
        <div class="part-persp" id="topicZineExp">Zine layout and explanation...</div>
      </section>

      <!-- PART 4: Further Resources -->
      <section class="part-section">
        <div class="part-header">Part 4 — Further Reading &amp; Authoritative Docs</div>
        <div class="part-text" id="topicReading">Documentation links...</div>
      </section>

      <!-- PART 5: Runnable Demo -->
      <section class="part-section">
        <div class="part-header">Part 5 — Runnable Demo (Terminal Experiment)</div>
        <div class="demo-block">
          <pre id="topicDemo">SETUP ... STEPS ... WHAT YOU SHOULD SEE ... CLEANUP</pre>
        </div>
      </section>
    </div>

  </main>

  <footer class="site-footer">
    Kubernetes Apartment Complex · Minimalist Tech / System Design Architecture Guide · Local Edition
  </footer>

  <script>
    const TOPICS = {topics_json};
    let currentCategory = 'All';
    let currentTopicNum = 1;

    // Master Diagram Flow Stages
    const masterStages = [
      {{ id: 'mClient', dot: {{x: 500, y: 39}}, label: 'Client submits application declaration to the cluster', conns: [] }},
      {{ id: 'mApi',    dot: {{x: 255, y: 147}}, label: 'API server authenticates, validates, and admits request', conns: ['mc0'] }},
      {{ id: 'mEtcd',   dot: {{x: 147, y: 224}}, label: 'etcd commits desired cluster state to Raft log', conns: ['mc1'] }},
      {{ id: 'mSched',  dot: {{x: 362, y: 224}}, label: 'Scheduler filters and scores candidate worker nodes', conns: ['mc2'] }},
      {{ id: 'mKubelet',dot: {{x: 637, y: 147}}, label: 'Kubelet on selected worker node picks up assigned pod', conns: ['mc3'] }},
      {{ id: 'mCri',    dot: {{x: 852, y: 147}}, label: 'Container runtime (CRI) pulls image and starts container', conns: ['mc4'] }},
      {{ id: 'mPods',   dot: {{x: 745, y: 302}}, label: 'Pod running healthy with IP and storage mounts', conns: ['mc5'] }},
      {{ id: 'mServices',dot: {{x: 500, y: 592}}, label: 'Service & Ingress register ready endpoint for live traffic', conns: ['mc6'] }}
    ];

    const masterNodeIds = ['mClient','mApi','mEtcd','mSched','mCtrl','mCcm','mWorkload','mRbac','mKubelet','mCri','mProxy','mCni','mPods','mStorage','mAutoscale','mIngress','mServices','mCoreDns'];
    const masterConnIds = ['mc0','mc1','mc2','mc3','mc4','mc5','mc6'];
    let masterPlaying = false;
    let masterTimer = null;

    function resetMasterFlow() {{
      masterPlaying = false;
      clearTimeout(masterTimer);
      masterNodeIds.forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
          const box = el.querySelector('.node-box');
          const title = el.querySelector('.node-title');
          if (box) box.classList.remove('active');
          if (title) title.classList.remove('active');
        }}
      }});
      masterConnIds.forEach(cid => {{
        const c = document.getElementById(cid);
        const d = document.getElementById(cid + 'd');
        if (c) c.classList.remove('active');
        if (d) d.classList.remove('on');
      }});
      document.getElementById('masterPacket').classList.remove('on');
      document.getElementById('masterStageLabel').textContent = 'Click any component below to jump to its topic, or press Play to trace cluster request flow';
      document.getElementById('masterPlayBtn').textContent = '▶ Play End-to-End Flow';
    }}

    function playMasterFlow() {{
      if (masterPlaying) return;
      resetMasterFlow();
      masterPlaying = true;
      document.getElementById('masterPacket').classList.add('on');
      document.getElementById('masterPlayBtn').textContent = '⏸ Running...';

      let i = 0;
      function step() {{
        masterNodeIds.forEach(id => {{
          const el = document.getElementById(id);
          if (el) {{
            const box = el.querySelector('.node-box');
            const title = el.querySelector('.node-title');
            if (box) box.classList.remove('active');
            if (title) title.classList.remove('active');
          }}
        }});
        masterConnIds.forEach(cid => {{
          const c = document.getElementById(cid);
          const d = document.getElementById(cid + 'd');
          if (c) c.classList.remove('active');
          if (d) d.classList.remove('on');
        }});

        if (i >= masterStages.length) {{
          masterPlaying = false;
          document.getElementById('masterStageLabel').textContent = 'End-to-End Cluster Request Flow Complete ✓ (Click any box to inspect deep-dive)';
          document.getElementById('masterPlayBtn').textContent = '▶ Play End-to-End Flow';
          return;
        }}

        const s = masterStages[i];
        if (s.conns) {{
          s.conns.forEach(cid => {{
            const c = document.getElementById(cid);
            const d = document.getElementById(cid + 'd');
            if (c) c.classList.add('active');
            if (d) d.classList.add('on');
          }});
        }}
        const el = document.getElementById(s.id);
        if (el) {{
          const box = el.querySelector('.node-box');
          const title = el.querySelector('.node-title');
          if (box) box.classList.add('active');
          if (title) title.classList.add('active');
        }}

        const pkt = document.getElementById('masterPacket');
        pkt.setAttribute('cx', s.dot.x);
        pkt.setAttribute('cy', s.dot.y);

        document.getElementById('masterStageLabel').textContent = s.label;
        i++;
        masterTimer = setTimeout(step, 1400);
      }}
      step();
    }}

    // Navigation and Routing
    function showHome() {{
      window.location.hash = '';
      document.getElementById('homeView').style.display = 'block';
      document.getElementById('topicView').style.display = 'none';
      window.scrollTo(0, 0);
    }}

    function goToTopic(num) {{
      window.location.hash = '#/topic/' + num;
    }}

    function renderTopicView(num) {{
      const topic = TOPICS.find(t => t.num === num);
      if (!topic) return;
      currentTopicNum = num;

      document.getElementById('homeView').style.display = 'none';
      document.getElementById('topicView').style.display = 'block';

      document.getElementById('topicBadge').textContent = 'Topic ' + String(topic.num).padStart(2, '0') + ' / 41';
      document.getElementById('topicTitle').textContent = topic.title;
      document.getElementById('topicMeta').textContent = topic.category + ' · Technical Reference & Apartment Zine';

      document.getElementById('topicTechDisc').textContent = topic.tech_disc;
      document.getElementById('topicTechPersp').textContent = topic.tech_persp;
      document.getElementById('topicTechImg').src = topic.tech_img;

      document.getElementById('topicDiagramIframe').src = topic.diagram;
      document.getElementById('topicDiagramLink').href = topic.diagram;

      document.getElementById('topicZineAnalogy').textContent = topic.zine_analogy;
      document.getElementById('topicZineImg').src = topic.zine_img;
      document.getElementById('topicZineExp').textContent = topic.zine_exp;

      document.getElementById('topicReading').innerHTML = formatMarkdownLinks(topic.reading);
      document.getElementById('topicDemo').textContent = topic.demo;

      document.getElementById('prevTopicBtn').disabled = (num <= 1);
      document.getElementById('nextTopicBtn').disabled = (num >= 41);

      window.scrollTo(0, 0);
    }}

    function navigateTopic(delta) {{
      const target = currentTopicNum + delta;
      if (target >= 1 && target <= 41) {{
        goToTopic(target);
      }}
    }}

    function formatMarkdownLinks(text) {{
      if (!text) return '<span style="color: var(--text-dim)">Refer to official Kubernetes documentation.</span>';
      return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1 ↗</a>');
    }}

    // Directory Filtering
    function renderTopicsGrid(list) {{
      const grid = document.getElementById('topicsGrid');
      grid.innerHTML = '';
      list.forEach(t => {{
        const card = document.createElement('div');
        card.className = 'topic-card';
        card.onclick = () => goToTopic(t.num);
        card.innerHTML = `
          <div>
            <div class="topic-card-header">
              <span class="topic-badge">Topic ${{String(t.num).padStart(2, '0')}}</span>
              <span class="topic-cat">${{t.category}}</span>
            </div>
            <div class="topic-title">${{t.title}}</div>
            <div class="topic-desc">${{t.tech_disc || t.tech_persp}}</div>
          </div>
          <div class="topic-footer">
            Explore topic &amp; diagram →
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function setCategoryFilter(cat, element) {{
      currentCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(el => el.classList.remove('active'));
      element.classList.add('active');
      filterTopics();
    }}

    function filterTopics() {{
      const q = document.getElementById('topicSearch').value.toLowerCase().trim();
      const filtered = TOPICS.filter(t => {{
        const matchCat = (currentCategory === 'All' || t.category === currentCategory);
        const matchQuery = !q || t.title.toLowerCase().includes(q) || t.tech_disc.toLowerCase().includes(q) || String(t.num) === q;
        return matchCat && matchQuery;
      }});
      renderTopicsGrid(filtered);
    }}

    // Hash change handler for routing
    window.addEventListener('hashchange', () => {{
      const hash = window.location.hash;
      const match = hash.match(/^#\/topic\/(\\d+)$/);
      if (match) {{
        renderTopicView(parseInt(match[1], 10));
      }} else {{
        showHome();
      }}
    }});

    // Initial load
    window.addEventListener('DOMContentLoaded', () => {{
      renderTopicsGrid(TOPICS);
      const hash = window.location.hash;
      const match = hash.match(/^#\/topic\/(\\d+)$/);
      if (match) {{
        renderTopicView(parseInt(match[1], 10));
      }} else {{
        showHome();
      }}
    }});
  </script>
</body>
</html>
"""
    return html


def update_demos_complete_markdown(header, topics):
    """Updates demos-complete.md by inserting the diagram iframe for all 41 topics."""
    with open("demos-complete.md", "r", encoding="utf-8") as f:
        content = f.read()

    header_and_topics = re.split(r"\n(?=## \d+\. )", content)
    header = header_and_topics[0]
    topics_raw = header_and_topics[1:]

    new_topics = []
    for idx, sec in enumerate(topics_raw, 1):
        m = re.match(r"## (\d+)\. (.+)", sec)
        if not m:
            new_topics.append(sec)
            continue
        num = int(m.group(1))

        # Check if iframe already present
        if f"diagrams/topic-{num:02d}.html" in sec:
            new_topics.append(sec)
            continue

        diagram_block = f"""

### Component architecture flow

<iframe src="diagrams/topic-{num:02d}.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-{num:02d}.html](diagrams/topic-{num:02d}.html).
"""

        # Insert right before **Part 2 — Analogy / Zine:**
        if "**Part 2 — Analogy / Zine:**" in sec:
            parts = sec.split("**Part 2 — Analogy / Zine:**", 1)
            new_sec = parts[0].rstrip() + "\n" + diagram_block + "\n**Part 2 — Analogy / Zine:**" + parts[1]
        else:
            parts = re.split(r"\n(?=\!\[.*?zine\.png\])", sec, 1)
            if len(parts) == 2:
                new_sec = parts[0].rstrip() + "\n" + diagram_block + "\n" + parts[1]
            else:
                new_sec = sec + "\n" + diagram_block

        new_topics.append(new_sec)

    updated_content = header + "\n" + "\n".join(new_topics)

    with open("demos-complete.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Updated demos-complete.md with embedded diagrams for all 41 topics.")


def create_server_script():
    server_code = """#!/usr/bin/env python3
\"\"\"
serve.py — Launches local HTTP server for the Kubernetes Apartment Complex site.
\"\"\"
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("Kubernetes Apartment Complex — Local Web Server")
        print(f"Serving at: {url}")
        print("Press Ctrl+C to stop the server.")
        print("=" * 60)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        httpd.serve_forever()
except OSError as e:
    if "Address already in use" in str(e):
        print(f"Port {PORT} is busy, trying port {PORT + 1}...")
        PORT += 1
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print(f"Serving at: {url}")
            httpd.serve_forever()
    else:
        raise
"""
    with open("serve.py", "w", encoding="utf-8") as f:
        f.write(server_code)
    os.chmod("serve.py", 0o755)
    print("Created serve.py local server runner.")


if __name__ == "__main__":
    header, topics = get_topics_and_header()
    print(f"Extracted {len(topics)} topics from demos-complete.md.")

    # Generate index.html
    html = generate_index_html(topics)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated index.html successfully.")

    # Update demos-complete.md
    update_demos_complete_markdown(header, topics)

    # Create serve.py
    create_server_script()

    print("Complete build finished successfully!")
