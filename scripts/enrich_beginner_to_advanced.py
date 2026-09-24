#!/usr/bin/env python3
"""
scripts/enrich_beginner_to_advanced.py

Revamps technical discussions across enriched topics to follow a clear
Beginner to Advanced pedagogical arc:
1. Beginner: What is this concept/resource, what problem does it solve, and why does it exist?
2. Intermediate: How it works, key attributes, specifications, and architecture.
3. Advanced: Controller loops, reconciliation mechanics, kernel interactions, and failure modes.
"""

import sys

# Updates for scripts/enriched_topics_21_30.py
# Specifically addressing Topic 28 (Node), Topic 29 (Namespace), Topic 30 (ResourceQuota)
TOPIC_28_NEW_TECH_DISC = """A **Node** is a worker machine in Kubernetes — either a physical bare-metal server or a cloud virtual machine (VM) — that provides the actual compute, memory, storage, and networking capacity to execute containerized applications. A Kubernetes cluster is essentially a unified pool of compute resources created by aggregating multiple nodes together.

### What is a Node & Why Does It Exist? (Beginner)
In traditional operations, applications are installed directly onto individual servers, requiring administrators to track hostnames, IP addresses, and which software runs on which box. If that server crashes, someone must manually SSH into a replacement machine and reinstall the service.
Kubernetes abstracts physical machines away. Instead of deploying to a specific server, you submit your workload to the cluster control plane, and Kubernetes automatically finds an available node with sufficient CPU and RAM. If a node fails, Kubernetes automatically evacuates and reschedules the workloads onto surviving nodes.

### Node Architecture & Anatomy (Intermediate)
Every node runs three core software components that allow it to be managed by the cluster:
1. **`kubelet`:** The primary node agent that registers the node with the API server, watches for Pod assignments, communicates with the container runtime to start/stop containers, runs health probes, and continuously reports node health.
2. **Container Runtime:** The underlying engine (such as `containerd` or `CRI-O`) that pulls container images, creates Linux namespaces/cgroups, and executes container processes.
3. **`kube-proxy`:** The network component that maintains host network routing and packet-filtering rules (using iptables or IPVS) to direct Service traffic to backend Pods.

#### Node Status & Capacity Metrics
When inspecting a node (`kubectl describe node <name>`), Kubernetes reports:
- **Addresses:** `InternalIP` (routable inside cluster), `ExternalIP` (public IP if cloud-hosted), and `Hostname`.
- **Capacity vs. Allocatable:** Total hardware capacity minus OS reservations (`system-reserved`) and kubelet reservations (`kube-reserved`). Schedulers place Pods strictly against **Allocatable** resources.
- **Conditions:** Binary health signals including `Ready` (node is healthy and accepting pods), `MemoryPressure`, `DiskPressure`, and `PIDPressure`.

#### Node Maintenance Operations
- **`kubectl cordon <node>`:** Marks the node as unschedulable (`spec.unschedulable: true`). Existing running pods continue uninterrupted, but the scheduler will place no new pods on this node.
- **`kubectl drain <node>`:** Cordons the node and gracefully evicts all existing pods via the Eviction API, respecting PodDisruptionBudgets so maintenance (OS patching, kernel upgrades) can occur safely.

### Node Lifecycle & The Node Controller (Advanced)
The **Node Controller** is an automated control loop running inside `kube-controller-manager` that actively manages node lifecycle transitions:
1. **Registration & PodCIDR Assignment:** When a new node joins the cluster, the controller assigns it a dedicated, non-overlapping subnet (PodCIDR, e.g., `10.244.1.0/24`) from the cluster IP pool.
2. **Heartbeat Monitoring via NodeLeases:** Modern nodes maintain lightweight heartbeats by updating a micro-object called a `Lease` in the `kube-node-lease` namespace every 10 seconds.
3. **Failure Detection & Automatic Tainting:** If a node misses heartbeats past `--node-monitor-grace-period` (default 40s), the Node Controller marks its condition as `NotReady` or `Unknown` and attaches built-in condition taints:
   - `node.kubernetes.io/not-ready:NoSchedule` (prevents new pods from landing on it)
   - `node.kubernetes.io/unreachable:NoExecute` (begins the eviction countdown)
4. **Eviction Execution:** If the node remains unreachable past `--pod-eviction-timeout` (default 5m), the controller initiates pod evictions, instructing workload controllers to recreate replacement replicas on healthy nodes.

```yaml
# toleration-node-failure.yaml
# WHY THIS YAML: This toleration governs the Node Controller's eviction interaction.
# 'key: node.kubernetes.io/unreachable' and 'node.kubernetes.io/not-ready':
#   these taints are automatically added by the Node Lifecycle Controller when a node
#   fails its heartbeat check and is marked NotReady.
# 'effect: NoExecute': triggers immediate eviction of Pods without this toleration.
# 'tolerationSeconds: 300': this Pod tolerates the taint for 5 minutes before eviction.
#   Longer windows prevent false-positive evictions during transient network blips.
apiVersion: v1
kind: Pod
metadata:
  name: tolerant-workload
spec:
  tolerations:
  - key: "node.kubernetes.io/unreachable"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 60
  - key: "node.kubernetes.io/not-ready"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 60
  containers:
  - name: worker
    image: registry.k8s.io/pause:3.9
```"""

