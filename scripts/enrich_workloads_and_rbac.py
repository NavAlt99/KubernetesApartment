#!/usr/bin/env python3
"""
scripts/enrich_workloads_and_rbac.py

Enriches RBAC (Topics 21-27) and Workload Controllers (Topics 32-41)
with a clear Beginner -> Intermediate -> Advanced pedagogical structure:
- Beginner: What is it, what problem does it solve, and why does it exist?
- Intermediate: How it works, primary attributes, specifications, and architecture.
- Advanced: Controller reconciliation loops, kernel/OS integration, edge cases, and failure modes.
"""

import re

# ==============================================================================
# TOPIC 21: PersistentVolumeClaim (PVC)
# ==============================================================================
T21_TECH = """A **PersistentVolumeClaim (PVC)** is a user's formal request for storage in a specific namespace. It allows developers to consume storage abstractly without needing to understand the underlying physical storage infrastructure (SAN, cloud disks, NFS).

### What is a PVC & Why Does It Exist? (Beginner)
In traditional enterprise IT, when a software developer needed storage for a database, they had to open a ticket with the storage team specifying LUN numbers, IOPS, RAID arrays, and SAN WWNs.
Kubernetes separates storage responsibilities into two distinct roles:
1. **The Cluster Administrator:** Provisions and configures physical storage pools (PersistentVolumes or StorageClasses).
2. **The Application Developer:** Simply requests what their application needs using a **PersistentVolumeClaim** ("I need 20 GiB of ReadWriteOnce storage").

The developer doesn't need to know whether the storage is an AWS EBS volume, a NetApp filer, or a local SSD. The cluster automatically finds a matching PersistentVolume and binds it to the claim.

### 1-to-1 Binding Mechanics (Intermediate)
The control plane's persistent volume controller continuously watches for unbound PVCs and attempts to pair them with suitable PVs:
- **Matching Criteria:**
  1. `storageClassName`: Must match the PV's StorageClass.
  2. `accessModes`: The PV must support the claim's required access mode (`ReadWriteOnce`, `ReadWriteMany`, `ReadOnlyMany`).
  3. `capacity`: The PV capacity must be **greater than or equal to** the requested size in the PVC.
- **Strict 1-to-1 Exclusivity:** Even if a PV has 100Gi and a PVC requests only 10Gi, once bound, that PV is completely dedicated to that single claim. No other PVC can attach to the remaining 90Gi.
- **PVC Phase Transitions:**
  - `Pending`: No matching PV currently exists, or waiting for a consumer pod to be scheduled.
  - `Bound`: Successfully paired with a volume.
  - `Lost`: The bound PV was deleted or permanently disconnected.

### Workload Consumption & Mount Mechanics (Advanced)
From the container's perspective, storage must appear as a standard local folder. The kubelet bridges the cluster storage abstraction to the container using Linux mount namespace mechanics:
- Pods mount storage by referencing the PVC name under `spec.volumes[*].persistentVolumeClaim.claimName`.
- When the pod is scheduled on a worker node, the kubelet instructs the CSI driver to attach and format the disk, then uses a Linux **bind mount** to inject the volume directory directly into the container's mount namespace (`mnt`) at the declared `mountPath`.
- **In-Use Protection:** Kubernetes applies the `kubernetes.io/pvc-protection` finalizer. If an operator attempts to delete an active PVC currently mounted by a running Pod, the deletion is deferred until the Pod terminates, preventing sudden filesystem corruption.

```yaml
# pvc-workload-claim.yaml
# WHY THIS YAML: Shows the full PVC consumption lifecycle in one manifest.
# PVC 'accessModes: ReadWriteOnce': binds only to PVs supporting single-node mounting.
# PVC 'resources.requests.storage: 20Gi': minimum capacity required for binding.
# Pod 'persistentVolumeClaim.claimName: database-storage': Pod references PVC by name;
#   kubelet instructs the CSI driver to mount the volume at mountPath.
# The PVC remains bound even if the Pod is deleted -- data persists across Pod restarts.
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-storage
  namespace: data-tier
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
---
apiVersion: v1
kind: Pod
metadata:
  name: database-server
  namespace: data-tier
spec:
  containers:
  - name: postgres
    image: registry.k8s.io/pause:3.9
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: database-storage
```"""

