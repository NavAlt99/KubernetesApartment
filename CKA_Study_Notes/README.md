# Certified Kubernetes Administrator (CKA) - Complete Study Notes

Converted from `Copy of Kodekloud CKA 2.docx` into organized Markdown modules with diagrams and formatted code/manifest blocks.

## 📚 Table of Contents

### [01. Core Concepts](./01-core-concepts.md)

- **File:** [`01-core-concepts.md`](./01-core-concepts.md)
- **Summary:** Kubernetes architecture, ETCD, API server, Controller Manager, Scheduler, Kubelet, Kube-Proxy, Pods, ReplicaSets, Deployments, Services, Namespaces, Imperative Commands, kubectl apply, and CustomResourceDefinitions (CRDs) & Operators.

### [02. Scheduling](./02-scheduling.md)

- **File:** [`02-scheduling.md`](./02-scheduling.md)
- **Summary:** Manual scheduling, Labels and Selectors, Taints and Tolerations, Node Affinity, Resource Requirements/Limits, DaemonSets, Static Pods, Multiple Schedulers, Topology Spread Constraints, PriorityClass & Pod Preemption, Pod Disruption Budgets (PDB), and LimitRanges.

### [03. Logging & Monitoring](./03-logging-and-monitoring.md)

- **File:** [`03-logging-and-monitoring.md`](./03-logging-and-monitoring.md)
- **Summary:** Metrics Server, cluster component monitoring (top node, top pod), advanced kubectl logs streaming/filtering, JSONPath queries and custom columns, sorting, event investigation, and systemd journal logs.

### [04. Application Lifecycle Management](./04-application-lifecycle-management.md)

- **File:** [`04-application-lifecycle-management.md`](./04-application-lifecycle-management.md)
- **Summary:** Rolling updates, rollbacks, commands and args (ENTRYPOINT/CMD), environment variables, ConfigMaps, Secrets, multi-container pods, init containers, self-healing, and Container Health Probes (Startup, Liveness, Readiness).

### [05. Cluster Maintenance](./05-cluster-maintenance.md)

- **File:** [`05-cluster-maintenance.md`](./05-cluster-maintenance.md)
- **Summary:** OS upgrades (drain, cordon, uncordon), Kubernetes version lifecycle, step-by-step kubeadm cluster upgrade playbook (control plane & worker nodes), kubeadm certificate expiration and renewal, and ETCD backup/restore methods.

### [06. Security](./06-security.md)

- **File:** [`06-security.md`](./06-security.md)
- **Summary:** Security primitives, TLS certificate generation/validation, Certificates API, KubeConfig, API groups, RBAC (Roles & ClusterRoles), modern Projected ServiceAccount Tokens (TokenRequest API), Image security, SecurityContexts, NetworkPolicies, Admission Controllers, and Pod Security Standards & Admission (PSA/PSS).

### [07. Networking](./07-networking.md)

- **File:** [`07-networking.md`](./07-networking.md)
- **Summary:** Linux networking prerequisites (routing, iptables, netns, DNS), CNI plugins (Weave, Flannel), Pod networking, Service networking (ClusterIP, NodePort), CoreDNS, modern Ingress v1 specification with TLS, Gateway API overview, kubectl port-forward debugging, and EndpointSlices & Headless Services.

### [08. Storage](./08-storage.md)

- **File:** [`08-storage.md`](./08-storage.md)
- **Summary:** Docker storage drivers, volumes, Container Storage Interface (CSI), Persistent Volumes (PV), Persistent Volume Claims (PVC), volume mounts, StorageClasses, live PVC volume expansion, and CSI VolumeSnapshots & VolumeSnapshotClasses.

### [09. Design and Install a Kubernetes Cluster](./09-cluster-design-and-installation.md)

- **File:** [`09-cluster-design-and-installation.md`](./09-cluster-design-and-installation.md)
- **Summary:** Cluster infrastructure planning, High Availability (HA) topology, stacked vs external ETCD, and automated deployment with kubeadm.

### [10. Troubleshooting](./10-troubleshooting.md)

- **File:** [`10-troubleshooting.md`](./10-troubleshooting.md)
- **Summary:** Application failure scenarios, service selector troubleshooting, control plane diagnosis (static pods), worker node failure triage (kubelet, containerd, swap, cgroups), network troubleshooting (CoreDNS, kube-proxy, CNI), and advanced interactive debugging with kubectl debug (ephemeral containers, pod copies, node chroot).


## 🖼 Diagrams & Media

All 430+ visual diagrams and lab screenshots extracted from the original docx are preserved in the [`images/`](./images/) directory and linked directly inside each module.
