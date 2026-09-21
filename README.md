# Kubernetes Apartment Complex

An illustrated, hands-on guide to Kubernetes control-plane components, node
runtime, networking, storage, RBAC, workload controllers, and autoscaling.

## Contents

- [Complete demo guide](demos-complete.md) — 41 runnable topics with technical
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

Read [demos-complete.md](demos-complete.md) for the 41 exercises. Each demo
has setup, live steps, expected observations, and cleanup. Optional add-ons
include ingress-nginx, a policy-enforcing CNI, metrics-server, and VPA; the
guide calls out the demos that require each one.

## Cleanup

```bash
./scripts/kind-down.sh
```

This removes the kind node containers and local cluster state, but does not
remove this repository or unrelated Docker images.