# ==============================================================================
# TOPIC 22: StorageClass
# ==============================================================================
T22_TECH = """A **StorageClass** provides dynamic, on-demand storage provisioning for Kubernetes clusters, completely eliminating the need for cluster administrators to manually pre-provision static PersistentVolumes.

### What is a StorageClass & Why Does It Exist? (Beginner)
In early Kubernetes environments, storage provisioning was purely manual (static provisioning):
- If a developer needed a 20Gi PVC, an administrator had to first manually log into AWS, create an EBS volume, write a 30-line `PersistentVolume` YAML manifest, and submit it to the cluster before the developer's claim could bind.
- If 100 microservices needed databases, administrators had to pre-create hundreds of disks ahead of time, guessing sizes and wasting money on idle volumes.

A **StorageClass** automates this by acting as a dynamic disk factory:
- The administrator creates a single StorageClass definition (e.g., `fast-ssd`).
- When a developer submits a PVC requesting `storageClassName: fast-ssd`, Kubernetes automatically communicates with the cloud provider (AWS, GCP, Azure, or SAN) to manufacture the physical disk in real time.
- As soon as the cloud disk is created, Kubernetes creates the PV and binds it to the PVC automatically — zero administrator tickets required.

### Key Architectural Parameters (Intermediate)
- **`provisioner`:** The CSI plugin driver responsible for communicating with cloud or storage APIs (e.g., `ebs.csi.aws.com`, `pd.csi.storage.gke.io`).
- **`volumeBindingMode`:**
  - `Immediate` (Default): The PV is provisioned dynamically as soon as the PVC is submitted. (Warning: risks provisioning storage in an Availability Zone where no compute capacity exists).
  - `WaitForFirstConsumer`: Delays volume creation and binding until a Pod using the claim is scheduled. Guarantees that the storage volume is provisioned in the exact same Availability Zone / topology domain as the scheduled worker node.
- **`allowVolumeExpansion`:** Enables online filesystem expansion without restarting workloads (`true`).
- **`reclaimPolicy`:** Sets whether dynamically provisioned volumes are `Delete` (cloud disk deleted with PVC) or `Retain` (cloud disk preserved).
- **`parameters`:** Vendor-specific configurations passed to the storage engine (e.g., IOPS, disk type `gp3`, disk encryption keys).

### Dynamic Provisioning Lifecycle & CSI Controllers (Advanced)
1. **The Claim Watch:** The CSI `external-provisioner` sidecar watches the API server for newly submitted PVCs referencing its StorageClass.
2. **Topology Discovery:** When `volumeBindingMode: WaitForFirstConsumer` is active, the scheduler selects a node first, passing the node's zone labels (`topology.kubernetes.io/zone=us-east-1a`) to the provisioner.
3. **RPC Volume Creation:** The provisioner issues a gRPC `CreateVolume` call to the cloud vendor's API, requesting an encrypted volume in that specific zone.
4. **Automatic Object Construction:** Upon receiving the cloud disk ID, the provisioner constructs a corresponding `PersistentVolume` object in etcd with matching capacity and access modes, instantly transitioning the developer's PVC to `Bound`.

```yaml
# dynamic-storage-class.yaml
# WHY THIS YAML: This StorageClass drives the dynamic provisioning workflow.
# 'provisioner: ebs.csi.aws.com': the CSI plugin receiving CreateVolume gRPC calls
#   when a PVC referencing this class is created -- calls the AWS EBS API.
# 'volumeBindingMode: WaitForFirstConsumer': provisioning DELAYED until a Pod is scheduled.
#   Ensures the EBS volume is created in the same AZ as the node -- avoids AZ failures.
# 'allowVolumeExpansion: true': operators can increase PVC size post-creation; no migration.
# 'reclaimPolicy: Delete': PVC deletion automatically destroys the EBS volume.
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-nvme-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
```"""

# ==============================================================================
# TOPIC 23: Role
# ==============================================================================
T23_TECH = """A **Role** is a namespaced Role-Based Access Control (RBAC) resource that defines a discrete set of additive permissions within a single Kubernetes namespace.

### What is an RBAC Role & Why Does It Exist? (Beginner)
Without access controls, anyone with access to the cluster could run `kubectl delete pods --all` and destroy production.
In Kubernetes, **access is denied by default**. A **Role** is how administrators declare what actions are permitted within a specific project or environment.
Think of a Role as an unassigned job description:
- It defines what tasks are allowed (e.g., "can view pods and read logs, but cannot delete anything").
- Crucially, a Role grants permissions to *nobody* by itself. It is purely a policy definition waiting to be bound to a person or service account using a `RoleBinding`.

### Anatomy of RBAC Policy Rules (Intermediate)
A Role contains an array of `rules`. Every rule evaluates three dimensions:
1. **`apiGroups`:** Which API group contains the resource.
   - Core resources (`pods`, `services`, `configmaps`, `secrets`) belong to the empty group `""`.
   - Workload controllers (`deployments`, `statefulsets`) belong to `"apps"`.
   - Batch workloads (`jobs`, `cronjobs`) belong to `"batch"`.
2. **`resources`:** The specific target objects (`pods`, `services`, `deployments`).
   - Subresources are targeted using slashes (e.g., `pods/log`, `pods/exec`, `pods/status`).
   - `resourceNames` (optional): Restricts the rule to specific named objects (e.g., only the Secret named `db-credentials`).
3. **`verbs`:** The allowed operations:
   - Read operations: `get` (single object), `list` (collection), `watch` (stream changes).
   - Write operations: `create`, `update` (replace), `patch` (partial update), `delete`, `deletecollection`.

### Namespace Scope & Security Boundaries (Advanced)
- **Strict Namespace Scoping:** A `Role` exists inside a single namespace and can *never* grant access to resources in other namespaces or cluster-scoped objects (like Nodes or PVs).
- **Additive Security Model:** Rules can only grant permissions; there is no "deny" verb in Kubernetes RBAC. If multiple roles apply to a user, their permissions are combined (union).
- **Privilege Escalation Prevention:** Kubernetes enforces that a user cannot create or update a Role containing permissions that the user does not already possess themselves, preventing developers from granting themselves superuser access.

```yaml
# namespaced-developer-role.yaml
# WHY THIS YAML: A Role defines the permission boundary within a single Namespace.
# 'namespace: development': Role ONLY applies to this namespace -- cannot grant cross-namespace access.
# 'resources: ["pods", "pods/log"]': access to Pod objects AND their log subresource.
#   Without 'pods/log', kubectl logs is denied even with pod get permissions.
# 'verbs: ["get", "list", "watch"]': read-only access -- satisfies least-privilege.
# This Role has ZERO effect until a RoleBinding attaches it to a subject.
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-operator
  namespace: development
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "patch"]
```"""

