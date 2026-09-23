#!/usr/bin/env python3
"""
scripts/build_website.py
Generates index.html with interactive architecture diagrams and quizzes,
updates demos-complete.md with embedded diagrams and quizzes,
and creates serve.py.
"""

import os
import re
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from quiz_data import QUIZZES

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
        elif num in [42, 43]:
            cat = "Workload & Pod Lifecycle"
        elif num in [44, 46]:
            cat = "Security & Governance"
        elif num == 45:
            cat = "Extensibility & Operators"

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
            "diagram": f"diagrams/topic-{num:02d}.html",
            "quiz": QUIZZES.get(num) or QUIZZES.get(str(num), [])
        })

    return header, topics


def generate_index_html(topics):
    total_topics = len(topics)
    topics_json = json.dumps(topics)

    category_counts = {}
    for t in topics:
        c = t["category"]
        category_counts[c] = category_counts.get(c, 0) + 1

    pills_html = ['<div class="cat-pill active" onclick="setCategoryFilter(\'All\', this)">All (' + str(total_topics) + ')</div>']
    for cat_name, count in category_counts.items():
        short_name = cat_name.split()[0]
        if "Lifecycle" in cat_name:
            short_name = "Lifecycle"
        elif "Governance" in cat_name:
            short_name = "Governance"
        elif "Operators" in cat_name:
            short_name = "Operators"
        pills_html.append('<div class="cat-pill" onclick="setCategoryFilter(\'' + cat_name + '\', this)">' + short_name + ' (' + str(count) + ')</div>')
    category_pills_str = "\n        ".join(pills_html)

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
    --bg: #090d16;
    --panel: #121526;
    --panel-hover: #191c32;
    --panel-border: #3b1d38;
    --cp-tint: #1e0b1c;
    --wn-tint: #1c1006;
    --accent: #f43f5e;
    --accent-glow: rgba(244, 63, 94, 0.6);
    --accent-dim: rgba(244, 63, 94, 0.15);
    --accent-pink: #ec4899;
    --accent-orange: #f97316;
    --accent-orange-glow: rgba(249, 115, 22, 0.65);
    --accent-red: #ef4444;
    --packet: #ff5722;
    --packet-glow: rgba(255, 87, 34, 0.85);
    --text-main: #fce7f3;
    --text-dim: #94a3b8;
    --line: #421e36;
    --region-cp-border: #ec4899;
    --region-wn-border: #f97316;
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

  /* Markdown Dropdown Menu */
  .dropdown {{
    position: relative;
    display: inline-block;
  }}
  .dropdown-toggle {{
    user-select: none;
  }}
  .dropdown-menu {{
    display: none;
    position: absolute;
    right: 0;
    top: calc(100% + 8px);
    background: #0d1527;
    border: 1px solid var(--panel-border);
    border-radius: 8px;
    min-width: 320px;
    max-height: 480px;
    overflow-y: auto;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7), 0 0 20px rgba(56, 189, 248, 0.15);
    z-index: 1000;
    padding: 8px 0;
    backdrop-filter: blur(8px);
  }}
  .dropdown-menu.show {{
    display: block;
    animation: fadeInDown 0.18s ease-out;
  }}
  @keyframes fadeInDown {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .dropdown-header {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    padding: 8px 16px 4px;
    font-weight: 700;
  }}
  .dropdown-divider {{
    height: 1px;
    background: var(--panel-border);
    margin: 6px 0;
  }}
  .dropdown-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    font-size: 12px;
    color: var(--text-main);
    text-decoration: none;
    transition: background 0.15s, color 0.15s;
  }}
  .dropdown-item:hover {{
    background: rgba(56, 189, 248, 0.12);
    color: #fff;
    text-decoration: none;
  }}
  .dropdown-item .icon {{
    font-size: 13px;
    min-width: 22px;
    font-weight: 700;
    color: var(--accent);
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
  .region-box {{ fill: none; stroke-width: 1.4; stroke-dasharray: 4 4; }}
  .region-cp {{ stroke: var(--region-cp-border); filter: drop-shadow(0 0 6px rgba(236, 72, 153, 0.3)); }}
  .region-wn {{ stroke: var(--region-wn-border); filter: drop-shadow(0 0 6px rgba(249, 115, 22, 0.3)); }}
  .region-neutral {{ stroke: #64748b; }}
  .region-label {{ fill: #f472b6; font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }}
  .region-wn + .region-label, rect.region-wn ~ text.region-label {{ fill: #fb923c !important; }}

  .node-box {{
    stroke-width: 1.3;
    transition: stroke 0.25s ease, filter 0.25s ease, fill 0.25s ease;
    cursor: pointer;
  }}
  .node-box.cp {{ fill: var(--cp-tint); stroke: #ec4899; }}
  .node-box.wn {{ fill: var(--wn-tint); stroke: #f97316; }}
  .node-box.client {{ fill: #1a0f1b; stroke: #ef4444; }}
  .node-box.neutral {{ fill: #160e20; stroke: #db2777; }}
  
  .interactive-node:hover .node-box {{
    stroke: var(--accent);
    filter: drop-shadow(0 0 10px var(--accent-glow));
  }}
  .interactive-node:hover .node-title {{
    fill: #fb7185;
  }}
  .node-box.active {{
    stroke: #f43f5e !important;
    filter: drop-shadow(0 0 10px rgba(244, 63, 94, 0.9)) drop-shadow(0 0 20px rgba(249, 115, 22, 0.6)) !important;
  }}

  /* Distinct color highlights in master flow */
  #mEtcd .node-box {{ stroke: #ef4444 !important; fill: #240c12 !important; }}
  #mApi .node-box {{ stroke: #f43f5e !important; }}
  #mSched .node-box {{ stroke: #ec4899 !important; }}
  #mCtrl .node-box {{ stroke: #f472b6 !important; }}
  #mKubelet .node-box {{ stroke: #ea580c !important; }}
  #mProxy .node-box {{ stroke: #f97316 !important; }}
  #mCri .node-box {{ stroke: #fb923c !important; }}
  #mCni .node-box {{ stroke: #fdba74 !important; }}

  .node-title {{ fill: #ffffff; font-size: 12px; font-weight: 600; transition: fill 0.25s ease; cursor: pointer; }}
  .node-title.active {{ fill: #fb7185; text-shadow: 0 0 8px rgba(251, 113, 133, 0.7); }}
  .node-sub {{ fill: #cbd5e1; font-size: 9.5px; cursor: pointer; }}

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
    fill: #ff5722; filter: drop-shadow(0 0 8px #ff5722) drop-shadow(0 0 16px #ec4899);
    opacity: 0; transition: opacity 0.2s ease, cx 0.55s cubic-bezier(.4,0,.2,1), cy 0.55s cubic-bezier(.4,0,.2,1);
  }}
  .packet.on {{ opacity: 1; }}

  /* Rich Technical Discussion & Manifest Typography */
  .content-h3 {{ font-size: 15px; font-weight: 700; color: #fb7185; margin: 20px 0 10px; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #3d1b32; padding-bottom: 4px; }}
  .content-h4 {{ font-size: 13.5px; font-weight: 700; color: #f97316; margin: 16px 0 8px; letter-spacing: 0.04em; }}
  .content-h5 {{ font-size: 12px; font-weight: 600; color: #fdba74; margin: 12px 0 6px; }}
  .content-p {{ font-size: 12px; line-height: 1.7; color: #e2e8f0; margin-bottom: 12px; }}
  .content-list {{ margin: 8px 0 14px 18px; list-style-type: none; }}
  .content-list li {{ position: relative; font-size: 12px; line-height: 1.65; color: #cbd5e1; margin-bottom: 7px; }}
  .content-list li::before {{ content: "▸"; position: absolute; left: -16px; color: #f43f5e; font-weight: bold; }}
  .inline-code {{ background: rgba(244, 63, 94, 0.12); border: 1px solid rgba(244, 63, 94, 0.28); color: #fda4af; padding: 1px 5px; border-radius: 4px; font-size: 11px; }}

  .code-block-wrapper {{ margin: 14px 0 18px; border-radius: 8px; border: 1px solid #3d1b32; overflow: hidden; background: #080c16; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }}
  .code-block-header {{ background: #150e1d; padding: 7px 12px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #291427; font-size: 10.5px; font-weight: 700; color: #fb7185; letter-spacing: 0.08em; }}
  .code-header-left {{ display: flex; align-items: center; gap: 8px; }}
  .code-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
  .code-dot.red {{ background: #ef4444; }}
  .code-dot.yellow {{ background: #f59e0b; }}
  .code-dot.green {{ background: #10b981; }}
  .code-filename {{ background: rgba(255,255,255,0.08); color: #cbd5e1; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-family: inherit; font-weight: 500; letter-spacing: 0.02em; border: 1px solid rgba(255,255,255,0.12); }}
  .code-box {{ background: transparent; padding: 12px 16px; overflow-x: auto; margin: 0; font-family: inherit; font-size: 11.5px; line-height: 1.55; color: #f1f5f9; white-space: pre; }}

  /* Copy Button */
  .code-copy-btn {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #e2e8f0;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 10.5px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.18s ease;
    user-select: none;
  }}
  .code-copy-btn:hover {{
    background: rgba(244, 63, 94, 0.22);
    border-color: #f43f5e;
    color: #fff;
    transform: translateY(-1px);
  }}
  .code-copy-btn.copied {{
    background: rgba(16, 185, 129, 0.2);
    border-color: #10b981;
    color: #10b981;
  }}

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

  /* Sections in Topic View */
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
  .demo-card {{
    background: #050811;
    border: 1px solid #1f293d;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  }}
  .demo-card-header {{
    background: #0f172a;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e293b;
    font-size: 11px;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 0.06em;
  }}
  .demo-card-meta {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .demo-card-title {{
    color: #38bdf8;
  }}
  .demo-card-actions {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .demo-content-area {{
    padding: 14px 16px;
    font-size: 12px;
    line-height: 1.6;
    color: #f8fafc;
    overflow-x: auto;
    white-space: pre-wrap;
    font-family: inherit;
    background: #050811;
  }}
  .demo-section-label {{
    color: #f43f5e;
    font-weight: 700;
    font-size: 11.5px;
    letter-spacing: 0.05em;
    margin-top: 14px;
    margin-bottom: 4px;
    display: block;
  }}
  .demo-section-label:first-child {{
    margin-top: 0;
  }}
  .demo-yaml-subcard {{
    margin: 10px 0 14px;
    border: 1px solid #3d1b32;
    background: #080c16;
    border-radius: 6px;
    overflow: hidden;
  }}
  .demo-yaml-subcard-header {{
    background: #181122;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 10.5px;
    font-weight: 700;
    color: #fb7185;
    border-bottom: 1px solid #291427;
  }}
  .demo-yaml-pre {{
    margin: 0;
    padding: 12px 14px;
    color: #f1f5f9;
    font-size: 11.5px;
    line-height: 1.55;
    overflow-x: auto;
    font-family: inherit;
    white-space: pre;
    background: transparent;
  }}

  /* Markdown Reader Modal */
  .md-modal-backdrop {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.82);
    backdrop-filter: blur(5px);
    z-index: 1000;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }}
  .md-modal-backdrop.show {{
    display: flex;
  }}
  .md-modal-container {{
    background: var(--bg);
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    width: 100%;
    max-width: 1020px;
    height: 88vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85);
    overflow: hidden;
  }}
  .md-modal-header {{
    background: var(--panel);
    padding: 12px 18px;
    border-bottom: 1px solid var(--panel-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    flex-shrink: 0;
  }}
  .md-modal-title-wrap {{
    display: flex;
    align-items: center;
    gap: 10px;
    overflow: hidden;
  }}
  .md-modal-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: var(--accent);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .md-modal-actions {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }}
  .md-modal-search {{
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid var(--panel-border);
    color: var(--text-main);
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 11px;
    font-family: inherit;
    width: 180px;
    outline: none;
  }}
  .md-modal-search:focus {{
    border-color: var(--accent);
  }}
  .md-modal-close {{
    background: transparent;
    border: none;
    color: var(--text-dim);
    font-size: 18px;
    cursor: pointer;
    padding: 2px 6px;
    line-height: 1;
    border-radius: 4px;
    transition: all 0.15s ease;
  }}
  .md-modal-close:hover {{
    color: #fff;
    background: rgba(244, 63, 94, 0.25);
  }}
  .md-modal-body {{
    padding: 28px 32px;
    overflow-y: auto;
    flex: 1;
    font-size: 13px;
    line-height: 1.7;
    color: #e2e8f0;
  }}
  .md-modal-body h1 {{ font-size: 20px; color: #fb7185; margin: 0 0 16px; border-bottom: 1px solid var(--panel-border); padding-bottom: 8px; }}
  .md-modal-body h2 {{ font-size: 16px; color: #f97316; margin: 26px 0 12px; border-bottom: 1px solid #291427; padding-bottom: 4px; }}
  .md-modal-body h3 {{ font-size: 14px; color: #fdba74; margin: 20px 0 8px; }}
  .md-modal-body h4 {{ font-size: 12.5px; color: #f43f5e; margin: 14px 0 6px; }}
  .md-modal-body p {{ margin-bottom: 12px; }}
  .md-modal-body table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 11.5px; }}
  .md-modal-body th, .md-modal-body td {{ border: 1px solid var(--panel-border); padding: 7px 10px; text-align: left; }}
  .md-modal-body th {{ background: var(--panel); color: var(--accent); font-weight: 700; }}
  .md-modal-body tr:nth-child(even) {{ background: rgba(255, 255, 255, 0.02); }}
  .md-modal-body img {{ max-width: 100%; border-radius: 6px; margin: 12px 0; border: 1px solid var(--panel-border); }}
  .md-modal-body blockquote {{ border-left: 3px solid var(--accent); padding: 6px 14px; background: rgba(244, 63, 94, 0.06); margin: 14px 0; color: #cbd5e1; border-radius: 0 4px 4px 0; }}

  /* Interactive Quiz Styles */
  .quiz-card {{
    background: #080d1a;
    border: 1px solid var(--panel-border);
    border-radius: 8px;
    padding: 18px 16px;
    margin-bottom: 18px;
  }}
  .quiz-question {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 14px;
    line-height: 1.5;
  }}
  .quiz-options {{
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .quiz-opt {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    text-align: left;
    font-family: inherit;
    line-height: 1.5;
  }}
  .quiz-opt:hover:not(:disabled) {{
    border-color: var(--accent);
    background: #142036;
  }}
  .quiz-opt.selected-correct {{
    border-color: #10b981 !important;
    background: rgba(16, 185, 129, 0.15) !important;
    color: #34d399 !important;
    font-weight: 600;
  }}
  .quiz-opt.selected-incorrect {{
    border-color: #ef4444 !important;
    background: rgba(239, 68, 68, 0.15) !important;
    color: #f87171 !important;
  }}
  .quiz-opt.reveal-correct {{
    border-color: #10b981 !important;
    background: rgba(16, 185, 129, 0.1) !important;
    color: #34d399 !important;
  }}
  .quiz-explanation {{
    margin-top: 14px;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 11.5px;
    line-height: 1.6;
    display: none;
  }}
  .quiz-explanation.correct {{
    background: rgba(16, 185, 129, 0.1);
    border-left: 3px solid #10b981;
    color: #e5edf7;
  }}
  .quiz-explanation.incorrect {{
    background: rgba(239, 68, 68, 0.1);
    border-left: 3px solid #ef4444;
    color: #e5edf7;
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
      <div class="dropdown">
        <button class="btn dropdown-toggle" id="markdownDropdownBtn" onclick="toggleMarkdownMenu(event)">
          📄 View Markdown ▾
        </button>
        <div class="dropdown-menu" id="markdownDropdownMenu">
          <div class="dropdown-header">Apartment Demos</div>
          <a href="demos-complete.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'demos-complete.md', 'Complete Apartment Demos ({total_topics} Topics)')">
            <span class="icon">🏢</span> Complete Apartment Demos ({total_topics} Topics)
          </a>
          <div class="dropdown-divider"></div>
          <div class="dropdown-header">CKA Exam Study Notes</div>
          <a href="CKA_Study_Notes/README.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/README.md', 'CKA Notes Overview &amp; Curriculum')">
            <span class="icon">📚</span> CKA Notes Overview &amp; Curriculum
          </a>
          <a href="CKA_Study_Notes/01-core-concepts.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/01-core-concepts.md', '01 Core Concepts &amp; Architecture')">
            <span class="icon">01</span> Core Concepts &amp; Architecture
          </a>
          <a href="CKA_Study_Notes/02-scheduling.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/02-scheduling.md', '02 Scheduling, Topology Spread &amp; PDB')">
            <span class="icon">02</span> Scheduling, Topology Spread &amp; PDB
          </a>
          <a href="CKA_Study_Notes/03-logging-and-monitoring.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/03-logging-and-monitoring.md', '03 Logging, Metrics &amp; JSONPath')">
            <span class="icon">03</span> Logging, Metrics &amp; JSONPath
          </a>
          <a href="CKA_Study_Notes/04-application-lifecycle-management.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/04-application-lifecycle-management.md', '04 Application Lifecycle &amp; Config')">
            <span class="icon">04</span> Application Lifecycle &amp; Config
          </a>
          <a href="CKA_Study_Notes/05-cluster-maintenance.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/05-cluster-maintenance.md', '05 Cluster Upgrades &amp; Maintenance')">
            <span class="icon">05</span> Cluster Upgrades &amp; Maintenance
          </a>
          <a href="CKA_Study_Notes/06-security.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/06-security.md', '06 Security, Projected Tokens &amp; RBAC')">
            <span class="icon">06</span> Security, Projected Tokens &amp; RBAC
          </a>
          <a href="CKA_Study_Notes/07-networking.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/07-networking.md', '07 Networking, Ingress v1 &amp; Gateway')">
            <span class="icon">07</span> Networking, Ingress v1 &amp; Gateway
          </a>
          <a href="CKA_Study_Notes/08-storage.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/08-storage.md', '08 Storage, PVC Expansion &amp; Snapshots')">
            <span class="icon">08</span> Storage, PVC Expansion &amp; Snapshots
          </a>
          <a href="CKA_Study_Notes/09-cluster-design-and-installation.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/09-cluster-design-and-installation.md', '09 Cluster Design &amp; Installation')">
            <span class="icon">09</span> Cluster Design &amp; Installation
          </a>
          <a href="CKA_Study_Notes/10-troubleshooting.md" class="dropdown-item" onclick="openMarkdownViewer(event, 'CKA_Study_Notes/10-troubleshooting.md', '10 Troubleshooting &amp; kubectl debug')">
            <span class="icon">10</span> Troubleshooting &amp; kubectl debug
          </a>
        </div>
      </div>
    </div>
  </header>

  <main class="main-wrap">

    <!-- VIEW 1: HOME PAGE (Interactive Architecture Diagram + Topics Index) -->
    <div id="homeView">
      <div class="hero-heading">
        <h1>Kubernetes Architecture Overview</h1>
        <p>Minimalist system design · Click any component box to explore the topic</p>
      </div>

      <!-- Master Architecture SVG Diagram -->
      <div class="arch-diagram-card">
        <div class="stage-label-bar" id="masterStageLabel">Click any component below to jump to its topic, or press Play to trace cluster request flow</div>
        
        <div class="controls-bar">
          <button class="btn btn-primary" id="masterPlayBtn" onclick="toggleMasterPlay()">▶ Play End-to-End Flow</button>
          <button class="btn" id="masterPrevBtn" onclick="masterPrevStep()" title="Previous Stage">← Prev</button>
          <button class="btn" id="masterNextBtn" onclick="masterNextStep()" title="Next Stage">Next →</button>
          <button class="btn" onclick="resetMasterFlow()">↺ Reset</button>
          <span id="masterStepIndicator" style="font-family:var(--font-mono);font-size:12px;color:var(--text-dim);margin-left:6px;font-weight:600;min-width:85px;text-align:center;">Step 0 / 17</span>
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
            <text class="node-title" x="255" y="374" text-anchor="middle">Workload Controllers &amp; Operators</text>
            <text class="node-sub" x="255" y="392" text-anchor="middle">Topics 32-38, 45 · Deployments, StatefulSets, Jobs, Operators</text>
          </g>

          <g class="interactive-node" id="mRbac" onclick="goToTopic(23)">
            <rect class="node-box cp" x="50" y="426" width="410" height="54" rx="10"/>
            <text class="node-title" x="255" y="448" text-anchor="middle">Security, RBAC &amp; Governance</text>
            <text class="node-sub" x="255" y="466" text-anchor="middle">Topics 23-31, 44, 46 · Roles, Quotas, PSA, LimitRanges</text>
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
            <text class="node-title" x="745" y="298" text-anchor="middle">Pods, Sidecars &amp; Health Probes</text>
            <text class="node-sub" x="745" y="316" text-anchor="middle">Topics 08, 12, 13, 42 · Application Sandboxes &amp; Probes</text>
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
            <text class="node-title" x="500" y="586" text-anchor="middle">Services &amp; EndpointSlices</text>
            <text class="node-sub" x="500" y="606" text-anchor="middle">Topics 16, 17, 43 · ClusterIP, Headless &amp; Slices</text>
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

          <line class="connector" id="mc_rbac" x1="255" y1="174" x2="255" y2="426"/>
          <line class="connector connector-dash" id="mc_rbacd" x1="255" y1="174" x2="255" y2="426"/>

          <line class="connector" id="mc_ctrl" x1="147" y1="252" x2="147" y2="274"/>
          <line class="connector connector-dash" id="mc_ctrld" x1="147" y1="252" x2="147" y2="274"/>

          <line class="connector" id="mc_workload" x1="147" y1="330" x2="255" y2="352"/>
          <line class="connector connector-dash" id="mc_workloadd" x1="147" y1="330" x2="255" y2="352"/>

          <line class="connector" id="mc_cni" x1="852" y1="174" x2="852" y2="196"/>
          <line class="connector connector-dash" id="mc_cnid" x1="852" y1="174" x2="852" y2="196"/>

          <path class="connector" id="mc_storage" d="M852 252 L852 352 L745 352" fill="none"/>
          <path class="connector connector-dash" id="mc_storaged" d="M852 252 L852 352 L745 352" fill="none"/>

          <line class="connector" id="mc_proxy" x1="637" y1="274" x2="637" y2="252"/>
          <line class="connector connector-dash" id="mc_proxyd" x1="637" y1="274" x2="637" y2="252"/>

          <line class="connector" id="mc_dns" x1="640" y1="592" x2="670" y2="592"/>
          <line class="connector connector-dash" id="mc_dnsd" x1="640" y1="592" x2="670" y2="592"/>

          <line class="connector" id="mc_ing" x1="360" y1="592" x2="330" y2="592"/>
          <line class="connector connector-dash" id="mc_ingd" x1="360" y1="592" x2="330" y2="592"/>

          <line class="connector" id="mc_auto" x1="745" y1="330" x2="745" y2="426"/>
          <line class="connector connector-dash" id="mc_autod" x1="745" y1="330" x2="745" y2="426"/>

          <circle class="packet" id="masterPacket" cx="500" cy="39" r="7"/>
        </svg>
      </div>

      <!-- Topics Directory & Search Filter -->
      <div class="section-title">
        <span>Topic Reference Catalog ({total_topics} Topics)</span>
        <span style="font-size: 11px; color: var(--text-dim); font-weight: normal;">Search or filter by category</span>
      </div>

      <div class="filter-controls">
        <input type="text" id="topicSearch" class="search-input" placeholder="Search topic by name, component, or keyword..." oninput="filterTopics()">
        {category_pills_str}
      </div>

      <div class="topics-grid" id="topicsGrid">
        <!-- Dynamically populated via JS -->
      </div>
    </div>

    <!-- VIEW 2: TOPIC VIEW (6 Parts including Quiz) -->
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
          Interactive component flow simulation · Play to trace request packet hops across component boundaries · <a id="topicDiagramLink" href="" target="_blank" style="color: var(--accent);">Open in standalone tab ↗</a>
        </p>
        <div class="diagram-iframe-wrap">
          <iframe id="topicDiagramIframe" class="diagram-iframe" src="" title="Component Diagram"></iframe>
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
        <div class="demo-card">
          <div class="demo-card-header">
            <div class="demo-card-meta">
              <span class="code-dot red"></span>
              <span class="code-dot yellow"></span>
              <span class="code-dot green"></span>
              <span class="demo-card-title">TERMINAL EXPERIMENT &amp; MANIFESTS</span>
            </div>
            <div class="demo-card-actions">
              <button class="code-copy-btn" id="copyDemoYamlBtn" style="display:none;" onclick="copyDemoYaml(this)" title="Copy YAML Manifest only">
                <svg class="copy-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                <span class="copy-text" id="copyDemoYamlText">Copy YAML</span>
              </button>
              <button class="code-copy-btn" id="copyDemoAllBtn" onclick="copyDemoAll(this)" title="Copy complete runnable demo script">
                <svg class="copy-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                <span class="copy-text">Copy All Demo</span>
              </button>
            </div>
          </div>
          <div id="topicDemoParsed" class="demo-content-area"></div>
          <pre id="topicDemo" style="display:none;"></pre>
        </div>
      </section>

      <!-- PART 6: Knowledge Check — Interactive Quiz -->
      <section class="part-section">
        <div class="part-header">Part 6 — Knowledge Check (Interactive Quiz)</div>
        <p class="part-text" style="color: var(--text-dim); font-size: 11.5px; margin-bottom: 14px;">
          Test your operational understanding. Select an option to check your answer and view the detailed architectural rationale.
        </p>
        <div id="topicQuizContainer">
          <!-- Dynamically populated via JS -->
        </div>
      </section>
    </div>

  </main>

  <footer class="site-footer">
    Kubernetes Apartment Complex · Minimalist Tech / System Design Architecture Guide · Local Edition
  </footer>

  <!-- Interactive Markdown Viewer Modal -->
  <div id="markdownModal" class="md-modal-backdrop" onclick="handleModalBackdropClick(event)">
    <div class="md-modal-container" onclick="event.stopPropagation()">
      <div class="md-modal-header">
        <div class="md-modal-title-wrap">
          <span style="font-size:16px;">📄</span>
          <span class="md-modal-title" id="mdModalTitle">Markdown Document</span>
        </div>
        <div class="md-modal-actions">
          <input type="text" id="mdModalSearch" class="md-modal-search" placeholder="Search in document..." oninput="filterModalContent(this.value)" />
          <a id="mdRawLink" href="" target="_blank" class="code-copy-btn" style="text-decoration:none;">Open Raw .md ↗</a>
          <button class="md-modal-close" onclick="closeMarkdownModal()" title="Close (Esc)">✕</button>
        </div>
      </div>
      <div class="md-modal-body" id="mdModalBody">
        <!-- Dynamically rendered markdown with copy buttons -->
      </div>
    </div>
  </div>

  <script>
    const TOPICS = {topics_json};
    let currentCategory = 'All';
    let currentTopicNum = 1;

    // Master Diagram Flow Stages (17-stop complete cluster lifecycle)
    const masterStages = [
      {{ id: 'mClient',    dot: {{x: 500, y: 39}},  label: 'Step 1/17: Client / kubectl submits declarative manifest to cluster', conns: [] }},
      {{ id: 'mApi',       dot: {{x: 255, y: 147}}, label: 'Step 2/17: kube-apiserver authenticates identity and validates OpenAPI schema', conns: ['mc0'] }},
      {{ id: 'mRbac',      dot: {{x: 255, y: 453}}, label: 'Step 3/17: Security & Admission pipeline enforces RBAC roles, LimitRanges & PSA quotas', conns: ['mc_rbac'] }},
      {{ id: 'mEtcd',      dot: {{x: 147, y: 224}}, label: 'Step 4/17: etcd commits declared target state to distributed Raft consensus log', conns: ['mc1'] }},
      {{ id: 'mCtrl',      dot: {{x: 147, y: 302}}, label: 'Step 5/17: kube-controller-manager detects spec divergence and begins reconciliation loop', conns: ['mc_ctrl'] }},
      {{ id: 'mWorkload',  dot: {{x: 255, y: 379}}, label: 'Step 6/17: Deployment / ReplicaSet controller generates unassigned Pod specifications', conns: ['mc_workload'] }},
      {{ id: 'mSched',     dot: {{x: 362, y: 224}}, label: 'Step 7/17: kube-scheduler filters candidate worker nodes and scores optimal placement', conns: ['mc2'] }},
      {{ id: 'mKubelet',   dot: {{x: 637, y: 147}}, label: 'Step 8/17: kubelet on selected worker node picks up assigned Pod via API watch', conns: ['mc3'] }},
      {{ id: 'mCri',       dot: {{x: 852, y: 147}}, label: 'Step 9/17: Container runtime (CRI) pulls image layers and creates container sandbox', conns: ['mc4'] }},
      {{ id: 'mCni',       dot: {{x: 852, y: 224}}, label: 'Step 10/17: CNI network plugin allocates unique Pod IP and configures veth pair', conns: ['mc_cni'] }},
      {{ id: 'mStorage',   dot: {{x: 745, y: 379}}, label: 'Step 11/17: CSI storage driver binds PVC and attaches PersistentVolume mount to Pod', conns: ['mc_storage'] }},
      {{ id: 'mPods',      dot: {{x: 745, y: 302}}, label: 'Step 12/17: Pod starts, passes startup/readiness health probes, and transitions to Running', conns: ['mc5'] }},
      {{ id: 'mProxy',     dot: {{x: 637, y: 224}}, label: 'Step 13/17: kube-proxy syncs endpoint addresses and programs kernel iptables / IPVS NAT', conns: ['mc_proxy'] }},
      {{ id: 'mServices',  dot: {{x: 500, y: 592}}, label: 'Step 14/17: EndpointSlice controller adds healthy Pod IP to ClusterIP Service endpoints', conns: ['mc6'] }},
      {{ id: 'mCoreDns',   dot: {{x: 810, y: 592}}, label: 'Step 15/17: CoreDNS dynamically registers cluster-internal service discovery A/SRV records', conns: ['mc_dns'] }},
      {{ id: 'mIngress',   dot: {{x: 190, y: 592}}, label: 'Step 16/17: Ingress Controller / Gateway routes external HTTP/TLS requests to Service', conns: ['mc_ing'] }},
      {{ id: 'mAutoscale', dot: {{x: 745, y: 453}}, label: 'Step 17/17: Horizontal Pod Autoscaler (HPA) monitors traffic metrics to adjust replicas', conns: ['mc_auto'] }}
    ];

    const masterNodeIds = ['mClient','mApi','mEtcd','mSched','mCtrl','mCcm','mWorkload','mRbac','mKubelet','mCri','mProxy','mCni','mPods','mStorage','mAutoscale','mIngress','mServices','mCoreDns'];
    const masterConnIds = ['mc0','mc1','mc2','mc3','mc4','mc5','mc6','mc_rbac','mc_ctrl','mc_workload','mc_cni','mc_storage','mc_proxy','mc_dns','mc_ing','mc_auto'];
    let masterCurrentStep = -1;
    let masterPlaying = false;
    let masterTimer = null;

    function masterClearHighlights() {{
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
    }}

    function masterUpdateControls() {{
      const playBtn = document.getElementById('masterPlayBtn');
      const ind = document.getElementById('masterStepIndicator');
      if (playBtn) {{
        playBtn.textContent = masterPlaying ? '⏸ Pause' : (masterCurrentStep >= 0 && masterCurrentStep < masterStages.length - 1 ? '▶ Resume' : '▶ Play End-to-End Flow');
      }}
      if (ind) {{
        ind.textContent = masterCurrentStep >= 0 ? `Step ${{masterCurrentStep + 1}} / ${{masterStages.length}}` : `Step 0 / ${{masterStages.length}}`;
      }}
    }}

    function masterShowStep(idx) {{
      if (idx < 0 || idx >= masterStages.length) return;
      masterCurrentStep = idx;
      masterClearHighlights();

      const s = masterStages[idx];
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
      if (pkt) {{
        pkt.classList.add('on');
        pkt.setAttribute('cx', s.dot.x);
        pkt.setAttribute('cy', s.dot.y);
      }}

      document.getElementById('masterStageLabel').textContent = s.label;
      masterUpdateControls();
    }}

    function masterPause() {{
      masterPlaying = false;
      clearTimeout(masterTimer);
      masterUpdateControls();
    }}

    function masterNextStep() {{
      masterPause();
      const nextIdx = (masterCurrentStep + 1) % masterStages.length;
      masterShowStep(nextIdx);
    }}

    function masterPrevStep() {{
      masterPause();
      const prevIdx = masterCurrentStep > 0 ? masterCurrentStep - 1 : masterStages.length - 1;
      masterShowStep(prevIdx);
    }}

    function resetMasterFlow() {{
      masterPlaying = false;
      clearTimeout(masterTimer);
      masterCurrentStep = -1;
      masterClearHighlights();
      const pkt = document.getElementById('masterPacket');
      if (pkt) pkt.classList.remove('on');
      document.getElementById('masterStageLabel').textContent = 'Click any component below to jump to its topic, or use Next → / Play to trace cluster request flow';
      masterUpdateControls();
    }}

    function toggleMasterPlay() {{
      if (masterPlaying) {{
        masterPause();
      }} else {{
        masterPlaying = true;
        masterUpdateControls();
        if (masterCurrentStep >= masterStages.length - 1 || masterCurrentStep < 0) {{
          masterShowStep(0);
        }}
        function autoStep() {{
          if (!masterPlaying) return;
          if (masterCurrentStep >= masterStages.length - 1) {{
            masterPlaying = false;
            document.getElementById('masterStageLabel').textContent = 'End-to-End Cluster Request Flow Complete ✓ (Click any box to inspect deep-dive)';
            masterUpdateControls();
            return;
          }}
          masterShowStep(masterCurrentStep + 1);
          masterTimer = setTimeout(autoStep, 1500);
        }}
        masterTimer = setTimeout(autoStep, 1500);
      }}
    }}

    function playMasterFlow() {{
      toggleMasterPlay();
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

      document.getElementById('topicBadge').textContent = 'Topic ' + String(topic.num).padStart(2, '0') + ' / ' + TOPICS.length;
      document.getElementById('topicTitle').textContent = topic.title;
      document.getElementById('topicMeta').textContent = topic.category + ' · Technical Reference & Apartment Zine';

      document.getElementById('topicTechDisc').innerHTML = formatRichMarkdown(topic.tech_disc);
      document.getElementById('topicTechPersp').innerHTML = formatRichMarkdown(topic.tech_persp);
      document.getElementById('topicTechImg').src = topic.tech_img;

      document.getElementById('topicDiagramIframe').src = topic.diagram;
      document.getElementById('topicDiagramLink').href = topic.diagram;

      document.getElementById('topicZineAnalogy').textContent = topic.zine_analogy;
      document.getElementById('topicZineImg').src = topic.zine_img;
      document.getElementById('topicZineExp').textContent = topic.zine_exp;

      document.getElementById('topicReading').innerHTML = formatMarkdownLinks(topic.reading);
      renderDemoBlock(topic.demo);

      // Render Quiz
      renderQuiz(topic.quiz || []);

      document.getElementById('prevTopicBtn').disabled = (num <= 1);
      document.getElementById('nextTopicBtn').disabled = (num >= TOPICS.length);

      window.scrollTo(0, 0);
    }}

    function renderQuiz(questions) {{
      const container = document.getElementById('topicQuizContainer');
      container.innerHTML = '';
      if (!questions || questions.length === 0) {{
        container.innerHTML = '<div style="color: var(--text-dim); font-size: 12px;">No quiz questions currently available for this topic.</div>';
        return;
      }}

      questions.forEach((q, qIndex) => {{
        const card = document.createElement('div');
        card.className = 'quiz-card';
        card.id = `quizCard_${{qIndex}}`;

        const qTitle = document.createElement('div');
        qTitle.className = 'quiz-question';
        qTitle.textContent = `Q${{qIndex + 1}}: ${{q.question}}`;
        card.appendChild(qTitle);

        const optionsWrap = document.createElement('div');
        optionsWrap.className = 'quiz-options';

        const optLetters = ['A', 'B', 'C', 'D'];
        q.options.forEach((optText, optIndex) => {{
          const optBtn = document.createElement('button');
          optBtn.className = 'quiz-opt';
          optBtn.id = `opt_${{qIndex}}_${{optIndex}}`;
          optBtn.innerHTML = `<strong>${{optLetters[optIndex]}})</strong> <span>${{optText}}</span>`;
          optBtn.onclick = () => selectQuizAnswer(qIndex, optIndex, q.answer, q.explanation);
          optionsWrap.appendChild(optBtn);
        }});
        card.appendChild(optionsWrap);

        const expBox = document.createElement('div');
        expBox.className = 'quiz-explanation';
        expBox.id = `exp_${{qIndex}}`;
        card.appendChild(expBox);

        container.appendChild(card);
      }});
    }}

    function selectQuizAnswer(qIndex, selectedIndex, correctIndex, explanation) {{
      const card = document.getElementById(`quizCard_${{qIndex}}`);
      if (!card) return;

      const buttons = card.querySelectorAll('.quiz-opt');
      buttons.forEach(btn => btn.disabled = true);

      const isCorrect = (selectedIndex === correctIndex);
      const selectedBtn = document.getElementById(`opt_${{qIndex}}_${{selectedIndex}}`);
      const correctBtn = document.getElementById(`opt_${{qIndex}}_${{correctIndex}}`);
      const expBox = document.getElementById(`exp_${{qIndex}}`);

      if (isCorrect) {{
        selectedBtn.classList.add('selected-correct');
        selectedBtn.innerHTML += ' ✓';
        expBox.className = 'quiz-explanation correct';
        expBox.innerHTML = `<strong>Correct!</strong> ${{explanation}}`;
      }} else {{
        selectedBtn.classList.add('selected-incorrect');
        selectedBtn.innerHTML += ' ✗';
        correctBtn.classList.add('reveal-correct');
        correctBtn.innerHTML += ' (Correct Answer)';
        expBox.className = 'quiz-explanation incorrect';
        expBox.innerHTML = `<strong>Incorrect.</strong> ${{explanation}}`;
      }}
      expBox.style.display = 'block';
    }}

    function navigateTopic(delta) {{
      const target = currentTopicNum + delta;
      if (target >= 1 && target <= TOPICS.length) {{
        goToTopic(target);
      }}
    }}

    function stripMarkdown(text) {{
      if (!text) return "";
      return text.replace(/```[\\s\\S]*?```/g, "")
                 .replace(/###+[\\s]+/g, "")
                 .replace(/[-*][\\s]+/g, "")
                 .replace(/[*_`]/g, "")
                 .replace(/[\\r\\n]+/g, " ")
                 .trim();
    }}

    function escapeHtml(str) {{
      return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }}

    // Clipboard Utility
    function copyTextToClipboard(text, btn, successLabel) {{
      const originalHtml = btn.innerHTML;
      function showSuccess() {{
        btn.classList.add('copied');
        btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> <span style="color:#10b981; font-weight:700;">${{successLabel || 'Copied!'}}</span>`;
        setTimeout(() => {{
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }}, 2000);
      }}

      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(text).then(showSuccess).catch(err => {{
          fallbackCopyText(text, showSuccess);
        }});
      }} else {{
        fallbackCopyText(text, showSuccess);
      }}
    }}

    function fallbackCopyText(text, callback) {{
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      ta.style.top = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {{
        document.execCommand('copy');
        if (callback) callback();
      }} catch (e) {{
        console.error('Fallback copy failed', e);
      }}
      document.body.removeChild(ta);
    }}

    function copySnippet(btn) {{
      const wrapper = btn.closest('.code-block-wrapper') || btn.closest('.demo-yaml-subcard');
      if (!wrapper) return;
      const codeEl = wrapper.querySelector('code') || wrapper.querySelector('pre');
      if (!codeEl) return;
      copyTextToClipboard(codeEl.innerText || codeEl.textContent, btn, 'Copied!');
    }}

    function copyDemoAll(btn) {{
      const rawPre = document.getElementById('topicDemo');
      if (!rawPre) return;
      copyTextToClipboard(rawPre.textContent, btn, 'Copied Demo!');
    }}

    let currentDemoYamlContent = null;
    function copyDemoYaml(btn) {{
      if (currentDemoYamlContent) {{
        copyTextToClipboard(currentDemoYamlContent, btn, 'Copied YAML!');
      }}
    }}

    function copyDemoYamlDirect(btn) {{
      const subcard = btn.closest('.demo-yaml-subcard');
      if (!subcard) return;
      const codeEl = subcard.querySelector('code');
      if (codeEl) {{
        copyTextToClipboard(codeEl.innerText || codeEl.textContent, btn, 'Copied YAML!');
      }}
    }}

    function renderDemoBlock(demoText) {{
      const container = document.getElementById('topicDemoParsed');
      const rawPre = document.getElementById('topicDemo');
      rawPre.textContent = demoText || '';
      
      if (!demoText) {{
        container.innerHTML = '<span style="color:var(--text-dim)">No demo experiment available.</span>';
        document.getElementById('copyDemoYamlBtn').style.display = 'none';
        currentDemoYamlContent = null;
        return;
      }}

      // Look for YAML (filename.yaml) block inside demoText
      const yamlMatch = demoText.match(/YAML\\s+\\(([^)]+)\\)\\n((?:  .*\\n?)+)/);
      if (yamlMatch) {{
        const filename = yamlMatch[1].trim();
        const rawYamlLines = yamlMatch[2].split('\\n');
        const unindentedYaml = rawYamlLines.map(l => l.startsWith('  ') ? l.slice(2) : l).join('\\n').trim();
        currentDemoYamlContent = unindentedYaml;
        
        const yamlBtn = document.getElementById('copyDemoYamlBtn');
        document.getElementById('copyDemoYamlText').textContent = 'Copy YAML (' + filename + ')';
        yamlBtn.style.display = 'inline-flex';

        const before = demoText.substring(0, yamlMatch.index);
        const after = demoText.substring(yamlMatch.index + yamlMatch[0].length);

        container.innerHTML = formatDemoSectionText(before) +
          `<div class="demo-yaml-subcard">` +
            `<div class="demo-yaml-subcard-header">` +
              `<div style="display:flex; align-items:center; gap:8px;">` +
                `<span class="code-dot yellow"></span>` +
                `<span style="color:#fdba74; font-weight:700;">YAML MANIFEST</span>` +
                `<span class="code-filename">${{escapeHtml(filename)}}</span>` +
              `</div>` +
              `<button class="code-copy-btn" onclick="copyDemoYamlDirect(this)" title="Copy ${{escapeHtml(filename)}}">` +
                `<svg class="copy-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>` +
                `<span class="copy-text">Copy YAML</span>` +
              `</button>` +
            `</div>` +
            `<pre class="demo-yaml-pre"><code>${{escapeHtml(unindentedYaml)}}</code></pre>` +
          `</div>` +
          formatDemoSectionText(after);
      }} else {{
        currentDemoYamlContent = null;
        document.getElementById('copyDemoYamlBtn').style.display = 'none';
        container.innerHTML = formatDemoSectionText(demoText);
      }}
    }}

    function formatDemoSectionText(text) {{
      if (!text) return '';
      return text.split('\\n').map(line => {{
        const trimmed = line.trim();
        if (['SETUP', 'STEPS', 'WHAT YOU SHOULD SEE', 'CLEANUP', 'NOTE'].includes(trimmed)) {{
          return `<div class="demo-section-label">▸ ${{escapeHtml(trimmed)}}</div>`;
        }}
        return escapeHtml(line);
      }}).join('\\n');
    }}

    function formatRichMarkdown(text) {{
      if (!text) return "";

      const codeBlocks = [];
      let working = text.replace(/```([a-zA-Z0-9_\\-]+)?[\\r\\n]([\\s\\S]*?)```/g, function(match, lang, code) {{
        let trimmed = code.trim();
        let displayLang = lang ? lang.toUpperCase() : "YAML / CONFIG";
        if (!lang) {{
          if (trimmed.includes("apiVersion:") || trimmed.includes("kind:")) displayLang = "YAML";
          else if (trimmed.includes("kubectl ") || trimmed.includes("curl ")) displayLang = "BASH";
        }}
        let filenameBadge = "";
        const lines = trimmed.split("\\n");
        if (lines[0] && lines[0].startsWith("# ") && lines[0].includes(".")) {{
          const fn = lines[0].replace(/^#\\s*/, "").trim();
          filenameBadge = `<span class="code-filename">${{escapeHtml(fn)}}</span>`;
        }}

        const placeholder = `__CODE_BLOCK_${{codeBlocks.length}}__`;
        codeBlocks.push(
          `<div class="code-block-wrapper">` +
            `<div class="code-block-header">` +
              `<div class="code-header-left">` +
                `<span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span>` +
                `<span class="code-lang">${{displayLang}}</span>` +
                filenameBadge +
              `</div>` +
              `<button class="code-copy-btn" onclick="copySnippet(this)" title="Copy snippet to clipboard">` +
                `<svg class="copy-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>` +
                `<span class="copy-text">Copy</span>` +
              `</button>` +
            `</div>` +
            `<pre class="code-box"><code>${{escapeHtml(trimmed)}}</code></pre>` +
          `</div>`
        );
        return `\\n\\n${{placeholder}}\\n\\n`;
      }});

      let html = escapeHtml(working);

      html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
      html = html.replace(/^#### (.*?)$/gm, '<h5 class="content-h5">$1</h5>');
      html = html.replace(/^### (.*?)$/gm, '<h4 class="content-h4">$1</h4>');
      html = html.replace(/^## (.*?)$/gm, '<h3 class="content-h3">$1</h3>');
      html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
      html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1 ↗</a>');

      const lines = html.split(/[\\r\\n]+/);
      let inList = false;
      let out = [];

      for (let i = 0; i < lines.length; i++) {{
        let line = lines[i].trim();
        if (!line) continue;

        const blockMatch = line.match(/^__CODE_BLOCK_(\\d+)__$/);
        if (blockMatch) {{
          if (inList) {{
            out.push("</ul>");
            inList = false;
          }}
          const idx = parseInt(blockMatch[1], 10);
          out.push(codeBlocks[idx]);
          continue;
        }}

        if (/^[-*][\\s]+(.*)$/.test(line)) {{
          let content = line.replace(/^[-*][\\s]+/, "");
          if (!inList) {{
            out.push('<ul class="content-list">');
            inList = true;
          }}
          out.push(`<li>${{content}}</li>`);
        }} else {{
          if (inList) {{
            out.push("</ul>");
            inList = false;
          }}
          if (line.startsWith("<h") || line.startsWith("<div") || line.startsWith("<pre")) {{
            out.push(line);
          }} else {{
            out.push(`<p class="content-p">${{line}}</p>`);
          }}
        }}
      }}
      if (inList) {{
        out.push("</ul>");
      }}

      return out.join('\\n');
    }}

    function formatMarkdownLinks(text) {{
      if (!text) return '<span style="color: var(--text-dim)">Refer to official Kubernetes documentation.</span>';
      return text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1 ↗</a>');
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
            <div class="topic-desc">${{stripMarkdown(t.tech_disc || t.tech_persp)}}</div>
          </div>
          <div class="topic-footer">
            Explore topic, diagram &amp; quiz →
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
      const match = hash.match(/^#\\/topic\\/(\\d+)$/);
      if (match) {{
        renderTopicView(parseInt(match[1], 10));
      }} else {{
        showHome();
      }}
    }});

    // Markdown Reader Modal Logic
    let originalModalHtml = '';
    function openMarkdownViewer(event, fileUrl, title) {{
      if (event) event.preventDefault();
      const menu = document.getElementById('markdownDropdownMenu');
      if (menu) menu.classList.remove('show');

      const modal = document.getElementById('markdownModal');
      const modalTitle = document.getElementById('mdModalTitle');
      const modalBody = document.getElementById('mdModalBody');
      const rawLink = document.getElementById('mdRawLink');
      const searchInput = document.getElementById('mdModalSearch');

      if (searchInput) searchInput.value = '';
      modalTitle.textContent = title || fileUrl;
      rawLink.href = fileUrl;
      modalBody.innerHTML = '<div style="padding:40px; text-align:center; color:var(--text-dim);"><div style="font-size:24px; margin-bottom:12px;">⏳</div>Loading document...</div>';
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';

      fetch(fileUrl)
        .then(res => {{
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.text();
        }})
        .then(mdText => {{
          const rendered = renderMarkdownDocument(mdText);
          modalBody.innerHTML = rendered;
          originalModalHtml = rendered;
        }})
        .catch(err => {{
          console.warn('Could not load markdown via fetch:', err);
          modalBody.innerHTML = `<div style="padding:30px; text-align:center;">
            <p style="color:#ef4444; margin-bottom:16px;">Direct browser fetch restricted in this environment.</p>
            <a href="${{fileUrl}}" target="_blank" class="btn btn-primary" style="display:inline-block;">Open ${{fileUrl}} directly ↗</a>
          </div>`;
        }});
    }}

    function closeMarkdownModal() {{
      const modal = document.getElementById('markdownModal');
      if (modal) modal.classList.remove('show');
      document.body.style.overflow = '';
    }}

    function handleModalBackdropClick(event) {{
      if (event.target === document.getElementById('markdownModal')) {{
        closeMarkdownModal();
      }}
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        closeMarkdownModal();
      }}
    }});

    function filterModalContent(query) {{
      const modalBody = document.getElementById('mdModalBody');
      if (!modalBody || !originalModalHtml) return;
      const q = (query || '').toLowerCase().trim();
      if (!q) {{
        modalBody.innerHTML = originalModalHtml;
        return;
      }}
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = originalModalHtml;
      const elements = tempDiv.querySelectorAll('h1, h2, h3, h4, p, li, .code-block-wrapper');
      elements.forEach(el => {{
        if (el.textContent.toLowerCase().includes(q)) {{
          el.style.display = '';
        }} else {{
          el.style.display = 'none';
        }}
      }});
      modalBody.innerHTML = tempDiv.innerHTML;
    }}

    function renderMarkdownDocument(md) {{
      if (!md) return '';
      const codeBlocks = [];
      let doc = md.replace(/```([a-zA-Z0-9_\\-]+)?[\\r\\n]([\\s\\S]*?)```/g, function(m, lang, code) {{
        let trimmed = code.trim();
        let displayLang = lang ? lang.toUpperCase() : "YAML / CONFIG";
        if (!lang) {{
          if (trimmed.includes("apiVersion:") || trimmed.includes("kind:")) displayLang = "YAML";
          else if (trimmed.includes("kubectl ") || trimmed.includes("curl ")) displayLang = "BASH";
        }}
        let filenameBadge = "";
        const lines = trimmed.split("\\n");
        if (lines[0] && lines[0].startsWith("# ") && lines[0].includes(".")) {{
          const fn = lines[0].replace(/^#\\s*/, "").trim();
          filenameBadge = `<span class="code-filename">${{escapeHtml(fn)}}</span>`;
        }}
        const idx = codeBlocks.length;
        codeBlocks.push(
          `<div class="code-block-wrapper">` +
            `<div class="code-block-header">` +
              `<div class="code-header-left">` +
                `<span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span>` +
                `<span class="code-lang">${{displayLang}}</span>` +
                filenameBadge +
              `</div>` +
              `<button class="code-copy-btn" onclick="copySnippet(this)" title="Copy code snippet">` +
                `<svg class="copy-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>` +
                `<span class="copy-text">Copy</span>` +
              `</button>` +
            `</div>` +
            `<pre class="code-box"><code>${{escapeHtml(trimmed)}}</code></pre>` +
          `</div>`
        );
        return `\\n\\n__MD_CODE_${{idx}}__\\n\\n`;
      }});

      let html = escapeHtml(doc);
      html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
      html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
      html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
      html = html.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
      html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
      html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
      html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1 ↗</a>');

      const lines = html.split(/[\\r\\n]+/);
      let inList = false;
      let out = [];

      for (let i = 0; i < lines.length; i++) {{
        let line = lines[i].trim();
        if (!line) continue;

        const blockMatch = line.match(/^__MD_CODE_(\\d+)__$/);
        if (blockMatch) {{
          if (inList) {{
            out.push("</ul>");
            inList = false;
          }}
          out.push(codeBlocks[parseInt(blockMatch[1], 10)]);
          continue;
        }}

        if (/^[-*][\\s]+(.*)$/.test(line)) {{
          let content = line.replace(/^[-*][\\s]+/, "");
          if (!inList) {{
            out.push('<ul class="content-list">');
            inList = true;
          }}
          out.push(`<li>${{content}}</li>`);
        }} else {{
          if (inList) {{
            out.push("</ul>");
            inList = false;
          }}
          if (line.startsWith("<h") || line.startsWith("<div") || line.startsWith("<pre")) {{
            out.push(line);
          }} else {{
            out.push(`<p>${{line}}</p>`);
          }}
        }}
      }}
      if (inList) {{
        out.push("</ul>");
      }}
      return out.join('\\n');
    }}

    // Markdown Dropdown Toggle
    function toggleMarkdownMenu(event) {{
      event.stopPropagation();
      const menu = document.getElementById('markdownDropdownMenu');
      if (menu) {{
        menu.classList.toggle('show');
      }}
    }}

    document.addEventListener('click', (e) => {{
      const menu = document.getElementById('markdownDropdownMenu');
      const btn = document.getElementById('markdownDropdownBtn');
      if (menu && menu.classList.contains('show') && !menu.contains(e.target) && e.target !== btn) {{
        menu.classList.remove('show');
      }}
    }});

    // Initial load
    window.addEventListener('DOMContentLoaded', () => {{
      renderTopicsGrid(TOPICS);
      const hash = window.location.hash;
      const match = hash.match(/^#\\/topic\\/(\\d+)$/);
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
    """Updates demos-complete.md by inserting the diagram iframe and quiz for all 41 topics."""
    with open("demos-complete.md", "r", encoding="utf-8") as f:
        content = f.read()

    header_and_topics = re.split(r"\n(?=## \d+\. )", content)
    header = header_and_topics[0]
    topics_raw = header_and_topics[1:]

    opt_letters = ['A', 'B', 'C', 'D']
    new_topics = []
    for idx, sec in enumerate(topics_raw, 1):
        m = re.match(r"## (\d+)\. (.+)", sec)
        if not m:
            new_topics.append(sec)
            continue
        num = int(m.group(1))

        # Ensure diagram iframe is present
        if f"diagrams/topic-{num:02d}.html" not in sec:
            diagram_block = f"""

### Component architecture flow

<iframe src="diagrams/topic-{num:02d}.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-{num:02d}.html](diagrams/topic-{num:02d}.html).
"""
            if "**Part 2 — Analogy / Zine:**" in sec:
                parts = sec.split("**Part 2 — Analogy / Zine:**", 1)
                sec = parts[0].rstrip() + "\n" + diagram_block + "\n**Part 2 — Analogy / Zine:**" + parts[1]
            else:
                parts = re.split(r"\n(?=\!\[.*?zine\.png\])", sec, 1)
                if len(parts) == 2:
                    sec = parts[0].rstrip() + "\n" + diagram_block + "\n" + parts[1]
                else:
                    sec = sec + "\n" + diagram_block

        # Check if quiz already present in section
        if "### Knowledge Check — Quiz" in sec:
            # Remove previous quiz to allow update
            sec = sec.split("### Knowledge Check — Quiz")[0].rstrip()

        # Build quiz markdown
        q_list = QUIZZES.get(num) or QUIZZES.get(str(num), [])
        if q_list:
            quiz_md_lines = ["\n\n### Knowledge Check — Quiz\n"]
            for q_idx, q in enumerate(q_list, 1):
                quiz_md_lines.append(f"**Q{q_idx}: {q['question']}**\n")
                for o_idx, opt in enumerate(q['options']):
                    quiz_md_lines.append(f"- [ ] {opt_letters[o_idx]}) {opt}")
                quiz_md_lines.append("\n<details>")
                quiz_md_lines.append("<summary>Reveal Answer &amp; Explanation</summary>\n")
                quiz_md_lines.append(f"**Correct Answer:** {opt_letters[q['answer']]}) {q['options'][q['answer']]}\n")
                quiz_md_lines.append(f"**Explanation:** {q['explanation']}\n")
                quiz_md_lines.append("</details>\n")
            quiz_block = "\n".join(quiz_md_lines)
            sec = sec.rstrip() + "\n" + quiz_block

        new_topics.append(sec)

    updated_content = header + "\n" + "\n".join(new_topics)

    with open("demos-complete.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Updated demos-complete.md with embedded diagrams and quizzes for all {len(new_topics)} topics.")


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
    print("Generated index.html with interactive quizzes successfully.")

    # Update demos-complete.md
    update_demos_complete_markdown(header, topics)

    # Create serve.py
    create_server_script()

    print("Complete build with quizzes finished successfully!")
