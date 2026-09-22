# quiz_data.py
# 82 high-yield, moderately difficult, straightforward Kubernetes engineering quiz questions across all 41 topics.

QUIZZES = {
    1: [
        {
            "question": "When a worker node running a Pod loses network connectivity to the control plane, what happens to the containers running on that node immediately?",
            "options": [
                "The local container runtime immediately terminates all running containers.",
                "The containers continue running locally, but the control plane cannot observe or update their status.",
                "The API server sends an SSH command to reboot the worker machine.",
                "etcd immediately purges the Pod object from cluster state."
            ],
            "answer": 1,
            "explanation": "The kubelet and local container runtime continue executing workloads based on local state even during control plane disconnection, though the control plane will mark the node NotReady after the lease timeout."
        },
        {
            "question": "Which core architectural principle fundamentally distinguishes Kubernetes from traditional imperative VM deployment scripts?",
            "options": [
                "Synchronous execution of linear shell scripts on remote hosts.",
                "Declarative desired state reconciliation via continuous control loops.",
                "Direct peer-to-peer communication between etcd and container runtimes.",
                "Requiring physical operator access to machines for all changes."
            ],
            "answer": 1,
            "explanation": "Kubernetes operates on declarative intent: you define the desired state in the API server, and independent controllers continuously reconcile actual state to match it."
        }
    ],
    2: [
        {
            "question": "If all control plane nodes become temporarily unreachable in a cluster, what is the immediate effect on already-running workloads on healthy worker nodes?",
            "options": [
                "All pods are immediately terminated by their local kubelets.",
                "Worker nodes stop routing network traffic between running pods.",
                "Existing pods and data plane networking continue running, but no new pods can be scheduled or state updated.",
                "The cluster automatically falls back to single-node Docker engines."
            ],
            "answer": 2,
            "explanation": "Data plane execution is decoupled from the control plane; existing pods and network routes remain functional, but scheduling, scaling, and API changes are blocked."
        },
        {
            "question": "What is the primary role of worker nodes relative to the control plane?",
            "options": [
                "Managing etcd quorum and evaluating RBAC authorization.",
                "Executing pod sandboxes, container processes, and local network/storage enforcement via kubelet and runtime.",
                "Authorizing TLS certificates for external client requests.",
                "Directly editing cluster manifests inside etcd storage."
            ],
            "answer": 1,
            "explanation": "Worker nodes represent the execution layer ('muscle') managed by kubelet, containerd, and kube-proxy, while the control plane ('brain') makes decisions and stores intent."
        }
    ],
    3: [
        {
            "question": "Which of the following is true regarding how cluster components communicate with etcd in standard Kubernetes?",
            "options": [
                "Both the scheduler and kubelet write directly to etcd over gRPC.",
                "Only the kube-apiserver communicates directly with etcd; all other components interact via the API server.",
                "etcd pushes event notifications directly to worker node kube-proxies.",
                "Admission webhooks persist rejected objects directly in etcd for audit logs."
            ],
            "answer": 1,
            "explanation": "kube-apiserver is the sole gateway and concurrency boundary for etcd, ensuring all reads and writes pass through authentication, authorization, and validation."
        },
        {
            "question": "In what order does the kube-apiserver process an incoming resource creation request?",
            "options": [
                "Mutating Admission -> Authentication -> Validation -> etcd",
                "Authentication -> Authorization -> Mutating Admission -> Schema/Validating Admission -> etcd",
                "Authorization -> Schema Validation -> Authentication -> etcd",
                "etcd Write -> Mutating Admission -> Authorization"
            ],
            "answer": 1,
            "explanation": "A request must first be authenticated (who are you?), then authorized (can you do this?), then mutated (defaults/sidecars injected), then validated (schema & policy rules), before being committed to etcd."
        }
    ],
    4: [
        {
            "question": "In a 3-node etcd cluster, how many node failures can the cluster tolerate while maintaining write operations?",
            "options": [
                "2 nodes",
                "1 node",
                "0 nodes",
                "3 nodes"
            ],
            "answer": 1,
            "explanation": "etcd requires a strict majority quorum ((N/2) + 1). For N=3, quorum is 2, meaning only 1 node failure is tolerated before writes are blocked."
        },
        {
            "question": "Why is low-latency disk I/O (such as NVMe/SSD) critical for etcd performance in production?",
            "options": [
                "etcd compiles Go binaries on every write transaction.",
                "Raft consensus requires sequential fsync writes to the write-ahead log (WAL) before acknowledging mutations.",
                "etcd stores container image layers on disk.",
                "kube-proxy streams raw packet capture logs into etcd."
            ],
            "answer": 1,
            "explanation": "Every Raft proposal requires appending to disk and fsyncing to the WAL; high disk write latency directly stalls Raft consensus heartbeats and API server writes."
        }
    ],
    5: [
        {
            "question": "During the scheduling cycle for an unscheduled Pod, what occurs if all candidate nodes are eliminated during the Filtering (predicates) phase?",
            "options": [
                "The Pod is scheduled on the control-plane node automatically.",
                "The Pod remains in Pending status with a PodScheduled condition of False and reason FailedScheduling.",
                "The kube-scheduler deletes the Pod from etcd.",
                "The Pod is assigned to a random worker node regardless of constraints."
            ],
            "answer": 1,
            "explanation": "If no node passes filtering (e.g. due to insufficient CPU/memory or untolerated taints), the pod stays Pending until cluster capacity or constraints change."
        },
        {
            "question": "How does the scheduler communicate its placement decision to the assigned worker node?",
            "options": [
                "The scheduler connects via SSH directly to the worker node.",
                "The scheduler creates a Binding subresource via the API server that sets pod.spec.nodeName.",
                "The scheduler pushes a gRPC message directly to containerd on the worker node.",
                "The scheduler writes the node IP into CoreDNS."
            ],
            "answer": 1,
            "explanation": "The scheduler does not contact nodes directly; it creates a Binding object via the API server, setting spec.nodeName. The target node's kubelet watches for pods bound to itself."
        }
    ],
    6: [
        {
            "question": "What design principle enables Kubernetes controllers to recover gracefully from network partitions or restarts without missing state changes?",
            "options": [
                "Edge-triggered interrupts stored in persistent message queues.",
                "Level-triggered reconciliation loops comparing desired state from the API server with observed cluster state.",
                "Synchronous RPC heartbeats between all worker nodes.",
                "Hardcoded sleep timers between sequential shell commands."
            ],
            "answer": 1,
            "explanation": "Level-triggered design means controllers reconcile based on current observed state rather than relying on having received every intermediate edge event, making them self-healing and idempotent."
        },
        {
            "question": "If a user manually deletes a Pod managed by a Deployment (via its ReplicaSet), what will the ReplicaSet controller do?",
            "options": [
                "It updates the Deployment replicas count to N - 1.",
                "It marks the Deployment as Failed.",
                "It observes that current replicas < desired replicas and creates a replacement Pod via the API server.",
                "It recreates the entire cluster worker node."
            ],
            "answer": 2,
            "explanation": "The ReplicaSet controller continuously compares observed replicas matching its selector against spec.replicas. If one is missing, it immediately issues an API request to create a new one."
        }
    ],
    7: [
        {
            "question": "What was the primary motivation for introducing the cloud-controller-manager (CCM) as a separate binary from kube-controller-manager?",
            "options": [
                "To make Kubernetes compatible with Windows worker nodes.",
                "To extract vendor-specific cloud provider code out-of-tree so cloud providers can update independently of Kubernetes core releases.",
                "To replace etcd with cloud databases like AWS DynamoDB.",
                "To eliminate the need for kubelet on cloud virtual machines."
            ],
            "answer": 1,
            "explanation": "Out-of-tree cloud controllers decouple cloud provider SDKs and release cycles from the core Kubernetes repository, removing proprietary drivers from the core codebase."
        },
        {
            "question": "Which controller within cloud-controller-manager is responsible for provisioning cloud load balancers when a Service of type LoadBalancer is created?",
            "options": [
                "Node lifecycle controller",
                "Service controller",
                "Route controller",
                "PersistentVolume label controller"
            ],
            "answer": 1,
            "explanation": "The cloud Service controller watches for Services of type: LoadBalancer and calls the cloud provider's API to provision and wire up external load balancers."
        }
    ],
    8: [
        {
            "question": "Who manages the lifecycle of a Static Pod running on a worker node?",
            "options": [
                "The kube-scheduler running on the control plane.",
                "The local kubelet on that specific node watching a local file directory or HTTP endpoint directly.",
                "The Deployment controller.",
                "CoreDNS."
            ],
            "answer": 1,
            "explanation": "Static Pods are configured locally on a node (typically in /etc/kubernetes/manifests) and supervised directly by the kubelet without scheduler involvement."
        },
        {
            "question": "What is a 'Mirror Pod' in the context of Static Pods?",
            "options": [
                "An identical backup container running on a secondary worker node.",
                "A read-only Pod representation created on the API server by kubelet so the Static Pod is visible via kubectl get pods.",
                "A sidecar container injected into every pod for logging.",
                "A container that replicates network packets for auditing."
            ],
            "answer": 1,
            "explanation": "The kubelet creates a Mirror Pod on the API server matching the static pod spec so cluster operators can observe its status using standard Kubernetes API tools."
        }
    ],
    9: [
        {
            "question": "If a container's liveness probe fails consecutively beyond failureThreshold, what action does the kubelet take?",
            "options": [
                "The kubelet removes the Pod from Service endpoints without restarting the container.",
                "The kubelet terminates the container and restarts it according to the Pod's restartPolicy.",
                "The kubelet evicts the Pod to a different worker node.",
                "The kubelet drains the entire node."
            ],
            "answer": 1,
            "explanation": "Liveness probe failures indicate an unhealthy process that cannot recover on its own; kubelet kills the container and restarts it according to restartPolicy."
        },
        {
            "question": "How does the kubelet authenticate itself when communicating with the kube-apiserver?",
            "options": [
                "Using plain HTTP with no authentication.",
                "Using mutual TLS (mTLS) with client certificates typically issued in the system:nodes group.",
                "Using the host operating system's root password.",
                "Through SSH key exchange on port 22."
            ],
            "answer": 1,
            "explanation": "Kubelets use client X.509 certificates belonging to the system:nodes group, authorized by the Node authorization mode on the API server."
        }
    ],
    10: [
        {
            "question": "What is the key performance advantage of kube-proxy running in ipvs mode compared to standard iptables mode in large clusters?",
            "options": [
                "IPVS compresses network packets using gzip.",
                "IPVS uses hash tables with O(1) lookup complexity, whereas iptables uses sequential rule chains with O(N) evaluation latency.",
                "IPVS replaces TCP with UDP for faster packet transmission.",
                "IPVS eliminates the need for container network interfaces."
            ],
            "answer": 1,
            "explanation": "Sequential iptables rule chains incur linear O(N) processing overhead as rule counts grow to tens of thousands; IPVS uses ipset hash tables providing near-constant O(1) routing latency."
        },
        {
            "question": "When an application inside a Pod sends traffic to a ClusterIP:port, where is the destination IP translated to an actual backend Pod IP?",
            "options": [
                "By the CoreDNS pod using DNS round-robin.",
                "In the Linux kernel on the sending node via iptables/IPVS NAT rules maintained by kube-proxy.",
                "In the cloud provider's external hardware gateway.",
                "Inside the application container's glibc runtime."
            ],
            "answer": 1,
            "explanation": "The virtual ClusterIP does not exist on any physical interface; packet destination is rewritten (DNAT) directly inside the node's kernel by the netfilter rules programmed by kube-proxy."
        }
    ],
    11: [
        {
            "question": "What role does the Container Runtime Interface (CRI) play in the Kubernetes node architecture?",
            "options": [
                "It compiles application source code into container images on the worker node.",
                "It is a gRPC interface that standardizes how kubelet communicates with pluggable container runtimes like containerd or CRI-O.",
                "It encrypts network traffic between pods across nodes.",
                "It manages persistent disk volume attachments in cloud storage."
            ],
            "answer": 1,
            "explanation": "CRI defines the gRPC protobuf specification for runtime and image services, allowing Kubernetes to support any compliant runtime without vendor lock-in."
        },
        {
            "question": "Why does a Pod sandbox include a 'pause' (or infra) container?",
            "options": [
                "To pause container execution when the node is low on memory.",
                "To hold the Linux network, IPC, and mount namespaces that all containers in the Pod share throughout its lifecycle.",
                "To provide a graphical terminal interface for container debugging.",
                "To cache container image layers locally."
            ],
            "answer": 1,
            "explanation": "The pause container holds the shared namespaces (particularly the network namespace) so that if an application container restarts, the Pod IP and network interface remain intact."
        }
    ],
    12: [
        {
            "question": "How do two containers residing within the same Pod communicate over the network?",
            "options": [
                "Through external Ingress controllers.",
                "Via localhost on their shared loopback network interface.",
                "By creating a public NodePort service.",
                "They cannot communicate over network sockets."
            ],
            "answer": 1,
            "explanation": "All containers in a Pod share the exact same network namespace and IP address, meaning they reach each other directly via localhost and shared ports."
        },
        {
            "question": "What is the primary operational trade-off of deploying sidecar containers across thousands of application pods?",
            "options": [
                "Incompatible CPU architectures between containers.",
                "Multiplied resource overhead (CPU/memory requests & limits) and increased pod startup/shutdown latency.",
                "Inability to mount volume storage.",
                "Breaking CoreDNS name resolution for the cluster."
            ],
            "answer": 1,
            "explanation": "Every sidecar consumes reserved CPU and memory quota across every pod replica, and lifecycle coupling can complicate graceful shutdown if the sidecar terminates before the main app finishes."
        }
    ],
    13: [
        {
            "question": "What happens if an Init Container fails its execution (exits with non-zero status) and the Pod's restartPolicy is Always?",
            "options": [
                "The main application container starts anyway.",
                "The kubelet restarts the failed Init Container repeatedly with exponential backoff until it succeeds.",
                "The Pod is immediately deleted from the cluster.",
                "The worker node is rebooted."
            ],
            "answer": 1,
            "explanation": "Init containers must run sequentially to successful completion (exit 0) before any app container can launch; failures trigger kubelet restarts subject to restart policy backoff."
        },
        {
            "question": "In what order do multiple Init Containers defined in a Pod spec execute?",
            "options": [
                "In parallel simultaneously.",
                "In the exact sequential order they are listed in the spec.initContainers array.",
                "In reverse alphabetical order by name.",
                "Randomly based on image pull completion."
            ],
            "answer": 1,
            "explanation": "Kubernetes guarantees strict sequential execution: Init Container 1 must finish with code 0 before Init Container 2 begins execution."
        }
    ],
    14: [
        {
            "question": "What fundamental networking requirement does the Kubernetes network model mandate for all CNI plugins?",
            "options": [
                "Every pod must use the same IP address as its host worker node.",
                "All pods can communicate with all other pods across nodes on a flat network without NAT.",
                "Every pod must have a dedicated public IPv4 address.",
                "Nodes can only communicate via SSH tunnels."
            ],
            "answer": 1,
            "explanation": "The fundamental Kubernetes IP-per-pod model requires that pods on any node can communicate with pods on any other node without Network Address Translation (NAT)."
        },
        {
            "question": "What Linux kernel mechanism is typically created by a CNI plugin to connect a Pod's network namespace to the host network?",
            "options": [
                "A virtual ethernet (veth) pair connecting the pod's eth0 to a host bridge or routing table.",
                "A loopback-only interface with no host connection.",
                "An NFS network mount point.",
                "A Unix domain socket in /tmp."
            ],
            "answer": 0,
            "explanation": "A veth pair functions like a virtual patch cable: one end sits inside the pod's network namespace as eth0, and the peer end sits in the host namespace attached to a bridge or routing engine."
        }
    ],
    15: [
        {
            "question": "How does a Pod resolve the service name 'auth-service' located in the same namespace 'production' without specifying an FQDN?",
            "options": [
                "CoreDNS broadcasts an ARP request across the node subnet.",
                "The pod's /etc/resolv.conf specifies search paths like production.svc.cluster.local, which the resolver appends automatically.",
                "The application container must hardcode the IP address in /etc/hosts.",
                "The Linux kernel queries the root DNS servers on the internet."
            ],
            "answer": 1,
            "explanation": "Kubelet configures /etc/resolv.conf with search domains (<namespace>.svc.cluster.local, svc.cluster.local, etc.), allowing short names to be expanded and resolved."
        },
        {
            "question": "Where does CoreDNS source its real-time mapping of Service names to ClusterIPs and Endpoint IPs?",
            "options": [
                "From a static text file hosted on GitHub.",
                "By watching the Kubernetes API server for Service and EndpointSlice resource events.",
                "By scanning worker node ARP tables every second.",
                "From the host operating system's /etc/bind/named.conf."
            ],
            "answer": 1,
            "explanation": "The CoreDNS kubernetes plugin connects to the kube-apiserver with an informer cache, watching Services and Endpoints to answer queries from live cluster state."
        }
    ],
    16: [
        {
            "question": "Why is a Service's ClusterIP virtual IP address preferred over calling individual Pod IPs directly from client applications?",
            "options": [
                "Pod IPs are slower because they require hardware encryption.",
                "Pod IPs are ephemeral and change upon container restart or rescheduling, whereas ClusterIP remains stable.",
                "Pod IPs are only reachable from the control plane node.",
                "ClusterIP bypasses all container network interfaces."
            ],
            "answer": 1,
            "explanation": "Pods are dynamic and mortal; a Service provides a durable, static IP and DNS name that load-balances traffic across the ever-shifting set of backend pods."
        },
        {
            "question": "Which Service type creates an external cloud load balancer and automatically configures NodePort and ClusterIP routes as well?",
            "options": [
                "type: ClusterIP",
                "type: NodePort",
                "type: LoadBalancer",
                "type: ExternalName"
            ],
            "answer": 2,
            "explanation": "In Kubernetes, Service types build upon each other: LoadBalancer allocates a cloud LB, which forwards to NodePort, which routes to ClusterIP."
        }
    ],
    17: [
        {
            "question": "Why did Kubernetes introduce EndpointSlice resources to replace monolithic Endpoints objects in large clusters?",
            "options": [
                "To support IPv6-only clusters.",
                "Monolithic Endpoints objects caused massive API server write amplification when a single pod changed in a service with thousands of replicas.",
                "Because EndpointSlice completely eliminates the need for kube-proxy.",
                "Endpoints could only store up to 5 IP addresses."
            ],
            "answer": 1,
            "explanation": "With monolithic Endpoints, a change to 1 pod in a 5,000-pod service required resending the entire multi-megabyte object to all nodes; EndpointSlices chunk endpoints into groups of 100, dramatically reducing API bandwidth."
        },
        {
            "question": "What condition must a Pod satisfy before the EndpointSlice controller adds its IP address to the active serving endpoints of a Service?",
            "options": [
                "The Pod must have passed its readiness probe (ContainersReady: True).",
                "The Pod must be running for at least 10 minutes.",
                "The Pod must be scheduled on the control plane node.",
                "The Pod must have no CPU limits defined."
            ],
            "answer": 0,
            "explanation": "A pod is only considered ready to serve live user traffic when its readiness probes pass; unready pods are excluded from active service endpoints."
        }
    ],
    18: [
        {
            "question": "What is the primary difference between a Kubernetes Ingress resource and an Ingress Controller?",
            "options": [
                "The Ingress resource is an active proxy process; the controller is just a documentation file.",
                "The Ingress resource is a declarative configuration object; the Ingress Controller is the actual daemon that watches the API and proxies traffic.",
                "Ingress operates at Layer 4 (TCP), while the controller operates at Layer 3 (IP).",
                "Ingress requires cloud provider hardware, while controllers run on bare metal."
            ],
            "answer": 1,
            "explanation": "An Ingress manifest (kind: Ingress) only declares routing rules; traffic does not flow until an Ingress Controller is deployed to parse those rules and proxy incoming HTTP requests."
        },
        {
            "question": "Which OSI layer does a standard Kubernetes Ingress operate at to provide host-based and path-based routing?",
            "options": [
                "Layer 3 (Network - IP packets)",
                "Layer 4 (Transport - TCP/UDP sockets)",
                "Layer 7 (Application - HTTP/HTTPS URLs, headers, and hostnames)",
                "Layer 2 (Data Link - MAC addresses)"
            ],
            "answer": 2,
            "explanation": "Ingress inspects HTTP requests (Host headers like api.example.com and URL paths like /v1/users) to direct traffic to appropriate internal services."
        }
    ],
    19: [
        {
            "question": "What happens in a namespace when no NetworkPolicies are applied versus when a single NetworkPolicy with podSelector: {} and ingress: [] is applied?",
            "options": [
                "Default behavior is allow-all; applying an empty ingress policy creates an isolation boundary that defaults to deny-all incoming traffic.",
                "Default behavior is deny-all; applying a policy enables allow-all.",
                "Applying a policy disables DNS resolution across the entire cluster.",
                "The container runtime pauses all running containers."
            ],
            "answer": 0,
            "explanation": "By default, pod networking is non-isolated (allow all). As soon as any NetworkPolicy selects a pod, that pod enters isolated mode where unselected traffic is rejected."
        },
        {
            "question": "Why might a newly created NetworkPolicy fail to enforce traffic blocking in a cluster running standard default kind?",
            "options": [
                "The policy YAML had invalid syntax.",
                "The default CNI plugin in standard kind (kindnet) does not implement NetworkPolicy enforcement; a policy-capable CNI (like Calico or Cilium) is required.",
                "NetworkPolicies only work in production cloud clusters.",
                "kube-apiserver disables NetworkPolicy by default."
            ],
            "answer": 1,
            "explanation": "NetworkPolicy is a declarative API spec; enforcement is the responsibility of the underlying CNI plugin dataplane (eBPF or iptables). Kindnet does not support NetworkPolicy."
        }
    ],
    20: [
        {
            "question": "What is the difference in scope between a PersistentVolume (PV) and a PersistentVolumeClaim (PVC)?",
            "options": [
                "A PV is namespaced, while a PVC is cluster-scoped.",
                "A PV is a cluster-wide storage resource, while a PVC is a namespaced request for storage.",
                "Both PV and PVC must reside in the kube-system namespace.",
                "A PV can only be mounted by one pod across the entire cluster lifetime."
            ],
            "answer": 1,
            "explanation": "PVs are cluster-level infrastructure objects created by admins or dynamic provisioners; PVCs are namespaced consumer objects created by developers."
        },
        {
            "question": "If a PersistentVolume has persistentVolumeReclaimPolicy set to Retain, what occurs when its bound PVC is deleted?",
            "options": [
                "The underlying storage disk and data are immediately wiped.",
                "The PV moves to Released status; the volume and data remain intact on physical storage until manually reclaimed.",
                "The PV is automatically assigned to a random new Pod.",
                "The storage volume is resized to 0GB."
            ],
            "answer": 1,
            "explanation": "Retain prevents automated data loss: when the claim is deleted, the volume transitions to Released and requires manual administrator cleanup."
        }
    ],
    21: [
        {
            "question": "What state does a PVC remain in if no existing PV matches its capacity and accessModes, and no dynamic provisioner is configured?",
            "options": [
                "Failed",
                "Pending",
                "Terminating",
                "Running"
            ],
            "answer": 1,
            "explanation": "The PVC remains Pending until a matching PV is created or dynamically provisioned, and any Pod referencing that PVC will be blocked from starting."
        },
        {
            "question": "Which access mode allows a single volume to be mounted read-write by multiple pods simultaneously across different worker nodes?",
            "options": [
                "ReadWriteOnce (RWO)",
                "ReadOnlyMany (ROX)",
                "ReadWriteMany (RWX)",
                "ReadWriteOncePod (RWOP)"
            ],
            "answer": 2,
            "explanation": "ReadWriteMany (RWX) permits simultaneous read/write mounting across multiple nodes (typically backed by NFS, CephFS, or cloud file storage)."
        }
    ],
    22: [
        {
            "question": "What is the primary purpose of setting volumeBindingMode: WaitForFirstConsumer on a StorageClass?",
            "options": [
                "It ensures volumes are created without filesystem formatting.",
                "It delays dynamic volume creation until a Pod referencing the PVC is scheduled, ensuring the volume is provisioned in the same availability zone as the Pod.",
                "It disables volume caching in memory.",
                "It prevents users from deleting the PVC."
            ],
            "answer": 1,
            "explanation": "Without this setting, volumes might be provisioned in an availability zone where candidate worker nodes lack capacity, preventing the pod from scheduling."
        },
        {
            "question": "In dynamic volume provisioning, what component detects an unbound PVC and calls the underlying storage infrastructure to create the disk?",
            "options": [
                "The kube-scheduler.",
                "The CSI external-provisioner controller.",
                "The CoreDNS daemon.",
                "The container runtime runc binary."
            ],
            "answer": 1,
            "explanation": "The CSI external-provisioner sidecar watches for PVCs with an associated StorageClass and issues CreateVolume gRPC requests to the CSI driver."
        }
    ],
    23: [
        {
            "question": "Can a standard Kubernetes Role grant permissions to list nodes or create namespaces?",
            "options": [
                "Yes, if the namespace field is omitted.",
                "No, because a Role is strictly namespaced and can only grant permissions on namespaced resources within its own namespace; cluster-scoped resources require a ClusterRole.",
                "Yes, if granted by an administrator.",
                "Only on worker nodes, not control plane nodes."
            ],
            "answer": 1,
            "explanation": "Roles are bounded by namespace; non-namespaced resources (like Nodes, Namespaces, and PersistentVolumes) can only be governed by ClusterRoles."
        },
        {
            "question": "How does the Kubernetes RBAC authorization engine evaluate permissions when multiple Roles or rules apply to a single identity?",
            "options": [
                "It uses a deny-first evaluation where explicit denies override allows.",
                "It uses purely additive (allow-only) evaluation; if any matching rule grants the verb on the resource, the action is permitted.",
                "It takes the intersection of all granted permissions.",
                "It grants access only if the client certificate was created within 24 hours."
            ],
            "answer": 1,
            "explanation": "Kubernetes RBAC has no 'deny' rules; all permissions are additive (whitelisting). Access is authorized if at least one rule grants the requested verb."
        }
    ],
    24: [
        {
            "question": "Can a RoleBinding located in namespace 'dev' reference a ClusterRole in its roleRef?",
            "options": [
                "No, RoleBindings can only bind namespaced Roles.",
                "Yes; it binds the ClusterRole's defined permissions, but scopes them strictly to namespace 'dev'.",
                "Yes, and it automatically grants the user cluster-wide admin access.",
                "Only if the user has root privileges on the control-plane host."
            ],
            "answer": 1,
            "explanation": "Referencing a ClusterRole in a namespaced RoleBinding is a common pattern to reuse common permission sets (e.g. edit or view) within an individual namespace."
        },
        {
            "question": "What happens if an administrator attempts to modify the roleRef field of an existing RoleBinding object?",
            "options": [
                "The API server updates all bound subjects immediately.",
                "The API server rejects the mutation because the roleRef field is immutable; the binding must be deleted and recreated.",
                "The referenced Role is deleted.",
                "The subjects lose access to the cluster permanently."
            ],
            "answer": 1,
            "explanation": "roleRef is an immutable field in Kubernetes RBAC to prevent accidental privilege escalation; you must delete and recreate the binding to point to a new role."
        }
    ],
    25: [
        {
            "question": "When is a ClusterRole strictly required instead of a namespaced Role?",
            "options": [
                "When deploying a container that uses more than 1GB of memory.",
                "When granting access to non-namespaced resources (e.g. Nodes, PersistentVolumes) or non-resource URLs (e.g. /healthz).",
                "Whenever using kind on a local machine.",
                "When mounting an emptyDir volume."
            ],
            "answer": 1,
            "explanation": "Non-namespaced API endpoints and cluster-wide resources do not belong to any individual namespace and therefore cannot be expressed in a namespaced Role."
        },
        {
            "question": "How do aggregated ClusterRoles work in Kubernetes?",
            "options": [
                "They combine multiple physical worker nodes into a single logical entity.",
                "The cluster dynamically combines rules from other ClusterRoles matching specified label selectors into an aggregate role.",
                "They merge all user passwords into a single hash.",
                "They compress API requests to improve network throughput."
            ],
            "answer": 1,
            "explanation": "ClusterRole aggregation allows custom controllers to extend built-in roles (like admin or edit) by labeling new ClusterRoles that are automatically merged."
        }
    ],
    26: [
        {
            "question": "What is the operational risk of binding the built-in cluster-admin ClusterRole to a ServiceAccount using a ClusterRoleBinding?",
            "options": [
                "It limits the ServiceAccount to reading configmaps only.",
                "It grants unrestricted superuser privileges across every namespace and cluster-scoped resource, creating a critical security risk if the token is compromised.",
                "It causes the kubelet to reboot every worker node.",
                "It disables TLS encryption across the cluster."
            ],
            "answer": 1,
            "explanation": "cluster-admin provides unrestricted access (* verbs on * resources); granting it globally violates least privilege and exposes the entire platform to compromise."
        },
        {
            "question": "Can a ClusterRoleBinding grant permissions that are limited to a single namespace?",
            "options": [
                "Yes, by setting the namespace field in the binding metadata.",
                "No; ClusterRoleBindings are cluster-scoped and always apply across all namespaces; to scope permissions to one namespace, use a RoleBinding.",
                "Yes, if the subject is a ServiceAccount.",
                "Only on worker nodes."
            ],
            "answer": 1,
            "explanation": "ClusterRoleBindings are inherently global; scoping permissions to a specific namespace requires a namespaced RoleBinding."
        }
    ],
    27: [
        {
            "question": "Under modern Kubernetes token projection (BoundServiceAccountTokenVolume), what happens when a Pod is deleted?",
            "options": [
                "The token remains valid indefinitely.",
                "The projected token is tied to the Pod's lifecycle and becomes invalid when the Pod is deleted.",
                "The entire ServiceAccount is automatically deleted.",
                "The API server revokes all client certificates."
            ],
            "answer": 1,
            "explanation": "Projected service account tokens are cryptographically signed, audience-bound, time-limited, and bound to the specific Pod's UID, mitigating stolen token replay attacks."
        },
        {
            "question": "Where does kubelet mount the projected ServiceAccount token inside a container by default?",
            "options": [
                "/etc/kubernetes/admin.conf",
                "/var/run/secrets/kubernetes.io/serviceaccount/",
                "/root/.kube/config",
                "/tmp/k8s/"
            ],
            "answer": 1,
            "explanation": "Kubelet automatically mounts the token, ca.crt, and namespace files into /var/run/secrets/kubernetes.io/serviceaccount/ unless automountServiceAccountToken: false is configured."
        }
    ],
    28: [
        {
            "question": "How does the Node lifecycle controller detect that a worker node has become unhealthy?",
            "options": [
                "By attempting to ping the host over ICMP every millisecond.",
                "By monitoring the node's Lease object in kube-node-lease; if no heartbeat renewal occurs within node-monitor-grace-period, the node is flagged NotReady.",
                "By polling the cloud provider's billing dashboard.",
                "By checking whether the containers on the node are serving HTTP 200."
            ],
            "answer": 1,
            "explanation": "Kubelets post periodic lease updates (heartbeats) every 10s; if missed beyond the grace period (default 40s), the controller marks the node NotReady."
        },
        {
            "question": "When a node transitions to NotReady, what taint is automatically applied to begin the pod eviction process?",
            "options": [
                "node.kubernetes.io/unreachable:NoExecute or node.kubernetes.io/not-ready:NoExecute",
                "node-role.kubernetes.io/control-plane:NoSchedule",
                "kubernetes.io/drain-active:PreferNoSchedule",
                "node.kubernetes.io/memory-pressure:AllowAll"
            ],
            "answer": 0,
            "explanation": "NoExecute taints evict pods immediately unless those pods specify a matching toleration with a tolerationSeconds grace window."
        }
    ],
    29: [
        {
            "question": "Why does a namespace sometimes become stuck in the Terminating state indefinitely?",
            "options": [
                "Because the cluster has run out of CPU capacity.",
                "Because one or more resources inside the namespace have finalizers that cannot be completed or cleared.",
                "Because the namespace name was longer than 10 characters.",
                "Because kube-proxy is running in iptables mode."
            ],
            "answer": 1,
            "explanation": "A namespace cannot be deleted until all resources within it are gone; if a custom resource or PVC has an unfulfilled finalizer, deletion hangs in Terminating."
        },
        {
            "question": "Which objects are NOT deleted when a namespace is deleted?",
            "options": [
                "Deployments and ReplicaSets in that namespace.",
                "Cluster-scoped objects like Nodes, PersistentVolumes, and ClusterRoles.",
                "Secrets and ConfigMaps in that namespace.",
                "Pods and Services in that namespace."
            ],
            "answer": 1,
            "explanation": "Namespace deletion cascades to all namespaced objects within its boundary, but cluster-scoped resources exist independently outside any namespace."
        }
    ],
    30: [
        {
            "question": "If a namespace has a ResourceQuota specifying limits on requests.cpu, what requirement is placed on all pods created in that namespace?",
            "options": [
                "Pods must run on bare metal servers.",
                "Every container in every submitted Pod must explicitly declare a CPU request, or a LimitRange must provide a default.",
                "Pods cannot use sidecar containers.",
                "Pods must be scheduled on the control-plane node."
            ],
            "answer": 1,
            "explanation": "If a quota restricts a resource type, the admission controller rejects any pod that fails to declare an explicit request/limit for that resource."
        },
        {
            "question": "At what point in the request lifecycle is a ResourceQuota enforced?",
            "options": [
                "By the kubelet when launching the container.",
                "By the ResourceQuota admission plugin in the kube-apiserver during API admission control.",
                "By the scheduler during node scoring.",
                "By CoreDNS when resolving DNS queries."
            ],
            "answer": 1,
            "explanation": "Quotas are enforced synchronously by admission controllers before the object is accepted and committed to etcd; violations return HTTP 403 Forbidden."
        }
    ],
    31: [
        {
            "question": "How does the Kubernetes Garbage Collector determine which dependent child objects to delete when a parent object is deleted?",
            "options": [
                "By scanning container image names for matches.",
                "By inspecting the metadata.ownerReferences field on child objects pointing to the parent UID.",
                "By searching for pods with matching creation timestamps.",
                "By asking the container runtime for process tree IDs."
            ],
            "answer": 1,
            "explanation": "Child resources (e.g. ReplicaSets created by a Deployment) maintain an ownerReferences array listing the parent's uid, kind, and apiVersion."
        },
        {
            "question": "What is the difference between Background cascading deletion and Orphan deletion?",
            "options": [
                "Background deletion deletes child objects after or alongside the parent; Orphan deletion leaves child objects running with their owner references cleared.",
                "Background deletion removes the cluster; Orphan deletion restores from backup.",
                "Orphan deletion is only used for temporary testing pods.",
                "Background deletion requires pausing the kubelet."
            ],
            "answer": 0,
            "explanation": "With propagationPolicy: Orphan, the parent is removed while child resources survive as unowned, standalone objects."
        }
    ],
    32: [
        {
            "question": "Why do modern Kubernetes deployments use Deployments instead of managing ReplicaSets directly?",
            "options": [
                "ReplicaSets cannot run on Linux.",
                "ReplicaSets do not provide declarative rolling updates, revision histories, or automated rollbacks; Deployments manage ReplicaSets to orchestrate those workflows.",
                "ReplicaSets only support a single replica.",
                "ReplicaSets bypass kube-proxy."
            ],
            "answer": 1,
            "explanation": "A ReplicaSet only maintains an exact pod count; it has no mechanism to update container images with zero downtime. Deployments orchestrate transitions between old and new ReplicaSets."
        },
        {
            "question": "What type of label selector syntax does a ReplicaSet support that the older ReplicationController lacked?",
            "options": [
                "SQL WHERE clauses.",
                "Set-based requirements (e.g. environment in (production, staging)).",
                "Regex evaluation on container logs.",
                "Plain text substring matching only."
            ],
            "answer": 1,
            "explanation": "ReplicaSets support rich set-based selectors (in, notin, exists), whereas legacy ReplicationControllers only supported exact equality (key = value)."
        }
    ],
    33: [
        {
            "question": "How does a Deployment perform a RollingUpdate without causing service downtime?",
            "options": [
                "It reboots all nodes simultaneously.",
                "It creates a new ReplicaSet and incrementally scales it up while scaling down the old ReplicaSet according to maxSurge and maxUnavailable parameters.",
                "It rewrites container binaries in-place inside running pods.",
                "It redirects traffic to an external maintenance page."
            ],
            "answer": 1,
            "explanation": "The Deployment controller creates a new ReplicaSet for the new revision and shifts traffic replica-by-replica, ensuring healthy pods always satisfy availability thresholds."
        },
        {
            "question": "How do you roll back a failed Deployment to its previous revision?",
            "options": [
                "By deleting the worker nodes.",
                "Using kubectl rollout undo deployment/<name>.",
                "By modifying the etcd Raft log manually.",
                "By restarting the kubelet daemon."
            ],
            "answer": 1,
            "explanation": "kubectl rollout undo instructs the Deployment controller to roll back the pod template spec to the previous recorded revision in its history."
        }
    ],
    34: [
        {
            "question": "Why does a StatefulSet require a Headless Service (clusterIP: None)?",
            "options": [
                "To encrypt pod network traffic with TLS.",
                "To provide predictable direct DNS A/SRV records for individual pods (e.g. pod-0.headless-svc.namespace.svc.cluster.local) rather than load-balancing across them.",
                "Because stateful applications cannot use IP addresses.",
                "To bypass the Linux kernel iptables rules."
            ],
            "answer": 1,
            "explanation": "Clustered stateful applications (databases, ZooKeeper, Kafka) need to address specific ordinal members directly for clustering and replication."
        },
        {
            "question": "When a StatefulSet replica pod is deleted or crashes, what happens to its PersistentVolumeClaim?",
            "options": [
                "The PVC is automatically deleted and recreated fresh.",
                "The PVC and storage are retained and automatically reattached to the replacement pod with the same ordinal index.",
                "The PVC is wiped and reformatted.",
                "The storage volume is converted into an emptyDir volume."
            ],
            "answer": 1,
            "explanation": "StatefulSet storage is persistent and sticky; data-web-0 is never deleted automatically when web-0 terminates, preserving data upon pod recreation."
        }
    ],
    35: [
        {
            "question": "What is the primary use case for a DaemonSet compared to a standard Deployment?",
            "options": [
                "Running short batch jobs that exit with code 0.",
                "Running cluster infrastructure agents (such as log shippers, monitoring agents, or CNI plugins) that must run exactly once on every eligible node.",
                "Running stateless web frontends behind an Ingress controller.",
                "Managing relational database failover."
            ],
            "answer": 1,
            "explanation": "A DaemonSet ensures that all (or some matching) nodes run a copy of a pod, automatically scaling as nodes are added or removed from the cluster."
        },
        {
            "question": "If a new worker node is added to a Kubernetes cluster, how does a DaemonSet respond?",
            "options": [
                "It waits for manual administrator approval before acting.",
                "The DaemonSet controller detects the new node and automatically schedules an agent pod onto it.",
                "It evicts pods from older nodes to free up licenses.",
                "It restarts all pods in the cluster."
            ],
            "answer": 1,
            "explanation": "The DaemonSet controller continuously watches for node additions and ensures immediate agent coverage without manual intervention."
        }
    ],
    36: [
        {
            "question": "What differentiates a Job's container lifecycle from a Deployment's container lifecycle?",
            "options": [
                "Jobs only run on Linux; Deployments run on Windows.",
                "A Job runs containers until a designated number of completions succeed (exit 0), whereas a Deployment continuously restarts containers to keep them running indefinitely.",
                "Job containers cannot access persistent volumes.",
                "Jobs bypass the Kubernetes API server."
            ],
            "answer": 1,
            "explanation": "Jobs supervise batch workloads designed to terminate upon completion; Deployments supervise persistent services designed to never terminate."
        },
        {
            "question": "What happens to a Job's pods after the workload has successfully completed?",
            "options": [
                "They are immediately deleted along with their logs.",
                "The pods are kept in Completed status so operators can inspect logs and exit statuses until the Job is cleaned up.",
                "The pods automatically transition to running web servers.",
                "The worker node is shut down."
            ],
            "answer": 1,
            "explanation": "Retaining completed pods allows operators to run kubectl logs and view output; automated cleanup can be managed via ttlSecondsAfterFinished."
        }
    ],
    37: [
        {
            "question": "What does the concurrencyPolicy: Forbid setting on a CronJob do if a previous job execution is still running when the next scheduled interval arrives?",
            "options": [
                "It kills the currently running job immediately.",
                "It skips the new execution until the currently running job has completed.",
                "It crashes the CronJob controller.",
                "It scales the worker node capacity."
            ],
            "answer": 1,
            "explanation": "Forbid prevents concurrent executions of the same job, avoiding duplicate batch processing or database lock contention."
        },
        {
            "question": "What Kubernetes object does the CronJob controller create when a scheduled trigger fires?",
            "options": [
                "A bare container process via SSH.",
                "A standard Job object, which in turn creates the execution pod.",
                "A StatefulSet.",
                "An Ingress rule."
            ],
            "answer": 1,
            "explanation": "CronJob operates as a higher-level orchestrator: on schedule, it instantiates a standard Job based on its jobTemplate."
        }
    ],
    38: [
        {
            "question": "Why is ReplicationController considered legacy in modern Kubernetes clusters?",
            "options": [
                "It cannot run in containerized environments.",
                "It was superseded by Deployments and ReplicaSets, which offer set-based selectors, declarative rolling updates, and rollback capabilities.",
                "It does not support Docker containers.",
                "It only works on single-node clusters."
            ],
            "answer": 1,
            "explanation": "ReplicationController was the original v1 replica primitive; Deployments and ReplicaSets replaced it with superior rollout orchestration and selector power."
        },
        {
            "question": "What label selector restriction does a ReplicationController have?",
            "options": [
                "It only supports equality-based selectors (key = value).",
                "It cannot select pods by label at all.",
                "It requires JSONPath expressions.",
                "It only works with pods named default."
            ],
            "answer": 0,
            "explanation": "ReplicationController only understands exact equality (app = frontend), while modern controllers support expressive set-based selectors (app in (frontend, api))."
        }
    ],
    39: [
        {
            "question": "What component must be running in the cluster for the HorizontalPodAutoscaler to scale based on CPU and memory utilization?",
            "options": [
                "An NFS storage server.",
                "The metrics-server (or a custom metrics provider implementing the Metrics API).",
                "Docker Desktop on macOS.",
                "A Ceph storage cluster."
            ],
            "answer": 1,
            "explanation": "HPA queries metrics.k8s.io to evaluate resource utilization; metrics-server collects container cgroup metrics from node kubelets and exposes them through this API."
        },
        {
            "question": "Why does HPA have a default stabilization window (typically 5 minutes) for scaling down replicas?",
            "options": [
                "Because the kube-apiserver is throttled to 1 write per 5 minutes.",
                "To prevent 'flapping' (rapid oscillation of scaling up and down in response to transient metric spikes).",
                "To allow container images to download.",
                "To wait for node operating system updates."
            ],
            "answer": 1,
            "explanation": "Rapid scaling oscillations degrade application stability; the cooldown window smooths out scale-down decisions over time."
        }
    ],
    40: [
        {
            "question": "What is the primary operational difference between HPA and VPA?",
            "options": [
                "HPA scales the number of Pod replicas (horizontal scaling), while VPA adjusts the CPU and memory requests/limits of existing containers (vertical scaling).",
                "HPA only works on worker nodes; VPA only works on the control plane.",
                "HPA scales storage; VPA scales networking.",
                "HPA requires Windows; VPA requires Linux."
            ],
            "answer": 0,
            "explanation": "HPA adds/removes pod replicas to handle load; VPA right-sizes individual container CPU and RAM requests based on historical consumption patterns."
        },
        {
            "question": "In updateMode: 'Auto', how does VPA apply updated CPU and memory recommendations to a running Pod?",
            "options": [
                "By dynamically adjusting kernel memory without restarting the container.",
                "By evicting the existing Pod so that the workload controller recreates it, at which point the VPA mutating admission webhook injects the new resource values.",
                "By editing the host BIOS settings.",
                "By changing the container image."
            ],
            "answer": 1,
            "explanation": "In current Kubernetes releases, pod resource changes require pod recreation; VPA evicts the pod and its admission webhook mutates the pod spec during recreation."
        }
    ],
    41: [
        {
            "question": "What type of disruptions does a Pod Disruption Budget (PDB) protect against?",
            "options": [
                "Involuntary disruptions like hardware power loss or kernel panics.",
                "Voluntary disruptions initiated by cluster administrators or automation, such as kubectl drain, node upgrades, and cluster autoscaler scale-down.",
                "Malicious cyberattacks on the network.",
                "Pod crashes caused by out-of-memory (OOM) errors."
            ],
            "answer": 1,
            "explanation": "PDBs govern voluntary management operations; they cannot prevent hardware crashes, but they intercept Eviction API calls during node maintenance to safeguard minimum available replicas."
        },
        {
            "question": "What happens if an administrator runs kubectl drain node-1 and evicting a pod would violate its PDB minAvailable constraint?",
            "options": [
                "The node drain immediately deletes the pod forcefully.",
                "The Eviction API rejects or delays the eviction request, causing kubectl drain to wait or retry until sufficient healthy replicas exist elsewhere.",
                "The PDB is automatically deleted.",
                "The entire cluster is placed in read-only mode."
            ],
            "answer": 1,
            "explanation": "The Eviction API checks active PDBs and returns HTTP 429 (Too Many Requests) if an eviction would breach the budget, protecting application availability during maintenance."
        }
    ]
}

print(f"Loaded {len(QUIZZES)} topic quizzes successfully.")
