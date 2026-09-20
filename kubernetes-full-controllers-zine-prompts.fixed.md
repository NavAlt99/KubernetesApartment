# Zine prompt pack: "Kubernetes Apartment Complex"
### Technical Discussion + Illustration → Analogy + Zine → Demo (with commands)

41 components across the full Kubernetes object model, each producing **three
parts**: a technical explanation + diagram prompt, an apartment-complex
analogy + zine illustration prompt, and a hands-on demo with real `kubectl`
commands the audience can run live.

## NON-NEGOTIABLE DELIVERY CONTRACT

This is an **image-production brief**. Every numbered entry needs real raster
artwork, not text-only output.

Each numbered entry produces **exactly two images**, both 16:9:

1. **Technical illustration**: generated from the entry's Part 1 image prompt
   with the Technical style block. A diagram only, no apartment imagery.
2. **Zine image**: ONE finished image generated from the entry's Part 2 image
   prompt with the Zine style block. It contains the apartment-complex
   analogy illustration AND the explanation text together, in a single
   image. It is not a separate illustration plus a separate page.

**Text inside the zine image.** Generate the zine image with the entry's
**Zine Text & Layout** copy written into it: the (Top) line as the title, and
the (Caption) / (Under Left) / (Under Right) lines as the explanation,
placed as written. An illustration with no explanation text is a FAILED
zine image and must be regenerated.

Other deliverables:

3. **Demos**: all Part 3 demos are text only, delivered in `demos-complete.txt`.
   Part 3 has no image-generation step.
4. **Manifest**: one row per entry mapping entry number to its technical
   illustration file, its zine image file, and its `demos-complete.txt` section.

Totals: 41 technical illustrations + 41 zine images (82 images) +
`demos-complete.txt` + manifest. There are no separately built pages.

**QA:** open representative images and verify the artwork is present and
legible. Fail a technical illustration if it is blank, has a checkerboard or
transparent background, or is missing its main subject. Fail a zine image if
it has no readable explanation text, or if the text is garbled or cut off.
Regenerate failed images. The final folder must make it possible to count
the numbered entries and confirm that every one has both an image file for
its technical illustration and one for its zine.

---

## Style blocks

**Technical Illustration style (Part 1 of every entry):**
```
Graphic design composition in an editorial layout / magazine spread style,
clean systems-diagram aesthetic, labeled boxes and directional arrows,
limited color palette (navy, white, mustard yellow, rust orange), no
gradients, no analogy imagery — purely technical, landscape orientation,
16:9 aspect ratio, solid flat off-white (#F5F1E8) full-bleed opaque
background, no transparency, no checkerboard pattern.
```

**Analogy / Zine style (Part 2 of every entry):**
```
Graphic design composition in a Risograph print / collage art / mixed
media zine aesthetic, clean bold outlines, limited color palette (navy,
white, mustard yellow, rust orange), no gradients, editorial illustration
feel, landscape orientation, 16:9 aspect ratio.
```

**Demo format (Part 3 of every entry):** a short narrated command sequence
— what to type, what it proves, and what to point out on screen. Assumes a
local cluster (minikube, kind, or similar) is already running. Part 3 is
**text only**: it is delivered in `demos-complete.txt`, not as an image and not on the
zine images.

---

# GROUP 1 — THE BIG PICTURE

## 1. The Cluster (Why Kubernetes?)

**Part 1 — Technical Discussion:** Kubernetes lets you manage many machines as one cluster. You describe the application you want to run, and Kubernetes chooses a suitable machine and keeps the application running there. You do not have to log in to each server and place every workload yourself.

**Image generation prompt:** [Technical style block] + "A systems diagram showing several isolated server icons scattered with no connections between them on the left, labeled 'STANDALONE VMs,' transitioning via an arrow into a single unified node graph on the right — one central control node connected to several worker nodes in a clean cluster topology, labeled 'KUBERNETES CLUSTER.'"

**Part 2 — Analogy / Zine:** Managing standalone buildings is exhausting; tying them into one complex lets you manage them as a single entity.

**Image generation prompt:** [Zine style block] + "Split composition. Left side: a chaotic scattered map of isolated standalone buildings, each with its own confused-looking manager running around holding separate clipboards, tangled roads leading nowhere, labeled 'MANAGING VMs ONE BY ONE.' Right side: the same buildings now enclosed by a single gate and fence into one organized complex, one calm manager sitting at a central office desk with a single unified dashboard, labeled 'THE CLUSTER.'"

* **Zine Text & Layout:**
* (Top): "Why Kubernetes? Because managing buildings one at a time is exhausting."
* (Under Left): "Standalone buildings, standalone managers, standalone problems."
* (Under Right): "Tie them into one complex and manage it as a single entity. Stop SSHing into individual machines — talk to the cluster, and it decides where your workload goes."

**Part 3 — Demo:**
```bash
kubectl cluster-info
kubectl get nodes -o wide
```
Point out: one command shows the whole "complex" — every node in the cluster, its role, and its status — instead of logging into each machine separately.

---

## 2. Control Plane vs. Worker Nodes

**Part 1 — Technical Discussion:** The Control Plane is the cluster's decision-maker. Worker Nodes are the machines that run your applications. If a Worker Node fails, Kubernetes can move or replace workloads on healthy nodes. If the Control Plane fails, running workloads may continue, but Kubernetes cannot make new scheduling or change decisions until it recovers.

**Image generation prompt:** [Technical style block] + "A systems diagram with two labeled zones connected by a directional arrow: left zone labeled 'CONTROL PLANE' containing small icons for decision-making/planning (a brain icon, a checklist icon); right zone labeled 'WORKER NODES' containing icons for compute/execution (a gear icon, a container stack icon). A caption box below reads 'Control Plane down = no changes possible. Worker Node down = workload reschedules.'"

**Part 2 — Analogy / Zine:** The office thinks (Leasing Office); the buildings do the actual physical work (Worker Nodes).

**Image generation prompt:** [Zine style block] + "Split composition. Left side: a clean, quiet leasing office interior, staff sitting calmly at desks thinking and reviewing plans on paper, labeled 'CONTROL PLANE — the office that thinks.' Right side: tall apartment buildings with maintenance crews actively carrying tools, climbing ladders, doing visible physical labor, labeled 'WORKER NODES — the buildings that work.'"

* **Zine Text & Layout:**
* (Top): "Two halves of the complex: the office that thinks, and the buildings that work."
* (Under Left): "The Leasing Office thinks — planning, deciding, recording. This is the Control Plane."
* (Under Right): "If a building crashes, workloads shift elsewhere. If the office crashes, buildings keep running — but nothing can be changed until the office is back."

**Part 3 — Demo:**
```bash
kubectl get nodes --selector='node-role.kubernetes.io/control-plane'
kubectl get pods -n kube-system -o wide
```
Point out: the control-plane node hosts the "office" components (api-server, scheduler, etc.) as Pods in `kube-system`, physically separate from the worker nodes running actual application workloads.

---

# GROUP 2 — CONTROL PLANE (THE LEASING OFFICE)

## 3. kube-apiserver

**Part 1 — Technical Discussion:** kube-apiserver is the front door of Kubernetes. kubectl, the scheduler, controllers, and other clients send requests to it. It checks and processes those requests, and it is the only Control Plane component that talks directly to etcd.

**Image generation prompt:** [Technical style block] + "A systems diagram with a central hub box labeled 'kube-apiserver,' multiple directional arrows pointing INTO it from labeled sources (kubectl, scheduler, controller-manager, kubelet), and a single arrow OUT to a box labeled 'etcd.' Caption: 'Single entry point. Only path to etcd.'"

**Part 2 — Analogy / Zine:** Every request must go through this one desk; nobody bypasses it.

**Image generation prompt:** [Zine style block] + "One front desk with a sign reading 'ALL REQUESTS HERE,' a single orderly queue of visitors of different types (a resident, a delivery person, a maintenance worker) all funneling into the same desk, a locked door labeled 'RECORDS ROOM' visible only behind the front desk clerk."

* **Zine Text & Layout:**
* (Top): "kube-apiserver — The Front Desk"
* (Caption): "Every request must go through this one desk; nobody bypasses it. It's the only component that talks to the records room, and it's what your kubectl commands hit."

**Part 3 — Demo:**
```bash
kubectl get --raw /api/v1 | head -c 300
kubectl proxy --port=8080 &
curl -s http://localhost:8080/api/v1/namespaces | head -c 300
```
Point out: every `kubectl` command is really just an HTTP request to this one server — you can bypass kubectl entirely and hit the same "front desk" directly with `curl`.

