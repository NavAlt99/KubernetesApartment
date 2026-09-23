#!/usr/bin/env python3
"""Build browsable GitHub Pages HTML pages from the repository Markdown."""

from pathlib import Path
import html
import re
import markdown

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    ROOT / "README.md",
    ROOT / "demos-complete.md",
    ROOT / "k8s-pod-flow.md",
    ROOT / "k8s-pod-creation-flow.md",
    ROOT / "kubernetes-full-controllers-zine-prompts.fixed.md",
    ROOT / "CKA_Study_Notes" / "README.md",
    *sorted((ROOT / "CKA_Study_Notes").glob("*.md")),
]


def output_path(source: Path) -> Path:
    return source.with_suffix(".html")


def rewrite_links(fragment: str) -> str:
    # The generated pages are the public Pages routes.  Keep external URLs,
    # anchors, images, and already-rendered HTML untouched.
    def replace(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()
        if url.startswith(("http://", "https://", "mailto:", "#", "/")):
            return match.group(0)
        # demos-complete.md lives at the repository root.  Its historical
        # ../CKA_Study_Notes links escaped the published site and became 404s.
        if url.startswith("../CKA_Study_Notes/"):
            url = url[3:]
        if url.lower().endswith(".md"):
            url = url[:-3] + ".html"
        return prefix + url + suffix

    return re.sub(r'([("\'])([^)"\']+)([)"\'])', replace, fragment)


def title_for(source: Path, text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else source.stem.replace("-", " ").title()


def build(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    body = markdown.markdown(
        text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "toc"],
    )
    body = rewrite_links(body)
    title = html.escape(title_for(source, text))
    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ max-width: 980px; margin: 0 auto; padding: 2rem 1.25rem 4rem; background: #090d16; color: #e2e8f0; font: 16px/1.65 system-ui, sans-serif; }}
    a {{ color: #fb7185; }}
    img {{ max-width: 100%; height: auto; }}
    pre {{ overflow-x: auto; padding: 1rem; background: #111827; border-radius: .5rem; }}
    code {{ background: #1e293b; padding: .1em .3em; border-radius: .25rem; }}
    pre code {{ background: transparent; padding: 0; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #334155; padding: .5rem; text-align: left; }}
    blockquote {{ border-left: 3px solid #fb7185; margin-left: 0; padding-left: 1rem; }}
  </style>
</head>
<body><main class="markdown-page">{body}</main></body>
</html>
'''
    output_path(source).write_text(page, encoding="utf-8")


if __name__ == "__main__":
    for source in PAGES:
        build(source)
    print(f"Built {len(PAGES)} Markdown pages.")
