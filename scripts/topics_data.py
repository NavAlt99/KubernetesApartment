# topics_data.py - Definitions for all 41 Kubernetes topics diagrams

TOPICS = [
    # 1. The Cluster (Why Kubernetes?)
    {
        "num": 1,
        "title": "The Cluster (Why Kubernetes?)",
        "heading": "The Cluster — Unified Control Plane",
        "subtitle": "Declarative control system — single management entity across machines",
        "completionLabel": "Cluster state synchronized across all worker nodes",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 380, "h": 400, "cls": "region-cp", "label": "Control Plane"},
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-wn", "label": "Worker Nodes"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 340, "y": 14, "w": 200, "h": 50, "title": "kubectl / Client", "sub": "declares desired state"},
            {"id": "nApi", "type": "cp", "x": 70, "y": 130, "w": 320, "h": 56, "title": "kube-apiserver", "sub": "entrypoint & cluster gateway"},
            {"id": "nEtcd", "type": "cp", "x": 70, "y": 220, "w": 150, "h": 56, "title": "etcd", "sub": "persists state"},
            {"id": "nCtrl", "type": "cp", "x": 240, "y": 220, "w": 150, "h": 56, "title": "Controllers", "sub": "reconcile drift"},
            {"id": "nSched", "type": "cp", "x": 70, "y": 310, "w": 320, "h": 56, "title": "kube-scheduler", "sub": "places workloads"},
            {"id": "nNode1", "type": "wn", "x": 490, "y": 140, "w": 320, "h": 66, "title": "Worker Node 1", "sub": "kubelet + containerd running Pod A"},
            {"id": "nNode2", "type": "wn", "x": 490, "y": 240, "w": 320, "h": 66, "title": "Worker Node 2", "sub": "kubelet + containerd running Pod B"},
            {"id": "nMesh", "type": "wn", "x": 490, "y": 340, "w": 320, "h": 54, "title": "Cluster Overlay Network", "sub": "unified pod-to-pod flat network"}
        ],
        "connectors": [
            {"id": "c0", "type": "path", "d": "M440 64 L440 96 L230 96 L230 130"},
            {"id": "c1", "type": "path", "d": "M180 186 L180 206 L145 206 L145 220"},
            {"id": "c2", "type": "path", "d": "M280 186 L280 206 L315 206 L315 220"},
            {"id": "c3", "type": "line", "x1": 230, "y1": 186, "x2": 230, "y2": 310},
            {"id": "c4", "type": "path", "d": "M390 338 L440 338 L440 173 L490 173"},
            {"id": "c5", "type": "path", "d": "M390 338 L440 338 L440 273 L490 273"},
            {"id": "c6", "type": "line", "x1": 650, "y1": 306, "x2": 650, "y2": 340}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 440, "y": 39}, "label": "Client submits multi-service application declaration to the cluster", "conns": []},
            {"id": "nApi", "dot": {"x": 230, "y": 158}, "label": "API server validates declaration and accepts workload intent", "conns": ["c0"]},
            {"id": "nEtcd", "dot": {"x": 145, "y": 248}, "label": "etcd records the desired state into consistent cluster storage", "conns": ["c1"]},
            {"id": "nCtrl", "dot": {"x": 315, "y": 248}, "label": "Controller manager monitors cluster state and triggers replica creation", "conns": ["c2"]},
            {"id": "nSched", "dot": {"x": 230, "y": 338}, "label": "Scheduler assigns workloads across available worker nodes", "conns": ["c3"]},
            {"id": "nNode1", "dot": {"x": 650, "y": 173}, "label": "Worker Node 1 pulls images and executes Pod A", "conns": ["c4"]},
            {"id": "nNode2", "dot": {"x": 650, "y": 273}, "label": "Worker Node 2 pulls images and executes Pod B", "conns": ["c5"]},
            {"id": "nMesh", "dot": {"x": 650, "y": 367}, "label": "Overlay network connects Pods across machines seamlessly", "conns": ["c6"]}
        ]
    },

    # 2. Control Plane vs. Worker Nodes
    {
        "num": 2,
        "title": "Control Plane vs. Worker Nodes",
        "heading": "Control Plane vs. Worker Nodes — Failure Isolation",
        "subtitle": "Separation of decision-making (brain) from physical workload execution (muscle)",
        "completionLabel": "Workload rescheduled to healthy worker domain",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 70, "w": 380, "h": 410, "cls": "region-cp", "label": "Control Plane (Decision Making)"},
            {"x": 460, "y": 70, "w": 380, "h": 410, "cls": "region-wn", "label": "Worker Nodes (Workload Execution)"}
        ],
        "nodes": [
            {"id": "nApi", "type": "cp", "x": 70, "y": 110, "w": 320, "h": 60, "title": "kube-apiserver", "sub": "heartbeat monitoring & cluster state"},
            {"id": "nNodeCtrl", "type": "cp", "x": 70, "y": 210, "w": 320, "h": 60, "title": "Node Lifecycle Controller", "sub": "detects node health & missed leases"},
            {"id": "nSched", "type": "cp", "x": 70, "y": 310, "w": 320, "h": 60, "title": "kube-scheduler", "sub": "re-assigns evicted pods"},
            {"id": "nWorker1", "type": "wn", "x": 490, "y": 110, "w": 320, "h": 70, "title": "Worker Node 1 (Unhealthy)", "sub": "kubelet stops reporting / machine failure"},
            {"id": "nEvict", "type": "wn", "x": 490, "y": 220, "w": 320, "h": 60, "title": "Eviction Queue", "sub": "pods marked for rescheduling"},
            {"id": "nWorker2", "type": "wn", "x": 490, "y": 320, "w": 320, "h": 70, "title": "Worker Node 2 (Healthy)", "sub": "receives new pod replica & runs container"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 490, "y1": 140, "x2": 390, "y2": 140},
            {"id": "c1", "type": "line", "x1": 230, "y1": 170, "x2": 230, "y2": 210},
            {"id": "c2", "type": "path", "d": "M390 240 L490 240"},
            {"id": "c3", "type": "line", "x1": 230, "y1": 270, "x2": 230, "y2": 310},
            {"id": "c4", "type": "path", "d": "M390 340 L490 340"}
        ],
        "stages": [
            {"id": "nWorker1", "dot": {"x": 650, "y": 145}, "label": "Worker Node 1 experiences hardware or network failure", "conns": []},
            {"id": "nApi", "dot": {"x": 230, "y": 140}, "label": "API server marks node lease expired after heartbeat timeout", "conns": ["c0"]},
            {"id": "nNodeCtrl", "dot": {"x": 230, "y": 240}, "label": "Node controller flags node NotReady and triggers pod eviction", "conns": ["c1"]},
            {"id": "nEvict", "dot": {"x": 650, "y": 250}, "label": "Workload pods queued for relocation to available capacity", "conns": ["c2"]},
            {"id": "nSched", "dot": {"x": 230, "y": 340}, "label": "Scheduler identifies healthy Worker Node 2 and binds pod", "conns": ["c3"]},
            {"id": "nWorker2", "dot": {"x": 650, "y": 355}, "label": "Worker Node 2 starts replacement pod with zero data loss", "conns": ["c4"]}
        ]
    },

    # 3. kube-apiserver
    {
        "num": 3,
        "title": "kube-apiserver",
        "heading": "kube-apiserver — Request Admission Pipeline",
        "subtitle": "Authentication, authorization, mutating & validating admission control",
        "completionLabel": "Validated object written to persistent state store",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 520, "h": 400, "cls": "region-cp", "label": "kube-apiserver Pipeline"},
            {"x": 600, "y": 80, "w": 240, "h": 400, "cls": "region-neutral", "label": "Storage Backend"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 50, "y": 20, "w": 200, "h": 46, "title": "kubectl / API Client", "sub": "HTTPS POST request"},
            {"id": "nAuth", "type": "cp", "x": 60, "y": 120, "w": 220, "h": 60, "title": "AuthN / AuthZ", "sub": "TLS cert / token + RBAC check"},
            {"id": "nMutating", "type": "cp", "x": 320, "y": 120, "w": 220, "h": 60, "title": "Mutating Webhooks", "sub": "defaults & sidecar injection"},
            {"id": "nSchema", "type": "cp", "x": 60, "y": 240, "w": 220, "h": 60, "title": "Object Schema Validation", "sub": "field syntax & required keys"},
            {"id": "nValidating", "type": "cp", "x": 320, "y": 240, "w": 220, "h": 60, "title": "Validating Webhooks", "sub": "security policy & quota gates"},
            {"id": "nWatch", "type": "cp", "x": 190, "y": 360, "w": 220, "h": 60, "title": "Watch Notification Bus", "sub": "broadcasts event to informers"},
            {"id": "nEtcd", "type": "neutral", "x": 630, "y": 220, "w": 180, "h": 90, "title": "etcd", "sub": "strongly consistent KV", "sub2": "only API server speaks to etcd"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 150, "y1": 66, "x2": 150, "y2": 120},
            {"id": "c1", "type": "line", "x1": 280, "y1": 150, "x2": 320, "y2": 150},
            {"id": "c2", "type": "path", "d": "M430 180 L430 210 L170 210 L170 240"},
            {"id": "c3", "type": "line", "x1": 280, "y1": 270, "x2": 320, "y2": 270},
            {"id": "c4", "type": "line", "x1": 540, "y1": 270, "x2": 630, "y2": 270},
            {"id": "c5", "type": "path", "d": "M630 290 L410 290 L410 360"}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 150, "y": 43}, "label": "Client issues HTTPS API request with bearer token or client certificate", "conns": []},
            {"id": "nAuth", "dot": {"x": 170, "y": 150}, "label": "API server verifies identity and authorizes RBAC permissions", "conns": ["c0"]},
            {"id": "nMutating", "dot": {"x": 430, "y": 150}, "label": "Mutating admission controllers apply default values and inject sidecars", "conns": ["c1"]},
            {"id": "nSchema", "dot": {"x": 170, "y": 270}, "label": "API server validates object against OpenAPI schema specifications", "conns": ["c2"]},
            {"id": "nValidating", "dot": {"x": 430, "y": 270}, "label": "Validating admission webhooks enforce admission governance rules", "conns": ["c3"]},
            {"id": "nEtcd", "dot": {"x": 720, "y": 265}, "label": "Accepted object is written directly to etcd with transaction lock", "conns": ["c4"]},
            {"id": "nWatch", "dot": {"x": 300, "y": 390}, "label": "Watch notification dispatched to controllers and schedulers", "conns": ["c5"]}
        ]
    },

    # 4. etcd
    {
        "num": 4,
        "title": "etcd",
        "heading": "etcd — Raft Consensus & State Persistence",
        "subtitle": "Strongly consistent distributed key-value store with leader quorum",
        "completionLabel": "Cluster state committed across Raft quorum",
        "width": 880, "height": 520,
        "regions": [
            {"x": 300, "y": 80, "w": 540, "h": 400, "cls": "region-cp", "label": "etcd Cluster (Raft Quorum)"}
        ],
        "nodes": [
            {"id": "nApi", "type": "client", "x": 60, "y": 220, "w": 200, "h": 70, "title": "kube-apiserver", "sub": "sole direct etcd client"},
            {"id": "nLeader", "type": "cp", "x": 340, "y": 130, "w": 220, "h": 76, "title": "etcd Leader", "sub": "handles write proposals", "sub2": "replicates Raft log entries"},
            {"id": "nFol1", "type": "cp", "x": 610, "y": 130, "w": 200, "h": 76, "title": "etcd Follower 1", "sub": "persists log to disk", "sub2": "acknowledges receipt"},
            {"id": "nFol2", "type": "cp", "x": 480, "y": 340, "w": 200, "h": 76, "title": "etcd Follower 2", "sub": "persists log to disk", "sub2": "quorum witness"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 260, "y1": 255, "x2": 340, "y2": 180},
            {"id": "c1", "type": "line", "x1": 560, "y1": 168, "x2": 610, "y2": 168},
            {"id": "c2", "type": "path", "d": "M450 206 L450 340 L480 340"}
        ],
        "stages": [
            {"id": "nApi", "dot": {"x": 160, "y": 255}, "label": "API server submits linearizable write request to the etcd leader", "conns": []},
            {"id": "nLeader", "dot": {"x": 450, "y": 168}, "label": "Raft Leader logs the entry and dispatches AppendEntries RPC", "conns": ["c0"]},
            {"id": "nFol1", "dot": {"x": 710, "y": 168}, "label": "Follower 1 appends entry to WAL and returns acknowledgement", "conns": ["c1"]},
            {"id": "nFol2", "dot": {"x": 580, "y": 378}, "label": "Follower 2 appends entry, satisfying 2-of-3 Raft quorum", "conns": ["c2"]},
            {"id": "nLeader", "dot": {"x": 450, "y": 168}, "label": "Leader commits entry, applies to KV store, and returns OK to API server", "conns": []}
        ]
    },

    # 5. kube-scheduler
    {
        "num": 5,
        "title": "kube-scheduler",
        "heading": "kube-scheduler — Filtering & Scoring Pipeline",
        "subtitle": "Evaluating node eligibility, constraints, affinity, and scoring candidate nodes",
        "completionLabel": "Pod binding committed to selected worker node",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-cp", "label": "kube-scheduler Engine"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Candidate Nodes"}
        ],
        "nodes": [
            {"id": "nWatch", "type": "cp", "x": 60, "y": 110, "w": 200, "h": 56, "title": "Informer Watch", "sub": "finds nodeName == \"\""},
            {"id": "nFilter", "type": "cp", "x": 60, "y": 210, "w": 200, "h": 64, "title": "Filtering (Predicates)", "sub": "checks CPU, RAM, taints", "sub2": "drops unviable nodes"},
            {"id": "nScore", "type": "cp", "x": 280, "y": 210, "w": 200, "h": 64, "title": "Scoring (Priorities)", "sub": "ranks candidate nodes", "sub2": "weights affinity & spread"},
            {"id": "nBind", "type": "cp", "x": 170, "y": 360, "w": 200, "h": 56, "title": "Binding Subresource", "sub": "PATCH pod.spec.nodeName"},
            {"id": "nNodeA", "type": "wn", "x": 570, "y": 140, "w": 240, "h": 60, "title": "Node A (Capacity Low)", "sub": "score: 42 (filtered out or ranked low)"},
            {"id": "nNodeB", "type": "wn", "x": 570, "y": 270, "w": 240, "h": 60, "title": "Node B (Optimal)", "sub": "score: 95 (best fit chosen)"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 160, "y1": 166, "x2": 160, "y2": 210},
            {"id": "c1", "type": "line", "x1": 260, "y1": 242, "x2": 280, "y2": 242},
            {"id": "c2", "type": "line", "x1": 380, "y1": 274, "x2": 270, "y2": 360},
            {"id": "c3", "type": "path", "d": "M370 388 L570 300"}
        ],
        "stages": [
            {"id": "nWatch", "dot": {"x": 160, "y": 138}, "label": "Scheduler detects newly created pod with no assigned node", "conns": []},
            {"id": "nFilter", "dot": {"x": 160, "y": 242}, "label": "Filtering phase eliminates nodes lacking resources or matching taints", "conns": ["c0"]},
            {"id": "nScore", "dot": {"x": 380, "y": 242}, "label": "Scoring phase ranks eligible nodes using topology spread and resource balance", "conns": ["c1"]},
            {"id": "nBind", "dot": {"x": 270, "y": 388}, "label": "Scheduler issues atomic binding call with chosen node to API server", "conns": ["c2"]},
            {"id": "nNodeB", "dot": {"x": 690, "y": 300}, "label": "Node B kubelet observes pod assignment and begins container startup", "conns": ["c3"]}
        ]
    }
]

print("Base topics loaded:", len(TOPICS))
