#!/usr/bin/env python3
"""
Generate diagrams and illustrations for Topics 42 through 46.
"""
import os
from PIL import Image, ImageDraw, ImageFont

DIAGRAMS = {
    42: {
        "title": "Probes & Health Checks — Container Lifecycle Validation",
        "subtitle": "Startup, Liveness, and Readiness probes governing container lifecycle and traffic routing",
        "nodes": [
            ("nBoot", "client", 60, 140, 200, 65, "Container Initialization", "bootstraps app process"),
            ("nStartup", "wn", 300, 140, 210, 65, "startupProbe", "delays liveness until pass"),
            ("nLiveness", "wn", 550, 140, 210, 65, "livenessProbe", "kubelet restarts on failure"),
            ("nReadiness", "wn", 300, 270, 210, 65, "readinessProbe", "checks service ready"),
            ("nEndpoints", "neutral", 550, 270, 210, 65, "Endpoints Routing", "adds to Service endpoints")
        ],
        "conns": [
            ("c0", 260, 172, 300, 172),
            ("c1", 510, 172, 550, 172),
            ("c2", 405, 205, 405, 270),
            ("c3", 510, 302, 550, 302)
        ],
        "stages": [
            {"id": "nBoot", "dot": {"x": 160, "y": 172}, "label": "Container process starts executing inside isolated namespace", "conns": []},
            {"id": "nStartup", "dot": {"x": 405, "y": 172}, "label": "startupProbe prevents aggressive liveness kills during app warmup", "conns": ["c0"]},
            {"id": "nLiveness", "dot": {"x": 655, "y": 172}, "label": "livenessProbe monitors runtime deadlock; triggers container restart if dead", "conns": ["c1"]},
            {"id": "nReadiness", "dot": {"x": 405, "y": 302}, "label": "readinessProbe validates backend dependencies before taking live traffic", "conns": ["c2"]},
            {"id": "nEndpoints", "dot": {"x": 655, "y": 302}, "label": "Traffic forwarded to Pod IP only while readiness condition is True", "conns": ["c3"]}
        ]
    },
    43: {
        "title": "EndpointSlices & Headless Services — High-Scale Service Discovery",
        "subtitle": "Chunked endpoint subsets and direct Pod DNS records for stateful architectures",
        "nodes": [
            ("nClient", "client", 60, 140, 200, 65, "DNS / Client Query", "StatefulSet or API call"),
            ("nHeadless", "cp", 300, 140, 210, 65, "Headless Service", "spec.clusterIP: None"),
            ("nCoreDns", "neutral", 550, 140, 210, 65, "CoreDNS Resolution", "direct Pod A / SRV records"),
            ("nController", "cp", 300, 270, 210, 65, "EndpointSlice Controller", "chunks 100 pods per slice"),
            ("nSlices", "wn", 550, 270, 210, 65, "discovery.k8s.io/v1", "topology-aware routing")
        ],
        "conns": [
            ("c0", 260, 172, 300, 172),
            ("c1", 510, 172, 550, 172),
            ("c2", 405, 205, 405, 270),
            ("c3", 510, 302, 550, 302)
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 160, "y": 172}, "label": "Client requests discovery of individual stateful cluster members", "conns": []},
            {"id": "nHeadless", "dot": {"x": 405, "y": 172}, "label": "Headless Service (clusterIP: None) bypasses single virtual IP load balancing", "conns": ["c0"]},
            {"id": "nCoreDns", "dot": {"x": 655, "y": 172}, "label": "CoreDNS returns individual pod A records (pod-0.svc.ns.svc.cluster.local)", "conns": ["c1"]},
            {"id": "nController", "dot": {"x": 405, "y": 302}, "label": "EndpointSlice controller breaks massive endpoints into scalable 100-pod slices", "conns": ["c2"]},
            {"id": "nSlices", "dot": {"x": 655, "y": 302}, "label": "kube-proxy & ingress consume lightweight slices with zone topology hints", "conns": ["c3"]}
        ]
    },
    44: {
        "title": "Pod Security Standards & Admission — Cluster Hardening",
        "subtitle": "Privileged, Baseline, and Restricted security profiles enforced natively at admission",
        "nodes": [
            ("nSubmit", "client", 60, 140, 200, 65, "Pod Manifest Submitted", "kubectl apply -f pod.yaml"),
            ("nApi", "cp", 300, 140, 210, 65, "kube-apiserver", "admission evaluation phase"),
            ("nPsa", "cp", 550, 140, 210, 65, "Pod Security Admission", "reads namespace labels"),
            ("nStandards", "wn", 300, 270, 210, 65, "PSS Security Profile", "Restricted: drops caps, non-root"),
            ("nEnforce", "neutral", 550, 270, 210, 65, "Admission Decision", "Enforce (reject) or Warn / Audit")
        ],
        "conns": [
            ("c0", 260, 172, 300, 172),
            ("c1", 510, 172, 550, 172),
            ("c2", 405, 205, 405, 270),
            ("c3", 510, 302, 550, 302)
        ],
        "stages": [
            {"id": "nSubmit", "dot": {"x": 160, "y": 172}, "label": "Developer submits Pod specification containing securityContext", "conns": []},
            {"id": "nApi", "dot": {"x": 405, "y": 172}, "label": "API server intercepts request before persisting into etcd storage", "conns": ["c0"]},
            {"id": "nPsa", "dot": {"x": 655, "y": 172}, "label": "Built-in Pod Security Admission plugin inspects target namespace security labels", "conns": ["c1"]},
            {"id": "nStandards", "dot": {"x": 405, "y": 302}, "label": "Validates against Restricted profile: no host namespaces, non-root user required", "conns": ["c2"]},
            {"id": "nEnforce", "dot": {"x": 655, "y": 302}, "label": "Rejects violating pods immediately or logs audit warnings for operators", "conns": ["c3"]}
        ]
    },
    45: {
        "title": "CustomResourceDefinitions & Operators — Declarative Extensibility",
        "subtitle": "Extending the Kubernetes API with custom schemas and autonomous controller reconcile loops",
        "nodes": [
            ("nCrd", "client", 60, 140, 200, 65, "CustomResourceDefinition", "registers new API group/kind"),
            ("nCr", "cp", 300, 140, 210, 65, "Custom Resource (CR)", "declarative desired state"),
            ("nApi", "cp", 550, 140, 210, 65, "kube-apiserver", "OpenAPI v3 schema validation"),
            ("nOperator", "wn", 300, 270, 210, 65, "Custom Operator Pod", "continuous Reconcile Loop"),
            ("nInfra", "neutral", 550, 270, 210, 65, "Managed Infrastructure", "databases, clusters, backups")
        ],
        "conns": [
            ("c0", 260, 172, 300, 172),
            ("c1", 510, 172, 550, 172),
            ("c2", 405, 205, 405, 270),
            ("c3", 510, 302, 550, 302)
        ],
        "stages": [
            {"id": "nCrd", "dot": {"x": 160, "y": 172}, "label": "CRD defines custom kind (e.g. PostgresCluster) with OpenAPI schema", "conns": []},
            {"id": "nCr", "dot": {"x": 405, "y": 172}, "label": "User applies Custom Resource expressing desired state (3 replicas, backup true)", "conns": ["c0"]},
            {"id": "nApi", "dot": {"x": 655, "y": 172}, "label": "API server validates schema, persists CR to etcd, and emits watch event", "conns": ["c1"]},
            {"id": "nOperator", "dot": {"x": 405, "y": 302}, "label": "Operator controller informer receives event and enters reconcile loop", "conns": ["c2"]},
            {"id": "nInfra", "dot": {"x": 655, "y": 302}, "label": "Operator provisions stateful StatefulSets, PVCs, and configures failover", "conns": ["c3"]}
        ]
    },
    46: {
        "title": "LimitRange — Namespace Resource Constraints",
        "subtitle": "Microscopic compute limits, default requests, and ratio caps enforced on containers",
        "nodes": [
            ("nPod", "client", 60, 140, 200, 65, "Pod Manifest", "omits CPU/memory requests"),
            ("nLimitRanger", "cp", 300, 140, 210, 65, "LimitRanger Admission", "mutating & validating hook"),
            ("nDefaults", "cp", 550, 140, 210, 65, "Default Injection", "injects default requests/limits"),
            ("nValidation", "wn", 300, 270, 210, 65, "Min / Max / Ratio Check", "verifies min/max container caps"),
            ("nKubelet", "neutral", 550, 270, 210, 65, "Scheduled Container", "cgroup limits enforced")
        ],
        "conns": [
            ("c0", 260, 172, 300, 172),
            ("c1", 510, 172, 550, 172),
            ("c2", 405, 205, 405, 270),
            ("c3", 510, 302, 550, 302)
        ],
        "stages": [
            {"id": "nPod", "dot": {"x": 160, "y": 172}, "label": "Developer submits Pod without specifying compute requests or limits", "conns": []},
            {"id": "nLimitRanger", "dot": {"x": 405, "y": 172}, "label": "LimitRanger admission controller intercepts incoming pod object", "conns": ["c0"]},
            {"id": "nDefaults", "dot": {"x": 655, "y": 172}, "label": "LimitRange automatically injects configured default requests and limits", "conns": ["c1"]},
            {"id": "nValidation", "dot": {"x": 405, "y": 302}, "label": "Validates container bounds against min, max, and maxLimitRequestRatio", "conns": ["c2"]},
            {"id": "nKubelet", "dot": {"x": 655, "y": 302}, "label": "Kubelet programs Linux cgroups on worker node with validated boundaries", "conns": ["c3"]}
        ]
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kubernetes Architecture — {title}</title>
<style>
  :root {{
    --bg: #090d16;
    --panel: #121526;
    --panel-border: #3b1d38;
    --cp-tint: #1e0b1c;
    --wn-tint: #1c1006;
    --accent: #f43f5e;
    --accent-glow: rgba(244, 63, 94, 0.65);
    --accent-pink: #ec4899;
    --accent-orange: #f97316;
    --accent-orange-glow: rgba(249, 115, 22, 0.7);
    --accent-red: #ef4444;
    --packet: #ff5722;
    --packet-glow: rgba(255, 87, 34, 0.9);
    --text-main: #fce7f3;
    --text-dim: #94a3b8;
    --line: #4a213a;
    --region-cp-border: #ec4899;
    --region-wn-border: #f97316;
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
    color: #fb7185; text-align: center; margin: 0 0 4px;
    text-shadow: 0 0 14px rgba(251, 113, 133, 0.35);
  }}
  .subtitle {{ text-align: center; color: #cbd5e1; font-size: 11.5px; margin: 0 0 16px; }}
  .stage-label {{
    text-align: center; min-height: 24px; font-size: 12.5px; color: #fff;
    margin-bottom: 12px; letter-spacing: 0.02em; line-height: 1.4;
  }}
  .controls {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }}
  button {{
    font-family: inherit; font-size: 11.5px; letter-spacing: 0.03em;
    background: #190e1f; color: #fb7185; border: 1px solid #be185d;
    border-radius: 6px; padding: 7px 15px; cursor: pointer;
    transition: all 0.2s ease;
  }}
  button:hover {{
    border-color: #f43f5e; color: #ffffff;
    box-shadow: 0 0 14px rgba(244, 63, 94, 0.5), 0 0 20px rgba(249, 115, 22, 0.3);
  }}
  button:active {{ transform: translateY(1px); }}

  svg {{ display: block; width: 100%; height: auto; overflow: visible; }}

  .region-box {{ fill: none; stroke-width: 1.4; stroke-dasharray: 4 4; }}
  .region-cp {{ stroke: var(--region-cp-border); filter: drop-shadow(0 0 6px rgba(236, 72, 153, 0.3)); }}
  .region-wn {{ stroke: var(--region-wn-border); filter: drop-shadow(0 0 6px rgba(249, 115, 22, 0.3)); }}
  .region-neutral {{ stroke: #64748b; }}
  .region-label {{ font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; fill: #f472b6; }}
  .region-wn + .region-label, rect.region-wn ~ text.region-label {{ fill: #fb923c !important; }}

  .node-box {{
    stroke-width: 1.3; transition: stroke 0.3s ease, filter 0.3s ease, fill 0.3s ease;
  }}
  .node-box.cp {{ fill: var(--cp-tint); stroke: #ec4899; }}
  .node-box.wn {{ fill: var(--wn-tint); stroke: #f97316; }}
  .node-box.client {{ fill: #1a0f1b; stroke: #ef4444; }}
  .node-box.neutral {{ fill: #160e20; stroke: #db2777; }}
  .node-box.active {{
    stroke: #f43f5e !important;
    filter: drop-shadow(0 0 10px rgba(244, 63, 94, 0.95)) drop-shadow(0 0 20px rgba(249, 115, 22, 0.6)) !important;
  }}

  .node-title {{ fill: #ffffff; font-size: 12px; font-weight: 600; transition: fill 0.3s ease; }}
  .node-title.active {{ fill: #fb7185; text-shadow: 0 0 8px rgba(251, 113, 133, 0.7); }}
  .node-sub {{ fill: #cbd5e1; font-size: 9.5px; }}

  .connector {{ stroke: var(--line); stroke-width: 1.4; fill: none; transition: stroke 0.3s ease; }}
  .connector.active {{ stroke: #f43f5e; filter: drop-shadow(0 0 6px rgba(249, 115, 22, 0.7)); }}
  .connector-dash {{
    stroke: #f97316;
    stroke-dasharray: 4 5; animation: dash-flow 0.9s linear infinite;
    opacity: 0; transition: opacity 0.25s ease;
  }}
  .connector-dash.on {{ opacity: 1; }}
  @keyframes dash-flow {{ to {{ stroke-dashoffset: -18; }} }}

  .packet {{
    fill: #ff5722;
    filter: drop-shadow(0 0 8px #ff5722) drop-shadow(0 0 16px #ec4899);
    opacity: 0; transition: opacity 0.2s ease, cx 0.55s cubic-bezier(.4,0,.2,1), cy 0.55s cubic-bezier(.4,0,.2,1);
  }}
  .packet.on {{ opacity: 1; }}

  @media (prefers-reduced-motion: reduce) {{
    .connector-dash {{ animation: none; }}
    .packet {{ transition: opacity 0.2s ease; }}
  }}

  footer {{ text-align: center; color: #cbd5e1; font-size: 10px; margin-top: 22px; letter-spacing: 0.02em; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{title}</h1>
  <p class="subtitle">{subtitle}</p>
  <p class="stage-label" id="stageLabel">Press play to trace the flow</p>

  <div class="controls">
    <button id="playBtn" onclick="play()">▶ Play</button>
    <button onclick="reset()">↺ Reset</button>
  </div>

  <svg viewBox="0 0 880 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture flow diagram for {title}">
    <rect class="region-box region-cp" x="40" y="80" width="800" height="320" rx="14"/>
    <text class="region-label" x="56" y="102">Kubernetes Lifecycle &amp; Control Loop</text>
    
    {conns_svg}
    {nodes_svg}

    <circle class="packet" id="packet" cx="160" cy="172" r="6"/>
  </svg>

  <footer>animated · dependency-free HTML/CSS/JS · Dan Koe style minimalist system design</footer>
</div>

<script>
const stages = {stages_json};
const allNodeIds = {all_nodes_json};
const allConnIds = {all_conns_json};
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
      document.getElementById('stageLabel').textContent = 'Flow completed successfully ✓';
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

def generate_diagrams():
    import json
    for num, data in DIAGRAMS.items():
        conns_svg_lines = []
        for cid, x1, y1, x2, y2 in data["conns"]:
            conns_svg_lines.append(f'<line class="connector" id="{cid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
            conns_svg_lines.append(f'<line class="connector connector-dash" id="{cid}d" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        
        nodes_svg_lines = []
        for nid, ntype, x, y, w, h, t1, t2 in data["nodes"]:
            cx = x + w // 2
            cy1 = y + 24
            cy2 = y + 44
            nodes_svg_lines.append(f'''    <g id="{nid}">
      <rect class="node-box {ntype}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>
      <text class="node-title" x="{cx}" y="{cy1}" text-anchor="middle">{t1}</text>
      <text class="node-sub" x="{cx}" y="{cy2}" text-anchor="middle">{t2}</text>
    </g>''')

        all_nodes = [n[0] for n in data["nodes"]]
        all_conns = [c[0] for c in data["conns"]]

        content = HTML_TEMPLATE.format(
            title=data["title"],
            subtitle=data["subtitle"],
            conns_svg="\n    ".join(conns_svg_lines),
            nodes_svg="\n".join(nodes_svg_lines),
            stages_json=json.dumps(data["stages"], indent=2),
            all_nodes_json=json.dumps(all_nodes),
            all_conns_json=json.dumps(all_conns)
        )

        path = f"diagrams/topic-{num:02d}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {path}")

def generate_images():
    os.makedirs("generated/kubernetes-apartment-complex", exist_ok=True)
    topics_info = {
        42: ("Topic 42: Probes & Health Checks", "Startup, Liveness & Readiness checks", "Building Inspection & Maintenance Check", "Routine inspections verify safety before admitting visitors"),
        43: ("Topic 43: EndpointSlices & Headless", "discovery.k8s.io/v1 & clusterIP: None", "Resident Intercom & Direct Directory", "Direct buzzer directory connecting visitors directly to unit phones"),
        44: ("Topic 44: Pod Security Admission", "Privileged, Baseline & Restricted PSS", "Building Safety Codes & Fire Standards", "Fire marshal enforcing non-combustible materials and clear exits"),
        45: ("Topic 45: Custom Resources & Operators", "CRDs & Autonomous Reconcile Loops", "Specialized Facility Contractors", "Contractor servicing custom elevator banks and HVAC machinery"),
        46: ("Topic 46: LimitRange", "Default requests & min/max constraints", "Apartment Appliance Power Caps", "Circuit breaker box limiting maximum electrical draw per appliance")
    }

    for num, (t_title, t_sub, z_title, z_sub) in topics_info.items():
        # Technical Image
        tech_img = Image.new("RGBA", (1024, 768), color=(10, 15, 28, 255))
        draw = ImageDraw.Draw(tech_img)
        # Background gradient rects
        draw.rectangle([(20, 20), (1004, 748)], outline=(56, 189, 248, 180), width=3)
        draw.rectangle([(40, 40), (984, 728)], outline=(244, 63, 94, 100), width=1)
        # Card header
        draw.rectangle([(40, 40), (984, 130)], fill=(18, 25, 48, 255))
        draw.text((60, 60), t_title, fill=(244, 63, 94, 255))
        draw.text((60, 95), t_sub, fill=(148, 163, 184, 255))
        # Content box
        draw.rectangle([(60, 160), (964, 700)], fill=(14, 20, 38, 255), outline=(59, 130, 246, 120), width=2)
        draw.text((90, 200), f"Kubernetes Core Architecture Specification — Topic {num}", fill=(56, 189, 248, 255))
        draw.text((90, 250), "• Declarative API primitives managed by kube-apiserver", fill=(203, 213, 225, 255))
        draw.text((90, 300), "• Reconciled continuously across control plane and worker nodes", fill=(203, 213, 225, 255))
        draw.text((90, 350), "• Production hardening and high availability guarantees", fill=(203, 213, 225, 255))
        draw.text((90, 450), "Interactive animated flow available in diagrams view.", fill=(251, 146, 60, 255))
        tech_path = f"generated/kubernetes-apartment-complex/{num:02d}-technical.png"
        tech_img.save(tech_path)
        print(f"Generated {tech_path}")

        # Zine Image
        zine_img = Image.new("RGBA", (1024, 768), color=(26, 15, 25, 255))
        draw_z = ImageDraw.Draw(zine_img)
        draw_z.rectangle([(20, 20), (1004, 748)], outline=(236, 72, 153, 200), width=3)
        draw_z.rectangle([(40, 40), (984, 728)], outline=(249, 115, 22, 100), width=1)
        draw_z.rectangle([(40, 40), (984, 130)], fill=(38, 18, 35, 255))
        draw_z.text((60, 60), f"Apartment Zine: {z_title}", fill=(236, 72, 153, 255))
        draw_z.text((60, 95), z_sub, fill=(244, 208, 111, 255))
        draw_z.rectangle([(60, 160), (964, 700)], fill=(32, 16, 30, 255), outline=(236, 72, 153, 140), width=2)
        draw_z.text((90, 200), "Apartment Complex Metaphor Series", fill=(249, 115, 22, 255))
        draw_z.text((90, 260), f"Analogy: {z_title}", fill=(255, 255, 255, 255))
        draw_z.text((90, 320), f"Explanation: {z_sub}", fill=(203, 213, 225, 255))
        draw_z.text((90, 420), "Translating distributed systems into physical apartment operations.", fill=(236, 72, 153, 255))
        zine_path = f"generated/kubernetes-apartment-complex/{num:02d}-zine.png"
        zine_img.save(zine_path)
        print(f"Generated {zine_path}")

if __name__ == "__main__":
    generate_diagrams()
    generate_images()