---

## 4. etcd

**Part 1 — Technical Discussion:** etcd is Kubernetes' database. It stores the important facts about the cluster, such as which Pods, Services, and Nodes should exist. Kubernetes uses it as the source of truth, so losing access to etcd means the Control Plane loses its reliable memory of the cluster.

**Image generation prompt:** [Technical style block] + "A systems diagram of a database cylinder icon labeled 'etcd (key-value store)' with a small replication icon showing 3 synced copies for high availability, one arrow labeled 'reads/writes' connecting to a 'kube-apiserver' box, caption reading 'Single source of truth. Corruption = cluster loses its state.'"

**Part 2 — Analogy / Zine:** Wall-to-wall filing cabinets holding the only copy of the complex's rules and state that actually counts.

**Image generation prompt:** [Zine style block] + "A locked records room behind reinforced glass, wall-to-wall labeled filing cabinets, a single staff member with a key, a small warning sign reading 'ONLY COPY — HANDLE WITH CARE.'"

* **Zine Text & Layout:**
* (Top): "etcd — The Locked Records Room"
* (Caption): "A highly available key-value store; if it corrupts, your cluster loses its memory."

**Part 3 — Demo:**
```bash
kubectl -n kube-system exec -it etcd-<node-name> -- etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/pods --prefix --keys-only | head -20
```
Point out: this is the raw storage every `kubectl get` command is actually querying indirectly through the API server — the "filing cabinets" behind the front desk.

---

## 5. kube-scheduler

**Part 1 — Technical Discussion:** kube-scheduler chooses a machine for a new Pod. It looks for a Node with enough CPU and memory and checks rules such as where the Pod is allowed or preferred to run. After it makes the choice, the kubelet on that Node can start the Pod.

**Image generation prompt:** [Technical style block] + "A systems diagram showing an unassigned Pod icon floating above a row of Node icons with different resource-capacity bars, a 'kube-scheduler' box evaluating the Nodes with a checklist icon, then a dotted arrow assigning the Pod to the best-fitting Node."

**Part 2 — Analogy / Zine:** Checks building capacity and rules, then pins new tenants to the best-fitting building.

**Image generation prompt:** [Zine style block] + "A staff member holding a building capacity chart, standing at a wall map of the complex, placing a new tenant pin onto the building with the most open space and matching amenities, other buildings shown at full or partial capacity."

* **Zine Text & Layout:**
* (Top): "kube-scheduler — The Unit Assigner"
* (Caption): "Assigns new Pods to Nodes based on CPU/RAM requirements and affinity rules."

**Part 3 — Demo:**
```bash
kubectl run demo-pod --image=nginx --dry-run=client -o yaml > demo-pod.yaml
kubectl apply -f demo-pod.yaml
kubectl get pod demo-pod -o wide
kubectl describe pod demo-pod | grep -A3 Events
```
Point out: the `describe` output's Events section shows the exact moment the scheduler assigned this Pod to a specific node — "Successfully assigned ... to <node>".

---

## 6. kube-controller-manager

**Part 1 — Technical Discussion:** kube-controller-manager runs several watchers called control loops. Each loop compares what you asked for with what is actually running. When something is missing or wrong, a controller takes action, such as creating a replacement when a Pod crashes.

**Image generation prompt:** [Technical style block] + "A systems diagram of a circular/looping arrow icon labeled 'control loop,' comparing two side-by-side panels: 'DESIRED STATE' (3 Pod icons) vs. 'ACTUAL STATE' (2 Pod icons, one greyed out/crashed), with an arrow from the loop icon spinning up a replacement Pod to match."

**Part 2 — Analogy / Zine:** Clipboard inspectors walking endless loops to ensure reality matches the promised plan, fixing discrepancies automatically.

**Image generation prompt:** [Zine style block] + "Inspectors walking a continuous looping hallway path throughout the complex, clipboards in hand, checking boxes at each unit door, one inspector noticing a vacant unit and immediately radioing for a replacement tenant to be moved in."

* **Zine Text & Layout:**
* (Top): "kube-controller-manager — The Looping Inspectors"
* (Caption): "Background control loops that detect crashed Pods and spin up replacements to match your deployment YAML."

**Part 3 — Demo:**
```bash
kubectl create deployment demo --image=nginx --replicas=3
kubectl get pods -l app=demo
kubectl delete pod $(kubectl get pods -l app=demo -o name | head -1)
kubectl get pods -l app=demo -w
```
Point out: kill one Pod and watch a replacement appear within seconds, unprompted — that's the control loop noticing the gap and closing it automatically.

---

## 7. cloud-controller-manager

**Part 1 — Technical Discussion:** cloud-controller-manager connects Kubernetes to a cloud provider. When you ask for something such as a LoadBalancer or cloud disk, it translates that Kubernetes request into the provider's API call and reports the result back to the cluster.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a 'cloud-controller-manager' box positioned between the Kubernetes cluster boundary and an external cloud provider icon (labeled generically 'AWS / GCP / Azure'), with an arrow labeled 'translates API calls' crossing the boundary."

**Part 2 — Analogy / Zine:** Signs paperwork to connect external utilities like rented parking gates.

**Image generation prompt:** [Zine style block] + "A staff member at a desk signing paperwork on the phone, an outside utility van visible through the office window with a logo representing an external vendor, a rented parking gate being installed outside the complex fence."

* **Zine Text & Layout:**
* (Top): "cloud-controller-manager — Outside Vendor Liaison"
* (Caption): "Translates Kubernetes requests into AWS/GCP/Azure API calls for things like cloud LoadBalancers."

**Part 3 — Demo:**
```bash
kubectl expose deployment demo --type=LoadBalancer --port=80 --target-port=80
kubectl get svc demo -w
```
Point out: on a real cloud cluster, `EXTERNAL-IP` moves from `<pending>` to a real IP as cloud-controller-manager calls out to the provider's API behind the scenes. (On local clusters like minikube, note it stays pending and mention `minikube tunnel` as the local workaround.)

---
## 8. Static Pods

**Part 1 — Technical Discussion:** A Static Pod is started from a manifest file on a Node's local disk. The kubelet watches that file and runs the Pod directly, without asking the API server. This lets a machine start important Control Plane Pods while the API server is still coming up.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a single Node with a 'kubelet' icon directly managing a Pod icon with a dotted boundary line drawn around it labeled 'no API server dependency,' separate from the normal API-server-managed Pods shown faded in the background."

**Part 2 — Analogy / Zine:** A local blueprint used to build the front desk before a front desk even exists.

**Image generation prompt:** [Zine style block] + "A temporary construction tent with a blueprint table set up on-site, a small crew independently assembling the very first front desk of the leasing office from a local blueprint, no office staff present yet to direct them."

* **Zine Text & Layout:**
* (Top): "Static Pods — The Bootstrapping Crew"
* (Caption): "Pods managed directly by a local kubelet to run control plane components without relying on the API server."

**Part 3 — Demo:**
```bash
ls /etc/kubernetes/manifests/
kubectl get pods -n kube-system -o wide | grep -E "apiserver|etcd|scheduler"
```
Point out: those YAML files on disk are what the kubelet reads directly, with no API server round-trip — proof that these Pods exist even before the "front desk" is up.

---

# GROUP 3 — WORKER NODES (THE BUILDINGS)

## 9. kubelet

**Part 1 — Technical Discussion:** kubelet is the agent on each Node. It reads the Pod instructions assigned to that Node, asks the container runtime to run the containers, and reports whether they are healthy. It is the local worker that turns Kubernetes instructions into running processes.

**Image generation prompt:** [Technical style block] + "A systems diagram of a single Node box containing a 'kubelet' icon with a checklist, monitoring several Container icons inside, arrows showing kubelet reporting status back up to the Control Plane."

**Part 2 — Analogy / Zine:** Receives the work order from the office and does headcounts to ensure assigned tenants are present and healthy.

**Image generation prompt:** [Zine style block] + "A superintendent kid holding a work order clipboard, walking down a hallway doing a headcount checklist at each unit door, checking off tenants as present and healthy, one door flagged with a concerned expression."

* **Zine Text & Layout:**
* (Top): "kubelet — The Superintendent"
* (Caption): "The primary node agent that ensures containers are actually running on that specific server."

**Part 3 — Demo:**
```bash
kubectl get pod demo-pod -o jsonpath='{.status.conditions}'
systemctl status kubelet   # run on the node itself
```
Point out: the Pod's status conditions (Ready, ContainersReady, etc.) are reported by the kubelet on that exact node — it's the local "superintendent" doing the headcount and phoning it in.