# ==============================================================================
# TOPIC 32: ReplicaSet
# ==============================================================================
T32_TECH = """A **ReplicaSet** is a core Kubernetes workload controller whose single responsibility is to maintain a stable, declared population of identical Pod replicas running at all times.

### What is a ReplicaSet & Why Does It Exist? (Beginner)
If you deploy a single standalone Pod directly (`kubectl run my-app`), and that Pod's process crashes or its worker node suffers a hardware failure, **the Pod is dead forever**. Kubernetes will not restart or reschedule a bare Pod.
To run reliable production applications, you need a continuous supervisor that guarantees availability:
- If you declare: "keep exactly 3 replicas of my-app running."
- If one container crashes, the supervisor launches a replacement instantly.
- If a traffic surge hits, you can change the number to 10, and 7 new pods launch immediately.
A **ReplicaSet** is that automated supervisor.

### How a ReplicaSet Works (Intermediate)
The ReplicaSet controller operates using a simple mathematical reconciliation loop:
1. **Count Active Pods:** It queries the API server for all healthy Pods in the namespace that match its `spec.selector`.
2. **Compute Difference:** `Drift = spec.replicas - active_pods`.
3. **Reconcile:**
   - If `Drift > 0`: Creates replacement Pods from its `spec.template`.
   - If `Drift < 0`: Deletes excess Pods gracefully.
   - If `Drift == 0`: Does nothing.

#### Set-Based Selectors vs. Legacy Selectors
Unlike the legacy `ReplicationController` which only supported exact equality (`env = prod`), ReplicaSets support rich **Set-Based Selectors** using `matchExpressions`:
- Operators: `In`, `NotIn`, `Exists`, `DoesNotExist`.
- Example: match pods where `tier: backend` AND `environment in (staging, production)`.

### Pod Adoption & Deployment Management (Advanced)
- **Automatic Pod Adoption:** A ReplicaSet does not only manage pods that it created itself. If an unmanaged Pod exists in the namespace whose labels match the ReplicaSet's selector, the ReplicaSet controller will actively adopt it, setting its `metadata.ownerReferences` to point to the ReplicaSet!
- **Label Selector Overlap Hazards:** If two different ReplicaSets define overlapping label selectors, they will enter an infinite fighting loop, repeatedly creating and deleting each other's pods.
- **Why We Use Deployments:** In production, engineers almost never write ReplicaSet manifests directly. Instead, you write `Deployments`. A Deployment manages multiple ReplicaSets behind the scenes to provide rolling updates and rollbacks.

```yaml
# set-based-replicaset.yaml
# WHY THIS YAML: Shows the label selector matching that drives ReplicaSet reconciliation.
# 'replicas: 3': the controller watches this number and creates/deletes Pods to match it.
#   The moment a Pod terminates, the controller creates a replacement -- no human needed.
# 'selector.matchExpressions': set-based selectors -- the improvement over ReplicationController.
#   'In: [nginx, nginx-proxy]' matches Pods with either label value, not just exact equality.
# 'template.metadata.labels': MUST match the selector or the API server rejects the spec.
# Use Deployments, not raw ReplicaSets -- Deployments add versioning and rolling updates.
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: api-replicaset
  labels:
    app: api-server
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server
    matchExpressions:
    - key: environment
      operator: In
      values: ["staging", "production"]
  template:
    metadata:
      labels:
        app: api-server
        environment: production
    spec:
      containers:
      - name: api
        image: registry.k8s.io/pause:3.9
```"""