TOPIC_29_NEW_TECH_DISC = """A **Namespace** is a logical virtual cluster inside a physical Kubernetes cluster. It provides a scope for resource names, role-based access control (RBAC), compute resource limits, and administrative boundaries, allowing multiple teams, projects, or environments to safely share the same physical cluster infrastructure.

### What is a Namespace & Why Does It Exist? (Beginner)
Imagine a company running 20 different software development teams. If everyone deployed applications to a single shared space, naming chaos would quickly occur: Team Alpha and Team Beta might both try to create a database Service named `db` or a deployment named `frontend`, causing conflicts. Furthermore, a developer on Team Alpha could accidentally delete Team Beta's pods.
Namespaces solve this by partitioning the cluster into isolated workspaces:
- **Name Collision Avoidance:** Resource names only need to be unique *within* a namespace. Both `team-alpha` and `team-beta` can have their own Service named `redis` without conflict.
- **Environment Separation:** You can run `development`, `staging`, and `production` namespaces on the exact same worker nodes, maximizing hardware utilization while keeping configurations separated.
- **Access Control Boundaries:** Security administrators can grant developers full administrative access to the `development` namespace while restricting them to read-only access in `production`.

### Core Namespace Rules & Mechanics (Intermediate)
#### Default Built-in Namespaces
Every standard Kubernetes cluster initializes with four default namespaces:
- **`default`:** The sandbox namespace used when no `--namespace` flag or context is specified.
- **`kube-system`:** The protected namespace containing cluster control plane components, CoreDNS, kube-proxy, and network plugins.
- **`kube-public`:** Readable by all users (including unauthenticated callers); typically stores public cluster discovery info (`cluster-info`).
- **`kube-node-lease`:** Holds lightweight `Lease` heartbeat objects for each worker node.

#### Namespaced vs. Cluster-Scoped Resources
Not every object in Kubernetes belongs to a namespace:
- **Namespaced Resources:** Workloads and application configurations (`Pods`, `Services`, `Deployments`, `ConfigMaps`, `Secrets`, `PersistentVolumeClaims`).
- **Cluster-Scoped Resources:** Underlying infrastructure and cluster-wide governance primitives (`Nodes`, `PersistentVolumes`, `StorageClasses`, `ClusterRoles`, and `Namespaces` themselves). You can verify an object's scope with:
  ```bash
  kubectl api-resources --namespaced=true   # lists namespaced resources
  kubectl api-resources --namespaced=false  # lists cluster-scoped resources
  ```

#### Service Discovery Across Namespaces
DNS makes inter-service communication intuitive:
- **Same Namespace:** A Pod in `production` can reach a service named `api-svc` in the same namespace using just `http://api-svc:8080`.
- **Cross-Namespace:** To reach a service across namespaces, use the Fully Qualified Domain Name (FQDN): `http://api-svc.other-namespace.svc.cluster.local:8080`.
*(Note: Namespaces do **not** provide network packet isolation by default. Pods in different namespaces can communicate freely unless a `NetworkPolicy` firewall is applied).*

### Namespace Governance & The Namespace Controller (Advanced)
The **Namespace Controller** running inside `kube-controller-manager` is responsible for enforcing namespace lifecycle transitions and cleanups:
1. **Capacity Fencing:** Namespaces act as the boundary for `ResourceQuota` (capping aggregate CPU, memory, and object counts) and `LimitRange` (enforcing min/max sizes on individual Pods).
2. **Pod Security Standards (PSS):** Modern clusters enforce security profiles (`privileged`, `baseline`, `restricted`) by adding labels to the Namespace manifest (e.g., `pod-security.kubernetes.io/enforce: restricted`).
3. **Namespace Deletion & Cascading Teardown:**
   - When an operator deletes a namespace (`kubectl delete ns team-alpha`), the namespace enters the **`Terminating`** phase.
   - The API server immediately rejects any attempts to create new resources within that namespace.
   - The Namespace Controller initiates a recursive cascading cleanup, systematically deleting all child resources (Pods, Services, PVCs, ConfigMaps, Secrets, RoleBindings).
   - Once all child resources are completely finalized, the controller removes the `kubernetes` finalizer, allowing etcd to permanently purge the namespace.

```yaml
# labeled-namespace-spec.yaml
# WHY THIS YAML: A Namespace is the primary isolation boundary and RBAC scope.
# 'labels.pod-security.kubernetes.io/enforce: restricted': activates Pod Security Admission
#   for this namespace -- every Pod creation is validated against security standards.
# Labels on Namespaces are used by NetworkPolicies ('namespaceSelector')
#   to target specific namespaces for ingress/egress rules.
# ResourceQuotas and LimitRanges are also Namespace-scoped, applying only within this boundary.
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha
  labels:
    tier: production
    network-isolation: "true"
    pod-security.kubernetes.io/enforce: restricted
```"""

