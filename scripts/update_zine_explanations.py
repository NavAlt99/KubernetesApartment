#!/usr/bin/env python3
"""
scripts/update_zine_explanations.py
Replaces the generic boilerplate zine_exp in original_zine_data.json with
meaningful descriptions that explain HOW the apartment metaphor maps to
the actual Kubernetes component's behavior.
"""

import json

IMPROVED_ZINE_EXP = {
    1: """The zine image shows isolated standalone buildings transforming into a unified apartment complex — and this is precisely how Kubernetes changes workload management. Just as managing separate buildings means separate keys, separate managers, and separate problems, running containers on individual VMs requires SSH access, manual restarts, and per-host configuration. The cluster metaphor captures Kubernetes' core value: you stop talking to individual machines and instead declare intent to the API server, which distributes and reconciles workloads across all nodes. The "single entity" in the image directly maps to the kube-apiserver acting as the sole gateway — one front desk for the entire complex.

* **Zine Text & Layout:**
* (Top): "Why Kubernetes? Because managing buildings one at a time is exhausting."
* (Under Left): "Standalone buildings, standalone managers, standalone problems."
* (Under Right): "Tie them into one complex and manage it as a single entity. Stop SSHing into individual machines — talk to the cluster, and it decides where your workload goes." """,

    2: """The two-panel split in the image maps exactly to Kubernetes' architectural separation of concerns. The Leasing Office (left) represents the Control Plane — it holds records, makes decisions, and issues instructions, but never physically lifts anything. The Buildings (right) represent Worker Nodes — they do the actual execution, running containers on hardware. The critical Kubernetes insight the image encodes is failure isolation: if a building collapses, the office dispatches the workload elsewhere; if the office goes dark, buildings keep existing tenants running (containers continue) but no new work can be assigned. This separation is why etcd, kube-apiserver, and kube-scheduler must never be co-located with application workloads.

* **Zine Text & Layout:**
* (Top): "Two halves of the complex: the office that thinks, and the buildings that work."
* (Under Left): "The Leasing Office thinks — planning, deciding, recording. This is the Control Plane."
* (Under Right): "If a building crashes, workloads shift elsewhere. If the office crashes, buildings keep running — but nothing can be changed until the office is back." """,

    3: """The Front Desk metaphor in the image captures kube-apiserver's defining property: it is the only entry point and the sole component that speaks directly to etcd. Just as every request at a hotel front desk gets logged, authenticated (ID check), and either approved or rejected before anything happens, every kubectl command, controller watch, and kubelet status update goes through the API server's pipeline: AuthN → AuthZ → Mutation → Validation → etcd write → Watch notification. The "nobody bypasses it" caption reflects the security architecture — even internal components like the scheduler and controllers cannot write to etcd directly; they must go through the API server's admission pipeline.

* **Zine Text & Layout:**
* (Top): "kube-apiserver — The Front Desk"
* (Caption): "Every request must go through this one desk; nobody bypasses it. It's the only component that talks to the records room, and it's what your kubectl commands hit." """,

    4: """The Locked Records Room image illustrates etcd's role as the only source of truth in the entire cluster. In the apartment metaphor, every lease, tenant record, and maintenance log lives in this one room — if it burns down, nobody knows who lives where or what rules apply. This mirrors etcd's position in Kubernetes: all object definitions (Pods, Services, Deployments), all cluster state, and all controller metadata are stored here. The "locked" aspect reflects that only the kube-apiserver holds the key — no other component writes to etcd directly. The "highly available" quality maps to the Raft quorum requirement: you need at least 2 of 3 rooms to agree before any record is considered committed.

* **Zine Text & Layout:**
* (Top): "etcd — The Locked Records Room"
* (Caption): "A highly available key-value store; if it corrupts, your cluster loses its memory." """,

    5: """The Unit Assigner image represents kube-scheduler's two-phase decision process. Just as a housing coordinator doesn't just pick any vacant unit but evaluates floor capacity, existing tenants, and accessibility requirements, kube-scheduler first filters out nodes that lack sufficient CPU/RAM, violate taints/tolerations, or fail topology constraints (Filtering Phase), then scores the remaining candidates based on resource balance, image locality, and affinity preferences (Scoring Phase). The image's assignment arrow from coordinator to node captures the Binding call — a PATCH to `pod.spec.nodeName` — which is the atomic moment a Pod is committed to a specific Worker Node.

* **Zine Text & Layout:**
* (Top): "kube-scheduler — The Unit Assigner"
* (Caption): "Assigns new Pods to Nodes based on CPU/RAM requirements and affinity rules." """,

    6: """The Looping Inspectors image captures kube-controller-manager's defining behavior: it runs dozens of independent control loops that continuously patrol cluster state. Just as building inspectors walk the floors on a schedule, detect vacant units, and trigger the leasing process — without being asked each time — controllers like ReplicaSet Controller, Node Lifecycle Controller, and EndpointSlice Controller watch for drift between desired state (etcd) and actual state (node reports), then issue corrective API calls. The "looping" aspect is critical: controllers are event-driven and level-triggered, meaning they reconcile even if events are missed, ensuring eventual convergence without manual intervention.

* **Zine Text & Layout:**
* (Top): "kube-controller-manager — The Looping Inspectors"
* (Caption): "Background control loops that detect crashed Pods and spin up replacements to match your deployment YAML." """,

    7: """The Outside Vendor Liaison image represents cloud-controller-manager's role as the bridge between Kubernetes' internal API model and external cloud provider APIs. Just as a complex might hire an external property management firm to handle parking structures, utility connections, and city permits — things beyond the building's own walls — cloud-controller-manager handles resources that exist in the cloud platform: provisioning AWS NLBs when Services of type LoadBalancer are created, updating VPC routing tables for Pod CIDR blocks, and removing cloud node entries when VMs are terminated. This decoupling keeps core Kubernetes cloud-agnostic while allowing per-cloud integrations.

* **Zine Text & Layout:**
* (Top): "cloud-controller-manager — Outside Vendor Liaison"
* (Caption): "Translates Kubernetes requests into AWS/GCP/Azure API calls for things like cloud LoadBalancers." """,

    8: """The Bootstrapping Crew image shows workers setting up the building's infrastructure before any tenants arrive — and this is exactly what Static Pods do for the Kubernetes control plane. Static Pods are defined as YAML manifests in `/etc/kubernetes/manifests/` on the control plane node, read directly by the kubelet via inotify file watches, with no dependency on the kube-apiserver or etcd. They are how kubeadm bootstraps the cluster: etcd, kube-apiserver, kube-scheduler, and kube-controller-manager all run as Static Pods before any cluster API is available. The Mirror Pod mechanic — a read-only reflection visible in `kubectl get pods -n kube-system` — explains why you see these pods in the API even though the API didn't create them.

* **Zine Text & Layout:**
* (Top): "Static Pods — The Bootstrapping Crew"
* (Caption): "Pods managed directly by a local kubelet to run control plane components without relying on the API server." """,

    9: """The Superintendent image captures the kubelet's position as the node-level agent that translates API-level Pod specs into actual running containers. Just as a building superintendent manages day-to-day operations — ensuring units are properly maintained, heating is working, and problems are reported to the office — the kubelet watches for Pods assigned to its node, instructs the container runtime (via CRI gRPC) to start/stop containers, mounts volumes, runs liveness and readiness probes, and reports node status back to the control plane. The kubelet is the only Kubernetes component that runs as a native systemd service rather than a container — because it must exist before any container infrastructure is available.

* **Zine Text & Layout:**
* (Top): "kubelet — The Superintendent"
* (Caption): "The primary node agent that ensures containers are actually running on that specific server." """,

    10: """The Lobby Directory image represents kube-proxy's role as the network translation layer that makes virtual Service IPs functional. Just as a lobby directory tells you which apartment number maps to which resident — and keeps that directory current as tenants move in and out — kube-proxy programs iptables/IPVS rules on every node so that traffic destined for a ClusterIP (a virtual, non-routable IP) is NAT-translated to the real Pod IP of a healthy backend. The directory is always current: when EndpointSlices change because Pods are added or removed, kube-proxy re-programs the rules. Without kube-proxy, the ClusterIP is just an IP address that goes nowhere.

* **Zine Text & Layout:**
* (Top): "kube-proxy — The Lobby Directory"
* (Caption): "Maintains network routing rules (iptables/IPVS) on the host to route traffic to active Pod IPs." """,

    11: """The Maintenance Staff image depicts the Container Runtime's (CRI) role as the operational layer between Kubernetes' orchestration decisions and the actual Linux kernel mechanics of running processes. Just as maintenance staff in a building don't design apartments but are essential for physically making them livable — hooking up plumbing, power, and walls — containerd (or CRI-O) translates kubelet instructions into kernel-level calls: creating cgroup hierarchies for resource limits, configuring Linux namespaces for isolation, mounting OverlayFS layers for the container filesystem, and invoking runc to spawn the actual process. Without the CRI layer, kubelet's PodSpec has no way to become a running process.

* **Zine Text & Layout:**
* (Top): "Container Runtime & CRI — The Maintenance Staff"
* (Caption): "Runs the actual containers via a standardized gRPC interface, handling image pulls, sandbox creation, and cgroup isolation." """,

    12: """The Roommate image perfectly captures sidecar containers' shared-namespace model. Just as two roommates share the same apartment (same address, same front door, same mailbox), sidecar containers in a Pod share the same Linux network namespace — meaning they communicate over `localhost` without crossing any network boundary — and share volumes declared in the Pod spec. The Envoy proxy sidecar in a service mesh intercepts all of the app container's traffic on localhost because they share the same network stack. The native sidecar (Kubernetes 1.28+) in `initContainers` with `restartPolicy: Always` starts before the app and stays alive, solving the Job-termination race condition that plagued legacy sidecar patterns.

* **Zine Text & Layout:**
* (Top): "Sidecar Containers — The Roommate"
* (Caption): "A helper container that shares the Pod's network namespace and volumes, running alongside the main container without coupling their code." """,

    13: """The Pre-Move Checklist image maps directly to init containers' sequential, gate-keeping role. Just as a property manager runs through a mandatory checklist before handing over apartment keys — verify utilities are connected, locks are changed, inspection is signed — init containers run to completion in declared order before any application container starts. They enforce startup dependencies: the app container does not start until all init containers exit with code 0. An init container can wait for a database (`nc -z postgres 5432`), seed a ConfigMap file into a shared emptyDir volume, or configure iptables rules (with elevated privileges) that the unprivileged app container then benefits from.

* **Zine Text & Layout:**
* (Top): "Init Containers — The Pre-Move Checklist"
* (Caption): "Runs prerequisite setup tasks to completion before any application container starts — verifying dependencies and seeding data." """,

    14: """The Wiring Crew image represents the CNI plugin's role in building the physical network fabric that Pods rely on. Just as a wiring crew installs the electrical and network cabling that makes apartments functional before tenants arrive — and that work is invisible once done — CNI plugins (Calico, Cilium, Flannel) run when a Pod is scheduled, create a virtual ethernet pair (veth), assign an IP address from the Pod CIDR, configure routing rules, and attach the interface to the Pod's network namespace. Once done, the Pod can communicate on the cluster network just like a properly wired apartment can plug in any device. NetworkPolicy enforcement is the CNI's equivalent of circuit breakers — selectively controlling which connections are allowed.

* **Zine Text & Layout:**
* (Top): "CNI — The Wiring Crew"
* (Caption): "Configures Pod networking on each node — assigning IPs, creating virtual interfaces, and establishing routes between Pods across nodes." """,

    15: """The Internal Phone Directory image maps CoreDNS' service discovery function precisely. Just as an apartment complex's internal directory lets you call "Front Desk" instead of memorizing the desk's extension number — and the directory updates automatically when staff change — CoreDNS resolves `my-service.my-namespace.svc.cluster.local` to a ClusterIP without requiring callers to know the IP directly. When Services or Endpoints change, CoreDNS's in-memory cache (backed by the API server watch) reflects the update within the TTL window. Every Pod is automatically configured with CoreDNS as its nameserver (`/etc/resolv.conf`), making service-to-service discovery work seamlessly within the cluster.

* **Zine Text & Layout:**
* (Top): "CoreDNS — The Internal Phone Directory"
* (Caption): "Resolves Service names to cluster IPs, so Pods find each other by name instead of tracking ephemeral IP addresses." """,

    16: """The Reception Desk image represents how a Kubernetes Service provides a stable virtual endpoint that decouples callers from the constantly-changing set of backend Pods. Just as a reception desk has one extension number that rings through to whichever staff member is available — even as staff come and go — a ClusterIP Service has one stable IP and port that load-balances traffic to matching Pods, selected by label selectors. When a Pod restarts and gets a new IP, the EndpointSlice controller updates the routing table; callers never need to know. The Service is a permanent address for an ephemeral population, which is why Deployments and Services are always created in pairs.

* **Zine Text & Layout:**
* (Top): "Services & ClusterIP — The Reception Desk"
* (Caption): "A stable virtual IP that load-balances traffic across matching Pods — decoupling callers from the constantly-changing Pod IP addresses." """,

    17: """The Building Address + Buzzer Panel image illustrates how NodePort and LoadBalancer Services extend the internal ClusterIP to be reachable from outside the cluster. Just as an apartment's external-facing buzzer panel (NodePort) lets visitors ring specific units from the street — even though internally residents call each other by apartment number — a NodePort Service opens a high-numbered port on every node, forwarding external traffic to the ClusterIP. A LoadBalancer Service adds a cloud-provisioned load balancer (the building's main lobby entrance) in front of those NodePorts, providing a single stable public IP. The trade-off: NodePort exposes a high-numbered port on every node; LoadBalancer incurs cloud costs per service.

* **Zine Text & Layout:**
* (Top): "NodePort & LoadBalancer — The Street-Facing Entrance"
* (Caption): "Opens the cluster's internal Services to external traffic — NodePort via host ports, LoadBalancer via a cloud-provisioned IP." """,

    18: """The Guest Concierge image captures how an Ingress controller acts as an intelligent HTTP/HTTPS router that fronts multiple Services with a single entry point. Just as a hotel concierge receives all guest requests at one desk and routes them to the right floor or department based on the request type — "conference room requests go left, restaurant reservations go right" — an Ingress controller (nginx, Traefik) inspects HTTP Host headers and URL paths, then forwards traffic to the appropriate backend Service. TLS termination at the concierge (Ingress) means backend Services don't need their own certificates. A single LoadBalancer IP can serve dozens of Services through host/path routing rules.

* **Zine Text & Layout:**
* (Top): "Ingress — The Guest Concierge"
* (Caption): "Routes external HTTP/HTTPS traffic to backend Services by hostname or URL path, with TLS termination at one central point." """,

    19: """The Security Door image maps NetworkPolicy's role as a namespace-level firewall that controls which Pods may communicate with which other Pods. Just as an apartment complex installs keycard-access doors between sections — so residents can't wander from the parking garage into the residential floors without authorization — NetworkPolicy rules restrict ingress and egress traffic between Pods at the kernel netfilter level (enforced by the CNI plugin). Without a NetworkPolicy, all Pods in a cluster can reach each other by default (flat network). Once any NetworkPolicy selects a Pod, the default behavior becomes deny-all for that Pod, and only explicitly allowed traffic flows. DNS traffic to port 53 must be explicitly allowed or DNS resolution breaks.

* **Zine Text & Layout:**
* (Top): "NetworkPolicy — The Security Door"
* (Caption): "Controls which Pods can communicate with which other Pods — enforcing namespace-level network segmentation at the kernel level." """,

    20: """The Pre-Built Storage Unit image represents a PersistentVolume's lifecycle independence from any individual Pod or tenant. Just as a storage unit in a complex exists as physical infrastructure that can be rented to one tenant, vacated, sanitized, and re-rented to another — independently of any specific lease — a PersistentVolume is provisioned by an administrator (or dynamically by a StorageClass) and exists as a cluster-level resource independent of any Pod. The Reclaim Policy (Retain/Delete/Recycle) determines what happens to the PV after a PVC releases it — like deciding whether a storage unit gets cleared out or preserved for the same tenant. AccessModes (ReadWriteOnce, ReadWriteMany) reflect the physical constraint of whether a storage unit can be accessed from one or multiple buildings simultaneously.

* **Zine Text & Layout:**
* (Top): "PersistentVolume — The Storage Unit"
* (Caption): "Represents actual cluster storage, provisioned ahead of time or dynamically, independent of any Pod's lifecycle." """,

    21: """The Rental Agreement image illustrates how a PersistentVolumeClaim is a formal request by a workload for specific storage characteristics — and the binding process that matches it to a suitable PersistentVolume. Just as a rental agreement specifies the storage unit size, access type (shared or exclusive), and duration, a PVC declares `accessModes`, `resources.requests.storage`, and optionally a `storageClassName`. The Kubernetes control plane then finds a PV that satisfies all constraints (capacity ≥ requested, matching access mode, matching StorageClass) and binds the two together. Once bound, the PVC is the Pod's exclusive handle to that storage — other Pods cannot claim the same PV while it's bound. If no PV matches, the PVC stays Pending until one becomes available.

* **Zine Text & Layout:**
* (Top): "PersistentVolumeClaim — The Rental Agreement"
* (Caption): "A request for storage that Kubernetes matches to a suitable PersistentVolume." """,

    22: """The Construction Blueprint image captures StorageClass as the template that defines how new storage gets dynamically manufactured on demand, eliminating the need for pre-provisioned PVs. Just as a blueprint specifies the materials, size standards, and construction method for new units — and a construction crew follows it every time a new unit is needed — a StorageClass specifies the provisioner (e.g., `ebs.csi.aws.com`), volume type (`gp3`), and parameters (IOPS, encryption). When a PVC references a StorageClass, the CSI provisioner receives a CreateVolume call, creates the actual disk in the cloud, and returns a PV that gets auto-bound to the PVC. The `volumeBindingMode: WaitForFirstConsumer` setting delays provisioning until a Pod is actually scheduled, ensuring the disk is created in the same availability zone as the node.

* **Zine Text & Layout:**
* (Top): "StorageClass — The Construction Blueprint"
* (Caption): "Defines how new storage gets dynamically provisioned on demand, so nobody has to pre-build units ahead of time." """,

    23: """The House Rules image maps directly to a Kubernetes Role's definition: a set of permissions scoped to a single Namespace that says what API verbs (get, list, create, delete) are allowed on which resources (pods, services, secrets). Just as house rules posted in a building define what residents may and may not do within that building — but are meaningless until someone agrees to follow them — a Role object does nothing on its own. It is purely a declaration of allowed actions. A Role cannot grant permissions outside its Namespace (that requires ClusterRole). Until a RoleBinding connects a Role to a subject (user, group, ServiceAccount), it has no effect on any entity.

* **Zine Text & Layout:**
* (Top): "Role — The House Rules"
* (Caption): "Defines what's permitted within one building (Namespace) — but grants it to nobody until a name is added." """,

    24: """The Sign-Up Sheet image represents RoleBinding as the object that activates a Role by connecting it to a specific identity. Just as house rules only become binding when a tenant signs the agreement — making them personally accountable to those rules — a RoleBinding is the `subjects:` list that says "these users/groups/ServiceAccounts are bound to this Role in this Namespace." The RoleBinding creates no new permissions itself; it references an existing Role or ClusterRole and binds it. Using a ClusterRole in a RoleBinding (not ClusterRoleBinding) grants only namespace-scoped permissions, which is a useful pattern for reusing permission templates without cluster-wide exposure.

* **Zine Text & Layout:**
* (Top): "RoleBinding — The Sign-Up Sheet"
* (Caption): "Grants a Role's permissions to a specific user, group, or ServiceAccount, within that same building (Namespace)." """,

    25: """The Master House Rules image illustrates ClusterRole's scope: unlike a Role that applies within one Namespace, ClusterRole permissions span the entire cluster and can include non-namespaced resources (Nodes, PersistentVolumes, ClusterRoles themselves). Just as master house rules at the complex level govern things that transcend individual buildings — elevator access, parking lot policies, fire safety standards — a ClusterRole can grant access to cluster-wide resources or be reused across Namespaces via RoleBindings. Aggregated ClusterRoles (`aggregationRule`) automatically merge permissions from ClusterRoles matching a label selector, allowing additive plugin-style extension of the admin role without modifying it directly.

* **Zine Text & Layout:**
* (Top): "ClusterRole — The Master House Rules"
* (Caption): "Like a Role, but scoped to the entire cluster instead of a single Namespace." """,

    26: """The Master Key image shows ClusterRoleBinding's function: granting a ClusterRole's permissions to a subject across all Namespaces and cluster-scoped resources simultaneously. Just as a master key opens every door in every building of the complex — a single physical key with unrestricted access — a ClusterRoleBinding gives the bound subject cluster-wide authority. This is why cluster-admin ClusterRoleBindings must be reviewed carefully: binding a compromised ServiceAccount or user to cluster-admin is equivalent to giving a stranger the master key to every room. Least-privilege design prefers RoleBindings (scoped to individual Namespaces) over ClusterRoleBindings wherever possible.

* **Zine Text & Layout:**
* (Top): "ClusterRoleBinding — The Master Key"
* (Caption): "Grants a ClusterRole's permissions to a subject across the entire cluster, not just one Namespace." """,

    27: """The Staff ID Badge image represents ServiceAccount as the identity credential that processes running inside Pods use to authenticate to the kube-apiserver — distinct from human users who use kubeconfig certificates or OIDC tokens. Just as a staff ID badge identifies which employee is making a request to the building office (and what they're allowed to access based on their role) — without confusing them with a visiting tenant — a ServiceAccount provides a stable identity for Pods. The kubelet automatically mounts a projected ServiceAccount token as a file inside every container (`/var/run/secrets/kubernetes.io/serviceaccount/token`), which the application uses as a bearer token for API calls. ServiceAccounts are namespace-scoped and bound to RBAC Roles for least-privilege access control.

* **Zine Text & Layout:**
* (Top): "ServiceAccount — The Staff ID Badge"
* (Caption): "Provides an identity for processes inside Pods to authenticate to the API server — distinct from a human user." """,

    28: """The Daily Check-In image maps precisely to the Node Controller's heartbeat-monitoring behavior. Just as a building manager does daily rounds to check that every unit superintendent has checked in — and flags a building as "unresponsive" after missed check-ins, then starts relocating tenants — the Node Controller watches `Lease` objects in `kube-node-lease`. If a node fails to renew its Lease within `node-monitor-grace-period` (default 40s), the controller marks it `NotReady`. After `pod-eviction-timeout` (default 5 minutes), eviction begins: pods are marked for rescheduling and the scheduler places them on healthy nodes. This is why redundancy across nodes matters — a single node failure can trigger this cascade.

* **Zine Text & Layout:**
* (Top): "Node Controller — The Daily Check-In"
* (Caption): "Watches Node health via heartbeats, marking a Node NotReady and evicting its Pods if it goes silent too long." """,

    29: """The Section Closure image illustrates the Namespace Controller's cleanup responsibility during namespace deletion. Just as closing a wing of the complex requires vacating every apartment, canceling all service contracts, and only then removing the section from the building registry — a Kubernetes Namespace cannot be fully deleted until every resource inside it (Pods, Services, PVCs, ConfigMaps, Secrets) is removed. The Namespace Controller issues deletion requests for all contained resources and sets a `DeletingTimestamp`. If a resource has a finalizer that prevents immediate deletion (e.g., a PVC with protection finalizer), the Namespace gets stuck in `Terminating` until the finalizer is cleared. This is a common operational problem requiring manual finalizer removal.

* **Zine Text & Layout:**
* (Top): "Namespace Controller — The Section Closure"
* (Caption): "Ensures every resource inside a Namespace is cleaned up before the Namespace itself is removed." """,

    30: """The Occupancy Limit Sign image shows how ResourceQuota enforces aggregate consumption caps at the Namespace level, preventing any single team or workload from monopolizing cluster capacity. Just as a section of the complex posts a maximum occupancy sign — "This wing: 50 units, 200 residents" — a ResourceQuota object tracks and limits the sum of CPU requests, memory limits, object counts (Pods, Services, PVCs), and storage requests within a Namespace. When a new Pod would exceed the quota, the API server's LimitRanger admission controller rejects it with a 403 error. LimitRange objects work alongside ResourceQuota by enforcing per-Pod defaults and maximums, ensuring every Pod declares requests/limits (required for quota accounting).

* **Zine Text & Layout:**
* (Top): "ResourceQuota — The Occupancy Limit Sign"
* (Caption): "Caps the total resources or object counts a single Namespace (fenced section) is allowed to consume." """,

    31: """The Cleanup Crew image maps the Garbage Collector controller's owner-reference traversal behavior. Just as a cleanup crew checks whether a storage unit's assigned tenant still has an active lease before clearing the unit — and automatically clears it if the tenant's file is gone — the Garbage Collector watches for objects whose `ownerReferences` point to a non-existent owner. When a Deployment is deleted, it removes its ReplicaSet (owner of Pods), triggering cascading deletion of all managed Pods. The propagation policy controls whether this cascade is `Foreground` (parent waits for children), `Background` (parent deletes immediately, children cleaned asynchronously), or `Orphan` (children kept, ownership reference cleared).

* **Zine Text & Layout:**
* (Top): "Garbage Collector — The Cleanup Crew"
* (Caption): "Automatically deletes objects whose owner is gone, using owner references to trace and clean up orphans." """,

    32: """The Occupancy Enforcer image shows the ReplicaSet's single, relentless job: maintain exactly the declared number of identical Pod replicas at all times. Just as a building occupancy enforcer continuously patrols the wing and immediately lists a vacant unit for re-occupancy the moment someone moves out — without waiting to be asked — the ReplicaSet controller watches its managed Pods' status and creates replacement Pods the moment one terminates, crashes, or fails a readiness probe. Label selectors are the ReplicaSet's matching criteria: it adopts any Pod whose labels match, which is why manually created Pods with matching labels can accidentally be adopted. Deployments are always preferred over raw ReplicaSets because they add versioning and rolling update orchestration.

* **Zine Text & Layout:**
* (Top): "ReplicaSet — The Occupancy Enforcer"
* (Caption): "Protects one number: 'always keep exactly 3 identical units occupied,' replacing any that go vacant instantly." """,

    33: """The Renovation Planner image captures Deployment's role in orchestrating zero-downtime updates by managing transitions between ReplicaSet versions. Just as a renovation planner doesn't demolish all apartments at once but vacates and renovates one floor at a time while residents stay in temporary units — a Deployment rolling update creates a new ReplicaSet (new version), scales it up one Pod at a time, while scaling down the old ReplicaSet — respecting `maxSurge` and `maxUnavailable` to ensure a minimum number of ready replicas always serve traffic. The revision history (`revisionHistoryLimit`) allows rollback to any previous ReplicaSet via `kubectl rollout undo`. Readiness probes gate each step: a new Pod must pass its readiness check before the next old Pod is terminated.

* **Zine Text & Layout:**
* (Top): "Deployment — The Renovation Planner"
* (Caption): "This is what you actually deploy. It creates the ReplicaSets and handles zero-downtime rolling updates." """,

    34: """The Named Units image represents StatefulSet's guarantee of stable, persistent identity per Pod — the opposite of Deployments, where Pods are fungible and interchangeable. Just as specific named apartment units (Unit 4A, 4B, 4C) have stable addresses, dedicated mailboxes, and stored belongings tied to that unit number — even if the same tenant moves back in — StatefulSet Pods retain the same DNS hostname (`pod-0.service`, `pod-1.service`) and the same PersistentVolumeClaim across restarts. Pods are created and deleted in strict ordinal order (0, 1, 2... for scale-up; 2, 1, 0 for scale-down), which is critical for distributed systems like Cassandra, Kafka, and etcd that require ordered peer discovery and quorum membership.

* **Zine Text & Layout:**
* (Top): "StatefulSet — The Named Units"
* (Caption): "Manages Pods needing stable identities and persistent storage tied to that identity — each Pod keeps its name and storage across restarts." """,

    35: """The Fire Extinguisher on Every Floor image captures DaemonSet's defining guarantee: exactly one Pod replica runs on every node in the cluster (or matching nodes). Just as fire safety regulations require an extinguisher on every floor — not "some floors" or "one extinguisher shared by all" — DaemonSets ensure node-level agents (log collectors like Fluent Bit, metrics exporters like Node Exporter, CNI plugins, kube-proxy itself) run on every node. When a new node joins the cluster, the DaemonSet controller automatically schedules the daemon Pod on it. DaemonSet Pods use tolerations to run on control plane nodes (which carry `NoSchedule` taints), allowing monitoring agents to cover every node including the control plane.

* **Zine Text & Layout:**
* (Top): "DaemonSet — The Fire Extinguisher on Every Floor"
* (Caption): "Ensures exactly one copy of a Pod runs on every Node — often used for node-level agents like log collectors." """,

    36: """The One-Time Moving Crew image maps to Job's finite-work execution model: unlike a Deployment that keeps Pods running indefinitely, a Job runs Pods until a defined number complete successfully, then stops. Just as a moving crew is hired for a specific job — pack and transport by Friday, then their engagement ends — a Kubernetes Job creates one or more Pods to complete a batch task (database migration, report generation, data transformation) and tracks completion via exit code 0. `completions` sets how many successful Pod runs are required; `parallelism` controls concurrent Pods. `backoffLimit` defines how many retries before the Job is declared Failed. `ttlSecondsAfterFinished` automatically cleans up completed Jobs after a set period.

* **Zine Text & Layout:**
* (Top): "Job — The One-Time Moving Crew"
* (Caption): "Runs Pods to completion for a finite task, then stops — unlike a Deployment, it doesn't keep Pods running forever." """,

    37: """The Scheduled Night Crew image maps CronJob to the building's recurring maintenance schedule. Just as a janitorial crew arrives every night at 2am without anyone having to call them — because the schedule is set in the building's annual contract — a CronJob creates a new Job on a cron expression schedule (e.g., `0 2 * * *` for 2am daily). Each trigger creates a fresh Job object, which spawns its Pod(s). `concurrencyPolicy: Forbid` prevents a new Job from starting if the previous one is still running, while `startingDeadlineSeconds` marks a Job as missed if it doesn't start within that window. CronJobs are stateless triggers — they do not track or aggregate results across runs.

* **Zine Text & Layout:**
* (Top): "CronJob — The Scheduled Night Crew"
* (Caption): "Creates Jobs on a repeating schedule — like a nightly backup task that runs automatically without anyone triggering it." """,

    38: """The Retired Enforcer image positions ReplicationController as the predecessor concept that established replica management — now fully superseded by ReplicaSet and Deployment. Just as a retired building superintendent followed the same principle (keep units occupied) but used older methods (paper ledgers, keys on hooks) that lacked the flexibility of modern digital systems — ReplicationController maintained a fixed replica count but only supported equality-based label selectors (`app=nginx`), not set-based ones (`app in [nginx, apache]`). It had no rolling update coordination. Deployments and ReplicaSets are strictly preferred; ReplicationController remains only for historical context and backward compatibility.

* **Zine Text & Layout:**
* (Top): "ReplicationController — The Retired Enforcer"
* (Caption): "The legacy predecessor to ReplicaSet — functionally similar, but superseded by more flexible label selectors." """,

    39: """The Staffing Manager image captures HPA's reactive scaling behavior: it monitors a metric signal and adjusts the number of Pod replicas in a Deployment or StatefulSet to maintain a target utilization level. Just as a staffing manager adds temporary staff during a busy season and sends them home when traffic drops — reading occupancy reports to decide how many people are needed — the HPA controller reads CPU/memory metrics from the Metrics Server (or custom metrics from Prometheus Adapter) every 15 seconds and computes: `desired replicas = ceil(currentReplicas × currentMetricValue / targetMetricValue)`. Scale-up is immediate; scale-down has a stabilization window (default 5 minutes) to prevent flapping. HPA requires Pods to have `resources.requests` declared, or it cannot compute utilization ratios.

* **Zine Text & Layout:**
* (Top): "HorizontalPodAutoscaler — The Staffing Manager"
* (Caption): "Automatically adjusts the number of Pod replicas based on CPU/memory usage — scaling out under load, back in when it drops." """,

    40: """The Unit Resizer image represents VPA's approach to right-sizing individual Pods' resource requests and limits, as opposed to HPA which adds more Pods. Just as a property manager analyzes how much space each tenant actually uses and offers to move them to a larger or smaller unit — rather than adding more tenants — VPA observes historical CPU and memory consumption, generates recommendations, and (in `Auto` mode) evicts and restarts Pods with updated `resources.requests` values. The trade-off is unavoidable: VPA cannot resize a running container in-place (in most cluster configurations), so it must evict the Pod. VPA and HPA should not both target CPU on the same Deployment, as they will conflict.

* **Zine Text & Layout:**
* (Top): "VerticalPodAutoscaler — The Unit Resizer"
* (Caption): "Automatically adjusts a Pod's CPU/memory requests based on usage history — resizing the Pod itself instead of adding more Pods." """,

    41: """The Maintenance Limit Rule image shows PDB's role in protecting application availability during voluntary disruptions like node drains, cluster upgrades, or rolling deployments. Just as a building code limits how many units can be under renovation simultaneously — ensuring the complex never falls below minimum occupancy — a PodDisruptionBudget sets a lower bound (`minAvailable`) or upper bound (`maxUnavailable`) on how many Pods in a workload can be disrupted at the same time. The Eviction API (used by `kubectl drain`) respects PDB constraints and will block further evictions if they would violate the budget. PDBs only protect against voluntary (planned) disruptions — a node crash is an involuntary disruption that PDB cannot prevent. Requires at least as many replicas as `minAvailable` to function correctly.

* **Zine Text & Layout:**
* (Top): "Pod Disruption Budget — The Maintenance Limit Rule"
* (Caption): "Limits how many Pods can be voluntarily disrupted at once during planned maintenance, protecting availability." """,
}

# Load and update the JSON
with open("scripts/original_zine_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

updated = 0
for item in data:
    num = item["num"]
    if num in IMPROVED_ZINE_EXP:
        item["zine_exp"] = IMPROVED_ZINE_EXP[num].strip()
        updated += 1

with open("scripts/original_zine_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated zine_exp for {updated} topics out of {len(data)} total.")
