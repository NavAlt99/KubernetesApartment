# Prompt: Generate animated architecture diagrams for the Kubernetes Apartment Complex site

Use this prompt (as-is, or per-topic with the `{{TOPIC}}` block filled in) to generate every diagram for the site so all 41 come out visually identical in style. Paste the **Style Lock** section into every generation request unmodified — it is the part that must never drift.

---

## Style Lock — do not deviate, do not restyle, do not "improve"

This is a fixed visual system, not a starting point. Every diagram generated under this prompt must satisfy every rule below exactly. If a rule and a topic's content conflict, adjust the content layout — never the rule.

**Aesthetic identity:** Minimalist tech / system-design-explainer style (the look used in system-design YouTube channels and "Dan Koe"-style minimal dark tech aesthetics) — not a cartoon, not the apartment-complex zine illustration style, not a hand-drawn or sketch style. This is the *technical* companion diagram, separate from the zine artwork.

**Canvas & background**
- Background color: `#0b1120` (near-black navy). Flat fill. No gradients on the background, no texture, no noise.
- Content max-width: 900–1000px, centered.
- Padding: minimum 24px on all sides on desktop; content must reflow on narrow viewports without breaking layout.

**Color palette — exact hex values, do not substitute**
- Background: `#0b1120`
- Panel / node fill (neutral): `#111a2e`
- Panel border (resting): `#1e2b47`
- Control-plane region tint: `#0f1f38`
- Worker-node region tint: `#14231c`
- Connector line (resting): `#24324f`
- Primary accent (active node / active connector / glow): `#38bdf8` (cyan-blue)
- Secondary accent (moving packet / request marker): `#f59e0b` (amber)
- Primary text: `#e5edf7`
- Secondary / dim text: `#7f93b3`
- No other colors permitted anywhere in a diagram. No red/green/purple unless a future topic explicitly requires a semantic status color (e.g. a failure state) — if so, ask before introducing a new hex value rather than picking one ad hoc.

**Typography**
- Font stack: `'JetBrains Mono', 'Fira Code', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace` — monospace only, everywhere, no exceptions.
- Node title: 12–13px, weight 600.
- Node subtitle/description: 9.5–10.5px, dim text color.
- Page heading: 15px, weight 600, uppercase, letter-spacing 0.08em, primary accent color.
- Subtitle under heading: 12px, dim text color.
- Sentence case for all node subtitles and body copy. Uppercase only for the page heading and region labels (region labels also get letter-spacing 0.06em).
- No emoji anywhere.

**Shapes & structure**
- Nodes are rounded rectangles, `rx="10"`, 1.2px stroke.
- Grouping regions (e.g. "Control plane", "Worker node") are dashed-border rounded containers (`stroke-dasharray: 3 4`, `rx="14"`), not solid boxes — a region is a boundary, not a node.
- Connectors are thin lines/paths, 1.4–1.5px stroke, `fill="none"`. Right-angle (L-shaped) routing between regions; straight lines within a tight vertical stack are acceptable only when nothing else could cross them.
- No drop shadows except the glow effect defined below. No skeuomorphism, no 3D, no bevels.