TOPIC_31_NEW_TECH_DISC = """**Garbage Collection** in Kubernetes is the automated background system responsible for detecting and deleting orphaned objects whose controlling parent resource no longer exists, ensuring cluster state remains clean and leak-free.

### What is Garbage Collection & Why Does It Exist? (Beginner)
In Kubernetes, higher-level controllers manage lower-level objects. For example, when you deploy an application, a `Deployment` creates a `ReplicaSet`, and that `ReplicaSet` creates multiple `Pods`.
What happens when you delete the `Deployment`? Without garbage collection, the underlying ReplicaSet and Pods would continue running forever as 'zombies' — consuming physical memory and CPU on worker nodes without any parent managing them.
Kubernetes solves this through automated ownership tracking: child resources maintain a cryptographic link back to their parent. When the parent is deleted, the Garbage Collector automatically traces the tree and deletes all child resources.

### Object Ownership & The Dependency Graph (Intermediate)
Kubernetes models the entire cluster's resources as a Directed Acyclic Graph (DAG) of ownership.
Child objects declare their parent controller via the `metadata.ownerReferences` field:
- **`apiVersion` & `kind`:** The API group and type of the owner (e.g., `apps/v1`, `ReplicaSet`).
- **`name`:** The string name of the owning object.
- **`uid`:** The unique UUID of the owner instance. This prevents accidental adoption if a parent is deleted and a new one with the exact same name is created.
- **`controller: true`:** Identifies which owner actively manages this child (an object can have multiple owners, but only one managing controller).
- **`blockOwnerDeletion: true`:** Ensures the parent cannot be fully removed from the cluster until this child has been safely deleted.

### Deletion Propagation & The Garbage Collector Controller (Advanced)
When deleting an object (`kubectl delete deployment <name>`), Kubernetes supports three distinct **Deletion Propagation Policies** governed by finalizers:
1. **`Background` (Default in most APIs):**
   - The API server deletes the parent object immediately.
   - The Garbage Collector controller running in `kube-controller-manager` discovers the orphaned children in the background and deletes them asynchronously.
2. **`Foreground` (`--cascade=foreground`):**
   - The parent object enters a `Terminating` state and receives the `foregroundDeletion` finalizer.
   - The parent remains visible in the cluster until every child object marked with `blockOwnerDeletion: true` is completely deleted.
   - Once all children are gone, the Garbage Collector removes the finalizer, and the parent is purged.
3. **`Orphan` (`--cascade=orphan`):**
   - The parent object is deleted, but the Garbage Collector explicitly strips the `ownerReferences` from all child objects.
   - The child Pods continue running independently as standalone, unmanaged workloads.

```yaml
# pod-with-owner-reference.yaml
# WHY THIS YAML: The ownerReference field is the Garbage Collector's dependency graph.
# 'ownerReferences.apiVersion/kind/name/uid': links this Pod to a specific ReplicaSet.
#   The uid is unique per object instance -- not just per name -- preventing stale refs.
# 'controller: true': marks this as the controlling owner (only one allowed per object).
# 'blockOwnerDeletion: true': Pod must be deleted before the owning ReplicaSet finalizes.
# When a Deployment is deleted, GC traces: Deployment -> ReplicaSet -> Pods, deleting each.
# Without ownerReferences, orphaned Pods keep running indefinitely after parent deletion.
apiVersion: v1
kind: Pod
metadata:
  name: managed-worker-pod
  ownerReferences:
  - apiVersion: apps/v1
    kind: ReplicaSet
    name: frontend-rs-v1
    uid: d4b3c2a1-0000-1111-2222-333344445555
    controller: true
    blockOwnerDeletion: true
spec:
  containers:
  - name: worker
    image: registry.k8s.io/pause:3.9
```"""

