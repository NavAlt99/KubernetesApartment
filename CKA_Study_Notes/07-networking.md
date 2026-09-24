# 07. Networking
## 📑 Table of Contents
- [1. Linux Networking Fundamentals: Switching, Routing, and Gateways](#1-linux-networking-fundamentals-switching-routing-and-gateways)
  - [Interfaces & Local Network Switching](#interfaces-local-network-switching)
  - [Connecting Distinct Subnets via Routers](#connecting-distinct-subnets-via-routers)
  - [Routing Tables & Default Gateways](#routing-tables-default-gateways)
  - [Configuring a Linux Host as a Router & IP Forwarding](#configuring-a-linux-host-as-a-router-ip-forwarding)
  - [Essential Linux Networking Command Cheat Sheet](#essential-linux-networking-command-cheat-sheet)
- [2. Linux DNS Resolution Architecture](#2-linux-dns-resolution-architecture)
  - [Local Static Resolution (`/etc/hosts`)](#local-static-resolution-etchosts)
  - [Centralized Name Resolution (`/etc/resolv.conf`)](#centralized-name-resolution-etcresolvconf)
  - [Resolution Precedence Order (`/etc/nsswitch.conf`)](#resolution-precedence-order-etcnsswitchconf)
  - [DNS Domain Hierarchy & Traversal](#dns-domain-hierarchy-traversal)
  - [Search Domains & FQDNs](#search-domains-fqdns)
  - [DNS Record Types & CLI Inspection Tools](#dns-record-types-cli-inspection-tools)
- [3. CoreDNS Architecture & Host Configuration](#3-coredns-architecture-host-configuration)
  - [Standalone CoreDNS Binary & Execution](#standalone-coredns-binary-execution)
  - [Corefile Configuration & File-based Resolution](#corefile-configuration-file-based-resolution)
- [4. Linux Network Namespaces Deep Dive](#4-linux-network-namespaces-deep-dive)
  - [Network Namespace Isolation Principles](#network-namespace-isolation-principles)
  - [Creating & Inspecting Namespaces (`ip netns`)](#creating-inspecting-namespaces-ip-netns)
  - [Connecting Two Namespaces via Virtual Ethernet Pairs (`veth`)](#connecting-two-namespaces-via-virtual-ethernet-pairs-veth)
  - [Connecting Multiple Namespaces via a Linux Bridge Switch](#connecting-multiple-namespaces-via-a-linux-bridge-switch)
  - [Connecting Namespaces to Host Network & External LAN](#connecting-namespaces-to-host-network-external-lan)
  - [Outbound Connectivity via NAT / IP Masquerading](#outbound-connectivity-via-nat-ip-masquerading)
  - [Inbound Connectivity via Port Forwarding (DNAT)](#inbound-connectivity-via-port-forwarding-dnat)
- [5. Docker Container Networking](#5-docker-container-networking)
  - [Docker Network Drivers (`none`, `host`, `bridge`)](#docker-network-drivers-none-host-bridge)
  - [Default Docker Bridge Architecture (`docker0`)](#default-docker-bridge-architecture-docker0)
  - [Inspecting Container Namespaces & `veth` Pairs](#inspecting-container-namespaces-veth-pairs)
  - [Docker Port Publishing & IPTables Port Mapping](#docker-port-publishing-iptables-port-mapping)
- [6. Container Network Interface (CNI) Architecture](#6-container-network-interface-cni-architecture)
  - [Standardizing Container Networking](#standardizing-container-networking)
  - [CNI Specification Responsibilities (`ADD`, `DEL`, `CHECK`)](#cni-specification-responsibilities-add-del-check)
  - [Supported CNI Plugins](#supported-cni-plugins)
  - [CNI vs Docker Container Network Model (CNM)](#cni-vs-docker-container-network-model-cnm)
- [7. Kubernetes Cluster Networking Architecture](#7-kubernetes-cluster-networking-architecture)
  - [Node Networking Requirements](#node-networking-requirements)
  - [Kubernetes Port Matrix & Firewall Rules](#kubernetes-port-matrix-firewall-rules)
  - [CKA Exam Strategy for Network Addons](#cka-exam-strategy-for-network-addons)
- [8. Pod Networking in Kubernetes](#8-pod-networking-in-kubernetes)
  - [The Fundamental Kubernetes Pod Network Model](#the-fundamental-kubernetes-pod-network-model)
  - [Manual Multi-Node Pod Network Implementation](#manual-multi-node-pod-network-implementation)
  - [Automating Pod Networking via CNI Scripts & Kubelet](#automating-pod-networking-via-cni-scripts-kubelet)
- [9. CNI Implementation in Kubernetes](#9-cni-implementation-in-kubernetes)
  - [Kubelet CNI Startup Flags](#kubelet-cni-startup-flags)
  - [CNI Directories: Binaries & Configuration](#cni-directories-binaries-configuration)
  - [CNI Configuration File Anatomy](#cni-configuration-file-anatomy)
- [10. Weave Net CNI Plugin & Overlay Networks](#10-weave-net-cni-plugin-overlay-networks)
  - [Weave Net Architecture & Peer Mesh Topology](#weave-net-architecture-peer-mesh-topology)
  - [Packet Encapsulation & Overlay Data Path](#packet-encapsulation-overlay-data-path)
  - [Deploying Weave Net via DaemonSet](#deploying-weave-net-via-daemonset)
  - [Resolving IP Overlaps via `IPALLOC_RANGE`](#resolving-ip-overlaps-via-ipalloc_range)
- [11. IP Address Management (IPAM)](#11-ip-address-management-ipam)
  - [CNI IPAM Responsibilities](#cni-ipam-responsibilities)
  - [Host-Local vs DHCP IPAM Plugins](#host-local-vs-dhcp-ipam-plugins)
  - [Weave Net IPAM Subnet Allocation](#weave-net-ipam-subnet-allocation)
  - [Troubleshooting & Inspecting CNI/IPAM in Practice](#troubleshooting-inspecting-cniipam-in-practice)
- [12. Kubernetes Service Networking](#12-kubernetes-service-networking)
  - [Virtual Nature of Services (ClusterIP vs NodePort)](#virtual-nature-of-services-clusterip-vs-nodeport)
  - [Kube-Proxy Architecture & Watch Mechanics](#kube-proxy-architecture-watch-mechanics)
  - [Kube-Proxy Modes: Userspace, IPTables, and IPVS](#kube-proxy-modes-userspace-iptables-and-ipvs)
  - [Service Cluster IP Allocation (`--service-cluster-ip-range`)](#service-cluster-ip-allocation---service-cluster-ip-range)
  - [IPTables Rules Breakdown for Services (DNAT Chains)](#iptables-rules-breakdown-for-services-dnat-chains)
- [13. DNS Resolution in Kubernetes](#13-dns-resolution-in-kubernetes)
  - [Cluster DNS Architecture & Name Conventions](#cluster-dns-architecture-name-conventions)
  - [Service DNS Records (Same Namespace, Cross-Namespace, FQDN)](#service-dns-records-same-namespace-cross-namespace-fqdn)
  - [Pod DNS Records (Hyphenated IP Format)](#pod-dns-records-hyphenated-ip-format)
- [14. CoreDNS in Kubernetes](#14-coredns-in-kubernetes)
  - [CoreDNS Deployment Architecture](#coredns-deployment-architecture)
  - [Corefile Configuration & Kubernetes Plugin](#corefile-configuration-kubernetes-plugin)
  - [Automatic Pod DNS Configuration by Kubelet (`/etc/resolv.conf`)](#automatic-pod-dns-configuration-by-kubelet-etcresolvconf)
  - [Kubernetes DNS Verification & Troubleshooting Playbook](#kubernetes-dns-verification-troubleshooting-playbook)
- [15. Ingress Controllers & Ingress Resources](#15-ingress-controllers-ingress-resources)
  - [Why Ingress? NodePort & LoadBalancer Limitations](#why-ingress-nodeport-loadbalancer-limitations)
  - [Ingress Controller vs Ingress Resource](#ingress-controller-vs-ingress-resource)
  - [Deploying NGINX Ingress Controller (Deployment, Service, ConfigMap, RBAC)](#deploying-nginx-ingress-controller-deployment-service-configmap-rbac)
  - [Ingress Routing Strategies (Single Backend, Path-Based, Host-Based)](#ingress-routing-strategies-single-backend-path-based-host-based)
  - [Ingress API Specification Evolution (`extensions/v1beta1` vs `networking.k8s.io/v1`)](#ingress-api-specification-evolution-extensionsv1beta1-vs-networkingk8siov1)
  - [Ingress Annotations & URL Rewriting (`rewrite-target`)](#ingress-annotations-url-rewriting-rewrite-target)
  - [Production Ingress Manifest with TLS & Multiple Hosts](#production-ingress-manifest-with-tls-multiple-hosts)
- [16. Modern Kubernetes Gateway API](#16-modern-kubernetes-gateway-api)
  - [Architectural Evolution: Ingress vs Gateway API](#architectural-evolution-ingress-vs-gateway-api)
  - [Core Personas & Resources (`GatewayClass`, `Gateway`, `HTTPRoute`)](#core-personas-resources-gatewayclass-gateway-httproute)
  - [Production HTTPRoute Manifest with Canary Traffic Splitting](#production-httproute-manifest-with-canary-traffic-splitting)
- [17. Kubernetes Network Policies (`networking.k8s.io/v1`)](#17-kubernetes-network-policies-networkingk8siov1)
  - [Traffic Isolation Model (Default-Allow vs Default-Deny)](#traffic-isolation-model-default-allow-vs-default-deny)
  - [Policy Types: Ingress and Egress](#policy-types-ingress-and-egress)
  - [Rule Selectors: Pod, Namespace, and IPBlock (The AND vs OR Trap)](#rule-selectors-pod-namespace-and-ipblock-the-and-vs-or-trap)
  - [Production NetworkPolicy Manifests](#production-networkpolicy-manifests)
- [18. EndpointSlices & Headless Services](#18-endpointslices-headless-services)
  - [Headless Services (`clusterIP: None`) for Stateful Discovery](#headless-services-clusterip-none-for-stateful-discovery)
  - [Scalable Endpoint Discovery with EndpointSlices (`discovery.k8s.io/v1`)](#scalable-endpoint-discovery-with-endpointslices-discoveryk8siov1)
- [19. Network Debugging & Port-Forwarding](#19-network-debugging-port-forwarding)
  - [Rapid Microservice Debugging via `kubectl port-forward`](#rapid-microservice-debugging-via-kubectl-port-forward)
  - [Ephemeral Diagnostic Pods & Network Troubleshooting Matrix](#ephemeral-diagnostic-pods-network-troubleshooting-matrix)
---
## 1. Linux Networking Fundamentals: Switching, Routing, and Gateways

Understanding Linux networking primitives is essential for mastering Kubernetes CNI, overlay networking, and service routing.

### Interfaces & Local Network Switching
To enable communication between two physical or virtual hosts within the same Layer 2 broadcast domain, both systems connect via network interfaces to a **network switch**.

- Each host requires a physical or virtual interface (e.g., `eth0`).
- Both hosts must be assigned IP addresses within the same subnet (e.g., `192.168.1.0/24`).
- A Layer 2 switch delivers frames solely within its local broadcast domain.

![Diagram](images/image20.png)

```bash
# Display all link-layer interfaces
ip link

# View assigned IP addresses on interfaces
ip addr

# Assign an IP address to an interface (temporary until reboot)
ip addr add 192.168.1.10/24 dev eth0
```

---

### Connecting Distinct Subnets via Routers
When Host B (`192.168.1.11`) needs to communicate with Host C (`192.168.2.10`) on a separate network (`192.168.2.0/24`), a switch cannot bridge the gap.

- A **Router** bridges two or more distinct networks.
- The router possesses an interface and IP on each network (e.g., `192.168.1.1` on Network 1 and `192.168.2.1` on Network 2).

![Diagram](images/image106.png)

---

### Routing Tables & Default Gateways
Hosts do not inherently know where routers reside on the local subnet. They must be configured with explicit routes or a **gateway**.

![Diagram](images/image261.png)

```bash
# View kernel routing table
route -n
# or modern iproute2 command:
ip route show
```

Without an entry for the remote subnet, sending packets to `192.168.2.10` fails with `Network is unreachable`.

To configure Host B to reach `192.168.2.0/24` via the router interface `192.168.1.1`:

```bash
# Add a static route for a specific subnet
ip route add 192.168.2.0/24 via 192.168.1.1
```

![Diagram](images/image30.png)

#### Default Gateway (`0.0.0.0/0`)
Rather than maintaining individual routes for every external destination (e.g., Internet services like Google at `172.217.194.0`), hosts use a **Default Gateway**:

```bash
# Configure default gateway for all unknown destination traffic
ip route add default via 192.168.1.1
# Equivalent syntax:
ip route add 0.0.0.0/0 via 192.168.1.1
```

> [!NOTE]
> A `0.0.0.0` entry in the `Gateway` column of `route -n` indicates a directly connected local network where no intermediate gateway is required.

---

### Configuring a Linux Host as a Router & IP Forwarding
A Linux host with two interfaces (`eth0` on `192.168.1.0/24` and `eth1` on `192.168.2.0/24`) can function as a software router.

By default, Linux drops packets arriving on one interface destined for another for security reasons. To enable packet forwarding:

```bash
# Temporarily enable IP forwarding (lost on reboot)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Persist across system reboots
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p
```

---

### Essential Linux Networking Command Cheat Sheet

![Diagram](images/image364.png)

| Operation | Command | Persistence Location |
| :--- | :--- | :--- |
| **List interfaces** | `ip link` | `/etc/network/interfaces` or `/etc/netplan/*` |
| **View IP addresses** | `ip addr` / `ip a` | System network config |
| **Assign IP address** | `ip addr add <ip/cidr> dev <interface>` | Network config files |
| **View routing table** | `ip route show` or `route -n` | Static routing config |
| **Add static route** | `ip route add <subnet> via <gateway>` | Static routing config |
| **Set default gateway** | `ip route add default via <gateway>` | Gateway config |
| **Check IP forwarding** | `cat /proc/sys/net/ipv4/ip_forward` | `/etc/sysctl.conf` (`net.ipv4.ip_forward=1`) |

---

## 2. Linux DNS Resolution Architecture

### Local Static Resolution (`/etc/hosts`)
The simplest form of name resolution maps hostnames directly to IP addresses on each local machine:

```bash
# /etc/hosts
127.0.0.1       localhost
192.168.1.11    db
192.168.1.12    web
```

The system trusts `/etc/hosts` implicitly without validating if the remote machine's actual hostname matches the alias.

---

### Centralized Name Resolution (`/etc/resolv.conf`)
Managing `/etc/hosts` across hundreds of servers is unmaintainable. Centralized DNS servers handle name resolution globally.

Clients point to DNS servers via `/etc/resolv.conf`:

```text
# /etc/resolv.conf
nameserver 192.168.1.1
nameserver 8.8.8.8
options edns0
```

---

### Resolution Precedence Order (`/etc/nsswitch.conf`)
When an application initiates a hostname lookup, Linux consults the Name Service Switch configuration `/etc/nsswitch.conf`:

```text
# /etc/nsswitch.conf
hosts:          files dns
```

- `files`: Query `/etc/hosts` first.
- `dns`: Query nameservers listed in `/etc/resolv.conf` if local files yield no match.

---

### DNS Domain Hierarchy & Traversal
Domain names group hosts hierarchically:
- **Root Domain (`.`):** Root nameservers.
- **Top-Level Domain (TLD):** `.com`, `.org`, `.net`, `.io`.
- **Domain:** `google.com`, `example.com`.
- **Subdomain:** `maps.google.com`, `drive.google.com`.

![Diagram](images/image170.png)

---

### Search Domains & FQDNs
To refer to systems by their short hostnames rather than their Fully Qualified Domain Name (FQDN), configure search domains in `/etc/resolv.conf`:

![Diagram](images/image212.png)
![Diagram](images/image196.png)

```text
# /etc/resolv.conf
search mycompany.com prod.mycompany.com
nameserver 192.168.1.1
```

When pinging `web`, the resolver automatically queries:
1. `web.mycompany.com`
2. `web.prod.mycompany.com`

---

### DNS Record Types & CLI Inspection Tools
- **`A` Record:** Maps hostname to IPv4 address.
- **`AAAA` Record:** Maps hostname to IPv6 address.
- **`CNAME` Record:** Canonical name alias mapping one name to another.

```bash
# Query DNS server directly (bypasses /etc/hosts)
nslookup web.mycompany.com

# Detailed DNS query output including TTL and authority
dig web.mycompany.com

# Inspect local DNS resolution configuration
cat /etc/resolv.conf
cat /etc/nsswitch.conf
```

---

## 3. CoreDNS Architecture & Host Configuration

CoreDNS is a flexible, extensible DNS server written in Go and the default DNS provider in Kubernetes.

### Standalone CoreDNS Binary & Execution
CoreDNS binaries can be run directly on Linux hosts:

![Diagram](images/image75.png)

```bash
# Download and unpack CoreDNS binary
curl -LO https://github.com/coredns/coredns/releases/download/v1.10.1/coredns_1.10.1_linux_amd64.tgz
tar -xvzf coredns_1.10.1_linux_amd64.tgz

# Run CoreDNS (binds to port 53 by default)
./coredns
```

---

### Corefile Configuration & File-based Resolution
CoreDNS reads its configuration from a file named `Corefile`.

![Diagram](images/image86.png)

```text
# Corefile: Serve DNS using local /etc/hosts file
.:53 {
    hosts /etc/hosts
    log
    errors
}
```

CoreDNS uses a modular plugin chain. In Kubernetes, the `kubernetes` plugin dynamically hooks into the Kubernetes API to serve Service and Pod DNS records.

---

## 4. Linux Network Namespaces Deep Dive

Containers are isolated from the host and each other using Linux namespaces (PID, Mount, UTS, IPC, Network).

### Network Namespace Isolation Principles
A host has its own routing table, ARP cache, and physical interfaces. A **Network Namespace** (`netns`) provides an isolated network stack:
- Private virtual network interfaces (e.g., `lo`, `eth0`).
- Dedicated routing tables and default gateways.
- Independent ARP cache and iptables rule sets.

---

### Creating & Inspecting Namespaces (`ip netns`)

```bash
# Create two network namespaces
ip netns add red
ip netns add blue

# List existing network namespaces
ip netns

# Execute commands within a namespace
ip netns exec red ip link
# Equivalent shorthand:
ip -n red link
```

Inside newly created namespaces, only the `lo` loopback interface is present, and it is initially `DOWN`.

```bash
# View routing and ARP tables inside the namespace (initially empty)
ip netns exec red route
ip netns exec red arp
```

![Diagram](images/image203.png)

---

### Connecting Two Namespaces via Virtual Ethernet Pairs (`veth`)
To connect two isolated namespaces directly, Linux uses a **Virtual Ethernet Pair** (`veth`), functioning like a virtual bidirectional patch cable.

![Diagram](images/image263.png)

```bash
# 1. Create a veth pair
ip link add veth-red type veth peer name veth-blue

# 2. Attach each end to its respective namespace
ip link set veth-red netns red
ip link set veth-blue netns blue

# 3. Assign IP addresses
ip -n red addr add 192.168.15.1/24 dev veth-red
ip -n blue addr add 192.168.15.2/24 dev veth-blue

# 4. Bring interfaces UP
ip -n red link set veth-red up
ip -n blue link set veth-blue up

# 5. Verify connectivity
ip netns exec red ping 192.168.15.2
```

---

### Connecting Multiple Namespaces via a Linux Bridge Switch
Direct `veth` pairs do not scale when interconnecting three or more namespaces. A **virtual switch** is required. In Linux, this is implemented as a **Bridge interface**.

![Diagram](images/image343.png)

```bash
# 1. Create the virtual bridge interface on the host
ip link add v-net-0 type bridge
ip link set dev v-net-0 up

# 2. Clean up old point-to-point links
ip -n red link del veth-red

# 3. Create veth pairs connecting each namespace to the bridge
ip link add veth-red type veth peer name veth-red-br
ip link add veth-blue type veth peer name veth-blue-br

# 4. Attach one end to the namespace and the other end to the bridge switch
ip link set veth-red netns red
ip link set veth-red-br master v-net-0

ip link set veth-blue netns blue
ip link set veth-blue-br master v-net-0

# 5. Assign IPs to namespace endpoints and bring links UP
ip -n red addr add 192.168.15.1/24 dev veth-red
ip -n blue addr add 192.168.15.2/24 dev veth-blue

ip -n red link set veth-red up
ip link set veth-red-br up

ip -n blue link set veth-blue up
ip link set veth-blue-br up
```

All connected namespaces can now communicate across the bridge.

---

### Connecting Namespaces to Host Network & External LAN
The host cannot ping namespaces directly because the bridge `v-net-0` lacks an IP on that subnet.

1. **Assign an IP to the host bridge interface:**
   ```bash
   ip addr add 192.168.15.5/24 dev v-net-0
   ```
   Now the host (`192.168.15.5`) can communicate with `192.168.15.1` (red) and `192.168.15.2` (blue).

2. **Configure default gateway inside namespaces:**
   To allow namespaces to route traffic destined for external networks through the host:
   ```bash
   ip netns exec blue ip route add default via 192.168.15.5
   ```

---

### Outbound Connectivity via NAT / IP Masquerading
When packets from `192.168.15.2` exit the host's physical network interface (`eth0`, e.g., `192.168.1.2`), external routers cannot reply because the private subnet `192.168.15.0/24` is not routable externally.

Enable NAT (Network Address Translation) via IP Masquerading using `iptables`:

```bash
# Masquerade outbound traffic from namespace subnet
iptables -t nat -A POSTROUTING -s 192.168.15.0/24 -j MASQUERADE
```

---

### Inbound Connectivity via Port Forwarding (DNAT)
To expose a service running inside a namespace (e.g., port 80 in blue namespace `192.168.15.2`) to external clients hitting the host on port 8080:

```bash
# Add Destination NAT rule in PREROUTING chain
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.15.2:80
```

---

## 5. Docker Container Networking

### Docker Network Drivers (`none`, `host`, `bridge`)

| Driver | Description | CLI Flag |
| :--- | :--- | :--- |
| **`none`** | Complete network isolation. Container only has a loopback interface. | `docker run --network none ...` |
| **`host`** | Container binds directly to host network namespace, sharing IP and ports. | `docker run --network host ...` |
| **`bridge`** | Default mode. Attached to internal bridge network (`docker0` at `172.17.0.0/16`). | `docker run --network bridge ...` |

```bash
# List Docker networks
docker network ls
```

---

### Default Docker Bridge Architecture (`docker0`)
When Docker initializes, it creates a virtual Linux bridge named `docker0` with default gateway `172.17.0.1`.

```bash
ip link show docker0
ip addr show docker0
```

---

### Inspecting Container Namespaces & `veth` Pairs
Docker creates an independent network namespace for each container.

![Diagram](images/image341.png)

```bash
# Docker hides namespaces by default; symlink to standard netns directory to inspect:
pid=$(docker inspect -f '{{.State.Pid}}' <container-id>)
mkdir -p /var/run/netns
ln -s /proc/$pid/ns/net /var/run/netns/<container-id>

# Now visible via ip netns
ip netns
```

For every container:
1. Docker creates a `veth` pair (e.g., `veth1234` on host, `eth0` inside container).
2. One end is attached to `docker0` as a slave interface.
3. The peer is placed inside the container's network namespace and assigned an IP (e.g., `172.17.0.2/16`).

![Diagram](images/image359.png)
![Diagram](images/image262.png)

```bash
# Inspect container IP directly
docker inspect <container-name> | grep -i IPAddress
```

---

### Docker Port Publishing & IPTables Port Mapping
To expose a containerized web server to external clients:

```bash
docker run -d --name nginx -p 8080:80 nginx
```

Docker configures an `iptables` DNAT rule in the `DOCKER` chain:

```bash
# View Docker NAT rules
iptables -nvL -t nat
```

Traffic reaching host port 8080 is translated to the container's internal IP and port:
```text
Chain DOCKER (2 references)
 pkts bytes target     prot opt in     out     source      destination
    0     0 DNAT       tcp  --  !docker0 *     0.0.0.0/0   0.0.0.0/0   tcp dpt:8080 to:172.17.0.2:80
```

---
## 6. Container Network Interface (CNI) Architecture

### Standardizing Container Networking
Without standards, container runtimes (rkt, Mesos, Kubernetes) implemented disparate, proprietary networking scripts. The **Container Network Interface (CNI)** was created under the CNCF to establish a uniform specification.

---

### CNI Specification Responsibilities (`ADD`, `DEL`, `CHECK`)
CNI establishes a clear separation of concerns between container runtimes and network plugins:

#### Container Runtime Responsibilities (e.g., Kubernetes / Kubelet):
1. Create a dedicated network namespace for each container.
2. Identify which CNI network the container belongs to.
3. Invoke the CNI plugin executable with the `ADD` command upon container creation.
4. Invoke the CNI plugin executable with the `DEL` command upon container deletion.
5. Provide configuration via standard JSON format over STDIN.

#### CNI Plugin Responsibilities:
1. Support standard CLI commands: `ADD`, `DEL`, `CHECK`, and `VERSION`.
2. Accept environment variables: `CNI_COMMAND`, `CNI_CONTAINERID`, `CNI_NETNS`, `CNI_IFNAME`, `CNI_PATH`.
3. Create virtual interfaces (`veth` pairs) and connect container to network.
4. Assign IP addresses and install appropriate routes inside the container.
5. Return standardized JSON response to STDOUT.

![Diagram](images/image173.png)

---

### Supported CNI Plugins
CNI ships with core plugins categorized by function:

![Diagram](images/image5.png)

- **Main Network Plugins:** `bridge`, `ipvlan`, `macvlan`, `ptp`, `vlan`, `host-device`.
- **IPAM Plugins (IP Address Management):** `host-local`, `dhcp`, `static`.
- **Meta Plugins:** `flannel`, `tuning`, `portmap`, `firewall`, `bandwidth`.
- **Third-Party Enterprise Plugins:** Weave Net, Calico, Cilium, Flannel, VMware NSX.

---

### CNI vs Docker Container Network Model (CNM)
- **Docker uses CNM (Container Network Model):** Native Docker engine does not natively support CNI without intermediate shims.
- **Kubernetes approach with Docker:** Kubernetes creates Docker containers with `--network none`, then directly invokes CNI plugins to wire networking into the container's network namespace.

---

## 7. Kubernetes Cluster Networking Architecture

### Node Networking Requirements
Every node (control plane and worker) must satisfy core infrastructure networking requirements:
1. At least one network interface with an assigned IP address.
2. Unique hostname and unique MAC address per node.
3. Full Layer 3 reachability between all nodes in the cluster.

---

### Kubernetes Port Matrix & Firewall Rules
Ensure host firewalls, cloud security groups (AWS SG, GCP Firewall, Azure NSG), and perimeter firewalls permit the following ports:

#### Control Plane Nodes:
| Port | Protocol | Component | Purpose |
| :--- | :--- | :--- | :--- |
| **6443** | TCP | `kube-apiserver` | Kubernetes API Server (Worker nodes, kubectl, controllers) |
| **2379-2380** | TCP | `etcd` server client / peer | 2379 for client access, 2380 for peer cluster communication |
| **10250** | TCP | `kubelet` API | Kubelet control plane API (used by apiserver for logs/exec) |
| **10259** | TCP | `kube-scheduler` | Scheduler health check & metrics (formerly 10251) |
| **10257** | TCP | `kube-controller-manager` | Controller Manager health & metrics (formerly 10252) |

#### Worker Nodes:
| Port | Protocol | Component | Purpose |
| :--- | :--- | :--- | :--- |
| **10250** | TCP | `kubelet` API | Kubelet control plane API |
| **10256** | TCP | `kube-proxy` | Kube-proxy health check server |
| **30000-32767** | TCP | NodePort Services | Default port range for exposed external NodePort Services |

---

### CKA Exam Strategy for Network Addons
> [!IMPORTANT]
> - Kubernetes does not provide an out-of-the-box pod network solution. A CNI addon **must** be deployed.
> - The Kubernetes documentation remains vendor-neutral; command links to third-party repositories (Calico, Weave, Cilium) are intentionally absent from exam-allowed documentation.
> - Familiarize yourself with applying CNI manifests: `kubectl apply -f <addon-url-or-manifest>.yaml`.

---

## 8. Pod Networking in Kubernetes

### The Fundamental Kubernetes Pod Network Model
Kubernetes mandates three non-negotiable networking rules:
1. **Every Pod receives its own unique IP address.**
2. **Pods can communicate with all other Pods on any node without NAT.**
3. **Agents on a node (e.g., kubelet) can communicate with all Pods on that node.**

![Diagram](images/image338.png)

---

### Manual Multi-Node Pod Network Implementation
To understand how CNI plugins operate, consider constructing a 3-node pod network manually:
- Nodes: `192.168.1.11` (Node 1), `192.168.1.12` (Node 2), `192.168.1.13` (Node 3).

#### Step 1: Create a Dedicated Bridge Subnet per Node
Assign non-overlapping subnets to each node's local bridge (`v-net-0`):
- Node 1: `10.244.1.0/24` (Bridge IP: `10.244.1.1/24`)
- Node 2: `10.244.2.0/24` (Bridge IP: `10.244.2.1/24`)
- Node 3: `10.244.3.0/24` (Bridge IP: `10.244.3.1/24`)

![Diagram](images/image274.png)

```bash
# Executed on Node 1:
ip link add v-net-0 type bridge
ip link set dev v-net-0 up
ip addr add 10.244.1.1/24 dev v-net-0
```

#### Step 2: Wire Newly Created Pods to Local Bridge
For each container created in its network namespace:

![Diagram](images/image360.png)
![Diagram](images/image57.png)

```bash
# 1. Create veth pair
ip link add veth-pod1 type veth peer name veth-pod1-br

# 2. Attach one end to container namespace, one end to bridge
ip link set veth-pod1 netns <container-ns>
ip link set veth-pod1-br master v-net-0

# 3. Configure IP and default route inside Pod namespace
ip -n <container-ns> addr add 10.244.1.2/24 dev veth-pod1
ip -n <container-ns> link set veth-pod1 up
ip link set veth-pod1-br up
ip -n <container-ns> ip route add default via 10.244.1.1
```

#### Step 3: Establish Cross-Node Routing
At this stage, Pods communicate within their own node, but cross-node packets fail with `Network is unreachable`.

![Diagram](images/image426.png)

Configure static routing entries on each host pointing remote Pod subnets to the physical IP of the hosting node:

```bash
# On Node 1 (192.168.1.11):
ip route add 10.244.2.0/24 via 192.168.1.12
ip route add 10.244.3.0/24 via 192.168.1.13

# On Node 2 (192.168.1.12):
ip route add 10.244.1.0/24 via 192.168.1.11
ip route add 10.244.3.0/24 via 192.168.1.13

# On Node 3 (192.168.1.13):
ip route add 10.244.1.0/24 via 192.168.1.11
ip route add 10.244.2.0/24 via 192.168.1.12
```

![Diagram](images/image125.png)

With these routes in place, all Pods communicate directly across nodes without NAT, satisfying the Kubernetes pod networking contract.

---

### Automating Pod Networking via CNI Scripts & Kubelet
In production, running manual network commands is unworkable. CNI automates this entire lifecycle.

![Diagram](images/image337.png)

1. The script provides an `ADD` section (wiring `veth`, IP allocation, default gateway) and a `DEL` section (interface deletion, releasing IP).
2. The `kubelet` invokes the configured CNI plugin on every Pod creation and teardown.

![Diagram](images/image414.png)
![Diagram](images/image390.png)

---

## 9. CNI Implementation in Kubernetes

### Kubelet CNI Startup Flags
The `kubelet` is the cluster component responsible for invoking CNI plugins on worker nodes.

![Diagram](images/image132.png)
![Diagram](images/image62.png)

Inspect Kubelet's CNI configuration flags:
```bash
ps -aux | grep kubelet
# or inspect systemd unit:
systemctl status kubelet.service
```

Relevant flags:
- `--network-plugin=cni`: Configures kubelet to use CNI (deprecated/in-tree in v1.24+ where CRI runtime handles CNI).
- `--cni-bin-dir=/opt/cni/bin`: Path where executable CNI binaries reside.
- `--cni-conf-dir=/etc/cni/net.d`: Directory containing CNI JSON configuration files.

---

### CNI Directories: Binaries & Configuration

#### 1. Binary Directory (`/opt/cni/bin`)
Contains standalone executable binaries for each network and IPAM plugin:

![Diagram](images/image19.png)

```bash
ls -l /opt/cni/bin
# Outputs: bridge, dhcp, flannel, host-local, loopback, macvlan, portmap, ptp, tuning, vlan, weave-net
```

#### 2. Configuration Directory (`/etc/cni/net.d`)
Contains JSON configuration files determining which CNI plugin kubelet executes:

![Diagram](images/image1.png)

```bash
ls -l /etc/cni/net.d/
```

> [!NOTE]
> If multiple configuration files exist in `/etc/cni/net.d/`, kubelet selects the file that appears first in **alphabetical lexicographical order**.

---

### CNI Configuration File Anatomy
A typical CNI configuration file specifies the network name, type, and IPAM mechanism:

![Diagram](images/image273.png)

```json
{
  "cniVersion": "0.4.0",
  "name": "mynet",
  "type": "bridge",
  "bridge": "v-net-0",
  "isGateway": true,
  "ipMasq": true,
  "ipam": {
    "type": "host-local",
    "subnet": "10.244.1.0/24",
    "routes": [
      { "dst": "0.0.0.0/0" }
    ]
  }
}
```

- `isGateway: true`: Assigns an IP address to the bridge interface so it functions as a gateway for Pods.
- `ipMasq: true`: Configures iptables IP Masquerade NAT for traffic leaving the node.
- `ipam.type: "host-local"`: Allocates IPs locally from the specified subnet without calling an external DHCP server.

---
## 10. Weave Net CNI Plugin & Overlay Networks

In large clusters with hundreds of nodes and thousands of Pods, configuring manual static routes on every node or physical router quickly exceeds hardware routing table limits. Overlay networks solve this scalability bottleneck.

### Weave Net Architecture & Peer Mesh Topology
Weave Net deploys a lightweight routing agent as a **DaemonSet** on every node in the cluster.

![Diagram](images/image209.png)

- Each Weave peer communicates with other peers across nodes, discovering cluster topology and maintaining an internal directory of node-to-pod mappings.
- Weave creates a custom Linux bridge named `weave` on each node.
- Pods attach to the `weave` bridge and are assigned IP addresses within the overlay range.

---

### Packet Encapsulation & Overlay Data Path
When Pod A on Node 1 transmits a packet to Pod B on Node 2:

![Diagram](images/image92.png)

1. The packet arrives at the local `weave` bridge.
2. The local Weave agent intercepts the packet, notes that the target Pod IP resides on Node 2, and **encapsulates** the entire Layer 2/3 packet inside a standard UDP/TCP packet.
3. The outer packet has Node 1's physical IP as source and Node 2's physical IP as destination.
4. The physical network routes this standard UDP packet across the underlying infrastructure.
5. On Node 2, the receiving Weave agent intercepts the packet, **decapsulates** the original payload, and delivers it cleanly into Pod B's network namespace.

---

### Deploying Weave Net via DaemonSet
Once the Kubernetes control plane is running, Weave Net can be installed with a single manifest:

```bash
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '
')"
```

Inspect Weave Net pods running across all nodes:
```bash
kubectl get pods -n kube-system -l name=weave-net -o wide
```

View Weave Net operational logs:
```bash
kubectl logs -n kube-system -l name=weave-net -c weave
```

---

### Resolving IP Overlaps via `IPALLOC_RANGE`
By default, Weave Net allocates Pod IPs from the `10.32.0.0/12` CIDR block.

> [!WARNING]
> If the host node's physical network (e.g., `10.40.56.0/24`) overlaps with `10.32.0.0/12`, Weave pods will fail with `CrashLoopBackOff`, and logs will report:
> `Network 10.32.0.0/12 overlaps with existing route 10.40.56.0/24 on host`.

To fix this, override the default allocation range by passing `&env.IPALLOC_RANGE=<cidr>`:

```bash
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '
')&env.IPALLOC_RANGE=10.50.0.0/16"
```

Verify the default route inside a test pod:
```bash
kubectl run test-pod --image=busybox --restart=Never --command -- sleep 3600
kubectl exec test-pod -- ip route
# default via 10.50.0.1 dev eth0
```

---

## 11. IP Address Management (IPAM)

### CNI IPAM Responsibilities
IP Address Management (IPAM) ensures:
1. Every Pod receives a unique IP address on creation.
2. No duplicate IPs are issued across the cluster.
3. IP addresses are cleanly returned to the pool upon Pod termination.

![Diagram](images/image65.png)

CNI delegates this responsibility to dedicated IPAM plugins.

---

### Host-Local vs DHCP IPAM Plugins
Two primary IPAM mechanisms exist:

![Diagram](images/image363.png)
![Diagram](images/image427.png)

1. **`host-local` (Default):**
   - Stores allocated IP addresses locally in a flat text file on each node (typically in `/var/lib/cni/networks/<net-name>/`).
   - Highly performant; requires no external infrastructure.
2. **`dhcp`:**
   - Issues IP requests to an external DHCP server via DHCP daemon running on the host.

---

### Weave Net IPAM Subnet Allocation
Weave Net allocates the entire cluster pod network (`10.32.0.0/12` by default, ~1 million addresses) and distributes non-overlapping IP slices dynamically across all active peer nodes.

![Diagram](images/image428.png)

---

### Troubleshooting & Inspecting CNI/IPAM in Practice

#### Check CNI configuration on a node:
```bash
cat /etc/cni/net.d/*.conf*
```

Example Flannel conflist (`/etc/cni/net.d/10-flannel.conflist`):
```json
{
  "name": "cbr0",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "flannel",
      "delegate": {
        "hairpinMode": true,
        "isDefaultGateway": true
      }
    },
    {
      "type": "portmap",
      "capabilities": {
        "portMappings": true
      }
    }
  ]
}
```

#### Identify active network plugin & pod subnet in Weave:
```bash
kubectl logs -n kube-system -l name=weave-net -c weave | grep -i ipalloc-range
```

#### Find default gateway inside scheduled pods:
```bash
kubectl exec <pod-name> -- ip route
```

---

## 12. Kubernetes Service Networking

### Virtual Nature of Services (ClusterIP vs NodePort)
Pods are ephemeral; their IP addresses change every time they are restarted or rescheduled. Kubernetes **Services** provide stable IP addresses, stable DNS names, and built-in load balancing.

![Diagram](images/image77.png)

There are two primary service types:
1. **`ClusterIP` (Default):** Accessible only from within the Kubernetes cluster.
2. **`NodePort`:** Exposes the service on a dedicated port (`30000-32767`) across every node's external IP address.

![Diagram](images/image98.png)

#### Services are Purely Virtual Objects
A Service has no dedicated network namespace, no physical interface, and no listening process.

![Diagram](images/image219.png)
![Diagram](images/image221.png)

When you run `ip addr` or `netstat` on a Kubernetes host, you will **not** find the Service IP (`ClusterIP`) bound to any interface.

![Diagram](images/image247.png)

---

### Kube-Proxy Architecture & Watch Mechanics
To route traffic destined for a virtual Service IP to healthy backend Pods, Kubernetes deploys **`kube-proxy`** on every worker and control plane node (via a `DaemonSet`).

![Diagram](images/image21.png)
![Diagram](images/image198.png)

1. `kube-proxy` continuously watches the Kubernetes API Server for creation, modification, or deletion of `Service` and `Endpoints` / `EndpointSlice` objects.
2. When a Service is created, `kube-proxy` programs packet filtering rules (e.g., iptables or IPVS) on the host kernel.
3. When a client Pod sends traffic to `ClusterIP:Port`, the kernel intercepts the packet and rewrites the destination to one of the healthy backend Pod IPs (`DNAT`).

---

### Kube-Proxy Modes: Userspace, IPTables, and IPVS
The operational proxy mode is configured via `--proxy-mode` in the `kube-proxy` configuration:

![Diagram](images/image389.png)

| Proxy Mode | Implementation | Characteristics |
| :--- | :--- | :--- |
| **`userspace`** (Legacy) | Proxies connections in user space via kube-proxy process. | Slow; double context switching between user/kernel space. |
| **`iptables`** (Default) | In-kernel packet inspection via Linux netfilter/iptables rules. | Fast; sequential $O(N)$ rule evaluation; can degrade at >10,000 services. |
| **`ipvs`** | IP Virtual Server in Linux kernel; uses hash tables. | High scalability $O(1)$; supports advanced balancing (least connection, weighted). |

Inspect kube-proxy's active mode from its pod logs:
```bash
kubectl logs -n kube-system -l k8s-app=kube-proxy | grep -i "Using"
# Output: "Using iptables Proxier." or "Using ipvs Proxier."
```

---

### Service Cluster IP Allocation (`--service-cluster-ip-range`)
Service IPs are allocated from a dedicated virtual CIDR specified on `kube-apiserver`:

![Diagram](images/image310.png)

```bash
cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep service-cluster-ip-range
# Output: - --service-cluster-ip-range=10.96.0.0/12
```

> [!IMPORTANT]
> The `--service-cluster-ip-range` (e.g., `10.96.0.0/12`) must **never overlap** with the Pod network CIDR (e.g., `10.244.0.0/16`) or the physical node host network (e.g., `192.168.1.0/24`).

---

### IPTables Rules Breakdown for Services (DNAT Chains)
In iptables mode, `kube-proxy` configures custom chains in the `nat` table:

![Diagram](images/image354.png)
![Diagram](images/image23.png)

```bash
# View iptables NAT rules associated with a specific service (e.g., db-service):
iptables -L -t nat -v -n | grep <service-name>
# Example: iptables -L -t nat | grep db-service
```

#### Packet Traversal Workflow:
1. Packet enters `PREROUTING` or `OUTPUT` chain and is directed to the `KUBE-SERVICES` chain.
2. Packets matching the virtual Service IP/port jump to `KUBE-SVC-<HASH>`.
3. The `KUBE-SVC-<HASH>` chain distributes packets across backend endpoints using `statistic mode random` into endpoint chains: `KUBE-SEP-<HASH>`.
4. The `KUBE-SEP` chain applies `DNAT`, replacing the Service IP with the selected Pod IP:
   `-j DNAT --to-destination 10.244.1.2:3306`.

---
## 13. DNS Resolution in Kubernetes

### Cluster DNS Architecture & Name Conventions
Kubernetes deploys an internal DNS service to enable automated name resolution between Pods and Services across all nodes and namespaces.

![Diagram](images/image52.png)
![Diagram](images/image35.png)

---

### Service DNS Records (Same Namespace, Cross-Namespace, FQDN)
Whenever a Service is created, the cluster DNS server automatically registers an `A` record mapping the service name to its virtual `ClusterIP`.

![Diagram](images/image425.png)

#### 1. Resolution within the Same Namespace
Pods residing in the same namespace can resolve the service using simply its unqualified name:

![Diagram](images/image119.png)

```text
curl http://web-service:80
```

#### 2. Cross-Namespace Resolution
When accessing a Service located in another namespace (e.g., `apps`), append the target namespace:

![Diagram](images/image430.png)

```text
curl http://web-service.apps:80
```

#### 3. Standard Subdomain Grouping
Services are grouped under the `svc` subdomain:

![Diagram](images/image243.png)

```text
curl http://web-service.apps.svc:80
```

#### 4. Fully Qualified Domain Name (FQDN)
All cluster resources reside under the cluster root domain (default: `cluster.local`):

![Diagram](images/image97.png)

```text
curl http://web-service.apps.svc.cluster.local:80
```

---

### Pod DNS Records (Hyphenated IP Format)
By default, standard DNS `A` records are **not** created using raw Pod names because Pod names are ephemeral and change upon recreation.

Instead, Kubernetes registers DNS records for Pods by replacing dots in their IP address with hyphens:
- **Format:** `<pod-ip-with-hyphens>.<namespace>.pod.cluster.local`
- **Example:** For a Pod at IP `10.244.1.5` in namespace `default`:
  ```text
  10-244-1-5.default.pod.cluster.local
  ```

---

## 14. CoreDNS in Kubernetes

### CoreDNS Deployment Architecture
Prior to Kubernetes v1.12, `kube-dns` was the default DNS server. In modern Kubernetes, **CoreDNS** is the standard.

![Diagram](images/image16.png)
![Diagram](images/image400.png)

CoreDNS is deployed in the `kube-system` namespace as a redundant `Deployment` backed by a `ReplicaSet` (default 2 replicas):

```bash
kubectl get deployment coredns -n kube-system
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

The CoreDNS Service is named `kube-dns` and carries a static ClusterIP (commonly `10.96.0.10`):
```bash
kubectl get svc kube-dns -n kube-system
# PORT(S): 53/UDP, 53/TCP, 9153/TCP
```

---

### Corefile Configuration & Kubernetes Plugin
CoreDNS loads its configuration from `/etc/coredns/Corefile`, mounted into CoreDNS pods via a `ConfigMap` named `coredns`:

![Diagram](images/image367.png)

```bash
kubectl describe cm coredns -n kube-system
```

```text
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
```

#### Corefile Directives Breakdown:
- **`kubernetes cluster.local ...`**: Core plugin linking CoreDNS to the Kubernetes API. Serves all records under the `cluster.local` top-level domain.
  - `pods insecure`: Enables hyphenated Pod IP resolution.
- **`forward . /etc/resolv.conf`**: Forwards external queries (e.g., `google.com`) to the upstream nameserver configured in the hosting node's `/etc/resolv.conf`.
- **`cache 30`**: Caches DNS responses for 30 seconds to minimize API server load.
- **`reload`**: Dynamically reloads CoreDNS when the ConfigMap changes without pod restarts.

![Diagram](images/image61.png)

---

### Automatic Pod DNS Configuration by Kubelet (`/etc/resolv.conf`)
When Kubelet spawns a Pod, it automatically injects `/etc/resolv.conf` with the `kube-dns` Service IP and cluster search domains:

![Diagram](images/image156.png)
![Diagram](images/image304.png)

```bash
# Inspect /etc/resolv.conf inside any running Pod:
kubectl run dns-test --image=busybox --restart=Never --rm -it -- cat /etc/resolv.conf
```

Typical injected `/etc/resolv.conf`:
```text
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

![Diagram](images/image211.png)

#### Search Domains & `ndots:5`:
When a query contains fewer than 5 dots (e.g., `web-service`), the resolver sequentially appends search paths:
1. `web-service.default.svc.cluster.local` (Matches!)
2. `web-service.svc.cluster.local`
3. `web-service.cluster.local`

---

### Kubernetes DNS Verification & Troubleshooting Playbook

#### Test Service Resolution via `nslookup`:
```bash
kubectl run -it --rm test-dns --image=busybox:1.28 --restart=Never -- nslookup web-service
```

#### Test Pod Direct Resolution:
```bash
kubectl exec -it <pod-name> -- nslookup 10-244-1-4.default.pod.cluster.local
```

#### CKA Common Diagnostic Scenarios:
1. **Application fails to reach database in another namespace:**
   - Verify environment variable `DB_HOST`.
   - Update from `mysql` to `mysql.<namespace>` (e.g., `mysql.payroll`).
2. **CoreDNS pods in `CrashLoopBackOff`:**
   - Check for upstream DNS loop: `kubectl logs -n kube-system -l k8s-app=kube-dns`.
   - Verify node's `/etc/resolv.conf` does not point to `127.0.0.1` or `127.0.0.53`.

---

## 15. Ingress Controllers & Ingress Resources

### Why Ingress? NodePort & LoadBalancer Limitations
Exposing production microservices using primitive Service types presents critical architectural challenges:

![Diagram](images/image256.png)
![Diagram](images/image408.png)
![Diagram](images/image22.png)

1. **`NodePort` Drawbacks:**
   - Restricts port allocation to high-range non-standard ports (`30000-32767`).
   - Requires external load balancers/proxies to map port 80/443 to the NodePort.
2. **`LoadBalancer` Drawbacks:**
   - Every Service of type `LoadBalancer` provisions an independent, paid cloud network load balancer.
   - 20 microservices = 20 external load balancers, causing cloud cost bloat.

![Diagram](images/image237.png)
![Diagram](images/image285.png)

#### The Solution: Kubernetes Ingress
Ingress operates as an intelligent, in-cluster **Layer 7 Application Gateway**:
- Single entry point (one IP / one external load balancer).
- Host-based and path-based routing to internal `ClusterIP` services.
- Centralized TLS/SSL termination.

![Diagram](images/image431.png)
![Diagram](images/image404.png)

Exposing the Ingress Controller itself is a one-time operation via NodePort or a single Cloud LoadBalancer:

![Diagram](images/image83.png)
![Diagram](images/image158.png)

---

### Ingress Controller vs Ingress Resource
Kubernetes splits Ingress into two distinct components:

| Component | Responsibility | Description |
| :--- | :--- | :--- |
| **Ingress Controller** | **The Data Plane** | Reverse proxy daemon (NGINX, HAProxy, Envoy, Traefik). **Not built-in**; must be explicitly deployed. |
| **Ingress Resource** | **The Control Plane** | Declarative YAML defining routing rules, hostnames, paths, and TLS certificates. |

![Diagram](images/image384.png)

---

### Deploying NGINX Ingress Controller (Deployment, Service, ConfigMap, RBAC)
To deploy an Ingress Controller, configure four core building blocks:

![Diagram](images/image432.png)
![Diagram](images/image139.png)

#### 1. Deployment (`nginx-ingress-controller`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingress-controller
  namespace: ingress-space
spec:
  replicas: 1
  selector:
    matchLabels:
      name: nginx-ingress
  template:
    metadata:
      labels:
        name: nginx-ingress
    spec:
      serviceAccountName: ingress-serviceaccount
      containers:
        - name: nginx-ingress-controller
          image: registry.k8s.io/ingress-nginx/controller:v1.8.1
          args:
            - /nginx-ingress-controller
            - --configmap=$(POD_NAMESPACE)/nginx-configuration
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          ports:
            - name: http
              containerPort: 80
            - name: https
              containerPort: 443
```

#### 2. ConfigMap (`nginx-configuration`)
Stores global NGINX settings (keep-alive, SSL ciphers, timeouts) decoupled from the controller binary:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-configuration
  namespace: ingress-space
```

#### 3. NodePort Service (Exposing the Controller)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-service
  namespace: ingress-space
spec:
  type: NodePort
  selector:
    name: nginx-ingress
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: https
      port: 443
      targetPort: 443
```

#### 4. ServiceAccount & RBAC Roles
The controller requires read permissions on `Services`, `Endpoints`, `Secrets`, and `Ingresses`:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ingress-serviceaccount
  namespace: ingress-space
```

---

### Ingress Routing Strategies (Single Backend, Path-Based, Host-Based)

![Diagram](images/image282.png)

#### 1. Single Backend Ingress
Routes all traffic unconditionally to one backend service:

![Diagram](images/image217.png)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-single
spec:
  defaultBackend:
    service:
      name: wear-service
      port:
        number: 80
```

#### 2. Path-Based Routing (Single Domain, Multiple URLs)
Routes traffic based on request URI path (e.g., `/wear` vs `/watch`):

![Diagram](images/image322.png)
![Diagram](images/image108.png)
![Diagram](images/image218.png)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-path-routing
spec:
  rules:
  - http:
      paths:
      - path: /wear
        pathType: Prefix
        backend:
          service:
            name: wear-service
            port:
              number: 80
      - path: /watch
        pathType: Prefix
        backend:
          service:
            name: watch-service
            port:
              number: 80
```

#### Default Backend (404 Fallback):
If incoming traffic does not match any configured rule, it is routed to the `default-backend`:

![Diagram](images/image241.png)

#### 3. Host-Based Routing (Virtual Name-Based Hosting)
Routes traffic based on the HTTP `Host` request header (e.g., `wear.my-online-store.com` vs `watch.my-online-store.com`):

![Diagram](images/image124.png)
![Diagram](images/image375.png)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-host-routing
spec:
  rules:
  - host: wear.my-online-store.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wear-service
            port:
              number: 80
  - host: watch.my-online-store.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: watch-service
            port:
              number: 80
```

---

### Ingress API Specification Evolution (`extensions/v1beta1` vs `networking.k8s.io/v1`)
In Kubernetes v1.19+, Ingress graduated from `extensions/v1beta1` to `networking.k8s.io/v1`:

![Diagram](images/image350.png)

| Field | Old (`extensions/v1beta1`) | Modern (`networking.k8s.io/v1`) |
| :--- | :--- | :--- |
| **`apiVersion`** | `extensions/v1beta1` or `networking.k8s.io/v1beta1` | `networking.k8s.io/v1` |
| **Backend Service** | `backend.serviceName: wear-svc`<br>`backend.servicePort: 80` | `backend.service.name: wear-svc`<br>`backend.service.port.number: 80` |
| **Path Type** | Optional | **Mandatory** (`pathType: Prefix` / `Exact`) |
| **Ingress Class** | Annotation: `kubernetes.io/ingress.class` | Spec field: `spec.ingressClassName: nginx` |

#### Imperative Ingress Creation (v1.20+):
```bash
# Create Ingress imperatively with rule
kubectl create ingress ingress-test   --rule="wear.my-online-store.com/wear*=wear-service:80"
```

---

### Ingress Annotations & URL Rewriting (`rewrite-target`)
Backend applications often do not expect ingress path prefixes in their request path.
- Ingress path: `http://<host>/pay`
- Target backend service expects: `http://pay-service:8282/`

Without rewriting, the backend receives `/pay` and throws an HTTP 404 error.

Use the `nginx.ingress.kubernetes.io/rewrite-target` annotation to rewrite the path:

![Diagram](images/image344.png)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pay-ingress
  namespace: critical-space
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - http:
      paths:
      - path: /pay
        pathType: Prefix
        backend:
          service:
            name: pay-service
            port:
              number: 8282
```

---

### Production Ingress Manifest with TLS & Multiple Hosts

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: enterprise-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.example.com
    secretName: example-tls-cert
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-api-service
            port:
              number: 8080
      - path: /static
        pathType: Exact
        backend:
          service:
            name: static-assets-service
            port:
              number: 80
  - http: # Default catch-all rule
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: default-web-service
            port:
              number: 80
```

#### Create Ingress TLS Secret Imperatively:
```bash
kubectl create secret tls example-tls-cert   --cert=tls.crt   --key=tls.key   --namespace=production
```

---
## 16. Modern Kubernetes Gateway API

The Gateway API is the official next-generation evolution of service networking in Kubernetes, designed to succeed Ingress.

### Architectural Evolution: Ingress vs Gateway API

| Feature | Ingress (`networking.k8s.io/v1`) | Gateway API (`gateway.networking.k8s.io/v1`) |
| :--- | :--- | :--- |
| **Design Model** | Monolithic single resource | Role-oriented separation of concerns |
| **Portability** | Relies on vendor annotations (`nginx.ingress.kubernetes.io/*`) | Standardized core specification across all implementations |
| **Protocol Support** | HTTP, HTTPS only | HTTP, HTTPS, gRPC, TCP, UDP, TLS |
| **Traffic Splitting / Canary** | Proprietary annotations (e.g., `canary-weight`) | First-class native weighted backend references |
| **Cross-Namespace Routing** | Restricted or insecure | Native cross-namespace route attachment via `ReferenceGrant` |

---

### Core Personas & Resources (`GatewayClass`, `Gateway`, `HTTPRoute`)
Gateway API divides networking duties across three distinct organizational roles:

1. **`GatewayClass` (Infrastructure Provider):**
   - Defines the controller template (e.g., Envoy, Istio, Cilium, NGINX).
   - Cluster-scoped resource managed by platform/cloud teams.
2. **`Gateway` (Cluster Operator):**
   - Instantiates a concrete network gateway listening on specific ports with TLS certs.
   - Namespaced resource pointing to a `GatewayClass`.
3. **`HTTPRoute` / `GRPCRoute` / `TLSRoute` (Application Developer):
   - Defines routing rules, header matchers, URL redirects, and traffic splitting.
   - Attaches to parent `Gateway` via `parentRefs`.

---

### Production HTTPRoute Manifest with Canary Traffic Splitting

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: store-route
  namespace: store
spec:
  parentRefs:
    - name: prod-gateway
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /store
      backendRefs:
        - name: store-v1-service
          port: 8080
          weight: 90 # 90% production traffic
        - name: store-v2-canary
          port: 8080
          weight: 10 # 10% canary traffic
```

---

## 17. Kubernetes Network Policies (`networking.k8s.io/v1`)

### Traffic Isolation Model (Default-Allow vs Default-Deny)
By default, Kubernetes implements an **open network model**: every Pod can communicate with every other Pod across all namespaces without restriction.

A **`NetworkPolicy`** restricts traffic at Layer 3 and Layer 4 using label selectors.
- Network policies are **additive** (allow-list only; there is no explicit "deny" action).
- Once a Pod is selected by any NetworkPolicy, it becomes **isolated**; all traffic not explicitly permitted is dropped.

> [!IMPORTANT]
> Network Policies are enforced by the **CNI plugin**. Not all CNI plugins support NetworkPolicies:
> - **Supported:** Calico, Cilium, Weave Net, Kube-router, Antrea.
> - **Unsupported:** Flannel (unless paired with Canal or Calico).

---

### Policy Types: Ingress and Egress
- **`Ingress`:** Controls incoming traffic to the selected Pods.
- **`Egress`:** Controls outgoing traffic initiated from the selected Pods.

```yaml
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
    - Ingress
    - Egress
```

---

### Rule Selectors: Pod, Namespace, and IPBlock (The AND vs OR Trap)
The CKA exam frequently tests the syntax distinction between combined (AND) vs separate (OR) selector elements in the `from` / `to` lists:

#### 1. The OR Logic (Separate List Items with dashes `-`)
Matches traffic if it comes from the namespace OR from the pod label:
```yaml
ingress:
  - from:
      - namespaceSelector:
          matchLabels:
            project: internal
      - podSelector:
          matchLabels:
            app: frontend
```

#### 2. The AND Logic (Single List Item, no additional dash)
Matches traffic **only** if it comes from pods labeled `app: frontend` **residing inside** namespaces labeled `project: internal`:
```yaml
ingress:
  - from:
      - namespaceSelector:
          matchLabels:
            project: internal
        podSelector:
          matchLabels:
            app: frontend
```

---

### Production NetworkPolicy Manifests

#### 1. Default-Deny All Ingress Traffic (Zero-Trust Namespace Baseline)
Isolates all pods in the namespace, dropping all inbound traffic unless explicitly whitelisted:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: default
spec:
  podSelector: {} # Selects all pods in the namespace
  policyTypes:
    - Ingress
```

#### 2. Fine-Grained Multi-Tier Database Isolation Policy
Allows ingress to `role: db` pods on port 3306 **only** from `role: api` pods in namespace `prod`, while permitting egress only to external backup storage via `ipBlock`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-network-policy
  namespace: prod
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              environment: prod
          podSelector:
            matchLabels:
              role: api
      ports:
        - protocol: TCP
          port: 3306
  egress:
    - to:
        - ipBlock:
            cidr: 192.168.100.0/24
            except:
              - 192.168.100.10/32
      ports:
        - protocol: TCP
          port: 443
```

---

## 18. EndpointSlices & Headless Services

### Headless Services (`clusterIP: None`) for Stateful Discovery
Distributed databases (Cassandra, MongoDB, PostgreSQL replicas), message queues (Kafka), and consensus systems (ZooKeeper, etcd) require direct peer-to-peer communication rather than load-balanced proxying through a single virtual IP.

A **Headless Service** is created by explicitly specifying `clusterIP: None`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
  namespace: database
spec:
  clusterIP: None # Headless Service
  selector:
    app: postgres
  ports:
    - port: 5432
      name: postgres
```

#### DNS Behavior for Headless Services:
- CoreDNS does **not** return a single ClusterIP.
- Instead, CoreDNS returns multiple `A` records containing the direct IP addresses of all healthy backing Pods.
- When paired with a `StatefulSet`, each individual Pod receives a deterministic FQDN:
  ```text
  $(pod-name).$(service-name).$(namespace).svc.cluster.local
  # Example: postgres-0.db-headless.database.svc.cluster.local
  ```

---

### Scalable Endpoint Discovery with EndpointSlices (`discovery.k8s.io/v1`)
In earlier Kubernetes versions, all backend Pod IPs were packed into a single monolithic `Endpoints` resource. As services scaled to thousands of pods, updating this massive object triggered severe etcd serialization and network overhead.

The **`EndpointSlice`** API divides endpoints into scalable chunks (default 100 endpoints per slice).

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: db-headless-7x89q
  namespace: database
  labels:
    kubernetes.io/service-name: db-headless
addressType: IPv4
ports:
  - name: postgres
    port: 5432
    protocol: TCP
endpoints:
  - addresses:
      - "10.244.2.15"
    conditions:
      ready: true
      serving: true
      terminating: false
    zone: us-east-1a
```

#### Key Capabilities:
- **Condition Tracking:** Explicitly distinguishes `ready`, `serving`, and `terminating` states for clean zero-downtime rolling updates.
- **Topology Hints:** Enables kube-proxy to prioritize routing traffic to endpoints located within the same availability zone.

---

## 19. Network Debugging & Port-Forwarding

### Rapid Microservice Debugging via `kubectl port-forward`
When diagnosing internal services or databases that have no external NodePort or Ingress configured, establish a direct tunnel from your local machine:

```bash
# Forward local workstation port 8080 to Pod port 80:
kubectl port-forward pod/nginx-pod 8080:80

# Forward local workstation port 8443 to Service port 8282:
kubectl port-forward svc/pay-service 8443:8282 -n critical-space

# Forward to a Deployment target:
kubectl port-forward deployment/web-app 8080:80

# Bind to all network interfaces on the local workstation:
kubectl port-forward --address 0.0.0.0 svc/pay-service 8443:8282
```

---

### Ephemeral Diagnostic Pods & Network Troubleshooting Matrix

#### Deploy Ephemeral Network Testing Pod:
```bash
kubectl run net-debug --image=nicolaka/netshoot --rm -it --restart=Never -- bash
```

#### Diagnostic Decision Flowchart:

```
[Issue: Service or Pod Connectivity Failure]
   │
   ├── 1. Check DNS Resolution:
   │      nslookup <service>.<namespace>.svc.cluster.local
   │      ├── Fails? -> Check CoreDNS pods: kubectl get pods -n kube-system -l k8s-app=kube-dns
   │      └── Passes -> Check Service Endpoints
   │
   ├── 2. Check Service Endpoints:
   │      kubectl get endpoints <service-name>
   │      ├── Empty? -> Verify Pod labels match Service selector:
   │      │             kubectl get pods --show-labels
   │      └── Populated -> Test direct Pod IP connectivity
   │
   ├── 3. Test Direct Pod IP Connectivity:
   │      curl http://<pod-ip>:<targetPort>
   │      ├── Fails? -> Check Container process listening on port:
   │      │             kubectl logs <pod-name>
   │      └── Passes -> Check Kube-Proxy & NetworkPolicies
   │
   └── 4. Check NetworkPolicies & IPTables:
          kubectl get networkpolicy -A
          iptables-save | grep <service-name>
```

---