# ==============================================================================
# TOPIC 33: Deployment
# ==============================================================================
T33_TECH = """A **Deployment** is the standard, production-grade workload primitive in Kubernetes for stateless applications. It provides declarative updates, zero-downtime rolling releases, automated rollbacks, and replica scaling.

### What is a Deployment & Why Does It Exist? (Beginner)
A ReplicaSet is great at keeping 5 copies of an application running. But what happens when you release version 2.0 of your software?
If you simply updated the container image in a ReplicaSet:
- It wouldn't update existing running pods (it only creates new pods when pods die).
- If you killed all old pods simultaneously, your customers would experience **complete downtime** while new containers booted up.
- If version 2.0 had a fatal crash bug, you would have no automated way to revert to version 1.0.

A **Deployment** solves this by managing the transition between application versions:
- It creates and manages underlying ReplicaSets automatically.
- It performs **zero-downtime rolling updates**: it starts one v2 pod, waits until it is fully healthy, then terminates one v1 pod, repeating until all pods are upgraded.
- It preserves a revision history, enabling instant one-command rollbacks (`kubectl rollout undo`).

### Deployment Strategies & Rollout Controls (Intermediate)
Deployments support two primary update strategies:
1. **`RollingUpdate` (Default & Industry Standard):**
   Gradually replaces old replicas with new replicas without downtime. Controlled by two key parameters:
   - **`maxSurge`:** How many pods can be created *above* the desired replica count during the rollout (e.g., `25%` or `1`).
   - **`maxUnavailable`:** How many pods can be unavailable during the rollout (e.g., set to `0` for zero-downtime guarantees).
2. **`Recreate`:**
   Kills all existing version 1 pods before creating version 2 pods. Results in downtime, but necessary for applications that cannot tolerate two different versions accessing a shared database simultaneously.

#### Rollout Management Commands
- `kubectl rollout status deployment/<name>`: Streams live update progress.
- `kubectl rollout history deployment/<name>`: Lists historical revisions.
- `kubectl rollout undo deployment/<name> --to-revision=2`: Instantly rolls back to a previous working version.
- `kubectl rollout pause / resume deployment/<name>`: Pauses a canary rollout for validation.

### Rollout Internals & Readiness Gating (Advanced)
A rollout is coordinated entirely by the Deployment Controller in `kube-controller-manager`:
1. **The Twin ReplicaSet Mechanism:**
   When you update a Deployment's container image, the Deployment controller does *not* edit the existing ReplicaSet. Instead, it computes a hash of the new pod template and creates a **brand-new ReplicaSet** (e.g., `frontend-7b98f5c6d4`).
2. **The Traffic Shift:**
   The controller incrementally scales the new ReplicaSet up from 0 to 4 while scaling the old ReplicaSet down from 4 to 0, respecting `maxSurge` and `maxUnavailable`.
3. **Readiness Probe as the Safety Gate:**
   A new pod is only counted as available once its `readinessProbe` returns HTTP 200. If the new image crashes or fails health checks, the rollout **stalls automatically**, leaving the remaining healthy old pods in place to serve traffic.

```yaml
# zero-downtime-deployment.yaml
# WHY THIS YAML: Governs the rolling update strategy enabling zero-downtime releases.
# 'strategy.type: RollingUpdate': scales up new ReplicaSet while scaling down old one.
# 'maxSurge: 1': allows 1 extra Pod above replicas count during rollout.
#   New ReplicaSet scales to 4 before old ReplicaSet starts shrinking.
# 'maxUnavailable: 0': zero Pods may be below desired count during rollout.
#   Guarantees full capacity throughout update -- at the cost of extra resources.
# 'readinessProbe': each new Pod must pass readiness before an old Pod is terminated.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app
spec:
  replicas: 4
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx
        image: registry.k8s.io/pause:3.9
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```"""

# ==============================================================================
# TOPIC 34: StatefulSet
# ==============================================================================
T34_TECH = """A **StatefulSet** is the specialized workload controller in Kubernetes designed to manage stateful applications — such as databases, distributed consensus systems, and message brokers (Kafka, MongoDB, Cassandra, PostgreSQL, ZooKeeper) — that require unique identities and persistent storage per replica.

### What is a StatefulSet & Why Does It Exist? (Beginner)
Standard Deployments treat Pods as **completely interchangeable and fungible** (like cattle):
- Pods receive random names like `web-7d6f5c8b-x4k9z`.
- If a Pod dies, a replacement with a new random name and new IP address takes its place.
- All replicas share the exact same storage claims.

This model completely breaks distributed stateful databases:
- In a Cassandra or ZooKeeper cluster, node #1 (`db-0`) is the primary or has specific partition data that node #2 (`db-1`) does not have.
- If `db-0` restarts, it **must** retain its identity (`db-0`), keep its exact same DNS address, and reconnect to its exact same dedicated physical disk.
A **StatefulSet** solves this by treating Pods as unique, ordered individuals (like pets).

### The Three Guarantees of StatefulSets (Intermediate)
StatefulSets provide three fundamental architectural guarantees:
1. **Stable, Predictable Network Identities:**
   Pods are assigned a fixed ordinal index from 0 to $N-1$ (`web-0`, `web-1`, `web-2`). Coupled with a **Headless Service** (`clusterIP: None`), each Pod gets a predictable, permanent DNS name:
   `web-0.db-service.production.svc.cluster.local`
   Even if `web-0` is rescheduled to a completely different physical server, its DNS name remains identical.
2. **Dedicated, Persistent Storage per Replica (`volumeClaimTemplates`):**
   Instead of all replicas mounting the same disk, the StatefulSet uses a `volumeClaimTemplate` to automatically manufacture a **dedicated, separate PVC for every single replica** (`data-web-0`, `data-web-1`, `data-web-2`). If `web-1` crashes, its replacement pod automatically reattaches to `data-web-1`.
3. **Ordered Deployment, Scaling, and Termination:**
   - Scaling up: Pods are created sequentially in strict numerical order (`0 -> 1 -> 2`). Pod `N` must be fully Running and Ready before Pod `N+1` is started.
   - Scaling down: Pods are terminated in reverse order (`2 -> 1 -> 0`), preventing data loss in quorum systems.

### Quorum Clustering & Split-Brain Safeguards (Advanced)
- **Headless Service DNS Records:** CoreDNS creates direct `A` records for each stateful pod, allowing database nodes to discover peer nodes and negotiate Raft/Paxos leader election directly without userspace proxy interference.
- **Persistent Storage Retention on Scale-Down:** When a StatefulSet is scaled down (e.g., from 3 replicas to 2), the excess Pod (`web-2`) is terminated, but its PersistentVolumeClaim (`data-web-2`) is **intentionally NOT deleted**. This prevents accidental data loss during scale-down operations.
- **`podManagementPolicy: Parallel`:** For applications that need stable identities and dedicated disks but do not require ordered startup (e.g., certain distributed batch processing systems), setting `podManagementPolicy: Parallel` allows all replicas to boot concurrently.

```yaml
# clustered-statefulset.yaml
# WHY THIS YAML: StatefulSet's ordered identity guarantees are configured here.
# 'serviceName: "db-cluster"': creates a Headless Service for stable DNS per Pod.
#   'db-0.db-cluster.<ns>.svc.cluster.local' persists across Pod restarts.
#   This stable DNS identity is essential for distributed peers (Cassandra, Kafka).
# 'podManagementPolicy: OrderedReady': Pods created 0, 1, 2 in sequence; each must be
#   Ready before next starts. Scale-down reverses order (2, 1, 0).
# 'volumeClaimTemplates': each Pod gets its OWN PVC that persists even if StatefulSet is deleted.
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: "db-cluster"
  replicas: 3
  podManagementPolicy: OrderedReady
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: db-engine
        image: registry.k8s.io/pause:3.9
        volumeMounts:
        - name: data
          mountPath: /var/lib/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```"""

