# Kubernetes Apartment Complex — Complete Demo Guide

![Kubernetes Apartment Complex overview](generated/kubernetes-apartment-complex/01-zine.png)

This guide combines the Kubernetes Apartment Complex zine entries with runnable demos. It is both a visual introduction and a technical reference: each entry explains the Kubernetes object or component, shows where it fits in the cluster architecture, calls out operational trade-offs, links to authoritative documentation, and ends with an observable command-line experiment.

## Technical description

Kubernetes is a declarative, API-driven control system. A user or automation client submits objects such as Deployments, Services, and PersistentVolumeClaims to the `kube-apiserver`. The API server authenticates and authorizes the request, applies admission and validation, and persists the accepted state in `etcd`. Controllers continuously compare that desired state with the state reported by Nodes and other resources. When they detect drift, they create, update, or remove objects until the system converges.

For a normal workload, the flow is:

1. A workload object declares the desired state, including the container image, replica count, resource requests, probes, labels, and policy references.
2. The scheduler filters and scores eligible Nodes using resources, taints and tolerations, affinity, topology, and other constraints, then binds each unscheduled Pod to a Node.
3. The kubelet on that Node asks the CRI runtime to create the Pod sandbox, pull images, start containers, mount volumes, and execute probes.
4. The CNI plugin supplies Pod networking, while Services and their EndpointSlices provide stable discovery and traffic routing. Ingress or Gateway controllers can add externally reachable HTTP routing.
5. Controllers, the kubelet, and status reporters publish observed state back through the API. A Deployment, for example, replaces failed replicas and coordinates a rollout; an HPA changes replica count when metrics indicate that demand has changed.

This separation is important: the control plane stores intent and makes decisions, while Nodes execute Pods. A Service is a stable network abstraction rather than a process, a PVC is a request for storage rather than a disk itself, and a PDB limits voluntary disruption rather than protecting against every failure. The “Technical perspective” paragraph in each entry expands these boundaries, failure modes, and production considerations; the demo then verifies the behavior in the cluster.

### Pod creation request flow

<iframe src="k8s-pod-flow-bytemonk.html" width="100%" height="760" style="border:none;"></iframe>

> [!TIP]
> If your Markdown viewer restricts embedded iframes or inline scripts, open [k8s-pod-flow-bytemonk.html](k8s-pod-flow-bytemonk.html) directly in any browser.

### Technical coverage map

The topics build from cluster internals to application operations. Use this map to see the engineering concern emphasized by each entry:

| Topic | Engineering focus |
| --- | --- |
| Cluster | Declarative management, scheduling, reconciliation, and platform trade-offs |
| Control Plane vs. Worker Nodes | Failure boundaries, high availability, and workload continuity |
| kube-apiserver | Authentication, authorization, admission, validation, watches, and API consistency |
| etcd | Strong consistency, quorum, encryption, backup, restore, and control-plane dependency |
| kube-scheduler | Feasibility filtering, scoring, resource requests, placement constraints, and topology |
| kube-controller-manager | Reconciliation, ownership, idempotency, eventual convergence, and drift correction |
| cloud-controller-manager | Provider APIs, cloud identity, quotas, load balancers, routes, and volumes |
| Static Pods | Node-local bootstrapping, manifest drift, and control-plane initialization |
| kubelet | Pod lifecycle enforcement, probes, volumes, status reporting, and node health |
| kube-proxy | Service datapath, virtual IPs, endpoint updates, and proxy implementation choices |
| Container Runtime & CRI | Runtime abstraction, image pulling, sandboxes, cgroups, logging, and isolation |
| Sidecar Containers | Shared namespaces and volumes, lifecycle coupling, telemetry, and resource overhead |
| Init Containers | Ordered initialization, retries, migrations, dependency checks, and startup latency |
| CNI | Pod interfaces, IP allocation, routing, encryption, and policy-capable dataplanes |
| CoreDNS | Service discovery, search paths, caching, forwarding, readiness, and DNS capacity |
| Services | Stable virtual endpoints, selectors, exposure types, and client decoupling |
| Endpoints | EndpointSlice scalability, readiness, serving state, topology, and backend convergence |
| Ingress | Layer-7 routing, TLS termination, controller responsibility, and Gateway API direction |
| NetworkPolicy | Namespaced allow rules, ingress/egress isolation, CNI enforcement, and DNS dependencies |
| PersistentVolume | Storage lifecycle, reclaim policy, access modes, topology, and backup limits |
| PersistentVolumeClaim | Workload storage requests, binding constraints, provisioning, and Pending diagnosis |
| StorageClass | Dynamic provisioning, parameters, binding mode, performance, cost, and retention |
| Role | Namespaced API permissions, verbs, resources, least privilege, and escalation risk |
| RoleBinding | Attaching permissions to identities and auditing effective namespace access |
| ClusterRole | Reusable or cluster-scoped permissions and the impact of broad rules |
| ClusterRoleBinding | Cluster-wide grants, platform automation, and high-impact access review |
| ServiceAccount | Workload identity, projected tokens, RBAC, and API credential hygiene |
| Node controller | Heartbeats, leases, failure detection, eviction timing, and redundancy |
| Namespace controller | Resource scope, cleanup, finalizers, and deletion stuck in Terminating |
| ResourceQuota | Aggregate resource/object limits, admission behavior, and capacity governance |
| Garbage Collector | Owner references, cascading deletion, propagation policy, and orphan prevention |
| ReplicaSet | Replica-count reconciliation, label selection, and why Deployments are preferred |
| Deployment | Rolling updates, readiness, revision history, rollback, and state migration concerns |
| StatefulSet | Stable identity, ordered operations, storage association, quorum, and recovery semantics |
| DaemonSet | Per-node coverage, selectors, tolerations, agent resources, and node lifecycle |
| Job | Finite work, completion tracking, retries, parallelism, and cleanup policy |
| CronJob | Scheduling, missed runs, concurrency, deadlines, history, and idempotency |
| ReplicationController | Legacy replica management, selector limitations, and migration to Deployments |
| HorizontalPodAutoscaler | Metric-driven replica scaling, requests, startup behavior, and traffic distribution |
| VerticalPodAutoscaler | Resource recommendations, evictions, update modes, and interaction with HPA |
| Pod Disruption Budget | Voluntary eviction limits, maintenance progress, replica count, and capacity |

## Before you start

41 self-contained demos. Each has: SETUP, YAML (if any), STEPS, WHAT YOU SHOULD SEE, CLEANUP.

BEFORE YOU START
----------------------------------------------------------------
1. Use a disposable local cluster. Some demos delete Pods, stop a kubelet, or drain a node.
2. These demos use kind with Docker as the host provider. Linux uses Docker Engine;
   macOS uses Docker Desktop. Inside every kind node, kubelet talks to containerd
   through CRI. The runtime should show as containerd://...
3. From the repository root, create the recommended multi-node cluster:
     ./scripts/kind-up.sh
   This uses the checked-in kind-multinode.yaml (1 control-plane + 2 workers),
   maps Ingress to localhost:8080/8443, and waits for every node to become Ready.
   If the cluster already exists without these port mappings, recreate it before
   running demo 18.
4. Every demo uses its own namespace (zine-demo, or demo-ns / other-ns where stated)
   and cleans up after itself, so demos can be run in ANY order.
5. Save each YAML block to the file named above it, then run the commands.
6. Add-ons some demos need first:
     - 18 Ingress: ingress-nginx's kind provider manifest
     - 19 NetworkPolicy: a CNI that enforces policy (Calico or Cilium; kindnet does not)
     - 39 HPA: metrics-server
     - 40 VPA: the VPA add-on
     - 41 PDB and 28 Node controller: two or more worker nodes
7. Commands marked 'run on the node' enter a kind node through the host Docker provider:
     docker exec -it zine-control-plane bash
     docker exec -it zine-worker bash
   Kind node names for this cluster are zine-control-plane, zine-worker,
   and zine-worker2. Run crictl and host-network checks inside those containers,
   not on the macOS host.
8. Text after # on a command line is an explanation, not part of the command.

LIVE OBSERVATION
----------------------------------------------------------------
For a practical, realtime run, keep a second terminal open while executing a demo:
     kubectl get pods -A -o wide -w
     kubectl get events -A --sort-by=.lastTimestamp -w
     kubectl get nodes -w
Use Ctrl+C to stop a watch. The STEPS below favor wait/watch commands so
rollouts, scheduling, replacement Pods, endpoints, and autoscaling are visible
as they converge instead of being checked only after the fact.

Quick reference - demos that need something extra:
  add-on:      18, 19, 39, 40
  2+ workers:  28, 41 (and 2, 35 read best with them)
  on the node: 4, 8, 9, 10, 11, 28

## 1. The Cluster (Why Kubernetes?)

**Part 1 — Technical Discussion:** Kubernetes is a declarative control system for managing compute, networking, and storage across a group of machines. You submit desired state through the API, and the control plane schedules Pods, reconciles drift, and reports status while Nodes execute the work. This removes manual placement from the normal workflow, but the cluster itself still requires capacity planning, security, upgrades, and observability.

![The Cluster (Why Kubernetes?) technical illustration](generated/kubernetes-apartment-complex/01-technical.png)

**Technical perspective:** Kubernetes provides a declarative control plane, scheduling, self-healing, service discovery, and rollout automation across many machines. Compared with standalone VMs, it removes the need to place and repair each workload manually, improves utilization through bin-packing, and makes the desired state reproducible. The trade-off is additional platform complexity: the cluster itself needs lifecycle management, observability, security, and capacity planning.


### Component architecture flow

<iframe src="diagrams/topic-01.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-01.html](diagrams/topic-01.html).

**Part 2 — Analogy / Zine:** Managing standalone buildings is exhausting; tying them into one complex lets you manage them as a single entity.

![The Cluster (Why Kubernetes?) zine illustration](generated/kubernetes-apartment-complex/01-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Why Kubernetes? Because managing buildings one at a time is exhausting."
* (Under Left): "Standalone buildings, standalone managers, standalone problems."
* (Under Right): "Tie them into one complex and manage it as a single entity. Stop SSHing into individual machines — talk to the cluster, and it decides where your workload goes."

**Further reading**

- [Kubernetes concepts](https://kubernetes.io/docs/concepts/)

### Demo — The Cluster (Why Kubernetes?)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl cluster-info
  2. kubectl get nodes -o wide

WHAT YOU SHOULD SEE
  cluster-info prints the control plane and CoreDNS URLs. get nodes lists every node with ROLES, STATUS, INTERNAL-IP.

CLEANUP
  (nothing to clean up)

NOTE
  One command shows the whole 'complex' instead of logging into each machine.
</pre></div>


### Knowledge Check — Quiz

**Q1: When a worker node running a Pod loses network connectivity to the control plane, what happens to the containers running on that node immediately?**

- [ ] A) The local container runtime immediately terminates all running containers.
- [ ] B) The containers continue running locally, but the control plane cannot observe or update their status.
- [ ] C) The API server sends an SSH command to reboot the worker machine.
- [ ] D) etcd immediately purges the Pod object from cluster state.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The containers continue running locally, but the control plane cannot observe or update their status.

**Explanation:** The kubelet and local container runtime continue executing workloads based on local state even during control plane disconnection, though the control plane will mark the node NotReady after the lease timeout.

</details>

**Q2: Which core architectural principle fundamentally distinguishes Kubernetes from traditional imperative VM deployment scripts?**

- [ ] A) Synchronous execution of linear shell scripts on remote hosts.
- [ ] B) Declarative desired state reconciliation via continuous control loops.
- [ ] C) Direct peer-to-peer communication between etcd and container runtimes.
- [ ] D) Requiring physical operator access to machines for all changes.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Declarative desired state reconciliation via continuous control loops.

**Explanation:** Kubernetes operates on declarative intent: you define the desired state in the API server, and independent controllers continuously reconcile actual state to match it.

</details>

## 2. Control Plane vs. Worker Nodes

**Part 1 — Technical Discussion:** The control plane exposes the API, stores cluster state, schedules Pods, and runs controllers; worker Nodes provide the kubelet, container runtime, and networking needed to execute them. A worker failure can trigger replacement or rescheduling when replicas and capacity are available, while an isolated control-plane failure may leave existing processes running but stops reliable changes and new placement decisions. High availability therefore requires redundant control-plane components and workloads spread across failure domains.

![Control Plane vs. Worker Nodes technical illustration](generated/kubernetes-apartment-complex/02-technical.png)

**Technical perspective:** The separation of control plane and workers creates a clear failure boundary. Workers execute Pods, while the control plane stores intent and coordinates scheduling and reconciliation. This lets workloads continue during some control-plane interruptions, while worker failure can be handled through rescheduling when replicas and capacity are available. High availability requires multiple control-plane instances and appropriately distributed workers.


### Component architecture flow

<iframe src="diagrams/topic-02.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-02.html](diagrams/topic-02.html).

**Part 2 — Analogy / Zine:** The office thinks (Leasing Office); the buildings do the actual physical work (Worker Nodes).

![Control Plane vs. Worker Nodes zine illustration](generated/kubernetes-apartment-complex/02-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Two halves of the complex: the office that thinks, and the buildings that work."
* (Under Left): "The Leasing Office thinks — planning, deciding, recording. This is the Control Plane."
* (Under Right): "If a building crashes, workloads shift elsewhere. If the office crashes, buildings keep running — but nothing can be changed until the office is back."

**Further reading**

- [Cluster architecture](https://kubernetes.io/docs/concepts/architecture/)

### Demo — Control Plane vs. Worker Nodes

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get nodes --show-labels | grep -E 'control-plane|NAME'
  2. kubectl get pods -n kube-system -o wide

WHAT YOU SHOULD SEE
  The control-plane node is labelled node-role.kubernetes.io/control-plane. kube-system shows the api-server, etcd, scheduler and controller-manager Pods on that node.

CLEANUP
  (nothing to clean up)

NOTE
  This guide assumes the three-node kind cluster above, so the control plane and workers are separate Docker containers.
</pre></div>


### Knowledge Check — Quiz

**Q1: If all control plane nodes become temporarily unreachable in a cluster, what is the immediate effect on already-running workloads on healthy worker nodes?**

- [ ] A) All pods are immediately terminated by their local kubelets.
- [ ] B) Worker nodes stop routing network traffic between running pods.
- [ ] C) Existing pods and data plane networking continue running, but no new pods can be scheduled or state updated.
- [ ] D) The cluster automatically falls back to single-node Docker engines.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** C) Existing pods and data plane networking continue running, but no new pods can be scheduled or state updated.

**Explanation:** Data plane execution is decoupled from the control plane; existing pods and network routes remain functional, but scheduling, scaling, and API changes are blocked.

</details>

**Q2: What is the primary role of worker nodes relative to the control plane?**

- [ ] A) Managing etcd quorum and evaluating RBAC authorization.
- [ ] B) Executing pod sandboxes, container processes, and local network/storage enforcement via kubelet and runtime.
- [ ] C) Authorizing TLS certificates for external client requests.
- [ ] D) Directly editing cluster manifests inside etcd storage.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Executing pod sandboxes, container processes, and local network/storage enforcement via kubelet and runtime.

**Explanation:** Worker nodes represent the execution layer ('muscle') managed by kubelet, containerd, and kube-proxy, while the control plane ('brain') makes decisions and stores intent.

</details>

## 3. kube-apiserver

**Part 1 — Technical Discussion:** kube-apiserver is the authenticated and validated HTTP API boundary for Kubernetes. kubectl, controllers, the scheduler, admission webhooks, and external automation all use it to read objects, submit desired state, and watch changes. It performs authentication, authorization, admission, conversion, and concurrency handling, and is the only control-plane component that directly reads or writes etcd.

![kube-apiserver technical illustration](generated/kubernetes-apartment-complex/03-technical.png)

**Technical perspective:** The API server is the authenticated, authorized, validated concurrency boundary for cluster state. Clients submit declarative objects through the Kubernetes API; admission, versioning, validation, and watches provide a consistent interface for controllers and tools. Keeping etcd behind the API server centralizes policy and prevents components from making ungoverned direct writes.


### Component architecture flow

<iframe src="diagrams/topic-03.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-03.html](diagrams/topic-03.html).

**Part 2 — Analogy / Zine:** Every request must go through this one desk; nobody bypasses it.

![kube-apiserver zine illustration](generated/kubernetes-apartment-complex/03-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kube-apiserver — The Front Desk"
* (Caption): "Every request must go through this one desk; nobody bypasses it. It's the only component that talks to the records room, and it's what your kubectl commands hit."

**Further reading**

- [API server reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [Kubernetes API concepts](https://kubernetes.io/docs/concepts/overview/kubernetes-api/)

### Demo — kube-apiserver

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get --raw /api/v1 | head -c 300
  2. kubectl proxy --port=8080 &
  3. sleep 2
  4. curl -s http://localhost:8080/api/v1/namespaces | head -c 300

WHAT YOU SHOULD SEE
  Both calls return raw JSON from the API server. kubectl is just an HTTP client.

CLEANUP
  kill %1   # stop the background kubectl proxy

NOTE
  Bypass kubectl and hit the 'front desk' directly with curl.
</pre></div>


### Knowledge Check — Quiz

**Q1: Which of the following is true regarding how cluster components communicate with etcd in standard Kubernetes?**

- [ ] A) Both the scheduler and kubelet write directly to etcd over gRPC.
- [ ] B) Only the kube-apiserver communicates directly with etcd; all other components interact via the API server.
- [ ] C) etcd pushes event notifications directly to worker node kube-proxies.
- [ ] D) Admission webhooks persist rejected objects directly in etcd for audit logs.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Only the kube-apiserver communicates directly with etcd; all other components interact via the API server.

**Explanation:** kube-apiserver is the sole gateway and concurrency boundary for etcd, ensuring all reads and writes pass through authentication, authorization, and validation.

</details>

**Q2: In what order does the kube-apiserver process an incoming resource creation request?**

- [ ] A) Mutating Admission -> Authentication -> Validation -> etcd
- [ ] B) Authentication -> Authorization -> Mutating Admission -> Schema/Validating Admission -> etcd
- [ ] C) Authorization -> Schema Validation -> Authentication -> etcd
- [ ] D) etcd Write -> Mutating Admission -> Authorization

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Authentication -> Authorization -> Mutating Admission -> Schema/Validating Admission -> etcd

