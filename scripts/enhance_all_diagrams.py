#!/usr/bin/env python3
"""
scripts/enhance_all_diagrams.py

Upgrades all 46 interactive flow diagrams in diagrams/topic-*.html:
1. Adds visual step badges (.step-badge, .step-done, kbd hints) to stageLabel for clear progression tracking.
2. Replaces generic completion messages (topics 42-46) with rich, concept-specific summaries.
3. Enriches stage labels with technical depth, explaining the underlying mechanism and consequence.
"""

import os
import re
import json

DIAGRAM_DIR = "diagrams"

# Topic-specific enhanced stage labels
# Keyed by topic number: list of new labels matching the stages array length
ENHANCED_LABELS = {
    1: [
        "Client submits desired state manifest (kubectl apply) declaring intent rather than manual host commands",
        "kube-apiserver authenticates client, validates OpenAPI schema, and verifies RBAC permissions",
        "etcd commits the desired state via Raft consensus — establishing the cluster's single source of truth",
        "Controller Manager detects gap between desired (2 replicas) and actual (0) state — triggers Pod creation",
        "kube-scheduler filters nodes by compute resources & taints, scores candidates, and binds Pods to winning nodes",
        "Worker Node 1 kubelet receives assigned Pod, calls CRI runtime (containerd) to pull image and run Pod A",
        "Worker Node 2 kubelet independently starts Pod B — worker nodes execute tasks autonomously",
        "CNI overlay network assigns Pod IPs and creates routing paths so Pod A and Pod B communicate directly"
    ],
    2: [
        "Worker Node 1 experiences hardware or network failure — kubelet halts lease renewals in kube-node-lease",
        "API server marks node lease expired after node-monitor-grace-period (40s default) — node marked NotReady",
        "Node Lifecycle Controller attaches node.kubernetes.io/unreachable:NoExecute taint to initiate eviction countdown",
        "Eviction grace period (default 5m) expires: uncontactable pods marked for termination and deletion",
        "kube-scheduler filters out failed Node 1 and binds evicted pod to healthy Worker Node 2 via nodeName patch",
        "Worker Node 2 kubelet pulls image and starts replacement pod — control plane self-healing completed"
    ],
    3: [
        "Client sends HTTPS API request with client certificate or bearer token to port 6443 — the sole cluster gateway",
        "Authentication (AuthN) verifies caller identity, then Authorization (AuthZ) checks RBAC permissions",
        "Mutating admission controllers inspect request to inject default values, labels, or sidecar containers",
        "Schema validation verifies object fields conform to strict Kubernetes OpenAPI specifications",
        "Validating admission webhooks and PodSecurity evaluate constraints; violations return HTTP 400/403",
        "Validated object serialized to Protocol Buffers and committed atomically to etcd with transaction lock",
        "HTTP/2 streaming watch channels push asynchronous event notifications instantly to subscribed controllers"
    ],
    4: [
        "API server forwards linearizable write request to current etcd Raft leader over gRPC port 2379",
        "Raft Leader writes entry to Write-Ahead Log (WAL) and broadcasts AppendEntries RPCs to all followers",
        "Follower 1 appends entry to local disk WAL with synchronous fdatasync() and returns ACK to leader",
        "Follower 2 appends entry, satisfying 2-of-3 Raft quorum majority required to commit durable state",
        "Leader commits entry, applies to bbolt KV store, and returns HTTP 201 OK response to API server"
    ],
    5: [
        "kube-scheduler detects newly created pod in etcd with spec.nodeName empty — scheduling queue fires",
        "Filtering Phase (Predicates): evaluates nodes and eliminates those lacking CPU/RAM or violating taints",
        "Candidate Node A evaluated: insufficient memory and taint mismatch fail filtering — hard rejection",
        "Scoring Phase (Priorities): ranks eligible nodes using LeastAllocated, ImageLocality, and topology spread",
        "Scheduler executes atomic Binding: writes pod.spec.nodeName=Node-B directly to the API server",
        "Node B kubelet observes pod assignment via watch stream and immediately begins CRI container startup"
    ],
    6: [
        "API server emits watch event notifying controller of resource change in cluster state",
        "Informer cache receives event, updates in-memory index, and enqueues resource key into WorkQueue",
        "WorkQueue deduplicates rapid bursts of events so only a single reconciliation worker processes the key",
        "Reconciler worker compares desired spec against live cluster status: desired=3 replicas, actual=2",
        "Reconciliation gap detected: controller builds creation request to bring live state into alignment",
        "Controller submits Pod creation to API server; etcd records new pod to satisfy desired state"
    ],
    7: [
        "User creates Service manifest with type: LoadBalancer to expose application externally",
        "cloud-controller-manager (CCM) Service Controller detects unfulfilled load balancer request",
        "CCM issues authenticated API call to cloud provider (AWS/GCP/Azure) requesting external load balancer",
        "Cloud provider provisions physical/cloud load balancer with public IP and configures health checks",
        "CCM patches Service status with assigned external IP and maps traffic to node NodePort endpoints"
    ],
    8: [
        "Operator places Pod manifest YAML directly into /etc/kubernetes/manifests/ on the control-plane host",
        "Local kubelet inotify filesystem watcher detects file creation without communicating with API server",
        "Kubelet instructs local CRI runtime to create sandbox and start containers directly from manifest",
        "Kubelet creates read-only Mirror Pod on API server so cluster operators can observe static pod status"
    ],
    9: [
        "kubelet SyncLoop receives pod assignment notification from API server watch channel",
        "Volume Manager calls CSI plugin to attach storage, formats filesystem, and mounts host directory",
        "kubelet issues RunPodSandbox gRPC call to container runtime (containerd/CRI-O) to configure namespaces",
        "Probe Manager initiates periodic HTTP/TCP liveness and readiness health checks against container ports",
        "Status Reporter streams container lifecycle condition updates (Running, Ready) back to API server"
    ],
    10: [
        "kube-proxy watches API server and learns of healthy backend pod endpoints belonging to Service",
        "kube-proxy writes deterministic/probabilistic iptables or IPVS routing rules into host Linux kernel",
        "Client container transmits TCP packet targeting virtual ClusterIP address (10.96.x.x)",
        "Linux kernel Netfilter PREROUTING chain rewrites virtual ClusterIP to real Pod IP via Destination NAT (DNAT)",
        "Subsequent connections load-balance across remaining endpoints without client needing service discovery logic"
    ],
    24: [
        "Authenticated identity (User, Group, or ServiceAccount) requests an action inside target namespace",
        "RoleBinding matches subject identity to specified Role reference (roleRef) within that namespace",
        "RBAC engine computes effective permissions: subject authorized to perform actions defined in Role"
    ],
    26: [
        "Automation identity or admin initiates operations spanning multiple namespaces or cluster-scoped objects",
        "ClusterRoleBinding associates subject directly with a ClusterRole across the entire cluster scope",
        "RBAC authorizer verifies cluster-wide permissions without requiring per-namespace RoleBindings"
    ],
    35: [
        "DaemonSet controller listens to node addition, deletion, and condition events from API server",
        "Controller evaluates node selectors, affinity, and taints against DaemonSet pod template",
        "Agent pod scheduled and reconciled on Worker Node 1 with node-level host privileges",
        "Agent pod scheduled and reconciled on Worker Node 2, ensuring exact single-instance coverage",
        "When Worker 3 joins cluster, DaemonSet controller automatically detects it and spawns agent pod"
    ],
    38: [
        "ReplicationController monitors running pod instances using legacy equality-based label selectors",
        "Selector validates exact key-value match (app=legacy) without set-based operator flexibility",
        "Controller maintains fixed replica count; lacks rolling update coordination and revision tracking",
        "Modern workloads migrate to Deployments and ReplicaSets for declarative rollouts and self-healing"
    ],
    42: [
        "Container process boots inside isolated Linux namespace and initializes application dependencies",
        "startupProbe holds liveness checks at bay during slow startup, preventing premature container kills",
        "livenessProbe checks for application deadlock; triggers local container restart via kubelet if failed",
        "readinessProbe validates external dependencies (DB/cache) before allowing container into service pool",
        "kube-proxy updates endpoints: incoming traffic routed to Pod IP only while readiness status is True"
    ],
    43: [
        "Client requests discovery of individual stateful cluster members using stable DNS domain",
        "Headless Service (clusterIP: None) bypasses virtual IP proxying and returns direct pod IP records",
        "CoreDNS returns A records for individual pods (e.g. pod-0.svc.ns.svc.cluster.local)",
        "EndpointSlice controller partitions massive endpoint lists into lightweight 100-pod slices",
        "kube-proxy & ingress consume scalable EndpointSlices with topology-aware routing hints"
    ],
    44: [
        "Developer submits Pod manifest containing container securityContext declarations",
        "API server intercepts request before persisting into etcd storage",
        "Pod Security Admission plugin inspects target namespace pod-security.kubernetes.io labels",
        "Validates spec against Baseline or Restricted profile: checks non-root, seccomp, and privilege escalation",
        "Admission verdict: compliant pods admitted to etcd, while violating specs are rejected with HTTP 403"
    ],
    45: [
        "CustomResourceDefinition (CRD) registers new resource kind (e.g. PostgresCluster) with OpenAPI v3 schema",
        "User applies Custom Resource expressing desired state (replicas: 3, backupEnabled: true)",
        "API server validates custom schema, commits object to etcd, and emits watch event",
        "Custom Operator controller catches watch event and enters autonomous reconcile loop",
        "Operator provisions underlying StatefulSets, Services, and PVCs to fulfill custom application lifecycle"
    ],
    46: [
        "Developer submits Pod manifest without specifying compute requests or limits",
        "LimitRanger admission controller intercepts incoming pod creation request synchronously",
        "LimitRange automatically injects configured default CPU/memory requests and limits into container spec",
        "Plugin validates container parameters against min, max, and maxLimitRequestRatio boundaries",
        "Kubelet enforces validated compute boundaries using Linux kernel cgroups on worker nodes"
    ]
}

