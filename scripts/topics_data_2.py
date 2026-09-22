#!/usr/bin/env python3
"""
scripts/make_all_topics.py
Generates diagrams for all 41 topics adhering strictly to the Style Lock.
"""

import os
import json
from build_all_diagrams import render_diagram
from topics_data import TOPICS

# We will add definitions for topics 6-41
ADDITIONAL_TOPICS = [
    # 6. kube-controller-manager
    {
        "num": 6,
        "title": "kube-controller-manager",
        "heading": "kube-controller-manager — Reconciliation Loops",
        "subtitle": "Continuous control loops: watch, compare desired vs observed, correct drift",
        "completionLabel": "Cluster state reconciled to match desired intent",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 480, "h": 400, "cls": "region-cp", "label": "Controller Reconciliation Engine"},
            {"x": 560, "y": 80, "w": 280, "h": 400, "cls": "region-neutral", "label": "API Server Boundary"}
        ],
        "nodes": [
            {"id": "nApiWatch", "type": "neutral", "x": 580, "y": 120, "w": 240, "h": 60, "title": "kube-apiserver", "sub": "watch stream of resource events"},
            {"id": "nInformer", "type": "cp", "x": 60, "y": 120, "w": 220, "h": 60, "title": "Informer / Reflector", "sub": "caches cluster objects in memory"},
            {"id": "nQueue", "type": "cp", "x": 300, "y": 120, "w": 200, "h": 60, "title": "WorkQueue", "sub": "rate-limited reconciliation keys"},
            {"id": "nCompare", "type": "cp", "x": 60, "y": 240, "w": 220, "h": 70, "title": "State Comparator", "sub": "desired vs observed check", "sub2": "detects missing replica"},
            {"id": "nWorker", "type": "cp", "x": 300, "y": 240, "w": 200, "h": 70, "title": "Reconciliation Worker", "sub": "executes idempotently", "sub2": "creates correction request"},
            {"id": "nApiMutate", "type": "neutral", "x": 580, "y": 240, "w": 240, "h": 70, "title": "State Update", "sub": "POST/PATCH to API server", "sub2": "triggers convergent action"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 580, "y1": 150, "x2": 280, "y2": 150},
            {"id": "c1", "type": "line", "x1": 280, "y1": 150, "x2": 300, "y2": 150},
            {"id": "c2", "type": "path", "d": "M400 180 L400 210 L170 210 L170 240"},
            {"id": "c3", "type": "line", "x1": 280, "y1": 275, "x2": 300, "y2": 275},
            {"id": "c4", "type": "line", "x1": 500, "y1": 275, "x2": 580, "y2": 275}
        ],
        "stages": [
            {"id": "nApiWatch", "dot": {"x": 700, "y": 150}, "label": "API server emits watch event notifying controller of resource change", "conns": []},
            {"id": "nInformer", "dot": {"x": 170, "y": 150}, "label": "Informer updates local memory cache and enqueues object key", "conns": ["c0"]},
            {"id": "nQueue", "dot": {"x": 400, "y": 150}, "label": "WorkQueue de-duplicates events and dispatches key to available worker", "conns": ["c1"]},
            {"id": "nCompare", "dot": {"x": 170, "y": 275}, "label": "Worker compares desired spec against observed cluster status", "conns": ["c2"]},
            {"id": "nWorker", "dot": {"x": 400, "y": 275}, "label": "Drift detected: worker builds mutation request to bring cluster into alignment", "conns": ["c3"]},
            {"id": "nApiMutate", "dot": {"x": 700, "y": 275}, "label": "Worker submits mutation to API server to create replacement resources", "conns": ["c4"]}
        ]
    },

    # 7. cloud-controller-manager
    {
        "num": 7,
        "title": "cloud-controller-manager",
        "heading": "cloud-controller-manager — Provider Integration",
        "subtitle": "Decoupling cloud APIs (load balancers, routes, node lifecycle) from core Kubernetes",
        "completionLabel": "Cloud infrastructure provisioned and wired to worker nodes",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 380, "h": 400, "cls": "region-cp", "label": "Kubernetes Control Plane"},
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-neutral", "label": "Cloud Provider Infrastructure"}
        ],
        "nodes": [
            {"id": "nSvc", "type": "cp", "x": 60, "y": 120, "w": 340, "h": 60, "title": "Service (type: LoadBalancer)", "sub": "user requests cloud ingress"},
            {"id": "nCcm", "type": "cp", "x": 60, "y": 230, "w": 340, "h": 70, "title": "cloud-controller-manager", "sub": "Service Controller loop", "sub2": "translates intent to cloud calls"},
            {"id": "nCloudApi", "type": "neutral", "x": 480, "y": 120, "w": 340, "h": 60, "title": "Cloud Provider API (AWS/GCP/Azure)", "sub": "provisions external load balancer"},
            {"id": "nCloudLb", "type": "neutral", "x": 480, "y": 230, "w": 340, "h": 70, "title": "Cloud Load Balancer", "sub": "public IP / DNS allocated", "sub2": "health checks target nodes"},
            {"id": "nWorker", "type": "wn", "x": 480, "y": 350, "w": 340, "h": 60, "title": "Worker Node NodePorts", "sub": "traffic routed to pod backends"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 230, "y1": 180, "x2": 230, "y2": 230},
            {"id": "c1", "type": "path", "d": "M400 265 L440 265 L440 150 L480 150"},
            {"id": "c2", "type": "line", "x1": 650, "y1": 180, "x2": 650, "y2": 230},
            {"id": "c3", "type": "line", "x1": 650, "y1": 300, "x2": 650, "y2": 350}
        ],
        "stages": [
            {"id": "nSvc", "dot": {"x": 230, "y": 150}, "label": "User applies Service with type: LoadBalancer", "conns": []},
            {"id": "nCcm", "dot": {"x": 230, "y": 265}, "label": "cloud-controller-manager detects unfulfilled load balancer service", "conns": ["c0"]},
            {"id": "nCloudApi", "dot": {"x": 650, "y": 150}, "label": "Controller issues authenticated API call to external cloud provider", "conns": ["c1"]},
            {"id": "nCloudLb", "dot": {"x": 650, "y": 265}, "label": "Cloud provider provisions hardware/software load balancer with public IP", "conns": ["c2"]},
            {"id": "nWorker", "dot": {"x": 650, "y": 380}, "label": "Load balancer registers worker NodePort backends for incoming traffic", "conns": ["c3"]}
        ]
    },

    # 8. Static Pods
    {
        "num": 8,
        "title": "Static Pods",
        "heading": "Static Pods — Node-Local Bootstrapping",
        "subtitle": "Direct kubelet lifecycle supervision from host manifests without API server mediation",
        "completionLabel": "Static pod running and registered as mirror pod",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-wn", "label": "Node Host System"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-cp", "label": "Control Plane (Visibility Only)"}
        ],
        "nodes": [
            {"id": "nDir", "type": "wn", "x": 60, "y": 120, "w": 420, "h": 60, "title": "/etc/kubernetes/manifests/", "sub": "host directory containing pod YAML files"},
            {"id": "nKubelet", "type": "wn", "x": 60, "y": 230, "w": 420, "h": 64, "title": "kubelet File Watcher", "sub": "inotify monitors directory directly", "sub2": "manages pod without scheduler"},
            {"id": "nRuntime", "type": "wn", "x": 60, "y": 350, "w": 420, "h": 60, "title": "Container Runtime (CRI)", "sub": "starts etcd / api-server container locally"},
            {"id": "nMirror", "type": "cp", "x": 560, "y": 230, "w": 260, "h": 64, "title": "Mirror Pod (API Server)", "sub": "read-only status object", "sub2": "allows kubectl get pods view"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 270, "y1": 294, "x2": 270, "y2": 350},
            {"id": "c2", "type": "line", "x1": 480, "y1": 262, "x2": 560, "y2": 262}
        ],
        "stages": [
            {"id": "nDir", "dot": {"x": 270, "y": 150}, "label": "Manifest placed directly in host filesystem (e.g. control-plane bootstrap)", "conns": []},
            {"id": "nKubelet", "dot": {"x": 270, "y": 262}, "label": "Local kubelet detects file change and parses pod specification", "conns": ["c0"]},
            {"id": "nRuntime", "dot": {"x": 270, "y": 380}, "label": "Kubelet instructs CRI runtime to create sandbox and start containers", "conns": ["c1"]},
            {"id": "nMirror", "dot": {"x": 690, "y": 262}, "label": "Kubelet creates read-only Mirror Pod on API server so cluster can observe it", "conns": ["c2"]}
        ]
    },

    # 9. kubelet
    {
        "num": 9,
        "title": "kubelet",
        "heading": "kubelet — Node Pod Lifecycle Enforcement",
        "subtitle": "Reconciling assigned PodSpecs into running sandboxes, volumes, and healthy containers",
        "completionLabel": "Container running and status conditions reported to API server",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-wn", "label": "Worker Node kubelet Architecture"}
        ],
        "nodes": [
            {"id": "nSync", "type": "wn", "x": 60, "y": 110, "w": 230, "h": 60, "title": "SyncLoop / PodWorkers", "sub": "receives pod update from API"},
            {"id": "nVol", "type": "wn", "x": 320, "y": 110, "w": 230, "h": 60, "title": "Volume Manager", "sub": "attaches & mounts disk volumes"},
            {"id": "nCri", "type": "wn", "x": 580, "y": 110, "w": 230, "h": 60, "title": "CRI (Runtime)", "sub": "pulls image, starts container"},
            {"id": "nProbe", "type": "wn", "x": 190, "y": 240, "w": 230, "h": 64, "title": "Probe Manager", "sub": "startup, liveness & readiness", "sub2": "monitors container health"},
            {"id": "nStatus", "type": "wn", "x": 450, "y": 240, "w": 230, "h": 64, "title": "Status Reporter", "sub": "reports Conditions to API", "sub2": "Ready, Initialized, ContainersReady"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 290, "y1": 140, "x2": 320, "y2": 140},
            {"id": "c1", "type": "line", "x1": 550, "y1": 140, "x2": 580, "y2": 140},
            {"id": "c2", "type": "path", "d": "M695 170 L695 200 L305 200 L305 240"},
            {"id": "c3", "type": "line", "x1": 420, "y1": 272, "x2": 450, "y2": 272}
        ],
        "stages": [
            {"id": "nSync", "dot": {"x": 175, "y": 140}, "label": "kubelet SyncLoop receives pod assignment notification", "conns": []},
            {"id": "nVol", "dot": {"x": 435, "y": 140}, "label": "Volume manager attaches requested storage and mounts host path", "conns": ["c0"]},
            {"id": "nCri", "dot": {"x": 695, "y": 140}, "label": "kubelet sends RunPodSandbox gRPC call to container runtime", "conns": ["c1"]},
            {"id": "nProbe", "dot": {"x": 305, "y": 272}, "label": "Probe manager initiates periodic health checks against container ports", "conns": ["c2"]},
            {"id": "nStatus", "dot": {"x": 565, "y": 272}, "label": "Status reporter streams condition updates back to the API server", "conns": ["c3"]}
        ]
    },

    # 10. kube-proxy
    {
        "num": 10,
        "title": "kube-proxy",
        "heading": "kube-proxy — Datapath & Virtual IPs",
        "subtitle": "Programming kernel iptables/IPVS rules to load balance ClusterIP traffic to pod endpoints",
        "completionLabel": "ClusterIP traffic translated and delivered to backend pod",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-wn", "label": "Node Network Kernel Engine"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Target Pod Endpoints"}
        ],
        "nodes": [
            {"id": "nWatch", "type": "wn", "x": 60, "y": 110, "w": 420, "h": 60, "title": "kube-proxy Daemon", "sub": "watches Services and EndpointSlices from API"},
            {"id": "nKernel", "type": "wn", "x": 60, "y": 230, "w": 420, "h": 70, "title": "Kernel Datapath (iptables / IPVS)", "sub": "programs NAT translation rules", "sub2": "10.96.0.10:80 -> Pod IP:80"},
            {"id": "nTraffic", "type": "client", "x": 60, "y": 360, "w": 420, "h": 60, "title": "Inbound Packet (ClusterIP)", "sub": "destined for virtual service IP"},
            {"id": "nPodA", "type": "wn", "x": 570, "y": 180, "w": 240, "h": 60, "title": "Pod Endpoint 1", "sub": "10.244.1.15:80 (Ready)"},
            {"id": "nPodB", "type": "wn", "x": 570, "y": 300, "w": 240, "h": 60, "title": "Pod Endpoint 2", "sub": "10.244.2.22:80 (Ready)"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 170, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 270, "y1": 360, "x2": 270, "y2": 300},
            {"id": "c2", "type": "path", "d": "M480 265 L570 210"},
            {"id": "c3", "type": "path", "d": "M480 265 L570 330"}
        ],
        "stages": [
            {"id": "nWatch", "dot": {"x": 270, "y": 140}, "label": "kube-proxy watches API server and learns of healthy backend pod endpoints", "conns": []},
            {"id": "nKernel", "dot": {"x": 270, "y": 265}, "label": "kube-proxy writes probabilistic DNAT rules into the Linux kernel", "conns": ["c0"]},
            {"id": "nTraffic", "dot": {"x": 270, "y": 390}, "label": "Client container sends TCP packet to virtual ClusterIP", "conns": ["c1"]},
            {"id": "nPodA", "dot": {"x": 690, "y": 210}, "label": "Kernel DNAT redirects packet to Pod Endpoint 1 without userspace hop", "conns": ["c2"]}
        ]
    }
]

print("Additional topics defined:", len(ADDITIONAL_TOPICS))