---

## 10. kube-proxy

**Part 1 — Technical Discussion:** kube-proxy helps traffic reach a Service's Pods. It installs network rules on each Node so a request sent to the Service can be forwarded to a healthy Pod. When Pods are replaced, kube-proxy updates those rules to use the current Pod addresses.

**Image generation prompt:** [Technical style block] + "A systems diagram of a routing table icon labeled 'kube-proxy' dynamically updating entries as Pod IP icons appear and disappear beneath a stable Service IP box, arrows showing incoming traffic being redirected to whichever Pod IPs are currently listed."

**Part 2 — Analogy / Zine:** Updates a directory on the fly so visitors find the right unit, even as tenants swap out.

**Image generation prompt:** [Zine style block] + "A lobby directory board being actively updated by a staff member's hand, small nameplate tags sliding in and out as tenants move, a visitor consulting the board and being pointed toward whichever unit currently matches."

* **Zine Text & Layout:**
* (Top): "kube-proxy — The Lobby Directory"
* (Caption): "Maintains network routing rules (iptables/IPVS) on the host to route traffic to active Pod IPs."

**Part 3 — Demo:**
```bash
kubectl get endpoints demo
sudo iptables -t nat -L | grep demo   # run on a worker node
```
Point out: the Endpoints list and the actual iptables rules line up — this is kube-proxy translating the Service's "permanent mailbox" into real routing rules on the host.

---

## 11. Container Runtime & CRI

**Part 1 — Technical Discussion:** The container runtime is the software that downloads images and starts containers. Kubernetes does not need to know every runtime's private details because it uses the Container Runtime Interface, or CRI, as a common set of instructions. This lets a cluster use runtimes such as containerd or CRI-O.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a 'kubelet' box connected via a labeled 'CRI (standard interface)' arrow to interchangeable runtime boxes below it — 'containerd' and 'CRI-O' shown as swappable modules plugging into the same socket shape."

**Part 2 — Analogy / Zine:** The physical crew carrying boxes, operating under a standard universal contract.

**Image generation prompt:** [Zine style block] + "A moving crew carrying labeled boxes into an apartment unit, a printed 'UNIVERSAL MOVING CONTRACT' document taped prominently to the wall that any moving company could sign and follow, two different crew uniforms shown as interchangeable."

* **Zine Text & Layout:**
* (Top): "Container Runtime & CRI — The Moving Crew & Contract"
* (Caption): "containerd or CRI-O pulls the image and runs the process; CRI ensures Kubernetes can swap runtimes seamlessly."

**Part 3 — Demo:**
```bash
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.containerRuntimeVersion}'
sudo crictl ps   # run on a worker node, talks to the runtime directly via CRI
```
Point out: `crictl` bypasses Kubernetes entirely and talks straight to the runtime — proof the runtime is a separate, swappable layer underneath.

---

## 12. Sidecar Containers

**Part 1 — Technical Discussion:** A sidecar is an extra container in the same Pod as the main application. The containers share the Pod's network and can share storage, so the sidecar can help with a supporting task such as collecting logs, handling a proxy, or exporting metrics.

**Image generation prompt:** [Technical style block] + "A systems diagram of a single Pod boundary box containing two smaller boxes side-by-side sharing the same network/storage icon underneath them — 'Main Container' and 'Sidecar Container' labeled separately, with a small arrow from the sidecar labeled 'ships logs out.'"

**Part 2 — Analogy / Zine:** Sits in the same unit handling side tasks, like shipping out logs, without bothering the main tenant.

**Image generation prompt:** [Zine style block] + "Inside one apartment unit, a quiet roommate figure in the corner handling a small side task — sorting and mailing out a stack of papers labeled 'LOGS' — while the main tenant goes about their day undisturbed in the foreground."

* **Zine Text & Layout:**
* (Top): "Sidecar Containers — The Roommate"
* (Caption): "Secondary containers in a Pod that share network/storage to handle logging, proxies (like Istio), or metrics."

**Part 3 — Demo:**
```yaml
# sidecar-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
spec:
  containers:
  - name: main
    image: nginx
  - name: log-shipper
    image: busybox
    command: ["sh", "-c", "while true; do echo shipping logs; sleep 5; done"]
```
```bash
kubectl apply -f sidecar-demo.yaml
kubectl get pod sidecar-demo   # note READY 2/2 — two containers, one Pod
kubectl logs sidecar-demo -c log-shipper
```
Point out: `READY 2/2` — two containers sharing one Pod, one address, one lifecycle — the roommate living in the same unit.

---

## 13. Init Containers

**Part 1 — Technical Discussion:** An init container runs before the main application containers. It must finish successfully before the application starts. This is useful for one-time preparation, such as downloading configuration or running a database migration.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a sequential timeline: 'Init Container (runs to completion)' box with a checkmark, an arrow labeled 'then' pointing to 'Main Container starts,' clearly showing the Init Container's box disappearing after completion."

**Part 2 — Analogy / Zine:** Cleans and preps the unit, then leaves completely before the main tenant moves in.

**Image generation prompt:** [Zine style block] + "A prep crew cleaning, painting, and setting up an empty apartment unit, then fully exiting through the front door with their tools packed up, the main tenant's moving truck visible arriving just after they leave."

* **Zine Text & Layout:**
* (Top): "Init Containers — The Prep Crew"
* (Caption): "Setup scripts that must run to completion (e.g. running DB migrations) before the main app container starts."

**Part 3 — Demo:**
```yaml
# init-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: prep-crew
    image: busybox
    command: ["sh", "-c", "echo prepping unit...; sleep 3"]
  containers:
  - name: main-tenant
    image: nginx
```
```bash
kubectl apply -f init-demo.yaml
kubectl get pod init-demo -w   # watch it sit in Init:0/1 before Running
kubectl logs init-demo -c prep-crew
```
Point out: the Pod's status literally reads `Init:0/1` until the prep crew finishes and exits — the main tenant can't move in until that's done.

---
# GROUP 4 — NETWORKING

## 14. CNI (Container Network Interface)

**Part 1 — Technical Discussion:** CNI plugins provide the network that Pods use. They give Pods IP addresses and set up the routes that let Pods communicate, even when they are on different Nodes. Examples include Calico and Cilium.

**Image generation prompt:** [Technical style block] + "A systems diagram of scattered Node boxes with no connecting lines on the left, transitioning via an arrow into the same Nodes now connected by a labeled network mesh with IP address tags on each Pod icon, captioned 'CNI plugin (e.g. Calico, Cilium).'"

**Part 2 — Analogy / Zine:** The crew that paves the roads and hands out addresses so tenants can reach each other.

**Image generation prompt:** [Zine style block] + "A construction crew in hard hats actively paving fresh roads between separate buildings and nailing numbered address plaques onto every unit door, previously stranded buildings now visibly connected."

* **Zine Text & Layout:**
* (Top): "CNI — The Road Crew"
* (Caption): "Plugins (Calico, Cilium) that provide the actual Pod-to-Pod IP networking."

**Part 3 — Demo:**
```bash
kubectl get pods -n kube-system -o wide | grep -iE "calico|cilium|flannel"
kubectl get pods -A -o custom-columns=NS:.metadata.namespace,POD:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName
```
Point out: every Pod, regardless of which node it's on, gets a routable IP — that flat addressing only works because the CNI plugin paved the roads between nodes.

---

## 15. CoreDNS

**Part 1 — Technical Discussion:** CoreDNS is the cluster's phone book. It translates a friendly Service name into the Service's network address. Applications can call a name such as a Service name instead of trying to remember changing IP addresses.

**Image generation prompt:** [Technical style block] + "A systems diagram of a lookup box labeled 'CoreDNS' receiving a query 'orders-service' and returning a resolved IP address, with an arrow showing the requesting Pod then connecting directly to that IP."

**Part 2 — Analogy / Zine:** Tenants look up a friendly name instead of memorizing unit numbers.

**Image generation prompt:** [Zine style block] + "A large signpost reading 'BUILDING DIRECTORY,' a tenant looking up a friendly name like 'Billing Office' on the board and being shown the current unit number, rather than needing to memorize it."

* **Zine Text & Layout:**
* (Top): "CoreDNS — The Building Directory"
* (Caption): "Internal DNS that resolves Service names to cluster IPs."

