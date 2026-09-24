#!/usr/bin/env python3
"""
scripts/enrich_all_topics_pedagogy.py

Enriches the technical discussions for key topics across the curriculum to ensure
a comprehensive Beginner -> Intermediate -> Advanced pedagogical progression:
- Beginner: What is it, what real-world problem does it solve, and why does it exist?
- Intermediate: How it works, primary attributes, specifications, and architecture.
- Advanced: Controller reconciliation loops, kernel/OS integration, edge cases, and failure modes.
"""

import re

# -------------------------------------------------------------
# Topic 1: The Cluster (Why Kubernetes?)
# -------------------------------------------------------------
T1_NEW_TECH = """Kubernetes is an open-source, production-grade container orchestration system designed to automate the deployment, scaling, management, and self-healing of containerized applications across a distributed fleet of machines.

### What is a Cluster & Why Does It Exist? (Beginner)
In the early days of containerization, developers ran Docker containers on standalone Virtual Machines (VMs). While running a container on a single machine was straightforward, running an application in production revealed serious operational limitations:
- **Manual Host Management:** If an application needed 20 containers, an operator had to manually choose which VM had free RAM, SSH into each machine, and run `docker run`.
- **No Self-Healing:** If a physical host crashed at 2 AM, every container on that host died. Nothing automatically detected the outage or restarted those containers on surviving machines.
- **Port Conflicts & Fragile Networking:** Two containers on the same host could not easily listen on port 80 without complex port-mapping tricks.
- **Configuration Drift:** Manually tweaking configuration files on 50 different servers inevitably led to snowflake servers that nobody could reproduce.

Kubernetes solves this by abstracting a collection of separate physical or virtual machines into a **single, unified, self-healing computer**. You stop managing individual servers; instead, you declare your desired application state to the cluster, and Kubernetes figures out where to run it, connects the networking, monitors health, and restarts failed components automatically.

### Core Architecture & The Declarative Model (Intermediate)
Kubernetes fundamentally shifts operations from an **Imperative Model** ("SSH into server X and start container Y") to a **Declarative Model** ("ensure 3 replicas of the web app are always running"):
- **Declarative Manifests:** You describe the target state of your application using declarative YAML manifests (specifying container images, port configurations, CPU/RAM needs, and replica counts).
- **The Reconciliation Loop:** Autonomous software control loops continuously compare the **actual state** of the cluster with the **desired state** recorded in etcd. If a node fails or a process crashes, the controller detects the gap and creates replacement pods.
- **Bin-Packing & Resource Scheduling:** Instead of guessing which server has free space, the cluster's scheduler reads your declared CPU and memory requests and automatically packs containers onto nodes to maximize hardware efficiency.
- **Three-Way Merge Apply:** With `kubectl apply`, Kubernetes calculates a three-way diff between your local YAML file, the live cluster state in etcd, and the recorded `last-applied-configuration` annotation, safely merging updates without overwriting fields managed by other controllers.

### Linux Kernel & Distributed System Foundations (Advanced)
Before Kubernetes can schedule multiple workloads on shared machines, the Linux kernel must provide isolation so containers cannot interfere with each other's processes, files, or network. Two foundational kernel primitives make this multi-tenant execution possible:
- **Namespaces (Isolation):** Linux namespaces (`pid`, `net`, `mnt`, `ipc`, `uts`, `user`) partition kernel resources so containers operate in isolated process spaces on shared Linux kernels.
- **Control Groups (cgroups v1/v2):** Kernel cgroups enforce granular compute constraints (CFS CPU bandwidth quota in `cpu.cfs_quota_us`, hard memory limits in `memory.max`, and block I/O priorities).
- **Distributed State Synchronization:** Kubernetes control planes rely on etcd and the Raft consensus algorithm to maintain linearizable, distributed state across multiple masters, ensuring no single point of failure in cluster decision-making.

```yaml
# cluster-workload-foundation.yaml
# WHY THIS YAML: Demonstrates the cluster's declarative model in action.
# 'replicas: 3' is the desired state the Controller Manager reconciles against.
#   If a pod dies, it creates a replacement — no human intervention needed.
# 'resources.requests' is what the Scheduler reads to decide which Node fits.
# 'resources.limits' is enforced at runtime by kernel cgroups on the Worker Node.
# The cluster unifies scheduling, execution, and healing into one declarative API.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-app
  namespace: default
  labels:
    tier: application
spec:
  replicas: 3
  selector:
    matchLabels:
      app: core-app
  template:
    metadata:
      labels:
        app: core-app
    spec:
      containers:
      - name: web
        image: registry.k8s.io/pause:3.9
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```"""