**Animation behavior — this is an architecture diagram with a traveling request marker, not a generic flowchart**
- Layout must reflect **actual component topology** (who talks to whom), never a simple top-to-bottom numbered list. If the real system has parallel branches (e.g. kubelet fans out to both the container runtime and the CNI plugin), draw them as parallel branches, not sequential steps.
- A single amber circular "packet" (`fill: #f59e0b`, soft glow via `drop-shadow`) travels along the connector paths between nodes in the order the real request/data actually flows.
- When the packet arrives at a node: that node's border switches to the cyan accent color and gets a soft cyan glow (`drop-shadow(0 0 8px rgba(56,189,248,0.55))`); the node title text also switches to accent color. Previous node returns to resting style.
- The connector the packet just traveled along lights up (accent-colored, animated dashed "flow" overlay, `stroke-dasharray: 4 5`, animating `stroke-dashoffset` continuously while active) for that step, then fades back to resting `#24324f` once the packet moves on — unless the diagram intentionally shows a persistent/idle relationship (call this out explicitly per-topic if so).
- A text caption above or below the diagram updates per step in plain English, one sentence, sentence case, no jargon-only phrasing without a plain-English clause attached.
- Provide **Play** and **Reset** buttons, monospace, same visual button style as the reference build (dark panel bg, accent-colored text, border brightens and glows on hover).
- Respect `prefers-reduced-motion: reduce` — disable the continuous dash animation under that media query; keep discrete state changes (they're not continuous motion) but drop the perpetual `@keyframes` loop.
- Step duration: 1.3–1.4s per node before advancing. This pacing must stay consistent across every topic's diagram — do not speed up "simpler" topics or slow down "complex" ones; consistency across the full set matters more than per-topic optimization.

**What this diagram is not**
- Not a sequence diagram with swimlanes and lifelines.
- Not a generic linear flowchart (box → arrow → box → arrow) unless the real topic has no meaningful parallel structure or containment (rare — most Kubernetes topics involve at least one region boundary or parallel branch).
- Not decorative — no icons, no illustrations, no clip-art, no isometric art. Text-in-boxes only, exactly like a real systems-design reference diagram.

**Technical implementation constraints**
- Output as a single self-contained `.html` file: inline `<style>`, inline `<svg>`, inline `<script>`. Zero external dependencies, zero network calls, zero build step.
- SVG viewBox sized to content with no wasted whitespace; recompute per topic (region box sizes, node counts, and connector paths differ per topic — do not force every topic into the exact same coordinate layout used for the Pod Creation reference build; reuse its *style*, not its literal pixel coordinates, unless the topology is identical).
- Must render and animate correctly in Safari and Chrome on macOS with no browser plugin, no server, opened via `file://`.
- Must NOT rely on GitHub's Markdown renderer executing the script — assume it will be opened as a standalone `.html` file or embedded via `<iframe>` in a renderer that permits raw HTML (VS Code preview, Obsidian, a static site build). Never promise it will animate on github.com's own file viewer.

---

## Per-topic block — fill this in for each of the 41 topics

```
{{TOPIC}}
Topic number: <n>
Topic name: <exact heading text from the source doc, e.g. "kube-scheduler">
Plain-English one-liner: <what this component/object does, in one sentence>

Real components/actors involved (list every box that must appear as a node):
- <actor 1>
- <actor 2>
- ...

Grouping regions needed (if any): <e.g. "Control plane" region containing X, Y, Z; "Worker node" region containing A, B>
  — omit this field entirely if the topic has no meaningful containment (e.g. RBAC objects like Role/RoleBinding may not need a control-plane/worker-node split)

Real request/data flow order (this drives the packet's path — list as an ordered sequence of node-to-node hops, including any parallel branches):
1. <node> -> <node>: <one-sentence plain-English caption for this hop>
2. <node> -> <node> (parallel with step 3): <caption>
3. <node> -> <node> (parallel with step 2): <caption>
...

Persistent/idle relationships to show without packet travel (if any): <e.g. "kubelet continuously watches API server" — shown as a static dim connector, not part of the packet's animated path>

Special notes / constraints specific to this topic: <anything the Style Lock doesn't already cover — e.g. this topic has no "request flow" at all and is better shown as a static structural diagram with no packet animation; call this out explicitly rather than forcing an animation where none makes sense>
```

---

## Full topic list from the source document (41 entries — fill in a `{{TOPIC}}` block for each)

1. The Cluster (Why Kubernetes?)
2. Control Plane vs. Worker Nodes
3. kube-apiserver
4. etcd
5. kube-scheduler
6. kube-controller-manager
7. cloud-controller-manager
8. Static Pods
9. kubelet
10. kube-proxy
11. Container Runtime & CRI
12. Sidecar Containers
13. Init Containers
14. CNI (Container Network Interface)
15. CoreDNS
16. Services
17. Endpoints
18. Ingress
19. NetworkPolicy
20. PersistentVolume (PV)
21. PersistentVolumeClaim (PVC)
22. StorageClass
23. Role
24. RoleBinding
25. ClusterRole
26. ClusterRoleBinding
27. ServiceAccount
28. Node (controller)
29. Namespace (controller)
30. ResourceQuota
31. Garbage Collector
32. ReplicaSet
33. Deployment
34. StatefulSet
35. DaemonSet
36. Job
37. CronJob
38. ReplicationController (legacy)
39. HorizontalPodAutoscaler (HPA)
40. VerticalPodAutoscaler (VPA)
41. Pod Disruption Budget (PDB)

---

## Reference implementation

Topic 1's worked example (Pod creation request flow, spanning Control Plane and Worker Node regions) is the canonical reference build — its file is `k8s-architecture-flow.html` from this same project. Every other topic's diagram should look like a sibling of that file: same palette, same fonts, same button style, same packet/glow mechanic, same caption behavior — only the topology, node count, region boundaries, and captions change per topic.

## Known gap to flag before generating art for all 41 topics

The source document (`demos-complete.md`) references existing illustration assets at paths like `generated/kubernetes-apartment-complex/01-zine.png` and `01-technical.png` for every topic. Those image files were **not** included in the upload — only the Markdown file referencing them was provided. Before treating this prompt as ready to batch-run:
- Confirm whether the intent is to *replace* those PNG references with the new animated `.html` diagrams entirely, or to *keep* the existing zine/technical PNGs alongside the new animated ones once that folder is supplied.
- If the PNGs are meant to stay, this Style Lock applies only to the new animated technical diagrams — it must not be used to regenerate or restyle the existing zine illustrations, which intentionally follow a different (apartment-complex metaphor) visual language.