# ==============================================================================
# TOPIC 35: DaemonSet
# ==============================================================================
T35_TECH = """A **DaemonSet** is a workload controller that guarantees that all (or a selected subset of) worker nodes in the cluster run exactly one copy of a specific Pod.

### What is a DaemonSet & Why Does It Exist? (Beginner)
A standard Deployment places pods wherever there is available CPU and RAM. If you have 10 nodes and a Deployment with 3 replicas, Kubernetes might place 2 pods on Node 1, 1 pod on Node 2, and leave the other 8 nodes empty.
However, certain operational infrastructure tools **must run on every single node**:
- **Log Collection Agents:** Tools like Fluentd, Fluent Bit, or Logstash need to tail log files written by containers on every host disk.
- **Node Monitoring Agents:** Tools like Prometheus Node Exporter, Datadog, or New Relic need to scrape host-level CPU, disk I/O, and memory metrics.
- **Cluster Networking Agents:** Core network plugins like Calico, Cilium, or kube-proxy must run on every machine to configure host iptables and routing.

A **DaemonSet** automates this:
- As new worker nodes are added to the cluster, the DaemonSet controller automatically schedules the agent pod onto the new machine.
- As worker nodes are deleted or decommissioned, the DaemonSet pods are automatically garbage collected.

### Selection & Tolerations (Intermediate)
- **Node Selectors & Affinity:** By default, a DaemonSet runs on every node. You can restrict it to a specific subset of nodes using `nodeSelector` or `nodeAffinity` (e.g., only run GPU telemetry daemons on nodes with label `accelerator: nvidia-gpu`).
- **Running on Control Plane Nodes via Tolerations:** Control plane nodes carry taints like `node-role.kubernetes.io/control-plane:NoSchedule` to block normal application pods. Because monitoring and network daemons must cover the entire cluster, DaemonSets declare matching **tolerations** to run on control plane nodes alongside worker nodes.
- **Rolling Update Strategy:** Supports `RollingUpdate` (default), upgrading daemon pods node-by-node with a configurable `maxUnavailable` threshold.

### Host Integration & Kernel Privileges (Advanced)
Unlike standard application containers that remain strictly isolated within independent Linux namespaces, host monitoring and logging agents need direct access to the underlying machine's network stack and kernel diagnostics (`/proc`, `/sys`). DaemonSets achieve this privileged host visibility through explicit pod security settings:
- `hostNetwork: true`: The daemon shares the node's physical network namespace, allowing it to inspect host interfaces.
- `hostPID: true`: The daemon shares the host process tree, allowing monitoring agents to observe all processes running on the machine.
- `hostPath` Volume Mounts: Mounts `/var/log`, `/var/lib/docker`, or `/sys` from the host OS directly into the container filesystem.
- **Capacity Planning Reality:** DaemonSet resource consumption scales linearly with cluster size. A DaemonSet requesting 500m CPU across a 100-node cluster consumes 50 CPU cores cluster-wide.

```yaml
# node-exporter-daemonset.yaml
# WHY THIS YAML: DaemonSet guarantees one Pod per node -- node-exporter needs this.
# 'tolerations: node-role.kubernetes.io/control-plane: NoSchedule': without this,
#   DaemonSet skips control plane nodes. This toleration ensures ALL nodes are covered.
# 'hostPID: true' and 'hostNetwork: true': required to read host-level metrics
#   from /proc and /sys -- these are node-level capabilities normal apps avoid.
# 'resources.requests': DaemonSet Pods consume resources on EVERY node.
#   500m CPU on 100 nodes = 50 CPUs cluster-wide. Size very carefully.
# 'updateStrategy.type: RollingUpdate': updates node by node, preserving metric coverage.
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
      containers:
      - name: node-exporter
        image: registry.k8s.io/pause:3.9
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
```"""