**Explanation:** A request must first be authenticated (who are you?), then authorized (can you do this?), then mutated (defaults/sidecars injected), then validated (schema & policy rules), before being committed to etcd.

</details>

## 4. etcd

**Part 1 — Technical Discussion:** etcd is a strongly consistent distributed key-value store that holds Kubernetes API state, including specifications, metadata, and status needed by controllers. The API server uses it as the authoritative record, so quorum, disk latency, encryption, access control, snapshots, and restore testing directly affect control-plane reliability. Existing containers may continue briefly during an etcd outage, but new decisions and durable state changes cannot safely converge.

![etcd technical illustration](generated/kubernetes-apartment-complex/04-technical.png)

**Technical perspective:** etcd stores Kubernetes state as a strongly consistent key-value database. Because the API server reconstructs the cluster’s desired and observed state from it, backups, quorum, encryption, latency, and restore testing are critical operational concerns. An etcd outage does not necessarily stop already-running containers immediately, but it prevents reliable control-plane progress and changes.


### Component architecture flow

<iframe src="diagrams/topic-04.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-04.html](diagrams/topic-04.html).

**Part 2 — Analogy / Zine:** Wall-to-wall filing cabinets holding the only copy of the complex's rules and state that actually counts.

![etcd zine illustration](generated/kubernetes-apartment-complex/04-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "etcd — The Locked Records Room"
* (Caption): "A highly available key-value store; if it corrupts, your cluster loses its memory."

**Further reading**

- [etcd: why etcd](https://etcd.io/docs/v3.5/learning/why/)
- [Kubernetes etcd guidance](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)

### Demo — etcd

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  ETCD_POD=$(kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}')
  echo $ETCD_POD

STEPS
  1. kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key get /registry/pods --prefix --keys-only | head -20

WHAT YOU SHOULD SEE
  A list of keys such as /registry/pods/kube-system/etcd-&lt;node&gt;. These are the 'filing cabinets' behind the API server.

CLEANUP
  (nothing to clean up)

NOTE
  Works on the kubeadm-style control plane used by kind. Managed clusters (EKS, GKE, AKS) hide etcd, so this will not work there. Do not use -it with a piped command.
</pre></div>


### Knowledge Check — Quiz

**Q1: In a 3-node etcd cluster, how many node failures can the cluster tolerate while maintaining write operations?**

- [ ] A) 2 nodes
- [ ] B) 1 node
- [ ] C) 0 nodes
- [ ] D) 3 nodes

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) 1 node

**Explanation:** etcd requires a strict majority quorum ((N/2) + 1). For N=3, quorum is 2, meaning only 1 node failure is tolerated before writes are blocked.

</details>

**Q2: Why is low-latency disk I/O (such as NVMe/SSD) critical for etcd performance in production?**

- [ ] A) etcd compiles Go binaries on every write transaction.
- [ ] B) Raft consensus requires sequential fsync writes to the write-ahead log (WAL) before acknowledging mutations.
- [ ] C) etcd stores container image layers on disk.
- [ ] D) kube-proxy streams raw packet capture logs into etcd.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Raft consensus requires sequential fsync writes to the write-ahead log (WAL) before acknowledging mutations.

**Explanation:** Every Raft proposal requires appending to disk and fsyncing to the WAL; high disk write latency directly stalls Raft consensus heartbeats and API server writes.

</details>

## 5. kube-scheduler

**Part 1 — Technical Discussion:** kube-scheduler assigns an unscheduled Pod to a feasible Node; it does not start the container itself. It filters Nodes using resource requests, taints, tolerations, affinity, topology, volumes, and other constraints, then scores the remaining candidates and writes a binding. The kubelet notices that assignment and performs the actual launch.

![kube-scheduler technical illustration](generated/kubernetes-apartment-complex/05-technical.png)

**Technical perspective:** The scheduler separates placement decision-making from execution. It filters nodes that violate resource, taint, affinity, topology, or policy constraints, then scores feasible nodes and binds the Pod to the selected one. This lets operators express placement intent without hard-coding a server, while requests and limits help the scheduler make capacity-aware decisions.


### Component architecture flow

<iframe src="diagrams/topic-05.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-05.html](diagrams/topic-05.html).

**Part 2 — Analogy / Zine:** Checks building capacity and rules, then pins new tenants to the best-fitting building.

![kube-scheduler zine illustration](generated/kubernetes-apartment-complex/05-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kube-scheduler — The Unit Assigner"
* (Caption): "Assigns new Pods to Nodes based on CPU/RAM requirements and affinity rules."

**Further reading**

- [Kubernetes scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Scheduling framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)

### Demo — kube-scheduler

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl run demo-pod --image=nginx -n zine-demo
  2. kubectl wait --for=condition=Ready pod/demo-pod -n zine-demo --timeout=60s
  3. kubectl get pod demo-pod -n zine-demo -o wide
  4. kubectl describe pod demo-pod -n zine-demo | grep -A6 Events

WHAT YOU SHOULD SEE
  Events shows 'Scheduled ... Successfully assigned zine-demo/demo-pod to &lt;node&gt;'. The NODE column matches.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The Scheduled event is the exact moment the scheduler picked a node.
</pre></div>


### Knowledge Check — Quiz

**Q1: During the scheduling cycle for an unscheduled Pod, what occurs if all candidate nodes are eliminated during the Filtering (predicates) phase?**

- [ ] A) The Pod is scheduled on the control-plane node automatically.
- [ ] B) The Pod remains in Pending status with a PodScheduled condition of False and reason FailedScheduling.
- [ ] C) The kube-scheduler deletes the Pod from etcd.
- [ ] D) The Pod is assigned to a random worker node regardless of constraints.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The Pod remains in Pending status with a PodScheduled condition of False and reason FailedScheduling.

**Explanation:** If no node passes filtering (e.g. due to insufficient CPU/memory or untolerated taints), the pod stays Pending until cluster capacity or constraints change.

</details>

**Q2: How does the scheduler communicate its placement decision to the assigned worker node?**

- [ ] A) The scheduler connects via SSH directly to the worker node.
- [ ] B) The scheduler creates a Binding subresource via the API server that sets pod.spec.nodeName.
- [ ] C) The scheduler pushes a gRPC message directly to containerd on the worker node.
- [ ] D) The scheduler writes the node IP into CoreDNS.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The scheduler creates a Binding subresource via the API server that sets pod.spec.nodeName.

**Explanation:** The scheduler does not contact nodes directly; it creates a Binding object via the API server, setting spec.nodeName. The target node's kubelet watches for pods bound to itself.

</details>

## 6. kube-controller-manager

**Part 1 — Technical Discussion:** kube-controller-manager hosts independent reconciliation loops for objects such as Nodes, endpoints, namespaces, and replication resources. Each controller watches API events, compares desired and observed state, and makes idempotent API changes until the difference converges. This eventual-consistency model enables self-healing, but bad probes, ownership, or resource settings can cause repeated ineffective repairs.

![kube-controller-manager technical illustration](generated/kubernetes-apartment-complex/06-technical.png)

**Technical perspective:** Controllers implement Kubernetes reconciliation: they observe API objects and cluster state, compute the difference, and issue idempotent changes until the difference disappears. This is why deleting a Pod managed by a Deployment is temporary. The model favors eventual convergence and automation, but requires correct ownership, probes, resource settings, and observability to avoid repeatedly reconciling a broken design.


### Component architecture flow

<iframe src="diagrams/topic-06.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-06.html](diagrams/topic-06.html).

**Part 2 — Analogy / Zine:** Clipboard inspectors walking endless loops to ensure reality matches the promised plan, fixing discrepancies automatically.

![kube-controller-manager zine illustration](generated/kubernetes-apartment-complex/06-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kube-controller-manager — The Looping Inspectors"
* (Caption): "Background control loops that detect crashed Pods and spin up replacements to match your deployment YAML."

**Further reading**

- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)

### Demo — kube-controller-manager

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo

STEPS
  1. kubectl get pods -l app=demo -n zine-demo
  2. kubectl delete pod $(kubectl get pods -l app=demo -n zine-demo -o name | head -1) -n zine-demo
  3. kubectl get pods -l app=demo -n zine-demo -w   # Ctrl+C after a new Pod is Running

WHAT YOU SHOULD SEE
  You deleted one Pod and a replacement appears within seconds. The count returns to 3.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The control loop noticed the gap and closed it with no command from you.
</pre></div>


### Knowledge Check — Quiz

**Q1: What design principle enables Kubernetes controllers to recover gracefully from network partitions or restarts without missing state changes?**

- [ ] A) Edge-triggered interrupts stored in persistent message queues.
- [ ] B) Level-triggered reconciliation loops comparing desired state from the API server with observed cluster state.
- [ ] C) Synchronous RPC heartbeats between all worker nodes.
- [ ] D) Hardcoded sleep timers between sequential shell commands.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Level-triggered reconciliation loops comparing desired state from the API server with observed cluster state.

**Explanation:** Level-triggered design means controllers reconcile based on current observed state rather than relying on having received every intermediate edge event, making them self-healing and idempotent.

</details>

**Q2: If a user manually deletes a Pod managed by a Deployment (via its ReplicaSet), what will the ReplicaSet controller do?**

- [ ] A) It updates the Deployment replicas count to N - 1.
- [ ] B) It marks the Deployment as Failed.
- [ ] C) It observes that current replicas < desired replicas and creates a replacement Pod via the API server.
- [ ] D) It recreates the entire cluster worker node.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** C) It observes that current replicas < desired replicas and creates a replacement Pod via the API server.

**Explanation:** The ReplicaSet controller continuously compares observed replicas matching its selector against spec.replicas. If one is missing, it immediately issues an API request to create a new one.

</details>

## 7. cloud-controller-manager

**Part 1 — Technical Discussion:** cloud-controller-manager isolates provider-specific integrations from the Kubernetes core. Its controllers translate Services, Nodes, routes, and persistent volumes into cloud API operations, then write the resulting addresses, identities, and status back to Kubernetes. Provisioning depends on cloud credentials, quotas, API latency, regional topology, and provider-specific behavior.

![cloud-controller-manager technical illustration](generated/kubernetes-apartment-complex/07-technical.png)

**Technical perspective:** The cloud controller manager keeps provider-specific integration outside the Kubernetes core. It translates Services, Nodes, routes, and cloud volumes into provider API operations and reports their status back through Kubernetes objects. This portability is valuable across clouds, but behavior depends on provider identity, permissions, quotas, latency, and the provider’s implementation of the integration.


### Component architecture flow

<iframe src="diagrams/topic-07.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-07.html](diagrams/topic-07.html).

**Part 2 — Analogy / Zine:** Signs paperwork to connect external utilities like rented parking gates.

![cloud-controller-manager zine illustration](generated/kubernetes-apartment-complex/07-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "cloud-controller-manager — Outside Vendor Liaison"
* (Caption): "Translates Kubernetes requests into AWS/GCP/Azure API calls for things like cloud LoadBalancers."

**Further reading**

- [Cloud controller manager](https://kubernetes.io/docs/concepts/architecture/cloud-controller/)

### Demo — cloud-controller-manager

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo

STEPS
  1. kubectl expose deployment demo --type=LoadBalancer --port=80 --target-port=80 -n zine-demo
  2. kubectl get svc demo -n zine-demo -w   # Ctrl+C when done

WHAT YOU SHOULD SEE
  On a cloud cluster EXTERNAL-IP moves from &lt;pending&gt; to a real IP. On kind it stays &lt;pending&gt; unless a cloud provider integration is installed.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Kind has no cloud provider by default, so &lt;pending&gt; is the expected result. To provision a real LoadBalancer on kind, install and run cloud-provider-kind separately; for a simple local HTTP test, use a NodePort instead.
</pre></div>


### Knowledge Check — Quiz

**Q1: What was the primary motivation for introducing the cloud-controller-manager (CCM) as a separate binary from kube-controller-manager?**

- [ ] A) To make Kubernetes compatible with Windows worker nodes.
- [ ] B) To extract vendor-specific cloud provider code out-of-tree so cloud providers can update independently of Kubernetes core releases.
- [ ] C) To replace etcd with cloud databases like AWS DynamoDB.
- [ ] D) To eliminate the need for kubelet on cloud virtual machines.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) To extract vendor-specific cloud provider code out-of-tree so cloud providers can update independently of Kubernetes core releases.

**Explanation:** Out-of-tree cloud controllers decouple cloud provider SDKs and release cycles from the core Kubernetes repository, removing proprietary drivers from the core codebase.

</details>

**Q2: Which controller within cloud-controller-manager is responsible for provisioning cloud load balancers when a Service of type LoadBalancer is created?**

- [ ] A) Node lifecycle controller
- [ ] B) Service controller
- [ ] C) Route controller
- [ ] D) PersistentVolume label controller

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Service controller

**Explanation:** The cloud Service controller watches for Services of type: LoadBalancer and calls the cloud provider's API to provision and wire up external load balancers.

</details>

## 8. Static Pods

**Part 1 — Technical Discussion:** A Static Pod is defined by a manifest on a Node’s filesystem and is launched directly by that Node’s kubelet. The kubelet mirrors it into the API as a read-only-style mirror Pod, but the API server is not the source of its desired state. This bootstrap path can start control-plane components before the API is available, while making distribution, updates, and drift node-local concerns.

![Static Pods technical illustration](generated/kubernetes-apartment-complex/08-technical.png)

**Technical perspective:** Static Pods are bootstrapped locally by the kubelet from files on a node, so they can start before the API server is available. This is useful for kubeadm-style control-plane bootstrapping, but local manifests are node-specific and are not ordinary API-managed workloads. Operators must manage file distribution, updates, and drift carefully.


### Component architecture flow

<iframe src="diagrams/topic-08.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-08.html](diagrams/topic-08.html).

**Part 2 — Analogy / Zine:** A local blueprint used to build the front desk before a front desk even exists.

![Static Pods zine illustration](generated/kubernetes-apartment-complex/08-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Static Pods — The Bootstrapping Crew"
* (Caption): "Pods managed directly by a local kubelet to run control plane components without relying on the API server."

**Further reading**

- [Static Pods](https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/)

### Demo — Static Pods

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. docker exec -it zine-control-plane bash
  2. ls /etc/kubernetes/manifests/
  3. exit
  4. kubectl get pods -n kube-system -o wide | grep -E 'apiserver|etcd|scheduler'

WHAT YOU SHOULD SEE
  The manifests folder lists kube-apiserver.yaml, etcd.yaml, kube-scheduler.yaml, kube-controller-manager.yaml. The same Pods appear in kube-system with the node name appended.

CLEANUP
  (nothing to clean up)

NOTE
  The kubelet reads those files directly, with no API server round-trip. Run the ls on the control-plane node itself, not your laptop.
</pre></div>


### Knowledge Check — Quiz

**Q1: Who manages the lifecycle of a Static Pod running on a worker node?**

- [ ] A) The kube-scheduler running on the control plane.
- [ ] B) The local kubelet on that specific node watching a local file directory or HTTP endpoint directly.
- [ ] C) The Deployment controller.
- [ ] D) CoreDNS.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The local kubelet on that specific node watching a local file directory or HTTP endpoint directly.

**Explanation:** Static Pods are configured locally on a node (typically in /etc/kubernetes/manifests) and supervised directly by the kubelet without scheduler involvement.

</details>

**Q2: What is a 'Mirror Pod' in the context of Static Pods?**

- [ ] A) An identical backup container running on a secondary worker node.
- [ ] B) A read-only Pod representation created on the API server by kubelet so the Static Pod is visible via kubectl get pods.
- [ ] C) A sidecar container injected into every pod for logging.
- [ ] D) A container that replicates network packets for auditing.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) A read-only Pod representation created on the API server by kubelet so the Static Pod is visible via kubectl get pods.

**Explanation:** The kubelet creates a Mirror Pod on the API server matching the static pod spec so cluster operators can observe its status using standard Kubernetes API tools.

</details>

## 9. kubelet

**Part 1 — Technical Discussion:** kubelet is the per-Node agent that reconciles assigned PodSpecs into running sandboxes and containers. It coordinates with the CRI runtime, mounts volumes, executes startup/readiness/liveness probes, applies restart policy, and reports conditions and container status to the API server. It can enforce local state, but it does not schedule Pods or replace the control plane’s higher-level controllers.

![kubelet technical illustration](generated/kubernetes-apartment-complex/09-technical.png)

**Technical perspective:** The kubelet is the node-level agent that turns a PodSpec into running containers. It coordinates with the runtime, mounts volumes, executes probes, reports status, and applies lifecycle policies. Kubernetes can declare the desired workload centrally, while the kubelet provides the local enforcement needed to keep that workload running on its assigned node.


### Component architecture flow

<iframe src="diagrams/topic-09.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-09.html](diagrams/topic-09.html).

**Part 2 — Analogy / Zine:** Receives the work order from the office and does headcounts to ensure assigned tenants are present and healthy.

![kubelet zine illustration](generated/kubernetes-apartment-complex/09-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kubelet — The Superintendent"
* (Caption): "The primary node agent that ensures containers are actually running on that specific server."

**Further reading**

- [Nodes and kubelet](https://kubernetes.io/docs/concepts/architecture/nodes/)

### Demo — kubelet

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl run demo-pod --image=nginx -n zine-demo
  kubectl wait --for=condition=Ready pod/demo-pod -n zine-demo --timeout=60s

STEPS
  1. kubectl get pod demo-pod -n zine-demo -o jsonpath='{.status.conditions}'
  2. docker exec zine-worker bash -lc "ps -ef | grep '[k]ubelet'"

WHAT YOU SHOULD SEE
  Conditions list Initialized, Ready, ContainersReady, PodScheduled, all 'True'. The process listing shows kubelet running inside the kind worker container.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The Pod's conditions are reported by the kubelet on that node.
</pre></div>


### Knowledge Check — Quiz

**Q1: If a container's liveness probe fails consecutively beyond failureThreshold, what action does the kubelet take?**

- [ ] A) The kubelet removes the Pod from Service endpoints without restarting the container.
- [ ] B) The kubelet terminates the container and restarts it according to the Pod's restartPolicy.
- [ ] C) The kubelet evicts the Pod to a different worker node.
- [ ] D) The kubelet drains the entire node.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The kubelet terminates the container and restarts it according to the Pod's restartPolicy.

