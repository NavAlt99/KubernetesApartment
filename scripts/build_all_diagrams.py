#!/usr/bin/env python3
"""
build_all_diagrams.py
Generates 41 minimalist tech animated architecture diagrams in diagrams/topic-01.html .. topic-41.html
Strictly follows the Style Lock in k8s-diagram-generation-prompt.md & k8s-pod-flow-bytemonk.html.
"""

import os
import json

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kubernetes Architecture — {title}</title>
<style>
  :root {{
    --bg: #0b1120;
    --panel: #111a2e;
    --panel-border: #1e2b47;
    --cp-tint: #0f1f38;
    --wn-tint: #14231c;
    --accent: #38bdf8;
    --accent-glow: rgba(56, 189, 248, 0.55);
    --packet: #f59e0b;
    --packet-glow: rgba(245, 158, 11, 0.6);
    --text-main: #e5edf7;
    --text-dim: #7f93b3;
    --line: #24324f;
    --region-cp-border: #2b3f66;
    --region-wn-border: #234030;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: var(--bg);
    color: var(--text-main);
    font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
  }}
  body {{
    padding: 24px 14px 32px;
    padding-top: max(24px, env(safe-area-inset-top));
    padding-bottom: max(32px, env(safe-area-inset-bottom));
  }}
  .wrap {{ max-width: 920px; margin: 0 auto; }}
  h1 {{
    font-size: 14px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--accent); text-align: center; margin: 0 0 4px;
  }}
  .subtitle {{ text-align: center; color: var(--text-dim); font-size: 11.5px; margin: 0 0 16px; }}
  .stage-label {{
    text-align: center; min-height: 24px; font-size: 12.5px; color: var(--text-main);
    margin-bottom: 12px; letter-spacing: 0.02em; line-height: 1.4;
  }}
  .controls {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }}
  button {{
    font-family: inherit; font-size: 11.5px; letter-spacing: 0.03em;
    background: var(--panel); color: var(--accent); border: 1px solid var(--panel-border);
    border-radius: 6px; padding: 7px 15px; cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
  }}
  button:hover {{ border-color: var(--accent); box-shadow: 0 0 12px rgba(56, 189, 248, 0.25); }}
  button:active {{ transform: translateY(1px); }}

  svg {{ display: block; width: 100%; height: auto; overflow: visible; }}

  .region-box {{ fill: none; stroke-width: 1.2; stroke-dasharray: 3 4; }}
  .region-cp {{ stroke: var(--region-cp-border); }}
  .region-wn {{ stroke: var(--region-wn-border); }}
  .region-neutral {{ stroke: var(--panel-border); }}
  .region-label {{ fill: var(--text-dim); font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; }}

  .node-box {{
    stroke-width: 1.2; transition: stroke 0.3s ease, filter 0.3s ease;
  }}
  .node-box.cp {{ fill: var(--cp-tint); stroke: var(--panel-border); }}
  .node-box.wn {{ fill: var(--wn-tint); stroke: var(--panel-border); }}
  .node-box.client {{ fill: var(--panel); stroke: var(--panel-border); }}
  .node-box.neutral {{ fill: var(--panel); stroke: var(--panel-border); }}
  .node-box.active {{ stroke: var(--accent); filter: drop-shadow(0 0 8px var(--accent-glow)); }}

  .node-title {{ fill: var(--text-main); font-size: 12px; font-weight: 600; transition: fill 0.3s ease; }}
  .node-title.active {{ fill: var(--accent); }}
  .node-sub {{ fill: var(--text-dim); font-size: 9.5px; }}

  .connector {{ stroke: var(--line); stroke-width: 1.4; fill: none; transition: stroke 0.3s ease; }}
  .connector.active {{ stroke: var(--accent); }}
  .connector-dash {{
    stroke-dasharray: 4 5; animation: dash-flow 0.9s linear infinite;
    opacity: 0; transition: opacity 0.25s ease;
  }}
  .connector-dash.on {{ opacity: 1; }}
  @keyframes dash-flow {{ to {{ stroke-dashoffset: -18; }} }}

  .packet {{
    fill: var(--packet); filter: drop-shadow(0 0 6px var(--packet-glow));
    opacity: 0; transition: opacity 0.2s ease, cx 0.55s cubic-bezier(.4,0,.2,1), cy 0.55s cubic-bezier(.4,0,.2,1);
  }}
  .packet.on {{ opacity: 1; }}

  @media (prefers-reduced-motion: reduce) {{
    .connector-dash {{ animation: none; }}
    .packet {{ transition: opacity 0.2s ease; }}
  }}

  footer {{ text-align: center; color: var(--text-dim); font-size: 10px; margin-top: 22px; letter-spacing: 0.02em; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{heading}</h1>
  <p class="subtitle">{subtitle}</p>
  <p class="stage-label" id="stageLabel">Press play to trace the flow</p>

  <div class="controls">
    <button id="playBtn" onclick="play()">▶ Play</button>
    <button onclick="reset()">↺ Reset</button>
  </div>

  <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{ariaLabel}">
{svgBody}
    <circle class="packet" id="packet" cx="{startPacketX}" cy="{startPacketY}" r="6"/>
  </svg>

  <footer>animated · dependency-free HTML/CSS/JS · Dan Koe style minimalist system design</footer>
</div>

<script>
const stages = {stagesJson};
const allNodeIds = {allNodeIdsJson};
const allConnIds = {allConnIdsJson};
let playing = false;
let timer = null;

function clearAll() {{
  allNodeIds.forEach(id => {{
    const box = document.querySelector('#' + id + ' .node-box');
    const title = document.querySelector('#' + id + ' .node-title');
    if (box) box.classList.remove('active');
    if (title) title.classList.remove('active');
  }});
  allConnIds.forEach(id => {{
    const c = document.getElementById(id);
    const d = document.getElementById(id + 'd');
    if (c) c.classList.remove('active');
    if (d) d.classList.remove('on');
  }});
}}

function reset() {{
  playing = false;
  clearTimeout(timer);
  clearAll();
  document.getElementById('packet').classList.remove('on');
  document.getElementById('stageLabel').textContent = 'Press play to trace the flow';
  document.getElementById('playBtn').textContent = '▶ Play';
}}

function play() {{
  if (playing) return;
  reset();
  playing = true;
  document.getElementById('packet').classList.add('on');
  document.getElementById('playBtn').textContent = '⏸ Running...';

  let i = 0;
  function step() {{
    clearAll();
    if (i >= stages.length) {{
      playing = false;
      document.getElementById('stageLabel').textContent = '{completionLabel} ✓';
      document.getElementById('playBtn').textContent = '▶ Play';
      return;
    }}
    const s = stages[i];
    if (s.conns) {{
      s.conns.forEach(cid => {{
        const c = document.getElementById(cid);
        const d = document.getElementById(cid + 'd');
        if (c) c.classList.add('active');
        if (d) d.classList.add('on');
      }});
    }}
    const box = document.querySelector('#' + s.id + ' .node-box');
    const title = document.querySelector('#' + s.id + ' .node-title');
    if (box) box.classList.add('active');
    if (title) title.classList.add('active');

    const packet = document.getElementById('packet');
    packet.setAttribute('cx', s.dot.x);
    packet.setAttribute('cy', s.dot.y);

    document.getElementById('stageLabel').textContent = s.label;
    i++;
    timer = setTimeout(step, 1350);
  }}
  step();
}}
</script>
</body>
</html>
"""

def render_diagram(topic_def):
    """Renders a single diagram HTML string."""
    width = topic_def.get("width", 880)
    height = topic_def.get("height", 520)
    
    svg_lines = []
    
    # Regions
    for reg in topic_def.get("regions", []):
        rx = reg.get("x", 40)
        ry = reg.get("y", 80)
        rw = reg.get("w", 380)
        rh = reg.get("h", 380)
        rcls = reg.get("cls", "region-cp")
        label = reg.get("label", "")
        svg_lines.append(f'    <!-- Region: {label} -->')
        svg_lines.append(f'    <rect class="region-box {rcls}" x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="14"/>')
        if label:
            svg_lines.append(f'    <text class="region-label" x="{rx + 16}" y="{ry + 22}">{label}</text>')
    
    # Connectors
    all_conn_ids = []
    for conn in topic_def.get("connectors", []):
        cid = conn["id"]
        all_conn_ids.append(cid)
        ctype = conn.get("type", "line")
        if ctype == "line":
            x1, y1, x2, y2 = conn["x1"], conn["y1"], conn["x2"], conn["y2"]
            svg_lines.append(f'    <line class="connector" id="{cid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
            svg_lines.append(f'    <line class="connector connector-dash" id="{cid}d" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        elif ctype == "path":
            d = conn["d"]
            svg_lines.append(f'    <path class="connector" id="{cid}" d="{d}" fill="none"/>')
            svg_lines.append(f'    <path class="connector connector-dash" id="{cid}d" d="{d}" fill="none"/>')

    # Nodes
    all_node_ids = []
    for node in topic_def.get("nodes", []):
        nid = node["id"]
        all_node_ids.append(nid)
        ntype = node.get("type", "neutral")
        nx, ny, nw, nh = node["x"], node["y"], node["w"], node["h"]
        title = node["title"]
        sub = node.get("sub", "")
        sub2 = node.get("sub2", "")
        
        svg_lines.append(f'    <!-- Node: {title} -->')
        svg_lines.append(f'    <g id="{nid}">')
        svg_lines.append(f'      <rect class="node-box {ntype}" x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10"/>')
        
        tx = nx + nw // 2
        ty = ny + 24 if sub else ny + nh // 2 + 5
        svg_lines.append(f'      <text class="node-title" x="{tx}" y="{ty}" text-anchor="middle">{title}</text>')
        if sub:
            svg_lines.append(f'      <text class="node-sub" x="{tx}" y="{ty + 18}" text-anchor="middle">{sub}</text>')
        if sub2:
            svg_lines.append(f'      <text class="node-sub" x="{tx}" y="{ty + 32}" text-anchor="middle">{sub2}</text>')
        svg_lines.append(f'    </g>')
        
    svg_body = "\n".join(svg_lines)
    
    stages = topic_def.get("stages", [])
    start_pkt_x = stages[0]["dot"]["x"] if stages else 440
    start_pkt_y = stages[0]["dot"]["y"] if stages else 50
    
    html = HTML_TEMPLATE.format(
        title=topic_def["title"],
        heading=topic_def["heading"],
        subtitle=topic_def["subtitle"],
        completionLabel=topic_def.get("completionLabel", "Operation complete"),
        width=width,
        height=height,
        ariaLabel=f"Architecture flow diagram for {topic_def['title']}",
        svgBody=svg_body,
        startPacketX=start_pkt_x,
        startPacketY=start_pkt_y,
        stagesJson=json.dumps(stages, indent=2),
        allNodeIdsJson=json.dumps(all_node_ids),
        allConnIdsJson=json.dumps(all_conn_ids)
    )
    return html

print("Helper loaded successfully")
