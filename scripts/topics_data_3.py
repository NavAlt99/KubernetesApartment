#!/usr/bin/env python3
"""
scripts/build_full_suite.py
Assembles and generates the complete suite of all 41 topic diagrams.
"""

import os
import json
from build_all_diagrams import render_diagram
from topics_data import TOPICS as TOPICS_1_5
from topics_data_2 import ADDITIONAL_TOPICS as TOPICS_6_10

# Master list of topic specifications (11-41)
REMAINING_TOPICS = [
    # 11. Container Runtime & CRI
    {
        "num": 11,
        "title": "Container Runtime & CRI",
        "heading": "Container Runtime & CRI — Runtime Abstraction",
        "subtitle": "Kubelet coordinates with runtime over gRPC to manage sandboxes and containers",
        "completionLabel": "Container process launched with cgroup and namespace isolation",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-wn", "label": "Container Runtime Architecture (Worker Node)"}
        ],
        "nodes": [
            {"id": "nKubelet", "type": "wn", "x": 60, "y": 120, "w": 220, "h": 60, "title": "kubelet", "sub": "initiates RunPodSandbox"},
            {"id": "nCri", "type": "wn", "x": 330, "y": 120, "w": 220, "h": 60, "title": "CRI gRPC Interface", "sub": "/run/containerd/containerd.sock"},
            {"id": "nRuntime", "type": "wn", "x": 600, "y": 120, "w": 220, "h": 60, "title": "containerd / CRI-O", "sub": "pulls images & unpacks rootfs"},
            {"id": "nRunc", "type": "wn", "x": 330, "y": 250, "w": 220, "h": 70, "title": "OCI Runtime (runc)", "sub": "creates low-level process", "sub2": "configures namespaces"},
            {"id": "nIsolation", "type": "wn", "x": 600, "y": 250, "w": 220, "h": 70, "title": "Linux Kernel Isolation", "sub": "cgroups (CPU/RAM limits)", "sub2": "pid, net, mnt, ipc namespaces"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 150, "x2": 330, "y2": 150},
            {"id": "c1", "type": "line", "x1": 550, "y1": 150, "x2": 600, "y2": 150},
            {"id": "c2", "type": "path", "d": "M710 180 L710 215 L440 215 L440 250"},
            {"id": "c3", "type": "line", "x1": 550, "y1": 285, "x2": 600, "y2": 285}
        ],
        "stages": [
            {"id": "nKubelet", "dot": {"x": 170, "y": 150}, "label": "kubelet sends RunPodSandbox gRPC request to container runtime endpoint", "conns": []},
            {"id": "nCri", "dot": {"x": 440, "y": 150}, "label": "CRI socket decodes protobuf request into runtime actions", "conns": ["c0"]},
            {"id": "nRuntime", "dot": {"x": 710, "y": 150}, "label": "containerd pulls container image layers and unpacks root filesystem", "conns": ["c1"]},
            {"id": "nRunc", "dot": {"x": 440, "y": 285}, "label": "OCI runtime (runc) creates sandbox pause container and network namespace", "conns": ["c2"]},
            {"id": "nIsolation", "dot": {"x": 710, "y": 285}, "label": "Linux kernel enforces cgroup resource limits and namespace isolation", "conns": ["c3"]}
        ]
    },

    # 12. Sidecar Containers
    {
        "num": 12,
        "title": "Sidecar Containers",
        "heading": "Sidecar Containers — Shared Lifecycle & Volumes",
        "subtitle": "Augmenting main application with logging, proxying, and telemetry in the same pod",
        "completionLabel": "Sidecar streaming logs and telemetry to external monitoring backend",
        "width": 880, "height": 520,
        "regions": [
            {"x": 140, "y": 80, "w": 520, "h": 400, "cls": "region-wn", "label": "Pod Boundary (Shared Network & IPC)"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 60, "y": 20, "w": 180, "h": 46, "title": "Client Request", "sub": "inbound user traffic"},
            {"id": "nApp", "type": "wn", "x": 160, "y": 120, "w": 220, "h": 70, "title": "Main App Container", "sub": "handles business logic", "sub2": "writes logs to shared volume"},
            {"id": "nVol", "type": "wn", "x": 420, "y": 120, "w": 220, "h": 70, "title": "Shared emptyDir / IPC", "sub": "mounted in both containers", "sub2": "localhost communication"},
            {"id": "nSidecar", "type": "wn", "x": 290, "y": 260, "w": 220, "h": 70, "title": "Sidecar Container", "sub": "Fluentbit / Envoy proxy", "sub2": "reads log stream continuously"},
            {"id": "nBackend", "type": "neutral", "x": 690, "y": 260, "w": 170, "h": 70, "title": "Telemetry Backend", "sub": "Elastic / Prometheus", "sub2": "centralized logs"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 150, "y1": 66, "x2": 270, "y2": 120},
            {"id": "c1", "type": "line", "x1": 380, "y1": 155, "x2": 420, "y2": 155},
            {"id": "c2", "type": "line", "x1": 530, "y1": 190, "x2": 400, "y2": 260},
            {"id": "c3", "type": "line", "x1": 510, "y1": 295, "x2": 690, "y2": 295}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 150, "y": 43}, "label": "Client request reaches main application container on published port", "conns": []},
            {"id": "nApp", "dot": {"x": 270, "y": 155}, "label": "Application processes request and emits structured log entry", "conns": ["c0"]},
            {"id": "nVol", "dot": {"x": 530, "y": 155}, "label": "Shared emptyDir volume stores application log file in memory/disk", "conns": ["c1"]},
            {"id": "nSidecar", "dot": {"x": 400, "y": 295}, "label": "Sidecar container tails shared log file or intercepts localhost traffic", "conns": ["c2"]},
            {"id": "nBackend", "dot": {"x": 775, "y": 295}, "label": "Sidecar ships telemetry asynchronously to external observability store", "conns": ["c3"]}
        ]
    },

    # 13. Init Containers
    {
        "num": 13,
        "title": "Init Containers",
        "heading": "Init Containers — Sequential Pre-flight Execution",
        "subtitle": "Running setup tasks, database migrations, and dependency checks before main app starts",
        "completionLabel": "Init stages completed successfully; main application container running",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-wn", "label": "Pod Startup Lifecycle (Worker Node)"}
        ],
        "nodes": [
            {"id": "nSched", "type": "client", "x": 60, "y": 120, "w": 180, "h": 60, "title": "Pod Scheduled", "sub": "kubelet begins sandbox"},
            {"id": "nInit1", "type": "wn", "x": 280, "y": 120, "w": 240, "h": 64, "title": "Init Container 1", "sub": "Database Schema Migration", "sub2": "must exit 0 before next step"},
            {"id": "nInit2", "type": "wn", "x": 560, "y": 120, "w": 240, "h": 64, "title": "Init Container 2", "sub": "Wait for Service Ready", "sub2": "verifies network dependencies"},
            {"id": "nApp", "type": "wn", "x": 420, "y": 260, "w": 240, "h": 64, "title": "Main App Container", "sub": "web service launches", "sub2": "readiness probes start"},
            {"id": "nReady", "type": "neutral", "x": 420, "y": 380, "w": 240, "h": 50, "title": "Pod Condition: Ready", "sub": "receives cluster service traffic"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 240, "y1": 150, "x2": 280, "y2": 150},
            {"id": "c1", "type": "line", "x1": 520, "y1": 150, "x2": 560, "y2": 150},
            {"id": "c2", "type": "path", "d": "M680 184 L680 220 L540 220 L540 260"},
            {"id": "c3", "type": "line", "x1": 540, "y1": 324, "x2": 540, "y2": 380}
        ],
        "stages": [
            {"id": "nSched", "dot": {"x": 150, "y": 150}, "label": "kubelet constructs pod network namespace and sandbox", "conns": []},
            {"id": "nInit1", "dot": {"x": 400, "y": 152}, "label": "Init Container 1 executes database schema migration and terminates with code 0", "conns": ["c0"]},
            {"id": "nInit2", "dot": {"x": 680, "y": 152}, "label": "Init Container 2 probes backend endpoints until healthy then exits with code 0", "conns": ["c1"]},
            {"id": "nApp", "dot": {"x": 540, "y": 292}, "label": "All init containers succeeded; kubelet starts main application container", "conns": ["c2"]},
            {"id": "nReady", "dot": {"x": 540, "y": 405}, "label": "Readiness probe succeeds; pod joins service endpoints for live traffic", "conns": ["c3"]}
        ]
    },

    # 14. CNI (Container Network Interface)
    {
        "num": 14,
        "title": "CNI (Container Network Interface)",
        "heading": "CNI — Pod Networking & IPAM Plumbing",
        "subtitle": "Configuring virtual ethernet pairs, IP address management, and flat network routing",
        "completionLabel": "Pod network interface configured with routable IP address",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-wn", "label": "Node CNI Execution Boundary"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Pod Network Namespace"}
        ],
        "nodes": [
            {"id": "nCri", "type": "wn", "x": 60, "y": 120, "w": 420, "h": 60, "title": "containerd / CRI", "sub": "calls CNI ADD /etc/cni/net.d/"},
            {"id": "nCni", "type": "wn", "x": 60, "y": 230, "w": 200, "h": 70, "title": "CNI Plugin", "sub": "Calico / Cilium / Kindnet", "sub2": "configures routing"},
            {"id": "nIpam", "type": "wn", "x": 280, "y": 230, "w": 200, "h": 70, "title": "IPAM Module", "sub": "allocates Pod IP", "sub2": "from node subnet pool"},
            {"id": "nVeth", "type": "wn", "x": 170, "y": 360, "w": 200, "h": 60, "title": "veth Pair Creation", "sub": "veth0 (host) <-> eth0 (pod)"},
            {"id": "nPodNet", "type": "wn", "x": 570, "y": 230, "w": 240, "h": 90, "title": "Pod eth0 Interface", "sub": "IP: 10.244.1.12/24", "sub2": "default gateway set to host veth", "sub2_pad": 10}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 160, "y2": 230},
            {"id": "c1", "type": "line", "x1": 260, "y1": 265, "x2": 280, "y2": 265},
            {"id": "c2", "type": "line", "x1": 270, "y1": 300, "x2": 270, "y2": 360},
            {"id": "c3", "type": "line", "x1": 370, "y1": 390, "x2": 570, "y2": 275}
        ],
        "stages": [
            {"id": "nCri", "dot": {"x": 270, "y": 150}, "label": "CRI invokes CNI plugin binaries during pod sandbox setup", "conns": []},
            {"id": "nCni", "dot": {"x": 160, "y": 265}, "label": "CNI plugin reads configuration from /etc/cni/net.d/", "conns": ["c0"]},
            {"id": "nIpam", "dot": {"x": 380, "y": 265}, "label": "IPAM allocator leases available IP address from node podCIDR block", "conns": ["c1"]},
            {"id": "nVeth", "dot": {"x": 270, "y": 390}, "label": "Kernel creates veth tunnel linking root network to pod namespace", "conns": ["c2"]},
            {"id": "nPodNet", "dot": {"x": 690, "y": 275}, "label": "Pod eth0 assigned IP address and default route added to node routing table", "conns": ["c3"]}
        ]
    },

    # 15. CoreDNS
    {
        "num": 15,
        "title": "CoreDNS",
        "heading": "CoreDNS — Service Discovery Resolution",
        "subtitle": "Resolving Kubernetes service names to virtual IPs and individual pod endpoint IPs",
        "completionLabel": "DNS record resolved to active service IP address",
        "width": 880, "height": 520,
        "regions": [
            {"x": 340, "y": 80, "w": 500, "h": 400, "cls": "region-cp", "label": "CoreDNS Cluster Architecture"}
        ],
        "nodes": [
            {"id": "nPod", "type": "wn", "x": 60, "y": 130, "w": 220, "h": 70, "title": "Client Pod", "sub": "curl my-svc.default", "sub2": "resolv.conf nameserver: 10.96.0.10"},
            {"id": "nSvcIp", "type": "cp", "x": 380, "y": 130, "w": 220, "h": 70, "title": "kube-dns Service IP", "sub": "10.96.0.10:53 (UDP/TCP)", "sub2": "load balanced across CoreDNS pods"},
            {"id": "nDnsEngine", "type": "cp", "x": 630, "y": 130, "w": 180, "h": 70, "title": "CoreDNS Engine", "sub": "Corefile plugins", "sub2": "kubernetes, forward, cache"},
            {"id": "nApiCache", "type": "cp", "x": 510, "y": 280, "w": 240, "h": 70, "title": "Kubernetes API Cache", "sub": "in-memory service map", "sub2": "watches Services & Endpoints"},
            {"id": "nAnswer", "type": "wn", "x": 60, "y": 280, "w": 220, "h": 70, "title": "DNS A-Record Response", "sub": "my-svc -> 10.96.44.12", "sub2": "client establishes connection"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 165, "x2": 380, "y2": 165},
            {"id": "c1", "type": "line", "x1": 600, "y1": 165, "x2": 630, "y2": 165},
            {"id": "c2", "type": "line", "x1": 720, "y1": 200, "x2": 630, "y2": 280},
            {"id": "c3", "type": "line", "x1": 510, "y1": 315, "x2": 280, "y2": 315}
        ],
        "stages": [
            {"id": "nPod", "dot": {"x": 170, "y": 165}, "label": "Client Pod issues DNS query for service domain using local resolver", "conns": []},
            {"id": "nSvcIp", "dot": {"x": 490, "y": 165}, "label": "Query arrives at CoreDNS ClusterIP virtual IP address", "conns": ["c0"]},
            {"id": "nDnsEngine", "dot": {"x": 720, "y": 165}, "label": "CoreDNS plugin evaluates query domain against cluster.local zone", "conns": ["c1"]},
            {"id": "nApiCache", "dot": {"x": 630, "y": 315}, "label": "CoreDNS retrieves registered Service virtual IP from cached API watcher", "conns": ["c2"]},
            {"id": "nAnswer", "dot": {"x": 170, "y": 315}, "label": "DNS A-record returned to client; TCP connection initiated to target service", "conns": ["c3"]}
        ]
    },

    # 16. Services
    {
        "num": 16,
        "title": "Services",
        "heading": "Services — Stable Virtual Endpoints",
        "subtitle": "Abstracting ephemeral pod IP churn behind durable ClusterIP and label selectors",
        "completionLabel": "Traffic distributed across healthy matching pod replicas",
        "width": 880, "height": 520,
        "regions": [
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-wn", "label": "Backend Pod Replicas (Ephemeral)"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 60, "y": 130, "w": 180, "h": 60, "title": "Client Caller", "sub": "makes HTTP request"},
            {"id": "nSvc", "type": "cp", "x": 60, "y": 250, "w": 340, "h": 70, "title": "Service (ClusterIP)", "sub": "stable IP: 10.96.100.5", "sub2": "selector: app=web"},
            {"id": "nPod1", "type": "wn", "x": 500, "y": 110, "w": 300, "h": 60, "title": "Pod 1 (10.244.1.20)", "sub": "labels: app=web (Healthy)"},
            {"id": "nPod2", "type": "wn", "x": 500, "y": 220, "w": 300, "h": 60, "title": "Pod 2 (10.244.2.35)", "sub": "labels: app=web (Healthy)"},
            {"id": "nPod3", "type": "wn", "x": 500, "y": 330, "w": 300, "h": 60, "title": "Pod 3 (10.244.1.88)", "sub": "replacement replica after rollout"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 150, "y1": 190, "x2": 150, "y2": 250},
            {"id": "c1", "type": "path", "d": "M400 285 L450 285 L450 140 L500 140"},
            {"id": "c2", "type": "line", "x1": 400, "y1": 285, "x2": 500, "y2": 250},
            {"id": "c3", "type": "path", "d": "M400 285 L450 285 L450 360 L500 360"}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 150, "y": 160}, "label": "Client connects to stable Service virtual IP address", "conns": []},
            {"id": "nSvc", "dot": {"x": 230, "y": 285}, "label": "Service selector matches active pod labels dynamically", "conns": ["c0"]},
            {"id": "nPod1", "dot": {"x": 650, "y": 140}, "label": "Request 1 dispatched to Pod 1 via kernel load balancing", "conns": ["c1"]},
            {"id": "nPod2", "dot": {"x": 650, "y": 250}, "label": "Request 2 load-balanced to Pod 2 without client config changes", "conns": ["c2"]},
            {"id": "nPod3", "dot": {"x": 650, "y": 360}, "label": "Failed pods replaced transparently while Service IP remains unchanged", "conns": ["c3"]}
        ]
    },

    # 17. Endpoints
    {
        "num": 17,
        "title": "Endpoints",
        "heading": "Endpoints & EndpointSlices — Dynamic Backend Convergence",
        "subtitle": "Scalable tracking of active pod IPs and readiness gating for traffic delivery",
        "completionLabel": "EndpointSlice updated and synced to node datapath",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-cp", "label": "Endpoint Controller Plane"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Serving Readiness Gate"}
        ],
        "nodes": [
            {"id": "nPodState", "type": "wn", "x": 60, "y": 120, "w": 420, "h": 60, "title": "Pod Readiness Probe Pass", "sub": "pod.status.conditions ContainersReady: True"},
            {"id": "nEpCtrl", "type": "cp", "x": 60, "y": 230, "w": 420, "h": 70, "title": "EndpointSlice Controller", "sub": "batches updates to prevent API churn", "sub2": "tracks addresses & serving ports"},
            {"id": "nEpSlice", "type": "cp", "x": 60, "y": 360, "w": 420, "h": 60, "title": "EndpointSlice Object", "sub": "addresses: [10.244.1.20], ready: true"},
            {"id": "nProxyWatch", "type": "wn", "x": 570, "y": 230, "w": 240, "h": 70, "title": "Datapath Listeners", "sub": "kube-proxy & Ingress controllers", "sub2": "receive incremental updates"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 270, "y1": 300, "x2": 270, "y2": 360},
            {"id": "c2", "type": "line", "x1": 480, "y1": 265, "x2": 570, "y2": 265}
        ],
        "stages": [
            {"id": "nPodState", "dot": {"x": 270, "y": 150}, "label": "Pod passes readiness probe and reports ready condition to API server", "conns": []},
            {"id": "nEpCtrl", "dot": {"x": 270, "y": 265}, "label": "EndpointSlice controller reconciles readiness state with service selector", "conns": ["c0"]},
            {"id": "nEpSlice", "dot": {"x": 270, "y": 390}, "label": "Controller publishes updated EndpointSlice with ready address entries", "conns": ["c1"]},
            {"id": "nProxyWatch", "dot": {"x": 690, "y": 265}, "label": "kube-proxy and ingress controllers update dataplane routing instantly", "conns": ["c2"]}
        ]
    },

    # 18. Ingress
    {
        "num": 18,
        "title": "Ingress",
        "heading": "Ingress — Layer-7 HTTP Routing & TLS",
        "subtitle": "Terminating TLS and routing HTTP host/path traffic into cluster services",
        "completionLabel": "Layer 7 HTTP traffic routed directly to upstream pod backend",
        "width": 880, "height": 520,
        "regions": [
            {"x": 260, "y": 80, "w": 580, "h": 400, "cls": "region-wn", "label": "Cluster Network Ingress Pipeline"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 50, "y": 220, "w": 180, "h": 60, "title": "External Client", "sub": "https://api.example.com/v1"},
            {"id": "nIngCtrl", "type": "wn", "x": 290, "y": 120, "w": 240, "h": 70, "title": "Ingress Controller", "sub": "ingress-nginx / Traefik", "sub2": "terminates TLS certificate"},
            {"id": "nRules", "type": "wn", "x": 580, "y": 120, "w": 230, "h": 70, "title": "Routing Rules Engine", "sub": "host: api.example.com", "sub2": "path: /v1 -> svc-api"},
            {"id": "nSvc", "type": "cp", "x": 420, "y": 260, "w": 240, "h": 60, "title": "Cluster Service (svc-api)", "sub": "abstracts backend pods"},
            {"id": "nPod", "type": "wn", "x": 420, "y": 370, "w": 240, "h": 60, "title": "Upstream Pod Container", "sub": "receives plain HTTP request"}
        ],
        "connectors": [
            {"id": "c0", "type": "path", "d": "M230 250 L260 250 L260 155 L290 155"},
            {"id": "c1", "type": "line", "x1": 530, "y1": 155, "x2": 580, "y2": 155},
            {"id": "c2", "type": "line", "x1": 695, "y1": 190, "x2": 540, "y2": 260},
            {"id": "c3", "type": "line", "x1": 540, "y1": 320, "x2": 540, "y2": 370}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 140, "y": 250}, "label": "External client sends HTTPS request with SNI hostname", "conns": []},
            {"id": "nIngCtrl", "dot": {"x": 410, "y": 155}, "label": "Ingress controller accepts TCP connection on 443 and terminates TLS", "conns": ["c0"]},
            {"id": "nRules", "dot": {"x": 695, "y": 155}, "label": "Controller matches hostname and URL path against Ingress resource rules", "conns": ["c1"]},
            {"id": "nSvc", "dot": {"x": 540, "y": 290}, "label": "Request matched to upstream service svc-api and endpoints resolved", "conns": ["c2"]},
            {"id": "nPod", "dot": {"x": 540, "y": 400}, "label": "Ingress proxies HTTP request directly to target backend pod IP", "conns": ["c3"]}
        ]
    },

    # 19. NetworkPolicy
    {
        "num": 19,
        "title": "NetworkPolicy",
        "heading": "NetworkPolicy — Declarative Traffic Isolation",
        "subtitle": "Allow-based ingress/egress filtering enforced at pod network boundaries",
        "completionLabel": "Allowed traffic permitted; unauthorized packets dropped",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-wn", "label": "NetworkPolicy Dataplane Filter (eBPF / iptables)"}
        ],
        "nodes": [
            {"id": "nFront", "type": "wn", "x": 60, "y": 130, "w": 220, "h": 60, "title": "Frontend Pod", "sub": "role: frontend (Authorized)"},
            {"id": "nRogue", "type": "wn", "x": 60, "y": 270, "w": 220, "h": 60, "title": "Untrusted Pod", "sub": "role: rogue (Unauthorized)"},
            {"id": "nPolicy", "type": "wn", "x": 350, "y": 200, "w": 220, "h": 80, "title": "CNI Policy Engine", "sub": "from: [role=frontend]", "sub2": "ports: [5432 (Postgres)]"},
            {"id": "nDb", "type": "wn", "x": 630, "y": 200, "w": 180, "h": 80, "title": "Database Pod", "sub": "role: db (Protected)", "sub2": "default-deny policy active"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 160, "x2": 350, "y2": 220},
            {"id": "c1", "type": "line", "x1": 280, "y1": 300, "x2": 350, "y2": 260},
            {"id": "c2", "type": "line", "x1": 570, "y1": 240, "x2": 630, "y2": 240}
        ],
        "stages": [
            {"id": "nFront", "dot": {"x": 170, "y": 160}, "label": "Frontend Pod attempts TCP handshake on database port 5432", "conns": []},
            {"id": "nPolicy", "dot": {"x": 460, "y": 240}, "label": "CNI dataplane checks NetworkPolicy ingress whitelist for matching labels", "conns": ["c0"]},
            {"id": "nDb", "dot": {"x": 720, "y": 240}, "label": "Frontend match succeeds: packets allowed to reach Database Pod", "conns": ["c2"]},
            {"id": "nRogue", "dot": {"x": 170, "y": 300}, "label": "Untrusted Pod attempts unauthorized connection to database", "conns": []},
            {"id": "nPolicy", "dot": {"x": 460, "y": 240}, "label": "Label mismatch: CNI policy engine silently drops unauthorized packets", "conns": ["c1"]}
        ]
    },

    # 20. PersistentVolume (PV)
    {
        "num": 20,
        "title": "PersistentVolume (PV)",
        "heading": "PersistentVolume (PV) — Cluster Storage Lifecycle",
        "subtitle": "Decoupling durable physical storage from individual pod lifecycles",
        "completionLabel": "Storage bound to claim and preserved across pod restarts",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-neutral", "label": "Cluster Storage Management"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Workload Binding"}
        ],
        "nodes": [
            {"id": "nDisk", "type": "neutral", "x": 60, "y": 120, "w": 420, "h": 60, "title": "Physical Storage Infrastructure", "sub": "NFS share / Cloud SSD / Local NVMe disk"},
            {"id": "nPv", "type": "cp", "x": 60, "y": 230, "w": 420, "h": 70, "title": "PersistentVolume (Cluster-Scoped)", "sub": "capacity: 50Gi, accessModes: ReadWriteOnce", "sub2": "reclaimPolicy: Retain / Delete"},
            {"id": "nPvc", "type": "wn", "x": 570, "y": 230, "w": 240, "h": 70, "title": "Bound PVC", "sub": "requests 50Gi storage", "sub2": "status: Bound"},
            {"id": "nPod", "type": "wn", "x": 570, "y": 360, "w": 240, "h": 60, "title": "Consumer Pod", "sub": "mounts volume to /data"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 480, "y1": 265, "x2": 570, "y2": 265},
            {"id": "c2", "type": "line", "x1": 690, "y1": 300, "x2": 690, "y2": 360}
        ],
        "stages": [
            {"id": "nDisk", "dot": {"x": 270, "y": 150}, "label": "Storage administrator or driver provisions physical storage block", "conns": []},
            {"id": "nPv", "dot": {"x": 270, "y": 265}, "label": "PersistentVolume registered in cluster with capacity and access mode", "conns": ["c0"]},
            {"id": "nPvc", "dot": {"x": 690, "y": 265}, "label": "PV controller binds matching PersistentVolumeClaim to available PV", "conns": ["c1"]},
            {"id": "nPod", "dot": {"x": 690, "y": 390}, "label": "Pod mounts bound volume into container directory with persistence guaranteed", "conns": ["c2"]}
        ]
    }
]

print("Remaining batch 1 parsed:", len(REMAINING_TOPICS))
