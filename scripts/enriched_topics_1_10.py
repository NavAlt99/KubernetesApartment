# scripts/enriched_topics_1_10.py
"""
Enriched technical discussions and perspectives for Topics 1-10.
Incorporates deep CKA Study Notes, Linux OS/Kernel concepts, bulleted points,
and production-grade YAML manifests.
"""

ENRICHED_1_10 = {
    1: {
        "tech_disc": """Kubernetes is an open-source, production-grade container orchestration system designed to automate the deployment, scaling, and operational lifecycle of containerized application workloads across distributed server clusters. Rather than managing physical or virtual servers as independent hosts requiring manual intervention, Kubernetes unifies compute, storage, and networking into a single declarative API plane.

### Core Architecture & Reconciliation Engine
- **Declarative State Model:** System state is declared as intent-driven objects (Pods, Deployments, Services). Operators never imperatively configure machines; instead, they declare the *target state*, and Kubernetes executes continuous reconciliation.
- **Continuous Control Loops:** Autonomous controllers repeatedly query actual cluster state against declared state in etcd. Any detected drift (e.g., node failure, process termination, network partition) triggers corrective reconciliation workflows.
- **Bin-Packing & Resource Efficiency:** The platform schedules containers dynamically based on declared resource requests and limits, maximizing host density while respecting compute, memory, and topology boundaries.
- **Three-Way Merge Apply:** Modern cluster management relies on `kubectl apply`, which computes a three-way diff between the local configuration manifest, the live cluster state, and the `kubectl.kubernetes.io/last-applied-configuration` annotation.

### Linux Kernel & OS Foundation
- **Namespaces (Isolation):** Linux namespaces (`pid`, `net`, `mnt`, `ipc`, `uts`, `user`) partition kernel resources so containers operate in isolated process spaces on shared Linux kernels.
- **Control Groups (cgroups v1/v2):** Kernel cgroups enforce granular compute constraints (CFS CPU bandwidth quota in `cpu.cfs_quota_us`, hard memory limits in `memory.max`, and block I/O priorities).
- **Systemd & Container Daemons:** Nodes execute as Linux systems managed by systemd, with system daemons (`kubelet`, `containerd`) running as prioritized system units.

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
```""",
        "tech_persp": """From an engineering and SRE perspective, Kubernetes shifts complexity from individual host administration to cluster lifecycle governance. While individual nodes become disposable cattle that can be replaced or upgraded without application downtime, the cluster itself introduces distributed systems operational overhead:
- **Blast Radius Boundaries:** A misconfigured admission webhook or global NetworkPolicy can disrupt cluster-wide workloads in seconds.
- **Kernel & Driver Compatibility:** Worker nodes depend on consistent Linux kernel configurations (`sysctl` network forwarding, overlayfs modules, and container runtime socket stability).
- **Control Plane Sizing:** As cluster object count grows, etcd memory footprint and kube-apiserver serialization latency scale non-linearly, requiring strict resource quotas and API rate limiting."""
    },

    2: {
        "tech_disc": """A Kubernetes cluster is strictly divided into two functional tiers: the **Control Plane** (the cluster brain responsible for state, decisions, and API orchestration) and **Worker Nodes** (the execution engines that run containerized workloads).

### Control Plane Anatomy & Topologies
- **Stacked Control Plane Topology:** Control plane components (`kube-apiserver`, `kube-controller-manager`, `kube-scheduler`) co-locate with etcd instances on dedicated control plane nodes. Recommended minimum: 3 nodes for quorum.
- **External etcd Topology:** etcd runs on dedicated external servers separated from API servers, isolating storage I/O from API compute workloads.
- **Node Heartbeats via NodeLeases:** In modern Kubernetes, worker nodes report heartbeats through lightweight `Lease` objects in the `kube-node-lease` namespace every 10 seconds, drastically reducing `kube-apiserver` etcd write load compared to full Node status updates.

### Linux OS Node Requirements
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
```""",
        "tech_persp": """The primary operational boundary in cluster design is preventing control plane starvation from noisy worker node tenants:
- **Control Plane Taints:** Control plane nodes are tainted with `node-role.kubernetes.io/control-plane:NoSchedule` by default so business workloads never consume control plane CPU or memory.
- **Split-Brain Scenarios:** If network partitions sever worker nodes from the control plane, local workloads continue running under kubelet supervision, but after the controller-manager `node-monitor-grace-period` (default 40s), the node is marked `NotReady`, and pod eviction scheduling begins after `pod-eviction-timeout` (default 5m)."""
    },

    3: {
        "tech_disc": """The `kube-apiserver` is the central gateway, management bridge, and only component in the cluster that directly interfaces with the `etcd` datastore. All other control plane components, worker node daemons, and user CLI tools communicate exclusively via the API server over secure HTTPS (port 6443).

### Request Processing Lifecycle Pipeline
1. **Authentication (AuthN):** Validates the caller's identity via X.509 Client Certificates (`/etc/kubernetes/pki`), OpenID Connect (OIDC) JWT tokens, or ServiceAccount bearer tokens.
2. **Authorization (AuthZ):** Evaluates permissions against access control modules. Configured via `--authorization-mode=Node,RBAC` to enforce least-privilege role policies and node self-isolation.
3. **Mutating Admission Controllers:** Intercepts requests to inject default values, sidecars, or storage policies (e.g., `DefaultStorageClass`, `MutatingAdmissionWebhook`).
4. **Schema Validation:** Verifies structural schema conformity against openAPI specifications.
5. **Validating Admission Controllers:** Evaluates compliance rules and security postures (e.g., `PodSecurity`, `ResourceQuota`, `ValidatingAdmissionWebhook`). Rejections immediately return HTTP 400/403.
6. **Persistence:** Serializes the validated object and commits it directly to `etcd`.

### Linux System & Network Concepts
- **mTLS Mutual Authentication:** Every connection requires bidirectional cryptographic verification using certificates signed by the cluster Certificate Authority (`ca.crt`).
- **HTTP/2 Streaming & Watch API:** Uses HTTP/2 persistent streaming multiplexing to support `watch` calls, pushing asynchronous state change notifications instantly to subscribed controllers without polling.

```yaml
# /etc/kubernetes/manifests/kube-apiserver.yaml -- Static Pod excerpt
# WHY THIS YAML: kube-apiserver itself runs as a Static Pod — its own manifest.
# '--secure-port=6443': the single front door; ALL kubectl, controller, and kubelet
#   traffic hits this port. No component bypasses it.
# '--etcd-servers': proves kube-apiserver is the ONLY component that talks to etcd.
# '--authorization-mode=Node,RBAC': every request traverses this AuthZ chain.
# '--enable-admission-plugins': defines what mutation/validation runs before etcd write.
apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - name: kube-apiserver
    image: registry.k8s.io/kube-apiserver:v1.28.0
    command:
    - kube-apiserver
    - --advertise-address=192.168.1.10
    - --secure-port=6443
    - --etcd-servers=https://127.0.0.1:2379
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
    - --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key
    - --authorization-mode=Node,RBAC
    - --enable-admission-plugins=NodeRestriction,LimitRanger,ResourceQuota
```""",
        "tech_persp": """The API server is stateless and horizontally scalable behind a TCP Layer-4 Load Balancer (HAProxy, Envoy, or AWS NLB). 
- **Production Vulnerabilities:** Unbounded watch queries (`kubectl get pods -A --watch`) from high numbers of controllers or CI/CD pipelines can exhaust API server memory.
- **Priority and Fairness (APF):** Modern clusters employ API Priority and Fairness to classify traffic into distinct priority queues (`workload-high`, `workload-low`, `system`), guaranteeing administrative access even during DDoS surges."""
    },

    4: {
        "tech_disc": """`etcd` is a strongly consistent, distributed, transactional key-value store that implements the **Raft Consensus Algorithm**. It acts as the single source of truth for all Kubernetes state, storing object specifications, status, metadata, and leases under hierarchical keys (e.g., `/registry/pods/default/nginx`).

### Raft Consensus & Quorum Mechanics
- **Leader Election & Heartbeats:** In a cluster of $N$ nodes, a majority quorum of $Q = \\lfloor N/2 \\rfloor + 1$ members is strictly required to commit any read/write transaction.
- **Cluster Sizing & Tolerances:**
  - 3 nodes: Quorum is 2 (tolerates 1 node failure).
  - 5 nodes: Quorum is 3 (tolerates 2 node failures).
  - Even numbers of nodes (e.g., 4 or 6) provide no extra failure tolerance and increase communication overhead.
- **MVCC (Multi-Version Concurrency Control):** etcd maintains historical revisions of keys. Compaction processes prune historical tombstones to prevent database bloat, followed by defragmentation to reclaim disk space.

### Linux Storage & Performance Realities
- **Fsync Latency Requirement:** etcd commits every transaction to disk using synchronous writes (`fdatasync`). Sequential write latency must remain below **10ms** (ideally < 2ms) to prevent Raft leader election timeouts and cluster instability. High-IOPS NVMe/SSD storage is non-negotiable.
- **BoltDB Engine:** Uses a B+ tree memory-mapped file backend (`bbolt`), benefiting directly from Linux kernel page cache performance.

```yaml
# etcd-backup-cronjob.yaml
# WHY THIS YAML: etcd is the single source of truth for ALL cluster state.
# This CronJob automates the critical disaster recovery operation: etcdctl snapshot save.
# 'schedule: "0 */4 * * *"': every 4 hours — data written since the last snapshot
#   is unrecoverable if etcd loses quorum and all members fail simultaneously.
# '--endpoints=https://127.0.0.1:2379': etcd is only reachable locally (by design).
# '--cacert/--cert/--key': etcd requires mTLS — the cluster CA chain in action.
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-snapshot-backup
  namespace: kube-system
spec:
  schedule: "0 */4 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: etcd-backup
            image: registry.k8s.io/etcd:3.5.9-0
            env:
            - name: ETCDCTL_API
              value: "3"
            command:
            - /bin/sh
            - -c
            - etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key snapshot save /backup/etcd-snapshot-$(date +%s).db
```""",
        "tech_persp": """etcd is the most critical failure point in Kubernetes. If etcd loses quorum, the entire control plane enters read-only failure: no pods can be created, updated, or scheduled, and controllers stall.
- **CKA Disaster Recovery Drill:** Administrators must master taking snapshots with `ETCDCTL_API=3 etcdctl snapshot save <file>` and restoring via `etcdctl snapshot restore <file> --data-dir=/var/lib/etcd-from-backup`.
- **Space Quotas:** etcd enforces a default 2GB storage quota (expandable to 8GB). Exceeding this quota triggers an `NOSPACE` alarm that locks the cluster into read-only mode until compaction and defragmentation are completed."""
    },

    5: {
        "tech_disc": """The `kube-scheduler` is the control plane component responsible for assigning newly created or unscheduled Pods (`spec.nodeName == ""`) to the most appropriate Worker Node in the cluster. It operates by watching the API server for unbound Pods and evaluating candidate nodes through a rigorous two-phase pipeline.

### Two-Phase Scheduling Pipeline
1. **Filtering Phase (Predicates):** Filters out nodes that do not meet the Pod's mandatory criteria.
   - `NodeResourcesFit`: Node has sufficient available CPU and memory allocatable capacity.
   - `NodeName` & `NodeSelector`: Checks explicit node names and key-value label selectors.
   - `PodTopologySpread`: Enforces failure domain distribution across zones or racks.
   - `NodePorts`: Verifies required host ports are not already occupied.
   - `Tolerations`: Ensures the Pod tolerates any active taints on the node.
2. **Scoring Phase (Priorities):** Ranks the remaining eligible nodes from 0 to 100 based on scoring plugins.
   - `ImageLocality`: Favors nodes that already have container images cached locally.
   - `NodeResourcesBalancedAllocation`: Scores nodes that achieve balanced CPU and memory utilization ratios.
   - `NodeAffinityScoring`: Awards higher scores for `preferredDuringSchedulingIgnoredDuringExecution` affinity rules.
3. **Binding Phase:** The scheduler constructs a `Binding` API object pointing the Pod to the winning node and posts it to `kube-apiserver`, populating `spec.nodeName`.

### Linux Capacity Evaluation
- The scheduler reads node capacity summaries reported by the kubelet based on kernel `/proc/meminfo` and `/sys/fs/cgroup/cpu` controllers.
- Workloads are evaluated against **Requests** (guaranteed reservation allocated by scheduler), not **Limits** (enforced by kernel cgroups).

```yaml
# advanced-pod-scheduling.yaml
# WHY THIS YAML: Demonstrates both phases of kube-scheduler's pipeline.
# FILTERING: 'tolerations' removes nodes that have the 'dedicated=high-compute:NoSchedule'
#   taint — without matching, the Scheduler discards those nodes before scoring.
# FILTERING + SCORING: 'requiredDuringScheduling' eliminates nodes outside allowed zones.
# 'resources.requests': the Scheduler checks NodeResourcesFit using these values —
#   nodes without 250m CPU or 256Mi free allocatable capacity are filtered out.
apiVersion: v1
kind: Pod
metadata:
  name: critical-service
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "high-compute"
    effect: "NoSchedule"
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values: ["us-east-1a", "us-east-1b"]
  containers:
  - name: app
    image: registry.k8s.io/pause:3.9
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
```""",
        "tech_persp": """The scheduler guarantees placement feasibility at scheduling time, but does not monitor subsequent node runtime performance:
- **Custom Schedulers:** Multiple schedulers can run concurrently. A pod declares a specific scheduler via `spec.schedulerName: custom-scheduler`.
- **Pending Pod Diagnosis:** If all nodes fail the filtering stage, the Pod remains stuck in `Pending`. Engineers troubleshoot this via `kubectl describe pod <name>` to view scheduler predicate events (e.g., `0/3 nodes available: 3 Insufficient memory`)."""
    },

    6: {
        "tech_disc": """The `kube-controller-manager` is a single binary that bundles dozens of distinct, autonomous control loops into a single process. Each controller is responsible for reconciling a specific slice of cluster state towards its declared intent.

### Core Bundled Controllers
- **Node Lifecycle Controller:** Monitors node health leases, assigns CIDR blocks, manages node taints (`node.kubernetes.io/unreachable`), and handles eviction timeouts.
- **ReplicaSet / Deployment Controller:** Ensures the exact number of Pod replicas declared in workload specs are running, creating or deleting pods as needed.
- **EndpointSlice Controller:** Watches Services and Pods to maintain updated network routing endpoint collections.
- **Job / CronJob Controller:** Spawns batch pods according to schedule and monitors them to completion exit codes.
- **ServiceAccount & Namespace Controllers:** Generates default ServiceAccounts and default tokens; cleans up resources during namespace deletion.

### High Availability & Leader Election
- When multiple control plane nodes run the controller manager, only **one** instance acts as active leader at any given time.
- Active leadership is acquired via a distributed lease lock stored as a `Lease` object in `kube-system` (`coordination.k8s.io/v1`). Standby instances continuously poll the lease, taking over immediately if the leader fails to renew within the renewal interval.

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
    - --leader-elect=true
    - --node-monitor-grace-period=40s
    - --node-monitor-period=5s
    - --pod-eviction-timeout=5m0s
    - --allocate-node-cidrs=true
    - --cluster-cidr=10.244.0.0/16
```""",
        "tech_persp": """Controllers operate on an **eventual consistency** paradigm. They are designed to be idempotent: running the reconciliation loop multiple times with the same input produces the exact same cluster state:
- **Rate-Limiting & Backoff:** If a controller repeatedly fails an operation (such as failing to create a Pod due to quota exhaustion), it applies exponential backoff to protect the API server from request flooding.
- **Cascading Deletions:** The Garbage Collector controller tracks parent-child hierarchies via `ownerReferences` on objects, ensuring that deleting a Deployment automatically cascades down to delete its managed ReplicaSets and Pods."""
    },

    7: {
        "tech_disc": """The `cloud-controller-manager` (CCM) isolates cloud-vendor-specific control loops from core Kubernetes codebase. Historically, cloud provider logic (AWS, Azure, GCP, OpenStack) was compiled directly into `kube-controller-manager` ("in-tree"). The modern architecture moves all vendor integration to an external out-of-tree binary.

### Key CCM Controllers
- **Node Controller:** Periodically checks cloud provider APIs to confirm if nodes that became unresponsive in Kubernetes have actually been terminated or deleted in the cloud console, cleaning them up promptly.
- **Route Controller:** Configures VPC routing tables and subnets so that Pod CIDR network packets can route between distinct VMs across cloud availability zones.
- **Service Controller:** Watches Services of `type: LoadBalancer` and interacts with cloud provider APIs to provision, configure, and delete cloud load balancers (AWS NLB/ALB, Google Cloud Load Balancing, Azure Load Balancer).

### Operational Integration
- The kubelet runs with `--cloud-provider=external`, marking the node with a taint `node.cloudprovider.kubernetes.io/uninitialized:NoSchedule` until the CCM initializes the node with cloud metadata (Zone, Region, InstanceType, ProviderID).

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
  name: cloud-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "instance"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
spec:
  type: LoadBalancer
  selector:
    app: public-web
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
```""",
        "tech_persp": """Running out-of-tree CCM decouples Kubernetes releases from cloud provider bugfixes:
- **Cloud IAM Identity:** The CCM requires explicit cloud IAM roles and credentials (or Workload Identity/IRSA) with permissions to provision network interfaces, load balancers, and route tables.
- **Orphaned Cloud Costs:** If a namespace containing a LoadBalancer Service is deleted forcefully while CCM is malfunctioning, the external cloud load balancer may remain active in the cloud account, incurring silent billing costs."""
    },

    8: {
        "tech_disc": """**Static Pods** are pods managed directly and exclusively by the local `kubelet` daemon on a specific node, completely bypassing the `kube-apiserver`, `kube-scheduler`, and workload controllers.

### Bootstrapping & Discovery Mechanism
- **Manifest Directory:** The kubelet periodically scans a local filesystem directory (configured via `staticPodPath` in `/var/lib/kubelet/config.yaml`, standard path: `/etc/kubernetes/manifests/`) using Linux `inotify` watches.
- **Local Supervision:** When a valid Pod manifest is written into this directory, the kubelet directly instructs the local container runtime to launch the containers. If the manifest is deleted, the kubelet terminates the containers immediately.
- **Mirror Pods:** To provide cluster observability, the kubelet creates a read-only **Mirror Pod** in the `kube-system` namespace on `kube-apiserver`. The mirror pod reflects status in `kubectl get pods`, but cannot be deleted or modified through the API.
- **Control Plane Self-Hosting:** Standard tools like `kubeadm` use static pods to bootstrap the entire Kubernetes control plane (`kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler`).

### Linux OS Integration
- Static pods execute container runtimes while the control plane is offline or uninitialized.
- File ownership in `/etc/kubernetes/manifests/` must be restricted to `root:root` with permissions `0600` or `0644`.

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
  - name: diagnostic-agent
    image: registry.k8s.io/pause:3.9
    volumeMounts:
    - name: host-log
      mountPath: /var/log
  volumes:
  - name: host-log
    hostPath:
      path: /var/log
```""",
        "tech_persp": """Static pods are the backbone of Kubernetes cluster bootstrapping and node-level operational recovery:
- **CKA Troubleshooting Pattern:** If `kubectl get nodes` fails because the API server is down, check `/etc/kubernetes/manifests/` on the control plane node. Inspect the manifest files and review container logs via `crictl ps` and `crictl logs <container-id>` or `/var/log/pods/`.
- **Name Appending:** The kubelet automatically appends the node hostname as a suffix to the static pod name (e.g., `kube-apiserver-control-plane-01`)."""
    },

    9: {
        "tech_disc": """The `kubelet` is the primary node-level agent that runs on every machine in the cluster. It bridges the Kubernetes declarative control plane and the host Linux operating system. It does not manage containers directly; instead, it orchestrates container lifecycle through standardized gRPC interfaces: **CRI** (runtime), **CNI** (networking), and **CSI** (storage).

### Kubelet Operational Architecture
- **PodSpec Watching:** Watches for PodSpecs assigned to its node from the API server, local manifest directory (`/etc/kubernetes/manifests`), or an HTTP URL endpoint.
- **Volume Mounting & Attachment:** Coordinates with CSI plugins to attach, format (`mkfs.ext4`), and mount PersistentVolumes into `/var/lib/kubelet/pods/<pod-uid>/volumes/`.
- **Health Probing Engine:**
  - `startupProbe`: Verifies slow-starting applications have initialized before enabling liveness checks.
  - `livenessProbe`: Determines when to restart a crashed or deadlocked container.
  - `readinessProbe`: Controls whether the Pod receives network traffic via Service Endpoints.
- **Node Status & Heartbeats:** Updates node conditions (`Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure`) and refreshes its 10-second `Lease` in `kube-node-lease`.

### Linux System & Kernel Mechanisms
- **cgroup Management:** Coordinates with systemd via `cgroupDriver: systemd` to create and nest cgroup hierarchies under `/sys/fs/cgroup/kubepods.slice/`.
- **OOM Score Adjustment:** Configures `/proc/<pid>/oom_score_adj` based on QoS class (`Guaranteed` = -997, `Burstable` = 100-999, `BestEffort` = 1000) so Linux kernel out-of-memory killer terminates non-critical pods first under host memory starvation.
- **Eviction Manager:** Monitors host thresholds (e.g., `imagefs.available < 15%`, `nodefs.available < 10%`, `memory.available < 100Mi`) and proactively evicts pods before kernel panics occur.

```yaml
# pod-with-probes.yaml
# WHY THIS YAML: These probes are the kubelet's health monitoring directives.
# 'startupProbe': kubelet will NOT run livenessProbe until this succeeds.
#   'failureThreshold: 30 x periodSeconds: 10' = up to 300s for slow startup.
#   Without this, slow-starting apps are killed by liveness checks prematurely.
# 'livenessProbe': failure causes kubelet to instruct the CRI to restart the container.
# 'readinessProbe': failure removes the Pod from the Service's EndpointSlice.
#   The kubelet -- not the API server -- executes these probes on the node locally.
apiVersion: v1
kind: Pod
metadata:
  name: resilient-web
spec:
  containers:
  - name: web
    image: registry.k8s.io/pause:3.9
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 15
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
```""",
        "tech_persp": """The kubelet is the ultimate authority on node execution:
- **Systemd Service Troubleshooting:** Kubelet runs as a native systemd unit (`systemctl status kubelet`, `journalctl -u kubelet -f`). Misconfigured cgroup drivers (`cgroupfs` vs `systemd`) are the #1 cause of kubelet boot failure.
- **Port 10250 Security:** Kubelet exposes an HTTPS API on port 10250 for `kubectl logs` and `kubectl exec`. This endpoint must be secured with `--anonymous-auth=false` and `--authorization-mode=Webhook` to prevent unauthenticated remote code execution."""
    },

    10: {
        "tech_disc": """`kube-proxy` is the network proxy that runs on every node in the cluster, responsible for implementing the Kubernetes **Service** virtual IP abstraction (ClusterIP). It does not act as an application-level reverse proxy; rather, it programs host Linux kernel networking rules to intercept traffic destined for Service IPs and translate them to Pod backend IPs.

### Operating Modes & Evolution
- **iptables Mode (Default):**
  - Programs Netfilter chains (`PREROUTING`, `OUTPUT`, `KUBE-SERVICES`, `KUBE-SVC-*`, `KUBE-SEP-*`).
  - Implements random load balancing using the `statistic` module (`-m statistic --mode random --probability 0.5`).
  - Limitation: Sequential rule evaluation causes $O(n)$ latency degradation when cluster Services exceed 5,000+.
- **IPVS Mode (High Scale):**
  - Utilizes Linux IP Virtual Server (L4 transport balancer) built into the Linux kernel.
  - Implements $O(1)$ hash table lookups with configurable load balancing algorithms (round-robin, least connections, source hashing).
- **Userspace Mode (Obsolete):**
  - Routed packets via user-space socket copies; deprecated due to excessive context-switch overhead.

### Linux Netfilter & Connection Tracking
- **DNAT (Destination NAT):** Rewrites the destination IP from virtual ClusterIP (`10.96.x.x`) to the selected Pod IP (`10.244.x.x`).
- **SNAT / Masquerade:** Rewrites source IP when traffic leaves the pod network or when `externalTrafficPolicy: Cluster` is used on NodePort.
- **conntrack:** Relies on the Linux kernel connection tracking table (`/proc/net/nf_conntrack`) to ensure return packets are un-NATed symmetrically.

```yaml
# service-network-spec.yaml
# WHY THIS YAML: This ClusterIP Service triggers kube-proxy's iptables/IPVS programming.
# 'type: ClusterIP': creates a virtual IP that exists nowhere physically.
#   It works ONLY because kube-proxy programs iptables DNAT rules on every node.
# 'selector: app: backend-api': kube-proxy reads the matching EndpointSlice to know
#   which Pod IPs to include in the DNAT rules. Rules update as Pods come and go.
# 'port: 80 -> targetPort: 8080': iptables rewrites BOTH destination IP and port.
# Without kube-proxy's rules, this ClusterIP would be completely unreachable.
apiVersion: v1
kind: Service
metadata:
  name: internal-api
spec:
  type: ClusterIP
  selector:
    app: backend-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```""",
        "tech_persp": """Understanding kube-proxy is essential for debugging service connectivity:
- **Virtual IP Non-Routability:** ClusterIPs are virtual synthetic IPs that do not belong to any physical or virtual network interface (`ip addr show` will never display a ClusterIP). Ping (`ICMP`) to a ClusterIP will fail by design unless explicitly answered by iptables.
- **Conntrack Table Exhaustion:** High-volume UDP workloads (such as DNS floods) can fill `/proc/sys/net/netfilter/nf_conntrack_max`, leading to dropped connections across the entire node."""
    }
}