# ==============================================================================
# TOPIC 36: Job
# ==============================================================================
T36_TECH = """A **Job** is a workload controller in Kubernetes that creates one or more Pods and tracks them to successful completion (process exit code 0), stopping when the required number of tasks finish.

### What is a Job & Why Does It Exist? (Beginner)
Controllers like Deployments, ReplicaSets, and DaemonSets are designed for **long-running continuous services** (web servers, APIs, caching daemons):
- If a web server container terminates, Kubernetes assumes it crashed and immediately restarts it.
- But what if you need to run a **finite, run-to-completion task**?
  - A database schema migration (`flyway migrate` or `rails db:migrate`).
  - An overnight data transformation script.
  - Generating and emailing monthly billing reports.

If you ran these batch tasks in a Deployment, the container would finish its task, exit with code 0 (success), and Kubernetes would immediately restart it, causing your billing report or database migration to run in an infinite loop!
A **Job** solves this by tracking tasks to completion: once the container exits with code 0, Kubernetes marks the Job complete and stops creating pods.

### Concurrency, Retries & Completion Controls (Intermediate)
A Job provides granular knobs to control batch execution:
- **`completions`:** How many successful pod completions are required before the Job is marked done (e.g., process 10 distinct message queues).
- **`parallelism`:** How many pods are allowed to run concurrently (e.g., run 2 worker pods at a time until 10 completions are achieved).
- **`backoffLimit`:** How many times Kubernetes will retry a failed pod before declaring the entire Job failed (default 6).
- **`activeDeadlineSeconds`:** A hard timeout duration. If the job runs longer than this limit, all running pods are terminated and the job fails with `DeadlineExceeded`.
- **`ttlSecondsAfterFinished`:** Automatically deletes the Job object and its finished pods after a designated time (e.g., 600s), preventing cluster state from accumulating thousands of dead historical batch jobs.

### Linux Process Termination & Failure Semantics (Advanced)
Batch computing requires knowing when a task has finished successfully versus crashed. The Job controller evaluates Linux process exit codes returned by the container runtime to determine job completion:
- **`restartPolicy: OnFailure`:** If the container process exits with non-zero, the local kubelet restarts the container inside the *same existing pod sandbox* on the same node (retaining cached data).
- **`restartPolicy: Never`:** If the container process fails, the kubelet leaves the failed pod in place for debugging, and the Job controller spawns a *brand-new pod* on potentially a different node.
- **Non-Retryable Failures (`podFailurePolicy`):** Modern Kubernetes allows defining failure rules: if a process exits with code 42 (e.g., invalid data format), fail the Job immediately without burning through retries.

```yaml
# batch-processing-job.yaml
# WHY THIS YAML: Job's completion tracking and retry semantics are configured here.
# 'completions: 4': Job must run 4 successful Pod completions to be considered Done.
#   Useful for parallelizing data processing across 4 independent dataset chunks.
# 'parallelism: 2': at most 2 Pods run simultaneously -- controls resource usage.
# 'backoffLimit: 3': after 3 failed Pod attempts, Job is marked Failed, no more Pods.
# 'restartPolicy: Never': failed containers get a NEW Pod, not an in-place restart.
# 'ttlSecondsAfterFinished: 600': auto-deletes Job and Pods 10 minutes after completion.
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-processor
spec:
  completions: 4
  parallelism: 2
  backoffLimit: 3
  ttlSecondsAfterFinished: 600
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: registry.k8s.io/pause:3.9
```"""

# ==============================================================================
# TOPIC 37: CronJob
# ==============================================================================
T37_TECH = """A **CronJob** runs Jobs on a recurring, automated time-based schedule using standard UNIX cron expressions (`minute hour day-of-month month day-of-week`).

### What is a CronJob & Why Does It Exist? (Beginner)
A standard Job runs once when you apply it to the cluster. But in production systems, many critical maintenance tasks must repeat on an automated schedule:
- Taking an etcd or database backup every night at 2:00 AM.
- Cleaning up temporary cloud storage buckets every Sunday at midnight.
- Generating and emailing weekly usage analytics every Monday morning.

Traditionally, administrators configured local Linux cron daemons (`crontab -e`) on individual servers. But if that specific server crashed, the cron job silently stopped running without alerting anyone.
A **CronJob** brings cron scheduling into the Kubernetes control plane:
- It is managed cluster-wide with high availability.
- At the scheduled time, the CronJob controller automatically creates a standard Kubernetes `Job` resource, which schedules and executes on any available worker node.

### Schedule Expressions & Concurrency Policies (Intermediate)
- **Schedule Syntax:** Standard 5-field cron format:
  - `0 2 * * *`: Every day at 2:00 AM UTC.
  - `*/15 * * * *`: Every 15 minutes.
  - `0 0 * * 0`: Every Sunday at midnight.
- **`concurrencyPolicy` (Preventing Overlapping Runs):**
  What happens if your 2:00 AM backup job takes 90 minutes to run, but the schedule triggers another job at 3:00 AM?
  - **`Allow` (Default):** Runs concurrent jobs simultaneously.
  - **`Forbid` (Critical for Backups):** If the previous job is still running, the CronJob controller skips the new execution, preventing database lock contention or corrupted backups.
  - **`Replace`:** Cancels the currently running job and starts a new one.
- **History Limits:** Controls how many finished Job objects are preserved:
  - `successfulJobsHistoryLimit`: default 3.
  - `failedJobsHistoryLimit`: default 1.

### Controller Timing & Missed Deadlines (Advanced)
- **`startingDeadlineSeconds`:** If the cluster control plane was down or uncontactable during the scheduled trigger window, this setting defines how long after the missed window the job can still be retroactively started. If missed by more than this threshold, the execution is recorded as missed and skipped.
- **Time Zone Support (`timeZone`):** Modern Kubernetes (1.27+) supports specifying explicit IANA time zones (e.g., `timeZone: "America/New_York"`), ensuring daylight saving time shifts do not disrupt business schedules.
- **Job Creation Semantics:** A CronJob is purely a scheduler — it does not run containers itself. It only creates `Job` objects, which in turn create `Pod` objects.

```yaml
# nightly-backup-cronjob.yaml
# WHY THIS YAML: CronJob's schedule and concurrency controls are configured here.
# 'schedule: "0 2 * * *"': runs at 2:00 AM UTC daily. The CronJob controller
#   compares this against cluster time and creates a Job object at each trigger.
# 'concurrencyPolicy: Forbid': if 2am Job is still running at 3am, 3am trigger is SKIPPED.
#   Prevents overlapping backup jobs from corrupting the same backup target.
# 'startingDeadlineSeconds: 300': if cluster was down at 2am, only schedules within
#   5 minutes of the missed trigger -- older missed runs are discarded.
# 'successfulJobsHistoryLimit: 3': limits retained completed Job objects for history inspection.
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 300
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup-agent
            image: registry.k8s.io/pause:3.9
```"""