# -------------------------------------------------------------
# Topic 2: Control Plane vs. Worker Nodes
# -------------------------------------------------------------
T2_NEW_TECH = """A Kubernetes cluster is strictly divided into two distinct functional tiers: the **Control Plane** (the cluster's brain that makes global decisions and orchestrates state) and **Worker Nodes** (the execution muscle that runs actual containerized workloads).

### The Two Halves of a Cluster (Beginner)
To run a reliable distributed system, you must separate **decision-making** from **physical execution**:
- **The Brain (Control Plane):** Responsible for maintaining cluster state, evaluating scheduling algorithms, monitoring system health, and reacting to cluster events. Crucially, the control plane *does not* run your user-facing business applications; its sole job is to manage the cluster.
- **The Muscle (Worker Nodes):** The machines (VMs or physical bare-metal servers) that provide raw compute power. They host the application containers, execute local health checks, and forward network traffic.

#### What Happens When Things Fail? (The Core Architectural Principle)
The decoupling of control plane and worker nodes provides critical failure isolation:
- **If a Worker Node crashes:** The control plane detects the missed heartbeats, marks the node `NotReady`, and automatically reschedules the dead node's pods onto surviving healthy worker nodes.
- **If the Control Plane goes offline:** Existing worker nodes and running application pods continue operating and serving customer traffic uninterrupted. The data plane is independent. However, no *changes* can occur: new pods cannot be scheduled, auto-scaling is frozen, and crashed pods cannot be replaced until the control plane recovers.

### Component Breakdown by Tier (Intermediate)
#### 1. Control Plane Tier Components
- **`kube-apiserver`:** The front door of the cluster. Every command (`kubectl`), controller, and node agent communicates exclusively through this REST API.
- **`etcd`:** The strongly consistent, distributed key-value database that stores the entire cluster's configuration, secrets, and live state.
- **`kube-scheduler`:** The matchmaker. It inspects newly created pods that lack a node assignment and selects the best worker node based on available resources, taints, and affinity rules.
- **`kube-controller-manager`:** The automated supervisor running loops that continuously reconcile actual state with desired state (e.g., node controller, replica controller).

#### 2. Worker Node Tier Components
- **`kubelet`:** The primary node daemon that receives pod specifications from the API server and coordinates with the container runtime to start and monitor containers.
- **Container Runtime (e.g., `containerd`):** The software that pulls container images and executes processes inside Linux cgroups and namespaces.
- **`kube-proxy`:** Manages network routing rules (iptables/IPVS) on each host to provide virtual Service IPs (ClusterIP).

### Topologies, Taints & Production Isolation (Advanced)
Control plane nodes must be protected from resource starvation caused by runaway user applications:
- **Control Plane Taints:** By default, control plane nodes carry the taint `node-role.kubernetes.io/control-plane:NoSchedule`. The scheduler will refuse to place regular business workloads on these nodes, reserving all CPU and memory for `etcd` and `kube-apiserver`.
- **Stacked vs. External etcd Topologies:**
  - *Stacked Topology:* etcd runs co-located on the same nodes as the API server. Simpler to manage and requires fewer VMs (minimum 3 for HA).
  - *External etcd Topology:* etcd runs on dedicated standalone server clusters separated from API servers. Provides maximum performance and I/O isolation, preventing heavy API traffic from impacting etcd disk sync latency.
- **Node Heartbeats via NodeLeases:** Worker nodes report health by updating lightweight `Lease` objects in `kube-node-lease` every 10 seconds, drastically reducing etcd write amplification compared to legacy full-node status updates.

### Linux OS Node Requirements
Worker nodes run standard Linux distributions whose default network and memory settings conflict with container orchestration. The host kernel must be explicitly tuned to permit cross-interface forwarding and predictable memory allocation:
- **Kernel Forwarding & Netfilter:** Nodes require `net.ipv4.ip_forward = 1` and `net.bridge.bridge-nf-call-iptables = 1` in `/etc/sysctl.d/k8s.conf` to allow bridge traffic traversal through iptables rules.
- **Swap Disabled:** The Linux kernel swap mechanism must be disabled (`swapoff -a`) so the kubelet and kernel OOM killer have deterministic memory accounting without page thrashing.
- **System Slices:** Worker nodes partition resources using systemd slices (`system.slice`, `kubelet.slice`, `runtime.slice`, and `kubepods.slice`).

```yaml
# node-affinity-spec.yaml
# WHY THIS YAML: Enforces the Control Plane / Worker Node separation boundary.
# 'DoesNotExist' for 'node-role.kubernetes.io/control-plane' tells the Scheduler:
#   never place this workload on a control plane node during the Filtering phase.
# This is how you prevent application Pods from competing with etcd, kube-apiserver,
#   or kube-scheduler for CPU/RAM on control plane nodes.
# Worker Nodes are the execution layer — this affinity rule enforces that boundary.
apiVersion: v1
kind: Pod
metadata:
  name: compute-workload
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node-role.kubernetes.io/control-plane
            operator: DoesNotExist
  containers:
  - name: worker
    image: registry.k8s.io/pause:3.9
```"""