**Part 3 — Demo:**
```bash
kubectl run dns-test --image=busybox --rm -it --restart=Never -- \
  nslookup demo.default.svc.cluster.local
```
Point out: nobody typed an IP address — just the Service's friendly name — and CoreDNS resolved it, exactly like asking the directory board instead of memorizing a unit number.

---

## 16. Services

**Part 1 — Technical Discussion:** A Service gives an application a stable name and virtual IP even though the Pods behind it may change. It sends incoming requests to matching healthy Pods, so clients do not need to track individual Pod IP addresses.

**Image generation prompt:** [Technical style block] + "A systems diagram of a fixed box labeled 'Service (stable IP)' at the top, with dotted arrows fanning down to several Pod icons that fade in and out below it, captioned 'Pods are ephemeral. The Service address never changes.'"

**Part 2 — Analogy / Zine:** A bolted mailbox that points to whichever tenants currently have the matching door nameplates.

**Image generation prompt:** [Zine style block] + "A fixed, bolted mailbox bank on a wall that never moves, small nameplate tags being slid in and out behind the scenes by a maintenance hand as tenants change, mail still always arriving at the same mailbox regardless."

* **Zine Text & Layout:**
* (Top): "Services — The Permanent Mailbox"
* (Caption): "Provides a stable internal IP and load balancing for a shifting set of ephemeral Pods."

**Part 3 — Demo:**
```bash
kubectl expose deployment demo --port=80 --name=demo-svc
kubectl get svc demo-svc
kubectl delete pod -l app=demo
kubectl get svc demo-svc   # same ClusterIP, unchanged
```
Point out: Pods got destroyed and replaced, but the Service's ClusterIP never moved — the mailbox stayed bolted to the wall the whole time.

---

## 17. Endpoints

**Part 1 — Technical Discussion:** Endpoints record which Pod addresses currently belong behind a Service. Kubernetes updates this list as matching Pods start, stop, or become unready. The Service uses the current list when it forwards traffic.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'Service' box with an arrow labeled 'selector match' pointing down to an 'Endpoints' list box containing several live Pod IP entries, one entry shown being crossed out and a new one added as Pods change."

**Part 2 — Analogy / Zine:** The actual mail-forwarding list taped inside the mailbox, updated every time a tenant moves in or out.

**Image generation prompt:** [Zine style block] + "A close-up of the inside of the mailbox from the previous page, revealing a taped index card list of current unit numbers being actively updated with a pencil, crossed-out old entries and freshly written new ones."

* **Zine Text & Layout:**
* (Top): "Endpoints — The Forwarding List"
* (Caption): "Maps a Service to the current set of Pod IPs actually backing it."

**Part 3 — Demo:**
```bash
kubectl get endpoints demo-svc -o wide
kubectl scale deployment demo --replicas=5
kubectl get endpoints demo-svc -o wide   # now lists 5 IPs
```
Point out: the Service address never changed, but the Endpoints list grew from 3 entries to 5 the moment more Pods came online — that's the forwarding list being rewritten live.

---

## 18. Ingress

**Part 1 — Technical Discussion:** Ingress describes how web traffic from outside the cluster should enter. An Ingress controller reads rules such as a hostname or URL path and sends each request to the correct internal Service.

**Image generation prompt:** [Technical style block] + "A systems diagram of a single gate icon labeled 'Ingress' at the cluster boundary, external traffic arrows labeled with different domain paths entering the gate, then branching internally to separate 'Service' boxes based on routing rules."

**Part 2 — Analogy / Zine:** The single outer gate reads visitor destinations and sends them down the right internal road.

**Image generation prompt:** [Zine style block] + "The complex's main outer gate with a gatekeeper reading visitor ID badges, directing each visitor down a different labeled internal road toward the correct building, a clipboard of routing rules in the gatekeeper's hand."

* **Zine Text & Layout:**
* (Top): "Ingress — The Main Gate"
* (Caption): "HTTP/S reverse proxy routing external domain traffic into your internal Services."

**Part 3 — Demo:**
```yaml
# demo-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ingress
spec:
  rules:
  - host: demo.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: demo-svc
            port:
              number: 80
```
```bash
kubectl apply -f demo-ingress.yaml
kubectl get ingress demo-ingress
curl -H "Host: demo.local" http://<ingress-controller-ip>/
```
Point out: one external address, but the hostname in the request decides which internal Service the gatekeeper routes you to.

---

## 19. NetworkPolicy

**Part 1 — Technical Discussion:** A NetworkPolicy is a traffic rule for Pods. It can allow or block connections based on labels, namespaces, ports, and traffic direction. The network plugin enforces the rule; without restrictive policies, Pods are generally allowed to communicate.

**Image generation prompt:** [Technical style block] + "A systems diagram of two Pod boxes with a firewall/shield icon in between them labeled 'NetworkPolicy,' one arrow shown blocked with a red X and another allowed with a green checkmark based on matching labels."

**Part 2 — Analogy / Zine:** A guest list posted on a unit's door — only visitors on the list get buzzed in, everyone else is turned away at that door.

**Image generation prompt:** [Zine style block] + "An apartment door with a posted 'APPROVED VISITORS ONLY' guest list, one visitor being buzzed in because their name matches the list, another visitor turned away at the door because their name isn't on it."

* **Zine Text & Layout:**
* (Top): "NetworkPolicy — The Guest List"
* (Caption): "Restricts which Pods can talk to which other Pods — without one, every door is unlocked to everyone."

**Part 3 — Demo:**
```yaml
# deny-demo.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
spec:
  podSelector: {}
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector: {}
```
```bash
kubectl create namespace other-ns
kubectl apply -f deny-demo.yaml
kubectl run intruder -n other-ns --image=busybox --rm -it --restart=Never -- \
  wget -qO- --timeout=3 demo-svc.default.svc.cluster.local
```
Point out: the request times out — the guest list only allows Pods from the same namespace in; the "intruder" from another namespace gets turned away at the door.

---

# GROUP 5 — STORAGE

## 20. PersistentVolume (PV)

**Part 1 — Technical Discussion:** A PersistentVolume, or PV, represents storage that Kubernetes can attach to a workload. The storage can be created ahead of time or created through a StorageClass. It can outlive a Pod, so data does not have to disappear when that Pod is replaced.

**Image generation prompt:** [Technical style block] + "A systems diagram of a storage cylinder icon labeled 'PersistentVolume' sitting outside any Pod boundary, at the cluster level, with a small tag reading 'lifecycle independent of any Pod.'"

**Part 2 — Analogy / Zine:** A separate storage facility building down the road, built to outlast any single tenant.

**Image generation prompt:** [Zine style block] + "A separate storage facility building down the road from the apartments, clearly standing independently, a sign reading 'PROPERTY OF THE COMPLEX, NOT ANY ONE TENANT.'"

* **Zine Text & Layout:**
* (Top): "PersistentVolume — The Storage Facility"
* (Caption): "Represents actual cluster storage, provisioned ahead of time or dynamically, independent of any Pod's lifecycle."

**Part 3 — Demo:**
```bash
kubectl get pv
kubectl describe pv <pv-name> | grep -A2 "Claim\|Status"
```
Point out: the PV exists and shows a status (Available/Bound/Released) whether or not any Pod is currently using it — the facility stands whether or not a tenant has claimed a unit in it yet.

---

## 21. PersistentVolumeClaim (PVC)

**Part 1 — Technical Discussion:** A PersistentVolumeClaim, or PVC, is a request for storage. It says how much storage is needed and sometimes describes the required access or storage class. Kubernetes finds a suitable PersistentVolume and binds the request to it.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'PersistentVolumeClaim' request box with an arrow labeled 'binds to' connecting it to a matching 'PersistentVolume' box, with a Pod box referencing the PVC by name."

**Part 2 — Analogy / Zine:** A universal rental agreement a tenant signs to claim a unit in the storage facility.

**Image generation prompt:** [Zine style block] + "A tenant signing a rental agreement document at a desk, the document then being matched and stapled to a specific storage facility unit key, the tenant walking away with the key in hand."

* **Zine Text & Layout:**
* (Top): "PersistentVolumeClaim — The Rental Agreement"
* (Caption): "A request for storage that Kubernetes matches to a suitable PersistentVolume."

**Part 3 — Demo:**
```yaml
# demo-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: demo-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
```
```bash
kubectl apply -f demo-pvc.yaml
kubectl get pvc demo-pvc
kubectl get pv   # watch a new PV get dynamically created and bound
```
Point out: the claim went in, and a matching PV bound to it (or was created on the fly) — the rental agreement got signed and matched to a real unit automatically.

---

## 22. StorageClass