**Explanation:** Liveness probe failures indicate an unhealthy process that cannot recover on its own; kubelet kills the container and restarts it according to restartPolicy.

</details>

**Q2: How does the kubelet authenticate itself when communicating with the kube-apiserver?**

- [ ] A) Using plain HTTP with no authentication.
- [ ] B) Using mutual TLS (mTLS) with client certificates typically issued in the system:nodes group.
- [ ] C) Using the host operating system's root password.
- [ ] D) Through SSH key exchange on port 22.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Using mutual TLS (mTLS) with client certificates typically issued in the system:nodes group.

**Explanation:** Kubelets use client X.509 certificates belonging to the system:nodes group, authorized by the Node authorization mode on the API server.

</details>

## 10. kube-proxy

**Part 1 — Technical Discussion:** kube-proxy implements the node-local datapath for Service virtual IPs. It watches Services and EndpointSlices, then programs packet rules—commonly iptables or IPVS—so traffic is translated and load-balanced toward eligible Pod addresses. The Service abstraction remains stable even as Pods change; some CNI or eBPF implementations can provide an equivalent datapath without the traditional kube-proxy process.

![kube-proxy technical illustration](generated/kubernetes-apartment-complex/10-technical.png)

**Technical perspective:** kube-proxy implements the Service data path on nodes by programming packet-forwarding rules, commonly with iptables or IPVS depending on configuration. The Service gives clients a stable virtual destination while backend Pod IPs change. Modern proxy replacements and some CNI implementations can provide equivalent behavior, so kube-proxy is an implementation component rather than the Service abstraction itself.


### Component architecture flow

<iframe src="diagrams/topic-10.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-10.html](diagrams/topic-10.html).

**Part 2 — Analogy / Zine:** Updates a directory on the fly so visitors find the right unit, even as tenants swap out.

![kube-proxy zine illustration](generated/kubernetes-apartment-complex/10-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kube-proxy — The Lobby Directory"
* (Caption): "Maintains network routing rules (iptables/IPVS) on the host to route traffic to active Pod IPs."

**Further reading**

- [kube-proxy](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-proxy/)
- [Service proxying](https://kubernetes.io/docs/concepts/services-networking/service-traffic-policies/)

### Demo — kube-proxy

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 -n zine-demo

STEPS
  1. kubectl get endpoints demo -n zine-demo
  2. docker exec zine-worker bash -lc "iptables -t nat -L KUBE-SERVICES -n | grep zine-demo"

WHAT YOU SHOULD SEE
  Endpoints lists 3 Pod IPs. The iptables output has a rule for the demo Service on port 80.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  If your cluster runs kube-proxy in IPVS mode, use 'sudo ipvsadm -Ln' instead. The Endpoints list and the rules line up.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the key performance advantage of kube-proxy running in ipvs mode compared to standard iptables mode in large clusters?**

- [ ] A) IPVS compresses network packets using gzip.
- [ ] B) IPVS uses hash tables with O(1) lookup complexity, whereas iptables uses sequential rule chains with O(N) evaluation latency.
- [ ] C) IPVS replaces TCP with UDP for faster packet transmission.
- [ ] D) IPVS eliminates the need for container network interfaces.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) IPVS uses hash tables with O(1) lookup complexity, whereas iptables uses sequential rule chains with O(N) evaluation latency.

**Explanation:** Sequential iptables rule chains incur linear O(N) processing overhead as rule counts grow to tens of thousands; IPVS uses ipset hash tables providing near-constant O(1) routing latency.

</details>

**Q2: When an application inside a Pod sends traffic to a ClusterIP:port, where is the destination IP translated to an actual backend Pod IP?**

- [ ] A) By the CoreDNS pod using DNS round-robin.
- [ ] B) In the Linux kernel on the sending node via iptables/IPVS NAT rules maintained by kube-proxy.
- [ ] C) In the cloud provider's external hardware gateway.
- [ ] D) Inside the application container's glibc runtime.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) In the Linux kernel on the sending node via iptables/IPVS NAT rules maintained by kube-proxy.

**Explanation:** The virtual ClusterIP does not exist on any physical interface; packet destination is rewritten (DNAT) directly inside the node's kernel by the netfilter rules programmed by kube-proxy.

</details>

## 11. Container Runtime & CRI

**Part 1 — Technical Discussion:** The container runtime pulls images, creates Pod sandboxes, starts processes, applies isolation, and reports their status. kubelet reaches it through the Container Runtime Interface, a standard gRPC contract that hides runtime-specific APIs and allows implementations such as containerd or CRI-O. Runtime configuration still affects cgroups, filesystem behavior, logging, image security, resource accounting, and node performance.

![Container Runtime & CRI technical illustration](generated/kubernetes-apartment-complex/11-technical.png)

**Technical perspective:** The Container Runtime Interface lets kubelet use a standard gRPC contract instead of depending on one runtime’s private API. containerd and CRI-O pull images, create sandboxes, start processes, and report container status. This modularity makes runtime choice possible, while image compatibility, cgroup configuration, logging, security isolation, and runtime performance still affect node behavior.


### Component architecture flow

<iframe src="diagrams/topic-11.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-11.html](diagrams/topic-11.html).

**Part 2 — Analogy / Zine:** The physical crew carrying boxes, operating under a standard universal contract.

![Container Runtime & CRI zine illustration](generated/kubernetes-apartment-complex/11-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Container Runtime & CRI — The Moving Crew & Contract"
* (Caption): "containerd or CRI-O pulls the image and runs the process; CRI ensures Kubernetes can swap runtimes seamlessly."

**Further reading**

- [Container runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
- [CRI specification](https://github.com/kubernetes/cri-api)

### Demo — Container Runtime & CRI

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  docker ps --filter name=zine-

STEPS
  1. kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.containerRuntimeVersion}'; echo
  2. docker exec zine-worker crictl ps

WHAT YOU SHOULD SEE
  First command prints something like containerd://1.7.x. crictl ps lists running containers straight from the runtime.

CLEANUP
  (nothing to clean up)

NOTE
  crictl bypasses Kubernetes and talks to the runtime through CRI. Run it on the node, not your laptop.
</pre></div>


### Knowledge Check — Quiz

**Q1: What role does the Container Runtime Interface (CRI) play in the Kubernetes node architecture?**

- [ ] A) It compiles application source code into container images on the worker node.
- [ ] B) It is a gRPC interface that standardizes how kubelet communicates with pluggable container runtimes like containerd or CRI-O.
- [ ] C) It encrypts network traffic between pods across nodes.
- [ ] D) It manages persistent disk volume attachments in cloud storage.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It is a gRPC interface that standardizes how kubelet communicates with pluggable container runtimes like containerd or CRI-O.

**Explanation:** CRI defines the gRPC protobuf specification for runtime and image services, allowing Kubernetes to support any compliant runtime without vendor lock-in.

</details>

**Q2: Why does a Pod sandbox include a 'pause' (or infra) container?**

- [ ] A) To pause container execution when the node is low on memory.
- [ ] B) To hold the Linux network, IPC, and mount namespaces that all containers in the Pod share throughout its lifecycle.
- [ ] C) To provide a graphical terminal interface for container debugging.
- [ ] D) To cache container image layers locally.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) To hold the Linux network, IPC, and mount namespaces that all containers in the Pod share throughout its lifecycle.

**Explanation:** The pause container holds the shared namespaces (particularly the network namespace) so that if an application container restarts, the Pod IP and network interface remain intact.

</details>

## 12. Sidecar Containers

**Part 1 — Technical Discussion:** A sidecar is a supporting container in the same Pod as an application container. Containers in one Pod share a network namespace and can share volumes, enabling local proxies, log shippers, certificate agents, or telemetry adapters to cooperate over localhost or files. The trade-off is coupled scheduling and failure behavior: resource requests, readiness, shutdown order, and restart semantics must cover the whole Pod.

![Sidecar Containers technical illustration](generated/kubernetes-apartment-complex/12-technical.png)

**Technical perspective:** A sidecar shares a Pod’s network namespace and can share volumes with the primary container, making close cooperation possible without building every concern into the application image. Sidecars are useful for proxies, log shipping, certificate renewal, and telemetry, but they increase resource consumption and failure coupling: the Pod’s lifecycle and readiness must account for the supporting container.


### Component architecture flow

<iframe src="diagrams/topic-12.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-12.html](diagrams/topic-12.html).

**Part 2 — Analogy / Zine:** Sits in the same unit handling side tasks, like shipping out logs, without bothering the main tenant.

![Sidecar Containers zine illustration](generated/kubernetes-apartment-complex/12-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Sidecar Containers — The Roommate"
* (Caption): "Secondary containers in a Pod that share network/storage to handle logging, proxies (like Istio), or metrics."

**Further reading**

- [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)

### Demo — Sidecar Containers

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (sidecar-demo.yaml)
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

STEPS
  1. kubectl apply -f sidecar-demo.yaml -n zine-demo
  2. kubectl wait --for=condition=Ready pod/sidecar-demo -n zine-demo --timeout=60s
  3. kubectl get pod sidecar-demo -n zine-demo
  4. kubectl logs sidecar-demo -c log-shipper -n zine-demo

WHAT YOU SHOULD SEE
  READY shows 2/2: two containers, one Pod. The log-shipper logs print 'shipping logs' every 5 seconds.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Two containers share one Pod: one address, one lifecycle.
</pre></div>


### Knowledge Check — Quiz

**Q1: How do two containers residing within the same Pod communicate over the network?**

- [ ] A) Through external Ingress controllers.
- [ ] B) Via localhost on their shared loopback network interface.
- [ ] C) By creating a public NodePort service.
- [ ] D) They cannot communicate over network sockets.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Via localhost on their shared loopback network interface.

**Explanation:** All containers in a Pod share the exact same network namespace and IP address, meaning they reach each other directly via localhost and shared ports.

</details>

**Q2: What is the primary operational trade-off of deploying sidecar containers across thousands of application pods?**

- [ ] A) Incompatible CPU architectures between containers.
- [ ] B) Multiplied resource overhead (CPU/memory requests & limits) and increased pod startup/shutdown latency.
- [ ] C) Inability to mount volume storage.
- [ ] D) Breaking CoreDNS name resolution for the cluster.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Multiplied resource overhead (CPU/memory requests & limits) and increased pod startup/shutdown latency.

**Explanation:** Every sidecar consumes reserved CPU and memory quota across every pod replica, and lifecycle coupling can complicate graceful shutdown if the sidecar terminates before the main app finishes.

</details>

## 13. Init Containers

**Part 1 — Technical Discussion:** An init container runs to completion before ordinary application containers are started. Init containers execute sequentially, and Kubernetes retries a failed init phase according to Pod restart behavior, making them useful for configuration generation, schema preparation, permissions, or dependency checks. Because they gate readiness, slow or non-idempotent initialization directly affects rollout and recovery time.

![Init Containers technical illustration](generated/kubernetes-apartment-complex/13-technical.png)

**Technical perspective:** Init containers create an ordered initialization phase. Kubernetes will not start the application containers until each init container exits successfully, and failed init work is retried according to Pod restart behavior. They are useful for migrations, configuration generation, and dependency checks, but long or fragile initialization directly delays application availability.


### Component architecture flow

<iframe src="diagrams/topic-13.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-13.html](diagrams/topic-13.html).

**Part 2 — Analogy / Zine:** Cleans and preps the unit, then leaves completely before the main tenant moves in.

![Init Containers zine illustration](generated/kubernetes-apartment-complex/13-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Init Containers — The Prep Crew"
* (Caption): "Setup scripts that must run to completion (e.g. running DB migrations) before the main app container starts."

**Further reading**

- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

### Demo — Init Containers

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (init-demo.yaml)
  apiVersion: v1
  kind: Pod
  metadata:
    name: init-demo
  spec:
    initContainers:
    - name: prep-crew
      image: busybox
      command: ["sh", "-c", "echo prepping unit...; sleep 10"]
    containers:
    - name: main-tenant
      image: nginx

STEPS
  1. kubectl apply -f init-demo.yaml -n zine-demo
  2. kubectl get pod init-demo -n zine-demo -w   # Ctrl+C after it shows Running
  3. kubectl logs init-demo -c prep-crew -n zine-demo

WHAT YOU SHOULD SEE
  STATUS reads Init:0/1, then PodInitializing, then Running. The init logs print 'prepping unit...'.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The init container sleeps 10 seconds so the Init:0/1 state is easy to catch on screen.
</pre></div>


### Knowledge Check — Quiz

**Q1: What happens if an Init Container fails its execution (exits with non-zero status) and the Pod's restartPolicy is Always?**

- [ ] A) The main application container starts anyway.
- [ ] B) The kubelet restarts the failed Init Container repeatedly with exponential backoff until it succeeds.
- [ ] C) The Pod is immediately deleted from the cluster.
- [ ] D) The worker node is rebooted.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The kubelet restarts the failed Init Container repeatedly with exponential backoff until it succeeds.

**Explanation:** Init containers must run sequentially to successful completion (exit 0) before any app container can launch; failures trigger kubelet restarts subject to restart policy backoff.

</details>

**Q2: In what order do multiple Init Containers defined in a Pod spec execute?**

- [ ] A) In parallel simultaneously.
- [ ] B) In the exact sequential order they are listed in the spec.initContainers array.
- [ ] C) In reverse alphabetical order by name.
- [ ] D) Randomly based on image pull completion.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) In the exact sequential order they are listed in the spec.initContainers array.

**Explanation:** Kubernetes guarantees strict sequential execution: Init Container 1 must finish with code 0 before Init Container 2 begins execution.

</details>

## 14. CNI (Container Network Interface)

**Part 1 — Technical Discussion:** The Container Network Interface is the plugin contract used to create Pod interfaces, allocate addresses, and configure routes or tunnels between Nodes. Implementations such as Calico and Cilium may also enforce NetworkPolicy, encrypt traffic, expose observability, or use eBPF datapaths. Kubernetes defines the expected Pod network model, while the CNI determines performance, failure behavior, and troubleshooting tools.

![CNI (Container Network Interface) technical illustration](generated/kubernetes-apartment-complex/14-technical.png)

**Technical perspective:** CNI is the plugin contract behind Pod networking. A plugin allocates Pod addresses, creates interfaces, installs routes, and may enforce network policy or encryption. Kubernetes defines the Pod network model, while the CNI implementation supplies the dataplane. Plugin choice therefore affects performance, security features, multi-network support, and troubleshooting methods.


### Component architecture flow

<iframe src="diagrams/topic-14.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-14.html](diagrams/topic-14.html).

**Part 2 — Analogy / Zine:** The crew that paves the roads and hands out addresses so tenants can reach each other.

![CNI (Container Network Interface) zine illustration](generated/kubernetes-apartment-complex/14-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "CNI — The Road Crew"
* (Caption): "Plugins (Calico, Cilium) that provide the actual Pod-to-Pod IP networking."

**Further reading**

- [Network plugins and CNI](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/)
- [CNI project](https://github.com/containernetworking/cni)

### Demo — CNI (Container Network Interface)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo

STEPS
  1. kubectl get pods -n kube-system -o wide | grep -iE 'calico|cilium|flannel|kindnet'
  2. kubectl get pods -A -o custom-columns=NS:.metadata.namespace,POD:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName

WHAT YOU SHOULD SEE
  A CNI Pod runs on each node (kindnet on kind, calico/cilium/flannel elsewhere). Every Pod has its own IP, even across nodes.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Flat Pod addressing works because the CNI plugin paved the roads between nodes.
</pre></div>


### Knowledge Check — Quiz

**Q1: What fundamental networking requirement does the Kubernetes network model mandate for all CNI plugins?**

- [ ] A) Every pod must use the same IP address as its host worker node.
- [ ] B) All pods can communicate with all other pods across nodes on a flat network without NAT.
- [ ] C) Every pod must have a dedicated public IPv4 address.
- [ ] D) Nodes can only communicate via SSH tunnels.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) All pods can communicate with all other pods across nodes on a flat network without NAT.

**Explanation:** The fundamental Kubernetes IP-per-pod model requires that pods on any node can communicate with pods on any other node without Network Address Translation (NAT).

</details>

**Q2: What Linux kernel mechanism is typically created by a CNI plugin to connect a Pod's network namespace to the host network?**

- [ ] A) A virtual ethernet (veth) pair connecting the pod's eth0 to a host bridge or routing table.
- [ ] B) A loopback-only interface with no host connection.
- [ ] C) An NFS network mount point.
- [ ] D) A Unix domain socket in /tmp.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) A virtual ethernet (veth) pair connecting the pod's eth0 to a host bridge or routing table.

**Explanation:** A veth pair functions like a virtual patch cable: one end sits inside the pod's network namespace as eth0, and the peer end sits in the host namespace attached to a bridge or routing engine.

</details>

## 15. CoreDNS

**Part 1 — Technical Discussion:** CoreDNS provides cluster-local DNS for Services, Pods, and configured external names. It watches Kubernetes records and answers names using zones and search paths, allowing clients to resolve a stable Service name while backend Pod IPs change. DNS latency, cache behavior, upstream forwarding, readiness, and CoreDNS capacity are operational dependencies for many applications.

![CoreDNS technical illustration](generated/kubernetes-apartment-complex/15-technical.png)

**Technical perspective:** CoreDNS provides cluster-local name resolution so applications can address Services by stable DNS names instead of tracking changing Pod IPs. It watches Kubernetes records and answers names according to configured zones and search paths. DNS failures can look like application failures, so caching, readiness, upstream forwarding, and CoreDNS capacity belong in cluster operations.


### Component architecture flow

<iframe src="diagrams/topic-15.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-15.html](diagrams/topic-15.html).

**Part 2 — Analogy / Zine:** Tenants look up a friendly name instead of memorizing unit numbers.

