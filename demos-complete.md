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
2. These demos target kind on macOS with Docker Desktop. Docker is the host-side
   runtime that creates the kind node containers; inside each kind node, kubelet
   talks to containerd through CRI.
3. Recommended: a multi-node kind cluster (1 control-plane + 2 workers).
     kind create cluster --name zine --config kind-multinode.yaml
   kind-multinode.yaml:
     kind: Cluster
     apiVersion: kind.x-k8s.io/v1alpha4
     nodes:
     - role: control-plane
       kubeadmConfigPatches:
       - |
         kind: InitConfiguration
         nodeRegistration:
           kubeletExtraArgs:
             node-labels: "ingress-ready=true"
       extraPortMappings:
       - containerPort: 80
         hostPort: 80
         protocol: TCP
       - containerPort: 443
         hostPort: 443
         protocol: TCP
     - role: worker
     - role: worker
   The extra port mappings are used by the kind Ingress demo. If the cluster
   already exists without them, recreate it before running demo 18.
4. Every demo uses its own namespace (zine-demo, or demo-ns / other-ns where stated)
   and cleans up after itself, so demos can be run in ANY order.
5. Save each YAML block to the file named above it, then run the commands.
6. Add-ons some demos need first:
     - 18 Ingress: ingress-nginx's kind provider manifest
     - 19 NetworkPolicy: a CNI that enforces policy (Calico or Cilium; kindnet does not)
     - 39 HPA: metrics-server
     - 40 VPA: the VPA add-on
     - 41 PDB and 28 Node controller: two or more worker nodes
7. Commands marked 'run on the node' use Docker Desktop to enter a kind node:
     docker exec -it zine-control-plane bash
     docker exec -it zine-worker bash
   Kind node names for this cluster are zine-control-plane, zine-worker,
   and zine-worker2. Run crictl and host-network checks inside those containers,
   not on the macOS host.
8. Text after # on a command line is an explanation, not part of the command.

Quick reference - demos that need something extra:
  add-on:      18, 19, 39, 40
  2+ workers:  28, 41 (and 2, 35 read best with them)
  on the node: 4, 8, 9, 10, 11, 28

## 1. The Cluster (Why Kubernetes?)

**Part 1 — Technical Discussion:** Kubernetes is a declarative control system for managing compute, networking, and storage across a group of machines. You submit desired state through the API, and the control plane schedules Pods, reconciles drift, and reports status while Nodes execute the work. This removes manual placement from the normal workflow, but the cluster itself still requires capacity planning, security, upgrades, and observability.

![The Cluster (Why Kubernetes?) technical illustration](generated/kubernetes-apartment-complex/01-technical.png)

**Technical perspective:** Kubernetes provides a declarative control plane, scheduling, self-healing, service discovery, and rollout automation across many machines. Compared with standalone VMs, it removes the need to place and repair each workload manually, improves utilization through bin-packing, and makes the desired state reproducible. The trade-off is additional platform complexity: the cluster itself needs lifecycle management, observability, security, and capacity planning.

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

```text
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
```

## 2. Control Plane vs. Worker Nodes

**Part 1 — Technical Discussion:** The control plane exposes the API, stores cluster state, schedules Pods, and runs controllers; worker Nodes provide the kubelet, container runtime, and networking needed to execute them. A worker failure can trigger replacement or rescheduling when replicas and capacity are available, while an isolated control-plane failure may leave existing processes running but stops reliable changes and new placement decisions. High availability therefore requires redundant control-plane components and workloads spread across failure domains.

![Control Plane vs. Worker Nodes technical illustration](generated/kubernetes-apartment-complex/02-technical.png)

**Technical perspective:** The separation of control plane and workers creates a clear failure boundary. Workers execute Pods, while the control plane stores intent and coordinates scheduling and reconciliation. This lets workloads continue during some control-plane interruptions, while worker failure can be handled through rescheduling when replicas and capacity are available. High availability requires multiple control-plane instances and appropriately distributed workers.

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

```text
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
```

## 3. kube-apiserver

**Part 1 — Technical Discussion:** kube-apiserver is the authenticated and validated HTTP API boundary for Kubernetes. kubectl, controllers, the scheduler, admission webhooks, and external automation all use it to read objects, submit desired state, and watch changes. It performs authentication, authorization, admission, conversion, and concurrency handling, and is the only control-plane component that directly reads or writes etcd.

![kube-apiserver technical illustration](generated/kubernetes-apartment-complex/03-technical.png)

**Technical perspective:** The API server is the authenticated, authorized, validated concurrency boundary for cluster state. Clients submit declarative objects through the Kubernetes API; admission, versioning, validation, and watches provide a consistent interface for controllers and tools. Keeping etcd behind the API server centralizes policy and prevents components from making ungoverned direct writes.

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

```text
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
```

## 4. etcd

**Part 1 — Technical Discussion:** etcd is a strongly consistent distributed key-value store that holds Kubernetes API state, including specifications, metadata, and status needed by controllers. The API server uses it as the authoritative record, so quorum, disk latency, encryption, access control, snapshots, and restore testing directly affect control-plane reliability. Existing containers may continue briefly during an etcd outage, but new decisions and durable state changes cannot safely converge.

![etcd technical illustration](generated/kubernetes-apartment-complex/04-technical.png)

**Technical perspective:** etcd stores Kubernetes state as a strongly consistent key-value database. Because the API server reconstructs the cluster’s desired and observed state from it, backups, quorum, encryption, latency, and restore testing are critical operational concerns. An etcd outage does not necessarily stop already-running containers immediately, but it prevents reliable control-plane progress and changes.

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

```text
SETUP
  ETCD_POD=$(kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}')
  echo $ETCD_POD

STEPS
  1. kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key get /registry/pods --prefix --keys-only | head -20

WHAT YOU SHOULD SEE
  A list of keys such as /registry/pods/kube-system/etcd-<node>. These are the 'filing cabinets' behind the API server.

CLEANUP
  (nothing to clean up)

NOTE
  Works on the kubeadm-style control plane used by kind. Managed clusters (EKS, GKE, AKS) hide etcd, so this will not work there. Do not use -it with a piped command.
```

## 5. kube-scheduler

