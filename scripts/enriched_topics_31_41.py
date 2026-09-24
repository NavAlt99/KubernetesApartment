# scripts/enriched_topics_31_41.py
"""
Enriched technical discussions and perspectives for Topics 31-41.
Incorporates deep CKA Study Notes, Linux OS/Kernel concepts, bulleted points,
and production-grade YAML manifests.
"""

ENRICHED_31_41 = {
    31: {
        "tech_disc": """The **Garbage Collector (GC)** is a core controller inside `kube-controller-manager` responsible for identifying and cleaning up orphaned API objects whose parent owner object has been deleted.

### Owner References & Ownership Hierarchies
- Objects declare ownership via the `metadata.ownerReferences` array in their API specification:
  - `apiVersion`: API group and version of parent.
  - `kind`: Kind of parent resource (e.g., `ReplicaSet`, `Job`).
  - `name`: Name of the parent.
  - `uid`: Universally unique identifier of the parent.
  - `blockOwnerDeletion: true`: Prevents parent deletion from completing until dependents are processed.

### Deletion Propagation Policies
- **`Foreground`:** The owner enters a deletion phase with finalizer `foregroundDeletion`. The owner remains visible until all dependent children with `blockOwnerDeletion: true` are completely deleted.
- **`Background` (Default):** The owner is deleted immediately. The Garbage Collector then asynchronously discovers and deletes the orphaned children in the background.
- **`Orphan`:** Strips the `ownerReferences` from dependent children and leaves them running independently without a parent controller.

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
```""",
        "tech_persp": """Cascading deletion control is essential when replacing parent controllers:
- **CLI Propagation Options:** `kubectl delete deployment <name> --cascade=orphan` deletes the Deployment object while leaving the underlying Pods running without disruption.
- **Dangling Resources:** If an operator manually edits a Pod and deletes its `ownerReferences`, higher-level workload rollouts and autoscalers lose track of the Pod, causing silent replica drift and orphaned resource consumption."""
    },

    32: {
        "tech_disc": """A **ReplicaSet** maintains a stable, declared population of identical Pod replicas running at any given time. It acts as the direct supervisor of Pods, continuously reconciling actual replica count with `spec.replicas`.

### Set-Based Label Selectors vs. Legacy Selectors
- Unlike legacy ReplicationControllers which only supported simple equality matches (`env = prod`), ReplicaSets support rich **set-based selectors** using `matchExpressions`:
  - Operators: `In`, `NotIn`, `Exists`, `DoesNotExist`.
  - Enables targeting multiple deployment tiers, versions, or environments under complex filtering logic.
- **Pod Acquisition & Adoption:** The ReplicaSet controller does not only manage pods it created; it automatically *adopts* any unbound Pod in the namespace whose labels match its selector!

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
```""",
        "tech_persp": """ReplicaSets are rarely deployed directly in production; instead, they are managed via higher-level Deployments:
- **Label Selector Overlap Hazards:** If two different ReplicaSets define overlapping label selectors, they will enter a violent reconciliation loop, continuously creating and terminating each other's Pods in an infinite fight for target count.
- **CKA Deployment Rollback Internals:** Every Deployment revision creates a new underlying ReplicaSet. Rolling back a Deployment (`kubectl rollout undo`) simply scales the target historical ReplicaSet back up and the current ReplicaSet down to 0."""
    },

    33: {
        "tech_disc": """A **Deployment** provides declarative management, automated rolling updates, and instant rollback capabilities for Pods and ReplicaSets. It represents the standard workload primitive for stateless web and API applications.

### Deployment Strategies & Update Mechanics
- **`RollingUpdate` (Default):**
  - Progressively replaces old Pods with new Pods with zero application downtime.
  - `maxSurge`: Maximum number of Pods that can be scheduled *above* the declared replica count (e.g., `25%`).
  - `maxUnavailable`: Maximum number of Pods that can be unavailable during the update (e.g., `0` for zero-downtime updates).
- **`Recreate`:** Terminates all running Pods simultaneously before launching new versions (causes downtime, but prevents dual-version database schema collisions).

### Rollout Lifecycle & Revision History
- Tracks historical changes via `revisionHistoryLimit` (default 10).
- Commands:
  - `kubectl rollout status deployment/<name>`
  - `kubectl rollout history deployment/<name>`
  - `kubectl rollout undo deployment/<name> --to-revision=2`
  - `kubectl rollout pause / resume deployment/<name>`

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
```""",
        "tech_persp": """Deployments require proper readiness probes to safely execute rolling updates:
- **The Broken Image Trap:** If a new container image is pushed with a fatal startup bug and no `readinessProbe` is configured, Kubernetes considers the container "Ready" as soon as the process starts, immediately terminating all healthy old replicas and causing a complete outage!
- **`maxUnavailable: 0` Requirement:** For critical services, pairing `maxUnavailable: 0` with thorough readiness probes guarantees that an unhealthy rollout stalls automatically without killing a single active serving pod."""
    },

    34: {
        "tech_disc": """A **StatefulSet** is the workload controller designed specifically for stateful applications (databases, clustered storage, distributed message queues like Kafka, ZooKeeper, MongoDB, PostgreSQL) that require unique identities and persistent state.

### Core Architectural Guarantees
1. **Stable Network Identity:** Each Pod receives a predictable, persistent ordinal index starting from 0 (`web-0`, `web-1`, `web-2`).
2. **Headless Service DNS Integration:** Pairs with a Headless Service (`clusterIP: None`) to publish stable direct DNS records:
   `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
3. **Dedicated Persistent Storage per Replica:** Uses `volumeClaimTemplates` to automatically provision a separate, dedicated PVC and PV for every individual ordinal index (e.g., `data-web-0`, `data-web-1`).
4. **Ordered Deployment & Termination:** Scales up sequentially from `0` to `N-1`. Scales down in reverse order from `N-1` to `0`. (Configurable to parallel via `podManagementPolicy: Parallel`).

```yaml
# clustered-statefulset.yaml
# WHY THIS YAML: StatefulSet's ordered identity guarantees are configured here.
# 'serviceName: "db-cluster"': creates a Headless Service for stable DNS per Pod.
#   'db-0.db-cluster.<ns>.svc.cluster.local' persists across Pod restarts.
#   This stable DNS identity is essential for distributed peers (Cassandra, Kafka).
# 'podManagementPolicy: OrderedReady': Pods created 0, 1, 2 in sequence; each must be
#   Ready before next starts. Scale-down reverses order (2, 1, 0).
# 'volumeClaimTemplates': each Pod gets its OWN PVC that persists even if StatefulSet is deleted.
apiVersion: v1
kind: Service
metadata:
  name: database-headless
spec:
  clusterIP: None
  selector:
    app: stateful-db
  ports:
  - port: 5432
    name: db
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db-cluster
spec:
  serviceName: "database-headless"
  replicas: 3
  selector:
    matchLabels:
      app: stateful-db
  template:
    metadata:
      labels:
        app: stateful-db
    spec:
      containers:
      - name: postgres
        image: registry.k8s.io/pause:3.9
        volumeMounts:
        - name: data-store
          mountPath: /var/lib/data
  volumeClaimTemplates:
  - metadata:
      name: data-store
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```""",
        "tech_persp": """StatefulSets protect against split-brain scenarios:
- **Volume Retention on Scale-Down:** When a StatefulSet is scaled down (e.g., from 3 to 2), the associated PVC (`data-db-cluster-2`) is **not deleted**. This prevents catastrophic accidental data loss.
- **At-Most-One-Pod Guarantee:** In network partitions, Kubernetes will never create a replacement stateful pod until the previous pod is confirmed terminated. Deleting a partitioned stateful pod with `--force --grace-period=0` can cause dual writes and data corruption if the old node is still alive!"""
    },

    35: {
        "tech_disc": """A **DaemonSet** ensures that all (or a selected subset of) Nodes run exactly one copy of a Pod. As new nodes join the cluster, the DaemonSet controller automatically adds the Pod; as nodes are decommissioned, the Pods are garbage collected.

### Standard Production Use Cases
- **Cluster Storage Daemons:** Ceph, GlusterFS, Rook.
- **Log Collection Daemons:** Fluentd, Fluent Bit, Promtail, Vector.
- **Node Monitoring & Security:** Prometheus `node-exporter`, Datadog Agent, Falco eBPF security sensors.

### Scheduling & Node Taint Toleration
- Modern DaemonSets are scheduled by the standard `kube-scheduler` using default node affinity.
- DaemonSets typically include universal tolerations allowing them to run on control plane nodes or tainted storage nodes (`node-role.kubernetes.io/control-plane:NoSchedule`).

### Host Integration
Unlike standard application containers that remain strictly isolated within independent Linux namespaces, host monitoring and logging agents need direct access to the underlying machine's network stack and kernel diagnostics (`/proc`, `/sys`). DaemonSets achieve this privileged host visibility through explicit pod security settings:
- Often configured with `hostNetwork: true`, `hostPID: true`, and host filesystem bind-mounts (`/var/log`, `/proc`, `/sys`) to monitor low-level Linux kernel metrics.

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
      - operator: "Exists"
      containers:
      - name: exporter
        image: registry.k8s.io/pause:3.9
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
```""",
        "tech_persp": """DaemonSets require strict resource sizing:
- **Node Sizing Footprint:** Because DaemonSets run on every node, their resource requests multiply linearly across the entire cluster. 10 DaemonSets requesting 200m CPU each will consume 2 full CPU cores on every single node before any application workload is scheduled.
- **Rolling Update Strategy:** Configured via `updateStrategy.type: RollingUpdate` (with optional `maxUnavailable`) or `OnDelete` (updates only when the old pod is manually killed)."""
    },

    36: {
        "tech_disc": """A **Job** creates one or more Pods and tracks them to successful termination (exit code 0). Unlike Deployments and ReplicaSets which continuously restart finished containers to keep them running, a Job ensures that batch tasks execute to completion.

### Concurrency & Completion Controls
- **`completions`:** Total number of Pods that must successfully finish with exit status 0 for the Job to be marked complete.
- **`parallelism`:** Maximum number of Pods executing concurrently at any single point in time.
- **`backoffLimit`:** Maximum retry attempts before marking the Job permanently as `Failed` (default 6). Retries use exponential backoff (10s, 20s, 40s...).
- **`activeDeadlineSeconds`:** Hard ceiling timeout duration for the Job; terminates all running pods once exceeded.

### Linux Process Termination & Restart Policy
Batch computing requires knowing when a task has finished successfully versus crashed. The Job controller evaluates Linux process exit codes returned by the container runtime to determine job completion:
- Container specs inside Jobs only support `restartPolicy: OnFailure` (restarts container inside existing pod sandbox) or `Never` (kubelet fails pod and Job controller spawns a fresh pod).

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
  name: database-schema-migration
spec:
  completions: 3
  parallelism: 2
  backoffLimit: 4
  activeDeadlineSeconds: 300
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrator
        image: busybox:1.36
        command: ["sh", "-c", "echo 'Executing database migration step'; sleep 5; exit 0"]
```""",
        "tech_persp": """Batch processing requires lifecycle cleanup planning:
- **Completed Pod Garbage Collection:** Completed Job pods remain in the cluster in phase `Completed` so operators can inspect logs (`kubectl logs`). Use `ttlSecondsAfterFinished: 300` to automatically delete completed Job records and prevent etcd object accumulation.
- **Pod Cleanup on Failure:** If a Job fails and uses `restartPolicy: Never`, multiple failed Pod objects will clutter the namespace until the Job is deleted."""
    },

    37: {
        "tech_disc": """A **CronJob** runs Jobs on a recurring, time-based schedule using standard UNIX cron format (`minute hour day-of-month month day-of-week`).

### Concurrency Policies & Job Spawning
- **`concurrencyPolicy`:**
  - `Allow` (Default): Permits multiple Job instances to execute concurrently.
  - `Forbid`: Skips the new Job run if the previous Job instance is still actively running.
  - `Replace`: Cancels and terminates the currently running Job and spawns the new scheduled Job.
- **`startingDeadlineSeconds`:** Window of time in seconds that a Job can start if it missed its scheduled time (e.g., due to cluster downtime). If missed past the deadline, the run is skipped.
- **History Limits:** `successfulJobsHistoryLimit` (default 3) and `failedJobsHistoryLimit` (default 1) prune finished Job API records automatically.

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
  name: nightly-etcd-snapshot
  namespace: maintenance
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 120
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: busybox:1.36
            command: ["sh", "-c", "echo 'Running backup at:'; date; sleep 10"]
```""",
        "tech_persp": """CronJob time scheduling depends on control plane timezone configuration:
- **Timezone Awareness:** In Kubernetes 1.27+, CronJobs support explicit timezone specifications (`spec.timeZone: "America/New_York"`). By default, all CronJobs evaluate against the UTC system clock of `kube-controller-manager`.
- **`concurrencyPolicy: Forbid` Sizing:** Long-running cron tasks with short schedules (e.g., every 5 minutes) must use `concurrencyPolicy: Forbid` to prevent runaway compute resource exhaustion if an execution experiences transient delays."""
    },

    38: {
        "tech_disc": """A **ReplicationController** is the legacy v1 ancestor to `ReplicaSet`. It served the same core purpose of ensuring that a specified number of Pod replicas were running at all times.

### Key Architectural Differences from ReplicaSet
- **Equality-Based Selectors Only:** ReplicationControllers exclusively support simple equality-based label selectors:
  ```yaml
  selector:
    app: frontend
    tier: web
  ```
- Does **not** support set-based operators (`In`, `NotIn`, `Exists`) or `matchExpressions`.
- Retained in the core API (`apiVersion: v1`) for backward compatibility, but fully superseded in modern production by `Deployment` and `ReplicaSet`.

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
  name: legacy-frontend-rc
spec:
  replicas: 2
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
```""",
        "tech_persp": """CKA Exam & Migration Insight:
- Modern Kubernetes best practices strictly mandate using **Deployments** for all stateless workloads. Never author new ReplicationController manifests in modern environments.
- Migrating from ReplicationController to Deployment requires deleting the ReplicationController with `--cascade=orphan` and creating a Deployment matching the existing pod labels to adopt the running pods without downtime."""
    },

    39: {
        "tech_disc": """The **HorizontalPodAutoscaler (HPA)** automatically scales the number of Pod replicas in a Deployment, ReplicaSet, or StatefulSet up or down based on observed resource utilization or custom application metrics.

### Autoscaling Algorithm & Formula
$$\\text{desiredReplicas} = \\left\\lceil \\text{currentReplicas} \\times \\left( \\frac{\\text{currentMetricValue}}{\\text{targetMetricValue}} \\right) \\right\\rceil$$

### Metric Source Categories (`autoscaling/v2`)
1. **Resource Metrics:** CPU and Memory utilization queried from `metrics-server` (which reads container cgroup stats from Kubelet Summary API).
2. **Custom Metrics:** Application-specific metrics from within the cluster (e.g., HTTP request rate per second, active websocket connections) via Prometheus Adapter.
3. **External Metrics:** Cloud or third-party metrics outside the cluster (e.g., AWS SQS queue depth).

### Scaling Behavior & Stabilization Windows
- Modern HPA specs define `behavior` policies:
  - `scaleDown.stabilizationWindowSeconds`: Defaults to 300s (5 minutes) to prevent "flapping" (rapid oscillations between scale-up and scale-down).

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
  name: web-scaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-app
  minReplicas: 2
  maxReplicas: 10
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
        value: 50
        periodSeconds: 60
```""",
        "tech_persp": """HPA requires explicit resource requests on every target container:
- **The Missing Requests Pitfall:** If a container does not declare `resources.requests.cpu`, HPA cannot compute percentage utilization! The HPA status will show `unknown / 60%`, and autoscaling will fail to trigger.
- **Metrics Server Dependency:** HPA requires `metrics-server` running in `kube-system`. Verify with `kubectl top pods` and `kubectl top nodes` before enabling HPA."""
    },

    40: {
        "tech_disc": """The **VerticalPodAutoscaler (VPA)** automatically right-sizes container CPU and memory requests and limits based on historical resource consumption patterns, avoiding manual guesswork in capacity planning.

### Architecture & Components
1. **VPA Recommender:** Queries historical usage from metrics-server / Prometheus and computes recommendations (`lowerBound`, `target`, `uncappedTarget`, `upperBound`).
2. **VPA Updater:** In `Auto` mode, identifies pods running with outdated resource specs and evicts them to trigger replacement.
3. **VPA Admission Controller:** A Mutating Admission Webhook that intercepts pod creation requests and injects the updated resource requests into the PodSpec before it is persisted to etcd.

### Operating Modes
- **`Off`:** Computes recommendations without modifying pods (ideal for cost audits).
- **`Initial`:** Injects recommendations only at pod creation time; never evicts running pods.
- **`Auto`:** Actively evicts and recreates running pods to apply updated resource values.

```yaml
# vpa-auto-spec.yaml
# WHY THIS YAML: VPA's update mode determines how recommendations are applied.
# 'updateMode: Auto': VPA evicts and recreates Pods with updated resource requests.
#   In-place resize (no eviction) requires K8s 1.27+ InPlacePodVerticalScaling feature.
# 'containerPolicies.minAllowed.cpu: 100m / maxAllowed.cpu: "4"': VPA recommendations
#   are bounded -- never below 100m (starvation floor) or above 4 CPU (cost ceiling).
# VPA Recommender samples CPU/memory usage over history (default 8 days) and computes
#   p50 recommendations for requests and p95 for limits.
# WARNING: VPA and HPA targeting the same metric on the same Deployment WILL conflict.
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-right-sizer
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: core-api
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
```""",
        "tech_persp": """VPA and HPA must be coordinated carefully:
- **VPA + HPA Conflict Hazard:** Do NOT use VPA and HPA simultaneously on the same metric (e.g., both targeting CPU utilization). HPA will add pods to lower CPU usage, while VPA will downscale pod CPU requests, creating destructive feedback loops.
- **Disruption Planning:** In `Auto` mode, VPA evicts running pods to resize them. Always combine VPA with `PodDisruptionBudgets` and multi-replica Deployments to prevent downtime during vertical resizing."""
    },

    41: {
        "tech_disc": """A **PodDisruptionBudget (PDB)** limits the number of concurrent voluntary disruptions that an application's Pods can suffer during cluster maintenance operations (e.g., `kubectl drain`, automated node pool upgrades, cluster autoscaler scale-downs).

### Specification Constraints
- Configured using **one** of two mutually exclusive fields:
  - `minAvailable`: Minimum number or percentage of healthy Pods that must remain running (e.g., `2` or `80%`).
  - `maxUnavailable`: Maximum number or percentage of Pods that can be disrupted simultaneously (e.g., `1` or `20%`).
- Selects target Pods using `spec.selector.matchLabels`.

### Eviction API Interception Mechanics
- Voluntary disruptions do not call the core Pod Delete API directly; they call the **Eviction API** (`/api/v1/namespaces/<ns>/pods/<name>/eviction`).
- The API server checks active PDBs before accepting the eviction:
  - If evicting the pod would violate the PDB constraint, the API server rejects the request with **HTTP 429 (Too Many Requests)**.
  - `kubectl drain` stalls and retries until new healthy replicas are running on other nodes.

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
  name: api-ha-budget
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: customer-api
```""",
        "tech_persp": """PDBs safeguard high availability during automated platform maintenance:
- **Voluntary vs. Involuntary Disruptions:** PDBs protect ONLY against **voluntary** disruptions (`kubectl drain`, node scale-down). They CANNOT prevent **involuntary** disruptions (hardware crashes, kernel panics, OOMKilled events, network cuts).
- **Drain Deadlocks:** A PDB requiring `minAvailable: 100%` or `maxUnavailable: 0` will permanently block `kubectl drain`, preventing cluster upgrades until an administrator intervenes."""
    }
}