![CoreDNS zine illustration](generated/kubernetes-apartment-complex/15-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "CoreDNS — The Building Directory"
* (Caption): "Internal DNS that resolves Service names to cluster IPs."

**Further reading**

- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [CoreDNS project](https://coredns.io/)

### Demo — CoreDNS

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 -n zine-demo

STEPS
  1. kubectl run dns-test --image=busybox --rm -it --restart=Never -n zine-demo -- nslookup demo.zine-demo.svc.cluster.local

WHAT YOU SHOULD SEE
  nslookup returns the Service's ClusterIP. Nobody typed an IP address.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The name resolves through CoreDNS, like asking the directory board.
</pre></div>


### Knowledge Check — Quiz

**Q1: How does a Pod resolve the service name 'auth-service' located in the same namespace 'production' without specifying an FQDN?**

- [ ] A) CoreDNS broadcasts an ARP request across the node subnet.
- [ ] B) The pod's /etc/resolv.conf specifies search paths like production.svc.cluster.local, which the resolver appends automatically.
- [ ] C) The application container must hardcode the IP address in /etc/hosts.
- [ ] D) The Linux kernel queries the root DNS servers on the internet.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The pod's /etc/resolv.conf specifies search paths like production.svc.cluster.local, which the resolver appends automatically.

**Explanation:** Kubelet configures /etc/resolv.conf with search domains (<namespace>.svc.cluster.local, svc.cluster.local, etc.), allowing short names to be expanded and resolved.

</details>

**Q2: Where does CoreDNS source its real-time mapping of Service names to ClusterIPs and Endpoint IPs?**

- [ ] A) From a static text file hosted on GitHub.
- [ ] B) By watching the Kubernetes API server for Service and EndpointSlice resource events.
- [ ] C) By scanning worker node ARP tables every second.
- [ ] D) From the host operating system's /etc/bind/named.conf.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) By watching the Kubernetes API server for Service and EndpointSlice resource events.

**Explanation:** The CoreDNS kubernetes plugin connects to the kube-apiserver with an informer cache, watching Services and Endpoints to answer queries from live cluster state.

</details>

## 16. Services

**Part 1 — Technical Discussion:** A Service selects Pods by labels and exposes them through a stable virtual endpoint independent of their ephemeral IPs. ClusterIP supports internal access, while NodePort and LoadBalancer extend exposure; headless Services deliberately return backend addresses for clients that need direct discovery. Correct selectors and readiness determine which backends receive traffic during rollout, termination, and failure.

![Services technical illustration](generated/kubernetes-apartment-complex/16-technical.png)

**Technical perspective:** A Service decouples clients from ephemeral Pods by selecting backends through labels and exposing a stable virtual endpoint. ClusterIP supports internal access, NodePort and LoadBalancer extend exposure, and headless Services return backend addresses for clients that need direct discovery. The abstraction simplifies rolling updates and rescheduling because consumers do not need to learn each new Pod IP.


### Component architecture flow

<iframe src="diagrams/topic-16.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-16.html](diagrams/topic-16.html).

**Part 2 — Analogy / Zine:** A bolted mailbox that points to whichever tenants currently have the matching door nameplates.

![Services zine illustration](generated/kubernetes-apartment-complex/16-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Services — The Permanent Mailbox"
* (Caption): "Provides a stable internal IP and load balancing for a shifting set of ephemeral Pods."

**Further reading**

- [Service networking](https://kubernetes.io/docs/concepts/services-networking/service/)

### Demo — Services

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 --name=demo-svc -n zine-demo

STEPS
  1. kubectl get svc demo-svc -n zine-demo
  2. kubectl delete pod -l app=demo -n zine-demo
  3. kubectl rollout status deployment/demo -n zine-demo
  4. kubectl get svc demo-svc -n zine-demo   # same CLUSTER-IP, unchanged

WHAT YOU SHOULD SEE
  All Pods were destroyed and replaced, but CLUSTER-IP is identical before and after.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The mailbox stayed bolted to the wall while the tenants changed.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why is a Service's ClusterIP virtual IP address preferred over calling individual Pod IPs directly from client applications?**

- [ ] A) Pod IPs are slower because they require hardware encryption.
- [ ] B) Pod IPs are ephemeral and change upon container restart or rescheduling, whereas ClusterIP remains stable.
- [ ] C) Pod IPs are only reachable from the control plane node.
- [ ] D) ClusterIP bypasses all container network interfaces.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Pod IPs are ephemeral and change upon container restart or rescheduling, whereas ClusterIP remains stable.

**Explanation:** Pods are dynamic and mortal; a Service provides a durable, static IP and DNS name that load-balances traffic across the ever-shifting set of backend pods.

</details>

**Q2: Which Service type creates an external cloud load balancer and automatically configures NodePort and ClusterIP routes as well?**

- [ ] A) type: ClusterIP
- [ ] B) type: NodePort
- [ ] C) type: LoadBalancer
- [ ] D) type: ExternalName

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** C) type: LoadBalancer

**Explanation:** In Kubernetes, Service types build upon each other: LoadBalancer allocates a cloud LB, which forwards to NodePort, which routes to ClusterIP.

</details>

## 17. Endpoints

**Part 1 — Technical Discussion:** EndpointSlices are the scalable, controller-maintained representation of Service backends. They record addresses and conditions such as ready, serving, terminating, and sometimes topology hints, allowing proxies to avoid sending new traffic to unsuitable Pods. The older Endpoints object is useful for inspection but is less efficient for large Services and is being superseded by EndpointSlices.

![Endpoints technical illustration](generated/kubernetes-apartment-complex/17-technical.png)

**Technical perspective:** EndpointSlices are the scalable representation of Service backends. They track the addresses, readiness, serving state, and topology information of selected Pods in smaller objects than the legacy Endpoints API. Controllers and proxies use them to update routing as Pods become ready, terminate, or move, reducing update size for Services with many endpoints.


### Component architecture flow

<iframe src="diagrams/topic-17.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-17.html](diagrams/topic-17.html).

**Part 2 — Analogy / Zine:** The actual mail-forwarding list taped inside the mailbox, updated every time a tenant moves in or out.

![Endpoints zine illustration](generated/kubernetes-apartment-complex/17-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Endpoints — The Forwarding List"
* (Caption): "Maps a Service to the current set of Pod IPs actually backing it."

**Further reading**

- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

### Demo — Endpoints

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 --name=demo-svc -n zine-demo

STEPS
  1. kubectl get endpoints demo-svc -n zine-demo
  2. kubectl scale deployment demo --replicas=5 -n zine-demo
  3. kubectl rollout status deployment/demo -n zine-demo
  4. kubectl get endpoints demo-svc -n zine-demo   # now lists 5 IPs

WHAT YOU SHOULD SEE
  Endpoints grows from 3 IPs to 5 while the Service address never changes.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  That is the forwarding list being rewritten live. On Kubernetes 1.33+ you may see a deprecation warning for Endpoints; 'kubectl get endpointslices -n zine-demo' shows the same data.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why did Kubernetes introduce EndpointSlice resources to replace monolithic Endpoints objects in large clusters?**

- [ ] A) To support IPv6-only clusters.
- [ ] B) Monolithic Endpoints objects caused massive API server write amplification when a single pod changed in a service with thousands of replicas.
- [ ] C) Because EndpointSlice completely eliminates the need for kube-proxy.
- [ ] D) Endpoints could only store up to 5 IP addresses.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Monolithic Endpoints objects caused massive API server write amplification when a single pod changed in a service with thousands of replicas.

**Explanation:** With monolithic Endpoints, a change to 1 pod in a 5,000-pod service required resending the entire multi-megabyte object to all nodes; EndpointSlices chunk endpoints into groups of 100, dramatically reducing API bandwidth.

</details>

**Q2: What condition must a Pod satisfy before the EndpointSlice controller adds its IP address to the active serving endpoints of a Service?**

- [ ] A) The Pod must have passed its readiness probe (ContainersReady: True).
- [ ] B) The Pod must be running for at least 10 minutes.
- [ ] C) The Pod must be scheduled on the control plane node.
- [ ] D) The Pod must have no CPU limits defined.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) The Pod must have passed its readiness probe (ContainersReady: True).

**Explanation:** A pod is only considered ready to serve live user traffic when its readiness probes pass; unready pods are excluded from active service endpoints.

</details>

## 18. Ingress

**Part 1 — Technical Discussion:** An Ingress resource declares layer-7 HTTP or HTTPS matches, such as hostnames and URL paths, and maps them to Services. An Ingress controller supplies the reverse proxy, listener, TLS termination, reload behavior, and integration with an external load balancer; the resource alone does not expose traffic. Gateway API is a newer option when teams need richer routing and clearer separation of responsibilities.

![Ingress technical illustration](generated/kubernetes-apartment-complex/18-technical.png)

**Technical perspective:** Ingress expresses layer-7 HTTP routing such as host and path matches, while an Ingress controller supplies the reverse proxy, TLS termination, and implementation-specific behavior. The resource alone does not expose traffic; the controller and its load-balancer integration do. For new designs, the Gateway API can provide a more expressive, role-oriented successor.


### Component architecture flow

<iframe src="diagrams/topic-18.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-18.html](diagrams/topic-18.html).

**Part 2 — Analogy / Zine:** The single outer gate reads visitor destinations and sends them down the right internal road.

![Ingress zine illustration](generated/kubernetes-apartment-complex/18-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Ingress — The Main Gate"
* (Caption): "HTTP/S reverse proxy routing external domain traffic into your internal Services."

**Further reading**

- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

### Demo — Ingress

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
  kubectl wait --namespace ingress-nginx --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=120s
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 --name=demo-svc -n zine-demo

YAML  (demo-ingress.yaml)
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: demo-ingress
  spec:
    ingressClassName: nginx
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

STEPS
  1. kubectl apply -f demo-ingress.yaml -n zine-demo
  2. kubectl get ingress demo-ingress -n zine-demo   # wait until ADDRESS is filled
  3. curl -i -H "Host: demo.local" http://localhost:8080/

WHAT YOU SHOULD SEE
  curl returns the nginx welcome page. Changing the Host header to something else returns a 404 from the gatekeeper.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  One external address, and the hostname in the request decides which Service you reach. This demo needs the kind ingress-nginx manifest and the 8080 -> 80 mapping in kind-multinode.yaml.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the primary difference between a Kubernetes Ingress resource and an Ingress Controller?**

- [ ] A) The Ingress resource is an active proxy process; the controller is just a documentation file.
- [ ] B) The Ingress resource is a declarative configuration object; the Ingress Controller is the actual daemon that watches the API and proxies traffic.
- [ ] C) Ingress operates at Layer 4 (TCP), while the controller operates at Layer 3 (IP).
- [ ] D) Ingress requires cloud provider hardware, while controllers run on bare metal.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The Ingress resource is a declarative configuration object; the Ingress Controller is the actual daemon that watches the API and proxies traffic.

**Explanation:** An Ingress manifest (kind: Ingress) only declares routing rules; traffic does not flow until an Ingress Controller is deployed to parse those rules and proxy incoming HTTP requests.

</details>

**Q2: Which OSI layer does a standard Kubernetes Ingress operate at to provide host-based and path-based routing?**

- [ ] A) Layer 3 (Network - IP packets)
- [ ] B) Layer 4 (Transport - TCP/UDP sockets)
- [ ] C) Layer 7 (Application - HTTP/HTTPS URLs, headers, and hostnames)
- [ ] D) Layer 2 (Data Link - MAC addresses)

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** C) Layer 7 (Application - HTTP/HTTPS URLs, headers, and hostnames)

**Explanation:** Ingress inspects HTTP requests (Host headers like api.example.com and URL paths like /v1/users) to direct traffic to appropriate internal services.

</details>

## 19. NetworkPolicy

**Part 1 — Technical Discussion:** NetworkPolicy is a declarative allow-list boundary for Pod ingress and egress. Policies select Pods and permit traffic by namespace, Pod labels, ports, and protocol, but enforcement is supplied by a policy-capable CNI rather than the API object itself. A rollout must account for DNS, health checks, control-plane access, default-allow behavior, and the fact that network policy is not application authentication.

![NetworkPolicy technical illustration](generated/kubernetes-apartment-complex/19-technical.png)

**Technical perspective:** NetworkPolicy is an allow-list-style authorization layer for network traffic. Policies select Pods and define permitted ingress or egress by namespace, Pod labels, ports, and direction, but only a policy-capable CNI can enforce them. A safe rollout starts with understanding default allow behavior, DNS dependencies, health checks, and the difference between isolation and application authentication.


### Component architecture flow

<iframe src="diagrams/topic-19.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-19.html](diagrams/topic-19.html).

**Part 2 — Analogy / Zine:** A guest list posted on a unit's door — only visitors on the list get buzzed in, everyone else is turned away at that door.

![NetworkPolicy zine illustration](generated/kubernetes-apartment-complex/19-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "NetworkPolicy — The Guest List"
* (Caption): "Restricts which Pods can talk to which other Pods — without one, every door is unlocked to everyone."

**Further reading**

- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

### Demo — NetworkPolicy

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo
  kubectl expose deployment demo --port=80 --name=demo-svc -n zine-demo
  kubectl create namespace other-ns

YAML  (deny-demo.yaml)
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

STEPS
  1. kubectl run before --image=busybox --rm -it --restart=Never -n other-ns -- wget -qO- --timeout=3 demo-svc.zine-demo.svc.cluster.local   # works
  2. kubectl apply -f deny-demo.yaml -n zine-demo
  3. kubectl run intruder --image=busybox --rm -it --restart=Never -n other-ns -- wget -qO- --timeout=3 demo-svc.zine-demo.svc.cluster.local   # now times out

WHAT YOU SHOULD SEE
  Before the policy the request returns the nginx page. After it the request times out.

CLEANUP
  kubectl delete namespace zine-demo other-ns

NOTE
  The default kind CNI (kindnet) does not enforce NetworkPolicy, so the second request will still succeed. Run this demo on a separate kind cluster configured with Calico or Cilium; do not try to replace kindnet in an already-running cluster.
</pre></div>


### Knowledge Check — Quiz

**Q1: What happens in a namespace when no NetworkPolicies are applied versus when a single NetworkPolicy with podSelector: {} and ingress: [] is applied?**

- [ ] A) Default behavior is allow-all; applying an empty ingress policy creates an isolation boundary that defaults to deny-all incoming traffic.
- [ ] B) Default behavior is deny-all; applying a policy enables allow-all.
- [ ] C) Applying a policy disables DNS resolution across the entire cluster.
- [ ] D) The container runtime pauses all running containers.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) Default behavior is allow-all; applying an empty ingress policy creates an isolation boundary that defaults to deny-all incoming traffic.

**Explanation:** By default, pod networking is non-isolated (allow all). As soon as any NetworkPolicy selects a pod, that pod enters isolated mode where unselected traffic is rejected.

</details>

**Q2: Why might a newly created NetworkPolicy fail to enforce traffic blocking in a cluster running standard default kind?**

- [ ] A) The policy YAML had invalid syntax.
- [ ] B) The default CNI plugin in standard kind (kindnet) does not implement NetworkPolicy enforcement; a policy-capable CNI (like Calico or Cilium) is required.
- [ ] C) NetworkPolicies only work in production cloud clusters.
- [ ] D) kube-apiserver disables NetworkPolicy by default.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The default CNI plugin in standard kind (kindnet) does not implement NetworkPolicy enforcement; a policy-capable CNI (like Calico or Cilium) is required.

**Explanation:** NetworkPolicy is a declarative API spec; enforcement is the responsibility of the underlying CNI plugin dataplane (eBPF or iptables). Kindnet does not support NetworkPolicy.

</details>

## 20. PersistentVolume (PV)

**Part 1 — Technical Discussion:** A PersistentVolume is a cluster storage resource whose lifecycle is decoupled from an individual Pod. Its provisioner, access mode, volume mode, reclaim policy, topology, and attachment semantics determine how it can be used and what happens after a claim is released. A PV preserves data across ordinary Pod replacement, but does not by itself provide backups, replication, consistency, or protection from deletion.

![PersistentVolume (PV) technical illustration](generated/kubernetes-apartment-complex/20-technical.png)

**Technical perspective:** A PersistentVolume represents storage independently of a Pod lifecycle. Its reclaim policy, access mode, volume mode, topology, and storage backend determine what survives Pod replacement and how it can be attached. Persistence prevents data loss from ordinary rescheduling, but it does not automatically provide backups, replication, consistency guarantees, or protection from operator error.


### Component architecture flow

<iframe src="diagrams/topic-20.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-20.html](diagrams/topic-20.html).

**Part 2 — Analogy / Zine:** A separate storage facility building down the road, built to outlast any single tenant.

![PersistentVolume (PV) zine illustration](generated/kubernetes-apartment-complex/20-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "PersistentVolume — The Storage Facility"
* (Caption): "Represents actual cluster storage, provisioned ahead of time or dynamically, independent of any Pod's lifecycle."

**Further reading**

- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Demo — PersistentVolume (PV)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl apply -f pv-setup.yaml -n zine-demo
  kubectl wait --for=condition=Ready pod/pvc-user -n zine-demo --timeout=90s

YAML  (pv-setup.yaml)
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: demo-pvc
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 1Gi
  ---
  apiVersion: v1
  kind: Pod
  metadata:
    name: pvc-user
  spec:
    containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts:
      - name: data
        mountPath: /data
    volumes:
    - name: data
      persistentVolumeClaim:
        claimName: demo-pvc

STEPS
  1. kubectl get pv
  2. PV=$(kubectl get pv -o jsonpath='{.items[0].metadata.name}')
  3. kubectl describe pv $PV | grep -E 'Status|Claim|StorageClass|Reclaim'
  4. kubectl delete pod pvc-user -n zine-demo
  5. kubectl get pv $PV   # still there after the Pod is gone

WHAT YOU SHOULD SEE
  The PV shows STATUS Bound and a Claim. After the Pod is deleted the PV is still listed: it lives at cluster level, independent of any Pod.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  This setup creates a claim and Pod so a PV exists to look at. The PV outlives the Pod.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the difference in scope between a PersistentVolume (PV) and a PersistentVolumeClaim (PVC)?**

- [ ] A) A PV is namespaced, while a PVC is cluster-scoped.
- [ ] B) A PV is a cluster-wide storage resource, while a PVC is a namespaced request for storage.
- [ ] C) Both PV and PVC must reside in the kube-system namespace.
- [ ] D) A PV can only be mounted by one pod across the entire cluster lifetime.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) A PV is a cluster-wide storage resource, while a PVC is a namespaced request for storage.