# -------------------------------------------------------------
# Topic 16: Services
# -------------------------------------------------------------
T16_NEW_TECH = """A **Service** is an abstract REST object in Kubernetes that defines a logical set of Pods and a consistent policy by which to access them, providing a stable network endpoint (IP address and DNS name) for an ephemeral population of containers.

### Why Do We Need Services? (Beginner)
In Kubernetes, **Pods are mortal and ephemeral**:
- A Pod can crash, be killed by the out-of-memory killer, or be deleted during a rolling deployment.
- When a replacement Pod is created, it receives a **completely new, dynamic IP address** from the node's PodCIDR pool.
- Furthermore, horizontally scaled applications have multiple identical Pod replicas running simultaneously across different nodes.

If frontend applications attempted to connect directly to backend Pod IP addresses, every pod restart or scale event would break network connections, requiring constant manual updates to client configurations.
A **Service** solves this by acting as a permanent front desk:
- It assigns a single, unchanging virtual IP (**ClusterIP**) and a stable internal DNS name (e.g., `auth-service`).
- Clients send traffic to the Service's stable IP or name, and Kubernetes automatically load-balances requests across all healthy backend Pods.
- As backend Pods appear, disappear, or restart, the Service updates its routing targets automatically. The client never needs to know the real Pod IPs.

### How Services Select Pods & Route Traffic (Intermediate)
Services decouple callers from backends using **Label Selectors**:
1. **The Selector Contract:** A Service declares a `spec.selector` (e.g., `app: web-frontend`). Any Pod in the same namespace with matching labels is automatically included in the Service's routing pool.
2. **Health Gating via Readiness Probes:** A Pod is only included in the Service's active routing pool if it passes its **readiness probe**. Crashing or booting Pods receive zero traffic.
3. **Port Mapping Decoupling:**
   - `port`: The port that the Service exposes to internal callers (e.g., port 80).
   - `targetPort`: The actual port the application container is listening on inside the Pod (e.g., port 8080).
   - This mapping allows microservices to expose clean standard ports (80/443) while internal applications run on arbitrary internal ports.

#### The 5 Service Types
- **`ClusterIP` (Default):** Exposes the Service on an internal virtual IP reachable *only* from within the cluster. Ideal for internal databases, caching layers, and private microservices.
- **`NodePort`:** Allocates a dedicated port from the cluster-wide range (default `30000-32767`) across every worker node's physical IP address. External traffic hitting `<Any-Node-IP>:<NodePort>` is forwarded to the Service.
- **`LoadBalancer`:** Extends NodePort by making cloud API calls (AWS, GCP, Azure) to automatically provision a dedicated public cloud load balancer with an external IP address.
- **`ExternalName`:** Acts as an internal DNS alias, redirecting internal cluster requests directly to an external third-party DNS CNAME (e.g., `db.vendor.com`) without proxying packets.
- **`Headless` (`clusterIP: None`):** Bypasses single virtual IP proxying. CoreDNS returns individual `A` records for each matching Pod, allowing clients (like database clusters) to connect directly to specific peer replicas.

### Virtual IPs & Kernel Netfilter Translation (Advanced)
A ClusterIP has no network interface card (NIC), no MAC address, and does not respond to ICMP ping. It is purely a routing rule programmed into the Linux kernel:
- **kube-proxy's Role:** kube-proxy watches the API server for changes to Services and EndpointSlices. On each worker node, it writes packet rewriting rules into host Linux Netfilter `iptables` or `IPVS` kernel tables.
- **Destination NAT (DNAT):** When a container sends a packet to a ClusterIP (`10.96.0.15:80`), the kernel's PREROUTING hook intercepts the packet before standard IP routing and transparently rewrites the destination IP and port to one of the healthy Pod IPs (`10.244.2.45:8080`).
- **Connection Tracking (conntrack):** The Linux kernel conntrack module remembers the translation so that return packets from the Pod have their source IP rewritten back to the ClusterIP before returning to the client container.

```yaml
# nodeport-service-spec.yaml
# WHY THIS YAML: This Service shows the ClusterIP + NodePort layered model.
# 'type: NodePort' creates BOTH a ClusterIP (internal) AND a NodePort (external).
# 'selector: app: web-frontend': EndpointSlice controller populates backends;
#   kube-proxy reads EndpointSlices to program its iptables rules.
# 'port: 80 -> targetPort: 8080': stable interface -> actual container port.
# 'nodePort: 30080': kube-proxy opens this port on every node's iptables chain.
apiVersion: v1
kind: Service
metadata:
  name: web-frontend
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 31080
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```"""