**Part 1 — Technical Discussion:** kube-scheduler assigns an unscheduled Pod to a feasible Node; it does not start the container itself. It filters Nodes using resource requests, taints, tolerations, affinity, topology, volumes, and other constraints, then scores the remaining candidates and writes a binding. The kubelet notices that assignment and performs the actual launch.

![kube-scheduler technical illustration](generated/kubernetes-apartment-complex/05-technical.png)

**Technical perspective:** The scheduler separates placement decision-making from execution. It filters nodes that violate resource, taint, affinity, topology, or policy constraints, then scores feasible nodes and binds the Pod to the selected one. This lets operators express placement intent without hard-coding a server, while requests and limits help the scheduler make capacity-aware decisions.

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

```text
SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl run demo-pod --image=nginx -n zine-demo
  2. kubectl wait --for=condition=Ready pod/demo-pod -n zine-demo --timeout=60s
  3. kubectl get pod demo-pod -n zine-demo -o wide
  4. kubectl describe pod demo-pod -n zine-demo | grep -A6 Events

WHAT YOU SHOULD SEE
  Events shows 'Scheduled ... Successfully assigned zine-demo/demo-pod to <node>'. The NODE column matches.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  The Scheduled event is the exact moment the scheduler picked a node.
```

## 6. kube-controller-manager

**Part 1 — Technical Discussion:** kube-controller-manager hosts independent reconciliation loops for objects such as Nodes, endpoints, namespaces, and replication resources. Each controller watches API events, compares desired and observed state, and makes idempotent API changes until the difference converges. This eventual-consistency model enables self-healing, but bad probes, ownership, or resource settings can cause repeated ineffective repairs.

![kube-controller-manager technical illustration](generated/kubernetes-apartment-complex/06-technical.png)

**Technical perspective:** Controllers implement Kubernetes reconciliation: they observe API objects and cluster state, compute the difference, and issue idempotent changes until the difference disappears. This is why deleting a Pod managed by a Deployment is temporary. The model favors eventual convergence and automation, but requires correct ownership, probes, resource settings, and observability to avoid repeatedly reconciling a broken design.

**Part 2 — Analogy / Zine:** Clipboard inspectors walking endless loops to ensure reality matches the promised plan, fixing discrepancies automatically.

![kube-controller-manager zine illustration](generated/kubernetes-apartment-complex/06-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kube-controller-manager — The Looping Inspectors"
* (Caption): "Background control loops that detect crashed Pods and spin up replacements to match your deployment YAML."

**Further reading**

- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)

### Demo — kube-controller-manager

```text
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
```

## 7. cloud-controller-manager

**Part 1 — Technical Discussion:** cloud-controller-manager isolates provider-specific integrations from the Kubernetes core. Its controllers translate Services, Nodes, routes, and persistent volumes into cloud API operations, then write the resulting addresses, identities, and status back to Kubernetes. Provisioning depends on cloud credentials, quotas, API latency, regional topology, and provider-specific behavior.

![cloud-controller-manager technical illustration](generated/kubernetes-apartment-complex/07-technical.png)

**Technical perspective:** The cloud controller manager keeps provider-specific integration outside the Kubernetes core. It translates Services, Nodes, routes, and cloud volumes into provider API operations and reports their status back through Kubernetes objects. This portability is valuable across clouds, but behavior depends on provider identity, permissions, quotas, latency, and the provider’s implementation of the integration.

**Part 2 — Analogy / Zine:** Signs paperwork to connect external utilities like rented parking gates.