TOPIC_30_NEW_TECH_DISC = """A **ResourceQuota** is a cluster governance policy that enforces aggregate resource consumption limits inside a single namespace, preventing any individual team, environment, or runaway application from consuming all cluster capacity.

### What is a ResourceQuota & Why Does It Exist? (Beginner)
In a multi-tenant cluster where development, staging, and microservices share the same worker nodes, computing resources are finite. A single poorly tested pod with an infinite memory leak or CPU spin could exhaust all physical RAM on a worker node, triggering the Linux kernel Out-Of-Memory (OOM) killer to terminate adjacent critical workloads.
A ResourceQuota acts as an organizational boundary fence:
- It allocates a fixed slice of total cluster capacity to a specific team (e.g., Team Alpha gets at most 8 CPU cores and 16 GiB RAM).
- It prevents unexpected cloud billing spikes by capping total resource requests.
- It prevents object flooding attacks (e.g., creating 10,000 Services or Secrets).

### Quota Dimensions & Resource Categories (Intermediate)
ResourceQuotas enforce limits across three distinct categories:
1. **Compute Resource Quotas:**
   - `requests.cpu` & `requests.memory`: Limits the cumulative sum of compute *guarantees* that pods in the namespace can request from the scheduler.
   - `limits.cpu` & `limits.memory`: Limits the cumulative ceiling of compute *burst capacity* that containers can consume before throttling or OOM kills occur.
2. **Storage Resource Quotas:**
   - `requests.storage`: Caps the total storage capacity requested across all PersistentVolumeClaims in the namespace (e.g., max 500Gi total disk).
   - `persistentvolumeclaims`: Limits the total number of storage claims allowed.
   - StorageClass-specific quotas: e.g., `<storage-class-name>.storageclass.storage.k8s.io/requests.storage`.
3. **Object Count Quotas:**
   - Restricts total instances of standard resources: `count/pods`, `count/services`, `count/secrets`, `count/configmaps`, `count/replicationcontrollers`.

#### Mandatory Request Requirement & LimitRange Synergy
When a ResourceQuota is applied to a namespace for CPU or memory, **every single container** created in that namespace must explicitly declare compute requests and limits. If a developer attempts to create a Pod without specifying `resources.requests`, the API server rejects it with an HTTP 403 Forbidden error because it cannot calculate quota usage.
To streamline developer experience, cluster operators deploy a **LimitRange** alongside the ResourceQuota. The LimitRange automatically injects default request and limit values into any incoming Pod that omitted them.

### Admission Enforcement & Scope Selectors (Advanced)
The **`ResourceQuota` Admission Controller** plugin evaluates requests synchronously inside the `kube-apiserver`:
- **Atomic Transaction Check:** When a pod creation request arrives, the admission plugin computes: `Current Usage + Incoming Request`. If the total exceeds the quota limit, the request is immediately rejected before etcd write.
- **Quota Scopes:** Quotas can be configured with `scopes` to apply only to specific pod subsets:
  - `Terminating`: Applies only to Pods with a finite runtime (`spec.activeDeadlineSeconds`).
  - `NotTerminating`: Applies to long-running service pods (Deployments, StatefulSets).
  - `BestEffort`: Applies only to pods with no compute requests/limits defined.
  - `PriorityClass`: Scopes quota limits to specific workload priority tiers.

```yaml
# team-resource-quota.yaml
# WHY THIS YAML: ResourceQuota enforces aggregate resource governance at Namespace level.
# 'requests.cpu: "8"': SUM of all Pod resource requests in this namespace cannot exceed 8 CPU.
#   If a new Pod would push total over the limit, API server's admission controller rejects it.
# 'limits.cpu: "16"': prevents namespace from claiming unlimited burst capacity.
# 'count/pods: "50"': caps the number of Pod objects, not just CPU/memory.
# Once quota is enabled, EVERY Pod MUST declare 'resources.requests' or it is rejected.
#   The quota system cannot account for undeclared resource consumption.
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-compute-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "16"
    limits.memory: 32Gi
    count/pods: "50"
    persistentvolumeclaims: "10"
```"""