# -------------------------------------------------------------
# Topic 18: Ingress
# -------------------------------------------------------------
T18_NEW_TECH = """An **Ingress** is an API resource in Kubernetes that manages external Layer-7 (HTTP and HTTPS) routing to Services within a cluster, providing hostname routing, URL path matching, and centralized TLS/SSL termination.

### Why Do We Need Ingress? (Beginner)
In a production microservice architecture, you might deploy 30 different web applications (e.g., `checkout`, `catalog`, `user-profile`, `auth`).
If you exposed each of these applications using a `LoadBalancer` Service:
- Your cloud provider would create **30 separate cloud load balancers**, incurring massive monthly cloud infrastructure costs.
- You would have to manage 30 separate public IP addresses, 30 DNS records, and 30 distinct SSL/TLS certificates.

An **Ingress** solves this by acting as an intelligent reverse-proxy gateway:
- You provision **one single cloud load balancer** for the entire cluster.
- The Ingress controller accepts all external HTTP/HTTPS traffic at this single public IP.
- Based on the request's **hostname** (e.g., `api.example.com` vs `store.example.com`) or **URL path** (e.g., `/users` vs `/orders`), Ingress intelligently routes traffic to the appropriate internal ClusterIP Service.
- SSL certificates are installed once on the Ingress resource, providing centralized TLS termination for all backend microservices.

### Ingress Resource vs. Ingress Controller (Intermediate)
Understanding Ingress requires understanding a fundamental Kubernetes architectural distinction:
1. **The Ingress Resource:** A declarative YAML manifest where you write your routing rules (hosts, paths, backend services, and TLS secrets). Creating an Ingress resource in etcd does *nothing* on its own.
2. **The Ingress Controller:** A specialized reverse proxy (such as Ingress-NGINX, Traefik, HAProxy, or cloud ALB ingress) deployed as a pod inside the cluster. The controller continuously watches the API server for Ingress resources, dynamically generating its own internal proxy configuration (e.g., `nginx.conf`) and reloading routing tables on the fly.
3. **`IngressClass`:** Because multiple ingress controllers can run in the same cluster (e.g., an external public Ingress and an internal corporate VPN Ingress), each Ingress manifest specifies an `ingressClassName: nginx` to declare which controller should process it.

### Layer-7 Routing, TLS & Dataplane Proxies (Advanced)
- **Layer-7 vs. Layer-4 Routing:** Standard Kubernetes Services operate strictly at Layer-4 (TCP/UDP transport layer) using kernel NAT rules — they cannot inspect HTTP headers, cookies, or URL paths. Ingress operates at Layer-7 (application layer), allowing deep HTTP inspection, path rewriting, rate limiting, and header manipulation.
- **TLS Termination:** The Ingress controller mounts a Kubernetes `Secret` of type `kubernetes.io/tls` containing `tls.crt` and `tls.key`. It terminates the encrypted HTTPS session at the edge and forwards plain HTTP traffic to backend pods over the internal overlay network, offloading CPU-intensive crypto operations from your application containers.
- **Traffic Bypassing kube-proxy:** Modern Ingress controllers do not route packets through the Service ClusterIP. Instead, they query the `EndpointSlice` API directly and route HTTP requests straight to the container's Pod IP, reducing network hops and latency.

```yaml
# tls-ingress-spec.yaml
# WHY THIS YAML: This Ingress resource is processed by the Ingress Controller,
#   NOT by kube-apiserver or kube-proxy directly.
# 'ingressClassName: nginx': selects which controller watches this object.
#   Multiple controllers can coexist; className routes to the right one.
# 'tls.secretName: tls-cert': the controller reads this Secret and configures
#   its virtual host to terminate HTTPS -- Layer 7, impossible with raw kube-proxy.
# 'rules.host / path': HTTP Host header and URL-path-based routing to backend Services.
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: core-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: tls-cert
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: core-app-service
            port:
              number: 80
```"""

