#!/usr/bin/env python3
"""
Generates 41 minimalist tech animated architecture diagrams for Kubernetes Apartment Complex topics.
Strictly adheres to the Style Lock defined in k8s-diagram-generation-prompt.md and k8s-pod-flow-bytemonk.html.
"""

import os
import json

DIAGRAM_TEMPLATE = """<!DOCTYPE html>
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
    text-align: center; min-height: 22px; font-size: 12.5px; color: var(--text-main);
    margin-bottom: 10px; letter-spacing: 0.02em; line-height: 1.4;
  }}
  .controls {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 18px; }}
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
  .region-label {{ fill: var(--text-dim); font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; }}

  .node-box {{
    stroke-width: 1.2; transition: stroke 0.3s ease, filter 0.3s ease;
  }}
  .node-box.cp {{ fill: var(--cp-tint); stroke: var(--panel-border); }}
  .node-box.wn {{ fill: var(--wn-tint); stroke: var(--panel-border); }}
  .node-box.client {{ fill: var(--panel); stroke: var(--panel-border); }}
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

  footer {{ text-align: center; color: var(--text-dim); font-size: 10px; margin-top: 20px; letter-spacing: 0.02em; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{heading}</h1>
  <p class="subtitle">{subtitle}</p>
  <p class="stage-label" id="stageLabel">Press play to trace the flow</p>

  <div class="controls">
    <button id="playBtn" onclick="togglePlay()">▶ Play</button>
    <button id="prevBtn" onclick="prevStep()" title="Previous step">← Prev</button>
    <button id="nextBtn" onclick="nextStep()" title="Next step">Next →</button>
    <button onclick="reset()">↺ Reset</button>
    <span id="stepIndicator" class="step-indicator">Step 0 / {{stages.length}}</span>
  </div>

  <svg viewBox="0 0 {viewBoxWidth} {viewBoxHeight}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{ariaLabel}">
{svgContent}
    <circle class="packet" id="packet" cx="{initialPacketX}" cy="{initialPacketY}" r="6"/>
  </svg>

  <footer>animated · dependency-free HTML/CSS/JS · Minimalist system design</footer>
</div>

<script>
const stages = {stagesJson};
const allNodeIds = {allNodeIdsJson};
const allConnIds = {allConnIdsJson};
let currentStep = -1;
let playing = false;
let timer = null;
const totalStages = stages.length;
const completionMessage = '{completionLabel} ✓';

function updateControls() {{
  const playBtn = document.getElementById('playBtn');
  const ind = document.getElementById('stepIndicator');
  if (playBtn) {{
    playBtn.textContent = playing ? '⏸ Pause' : (currentStep >= 0 && currentStep < totalStages - 1 ? '▶ Resume' : '▶ Play');
  }}
  if (ind) {{
    ind.textContent = currentStep >= 0 ? `Step ${{currentStep + 1}} / ${{totalStages}}` : `Step 0 / ${{totalStages}}`;
  }}
}}

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

function showStep(idx) {{
  if (idx < 0 || idx >= totalStages) return;
  currentStep = idx;
  clearAll();

  const s = stages[idx];
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
  if (packet) {{
    packet.classList.add('on');
    packet.setAttribute('cx', s.dot.x);
    packet.setAttribute('cy', s.dot.y);
  }}

  document.getElementById('stageLabel').textContent = s.label;
  updateControls();
}}

function pauseFlow() {{
  playing = false;
  clearTimeout(timer);
  updateControls();
}}

function nextStep() {{
  pauseFlow();
  const nextIdx = (currentStep + 1) % totalStages;
  showStep(nextIdx);
}}

function prevStep() {{
  pauseFlow();
  const prevIdx = currentStep > 0 ? currentStep - 1 : totalStages - 1;
  showStep(prevIdx);
}}

function reset() {{
  playing = false;
  clearTimeout(timer);
  currentStep = -1;
  clearAll();
  const packet = document.getElementById('packet');
  if (packet) packet.classList.remove('on');
  document.getElementById('stageLabel').textContent = 'Press play or Next → to trace the flow';
  updateControls();
}}

function togglePlay() {{
  if (playing) {{
    pauseFlow();
  }} else {{
    playing = true;
    updateControls();
    if (currentStep >= totalStages - 1 || currentStep < 0) {{
      showStep(0);
    }}
    function autoStep() {{
      if (!playing) return;
      if (currentStep >= totalStages - 1) {{
        playing = false;
        document.getElementById('stageLabel').textContent = completionMessage;
        updateControls();
        return;
      }}
      showStep(currentStep + 1);
      timer = setTimeout(autoStep, 1400);
    }}
    timer = setTimeout(autoStep, 1400);
  }}
}}

function play() {{
  togglePlay();
}}

window.addEventListener('keydown', (e) => {{
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowRight') {{ nextStep(); }}
  else if (e.key === 'ArrowLeft') {{ prevStep(); }}
  else if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
}});
</script>
</body>
</html>
"""