# ==============================================================================
# TOPIC 39: HorizontalPodAutoscaler (HPA)
# ==============================================================================
T39_TECH = """The **HorizontalPodAutoscaler (HPA)** automatically scales the number of Pod replicas in a Deployment, ReplicaSet, or StatefulSet up or down in response to observed CPU utilization, memory consumption, or custom application metrics.

### What is HPA & Why Does It Exist? (Beginner)
Application traffic in real-world systems is rarely static:
- An e-commerce platform might need 4 pods on a quiet Tuesday morning, but requires 40 pods during Black Friday marketing rushes.
- If you permanently size your application for peak load, you waste thousands of dollars paying for idle cloud servers 90% of the year.
- If you size for average load, your application will crash under unexpected traffic surges.

The **HorizontalPodAutoscaler** solves this by automating capacity management:
- You declare: "Keep average CPU utilization around 60%, with a minimum of 2 pods and a maximum of 20 pods."
- When traffic surges and average CPU exceeds 60%, HPA automatically scales up the Deployment to add more pods.
- When traffic subsides, HPA scales back down to your minimum floor to save costs.

### The Autoscaling Algorithm & Metrics (Intermediate)
The HPA controller queries the `metrics.k8s.io` API (provided by Metrics Server) every 15 seconds (default `--horizontal-pod-autoscaler-sync-period`).
1. **The Scaling Formula:**
   $$\\text{Desired Replicas} = \\left\\lceil \\text{Current Replicas} \\times \\left( \\frac{\\text{Current Metric Value}}{\\text{Target Metric Value}} \\right) \\right\\rceil$$
   *Example:* If you have 2 replicas running at 90% CPU and your target is 60%: $\\lceil 2 \\times (90 / 60) \\rceil = 3$ replicas.
2. **Metric Types (`autoscaling/v2`):**
   - **Resource Metrics:** Built-in container metrics (`cpu`, `memory`).
   - **Custom Metrics:** Application-specific metrics from Prometheus (e.g., HTTP requests per second, queue depth).
   - **External Metrics:** Metrics originating outside the cluster (e.g., AWS SQS message backlog size).
3. **Mandatory Resource Requests:**
   HPA calculates CPU utilization as a percentage of the container's **`resources.requests.cpu`**. If a Pod does not declare CPU requests, HPA cannot calculate percentage utilization and will fail to autoscale!

### Stabilization Windows & Flapping Prevention (Advanced)
To prevent rapid "flapping" (repeatedly scaling up and down in response to short bursty traffic spikes), HPA provides fine-grained **`behavior` controls**:
- **Scale-Down Stabilization Window (Default 300s):** When traffic drops, HPA waits 5 minutes before removing pods, ensuring that a transient traffic dip doesn't prematurely terminate replicas needed for subsequent requests.
- **Rate-Limiting Scaling Velocity:** Operators can set limits (e.g., "scale up by at most 100% or 4 pods per minute") to prevent sudden resource starvation across worker nodes.

```yaml
# hpa-v2-production.yaml
# WHY THIS YAML: HPA v2 spec shows the metrics and scaling behavior configuration.
# 'scaleTargetRef': HPA controller watches this Deployment and adjusts 'spec.replicas'.
# 'metrics.type: Resource / averageUtilization: 60': scales when avg CPU exceeds 60%.
#   Formula: desiredReplicas = ceil(currentReplicas x currentCPU / 60).
# 'minReplicas: 2 / maxReplicas: 20': HPA never goes below 2 (availability) or above 20 (cost).
# 'stabilizationWindowSeconds: 300': prevents scale-down for 5 min after a spike (anti-flapping).
# REQUIRES 'resources.requests.cpu' on every Pod -- without it, utilization is undefined.
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-autoscaler
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```"""