# Enhanced completion messages for topics with generic messages
COMPLETION_MESSAGES = {
    42: "Container lifecycle validated: startup warmup guarded, liveness monitored, and readiness traffic-gating active ✓",
    43: "High-scale discovery active: EndpointSlices chunked for efficiency and headless DNS records mapped ✓",
    44: "Security boundaries enforced: Pod Security Standards validated at admission before etcd commit ✓",
    45: "Custom controller reconciled: CRD schema verified and custom operator state loop active ✓",
    46: "Namespace constraints enforced: LimitRange default requests injected and node cgroups bounded ✓"
}

# CSS enhancement to insert for .step-badge and kbd
CSS_ENHANCEMENT = """
  .step-badge {
    display: inline-block;
    background: rgba(244, 63, 94, 0.18);
    color: #fb7185;
    border: 1px solid #be185d;
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 8px;
    letter-spacing: 0.04em;
    vertical-align: middle;
  }
  .step-badge.step-done {
    background: rgba(34, 197, 94, 0.18);
    color: #4ade80;
    border-color: #16a34a;
  }
  kbd {
    background: #190e1f;
    border: 1px solid #be185d;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 11px;
    color: #fce7f3;
  }
"""

def enhance_diagram(file_path, topic_num):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add CSS enhancement if not already present
    if ".step-badge" not in html:
        html = html.replace("</style>", CSS_ENHANCEMENT + "\n</style>", 1)

    # 2. Update completionMessage if topic is 42-46
    if topic_num in COMPLETION_MESSAGES:
        new_cm = COMPLETION_MESSAGES[topic_num]
        html = re.sub(
            r"completionMessage = '([^']+)';",
            f"completionMessage = '{new_cm}';",
            html
        )

    # 3. Update stage labels if defined
    if topic_num in ENHANCED_LABELS:
        new_labels = ENHANCED_LABELS[topic_num]
        m = re.search(r'const stages = (\[.*?\]);', html, re.S)
        if m:
            stages = json.loads(m.group(1))
            if len(stages) == len(new_labels):
                for i, lab in enumerate(new_labels):
                    stages[i]["label"] = lab
                new_stages_json = json.dumps(stages, indent=2)
                html = html[:m.start(1)] + new_stages_json + html[m.end(1):]
            else:
                print(f"Warning: topic {topic_num} stage count mismatch ({len(stages)} vs {len(new_labels)})")

    # 4. Enhance JS stageLabel update calls for visual step badges
    # Replace: document.getElementById('stageLabel').textContent = s.label;
    html = re.sub(
        r"document\.getElementById\('stageLabel'\)\.textContent\s*=\s*s\.label;",
        "document.getElementById('stageLabel').innerHTML = '<span class=\"step-badge\">Step ' + (idx + 1) + ' / ' + totalStages + '</span> ' + s.label;",
        html
    )

    # Replace: document.getElementById('stageLabel').textContent = completionMessage;
    html = re.sub(
        r"document\.getElementById\('stageLabel'\)\.textContent\s*=\s*completionMessage;",
        "document.getElementById('stageLabel').innerHTML = '<span class=\"step-badge step-done\">Complete</span> ' + completionMessage;",
        html
    )

    # Replace initial reset text with keyboard hints
    html = re.sub(
        r"document\.getElementById\('stageLabel'\)\.textContent\s*=\s*'Press play.*?;",
        "document.getElementById('stageLabel').innerHTML = 'Press play or <kbd>Next →</kbd> to trace flow (or use <kbd>→</kbd> <kbd>←</kbd> <kbd>Space</kbd>)';",
        html
    )

    # Also update the default HTML stageLabel text
    html = re.sub(
        r'<p class="stage-label" id="stageLabel">Press play to trace the flow</p>',
        '<p class="stage-label" id="stageLabel">Press play or <kbd>Next →</kbd> to trace flow (or use <kbd>→</kbd> <kbd>←</kbd> <kbd>Space</kbd>)</p>',
        html
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    enhanced_count = 0
    for i in range(1, 47):
        fpath = os.path.join(DIAGRAM_DIR, f"topic-{i:02d}.html")
        if os.path.exists(fpath):
            enhance_diagram(fpath, i)
            enhanced_count += 1
    print(f"Successfully upgraded all {enhanced_count} interactive flow diagrams in {DIAGRAM_DIR}/")

if __name__ == "__main__":
    main()