![cloud-controller-manager zine illustration](generated/kubernetes-apartment-complex/07-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "cloud-controller-manager — Outside Vendor Liaison"
* (Caption): "Translates Kubernetes requests into AWS/GCP/Azure API calls for things like cloud LoadBalancers."

**Further reading**

- [Cloud controller manager](https://kubernetes.io/docs/concepts/architecture/cloud-controller/)

### Demo — cloud-controller-manager

```text
SETUP
  kubectl create namespace zine-demo
  kubectl create deployment demo --image=nginx --replicas=3 -n zine-demo
  kubectl rollout status deployment/demo -n zine-demo

STEPS
  1. kubectl expose deployment demo --type=LoadBalancer --port=80 --target-port=80 -n zine-demo
  2. kubectl get svc demo -n zine-demo -w   # Ctrl+C when done

WHAT YOU SHOULD SEE
  On a cloud cluster EXTERNAL-IP moves from <pending> to a real IP. On kind it stays <pending> unless a cloud provider integration is installed.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Kind has no cloud provider by default, so <pending> is the expected result. To provision a real LoadBalancer on kind, install and run cloud-provider-kind separately; for a simple local HTTP test, use a NodePort instead.
```

## 8. Static Pods

**Part 1 — Technical Discussion:** A Static Pod is defined by a manifest on a Node’s filesystem and is launched directly by that Node’s kubelet. The kubelet mirrors it into the API as a read-only-style mirror Pod, but the API server is not the source of its desired state. This bootstrap path can start control-plane components before the API is available, while making distribution, updates, and drift node-local concerns.

![Static Pods technical illustration](generated/kubernetes-apartment-complex/08-technical.png)

**Technical perspective:** Static Pods are bootstrapped locally by the kubelet from files on a node, so they can start before the API server is available. This is useful for kubeadm-style control-plane bootstrapping, but local manifests are node-specific and are not ordinary API-managed workloads. Operators must manage file distribution, updates, and drift carefully.

**Part 2 — Analogy / Zine:** A local blueprint used to build the front desk before a front desk even exists.

![Static Pods zine illustration](generated/kubernetes-apartment-complex/08-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Static Pods — The Bootstrapping Crew"
* (Caption): "Pods managed directly by a local kubelet to run control plane components without relying on the API server."

**Further reading**

- [Static Pods](https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/)

### Demo — Static Pods

```text
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
```

## 9. kubelet

**Part 1 — Technical Discussion:** kubelet is the per-Node agent that reconciles assigned PodSpecs into running sandboxes and containers. It coordinates with the CRI runtime, mounts volumes, executes startup/readiness/liveness probes, applies restart policy, and reports conditions and container status to the API server. It can enforce local state, but it does not schedule Pods or replace the control plane’s higher-level controllers.

![kubelet technical illustration](generated/kubernetes-apartment-complex/09-technical.png)

**Technical perspective:** The kubelet is the node-level agent that turns a PodSpec into running containers. It coordinates with the runtime, mounts volumes, executes probes, reports status, and applies lifecycle policies. Kubernetes can declare the desired workload centrally, while the kubelet provides the local enforcement needed to keep that workload running on its assigned node.

**Part 2 — Analogy / Zine:** Receives the work order from the office and does headcounts to ensure assigned tenants are present and healthy.

![kubelet zine illustration](generated/kubernetes-apartment-complex/09-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "kubelet — The Superintendent"
* (Caption): "The primary node agent that ensures containers are actually running on that specific server."

**Further reading**

- [Nodes and kubelet](https://kubernetes.io/docs/concepts/architecture/nodes/)

### Demo — kubelet

```text
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
```

## 10. kube-proxy

**Part 1 — Technical Discussion:** kube-proxy implements the node-local datapath for Service virtual IPs. It watches Services and EndpointSlices, then programs packet rules—commonly iptables or IPVS—so traffic is translated and load-balanced toward eligible Pod addresses. The Service abstraction remains stable even as Pods change; some CNI or eBPF implementations can provide an equivalent datapath without the traditional kube-proxy process.

![kube-proxy technical illustration](generated/kubernetes-apartment-complex/10-technical.png)

**Technical perspective:** kube-proxy implements the Service data path on nodes by programming packet-forwarding rules, commonly with iptables or IPVS depending on configuration. The Service gives clients a stable virtual destination while backend Pod IPs change. Modern proxy replacements and some CNI implementations can provide equivalent behavior, so kube-proxy is an implementation component rather than the Service abstraction itself.

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

```text
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
```

## 11. Container Runtime & CRI

**Part 1 — Technical Discussion:** The container runtime pulls images, creates Pod sandboxes, starts processes, applies isolation, and reports their status. kubelet reaches it through the Container Runtime Interface, a standard gRPC contract that hides runtime-specific APIs and allows implementations such as containerd or CRI-O. Runtime configuration still affects cgroups, filesystem behavior, logging, image security, resource accounting, and node performance.

![Container Runtime & CRI technical illustration](generated/kubernetes-apartment-complex/11-technical.png)

**Technical perspective:** The Container Runtime Interface lets kubelet use a standard gRPC contract instead of depending on one runtime’s private API. containerd and CRI-O pull images, create sandboxes, start processes, and report container status. This modularity makes runtime choice possible, while image compatibility, cgroup configuration, logging, security isolation, and runtime performance still affect node behavior.

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

```text
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
```

## 12. Sidecar Containers

**Part 1 — Technical Discussion:** A sidecar is a supporting container in the same Pod as an application container. Containers in one Pod share a network namespace and can share volumes, enabling local proxies, log shippers, certificate agents, or telemetry adapters to cooperate over localhost or files. The trade-off is coupled scheduling and failure behavior: resource requests, readiness, shutdown order, and restart semantics must cover the whole Pod.

![Sidecar Containers technical illustration](generated/kubernetes-apartment-complex/12-technical.png)

**Technical perspective:** A sidecar shares a Pod’s network namespace and can share volumes with the primary container, making close cooperation possible without building every concern into the application image. Sidecars are useful for proxies, log shipping, certificate renewal, and telemetry, but they increase resource consumption and failure coupling: the Pod’s lifecycle and readiness must account for the supporting container.

**Part 2 — Analogy / Zine:** Sits in the same unit handling side tasks, like shipping out logs, without bothering the main tenant.

![Sidecar Containers zine illustration](generated/kubernetes-apartment-complex/12-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Sidecar Containers — The Roommate"
* (Caption): "Secondary containers in a Pod that share network/storage to handle logging, proxies (like Istio), or metrics."

**Further reading**

- [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)

### Demo — Sidecar Containers

```text
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
```

## 13. Init Containers

**Part 1 — Technical Discussion:** An init container runs to completion before ordinary application containers are started. Init containers execute sequentially, and Kubernetes retries a failed init phase according to Pod restart behavior, making them useful for configuration generation, schema preparation, permissions, or dependency checks. Because they gate readiness, slow or non-idempotent initialization directly affects rollout and recovery time.

![Init Containers technical illustration](generated/kubernetes-apartment-complex/13-technical.png)

**Technical perspective:** Init containers create an ordered initialization phase. Kubernetes will not start the application containers until each init container exits successfully, and failed init work is retried according to Pod restart behavior. They are useful for migrations, configuration generation, and dependency checks, but long or fragile initialization directly delays application availability.

**Part 2 — Analogy / Zine:** Cleans and preps the unit, then leaves completely before the main tenant moves in.

![Init Containers zine illustration](generated/kubernetes-apartment-complex/13-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Init Containers — The Prep Crew"
* (Caption): "Setup scripts that must run to completion (e.g. running DB migrations) before the main app container starts."

**Further reading**

- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

### Demo — Init Containers

```text
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
```

## 14. CNI (Container Network Interface)

**Part 1 — Technical Discussion:** The Container Network Interface is the plugin contract used to create Pod interfaces, allocate addresses, and configure routes or tunnels between Nodes. Implementations such as Calico and Cilium may also enforce NetworkPolicy, encrypt traffic, expose observability, or use eBPF datapaths. Kubernetes defines the expected Pod network model, while the CNI determines performance, failure behavior, and troubleshooting tools.

![CNI (Container Network Interface) technical illustration](generated/kubernetes-apartment-complex/14-technical.png)

**Technical perspective:** CNI is the plugin contract behind Pod networking. A plugin allocates Pod addresses, creates interfaces, installs routes, and may enforce network policy or encryption. Kubernetes defines the Pod network model, while the CNI implementation supplies the dataplane. Plugin choice therefore affects performance, security features, multi-network support, and troubleshooting methods.

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

```text
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
```

## 15. CoreDNS

**Part 1 — Technical Discussion:** CoreDNS provides cluster-local DNS for Services, Pods, and configured external names. It watches Kubernetes records and answers names using zones and search paths, allowing clients to resolve a stable Service name while backend Pod IPs change. DNS latency, cache behavior, upstream forwarding, readiness, and CoreDNS capacity are operational dependencies for many applications.

![CoreDNS technical illustration](generated/kubernetes-apartment-complex/15-technical.png)

**Technical perspective:** CoreDNS provides cluster-local name resolution so applications can address Services by stable DNS names instead of tracking changing Pod IPs. It watches Kubernetes records and answers names according to configured zones and search paths. DNS failures can look like application failures, so caching, readiness, upstream forwarding, and CoreDNS capacity belong in cluster operations.

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

```text
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
```

## 16. Services

**Part 1 — Technical Discussion:** A Service selects Pods by labels and exposes them through a stable virtual endpoint independent of their ephemeral IPs. ClusterIP supports internal access, while NodePort and LoadBalancer extend exposure; headless Services deliberately return backend addresses for clients that need direct discovery. Correct selectors and readiness determine which backends receive traffic during rollout, termination, and failure.

![Services technical illustration](generated/kubernetes-apartment-complex/16-technical.png)

**Technical perspective:** A Service decouples clients from ephemeral Pods by selecting backends through labels and exposing a stable virtual endpoint. ClusterIP supports internal access, NodePort and LoadBalancer extend exposure, and headless Services return backend addresses for clients that need direct discovery. The abstraction simplifies rolling updates and rescheduling because consumers do not need to learn each new Pod IP.

**Part 2 — Analogy / Zine:** A bolted mailbox that points to whichever tenants currently have the matching door nameplates.

![Services zine illustration](generated/kubernetes-apartment-complex/16-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Services — The Permanent Mailbox"
* (Caption): "Provides a stable internal IP and load balancing for a shifting set of ephemeral Pods."

**Further reading**

- [Service networking](https://kubernetes.io/docs/concepts/services-networking/service/)

### Demo — Services

```text
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
```

## 17. Endpoints

**Part 1 — Technical Discussion:** EndpointSlices are the scalable, controller-maintained representation of Service backends. They record addresses and conditions such as ready, serving, terminating, and sometimes topology hints, allowing proxies to avoid sending new traffic to unsuitable Pods. The older Endpoints object is useful for inspection but is less efficient for large Services and is being superseded by EndpointSlices.

![Endpoints technical illustration](generated/kubernetes-apartment-complex/17-technical.png)

**Technical perspective:** EndpointSlices are the scalable representation of Service backends. They track the addresses, readiness, serving state, and topology information of selected Pods in smaller objects than the legacy Endpoints API. Controllers and proxies use them to update routing as Pods become ready, terminate, or move, reducing update size for Services with many endpoints.

**Part 2 — Analogy / Zine:** The actual mail-forwarding list taped inside the mailbox, updated every time a tenant moves in or out.

![Endpoints zine illustration](generated/kubernetes-apartment-complex/17-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Endpoints — The Forwarding List"
* (Caption): "Maps a Service to the current set of Pod IPs actually backing it."

**Further reading**

- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

### Demo — Endpoints

```text
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
```

## 18. Ingress

**Part 1 — Technical Discussion:** An Ingress resource declares layer-7 HTTP or HTTPS matches, such as hostnames and URL paths, and maps them to Services. An Ingress controller supplies the reverse proxy, listener, TLS termination, reload behavior, and integration with an external load balancer; the resource alone does not expose traffic. Gateway API is a newer option when teams need richer routing and clearer separation of responsibilities.

![Ingress technical illustration](generated/kubernetes-apartment-complex/18-technical.png)

**Technical perspective:** Ingress expresses layer-7 HTTP routing such as host and path matches, while an Ingress controller supplies the reverse proxy, TLS termination, and implementation-specific behavior. The resource alone does not expose traffic; the controller and its load-balancer integration do. For new designs, the Gateway API can provide a more expressive, role-oriented successor.

**Part 2 — Analogy / Zine:** The single outer gate reads visitor destinations and sends them down the right internal road.

![Ingress zine illustration](generated/kubernetes-apartment-complex/18-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Ingress — The Main Gate"
* (Caption): "HTTP/S reverse proxy routing external domain traffic into your internal Services."

**Further reading**

- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

### Demo — Ingress

```text
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
  3. curl -H "Host: demo.local" http://localhost/

WHAT YOU SHOULD SEE
  curl returns the nginx welcome page. Changing the Host header to something else returns a 404 from the gatekeeper.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  One external address, and the hostname in the request decides which Service you reach. This demo needs the kind ingress-nginx manifest and the port 80 mapping in the cluster config above.
```

## 19. NetworkPolicy

**Part 1 — Technical Discussion:** NetworkPolicy is a declarative allow-list boundary for Pod ingress and egress. Policies select Pods and permit traffic by namespace, Pod labels, ports, and protocol, but enforcement is supplied by a policy-capable CNI rather than the API object itself. A rollout must account for DNS, health checks, control-plane access, default-allow behavior, and the fact that network policy is not application authentication.

![NetworkPolicy technical illustration](generated/kubernetes-apartment-complex/19-technical.png)

**Technical perspective:** NetworkPolicy is an allow-list-style authorization layer for network traffic. Policies select Pods and define permitted ingress or egress by namespace, Pod labels, ports, and direction, but only a policy-capable CNI can enforce them. A safe rollout starts with understanding default allow behavior, DNS dependencies, health checks, and the difference between isolation and application authentication.

**Part 2 — Analogy / Zine:** A guest list posted on a unit's door — only visitors on the list get buzzed in, everyone else is turned away at that door.

![NetworkPolicy zine illustration](generated/kubernetes-apartment-complex/19-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "NetworkPolicy — The Guest List"
* (Caption): "Restricts which Pods can talk to which other Pods — without one, every door is unlocked to everyone."

**Further reading**

- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

### Demo — NetworkPolicy

```text
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
```

## 20. PersistentVolume (PV)

**Part 1 — Technical Discussion:** A PersistentVolume is a cluster storage resource whose lifecycle is decoupled from an individual Pod. Its provisioner, access mode, volume mode, reclaim policy, topology, and attachment semantics determine how it can be used and what happens after a claim is released. A PV preserves data across ordinary Pod replacement, but does not by itself provide backups, replication, consistency, or protection from deletion.

![PersistentVolume (PV) technical illustration](generated/kubernetes-apartment-complex/20-technical.png)

**Technical perspective:** A PersistentVolume represents storage independently of a Pod lifecycle. Its reclaim policy, access mode, volume mode, topology, and storage backend determine what survives Pod replacement and how it can be attached. Persistence prevents data loss from ordinary rescheduling, but it does not automatically provide backups, replication, consistency guarantees, or protection from operator error.

**Part 2 — Analogy / Zine:** A separate storage facility building down the road, built to outlast any single tenant.

![PersistentVolume (PV) zine illustration](generated/kubernetes-apartment-complex/20-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "PersistentVolume — The Storage Facility"
* (Caption): "Represents actual cluster storage, provisioned ahead of time or dynamically, independent of any Pod's lifecycle."

**Further reading**

- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Demo — PersistentVolume (PV)

```text
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
```

## 21. PersistentVolumeClaim (PVC)

**Part 1 — Technical Discussion:** A PersistentVolumeClaim is a workload-facing request for capacity and storage characteristics rather than a provider-specific disk definition. Kubernetes binds it to a compatible PV—or triggers dynamic provisioning—using capacity, access mode, volume mode, StorageClass, and topology constraints. A Pending claim is therefore a useful diagnostic signal for missing capacity, an unavailable provisioner, or incompatible scheduling requirements.

![PersistentVolumeClaim (PVC) technical illustration](generated/kubernetes-apartment-complex/21-technical.png)

**Technical perspective:** A PersistentVolumeClaim is a workload-facing storage request. Kubernetes binds it to a compatible PV using capacity, access mode, volume mode, and StorageClass constraints, allowing application manifests to avoid provider-specific disk details. A claim can remain Pending when no matching or provisionable storage exists, so capacity, topology, and provisioner health must be checked.

**Part 2 — Analogy / Zine:** A universal rental agreement a tenant signs to claim a unit in the storage facility.

![PersistentVolumeClaim (PVC) zine illustration](generated/kubernetes-apartment-complex/21-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "PersistentVolumeClaim — The Rental Agreement"
* (Caption): "A request for storage that Kubernetes matches to a suitable PersistentVolume."

**Further reading**

- [PersistentVolumeClaims](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)

### Demo — PersistentVolumeClaim (PVC)

```text
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
```

## 22. StorageClass

**Part 1 — Technical Discussion:** A StorageClass defines the policy for dynamically provisioning volumes. It selects a provisioner and parameters such as disk type, filesystem, replication, encryption, reclaim policy, and volume-binding mode. Dynamic provisioning reduces manual work, but its defaults directly affect cost, performance, data retention, and whether a volume can be placed in the same topology as its consumer.

![StorageClass technical illustration](generated/kubernetes-apartment-complex/22-technical.png)

**Technical perspective:** A StorageClass is a policy and provisioning recipe for dynamic volumes. It selects a provisioner and parameters such as disk type, replication, filesystem, and binding mode. Dynamic provisioning reduces manual storage administration, while the chosen defaults and reclaim behavior have direct cost, performance, availability, and data-retention consequences.

**Part 2 — Analogy / Zine:** The complex's pre-approved construction blueprint for building a brand-new storage unit on demand, instead of waiting for one to already exist.

![StorageClass zine illustration](generated/kubernetes-apartment-complex/22-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "StorageClass — The Construction Blueprint"
* (Caption): "Defines how new storage gets dynamically provisioned on demand, so nobody has to pre-build units ahead of time."

**Further reading**

- [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/)

### Demo — StorageClass

```text
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
```

## 23. Role

**Part 1 — Technical Discussion:** A Role defines namespaced RBAC permissions as API groups, resources, resource names, and verbs such as get, list, create, or update. It is a permission rule—not an identity or a grant—and has no effect until a RoleBinding attaches it to a subject. Least privilege requires avoiding unnecessary wildcards and treating access to Secrets or workload creation as potentially sensitive.

![Role technical illustration](generated/kubernetes-apartment-complex/23-technical.png)

**Technical perspective:** A Role defines namespaced permissions as API groups, resources, resource names, and verbs. It is deliberately separate from identity: writing a permission rule does nothing until a binding attaches it to a subject. This separation supports least privilege and reviewable policy, but wildcard permissions and access to Secrets can create broad escalation paths.

**Part 2 — Analogy / Zine:** A printed set of house rules for one specific building — what's allowed inside, but nobody's name is on it yet.

![Role zine illustration](generated/kubernetes-apartment-complex/23-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Role — The House Rules"
* (Caption): "Defines what's permitted within one building (Namespace) — but grants it to nobody until a name is added."

**Further reading**

- [RBAC roles and permissions](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole)

### Demo — Role

```text
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
```

## 24. RoleBinding

**Part 1 — Technical Discussion:** A RoleBinding grants a Role or ClusterRole to a user, group, or ServiceAccount within one Namespace. The binding is the effective assignment: reviewing a Role without reviewing its bindings can miss broad groups or automation identities that receive the permission. Namespace scope limits where the grant applies, even when the referenced role is cluster-scoped.

![RoleBinding technical illustration](generated/kubernetes-apartment-complex/24-technical.png)

**Technical perspective:** A RoleBinding attaches a Role or ClusterRole’s permissions to a user, group, or ServiceAccount within a namespace. The binding is the grant that makes the rule effective, and namespace scope limits where it applies. Reviewing bindings—not just roles—is essential because an apparently narrow role can become powerful when bound to a broad group.

**Part 2 — Analogy / Zine:** The clipboard sign-up sheet where a specific tenant's name gets added under the house rules, officially granting them those permissions.

![RoleBinding zine illustration](generated/kubernetes-apartment-complex/24-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "RoleBinding — The Sign-Up Sheet"
* (Caption): "Grants a Role's permissions to a specific user, group, or ServiceAccount, within that same building (Namespace)."

**Further reading**

- [RoleBindings](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)

### Demo — RoleBinding

```text
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
```

## 25. ClusterRole

**Part 1 — Technical Discussion:** A ClusterRole describes reusable RBAC permissions that can apply across namespaces or to cluster-scoped resources such as Nodes and PersistentVolumes. A namespaced RoleBinding can use a ClusterRole while restricting the grant to that namespace, whereas a ClusterRoleBinding grants it cluster-wide. This reuse improves consistency, but broad rules can expose or mutate resources far beyond one application.

![ClusterRole technical illustration](generated/kubernetes-apartment-complex/25-technical.png)

**Technical perspective:** A ClusterRole describes permissions that can apply across namespaces or to cluster-scoped resources such as Nodes. It can also be referenced by a namespaced RoleBinding for reusable namespaced rules. Cluster-wide permission definitions improve consistency, but a careless binding can grant visibility or mutation across the entire cluster.

**Part 2 — Analogy / Zine:** A master house-rules sheet that applies across every building in the entire complex, not just one.

![ClusterRole zine illustration](generated/kubernetes-apartment-complex/25-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ClusterRole — The Master House Rules"
* (Caption): "Like a Role, but scoped to the entire cluster instead of a single Namespace."

**Further reading**

- [RBAC roles and permissions](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole)

### Demo — ClusterRole

```text
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
```

## 26. ClusterRoleBinding

**Part 1 — Technical Discussion:** A ClusterRoleBinding attaches a ClusterRole to a subject at cluster scope, making its permissions effective across namespaces and for covered cluster-scoped resources. It is appropriate for tightly controlled platform controllers, but it is one of the highest-impact RBAC grants. Prefer a namespaced RoleBinding where possible and audit effective permissions rather than relying only on role names.

![ClusterRoleBinding technical illustration](generated/kubernetes-apartment-complex/26-technical.png)

**Technical perspective:** A ClusterRoleBinding grants a ClusterRole to subjects at cluster scope. It is appropriate for tightly controlled platform automation that must inspect or manage many namespaces, but it is one of the highest-impact RBAC objects. Use narrowly scoped roles and bindings where possible, audit effective permissions, and avoid giving application identities cluster-admin access.

**Part 2 — Analogy / Zine:** A master key issued to one person that works on every building in the complex, not just one unit.

![ClusterRoleBinding zine illustration](generated/kubernetes-apartment-complex/26-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ClusterRoleBinding — The Master Key"
* (Caption): "Grants a ClusterRole's permissions to a subject across the entire cluster, not just one Namespace."

**Further reading**

- [RoleBindings](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)

### Demo — ClusterRoleBinding

```text
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
```

## 27. ServiceAccount

**Part 1 — Technical Discussion:** A ServiceAccount is a Kubernetes identity intended for workloads rather than human operators. A Pod can receive a projected, usually short-lived token for that identity, and the API server uses RBAC to decide what the application may do. Dedicated accounts, automount controls, rotation, and minimal permissions reduce the impact of a compromised workload.

![ServiceAccount technical illustration](generated/kubernetes-apartment-complex/27-technical.png)

**Technical perspective:** A ServiceAccount gives software in a Pod a Kubernetes identity distinct from a human kubeconfig user. Tokens and projected credentials let applications authenticate to the API server, while RBAC determines what that identity may do. Treat ServiceAccounts as security principals: use dedicated accounts, short-lived projected tokens, and only the permissions the workload needs.

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

```text
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
```

## 28. Node (controller)

**Part 1 — Technical Discussion:** The Node controller combines kubelet heartbeats and lease updates into a cluster-level health decision. When communication stops, it marks the Node unhealthy and, after configured toleration periods, enables eviction or replacement of eligible workloads. Detection is deliberately delayed to avoid reacting to transient partitions, so replicas, topology spread, and graceful shutdown remain necessary for resilience.

![Node (controller) technical illustration](generated/kubernetes-apartment-complex/28-technical.png)

**Technical perspective:** The Node controller turns kubelet heartbeats and lease updates into a cluster-level health view. When a node stops reporting, Kubernetes marks it unhealthy and eventually evicts or recreates eligible workloads, subject to timing and disruption rules. Detection is intentionally delayed to avoid reacting to transient network loss, so applications still need redundancy and graceful failure handling.

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

```text
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
```

## 29. Namespace (controller)

**Part 1 — Technical Discussion:** Namespaces scope namespaced objects and provide a boundary for RBAC, quotas, and many policy resources. The Namespace controller coordinates deletion by discovering and removing contained objects before finalizing the Namespace. Finalizers or unavailable controllers can leave deletion in Terminating, so forced removal should be treated as a repair action with possible orphaned resources.

![Namespace (controller) technical illustration](generated/kubernetes-apartment-complex/29-technical.png)

**Technical perspective:** Namespaces partition namespaced objects and provide a scope for access control, quotas, and policy. They are useful administrative boundaries, not hard security walls or virtual clusters. Deleting a Namespace initiates cleanup of its contents, so finalizers or an unresponsive controller can leave termination stuck until the dependency is resolved.

**Part 2 — Analogy / Zine:** When a fenced section of the property is being shut down, every tenant and piece of furniture inside is cleared out first before the fence itself comes down.

![Namespace (controller) zine illustration](generated/kubernetes-apartment-complex/29-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Namespace Controller — The Section Closure"
* (Caption): "Ensures every resource inside a Namespace is cleaned up before the Namespace itself is removed."

**Further reading**

- [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)

### Demo — Namespace (controller)

```text
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
```

## 30. ResourceQuota

**Part 1 — Technical Discussion:** ResourceQuota limits aggregate resource consumption or object counts within a namespace. Admission can reject new or updated objects when their requests, limits, storage, or count would exceed the quota, protecting shared clusters from one tenant exhausting capacity. Quotas work best with LimitRanges, accurate requests, monitoring, and enough headroom for controllers and system objects.

![ResourceQuota technical illustration](generated/kubernetes-apartment-complex/30-technical.png)

**Technical perspective:** ResourceQuota limits aggregate consumption or object counts within a namespace. It protects shared clusters from one team exhausting CPU, memory, storage, or API objects, and can require requests or limits before admission. Quota must be paired with LimitRanges, monitoring, and realistic capacity planning; otherwise valid workloads may be rejected unexpectedly.

**Part 2 — Analogy / Zine:** A posted occupancy limit sign on a fenced section — once it's full, the front desk simply refuses to let anyone else move in.

![ResourceQuota zine illustration](generated/kubernetes-apartment-complex/30-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ResourceQuota — The Occupancy Limit Sign"
* (Caption): "Caps the total resources or object counts a single Namespace (fenced section) is allowed to consume."

**Further reading**

- [Resource quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

### Demo — ResourceQuota

```text
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
```

## 31. Garbage Collector

**Part 1 — Technical Discussion:** The garbage collector follows ownerReferences to identify dependent objects and remove them when an owner is deleted. Foreground, background, and orphan propagation policies control whether dependents block deletion, disappear asynchronously, or are intentionally retained. Controllers must set ownership deliberately because incorrect references can cause unexpected cleanup or leave unmanaged objects behind.

![Garbage Collector technical illustration](generated/kubernetes-apartment-complex/31-technical.png)

**Technical perspective:** The garbage collector follows ownerReferences to remove dependents when their owner is deleted. This keeps ReplicaSet Pods, Job Pods, and related objects from becoming unmanaged orphans, while propagation policies control foreground, background, or orphan deletion. Incorrect ownership metadata can cause unexpected cleanup, so controllers must establish ownership deliberately.

**Part 2 — Analogy / Zine:** The cleanup crew that removes any leftover furniture in a unit once the tenant who ordered it moves out — nothing is left behind unclaimed.

![Garbage Collector zine illustration](generated/kubernetes-apartment-complex/31-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Garbage Collector — The Cleanup Crew"
* (Caption): "Automatically deletes objects whose owner is gone, using owner references to trace and clean up orphans."

**Further reading**

- [Owners and dependents](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)

### Demo — Garbage Collector

```text
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
```

## 32. ReplicaSet

**Part 1 — Technical Discussion:** A ReplicaSet reconciles a target count of interchangeable Pods selected by labels. It replaces missing or excess replicas, but it does not provide application-version strategy, rollout pacing, or rollback history. Deployments normally own ReplicaSets so that this low-level count reconciliation is combined with controlled releases.

![ReplicaSet technical illustration](generated/kubernetes-apartment-complex/32-technical.png)

**Technical perspective:** A ReplicaSet maintains a target number of interchangeable Pods selected by labels. It repairs count drift but does not provide rollout strategy, revision history, or application version management. Deployments normally own ReplicaSets because they add controlled replacement and rollback while retaining ReplicaSet reconciliation underneath.

**Part 2 — Analogy / Zine:** Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly.

![ReplicaSet zine illustration](generated/kubernetes-apartment-complex/32-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ReplicaSet — The Occupancy Enforcer"
* (Caption): "Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly."

**Further reading**

- [ReplicaSets](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)

### Demo — ReplicaSet

```text
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
```

## 33. Deployment

**Part 1 — Technical Discussion:** A Deployment manages ReplicaSets and turns a Pod-template change into a controlled rollout. Rolling-update limits, readiness, progress deadlines, revision history, and rollback determine how quickly a new version replaces the old one and whether traffic remains available. Deployments suit stateless or externally coordinated workloads; database migrations, API compatibility, and probe quality still require application-level planning.

![Deployment technical illustration](generated/kubernetes-apartment-complex/33-technical.png)

**Technical perspective:** A Deployment turns an application version change into a controlled ReplicaSet transition. Rolling-update limits balance availability against rollout speed, readiness gates prevent unready Pods from receiving traffic, and revision history enables rollback. Deployments make stateless releases repeatable, but state migration, backward compatibility, and probe quality still determine whether an update is safe.

**Part 2 — Analogy / Zine:** Manages swapping an entire set of units from a v1 layout to a v2 layout gradually, with a lever to rollback if inspections fail.

![Deployment zine illustration](generated/kubernetes-apartment-complex/33-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Deployment — The Renovation Planner"
* (Caption): "This is what you actually deploy. It creates the ReplicaSets and handles zero-downtime rolling updates."

**Further reading**

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

### Demo — Deployment

```text
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
```

## 34. StatefulSet

**Part 1 — Technical Discussion:** A StatefulSet gives replicas stable ordinal names, network identities, and commonly one persistent volume per replica. Ordered creation, updates, and termination can support quorum systems and clustered databases, but the controller does not create replication, consensus, or backups for the application. Operators must understand failover, storage attachment, recovery order, and disruption limits before using it for stateful systems.

![StatefulSet technical illustration](generated/kubernetes-apartment-complex/34-technical.png)

**Technical perspective:** A StatefulSet gives replicas stable ordinal identities, predictable network names, and individually associated storage. Ordered creation and termination can support clustered databases and quorum systems, but StatefulSet does not automatically make an application distributed or consistent. The application must understand identity, failover, storage semantics, and backup/recovery.

**Part 2 — Analogy / Zine:** Named, numbered units where the same tenant always returns to the exact same unit with their exact same furniture — never shuffled to a different room.

![StatefulSet zine illustration](generated/kubernetes-apartment-complex/34-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "StatefulSet — The Named Units"
* (Caption): "Manages Pods needing stable identities and persistent storage tied to that identity — each Pod keeps its name and storage across restarts."

**Further reading**

- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

### Demo — StatefulSet

```text
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
```

## 35. DaemonSet

**Part 1 — Technical Discussion:** A DaemonSet expresses node coverage rather than a fixed replica count: one Pod is scheduled on every matching Node, including eligible Nodes added later. It is suited to log collectors, monitoring agents, storage helpers, and networking components that need local access. Selectors, taints, tolerations, host access, and resource requests determine coverage and the amount of workload capacity consumed.

![DaemonSet technical illustration](generated/kubernetes-apartment-complex/35-technical.png)

**Technical perspective:** A DaemonSet expresses node coverage rather than a replica count: one Pod is scheduled on each matching node, including nodes added later. This suits agents that need local access, such as log collectors, monitors, and networking components. Taints, tolerations, selectors, and resource requests determine where the agent can run and whether it competes with workloads.

**Part 2 — Analogy / Zine:** A dedicated fire extinguisher mounted in every single building — one per building, automatically, no exceptions.

![DaemonSet zine illustration](generated/kubernetes-apartment-complex/35-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "DaemonSet — The Fire Extinguisher on Every Floor"
* (Caption): "Ensures exactly one copy of a Pod runs on every Node — often used for node-level agents like log collectors."

**Further reading**

- [DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)

### Demo — DaemonSet

```text
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
```

## 36. Job

**Part 1 — Technical Discussion:** A Job represents finite work and tracks successful and failed Pod completions. It can retry failures, run completions in parallel, and retain or clean up finished Pods according to policy, making it appropriate for migrations, batch processing, and maintenance. The task should be idempotent or otherwise safe to retry because a failure can occur after work has partially completed.

![Job technical illustration](generated/kubernetes-apartment-complex/36-technical.png)

**Technical perspective:** A Job represents finite work and tracks successful and failed Pod completions. It can retry failures, run parallel workers, and retain or clean up finished Pods according to policy. Jobs are a better fit than Deployments for migrations, batch processing, and one-time maintenance because completion—not continuous availability—is the desired state.

**Part 2 — Analogy / Zine:** A one-time moving crew hired to move a single tenant's boxes — once the job is done, the crew packs up and leaves for good, not staying on payroll.

![Job zine illustration](generated/kubernetes-apartment-complex/36-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "Job — The One-Time Moving Crew"
* (Caption): "Runs Pods to completion for a finite task, then stops — unlike a Deployment, it doesn't keep Pods running forever."

**Further reading**

- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)

### Demo — Job

```text
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
```

## 37. CronJob

**Part 1 — Technical Discussion:** A CronJob creates Jobs according to a cron schedule and transfers the actual work and retry behavior to each Job. Concurrency policy, missed-run handling, starting deadlines, history limits, time zones, and idempotency determine whether recurring execution is safe. Scheduling is not an exactly-once guarantee, so jobs must tolerate retries, controller restarts, and—depending on policy—overlap.

![CronJob technical illustration](generated/kubernetes-apartment-complex/37-technical.png)

**Technical perspective:** A CronJob creates Jobs from a schedule, adding automation for backups, reports, cleanup, and other recurring work. Concurrency policy, missed schedules, starting deadlines, history limits, and idempotency determine whether repeated runs are safe. A CronJob schedules work; it does not guarantee exactly-once execution, so the task must tolerate retries and overlap appropriately.

**Part 2 — Analogy / Zine:** The scheduled overnight cleaning crew that shows up automatically every night at 2 AM, does the job, and leaves — nobody has to call them each time.

![CronJob zine illustration](generated/kubernetes-apartment-complex/37-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "CronJob — The Scheduled Night Crew"
* (Caption): "Creates Jobs on a repeating schedule — like a nightly backup task that runs automatically without anyone triggering it."

**Further reading**

- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)

### Demo — CronJob

```text
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
```

## 38. ReplicationController (legacy)

**Part 1 — Technical Discussion:** ReplicationController is the predecessor to ReplicaSet and maintains a fixed count of Pods selected by its older selector model. It can repair replica-count drift but lacks the expressive selectors and modern rollout relationship provided by ReplicaSet and Deployment. It remains relevant when operating legacy manifests, but new workloads should normally use Deployments.

![ReplicationController (legacy) technical illustration](generated/kubernetes-apartment-complex/38-technical.png)

**Technical perspective:** ReplicationController is the predecessor to ReplicaSet. It maintains a fixed count of matching Pods, but its selector model is less expressive and it is not the normal choice for new applications. Understanding it matters when operating older clusters or manifests, while migrations generally move to Deployments and ReplicaSets.

**Part 2 — Analogy / Zine:** The original, retired occupancy-enforcer clipboard system the complex used before the newer, more flexible enforcer took over — still technically works, but nobody sets it up new anymore.

![ReplicationController (legacy) zine illustration](generated/kubernetes-apartment-complex/38-zine.png)

**Zine explanation:** The illustration translates the Kubernetes mechanism into the apartment-complex metaphor so the operational relationship is easier to remember.

* **Zine Text & Layout:**
* (Top): "ReplicationController — The Retired Enforcer"
* (Caption): "The legacy predecessor to ReplicaSet — functionally similar, but superseded by more flexible label selectors."

**Further reading**

- [ReplicationController](https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/)

### Demo — ReplicationController (legacy)

```text
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
```

## 39. HorizontalPodAutoscaler (HPA)

**Part 1 — Technical Discussion:** HPA adjusts a scalable target’s replica count from observed resource, custom, or external metrics. It compares current values with a target, applies stabilization and scaling policies, and changes the workload’s desired replicas; it does not resize an individual Pod. Effective horizontal scaling requires usable metrics, meaningful resource requests, startup tolerance, sufficient cluster capacity, and an application that can distribute traffic across replicas.

![HorizontalPodAutoscaler (HPA) technical illustration](generated/kubernetes-apartment-complex/39-technical.png)

**Technical perspective:** HPA changes the number of replicas based on observed metrics and a target such as average CPU utilization or an external/custom metric. Horizontal scaling improves concurrency and availability when the application is stateless or replicated, but it needs accurate requests, metrics availability, startup tolerance, and a workload that can actually share traffic across replicas.

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

```text
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
  Needs metrics-server. Until it reports, TARGETS shows <unknown>. Scale-down is deliberately slow (about 5 minutes).
```

## 40. VerticalPodAutoscaler (VPA)

**Part 1 — Technical Discussion:** VPA analyzes historical usage and produces CPU and memory recommendations, or applies them according to its update mode. Applying a new recommendation may evict and recreate Pods so that scheduling can use the new requests, which makes disruption and capacity planning important. VPA is complementary to some workloads but can conflict with HPA when both react to the same resource signal, and it requires the VPA add-on.

![VerticalPodAutoscaler (VPA) technical illustration](generated/kubernetes-apartment-complex/40-technical.png)

**Technical perspective:** VPA adjusts or recommends Pod resource requests and limits using historical usage. It is useful when sizing is difficult or workload demand changes vertically, but applying recommendations can restart Pods and may conflict with HPA or tightly constrained scheduling. VPA therefore requires an explicit update mode, disruption planning, and attention to workload eviction behavior.

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

```text
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
```

## 41. Pod Disruption Budget (PDB)

**Part 1 — Technical Discussion:** A PodDisruptionBudget limits voluntary evictions of selected Pods during operations such as node drain or voluntary cluster maintenance. `minAvailable` and `maxUnavailable` express an availability requirement, but the budget does not prevent crashes, hardware loss, or every involuntary disruption. A strict budget can also block maintenance when there are too few replicas or no spare schedulable Nodes, so it must match real capacity and recovery behavior.

![Pod Disruption Budget (PDB) technical illustration](generated/kubernetes-apartment-complex/41-technical.png)

**Technical perspective:** A PodDisruptionBudget limits voluntary evictions during planned operations such as node drains; it does not protect against crashes, hardware failure, or all forms of involuntary disruption. A realistic budget balances availability with maintenance progress and only works when the application has enough replicas and schedulable capacity elsewhere.

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

```text
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
```
