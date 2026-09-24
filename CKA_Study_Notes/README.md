# Certified Kubernetes Administrator (CKA) — Complete Study Guide & Notes

A comprehensive, high-yield, exam-oriented study companion for the **Certified Kubernetes Administrator (CKA)** certification. Reorganized into structured modules with visual architecture diagrams, production manifests, and troubleshooting checklists.

---

## 📑 Master Index & Curriculum

| # | Module | Exam Domain & Focus | Key Concepts & Commands | Quick Link |
| :--- | :--- | :--- | :--- | :---: |
| **01** | **[Core Concepts](./01-core-concepts.md)** | Cluster Architecture & Workloads (25%) | Control plane (`etcd`, `apiserver`, `scheduler`, `controller-manager`), Worker nodes (`kubelet`, `kube-proxy`), Pods, ReplicaSets, Deployments, Services, Namespaces, Imperative commands, CRDs & Operators | [Read ➔](./01-core-concepts.md) |
| **02** | **[Scheduling](./02-scheduling.md)** | Workload Scheduling (15%) | Manual scheduling, Labels/Selectors, Taints & Tolerations, Node Affinity, Resource Requests & Limits, DaemonSets, Static Pods, Custom Schedulers, PriorityClasses, Pod Disruption Budgets (PDB) | [Read ➔](./02-scheduling.md) |
| **03** | **[Logging & Monitoring](./03-logging-and-monitoring.md)** | Cluster Observability & Triaging | Metrics Server, `cAdvisor`, `kubectl top` (node/pod), Multi-container logs, JSONPath queries, custom-columns, sorting, cluster events, `journalctl` daemon logs | [Read ➔](./03-logging-and-monitoring.md) |
| **04** | **[Application Lifecycle](./04-application-lifecycle-management.md)** | Workloads & Configuration (20%) | Rolling updates, rollbacks, commands & args (`ENTRYPOINT`/`CMD`), ConfigMaps, Secrets, multi-container pods, Native Sidecars, Init Containers, Startup/Liveness/Readiness probes | [Read ➔](./04-application-lifecycle-management.md) |
| **05** | **[Cluster Maintenance](./05-cluster-maintenance.md)** | Cluster Operations (10%) | OS upgrades (`drain`, `cordon`, `uncordon`), Version skew policy, Step-by-step `kubeadm` upgrade playbook (control plane & workers), Kubeadm certificate renewal, `etcd` snapshot backup & restore | [Read ➔](./05-cluster-maintenance.md) |
| **06** | **[Security](./06-security.md)** | Cluster Security (25%) | Security primitives, TLS bootstrapping, Certificates API (`CSR`), KubeConfig management, RBAC (Roles & ClusterRoles), Projected ServiceAccount Tokens, SecurityContexts, NetworkPolicies, PSA/PSS | [Read ➔](./06-security.md) |
| **07** | **[Networking](./07-networking.md)** | Services & Networking (20%) | Linux networking (netns, iptables, routing), CNI plugins, ClusterIP & NodePort service routing, CoreDNS resolution, Modern Ingress v1 (TLS, path types), Gateway API, `kubectl port-forward`, EndpointSlices | [Read ➔](./07-networking.md) |
| **08** | **[Storage](./08-storage.md)** | Persistent Storage (10%) | Docker storage drivers, Container Storage Interface (CSI), PersistentVolumes (PV), PersistentVolumeClaims (PVC), StorageClasses, Dynamic provisioning, PVC expansion, VolumeSnapshots | [Read ➔](./08-storage.md) |
| **09** | **[Cluster Design & Install](./09-cluster-design-and-installation.md)** | Installation & HA Architecture | Multi-master HA topologies, Stacked vs External ETCD, Load balancers, Automated cluster deployment via `kubeadm` | [Read ➔](./09-cluster-design-and-installation.md) |
| **10** | **[Troubleshooting](./10-troubleshooting.md)** | Troubleshooting & Diagnostics (30%) | Multi-tier app triage, Control plane failure diagnosis (Static Pods, API server, etcd), Worker node triage (`kubelet`, `containerd`, swap, cgroups), CoreDNS/CNI issues, `kubectl debug` | [Read ➔](./10-troubleshooting.md) |

---

## 💡 How to Use These Notes Efficiently

- **Clickable Anchor Navigation:** Every module begins with a `## 📑 Table of Contents` linking directly to internal topics, manifests, and exam checklists.
- **Exam Tips & Checklists:** Focus on syntax-highlighted `bash` and `yaml` blocks designed for rapid copy-paste and memorization.
- **Embedded Architecture Diagrams:** 430+ diagrams from the original course material are placed contextually in [`images/`](./images/) to clarify complex control plane and networking flows.
- **Command References:** Streamlined CLI commands with flags frequently tested on the CKA exam (`-o jsonpath`, `--dry-run=client -o yaml`, `--sort-by`, `--field-selector`).

---

## 🖼 Diagrams & Media Repository

All visual diagrams, topology maps, and lab verification screenshots are preserved in the [`images/`](./images/) directory and cross-referenced across the study notes.