TOPIC_6_NEW_TECH_DISC = """The `kube-controller-manager` is the cluster's continuous automation engine. It bundles dozens of distinct, autonomous control loops into a single binary, running continuously to reconcile the cluster's observed real-world state with the user's declared desired state.

### The Controller Pattern in Kubernetes (Beginner)
In traditional server management, operations are imperative: an administrator logs into a server, runs a command to install an app, and manually restarts it if it crashes.
Kubernetes uses the **Declarative Model**. Instead of issuing imperative instructions, you define your *desired end state* in YAML (e.g., "always keep 3 copies of nginx running").
Software robots called **Controllers** constantly monitor the system. If a worker node crashes and takes down a copy of your app, the controller detects that 2 copies exist instead of the desired 3, and immediately creates a replacement. You never have to manually instruct the cluster to fix itself.

### Architecture of kube-controller-manager (Intermediate)
Rather than executing 40 separate daemon processes on the control plane, Kubernetes combines all core control loops into one multi-threaded daemon: `kube-controller-manager`.
Core bundled controllers include:
- **Deployment & ReplicaSet Controllers:** Watch deployment manifests and scale Pods up or down to match `spec.replicas`.
- **Node Lifecycle Controller:** Monitors node heartbeats, applies condition taints, and initiates pod evictions during hardware failures.
- **EndpointSlice Controller:** Watches Services and Pods to maintain live network routing directories for kube-proxy.
- **Job & CronJob Controllers:** Supervise batch workloads, tracking processes to exit code 0 and triggering scheduled tasks.
- **Namespace Controller:** Enforces clean cascading deletions of all child resources when a namespace is deleted.
- **ServiceAccount Controller:** Automatically generates default ServiceAccounts and projected security tokens for new namespaces.

### Controller Internals: Informers, WorkQueues & Leader Election (Advanced)
A naive controller would repeatedly poll the API server (`GET /api/v1/pods` every 5 seconds), which would quickly overwhelm etcd and exhaust control plane CPU. Instead, controllers use a high-performance event-driven pipeline:
1. **Reflector & List-Watch:** The controller initiates an HTTP/2 streaming `watch` request to `kube-apiserver`, receiving asynchronous change deltas (Added, Modified, Deleted) in real time.
2. **Informer & Local Cache:** An Informer stores received objects in an in-memory local cache (`Indexer`). Read queries are resolved against local RAM with zero API server load.
3. **WorkQueue with Deduplication:** When a resource changes, the Informer pushes the object's key (e.g., `default/nginx-deployment`) into a rate-limited WorkQueue. Rapid bursts of changes to the same object are collapsed into a single queue entry.
4. **Reconciliation Loop:** Available worker threads pop keys from the WorkQueue and execute `Reconcile(key)`:
   - Query local cache for desired state vs actual state.
   - If drift exists, construct and send a single corrective PATCH request to the API server.
5. **Leader Election for High Availability:** When multiple control-plane instances run `kube-controller-manager`, only **one** instance acts as the active leader by holding a `Lease` lock in `kube-system`. Follower instances standby and take over within seconds if the leader crashes.

```yaml
# /etc/kubernetes/manifests/kube-controller-manager.yaml -- Flags excerpt
# WHY THIS YAML: These flags configure the controller loops inside kube-controller-manager.
# '--leader-elect=true': only ONE active instance in HA; others watch the Lease lock.
# '--node-monitor-grace-period=40s': how long before a silent node is marked NotReady.
# '--pod-eviction-timeout=5m0s': after NotReady, pods wait this long before rescheduling.
# '--cluster-cidr=10.244.0.0/16': the Pod IP block; the controller assigns per-node CIDRs.
apiVersion: v1
kind: Pod
metadata:
  name: kube-controller-manager
  namespace: kube-system
spec:
  containers:
  - name: kube-controller-manager
    image: registry.k8s.io/kube-controller-manager:v1.28.0
    command:
    - kube-controller-manager
    - --allocate-node-cidrs=true
    - --cluster-cidr=10.244.0.0/16
    - --leader-elect=true
    - --node-monitor-grace-period=40s
    - --pod-eviction-timeout=5m0s
    - --use-service-account-credentials=true
```"""