# -------------------------------------------------------------
# Topic 19: NetworkPolicy
# -------------------------------------------------------------
T19_NEW_TECH = """A **NetworkPolicy** is a declarative firewall specification in Kubernetes that controls Layer-3 and Layer-4 network traffic flow between Pods, namespaces, and external IP blocks.

### Why Do We Need NetworkPolicies? (Beginner)
By default, Kubernetes implements an entirely **flat and open network model**:
- Every Pod can communicate with every other Pod in the cluster without NAT.
- Cross-namespace traffic is completely unrestricted by default.
- If a hacker compromises an untrusted frontend pod (such as a public-facing website), they can immediately probe and communicate with sensitive internal databases, caching layers, or payment processors in any namespace across the cluster.

A **NetworkPolicy** acts as an internal network firewall:
- By default, all Pods are unisolated (allow-all).
- As soon as a NetworkPolicy selects a Pod via label matching, that Pod transitions into **isolated mode**.
- All incoming and outgoing connections are dropped *except* those explicitly permitted by whitelist rules in the policy.
- This enforces the security principle of **least privilege**: a frontend pod can only talk to the API gateway on port 8080, and the API gateway can only talk to PostgreSQL on port 5432.

### Policy Structure: Ingress & Egress Rules (Intermediate)
A NetworkPolicy defines directional filtering:
1. **`podSelector`:** Identifies which Pods this policy governs using label matching (e.g., `role: db`).
2. **`policyTypes`:** Specifies whether the policy controls `Ingress` (incoming traffic), `Egress` (outgoing traffic), or both.
3. **Whitelist Matching Criteria (3 Match Vectors):**
   - **`podSelector`:** Permits traffic from/to specific Pods in the same namespace.
   - **`namespaceSelector`:** Permits traffic from/to all Pods residing in namespaces that match specific labels.
   - **`ipBlock`:** Permits or blocks CIDR ranges (e.g., allowing outbound traffic to the company VPN while blocking public internet).
4. **Port Enforcement:** Rules specify exact transport protocols (`TCP`, `UDP`, `SCTP`) and destination ports (e.g., port 5432).

#### The Default-Deny Security Baseline
Production clusters establish a zero-trust posture by deploying a **Default-Deny All Ingress** policy in every namespace:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}  # selects all pods in namespace
  policyTypes:
  - Ingress        # no ingress rules defined = drop all incoming traffic
```
Engineers then add granular policies to explicitly permit only legitimate traffic paths.

### CNI Implementation & Kernel Packet Filtering (Advanced)
A critical architectural detail: **Kubernetes itself does not enforce NetworkPolicies!**
- **CNI Plugin Requirement:** Neither `kube-apiserver` nor `kube-proxy` filter packets. NetworkPolicies require a policy-capable **Container Network Interface (CNI)** plugin installed in the cluster (such as Calico, Cilium, Antrea, or Weave Net).
- **Silent Failure Warning:** If you deploy a NetworkPolicy on a cluster running a basic CNI that lacks policy support (like basic Flannel), the API server will save the policy without errors, but **no traffic will be filtered**.
- **Kernel-Level Enforcement:** Policy-aware CNIs translate NetworkPolicy YAML into Linux kernel filtering structures:
  - *Calico:* Writes granular Linux `iptables` and `ipset` rules directly into host filter chains.
  - *Cilium:* Compiles policies into high-performance Linux kernel **eBPF (Extended Berkeley Packet Filter)** bytecode attached to virtual ethernet (`veth`) network interfaces, evaluating rules with near-zero latency.

```yaml
# strict-backend-network-policy.yaml
# WHY THIS YAML: Enforces namespace-level network segmentation via the CNI plugin.
# 'podSelector: app: backend': once ANY NetworkPolicy selects this Pod,
#   default becomes deny-all -- only explicitly allowed traffic flows.
# 'policyTypes: [Ingress, Egress]': both directions are now controlled.
# 'ingress.from.namespaceSelector: frontend': ONLY the frontend namespace may connect.
# 'egress.ports.port: 5432': Pods may only make outbound connections to PostgreSQL.
# WARNING: Must explicitly allow DNS (port 53) or DNS resolution breaks.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```"""

