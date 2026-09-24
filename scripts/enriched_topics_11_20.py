# scripts/enriched_topics_11_20.py
"""
Enriched technical discussions and perspectives for Topics 11-20.
Incorporates deep CKA Study Notes, Linux OS/Kernel concepts, bulleted points,
and production-grade YAML manifests.
"""

ENRICHED_11_20 = {
    11: {
        "tech_disc": """The **Container Runtime** is the software stack on each worker node responsible for executing containers. Kubernetes interacts with container runtimes via the **Container Runtime Interface (CRI)**, a gRPC API that standardizes how the kubelet manages container sandboxes, image pulling, and container lifecycles across diverse runtimes (containerd, CRI-O).

### CRI Architecture: High-Level vs. Low-Level Runtimes
- **CRI Layer (containerd / CRI-O):** Manages image distribution, local image storage snapshots, lifecycle events, and communicates with the kubelet via Unix domain sockets (e.g., `/run/containerd/containerd.sock`).
- **OCI Layer (runc / crun):** Low-level Open Container Initiative compliant runtime that invokes kernel system calls (`clone`, `unshare`, `pivot_root`, `setns`) to configure namespaces and cgroups, spawning the actual isolated Linux process.
- **crictl CLI Utility:** The official CKA command-line tool for inspecting CRI runtimes directly (`crictl pods`, `crictl ps`, `crictl images`, `crictl logs`).

### Linux OS & Kernel Foundation
Containers do not exist as independent virtual machines; they are regular Linux processes constrained by the kernel. The container runtime orchestrates these native kernel boundaries whenever a pod starts:
- **Namespaces:** Isolates visibility per container (Mount `mnt`, Process ID `pid`, Network `net`, Inter-Process `ipc`, Hostname `uts`, User `user`).
- **Control Groups (cgroups v2):** Enforces resource boundaries under unified hierarchy `/sys/fs/cgroup/kubepods.slice/`.
- **OverlayFS:** Union filesystem combining read-only image layers (`lowerdir`), a thin writable container layer (`upperdir`), and a merged execution mount (`merged`).

```yaml
# oci-security-pod.yaml
# WHY THIS YAML: These security fields are translated by containerd into OCI runtime spec,
#   which runc passes to Linux kernel syscalls when creating the container sandbox.
# 'runAsNonRoot: true': containerd verifies UID != 0 before starting the container.
# 'seccompProfile: RuntimeDefault': containerd loads a BPF filter blocking dangerous syscalls.
# 'allowPrivilegeEscalation: false': sets the no_new_privs prctl flag via runc.
# 'capabilities.drop: ALL': runc calls cap_set_proc() stripping all Linux capabilities.
apiVersion: v1
kind: Pod
metadata:
  name: hardened-container
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: registry.k8s.io/pause:3.9
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```""",
        "tech_persp": """Dockershim was permanently removed in Kubernetes 1.24, making containerd and CRI-O the standard production runtimes:
- **cgroup Driver Alignment:** Both containerd (`SystemdCgroup = true` in `/etc/containerd/config.toml`) and kubelet (`cgroupDriver: systemd`) must match systemd. Mismatched drivers cause node instability and crash loops.
- **Image Garbage Collection:** Kubelet instructs CRI to clean up unused image layers when disk utilization passes `imageGCHighThresholdPercent` (default 85%)."""
    },

    12: {
        "tech_disc": """A **Sidecar Container** is a multi-container Pod architectural pattern where a secondary container runs alongside the primary application container to augment, proxy, or enhance its functionality (e.g., logging agents, Envoy service mesh proxies, metric exporters, vault credential refreshers).

### Shared Pod Sandbox Mechanics
- **Shared Network Namespace:** All containers within the same Pod share the exact same Linux network namespace (`netns`). They communicate with each other over the loopback interface (`localhost:port`) with zero network virtualization overhead.
- **Shared Volumes:** Containers share filesystem data in-memory or on-disk via `emptyDir` volumes, allowing log shippers (e.g., Fluent Bit) to tail logs written by application containers.
- **Native Sidecar Containers (K8s 1.28+):** Built directly into `initContainers` using `restartPolicy: Always`. Unlike legacy sidecars, native sidecars start *before* application containers and do not block Pod shutdown.

### Linux Namespace Sharing
The sidecar pattern functions because Kubernetes groups containers under shared Linux namespaces rather than isolating each container entirely. This selective boundary sharing enables sidecars to assist the main app with zero network overhead:
- Processes in the Pod share the network namespace (`/proc/<pid>/ns/net`) and optionally the PID namespace if `shareProcessNamespace: true` is configured, allowing sidecars to monitor application PIDs directly.

```yaml
# native-sidecar-pod.yaml
# WHY THIS YAML: Demonstrates the native sidecar pattern (Kubernetes 1.28+).
# 'initContainers' with 'restartPolicy: Always': this is what makes it a native sidecar.
#   It starts BEFORE application containers but does NOT exit -- stays running alongside.
# 'shared-logs emptyDir volume': both containers mount the SAME Linux tmpfs directory.
#   The sidecar reads logs written by web-app because they share the same volume mount
#   -- enabled by the Pod's shared mount namespace (all containers share Pod volumes).
apiVersion: v1
kind: Pod
metadata:
  name: web-with-sidecar
spec:
  initContainers:
  - name: telemetry-sidecar
    image: registry.k8s.io/pause:3.9
    restartPolicy: Always
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app
  containers:
  - name: web-app
    image: registry.k8s.io/pause:3.9
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app
  volumes:
  - name: shared-logs
    emptyDir: {}
```""",
        "tech_persp": """Sidecars introduce operational trade-offs in resource footprint and lifecycle management:
- **Resource Summation:** Pod resource requests and limits equal the sum of all primary containers plus sidecar containers. Excessive sidecars reduce node scheduling density.
- **Shutdown Race Conditions:** With legacy sidecars, if the application container finishes but the sidecar keeps running, the Pod never terminates, causing Job failures. Native sidecars (`restartPolicy: Always`) solve this problem natively."""
    },

    13: {
        "tech_disc": """**Init Containers** are specialized containers that run sequentially to completion before any application containers in the Pod are started. If an init container fails, the kubelet restarts the Pod until the init container succeeds (governed by `restartPolicy`).

### Primary Use Cases & Guarantees
- **Sequential Execution:** Multiple init containers run in strict declared array order (`init[0] -> init[1] -> init[2]`).
- **Prerequisite Blocking:** Verifies network dependencies (e.g., waiting for PostgreSQL or Redis with `nc -z` or `curl`) before the primary app starts.
- **Privileged Pre-flight Setup:** Can run with elevated Linux capabilities (`NET_ADMIN`) to configure iptables rules (e.g., Istio proxy redirection) while leaving the primary application completely unprivileged.
- **Filesystem Hydration:** Clones git repos, seeds configuration templates, or unpacks assets into a shared `emptyDir` volume.

### Linux Execution Flow
Init containers enforce strict prerequisites before main applications boot. The kubelet relies on Linux process exit status codes to coordinate this startup pipeline:
- Kubelet starts the init container sandbox, binds volumes, and monitors process exit code.
- Kubelet proceeds to the next container only when the process exits with **status code 0**.

```yaml
# init-container-dependency.yaml
# WHY THIS YAML: Init containers enforce startup prerequisites before the main app starts.
# The kubelet runs init containers IN ORDER, each must exit code 0 before the next starts.
# Common pattern: init container runs 'until nc -z postgres 5432; do sleep 2; done'
#   -- the main app container will not start until the DB port is confirmed open.
# Init containers share Pod volumes (emptyDir, PVCs), allowing pre-seeding of config
#   files, DB migrations, or secrets into shared storage before the app reads them.
apiVersion: v1
kind: Pod
metadata:
  name: app-with-preflight
spec:
  initContainers:
  - name: wait-for-db
    image: busybox:1.36
    command: ['sh', '-c', 'until nc -z -w 2 db-service 5432; do echo waiting for db...; sleep 2; done']
  - name: hydrate-config
    image: busybox:1.36
    command: ['sh', '-c', 'echo "database_url=postgres://db-service" > /work/app.env']
    volumeMounts:
    - name: config-vol
      mountPath: /work
  containers:
  - name: api
    image: registry.k8s.io/pause:3.9
    volumeMounts:
    - name: config-vol
      mountPath: /work
  volumes:
  - name: config-vol
    emptyDir: {}
```""",
        "tech_persp": """Init containers must be idempotent because crashes or node reboots will cause them to re-execute from the beginning:
- **Resource Computation:** The effective resource request of a Pod is `max(max(init_containers), sum(app_containers))`. An init container requesting 4 CPU cores will cause the entire Pod to require 4 cores during scheduling, even if it runs for only 5 seconds.
- **Debugging Blocked Pods:** When a Pod is stuck in `Init:0/1`, run `kubectl logs <pod-name> -c <init-container-name>` to inspect why the preflight check is stalling."""
    },

    14: {
        "tech_disc": """The **Container Network Interface (CNI)** is a CNCF specification that standardizes how third-party networking plugins configure Linux network namespaces for containers. Kubernetes mandates a flat, non-NAT network model across the entire cluster.

### Fundamental Kubernetes Networking Rules
1. Every Pod receives a unique, routable IP address within the cluster.
2. All Pods can communicate with all other Pods on any node without Network Address Translation (NAT).
3. All Nodes can communicate directly with all Pods without NAT.
4. The IP that a Pod sees for itself is the exact same IP that any other Pod sees for it.

### Linux Kernel Networking Mechanisms
Every container starts inside an empty, isolated network namespace without interfaces. The CNI plugin connects this isolated bubble to the host and cluster network using virtual Linux networking devices:
- **Virtual Ethernet (veth) Pairs:** CNI creates a Linux `veth` pair (`veth-host` and `veth-pod`). One end is connected to the host network namespace (attached to bridge `cni0` or routed via eBPF), while the other is moved into the container's network namespace as `eth0`.
- **IPAM (IP Address Management):** Allocates subnets to worker nodes from cluster PodCIDR using plugins like `host-local` or cloud VPC IPAM.
- **Encapsulation vs. Direct Routing:**
  - *Overlay Networks (VXLAN / Geneve):* Encapsulates Pod L2 frames inside host UDP packets (Flannel, Calico VXLAN). Operates over any underlying network.
  - *Direct / BGP Routing:* Advertises Pod routes via BGP directly to physical or cloud routers (Calico BGP, Cilium BGP) with zero encapsulation overhead.

```yaml
# calico-ippool-spec.yaml
# WHY THIS YAML: This Calico IPPool defines the CIDR range for Pod IP allocation.
# 'cidr: 192.168.0.0/16': every Pod gets an IP from this block via CNI IPAM.
#   When kubelet calls the CNI ADD command for a new Pod, Calico allocates from here.
# 'ipipMode: Always': cross-node Pod traffic is IP-in-IP encapsulated, enabling
#   pod-to-pod routing across nodes without BGP routing support.
# 'natOutgoing: true': enables SNAT so Pod traffic leaving the cluster uses the node IP.
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: default-ipv4-ippool
spec:
  cidr: 10.244.0.0/16
  ipipMode: Never
  vxlanMode: Always
  natOutgoing: true
  nodeSelector: all()
```""",
        "tech_persp": """Selecting and operating a CNI determines cluster security and performance:
- **MTU Sizing:** VXLAN encapsulation adds a 50-byte outer header. If host MTU is 1500, CNI interface MTU must be configured to 1450. MTU mismatches result in silent packet dropping for packets larger than the threshold.
- **eBPF Acceleration:** Modern CNIs (Cilium, Calico eBPF) bypass iptables entirely, programming eBPF programs directly into Linux kernel socket filters (`tc` / `xdp`), cutting network latency by up to 40%."""
    },

    15: {
        "tech_disc": """**CoreDNS** is the cluster-internal DNS server deployed as a high-availability Deployment in `kube-system`. It resolves Kubernetes Service names, headless Service endpoints, and external domains for all Pods across the cluster.

### Service Discovery Naming Conventions
- **Standard Service Record:** `<service-name>.<namespace>.svc.cluster.local` resolves to the virtual ClusterIP.
- **Headless Service Record (`clusterIP: None`):** Returns the individual IPs of all ready Pods matching the selector (`A` records) or `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
- **SRV Records:** Resolves named ports (e.g., `_http._tcp.<service>.<namespace>.svc.cluster.local`).

### Linux DNS Resolution & resolv.conf
Applications expect to discover services using simple DNS names like 'auth-db' instead of dynamic IP addresses. To facilitate this transparently, the kubelet configures the standard Linux resolver file inside every container filesystem:
- Kubelet automatically populates `/etc/resolv.conf` in every container with:
  ```text
  nameserver 10.96.0.10
  search <namespace>.svc.cluster.local svc.cluster.local cluster.local
  options ndots:5
  ```
- **The `ndots:5` Challenge:** Any query with fewer than 5 dots (e.g., `google.com`) searches sequentially through every local search path first before querying the root servers, generating 4-5 redundant DNS queries per external lookup.

```yaml
# coredns-configmap.yaml
# WHY THIS YAML: This ConfigMap IS the CoreDNS Corefile -- its runtime configuration.
# 'cluster.local': the cluster domain. Services resolve as:
#   <service>.<namespace>.svc.cluster.local -> ClusterIP address.
# 'kubernetes cluster.local': uses the Kubernetes API as the DNS backend,
#   watching Service and EndpointSlice objects to answer queries in real time.
# 'forward . /etc/resolv.conf': external domain queries forwarded to node DNS.
# Every Pod's /etc/resolv.conf is auto-configured to use this CoreDNS ClusterIP.
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
          ready
          kubernetes cluster.local in-addr.arpa ip6.arpa {
             pods insecure
             fallthrough in-addr.arpa ip6.arpa
             ttl 30
          }
          prometheus :9153
          forward . /etc/resolv.conf
          cache 30
          loop
          reload
          loadbalance
      }
```""",
        "tech_persp": """DNS failure is one of the most common causes of cluster-wide outages:
- **NodeLocal DNSCache:** In high-concurrency clusters, deploying `NodeLocal DNSCache` (a DaemonSet running CoreDNS on `169.254.20.10`) avoids conntrack UDP race conditions and eliminates DNS latency.
- **CoreDNS Autoscaling:** CoreDNS must be scaled proportionally using `cluster-proportional-autoscaler` based on the number of nodes and cores in the cluster."""
    },

    16: {
        "tech_disc": """A **Service** is an abstract REST object in Kubernetes that defines a logical set of Pods and a consistent policy by which to access them, providing a stable network endpoint (IP address and DNS name) for an ephemeral population of containers.

### Why Do We Need Services? (Beginner)
In Kubernetes, **Pods are mortal and ephemeral**:
- A Pod can crash, be killed by the out-of-memory killer, or be deleted during a rolling deployment.
- When a replacement Pod is created, it receives a **completely new, dynamic IP address** from the node's PodCIDR pool.
- Furthermore, horizontally scaled applications have multiple identical Pod replicas running simultaneously across different nodes.

If frontend applications attempted to connect directly to backend Pod IP addresses, every pod restart or scale event would break network connections, requiring constant manual updates to client configurations.
A **Service** solves this by acting as a permanent front desk:
- It assigns a single, unchanging virtual IP (**ClusterIP**) and a stable internal DNS name (e.g., `auth-service`).
- Clients send traffic to the Service's stable IP or name, and Kubernetes automatically load-balances requests across all healthy backend Pods.
- As backend Pods appear, disappear, or restart, the Service updates its routing targets automatically. The client never needs to know the real Pod IPs.

### How Services Select Pods & Route Traffic (Intermediate)
Services decouple callers from backends using **Label Selectors**:
1. **The Selector Contract:** A Service declares a `spec.selector` (e.g., `app: web-frontend`). Any Pod in the same namespace with matching labels is automatically included in the Service's routing pool.
2. **Health Gating via Readiness Probes:** A Pod is only included in the Service's active routing pool if it passes its **readiness probe**. Crashing or booting Pods receive zero traffic.
3. **Port Mapping Decoupling:**
   - `port`: The port that the Service exposes to internal callers (e.g., port 80).
   - `targetPort`: The actual port the application container is listening on inside the Pod (e.g., port 8080).
   - This mapping allows microservices to expose clean standard ports (80/443) while internal applications run on arbitrary internal ports.

#### The 5 Service Types
- **`ClusterIP` (Default):** Exposes the Service on an internal virtual IP reachable *only* from within the cluster. Ideal for internal databases, caching layers, and private microservices.
- **`NodePort`:** Allocates a dedicated port from the cluster-wide range (default `30000-32767`) across every worker node's physical IP address. External traffic hitting `<Any-Node-IP>:<NodePort>` is forwarded to the Service.
- **`LoadBalancer`:** Extends NodePort by making cloud API calls (AWS, GCP, Azure) to automatically provision a dedicated public cloud load balancer with an external IP address.
- **`ExternalName`:** Acts as an internal DNS alias, redirecting internal cluster requests directly to an external third-party DNS CNAME (e.g., `db.vendor.com`) without proxying packets.
- **`Headless` (`clusterIP: None`):** Bypasses single virtual IP proxying. CoreDNS returns individual `A` records for each matching Pod, allowing clients (like database clusters) to connect directly to specific peer replicas.

### Virtual IPs & Kernel Netfilter Translation (Advanced)
A ClusterIP has no network interface card (NIC), no MAC address, and does not respond to ICMP ping. It is purely a routing rule programmed into the Linux kernel:
- **kube-proxy's Role:** kube-proxy watches the API server for changes to Services and EndpointSlices. On each worker node, it writes packet rewriting rules into host Linux Netfilter `iptables` or `IPVS` kernel tables.
- **Destination NAT (DNAT):** When a container sends a packet to a ClusterIP (`10.96.0.15:80`), the kernel's PREROUTING hook intercepts the packet before standard IP routing and transparently rewrites the destination IP and port to one of the healthy Pod IPs (`10.244.2.45:8080`).
- **Connection Tracking (conntrack):** The Linux kernel conntrack module remembers the translation so that return packets from the Pod have their source IP rewritten back to the ClusterIP before returning to the client container.

```yaml
# nodeport-service-spec.yaml
# WHY THIS YAML: This Service shows the ClusterIP + NodePort layered model.
# 'type: NodePort' creates BOTH a ClusterIP (internal) AND a NodePort (external).
# 'selector: app: web-frontend': EndpointSlice controller populates backends;
#   kube-proxy reads EndpointSlices to program its iptables rules.
# 'port: 80 -> targetPort: 8080': stable interface -> actual container port.
# 'nodePort: 30080': kube-proxy opens this port on every node's iptables chain.
apiVersion: v1
kind: Service
metadata:
  name: web-frontend
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 31080
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```""",
        "tech_persp": """Traffic routing policies impact network hops and client source IP preservation:
- **`externalTrafficPolicy: Local` vs `Cluster`:**
  - `Cluster` (default): Routes traffic to any node, potentially forwarding across nodes with SNAT (hiding client real IP).
  - `Local`: Only routes to pods on the node receiving the packet. Preserves the real client IP and avoids extra network hops, but risks uneven load distribution if nodes have unequal pod replicas."""
    },

    17: {
        "tech_disc": """**Endpoints** and **EndpointSlices** bridge the declarative Service abstraction with physical, live Pod network IP addresses. When a Service defines a `spec.selector`, the EndpointSlice controller automatically queries matching, healthy Pods and maintains the active backend pool.

### Architectural Evolution: Endpoints vs. EndpointSlices
- **Legacy Endpoints Resource:** Stored all backend IPs and ports in a single monolithic API object (`/api/v1/endpoints/<service-name>`). For high-replica workloads (1,000+ pods), any single pod scaling event or health change forced the API server to re-serialize the entire multi-megabyte object to etcd and blast it to all kube-proxies.
- **EndpointSlice API (`discovery.k8s.io/v1`):** Splits backend collections into distinct slices containing a maximum of 100 endpoints each. Modifying one pod updates only its corresponding slice, reducing network and etcd load by up to 90%.

### Readiness Probe Integration
- If a Pod's `readinessProbe` fails, the EndpointSlice controller immediately strips its IP address from the EndpointSlice, stopping incoming Service traffic without killing the container.

```yaml
# custom-manual-endpoints.yaml
# WHY THIS YAML: Manual Endpoints/EndpointSlices route a Service to non-Pod backends.
# A Service WITHOUT a 'selector' tells the controller NOT to auto-manage backends.
# The Endpoints object lists IP:port pairs that kube-proxy uses to program
#   its iptables/IPVS rules, exactly as it would for Pod-backed endpoints.
# This lets Kubernetes Services act as stable internal DNS names for external systems
#   (legacy VMs, managed databases), enabling transparent migration to in-cluster Pods.
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: external-database-1
  labels:
    kubernetes.io/service-name: external-database
addressType: IPv4
ports:
- name: ""
  port: 5432
  protocol: TCP
endpoints:
- addresses:
  - "192.168.1.50"
  conditions:
    ready: true
```""",
        "tech_persp": """Endpoint management is the heartbeat of zero-downtime rolling deployments:
- **Graceful Termination Drain:** When a pod is deleted, the EndpointSlice controller asynchronously removes it from endpoints while the kubelet sends `SIGTERM` to the container. If the application terminates immediately without waiting for endpoint propagation, in-flight TCP requests receive connection resets (`RST`). Always implement a `preStop` hook (`sleep 5`) in the container spec to allow endpoint propagation before stopping server listeners."""
    },

    18: {
        "tech_disc": """An **Ingress** is an API resource in Kubernetes that manages external Layer-7 (HTTP and HTTPS) routing to Services within a cluster, providing hostname routing, URL path matching, and centralized TLS/SSL termination.

### Why Do We Need Ingress? (Beginner)
In a production microservice architecture, you might deploy 30 different web applications (e.g., `checkout`, `catalog`, `user-profile`, `auth`).
If you exposed each of these applications using a `LoadBalancer` Service:
- Your cloud provider would create **30 separate cloud load balancers**, incurring massive monthly cloud infrastructure costs.
- You would have to manage 30 separate public IP addresses, 30 DNS records, and 30 distinct SSL/TLS certificates.

An **Ingress** solves this by acting as an intelligent reverse-proxy gateway:
- You provision **one single cloud load balancer** for the entire cluster.
- The Ingress controller accepts all external HTTP/HTTPS traffic at this single public IP.
- Based on the request's **hostname** (e.g., `api.example.com` vs `store.example.com`) or **URL path** (e.g., `/users` vs `/orders`), Ingress intelligently routes traffic to the appropriate internal ClusterIP Service.
- SSL certificates are installed once on the Ingress resource, providing centralized TLS termination for all backend microservices.

### Ingress Resource vs. Ingress Controller (Intermediate)
Understanding Ingress requires understanding a fundamental Kubernetes architectural distinction:
1. **The Ingress Resource:** A declarative YAML manifest where you write your routing rules (hosts, paths, backend services, and TLS secrets). Creating an Ingress resource in etcd does *nothing* on its own.
2. **The Ingress Controller:** A specialized reverse proxy (such as Ingress-NGINX, Traefik, HAProxy, or cloud ALB ingress) deployed as a pod inside the cluster. The controller continuously watches the API server for Ingress resources, dynamically generating its own internal proxy configuration (e.g., `nginx.conf`) and reloading routing tables on the fly.
3. **`IngressClass`:** Because multiple ingress controllers can run in the same cluster (e.g., an external public Ingress and an internal corporate VPN Ingress), each Ingress manifest specifies an `ingressClassName: nginx` to declare which controller should process it.

### Layer-7 Routing, TLS & Dataplane Proxies (Advanced)
- **Layer-7 vs. Layer-4 Routing:** Standard Kubernetes Services operate strictly at Layer-4 (TCP/UDP transport layer) using kernel NAT rules — they cannot inspect HTTP headers, cookies, or URL paths. Ingress operates at Layer-7 (application layer), allowing deep HTTP inspection, path rewriting, rate limiting, and header manipulation.
- **TLS Termination:** The Ingress controller mounts a Kubernetes `Secret` of type `kubernetes.io/tls` containing `tls.crt` and `tls.key`. It terminates the encrypted HTTPS session at the edge and forwards plain HTTP traffic to backend pods over the internal overlay network, offloading CPU-intensive crypto operations from your application containers.
- **Traffic Bypassing kube-proxy:** Modern Ingress controllers do not route packets through the Service ClusterIP. Instead, they query the `EndpointSlice` API directly and route HTTP requests straight to the container's Pod IP, reducing network hops and latency.

```yaml
# tls-ingress-spec.yaml
# WHY THIS YAML: This Ingress resource is processed by the Ingress Controller,
#   NOT by kube-apiserver or kube-proxy directly.
# 'ingressClassName: nginx': selects which controller watches this object.
#   Multiple controllers can coexist; className routes to the right one.
# 'tls.secretName: tls-cert': the controller reads this Secret and configures
#   its virtual host to terminate HTTPS -- Layer 7, impossible with raw kube-proxy.
# 'rules.host / path': HTTP Host header and URL-path-based routing to backend Services.
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: core-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: tls-cert
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: core-app-service
            port:
              number: 80
```""",
        "tech_persp": """Ingress controllers operate as the public-facing edge of the cluster:
- **TLS Secret Management:** TLS certificates are stored in `kubernetes.io/tls` Secrets containing `tls.crt` and `tls.key`. Automatic certificate issuance and renewal are standardly delegated to `cert-manager` via ACME/Let's Encrypt.
- **Controller Reload Penalties:** Older ingress-nginx setups reloaded the NGINX master process upon any backend endpoint change, causing transient client latency spikes. Modern controllers use dynamic Lua shared-memory routing to update backends without process reloads."""
    },

    19: {
        "tech_disc": """A **NetworkPolicy** is a declarative firewall specification in Kubernetes that controls Layer-3 and Layer-4 network traffic flow between Pods, namespaces, and external IP blocks.

### Why Do We Need NetworkPolicies? (Beginner)
By default, Kubernetes implements an entirely **flat and open network model**:
- Every Pod can communicate with every other Pod in the cluster without NAT.
- Cross-namespace traffic is completely unrestricted by default.
- If a hacker compromises an untrusted frontend pod (such as a public-facing website), they can immediately probe and communicate with sensitive internal databases, caching layers, or payment processors in any namespace across the cluster.

A **NetworkPolicy** acts as an internal network firewall:
- By default, all Pods are unisolated (allow-all).
- As soon as a NetworkPolicy selects a Pod via label matching, that Pod transitions into **isolated mode**.
- All incoming and outgoing connections are dropped *except* those explicitly permitted by whitelist rules in the policy.
- This enforces the security principle of **least privilege**: a frontend pod can only talk to the API gateway on port 8080, and the API gateway can only talk to PostgreSQL on port 5432.

### Policy Structure: Ingress & Egress Rules (Intermediate)
A NetworkPolicy defines directional filtering:
1. **`podSelector`:** Identifies which Pods this policy governs using label matching (e.g., `role: db`).
2. **`policyTypes`:** Specifies whether the policy controls `Ingress` (incoming traffic), `Egress` (outgoing traffic), or both.
3. **Whitelist Matching Criteria (3 Match Vectors):**
   - **`podSelector`:** Permits traffic from/to specific Pods in the same namespace.
   - **`namespaceSelector`:** Permits traffic from/to all Pods residing in namespaces that match specific labels.
   - **`ipBlock`:** Permits or blocks CIDR ranges (e.g., allowing outbound traffic to the company VPN while blocking public internet).
4. **Port Enforcement:** Rules specify exact transport protocols (`TCP`, `UDP`, `SCTP`) and destination ports (e.g., port 5432).

#### The Default-Deny Security Baseline
Production clusters establish a zero-trust posture by deploying a **Default-Deny All Ingress** policy in every namespace:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}  # selects all pods in namespace
  policyTypes:
  - Ingress        # no ingress rules defined = drop all incoming traffic
```
Engineers then add granular policies to explicitly permit only legitimate traffic paths.

### CNI Implementation & Kernel Packet Filtering (Advanced)
A critical architectural detail: **Kubernetes itself does not enforce NetworkPolicies!**
- **CNI Plugin Requirement:** Neither `kube-apiserver` nor `kube-proxy` filter packets. NetworkPolicies require a policy-capable **Container Network Interface (CNI)** plugin installed in the cluster (such as Calico, Cilium, Antrea, or Weave Net).
- **Silent Failure Warning:** If you deploy a NetworkPolicy on a cluster running a basic CNI that lacks policy support (like basic Flannel), the API server will save the policy without errors, but **no traffic will be filtered**.
- **Kernel-Level Enforcement:** Policy-aware CNIs translate NetworkPolicy YAML into Linux kernel filtering structures:
  - *Calico:* Writes granular Linux `iptables` and `ipset` rules directly into host filter chains.
  - *Cilium:* Compiles policies into high-performance Linux kernel **eBPF (Extended Berkeley Packet Filter)** bytecode attached to virtual ethernet (`veth`) network interfaces, evaluating rules with near-zero latency.

```yaml
# strict-backend-network-policy.yaml
# WHY THIS YAML: Enforces namespace-level network segmentation via the CNI plugin.
# 'podSelector: app: backend': once ANY NetworkPolicy selects this Pod,
#   default becomes deny-all -- only explicitly allowed traffic flows.
# 'policyTypes: [Ingress, Egress]': both directions are now controlled.
# 'ingress.from.namespaceSelector: frontend': ONLY the frontend namespace may connect.
# 'egress.ports.port: 5432': Pods may only make outbound connections to PostgreSQL.
# WARNING: Must explicitly allow DNS (port 53) or DNS resolution breaks.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```""",
        "tech_persp": """NetworkPolicies are a mandatory requirement for PCI-DSS, HIPAA, and SOC2 compliance:
- **Flannel Gotcha:** Flannel does NOT enforce NetworkPolicies! Clusters using pure Flannel will silently ignore NetworkPolicy manifests, leaving workloads completely unisolated. Canal (Flannel + Calico policy engine) or Calico must be used.
- **DNS Egress Lockdown:** When configuring an Egress default-deny policy, workloads immediately lose the ability to resolve names because port 53 UDP/TCP to CoreDNS is blocked. Always include an explicit egress rule permitting DNS traffic."""
    },

    20: {
        "tech_disc": """A **PersistentVolume (PV)** is an API resource representing a piece of networked or local storage in the cluster, provisioned ahead of time by an administrator or dynamically via a StorageClass, that exists independently of any Pod that consumes it.

### Why Do We Need PersistentVolumes? (Beginner)
Containers were originally designed to be completely **stateless and ephemeral**:
- When a container writes a file to its local filesystem (like `/var/lib/mysql`), that data is written to a thin, temporary container write layer.
- If the container crashes, restarts, or is rescheduled to another worker node, that local write layer is wiped out. **All data is permanently lost.**
- Normal Pod volumes (`emptyDir`) only survive as long as the Pod lives; deleting the Pod destroys the volume.

Stateful applications (databases, key-value stores, document repositories) require storage that survives container terminations and node crashes.
A **PersistentVolume (PV)** solves this by decoupling storage from the compute lifecycle:
- A PV represents actual physical storage (e.g., an AWS EBS volume, a Google Persistent Disk, an NFS network share, or a local NVMe disk).
- It is a **cluster-scoped resource** (it does not belong to a namespace), meaning it exists independently of any application.
- When a Pod mounts a PV, it can write data safely. If the Pod crashes and restarts three days later on a different physical server, Kubernetes reconnects that exact same storage volume with all data intact.

### Core PV Attributes & Access Modes (Intermediate)
When a storage volume is defined in Kubernetes, it declares three fundamental properties:
1. **Capacity:** The size of storage provided (e.g., `storage: 50Gi`).
2. **Access Modes:** Dictates how many nodes can mount the storage simultaneously:
   - **`ReadWriteOnce` (RWO):** Can be mounted as read-write by a **single worker node** at a time. Standard for cloud block storage (AWS EBS, GCP Persistent Disk) where a physical virtual disk cannot be attached to multiple VMs concurrently.
   - **`ReadOnlyMany` (ROX):** Can be mounted as read-only by multiple worker nodes simultaneously (e.g., shared reference datasets).
   - **`ReadWriteMany` (RWX):** Can be mounted as read-write by **many worker nodes** simultaneously. Requires network-attached filesystems (NFS, CephFS, AWS EFS).
   - **`ReadWriteOncePod` (RWOP):** Enforces that only a single *Pod* across the entire cluster can mount the volume at a time.
3. **PersistentVolume Reclaim Policy:** Determines what happens to the underlying storage when an application is done with it:
   - **`Retain`:** The PV and its physical storage data are preserved. The volume enters `Released` status and an administrator must manually recover or clean the data.
   - **`Delete`:** Deleting the application's claim automatically destroys the physical cloud disk, preventing runaway cloud storage costs.

### The Storage Subsystem & CSI Node Plugins (Advanced)
A PersistentVolume is an API abstraction, but actual data lives on a Linux block device or network mount. The mounting sequence involves a coordinated pipeline:
1. **Container Storage Interface (CSI):** Standard gRPC specification allowing third-party storage vendors (AWS, NetApp, Dell) to write out-of-tree storage plugins for Kubernetes.
2. **Attach Phase (`AttachVolume`):** The control plane storage controller calls the cloud API to attach the virtual disk to the specific worker node VM where the Pod was scheduled.
3. **Mount Phase (`NodeStageVolume` & `NodePublishVolume`):** On the worker node, the local `kubelet` calls the CSI node driver:
   - The driver formats the raw disk with a Linux filesystem (`mkfs.ext4` or `mkfs.xfs`) if newly provisioned.
   - It executes a kernel `mount` system call to attach the device to a host directory (`/var/lib/kubelet/pods/<pod-id>/volumes/...`).
   - Finally, it uses a Linux **bind mount** to inject that host directory directly into the container's isolated mount namespace (`mnt`).

```yaml
# nfs-persistent-volume.yaml
# WHY THIS YAML: Demonstrates the administrator-provisioned PV lifecycle.
# 'capacity.storage: 50Gi': the PV advertises its size -- PVCs requesting >50Gi won't bind.
# 'accessModes: ReadWriteMany': NFS supports multiple nodes mounting simultaneously.
#   Block storage (EBS) would be ReadWriteOnce -- one node at a time only.
# 'persistentVolumeReclaimPolicy: Retain': when PVC is deleted, PV is NOT destroyed.
#   Moves to 'Released' state; admin must manually reclaim before rebinding.
# 'storageClassName: ""': empty string means only manual PVC binding (no dynamic provisioning).
apiVersion: v1
kind: PersistentVolume
metadata:
  name: static-nfs-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  nfs:
    path: /srv/nfs/shared-data
    server: 192.168.1.100
```""",
        "tech_persp": """PVs decouple storage provisioning from application deployment:
- **Multi-Attach Errors:** When a node crashes, cloud block storage (AWS EBS, GCP PD) attached to that node remains locked in the cloud hypervisor. When the pod is rescheduled to another node, it becomes stuck in `ContainerCreating` with `VolumeAttachment` timeout errors until the detachment completes.
- **Backup Limitations:** PV objects represent storage handles, not backup systems. Snapshots must be scheduled using `VolumeSnapshot` objects and CSI snapshot controllers."""
    }
}