TOPIC_7_NEW_TECH_DISC = """The `cloud-controller-manager` (CCM) is the dedicated control plane component that connects Kubernetes to external cloud infrastructure, allowing clusters running in AWS, Google Cloud, Azure, or OpenStack to provision and manage native cloud resources.

### Why Does cloud-controller-manager Exist? (Beginner)
Core Kubernetes is completely open-source and cloud-agnostic — it contains no vendor-specific code. A vanilla Kubernetes cluster knows what a "Pod" or "Service" is, but has no built-in knowledge of an AWS Network Load Balancer, an Azure Virtual Network, or a GCP Persistent Disk.
However, when you run Kubernetes in the cloud, you frequently need real cloud infrastructure:
- You want an external public IP address that automatically provisions a cloud load balancer.
- You want the cluster to automatically know if an underlying cloud VM has been shut down or terminated in your cloud management console.
The `cloud-controller-manager` acts as the translator: it watches Kubernetes resource requests and translates them into authenticated API calls to your cloud provider.

### Core Cloud Controller Loops (Intermediate)
The CCM runs three primary internal controllers:
1. **Node Controller:**
   - When a new worker node boots up, the CCM queries the cloud API to obtain cloud-specific metadata: the VM's cloud provider ID, instance type, and failure-domain topology labels (`topology.kubernetes.io/zone`, `topology.kubernetes.io/region`).
   - If a node stops responding, the CCM queries the cloud API to check if the underlying VM was deleted or terminated in the cloud console. If the VM is gone, the CCM immediately deletes the Node object from the cluster rather than waiting for lengthy timeout countdowns.
2. **Service Controller:**
   - Watches for Kubernetes Services configured with `type: LoadBalancer`.
   - Makes authenticated API requests to the cloud provider to provision a managed cloud load balancer (e.g., AWS NLB, GCP Cloud Load Balancing).
   - Once the cloud provider assigns a public IP address or DNS hostname, the controller writes it into `Service.status.loadBalancer.ingress`.
3. **Route Controller:**
   - In cloud environments without an overlay CNI (like AWS VPC CNI or GKE native networking), the Route Controller configures cloud VPC route tables so that packets destined for a node's PodCIDR are correctly forwarded across VPC subnets.

### Out-of-Tree Cloud Provider Architecture (Advanced)
In early versions of Kubernetes, cloud provider code was compiled directly inside `kube-controller-manager` and `kubelet` (known as "in-tree" cloud providers, enabled via `--cloud-provider=aws`).
This legacy model had major architectural flaws:
- Cloud vendors could only fix bugs or add new load balancer features by waiting for core Kubernetes quarterly releases.
- Security vulnerabilities in cloud SDKs required patching the entire Kubernetes control plane.
- The Kubernetes binary was bloated with gigabytes of third-party cloud SDK dependencies.
Modern Kubernetes has completely migrated to the **Out-of-Tree Cloud Provider** model:
- Core Kubernetes binaries contain zero cloud SDKs (`--cloud-provider=external`).
- Cloud providers maintain their own independent open-source CCM binaries (e.g., `aws-cloud-controller-manager`, `cloud-provider-azure`).
- Cloud vendors release updates, security patches, and support for new cloud services independently from the core Kubernetes release cycle.

```yaml
# cloud-loadbalancer-service.yaml
# WHY THIS YAML: This Service spec triggers the cloud-controller-manager's Service Controller.
# 'type: LoadBalancer': when the API server persists this, CCM's Service Controller
#   calls the cloud provider API (AWS/GCP/Azure) to provision an actual load balancer.
# 'annotations': cloud-specific parameters passed to the CCM for LB configuration.
# 'aws-load-balancer-type: external' tells CCM to create an AWS NLB, not an ALB.
# This proves 'type: LoadBalancer' is a Kubernetes intent — CCM translates it to infra.
apiVersion: v1
kind: Service
metadata:
  name: cloud-public-api
  namespace: production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "instance"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
spec:
  type: LoadBalancer
  selector:
    app: backend-gateway
  ports:
  - port: 443
    targetPort: 8443
    protocol: TCP
```"""