# -------------------------------------------------------------
# Topic 20: PersistentVolume (PV)
# -------------------------------------------------------------
T20_NEW_TECH = """A **PersistentVolume (PV)** is an API resource representing a piece of networked or local storage in the cluster, provisioned ahead of time by an administrator or dynamically via a StorageClass, that exists independently of any Pod that consumes it.

### Why Do We Need PersistentVolumes? (Beginner)
Containers were originally designed to be completely **stateless and ephemeral**:
- When a container writes a file to its local filesystem (like `/var/lib/mysql`), that data is written to a thin, temporary container write layer.
- If the container crashes, restarts, or is rescheduled to another worker node, that local write layer is wiped out. **All data is permanently lost.**
- Normal Pod volumes (`emptyDir`) only survive as long as the Pod lives; deleting the Pod destroys the volume.

Stateful applications (databases, key-value stores, document repositories) require storage that survives container terminations and node crashes.
A **PersistentVolume (PV)** solves this by decoupling storage from the compute lifecycle:
- A PV represents actual physical storage (e.g., an AWS EBS volume, a Google Persistent Disk, an NFS network share, or a local NVMe disk).
- It is a **cluster-scoped resource** (it does not belong to a namespace), meaning it exists independently of any application.
- When a Pod mounts a PV, it can write data safely. If the Pod crashes and restarts three days later on a different physical server, Kubernetes reconnects that exact same storage volume with all data intact.

### Core PV Attributes & Access Modes (Intermediate)
When a storage volume is defined in Kubernetes, it declares three fundamental properties:
1. **Capacity:** The size of storage provided (e.g., `storage: 50Gi`).
2. **Access Modes:** Dictates how many nodes can mount the storage simultaneously:
   - **`ReadWriteOnce` (RWO):** Can be mounted as read-write by a **single worker node** at a time. Standard for cloud block storage (AWS EBS, GCP Persistent Disk) where a physical virtual disk cannot be attached to multiple VMs concurrently.
   - **`ReadOnlyMany` (ROX):** Can be mounted as read-only by multiple worker nodes simultaneously (e.g., shared reference datasets).
   - **`ReadWriteMany` (RWX):** Can be mounted as read-write by **many worker nodes** simultaneously. Requires network-attached filesystems (NFS, CephFS, AWS EFS).
   - **`ReadWriteOncePod` (RWOP):** Enforces that only a single *Pod* across the entire cluster can mount the volume at a time.
3. **PersistentVolume Reclaim Policy:** Determines what happens to the underlying storage when an application is done with it:
   - **`Retain`:** The PV and its physical storage data are preserved. The volume enters `Released` status and an administrator must manually recover or clean the data.
   - **`Delete`:** Deleting the application's claim automatically destroys the physical cloud disk, preventing runaway cloud storage costs.

### The Storage Subsystem & CSI Node Plugins (Advanced)
A PersistentVolume is an API abstraction, but actual data lives on a Linux block device or network mount. The mounting sequence involves a coordinated pipeline:
1. **Container Storage Interface (CSI):** Standard gRPC specification allowing third-party storage vendors (AWS, NetApp, Dell) to write out-of-tree storage plugins for Kubernetes.
2. **Attach Phase (`AttachVolume`):** The control plane storage controller calls the cloud API to attach the virtual disk to the specific worker node VM where the Pod was scheduled.
3. **Mount Phase (`NodeStageVolume` & `NodePublishVolume`):** On the worker node, the local `kubelet` calls the CSI node driver:
   - The driver formats the raw disk with a Linux filesystem (`mkfs.ext4` or `mkfs.xfs`) if newly provisioned.
   - It executes a kernel `mount` system call to attach the device to a host directory (`/var/lib/kubelet/pods/<pod-id>/volumes/...`).
   - Finally, it uses a Linux **bind mount** to inject that host directory directly into the container's isolated mount namespace (`mnt`).

```yaml
# nfs-persistent-volume.yaml
# WHY THIS YAML: Demonstrates the administrator-provisioned PV lifecycle.
# 'capacity.storage: 50Gi': the PV advertises its size -- PVCs requesting >50Gi won't bind.
# 'accessModes: ReadWriteMany': NFS supports multiple nodes mounting simultaneously.
#   Block storage (EBS) would be ReadWriteOnce -- one node at a time only.
# 'persistentVolumeReclaimPolicy: Retain': when PVC is deleted, PV is NOT destroyed.
#   Moves to 'Released' state; admin must manually reclaim before rebinding.
# 'storageClassName: ""': empty string means only manual PVC binding (no dynamic provisioning).
apiVersion: v1
kind: PersistentVolume
metadata:
  name: static-nfs-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  nfs:
    path: /srv/nfs/shared-data
    server: 192.168.1.100
```"""

