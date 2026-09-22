#!/usr/bin/env python3
"""
scripts/rebuild_all_content.py
Combines enriched technical discussions (CKA notes, Linux concepts, subtopics, YAML manifests)
with original zine analogies, builds demos-complete.md, and updates build_website.py.
"""

import os
import json
import re
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enriched_topics_1_10 import ENRICHED_1_10
from enriched_topics_11_20 import ENRICHED_11_20
from enriched_topics_21_30 import ENRICHED_21_30
from enriched_topics_31_41 import ENRICHED_31_41

ALL_ENRICHED = {}
ALL_ENRICHED.update(ENRICHED_1_10)
ALL_ENRICHED.update(ENRICHED_11_20)
ALL_ENRICHED.update(ENRICHED_21_30)
ALL_ENRICHED.update(ENRICHED_31_41)

with open("scripts/original_zine_data.json", "r", encoding="utf-8") as f:
    ORIGINAL_DATA = json.load(f)

# Extract existing header from demos-complete.md
with open("demos-complete.md", "r", encoding="utf-8") as f:
    content = f.read()

header = re.split(r"\n(?=## 1\. )", content)[0].strip()

opt_letters = ['A', 'B', 'C', 'D']

new_sections = []
for item in ORIGINAL_DATA:
    num = item["num"]
    title = item["title"]
    enriched = ALL_ENRICHED.get(num, {})
    
    tech_disc = enriched.get("tech_disc", item.get("tech_disc", "")).strip()
    tech_persp = enriched.get("tech_persp", item.get("tech_persp", "")).strip()
    zine_analogy = item["zine_analogy"].strip()
    zine_exp = item["zine_exp"].strip()
    reading = item["reading"].strip()
    demo = item["demo"].strip()
    quizzes = item.get("quiz", [])
    
    sec_md = f"""## {num}. {title}

**Part 1 — Technical Discussion:** {tech_disc}

![{title} technical illustration](generated/kubernetes-apartment-complex/{num:02d}-technical.png)

**Technical perspective:** {tech_persp}

### Component architecture flow

<iframe src="diagrams/topic-{num:02d}.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-{num:02d}.html](diagrams/topic-{num:02d}.html).

**Part 2 — Analogy / Zine:** {zine_analogy}

![{title} zine illustration](generated/kubernetes-apartment-complex/{num:02d}-zine.png)

**Zine explanation:** {zine_exp}

**Further reading**

{reading}

### Demo — {title}

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
{demo}
</pre></div>

### Knowledge Check — Quiz"""

    for q_idx, q in enumerate(quizzes):
        ans_idx = q["answer"]
        ans_text = q["options"][ans_idx]
        sec_md += f"""

**Q{q_idx + 1}: {q['question']}**

- [ ] A) {q['options'][0]}
- [ ] B) {q['options'][1]}
- [ ] C) {q['options'][2]}
- [ ] D) {q['options'][3]}

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** {opt_letters[ans_idx]}) {ans_text}

**Explanation:** {q['explanation']}

</details>"""

    new_sections.append(sec_md)

final_markdown = header + "\n\n" + "\n\n".join(new_sections) + "\n"

with open("demos-complete.md", "w", encoding="utf-8") as f:
    f.write(final_markdown)

print(f"Updated demos-complete.md with all {len(new_sections)} enriched topics!")
