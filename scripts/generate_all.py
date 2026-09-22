#!/usr/bin/env python3
"""
scripts/generate_all.py
Compiles all 41 topics and generates diagrams/topic-01.html through topic-41.html
"""

import os
from build_all_diagrams import render_diagram
from topics_data import TOPICS as T1_5
from topics_data_2 import ADDITIONAL_TOPICS as T6_10
from topics_data_3 import REMAINING_TOPICS as T11_20
from topics_data_4 import FINAL_TOPICS as T21_41

ALL_TOPICS = T1_5 + T6_10 + T11_20 + T21_41

print(f"Total topics defined: {len(ALL_TOPICS)}")
assert len(ALL_TOPICS) == 41, f"Expected 41 topics, got {len(ALL_TOPICS)}"

os.makedirs("diagrams", exist_ok=True)

for topic in ALL_TOPICS:
    num = topic["num"]
    filename = f"diagrams/topic-{num:02d}.html"
    html_content = render_diagram(topic)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated {filename}: {topic['title']}")

print("All 41 diagrams generated successfully in diagrams/!")