**Part 1 — Technical Discussion:** A StorageClass is a recipe for creating storage. It tells Kubernetes which storage provider and settings to use when a PVC asks for space. This allows storage to be created on demand instead of requiring an administrator to prepare every PV first.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'StorageClass' template box feeding a provisioning arrow that dynamically generates new 'PersistentVolume' boxes on demand, labeled 'no manual pre-creation needed.'"

**Part 2 — Analogy / Zine:** The complex's pre-approved construction blueprint for building a brand-new storage unit on demand, instead of waiting for one to already exist.

**Image generation prompt:** [Zine style block] + "A construction blueprint labeled 'STANDARD STORAGE UNIT BLUEPRINT' pinned to an office wall, a construction crew breaking ground on a brand new storage facility unit the moment a tenant's rental agreement comes in, no waiting for a pre-built unit."

* **Zine Text & Layout:**
* (Top): "StorageClass — The Construction Blueprint"
* (Caption): "Defines how new storage gets dynamically provisioned on demand, so nobody has to pre-build units ahead of time."

**Part 3 — Demo:**
```bash
kubectl get storageclass
kubectl describe storageclass standard
```
Point out: this is the blueprint referenced automatically when a PVC doesn't specify one — it's why the PV in the previous demo appeared without anyone manually creating it first.

---
# GROUP 6 — ACCESS CONTROL

## 23. Role

**Part 1 — Technical Discussion:** A Role is a list of actions that are allowed inside one Namespace. For example, it can allow reading Pods or creating ConfigMaps. A Role is only a rule; it does not give anyone access until a binding connects it to a user, group, or ServiceAccount.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'Role' box listing permission verbs (get, list, watch, create) next to resource icons (Pods, Services), entirely contained within one Namespace boundary box, with a note 'grants nothing until bound.'"

**Part 2 — Analogy / Zine:** A printed set of house rules for one specific building — what's allowed inside, but nobody's name is on it yet.

**Image generation prompt:** [Zine style block] + "A printed house-rules sheet pinned to a single building's lobby wall, listing permitted actions like 'may enter gym, may use laundry room,' a blank space at the bottom where a resident's name would go, currently empty."

* **Zine Text & Layout:**
* (Top): "Role — The House Rules"
* (Caption): "Defines what's permitted within one building (Namespace) — but grants it to nobody until a name is added."

**Part 3 — Demo:**
```bash
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n default
kubectl get role pod-reader -o yaml
```
Point out: the Role now exists with real permissions listed, but running `kubectl auth can-i get pods --as=someuser` still says no — the house rules are posted, but no name is attached yet.

---

## 24. RoleBinding

**Part 1 — Technical Discussion:** A RoleBinding connects a Role to a person, group, or ServiceAccount. That connection gives the subject the listed permissions in the Role's Namespace. Without the binding, the Role's permissions are not assigned to anyone.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a 'Role' box connected by an arrow labeled 'RoleBinding' to a 'Subject' box (user/group/ServiceAccount icon), both contained within the same Namespace boundary."

**Part 2 — Analogy / Zine:** The clipboard sign-up sheet where a specific tenant's name gets added under the house rules, officially granting them those permissions.

**Image generation prompt:** [Zine style block] + "A staff member writing a specific tenant's name onto the blank line at the bottom of the house-rules sheet from the previous page, the tenant now shown using the gym and laundry room they were granted access to."

* **Zine Text & Layout:**
* (Top): "RoleBinding — The Sign-Up Sheet"
* (Caption): "Grants a Role's permissions to a specific user, group, or ServiceAccount, within that same building (Namespace)."

**Part 3 — Demo:**
```bash
kubectl create rolebinding read-pods-binding \
  --role=pod-reader --user=jane -n default
kubectl auth can-i get pods --as=jane -n default
```
Point out: `can-i` flips from "no" to "yes" the instant the binding exists — the name got added to the sign-up sheet.

---

## 25. ClusterRole

**Part 1 — Technical Discussion:** A ClusterRole is a permission list that is not limited to one Namespace. It can describe access across many Namespaces or to cluster-wide objects such as Nodes. It still needs a binding before it grants access.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'ClusterRole' box listing permission verbs, drawn spanning across ALL Namespace boundary boxes in the cluster diagram at once, rather than sitting inside just one."

**Part 2 — Analogy / Zine:** A master house-rules sheet that applies across every building in the entire complex, not just one.

**Image generation prompt:** [Zine style block] + "A master rules document being posted simultaneously on the front gate of the entire complex and on every individual building's lobby wall at once, labeled 'COMPLEX-WIDE RULES,' contrasted with the single-building rules sheet from before."

* **Zine Text & Layout:**
* (Top): "ClusterRole — The Master House Rules"
* (Caption): "Like a Role, but scoped to the entire cluster instead of a single Namespace."

**Part 3 — Demo:**
```bash
kubectl create clusterrole node-reader --verb=get,list,watch --resource=nodes
kubectl get clusterrole node-reader -o yaml
```
Point out: `nodes` is a cluster-scoped resource — it doesn't belong to any one Namespace, which is exactly why this permission had to be a ClusterRole and couldn't be a plain Role.

---

## 26. ClusterRoleBinding

**Part 1 — Technical Discussion:** A ClusterRoleBinding connects a ClusterRole to a subject for the whole cluster. The subject receives those permissions across Namespaces and for any cluster-scoped resources covered by the role.

**Image generation prompt:** [Technical style block] + "A systems diagram showing a 'ClusterRole' box connected via an arrow labeled 'ClusterRoleBinding' to a 'Subject' box, with the granted access shown fanning out across every Namespace boundary in the cluster diagram."

**Part 2 — Analogy / Zine:** A master key issued to one person that works on every building in the complex, not just one unit.

**Image generation prompt:** [Zine style block] + "A staff member handing over a single labeled 'MASTER KEY' to one person, that person shown using the same key to unlock doors across several different buildings in the complex, contrasted with a normal single-building key from before."

* **Zine Text & Layout:**
* (Top): "ClusterRoleBinding — The Master Key"
* (Caption): "Grants a ClusterRole's permissions to a subject across the entire cluster, not just one Namespace."

**Part 3 — Demo:**
```bash
kubectl create clusterrolebinding read-nodes-binding \
  --clusterrole=node-reader --user=jane
kubectl auth can-i get nodes --as=jane
kubectl auth can-i get nodes --as=jane -n kube-system
```
Point out: access works the same regardless of which Namespace jane checks from — the master key isn't scoped to any one building.

---

## 27. ServiceAccount

**Part 1 — Technical Discussion:** A ServiceAccount is an identity for software running in a Pod. An application can use that identity when it calls the Kubernetes API. It is separate from the account a human uses with kubectl.

**Image generation prompt:** [Technical style block] + "A systems diagram of a Pod box containing a 'ServiceAccount' identity badge icon, an arrow labeled 'authenticates as' pointing from the badge to the kube-apiserver box."

**Part 2 — Analogy / Zine:** A staff ID badge issued to a robot maintenance worker so the front desk knows it's an authorized employee, not a random visitor.

**Image generation prompt:** [Zine style block] + "A small robot maintenance worker wearing a clipped-on staff ID badge, presenting the badge at the front desk, the clerk waving it through as an authorized employee rather than treating it like an outside visitor."

* **Zine Text & Layout:**
* (Top): "ServiceAccount — The Staff ID Badge"
* (Caption): "Provides an identity for processes inside Pods to authenticate to the API server — distinct from a human user."

**Part 3 — Demo:**
```bash
kubectl create serviceaccount demo-bot
kubectl run badge-test --image=busybox --overrides='{"spec":{"serviceAccountName":"demo-bot"}}' \
  --rm -it --restart=Never -- sh -c 'head -c 50 /var/run/secrets/kubernetes.io/serviceaccount/token'
```
Point out: every Pod automatically gets a mounted token file — that's its staff ID badge, minted and clipped on without a human ever logging in.

---
# GROUP 7 — RESOURCE & CLUSTER CONTROLLERS

## 28. Node (controller)

**Part 1 — Technical Discussion:** The Node controller watches for regular health messages from each kubelet. If a Node stops reporting, the controller marks it NotReady. After a period of time, Kubernetes can remove the Node's workloads so they can be recreated elsewhere.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'Node Controller' box receiving periodic heartbeat pulse arrows from several Node boxes, one Node's heartbeat stopping and its box turning to a warning color labeled 'NotReady after timeout.'"

**Part 2 — Analogy / Zine:** The office worker who checks in on every building daily, and starts moving tenants out if a building goes quiet for too long.

