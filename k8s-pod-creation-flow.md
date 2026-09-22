# What Happens When You Create a Pod in Kubernetes

This sequence diagram traces the full lifecycle of a `kubectl apply -f pod.yaml` (or any resource creation) request — from the client, through the control plane, down to the container actually running on a worker node.

```mermaid
sequenceDiagram
    autonumber
    participant User as kubectl (Client)
    participant API as API Server
    participant Etcd as etcd
    participant Auth as AuthN/AuthZ + Admission Controllers
    participant Sched as Scheduler
    participant Kubelet as Kubelet (Worker Node)
    participant CRI as Container Runtime (CRI)
    participant CNI as CNI Plugin
    participant CSI as CSI Plugin (if volumes)

    User->>API: POST /api/v1/pods (Pod spec, YAML/JSON)
    API->>Auth: Authenticate request (certs, tokens, OIDC)
    Auth-->>API: Authenticated

    API->>Auth: Authorize (RBAC check)
    Auth-->>API: Authorized

    API->>Auth: Run Admission Controllers<br/>(Mutating: defaults, sidecar injection)
    Auth-->>API: Mutated Pod spec

    API->>Auth: Run Admission Controllers<br/>(Validating: policies, quotas, PSP/PSA)
    Auth-->>API: Validated

    API->>Etcd: Persist Pod object (nodeName: unassigned)
    Etcd-->>API: Write ack
    API-->>User: 201 Created (Pod status: Pending)

    Note over API,Sched: Scheduler watches API Server for<br/>unscheduled Pods (nodeName == "")

    API->>Sched: Notify: new unscheduled Pod
    Sched->>Sched: Filtering phase<br/>(resource fits? taints/tolerations?<br/>node selectors? affinity rules?)
    Sched->>Sched: Scoring phase<br/>(rank feasible nodes)
    Sched->>API: Bind Pod to chosen Node (PATCH nodeName)
    API->>Etcd: Persist binding
    Etcd-->>API: Write ack

    Note over API,Kubelet: Kubelet on the target node watches<br/>API Server for Pods bound to itself

    API->>Kubelet: Notify: Pod assigned to this node
    Kubelet->>Kubelet: Admit Pod locally<br/>(resource checks, PodAdmitHandlers)

    opt Volumes required
        Kubelet->>CSI: Mount requested volumes
        CSI-->>Kubelet: Volumes attached & mounted
    end

    Kubelet->>CRI: RunPodSandbox()<br/>(create pause/infra container)
    CRI-->>Kubelet: Sandbox created (network namespace)

    Kubelet->>CNI: Set up pod networking<br/>(assign IP, configure interfaces)
    CNI-->>Kubelet: Network ready

    loop For each container in Pod spec
        Kubelet->>CRI: PullImage() if not cached
        CRI-->>Kubelet: Image ready
        Kubelet->>CRI: CreateContainer() + StartContainer()
        CRI-->>Kubelet: Container running
    end

    Kubelet->>Kubelet: Run readiness/liveness probes
    Kubelet->>API: Update Pod status (Running, container statuses)
    API->>Etcd: Persist status update
    Etcd-->>API: Write ack

    Note over User,CSI: Pod is now Running.<br/>kubectl get pods reflects live status<br/>via watch on the API Server.
```

## Key stages at a glance

1. **Submission** — `kubectl` sends the manifest to the API server as an authenticated HTTPS request.
2. **Gatekeeping** — AuthN, AuthZ (RBAC), then mutating and validating admission webhooks run before anything is written.
3. **Persistence** — The API server is the only component that talks to `etcd` directly; every other component reads/writes through it.
4. **Scheduling** — The scheduler doesn't get pushed pods; it *watches* for pods with no `nodeName` and binds one once filtering + scoring pick a node.
5. **Kubelet takeover** — Once bound, the kubelet on that node is now responsible for the pod's entire lifecycle.
6. **Sandbox → Network → Containers** — CRI creates the pause container first (holds the network namespace), CNI wires up networking, then real containers start inside that sandbox.
7. **Status loop** — The kubelet continuously reports status back through the API server, which is what `kubectl get pods -w` is watching.

## Notes for editing
- Rendered natively by GitHub, GitLab, VS Code (Markdown Preview Mermaid Support extension), Obsidian, and most static site generators (mkdocs-material, Docusaurus).
- To extend this for a specific resource (Deployment, StatefulSet, Job), add a preceding block showing the controller (Deployment controller, etc.) creating the Pod object it wraps — the pod-level flow from admission onward stays identical.
- If you want a **flowchart** (branching/decision-shape) version instead of this sequence-diagram (time-ordered) version, that's a quick variant — let me know.