TOPIC_8_NEW_TECH_DISC = """**Static Pods** are specialized pods managed directly and exclusively by the local `kubelet` daemon on a single host, without involvement from the `kube-apiserver` or `kube-scheduler`.

### The Chicken-and-Egg Dilemma & Why Static Pods Exist (Beginner)
In standard Kubernetes operations, when you create a Pod, the request is sent to the `kube-apiserver`, saved in `etcd`, and scheduled by `kube-scheduler` onto a worker node. The node's `kubelet` then receives the assignment and starts the container.
This raises a fundamental architectural paradox:
*If Kubernetes runs applications as containerized Pods, how do you run the control plane itself?*
You cannot ask the `kube-apiserver` to schedule the `kube-apiserver` Pod because it doesn't exist yet!
Static Pods resolve this chicken-and-egg problem. They allow the `kubelet` to run containers directly by reading manifest files from the local host disk, allowing the control plane components to bootstrap themselves before any cluster API exists.

### How Static Pods Work (Intermediate)
The mechanism is deliberately simple and resilient:
1. **File Drop:** An operator or bootstrap tool (like `kubeadm`) places regular Pod manifest YAML files into a designated local directory on the control plane node (conventionally `/etc/kubernetes/manifests/`).
2. **Local inotify Watch:** The local `kubelet` monitors this directory using Linux kernel `inotify` file-system events.
3. **Local Execution:** Whenever a YAML file is added or modified in that directory, the `kubelet` reads it and directly instructs the local container runtime (`containerd`) to launch the pod.
4. **Autonomous Self-Healing:** If a static pod crashes or is killed, the local `kubelet` immediately restarts it. The kubelet maintains this pod even if the network is completely down or all other control plane components are offline.

#### Mirror Pods on the API Server
Because static pods are created without the API server, other cluster components and administrators wouldn't normally know they exist.
To provide cluster-wide visibility, once the `kube-apiserver` becomes available, the `kubelet` automatically registers a **Mirror Pod** in the `kube-system` namespace.
- You can inspect static pods with standard commands: `kubectl get pods -n kube-system`.
- Their names typically append the node name (e.g., `kube-apiserver-control-plane-node1`).
- Mirror pods are strictly **read-only reflections**: running `kubectl delete pod kube-apiserver-...` will delete the mirror representation momentarily, but the local `kubelet` continues running the container and immediately recreates the mirror pod.

### Production Realities & Troubleshooting (Advanced)
- **Modifying or Deleting Static Pods:** To update or remove a static pod, you must log into the physical host machine and modify or delete the YAML file directly in `/etc/kubernetes/manifests/`.
- **Host Resource Access:** Control plane static pods frequently use `hostNetwork: true` and host filesystem volume mounts (`/etc/kubernetes/pki`, `/var/lib/etcd`) because they must bind directly to host network ports (such as `6443` or `2379`) before any container overlay network (CNI) is functional.
- **Troubleshooting When API Server Fails:** When a control plane crashes, `kubectl` is unusable. Engineers troubleshoot static pods directly on the host using the Container Runtime CLI (`crictl`):
  ```bash
  crictl ps              # view active containers
  crictl pods            # view active pod sandboxes
  crictl logs <id>       # view crash logs of failing static pod
  ```

```yaml
# /etc/kubernetes/manifests/node-diagnostics.yaml
# WHY THIS YAML: Placed in the Static Pod directory — kubelet reads via inotify.
# The kubelet starts this container WITHOUT consulting kube-apiserver, etcd, or scheduler.
# 'hostNetwork: true': shares the node's network namespace — needed before CNI is ready.
# 'hostPID: true': shares the node's PID namespace — needed for node-level diagnostics.
# 'hostPath /var/log': mounts the node's actual log directory into the container.
# This is the exact pattern kubeadm uses to bootstrap etcd and kube-apiserver.
apiVersion: v1
kind: Pod
metadata:
  name: node-diagnostics
  namespace: kube-system
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: inspector
    image: registry.k8s.io/pause:3.9
    volumeMounts:
    - name: host-log
      mountPath: /var/log
  volumes:
  - name: host-log
    hostPath:
      path: /var/log
```"""

TOPIC_38_NEW_TECH_DISC = """The **ReplicationController** was the original workload supervisor in Kubernetes v1.0. It introduced the core principle of declarative container supervision, ensuring that a specified number of identical Pod replicas remain running at all times. While now superseded by `ReplicaSets` and `Deployments`, understanding it illuminates why modern Kubernetes controllers were designed the way they are.

### What was a ReplicationController & Why Did It Exist? (Beginner)
In the earliest days of container operations, if a container crashed, the host system might restart it (using Docker's local restart policy). But if the *entire physical server* crashed or lost power, all containers running on that server were permanently dead until human operators stepped in.
The ReplicationController revolutionized this by shifting responsibility from the local server to the cluster control plane:
- You declare: "I want 3 replicas of my web app."
- If Node 1 dies taking down replica #1, the ReplicationController detects that only 2 replicas exist across the cluster, and automatically tells the scheduler to launch a 3rd replica on Node 2.
- It was the first true self-healing workload mechanism in Kubernetes.

### Key Architectural Limitations & Why It Was Retired (Intermediate)
While revolutionary, the ReplicationController had two major architectural limitations that led to its obsolescence:
1. **Equality-Based Selectors Only:**
   A ReplicationController can only select Pods using strict equality: `app = frontend` or `tier = cache`. It cannot express complex set-based queries such as:
   - "Match pods where environment is either `production` OR `staging`" (`environment in (production, staging)`).
   - "Match pods that have a release label, regardless of value" (`release exists`).
   This limitation made multi-tier canary deployments and complex label groupings unwieldy.
2. **No Built-in Rolling Update Orchestration:**
   The ReplicationController had no native concept of application versioning, canary releases, or rollbacks. Upgrades required client-side tooling (`kubectl rolling-update`) that sent hundreds of individual imperative API commands over the network. If the administrator's laptop battery died or network disconnected midway through the rollout, the cluster was left in a half-deployed, corrupted state.

### Evolution to ReplicaSet & Deployment (Advanced)
To solve these fundamental limitations, the Kubernetes community split workload management into two cleaner, modular tiers:
1. **`ReplicaSet` (`apps/v1`):** The direct successor to ReplicationController. It provides the same core replica-guarantee loop, but adds powerful **Set-Based Selectors** (`matchExpressions` with `In`, `NotIn`, and `Exists`).
2. **`Deployment` (`apps/v1`):** A higher-level controller that manages ReplicaSets. The Deployment controller runs *server-side* on the control plane, orchestrating zero-downtime rolling updates, canary rollouts, and instant rollbacks with full revision history.
- **Migration Path:** You can seamlessly replace a legacy `ReplicationController` with a `Deployment` by ensuring the label selectors match. The new Deployment will automatically adopt the existing running Pods without terminating or restarting them.

```yaml
# legacy-replication-controller.yaml
# WHY THIS YAML: Historical reference only -- do NOT use in new deployments.
# 'selector: app: legacy-app': only supports equality-based selectors (key=value).
#   Cannot express 'app in [v1, v2]' or 'env != prod' -- ReplicaSet can.
# NO 'strategy' field: ReplicationController has no rolling update support.
#   Updates require manual Pod deletion or blue/green swap -- Deployment automates this.
# Migration: delete RC, create Deployment with same selector -- it adopts existing Pods.
apiVersion: v1
kind: ReplicationController
metadata:
  name: legacy-frontend
spec:
  replicas: 3
  selector:
    app: legacy-app
  template:
    metadata:
      labels:
        app: legacy-app
    spec:
      containers:
      - name: web
        image: registry.k8s.io/pause:3.9
```"""