**Image generation prompt:** [Zine style block] + "An office staff member phoning each building daily for a check-in call, one building not answering the phone for several days in a row, the staff member starting to arrange for tenants to be moved to other buildings."

* **Zine Text & Layout:**
* (Top): "Node Controller — The Daily Check-In"
* (Caption): "Watches Node health via heartbeats, marking a Node NotReady and evicting its Pods if it goes silent too long."

**Part 3 — Demo:**
```bash
kubectl get nodes
kubectl describe node <node-name> | grep -A5 Conditions
# simulate: stop kubelet on that node, then re-check
kubectl get nodes -w
```
Point out: watch the node's status flip from Ready to NotReady after the heartbeat stops — and eventually Pods scheduled there get evicted and rescheduled elsewhere.

---

## 29. Namespace (controller)

**Part 1 — Technical Discussion:** The Namespace controller manages the lifetime of a Namespace. When the Namespace is deleted, it helps remove the objects inside it first. Only after the contents are cleaned up can the Namespace disappear completely.

**Image generation prompt:** [Technical style block] + "A systems diagram of a Namespace boundary box marked 'Terminating,' with arrows showing every resource inside it (Pods, Services, ConfigMaps) being individually deleted one by one before the boundary box itself finally disappears."

**Part 2 — Analogy / Zine:** When a fenced section of the property is being shut down, every tenant and piece of furniture inside is cleared out first before the fence itself comes down.

**Image generation prompt:** [Zine style block] + "A fenced section of the property with a 'CLOSING DOWN' sign, movers actively clearing out tenants and furniture one by one from inside the fence, the fence itself still standing until everything inside is empty."

* **Zine Text & Layout:**
* (Top): "Namespace Controller — The Section Closure"
* (Caption): "Ensures every resource inside a Namespace is cleaned up before the Namespace itself is removed."

**Part 3 — Demo:**
```bash
kubectl create namespace demo-ns
kubectl run temp-pod --image=nginx -n demo-ns
kubectl delete namespace demo-ns
kubectl get namespace demo-ns -w   # watch it sit in "Terminating"
```
Point out: the Namespace lingers in `Terminating` status while its contents (like `temp-pod`) get cleaned up first — the fence doesn't come down until the section is empty.

---

## 30. ResourceQuota

**Part 1 — Technical Discussion:** A ResourceQuota sets a limit for one Namespace. The limit can cover CPU and memory or the number of objects such as Pods and Services. Kubernetes rejects new objects when they would push the Namespace over its quota.

**Image generation prompt:** [Technical style block] + "A systems diagram of a Namespace boundary box with a gauge/meter icon labeled 'ResourceQuota: max 10 Pods, 4 CPU' at its border, a new Pod creation request being blocked with a red X once the limit is reached."

**Part 2 — Analogy / Zine:** A posted occupancy limit sign on a fenced section — once it's full, the front desk simply refuses to let anyone else move in.

**Image generation prompt:** [Zine style block] + "A posted sign at the entrance of a fenced section reading 'MAX OCCUPANCY: 10 UNITS,' a new tenant being turned away at the gate because the section has already hit its limit."

* **Zine Text & Layout:**
* (Top): "ResourceQuota — The Occupancy Limit Sign"
* (Caption): "Caps the total resources or object counts a single Namespace (fenced section) is allowed to consume."

**Part 3 — Demo:**
```yaml
# quota-demo.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pod-limit
  namespace: demo-ns
spec:
  hard:
    pods: "2"
```
```bash
kubectl apply -f quota-demo.yaml
kubectl run p1 --image=nginx -n demo-ns
kubectl run p2 --image=nginx -n demo-ns
kubectl run p3 --image=nginx -n demo-ns   # this one gets rejected
```
Point out: the third Pod creation is flatly refused with a quota-exceeded error — the section hit its posted occupancy limit.

---

## 31. Garbage Collector

**Part 1 — Technical Discussion:** The Garbage Collector removes Kubernetes objects that were left behind without their owner. It follows owner references, such as a ReplicaSet owning its Pods. If the owner is deleted, Kubernetes can clean up the dependent objects too.

**Image generation prompt:** [Technical style block] + "A systems diagram of an 'owner reference' arrow connecting a child Pod box to a parent ReplicaSet box, the parent box being deleted, and a 'Garbage Collector' icon automatically sweeping away the now-orphaned child Pod box."

**Part 2 — Analogy / Zine:** The cleanup crew that removes any leftover furniture in a unit once the tenant who ordered it moves out — nothing is left behind unclaimed.

**Image generation prompt:** [Zine style block] + "A cleanup crew sweeping leftover furniture and boxes out of an apartment unit whose tenant has already moved out, a small tag on the furniture reading 'ordered by: [former tenant]' explaining why it's being cleared."

* **Zine Text & Layout:**
* (Top): "Garbage Collector — The Cleanup Crew"
* (Caption): "Automatically deletes objects whose owner is gone, using owner references to trace and clean up orphans."

**Part 3 — Demo:**
```bash
kubectl create deployment gc-demo --image=nginx --replicas=2
kubectl get pods -l app=gc-demo -o yaml | grep -A2 ownerReferences
kubectl delete deployment gc-demo
kubectl get pods -l app=gc-demo   # empty — cascaded automatically
```
Point out: nobody deleted the Pods or the ReplicaSet directly — deleting the Deployment cascaded all the way down via owner references, exactly like clearing out furniture nobody's claiming anymore.

---
# GROUP 8 — WORKLOAD CONTROLLERS

## 32. ReplicaSet

**Part 1 — Technical Discussion:** A ReplicaSet keeps a chosen number of matching Pods running. If one Pod disappears, it creates another to restore the count. It focuses on keeping the number of identical replicas correct.

**Image generation prompt:** [Technical style block] + "A systems diagram of a counter box reading '3/3 desired,' three identical Pod icons beneath it, one Pod icon shown crashing/greying out and a new identical Pod icon immediately spawning to restore the count to 3/3."

**Part 2 — Analogy / Zine:** Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly.

**Image generation prompt:** [Zine style block] + "An occupancy counter board on the wall permanently reading '3/3 FILLED,' one unit shown going vacant with a 'VACANT' sign, immediately followed by a new identical tenant moving in to restore the count."

* **Zine Text & Layout:**
* (Top): "ReplicaSet — The Occupancy Enforcer"
* (Caption): "Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly."

**Part 3 — Demo:**
```bash
kubectl create deployment rs-demo --image=nginx --replicas=3
kubectl get replicaset -l app=rs-demo
kubectl delete pod $(kubectl get pods -l app=rs-demo -o name | head -1)
kubectl get pods -l app=rs-demo
```
Point out: the count self-heals back to 3 immediately — the ReplicaSet only cares about the number, not which specific Pods make it up.

---

## 33. Deployment

**Part 1 — Technical Discussion:** A Deployment manages ReplicaSets and makes application updates safer. It replaces old Pods with new Pods gradually, so the application can keep serving traffic during the update. If the new version is bad, the Deployment can roll back to the previous version.

**Image generation prompt:** [Technical style block] + "A systems diagram showing 'Deployment' box managing two ReplicaSet boxes labeled 'v1 (scaling down)' and 'v2 (scaling up)' side by side with a gradual arrow between them, plus a small 'rollback' arrow looping back to v1."

**Part 2 — Analogy / Zine:** Manages swapping an entire set of units from a v1 layout to a v2 layout gradually, with a lever to rollback if inspections fail.

**Image generation prompt:** [Zine style block] + "A renovation planner staff member holding two blueprints side by side labeled 'v1 LAYOUT' and 'v2 LAYOUT,' overseeing units being swapped over gradually one at a time, with a clearly visible lever on the wall labeled 'ROLLBACK' within easy reach."

* **Zine Text & Layout:**
* (Top): "Deployment — The Renovation Planner"
* (Caption): "This is what you actually deploy. It creates the ReplicaSets and handles zero-downtime rolling updates."

**Part 3 — Demo:**
```bash
kubectl create deployment deploy-demo --image=nginx:1.24 --replicas=3
kubectl set image deployment/deploy-demo nginx=nginx:1.25
kubectl rollout status deployment/deploy-demo
kubectl rollout undo deployment/deploy-demo
```
Point out: the update rolled through gradually with zero downtime, and `rollout undo` pulled the rollback lever instantly back to the previous version.

---

## 34. StatefulSet

**Part 1 — Technical Discussion:** A StatefulSet is for applications whose Pods need lasting identities. Each Pod gets a predictable name and can keep its own storage. When the Pod restarts, Kubernetes brings it back with the same identity instead of treating it as an interchangeable copy.

