# Kubernetes Apartment Complex

An illustrated, hands-on guide to Kubernetes control-plane components, node
runtime, networking, storage, RBAC, workload controllers, and autoscaling.

## Contents

- [Complete demo guide](demos-complete.md) — 46 runnable topics with technical
  explanations, zine illustrations, realtime observations, and kind demos.
- [`kind-multinode.yaml`](kind-multinode.yaml) — one control-plane and two
  worker nodes, with local Ingress mapped to ports 8080 and 8443.
- [`scripts/kind-up.sh`](scripts/kind-up.sh) — create or reuse the lab cluster.
- [`scripts/kind-doctor.sh`](scripts/kind-doctor.sh) — inspect nodes, components,
  containerd, and kind node containers.
- [`scripts/kind-down.sh`](scripts/kind-down.sh) — remove the disposable lab.
- [Generated illustrations](generated/kubernetes-apartment-complex/) — one
  technical image and one apartment-complex zine image per topic.
- [Zine prompt pack](kubernetes-full-controllers-zine-prompts.fixed.md)
- [CKA Study Notes (10 Modules)](CKA_Study_Notes/README.md) — comprehensive companion study modules with 430+ diagrams, architecture flows, command reference, and exam notes.

## 📚 CKA Study Notes (Companion Modules)

The companion modules in [`CKA_Study_Notes/`](CKA_Study_Notes/README.md) provide in-depth theory, diagrams, and CLI commands mapped to the 46 apartment complex topics:

| Module | Title | Key Concepts & Coverage |
| --- | --- | --- |
| [01](CKA_Study_Notes/01-core-concepts.md) | [Core Concepts](CKA_Study_Notes/01-core-concepts.md) | Cluster Architecture, etcd, API Server, Controller Manager, Scheduler, Kubelet, Kube-Proxy, Pods, ReplicaSets, Deployments, Services, Namespaces, Imperative Commands |
| [02](CKA_Study_Notes/02-scheduling.md) | [Scheduling](CKA_Study_Notes/02-scheduling.md) | Manual Scheduling, Labels/Selectors, Taints/Tolerations, Node Affinity, Resource Requirements/Limits, DaemonSets, Static Pods, Custom Schedulers, Topology Spread Constraints, PriorityClass & Pod Preemption, Pod Disruption Budgets (PDB) |
| [03](CKA_Study_Notes/03-logging-and-monitoring.md) | [Logging & Monitoring](CKA_Study_Notes/03-logging-and-monitoring.md) | Metrics Server, Cluster Monitoring (`top node`/`top pod`), Advanced `kubectl logs` streaming/timestamps/previous, JSONPath expressions, Custom Columns, Sorting, Cluster Events, `journalctl` Kubelet Logs |
| [04](CKA_Study_Notes/04-application-lifecycle-management.md) | [Application Lifecycle Management](CKA_Study_Notes/04-application-lifecycle-management.md) | Rolling Updates, Rollbacks, Commands/Args, ConfigMaps, Secrets, Multi-Container Pods & Native Sidecars, Init Containers |
| [05](CKA_Study_Notes/05-cluster-maintenance.md) | [Cluster Maintenance](CKA_Study_Notes/05-cluster-maintenance.md) | OS Upgrades (`drain`/`cordon`/`uncordon`), Version Lifecycle, Step-by-Step Kubeadm Cluster Upgrade Playbook (Control Plane & Worker Nodes), Kubeadm Certificate Expiry & Renewal, etcd Backup & Snapshot Restore |
| [06](CKA_Study_Notes/06-security.md) | [Security](CKA_Study_Notes/06-security.md) | Security Primitives, TLS Bootstrapping & Certificates API, KubeConfig, RBAC (Roles & ClusterRoles), Projected ServiceAccount Tokens (`TokenRequest` API), Image Security, SecurityContexts, NetworkPolicies, Admission Controllers |
| [07](CKA_Study_Notes/07-networking.md) | [Networking](CKA_Study_Notes/07-networking.md) | Linux Networking (netns, iptables, routing), CNI Plugins, ClusterIP & NodePort Services, CoreDNS, Modern Ingress v1 Spec (TLS termination, path types), Gateway API, `kubectl port-forward` Debugging |
| [08](CKA_Study_Notes/08-storage.md) | [Storage](CKA_Study_Notes/08-storage.md) | Docker Storage Drivers, CSI Architecture, PersistentVolumes (PV), PersistentVolumeClaims (PVC), StorageClasses, Live PVC Volume Expansion (`allowVolumeExpansion`), CSI Volume Snapshots & VolumeSnapshotClasses |
| [09](CKA_Study_Notes/09-cluster-design-and-installation.md) | [Design & Install Cluster](CKA_Study_Notes/09-cluster-design-and-installation.md) | HA Topologies, Stacked vs External etcd, Automated Kubeadm Cluster Deployment |
| [10](CKA_Study_Notes/10-troubleshooting.md) | [Troubleshooting](CKA_Study_Notes/10-troubleshooting.md) | Application Failures, Service Routing Diagnosis, Control Plane Static Pod Diagnosis, Worker Node NotReady Triage (cgroups, containerd, swap), Network Troubleshooting, Interactive `kubectl debug` (ephemeral containers, pod copies, node chroot) |

