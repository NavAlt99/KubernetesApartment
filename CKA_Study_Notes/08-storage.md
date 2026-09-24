# 08. Kubernetes Storage

A high-yield, exam-focused study guide covering container storage fundamentals, Kubernetes Volumes, PersistentVolumes (PV), PersistentVolumeClaims (PVC), StorageClasses, Volume Expansion, and CSI Volume Snapshots for the Certified Kubernetes Administrator (CKA) exam.

---

## 📑 Table of Contents

- [1. Docker Storage Fundamentals](#1-docker-storage-fundamentals)
  - [1.1 Docker Host Storage Architecture](#11-docker-host-storage-architecture)
  - [1.2 Layered Architecture & Build Cache](#12-layered-architecture--build-cache)
  - [1.3 Image Layers vs Container Layer (Copy-on-Write)](#13-image-layers-vs-container-layer-copy-on-write)
  - [1.4 Data Persistence: Volume Mounts vs Bind Mounts](#14-data-persistence-volume-mounts-vs-bind-mounts)
  - [1.5 Docker Storage Drivers](#15-docker-storage-drivers)
  - [1.6 Docker Volume Driver Plugins](#16-docker-volume-driver-plugins)
- [2. Container Storage Interface (CSI)](#2-container-storage-interface-csi)
  - [2.1 Evolution: CRI, CNI, and CSI](#21-evolution-cri-cni-and-csi)
  - [2.2 CSI Architecture & RPC Specification](#22-csi-architecture--rpc-specification)
- [3. Kubernetes Volumes](#3-kubernetes-volumes)
  - [3.1 Ephemeral Pod Lifecycle & Volume Need](#31-ephemeral-pod-lifecycle--volume-need)
  - [3.2 Volume Definition & Mount Syntax](#32-volume-definition--mount-syntax)
  - [3.3 Volume Storage Types & `hostPath` Limitations](#33-volume-storage-types--hostpath-limitations)
- [4. Persistent Volumes (PV)](#4-persistent-volumes-pv)
  - [4.1 Architecture & Administrator Workflow](#41-architecture--administrator-workflow)
  - [4.2 Access Modes](#42-access-modes)
  - [4.3 PersistentVolume Manifest & Management](#43-persistentvolume-manifest--management)
- [5. Persistent Volume Claims (PVC)](#5-persistent-volume-claims-pvc)
  - [5.1 Architecture & Binding Mechanism](#51-architecture--binding-mechanism)
  - [5.2 1-to-1 Binding Principle & Capacity Matching](#52-1-to-1-binding-principle--capacity-matching)
  - [5.3 PVC Manifest & Binding Lifecycle](#53-pvc-manifest--binding-lifecycle)
  - [5.4 PersistentVolume Reclaim Policies](#54-persistentvolume-reclaim-policies)
  - [5.5 Using PVCs in Pods & Deployments](#55-using-pvcs-in-pods--deployments)
- [6. Hands-On CKA Scenarios & Troubleshooting](#6-hands-on-cka-scenarios--troubleshooting)
  - [6.1 Scenario 1: Inspecting & Persisting Container Logs with `hostPath`](#61-scenario-1-inspecting--persisting-container-logs-with-hostpath)
  - [6.2 Scenario 2: Creating a PersistentVolume (`pv-log`)](#62-scenario-2-creating-a-persistentvolume-pv-log)
  - [6.3 Scenario 3: Troubleshooting PVC Binding Failures (`claim-log-1`)](#63-scenario-3-troubleshooting-pvc-binding-failures-claim-log-1)
  - [6.4 Scenario 4: Mounting PVC into Application Pod](#64-scenario-4-mounting-pvc-into-application-pod)
- [7. StorageClasses & Dynamic Provisioning](#7-storageclasses--dynamic-provisioning)
  - [7.1 Static vs Dynamic Provisioning](#71-static-vs-dynamic-provisioning)
  - [7.2 StorageClass Architecture & Provisioners](#72-storageclass-architecture--provisioners)
  - [7.3 Volume Binding Modes: `Immediate` vs `WaitForFirstConsumer`](#73-volume-binding-modes-immediate-vs-waitforfirstconsumer)
  - [7.4 CKA Troubleshooting: Delayed Binding with Local Storage](#74-cka-troubleshooting-delayed-binding-with-local-storage)
- [8. PVC Volume Expansion (Resizing)](#8-pvc-volume-expansion-resizing)
  - [8.1 Enabling Volume Expansion in StorageClass](#81-enabling-volume-expansion-in-storageclass)
  - [8.2 Expanding an Existing PVC & Filesystem Status](#82-expanding-an-existing-pvc--filesystem-status)
- [9. CSI Volume Snapshots & VolumeSnapshotClass](#9-csi-volume-snapshots--volumesnapshotclass)
  - [9.1 VolumeSnapshotClass](#91-volumesnapshotclass)
  - [9.2 Creating a VolumeSnapshot from a PVC](#92-creating-a-volumesnapshot-from-a-pvc)
  - [9.3 Restoring a PVC from a VolumeSnapshot](#93-restoring-a-pvc-from-a-volumesnapshot)
- [10. CKA Exam Quick Reference & Cheat Sheet](#10-cka-exam-quick-reference--cheat-sheet)

---

## 1. Docker Storage Fundamentals

Understanding Docker's native storage mechanism is the foundation for mastering Kubernetes storage abstractions.

### 1.1 Docker Host Storage Architecture

When Docker is installed on a host, it organizes all runtime data under `/var/lib/docker`:

```text
/var/lib/docker/
├── aufs/ (or overlay2/)   # Storage driver specific container layers
├── containers/             # Metadata and configs for active/stopped containers
├── image/                  # Image metadata and layer database
└── volumes/                # Managed persistent Docker volumes
```

![Diagram](images/image351.png)

- **`image/`**: Stores read-only layers representing container images.
- **`containers/`**: Stores container configurations and execution metadata.
- **`volumes/`**: Default location where Docker creates and manages persistent volumes.

---

### 1.2 Layered Architecture & Build Cache

Docker images are composed of immutable, read-only layers stacked on top of each other. Each instruction in a `Dockerfile` generates a distinct layer containing only the diff from the previous layer.

![Diagram](images/image287.png)

![Diagram](images/image280.png)

#### Build Cache & Layer Reusability
When multiple images share identical base instructions (e.g., base OS, package updates, dependencies), Docker pulls or reuses existing cached layers rather than rebuilding them. Only layers after a modified instruction are rebuilt.

![Diagram](images/image17.png)

---

### 1.3 Image Layers vs Container Layer (Copy-on-Write)

Arranging image layers bottom-up:

![Diagram](images/image397.png)

1. **Image Layers (Read-Only)**: Generated during `docker build`. Once built, these layers are completely immutable and shared across all container instances running that image.
2. **Container Layer (Read-Write)**: Created when `docker run` starts a container. All runtime changes (temporary files, log files, modified configs) reside exclusively in this writable layer.

![Diagram](images/image172.png)

#### Copy-on-Write (CoW) Mechanism
- Files baked into the base image remain unaltered in their read-only layers.
- If a running container modifies an existing image file, Docker copies that file from the read-only layer up into the read-write container layer, where modifications are saved.
- **Lifecycle Limitation**: When the container is destroyed, its writable container layer and all uncommitted modifications are permanently deleted.

---

### 1.4 Data Persistence: Volume Mounts vs Bind Mounts

To retain data beyond container deletion, Docker supports two primary mount mechanisms:

| Feature | Volume Mount | Bind Mount |
| :--- | :--- | :--- |
| **Source Location** | Managed inside `/var/lib/docker/volumes/` | Any arbitrary path on the host (`/data`, etc.) |
| **Creation** | Docker automatically creates the volume directory | Path must already exist or Docker creates it as root |
| **Management** | Managed via Docker CLI (`docker volume ...`) | Managed directly by host OS file system tools |
| **Portability** | High; decoupled from host filesystem structure | Low; tightly coupled to specific host paths |

![Diagram](images/image314.png)

#### Volume Mount Example
```bash
# 1. Create a managed volume
docker volume create data_volume

# 2. Mount into container (-v syntax)
docker run -d -v data_volume:/var/lib/mysql mysql

# Auto-creation: If data_volume2 does not exist, Docker creates it automatically
docker run -d -v data_volume2:/var/lib/mysql mysql
```

#### Bind Mount Example
```bash
# Old -v syntax
docker run -d -v /data/mysql:/var/lib/mysql mysql

# Preferred modern --mount syntax (verbose key-value format)
docker run -d \
  --mount type=bind,source=/data/mysql,target=/var/lib/mysql \
  mysql
```

---

### 1.5 Docker Storage Drivers

Storage drivers manage the container's read-write layer and implement the Copy-on-Write (CoW) mechanism across image layers.

- **Common Drivers**: `overlay2` (default for modern Linux), `aufs`, `btrfs`, `zfs`, `devicemapper`.
- **Selection**: Automatically chosen by Docker based on the host kernel and underlying OS filesystem support.

> [!NOTE]
> Storage drivers only manage ephemeral image and container layers. They **do not** manage persistent volumes. Persistent volumes are handled by **Volume Driver Plugins**.

---

### 1.6 Docker Volume Driver Plugins

Volume driver plugins allow Docker to create volumes on external, remote, or cloud storage solutions rather than the default local `/var/lib/docker/volumes` path.

![Diagram](images/image187.png)

- **Common Plugins**: Local (default), RexRay, Portworx, Flocker, DigitalOcean Block Storage, GlusterFS, NetApp.
- **Multi-Cloud Support**: Plugins like RexRay connect directly to AWS EBS, GCP Persistent Disk, or OpenStack Cinder.

![Diagram](images/image128.png)

```bash
# Running container backed by cloud block storage via volume plugin
docker run -d \
  --volume-driver rexray/ebs \
  -v ebs-volume:/var/lib/mysql \
  mysql
```

---

## 2. Container Storage Interface (CSI)

### 2.1 Evolution: CRI, CNI, and CSI

Early Kubernetes versions maintained in-tree storage drivers where vendor-specific code lived directly inside the core Kubernetes codebase. To decouple third-party plugins from Kubernetes releases, standard interfaces were introduced:

1. **CRI (Container Runtime Interface)**: Standard interface for container engines (containerd, CRI-O).
2. **CNI (Container Network Interface)**: Standard interface for network plugins (Calico, Flannel, Cilium).
3. **CSI (Container Storage Interface)**: Standard universal interface for storage providers.

![Diagram](images/image41.png)

![Diagram](images/image142.png)

---

### 2.2 CSI Architecture & RPC Specification

CSI is a vendor-neutral specification allowing container orchestrators (Kubernetes, Mesos, Cloud Foundry) to interact with any storage provider through standardized gRPC remote procedure calls.

![Diagram](images/image284.png)

![Diagram](images/image317.png)

#### Key CSI Operations:
- **`CreateVolume` / `DeleteVolume`**: Orchestrator requests storage creation or decommission on the storage backend.
- **`ControllerPublishVolume` / `ControllerUnpublishVolume`**: Storage controller attaches/detaches block storage to/from a specific compute node.
- **`NodeStageVolume` / `NodePublishVolume`**: Formats the volume and mounts it into the Pod container target filesystem.

---

## 3. Kubernetes Volumes

### 3.1 Ephemeral Pod Lifecycle & Volume Need

Pods are ephemeral resources. When a container terminates or a Pod restarts, all data written inside the container's root filesystem is lost. 

Attaching a volume at the Pod level decouples storage lifecycle from container lifecycles:
- Data persists across container crashes within the same Pod.
- Different containers in the same Pod can share files by mounting the same volume.

---

### 3.2 Volume Definition & Mount Syntax

A volume is defined in `spec.volumes` and mounted into container paths using `spec.containers[*].volumeMounts`.

![Diagram](images/image122.png)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: random-number-generator
spec:
  containers:
  - name: alpine
    image: alpine
    command: ["/bin/sh", "-c"]
    args: ["shuf -i 1-100 -n 1 > /opt/number.out; sleep 3600"]
    volumeMounts:
    - name: data-volume
      mountPath: /opt
  volumes:
  - name: data-volume
    hostPath:
      path: /data
      type: DirectoryOrCreate
```

---

### 3.3 Volume Storage Types & `hostPath` Limitations

While `hostPath` maps a directory from the local worker node into the Pod:
- **Single Node Clusters**: Works fine for local testing.
- **Multi-Node Clusters**: **Never recommended for production**. If the Pod is rescheduled onto another worker node, it accesses a completely different local directory lacking previous data.

![Diagram](images/image398.png)

#### Cluster & Cloud Storage Alternatives:
Kubernetes supports enterprise networked and cloud storage solutions:
- **Network Storage**: NFS, CephFS, GlusterFS, iSCSI.
- **Cloud Volumes**: AWS EBS, GCE Persistent Disk, Azure Disk/File.

```yaml
# Mounting an AWS EBS volume directly inside a Pod
spec:
  volumes:
  - name: data-volume
    awsElasticBlockStore:
      volumeID: "vol-049df61146c4d7951"
      fsType: ext4
```

> [!WARNING]
> Defining storage configurations directly inside Pod manifests tightly couples application manifests with cluster infrastructure. This operational limitation led to the separation of **PersistentVolumes (PV)** and **PersistentVolumeClaims (PVC)**.

---

## 4. Persistent Volumes (PV)

### 4.1 Architecture & Administrator Workflow

- **PersistentVolume (PV)**: A cluster-scoped storage resource provisioned by a cluster administrator (or dynamically via StorageClasses). It captures low-level storage details (e.g., NFS server IP, cloud disk ID, local disk path).
- **Decoupling**: Developers request storage via **PersistentVolumeClaims (PVC)** without needing to know underlying storage backend IPs, credentials, or volume IDs.

![Diagram](images/image399.png)

---

### 4.2 Access Modes

Access modes specify how nodes can attach and mount the volume:

![Diagram](images/image251.png)

| Access Mode | CLI Abbr | Description | Common Backends |
| :--- | :--- | :--- | :--- |
| **ReadWriteOnce** | `RWO` | Mounted as read-write by a **single node** only | AWS EBS, GCE PD, Azure Disk |
| **ReadOnlyMany** | `ROX` | Mounted as read-only by **many nodes** simultaneously | NFS, CephFS |
| **ReadWriteMany** | `RWX` | Mounted as read-write by **many nodes** simultaneously | NFS, Azure File, GlusterFS |
| **ReadWriteOncePod** | `RWOP` | Mounted as read-write by a **single Pod** across the cluster | CSI-supported drivers (k8s 1.22+) |

> [!IMPORTANT]
> Access modes indicate **node-level concurrency**, not Pod concurrency. Multiple Pods running on the **same worker node** can all access an `RWO` volume simultaneously.

---

### 4.3 PersistentVolume Manifest & Management

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-vol1
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /tmp/data
```

#### Core CLI Commands:
```bash
# Create PersistentVolume
kubectl apply -f pv-vol1.yaml

# Verify PV creation & status
kubectl get pv

# Sample Output:
# NAME      CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   AGE
# pv-vol1   1Gi        RWO            Retain           Available                          12s

# Describe details
kubectl describe pv pv-vol1

# Delete PV
kubectl delete pv pv-vol1
```

---

## 5. Persistent Volume Claims (PVC)

### 5.1 Architecture & Binding Mechanism

A **PersistentVolumeClaim (PVC)** is a namespace-scoped request for storage by a user. Kubernetes automatically searches for an `Available` PersistentVolume that satisfies the claim's requirements and binds them together.

Binding criteria evaluated:
1. **Sufficient Storage Capacity** (`requests.storage` $\le$ PV capacity).
2. **Matching Access Modes** (`accessModes`).
3. **Matching StorageClass** (`storageClassName`).
4. **Label Selectors** (`selector.matchLabels` if specified).

![Diagram](images/image226.png)

---

### 5.2 1-to-1 Binding Principle & Capacity Matching

- **Strict 1-to-1 Mapping**: Every bound PVC is bound to exactly one PV. No other PVC can claim remaining surplus capacity of that PV.
- **Smaller Claim vs Larger Volume**: If a PVC requests `500Mi` and the only available matching PV is `1Gi`, Kubernetes binds the `500Mi` claim to the `1Gi` volume. The remaining `500Mi` is locked and unusable by other claims.

![Diagram](images/image84.png)

- **Pending Claims**: If no suitable PV is available, the PVC remains in `Pending` status until a matching volume is created or dynamic provisioning triggers.

---

### 5.3 PVC Manifest & Binding Lifecycle

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myclaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

```bash
# Apply PVC manifest
kubectl apply -f myclaim.yaml

# Check PVC binding status
kubectl get pvc
# NAME      STATUS   VOLUME    CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# myclaim   Bound    pv-vol1   1Gi        RWO                           5s

# Check corresponding PV status (becomes Bound to default/myclaim)
kubectl get pv
# NAME      CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM             STORAGECLASS   AGE
# pv-vol1   1Gi        RWO            Retain           Bound    default/myclaim                  2m
```

---

### 5.4 PersistentVolume Reclaim Policies

The reclaim policy tells Kubernetes what to do with the physical volume once its associated PVC is deleted:

| Reclaim Policy | Behavior upon PVC Deletion | Target PV Status |
| :--- | :--- | :--- |
| **`Retain`** (Default for manual PV) | Underlying volume and storage remain untouched. Data is preserved. | `Released`. Needs manual cleanup before re-use. |
| **`Delete`** (Default for Dynamic PV) | Automatically deletes the Kubernetes PV object and the physical storage asset (e.g. AWS EBS). | N/A (Destroyed). |
| **`Recycle`** (*Deprecated*) | Scrubs volume data via basic `rm -rf /thevolume/*` and makes the PV available again. | `Available`. |

---

### 5.5 Using PVCs in Pods & Deployments

To consume a PVC inside a Pod, reference the claim name under `spec.volumes[*].persistentVolumeClaim.claimName`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: nginx
      volumeMounts:
      - name: mypd
        mountPath: /var/www/html
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: myclaim
```

> [!TIP]
> In Deployments or StatefulSets, place `volumes` under `spec.template.spec.volumes` and `volumeMounts` under `spec.template.spec.containers[*].volumeMounts`.

---

## 6. Hands-On CKA Scenarios & Troubleshooting

### 6.1 Scenario 1: Inspecting & Persisting Container Logs with `hostPath`

**Problem Statement:** An application Pod named `webapp` outputs logs directly to `/log/app.log`. Because storage is ephemeral, deleting the Pod destroys the log history. Configure a hostPath volume to persist logs to `/var/log/webapp` on the host.

1. Inspect container logs via `exec`:
   ```bash
   kubectl exec webapp -- cat /log/app.log
   ```

2. Export the current Pod definition:
   ```bash
   kubectl get pod webapp -o yaml > webapp.yaml
   ```

3. Update `webapp.yaml` with `volumeMounts` and `hostPath`:
   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: webapp
   spec:
     containers:
     - name: event-simulator
       image: kodekloud/event-simulator
       env:
       - name: LOG_HANDLERS
         value: file
       volumeMounts:
       - mountPath: /log
         name: log-volume
     volumes:
     - name: log-volume
       hostPath:
         path: /var/log/webapp
         type: DirectoryOrCreate
   ```

4. Recreate the Pod using `--force`:
   ```bash
   kubectl replace -f webapp.yaml --force
   ```

---

### 6.2 Scenario 2: Creating a PersistentVolume (`pv-log`)

**Requirements:**
- Volume Name: `pv-log`
- Capacity: `100Mi`
- Access Modes: `ReadWriteMany`
- Host Path: `/pv/log`
- Reclaim Policy: `Retain`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-log
spec:
  capacity:
    storage: 100Mi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /pv/log
```

Apply and verify:
```bash
kubectl apply -f pv-log.yaml
kubectl get pv pv-log
```

---

### 6.3 Scenario 3: Troubleshooting PVC Binding Failures (`claim-log-1`)

**Diagnostic Exercise:** A student created a PVC that remained in `Pending` status.

#### ❌ Non-Working Manifest Analysis
```yaml
# BROKEN SPEC: Will remain in Pending state
apiVersion: v1 
kind: PersistentVolumeClaim
metadata:
  name: claim-log-1
spec:
  accessModes:
    - ReadWriteOnce                      # ERROR 1: pv-log only supports ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 50Mi
  storageClassName: ""                   # Restricts to PVs with no storageClassName
  selector:
    matchLabels:
      release: "stable"                  # ERROR 2: pv-log does not possess this label
    matchExpressions:
      - {key: environment, operator: In, values: [dev]} # ERROR 3: Label missing on PV
```

**Why it failed:**
1. **Access Mode Mismatch**: `pv-log` offers `ReadWriteMany`, but claim requests `ReadWriteOnce`.
2. **Selector Mismatch**: The claim requires labels `release: stable` and `environment: dev` which do not exist on `pv-log`.

#### ✅ Fixed Working Manifest
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claim-log-1
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Mi
```

Apply and verify:
```bash
kubectl apply -f claim-log-1.yaml
kubectl get pvc claim-log-1
kubectl get pv pv-log
```

---

### 6.4 Scenario 4: Mounting PVC into Application Pod

Update the `webapp` Pod to consume `claim-log-1`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
spec:
  containers:
  - name: event-simulator
    image: kodekloud/event-simulator
    env:
    - name: LOG_HANDLERS
      value: file
    volumeMounts:
    - mountPath: /log
      name: log-volume
  volumes:
  - name: log-volume
    persistentVolumeClaim:
      claimName: claim-log-1
```

Apply the updated Pod:
```bash
kubectl replace -f webapp.yaml --force
```

---

## 7. StorageClasses & Dynamic Provisioning

### 7.1 Static vs Dynamic Provisioning

#### Static Provisioning (Manual)
1. Storage admin manually creates disks in cloud/SAN (e.g. AWS EBS, GCE PD).
2. Admin manually writes and creates a `PersistentVolume` manifest pointing to disk ID.
3. User writes a `PersistentVolumeClaim`.
4. Kubernetes binds PVC to PV.

![Diagram](images/image176.png)

![Diagram](images/image233.png)

![Diagram](images/image121.png)

*Bottleneck: Highly manual, slow, and doesn't scale for large multi-tenant clusters.*

---

#### Dynamic Provisioning (Automated via StorageClass)
1. Administrator defines a **`StorageClass`** with a provisioner and parameters.
2. User submits a `PersistentVolumeClaim` specifying `storageClassName`.
3. The StorageClass automatically provisions the cloud disk, creates a `PersistentVolume`, and binds it to the PVC.

![Diagram](images/image307.png)

![Diagram](images/image96.png)

---

### 7.2 StorageClass Architecture & Provisioners

A StorageClass specifies the provisioner plugin and backend storage attributes:

![Diagram](images/image213.png)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: google-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: none
```

#### Common In-Tree & CSI Provisioners:
- **AWS EBS CSI**: `ebs.csi.aws.com` (legacy: `kubernetes.io/aws-ebs`)
- **GCP Persistent Disk CSI**: `pd.csi.storage.gke.io` (legacy: `kubernetes.io/gce-pd`)
- **Azure Disk CSI**: `disk.csi.azure.com`
- **Local Storage (No Dynamic Provisioning)**: `kubernetes.io/no-provisioner`

---

### 7.3 Volume Binding Modes: `Immediate` vs `WaitForFirstConsumer`

The `volumeBindingMode` attribute determines when volume provisioning and binding occur:

| Binding Mode | Description | Typical Use Case |
| :--- | :--- | :--- |
| **`Immediate`** (Default) | PV is created and bound immediately once the PVC is submitted. | Centralized cloud storage unconstrained by topology. |
| **`WaitForFirstConsumer`** | Delays volume binding and provisioning until a Pod requesting the PVC is created and scheduled. | Topology-constrained storage (Local PVs, specific Availability Zones). |

> [!IMPORTANT]
> With `WaitForFirstConsumer`, the scheduler factors in Pod scheduling constraints (node affinity, tolerations, resource availability) **before** creating or binding the volume on the targeted node.

---

### 7.4 CKA Troubleshooting: Delayed Binding with Local Storage

#### 1. Inspect Cluster StorageClasses
```bash
kubectl get storageclasses
# OR
kubectl get sc
```

![Diagram](images/image248.png)

#### 2. Identifying Non-Dynamic Provisioners
StorageClasses using `kubernetes.io/no-provisioner` do **not** support dynamic volume provisioning. PVs for these classes must be manually created.

#### 3. Analyzing Pending PVC with `WaitForFirstConsumer`
A PVC named `local-pvc` is created with `storageClassName: local-storage`. A matching PV `local-pv` exists, but the PVC stays in `Pending` state.

![Diagram](images/image165.png)

```yaml
# local-pvc definition
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 500Mi
```

**Diagnostic Reason:**
The StorageClass `local-storage` defines `volumeBindingMode: WaitForFirstConsumer`. The binding will remain delayed until a Pod actively claiming `local-pvc` is scheduled.

#### 4. Resolving by Creating the Consuming Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      volumeMounts:
      - name: mypd
        mountPath: /var/www/html
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: local-pvc
```

Once `nginx` is applied, the Pod is scheduled to a node, triggering immediate binding of `local-pvc` to `local-pv`.

#### 5. Defining a Delayed-Binding StorageClass
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: delayed-volume-sc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

---

## 8. PVC Volume Expansion (Resizing)

Kubernetes allows online resizing of Persistent Volumes without downtime if supported by the underlying storage provider and CSI driver.

### 8.1 Enabling Volume Expansion in StorageClass

The StorageClass must have `allowVolumeExpansion: true`:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-sc
provisioner: csi.example.com
allowVolumeExpansion: true # REQUIRED for PVC resizing
volumeBindingMode: Immediate
```

---

### 8.2 Expanding an Existing PVC & Filesystem Status

> [!CAUTION]
> You can **only increase** volume size. Shrinking volume capacity is never supported in Kubernetes.

1. Edit the PVC directly or patch the storage request:
   ```bash
   # Option A: Interactive edit
   kubectl edit pvc data-pvc

   # Option B: Imperative JSON patch
   kubectl patch pvc data-pvc -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
   ```

2. Inspect expansion progress:
   ```bash
   kubectl describe pvc data-pvc
   ```

3. **`FileSystemResizePending` Condition**:
   - If the underlying physical volume is resized by the CSI controller, but the filesystem within the Pod has not yet expanded, the PVC status reports `FileSystemResizePending`.
   - Once a Pod mounts the volume, `kubelet` resizes the internal filesystem and clears the condition.

---

## 9. CSI Volume Snapshots & VolumeSnapshotClass

Kubernetes provides standard Custom Resource Definitions (`snapshot.storage.k8s.io`) for point-in-time copies of volumes.

### 9.1 VolumeSnapshotClass

Defines the CSI snapshot driver and deletion policy:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-aws-vsc
driver: ebs.csi.aws.com
deletionPolicy: Delete # Or 'Retain' to preserve cloud snapshot after object deletion
```

---

### 9.2 Creating a VolumeSnapshot from a PVC

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-backup-snapshot
  namespace: database
spec:
  volumeSnapshotClassName: csi-aws-vsc
  source:
    persistentVolumeClaimName: mysql-data-pvc
```

Check snapshot readiness:
```bash
kubectl get volumesnapshot -n database
# NAME                    READYTOUSE   SOURCEPVC        RESTORESIZE   AGE
# mysql-backup-snapshot   true         mysql-data-pvc   10Gi          45s
```

---

### 9.3 Restoring a PVC from a VolumeSnapshot

Create a new PVC initialized with data from an existing snapshot by configuring the `dataSource` field:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-restored-pvc
  namespace: database
spec:
  storageClassName: expandable-sc
  dataSource:
    name: mysql-backup-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi # Must be greater than or equal to snapshot size
```

---

## 10. CKA Exam Quick Reference & Cheat Sheet

```bash
# Core Resource Queries
kubectl get pv
kubectl get pvc -n <namespace>
kubectl get sc
kubectl get volumesnapshot -n <namespace>

# Describe & Inspect Events
kubectl describe pvc <pvc-name>
kubectl describe pv <pv-name>

# Fast Dry-Run Generation
kubectl run test-pod --image=nginx --dry-run=client -o yaml > pod.yaml

# Patching Resources
kubectl patch pvc <pvc-name> -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
```

### Essential Exam Takeaways:
1. **Scope Distinction**: `PersistentVolume` and `StorageClass` are **cluster-scoped** resources. `PersistentVolumeClaim` and `Pod` are **namespace-scoped** resources.
2. **1-to-1 Rule**: One PVC binds to exactly one PV. Unused capacity in a bound PV cannot be shared.
3. **Delayed Binding**: If a PVC is `Pending` with `WaitForFirstConsumer`, inspect whether a Pod utilizing the claim has been scheduled.
4. **Volume Expansion**: Requires `allowVolumeExpansion: true` on the `StorageClass`. Can only expand, never reduce.
5. **Snapshot Restoration**: PVC created from snapshot must request capacity $\ge$ the snapshot's `restoreSize`.