**Image generation prompt:** [Technical style block] + "A systems diagram of three Pod boxes labeled with fixed sequential names 'app-0,' 'app-1,' 'app-2,' each permanently connected to its own labeled PersistentVolume, contrasted with a Deployment's interchangeable unlabeled Pod icons shown faded in the background."

**Part 2 — Analogy / Zine:** Named, numbered units where the same tenant always returns to the exact same unit with their exact same furniture — never shuffled to a different room.

**Image generation prompt:** [Zine style block] + "Three apartment doors clearly numbered 'UNIT-0,' 'UNIT-1,' 'UNIT-2,' each tenant shown moving out temporarily and then returning to their exact same numbered unit with their exact same furniture waiting for them, contrasted with the shuffled anonymous units from the Deployment page."

* **Zine Text & Layout:**
* (Top): "StatefulSet — The Named Units"
* (Caption): "Manages Pods needing stable identities and persistent storage tied to that identity — each Pod keeps its name and storage across restarts."

**Part 3 — Demo:**
```yaml
# statefulset-demo.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "web"
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
```
```bash
kubectl apply -f statefulset-demo.yaml
kubectl get pods -l app=web   # note: web-0, web-1, web-2 — stable names
kubectl delete pod web-1
kubectl get pods -l app=web -w   # replacement comes back as web-1, not a random name
```
Point out: the replacement Pod comes back with the exact same name, `web-1` — the tenant returned to the same numbered unit, not a random new one.

---

## 35. DaemonSet

**Part 1 — Technical Discussion:** A DaemonSet places one copy of a Pod on every matching Node. It is useful for Node-level work, such as collecting logs or monitoring the machine. When a new matching Node joins, the DaemonSet adds the Pod there too.

**Image generation prompt:** [Technical style block] + "A systems diagram of every Node box in the cluster, each one containing an identical small Pod icon automatically placed on it, labeled 'DaemonSet: one copy per node, no scheduler math needed.'"

**Part 2 — Analogy / Zine:** A dedicated fire extinguisher mounted in every single building — one per building, automatically, no exceptions.

**Image generation prompt:** [Zine style block] + "An aerial view of every building in the complex, each one shown with an identical fire extinguisher mounted by the front door, a maintenance worker walking past confirming every building has exactly one, no building skipped."

* **Zine Text & Layout:**
* (Top): "DaemonSet — The Fire Extinguisher on Every Floor"
* (Caption): "Ensures exactly one copy of a Pod runs on every Node — often used for node-level agents like log collectors."

**Part 3 — Demo:**
```yaml
# daemonset-demo.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
spec:
  selector:
    matchLabels:
      app: node-agent
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      containers:
      - name: agent
        image: busybox
        command: ["sh", "-c", "while true; do sleep 3600; done"]
```
```bash
kubectl apply -f daemonset-demo.yaml
kubectl get pods -l app=node-agent -o wide
kubectl get nodes | wc -l   # compare counts — they should match
```
Point out: the Pod count matches the Node count exactly, one per building — and if you add a new Node to the cluster, a new Pod appears there automatically, with no scheduler decision needed.

---

## 36. Job

**Part 1 — Technical Discussion:** A Job runs Pods for a task that should finish. It keeps track of successful completions and can retry failures. Once the requested work is complete, the Job stops instead of keeping a service running forever.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'Job' box spawning a Pod icon that runs a task to a checkmark completion state, then the Pod box fading away, with a completion counter reading '1/1 Completed,' contrasted with a Deployment's Pod icon shown looping forever."

**Part 2 — Analogy / Zine:** A one-time moving crew hired to move a single tenant's boxes — once the job is done, the crew packs up and leaves for good, not staying on payroll.

**Image generation prompt:** [Zine style block] + "A moving crew finishing carrying the last box into a unit, a supervisor checking off 'JOB COMPLETE' on a clipboard, the crew then packing their truck and driving away for good, contrasted with a permanent building staff member who stays forever."

* **Zine Text & Layout:**
* (Top): "Job — The One-Time Moving Crew"
* (Caption): "Runs Pods to completion for a finite task, then stops — unlike a Deployment, it doesn't keep Pods running forever."

**Part 3 — Demo:**
```yaml
# job-demo.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: one-time-task
spec:
  template:
    spec:
      containers:
      - name: task
        image: busybox
        command: ["sh", "-c", "echo doing the move; sleep 5; echo done"]
      restartPolicy: Never
```
```bash
kubectl apply -f job-demo.yaml
kubectl get jobs -w   # watch COMPLETIONS go from 0/1 to 1/1
kubectl logs job/one-time-task
```
Point out: once it hits `1/1 Completed`, the Job stops — the crew finished the move and isn't hanging around drawing a paycheck.

---

## 37. CronJob

**Part 1 — Technical Discussion:** A CronJob starts Jobs on a schedule. You can use a cron expression to say when the work should run, such as every night at 2:00 AM. Each scheduled run creates a separate Job.

**Image generation prompt:** [Technical style block] + "A systems diagram of a clock/calendar icon labeled 'CronJob: 0 2 * * *' with a repeating arrow spawning a new 'Job' box each time the schedule fires, a trail of past completed Job boxes shown behind it."

**Part 2 — Analogy / Zine:** The scheduled overnight cleaning crew that shows up automatically every night at 2 AM, does the job, and leaves — nobody has to call them each time.

**Image generation prompt:** [Zine style block] + "A wall calendar with '2:00 AM — CLEANING CREW' circled on every night, a cleaning crew shown arriving automatically through the gate at that exact time each night, doing their rounds, then leaving before sunrise, no phone call needed."

* **Zine Text & Layout:**
* (Top): "CronJob — The Scheduled Night Crew"
* (Caption): "Creates Jobs on a repeating schedule — like a nightly backup task that runs automatically without anyone triggering it."

**Part 3 — Demo:**
```yaml
# cronjob-demo.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-task
spec:
  schedule: "*/2 * * * *"   # every 2 minutes, for demo purposes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: task
            image: busybox
            command: ["sh", "-c", "echo nightly cleanup ran"]
          restartPolicy: Never
```
```bash
kubectl apply -f cronjob-demo.yaml
kubectl get cronjob nightly-task
kubectl get jobs -w   # watch a new Job appear every 2 minutes, unprompted
```
Point out: nobody ran a command — new Jobs just appear on schedule, exactly like the cleaning crew showing up at 2 AM without a phone call.

---

## 38. ReplicationController (legacy)

**Part 1 — Technical Discussion:** ReplicationController is the older Kubernetes object for keeping a fixed number of matching Pods alive. It is similar to a ReplicaSet but has less flexible label matching. New applications normally use Deployments, which manage ReplicaSets instead.

**Image generation prompt:** [Technical style block] + "A systems diagram showing an old, faded 'ReplicationController' box with a basic equality-only selector, next to a modern 'ReplicaSet' box with a richer set-based selector, an arrow labeled 'superseded by' pointing from the old box to the new one."

**Part 2 — Analogy / Zine:** The original, retired occupancy-enforcer clipboard system the complex used before the newer, more flexible enforcer took over — still technically works, but nobody sets it up new anymore.

**Image generation prompt:** [Zine style block] + "A dusty, old-fashioned clipboard system labeled 'ORIGINAL OCCUPANCY ENFORCER (RETIRED)' sitting in a closet, next to it the modern occupancy counter board from before actively in use on the wall, a small museum-style placard reading 'still works, but replaced.'"

* **Zine Text & Layout:**
* (Top): "ReplicationController — The Retired Enforcer"
* (Caption): "The legacy predecessor to ReplicaSet — functionally similar, but superseded by more flexible label selectors."

**Part 3 — Demo:**
```yaml
# rc-demo.yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: rc-demo
spec:
  replicas: 2
  selector:
    app: rc-demo
  template:
    metadata:
      labels:
        app: rc-demo
    spec:
      containers:
      - name: nginx
        image: nginx
```
```bash
kubectl apply -f rc-demo.yaml
kubectl get rc rc-demo
kubectl explain replicationcontroller | head -5   # note the deprecation-flavored description
```
Point out: it still works exactly like a ReplicaSet — but nobody builds new systems on it; it's kept around mainly for backward compatibility with older clusters.

---
# GROUP 9 — POD AUTOSCALING CONTROLLERS

## 39. HorizontalPodAutoscaler (HPA)

