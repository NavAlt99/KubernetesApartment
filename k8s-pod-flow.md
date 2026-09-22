# Kubernetes Pod Creation — Animated Flow

An animated, dark-themed (ByteMonk/system-design-video style) diagram tracing a pod creation request from `kubectl` to a running container. Dependency-free HTML/CSS/JS — no external libraries.

## Files
- `k8s-pod-flow-bytemonk.html` — the standalone animated diagram. Open it directly in any browser.

## Option A — Open directly in a browser
Just double-click `k8s-pod-flow-bytemonk.html`, or run:
```bash
open k8s-pod-flow-bytemonk.html   # macOS
xdg-open k8s-pod-flow-bytemonk.html   # Linux
start k8s-pod-flow-bytemonk.html   # Windows
```

## Option B — Embed in this Markdown, rendered in a browser (works in VS Code preview, Obsidian, browser-based Markdown viewers)

Most Markdown renderers (VS Code preview, Obsidian, Typora, browser Markdown extensions) allow raw HTML passthrough, including `<iframe>`. **GitHub's own web renderer strips `<script>` and sanitizes `<iframe>`/inline JS for security**, so the animation will not run natively on github.com — the file will still be there and downloadable/openable, just not animated on the page itself. Everywhere else that renders raw HTML in Markdown, this works:

```html
<iframe src="k8s-pod-flow-bytemonk.html" width="100%" height="760" style="border:none;"></iframe>
```

## Option C — GitHub Pages / any static host
Since GitHub itself won't execute the JS inline, if you want it live *on GitHub* specifically:
1. Push `k8s-pod-flow-bytemonk.html` to your repo.
2. Enable GitHub Pages (Settings → Pages → deploy from branch).
3. Link to it from your README: `[▶ View animated diagram](https://<username>.github.io/<repo>/k8s-pod-flow-bytemonk.html)`

This gives you a live, animated, fully working page — GitHub Pages serves the raw HTML/JS with no sanitization, unlike the repo file viewer.

## Option D — Static fallback for the GitHub README itself
If you want *something* visible directly on the GitHub-rendered README (not just a link), pair this animated version with the static Mermaid sequence diagram from `k8s-pod-creation-flow.md` — Mermaid renders natively on GitHub without needing JS. Use the animated HTML as the "click to see it live" companion.