**Explanation:** PVs are cluster-level infrastructure objects created by admins or dynamic provisioners; PVCs are namespaced consumer objects created by developers.

</details>

**Q2: If a PersistentVolume has persistentVolumeReclaimPolicy set to Retain, what occurs when its bound PVC is deleted?**

- [ ] A) The underlying storage disk and data are immediately wiped.
- [ ] B) The PV moves to Released status; the volume and data remain intact on physical storage until manually reclaimed.
- [ ] C) The PV is automatically assigned to a random new Pod.
- [ ] D) The storage volume is resized to 0GB.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The PV moves to Released status; the volume and data remain intact on physical storage until manually reclaimed.

**Explanation:** Retain prevents automated data loss: when the claim is deleted, the volume transitions to Released and requires manual administrator cleanup.

</details>

## 21. PersistentVolumeClaim (PVC)

**Part 1 — Technical Discussion:** A PersistentVolumeClaim is a workload-facing request for capacity and storage characteristics rather than a provider-specific disk definition. Kubernetes binds it to a compatible PV—or triggers dynamic provisioning—using capacity, access mode, volume mode, StorageClass, and topology constraints. A Pending claim is therefore a useful diagnostic signal for missing capacity, an unavailable provisioner, or incompatible scheduling requirements.

![PersistentVolumeClaim (PVC) technical illustration](generated/kubernetes-apartment-complex/21-technical.png)

**Technical perspective:** A PersistentVolumeClaim is a workload-facing storage request. Kubernetes binds it to a compatible PV using capacity, access mode, volume mode, and StorageClass constraints, allowing application manifests to avoid provider-specific disk details. A claim can remain Pending when no matching or provisionable storage exists, so capacity, topology, and provisioner health must be checked.


### Component architecture flow

<iframe src="diagrams/topic-21.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-21.html](diagrams/topic-21.html).

**Part 2 — Analogy / Zine:** A universal rental agreement a tenant signs to claim a unit in the storage facility.

![PersistentVolumeClaim (PVC) zine illustration](generated/kubernetes-apartment-complex/21-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "PersistentVolumeClaim — The Rental Agreement"
* (Caption): "A request for storage that Kubernetes matches to a suitable PersistentVolume."

**Further reading**

- [PersistentVolumeClaims](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)

### Demo — PersistentVolumeClaim (PVC)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (demo-pvc.yaml)
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: demo-pvc
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 1Gi
  ---
  apiVersion: v1
  kind: Pod
  metadata:
    name: pvc-user
  spec:
    containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo hello > /data/hello.txt; sleep 3600"]
      volumeMounts:
      - name: data
        mountPath: /data
    volumes:
    - name: data
      persistentVolumeClaim:
        claimName: demo-pvc

STEPS
  1. kubectl apply -f demo-pvc.yaml -n zine-demo
  2. kubectl get pvc demo-pvc -n zine-demo   # Pending until a Pod uses it, if WaitForFirstConsumer
  3. kubectl wait --for=condition=Ready pod/pvc-user -n zine-demo --timeout=90s
  4. kubectl get pvc demo-pvc -n zine-demo   # now Bound
  5. kubectl get pv

WHAT YOU SHOULD SEE
  The PVC goes Pending, then Bound once the Pod starts. A new PV appears with the claim's name, provisioned automatically.

CLEANUP
  kubectl delete namespace zine-demo   # the PV is removed too under the default Delete reclaim policy

NOTE
  The claim is matched to a real volume without anyone creating the PV by hand.
</pre></div>


### Knowledge Check — Quiz

**Q1: What state does a PVC remain in if no existing PV matches its capacity and accessModes, and no dynamic provisioner is configured?**

- [ ] A) Failed
- [ ] B) Pending
- [ ] C) Terminating
- [ ] D) Running

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Pending

**Explanation:** The PVC remains Pending until a matching PV is created or dynamically provisioned, and any Pod referencing that PVC will be blocked from starting.

</details>

**Q2: Which access mode allows a single volume to be mounted read-write by multiple pods simultaneously across different worker nodes?**

- [ ] A) ReadWriteOnce (RWO)
- [ ] B) ReadOnlyMany (ROX)
- [ ] C) ReadWriteMany (RWX)
- [ ] D) ReadWriteOncePod (RWOP)

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** C) ReadWriteMany (RWX)

**Explanation:** ReadWriteMany (RWX) permits simultaneous read/write mounting across multiple nodes (typically backed by NFS, CephFS, or cloud file storage).

</details>

## 22. StorageClass

**Part 1 — Technical Discussion:** A StorageClass defines the policy for dynamically provisioning volumes. It selects a provisioner and parameters such as disk type, filesystem, replication, encryption, reclaim policy, and volume-binding mode. Dynamic provisioning reduces manual work, but its defaults directly affect cost, performance, data retention, and whether a volume can be placed in the same topology as its consumer.

![StorageClass technical illustration](generated/kubernetes-apartment-complex/22-technical.png)

**Technical perspective:** A StorageClass is a policy and provisioning recipe for dynamic volumes. It selects a provisioner and parameters such as disk type, replication, filesystem, and binding mode. Dynamic provisioning reduces manual storage administration, while the chosen defaults and reclaim behavior have direct cost, performance, availability, and data-retention consequences.


### Component architecture flow

<iframe src="diagrams/topic-22.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-22.html](diagrams/topic-22.html).

**Part 2 — Analogy / Zine:** The complex's pre-approved construction blueprint for building a brand-new storage unit on demand, instead of waiting for one to already exist.

![StorageClass zine illustration](generated/kubernetes-apartment-complex/22-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "StorageClass — The Construction Blueprint"
* (Caption): "Defines how new storage gets dynamically provisioned on demand, so nobody has to pre-build units ahead of time."

**Further reading**

- [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/)

### Demo — StorageClass

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get storageclass
  2. SC=$(kubectl get storageclass -o jsonpath='{.items[0].metadata.name}')
  3. kubectl describe storageclass $SC

WHAT YOU SHOULD SEE
  One StorageClass is marked (default). describe shows its Provisioner, ReclaimPolicy and VolumeBindingMode.

CLEANUP
  (nothing to clean up)

NOTE
  This is the blueprint used automatically when a PVC names no class, which is why the PV in entry 21 appeared with no manual step. The default class in this kind cluster is commonly named 'standard'. Verify with 'kubectl get storageclass' because the name depends on the provisioner installed.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the primary purpose of setting volumeBindingMode: WaitForFirstConsumer on a StorageClass?**

- [ ] A) It ensures volumes are created without filesystem formatting.
- [ ] B) It delays dynamic volume creation until a Pod referencing the PVC is scheduled, ensuring the volume is provisioned in the same availability zone as the Pod.
- [ ] C) It disables volume caching in memory.
- [ ] D) It prevents users from deleting the PVC.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It delays dynamic volume creation until a Pod referencing the PVC is scheduled, ensuring the volume is provisioned in the same availability zone as the Pod.

**Explanation:** Without this setting, volumes might be provisioned in an availability zone where candidate worker nodes lack capacity, preventing the pod from scheduling.

</details>

**Q2: In dynamic volume provisioning, what component detects an unbound PVC and calls the underlying storage infrastructure to create the disk?**

- [ ] A) The kube-scheduler.
- [ ] B) The CSI external-provisioner controller.
- [ ] C) The CoreDNS daemon.
- [ ] D) The container runtime runc binary.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The CSI external-provisioner controller.

**Explanation:** The CSI external-provisioner sidecar watches for PVCs with an associated StorageClass and issues CreateVolume gRPC requests to the CSI driver.

</details>

## 23. Role

**Part 1 — Technical Discussion:** A Role defines namespaced RBAC permissions as API groups, resources, resource names, and verbs such as get, list, create, or update. It is a permission rule—not an identity or a grant—and has no effect until a RoleBinding attaches it to a subject. Least privilege requires avoiding unnecessary wildcards and treating access to Secrets or workload creation as potentially sensitive.

![Role technical illustration](generated/kubernetes-apartment-complex/23-technical.png)

**Technical perspective:** A Role defines namespaced permissions as API groups, resources, resource names, and verbs. It is deliberately separate from identity: writing a permission rule does nothing until a binding attaches it to a subject. This separation supports least privilege and reviewable policy, but wildcard permissions and access to Secrets can create broad escalation paths.


### Component architecture flow

<iframe src="diagrams/topic-23.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-23.html](diagrams/topic-23.html).

**Part 2 — Analogy / Zine:** A printed set of house rules for one specific building — what's allowed inside, but nobody's name is on it yet.

![Role zine illustration](generated/kubernetes-apartment-complex/23-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Role — The House Rules"
* (Caption): "Defines what's permitted within one building (Namespace) — but grants it to nobody until a name is added."

**Further reading**

- [RBAC roles and permissions](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole)

### Demo — Role

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl create role pod-reader --verb=get,list,watch --resource=pods -n zine-demo
  2. kubectl get role pod-reader -n zine-demo -o yaml
  3. kubectl auth can-i get pods --as=jane -n zine-demo   # no

WHAT YOU SHOULD SEE
  The Role lists the get, list, watch verbs on pods. can-i answers 'no'.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The house rules are posted, but no name is attached to them yet.
</pre></div>


### Knowledge Check — Quiz

**Q1: Can a standard Kubernetes Role grant permissions to list nodes or create namespaces?**

- [ ] A) Yes, if the namespace field is omitted.
- [ ] B) No, because a Role is strictly namespaced and can only grant permissions on namespaced resources within its own namespace; cluster-scoped resources require a ClusterRole.
- [ ] C) Yes, if granted by an administrator.
- [ ] D) Only on worker nodes, not control plane nodes.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) No, because a Role is strictly namespaced and can only grant permissions on namespaced resources within its own namespace; cluster-scoped resources require a ClusterRole.

**Explanation:** Roles are bounded by namespace; non-namespaced resources (like Nodes, Namespaces, and PersistentVolumes) can only be governed by ClusterRoles.

</details>

**Q2: How does the Kubernetes RBAC authorization engine evaluate permissions when multiple Roles or rules apply to a single identity?**

- [ ] A) It uses a deny-first evaluation where explicit denies override allows.
- [ ] B) It uses purely additive (allow-only) evaluation; if any matching rule grants the verb on the resource, the action is permitted.
- [ ] C) It takes the intersection of all granted permissions.
- [ ] D) It grants access only if the client certificate was created within 24 hours.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It uses purely additive (allow-only) evaluation; if any matching rule grants the verb on the resource, the action is permitted.

**Explanation:** Kubernetes RBAC has no 'deny' rules; all permissions are additive (whitelisting). Access is authorized if at least one rule grants the requested verb.

</details>

## 24. RoleBinding

**Part 1 — Technical Discussion:** A RoleBinding grants a Role or ClusterRole to a user, group, or ServiceAccount within one Namespace. The binding is the effective assignment: reviewing a Role without reviewing its bindings can miss broad groups or automation identities that receive the permission. Namespace scope limits where the grant applies, even when the referenced role is cluster-scoped.

![RoleBinding technical illustration](generated/kubernetes-apartment-complex/24-technical.png)

**Technical perspective:** A RoleBinding attaches a Role or ClusterRole’s permissions to a user, group, or ServiceAccount within a namespace. The binding is the grant that makes the rule effective, and namespace scope limits where it applies. Reviewing bindings—not just roles—is essential because an apparently narrow role can become powerful when bound to a broad group.


### Component architecture flow

<iframe src="diagrams/topic-24.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-24.html](diagrams/topic-24.html).

**Part 2 — Analogy / Zine:** The clipboard sign-up sheet where a specific tenant's name gets added under the house rules, officially granting them those permissions.

![RoleBinding zine illustration](generated/kubernetes-apartment-complex/24-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "RoleBinding — The Sign-Up Sheet"
* (Caption): "Grants a Role's permissions to a specific user, group, or ServiceAccount, within that same building (Namespace)."

**Further reading**

- [RoleBindings](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)

### Demo — RoleBinding

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create role pod-reader --verb=get,list,watch --resource=pods -n zine-demo

STEPS
  1. kubectl auth can-i get pods --as=jane -n zine-demo   # no
  2. kubectl create rolebinding read-pods-binding --role=pod-reader --user=jane -n zine-demo
  3. kubectl auth can-i get pods --as=jane -n zine-demo   # yes

WHAT YOU SHOULD SEE
  can-i flips from 'no' to 'yes' the moment the binding exists.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The name got added to the sign-up sheet.
</pre></div>


### Knowledge Check — Quiz

**Q1: Can a RoleBinding located in namespace 'dev' reference a ClusterRole in its roleRef?**

- [ ] A) No, RoleBindings can only bind namespaced Roles.
- [ ] B) Yes; it binds the ClusterRole's defined permissions, but scopes them strictly to namespace 'dev'.
- [ ] C) Yes, and it automatically grants the user cluster-wide admin access.
- [ ] D) Only if the user has root privileges on the control-plane host.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Yes; it binds the ClusterRole's defined permissions, but scopes them strictly to namespace 'dev'.

**Explanation:** Referencing a ClusterRole in a namespaced RoleBinding is a common pattern to reuse common permission sets (e.g. edit or view) within an individual namespace.

</details>

**Q2: What happens if an administrator attempts to modify the roleRef field of an existing RoleBinding object?**

- [ ] A) The API server updates all bound subjects immediately.
- [ ] B) The API server rejects the mutation because the roleRef field is immutable; the binding must be deleted and recreated.
- [ ] C) The referenced Role is deleted.
- [ ] D) The subjects lose access to the cluster permanently.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The API server rejects the mutation because the roleRef field is immutable; the binding must be deleted and recreated.

**Explanation:** roleRef is an immutable field in Kubernetes RBAC to prevent accidental privilege escalation; you must delete and recreate the binding to point to a new role.

</details>

## 25. ClusterRole

**Part 1 — Technical Discussion:** A ClusterRole describes reusable RBAC permissions that can apply across namespaces or to cluster-scoped resources such as Nodes and PersistentVolumes. A namespaced RoleBinding can use a ClusterRole while restricting the grant to that namespace, whereas a ClusterRoleBinding grants it cluster-wide. This reuse improves consistency, but broad rules can expose or mutate resources far beyond one application.

![ClusterRole technical illustration](generated/kubernetes-apartment-complex/25-technical.png)

**Technical perspective:** A ClusterRole describes permissions that can apply across namespaces or to cluster-scoped resources such as Nodes. It can also be referenced by a namespaced RoleBinding for reusable namespaced rules. Cluster-wide permission definitions improve consistency, but a careless binding can grant visibility or mutation across the entire cluster.


### Component architecture flow

<iframe src="diagrams/topic-25.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-25.html](diagrams/topic-25.html).

**Part 2 — Analogy / Zine:** A master house-rules sheet that applies across every building in the entire complex, not just one.

![ClusterRole zine illustration](generated/kubernetes-apartment-complex/25-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ClusterRole — The Master House Rules"
* (Caption): "Like a Role, but scoped to the entire cluster instead of a single Namespace."

**Further reading**

- [RBAC roles and permissions](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole)

### Demo — ClusterRole

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl create clusterrole node-reader --verb=get,list,watch --resource=nodes
  2. kubectl get clusterrole node-reader -o yaml
  3. kubectl api-resources --namespaced=false | grep -w nodes

WHAT YOU SHOULD SEE
  The ClusterRole is created with rules for nodes. api-resources shows nodes with NAMESPACED false.

CLEANUP
  kubectl delete clusterrole node-reader

NOTE
  Nodes are cluster-scoped, so this had to be a ClusterRole and could not be a plain Role.
</pre></div>


### Knowledge Check — Quiz

**Q1: When is a ClusterRole strictly required instead of a namespaced Role?**

- [ ] A) When deploying a container that uses more than 1GB of memory.
- [ ] B) When granting access to non-namespaced resources (e.g. Nodes, PersistentVolumes) or non-resource URLs (e.g. /healthz).
- [ ] C) Whenever using kind on a local machine.
- [ ] D) When mounting an emptyDir volume.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) When granting access to non-namespaced resources (e.g. Nodes, PersistentVolumes) or non-resource URLs (e.g. /healthz).

**Explanation:** Non-namespaced API endpoints and cluster-wide resources do not belong to any individual namespace and therefore cannot be expressed in a namespaced Role.

</details>

**Q2: How do aggregated ClusterRoles work in Kubernetes?**

- [ ] A) They combine multiple physical worker nodes into a single logical entity.
- [ ] B) The cluster dynamically combines rules from other ClusterRoles matching specified label selectors into an aggregate role.
- [ ] C) They merge all user passwords into a single hash.
- [ ] D) They compress API requests to improve network throughput.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The cluster dynamically combines rules from other ClusterRoles matching specified label selectors into an aggregate role.

**Explanation:** ClusterRole aggregation allows custom controllers to extend built-in roles (like admin or edit) by labeling new ClusterRoles that are automatically merged.

</details>

## 26. ClusterRoleBinding

**Part 1 — Technical Discussion:** A ClusterRoleBinding attaches a ClusterRole to a subject at cluster scope, making its permissions effective across namespaces and for covered cluster-scoped resources. It is appropriate for tightly controlled platform controllers, but it is one of the highest-impact RBAC grants. Prefer a namespaced RoleBinding where possible and audit effective permissions rather than relying only on role names.

![ClusterRoleBinding technical illustration](generated/kubernetes-apartment-complex/26-technical.png)

**Technical perspective:** A ClusterRoleBinding grants a ClusterRole to subjects at cluster scope. It is appropriate for tightly controlled platform automation that must inspect or manage many namespaces, but it is one of the highest-impact RBAC objects. Use narrowly scoped roles and bindings where possible, audit effective permissions, and avoid giving application identities cluster-admin access.


### Component architecture flow

<iframe src="diagrams/topic-26.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-26.html](diagrams/topic-26.html).

**Part 2 — Analogy / Zine:** A master key issued to one person that works on every building in the complex, not just one unit.