def apply_updates():
    # 1. Update enriched_topics_1_10.py (Topics 1 and 2)
    with open("scripts/enriched_topics_1_10.py", "r", encoding="utf-8") as f:
        c1 = f.read()
    c1 = re.sub(
        r'(1:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T1_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c1,
        flags=re.S
    )
    c1 = re.sub(
        r'(2:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T2_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c1,
        flags=re.S
    )
    with open("scripts/enriched_topics_1_10.py", "w", encoding="utf-8") as f:
        f.write(c1)
    print("Updated enriched_topics_1_10.py (Topics 1 & 2)")

    # 2. Update enriched_topics_11_20.py (Topics 16, 18, 19, 20)
    with open("scripts/enriched_topics_11_20.py", "r", encoding="utf-8") as f:
        c2 = f.read()
    c2 = re.sub(
        r'(16:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T16_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c2,
        flags=re.S
    )
    c2 = re.sub(
        r'(18:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T18_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c2,
        flags=re.S
    )
    c2 = re.sub(
        r'(19:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T19_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c2,
        flags=re.S
    )
    c2 = re.sub(
        r'(20:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + T20_NEW_TECH.replace('\\', '\\\\') + r'\g<2>',
        c2,
        flags=re.S
    )
    with open("scripts/enriched_topics_11_20.py", "w", encoding="utf-8") as f:
        f.write(c2)
    print("Updated enriched_topics_11_20.py (Topics 16, 18, 19, 20)")

if __name__ == "__main__":
    apply_updates()