**Part 1 — Technical Discussion:** The HorizontalPodAutoscaler, or HPA, changes how many Pod copies are running. It watches metrics such as CPU or memory use, adds Pods when demand rises, and removes Pods when demand falls. It changes the number of copies, not the size of each Pod.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'HorizontalPodAutoscaler' box watching a CPU-usage gauge feeding from a Deployment's Pods, an arrow labeled 'scale out' adding more Pod icons as the gauge rises into the red zone, and 'scale in' removing them as it drops."

**Part 2 — Analogy / Zine:** The staffing manager who calls in more substitute teachers automatically when the lunch rush hits a certain crowd size, and sends them home once things quiet down.

**Image generation prompt:** [Zine style block] + "A staffing manager watching a crowd-size gauge at the school cafeteria door, automatically phoning in extra substitute teachers as the gauge climbs into the busy zone, then sending the extras home as the gauge drops back down after the rush."

* **Zine Text & Layout:**
* (Top): "HorizontalPodAutoscaler — The Staffing Manager"
* (Caption): "Automatically adjusts the number of Pod replicas based on CPU/memory usage — scaling out under load, back in when it drops."

**Part 3 — Demo:**
```bash
kubectl create deployment hpa-demo --image=registry.k8s.io/hpa-example
kubectl set resources deployment hpa-demo --requests=cpu=200m
kubectl expose deployment hpa-demo --port=80
kubectl autoscale deployment hpa-demo --cpu-percent=50 --min=1 --max=5
kubectl run load-generator --image=busybox --rm -it --restart=Never -- \
  sh -c "while true; do wget -q -O- http://hpa-demo; done"
kubectl get hpa hpa-demo -w
```
Point out: watch the REPLICAS column climb on its own as CPU load spikes from the generated traffic, then fall back down once the load stops — no one is manually scaling anything.

---

## 40. VerticalPodAutoscaler (VPA)

**Part 1 — Technical Discussion:** The VerticalPodAutoscaler, or VPA, recommends or changes the CPU and memory sizes requested by a Pod. It uses observed usage to decide whether each Pod needs more or less capacity. Unlike HPA, it changes Pod size rather than adding more Pod copies, and it requires the VPA add-on.

**Image generation prompt:** [Technical style block] + "A systems diagram of a 'VerticalPodAutoscaler' box observing a single Pod's resource usage history graph, then an arrow labeled 'resize' shrinking or enlarging that same Pod's box dimensions directly, contrasted with HPA's approach of adding more Pod boxes."

**Part 2 — Analogy / Zine:** Instead of calling in more staff, this manager just gives one tenant a bigger unit when they clearly need more space, and downsizes them if they don't need it anymore.

**Image generation prompt:** [Zine style block] + "A staff member observing one tenant's unit clearly overflowing with belongings, then knocking down a wall to expand that same unit into a bigger one, contrasted with the previous page's staffing manager calling in extra substitutes instead."

* **Zine Text & Layout:**
* (Top): "VerticalPodAutoscaler — The Unit Resizer"
* (Caption): "Automatically adjusts a Pod's CPU/memory requests based on usage history — resizing the Pod itself instead of adding more Pods."

**Part 3 — Demo:**
```yaml
# vpa-demo.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-demo
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: hpa-demo
  updatePolicy:
    updateMode: "Auto"
```
```bash
kubectl apply -f vpa-demo.yaml
kubectl describe vpa vpa-demo   # shows recommended CPU/memory under "Recommendation"
```
Point out: the Recommendation section shows a suggested request size based on actual observed usage — in Auto mode, VPA will evict and recreate the Pod with these new sizes, resizing the unit rather than adding another one.

---

## 41. Pod Disruption Budget (PDB)

**Part 1 — Technical Discussion:** A PodDisruptionBudget, or PDB, protects an application during planned maintenance. It sets how many matching Pods may be voluntarily taken down at the same time, such as during a Node drain. It cannot prevent an unexpected failure like a crashed Node.

**Image generation prompt:** [Technical style block] + "A systems diagram of a group of Pod icons with a 'PodDisruptionBudget: minAvailable=2' shield icon around them, a node-drain operation attempting to evict all of them but being blocked partway through, leaving 2 Pods standing."

**Part 2 — Analogy / Zine:** A rule posted during planned building maintenance: at least 2 units in this wing must stay occupied and undisturbed at any given time, no matter how many maintenance requests come in at once.

**Image generation prompt:** [Zine style block] + "A maintenance crew with a work order to renovate several units at once, a posted sign reading 'AT LEAST 2 UNITS MUST STAY UNDISTURBED AT ALL TIMES,' the crew shown pausing partway through because renovating the next unit would drop the count below 2."

* **Zine Text & Layout:**
* (Top): "Pod Disruption Budget — The Maintenance Limit Rule"
* (Caption): "Limits how many Pods can be voluntarily disrupted at once during planned maintenance, protecting availability."

**Part 3 — Demo:**
```yaml
# pdb-demo.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: demo-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: demo
```
```bash
kubectl apply -f pdb-demo.yaml
kubectl get pdb demo-pdb
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```
Point out: if draining that node would violate `minAvailable: 2`, the drain operation stalls on those specific Pods — the maintenance limit rule is actively blocking it from taking too many units offline at once.

---
---

## Note on "System Controllers"

Your list's **System Controllers** category — API Server, Controller Manager,
Scheduler — is the same trio already covered in **Group 2 (Control Plane)**
as entries #3 (kube-apiserver), #6 (kube-controller-manager), and #5
(kube-scheduler) above, so they aren't duplicated as separate entries here.

---

## Full topic index (41 entries)

**Group 1 — Big Picture:** 1. The Cluster · 2. Control Plane vs. Worker Nodes
**Group 2 — Control Plane:** 3. kube-apiserver · 4. etcd · 5. kube-scheduler · 6. kube-controller-manager · 7. cloud-controller-manager · 8. Static Pods
**Group 3 — Worker Nodes:** 9. kubelet · 10. kube-proxy · 11. Container Runtime & CRI · 12. Sidecar Containers · 13. Init Containers
**Group 4 — Networking:** 14. CNI · 15. CoreDNS · 16. Services · 17. Endpoints · 18. Ingress · 19. NetworkPolicy
**Group 5 — Storage:** 20. PersistentVolume · 21. PersistentVolumeClaim · 22. StorageClass
**Group 6 — Access Control:** 23. Role · 24. RoleBinding · 25. ClusterRole · 26. ClusterRoleBinding · 27. ServiceAccount
**Group 7 — Resource & Cluster:** 28. Node controller · 29. Namespace controller · 30. ResourceQuota · 31. Garbage Collector
**Group 8 — Workload Controllers:** 32. ReplicaSet · 33. Deployment · 34. StatefulSet · 35. DaemonSet · 36. Job · 37. CronJob · 38. ReplicationController (legacy)
**Group 9 — Autoscaling:** 39. HorizontalPodAutoscaler · 40. VerticalPodAutoscaler · 41. Pod Disruption Budget

(System Controllers — API Server, Controller Manager, Scheduler — folded into Group 2, entries #3, #5, #6.)

---

## Tips for use

- Each numbered section = one three-part sequence: Technical Discussion +
  Illustration → Analogy + Zine → Demo with runnable commands. That's 41
  distinct topics (the System Controllers category is folded into entries #3, #5,
  #6), ~120+ total prompt/command blocks.
- Run demos on a disposable local cluster (`kind create cluster` or
  `minikube start`) — several demos delete Pods, drain nodes, or evict
  workloads.
- The demos in `demos-complete.txt` are self-contained: each creates its own
  resources in its own namespace and cleans up afterwards, so they can be run
  in any order. The Part 3 demos inside this brief are the short originals;
  use `demos-complete.txt` for presenting.
- Keep the two illustration style blocks visually distinct: the Part 1
  technical illustration should look like a clean systems/architecture
  diagram with no story elements; the Part 2 zine image should look like an
  illustrated editorial zine scene with its title and short explanation text
  placed on the image, and no raw technical diagram elements.
- Maintain a consistent recurring cast across all Part 2 zine images (the same
  superintendent character, the same front-desk clerk, the same staffing
  manager, etc.) for visual continuity across all 41 topics.
- Negative prompt suggestions for image generation: `photorealistic, 3D
  render, gradient, glossy, watermark, hand-drawn sketch style, stick
  figures, raw sketch, clutter`.
- Some demos (VPA, PDB, HPA's metrics-server dependency) require add-ons not
  installed by default — mention this to the audience before running live,
  or pre-install `metrics-server` and the VPA add-on ahead of time.