def update_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for old_str, new_str in replacements:
        if old_str in content:
            content = content.replace(old_str, new_str, 1)
            print(f"Replaced section in {filepath}")
        else:
            print(f"FAILED to find target section in {filepath}!")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# We will apply updates via Python module data editing
import enriched_topics_21_30
import enriched_topics_31_41
import enriched_topics_1_10

def apply_direct():
    # 1. enriched_topics_21_30.py
    with open("scripts/enriched_topics_21_30.py", "r", encoding="utf-8") as f:
        c21_30 = f.read()
    
    # We replace ENRICHED_21_30[28]["tech_disc"], ENRICHED_21_30[29]["tech_disc"], ENRICHED_21_30[30]["tech_disc"]
    import re
    # Replace topic 28 tech_disc
    c21_30 = re.sub(
        r'(28:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_28_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c21_30,
        flags=re.S
    )
    # Replace topic 29 tech_disc
    c21_30 = re.sub(
        r'(29:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_29_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c21_30,
        flags=re.S
    )
    # Replace topic 30 tech_disc
    c21_30 = re.sub(
        r'(30:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_30_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c21_30,
        flags=re.S
    )
    with open("scripts/enriched_topics_21_30.py", "w", encoding="utf-8") as f:
        f.write(c21_30)
    print("Updated scripts/enriched_topics_21_30.py (Topics 28, 29, 30)")

    # 2. enriched_topics_31_41.py (Topic 31: Garbage Collector, Topic 38: ReplicationController)
    with open("scripts/enriched_topics_31_41.py", "r", encoding="utf-8") as f:
        c31_41 = f.read()
    c31_41 = re.sub(
        r'(31:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_31_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c31_41,
        flags=re.S
    )
    c31_41 = re.sub(
        r'(38:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_38_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c31_41,
        flags=re.S
    )
    with open("scripts/enriched_topics_31_41.py", "w", encoding="utf-8") as f:
        f.write(c31_41)
    print("Updated scripts/enriched_topics_31_41.py (Topics 31, 38)")

    # 3. enriched_topics_1_10.py (Topic 6: kube-controller-manager, Topic 7: cloud-controller-manager, Topic 8: Static Pods)
    with open("scripts/enriched_topics_1_10.py", "r", encoding="utf-8") as f:
        c1_10 = f.read()
    c1_10 = re.sub(
        r'(6:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_6_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c1_10,
        flags=re.S
    )
    c1_10 = re.sub(
        r'(7:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_7_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c1_10,
        flags=re.S
    )
    c1_10 = re.sub(
        r'(8:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")',
        r'\g<1>' + TOPIC_8_NEW_TECH_DISC.replace('\\', '\\\\') + r'\g<2>',
        c1_10,
        flags=re.S
    )
    with open("scripts/enriched_topics_1_10.py", "w", encoding="utf-8") as f:
        f.write(c1_10)
    print("Updated scripts/enriched_topics_1_10.py (Topics 6, 7, 8)")

if __name__ == "__main__":
    apply_direct()
