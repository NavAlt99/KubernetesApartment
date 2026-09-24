#!/usr/bin/env python3
"""
scripts/update_yaml_commentary.py

Adds inline explanatory comments to YAML blocks in all enriched_topics_*.py files,
explaining WHY each section/field is relevant to the Kubernetes component being discussed.
"""

PATCHES = {
    "scripts/enriched_topics_1_10.py": [
        (
            "# cluster-workload-foundation.yaml",
            "# cluster-workload-foundation.yaml\n"
            "# WHY THIS YAML: Demonstrates the cluster's declarative model in action.\n"
            "# 'replicas: 3' is the desired state the Controller Manager reconciles against.\n"
            "#   If a pod dies, it creates a replacement — no human intervention needed.\n"
            "# 'resources.requests' is what the Scheduler reads to decide which Node fits.\n"
            "# 'resources.limits' is enforced at runtime by kernel cgroups on the Worker Node.\n"
            "# The cluster unifies scheduling, execution, and healing into one declarative API."
        ),
        (
            "# node-affinity-spec.yaml",
            "# node-affinity-spec.yaml\n"
            "# WHY THIS YAML: Enforces the Control Plane / Worker Node separation boundary.\n"
            "# 'DoesNotExist' for 'node-role.kubernetes.io/control-plane' tells the Scheduler:\n"
            "#   never place this workload on a control plane node during the Filtering phase.\n"
            "# This is how you prevent application Pods from competing with etcd, kube-apiserver,\n"
            "#   or kube-scheduler for CPU/RAM on control plane nodes.\n"
            "# Worker Nodes are the execution layer — this affinity rule enforces that boundary."
        ),
        (
            "# /etc/kubernetes/manifests/kube-apiserver.yaml (Static Pod excerpt)",
            "# /etc/kubernetes/manifests/kube-apiserver.yaml -- Static Pod excerpt\n"
            "# WHY THIS YAML: kube-apiserver itself runs as a Static Pod — its own manifest.\n"
            "# '--secure-port=6443': the single front door; ALL kubectl, controller, and kubelet\n"
            "#   traffic hits this port. No component bypasses it.\n"
            "# '--etcd-servers': proves kube-apiserver is the ONLY component that talks to etcd.\n"
            "# '--authorization-mode=Node,RBAC': every request traverses this AuthZ chain.\n"
            "# '--enable-admission-plugins': defines what mutation/validation runs before etcd write."
        ),
        (
            "# etcd-backup-cronjob.yaml",
            "# etcd-backup-cronjob.yaml\n"
            "# WHY THIS YAML: etcd is the single source of truth for ALL cluster state.\n"
            "# This CronJob automates the critical disaster recovery operation: etcdctl snapshot save.\n"
            "# 'schedule: \"0 */4 * * *\"': every 4 hours — data written since the last snapshot\n"
            "#   is unrecoverable if etcd loses quorum and all members fail simultaneously.\n"
            "# '--endpoints=https://127.0.0.1:2379': etcd is only reachable locally (by design).\n"
            "# '--cacert/--cert/--key': etcd requires mTLS — the cluster CA chain in action."
        ),
        (
            "# advanced-pod-scheduling.yaml",
            "# advanced-pod-scheduling.yaml\n"
            "# WHY THIS YAML: Demonstrates both phases of kube-scheduler's pipeline.\n"
            "# FILTERING: 'tolerations' removes nodes that have the 'dedicated=high-compute:NoSchedule'\n"
            "#   taint — without matching, the Scheduler discards those nodes before scoring.\n"
            "# FILTERING + SCORING: 'requiredDuringScheduling' eliminates nodes outside allowed zones.\n"
            "# 'resources.requests': the Scheduler checks NodeResourcesFit using these values —\n"
            "#   nodes without 250m CPU or 256Mi free allocatable capacity are filtered out."
        ),
        (
            "# /etc/kubernetes/manifests/kube-controller-manager.yaml (Flags excerpt)",
            "# /etc/kubernetes/manifests/kube-controller-manager.yaml -- Flags excerpt\n"
            "# WHY THIS YAML: These flags configure the controller loops inside kube-controller-manager.\n"
            "# '--leader-elect=true': only ONE active instance in HA; others watch the Lease lock.\n"
            "# '--node-monitor-grace-period=40s': how long before a silent node is marked NotReady.\n"
            "# '--pod-eviction-timeout=5m0s': after NotReady, pods wait this long before rescheduling.\n"
            "# '--cluster-cidr=10.244.0.0/16': the Pod IP block; the controller assigns per-node CIDRs."
        ),
        (
            "# cloud-loadbalancer-service.yaml",
            "# cloud-loadbalancer-service.yaml\n"
            "# WHY THIS YAML: This Service spec triggers the cloud-controller-manager's Service Controller.\n"
            "# 'type: LoadBalancer': when the API server persists this, CCM's Service Controller\n"
            "#   calls the cloud provider API (AWS/GCP/Azure) to provision an actual load balancer.\n"
            "# 'annotations': cloud-specific parameters passed to the CCM for LB configuration.\n"
            "# 'aws-load-balancer-type: external' tells CCM to create an AWS NLB, not an ALB.\n"
            "# This proves 'type: LoadBalancer' is a Kubernetes intent — CCM translates it to infra."
        ),
        (
            "# /etc/kubernetes/manifests/node-diagnostics.yaml",
            "# /etc/kubernetes/manifests/node-diagnostics.yaml\n"
            "# WHY THIS YAML: Placed in the Static Pod directory — kubelet reads via inotify.\n"
            "# The kubelet starts this container WITHOUT consulting kube-apiserver, etcd, or scheduler.\n"
            "# 'hostNetwork: true': shares the node's network namespace — needed before CNI is ready.\n"
            "# 'hostPID: true': shares the node's PID namespace — needed for node-level diagnostics.\n"
            "# 'hostPath /var/log': mounts the node's actual log directory into the container.\n"
            "# This is the exact pattern kubeadm uses to bootstrap etcd and kube-apiserver."
        ),
        (
            "# pod-with-probes.yaml",
            "# pod-with-probes.yaml\n"
            "# WHY THIS YAML: These probes are the kubelet's health monitoring directives.\n"
            "# 'startupProbe': kubelet will NOT run livenessProbe until this succeeds.\n"
            "#   'failureThreshold: 30 x periodSeconds: 10' = up to 300s for slow startup.\n"
            "#   Without this, slow-starting apps are killed by liveness checks prematurely.\n"
            "# 'livenessProbe': failure causes kubelet to instruct the CRI to restart the container.\n"
            "# 'readinessProbe': failure removes the Pod from the Service's EndpointSlice.\n"
            "#   The kubelet -- not the API server -- executes these probes on the node locally."
        ),
        (
            "# service-network-spec.yaml",
            "# service-network-spec.yaml\n"
            "# WHY THIS YAML: This ClusterIP Service triggers kube-proxy's iptables/IPVS programming.\n"
            "# 'type: ClusterIP': creates a virtual IP that exists nowhere physically.\n"
            "#   It works ONLY because kube-proxy programs iptables DNAT rules on every node.\n"
            "# 'selector: app: backend-api': kube-proxy reads the matching EndpointSlice to know\n"
            "#   which Pod IPs to include in the DNAT rules. Rules update as Pods come and go.\n"
            "# 'port: 80 -> targetPort: 8080': iptables rewrites BOTH destination IP and port.\n"
            "# Without kube-proxy's rules, this ClusterIP would be completely unreachable."
        ),
    ],

    "scripts/enriched_topics_11_20.py": [
        (
            "# oci-security-pod.yaml",
            "# oci-security-pod.yaml\n"
            "# WHY THIS YAML: These security fields are translated by containerd into OCI runtime spec,\n"
            "#   which runc passes to Linux kernel syscalls when creating the container sandbox.\n"
            "# 'runAsNonRoot: true': containerd verifies UID != 0 before starting the container.\n"
            "# 'seccompProfile: RuntimeDefault': containerd loads a BPF filter blocking dangerous syscalls.\n"
            "# 'allowPrivilegeEscalation: false': sets the no_new_privs prctl flag via runc.\n"
            "# 'capabilities.drop: ALL': runc calls cap_set_proc() stripping all Linux capabilities."
        ),
        (
            "# native-sidecar-pod.yaml",
            "# native-sidecar-pod.yaml\n"
            "# WHY THIS YAML: Demonstrates the native sidecar pattern (Kubernetes 1.28+).\n"
            "# 'initContainers' with 'restartPolicy: Always': this is what makes it a native sidecar.\n"
            "#   It starts BEFORE application containers but does NOT exit -- stays running alongside.\n"
            "# 'shared-logs emptyDir volume': both containers mount the SAME Linux tmpfs directory.\n"
            "#   The sidecar reads logs written by web-app because they share the same volume mount\n"
            "#   -- enabled by the Pod's shared mount namespace (all containers share Pod volumes)."
        ),
        (
            "# init-container-dependency.yaml",
            "# init-container-dependency.yaml\n"
            "# WHY THIS YAML: Init containers enforce startup prerequisites before the main app starts.\n"
            "# The kubelet runs init containers IN ORDER, each must exit code 0 before the next starts.\n"
            "# Common pattern: init container runs 'until nc -z postgres 5432; do sleep 2; done'\n"
            "#   -- the main app container will not start until the DB port is confirmed open.\n"
            "# Init containers share Pod volumes (emptyDir, PVCs), allowing pre-seeding of config\n"
            "#   files, DB migrations, or secrets into shared storage before the app reads them."
        ),
        (
            "# calico-ippool-spec.yaml",
            "# calico-ippool-spec.yaml\n"
            "# WHY THIS YAML: This Calico IPPool defines the CIDR range for Pod IP allocation.\n"
            "# 'cidr: 192.168.0.0/16': every Pod gets an IP from this block via CNI IPAM.\n"
            "#   When kubelet calls the CNI ADD command for a new Pod, Calico allocates from here.\n"
            "# 'ipipMode: Always': cross-node Pod traffic is IP-in-IP encapsulated, enabling\n"
            "#   pod-to-pod routing across nodes without BGP routing support.\n"
            "# 'natOutgoing: true': enables SNAT so Pod traffic leaving the cluster uses the node IP."
        ),
        (
            "# coredns-configmap.yaml",
            "# coredns-configmap.yaml\n"
            "# WHY THIS YAML: This ConfigMap IS the CoreDNS Corefile -- its runtime configuration.\n"
            "# 'cluster.local': the cluster domain. Services resolve as:\n"
            "#   <service>.<namespace>.svc.cluster.local -> ClusterIP address.\n"
            "# 'kubernetes cluster.local': uses the Kubernetes API as the DNS backend,\n"
            "#   watching Service and EndpointSlice objects to answer queries in real time.\n"
            "# 'forward . /etc/resolv.conf': external domain queries forwarded to node DNS.\n"
            "# Every Pod's /etc/resolv.conf is auto-configured to use this CoreDNS ClusterIP."
        ),
        (
            "# nodeport-service-spec.yaml",
            "# nodeport-service-spec.yaml\n"
            "# WHY THIS YAML: This Service shows the ClusterIP + NodePort layered model.\n"
            "# 'type: NodePort' creates BOTH a ClusterIP (internal) AND a NodePort (external).\n"
            "# 'selector: app: web-frontend': EndpointSlice controller populates backends;\n"
            "#   kube-proxy reads EndpointSlices to program its iptables rules.\n"
            "# 'port: 80 -> targetPort: 8080': stable interface -> actual container port.\n"
            "# 'nodePort: 30080': kube-proxy opens this port on every node's iptables chain."
        ),
        (
            "# custom-manual-endpoints.yaml",
            "# custom-manual-endpoints.yaml\n"
            "# WHY THIS YAML: Manual Endpoints/EndpointSlices route a Service to non-Pod backends.\n"
            "# A Service WITHOUT a 'selector' tells the controller NOT to auto-manage backends.\n"
            "# The Endpoints object lists IP:port pairs that kube-proxy uses to program\n"
            "#   its iptables/IPVS rules, exactly as it would for Pod-backed endpoints.\n"
            "# This lets Kubernetes Services act as stable internal DNS names for external systems\n"
            "#   (legacy VMs, managed databases), enabling transparent migration to in-cluster Pods."
        ),
        (
            "# tls-ingress-spec.yaml",
            "# tls-ingress-spec.yaml\n"
            "# WHY THIS YAML: This Ingress resource is processed by the Ingress Controller,\n"
            "#   NOT by kube-apiserver or kube-proxy directly.\n"
            "# 'ingressClassName: nginx': selects which controller watches this object.\n"
            "#   Multiple controllers can coexist; className routes to the right one.\n"
            "# 'tls.secretName: tls-cert': the controller reads this Secret and configures\n"
            "#   its virtual host to terminate HTTPS -- Layer 7, impossible with raw kube-proxy.\n"
            "# 'rules.host / path': HTTP Host header and URL-path-based routing to backend Services."
        ),
        (
            "# strict-backend-network-policy.yaml",
            "# strict-backend-network-policy.yaml\n"
            "# WHY THIS YAML: Enforces namespace-level network segmentation via the CNI plugin.\n"
            "# 'podSelector: app: backend': once ANY NetworkPolicy selects this Pod,\n"
            "#   default becomes deny-all -- only explicitly allowed traffic flows.\n"
            "# 'policyTypes: [Ingress, Egress]': both directions are now controlled.\n"
            "# 'ingress.from.namespaceSelector: frontend': ONLY the frontend namespace may connect.\n"
            "# 'egress.ports.port: 5432': Pods may only make outbound connections to PostgreSQL.\n"
            "# WARNING: Must explicitly allow DNS (port 53) or DNS resolution breaks."
        ),
        (
            "# nfs-persistent-volume.yaml",
            "# nfs-persistent-volume.yaml\n"
            "# WHY THIS YAML: Demonstrates the administrator-provisioned PV lifecycle.\n"
            "# 'capacity.storage: 50Gi': the PV advertises its size -- PVCs requesting >50Gi won't bind.\n"
            "# 'accessModes: ReadWriteMany': NFS supports multiple nodes mounting simultaneously.\n"
            "#   Block storage (EBS) would be ReadWriteOnce -- one node at a time only.\n"
            "# 'persistentVolumeReclaimPolicy: Retain': when PVC is deleted, PV is NOT destroyed.\n"
            "#   Moves to 'Released' state; admin must manually reclaim before rebinding.\n"
            "# 'storageClassName: \"\"': empty string means only manual PVC binding (no dynamic provisioning)."
        ),
    ],

    "scripts/enriched_topics_21_30.py": [
        (
            "# pvc-workload-claim.yaml",
            "# pvc-workload-claim.yaml\n"
            "# WHY THIS YAML: Shows the full PVC consumption lifecycle in one manifest.\n"
            "# PVC 'accessModes: ReadWriteOnce': binds only to PVs supporting single-node mounting.\n"
            "# PVC 'resources.requests.storage: 20Gi': minimum capacity required for binding.\n"
            "# Pod 'persistentVolumeClaim.claimName: database-storage': Pod references PVC by name;\n"
            "#   kubelet instructs the CSI driver to mount the volume at mountPath.\n"
            "# The PVC remains bound even if the Pod is deleted -- data persists across Pod restarts."
        ),
        (
            "# dynamic-storage-class.yaml",
            "# dynamic-storage-class.yaml\n"
            "# WHY THIS YAML: This StorageClass drives the dynamic provisioning workflow.\n"
            "# 'provisioner: ebs.csi.aws.com': the CSI plugin receiving CreateVolume gRPC calls\n"
            "#   when a PVC referencing this class is created -- calls the AWS EBS API.\n"
            "# 'volumeBindingMode: WaitForFirstConsumer': provisioning DELAYED until a Pod is scheduled.\n"
            "#   Ensures the EBS volume is created in the same AZ as the node -- avoids AZ failures.\n"
            "# 'allowVolumeExpansion: true': operators can increase PVC size post-creation; no migration.\n"
            "# 'reclaimPolicy: Delete': PVC deletion automatically destroys the EBS volume."
        ),
        (
            "# namespaced-developer-role.yaml",
            "# namespaced-developer-role.yaml\n"
            "# WHY THIS YAML: A Role defines the permission boundary within a single Namespace.\n"
            "# 'namespace: development': Role ONLY applies to this namespace -- cannot grant cross-namespace access.\n"
            "# 'resources: [\"pods\", \"pods/log\"]': access to Pod objects AND their log subresource.\n"
            "#   Without 'pods/log', kubectl logs is denied even with pod get permissions.\n"
            "# 'verbs: [\"get\", \"list\", \"watch\"]': read-only access -- satisfies least-privilege.\n"
            "# This Role has ZERO effect until a RoleBinding attaches it to a subject."
        ),
        (
            "# role-binding-spec.yaml",
            "# role-binding-spec.yaml\n"
            "# WHY THIS YAML: A RoleBinding ACTIVATES a Role by connecting it to specific subjects.\n"
            "# 'roleRef.kind: Role': references a namespace-scoped Role (not cluster-wide).\n"
            "# 'subjects': the identities receiving the permissions.\n"
            "#   'kind: User / name: alice': a human user identified by their kubeconfig credential.\n"
            "#   'kind: ServiceAccount': a Pod's identity -- allows in-cluster processes to use this role.\n"
            "# A RoleBinding cannot grant permissions beyond what is in the referenced Role.\n"
            "# Changing subjects is the fastest way to grant/revoke access without modifying the Role."
        ),
        (
            "# node-viewer-clusterrole.yaml",
            "# node-viewer-clusterrole.yaml\n"
            "# WHY THIS YAML: A ClusterRole grants permissions to cluster-scoped resources.\n"
            "# 'resources: [\"nodes\"]': Nodes have no namespace -- a regular Role CANNOT grant this.\n"
            "#   Only ClusterRole can grant access to non-namespaced API objects.\n"
            "# 'resources: [\"nodes/metrics\", \"nodes/stats\"]': subresources for kubelet metric endpoints.\n"
            "# ClusterRoles can also be used in namespace-scoped RoleBindings to reuse\n"
            "#   permission templates across namespaces without granting cluster-wide access."
        ),
        (
            "# sre-clusterrolebinding.yaml",
            "# sre-clusterrolebinding.yaml\n"
            "# WHY THIS YAML: A ClusterRoleBinding grants cluster-wide permissions -- use with caution.\n"
            "# 'roleRef.kind: ClusterRole': must reference a ClusterRole for cluster-wide binding.\n"
            "# 'subjects.kind: Group': binds an entire OIDC/LDAP group, not just one user.\n"
            "#   Group membership changes in the identity provider automatically update K8s access.\n"
            "# ClusterRoleBindings don't expire -- treat cluster-admin bindings as critical security assets.\n"
            "# Prefer namespace-scoped RoleBindings when cluster-wide access is not required."
        ),
        (
            "# secure-serviceaccount-pod.yaml",
            "# secure-serviceaccount-pod.yaml\n"
            "# WHY THIS YAML: Shows secure ServiceAccount usage for in-cluster API access.\n"
            "# 'serviceAccountName: metrics-reader': kubelet mounts a projected SA token at\n"
            "#   /var/run/secrets/kubernetes.io/serviceaccount/token inside the container.\n"
            "#   The app uses this bearer token to authenticate to kube-apiserver as this SA identity.\n"
            "# 'automountServiceAccountToken: false': when set on the SA, no token is mounted --\n"
            "#   best practice for Pods that don't need API access (prevents credential exposure).\n"
            "# RBAC RoleBindings determine what the SA can DO with the token after authenticating."
        ),
        (
            "# toleration-node-failure.yaml",
            "# toleration-node-failure.yaml\n"
            "# WHY THIS YAML: This toleration governs the Node Controller's eviction interaction.\n"
            "# 'key: node.kubernetes.io/unreachable' and 'node.kubernetes.io/not-ready':\n"
            "#   these taints are automatically added by the Node Lifecycle Controller when a node\n"
            "#   fails its heartbeat check and is marked NotReady.\n"
            "# 'effect: NoExecute': triggers immediate eviction of Pods without this toleration.\n"
            "# 'tolerationSeconds: 300': this Pod tolerates the taint for 5 minutes before eviction.\n"
            "#   Longer windows prevent false-positive evictions during transient network blips."
        ),
        (
            "# labeled-namespace-spec.yaml",
            "# labeled-namespace-spec.yaml\n"
            "# WHY THIS YAML: A Namespace is the primary isolation boundary and RBAC scope.\n"
            "# 'labels.pod-security.kubernetes.io/enforce: restricted': activates Pod Security Admission\n"
            "#   for this namespace -- every Pod creation is validated against security standards.\n"
            "# Labels on Namespaces are used by NetworkPolicies ('namespaceSelector')\n"
            "#   to target specific namespaces for ingress/egress rules.\n"
            "# ResourceQuotas and LimitRanges are also Namespace-scoped, applying only within this boundary."
        ),
        (
            "# team-resource-quota.yaml",
            "# team-resource-quota.yaml\n"
            "# WHY THIS YAML: ResourceQuota enforces aggregate resource governance at Namespace level.\n"
            "# 'requests.cpu: \"8\"': SUM of all Pod resource requests in this namespace cannot exceed 8 CPU.\n"
            "#   If a new Pod would push total over the limit, API server's admission controller rejects it.\n"
            "# 'limits.cpu: \"16\"': prevents namespace from claiming unlimited burst capacity.\n"
            "# 'count/pods: \"50\"': caps the number of Pod objects, not just CPU/memory.\n"
            "# Once quota is enabled, EVERY Pod MUST declare 'resources.requests' or it is rejected.\n"
            "#   The quota system cannot account for undeclared resource consumption."
        ),
    ],

    "scripts/enriched_topics_31_41.py": [
        (
            "# pod-with-owner-reference.yaml",
            "# pod-with-owner-reference.yaml\n"
            "# WHY THIS YAML: The ownerReference field is the Garbage Collector's dependency graph.\n"
            "# 'ownerReferences.apiVersion/kind/name/uid': links this Pod to a specific ReplicaSet.\n"
            "#   The uid is unique per object instance -- not just per name -- preventing stale refs.\n"
            "# 'controller: true': marks this as the controlling owner (only one allowed per object).\n"
            "# 'blockOwnerDeletion: true': Pod must be deleted before the owning ReplicaSet finalizes.\n"
            "# When a Deployment is deleted, GC traces: Deployment -> ReplicaSet -> Pods, deleting each.\n"
            "# Without ownerReferences, orphaned Pods keep running indefinitely after parent deletion."
        ),
        (
            "# set-based-replicaset.yaml",
            "# set-based-replicaset.yaml\n"
            "# WHY THIS YAML: Shows the label selector matching that drives ReplicaSet reconciliation.\n"
            "# 'replicas: 3': the controller watches this number and creates/deletes Pods to match it.\n"
            "#   The moment a Pod terminates, the controller creates a replacement -- no human needed.\n"
            "# 'selector.matchExpressions': set-based selectors -- the improvement over ReplicationController.\n"
            "#   'In: [nginx, nginx-proxy]' matches Pods with either label value, not just exact equality.\n"
            "# 'template.metadata.labels': MUST match the selector or the API server rejects the spec.\n"
            "# Use Deployments, not raw ReplicaSets -- Deployments add versioning and rolling updates."
        ),
        (
            "# zero-downtime-deployment.yaml",
            "# zero-downtime-deployment.yaml\n"
            "# WHY THIS YAML: Governs the rolling update strategy enabling zero-downtime releases.\n"
            "# 'strategy.type: RollingUpdate': scales up new ReplicaSet while scaling down old one.\n"
            "# 'maxSurge: 1': allows 1 extra Pod above replicas count during rollout.\n"
            "#   New ReplicaSet scales to 4 before old ReplicaSet starts shrinking.\n"
            "# 'maxUnavailable: 0': zero Pods may be below desired count during rollout.\n"
            "#   Guarantees full capacity throughout update -- at the cost of extra resources.\n"
            "# 'readinessProbe': each new Pod must pass readiness before an old Pod is terminated."
        ),
        (
            "# clustered-statefulset.yaml",
            "# clustered-statefulset.yaml\n"
            "# WHY THIS YAML: StatefulSet's ordered identity guarantees are configured here.\n"
            "# 'serviceName: \"db-cluster\"': creates a Headless Service for stable DNS per Pod.\n"
            "#   'db-0.db-cluster.<ns>.svc.cluster.local' persists across Pod restarts.\n"
            "#   This stable DNS identity is essential for distributed peers (Cassandra, Kafka).\n"
            "# 'podManagementPolicy: OrderedReady': Pods created 0, 1, 2 in sequence; each must be\n"
            "#   Ready before next starts. Scale-down reverses order (2, 1, 0).\n"
            "# 'volumeClaimTemplates': each Pod gets its OWN PVC that persists even if StatefulSet is deleted."
        ),
        (
            "# node-exporter-daemonset.yaml",
            "# node-exporter-daemonset.yaml\n"
            "# WHY THIS YAML: DaemonSet guarantees one Pod per node -- node-exporter needs this.\n"
            "# 'tolerations: node-role.kubernetes.io/control-plane: NoSchedule': without this,\n"
            "#   DaemonSet skips control plane nodes. This toleration ensures ALL nodes are covered.\n"
            "# 'hostPID: true' and 'hostNetwork: true': required to read host-level metrics\n"
            "#   from /proc and /sys -- these are node-level capabilities normal apps avoid.\n"
            "# 'resources.requests': DaemonSet Pods consume resources on EVERY node.\n"
            "#   500m CPU on 100 nodes = 50 CPUs cluster-wide. Size very carefully.\n"
            "# 'updateStrategy.type: RollingUpdate': updates node by node, preserving metric coverage."
        ),
        (
            "# batch-processing-job.yaml",
            "# batch-processing-job.yaml\n"
            "# WHY THIS YAML: Job's completion tracking and retry semantics are configured here.\n"
            "# 'completions: 4': Job must run 4 successful Pod completions to be considered Done.\n"
            "#   Useful for parallelizing data processing across 4 independent dataset chunks.\n"
            "# 'parallelism: 2': at most 2 Pods run simultaneously -- controls resource usage.\n"
            "# 'backoffLimit: 3': after 3 failed Pod attempts, Job is marked Failed, no more Pods.\n"
            "# 'restartPolicy: Never': failed containers get a NEW Pod, not an in-place restart.\n"
            "# 'ttlSecondsAfterFinished: 600': auto-deletes Job and Pods 10 minutes after completion."
        ),
        (
            "# nightly-backup-cronjob.yaml",
            "# nightly-backup-cronjob.yaml\n"
            "# WHY THIS YAML: CronJob's schedule and concurrency controls are configured here.\n"
            "# 'schedule: \"0 2 * * *\"': runs at 2:00 AM UTC daily. The CronJob controller\n"
            "#   compares this against cluster time and creates a Job object at each trigger.\n"
            "# 'concurrencyPolicy: Forbid': if 2am Job is still running at 3am, 3am trigger is SKIPPED.\n"
            "#   Prevents overlapping backup jobs from corrupting the same backup target.\n"
            "# 'startingDeadlineSeconds: 300': if cluster was down at 2am, only schedules within\n"
            "#   5 minutes of the missed trigger -- older missed runs are discarded.\n"
            "# 'successfulJobsHistoryLimit: 3': limits retained completed Job objects for history inspection."
        ),
        (
            "# legacy-replication-controller.yaml",
            "# legacy-replication-controller.yaml\n"
            "# WHY THIS YAML: Historical reference only -- do NOT use in new deployments.\n"
            "# 'selector: app: legacy-app': only supports equality-based selectors (key=value).\n"
            "#   Cannot express 'app in [v1, v2]' or 'env != prod' -- ReplicaSet can.\n"
            "# NO 'strategy' field: ReplicationController has no rolling update support.\n"
            "#   Updates require manual Pod deletion or blue/green swap -- Deployment automates this.\n"
            "# Migration: delete RC, create Deployment with same selector -- it adopts existing Pods."
        ),
        (
            "# hpa-v2-production.yaml",
            "# hpa-v2-production.yaml\n"
            "# WHY THIS YAML: HPA v2 spec shows the metrics and scaling behavior configuration.\n"
            "# 'scaleTargetRef': HPA controller watches this Deployment and adjusts 'spec.replicas'.\n"
            "# 'metrics.type: Resource / averageUtilization: 60': scales when avg CPU exceeds 60%.\n"
            "#   Formula: desiredReplicas = ceil(currentReplicas x currentCPU / 60).\n"
            "# 'minReplicas: 2 / maxReplicas: 20': HPA never goes below 2 (availability) or above 20 (cost).\n"
            "# 'stabilizationWindowSeconds: 300': prevents scale-down for 5 min after a spike (anti-flapping).\n"
            "# REQUIRES 'resources.requests.cpu' on every Pod -- without it, utilization is undefined."
        ),
        (
            "# vpa-auto-spec.yaml",
            "# vpa-auto-spec.yaml\n"
            "# WHY THIS YAML: VPA's update mode determines how recommendations are applied.\n"
            "# 'updateMode: Auto': VPA evicts and recreates Pods with updated resource requests.\n"
            "#   In-place resize (no eviction) requires K8s 1.27+ InPlacePodVerticalScaling feature.\n"
            "# 'containerPolicies.minAllowed.cpu: 100m / maxAllowed.cpu: \"4\"': VPA recommendations\n"
            "#   are bounded -- never below 100m (starvation floor) or above 4 CPU (cost ceiling).\n"
            "# VPA Recommender samples CPU/memory usage over history (default 8 days) and computes\n"
            "#   p50 recommendations for requests and p95 for limits.\n"
            "# WARNING: VPA and HPA targeting the same metric on the same Deployment WILL conflict."
        ),
        (
            "# pdb-high-availability.yaml",
            "# pdb-high-availability.yaml\n"
            "# WHY THIS YAML: PDB protects workload availability during planned (voluntary) disruptions.\n"
            "# 'selector.matchLabels: app: critical-api': PDB applies to all Pods with this label.\n"
            "# 'minAvailable: 2': the Eviction API (used by 'kubectl drain') REFUSES to evict\n"
            "#   a Pod if doing so would drop available Pod count below 2. Drain pauses and waits.\n"
            "# PDB ONLY protects against voluntary disruptions: drain, rolling updates, cluster upgrades.\n"
            "#   A node CRASH bypasses PDB -- it is not a voluntary disruption.\n"
            "# Critical rule: 'minAvailable' must be less than total replicas.\n"
            "#   minAvailable: 3 with replicas: 3 = drain blocks forever -- never undrained."
        ),
    ],
}


def patch_file(filepath, patch_list):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    changes = 0
    for old_comment, new_comment in patch_list:
        if old_comment in content:
            content = content.replace(old_comment, new_comment, 1)
            changes += 1
        else:
            print(f"  WARNING: Could not find pattern in {filepath}:")
            print(f"    '{old_comment[:70]}'")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Patched {changes}/{len(patch_list)} YAML comment blocks in {filepath}")


for filepath, patches in PATCHES.items():
    patch_file(filepath, patches)

print("\nDone! All YAML blocks have been updated with relevance explanations.")
