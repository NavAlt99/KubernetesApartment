# topics_data_4.py - Topics 21 to 41 definitions

FINAL_TOPICS = [
    # 21. PersistentVolumeClaim (PVC)
    {
        "num": 21,
        "title": "PersistentVolumeClaim (PVC)",
        "heading": "PersistentVolumeClaim (PVC) — Storage Requests",
        "subtitle": "Workload abstraction requesting capacity and access mode without host details",
        "completionLabel": "PVC bound to volume and attached to worker node",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-cp", "label": "Namespace Storage Binding"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-neutral", "label": "Available Volumes"}
        ],
        "nodes": [
            {"id": "nClaim", "type": "cp", "x": 60, "y": 120, "w": 420, "h": 64, "title": "PVC (Namespaced)", "sub": "requests 20Gi ReadWriteOnce", "sub2": "status: Pending -> Bound"},
            {"id": "nBinder", "type": "cp", "x": 60, "y": 240, "w": 420, "h": 64, "title": "PV Binder Controller", "sub": "evaluates volume capacity & access modes", "sub2": "matches claim to candidate volume"},
            {"id": "nPv", "type": "neutral", "x": 570, "y": 180, "w": 240, "h": 64, "title": "PersistentVolume (PV)", "sub": "20Gi cluster volume", "sub2": "claimRef set to this PVC"},
            {"id": "nNodeMount", "type": "wn", "x": 60, "y": 360, "w": 420, "h": 60, "title": "Node Volume Attachment", "sub": "Kubelet mounts volume to target pod container"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 184, "x2": 270, "y2": 240},
            {"id": "c1", "type": "line", "x1": 480, "y1": 272, "x2": 570, "y2": 212},
            {"id": "c2", "type": "line", "x1": 270, "y1": 304, "x2": 270, "y2": 360}
        ],
        "stages": [
            {"id": "nClaim", "dot": {"x": 270, "y": 152}, "label": "User submits PersistentVolumeClaim requesting 20Gi storage", "conns": []},
            {"id": "nBinder", "dot": {"x": 270, "y": 272}, "label": "PV controller scans available PersistentVolumes for best matching fit", "conns": ["c0"]},
            {"id": "nPv", "dot": {"x": 690, "y": 212}, "label": "Matching PV found: controller sets mutual binding references", "conns": ["c1"]},
            {"id": "nNodeMount", "dot": {"x": 270, "y": 390}, "label": "Storage attached to assigned worker node and mounted into pod directory", "conns": ["c2"]}
        ]
    },

    # 22. StorageClass
    {
        "num": 22,
        "title": "StorageClass",
        "heading": "StorageClass — Dynamic Volume Provisioning",
        "subtitle": "Just-in-time automated volume creation via CSI storage plugins",
        "completionLabel": "Dynamic volume provisioned on demand and bound to PVC",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 440, "h": 400, "cls": "region-cp", "label": "Kubernetes Control Plane"},
            {"x": 520, "y": 80, "w": 320, "h": 400, "cls": "region-neutral", "label": "Storage Infrastructure API"}
        ],
        "nodes": [
            {"id": "nPvc", "type": "cp", "x": 60, "y": 120, "w": 400, "h": 60, "title": "PVC (storageClassName: fast)", "sub": "requests dynamic provisioning"},
            {"id": "nSc", "type": "cp", "x": 60, "y": 230, "w": 400, "h": 70, "title": "StorageClass Definition", "sub": "provisioner: ebs.csi.aws.com", "sub2": "parameters: type=gp3, iops=3000"},
            {"id": "nCsi", "type": "neutral", "x": 550, "y": 120, "w": 260, "h": 70, "title": "CSI Provisioner Controller", "sub": "calls external storage driver", "sub2": "monitors unfulfilled claims"},
            {"id": "nCloudDisk", "type": "neutral", "x": 550, "y": 250, "w": 260, "h": 60, "title": "Storage API Disk Creation", "sub": "disk volume created in cloud / SAN"},
            {"id": "nPvCreated", "type": "cp", "x": 60, "y": 360, "w": 400, "h": 60, "title": "Automatic PV Created", "sub": "registered in cluster and bound to PVC"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 260, "y1": 180, "x2": 260, "y2": 230},
            {"id": "c1", "type": "line", "x1": 460, "y1": 265, "x2": 550, "y2": 155},
            {"id": "c2", "type": "line", "x1": 680, "y1": 190, "x2": 680, "y2": 250},
            {"id": "c3", "type": "line", "x1": 550, "y1": 280, "x2": 460, "y2": 390}
        ],
        "stages": [
            {"id": "nPvc", "dot": {"x": 260, "y": 150}, "label": "PVC created requesting StorageClass without pre-existing PV", "conns": []},
            {"id": "nSc", "dot": {"x": 260, "y": 265}, "label": "StorageClass specifies CSI provisioner and underlying disk parameters", "conns": ["c0"]},
            {"id": "nCsi", "dot": {"x": 680, "y": 155}, "label": "CSI external-provisioner intercepts claim and invokes CreateVolume RPC", "conns": ["c1"]},
            {"id": "nCloudDisk", "dot": {"x": 680, "y": 280}, "label": "Storage provider provisions physical disk volume automatically", "conns": ["c2"]},
            {"id": "nPvCreated", "dot": {"x": 260, "y": 390}, "label": "CSI creates matching PV object in cluster; PVC transitions to Bound", "conns": ["c3"]}
        ]
    },

    # 23. Role
    {
        "num": 23,
        "title": "Role",
        "heading": "Role — Namespaced API Permissions",
        "subtitle": "Granting least-privilege API verbs and resources inside a single namespace",
        "completionLabel": "API operation validated against namespace role permissions",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "RBAC Namespace Authorization Boundary"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "API Client / User", "sub": "GET /api/v1/namespaces/demo/pods"},
            {"id": "nAuthz", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 60, "title": "RBAC Authorizer", "sub": "inspects request attributes"},
            {"id": "nRole", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Namespace Role", "sub": "resources: [\"pods\"]", "sub2": "verbs: [\"get\", \"list\"]"},
            {"id": "nMatch", "type": "cp", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Rule Evaluation", "sub": "verb \"get\" matches role", "sub2": "namespace: demo matched"},
            {"id": "nDecision", "type": "neutral", "x": 190, "y": 280, "w": 230, "h": 70, "title": "Authorization Decision", "sub": "HTTP 200 OK (Allowed)", "sub2": "unauthorized verbs get 403"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280},
            {"id": "c3", "type": "line", "x1": 465, "y1": 315, "x2": 420, "y2": 315}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 170, "y": 170}, "label": "Client requests namespaced resource operation from API server", "conns": []},
            {"id": "nAuthz", "dot": {"x": 440, "y": 170}, "label": "API server RBAC authorizer evaluates subject and namespace scope", "conns": ["c0"]},
            {"id": "nRole", "dot": {"x": 710, "y": 175}, "label": "Authorizer resolves Role rules granting specific verbs on resources", "conns": ["c1"]},
            {"id": "nMatch", "dot": {"x": 580, "y": 315}, "label": "Requested verb matches rule definition in target namespace", "conns": ["c2"]},
            {"id": "nDecision", "dot": {"x": 305, "y": 315}, "label": "Access granted; API server fulfills request with HTTP 200 OK", "conns": ["c3"]}
        ]
    },

    # 24. RoleBinding
    {
        "num": 24,
        "title": "RoleBinding",
        "heading": "RoleBinding — Attaching Identities to Permissions",
        "subtitle": "Connecting subjects (users, groups, service accounts) to specific roles in a namespace",
        "completionLabel": "Role binding verified; effective namespace permissions applied",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "RBAC Binding Architecture (Namespace Scope)"}
        ],
        "nodes": [
            {"id": "nSubject", "type": "client", "x": 60, "y": 200, "w": 220, "h": 70, "title": "Subject Identity", "sub": "User: developer / SA", "sub2": "submits authenticated token"},
            {"id": "nBinding", "type": "cp", "x": 330, "y": 200, "w": 220, "h": 70, "title": "RoleBinding (Namespace)", "sub": "binds subject to roleRef", "sub2": "scoped strictly to demo-ns"},
            {"id": "nRole", "type": "cp", "x": 600, "y": 200, "w": 220, "h": 70, "title": "Target Role", "sub": "pod-reader role", "sub2": "verbs: [\"get\", \"watch\", \"list\"]"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 235, "x2": 330, "y2": 235},
            {"id": "c1", "type": "line", "x1": 550, "y1": 235, "x2": 600, "y2": 235}
        ],
        "stages": [
            {"id": "nSubject", "dot": {"x": 170, "y": 235}, "label": "Authenticated identity attempts operation inside namespace", "conns": []},
            {"id": "nBinding", "dot": {"x": 440, "y": 235}, "label": "RoleBinding maps identity to specified roleRef in namespace", "conns": ["c0"]},
            {"id": "nRole", "dot": {"x": 710, "y": 235}, "label": "Effective permissions computed: subject authorized to perform pod actions", "conns": ["c1"]}
        ]
    },

    # 25. ClusterRole
    {
        "num": 25,
        "title": "ClusterRole",
        "heading": "ClusterRole — Scoped or Global Rules",
        "subtitle": "Defining reusable permissions for non-namespaced resources or multi-namespace templates",
        "completionLabel": "ClusterRole evaluated across cluster-wide resource catalog",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Cluster-Wide RBAC Governance"}
        ],
        "nodes": [
            {"id": "nClient", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "Cluster Operator", "sub": "GET /api/v1/nodes"},
            {"id": "nAuthz", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 60, "title": "Cluster Authorizer", "sub": "checks cluster-scoped rules"},
            {"id": "nCRole", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "ClusterRole Definition", "sub": "resources: [\"nodes\", \"pv\"]", "sub2": "verbs: [\"get\", \"list\", \"watch\"]"},
            {"id": "nScope", "type": "cp", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Cluster-Scoped Match", "sub": "non-namespaced resource", "sub2": "valid across entire cluster"},
            {"id": "nSuccess", "type": "neutral", "x": 190, "y": 280, "w": 230, "h": 70, "title": "Operation Permitted", "sub": "returns cluster node listing", "sub2": "governs all failure domains"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280},
            {"id": "c3", "type": "line", "x1": 465, "y1": 315, "x2": 420, "y2": 315}
        ],
        "stages": [
            {"id": "nClient", "dot": {"x": 170, "y": 170}, "label": "Client attempts access to cluster-scoped resources (Nodes, Storage)", "conns": []},
            {"id": "nAuthz", "dot": {"x": 440, "y": 170}, "label": "RBAC authorizer determines request targets non-namespaced API group", "conns": ["c0"]},
            {"id": "nCRole", "dot": {"x": 710, "y": 175}, "label": "ClusterRole rules evaluated for resource and verb match", "conns": ["c1"]},
            {"id": "nScope", "dot": {"x": 580, "y": 315}, "label": "Cluster-level grant verified without requiring namespace context", "conns": ["c2"]},
            {"id": "nSuccess", "dot": {"x": 305, "y": 315}, "label": "Client successfully retrieves cluster infrastructure data", "conns": ["c3"]}
        ]
    },

    # 26. ClusterRoleBinding
    {
        "num": 26,
        "title": "ClusterRoleBinding",
        "heading": "ClusterRoleBinding — Global Grants",
        "subtitle": "Binding high-impact cluster permissions to platform automation and administrators",
        "completionLabel": "Cluster-wide grant active across every namespace",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Global Authorization Pipeline"}
        ],
        "nodes": [
            {"id": "nSubject", "type": "client", "x": 60, "y": 200, "w": 220, "h": 70, "title": "Platform Controller / Admin", "sub": "system:serviceaccount", "sub2": "cluster-admin identity"},
            {"id": "nBinding", "type": "cp", "x": 330, "y": 200, "w": 220, "h": 70, "title": "ClusterRoleBinding", "sub": "global binding scope", "sub2": "no namespace boundary"},
            {"id": "nCRole", "type": "cp", "x": 600, "y": 200, "w": 220, "h": 70, "title": "ClusterRole (admin)", "sub": "resources: [\"*\"], verbs: [\"*\"]", "sub2": "authorizes all cluster actions"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 235, "x2": 330, "y2": 235},
            {"id": "c1", "type": "line", "x1": 550, "y1": 235, "x2": 600, "y2": 235}
        ],
        "stages": [
            {"id": "nSubject", "dot": {"x": 170, "y": 235}, "label": "Automation identity executes operations across multiple namespaces", "conns": []},
            {"id": "nBinding", "dot": {"x": 440, "y": 235}, "label": "ClusterRoleBinding grants subject permissions cluster-wide", "conns": ["c0"]},
            {"id": "nCRole", "dot": {"x": 710, "y": 235}, "label": "Subject authorized to reconcile objects across all cluster boundaries", "conns": ["c1"]}
        ]
    },

    # 27. ServiceAccount
    {
        "num": 27,
        "title": "ServiceAccount",
        "heading": "ServiceAccount — Workload Identity & Projected Tokens",
        "subtitle": "Projecting time-bound, audience-scoped JWT tokens into pods for API authentication",
        "completionLabel": "Workload authenticated and authorized as ServiceAccount",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 380, "h": 400, "cls": "region-wn", "label": "Pod Filesystem on Worker Node"},
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-cp", "label": "API Server Authentication"}
        ],
        "nodes": [
            {"id": "nToken", "type": "wn", "x": 60, "y": 120, "w": 340, "h": 70, "title": "Projected Token Volume", "sub": "/var/run/secrets/kubernetes.io/", "sub2": "time-bound token, refreshed by kubelet"},
            {"id": "nApp", "type": "wn", "x": 60, "y": 250, "w": 340, "h": 70, "title": "Application Container", "sub": "reads JWT bearer token", "sub2": "attaches Authorization header"},
            {"id": "nApi", "type": "cp", "x": 480, "y": 120, "w": 340, "h": 70, "title": "API TokenReview / AuthN", "sub": "validates cryptographically", "sub2": "verifies audience & expiration"},
            {"id": "nRbac", "type": "cp", "x": 480, "y": 250, "w": 340, "h": 70, "title": "RBAC Evaluation", "sub": "maps token to ServiceAccount identity", "sub2": "enforces role permissions"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 230, "y1": 190, "x2": 230, "y2": 250},
            {"id": "c1", "type": "line", "x1": 400, "y1": 285, "x2": 480, "y2": 155},
            {"id": "c2", "type": "line", "x1": 650, "y1": 190, "x2": 650, "y2": 250}
        ],
        "stages": [
            {"id": "nToken", "dot": {"x": 230, "y": 155}, "label": "kubelet projects short-lived OIDC signed token into container volume", "conns": []},
            {"id": "nApp", "dot": {"x": 230, "y": 285}, "label": "Application reads token and makes API call with Bearer authorization header", "conns": ["c0"]},
            {"id": "nApi", "dot": {"x": 650, "y": 155}, "label": "API server authenticates token signature and checks token expiration", "conns": ["c1"]},
            {"id": "nRbac", "dot": {"x": 650, "y": 285}, "label": "API server grants ServiceAccount exact permissions defined in RoleBindings", "conns": ["c2"]}
        ]
    },

    # 28. Node (controller)
    {
        "num": 28,
        "title": "Node (controller)",
        "heading": "Node Lifecycle Controller — Health & Eviction",
        "subtitle": "Monitoring node leases, grace periods, and coordinating eviction upon node failure",
        "completionLabel": "Unhealthy node marked NotReady and pods safely evicted",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 380, "h": 400, "cls": "region-wn", "label": "Worker Node Heartbeat"},
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-cp", "label": "Node Lifecycle Controller"}
        ],
        "nodes": [
            {"id": "nLease", "type": "wn", "x": 60, "y": 120, "w": 340, "h": 70, "title": "Node Lease Object", "sub": "kubelet renews every 10s", "sub2": "heartbeat mechanism"},
            {"id": "nFail", "type": "wn", "x": 60, "y": 250, "w": 340, "h": 70, "title": "Heartbeat Missed", "sub": "network partition or crash", "sub2": "lease renewal stops"},
            {"id": "nController", "type": "cp", "x": 480, "y": 120, "w": 340, "h": 70, "title": "Node Controller Watch", "sub": "node-monitor-grace-period: 40s", "sub2": "detects expired lease"},
            {"id": "nEviction", "type": "cp", "x": 480, "y": 250, "w": 340, "h": 70, "title": "NotReady & Pod Eviction", "sub": "taints node: NoExecute", "sub2": "evicts pods to healthy nodes"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 230, "y1": 190, "x2": 230, "y2": 250},
            {"id": "c1", "type": "line", "x1": 400, "y1": 285, "x2": 480, "y2": 155},
            {"id": "c2", "type": "line", "x1": 650, "y1": 190, "x2": 650, "y2": 250}
        ],
        "stages": [
            {"id": "nLease", "dot": {"x": 230, "y": 155}, "label": "kubelet continuously renews node lease object in kube-node-lease", "conns": []},
            {"id": "nFail", "dot": {"x": 230, "y": 285}, "label": "Node failure causes lease updates to cease", "conns": ["c0"]},
            {"id": "nController", "dot": {"x": 650, "y": 155}, "label": "Node controller detects lease expiration after grace period elapsed", "conns": ["c1"]},
            {"id": "nEviction", "dot": {"x": 650, "y": 285}, "label": "Node marked NotReady; controller adds NoExecute taint and evicts pods", "conns": ["c2"]}
        ]
    },

    # 29. Namespace (controller)
    {
        "num": 29,
        "title": "Namespace (controller)",
        "heading": "Namespace Controller — Resource Scope & Cleanup",
        "subtitle": "Enforcing isolation boundaries and executing orderly cascading deletion via finalizers",
        "completionLabel": "Namespace resources deleted and finalizers cleared",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Namespace Deletion Pipeline"}
        ],
        "nodes": [
            {"id": "nReq", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "kubectl delete ns demo", "sub": "sets deletionTimestamp"},
            {"id": "nTerm", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 60, "title": "Terminating State", "sub": "admission rejects new writes"},
            {"id": "nCascade", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Resource Cleaner", "sub": "deletes pods, services, secrets", "sub2": "waits for resource exit"},
            {"id": "nFinal", "type": "neutral", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Finalizer Removal", "sub": "clears kubernetes finalizer", "sub2": "namespace record deleted"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nReq", "dot": {"x": 170, "y": 170}, "label": "User requests deletion of namespace demo", "conns": []},
            {"id": "nTerm", "dot": {"x": 440, "y": 170}, "label": "Namespace marked Terminating: prevents creation of new resources", "conns": ["c0"]},
            {"id": "nCascade", "dot": {"x": 710, "y": 175}, "label": "Namespace controller systematically deletes all namespaced objects", "conns": ["c1"]},
            {"id": "nFinal", "dot": {"x": 580, "y": 315}, "label": "All resources cleared; controller removes finalizer and drops namespace", "conns": ["c2"]}
        ]
    },

    # 30. ResourceQuota
    {
        "num": 30,
        "title": "ResourceQuota",
        "heading": "ResourceQuota — Capacity Governance",
        "subtitle": "Admission controller enforcing hard ceilings on aggregate CPU, memory, and object counts",
        "completionLabel": "ResourceQuota evaluated: valid requests accepted, overages rejected",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Admission Quota Evaluation"}
        ],
        "nodes": [
            {"id": "nReq", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "Pod Submission", "sub": "requests 2 CPU, 4Gi RAM"},
            {"id": "nPlugin", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "ResourceQuota Plugin", "sub": "evaluates proposed delta", "sub2": "current + requested usage"},
            {"id": "nQuota", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Quota Definition", "sub": "hard limits: 4 CPU, 8Gi RAM", "sub2": "used: 1 CPU, 2Gi RAM"},
            {"id": "nAllow", "type": "neutral", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Request Accepted", "sub": "under ceiling: usage updated", "sub2": "over ceiling: 403 Forbidden"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nReq", "dot": {"x": 170, "y": 170}, "label": "User submits pod creation spec with explicit resource requests", "conns": []},
            {"id": "nPlugin", "dot": {"x": 440, "y": 175}, "label": "ResourceQuota admission controller calculates new cumulative total", "conns": ["c0"]},
            {"id": "nQuota", "dot": {"x": 710, "y": 175}, "label": "Plugin compares total against namespace hard capacity limits", "conns": ["c1"]},
            {"id": "nAllow", "dot": {"x": 580, "y": 315}, "label": "Request is within limits: pod admitted and quota usage tally updated", "conns": ["c2"]}
        ]
    },

    # 31. Garbage Collector
    {
        "num": 31,
        "title": "Garbage Collector",
        "heading": "Garbage Collector — Cascading Object Deletion",
        "subtitle": "Walking ownerReferences graphs to clean up orphaned ReplicaSets and pods",
        "completionLabel": "Dependent resources automatically purged via cascading deletion",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "OwnerReferences Graph & Garbage Collection"}
        ],
        "nodes": [
            {"id": "nDeleteParent", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "Delete Deployment", "sub": "parent object marked deleted"},
            {"id": "nGc", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "GC Graph Scanner", "sub": "tracks ownerReferences", "sub2": "detects orphan children"},
            {"id": "nRs", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Dependent ReplicaSet", "sub": "owner: Deployment/app", "sub2": "queued for cascading deletion"},
            {"id": "nPods", "type": "wn", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Dependent Pods", "sub": "owner: ReplicaSet/app-123", "sub2": "terminated and cleaned up"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nDeleteParent", "dot": {"x": 170, "y": 170}, "label": "User or script deletes top-level parent object (e.g. Deployment)", "conns": []},
            {"id": "nGc", "dot": {"x": 440, "y": 175}, "label": "Garbage collector inspects in-memory graph of object owner references", "conns": ["c0"]},
            {"id": "nRs", "dot": {"x": 710, "y": 175}, "label": "GC issues foreground/background deletion on dependent ReplicaSet", "conns": ["c1"]},
            {"id": "nPods", "dot": {"x": 580, "y": 315}, "label": "Child pods owned by ReplicaSet are automatically purged with zero leaks", "conns": ["c2"]}
        ]
    },

    # 32. ReplicaSet
    {
        "num": 32,
        "title": "ReplicaSet",
        "heading": "ReplicaSet — Pod Count Reconciliation",
        "subtitle": "Maintaining exact count of healthy pods using set-based label selectors",
        "completionLabel": "Replica count reconciled: pod count matches desired spec",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-cp", "label": "ReplicaSet Controller"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Live Pod Instances"}
        ],
        "nodes": [
            {"id": "nSpec", "type": "cp", "x": 60, "y": 120, "w": 420, "h": 60, "title": "ReplicaSet Spec", "sub": "replicas: 3, selector: app=demo"},
            {"id": "nCompare", "type": "cp", "x": 60, "y": 230, "w": 420, "h": 70, "title": "Count Reconciliation Loop", "sub": "matches live pods by label", "sub2": "active: 2, desired: 3 (diff: +1)"},
            {"id": "nAct", "type": "cp", "x": 60, "y": 360, "w": 420, "h": 60, "title": "Corrective API Action", "sub": "creates replacement pod via API"},
            {"id": "nPodList", "type": "wn", "x": 570, "y": 210, "w": 240, "h": 100, "title": "Matching Pods", "sub": "pod-1 (Running)", "sub2": "pod-2 (Running)", "sub2_pad": 10}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 480, "y1": 265, "x2": 570, "y2": 260},
            {"id": "c2", "type": "line", "x1": 270, "y1": 300, "x2": 270, "y2": 360}
        ],
        "stages": [
            {"id": "nSpec", "dot": {"x": 270, "y": 150}, "label": "ReplicaSet declares desired state of 3 healthy pod replicas", "conns": []},
            {"id": "nCompare", "dot": {"x": 270, "y": 265}, "label": "Controller queries live pods matching selector app=demo", "conns": ["c0"]},
            {"id": "nPodList", "dot": {"x": 690, "y": 260}, "label": "Only 2 active pods found: controller detects shortage of 1 replica", "conns": ["c1"]},
            {"id": "nAct", "dot": {"x": 270, "y": 390}, "label": "Controller creates new pod instance to bring cluster into alignment", "conns": ["c2"]}
        ]
    },

    # 33. Deployment
    {
        "num": 33,
        "title": "Deployment",
        "heading": "Deployment — Rolling Updates & Rollbacks",
        "subtitle": "Coordinating zero-downtime rollouts by incrementally shifting traffic across ReplicaSets",
        "completionLabel": "Rolling update completed with zero service interruption",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Deployment Controller Orchestration"}
        ],
        "nodes": [
            {"id": "nUpdate", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "Update Image to v2", "sub": "kubectl set image deployment"},
            {"id": "nDeploy", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "Deployment Controller", "sub": "manages ReplicaSets", "sub2": "maxSurge: 25%, maxUnavailable: 25%"},
            {"id": "nRsOld", "type": "cp", "x": 600, "y": 110, "w": 220, "h": 60, "title": "Old ReplicaSet (v1)", "sub": "scaled down: 3 -> 2 -> 0"},
            {"id": "nRsNew", "type": "cp", "x": 600, "y": 220, "w": 220, "h": 60, "title": "New ReplicaSet (v2)", "sub": "scaled up: 0 -> 1 -> 3"},
            {"id": "nRollback", "type": "neutral", "x": 330, "y": 280, "w": 220, "h": 60, "title": "Instant Rollback Ready", "sub": "revision history preserved"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 150, "x2": 600, "y2": 140},
            {"id": "c2", "type": "line", "x1": 550, "y1": 190, "x2": 600, "y2": 230},
            {"id": "c3", "type": "line", "x1": 440, "y1": 210, "x2": 440, "y2": 280}
        ],
        "stages": [
            {"id": "nUpdate", "dot": {"x": 170, "y": 170}, "label": "Operator updates Deployment container image from nginx:1.24 to 1.25", "conns": []},
            {"id": "nDeploy", "dot": {"x": 440, "y": 175}, "label": "Deployment creates new ReplicaSet for v2 with hash suffix", "conns": ["c0"]},
            {"id": "nRsNew", "dot": {"x": 710, "y": 250}, "label": "New ReplicaSet launches first v2 pod and waits for readiness probe", "conns": ["c2"]},
            {"id": "nRsOld", "dot": {"x": 710, "y": 140}, "label": "Once v2 pod is ready, old ReplicaSet terminates one v1 pod", "conns": ["c1"]},
            {"id": "nRollback", "dot": {"x": 440, "y": 310}, "label": "Rollout completes; revision history preserved for instant one-command rollback", "conns": ["c3"]}
        ]
    },

    # 34. StatefulSet
    {
        "num": 34,
        "title": "StatefulSet",
        "heading": "StatefulSet — Stable Identity & Ordered Storage",
        "subtitle": "Predictable ordinal indexing, dedicated PVC templates, and headless DNS names",
        "completionLabel": "Stateful replicas initialized in strict sequential order",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-wn", "label": "Stateful Set Cluster Architecture"}
        ],
        "nodes": [
            {"id": "nPod0", "type": "wn", "x": 60, "y": 140, "w": 230, "h": 70, "title": "Pod web-0 (Primary)", "sub": "DNS: web-0.web.svc", "sub2": "PVC: data-web-0 (Retained)"},
            {"id": "nPod1", "type": "wn", "x": 320, "y": 140, "w": 230, "h": 70, "title": "Pod web-1 (Replica)", "sub": "DNS: web-1.web.svc", "sub2": "launches only after 0 is Ready"},
            {"id": "nPod2", "type": "wn", "x": 580, "y": 140, "w": 230, "h": 70, "title": "Pod web-2 (Replica)", "sub": "DNS: web-2.web.svc", "sub2": "stable network identity"},
            {"id": "nHeadless", "type": "cp", "x": 320, "y": 280, "w": 230, "h": 70, "title": "Headless Service", "sub": "clusterIP: None", "sub2": "direct SRV/A records per pod"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 290, "y1": 175, "x2": 320, "y2": 175},
            {"id": "c1", "type": "line", "x1": 550, "y1": 175, "x2": 580, "y2": 175},
            {"id": "c2", "type": "line", "x1": 435, "y1": 210, "x2": 435, "y2": 280}
        ],
        "stages": [
            {"id": "nPod0", "dot": {"x": 175, "y": 175}, "label": "StatefulSet launches web-0 with dedicated persistent volume data-web-0", "conns": []},
            {"id": "nPod1", "dot": {"x": 435, "y": 175}, "label": "Controller waits until web-0 is Running and Ready before creating web-1", "conns": ["c0"]},
            {"id": "nPod2", "dot": {"x": 695, "y": 175}, "label": "web-2 created with predictable ordinal index and attached storage", "conns": ["c1"]},
            {"id": "nHeadless", "dot": {"x": 435, "y": 315}, "label": "Headless service allows cluster members to discover peer pods directly by name", "conns": ["c2"]}
        ]
    },

    # 35. DaemonSet
    {
        "num": 35,
        "title": "DaemonSet",
        "heading": "DaemonSet — Per-Node Agent Deployment",
        "subtitle": "Ensuring exactly one copy of a pod runs on every matching cluster node",
        "completionLabel": "Host-level agents running on all current and future worker nodes",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 380, "h": 400, "cls": "region-cp", "label": "DaemonSet Controller"},
            {"x": 460, "y": 80, "w": 380, "h": 400, "cls": "region-wn", "label": "Node Coverage"}
        ],
        "nodes": [
            {"id": "nWatch", "type": "cp", "x": 60, "y": 130, "w": 340, "h": 60, "title": "Node Watcher Loop", "sub": "tracks node additions & removals"},
            {"id": "nMatch", "type": "cp", "x": 60, "y": 250, "w": 340, "h": 70, "title": "Tolerations & Selectors", "sub": "tolerates NoSchedule for control-plane", "sub2": "targets 100% of matching nodes"},
            {"id": "nNode1", "type": "wn", "x": 490, "y": 110, "w": 320, "h": 60, "title": "Worker 1: Agent Pod", "sub": "Fluentbit / Node Exporter"},
            {"id": "nNode2", "type": "wn", "x": 490, "y": 220, "w": 320, "h": 60, "title": "Worker 2: Agent Pod", "sub": "Fluentbit / Node Exporter"},
            {"id": "nNodeNew", "type": "wn", "x": 490, "y": 330, "w": 320, "h": 60, "title": "Newly Joined Worker 3", "sub": "pod scheduled automatically on join"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 230, "y1": 190, "x2": 230, "y2": 250},
            {"id": "c1", "type": "path", "d": "M400 285 L440 285 L440 140 L490 140"},
            {"id": "c2", "type": "line", "x1": 400, "y1": 285, "x2": 490, "y2": 250},
            {"id": "c3", "type": "path", "d": "M400 285 L440 285 L440 360 L490 360"}
        ],
        "stages": [
            {"id": "nWatch", "dot": {"x": 230, "y": 160}, "label": "DaemonSet controller listens to node creation and deletion events", "conns": []},
            {"id": "nMatch", "dot": {"x": 230, "y": 285}, "label": "Controller evaluates node selectors and tolerations", "conns": ["c0"]},
            {"id": "nNode1", "dot": {"x": 650, "y": 140}, "label": "Agent pod reconciled on Worker Node 1", "conns": ["c1"]},
            {"id": "nNode2", "dot": {"x": 650, "y": 250}, "label": "Agent pod reconciled on Worker Node 2", "conns": ["c2"]},
            {"id": "nNodeNew", "dot": {"x": 650, "y": 360}, "label": "When Worker 3 joins cluster, DaemonSet immediately spawns new agent pod", "conns": ["c3"]}
        ]
    },

    # 36. Job
    {
        "num": 36,
        "title": "Job",
        "heading": "Job — Run-to-Completion Batch Execution",
        "subtitle": "Supervising tasks that run until successful exit instead of continuous services",
        "completionLabel": "Batch computation completed; pod cleanly terminated",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Job Lifecycle Management"}
        ],
        "nodes": [
            {"id": "nJob", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "Job Specification", "sub": "completions: 1, parallelism: 1"},
            {"id": "nPod", "type": "wn", "x": 330, "y": 140, "w": 220, "h": 70, "title": "Worker Pod", "sub": "executes data processing", "sub2": "restartPolicy: OnFailure"},
            {"id": "nExit", "type": "wn", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Container Exit 0", "sub": "process terminates cleanly", "sub2": "kubelet marks Completed"},
            {"id": "nDone", "type": "neutral", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Job Status: Succeeded", "sub": "completions: 1/1", "sub2": "no restart; pods retained for logs"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nJob", "dot": {"x": 170, "y": 170}, "label": "User applies Job manifest declaring finite unit of batch computation", "conns": []},
            {"id": "nPod", "dot": {"x": 440, "y": 175}, "label": "Job controller creates pod to run computation", "conns": ["c0"]},
            {"id": "nExit", "dot": {"x": 710, "y": 175}, "label": "Batch process finishes calculations and exits with return code 0", "conns": ["c1"]},
            {"id": "nDone", "dot": {"x": 580, "y": 315}, "label": "Job controller increments completions counter and stops creating pods", "conns": ["c2"]}
        ]
    },

    # 37. CronJob
    {
        "num": 37,
        "title": "CronJob",
        "heading": "CronJob — Periodic Scheduled Automation",
        "subtitle": "Time-based scheduling of batch jobs with concurrency policy and deadline handling",
        "completionLabel": "Scheduled Job dispatched according to cron timetable",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "CronJob Dispatch Pipeline"}
        ],
        "nodes": [
            {"id": "nCron", "type": "cp", "x": 60, "y": 140, "w": 220, "h": 70, "title": "CronJob Controller", "sub": "schedule: \"0 2 * * *\"", "sub2": "tracks lastScheduleTime"},
            {"id": "nTimer", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "Clock Trigger Check", "sub": "checks current timestamp", "sub2": "evaluates concurrencyPolicy"},
            {"id": "nJob", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Spawned Job Object", "sub": "created at schedule deadline", "sub2": "inherits template metadata"},
            {"id": "nPod", "type": "wn", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Execution Pod", "sub": "runs nightly backup batch", "sub2": "retains history based on limit"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 175, "x2": 330, "y2": 175},
            {"id": "c1", "type": "line", "x1": 550, "y1": 175, "x2": 600, "y2": 175},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nCron", "dot": {"x": 170, "y": 175}, "label": "CronJob controller evaluates cron schedule against current cluster clock", "conns": []},
            {"id": "nTimer", "dot": {"x": 440, "y": 175}, "label": "Scheduled execution time reached: controller validates concurrency policy", "conns": ["c0"]},
            {"id": "nJob", "dot": {"x": 710, "y": 175}, "label": "Controller creates new Job resource for this execution interval", "conns": ["c1"]},
            {"id": "nPod", "dot": {"x": 580, "y": 315}, "label": "Job creates pod to execute task; older completed jobs pruned by history limit", "conns": ["c2"]}
        ]
    },

    # 38. ReplicationController (legacy)
    {
        "num": 38,
        "title": "ReplicationController (legacy)",
        "heading": "ReplicationController — Legacy Replica Management",
        "subtitle": "Early Kubernetes equality-based replica management, succeeded by Deployments",
        "completionLabel": "Legacy replication loop maintained; modern Deployments recommended",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Legacy Replication Architecture"}
        ],
        "nodes": [
            {"id": "nRc", "type": "cp", "x": 60, "y": 140, "w": 220, "h": 70, "title": "ReplicationController", "sub": "spec.replicas: 3", "sub2": "equality selector: app=old"},
            {"id": "nMatch", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "Equality Matcher", "sub": "supports only = and !=", "sub2": "lacks set-based expressions"},
            {"id": "nPods", "type": "wn", "x": 600, "y": 140, "w": 220, "h": 70, "title": "Maintained Pods", "sub": "pod count held at 3", "sub2": "replaces crashed pods"},
            {"id": "nModern", "type": "neutral", "x": 330, "y": 280, "w": 220, "h": 70, "title": "Modern Migration", "sub": "migrate to Deployments", "sub2": "gains rolling updates & history"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 175, "x2": 330, "y2": 175},
            {"id": "c1", "type": "line", "x1": 550, "y1": 175, "x2": 600, "y2": 175},
            {"id": "c2", "type": "line", "x1": 440, "y1": 210, "x2": 440, "y2": 280}
        ],
        "stages": [
            {"id": "nRc", "dot": {"x": 170, "y": 175}, "label": "ReplicationController maintains configured number of pod instances", "conns": []},
            {"id": "nMatch", "dot": {"x": 440, "y": 175}, "label": "Selector checks exact equality match without set-based flexibility", "conns": ["c0"]},
            {"id": "nPods", "dot": {"x": 710, "y": 175}, "label": "Target pod copies maintained; lacks built-in rollout orchestration", "conns": ["c1"]},
            {"id": "nModern", "dot": {"x": 440, "y": 315}, "label": "Workloads migrate to Deployments and ReplicaSets for declarative rollouts", "conns": ["c2"]}
        ]
    },

    # 39. HorizontalPodAutoscaler (HPA)
    {
        "num": 39,
        "title": "HorizontalPodAutoscaler (HPA)",
        "heading": "HorizontalPodAutoscaler (HPA) — Dynamic Replica Scaling",
        "subtitle": "Adjusting workload replica count dynamically based on observed CPU and custom metrics",
        "completionLabel": "Replica count scaled horizontally to absorb traffic demand",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 460, "h": 400, "cls": "region-cp", "label": "Autoscaling Control Loop"},
            {"x": 540, "y": 80, "w": 300, "h": 400, "cls": "region-wn", "label": "Scalable Deployment"}
        ],
        "nodes": [
            {"id": "nMetrics", "type": "cp", "x": 60, "y": 120, "w": 420, "h": 60, "title": "Metrics Server / Custom Metrics API", "sub": "polls cgroup CPU/memory from kubelets"},
            {"id": "nHpa", "type": "cp", "x": 60, "y": 230, "w": 420, "h": 70, "title": "HPA Controller Loop", "sub": "evaluates formula: ceil[current * (metric / target)]", "sub2": "target: 50% CPU, current: 85%"},
            {"id": "nScale", "type": "cp", "x": 60, "y": 360, "w": 420, "h": 60, "title": "Scale Subresource PATCH", "sub": "patches deployment.spec.replicas: 2 -> 4"},
            {"id": "nDeploy", "type": "wn", "x": 570, "y": 220, "w": 240, "h": 90, "title": "Deployment Replicas", "sub": "spawns new pods", "sub2": "traffic spread across 4 replicas", "sub2_pad": 10}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 270, "y1": 180, "x2": 270, "y2": 230},
            {"id": "c1", "type": "line", "x1": 270, "y1": 300, "x2": 270, "y2": 360},
            {"id": "c2", "type": "line", "x1": 480, "y1": 390, "x2": 570, "y2": 265}
        ],
        "stages": [
            {"id": "nMetrics", "dot": {"x": 270, "y": 150}, "label": "Metrics server aggregates container CPU utilization across all active pods", "conns": []},
            {"id": "nHpa", "dot": {"x": 270, "y": 265}, "label": "HPA controller compares average CPU against target threshold", "conns": ["c0"]},
            {"id": "nScale", "dot": {"x": 270, "y": 390}, "label": "Calculates required scale ratio and issues PATCH to Deployment /scale endpoint", "conns": ["c1"]},
            {"id": "nDeploy", "dot": {"x": 690, "y": 265}, "label": "Deployment spawns 2 additional pods; load distributed evenly to normalize CPU", "conns": ["c2"]}
        ]
    },

    # 40. VerticalPodAutoscaler (VPA)
    {
        "num": 40,
        "title": "VerticalPodAutoscaler (VPA)",
        "heading": "VerticalPodAutoscaler (VPA) — Right-sizing CPU & Memory",
        "subtitle": "Analyzing historical usage, evicting pods, and adjusting requests on recreation",
        "completionLabel": "Pod right-sized with updated CPU and memory boundaries",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "VPA Optimization Pipeline"}
        ],
        "nodes": [
            {"id": "nRec", "type": "cp", "x": 60, "y": 130, "w": 220, "h": 70, "title": "VPA Recommender", "sub": "computes optimal requests", "sub2": "target: 500m CPU, 1Gi RAM"},
            {"id": "nUpd", "type": "cp", "x": 330, "y": 130, "w": 220, "h": 70, "title": "VPA Updater", "sub": "in Auto mode", "sub2": "evicts undersized pod"},
            {"id": "nAdm", "type": "cp", "x": 600, "y": 130, "w": 220, "h": 70, "title": "VPA Admission Webhook", "sub": "intercepts pod recreation", "sub2": "mutates container requests"},
            {"id": "nNewPod", "type": "wn", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Right-Sized Pod", "sub": "starts with new CPU/RAM limits", "sub2": "eliminates OOMKills"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 165, "x2": 330, "y2": 165},
            {"id": "c1", "type": "line", "x1": 550, "y1": 165, "x2": 600, "y2": 165},
            {"id": "c2", "type": "line", "x1": 710, "y1": 200, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nRec", "dot": {"x": 170, "y": 165}, "label": "VPA Recommender models historical container utilization percentiles", "conns": []},
            {"id": "nUpd", "dot": {"x": 440, "y": 165}, "label": "Updater evicts pod if current request drifts significantly from target", "conns": ["c0"]},
            {"id": "nAdm", "dot": {"x": 710, "y": 165}, "label": "When workload controller recreates pod, mutating webhook overrides requests", "conns": ["c1"]},
            {"id": "nNewPod", "dot": {"x": 580, "y": 315}, "label": "Pod restarts on worker node with right-sized CPU and memory guarantees", "conns": ["c2"]}
        ]
    },

    # 41. Pod Disruption Budget (PDB)
    {
        "num": 41,
        "title": "Pod Disruption Budget (PDB)",
        "heading": "Pod Disruption Budget (PDB) — Maintenance Protection",
        "subtitle": "Guaranteed minimum replica thresholds during voluntary node drains and upgrades",
        "completionLabel": "Disruption budget safeguarded; eviction gated safely",
        "width": 880, "height": 520,
        "regions": [
            {"x": 40, "y": 80, "w": 800, "h": 400, "cls": "region-cp", "label": "Voluntary Eviction & Disruption Budget Pipeline"}
        ],
        "nodes": [
            {"id": "nDrain", "type": "client", "x": 60, "y": 140, "w": 220, "h": 60, "title": "kubectl drain node-1", "sub": "voluntary node maintenance"},
            {"id": "nEvictApi", "type": "cp", "x": 330, "y": 140, "w": 220, "h": 70, "title": "Eviction API Subresource", "sub": "calls /pods/eviction", "sub2": "consults active PDBs"},
            {"id": "nPdb", "type": "cp", "x": 600, "y": 140, "w": 220, "h": 70, "title": "PDB Policy Check", "sub": "minAvailable: 2", "sub2": "current healthy: 3 (Allowed: 1)"},
            {"id": "nDecision", "type": "neutral", "x": 465, "y": 280, "w": 230, "h": 70, "title": "Gated Eviction Result", "sub": "1 pod evicted safely", "sub2": "remaining drain attempts blocked if <= 2"}
        ],
        "connectors": [
            {"id": "c0", "type": "line", "x1": 280, "y1": 170, "x2": 330, "y2": 170},
            {"id": "c1", "type": "line", "x1": 550, "y1": 170, "x2": 600, "y2": 170},
            {"id": "c2", "type": "line", "x1": 710, "y1": 210, "x2": 580, "y2": 280}
        ],
        "stages": [
            {"id": "nDrain", "dot": {"x": 170, "y": 170}, "label": "Administrator drains worker node for operating system maintenance", "conns": []},
            {"id": "nEvictApi", "dot": {"x": 440, "y": 175}, "label": "Drain sends eviction requests rather than hard pod deletion", "conns": ["c0"]},
            {"id": "nPdb", "dot": {"x": 710, "y": 175}, "label": "PDB verifies remaining healthy replicas satisfy minAvailable threshold", "conns": ["c1"]},
            {"id": "nDecision", "dot": {"x": 580, "y": 315}, "label": "Eviction permitted without violating application availability requirements", "conns": ["c2"]}
        ]
    }
]

print("Topics 21-41 defined:", len(FINAL_TOPICS))