![ClusterRoleBinding zine illustration](generated/kubernetes-apartment-complex/26-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ClusterRoleBinding — The Master Key"
* (Caption): "Grants a ClusterRole's permissions to a subject across the entire cluster, not just one Namespace."

**Further reading**

- [RoleBindings](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)

### Demo — ClusterRoleBinding

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create clusterrole node-reader --verb=get,list,watch --resource=nodes

STEPS
  1. kubectl auth can-i get nodes --as=jane   # no
  2. kubectl create clusterrolebinding read-nodes-binding --clusterrole=node-reader --user=jane
  3. kubectl auth can-i get nodes --as=jane   # yes
  4. kubectl auth can-i get nodes --as=jane -n kube-system   # yes, same answer in any namespace

WHAT YOU SHOULD SEE
  can-i flips from 'no' to 'yes', and the answer is the same in every namespace.

CLEANUP
  kubectl delete clusterrolebinding read-nodes-binding
  kubectl delete clusterrole node-reader

NOTE
  The master key is not scoped to any one building.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the operational risk of binding the built-in cluster-admin ClusterRole to a ServiceAccount using a ClusterRoleBinding?**

- [ ] A) It limits the ServiceAccount to reading configmaps only.
- [ ] B) It grants unrestricted superuser privileges across every namespace and cluster-scoped resource, creating a critical security risk if the token is compromised.
- [ ] C) It causes the kubelet to reboot every worker node.
- [ ] D) It disables TLS encryption across the cluster.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It grants unrestricted superuser privileges across every namespace and cluster-scoped resource, creating a critical security risk if the token is compromised.

**Explanation:** cluster-admin provides unrestricted access (* verbs on * resources); granting it globally violates least privilege and exposes the entire platform to compromise.

</details>

**Q2: Can a ClusterRoleBinding grant permissions that are limited to a single namespace?**

- [ ] A) Yes, by setting the namespace field in the binding metadata.
- [ ] B) No; ClusterRoleBindings are cluster-scoped and always apply across all namespaces; to scope permissions to one namespace, use a RoleBinding.
- [ ] C) Yes, if the subject is a ServiceAccount.
- [ ] D) Only on worker nodes.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) No; ClusterRoleBindings are cluster-scoped and always apply across all namespaces; to scope permissions to one namespace, use a RoleBinding.

**Explanation:** ClusterRoleBindings are inherently global; scoping permissions to a specific namespace requires a namespaced RoleBinding.

</details>

## 27. ServiceAccount

**Part 1 — Technical Discussion:** A ServiceAccount is a Kubernetes identity intended for workloads rather than human operators. A Pod can receive a projected, usually short-lived token for that identity, and the API server uses RBAC to decide what the application may do. Dedicated accounts, automount controls, rotation, and minimal permissions reduce the impact of a compromised workload.

![ServiceAccount technical illustration](generated/kubernetes-apartment-complex/27-technical.png)

**Technical perspective:** A ServiceAccount gives software in a Pod a Kubernetes identity distinct from a human kubeconfig user. Tokens and projected credentials let applications authenticate to the API server, while RBAC determines what that identity may do. Treat ServiceAccounts as security principals: use dedicated accounts, short-lived projected tokens, and only the permissions the workload needs.


### Component architecture flow

<iframe src="diagrams/topic-27.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-27.html](diagrams/topic-27.html).

**Part 2 — Analogy / Zine:** A staff ID badge issued to a robot maintenance worker so the front desk knows it's an authorized employee, not a random visitor.

![ServiceAccount zine illustration](generated/kubernetes-apartment-complex/27-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ServiceAccount — The Staff ID Badge"
* (Caption): "Provides an identity for processes inside Pods to authenticate to the API server — distinct from a human user."

**Further reading**

- [ServiceAccounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

### Demo — ServiceAccount

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create serviceaccount demo-bot -n zine-demo

STEPS
  1. kubectl run badge-test --image=busybox -n zine-demo --overrides='{"spec":{"serviceAccountName":"demo-bot"}}' --rm -it --restart=Never -- sh -c 'ls /var/run/secrets/kubernetes.io/serviceaccount/; head -c 50 /var/run/secrets/kubernetes.io/serviceaccount/token; echo'

WHAT YOU SHOULD SEE
  The folder contains ca.crt, namespace and token. The first 50 characters of the token print (it starts with eyJ).

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Every Pod gets a token mounted automatically: its staff ID badge. The token is short-lived and rotated by the kubelet.
</pre></div>


### Knowledge Check — Quiz

**Q1: Under modern Kubernetes token projection (BoundServiceAccountTokenVolume), what happens when a Pod is deleted?**

- [ ] A) The token remains valid indefinitely.
- [ ] B) The projected token is tied to the Pod's lifecycle and becomes invalid when the Pod is deleted.
- [ ] C) The entire ServiceAccount is automatically deleted.
- [ ] D) The API server revokes all client certificates.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The projected token is tied to the Pod's lifecycle and becomes invalid when the Pod is deleted.

**Explanation:** Projected service account tokens are cryptographically signed, audience-bound, time-limited, and bound to the specific Pod's UID, mitigating stolen token replay attacks.

</details>

**Q2: Where does kubelet mount the projected ServiceAccount token inside a container by default?**

- [ ] A) /etc/kubernetes/admin.conf
- [ ] B) /var/run/secrets/kubernetes.io/serviceaccount/
- [ ] C) /root/.kube/config
- [ ] D) /tmp/k8s/

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) /var/run/secrets/kubernetes.io/serviceaccount/

**Explanation:** Kubelet automatically mounts the token, ca.crt, and namespace files into /var/run/secrets/kubernetes.io/serviceaccount/ unless automountServiceAccountToken: false is configured.

</details>

## 28. Node (controller)

**Part 1 — Technical Discussion:** The Node controller combines kubelet heartbeats and lease updates into a cluster-level health decision. When communication stops, it marks the Node unhealthy and, after configured toleration periods, enables eviction or replacement of eligible workloads. Detection is deliberately delayed to avoid reacting to transient partitions, so replicas, topology spread, and graceful shutdown remain necessary for resilience.

![Node (controller) technical illustration](generated/kubernetes-apartment-complex/28-technical.png)

**Technical perspective:** The Node controller turns kubelet heartbeats and lease updates into a cluster-level health view. When a node stops reporting, Kubernetes marks it unhealthy and eventually evicts or recreates eligible workloads, subject to timing and disruption rules. Detection is intentionally delayed to avoid reacting to transient network loss, so applications still need redundancy and graceful failure handling.


### Component architecture flow

<iframe src="diagrams/topic-28.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-28.html](diagrams/topic-28.html).

**Part 2 — Analogy / Zine:** The office worker who checks in on every building daily, and starts moving tenants out if a building goes quiet for too long.

![Node (controller) zine illustration](generated/kubernetes-apartment-complex/28-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Node Controller — The Daily Check-In"
* (Caption): "Watches Node health via heartbeats, marking a Node NotReady and evicting its Pods if it goes silent too long."

**Further reading**

- [Node lifecycle](https://kubernetes.io/docs/concepts/architecture/nodes/#node-lifecycle)
- [Node controller](https://kubernetes.io/docs/concepts/architecture/nodes/)

### Demo — Node (controller)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get nodes
  2. NODE=$(kubectl get nodes -o jsonpath='{.items[-1].metadata.name}')
  3. kubectl describe node $NODE | grep -A8 Conditions
  4. # simulate a dead node: on a WORKER node stop the kubelet
  5. docker exec zine-worker systemctl stop kubelet
  6. kubectl get nodes -w   # Ctrl+C once it shows NotReady

WHAT YOU SHOULD SEE
  The node moves from Ready to NotReady after about 40 seconds. After the eviction timeout (about 5 minutes) its Pods are rescheduled onto healthy nodes.

CLEANUP
  docker exec zine-worker systemctl start kubelet

NOTE
  Needs a multi-node cluster. Do NOT stop the kubelet on your only node or the control plane goes dark.
</pre></div>


### Knowledge Check — Quiz

**Q1: How does the Node lifecycle controller detect that a worker node has become unhealthy?**

- [ ] A) By attempting to ping the host over ICMP every millisecond.
- [ ] B) By monitoring the node's Lease object in kube-node-lease; if no heartbeat renewal occurs within node-monitor-grace-period, the node is flagged NotReady.
- [ ] C) By polling the cloud provider's billing dashboard.
- [ ] D) By checking whether the containers on the node are serving HTTP 200.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) By monitoring the node's Lease object in kube-node-lease; if no heartbeat renewal occurs within node-monitor-grace-period, the node is flagged NotReady.

**Explanation:** Kubelets post periodic lease updates (heartbeats) every 10s; if missed beyond the grace period (default 40s), the controller marks the node NotReady.

</details>

**Q2: When a node transitions to NotReady, what taint is automatically applied to begin the pod eviction process?**

- [ ] A) node.kubernetes.io/unreachable:NoExecute or node.kubernetes.io/not-ready:NoExecute
- [ ] B) node-role.kubernetes.io/control-plane:NoSchedule
- [ ] C) kubernetes.io/drain-active:PreferNoSchedule
- [ ] D) node.kubernetes.io/memory-pressure:AllowAll

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) node.kubernetes.io/unreachable:NoExecute or node.kubernetes.io/not-ready:NoExecute

**Explanation:** NoExecute taints evict pods immediately unless those pods specify a matching toleration with a tolerationSeconds grace window.

</details>

## 29. Namespace (controller)

**Part 1 — Technical Discussion:** Namespaces scope namespaced objects and provide a boundary for RBAC, quotas, and many policy resources. The Namespace controller coordinates deletion by discovering and removing contained objects before finalizing the Namespace. Finalizers or unavailable controllers can leave deletion in Terminating, so forced removal should be treated as a repair action with possible orphaned resources.

![Namespace (controller) technical illustration](generated/kubernetes-apartment-complex/29-technical.png)

**Technical perspective:** Namespaces partition namespaced objects and provide a scope for access control, quotas, and policy. They are useful administrative boundaries, not hard security walls or virtual clusters. Deleting a Namespace initiates cleanup of its contents, so finalizers or an unresponsive controller can leave termination stuck until the dependency is resolved.


### Component architecture flow

<iframe src="diagrams/topic-29.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-29.html](diagrams/topic-29.html).

**Part 2 — Analogy / Zine:** When a fenced section of the property is being shut down, every tenant and piece of furniture inside is cleared out first before the fence itself comes down.

![Namespace (controller) zine illustration](generated/kubernetes-apartment-complex/29-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Namespace Controller — The Section Closure"
* (Caption): "Ensures every resource inside a Namespace is cleaned up before the Namespace itself is removed."

**Further reading**

- [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)

### Demo — Namespace (controller)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl create namespace demo-ns
  2. kubectl run temp-pod --image=nginx -n demo-ns
  3. kubectl wait --for=condition=Ready pod/temp-pod -n demo-ns --timeout=60s
  4. kubectl delete namespace demo-ns --wait=false
  5. kubectl get namespace demo-ns -w   # shows Terminating, then disappears

WHAT YOU SHOULD SEE
  The namespace sits in Terminating while temp-pod is cleaned up, then disappears. --wait=false keeps your terminal free so you can watch.

CLEANUP
  (nothing to clean up)

NOTE
  The fence does not come down until the section is empty.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why does a namespace sometimes become stuck in the Terminating state indefinitely?**

- [ ] A) Because the cluster has run out of CPU capacity.
- [ ] B) Because one or more resources inside the namespace have finalizers that cannot be completed or cleared.
- [ ] C) Because the namespace name was longer than 10 characters.
- [ ] D) Because kube-proxy is running in iptables mode.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Because one or more resources inside the namespace have finalizers that cannot be completed or cleared.

**Explanation:** A namespace cannot be deleted until all resources within it are gone; if a custom resource or PVC has an unfulfilled finalizer, deletion hangs in Terminating.

</details>

**Q2: Which objects are NOT deleted when a namespace is deleted?**

- [ ] A) Deployments and ReplicaSets in that namespace.
- [ ] B) Cluster-scoped objects like Nodes, PersistentVolumes, and ClusterRoles.
- [ ] C) Secrets and ConfigMaps in that namespace.
- [ ] D) Pods and Services in that namespace.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Cluster-scoped objects like Nodes, PersistentVolumes, and ClusterRoles.

**Explanation:** Namespace deletion cascades to all namespaced objects within its boundary, but cluster-scoped resources exist independently outside any namespace.

</details>

## 30. ResourceQuota

**Part 1 — Technical Discussion:** ResourceQuota limits aggregate resource consumption or object counts within a namespace. Admission can reject new or updated objects when their requests, limits, storage, or count would exceed the quota, protecting shared clusters from one tenant exhausting capacity. Quotas work best with LimitRanges, accurate requests, monitoring, and enough headroom for controllers and system objects.

![ResourceQuota technical illustration](generated/kubernetes-apartment-complex/30-technical.png)

**Technical perspective:** ResourceQuota limits aggregate consumption or object counts within a namespace. It protects shared clusters from one team exhausting CPU, memory, storage, or API objects, and can require requests or limits before admission. Quota must be paired with LimitRanges, monitoring, and realistic capacity planning; otherwise valid workloads may be rejected unexpectedly.


### Component architecture flow

<iframe src="diagrams/topic-30.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-30.html](diagrams/topic-30.html).

**Part 2 — Analogy / Zine:** A posted occupancy limit sign on a fenced section — once it's full, the front desk simply refuses to let anyone else move in.

![ResourceQuota zine illustration](generated/kubernetes-apartment-complex/30-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ResourceQuota — The Occupancy Limit Sign"
* (Caption): "Caps the total resources or object counts a single Namespace (fenced section) is allowed to consume."

**Further reading**

- [Resource quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

### Demo — ResourceQuota

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace demo-ns

YAML  (quota-demo.yaml)
  apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: pod-limit
  spec:
    hard:
      pods: "2"

STEPS
  1. kubectl apply -f quota-demo.yaml -n demo-ns
  2. kubectl run p1 --image=nginx -n demo-ns
  3. kubectl run p2 --image=nginx -n demo-ns
  4. kubectl run p3 --image=nginx -n demo-ns   # rejected
  5. kubectl describe quota pod-limit -n demo-ns

WHAT YOU SHOULD SEE
  The third Pod is refused with: exceeded quota: pod-limit, requested: pods=1, used: pods=2, limited: pods=2.

CLEANUP
  kubectl delete namespace demo-ns

NOTE
  The namespace hit its posted occupancy limit. The namespace is set with -n, so the YAML has no namespace field.
</pre></div>


### Knowledge Check — Quiz

**Q1: If a namespace has a ResourceQuota specifying limits on requests.cpu, what requirement is placed on all pods created in that namespace?**

- [ ] A) Pods must run on bare metal servers.
- [ ] B) Every container in every submitted Pod must explicitly declare a CPU request, or a LimitRange must provide a default.
- [ ] C) Pods cannot use sidecar containers.
- [ ] D) Pods must be scheduled on the control-plane node.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Every container in every submitted Pod must explicitly declare a CPU request, or a LimitRange must provide a default.

**Explanation:** If a quota restricts a resource type, the admission controller rejects any pod that fails to declare an explicit request/limit for that resource.

</details>

**Q2: At what point in the request lifecycle is a ResourceQuota enforced?**

- [ ] A) By the kubelet when launching the container.
- [ ] B) By the ResourceQuota admission plugin in the kube-apiserver during API admission control.
- [ ] C) By the scheduler during node scoring.
- [ ] D) By CoreDNS when resolving DNS queries.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) By the ResourceQuota admission plugin in the kube-apiserver during API admission control.

**Explanation:** Quotas are enforced synchronously by admission controllers before the object is accepted and committed to etcd; violations return HTTP 403 Forbidden.

</details>

## 31. Garbage Collector

**Part 1 — Technical Discussion:** The garbage collector follows ownerReferences to identify dependent objects and remove them when an owner is deleted. Foreground, background, and orphan propagation policies control whether dependents block deletion, disappear asynchronously, or are intentionally retained. Controllers must set ownership deliberately because incorrect references can cause unexpected cleanup or leave unmanaged objects behind.

![Garbage Collector technical illustration](generated/kubernetes-apartment-complex/31-technical.png)

**Technical perspective:** The garbage collector follows ownerReferences to remove dependents when their owner is deleted. This keeps ReplicaSet Pods, Job Pods, and related objects from becoming unmanaged orphans, while propagation policies control foreground, background, or orphan deletion. Incorrect ownership metadata can cause unexpected cleanup, so controllers must establish ownership deliberately.


### Component architecture flow

<iframe src="diagrams/topic-31.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-31.html](diagrams/topic-31.html).

**Part 2 — Analogy / Zine:** The cleanup crew that removes any leftover furniture in a unit once the tenant who ordered it moves out — nothing is left behind unclaimed.

![Garbage Collector zine illustration](generated/kubernetes-apartment-complex/31-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Garbage Collector — The Cleanup Crew"
* (Caption): "Automatically deletes objects whose owner is gone, using owner references to trace and clean up orphans."

**Further reading**

- [Owners and dependents](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)

### Demo — Garbage Collector

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl create deployment gc-demo --image=nginx --replicas=2 -n zine-demo
  2. kubectl rollout status deployment/gc-demo -n zine-demo
  3. kubectl get pods -l app=gc-demo -n zine-demo -o jsonpath='{.items[0].metadata.ownerReferences}'; echo
  4. kubectl get replicaset -l app=gc-demo -n zine-demo
  5. kubectl delete deployment gc-demo -n zine-demo
  6. kubectl get replicaset,pods -l app=gc-demo -n zine-demo   # empty, cascaded

WHAT YOU SHOULD SEE
  The Pod's ownerReferences point to a ReplicaSet. After deleting the Deployment, the ReplicaSet and Pods are gone too.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Nobody deleted the Pods or ReplicaSet directly; deletion cascaded through owner references.
</pre></div>


### Knowledge Check — Quiz

**Q1: How does the Kubernetes Garbage Collector determine which dependent child objects to delete when a parent object is deleted?**

- [ ] A) By scanning container image names for matches.
- [ ] B) By inspecting the metadata.ownerReferences field on child objects pointing to the parent UID.
- [ ] C) By searching for pods with matching creation timestamps.
- [ ] D) By asking the container runtime for process tree IDs.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) By inspecting the metadata.ownerReferences field on child objects pointing to the parent UID.