## Runtime model

The host provider is Docker: Docker Engine on Linux or Docker Desktop on macOS.
kind creates three Linux node containers, and kubelet inside each node talks to
containerd through CRI. Verify that boundary after startup:

```bash
kubectl get nodes -o custom-columns='NAME:.metadata.name,RUNTIME:.status.nodeInfo.containerRuntimeVersion'
docker exec zine-worker crictl info
```

The output should show `containerd://...`. On macOS, Docker Desktop runs the
Linux containers inside a VM, so the checked-in port mappings are the reliable
way to reach Ingress from the host.

## Linux setup

These commands target Ubuntu/Debian. For other Linux distributions, use the
[official Docker Engine instructions](https://docs.docker.com/engine/install/),
then continue with the kind and kubectl steps.

1. Install Docker Engine and containerd:

   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   . /etc/os-release
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   sudo systemctl enable --now docker
   ```

2. Let the current user run Docker, then open a new login session:

   ```bash
   sudo usermod -aG docker "$USER"
   newgrp docker
   docker run --rm hello-world
   ```

3. Install `kubectl` and kind. The architecture mapping covers amd64 and arm64:

   ```bash
   KUBECTL_VERSION="$(curl -L -s https://dl.k8s.io/release/stable.txt)"
   KUBECTL_ARCH="$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')"
   curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${KUBECTL_ARCH}/kubectl"
   chmod +x kubectl && sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl

   KIND_VERSION="v0.33.0"
   curl -Lo kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${KUBECTL_ARCH}"
   chmod +x kind && sudo install -m 0755 kind /usr/local/bin/kind && rm kind
   ```

4. Check the installation:

   ```bash
   docker version
   kind version
   kubectl version --client
   ```

## macOS setup

1. Install and start [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/).
   Give Docker Desktop at least 6 GB of memory for this three-node lab.

2. Install the CLI tools with Homebrew:

   ```bash
   brew install docker kubectl kind
   docker version
   kind version
   kubectl version --client
   docker run --rm hello-world
   ```

   Docker Desktop provides the Linux VM and Docker engine. The kind nodes
   created inside it still use containerd through CRI.

## Start and verify the realtime lab

From the repository root:

```bash
./scripts/kind-up.sh
./scripts/kind-doctor.sh
```

In a second terminal, watch the cluster while running a demo:

```bash
kubectl get pods -A -o wide -w
kubectl get events -A --sort-by=.lastTimestamp -w
```

Use Ctrl+C to stop a watch. For the Ingress demo, use:

```bash
curl -i -H 'Host: demo.local' http://localhost:8080/
```

For node-level runtime inspection, run commands inside a kind node:

```bash
docker exec -it zine-control-plane bash
docker exec -it zine-worker bash
docker exec zine-worker crictl ps
```

Read [demos-complete.md](demos-complete.md) for the 46 exercises. Each demo
has setup, live steps, expected observations, and cleanup. Optional add-ons
include ingress-nginx, a policy-enforcing CNI, metrics-server, and VPA; the
guide calls out the demos that require each one.

## Cleanup

```bash
./scripts/kind-down.sh
```

This removes the kind node containers and local cluster state, but does not
remove this repository or unrelated Docker images.