# ==============================================================================
# TOPIC 41: PodDisruptionBudget (PDB)
# ==============================================================================
T41_TECH = """A **PodDisruptionBudget (PDB)** limits the number of concurrent voluntary disruptions that an application's Pods can suffer during cluster maintenance operations, safeguarding high availability.

### Voluntary vs. Involuntary Disruptions (Beginner)
In a Kubernetes cluster, workloads face two completely different categories of disruption:
1. **Involuntary Disruptions:** Uncontrollable hardware or cloud outages:
   - A physical server loses power.
   - A cloud hypervisor crashes.
   - A kernel panic or network switch failure.
   *(Kubernetes handles involuntary disruptions via the Node Controller and self-healing).*
2. **Voluntary Disruptions:** Planned maintenance initiated by cluster operators or automated system agents:
   - An administrator runs `kubectl drain <node>` to upgrade the host Linux kernel.
   - The Cluster Autoscaler drains an under-utilized node to scale down the VM fleet and save money.
   - A Deployment rolling update replaces pods.

If an automated node-drain operation evicts all 3 replicas of your payment service simultaneously, **your application suffers a complete outage during planned maintenance!**
A **PodDisruptionBudget** acts as a contractual safety limit: it tells cluster maintenance tools: "You are allowed to evict pods for maintenance, but you must ensure at least 2 replicas remain alive at all times."

### PDB Specifications: minAvailable vs. maxUnavailable (Intermediate)
A PDB targets Pods using label selectors and defines one of two constraint formulas:
- **`minAvailable`:** Specifies the minimum number (or percentage) of Pods that must remain running and Ready during maintenance:
  - `minAvailable: 2` (at least 2 pods must stay alive)
  - `minAvailable: 75%` (at least 75% of desired replicas must stay alive)
- **`maxUnavailable`:** Specifies the maximum number of Pods that can be disrupted concurrently:
  - `maxUnavailable: 1` (maintenance tools can only take down 1 pod at a time)
  - `maxUnavailable: 20%`

#### The Critical Sizing Deadlock Trap
A common operational mistake is configuring `minAvailable: 3` on a Deployment with only `replicas: 3`:
- If an administrator tries to drain a node running one of those pods, the Eviction API sees that evicting 1 pod would leave only 2 available — violating `minAvailable: 3`.
- The drain operation will **block indefinitely**, hanging automated cluster upgrades and node maintenance forever!
- **Rule of Thumb:** Always ensure `minAvailable < replicas`.

### The Eviction API Interception Mechanics (Advanced)
A PodDisruptionBudget is enforced by the **Eviction API** (`/v1/pods/<name>/eviction`):
1. **The Interception:** When an administrator runs `kubectl drain`, the CLI does *not* call `DELETE /api/v1/pods/<name>`. Instead, it sends an HTTP POST to the pod's `eviction` subresource.
2. **Policy Verification:** The API server inspects all active PDBs matching the target pod.
3. **Verdict:**
   - If disrupting the pod satisfies the budget: The pod is safely deleted and marked for rescheduling.
   - If disrupting the pod violates the budget: The API server returns **HTTP 429 Too Many Requests**, and the drain tool pauses, backs off, and retries later until a new replica becomes ready on another node.

```yaml
# pdb-high-availability.yaml
# WHY THIS YAML: PDB protects workload availability during planned (voluntary) disruptions.
# 'selector.matchLabels: app: critical-api': PDB applies to all Pods with this label.
# 'minAvailable: 2': the Eviction API (used by 'kubectl drain') REFUSES to evict
#   a Pod if doing so would drop available Pod count below 2. Drain pauses and waits.
# PDB ONLY protects against voluntary disruptions: drain, rolling updates, cluster upgrades.
#   A node CRASH bypasses PDB -- it is not a voluntary disruption.
# Critical rule: 'minAvailable' must be less than total replicas.
#   minAvailable: 3 with replicas: 3 = drain blocks forever -- never undrained.
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: critical-api
```"""

def apply_all():
    # 1. enriched_topics_21_30.py (Topics 21, 22, 23)
    with open("scripts/enriched_topics_21_30.py", "r", encoding="utf-8") as f:
        c21_30 = f.read()
    c21_30 = re.sub(r'(21:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T21_TECH.replace('\\', '\\\\') + r'\g<2>', c21_30, flags=re.S)
    c21_30 = re.sub(r'(22:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T22_TECH.replace('\\', '\\\\') + r'\g<2>', c21_30, flags=re.S)
    c21_30 = re.sub(r'(23:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T23_TECH.replace('\\', '\\\\') + r'\g<2>', c21_30, flags=re.S)
    with open("scripts/enriched_topics_21_30.py", "w", encoding="utf-8") as f:
        f.write(c21_30)
    print("Updated enriched_topics_21_30.py (Topics 21, 22, 23)")

    # 2. enriched_topics_31_41.py (Topics 32, 33, 34, 35, 36, 37, 39, 41)
    with open("scripts/enriched_topics_31_41.py", "r", encoding="utf-8") as f:
        c31_41 = f.read()
    c31_41 = re.sub(r'(32:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T32_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(33:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T33_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(34:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T34_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(35:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T35_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(36:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T36_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(37:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T37_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(39:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T39_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    c31_41 = re.sub(r'(41:\s*{\s*"tech_disc":\s*""").*?("""\s*,\s*"tech_persp")', r'\g<1>' + T41_TECH.replace('\\', '\\\\') + r'\g<2>', c31_41, flags=re.S)
    with open("scripts/enriched_topics_31_41.py", "w", encoding="utf-8") as f:
        f.write(c31_41)
    print("Updated enriched_topics_31_41.py (Topics 32, 33, 34, 35, 36, 37, 39, 41)")

if __name__ == "__main__":
    apply_all()