**Explanation:** Child resources (e.g. ReplicaSets created by a Deployment) maintain an ownerReferences array listing the parent's uid, kind, and apiVersion.

</details>

**Q2: What is the difference between Background cascading deletion and Orphan deletion?**

- [ ] A) Background deletion deletes child objects after or alongside the parent; Orphan deletion leaves child objects running with their owner references cleared.
- [ ] B) Background deletion removes the cluster; Orphan deletion restores from backup.
- [ ] C) Orphan deletion is only used for temporary testing pods.
- [ ] D) Background deletion requires pausing the kubelet.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) Background deletion deletes child objects after or alongside the parent; Orphan deletion leaves child objects running with their owner references cleared.

**Explanation:** With propagationPolicy: Orphan, the parent is removed while child resources survive as unowned, standalone objects.

</details>

## 32. ReplicaSet

**Part 1 — Technical Discussion:** A ReplicaSet reconciles a target count of interchangeable Pods selected by labels. It replaces missing or excess replicas, but it does not provide application-version strategy, rollout pacing, or rollback history. Deployments normally own ReplicaSets so that this low-level count reconciliation is combined with controlled releases.

![ReplicaSet technical illustration](generated/kubernetes-apartment-complex/32-technical.png)

**Technical perspective:** A ReplicaSet maintains a target number of interchangeable Pods selected by labels. It repairs count drift but does not provide rollout strategy, revision history, or application version management. Deployments normally own ReplicaSets because they add controlled replacement and rollback while retaining ReplicaSet reconciliation underneath.


### Component architecture flow

<iframe src="diagrams/topic-32.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-32.html](diagrams/topic-32.html).

**Part 2 — Analogy / Zine:** Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly.

![ReplicaSet zine illustration](generated/kubernetes-apartment-complex/32-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ReplicaSet — The Occupancy Enforcer"
* (Caption): "Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly."

**Further reading**

- [ReplicaSets](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)

### Demo — ReplicaSet

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment rs-demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/rs-demo -n zine-demo

STEPS
  1. kubectl get replicaset -l app=rs-demo -n zine-demo
  2. kubectl delete pod $(kubectl get pods -l app=rs-demo -n zine-demo -o name | head -1) -n zine-demo
  3. kubectl get pods -l app=rs-demo -n zine-demo

WHAT YOU SHOULD SEE
  The ReplicaSet shows DESIRED 3, CURRENT 3, READY 3. After you delete one Pod, a new one appears and the count returns to 3.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The ReplicaSet only cares about the number, not which Pods make it up.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why do modern Kubernetes deployments use Deployments instead of managing ReplicaSets directly?**

- [ ] A) ReplicaSets cannot run on Linux.
- [ ] B) ReplicaSets do not provide declarative rolling updates, revision histories, or automated rollbacks; Deployments manage ReplicaSets to orchestrate those workflows.
- [ ] C) ReplicaSets only support a single replica.
- [ ] D) ReplicaSets bypass kube-proxy.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) ReplicaSets do not provide declarative rolling updates, revision histories, or automated rollbacks; Deployments manage ReplicaSets to orchestrate those workflows.

**Explanation:** A ReplicaSet only maintains an exact pod count; it has no mechanism to update container images with zero downtime. Deployments orchestrate transitions between old and new ReplicaSets.

</details>

**Q2: What type of label selector syntax does a ReplicaSet support that the older ReplicationController lacked?**

- [ ] A) SQL WHERE clauses.
- [ ] B) Set-based requirements (e.g. environment in (production, staging)).
- [ ] C) Regex evaluation on container logs.
- [ ] D) Plain text substring matching only.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Set-based requirements (e.g. environment in (production, staging)).

**Explanation:** ReplicaSets support rich set-based selectors (in, notin, exists), whereas legacy ReplicationControllers only supported exact equality (key = value).

</details>

## 33. Deployment

**Part 1 — Technical Discussion:** A Deployment manages ReplicaSets and turns a Pod-template change into a controlled rollout. Rolling-update limits, readiness, progress deadlines, revision history, and rollback determine how quickly a new version replaces the old one and whether traffic remains available. Deployments suit stateless or externally coordinated workloads; database migrations, API compatibility, and probe quality still require application-level planning.

![Deployment technical illustration](generated/kubernetes-apartment-complex/33-technical.png)

**Technical perspective:** A Deployment turns an application version change into a controlled ReplicaSet transition. Rolling-update limits balance availability against rollout speed, readiness gates prevent unready Pods from receiving traffic, and revision history enables rollback. Deployments make stateless releases repeatable, but state migration, backward compatibility, and probe quality still determine whether an update is safe.


### Component architecture flow

<iframe src="diagrams/topic-33.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-33.html](diagrams/topic-33.html).

**Part 2 — Analogy / Zine:** Manages swapping an entire set of units from a v1 layout to a v2 layout gradually, with a lever to rollback if inspections fail.

![Deployment zine illustration](generated/kubernetes-apartment-complex/33-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Deployment — The Renovation Planner"
* (Caption): "This is what you actually deploy. It creates the ReplicaSets and handles zero-downtime rolling updates."

**Further reading**

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

### Demo — Deployment

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment deploy-demo --image=nginx:1.24 --replicas=3 -n zine-demo
  kubectl rollout status deployment/deploy-demo -n zine-demo

STEPS
  1. kubectl set image deployment/deploy-demo nginx=nginx:1.25 -n zine-demo
  2. kubectl rollout status deployment/deploy-demo -n zine-demo
  3. kubectl get replicaset -l app=deploy-demo -n zine-demo
  4. kubectl rollout history deployment/deploy-demo -n zine-demo
  5. kubectl rollout undo deployment/deploy-demo -n zine-demo
  6. kubectl get deployment deploy-demo -n zine-demo -o jsonpath='{.spec.template.spec.containers[0].image}'; echo

WHAT YOU SHOULD SEE
  Two ReplicaSets appear (old scaling down, new scaling up). After undo the image reads nginx:1.24 again.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The container is named 'nginx' because create deployment names it after the image. Rolling update, then rollback with zero downtime.
</pre></div>


### Knowledge Check — Quiz

**Q1: How does a Deployment perform a RollingUpdate without causing service downtime?**

- [ ] A) It reboots all nodes simultaneously.
- [ ] B) It creates a new ReplicaSet and incrementally scales it up while scaling down the old ReplicaSet according to maxSurge and maxUnavailable parameters.
- [ ] C) It rewrites container binaries in-place inside running pods.
- [ ] D) It redirects traffic to an external maintenance page.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It creates a new ReplicaSet and incrementally scales it up while scaling down the old ReplicaSet according to maxSurge and maxUnavailable parameters.

**Explanation:** The Deployment controller creates a new ReplicaSet for the new revision and shifts traffic replica-by-replica, ensuring healthy pods always satisfy availability thresholds.

</details>

**Q2: How do you roll back a failed Deployment to its previous revision?**

- [ ] A) By deleting the worker nodes.
- [ ] B) Using kubectl rollout undo deployment/<name>.
- [ ] C) By modifying the etcd Raft log manually.
- [ ] D) By restarting the kubelet daemon.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Using kubectl rollout undo deployment/<name>.

**Explanation:** kubectl rollout undo instructs the Deployment controller to roll back the pod template spec to the previous recorded revision in its history.

</details>

## 34. StatefulSet

**Part 1 — Technical Discussion:** A StatefulSet gives replicas stable ordinal names, network identities, and commonly one persistent volume per replica. Ordered creation, updates, and termination can support quorum systems and clustered databases, but the controller does not create replication, consensus, or backups for the application. Operators must understand failover, storage attachment, recovery order, and disruption limits before using it for stateful systems.

![StatefulSet technical illustration](generated/kubernetes-apartment-complex/34-technical.png)

**Technical perspective:** A StatefulSet gives replicas stable ordinal identities, predictable network names, and individually associated storage. Ordered creation and termination can support clustered databases and quorum systems, but StatefulSet does not automatically make an application distributed or consistent. The application must understand identity, failover, storage semantics, and backup/recovery.


### Component architecture flow

<iframe src="diagrams/topic-34.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-34.html](diagrams/topic-34.html).

**Part 2 — Analogy / Zine:** Named, numbered units where the same tenant always returns to the exact same unit with their exact same furniture — never shuffled to a different room.

![StatefulSet zine illustration](generated/kubernetes-apartment-complex/34-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "StatefulSet — The Named Units"
* (Caption): "Manages Pods needing stable identities and persistent storage tied to that identity — each Pod keeps its name and storage across restarts."

**Further reading**

- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

### Demo — StatefulSet

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (statefulset-demo.yaml)
  apiVersion: v1
  kind: Service
  metadata:
    name: web
  spec:
    clusterIP: None
    selector:
      app: web
    ports:
    - port: 80
  ---
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

STEPS
  1. kubectl apply -f statefulset-demo.yaml -n zine-demo
  2. kubectl rollout status statefulset/web -n zine-demo
  3. kubectl get pods -l app=web -n zine-demo   # web-0, web-1, web-2
  4. kubectl delete pod web-1 -n zine-demo
  5. kubectl get pods -l app=web -n zine-demo -w   # Ctrl+C when web-1 is Running again

WHAT YOU SHOULD SEE
  Pods are named web-0, web-1, web-2 and start in order. The replacement comes back as web-1, not a random name.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  A StatefulSet needs a headless Service (clusterIP: None), so the YAML includes one. The tenant returns to the same numbered unit.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why does a StatefulSet require a Headless Service (clusterIP: None)?**

- [ ] A) To encrypt pod network traffic with TLS.
- [ ] B) To provide predictable direct DNS A/SRV records for individual pods (e.g. pod-0.headless-svc.namespace.svc.cluster.local) rather than load-balancing across them.
- [ ] C) Because stateful applications cannot use IP addresses.
- [ ] D) To bypass the Linux kernel iptables rules.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) To provide predictable direct DNS A/SRV records for individual pods (e.g. pod-0.headless-svc.namespace.svc.cluster.local) rather than load-balancing across them.

**Explanation:** Clustered stateful applications (databases, ZooKeeper, Kafka) need to address specific ordinal members directly for clustering and replication.

</details>

**Q2: When a StatefulSet replica pod is deleted or crashes, what happens to its PersistentVolumeClaim?**

- [ ] A) The PVC is automatically deleted and recreated fresh.
- [ ] B) The PVC and storage are retained and automatically reattached to the replacement pod with the same ordinal index.
- [ ] C) The PVC is wiped and reformatted.
- [ ] D) The storage volume is converted into an emptyDir volume.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The PVC and storage are retained and automatically reattached to the replacement pod with the same ordinal index.

**Explanation:** StatefulSet storage is persistent and sticky; data-web-0 is never deleted automatically when web-0 terminates, preserving data upon pod recreation.

</details>

## 35. DaemonSet

**Part 1 — Technical Discussion:** A DaemonSet expresses node coverage rather than a fixed replica count: one Pod is scheduled on every matching Node, including eligible Nodes added later. It is suited to log collectors, monitoring agents, storage helpers, and networking components that need local access. Selectors, taints, tolerations, host access, and resource requests determine coverage and the amount of workload capacity consumed.

![DaemonSet technical illustration](generated/kubernetes-apartment-complex/35-technical.png)

**Technical perspective:** A DaemonSet expresses node coverage rather than a replica count: one Pod is scheduled on each matching node, including nodes added later. This suits agents that need local access, such as log collectors, monitors, and networking components. Taints, tolerations, selectors, and resource requests determine where the agent can run and whether it competes with workloads.


### Component architecture flow

<iframe src="diagrams/topic-35.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-35.html](diagrams/topic-35.html).

**Part 2 — Analogy / Zine:** A dedicated fire extinguisher mounted in every single building — one per building, automatically, no exceptions.

![DaemonSet zine illustration](generated/kubernetes-apartment-complex/35-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "DaemonSet — The Fire Extinguisher on Every Floor"
* (Caption): "Ensures exactly one copy of a Pod runs on every Node — often used for node-level agents like log collectors."

**Further reading**

- [DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)

### Demo — DaemonSet

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (daemonset-demo.yaml)
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

STEPS
  1. kubectl apply -f daemonset-demo.yaml -n zine-demo
  2. kubectl rollout status daemonset/node-agent -n zine-demo
  3. kubectl get pods -l app=node-agent -n zine-demo -o wide
  4. kubectl get nodes --no-headers | wc -l   # total nodes; compare with the Pod count

WHAT YOU SHOULD SEE
  One Pod runs on each worker node. On a cluster whose control-plane node is tainted (the default), the count is the number of worker nodes, one less than the total node count.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Add a toleration for node-role.kubernetes.io/control-plane:NoSchedule to the Pod template if you want the control-plane node included; the Pod count then equals the node count.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the primary use case for a DaemonSet compared to a standard Deployment?**

- [ ] A) Running short batch jobs that exit with code 0.
- [ ] B) Running cluster infrastructure agents (such as log shippers, monitoring agents, or CNI plugins) that must run exactly once on every eligible node.
- [ ] C) Running stateless web frontends behind an Ingress controller.
- [ ] D) Managing relational database failover.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Running cluster infrastructure agents (such as log shippers, monitoring agents, or CNI plugins) that must run exactly once on every eligible node.

**Explanation:** A DaemonSet ensures that all (or some matching) nodes run a copy of a pod, automatically scaling as nodes are added or removed from the cluster.

</details>

**Q2: If a new worker node is added to a Kubernetes cluster, how does a DaemonSet respond?**

- [ ] A) It waits for manual administrator approval before acting.
- [ ] B) The DaemonSet controller detects the new node and automatically schedules an agent pod onto it.
- [ ] C) It evicts pods from older nodes to free up licenses.
- [ ] D) It restarts all pods in the cluster.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The DaemonSet controller detects the new node and automatically schedules an agent pod onto it.

**Explanation:** The DaemonSet controller continuously watches for node additions and ensures immediate agent coverage without manual intervention.

</details>

## 36. Job

**Part 1 — Technical Discussion:** A Job represents finite work and tracks successful and failed Pod completions. It can retry failures, run completions in parallel, and retain or clean up finished Pods according to policy, making it appropriate for migrations, batch processing, and maintenance. The task should be idempotent or otherwise safe to retry because a failure can occur after work has partially completed.

![Job technical illustration](generated/kubernetes-apartment-complex/36-technical.png)

**Technical perspective:** A Job represents finite work and tracks successful and failed Pod completions. It can retry failures, run parallel workers, and retain or clean up finished Pods according to policy. Jobs are a better fit than Deployments for migrations, batch processing, and one-time maintenance because completion—not continuous availability—is the desired state.


### Component architecture flow

<iframe src="diagrams/topic-36.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-36.html](diagrams/topic-36.html).

**Part 2 — Analogy / Zine:** A one-time moving crew hired to move a single tenant's boxes — once the job is done, the crew packs up and leaves for good, not staying on payroll.

![Job zine illustration](generated/kubernetes-apartment-complex/36-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Job — The One-Time Moving Crew"
* (Caption): "Runs Pods to completion for a finite task, then stops — unlike a Deployment, it doesn't keep Pods running forever."

**Further reading**

- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)

### Demo — Job

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (job-demo.yaml)
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

STEPS
  1. kubectl apply -f job-demo.yaml -n zine-demo
  2. kubectl get jobs -n zine-demo -w   # Ctrl+C when COMPLETIONS is 1/1
  3. kubectl logs job/one-time-task -n zine-demo

WHAT YOU SHOULD SEE
  COMPLETIONS goes from 0/1 to 1/1. The logs print 'doing the move' then 'done'. The Pod ends as Completed.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Once it hits 1/1 the Job stops; the crew finished the move.
</pre></div>


### Knowledge Check — Quiz

**Q1: What differentiates a Job's container lifecycle from a Deployment's container lifecycle?**

- [ ] A) Jobs only run on Linux; Deployments run on Windows.
- [ ] B) A Job runs containers until a designated number of completions succeed (exit 0), whereas a Deployment continuously restarts containers to keep them running indefinitely.
- [ ] C) Job containers cannot access persistent volumes.
- [ ] D) Jobs bypass the Kubernetes API server.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) A Job runs containers until a designated number of completions succeed (exit 0), whereas a Deployment continuously restarts containers to keep them running indefinitely.

**Explanation:** Jobs supervise batch workloads designed to terminate upon completion; Deployments supervise persistent services designed to never terminate.

</details>

**Q2: What happens to a Job's pods after the workload has successfully completed?**

- [ ] A) They are immediately deleted along with their logs.
- [ ] B) The pods are kept in Completed status so operators can inspect logs and exit statuses until the Job is cleaned up.
- [ ] C) The pods automatically transition to running web servers.
- [ ] D) The worker node is shut down.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The pods are kept in Completed status so operators can inspect logs and exit statuses until the Job is cleaned up.

**Explanation:** Retaining completed pods allows operators to run kubectl logs and view output; automated cleanup can be managed via ttlSecondsAfterFinished.

</details>

## 37. CronJob

**Part 1 — Technical Discussion:** A CronJob creates Jobs according to a cron schedule and transfers the actual work and retry behavior to each Job. Concurrency policy, missed-run handling, starting deadlines, history limits, time zones, and idempotency determine whether recurring execution is safe. Scheduling is not an exactly-once guarantee, so jobs must tolerate retries, controller restarts, and—depending on policy—overlap.

![CronJob technical illustration](generated/kubernetes-apartment-complex/37-technical.png)

**Technical perspective:** A CronJob creates Jobs from a schedule, adding automation for backups, reports, cleanup, and other recurring work. Concurrency policy, missed schedules, starting deadlines, history limits, and idempotency determine whether repeated runs are safe. A CronJob schedules work; it does not guarantee exactly-once execution, so the task must tolerate retries and overlap appropriately.


### Component architecture flow

<iframe src="diagrams/topic-37.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-37.html](diagrams/topic-37.html).

