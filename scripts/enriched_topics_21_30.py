# scripts/enriched_topics_21_30.py
"""
Enriched technical discussions and perspectives for Topics 21-30.
Incorporates deep CKA Study Notes, Linux OS/Kernel concepts, bulleted points,
and production-grade YAML manifests.
"""

ENRICHED_21_30 = {
    21: {
        "tech_disc": """A **PersistentVolumeClaim (PVC)** is a user's request for storage in a specific namespace. It functions analogously to how a Pod requests compute resources (CPU/RAM): while administrators or StorageClasses provision PersistentVolumes, developers create PVCs declaring required capacity and access modes.

### 1-to-1 Binding Mechanics
- **Matching Criteria:** The control plane storage controller attempts to bind a PVC to an available PV based on:
  1. Matching `storageClassName`.
  2. Matching or compatible `accessModes`.
  3. PV capacity $\\ge$ PVC requested storage.
- **Strict 1-to-1 Exclusivity:** Even if a PV has 100Gi and a PVC requests only 10Gi, once bound, that PV is completely consumed by that single claim. No other PVC can attach to the remainder.
- **PVC Phase Transitions:** `Pending` (no matching PV or waiting for consumer) $\\rightarrow$ `Bound` (successfully paired) $\\rightarrow$ `Lost` (bound PV was deleted).

### Workload Consumption
- Pods mount storage by referencing the PVC name under `spec.volumes[*].persistentVolumeClaim.claimName`.
- Linux mount paths (`mountPath`) are injected into the container's mount namespace (`mnt`) via Linux bind mounts.

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
```""",
        "tech_persp": """PVC lifecycle errors can halt stateful deployments:
- **Pending PVC Diagnosis:** Run `kubectl describe pvc <name>` to inspect events. Common root causes include no available PVs matching the criteria, StorageClass misconfiguration, or quota exhaustion.
- **In-Use Protection:** Kubernetes applies the `kubernetes.io/pvc-protection` finalizer. If an operator attempts to delete an active PVC currently mounted by a running Pod, the deletion is deferred until the Pod terminates, preventing sudden filesystem corruption."""
    },

    22: {
        "tech_disc": """A **StorageClass** provides dynamic storage provisioning for Kubernetes clusters, eliminating the administrative overhead of manually creating static PersistentVolumes. It acts as an abstraction template defining provisioner plugins, cloud storage parameters, and volume binding behaviors.

### Key Architectural Parameters
- **`provisioner`:** The CSI plugin driver responsible for communicating with cloud or storage APIs (e.g., `ebs.csi.aws.com`, `pd.csi.storage.gke.io`).
- **`volumeBindingMode`:**
  - `Immediate` (Default): The PV is provisioned dynamically as soon as the PVC is submitted. (Warning: risks provisioning storage in an Availability Zone where no compute capacity exists).
  - `WaitForFirstConsumer`: Delays volume creation and binding until a Pod using the claim is scheduled. Guarantees that the storage volume is provisioned in the exact same Availability Zone / topology domain as the scheduled worker node.
- **`allowVolumeExpansion`:** Enables online filesystem expansion without restarting workloads (`true`).
- **`reclaimPolicy`:** Sets whether dynamically provisioned volumes are `Delete` or `Retain`.

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
```""",
        "tech_persp": """Dynamic storage provisioning is mandatory for modern multi-zone cloud architectures:
- **AZ Placement Conflicts:** Using `volumeBindingMode: Immediate` with cloud block storage often results in `volume node affinity conflict` errors if the cloud disk is created in `us-east-1a` while the scheduler attempts to place the Pod in `us-east-1b`. Always use `WaitForFirstConsumer` in multi-zone clusters.
- **Default StorageClass:** Marking a class with annotation `storageclass.kubernetes.io/is-default-class: "true"` automatically assigns it to any PVC submitted without an explicit `storageClassName`."""
    },

    23: {
        "tech_disc": """A **Role** is a namespaced Role-Based Access Control (RBAC) resource that defines a discrete set of additive permissions within a single Kubernetes namespace. Permissions cannot deny access; access is denied by default unless explicitly granted by a rule.

### Anatomy of RBAC Policy Rules
- **`apiGroups`:** The core API group is denoted by `""`. Other groups include `"apps"`, `"batch"`, `"networking.k8s.io"`.
- **`resources`:** The target objects (`pods`, `services`, `deployments`, `configmaps`). Subresources are targeted using slashes (e.g., `pods/log`, `pods/exec`, `pods/status`).
- **`resourceNames`:** (Optional) Restricts access to specific named instances of a resource (e.g., only the ConfigMap named `app-config`).
- **`verbs`:** Allowed API operations (`get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`).

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
```""",
        "tech_persp": """RBAC Role definition is the cornerstone of multi-tenant namespace security:
- **Principle of Least Privilege:** Avoid granting wildcard (`"*"`) verbs or resources.
- **Privilege Escalation Risks:** Granting `create` or `patch` on `pods/exec` grants arbitrary command execution inside containers, effectively yielding the privileges of the container process. Similarly, access to `secrets` allows token theft."""
    },

    24: {
        "tech_disc": """A **RoleBinding** grants the permissions defined in a `Role` (or a `ClusterRole`) to a defined list of **Subjects** within a specific namespace.

### Subject Types & Scopes
- **`User`:** External human identities authenticated via X.509 certs or OIDC (e.g., `alice@company.com`).
- **`Group`:** Collections of users (e.g., `system:authenticated`, `dev-team`).
- **`ServiceAccount`:** Workload identities assigned to Pods within the cluster.

### ClusterRole Reusability via RoleBinding
- A RoleBinding can reference a **ClusterRole** as its `roleRef`. In this pattern, the broad permissions defined in the ClusterRole apply **only within the namespace of the RoleBinding**. This avoids duplicating common Role templates across hundreds of namespaces.
- **Immutability:** The `roleRef` field of a RoleBinding is immutable upon creation. To change the referenced Role, the RoleBinding must be deleted and recreated.

```yaml
# role-binding-spec.yaml
# WHY THIS YAML: A RoleBinding ACTIVATES a Role by connecting it to specific subjects.
# 'roleRef.kind: Role': references a namespace-scoped Role (not cluster-wide).
# 'subjects': the identities receiving the permissions.
#   'kind: User / name: alice': a human user identified by their kubeconfig credential.
#   'kind: ServiceAccount': a Pod's identity -- allows in-cluster processes to use this role.
# A RoleBinding cannot grant permissions beyond what is in the referenced Role.
# Changing subjects is the fastest way to grant/revoke access without modifying the Role.
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-pod-operator
  namespace: development
subjects:
- kind: ServiceAccount
  name: cicd-deployer
  namespace: development
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-operator
  apiGroup: rbac.authorization.k8s.io
```""",
        "tech_persp": """Auditing effective permissions is a mandatory CKA administrative skill:
- **`kubectl auth can-i` Testing:** Verify access directly from the CLI without switching credentials:
  ```bash
  kubectl auth can-i create pods --as=system:serviceaccount:development:cicd-deployer -n development
  ```
- **Namespace Boundary Leaks:** Accidental assignment of an administrative ClusterRole via a ClusterRoleBinding instead of a RoleBinding grants cluster-wide superuser access across all namespaces."""
    },

    25: {
        "tech_disc": """A **ClusterRole** is a cluster-scoped RBAC resource. Unlike namespaced Roles, ClusterRoles govern permissions across the entire cluster (all namespaces) or for non-namespaced cluster-level resources.

### Scope of ClusterRole Grants
1. **Cluster-Scoped Resources:** Resources that do not belong to any namespace (`nodes`, `persistentvolumes`, `namespaces`, `storageclasses`).
2. **Non-Resource URLs:** HTTP endpoints exposed by the API server (`/healthz`, `/metrics`, `/version`, `/api`).
3. **Aggregated ClusterRoles:** Combines multiple ClusterRoles into one using label selectors (`aggregationRule.clusterRoleSelectors`).
4. **Namespace Template:** Defines a standardized permission set reusable across namespaces via individual RoleBindings.

```yaml
# node-viewer-clusterrole.yaml
# WHY THIS YAML: A ClusterRole grants permissions to cluster-scoped resources.
# 'resources: ["nodes"]': Nodes have no namespace -- a regular Role CANNOT grant this.
#   Only ClusterRole can grant access to non-namespaced API objects.
# 'resources: ["nodes/metrics", "nodes/stats"]': subresources for kubelet metric endpoints.
# ClusterRoles can also be used in namespace-scoped RoleBindings to reuse
#   permission templates across namespaces without granting cluster-wide access.
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-node-observer
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/status"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["persistentvolumes"]
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
```""",
        "tech_persp": """ClusterRoles represent the highest administrative security tier:
- **Built-in Superuser Roles:** Kubernetes ships with built-in ClusterRoles: `cluster-admin` (complete superuser access), `admin`, `edit`, and `view`. Modifying built-in ClusterRoles is discouraged because cluster upgrades will reconcile and overwrite changes.
- **Node Restriction:** The `Node` authorizer and `NodeRestriction` admission plugin restrict kubelet identities from modifying objects outside their own node, mitigating worker node compromise."""
    },

    26: {
        "tech_disc": """A **ClusterRoleBinding** binds a `ClusterRole` to subjects across the **entire cluster** and across every single namespace.

### Global Authorization Boundary
- While a `RoleBinding` restricts permissions to its host namespace, a `ClusterRoleBinding` grants the referenced ClusterRole's permissions globally.
- Binding the `cluster-admin` ClusterRole to a subject grants unrestricted, multi-tenant administrative power, effectively bypassing all namespace isolation.
- Used standardly by platform daemons, CNI networking plugins, CSI storage drivers, and monitoring operators (e.g., Prometheus) that require cluster-wide metrics scraping.

```yaml
# sre-clusterrolebinding.yaml
# WHY THIS YAML: A ClusterRoleBinding grants cluster-wide permissions -- use with caution.
# 'roleRef.kind: ClusterRole': must reference a ClusterRole for cluster-wide binding.
# 'subjects.kind: Group': binds an entire OIDC/LDAP group, not just one user.
#   Group membership changes in the identity provider automatically update K8s access.
# ClusterRoleBindings don't expire -- treat cluster-admin bindings as critical security assets.
# Prefer namespace-scoped RoleBindings when cluster-wide access is not required.
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: sre-global-observers
subjects:
- kind: Group
  name: sre-engineering
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-node-observer
  apiGroup: rbac.authorization.k8s.io
```""",
        "tech_persp": """Misconfigured ClusterRoleBindings are a top vulnerability in Kubernetes clusters:
- **Audit & Review:** Platform engineers must routinely audit all active ClusterRoleBindings:
  ```bash
  kubectl get clusterrolebindings -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.roleRef.name}{"\t"}{.subjects[*].name}{"\n"}{end}'
  ```
- **Default ServiceAccount Hardening:** Never bind a ClusterRole to `system:serviceaccount:<namespace>:default`, as any unprivileged pod created in that namespace inherits cluster-level authority."""
    },

    27: {
        "tech_disc": """A **ServiceAccount** provides an authenticable identity for in-cluster processes running inside Pods to interact with the `kube-apiserver`. Unlike human users managed by external enterprise directories, ServiceAccounts are native API objects.

### Modern Token Architecture: Bound Projected ServiceAccount Tokens
- **Legacy Tokens (Pre-1.24):** Used static, non-expiring JWT tokens stored in indefinitely persisting Secret objects.
- **Bound Projected Tokens (Modern Standard):** Tokens are short-lived, time-bound, audience-restricted OpenID Connect (OIDC) JWTs issued directly by the API server's TokenRequest API.
- **Linux Volume Mount:** The kubelet mounts the projected token as an in-memory `tmpfs` volume inside every container at `/var/run/secrets/kubernetes.io/serviceaccount/`:
  - `token`: Short-lived cryptographic JWT.
  - `ca.crt`: Certificate Authority bundle for verifying API server identity.
  - `namespace`: The current namespace string.
- **Token Invalidation:** Tokens are cryptographically bound to the specific Pod instance; deleting the Pod immediately invalidates the token.

```yaml
# secure-serviceaccount-pod.yaml
# WHY THIS YAML: Shows secure ServiceAccount usage for in-cluster API access.
# 'serviceAccountName: metrics-reader': kubelet mounts a projected SA token at
#   /var/run/secrets/kubernetes.io/serviceaccount/token inside the container.
#   The app uses this bearer token to authenticate to kube-apiserver as this SA identity.
# 'automountServiceAccountToken: false': when set on the SA, no token is mounted --
#   best practice for Pods that don't need API access (prevents credential exposure).
# RBAC RoleBindings determine what the SA can DO with the token after authenticating.
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auditor-sa
  namespace: security
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: auditor-pod
  namespace: security
spec:
  serviceAccountName: auditor-sa
  automountServiceAccountToken: true
  containers:
  - name: auditor
    image: registry.k8s.io/pause:3.9
```""",
        "tech_persp": """Securing workload identity is essential for zero-trust Kubernetes architectures:
- **`automountServiceAccountToken: false`:** Workloads that do not need to call the Kubernetes API should always set `automountServiceAccountToken: false` on either the ServiceAccount or PodSpec, eliminating credentials that attackers could steal via container breakout.
- **Cloud Workload Identity:** Modern cloud architectures (AWS IRSA, GCP Workload Identity, Azure Workload ID) federate the ServiceAccount OIDC token directly with cloud IAM, eliminating static hardcoded cloud API keys."""
    },

    28: {
        "tech_disc": """The **Node Controller** is an internal control loop running inside `kube-controller-manager` responsible for managing the registration, health tracking, and eviction lifecycle of worker nodes.

### Health Tracking & Taint Enforcement Lifecycle
1. **Registration & CIDR Assignment:** Assigns an isolated PodCIDR subnet block (e.g., `10.244.1.0/24`) to newly joined nodes when `--allocate-node-cidrs=true`.
2. **Lease Monitoring:** Watches the `kube-node-lease` namespace. If a node fails to renew its lease within `--node-monitor-grace-period` (default 40s), the controller marks the Node status as `NotReady` or `Unknown`.
3. **Automatic Tainting:** Applies built-in condition taints:
   - `node.kubernetes.io/not-ready:NoSchedule`
   - `node.kubernetes.io/unreachable:NoExecute`
4. **Eviction Execution:** If a node remains unreachable past `--pod-eviction-timeout` (default 5m), the controller initiates pod evictions, triggering workload controllers to recreate pods on healthy nodes.

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
```""",
        "tech_persp": """The Node Controller handles cluster-wide partition survival:
- **`tolerationSeconds` Tuning:** Stateful workloads (databases) often reduce `tolerationSeconds` from 300s down to 30s to initiate faster failover upon node hardware crashes.
- **Zone Disruption / Eviction Rate Limiting:** To prevent mass eviction storms during large-scale network partitions, the Node Controller monitors the percentage of unhealthy nodes in each zone. If more than 55% of nodes are unhealthy, it throttles eviction rates down to `0.1` nodes/second."""
    },

    29: {
        "tech_disc": """The **Namespace Controller** manages the lifecycle, state reconciliation, and cascading deletion of `Namespace` resources in a cluster.

### Scoping & Lifecycle Transitions
- **Logical Administrative Scope:** Namespaces partition object names, RBAC boundaries, ResourceQuotas, and LimitRanges within a single physical cluster. (Note: Namespaces do **not** provide network isolation by default; NetworkPolicies must be applied).
- **Phases:**
  - `Active`: Operating normally; accepting new resources.
  - `Terminating`: Deletion initiated. The controller rejects all new resource creation requests and walks through every namespaced resource to execute graceful cleanup.
- **Finalizer Pipeline:** Namespaces contain the `kubernetes` finalizer. The controller recursively deletes all Pods, Services, PVCs, ConfigMaps, and custom resources before releasing the namespace record from etcd.

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
```""",
        "tech_persp": """Stuck namespace deletion is a notorious operational headache:
- **Terminating Namespace Diagnosis:** If a namespace is permanently stuck in `Terminating`, inspect remaining resources with finalizers:
  ```bash
  kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n <namespace>
  ```
- **Custom Resource Finalizer Deadlocks:** Often, an uninstalled Custom Resource Definition (CRD) leaves custom objects with dangling finalizers that block the namespace controller indefinitely."""
    },

    30: {
        "tech_disc": """A **ResourceQuota** enforces aggregate resource consumption limits within a namespace, preventing individual teams or runaway workloads from monopolizing cluster compute and storage capacity.

### Quota Dimension Categories
- **Compute Resources:** Enforces total CPU and Memory reservations across all pods in the namespace (`requests.cpu`, `limits.cpu`, `requests.memory`, `limits.memory`).
- **Storage Subsystems:** Enforces total capacity requests (`requests.storage`) and PVC counts, optionally qualified by StorageClass (e.g., `fast-nvme.storageclass/requests.storage: 500Gi`).
- **Object Counts:** Restricts total API instances (`pods`, `services`, `services.loadbalancers`, `configmaps`, `secrets`).

### Admission Enforcement
- Enforced synchronously by the **`ResourceQuota` Admission Plugin** on `kube-apiserver`.
- **Mandatory Request Requirement:** If a namespace defines a compute quota for CPU or memory, **every single container** created in that namespace must explicitly declare that resource request/limit, or creation is rejected with HTTP 403 Forbidden (unless a `LimitRange` automatically injects defaults).

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
  name: compute-storage-quota
  namespace: development
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
    services.loadbalancers: "1"
    requests.storage: 100Gi
---
apiVersion: v1
kind: LimitRange
metadata:
  name: default-compute-limits
  namespace: development
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
```""",
        "tech_persp": """ResourceQuotas are vital for multi-tenant cluster cost governance:
- **Quota Tracking Commands:** Administrators inspect current quota usage vs. hard limits using:
  ```bash
  kubectl get resourcequota -n <namespace>
  kubectl describe resourcequota <quota-name> -n <namespace>
  ```
- **Deployment Rollout Deadlocks:** During a rolling update, a Deployment temporarily runs old replicas plus new replicas (`maxSurge`). If the namespace quota has zero headroom remaining, new pods cannot be created, completely stalling the rollout."""
    }
}
