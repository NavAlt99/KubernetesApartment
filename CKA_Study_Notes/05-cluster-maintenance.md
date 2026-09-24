# 05. Cluster Maintenance

## 📑 Table of Contents
- [1. Node Maintenance & OS Upgrades](#1-node-maintenance--os-upgrades)
  - [Node Failure & Pod Eviction Timeout](#node-failure--pod-eviction-timeout)
  - [Drain, Cordon, and Uncordon](#drain-cordon-and-uncordon)
- [2. Kubernetes Software Versions & Skew Policy](#2-kubernetes-software-versions--skew-policy)
  - [Version Anatomy](#version-anatomy)
  - [Component Version Skew Rules](#component-version-skew-rules)
  - [Support Lifecycle](#support-lifecycle)
- [3. Step-by-Step Kubeadm Cluster Upgrade Playbook](#3-step-by-step-kubeadm-cluster-upgrade-playbook)
  - [Phase 1: Upgrade the Control Plane Node](#phase-1-upgrade-the-control-plane-node)
  - [Phase 2: Upgrade Worker Nodes (One by One)](#phase-2-upgrade-worker-nodes-one-by-one)
- [4. Kubeadm Certificate Management & Renewal](#4-kubeadm-certificate-management--renewal)
  - [Check Expiration](#check-expiration)
  - [Renew Certificates](#renew-certificates)
  - [Post-Renewal Verification](#post-renewal-verification)
- [5. ETCD Backup and Snapshot Restore](#5-etcd-backup-and-snapshot-restore)
  - [Backup Strategies: Declarative vs. etcd Snapshot](#backup-strategies-declarative-vs-etcd-snapshot)
  - [Creating an ETCD Snapshot](#creating-an-etcd-snapshot)
  - [Restoring an ETCD Snapshot (Static Pod Architecture)](#restoring-an-etcd-snapshot-static-pod-architecture)
  - [TLS Authentication Flags for etcdctl](#tls-authentication-flags-for-etcdctl)

---

## 1. Node Maintenance & OS Upgrades

### Node Failure & Pod Eviction Timeout
When a node becomes unreachable or shuts down:
- **Pod Eviction Timeout (`default: 5m`):** Configured on `kube-controller-manager` via `--pod-eviction-timeout=5m0s`.
- If the node recovers within 5 minutes, pods resume without recreation.
- If down for > 5 minutes, the node is marked `NotReady`, and its pods are terminated and rescheduled on healthy nodes (if managed by a ReplicaSet/Deployment). Bare pods are not recreated.

![Node Failure Impact](images/image429.png)
![Pod Re-creation on Alternate Node](images/image298.png)

### Drain, Cordon, and Uncordon

To safely take a node offline for maintenance (kernel patching, hardware upgrade):

| Command | Action | Impact on Existing Pods | Impact on New Pods |
| :--- | :--- | :--- | :--- |
| `kubectl cordon <node>` | Marks node unschedulable | **No change** (keeps running) | Blocks new pods |
| `kubectl drain <node>` | Cordons + evicts pods | Evicts graceful termination | Blocks new pods |
| `kubectl uncordon <node>` | Marks node schedulable | No auto fallback of old pods | Allows new pods |

#### Drain Commands:
```bash
# 1. Drain node (safely evicts workloads to other nodes)
kubectl drain node01 --ignore-daemonsets

# 2. If node hosts pods with local emptyDir storage, force eviction:
kubectl drain node01 --ignore-daemonsets --delete-emptydir-data --force

# 3. Perform maintenance / reboot node...

# 4. Return node to scheduling pool:
kubectl uncordon node01
```

![Drain Node Workflow](images/image100.png)
![Uncordon Node](images/image36.png)

---

## 2. Kubernetes Software Versions & Skew Policy

### Version Anatomy
Kubernetes adheres to Semantic Versioning (`vMAJOR.MINOR.PATCH`, e.g., `v1.31.2`):
- **MAJOR (`1`):** Core API changes.
- **MINOR (`31`):** Feature additions, API enhancements (released ~3 times per year).
- **PATCH (`2`):** Bug fixes and security patches.

![Kubernetes Version Breakdown](images/image279.png)
![Release Lifecycle](images/image210.png)

### Component Version Skew Rules
`kube-apiserver` is the primary hub of the control plane. No component can be at a higher minor version than the API server:

![Component Version Skew](images/image117.png)
![Version Permissibility](images/image299.png)

- **`kube-apiserver`:** Version **X**
- **`kube-scheduler` & `kube-controller-manager`:** Permitted at **X** or **X - 1**
- **`kubelet` & `kube-proxy`:** Permitted at **X**, **X - 1**, or **X - 2**
- **`kubectl`:** Permitted at **X + 1**, **X**, or **X - 1**

### Support Lifecycle
- Kubernetes officially maintains the **three most recent minor versions** (e.g., 1.31, 1.30, 1.29).
- **Never skip minor versions during an upgrade** (e.g., to go from `1.29` to `1.31`, upgrade `1.29` ➔ `1.30` ➔ `1.31`).

---

## 3. Step-by-Step Kubeadm Cluster Upgrade Playbook

### Upgrade Strategy
1. Upgrade the primary Control Plane node.
2. Upgrade secondary Control Plane nodes (in HA clusters).
3. Upgrade Worker nodes sequentially (one-by-one) to maintain application availability.

![Upgrade Control Plane First](images/image6.png)
![Upgrade Node Steps](images/image11.png)

---

### Phase 1: Upgrade the Control Plane Node

1. **Drain the Control Plane node:**
   ```bash
   kubectl drain controlplane --ignore-daemonsets
   ```

2. **Upgrade the `kubeadm` binary:**
   ```bash
   sudo apt-mark unhold kubeadm
   sudo apt-get update && sudo apt-get install -y kubeadm=1.31.0-1.1
   sudo apt-mark hold kubeadm
   
   kubeadm version
   ```

3. **Plan and apply the upgrade:**
   ```bash
   # View upgrade plan and verify component compatibility:
   sudo kubeadm upgrade plan
   
   # Apply control plane upgrade (upgrades static pod manifests):
   sudo kubeadm upgrade apply v1.31.0 -y
   ```

4. **Upgrade `kubelet` and `kubectl` on Control Plane:**
   ```bash
   sudo apt-mark unhold kubelet kubectl
   sudo apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
   sudo apt-mark hold kubelet kubectl
   
   sudo systemctl daemon-reload
   sudo systemctl restart kubelet
   ```

5. **Uncordon the Control Plane node:**
   ```bash
   kubectl uncordon controlplane
   ```

---

### Phase 2: Upgrade Worker Nodes (One by One)

![Worker Node Upgrade](images/image258.png)
![Worker Node Complete](images/image104.png)
![Cluster Nodes Upgraded](images/image181.png)

1. **Drain the Worker node from the Control Plane:**
   ```bash
   kubectl drain node01 --ignore-daemonsets --delete-emptydir-data --force
   ```

2. **Log into the Worker node:**
   ```bash
   ssh node01
   ```

3. **Upgrade `kubeadm` on Worker:**
   ```bash
   sudo apt-mark unhold kubeadm
   sudo apt-get update && sudo apt-get install -y kubeadm=1.31.0-1.1
   sudo apt-mark hold kubeadm
   ```

4. **Upgrade local node configuration:**
   ```bash
   sudo kubeadm upgrade node
   ```

5. **Upgrade `kubelet` and `kubectl` on Worker:**
   ```bash
   sudo apt-mark unhold kubelet kubectl
   sudo apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
   sudo apt-mark hold kubelet kubectl
   
   sudo systemctl daemon-reload
   sudo systemctl restart kubelet
   ```

6. **Exit Worker and Uncordon from Control Plane:**
   ```bash
   exit
   kubectl uncordon node01
   ```

7. **Verify node status:**
   ```bash
   kubectl get nodes -o wide
   ```

---

## 4. Kubeadm Certificate Management & Renewal

Kubeadm-generated TLS certificates expire after **1 year** by default.

### Check Expiration
```bash
kubeadm certs check-expiration
```
*Displays expiration date, remaining days, and authority for apiserver, etcd, front-proxy, etc.*

### Renew Certificates
```bash
# Renew all certificates simultaneously:
sudo kubeadm certs renew all

# Or renew specific component:
sudo kubeadm certs renew apiserver
```

### Post-Renewal Verification
```bash
# Restart kubelet to reload static pod certificates:
sudo systemctl restart kubelet

# Refresh admin kubeconfig credentials for root user:
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

## 5. ETCD Backup and Snapshot Restore

### Backup Strategies: Declarative vs. etcd Snapshot
1. **Resource Manifest Backup (Declarative):**
   - Store all YAML configs in Git (Infrastructure as Code).
   - Alternatively, query the API server using CLI / tools like Velero:
     ```bash
     kubectl get all --all-namespaces -o yaml > cluster-backup.yaml
     ```
   ![Resource Backup](images/image33.png)
   ![GitOps Manifests](images/image160.png)
   ![Velero Tool](images/image401.png)

2. **Database Snapshot (State Store):**
   - Direct backup of `/var/lib/etcd` or online snapshot using `etcdctl`.
   ![etcd Data Directory](images/image232.png)

---

### Creating an ETCD Snapshot

![etcd Snapshot](images/image3.png)

> [!TIP]
> **Locating ETCD Certificates & Endpoints on the Control Plane:**
> If you don't know the exact certificate paths or listen URLs during the exam, inspect the static pod manifest or pod description:
> ```bash
> # Option 1: Inspect the manifest directly
> cat /etc/kubernetes/manifests/etcd.yaml | grep -E "cert|key|listen-client-urls"
> 
> # Option 2: Describe the running etcd pod
> kubectl describe pod etcd-controlplane -n kube-system
> ```
> Typical locations:
> - CA Cert: `--cacert=/etc/kubernetes/pki/etcd/ca.crt`
> - Server Cert: `--cert=/etc/kubernetes/pki/etcd/server.crt`
> - Server Key: `--key=/etc/kubernetes/pki/etcd/server.key`
> - Endpoints: `https://127.0.0.1:2379` (peer port: `2380`)

Always use `ETCDCTL_API=3` and supply TLS certificates:

```bash
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/snapshot-pre-boot.db
```

Verify snapshot health and size:
```bash
ETCDCTL_API=3 etcdctl snapshot status /opt/snapshot-pre-boot.db --write-out=table
```

---

### Restoring an ETCD Snapshot (Static Pod Architecture)

![Restore Architecture](images/image289.png)
![Restore Process](images/image244.png)
![Static Pod Reload](images/image355.png)

1. **Restore snapshot to a NEW host directory:**
   ```bash
   ETCDCTL_API=3 etcdctl snapshot restore /opt/snapshot-pre-boot.db \
     --data-dir=/var/lib/etcd-from-backup
   ```

2. **Update the Static Pod manifest (`/etc/kubernetes/manifests/etcd.yaml`):**
   - Update the `hostPath` for `etcd-data` volume from `/var/lib/etcd` to the new path `/var/lib/etcd-from-backup`:
     ```yaml
     volumes:
     - hostPath:
         path: /var/lib/etcd-from-backup
         type: DirectoryOrCreate
       name: etcd-data
     ```

3. **Verify Static Pod Recreation:**
   - Kubelet detects manifest edits automatically and recreates the etcd container.
   ```bash
   # Watch etcd container reload:
   sudo crictl ps | grep etcd
   
   # Verify cluster API responds:
   kubectl get pods -n kube-system
   ```

---

### TLS Authentication Flags for etcdctl

![TLS Flags](images/image253.png)
![etcd Config](images/image396.png)

```bash
export ETCDCTL_API=3
# Essential flags:
# --endpoints=https://127.0.0.1:2379   -> etcd listen address
# --cacert=/etc/kubernetes/pki/etcd/ca.crt
# --cert=/etc/kubernetes/pki/etcd/server.crt
# --key=/etc/kubernetes/pki/etcd/server.key
```