**Part 2 — Analogy / Zine:** The scheduled overnight cleaning crew that shows up automatically every night at 2 AM, does the job, and leaves — nobody has to call them each time.

![CronJob zine illustration](generated/kubernetes-apartment-complex/37-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "CronJob — The Scheduled Night Crew"
* (Caption): "Creates Jobs on a repeating schedule — like a nightly backup task that runs automatically without anyone triggering it."

**Further reading**

- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)

### Demo — CronJob

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (cronjob-demo.yaml)
  apiVersion: batch/v1
  kind: CronJob
  metadata:
    name: nightly-task
  spec:
    schedule: "*/2 * * * *"
    jobTemplate:
      spec:
        template:
          spec:
            containers:
            - name: task
              image: busybox
              command: ["sh", "-c", "echo nightly cleanup ran"]
            restartPolicy: Never

STEPS
  1. kubectl apply -f cronjob-demo.yaml -n zine-demo
  2. kubectl get cronjob nightly-task -n zine-demo
  3. kubectl get jobs -n zine-demo -w   # wait up to 2 minutes; Ctrl+C after a Job appears
  4. kubectl logs job/$(kubectl get jobs -n zine-demo -o name | head -1 | cut -d/ -f2) -n zine-demo

WHAT YOU SHOULD SEE
  A new Job appears every 2 minutes with no command from you. Its logs print 'nightly cleanup ran'.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The schedule is every 2 minutes for the demo; a real nightly job would use 0 2 * * *.
</pre></div>


### Knowledge Check — Quiz

**Q1: What does the concurrencyPolicy: Forbid setting on a CronJob do if a previous job execution is still running when the next scheduled interval arrives?**

- [ ] A) It kills the currently running job immediately.
- [ ] B) It skips the new execution until the currently running job has completed.
- [ ] C) It crashes the CronJob controller.
- [ ] D) It scales the worker node capacity.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It skips the new execution until the currently running job has completed.

**Explanation:** Forbid prevents concurrent executions of the same job, avoiding duplicate batch processing or database lock contention.

</details>

**Q2: What Kubernetes object does the CronJob controller create when a scheduled trigger fires?**

- [ ] A) A bare container process via SSH.
- [ ] B) A standard Job object, which in turn creates the execution pod.
- [ ] C) A StatefulSet.
- [ ] D) An Ingress rule.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) A standard Job object, which in turn creates the execution pod.

**Explanation:** CronJob operates as a higher-level orchestrator: on schedule, it instantiates a standard Job based on its jobTemplate.

</details>

## 38. ReplicationController (legacy)

**Part 1 — Technical Discussion:** ReplicationController is the predecessor to ReplicaSet and maintains a fixed count of Pods selected by its older selector model. It can repair replica-count drift but lacks the expressive selectors and modern rollout relationship provided by ReplicaSet and Deployment. It remains relevant when operating legacy manifests, but new workloads should normally use Deployments.

![ReplicationController (legacy) technical illustration](generated/kubernetes-apartment-complex/38-technical.png)

**Technical perspective:** ReplicationController is the predecessor to ReplicaSet. It maintains a fixed count of matching Pods, but its selector model is less expressive and it is not the normal choice for new applications. Understanding it matters when operating older clusters or manifests, while migrations generally move to Deployments and ReplicaSets.


### Component architecture flow

<iframe src="diagrams/topic-38.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-38.html](diagrams/topic-38.html).

**Part 2 — Analogy / Zine:** The original, retired occupancy-enforcer clipboard system the complex used before the newer, more flexible enforcer took over — still technically works, but nobody sets it up new anymore.

![ReplicationController (legacy) zine illustration](generated/kubernetes-apartment-complex/38-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ReplicationController — The Retired Enforcer"
* (Caption): "The legacy predecessor to ReplicaSet — functionally similar, but superseded by more flexible label selectors."

**Further reading**

- [ReplicationController](https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/)

### Demo — ReplicationController (legacy)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (rc-demo.yaml)
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

STEPS
  1. kubectl apply -f rc-demo.yaml -n zine-demo
  2. kubectl get rc rc-demo -n zine-demo
  3. kubectl delete pod $(kubectl get pods -l app=rc-demo -n zine-demo -o name | head -1) -n zine-demo
  4. kubectl get pods -l app=rc-demo -n zine-demo
  5. kubectl explain replicationcontroller | head -8

WHAT YOU SHOULD SEE
  It self-heals exactly like a ReplicaSet: delete a Pod and a new one appears.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Still works, but nobody builds new systems on it. Use a Deployment instead.
</pre></div>


### Knowledge Check — Quiz

**Q1: Why is ReplicationController considered legacy in modern Kubernetes clusters?**

- [ ] A) It cannot run in containerized environments.
- [ ] B) It was superseded by Deployments and ReplicaSets, which offer set-based selectors, declarative rolling updates, and rollback capabilities.
- [ ] C) It does not support Docker containers.
- [ ] D) It only works on single-node clusters.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) It was superseded by Deployments and ReplicaSets, which offer set-based selectors, declarative rolling updates, and rollback capabilities.

**Explanation:** ReplicationController was the original v1 replica primitive; Deployments and ReplicaSets replaced it with superior rollout orchestration and selector power.

</details>

**Q2: What label selector restriction does a ReplicationController have?**

- [ ] A) It only supports equality-based selectors (key = value).
- [ ] B) It cannot select pods by label at all.
- [ ] C) It requires JSONPath expressions.
- [ ] D) It only works with pods named default.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) It only supports equality-based selectors (key = value).

**Explanation:** ReplicationController only understands exact equality (app = frontend), while modern controllers support expressive set-based selectors (app in (frontend, api)).

</details>

## 39. HorizontalPodAutoscaler (HPA)

**Part 1 — Technical Discussion:** HPA adjusts a scalable target’s replica count from observed resource, custom, or external metrics. It compares current values with a target, applies stabilization and scaling policies, and changes the workload’s desired replicas; it does not resize an individual Pod. Effective horizontal scaling requires usable metrics, meaningful resource requests, startup tolerance, sufficient cluster capacity, and an application that can distribute traffic across replicas.

![HorizontalPodAutoscaler (HPA) technical illustration](generated/kubernetes-apartment-complex/39-technical.png)

**Technical perspective:** HPA changes the number of replicas based on observed metrics and a target such as average CPU utilization or an external/custom metric. Horizontal scaling improves concurrency and availability when the application is stateless or replicated, but it needs accurate requests, metrics availability, startup tolerance, and a workload that can actually share traffic across replicas.


### Component architecture flow

<iframe src="diagrams/topic-39.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-39.html](diagrams/topic-39.html).

**Part 2 — Analogy / Zine:** The staffing manager who calls in more substitute teachers automatically when the lunch rush hits a certain crowd size, and sends them home once things quiet down.

![HorizontalPodAutoscaler (HPA) zine illustration](generated/kubernetes-apartment-complex/39-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "HorizontalPodAutoscaler — The Staffing Manager"
* (Caption): "Automatically adjusts the number of Pod replicas based on CPU/memory usage — scaling out under load, back in when it drops."

**Further reading**

- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Autoscaling concepts](https://kubernetes.io/docs/concepts/workloads/autoscaling/)

### Demo — HorizontalPodAutoscaler (HPA)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl get deployment metrics-server -n kube-system || (kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml && kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]')
  kubectl create namespace zine-demo
  kubectl create deployment hpa-demo --image=registry.k8s.io/hpa-example -n zine-demo
  kubectl set resources deployment hpa-demo --requests=cpu=200m -n zine-demo
  kubectl rollout status deployment/hpa-demo -n zine-demo
  kubectl expose deployment hpa-demo --port=80 -n zine-demo

STEPS
  1. kubectl autoscale deployment hpa-demo --cpu-percent=50 --min=1 --max=5 -n zine-demo
  2. kubectl run load-generator --image=busybox -n zine-demo --restart=Never -- sh -c 'while true; do wget -q -O- http://hpa-demo; done'
  3. kubectl get hpa hpa-demo -n zine-demo -w   # Ctrl+C after REPLICAS climbs above 1
  4. kubectl delete pod load-generator -n zine-demo
  5. kubectl get hpa hpa-demo -n zine-demo -w   # replicas fall back after about 5 minutes

WHAT YOU SHOULD SEE
  TARGETS climbs above 50% and REPLICAS rises toward 5. After the load stops it falls back to 1.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Needs metrics-server. Until it reports, TARGETS shows &lt;unknown&gt;. Scale-down is deliberately slow (about 5 minutes).
</pre></div>


### Knowledge Check — Quiz

**Q1: What component must be running in the cluster for the HorizontalPodAutoscaler to scale based on CPU and memory utilization?**

- [ ] A) An NFS storage server.
- [ ] B) The metrics-server (or a custom metrics provider implementing the Metrics API).
- [ ] C) Docker Desktop on macOS.
- [ ] D) A Ceph storage cluster.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The metrics-server (or a custom metrics provider implementing the Metrics API).

**Explanation:** HPA queries metrics.k8s.io to evaluate resource utilization; metrics-server collects container cgroup metrics from node kubelets and exposes them through this API.

</details>

**Q2: Why does HPA have a default stabilization window (typically 5 minutes) for scaling down replicas?**

- [ ] A) Because the kube-apiserver is throttled to 1 write per 5 minutes.
- [ ] B) To prevent 'flapping' (rapid oscillation of scaling up and down in response to transient metric spikes).
- [ ] C) To allow container images to download.
- [ ] D) To wait for node operating system updates.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) To prevent 'flapping' (rapid oscillation of scaling up and down in response to transient metric spikes).

**Explanation:** Rapid scaling oscillations degrade application stability; the cooldown window smooths out scale-down decisions over time.

</details>

## 40. VerticalPodAutoscaler (VPA)

**Part 1 — Technical Discussion:** VPA analyzes historical usage and produces CPU and memory recommendations, or applies them according to its update mode. Applying a new recommendation may evict and recreate Pods so that scheduling can use the new requests, which makes disruption and capacity planning important. VPA is complementary to some workloads but can conflict with HPA when both react to the same resource signal, and it requires the VPA add-on.

![VerticalPodAutoscaler (VPA) technical illustration](generated/kubernetes-apartment-complex/40-technical.png)

**Technical perspective:** VPA adjusts or recommends Pod resource requests and limits using historical usage. It is useful when sizing is difficult or workload demand changes vertically, but applying recommendations can restart Pods and may conflict with HPA or tightly constrained scheduling. VPA therefore requires an explicit update mode, disruption planning, and attention to workload eviction behavior.


### Component architecture flow

<iframe src="diagrams/topic-40.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-40.html](diagrams/topic-40.html).

**Part 2 — Analogy / Zine:** Instead of calling in more staff, this manager just gives one tenant a bigger unit when they clearly need more space, and downsizes them if they don't need it anymore.

![VerticalPodAutoscaler (VPA) zine illustration](generated/kubernetes-apartment-complex/40-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "VerticalPodAutoscaler — The Unit Resizer"
* (Caption): "Automatically adjusts a Pod's CPU/memory requests based on usage history — resizing the Pod itself instead of adding more Pods."

**Further reading**

- [Vertical Pod Autoscaling](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Autoscaling concepts](https://kubernetes.io/docs/concepts/workloads/autoscaling/)

### Demo — VerticalPodAutoscaler (VPA)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  # Install the VPA add-on first: git clone https://github.com/kubernetes/autoscaler.git && cd autoscaler/vertical-pod-autoscaler && ./hack/vpa-up.sh
  kubectl get pods -n kube-system | grep vpa   # recommender, updater, admission-controller must be Running
  kubectl create namespace zine-demo
  kubectl create deployment hpa-demo --image=registry.k8s.io/hpa-example -n zine-demo
  kubectl set resources deployment hpa-demo --requests=cpu=100m -n zine-demo
  kubectl rollout status deployment/hpa-demo -n zine-demo

YAML  (vpa-demo.yaml)
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

STEPS
  1. kubectl apply -f vpa-demo.yaml -n zine-demo
  2. sleep 120   # give the recommender time to observe usage
  3. kubectl describe vpa vpa-demo -n zine-demo   # see Recommendation

WHAT YOU SHOULD SEE
  Under Recommendation you see Lower Bound, Target and Upper Bound for CPU and memory, based on observed usage.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  In Auto mode VPA evicts and recreates the Pod with the new sizes; use updateMode: "Off" if you only want recommendations. The Deployment is created fresh here, so this demo does not depend on entry 39.
</pre></div>


### Knowledge Check — Quiz

**Q1: What is the primary operational difference between HPA and VPA?**

- [ ] A) HPA scales the number of Pod replicas (horizontal scaling), while VPA adjusts the CPU and memory requests/limits of existing containers (vertical scaling).
- [ ] B) HPA only works on worker nodes; VPA only works on the control plane.
- [ ] C) HPA scales storage; VPA scales networking.
- [ ] D) HPA requires Windows; VPA requires Linux.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** A) HPA scales the number of Pod replicas (horizontal scaling), while VPA adjusts the CPU and memory requests/limits of existing containers (vertical scaling).

**Explanation:** HPA adds/removes pod replicas to handle load; VPA right-sizes individual container CPU and RAM requests based on historical consumption patterns.

</details>

**Q2: In updateMode: 'Auto', how does VPA apply updated CPU and memory recommendations to a running Pod?**

- [ ] A) By dynamically adjusting kernel memory without restarting the container.
- [ ] B) By evicting the existing Pod so that the workload controller recreates it, at which point the VPA mutating admission webhook injects the new resource values.
- [ ] C) By editing the host BIOS settings.
- [ ] D) By changing the container image.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) By evicting the existing Pod so that the workload controller recreates it, at which point the VPA mutating admission webhook injects the new resource values.

**Explanation:** In current Kubernetes releases, pod resource changes require pod recreation; VPA evicts the pod and its admission webhook mutates the pod spec during recreation.

</details>

## 41. Pod Disruption Budget (PDB)

**Part 1 — Technical Discussion:** A PodDisruptionBudget limits voluntary evictions of selected Pods during operations such as node drain or voluntary cluster maintenance. `minAvailable` and `maxUnavailable` express an availability requirement, but the budget does not prevent crashes, hardware loss, or every involuntary disruption. A strict budget can also block maintenance when there are too few replicas or no spare schedulable Nodes, so it must match real capacity and recovery behavior.

![Pod Disruption Budget (PDB) technical illustration](generated/kubernetes-apartment-complex/41-technical.png)

**Technical perspective:** A PodDisruptionBudget limits voluntary evictions during planned operations such as node drains; it does not protect against crashes, hardware failure, or all forms of involuntary disruption. A realistic budget balances availability with maintenance progress and only works when the application has enough replicas and schedulable capacity elsewhere.


### Component architecture flow

<iframe src="diagrams/topic-41.html" width="100%" height="560" style="border:none;"></iframe>

> [!TIP]
> View the interactive animated diagram in [diagrams/topic-41.html](diagrams/topic-41.html).

**Part 2 — Analogy / Zine:** A rule posted during planned building maintenance: at least 2 units in this wing must stay occupied and undisturbed at any given time, no matter how many maintenance requests come in at once.

![Pod Disruption Budget (PDB) zine illustration](generated/kubernetes-apartment-complex/41-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Pod Disruption Budget — The Maintenance Limit Rule"
* (Caption): "Limits how many Pods can be voluntarily disrupted at once during planned maintenance, protecting availability."

**Further reading**

- [Pod disruption budgets](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Eviction API](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/)

### Demo — Pod Disruption Budget (PDB)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo

YAML  (pdb-demo.yaml)
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: demo-pdb
  spec:
    minAvailable: 2
    selector:
      matchLabels:
        app: demo

STEPS
  1. kubectl apply -f pdb-demo.yaml -n zine-demo
  2. kubectl get pdb demo-pdb -n zine-demo   # ALLOWED DISRUPTIONS should be 1
  3. kubectl get pods -l app=demo -n zine-demo -o wide
  4. NODE=$(kubectl get pods -l app=demo -n zine-demo -o jsonpath='{.items[0].spec.nodeName}')
  5. kubectl drain $NODE --ignore-daemonsets --delete-emptydir-data --timeout=60s

WHAT YOU SHOULD SEE
  The drain evicts Pods one at a time and stalls with 'Cannot evict pod ... would violate the pod's disruption budget' once only 2 remain. The --timeout=60s ends the drain by itself; you can also press Ctrl+C.

CLEANUP
  kubectl uncordon $NODE
  kubectl delete namespace zine-demo

NOTE
  Needs 2 or more worker nodes so evicted Pods have somewhere to go. Do not drain your only node.
</pre></div>


### Knowledge Check — Quiz

**Q1: What type of disruptions does a Pod Disruption Budget (PDB) protect against?**

- [ ] A) Involuntary disruptions like hardware power loss or kernel panics.
- [ ] B) Voluntary disruptions initiated by cluster administrators or automation, such as kubectl drain, node upgrades, and cluster autoscaler scale-down.
- [ ] C) Malicious cyberattacks on the network.
- [ ] D) Pod crashes caused by out-of-memory (OOM) errors.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) Voluntary disruptions initiated by cluster administrators or automation, such as kubectl drain, node upgrades, and cluster autoscaler scale-down.

**Explanation:** PDBs govern voluntary management operations; they cannot prevent hardware crashes, but they intercept Eviction API calls during node maintenance to safeguard minimum available replicas.

</details>

**Q2: What happens if an administrator runs kubectl drain node-1 and evicting a pod would violate its PDB minAvailable constraint?**

- [ ] A) The node drain immediately deletes the pod forcefully.
- [ ] B) The Eviction API rejects or delays the eviction request, causing kubectl drain to wait or retry until sufficient healthy replicas exist elsewhere.
- [ ] C) The PDB is automatically deleted.
- [ ] D) The entire cluster is placed in read-only mode.

<details>
<summary>Reveal Answer &amp; Explanation</summary>

**Correct Answer:** B) The Eviction API rejects or delays the eviction request, causing kubectl drain to wait or retry until sufficient healthy replicas exist elsewhere.

**Explanation:** The Eviction API checks active PDBs and returns HTTP 429 (Too Many Requests) if an eviction would breach the budget, protecting application availability during maintenance.

</details>
