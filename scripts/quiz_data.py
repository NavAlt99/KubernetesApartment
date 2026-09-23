# scripts/quiz_data.py
# Comprehensive engineering quiz questions across all 41 topics (246 questions, 6 per topic).

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
            },
            {
                    "question": "Which Linux kernel feature is responsible for isolating container process trees, network interfaces, and mount tables, as opposed to limiting compute consumption?",
                    "options": [
                            "Control Groups (cgroups)",
                            "Linux Namespaces (pid, net, mnt, ipc, uts, user)",
                            "Seccomp system call profiles",
                            "eBPF packet filters"
                    ],
                    "answer": 1,
                    "explanation": "Linux namespaces partition kernel resources so containers operate in isolated process spaces on shared Linux kernels, whereas cgroups enforce resource bandwidth constraints (CPU/RAM limits)."
            },
            {
                    "question": "When managing resources using `kubectl apply`, how does Kubernetes calculate which fields to update, delete, or retain?",
                    "options": [
                            "It performs a direct overwrite of all fields from the local file without reading the live object.",
                            "It computes a three-way diff between the local configuration manifest, the live cluster state, and the `kubectl.kubernetes.io/last-applied-configuration` annotation.",
                            "It sends an SSH payload to all worker nodes to rewrite local systemd unit files.",
                            "It hashes the manifest and rejects the update if any live field has diverged."
                    ],
                    "answer": 1,
                    "explanation": "Three-way merge apply compares the local file, the live API object in etcd, and the recorded last-applied annotation to merge changes without wiping out fields managed by other controllers (e.g., status or autoscalers)."
            },
            {
                    "question": "Which Linux kernel sysctl parameter is strictly required on worker nodes to allow packet forwarding between Pod network interfaces and physical network interfaces?",
                    "options": [
                            "net.ipv4.ip_forward = 1",
                            "kernel.pid_max = 1000",
                            "vm.swappiness = 100",
                            "fs.file-max = 65536"
                    ],
                    "answer": 0,
                    "explanation": "Linux kernel packet routing requires `net.ipv4.ip_forward = 1` so the host kernel forwards transit packets between virtual ethernet (veth) pairs and the host physical network adapter."
            },
            {
                    "question": "From an operational reliability perspective, why can a misconfigured Validating Admission Webhook with `failurePolicy: Fail` cause a cluster-wide outage?",
                    "options": [
                            "It permanently corrupts the Raft database file on disk.",
                            "If the webhook endpoint becomes unreachable, the API server rejects all matching resource requests (such as Pod creation and lease renewals) cluster-wide.",
                            "It forces the kubelet to restart every running container on worker nodes.",
                            "It revokes all worker node TLS bootstrap certificates."
                    ],
                    "answer": 1,
                    "explanation": "When `failurePolicy: Fail` is configured, if the webhook service crashes or network connectivity is lost, the API server must fail-closed and reject all matching admission requests, potentially freezing cluster deployments and controller operations."
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
            },
            {
                    "question": "What is the primary operational trade-off of a 'Stacked etcd' control plane topology compared to an 'External etcd' topology?",
                    "options": [
                            "Stacked topology requires more physical machines than external topology.",
                            "Stacked topology co-locates etcd with API servers on the same nodes, reducing machine count but increasing risk of resource contention between API server compute and etcd disk I/O.",
                            "Stacked topology does not support High Availability failover.",
                            "Stacked topology cannot run containerized workloads."
                    ],
                    "answer": 1,
                    "explanation": "In a stacked topology, etcd members run on the control plane nodes alongside kube-apiserver and controllers. This uses fewer machines but creates shared CPU, RAM, and disk I/O contention between API processing and etcd consensus."
            },
            {
                    "question": "How do worker nodes report health and liveliness to the control plane in modern Kubernetes to avoid heavy etcd write loads?",
                    "options": [
                            "By opening an SSH tunnel directly into the active etcd leader every 5 seconds.",
                            "By updating a lightweight `Lease` object in the `kube-node-lease` namespace at regular intervals (default every 10s).",
                            "By writing full Node status specifications into etcd every second.",
                            "By broadcasting ICMP ping packets across all master node physical interfaces."
                    ],
                    "answer": 1,
                    "explanation": "The NodeLease feature replaces heavy Node status heartbeats with lightweight micro-updates to `Lease` objects in `kube-node-lease`, drastically reducing etcd write amplification in large clusters."
            },
            {
                    "question": "What is the standard mechanism used to prevent general application Pods from being scheduled onto control plane nodes?",
                    "options": [
                            "A hardcoded kernel firewall rule blocking TCP traffic to control plane host IPs.",
                            "A node taint such as `node-role.kubernetes.io/control-plane:NoSchedule`, which normal Pods do not tolerate.",
                            "Completely disabling the kubelet service on control plane hosts.",
                            "Creating a ResourceQuota with `pods: 0` in every user namespace."
                    ],
                    "answer": 1,
                    "explanation": "Control plane nodes are marked with taints (traditionally `node-role.kubernetes.io/control-plane:NoSchedule` or `node-role.kubernetes.io/master:NoSchedule`). Only platform pods with matching tolerations can run there."
            },
            {
                    "question": "What is the key difference between running `kubectl cordon <node>` and `kubectl drain <node>`?",
                    "options": [
                            "Cordon deletes the node object from the cluster; drain reboots the operating system.",
                            "Cordon only marks the node unschedulable for new Pods; drain marks it unschedulable AND evicts existing running Pods.",
                            "Cordon kills all containers immediately with SIGKILL; drain gives a 30-minute grace period.",
                            "Cordon applies only to worker nodes; drain applies only to control plane nodes."
                    ],
                    "answer": 1,
                    "explanation": "`kubectl cordon` sets `spec.unschedulable: true` so no new pods are placed on the node. `kubectl drain` cordons the node and then calls the Eviction API to gracefully evict existing pods."
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
            },
            {
                    "question": "Why is the kube-apiserver described as completely stateless?",
                    "options": [
                            "It loses all authentication tokens whenever an administrator logs out of the terminal.",
                            "It does not persist any cluster state in its own memory or local disk; all durable state is stored in etcd.",
                            "It runs as a serverless function that shuts down after every HTTP request.",
                            "It communicates exclusively via UDP packets."
                    ],
                    "answer": 1,
                    "explanation": "kube-apiserver stores no state locally on disk or memory; it reads and writes all persistent object state directly to etcd. Because it is stateless, multiple API server instances can run active-active behind a load balancer."
            },
            {
                    "question": "What role does API Priority and Fairness (APF) play in kube-apiserver protection?",
                    "options": [
                            "It automatically encrypts Secret objects using external cloud KMS keys.",
                            "It classifies incoming requests into priority levels and flow schemas to prevent rogue or misconfigured clients from overwhelming the API server.",
                            "It balances network bandwidth equally between worker node ethernet interfaces.",
                            "It automatically scales the number of replica pods when CPU usage exceeds 80%."
                    ],
                    "answer": 1,
                    "explanation": "APF inspects incoming requests, assigns them to flow schemas and priority queues (e.g., exempt, system, leader-election, workload-high), and drops or throttles low-priority traffic during traffic spikes to protect critical control plane operations."
            },
            {
                    "question": "In the Kubernetes API schema hierarchy, what does GVR stand for?",
                    "options": [
                            "Gateway, VirtualService, Route",
                            "Group, Version, Resource",
                            "Global, Variable, Replica",
                            "Governance, Validation, Reconciliation"
                    ],
                    "answer": 1,
                    "explanation": "GVR stands for Group, Version, Resource (e.g., Group: `apps`, Version: `v1`, Resource: `deployments`). It defines the exact REST URL path exposed by the API server."
            },
            {
                    "question": "What is the purpose of Mutating Admission Webhooks versus Validating Admission Webhooks?",
                    "options": [
                            "Mutating webhooks can modify the incoming object spec (inject sidecars, defaults); Validating webhooks can only accept or reject the object.",
                            "Mutating webhooks check user RBAC permissions; Validating webhooks write to etcd.",
                            "Mutating webhooks run after the object is committed to etcd; Validating webhooks run before.",
                            "Mutating webhooks apply only to Nodes; Validating webhooks apply only to Pods."
                    ],
                    "answer": 0,
                    "explanation": "Mutating admission webhooks run first and can alter the submitted object (e.g., injecting proxy sidecars or security contexts). Validating webhooks run afterward and only return an accept/reject verdict."
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
            },
            {
                    "question": "Why is an odd number of members (such as 3 or 5) strongly recommended for an etcd cluster?",
                    "options": [
                            "Even-numbered clusters consume twice as much network bandwidth per Raft heartbeat.",
                            "Adding an even node increases cluster resource consumption without improving fault tolerance (a 4-node cluster still requires 3 for quorum, tolerating only 1 failure just like a 3-node cluster).",
                            "etcd refuses to start if it detects an even number of peer URLs in its configuration file.",
                            "Linux kernel bridge drivers cannot route multicast traffic across even node counts."
                    ],
                    "answer": 1,
                    "explanation": "Quorum is calculated as (N/2) + 1. In a 3-node cluster, quorum is 2 (tolerates 1 failure). In a 4-node cluster, quorum is 3 (still tolerates only 1 failure). Thus, the 4th node adds overhead without increasing fault tolerance."
            },
            {
                    "question": "When etcd disk space reaches its quota limit (default 2GB to 8GB), what happens to API server operations?",
                    "options": [
                            "etcd automatically purges the oldest half of all user namespaces.",
                            "etcd enters maintenance alarm mode and raises an `NOSPACE` alarm, rejecting all new write and update requests until compacted and defragmented.",
                            "The host operating system immediately kernel-panics to prevent data loss.",
                            "etcd automatically provisions an external cloud block storage volume."
                    ],
                    "answer": 1,
                    "explanation": "When space exceeds the storage quota, etcd raises an alarm and disables write operations to prevent database file corruption. Operators must compact revisions and run `etcdctl defrag` to reclaim space and disarm the alarm."
            },
            {
                    "question": "What is the difference between a linearizable read and a serializable read in etcd?",
                    "options": [
                            "Linearizable reads consult the Raft leader to verify it is still the legitimate leader before returning data; serializable reads return local data immediately, risking stale reads.",
                            "Linearizable reads are cached in Redis; serializable reads bypass cache.",
                            "Linearizable reads only return binary data; serializable reads return JSON.",
                            "Linearizable reads are executed on worker nodes; serializable reads run on control plane nodes."
                    ],
                    "answer": 0,
                    "explanation": "Linearizable (quorum) reads ensure you never read stale data by confirming leader lease with quorum before responding. Serializable reads read directly from local member state without contacting quorum, offering lower latency but risking stale reads."
            },
            {
                    "question": "Which command sequence correctly performs an offline restore of an etcd snapshot onto a new cluster node?",
                    "options": [
                            "kubectl apply -f etcd-snapshot.db",
                            "etcdctl snapshot restore /backup/etcd-snapshot.db --data-dir=/var/lib/etcd-restored",
                            "systemctl restart etcd --import-snapshot=/backup/etcd-snapshot.db",
                            "etcd-tool --restore --all-namespaces /backup/etcd-snapshot.db"
                    ],
                    "answer": 1,
                    "explanation": "`etcdctl snapshot restore <file> --data-dir=<new-dir>` initializes a fresh etcd data directory from the snapshot before etcd is started."
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
            },
            {
                    "question": "In the scheduling cycle of kube-scheduler, what are the two primary phases executed for each unscheduled Pod?",
                    "options": [
                            "Authentication and Authorization",
                            "Filtering (Predicates) and Scoring (Priorities)",
                            "Eviction and Preemption",
                            "Image Pulling and Sandbox Initialization"
                    ],
                    "answer": 1,
                    "explanation": "kube-scheduler first executes Filtering (eliminating nodes that do not meet requirements like compute, taints, ports), then Scoring (ranking eligible candidate nodes according to priority functions to pick the best host)."
            },
            {
                    "question": "What is the key difference between `requiredDuringSchedulingIgnoredDuringExecution` and `preferredDuringSchedulingIgnoredDuringExecution` in node affinity?",
                    "options": [
                            "Required is a hard constraint (pod stays Pending if no node matches); Preferred is a soft preference (scheduler will schedule on non-matching node if necessary).",
                            "Required runs before pod creation; Preferred runs after pod creation.",
                            "Preferred will evict the pod if node labels change later; Required will not.",
                            "Required is deprecated in Kubernetes 1.25+; Preferred is the only supported syntax."
                    ],
                    "answer": 0,
                    "explanation": "`requiredDuringScheduling...` acts as a hard requirement that must be satisfied for scheduling. `preferredDuringScheduling...` assigns weighted preference points to matching nodes, but does not block scheduling if no match exists."
            },
            {
                    "question": "What occurs when a higher-priority Pod with a `PriorityClass` cannot find any node with sufficient compute resources?",
                    "options": [
                            "The API server automatically doubles the CPU clock frequency of worker nodes.",
                            "kube-scheduler initiates Preemption, evicting lower-priority Pods from a candidate node to make room for the higher-priority Pod.",
                            "The higher-priority Pod is immediately converted into a DaemonSet.",
                            "The scheduler crashes with an unhandled exception."
                    ],
                    "answer": 1,
                    "explanation": "If a high-priority pod cannot be scheduled, kube-scheduler identifies a candidate node and evicts lower-priority victim pods so the high-priority workload can bind."
            },
            {
                    "question": "When configuring Pod anti-affinity to ensure that no two replicas of a database run on the same physical server, what should the `topologyKey` be set to?",
                    "options": [
                            "kubernetes.io/os",
                            "kubernetes.io/hostname",
                            "topology.kubernetes.io/zone",
                            "node.kubernetes.io/instance-type"
                    ],
                    "answer": 1,
                    "explanation": "`topologyKey: kubernetes.io/hostname` scopes the anti-affinity domain to individual hostnames, ensuring no two matching pods land on the same physical or virtual host."
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
            },
            {
                    "question": "What concurrency and high-availability mechanism does `kube-controller-manager` use when multiple instances run across control plane nodes?",
                    "options": [
                            "Active-Active round-robin load balancing of controller loops across all instances.",
                            "Active-Passive leader election using a Lease lock in `kube-system`; only the elected leader runs control loops while standbys idle.",
                            "Shared memory IPC over high-speed InfiniBand links.",
                            "Sharding controllers across nodes based on namespace alphabetical order."
                    ],
                    "answer": 1,
                    "explanation": "To prevent split-brain dual-reconciliation where multiple instances issue conflicting changes, `kube-controller-manager` uses an active-passive leader election lock. Only the active leader executes controllers."
            },
            {
                    "question": "Which architectural concept explains why Kubernetes controllers can self-heal after extended network partitions or restarts without missing events?",
                    "options": [
                            "Edge-triggered event delivery only",
                            "Level-triggered reconciliation loops comparing desired state against actual state continuously",
                            "Storing past event logs in local SQLite databases",
                            "Mandatory daily reboots of all worker nodes"
                    ],
                    "answer": 1,
                    "explanation": "Kubernetes is level-triggered rather than edge-triggered: controllers observe the current actual state and drive it toward desired state, meaning missed transient edge events do not prevent reconciliation once connectivity resumes."
            },
            {
                    "question": "If a platform administrator wants to disable only the Route and ServiceAccountToken controllers in kube-controller-manager, which command-line flag is used?",
                    "options": [
                            "--disable-controllers=route,serviceaccount-token",
                            "--controllers=*, -route, -serviceaccount-token",
                            "--exclude-controllers=route,serviceaccount-token",
                            "--skip-controllers=route,serviceaccount-token"
                    ],
                    "answer": 1,
                    "explanation": "The `--controllers` flag accepts a comma-separated list of controllers where `*` includes all default controllers and prefixing with `-` excludes specific controllers (e.g. `*, -route, -serviceaccount-token`)."
            },
            {
                    "question": "What internal client-go caching component do controllers use to efficiently watch API resources without polling the API server?",
                    "options": [
                            "Redis Cache Client",
                            "SharedInformer with Reflector, DeltaFIFO queue, and Local Indexer Cache",
                            "Direct raw TCP socket dump",
                            "Local file-based SQLite replica"
                    ],
                    "answer": 1,
                    "explanation": "client-go's `SharedInformer` establishes a watch stream with the API server, maintains an in-memory cached index (Lister), and dispatches add/update/delete notifications to worker queues, avoiding API server polling overhead."
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
            },
            {
                    "question": "What was the primary architectural motivation behind moving cloud provider code out of `kube-controller-manager` into `cloud-controller-manager`?",
                    "options": [
                            "To force cloud providers to write their integrations in Python instead of Go.",
                            "To decouple cloud provider release cycles and private SDKs from core Kubernetes releases, allowing independent development and out-of-tree plugins.",
                            "To eliminate the need for container runtimes on worker nodes.",
                            "To make Kubernetes compatible only with private on-premises hardware."
                    ],
                    "answer": 1,
                    "explanation": "In-tree cloud providers tightly coupled vendor SDKs to the Kubernetes core binary. Out-of-tree `cloud-controller-manager` enables cloud vendors to release fixes and features without waiting for upstream Kubernetes releases."
            },
            {
                    "question": "Which specific controller inside `cloud-controller-manager` is responsible for querying the cloud provider API to delete Kubernetes Node objects when a cloud VM is destroyed?",
                    "options": [
                            "Route Controller",
                            "Node Lifecycle Controller (Node Controller)",
                            "Service Controller",
                            "PersistentVolume Controller"
                    ],
                    "answer": 1,
                    "explanation": "The cloud-controller-manager's node controller queries cloud infrastructure APIs to verify whether an instance still exists. If the VM was terminated in the cloud, it cleans up the corresponding Kubernetes Node object."
            },
            {
                    "question": "What task does the Route Controller inside `cloud-controller-manager` perform?",
                    "options": [
                            "It programs DNS records inside CoreDNS.",
                            "It configures cloud VPC routing tables so packets destined for a node's Pod CIDR are forwarded to that node's cloud VM IP.",
                            "It generates TLS certificates for Ingress controllers.",
                            "It manages SSH authorized keys for node access."
                    ],
                    "answer": 1,
                    "explanation": "In clouds with non-overlay VPC routing, the Route Controller configures the cloud VPC route table so traffic destined for a pod subnet assigned to a specific worker node is routed to that node's VM interface."
            },
            {
                    "question": "Which node label is automatically applied by cloud-controller-manager to indicate the physical failure domain of an instance?",
                    "options": [
                            "topology.kubernetes.io/zone and topology.kubernetes.io/region",
                            "hardware.architecture/rack-number",
                            "cloud.provider/datacenter-room",
                            "kubernetes.io/physical-server-bay"
                    ],
                    "answer": 0,
                    "explanation": "cloud-controller-manager queries cloud instance metadata and populates standard topology labels: `topology.kubernetes.io/zone` (e.g. `us-east-1a`) and `topology.kubernetes.io/region` (e.g. `us-east-1`)."
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
            },
            {
                    "question": "How does the Kubelet discover and maintain Static Pods without communicating with the kube-scheduler?",
                    "options": [
                            "It queries an external Git repository every 60 seconds.",
                            "It scans a local host filesystem directory (such as `/etc/kubernetes/manifests`) for YAML files using inotify filesystem watches.",
                            "It reads static pod configurations from worker node BIOS NVRAM.",
                            "It listens on a raw UDP multicast port broadcast by the control plane."
                    ],
                    "answer": 1,
                    "explanation": "Static Pods are defined directly on the node filesystem (configured via `staticPodPath` in Kubelet configuration). Kubelet monitors the folder and directly starts and restarts the containers via the local CRI runtime."
            },
            {
                    "question": "What is the purpose of the 'Mirror Pod' that the Kubelet creates in the kube-apiserver for every local Static Pod?",
                    "options": [
                            "It provides visibility of the Static Pod to cluster administrators and allows `kubectl get pods` to display its status.",
                            "It runs a backup copy of the container on a worker node in case the control plane fails.",
                            "It proxies HTTP network traffic from user namespaces into the static container.",
                            "It allows the kube-scheduler to migrate the Static Pod to another host."
                    ],
                    "answer": 0,
                    "explanation": "Mirror Pods are read-only representations in the API server that allow operators to view static pod status via `kubectl`. Deleting a mirror pod via `kubectl delete` does not delete the static pod; the Kubelet simply recreates the mirror."
            },
            {
                    "question": "What happens when a node's filesystem disk usage exceeds the Kubelet's `imageGCHighThresholdPercent` (default 85%)?",
                    "options": [
                            "The Kubelet immediately formats the node's disk partition.",
                            "The Kubelet initiates image garbage collection, deleting unused container images until disk usage drops below `imageGCLowThresholdPercent` (default 80%).",
                            "The Kubelet terminates all Running pods with exit code 137.",
                            "The Kubelet disables all network interfaces on the node."
                    ],
                    "answer": 1,
                    "explanation": "Image garbage collection triggers when disk usage crosses `imageGCHighThresholdPercent`, removing unreferenced images in order of least recently used until usage falls back below the low threshold."
            },
            {
                    "question": "Why is it mandatory for the Kubelet's cgroup driver (`cgroupDriver`) to match the container runtime's cgroup driver (typically `systemd`) on modern Linux distributions?",
                    "options": [
                            "Mismatched drivers cause the Linux kernel to refuse mounting ext4 partitions.",
                            "Having two different cgroup managers (e.g., Kubelet using cgroupfs while containerd uses systemd) creates split resource accounting and leads to node instability under memory pressure.",
                            "systemd only supports single-core CPU processors.",
                            "Kubernetes requires cgroupfs for IPv6 network routing."
                    ],
                    "answer": 1,
                    "explanation": "When systemd is the init system, having Kubelet allocate cgroups via `cgroupfs` while containerd allocates via `systemd` results in conflicting cgroup hierarchies, inaccurate resource tracking, and failed process evictions under load."
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
            },
            {
                    "question": "Why does `kube-proxy` operating in IPVS mode scale better in clusters with tens of thousands of Services compared to iptables mode?",
                    "options": [
                            "IPVS compiles packet routing rules directly into Python scripts.",
                            "IPVS uses hash tables with O(1) lookup complexity, whereas iptables uses sequential rule lists with O(n) traversal latency.",
                            "IPVS runs in user-space, avoiding kernel context switches.",
                            "IPVS eliminates the need for network interface cards."
                    ],
                    "answer": 1,
                    "explanation": "In iptables mode, packet processing traverses sequential chains of rules whose evaluation cost grows linearly O(n) with service count. IPVS uses kernel hash tables offering near-constant O(1) latency regardless of service scale."
            },
            {
                    "question": "What is the primary benefit and trade-off of setting `externalTrafficPolicy: Local` on a Service of type NodePort or LoadBalancer?",
                    "options": [
                            "Benefit: Preserves client source IP and avoids extra network hops; Trade-off: Potential uneven traffic distribution if pods are not evenly distributed across all nodes.",
                            "Benefit: Enables automatic gzip compression; Trade-off: Disables TLS termination.",
                            "Benefit: Encrypts packet payloads; Trade-off: Doubles CPU consumption.",
                            "Benefit: Allows routing across external internet gateways; Trade-off: Disables DNS resolution."
                    ],
                    "answer": 0,
                    "explanation": "Setting `externalTrafficPolicy: Local` prevents kube-proxy from SNATing the client IP to the node IP and only forwards traffic to local pods on the entry node, preserving the client IP address but dropping or skewing traffic if that node lacks pod endpoints."
            },
            {
                    "question": "What Linux kernel table does `kube-proxy` rely on in iptables mode to track bi-directional connection states for translated Service IPs?",
                    "options": [
                            "ARP cache table",
                            "Netfilter Connection Tracking (conntrack) table",
                            "BGP routing table",
                            "DNS lookup table"
                    ],
                    "answer": 1,
                    "explanation": "Netfilter's `conntrack` facility tracks stateful network flows so reply packets from backend pods can be un-DNATed back to the original cluster virtual IP and returned to the client seamlessly."
            },
            {
                    "question": "Which Kubernetes API resource replaced the legacy `Endpoints` resource to improve kube-proxy performance and control plane scalability in large clusters?",
                    "options": [
                            "IngressRoute",
                            "EndpointSlice",
                            "ServiceMesh",
                            "VirtualIPMap"
                    ],
                    "answer": 1,
                    "explanation": "The `EndpointSlice` resource breaks large monolithic Endpoints objects (which had to be re-sent entirely on any single pod change) into scalable chunks of 100 endpoints by default, drastically lowering API bandwidth and kube-proxy processing time."
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
            },
            {
                    "question": "In the modern Kubernetes container execution hierarchy, what is the role of `containerd-shim`?",
                    "options": [
                            "It compiles Go source code inside the container during startup.",
                            "It serves as a lightweight parent process for the container, holding stdin/stdout/stderr pipes and exit status open so the container daemon (`containerd`) can restart without terminating running containers.",
                            "It manages node-level DNS caching.",
                            "It allocates persistent disk volumes from cloud storage providers."
                    ],
                    "answer": 1,
                    "explanation": "`containerd-shim` sits between containerd and runc. It holds container file descriptors open, captures exit codes, and allows daemonless containers that remain running even if containerd is restarted or upgraded."
            },
            {
                    "question": "Which CLI diagnostic tool is specifically designed for inspecting and troubleshooting the Kubernetes CRI runtime directly on a worker node without relying on Docker?",
                    "options": [
                            "kubectl",
                            "crictl",
                            "kubeadm",
                            "systemd-analyze"
                    ],
                    "answer": 1,
                    "explanation": "`crictl` is the official CRI-compatible debugging CLI tool maintained by the Kubernetes SIG-node community, designed specifically to inspect pods, containers, and images through the CRI gRPC interface."
            },
            {
                    "question": "What is the purpose of configuring a `RuntimeClass` in Kubernetes?",
                    "options": [
                            "To select the JVM version used by Java web applications.",
                            "To select alternative OCI runtimes (such as gVisor `runsc` for kernel sandbox isolation or Kata Containers for lightweight VM isolation) for specific Pod workloads.",
                            "To assign priority classes to batch jobs.",
                            "To enforce storage quotas on local volumes."
                    ],
                    "answer": 1,
                    "explanation": "`RuntimeClass` allows cluster administrators to define different container runtimes (e.g., standard `runc`, sandbox-isolated `runsc`, or hardware-virtualized `kata`) and allow pods to select them via `spec.runtimeClassName`."
            },
            {
                    "question": "What happens when a container image is specified with a tag like `:latest` and `imagePullPolicy` is omitted?",
                    "options": [
                            "The image is never pulled if an image with the same name exists locally.",
                            "The pull policy defaults to `Always`, forcing the Kubelet to contact the registry to check whether a newer digest exists before starting the container.",
                            "The Kubelet fails container creation with an ErrImageNeverPull error.",
                            "The image is compiled from the nearest git branch."
                    ],
                    "answer": 1,
                    "explanation": "When an image tag is `:latest` or omitted, `imagePullPolicy` defaults to `Always`. For any explicit version tag (e.g. `:v1.2.3`), it defaults to `IfNotPresent`."
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
            },
            {
                    "question": "What is the primary role of the `pause` container (infrastructure container) in a Kubernetes Pod?",
                    "options": [
                            "It pauses execution of containers when CPU usage exceeds 90%.",
                            "It initializes and holds the shared Linux namespaces (Network, IPC) so application containers can join the same network space and communicate over localhost.",
                            "It performs periodic health checks against worker node disks.",
                            "It compiles container logs into Prometheus metrics."
                    ],
                    "answer": 1,
                    "explanation": "The pause container serves as the parent anchor for the Pod sandbox. It requests and holds the network interface and IPC namespaces open; if an application container restarts, the pod's IP and port bindings remain intact."
            },
            {
                    "question": "When a Pod is being terminated gracefully, what sequence of events occurs on the worker node?",
                    "options": [
                            "The Kubelet immediately sends SIGKILL to all processes and wipes the disk.",
                            "The Kubelet executes any configured `preStop` lifecycle hooks, sends `SIGTERM` to container processes, waits up to `terminationGracePeriodSeconds` (default 30s), and sends `SIGKILL` only if processes have not exited.",
                            "The Kubelet pauses all other pods on the node until the target container shuts down.",
                            "The Kubelet drains the node's memory into swap space."
                    ],
                    "answer": 1,
                    "explanation": "Graceful termination runs `preStop` hooks first, sends `SIGTERM` to allow in-flight connections to finish, waits for the grace period (default 30s), and issues `SIGKILL` as a last resort."
            },
            {
                    "question": "What is the difference between a Pod's `restartPolicy: Always` versus `restartPolicy: OnFailure`?",
                    "options": [
                            "Always restarts containers regardless of exit status (0 or non-zero); OnFailure restarts only if the container exits with a non-zero error code.",
                            "Always applies to worker nodes; OnFailure applies only to the control plane.",
                            "Always restarts the host machine; OnFailure restarts only the Docker daemon.",
                            "Always is used exclusively for batch Jobs; OnFailure is used for Deployments."
                    ],
                    "answer": 0,
                    "explanation": "`Always` ensures containers are continually restarted even after clean exits (code 0), which is standard for long-running services. `OnFailure` restarts containers only on non-zero exit codes (crashes), standard for batch jobs."
            },
            {
                    "question": "How do multiple containers in the same Pod access shared local storage?",
                    "options": [
                            "By opening an NFS socket between their respective IP addresses.",
                            "By declaring a shared `volume` in `spec.volumes` (e.g. `emptyDir: {}`) and mounting it in each container's `volumeMounts`.",
                            "By writing directly to the host's `/root` directory.",
                            "Containers in the same pod cannot share filesystem volumes."
                    ],
                    "answer": 1,
                    "explanation": "Volumes defined at the Pod level can be mounted into any or all containers in that Pod at chosen mount paths, enabling fast in-memory or disk file sharing between co-located containers."
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
            },
            {
                    "question": "In Kubernetes 1.28+, how are native sidecar containers configured in a Pod specification?",
                    "options": [
                            "Inside a top-level `spec.sidecars` field.",
                            "Inside `spec.initContainers` with `restartPolicy: Always`.",
                            "Inside `metadata.annotations` with `sidecar.istio.io/inject: true`.",
                            "Inside `spec.containers` with `role: sidecar`."
                    ],
                    "answer": 1,
                    "explanation": "Native sidecars are defined within `spec.initContainers` having `restartPolicy: Always`. They start before regular application containers and remain running for the entire lifecycle of the Pod."
            },
            {
                    "question": "What problem does the native sidecar feature solve compared to traditional legacy multi-container Pod patterns?",
                    "options": [
                            "It eliminates the need for container images.",
                            "It guarantees that helper services (such as logging or service mesh proxies) start before app containers begin and terminate gracefully after app containers finish.",
                            "It reduces container memory consumption to zero.",
                            "It bypasses Linux cgroup CPU bandwidth throttling."
                    ],
                    "answer": 1,
                    "explanation": "Legacy sidecars were regular containers with no deterministic startup or shutdown ordering, causing app containers to fail if proxies weren't ready, or preventing batch jobs from completing because the sidecar never exited."
            },
            {
                    "question": "How do Service Mesh sidecars (such as Envoy in Istio or Linkerd) transparently intercept inbound and outbound TCP traffic for an application container?",
                    "options": [
                            "By modifying the application source code at compile time.",
                            "By using an init container (running with `NET_ADMIN` capability) to configure iptables PREROUTING and OUTPUT rules that redirect traffic to the sidecar's localhost proxy port.",
                            "By assigning a separate IP address to the sidecar container.",
                            "By intercepting packets at the hardware router layer."
                    ],
                    "answer": 1,
                    "explanation": "An `istio-init` container runs with `CAP_NET_ADMIN` to inject iptables rules into the Pod's shared network namespace, redirecting incoming and outgoing TCP flows to Envoy's local listening port (typically 15001/15006)."
            },
            {
                    "question": "How are compute resource requests (CPU and Memory) calculated for a Pod running both an application container and a sidecar container?",
                    "options": [
                            "The Kubelet only accounts for the larger container's resources.",
                            "The Pod's total resource request is the sum of the requests of all running application and sidecar containers.",
                            "Sidecars do not consume Pod quota and run without resource tracking.",
                            "The scheduler ignores sidecar limits during node placement."
                    ],
                    "answer": 1,
                    "explanation": "Because regular and native sidecars run concurrently throughout the Pod lifecycle, the scheduler and kubelet calculate the Pod's total resource requests by summing the requests of all active containers."
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
            },
            {
                    "question": "In what order do multiple Init Containers execute within a Pod?",
                    "options": [
                            "In parallel simultaneously to minimize startup latency.",
                            "Sequentially, in the exact order they are defined in `spec.initContainers`, with each completing successfully before the next begins.",
                            "In reverse alphabetical order based on their container name.",
                            "In random order determined by the Kubelet."
                    ],
                    "answer": 1,
                    "explanation": "Init containers run strictly sequentially. Each init container must run to completion with exit code 0 before the next init container is started. If any fails, the pod restarts according to its `restartPolicy`."
            },
            {
                    "question": "Which of the following probe types is supported on standard Init Containers?",
                    "options": [
                            "LivenessProbe",
                            "ReadinessProbe",
                            "StartupProbe",
                            "None of the above (standard init containers do not support probes)"
                    ],
                    "answer": 3,
                    "explanation": "Standard init containers do not support readiness, liveness, or startup probes because their readiness is directly defined by process termination with exit code 0."
            },
            {
                    "question": "What is a major security advantage of performing database schema migrations or security credential downloads in an Init Container rather than the main application container?",
                    "options": [
                            "Init containers are immune to Linux kernel vulnerabilities.",
                            "Migration tools, compiler toolchains, or administrative database credentials do not need to be present inside the final production application container image.",
                            "Init containers run without using network interfaces.",
                            "Init containers bypass Kubernetes RBAC policies."
                    ],
                    "answer": 1,
                    "explanation": "Separating setup into an init container keeps the runtime application container image minimal and secure (distroless), removing administrative tools, database migration utilities, and elevated credentials from the long-running attack surface."
            },
            {
                    "question": "How does the Kubernetes scheduler calculate effective resource requests for a Pod with multiple Init Containers?",
                    "options": [
                            "It takes the sum of all init containers plus all app containers.",
                            "It takes the maximum of: (the highest init container request) or (the sum of all app/sidecar container requests).",
                            "It completely ignores init container resource requests.",
                            "It doubles the memory requested by the first init container."
                    ],
                    "answer": 1,
                    "explanation": "Because init containers run sequentially, only one runs at a time. Therefore, the scheduler computes the effective request as `max(max(init_container_requests), sum(app_container_requests))`."
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
            },
            {
                    "question": "What are the fundamental tenets of the Kubernetes network model that every CNI plugin must satisfy?",
                    "options": [
                            "All pods share a single IP address and communicate using port offsets.",
                            "Every pod receives a unique IP address reachable by every other pod in the cluster without NAT, and node agents (kubelet) can communicate with all pods on that node.",
                            "Pods can only communicate with other pods running on the exact same physical host.",
                            "All pod traffic must route through an external internet proxy."
                    ],
                    "answer": 1,
                    "explanation": "The Kubernetes IP-per-Pod model requires that all pods communicate with all other pods across nodes without NAT, and agents on a node can reach all pods on that same node directly."
            },
            {
                    "question": "On Linux hosts running an overlay CNI (such as Calico VXLAN or Flannel), why must the CNI interface MTU be set lower than the physical host network MTU (e.g. 1450 vs 1500)?",
                    "options": [
                            "To account for the 50-byte encapsulation header (Ethernet + IP + UDP + VXLAN) and prevent packet fragmentation.",
                            "Because Linux kernel bridges do not support MTUs above 1450.",
                            "To reduce memory consumption inside containerd.",
                            "To comply with Wi-Fi 802.11 standards."
                    ],
                    "answer": 0,
                    "explanation": "VXLAN encapsulation adds outer IP, UDP, and VXLAN headers (typically 50 bytes). If the CNI MTU matches the host MTU (1500), inner packets exceeding 1450 bytes will exceed physical MTU, causing silent packet drops or fragmentation."
            },
            {
                    "question": "Where are CNI network configuration files and executable binaries stored on a standard Linux Kubernetes node?",
                    "options": [
                            "Config: `/etc/cni/net.d/`, Binaries: `/opt/cni/bin/`",
                            "Config: `/var/log/cni/`, Binaries: `/usr/bin/`",
                            "Config: `/etc/kubernetes/manifests/`, Binaries: `/tmp/`",
                            "Config: `/home/cni/`, Binaries: `/sbin/`"
                    ],
                    "answer": 0,
                    "explanation": "Standard CNI paths on Linux are `/etc/cni/net.d/` for JSON configuration files (read by the runtime in lexicographical order) and `/opt/cni/bin/` for CNI plugin binaries (bridge, loopback, host-local, calico, cilium)."
            },
            {
                    "question": "What is the primary operational advantage of eBPF-based CNI implementations (such as Cilium or Calico eBPF mode) over traditional iptables-based CNI networking?",
                    "options": [
                            "eBPF allows containers to run without Docker.",
                            "eBPF programs attach directly to kernel socket and network hooks (tc/xdp), bypassing iptables rule evaluation and connection tracking for significantly lower latency and higher throughput.",
                            "eBPF encrypts all cluster memory using hardware TPMs.",
                            "eBPF eliminates the need for worker nodes."
                    ],
                    "answer": 1,
                    "explanation": "eBPF attaches programs directly to Linux network interface layers (traffic control `tc` and eXpress Data Path `xdp`), routing packets directly in kernel space without the overhead of traversing hundreds of iptables chains and conntrack locks."
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
            },
            {
                    "question": "In what order are plugins evaluated inside the CoreDNS `Corefile`?",
                    "options": [
                            "In the exact order they are written line-by-line in the Corefile.",
                            "In a predefined compile-time plugin order determined by `plugin.cfg` in the CoreDNS binary, regardless of their line order in the Corefile.",
                            "In alphabetical order based on plugin name.",
                            "In random order determined at server startup."
                    ],
                    "answer": 1,
                    "explanation": "CoreDNS plugin execution order is determined at compile time by the ordering in `plugin.cfg`, not the order in which directives appear in the Corefile ConfigMap."
            },
            {
                    "question": "What DNS records are returned when querying a Headless Service (`spec.clusterIP: None`) compared to a standard ClusterIP Service?",
                    "options": [
                            "A Headless Service returns a CNAME pointing to google.com.",
                            "A standard Service returns the single virtual ClusterIP; a Headless Service returns multiple `A` records containing the direct IP addresses of all ready backend Pods.",
                            "A Headless Service returns an error because it has no virtual IP.",
                            "A Headless Service returns the IP address of the kube-apiserver."
                    ],
                    "answer": 1,
                    "explanation": "A standard Service returns its single virtual ClusterIP. A Headless Service (`clusterIP: None`) has no virtual IP; CoreDNS resolves queries directly to the set of individual ready Pod IPs (A/AAAA records)."
            },
            {
                    "question": "Why does setting `options ndots:5` in `/etc/resolv.conf` create extra network overhead for external domain queries (like `api.stripe.com`)?",
                    "options": [
                            "It encrypts all DNS requests with 5 separate keys.",
                            "Any hostname containing fewer than 5 dots is treated as an incomplete local name and appended to every local search domain (e.g. `api.stripe.com.default.svc.cluster.local`) before querying the root domain.",
                            "It forces CoreDNS to query 5 different external DNS servers simultaneously.",
                            "It restricts queries to 5 packets per second."
                    ],
                    "answer": 1,
                    "explanation": "With `ndots:5`, any domain with fewer than 5 dots is checked sequentially against all search domains (`<ns>.svc.cluster.local`, `svc.cluster.local`, `cluster.local`) first. Each external lookup incurs 3-4 failed DNS queries before resolving."
            },
            {
                    "question": "What is the primary role of the `NodeLocal DNSCache` daemon in large Kubernetes clusters?",
                    "options": [
                            "It stores DNS query records in etcd for compliance auditing.",
                            "It runs a caching DNS agent on a link-local IP (`169.254.20.10`) on every worker node, serving queries locally to eliminate conntrack UDP race conditions and reduce CoreDNS control plane load.",
                            "It synchronizes external cloud Route53 records.",
                            "It forces all DNS queries to use IPv6."
                    ],
                    "answer": 1,
                    "explanation": "NodeLocal DNSCache runs a local cache instance on each node listening on a link-local address. Pods query localhost, reducing CoreDNS network traffic and avoiding Linux conntrack UDP race conditions that cause sporadic 5-second DNS timeouts."
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
            },
            {
                    "question": "In a Kubernetes Service manifest, what is the distinction between `port` and `targetPort`?",
                    "options": [
                            "`port` is the port exposed on the Service's virtual ClusterIP; `targetPort` is the actual port the application container listens on inside the backend Pod.",
                            "`port` is for UDP traffic; `targetPort` is for TCP traffic.",
                            "`port` is the host node port; `targetPort` is the proxy port.",
                            "`port` is deprecated in Kubernetes 1.29+."
                    ],
                    "answer": 0,
                    "explanation": "`spec.ports[*].port` defines the listening port exposed by the Service abstraction itself inside the cluster. `spec.ports[*].targetPort` defines the destination container port on the backend Pod to which packets are forwarded."
            },
            {
                    "question": "Why does pinging a Service's virtual ClusterIP (e.g. `ping 10.96.0.1`) typically fail, even when the Service is routing HTTP traffic properly?",
                    "options": [
                            "ClusterIP addresses are virtual entries in iptables/IPVS rules that translate specific TCP/UDP transport ports; they are not real physical network interfaces and do not respond to ICMP Echo packets.",
                            "The Linux kernel permanently disables ICMP in containerized environments.",
                            "ClusterIPs require an active BGP session to respond to pings.",
                            "CoreDNS blocks ICMP packets by default."
                    ],
                    "answer": 0,
                    "explanation": "A ClusterIP does not exist as an interface or ARP responder on any host; it exists solely as a destination translation target in iptables/IPVS for specified TCP/UDP ports. ICMP ping packets have no port and are dropped."
            },
            {
                    "question": "What requirement must be met when defining a Kubernetes Service with multiple ports in `spec.ports`?",
                    "options": [
                            "All ports must use the UDP protocol.",
                            "Every port entry in `spec.ports` must have a unique `name` assigned to it.",
                            "The Service type must be LoadBalancer.",
                            "The Service must use `clusterIP: None`."
                    ],
                    "answer": 1,
                    "explanation": "When multiple ports are defined in a Service, Kubernetes requires each port to specify a unique `name` (e.g. `name: http` and `name: https`) to prevent ambiguity in EndpointSlice and DNS SRV records."
            },
            {
                    "question": "How can an operator configure a Service to route subsequent requests from the same client IP to the same backend Pod?",
                    "options": [
                            "By setting `spec.sessionAffinity: ClientIP` on the Service.",
                            "By enabling HTTP cookies in kube-proxy.",
                            "By creating a StatefulSet with ordinal routing.",
                            "By assigning a static MAC address to the pod."
                    ],
                    "answer": 0,
                    "explanation": "Setting `spec.sessionAffinity: ClientIP` instructs kube-proxy to program iptables/IPVS rules that map connections from the same client IP address to the same backend pod for a configurable timeout period."
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
            },
            {
                    "question": "What is the relationship between the three primary Kubernetes Service types: ClusterIP, NodePort, and LoadBalancer?",
                    "options": [
                            "They are mutually exclusive and operate on completely different network OSI layers.",
                            "They form a strict superset hierarchy: A NodePort is automatically a ClusterIP, and a LoadBalancer is automatically both a NodePort and a ClusterIP.",
                            "NodePort replaces ClusterIP, while LoadBalancer replaces kube-proxy.",
                            "LoadBalancer operates only on worker nodes, while NodePort operates only on control plane nodes."
                    ],
                    "answer": 1,
                    "explanation": "Service types form an inclusive hierarchy: When you create a `NodePort`, Kubernetes automatically assigns a `ClusterIP`. When you create a `LoadBalancer`, Kubernetes provisions a cloud load balancer, opens a `NodePort` on all nodes, and allocates a `ClusterIP`."
            },
            {
                    "question": "Which field in a Service of type LoadBalancer restricts inbound access to specific external CIDR IP ranges at the cloud firewall level?",
                    "options": [
                            "spec.ipBlockList",
                            "spec.loadBalancerSourceRanges",
                            "spec.allowedIngressCIDRs",
                            "metadata.annotations.firewall-rule"
                    ],
                    "answer": 1,
                    "explanation": "`spec.loadBalancerSourceRanges` allows operators to specify client CIDRs (e.g., `['203.0.113.0/24']`). Supported cloud providers configure their security groups/firewalls to allow traffic only from those IP blocks."
            },
            {
                    "question": "When `externalTrafficPolicy: Local` is enabled on a NodePort/LoadBalancer Service, what port is allocated for cloud load balancer health checks to determine which nodes have ready Pods?",
                    "options": [
                            "spec.healthCheckNodePort",
                            "spec.ports[0].targetPort",
                            "spec.clusterIPPort",
                            "Kubelet port 10250"
                    ],
                    "answer": 0,
                    "explanation": "When `externalTrafficPolicy: Local` is used, Kubernetes allocates `spec.healthCheckNodePort`. Cloud load balancers probe this HTTP port; nodes with zero local pod replicas return HTTP 503, ensuring traffic is only routed to nodes hosting live pods."
            },
            {
                    "question": "How does MetalLB enable Service type LoadBalancer functionality on bare-metal Kubernetes clusters without cloud provider APIs?",
                    "options": [
                            "By rewriting the Linux kernel routing table on client laptops.",
                            "By operating in Layer 2 mode (announcing IPs via ARP/NDP from a leader node) or BGP mode (peering with network routers to announce pod/service routes).",
                            "By deploying an external NGINX reverse proxy on every worker node.",
                            "By converting all NodePort services to DNS CNAME records."
                    ],
                    "answer": 1,
                    "explanation": "MetalLB provides bare-metal load balancing using standard network protocols: Layer 2 mode uses ARP (IPv4) or NDP (IPv6) to bind service IPs to node MAC addresses, while BGP mode establishes dynamic routing sessions with upstream datacenter switches."
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
            },
            {
                    "question": "What is the architectural difference between an `Ingress` resource and an `Ingress Controller` in Kubernetes?",
                    "options": [
                            "An Ingress is a control plane daemon; an Ingress Controller is a worker node daemon.",
                            "An Ingress is a declarative API metadata resource defining routing rules; an Ingress Controller is the running reverse proxy daemon (like NGINX or Envoy) that watches the API and executes the routing.",
                            "Ingress handles UDP traffic; Ingress Controller handles TCP traffic.",
                            "Ingress is deprecated; Ingress Controller is its replacement."
                    ],
                    "answer": 1,
                    "explanation": "An Ingress object is simply declarative configuration in etcd describing hostname/path routing and TLS rules. An Ingress Controller (such as ingress-nginx or Traefik) is the actual software daemon that fulfills those rules by proxying HTTP(S) traffic."
            },
            {
                    "question": "Which Ingress path type matches an incoming request URL prefix on a element-by-element path segment basis?",
                    "options": [
                            "Exact",
                            "Prefix",
                            "ImplementationSpecific",
                            "Regex"
                    ],
                    "answer": 1,
                    "explanation": "`pathType: Prefix` matches URL path prefixes split by `/` delimiters. For example, `/v1` matches `/v1/` and `/v1/users`, but does not match `/v10`."
            },
            {
                    "question": "How is TLS termination configured on an Ingress resource to decrypt HTTPS traffic?",
                    "options": [
                            "By pasting raw certificate strings directly into `spec.rules`.",
                            "By specifying `spec.tls[*].secretName` referencing a `kubernetes.io/tls` Secret containing `tls.crt` and `tls.key` in the same namespace.",
                            "By installing the certificate directly onto the worker node's host BIOS.",
                            "By configuring a NodePort with port 443."
                    ],
                    "answer": 1,
                    "explanation": "Ingress specifies `spec.tls` blocks with hostnames and `secretName`. The referenced Secret must exist in the same namespace and contain `tls.crt` (public cert chain) and `tls.key` (private key)."
            },
            {
                    "question": "What new Kubernetes standard is designed to succeed Ingress by providing expressive, role-oriented, and cross-namespace routing capabilities?",
                    "options": [
                            "ServiceMesh API",
                            "Gateway API (`GatewayClass`, `Gateway`, `HTTPRoute`)",
                            "EgressRoute API",
                            "VirtualService API"
                    ],
                    "answer": 1,
                    "explanation": "The Kubernetes Gateway API provides a modern, role-oriented replacement for Ingress, separating platform infrastructure governance (`GatewayClass`, `Gateway`) from application routing rules (`HTTPRoute`, `GRPCRoute`)."
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
            },
            {
                    "question": "What is the network security posture of a Kubernetes namespace before any `NetworkPolicy` is created in that namespace?",
                    "options": [
                            "Default-Deny (all incoming and outgoing traffic is blocked).",
                            "Default-Allow (all Pods can communicate with all other Pods across all namespaces and external networks).",
                            "Only DNS traffic is permitted; all HTTP traffic is blocked.",
                            "Pods can communicate only with the kube-apiserver."
                    ],
                    "answer": 1,
                    "explanation": "By default, Kubernetes network namespaces are completely open (non-isolated). All pods can communicate with any other pod across any namespace unless a NetworkPolicy selects the pod and enforces isolation."
            },
            {
                    "question": "What is the result when a NetworkPolicy has `policyTypes: [Ingress]` and an empty `spec.podSelector: {}`, but no `ingress` rules defined?",
                    "options": [
                            "It allows all inbound traffic to all pods in the namespace.",
                            "It isolates all pods in the namespace and blocks 100% of incoming traffic (Default-Deny Ingress).",
                            "It crashes the CNI plugin on all worker nodes.",
                            "It deletes all Services in the namespace."
                    ],
                    "answer": 1,
                    "explanation": "Selecting all pods (`podSelector: {}`) for Ingress without providing any `ingress` rules creates a default-deny ingress policy, isolating all pods in the namespace from all inbound network traffic."
            },
            {
                    "question": "In a NetworkPolicy ingress rule, what is the semantic difference between two items in a single `from` list element versus two separate elements in the `from` list?",
                    "options": [
                            "Single element with both `namespaceSelector` and `podSelector` is an AND (intersection); separate list items represent an OR (union).",
                            "Single element is an OR; separate list items represent an AND.",
                            "Single element applies to TCP; separate elements apply to UDP.",
                            "There is no difference in rule evaluation."
                    ],
                    "answer": 0,
                    "explanation": "In YAML, a single map entry containing both selectors (`- namespaceSelector: ... ;   podSelector: ...`) is an AND: the pod must match BOTH. Two list items (`- namespaceSelector: ... ; - podSelector: ...`) is an OR: traffic from either is allowed."
            },
            {
                    "question": "Why would applying a valid `NetworkPolicy` manifest have no effect on network traffic in a standard kind cluster running default kindnet?",
                    "options": [
                            "NetworkPolicies only work on physical fiber-optic cables.",
                            "NetworkPolicy enforcement requires a policy-aware CNI plugin (such as Calico or Cilium); default basic CNIs (like kindnet or flannel) do not program or enforce policy rules.",
                            "kind clusters do not have an API server.",
                            "The `NetworkPolicy` API must be enabled via a feature flag in the Linux kernel."
                    ],
                    "answer": 1,
                    "explanation": "The API server accepts NetworkPolicy objects in all clusters, but actual enforcement happens at the data plane. If the installed CNI (like basic flannel or kindnet) lacks a policy controller, rules are simply ignored."
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
            },
            {
                    "question": "What is the primary architectural difference in lifecycle and scope between a `PersistentVolume` (PV) and a `PersistentVolumeClaim` (PVC)?",
                    "options": [
                            "PV is namespace-scoped; PVC is cluster-scoped.",
                            "PV is a cluster-scoped storage resource provisioned by an administrator or CSI driver; PVC is a namespace-scoped request for storage made by a user/developer.",
                            "PVs can only be attached to worker nodes; PVCs attach to control plane nodes.",
                            "PVs store metadata; PVCs store actual data files."
                    ],
                    "answer": 1,
                    "explanation": "A PersistentVolume is a cluster-wide resource representing underlying storage capacity. A PersistentVolumeClaim is a namespaced request that binds to a matching PV, separating platform storage provisioning from tenant consumption."
            },
            {
                    "question": "What happens when a PersistentVolume with `persistentVolumeReclaimPolicy: Retain` is unbound after its associated PVC is deleted?",
                    "options": [
                            "The PV and its underlying storage volume are immediately erased and deleted.",
                            "The PV transitions to the `Released` status phase; the volume and data remain intact on the storage backend, but the PV cannot be bound to another PVC until manually scrubbed by an admin.",
                            "The PV is immediately reassigned to the default namespace.",
                            "The storage backend formats the partition using ext4."
                    ],
                    "answer": 1,
                    "explanation": "Under `Retain`, when a PVC is deleted, the PV moves to `Released`. The data is preserved safely on the storage device, but the PV cannot be claimed by another PVC until an administrator cleans the data and resets `claimRef`."
            },
            {
                    "question": "What is the meaning of the `ReadWriteOncePod` (RWOP) access mode introduced in Kubernetes 1.22+?",
                    "options": [
                            "The volume can be mounted as read-write by multiple pods across different nodes.",
                            "The volume can be mounted as read-write by exactly one single Pod in the entire cluster, preventing multiple pods on the same node from corrupting the volume.",
                            "The volume can only be written to once, after which it becomes read-only.",
                            "The volume is wiped every time the pod restarts."
                    ],
                    "answer": 1,
                    "explanation": "`ReadWriteOnce` (RWO) allows multiple pods on the *same node* to read/write the volume. `ReadWriteOncePod` (RWOP) strictly restricts read-write access to a *single pod in the entire cluster*, preventing concurrent write corruption."
            },
            {
                    "question": "Why must a PersistentVolume using a `local` volume source specify `nodeAffinity` in its specification?",
                    "options": [
                            "To ensure the volume is replicated to all other nodes in the cluster.",
                            "Because local storage exists on a specific physical disk on a specific node; the scheduler must bind and run consuming Pods on that exact node.",
                            "To assign an IP address to the local disk.",
                            "To enable encryption at rest on the local partition."
                    ],
                    "answer": 1,
                    "explanation": "A local PV is tied directly to a local disk or partition on a single machine. The `nodeAffinity` field informs the Kubernetes scheduler which node hosts the data so workloads are placed where the disk physically exists."
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
            },
            {
                    "question": "What three main criteria does the PersistentVolume controller evaluate when binding a PVC to a PersistentVolume?",
                    "options": [
                            "Pod CPU request, Node memory capacity, and Kernel version.",
                            "StorageClass name, Access Modes, and Capacity (PV capacity must be >= requested PVC capacity).",
                            "Container image tag, Namespace quota, and Host network port.",
                            "Git commit SHA, Docker daemon version, and DNS search domain."
                    ],
                    "answer": 1,
                    "explanation": "A PVC binds to a PV only when both share the same StorageClass (or both have none), the PV supports all requested access modes (RWO, RWX, etc.), and the PV capacity meets or exceeds the requested storage size."
            },
            {
                    "question": "If a user requires expanding an existing PersistentVolumeClaim from 10Gi to 50Gi, what must be true about the underlying StorageClass?",
                    "options": [
                            "The StorageClass must have `allowVolumeExpansion: true`.",
                            "The StorageClass must be marked as `readOnly: true`.",
                            "The StorageClass must use `reclaimPolicy: Recycle`.",
                            "Storage expansion is strictly prohibited in Kubernetes without recreating the cluster."
                    ],
                    "answer": 0,
                    "explanation": "Volume expansion requires `allowVolumeExpansion: true` on the StorageClass. When enabled, users can edit `spec.resources.requests.storage` on the PVC, and the CSI driver will resize the underlying storage volume."
            },
            {
                    "question": "What is the purpose of the `kubernetes.io/pvc-protection` finalizer attached to a PersistentVolumeClaim?",
                    "options": [
                            "It encrypts files written to the volume with AES-256.",
                            "It delays the physical deletion of a PVC while it is actively being used by a running Pod, preventing data corruption or abrupt volume detachment.",
                            "It automatically synchronizes PVC contents to an external S3 bucket.",
                            "It prevents users from deleting any namespaces."
                    ],
                    "answer": 1,
                    "explanation": "The Storage Object Protection feature attaches the `kubernetes.io/pvc-protection` finalizer to active PVCs. If an operator runs `kubectl delete pvc`, the PVC stays in `Terminating` until no active Pod is referencing it."
            },
            {
                    "question": "How can a single PersistentVolumeClaim be mounted into two different directories inside a container, or shared across multiple subdirectories, without exposing the root of the volume?",
                    "options": [
                            "Using the `volumeMounts.subPath` parameter.",
                            "By creating multiple symlinks in the container Dockerfile.",
                            "Using the `spec.volumeDevices` array.",
                            "PVCs cannot mount subdirectories."
                    ],
                    "answer": 0,
                    "explanation": "`volumeMounts.subPath` allows mounting a specific subfolder within a volume instead of its root directory, enabling sharing of a single volume across multiple mounts or containers without exposing the parent filesystem."
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
            },
            {
                    "question": "What is the key difference between `volumeBindingMode: Immediate` and `volumeBindingMode: WaitForFirstConsumer` on a StorageClass?",
                    "options": [
                            "Immediate allocates storage and binds the volume as soon as the PVC is created; WaitForFirstConsumer delays provisioning and binding until a Pod using the PVC is scheduled, ensuring the volume is created in the pod's availability zone.",
                            "Immediate provisions storage on SSDs; WaitForFirstConsumer provisions on HDDs.",
                            "Immediate is used for NFS; WaitForFirstConsumer is used for iSCSI.",
                            "Immediate skips volume format; WaitForFirstConsumer formats the filesystem."
                    ],
                    "answer": 0,
                    "explanation": "With `Immediate`, cloud disks are provisioned immediately upon PVC creation without knowing where the consumer pod will run, risking multi-zone scheduling deadlocks. `WaitForFirstConsumer` delays creation until scheduling, guaranteeing zonal alignment."
            },
            {
                    "question": "How does Kubernetes determine which StorageClass to use when a developer creates a PVC without specifying `storageClassName`?",
                    "options": [
                            "It rejects the PVC with an HTTP 400 Bad Request.",
                            "It uses the StorageClass marked with the annotation `storageclass.kubernetes.io/is-default-class: 'true'`. If none exists, dynamic provisioning fails.",
                            "It randomly selects a StorageClass from the cluster.",
                            "It always falls back to hostPath storage."
                    ],
                    "answer": 1,
                    "explanation": "If `storageClassName` is omitted from a PVC, the dynamic provisioner looks for a StorageClass with the default annotation. If a default class is found, it is used; otherwise, the PVC remains unbound until a class or PV is supplied."
            },
            {
                    "question": "In the modern Container Storage Interface (CSI) specification, what are the two distinct plugins deployed for a storage driver?",
                    "options": [
                            "A Client plugin and a Server plugin.",
                            "A CSI Controller plugin (Deployment for provisioning/attaching volumes via cloud APIs) and a CSI Node plugin (DaemonSet for formatting/mounting volumes onto worker nodes).",
                            "A Master plugin and a Worker plugin.",
                            "An Ingress plugin and an Egress plugin."
                    ],
                    "answer": 1,
                    "explanation": "A complete CSI driver consists of a central Controller plugin (watches PV/PVCs and invokes cloud APIs to create/attach disks) and a Node plugin running on every node (invoked by Kubelet to format, partition, and mount disks locally)."
            },
            {
                    "question": "Which Kubernetes resource allows taking point-in-time copies of a PersistentVolumeClaim for backup and disaster recovery?",
                    "options": [
                            "VolumeSnapshot",
                            "StorageBackup",
                            "DiskClone",
                            "PVCCopy"
                    ],
                    "answer": 0,
                    "explanation": "The CSI Snapshotting feature uses `VolumeSnapshot` (namespaced user request), `VolumeSnapshotClass` (storage driver parameters), and `VolumeSnapshotContent` (cluster-scoped snapshot record) to manage point-in-time storage backups."
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
            },
            {
                    "question": "What is the maximum data storage size limit for a single ConfigMap object in standard Kubernetes?",
                    "options": [
                            "10 Megabytes (10MB)",
                            "1 Megabyte (1MB)",
                            "512 Kilobytes (512KB)",
                            "Unlimited (bounded only by host RAM)"
                    ],
                    "answer": 1,
                    "explanation": "Because ConfigMaps are stored directly as JSON/protobuf entries within etcd, they are bounded by etcd's default request and value size limit of 1 Megabyte (1MB)."
            },
            {
                    "question": "How does setting `immutable: true` on a ConfigMap improve cluster performance and operational safety?",
                    "options": [
                            "It encrypts the ConfigMap with GPG keys.",
                            "It protects against accidental configuration drift and significantly reduces kube-apiserver load by allowing Kubelets to stop watching the ConfigMap for updates.",
                            "It forces the ConfigMap to be stored in the Linux kernel ring buffer.",
                            "It prevents the ConfigMap from being backed up by etcd snapshots."
                    ],
                    "answer": 1,
                    "explanation": "Marking a ConfigMap immutable ensures its contents cannot be altered, which allows Kubelets to close active watch connections to the API server, significantly reducing control plane watch overhead in large-scale deployments."
            },
            {
                    "question": "When a ConfigMap is mounted into a Pod as a volume, how are updates to the ConfigMap reflected inside the running container?",
                    "options": [
                            "The container is immediately killed and restarted with exit code 0.",
                            "The Kubelet's periodic sync loop updates the projected symlink targets inside the container without restarting the pod, though applications must detect the file modification themselves.",
                            "Updates are never reflected until the worker node is rebooted.",
                            "The Kubelet re-executes the container entrypoint script."
                    ],
                    "answer": 1,
                    "explanation": "Volume-mounted ConfigMaps are updated automatically by the Kubelet using atomic directory symlink swapping. In contrast, environment variables loaded via `valueFrom` or `envFrom` are never updated without a pod restart."
            },
            {
                    "question": "Which field in a ConfigMap manifest is specifically designed to store non-UTF-8 binary data such as small certificates or gzip archives?",
                    "options": [
                            "spec.binaryFiles",
                            "binaryData (base64-encoded strings)",
                            "data.bytes",
                            "metadata.rawBinary"
                    ],
                    "answer": 1,
                    "explanation": "The `binaryData` field allows storing binary assets as base64-encoded strings, whereas standard `data` requires valid UTF-8 strings."
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
            },
            {
                    "question": "By default in a vanilla Kubernetes installation without external configuration, how are Secret resources stored inside the etcd database?",
                    "options": [
                            "Encrypted using hardware AES-NI instructions.",
                            "Encrypted with RSA-4096 bit public keys.",
                            "Unencrypted as plain base64-encoded text, meaning anyone with read access to etcd can decode the secrets in plaintext.",
                            "Stored in volatile worker node memory only."
                    ],
                    "answer": 2,
                    "explanation": "By default, Kubernetes Secrets are merely base64-encoded strings stored in plaintext in etcd. Base64 is an encoding format, NOT encryption; anyone with access to etcd or API backup files can immediately decode the contents."
            },
            {
                    "question": "To enable native Encryption at Rest for Secrets inside etcd, what resource file must be passed to the `kube-apiserver` via `--encryption-provider-config`?",
                    "options": [
                            "KubeletConfiguration",
                            "EncryptionConfiguration (specifying providers such as `kms`, `aescbc`, or `secretbox`)",
                            "SecurityContextConstraints",
                            "ClusterRoleBinding"
                    ],
                    "answer": 1,
                    "explanation": "The `EncryptionConfiguration` file configures encryption providers (e.g. cloud KMS, AES-CBC, secretbox). The first provider in the list encrypts newly written secrets, while subsequent providers allow reading previously written secrets."
            },
            {
                    "question": "When a Secret is mounted into a Pod as a volume, what underlying filesystem technology does Kubelet use on the worker node to safeguard credentials?",
                    "options": [
                            "An encrypted NTFS partition.",
                            "A RAM-backed `tmpfs` volume, ensuring the secret payload is stored in memory and never written to the host's physical hard drive.",
                            "A remote S3 bucket mount.",
                            "An unformatted raw disk block."
                    ],
                    "answer": 1,
                    "explanation": "Kubelet mounts secrets as `tmpfs` (temporary in-memory filesystems). Because tmpfs resides strictly in volatile RAM, secrets are never flushed or written to the node's physical persistent storage."
            },
            {
                    "question": "What is the primary difference between a native Kubernetes Secret and using an External Secrets Operator (ESO) with HashiCorp Vault or AWS Secrets Manager?",
                    "options": [
                            "Native Secrets do not work with container images.",
                            "External Secrets Operator synchronizes secrets from an enterprise secret management system into Kubernetes Secrets dynamically, maintaining centralized rotation, auditing, and fine-grained access policies outside the cluster.",
                            "Native Secrets require Java runtimes to decrypt.",
                            "External Secrets Operator stores secrets directly in DNS TXT records."
                    ],
                    "answer": 1,
                    "explanation": "External Secrets Operator bridges Kubernetes with external vaults (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault), allowing security teams to manage secrets, rotations, and audit trails centrally outside of Kubernetes YAML."
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
            },
            {
                    "question": "What is the scope and limitation of a Kubernetes `Role` compared to a `ClusterRole`?",
                    "options": [
                            "A Role can grant permissions across all namespaces and cluster-scoped resources.",
                            "A Role is strictly namespace-scoped; its permission rules apply only to resources within the specific namespace in which the Role is defined.",
                            "A Role can only be bound to ServiceAccounts, never to human Users.",
                            "A Role applies only to worker nodes."
                    ],
                    "answer": 1,
                    "explanation": "A `Role` is always bound to a single namespace and can only grant access to namespaced resources (Pods, Services, Deployments) within that namespace. It cannot grant access to cluster-scoped resources like Nodes or PVs."
            },
            {
                    "question": "Which design principle governs all Kubernetes RBAC authorization rules?",
                    "options": [
                            "Deny rules always take precedence over Allow rules.",
                            "RBAC is purely additive (white-listing only); there are no 'Deny' rules. If an action is not explicitly permitted by a rule, it is denied by default.",
                            "Permissions are inherited automatically from parent namespaces.",
                            "Root users are hardcoded in the Linux kernel and bypass RBAC."
                    ],
                    "answer": 1,
                    "explanation": "Kubernetes RBAC is strictly additive: rules grant capabilities (`allow`). There is no syntax to declare a `deny`. All actions not explicitly permitted by at least one binding evaluating to true are forbidden."
            },
            {
                    "question": "What happens if a `RoleBinding` in namespace `finance` references a `ClusterRole` named `secret-reader` in its `roleRef`?",
                    "options": [
                            "The subjects gain permission to read Secrets across all namespaces in the cluster.",
                            "The subjects gain permission to read Secrets ONLY within the `finance` namespace.",
                            "The API server rejects the RoleBinding with a validation error.",
                            "The cluster converts the namespace into a cluster administrator."
                    ],
                    "answer": 1,
                    "explanation": "A `RoleBinding` can reference a `ClusterRole`. When it does, it scopes the permissions defined in the ClusterRole strictly down to the namespace of the RoleBinding, enabling reuse of common permission definitions across namespaces."
            },
            {
                    "question": "How are subresources (such as reading pod logs or executing commands inside a container) represented in RBAC rules?",
                    "options": [
                            "By listing them as `resources: [\"pods/log\", \"pods/exec\"]` in the rule definition.",
                            "By adding annotations to the pod manifest.",
                            "By granting full root access to the Node object.",
                            "Subresources cannot be controlled with RBAC."
                    ],
                    "answer": 0,
                    "explanation": "Subresources use a slash delimiter format in the `resources` array (e.g., `pods/log`, `pods/exec`, `pods/status`, `deployments/scale`), allowing granular RBAC controls without granting broad object access."
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
            },
            {
                    "question": "Which types of resources require a `ClusterRole` and `ClusterRoleBinding` rather than a standard `Role`?",
                    "options": [
                            "Namespaced Pods and ConfigMaps.",
                            "Cluster-scoped resources (such as `Nodes`, `PersistentVolumes`, `StorageClasses`, `Namespaces`) and non-resource URL paths (like `/healthz`, `/metrics`).",
                            "Deployments with more than 10 replicas.",
                            "Pods running with hostNetwork: true."
                    ],
                    "answer": 1,
                    "explanation": "Non-namespaced resources (Nodes, PVs, Namespaces, StorageClasses) and non-resource HTTP endpoints (`/healthz`, `/metrics`, `/livez`) do not belong to any namespace and can only be authorized via ClusterRoles and ClusterRoleBindings."
            },
            {
                    "question": "What is an Aggregated ClusterRole and how is it constructed?",
                    "options": [
                            "A ClusterRole created by merging etcd database tables directly.",
                            "A ClusterRole that uses `aggregationRule.clusterRoleSelectors` to dynamically combine permissions from multiple other ClusterRoles matching specific label selectors.",
                            "A ClusterRole that automatically grants admin rights to every user in the company.",
                            "A ClusterRole generated by the CNI plugin."
                    ],
                    "answer": 1,
                    "explanation": "Aggregated ClusterRoles combine permissions from other ClusterRoles using label selectors (`matchLabels`). Controllers dynamically populate the aggregated role's rules, allowing custom CRDs to automatically extend default roles like `admin` or `edit`."
            },
            {
                    "question": "Which built-in user-facing ClusterRole provides full read-write access to namespaced resources (except Roles and RoleBindings) while denying cluster-scoped administrative rights?",
                    "options": [
                            "cluster-admin",
                            "admin",
                            "view",
                            "system:node"
                    ],
                    "answer": 1,
                    "explanation": "The built-in `admin` role grants read-write access to most namespaced resources (including Deployments, Services, Secrets), whereas `cluster-admin` grants unrestricted superuser rights across the entire cluster."
            },
            {
                    "question": "How can an administrator quickly verify whether a specific ServiceAccount or user has permission to perform an action using the CLI?",
                    "options": [
                            "kubectl auth can-i <verb> <resource> --as=<user> [-n <namespace>]",
                            "kubectl test rbac --user=<user>",
                            "kubectl get permissions --all",
                            "kubectl describe cluster-admin"
                    ],
                    "answer": 0,
                    "explanation": "`kubectl auth can-i <verb> <resource>` (e.g. `kubectl auth can-i create deployments --as=developer -n dev`) queries the API server's SelfSubjectAccessReview API to evaluate and report whether the action is authorized."
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
            },
            {
                    "question": "What is the primary difference between a `ServiceAccount` and a standard Kubernetes User account?",
                    "options": [
                            "ServiceAccounts are managed directly by Kubernetes API resources for in-cluster processes/Pods; User accounts represent humans and are managed externally (via certificates, OIDC, LDAP) without API objects.",
                            "ServiceAccounts can only be used on Windows nodes.",
                            "User accounts are stored in etcd; ServiceAccounts are stored on GitHub.",
                            "ServiceAccounts cannot be bound to RBAC roles."
                    ],
                    "answer": 0,
                    "explanation": "Kubernetes does not have an API resource for human Users (they are authenticated via external IdPs, X.509 certs, or tokens). ServiceAccounts are first-class namespaced Kubernetes API objects designed for machine workloads."
            },
            {
                    "question": "In modern Kubernetes (1.24+), how are ServiceAccount tokens provided to Pods by default?",
                    "options": [
                            "As static, non-expiring secret tokens permanently saved in the namespace's Secret store.",
                            "Via the `TokenRequest` API as time-bound, audience-restricted, automatically rotated projected volume tokens mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`.",
                            "Through an unencrypted environment variable called `$K8S_TOKEN`.",
                            "By opening an SSH connection to the kube-apiserver."
                    ],
                    "answer": 1,
                    "explanation": "Bound Service Account Token Volume projection issues short-lived, time-expiring JWT tokens tied directly to the specific pod instance and API audience, replacing the insecure legacy pattern of eternal static Secret tokens."
            },
            {
                    "question": "If a Pod does not need to communicate with the Kubernetes API server, what setting should be applied for security hardening?",
                    "options": [
                            "`automountServiceAccountToken: false` on the Pod spec or ServiceAccount.",
                            "`hostNetwork: false`.",
                            "`dnsPolicy: None`.",
                            "Assigning `priorityClassName: system-cluster-critical`."
                    ],
                    "answer": 0,
                    "explanation": "Setting `automountServiceAccountToken: false` prevents Kubelet from mounting API credentials into the container filesystem, neutralizing credential theft risk if the application container is compromised."
            },
            {
                    "question": "Where does Kubelet mount in-pod API credentials by default inside a container?",
                    "options": [
                            "/etc/kubernetes/admin.conf",
                            "/var/run/secrets/kubernetes.io/serviceaccount/",
                            "/root/.kube/config",
                            "/tmp/k8s-credentials/"
                    ],
                    "answer": 1,
                    "explanation": "The standard credential mount path inside every pod is `/var/run/secrets/kubernetes.io/serviceaccount/`, containing `token` (JWT), `ca.crt` (cluster CA certificate), and `namespace` (the pod's namespace name)."
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
            },
            {
                    "question": "How long after a worker node stops reporting heartbeats does the Node Lifecycle Controller mark the node as `NotReady` or `Unknown` by default?",
                    "options": [
                            "5 seconds",
                            "40 seconds (`node-monitor-grace-period`)",
                            "10 minutes",
                            "1 hour"
                    ],
                    "answer": 1,
                    "explanation": "The default `node-monitor-grace-period` in kube-controller-manager is 40 seconds. If no lease heartbeat is received within this window, the controller changes the node's Ready condition to Unknown or False."
            },
            {
                    "question": "When a node transitions to `NotReady` or `Unreachable`, what taint is automatically applied by the Node Lifecycle Controller?",
                    "options": [
                            "`node.kubernetes.io/not-ready:NoExecute` or `node.kubernetes.io/unreachable:NoExecute`",
                            "`kubernetes.io/shutdown:Crash`",
                            "`node.critical/evict:Immediate`",
                            "`hardware.failure/reboot:True`"
                    ],
                    "answer": 0,
                    "explanation": "The controller injects `node.kubernetes.io/not-ready:NoExecute` or `node.kubernetes.io/unreachable:NoExecute`. Pods without matching tolerations begin eviction."
            },
            {
                    "question": "By default, how long will a standard Pod tolerate a `node.kubernetes.io/not-ready:NoExecute` taint before the node controller evicts it?",
                    "options": [
                            "0 seconds (immediate eviction)",
                            "300 seconds (5 minutes, configured via default tolerationSeconds)",
                            "24 hours",
                            "Indefinitely"
                    ],
                    "answer": 1,
                    "explanation": "Kubernetes automatically appends default tolerations to all pods for `not-ready` and `unreachable` with `tolerationSeconds: 300` (5 minutes), preventing immediate mass eviction during transient network blips."
            },
            {
                    "question": "Which Kubelet Node condition indicates that the host's Linux process table is running out of available PID numbers?",
                    "options": [
                            "MemoryPressure",
                            "PIDPressure",
                            "DiskPressure",
                            "NetworkUnavailable"
                    ],
                    "answer": 1,
                    "explanation": "`PIDPressure` indicates that the number of allocated Linux process IDs on the host is nearing the system limit (`kernel.pid_max`), prompting Kubelet to reject new pods to prevent host kernel lockups."
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
            },
            {
                    "question": "What action does the Namespace Controller take when a user executes `kubectl delete namespace <name>`?",
                    "options": [
                            "It immediately deletes the namespace object, leaving running pods orphaned.",
                            "It transitions the namespace status to `Terminating` and initiates asynchronous cascading deletion of all namespaced resources (Pods, Services, PVCs, ConfigMaps) inside that namespace.",
                            "It sends an email notification to cluster administrators for approval.",
                            "It reboots all worker nodes."
                    ],
                    "answer": 1,
                    "explanation": "Deleting a namespace puts it into `Terminating`. The namespace controller discovers and deletes all resources residing in that namespace in order before finalizing namespace deletion."
            },
            {
                    "question": "Why does a namespace occasionally become stuck in the `Terminating` status indefinitely?",
                    "options": [
                            "Because the cluster has run out of CPU quota.",
                            "One or more resources within the namespace have active `finalizers` that cannot be cleared (e.g., an unavailable custom metrics API or dangling PVC protection).",
                            "Because DNS records cannot be deleted without an internet connection.",
                            "Because worker nodes refuse to run garbage collection."
                    ],
                    "answer": 1,
                    "explanation": "A namespace cannot be completely deleted while objects inside it still have pending finalizers, or if an aggregated API service responsible for a resource type is unresponsive."
            },
            {
                    "question": "Which of the following resources is strictly non-namespaced (cluster-scoped)?",
                    "options": [
                            "ConfigMap",
                            "PersistentVolume (PV)",
                            "Service",
                            "Secret"
                    ],
                    "answer": 1,
                    "explanation": "`PersistentVolume`, `Node`, `Namespace`, `StorageClass`, and `ClusterRole` are cluster-scoped (non-namespaced) resources. ConfigMap, Service, and Secret are namespaced."
            },
            {
                    "question": "Which command displays all Kubernetes resource types along with their API group and whether they are namespaced or cluster-scoped?",
                    "options": [
                            "kubectl api-resources",
                            "kubectl get all --all-namespaces",
                            "kubectl explain schema",
                            "kubectl cluster-info dump"
                    ],
                    "answer": 0,
                    "explanation": "`kubectl api-resources` lists all resource types registered with the API server, showing their short name, API group, whether they are namespaced (true/false), and Kind."
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
            },
            {
                    "question": "What is the primary difference in scope and enforcement between a `ResourceQuota` and a `LimitRange`?",
                    "options": [
                            "ResourceQuota enforces aggregate resource consumption limits across an entire namespace; LimitRange sets default, minimum, and maximum resource constraints on individual containers/Pods.",
                            "ResourceQuota is for storage; LimitRange is for CPU.",
                            "ResourceQuota applies to worker nodes; LimitRange applies to control plane nodes.",
                            "ResourceQuota applies to external users; LimitRange applies to internal pods."
                    ],
                    "answer": 0,
                    "explanation": "A ResourceQuota bounds total cumulative usage in a namespace (e.g. max 20 CPUs, 50 Pods total). A LimitRange enforces per-pod or per-container boundaries (e.g. min 100m CPU, default 256Mi RAM) and injects default requests/limits."
            },
            {
                    "question": "If a namespace has a `ResourceQuota` restricting total `requests.cpu`, what happens if a user submits a Pod that does NOT declare any CPU request or limit?",
                    "options": [
                            "The Pod is assigned 100% of the host node's CPU.",
                            "The API server rejects Pod creation with HTTP 403 Forbidden, unless a `LimitRange` in the namespace injects default CPU requests.",
                            "The scheduler automatically assigns 1 milliCPU.",
                            "The ResourceQuota is automatically disabled."
                    ],
                    "answer": 1,
                    "explanation": "When a quota restricts compute resources, every submitted container must specify that resource. If a container lacks requests/limits and no LimitRange provides defaults, the admission controller rejects the creation request."
            },
            {
                    "question": "What is the difference between `default` and `defaultRequest` in a container `LimitRange` specification?",
                    "options": [
                            "`default` sets the container resource Limit; `defaultRequest` sets the container resource Request.",
                            "`default` is for memory; `defaultRequest` is for CPU.",
                            "`default` applies to Deployments; `defaultRequest` applies to Jobs.",
                            "`default` is deprecated."
                    ],
                    "answer": 0,
                    "explanation": "In a LimitRange, `default` defines the fallback resource *limits* applied when a pod omits them, while `defaultRequest` defines the fallback resource *requests*."
            },
            {
                    "question": "Which ResourceQuota scope restricts resource calculations only to Pods that have an active deadline specified (such as batch Jobs)?",
                    "options": [
                            "BestEffort",
                            "Terminating",
                            "NotTerminating",
                            "PriorityClass"
                    ],
                    "answer": 1,
                    "explanation": "The `Terminating` scope matches Pods that have `spec.activeDeadlineSeconds >= 0` (like batch jobs), allowing separate quotas for short-lived batch workloads versus non-terminating long-running services."
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
            },
            {
                    "question": "What is the primary function of `metadata.ownerReferences` on Kubernetes API objects?",
                    "options": [
                            "It specifies which human developer owns the git commit.",
                            "It links child resources (such as Pods managed by a ReplicaSet) to their parent controller, allowing the Garbage Collector to automatically clean up dependents when the parent is deleted.",
                            "It authorizes external TLS connections.",
                            "It sets billing chargeback codes for cloud accounting."
                    ],
                    "answer": 1,
                    "explanation": "OwnerReferences establish parent-child relationships between API objects (e.g. Deployment -> ReplicaSet -> Pod). The Garbage Collector uses these links to prune orphaned dependent resources automatically."
            },
            {
                    "question": "What is the difference between `propagationPolicy: Background` and `propagationPolicy: Foreground` during cascading resource deletion?",
                    "options": [
                            "Background deletes the parent first and cleans up child objects asynchronously in the background; Foreground marks the parent in 'deletion in progress' until all child objects are deleted first.",
                            "Background deletes resources at midnight; Foreground deletes immediately.",
                            "Background is for worker nodes; Foreground is for control plane nodes.",
                            "Background only deletes Services; Foreground only deletes Pods."
                    ],
                    "answer": 0,
                    "explanation": "With `Background`, Kubernetes deletes the owner object immediately, then the garbage collector deletes dependents later. With `Foreground`, the owner enters `Terminating` with a finalizer, waiting until all dependents are deleted before disappearing."
            },
            {
                    "question": "What restriction applies to `ownerReferences` regarding namespace boundaries?",
                    "options": [
                            "OwnerReferences can cross namespaces only if both namespaces share the same prefix.",
                            "Cross-namespace owner references are disallowed by design; a namespaced child resource can only have an ownerReference to a parent within the same namespace.",
                            "OwnerReferences can only point to objects in the `default` namespace.",
                            "There are no namespace restrictions on OwnerReferences."
                    ],
                    "answer": 1,
                    "explanation": "By design, namespaced resources cannot specify owners in different namespaces. This prevents privilege escalation or accidental cross-tenant deletion across namespace boundaries."
            },
            {
                    "question": "How do `finalizers` on an object interact with the Kubernetes Garbage Collector?",
                    "options": [
                            "They immediately erase the object from etcd.",
                            "They inform the API server that asynchronous cleanup actions (like external cloud load balancer teardown) must succeed before the object can be completely purged from etcd.",
                            "They force all pods into CrashLoopBackOff.",
                            "They encrypt the object with AES-256."
                    ],
                    "answer": 1,
                    "explanation": "Finalizers are string identifiers (e.g. `kubernetes.io/pv-protection`) in `metadata.finalizers`. When an object is deleted, it remains in `Terminating` with a `deletionTimestamp` until controllers finish cleanup and remove their finalizers."
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
            },
            {
                    "question": "What distinguishes a `ReplicaSet` from its predecessor, the legacy `ReplicationController`?",
                    "options": [
                            "ReplicaSets can run on Windows, whereas ReplicationControllers only run on Linux.",
                            "ReplicaSets support set-based label selectors (`matchExpressions` with `In`, `NotIn`, `Exists`), whereas ReplicationControllers only support simple equality-based selectors.",
                            "ReplicaSets do not use etcd.",
                            "ReplicaSets can only manage a single Pod replica."
                    ],
                    "answer": 1,
                    "explanation": "The primary evolution from ReplicationController to ReplicaSet was the introduction of set-based selectors (`matchExpressions`), allowing complex queries across environments, tiers, and versions."
            },
            {
                    "question": "Why is it generally considered an anti-pattern for developers to manage `ReplicaSet` objects directly?",
                    "options": [
                            "ReplicaSets are deprecated and will be removed in the next release.",
                            "Deployments manage ReplicaSets automatically, providing declarative rolling updates, rollbacks, and revision history that raw ReplicaSets lack.",
                            "ReplicaSets cannot restart crashed containers.",
                            "ReplicaSets consume twice as much network bandwidth."
                    ],
                    "answer": 1,
                    "explanation": "Deployments sit on top of ReplicaSets. While ReplicaSets ensure replica counts, they do not support automated rolling updates or rollbacks. Deployments manage ReplicaSet lifecycles declaratively."
            },
            {
                    "question": "What happens if an existing running Pod has labels matching a newly created `ReplicaSet`'s selector?",
                    "options": [
                            "The ReplicaSet deletes the existing Pod immediately.",
                            "The ReplicaSet adopts the existing Pod and counts it toward its desired replica count.",
                            "The ReplicaSet fails to start with a duplicate label error.",
                            "The API server renames the Pod."
                    ],
                    "answer": 1,
                    "explanation": "ReplicaSets operate on label matching, not creation lineage. A ReplicaSet will automatically adopt any unowned Pod matching its selector, counting it toward `spec.replicas`."
            },
            {
                    "question": "What is the purpose of the `pod-template-hash` label injected into Pods by the Deployment controller?",
                    "options": [
                            "It serves as a cryptographic checksum to detect container tampering.",
                            "It ensures that different ReplicaSets created by a Deployment do not have overlapping label selectors, preventing multi-ReplicaSet selector collisions.",
                            "It defines the root password for the pod.",
                            "It hashes the pod's IP address for load balancing."
                    ],
                    "answer": 1,
                    "explanation": "The Deployment controller hashes the `PodTemplateSpec` and injects `pod-template-hash` into the child ReplicaSet and Pod labels so the Deployment can distinguish between replicas of different revisions."
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
            },
            {
                    "question": "What is the default deployment strategy in Kubernetes, and what are its two primary tuning parameters?",
                    "options": [
                            "Recreate (downtime); tuned by `activeDeadlineSeconds`.",
                            "RollingUpdate; tuned by `maxSurge` (maximum pods created above desired count) and `maxUnavailable` (maximum pods unavailable during the update).",
                            "Canary; tuned by `canaryPercentage`.",
                            "BlueGreen; tuned by `color`."
                    ],
                    "answer": 1,
                    "explanation": "The default strategy is `RollingUpdate`. It is governed by `maxSurge` (how many extra pods can be created above `spec.replicas`) and `maxUnavailable` (how many pods can be down during the rollout), both defaulting to 25%."
            },
            {
                    "question": "Which command rolls back a Deployment to a specific historical revision number?",
                    "options": [
                            "kubectl rollout undo deployment/<name> --to-revision=<N>",
                            "kubectl deployment rollback <name> -v <N>",
                            "kubectl revert deployment <name> --revision <N>",
                            "kubectl apply --rollback <N>"
                    ],
                    "answer": 0,
                    "explanation": "`kubectl rollout undo deployment/<name> --to-revision=<N>` restores the pod template from the specified historical ReplicaSet revision recorded in the rollout history."
            },
            {
                    "question": "What happens to an in-progress RollingUpdate if the new version's Pods fail their `readinessProbe` checks?",
                    "options": [
                            "The Deployment controller immediately terminates all old healthy pods.",
                            "The new Pods never transition to `Ready`, preventing the Deployment controller from progressing further or terminating additional old Pods, thereby containing the failure.",
                            "The entire cluster enters emergency maintenance mode.",
                            "The Kubelet deletes the Deployment manifest from etcd."
                    ],
                    "answer": 1,
                    "explanation": "Rolling updates wait for new pods to report Ready before terminating old pods. If readiness probes fail, the rollout stalls, preserving the existing healthy pods and preventing user downtime."
            },
            {
                    "question": "How can an administrator pause an active Deployment rollout to inspect the state or execute canary testing before completing the update?",
                    "options": [
                            "kubectl rollout pause deployment/<name>",
                            "kubectl stop deployment/<name>",
                            "kubectl drain deployment/<name>",
                            "systemctl stop kube-deployment"
                    ],
                    "answer": 0,
                    "explanation": "`kubectl rollout pause deployment/<name>` pauses the rollout, allowing operators to make multiple changes or verify canary behavior before resuming the rollout with `kubectl rollout resume`."
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
            },
            {
                    "question": "What three core guarantees distinguish a `StatefulSet` from a `Deployment`?",
                    "options": [
                            "Faster container startup, zero CPU usage, and automated SSL certs.",
                            "Stable, unique network identifiers (predictable ordinal DNS names); stable, persistent storage bound to each pod; and ordered, graceful deployment and scaling.",
                            "Ability to run without Docker, automated backups to S3, and root host access.",
                            "Guaranteed execution only on control plane nodes."
                    ],
                    "answer": 1,
                    "explanation": "StatefulSets provide stable ordinal indices (`pod-0`, `pod-1`), deterministic network identities via Headless Services (`pod-0.svc.ns.svc.cluster.local`), and persistent storage that stays bound to the same ordinal across restarts."
            },
            {
                    "question": "Why is a Headless Service (`spec.clusterIP: None`) strictly required for a StatefulSet?",
                    "options": [
                            "StatefulSets cannot route HTTP traffic.",
                            "It enables direct DNS resolution for each individual Pod ordinal (e.g. `statefulset-0.service-name`), allowing clustered stateful databases (Cassandra, ZooKeeper, Kafka) to locate specific peers directly.",
                            "Headless Services bypass Linux kernel routing tables.",
                            "It encrypts database network traffic."
                    ],
                    "answer": 1,
                    "explanation": "Clustered stateful applications need peer-to-peer discovery rather than generic load balancing. A Headless Service creates direct SRV/A records for every pod ordinal (`<pod-name>.<service-name>.<ns>.svc.cluster.local`)."
            },
            {
                    "question": "What happens to the PersistentVolumeClaims created by a StatefulSet's `volumeClaimTemplates` when the StatefulSet is scaled down or deleted?",
                    "options": [
                            "The PVCs and underlying storage disks are immediately deleted.",
                            "The PVCs are deliberately NOT deleted, preserving critical application data and allowing pods to reattach to the exact same storage when scaled back up.",
                            "The PVCs are merged into a single archive file.",
                            "The PVCs are transferred to the default namespace."
                    ],
                    "answer": 1,
                    "explanation": "To safeguard stateful data against accidental data loss during scale-down operations, StatefulSets do not delete PVCs created from `volumeClaimTemplates`. Deleting them requires manual administrative action."
            },
            {
                    "question": "What is the purpose of `spec.updateStrategy.rollingUpdate.partition` in a StatefulSet?",
                    "options": [
                            "It partitions the hard drive into separate partitions.",
                            "It enables canary deployments by updating only Pods with an ordinal greater than or equal to the partition number, leaving lower-numbered ordinals on the old version.",
                            "It restricts pod execution to specific CPU cores.",
                            "It splits network traffic across different VPC subnets."
                    ],
                    "answer": 1,
                    "explanation": "Setting a partition number (e.g. `partition: 3` on a 5-replica set) updates only pods 3 and 4, allowing staged canary verification before rolling out the update to pods 0, 1, and 2."
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
            },
            {
                    "question": "What is the primary operational role of a `DaemonSet` in a Kubernetes cluster?",
                    "options": [
                            "To run short-lived computational batch scripts that exit upon completion.",
                            "To ensure that all (or eligible) worker nodes execute exactly one copy of a specific Pod (e.g. CNI networking agents, log collectors, node monitoring daemons).",
                            "To provide external Layer-7 HTTP routing.",
                            "To manage the etcd Raft consensus loop."
                    ],
                    "answer": 1,
                    "explanation": "A DaemonSet guarantees that every eligible node in the cluster runs a single replica of a pod. As new nodes join the cluster, the DaemonSet controller automatically adds the pod to them."
            },
            {
                    "question": "When an administrator executes `kubectl drain <node>`, why must the `--ignore-daemonsets` flag typically be specified?",
                    "options": [
                            "Because DaemonSets cannot run on worker nodes.",
                            "Because DaemonSets are bound to every node; if evicted, the DaemonSet controller would immediately recreate them on that same node, causing the drain command to fail or hang.",
                            "Because DaemonSets ignore SIGTERM signals.",
                            "Because DaemonSets are managed by systemd."
                    ],
                    "answer": 1,
                    "explanation": "Without `--ignore-daemonsets`, `kubectl drain` refuses to proceed because evicting a daemonset pod is futile: the daemonset controller would immediately schedule a new copy on the same node."
            },
            {
                    "question": "How can an operator configure a DaemonSet to run only on nodes equipped with physical GPU hardware?",
                    "options": [
                            "By setting `spec.gpu: true` on the DaemonSet.",
                            "By configuring `nodeSelector` or `spec.template.spec.affinity.nodeAffinity` on the DaemonSet pod template to match GPU node labels (e.g. `accelerator: nvidia-tesla`).",
                            "By installing the CUDA driver into the kube-apiserver.",
                            "DaemonSets cannot be targeted to specific nodes."
                    ],
                    "answer": 1,
                    "explanation": "DaemonSets evaluate node selectors and node affinity. Specifying node matching rules restricts the DaemonSet controller to creating pods only on nodes possessing the matching labels."
            },
            {
                    "question": "What update strategies are supported by the DaemonSet controller in `spec.updateStrategy.type`?",
                    "options": [
                            "`RollingUpdate` (default, updates nodes gradually according to `maxUnavailable`) and `OnDelete` (updates a node's pod only when the old pod is manually killed).",
                            "`Recreate` and `Immediate`.",
                            "`BlueGreen` and `Canary`.",
                            "`Parallel` and `Serial`."
                    ],
                    "answer": 0,
                    "explanation": "DaemonSets support `RollingUpdate` (automatically terminates and replaces old daemon pods node by node) and `OnDelete` (does not touch running pods until an administrator or automation explicitly deletes them)."
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
            },
            {
                    "question": "Which `restartPolicy` values are valid for a Kubernetes `Job` object?",
                    "options": [
                            "Only `Always`",
                            "`Never` or `OnFailure` (setting `Always` is strictly rejected by the API server)",
                            "`Conditional` or `Fallback`",
                            "`OnError` only"
                    ],
                    "answer": 1,
                    "explanation": "Jobs run batch processes to completion. A `restartPolicy: Always` makes no sense for a finite job and is rejected by the API server schema; only `Never` (create a new pod on failure) or `OnFailure` (restart container inside same pod) are allowed."
            },
            {
                    "question": "In a Kubernetes Job specification, what is the operational difference between `completions` and `parallelism`?",
                    "options": [
                            "`completions` defines how many successful pod terminations are required for the Job to finish; `parallelism` defines the maximum number of pods that can run concurrently.",
                            "`completions` is for CPU; `parallelism` is for RAM.",
                            "`completions` sets timeout seconds; `parallelism` sets retry count.",
                            "`completions` applies only to CronJobs."
                    ],
                    "answer": 0,
                    "explanation": "`spec.completions` specifies the target total count of successful pod runs needed, while `spec.parallelism` dictates how many worker pods are allowed to execute at the same time."
            },
            {
                    "question": "What does the `backoffLimit` field (default 6) in a Job manifest configure?",
                    "options": [
                            "The maximum network bandwidth allocated to the job.",
                            "The maximum number of retries before the Job controller marks the entire Job as permanently Failed.",
                            "The delay in milliseconds between log entries.",
                            "The number of backup nodes."
                    ],
                    "answer": 1,
                    "explanation": "`backoffLimit` dictates how many times failed pod runs will be retried with exponential backoff delay (10s, 20s, 40s...) before the Job controller gives up and sets the Job condition to Failed."
            },
            {
                    "question": "How can completed batch Jobs and their associated Pods be automatically cleaned up after finishing without manual scripting?",
                    "options": [
                            "By setting `spec.ttlSecondsAfterFinished` on the Job manifest.",
                            "By configuring a ResourceQuota with `ttl: 0`.",
                            "By setting `imagePullPolicy: Never`.",
                            "Kubernetes automatically deletes all Jobs after 60 seconds."
                    ],
                    "answer": 0,
                    "explanation": "The TTL-after-finished controller automatically purges completed or failed Jobs and their associated pods after the duration configured in `spec.ttlSecondsAfterFinished` expires."
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
            },
            {
                    "question": "What are the three supported options for `concurrencyPolicy` in a Kubernetes `CronJob`?",
                    "options": [
                            "`Immediate`, `Delayed`, `Queued`",
                            "`Allow` (concurrent runs permitted), `Forbid` (skip new run if previous has not finished), `Replace` (cancel running job and start new one)",
                            "`Fast`, `Normal`, `Slow`",
                            "`Exclusive`, `Shared`, `Distributed`"
                    ],
                    "answer": 1,
                    "explanation": "`concurrencyPolicy` defines behavior when a new schedule arrives while an older job is still running: `Allow` runs both concurrently; `Forbid` skips the new execution; `Replace` terminates the older job and launches the new one."
            },
            {
                    "question": "What is the purpose of `startingDeadlineSeconds` on a CronJob?",
                    "options": [
                            "The time limit for the container image to download.",
                            "The window of time in seconds after the scheduled trigger time during which a missed Job execution can still be started (e.g. if the cluster was down or paused).",
                            "The execution duration limit for the running job process.",
                            "The DNS lookup timeout."
                    ],
                    "answer": 1,
                    "explanation": "If a CronJob misses its scheduled time (due to control plane downtime or node maintenance), `startingDeadlineSeconds` defines how long after the missed schedule it is still allowed to start; past the deadline, it is counted as a missed run."
            },
            {
                    "question": "How can an administrator temporarily pause all future automated runs of a CronJob without deleting the resource?",
                    "options": [
                            "By setting `spec.suspend: true` on the CronJob manifest.",
                            "By changing the schedule to `* * * * *`.",
                            "By deleting the kube-controller-manager.",
                            "By adding a `NoSchedule` taint to all worker nodes."
                    ],
                    "answer": 0,
                    "explanation": "Setting `spec.suspend: true` pauses execution of all future scheduled runs while preserving the CronJob definition, historical jobs, and configuration intact."
            },
            {
                    "question": "Which parameters control the pruning of finished historical Job objects created by a CronJob?",
                    "options": [
                            "`spec.successfulJobsHistoryLimit` (default 3) and `spec.failedJobsHistoryLimit` (default 1)",
                            "`spec.retentionPolicy.keepDays`",
                            "`metadata.historyPruneSeconds`",
                            "`spec.maxBackupCount`"
                    ],
                    "answer": 0,
                    "explanation": "`successfulJobsHistoryLimit` (default 3) and `failedJobsHistoryLimit` (default 1) govern how many completed and failed Job records the CronJob controller retains in the API server before pruning."
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
            },
            {
                    "question": "Why is the legacy `ReplicationController` retained in the core Kubernetes API (`apiVersion: v1`)?",
                    "options": [
                            "It is the required controller for all control plane components.",
                            "For strict backward compatibility with original Kubernetes v1 manifests, though it is fully superseded by Deployments and ReplicaSets.",
                            "It offers better performance than ReplicaSet on ARM64 hardware.",
                            "It is used exclusively for Windows container workloads."
                    ],
                    "answer": 1,
                    "explanation": "`ReplicationController` is preserved in the core `v1` API group so that legacy automation and original manifests from early Kubernetes releases continue to function without breaking backward compatibility."
            },
            {
                    "question": "Which selector operator is completely unsupported by a `ReplicationController`?",
                    "options": [
                            "Equality (`environment = production`)",
                            "Set-based operators (`tier in (frontend, backend)` or `matchExpressions`)",
                            "String matching",
                            "Exact label keys"
                    ],
                    "answer": 1,
                    "explanation": "ReplicationControllers only support equality-based matching (`selector: { app: web }`). They cannot parse `matchExpressions` or set-based operators (`In`, `NotIn`, `Exists`), which were introduced with ReplicaSets."
            },
            {
                    "question": "Can a modern Kubernetes `Deployment` object manage a `ReplicationController`?",
                    "options": [
                            "Yes, if configured with `spec.controllerKind: ReplicationController`.",
                            "No; Deployments are designed exclusively to manage `ReplicaSet` objects (`apps/v1`).",
                            "Yes, but only in the `kube-system` namespace.",
                            "Yes, if the cluster runs in legacy compatibility mode."
                    ],
                    "answer": 1,
                    "explanation": "Deployments exclusively create and manage ReplicaSets. They have no code path to manage legacy ReplicationControllers."
            },
            {
                    "question": "What is the recommended migration path to upgrade an application running under a `ReplicationController` to a `Deployment` without downtime?",
                    "options": [
                            "Delete all worker nodes and restore from an etcd backup.",
                            "Deploy a Deployment whose pod template has the identical labels; the Deployment's ReplicaSet will adopt the pods (or roll out new ones), after which the ReplicationController can be deleted with `--cascade=orphan`.",
                            "Rename the `kind: ReplicationController` line to `kind: Deployment` without changing the schema.",
                            "Reboot the cluster."
                    ],
                    "answer": 1,
                    "explanation": "Because Kubernetes works on label matching, deploying a Deployment with identical labels and deleting the ReplicationController with `--cascade=orphan` allows zero-downtime adoption of existing workloads."
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
            },
            {
                    "question": "What cluster service must be running for the Horizontal Pod Autoscaler (HPA) to scale workloads based on CPU and memory utilization?",
                    "options": [
                            "CoreDNS",
                            "Metrics Server (aggregating resource metrics from Kubelet Summary APIs)",
                            "Flannel CNI",
                            "External Secrets Operator"
                    ],
                    "answer": 1,
                    "explanation": "HPA queries the `metrics.k8s.io` API. This API is fulfilled by the cluster `Metrics Server`, which periodically scrapes container CPU and RAM usage from Kubelet `/stats/summary` endpoints."
            },
            {
                    "question": "What is the mathematical scaling formula used by the HPA controller to determine desired replica count?",
                    "options": [
                            "`desiredReplicas = ceil[currentReplicas * (currentMetricValue / targetMetricValue)]`",
                            "`desiredReplicas = currentReplicas + (currentMetricValue * 2)`",
                            "`desiredReplicas = maxReplicas - minReplicas`",
                            "`desiredReplicas = floor[targetMetricValue / currentReplicas]`"
                    ],
                    "answer": 0,
                    "explanation": "The HPA evaluates the ratio of observed metric value to target value: `desiredReplicas = ceil[currentReplicas * (currentMetricValue / targetMetricValue)]`, scaling up or down to keep metrics near target."
            },
            {
                    "question": "What is the purpose of the `spec.behavior.scaleDown.stabilizationWindowSeconds` setting in an HPA definition?",
                    "options": [
                            "It delays the startup of containers.",
                            "It prevents rapid 'flapping' (thrashing) by observing metrics over a sustained window (default 300s / 5 minutes) before scaling down replicas.",
                            "It restricts pod network throughput.",
                            "It forces CPU throttling on worker nodes."
                    ],
                    "answer": 1,
                    "explanation": "A stabilization window smooths out momentary spikes and dips in load. During scale-down, HPA looks back across the stabilization window and picks the highest desired replica count calculated during that window, avoiding premature downscaling."
            },
            {
                    "question": "What requirement must application containers meet for an HPA targeting `type: Resource` (e.g. 80% CPU utilization) to calculate percentages?",
                    "options": [
                            "Containers must run as root.",
                            "Containers must have explicit `resources.requests` defined for that resource; without requests, HPA cannot calculate percentage utilization and will report `<unknown>`.",
                            "Containers must expose a `/metrics` Prometheus endpoint.",
                            "Containers must be part of a DaemonSet."
                    ],
                    "answer": 1,
                    "explanation": "Target percentage utilization is calculated relative to container resource requests (`actual_usage / requested_resource * 100`). If `requests.cpu` is omitted, HPA has no baseline and cannot compute target percentages."
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
            },
            {
                    "question": "What are the three primary components that constitute the Kubernetes Vertical Pod Autoscaler (VPA)?",
                    "options": [
                            "Ingress, Service, and EndpointSlice",
                            "VPA Recommender (computes resource recommendations), VPA Updater (evicts pods needing resizing), and VPA Admission Controller (injects recommended requests upon pod recreation)",
                            "Kubelet, Containerd, and Runc",
                            "Prometheus, Grafana, and Alertmanager"
                    ],
                    "answer": 1,
                    "explanation": "VPA operates via three decoupled components: Recommender (observes historic usage and calculates target CPU/RAM), Updater (evicts out-of-spec pods), and Mutating Admission Controller (injects new resource values when pods recreate)."
            },
            {
                    "question": "What is the operational effect of setting `updateMode: 'Off'` in a VerticalPodAutoscaler manifest?",
                    "options": [
                            "The VPA is completely uninstalled.",
                            "The VPA computes and publishes recommended resource requests in its status field, but never modifies, evicts, or resizes running Pods.",
                            "The VPA shuts down all worker nodes.",
                            "The VPA deletes all Pods matching the targetRef."
                    ],
                    "answer": 1,
                    "explanation": "`updateMode: 'Off'` operates as a safe observation tool. The recommender logs optimal resource sizes in `status.recommendation`, enabling engineers to review recommendations without risking automated pod disruptions."
            },
            {
                    "question": "Why should HPA and VPA generally NOT be configured to scale the same workload based on the same resource metric (such as CPU utilization)?",
                    "options": [
                            "Linux kernels do not support both autoscalers simultaneously.",
                            "They enter a race condition (thrashing loop): high CPU causes VPA to increase pod CPU requests, while HPA simultaneously adds more replicas, leading to severe resource over-allocation.",
                            "etcd database corruption will occur.",
                            "The API server blocks the creation of the VPA manifest."
                    ],
                    "answer": 1,
                    "explanation": "Scaling both horizontally (HPA) and vertically (VPA) on the same metric creates conflicting control loops. If CPU spikes, VPA raises the pod's CPU request while HPA adds replicas, resulting in unpredictable and compounding resource expansion."
            },
            {
                    "question": "How does the Kubernetes 'In-Place Pod Resource Resizing' feature (alpha/beta in K8s 1.27+) improve upon traditional VPA behavior?",
                    "options": [
                            "It eliminates the need for Linux cgroups.",
                            "It allows container CPU and memory requests/limits to be adjusted dynamically without restarting or evicting the container, avoiding application downtime.",
                            "It converts containers into virtual machines.",
                            "It doubles host physical RAM on demand."
                    ],
                    "answer": 1,
                    "explanation": "Traditionally, changing pod resources required pod eviction and restart. In-place resizing allows modifying `resources.requests` and `resources.limits` on running containers without restart by adjusting cgroup limits live in the Linux kernel."
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
            },
            {
                    "question": "In a `PodDisruptionBudget` (PDB) specification, what is the constraint regarding `minAvailable` and `maxUnavailable`?",
                    "options": [
                            "Both must always be specified simultaneously.",
                            "They are mutually exclusive; you can specify either `minAvailable` OR `maxUnavailable`, but never both in the same PDB.",
                            "`minAvailable` is for memory; `maxUnavailable` is for CPU.",
                            "`minAvailable` is deprecated."
                    ],
                    "answer": 1,
                    "explanation": "A PDB specification allows either `minAvailable` (minimum healthy pods that must remain) or `maxUnavailable` (maximum pods that can be down simultaneously). Specifying both in the same PDB is rejected by the API server schema."
            },
            {
                    "question": "What happens if an administrator runs `kubectl drain <node>` when a Pod running on that node is protected by a PDB requiring `minAvailable: 100%`?",
                    "options": [
                            "The node is drained immediately without warnings.",
                            "The Eviction API rejects the eviction with HTTP 429 Too Many Requests, causing `kubectl drain` to stall and retry indefinitely until the timeout expires or the budget is relaxed.",
                            "The PDB is automatically deleted by the node controller.",
                            "The entire cluster is rebooted."
                    ],
                    "answer": 1,
                    "explanation": "A PDB of `minAvailable: 100%` or `maxUnavailable: 0` creates a drain deadlock. The API server refuses eviction requests, blocking automated node upgrades or drain operations until an operator intervenes."
            },
            {
                    "question": "Does a PodDisruptionBudget protect applications from involuntary disruptions such as hardware node power loss or kernel panics?",
                    "options": [
                            "Yes; PDBs restart hardware automatically.",
                            "No; PDBs safeguard ONLY against voluntary disruptions (e.g. `kubectl drain`, cluster autoscaler scale-down, automated node pool upgrades); they cannot prevent physical hardware crashes or kernel failures.",
                            "Yes, by maintaining a redundant cold spare node.",
                            "Yes, if the cluster runs on cloud VMs."
                    ],
                    "answer": 1,
                    "explanation": "PDBs govern only voluntary administrative operations routed through the Kubernetes Eviction API. They cannot prevent involuntary disruptions like hardware failure, kernel panics, or unexpected host reboots."
            },
            {
                    "question": "What is the purpose of the `spec.unhealthyPodEvictionPolicy` setting introduced in Kubernetes 1.27+ for PDBs?",
                    "options": [
                            "It sends an alert to PagerDuty when a pod is unhealthy.",
                            "It controls whether pods that are already unhealthy or failing readiness probes are allowed to be evicted immediately during a drain, preventing unhealthy pods from permanently blocking node maintenance.",
                            "It automatically restarts all unhealthy pods every 60 seconds.",
                            "It marks unhealthy pods as completed."
                    ],
                    "answer": 1,
                    "explanation": "`unhealthyPodEvictionPolicy: AlwaysAllow` allows eviction of pods that are already not ready/unhealthy regardless of budget constraints, ensuring broken application pods do not deadlock cluster node maintenance drains."
            }
    ],
    42: [
            {
                    "question": "What is the primary operational distinction between a `livenessProbe` and a `readinessProbe` in Kubernetes?",
                    "options": [
                            "A livenessProbe restarts the container if it fails, whereas a readinessProbe removes the Pod's IP from Service endpoints without restarting it.",
                            "A livenessProbe checks CPU usage, whereas a readinessProbe checks memory usage.",
                            "A readinessProbe kills the Pod immediately, while a livenessProbe sends a warning to the event log.",
                            "A livenessProbe is executed only once at boot, while a readinessProbe runs continuously."
                    ],
                    "answer": 0,
                    "explanation": "If a livenessProbe fails `failureThreshold` times, kubelet restarts the container. If a readinessProbe fails, kubelet sets `Ready=False` so endpoints controllers remove the pod from Service traffic routing without terminating the process."
            },
            {
                    "question": "When deploying a legacy or JVM-based application that takes 3 minutes to warm up before serving requests, which probe should you configure to prevent premature container restarts?",
                    "options": [
                            "A high-frequency `readinessProbe` with `failureThreshold: 1`.",
                            "A `startupProbe` with sufficient `failureThreshold` and `periodSeconds` to disable liveness/readiness probes until initialization completes.",
                            "An initContainer running `sleep 180`.",
                            "A `terminationGracePeriodSeconds` set to 300."
                    ],
                    "answer": 1,
                    "explanation": "A `startupProbe` disables liveness and readiness checks until it succeeds for the first time. This protects slow-starting applications from being killed by aggressive liveness probes during boot."
            },
            {
                    "question": "Which of the following is NOT a native probe mechanism supported by the Kubernetes kubelet in modern versions (v1.24+)?",
                    "options": [
                            "`httpGet`",
                            "`tcpSocket`",
                            "`grpc`",
                            "`smtpPing`"
                    ],
                    "answer": 3,
                    "explanation": "Kubernetes natively supports four probe mechanisms: `httpGet` (HTTP status 200-399), `tcpSocket` (TCP connection establishment), `exec` (exit code 0 inside container), and `grpc` (gRPC health checking protocol). `smtpPing` is not a Kubernetes probe type."
            },
            {
                    "question": "What happens if a Pod's container defines a `readinessProbe` with `initialDelaySeconds: 10`, `periodSeconds: 5`, and `failureThreshold: 3`, and the probe endpoint starts returning HTTP 500?",
                    "options": [
                            "The container is instantly killed and rescheduled to another node.",
                            "After 3 consecutive failures (approx. 15 seconds), the Pod condition Ready becomes False, and endpoints controllers strip its IP from backend Services.",
                            "The API server scales the deployment replicas up by 1.",
                            "The Pod enters CrashLoopBackOff state."
                    ],
                    "answer": 1,
                    "explanation": "Readiness failure transitions the Pod to not ready. The container process continues running, but Service endpoints stop routing ingress traffic to it until consecutive successful probes pass `successThreshold`."
            },
            {
                    "question": "Why is running an intensive shell script in an `exec` probe every 2 seconds generally considered an anti-pattern in high-density production clusters?",
                    "options": [
                            "Because `exec` probes run on the control plane instead of the worker node.",
                            "Because each `exec` probe invocation forks and executes new processes inside the container namespace, consuming host PID resources and CPU overhead.",
                            "Because `exec` probes automatically invalidate Docker image layers.",
                            "Because `exec` probes can only check files in `/tmp`."
                    ],
                    "answer": 1,
                    "explanation": "Executing shell commands inside a container requires the container runtime to fork and exec a process (e.g. `/bin/sh`), which incurs kernel overhead, creates transient PIDs, and risks node exhaustion at high scale compared to lightweight socket/HTTP probes."
            },
            {
                    "question": "Which container probe setting controls how many consecutive successful probe responses are required before a previously failed container is marked healthy again?",
                    "options": [
                            "`initialDelaySeconds`",
                            "`timeoutSeconds`",
                            "`successThreshold`",
                            "`failureThreshold`"
                    ],
                    "answer": 2,
                    "explanation": "`successThreshold` defines minimum consecutive successes for the probe to be considered successful after having failed (defaults to 1; must be 1 for liveness and startup probes)."
            }
    ],
    43: [
            {
                    "question": "What primary scalability bottleneck in large Kubernetes clusters led to the creation of `EndpointSlice` resources to replace legacy `Endpoints`?",
                    "options": [
                            "Legacy Endpoints did not support IPv6.",
                            "A single Endpoints object contained all Pod IPs for a service; updating a single Pod in a 5,000-replica service forced the API server to serialize and broadcast the entire multi-megabyte object to all nodes.",
                            "Legacy Endpoints were limited to only 3 backend pods.",
                            "Endpoints could not resolve DNS SRV records."
                    ],
                    "answer": 1,
                    "explanation": "Monolithic Endpoints objects scaled poorly because any single pod change caused complete re-serialization and transmission of thousands of IPs. EndpointSlices chunk endpoints into smaller sets (default 100 endpoints per slice), drastically reducing network and CPU overhead."
            },
            {
                    "question": "By default, how many backend endpoints does the Kubernetes `EndpointSlice` controller pack into a single `EndpointSlice` resource before creating an additional slice?",
                    "options": [
                            "10",
                            "100",
                            "1,000",
                            "65,535"
                    ],
                    "answer": 1,
                    "explanation": "By default, the EndpointSlice controller distributes endpoints across slices of up to 100 endpoints each (controlled by the `--max-endpoints-per-slice` flag on kube-controller-manager)."
            },
            {
                    "question": "How do you define a 'Headless Service' in Kubernetes, and what is its primary DNS behavior?",
                    "options": [
                            "Set `spec.type: ExternalName`; it maps external CNAME records.",
                            "Set `spec.clusterIP: None`; DNS queries for the service name return direct A/AAAA records for the individual backing Pod IPs instead of a single virtual ClusterIP.",
                            "Omit `spec.ports`; it disables all networking on the pod.",
                            "Set `metadata.annotations: headless=true`; it disables TLS termination."
                    ],
                    "answer": 1,
                    "explanation": "Specifying `clusterIP: None` creates a Headless Service. Without a virtual cluster IP, CoreDNS returns the set of matching Pod IP addresses directly, which is critical for stateful clustering (e.g. Cassandra, ZooKeeper, Elasticsearch)."
            },
            {
                    "question": "When querying CoreDNS for a StatefulSet pod named `db-0` governed by a headless service named `db-headless` in namespace `prod`, what FQDN resolves directly to `db-0`'s IP?",
                    "options": [
                            "`db-0.db-headless.prod.svc.cluster.local`",
                            "`db-headless.db-0.prod.pod.cluster.local`",
                            "`db-0.prod.cluster.local`",
                            "`statefulset.db-0.svc.cluster.local`"
                    ],
                    "answer": 0,
                    "explanation": "Kubernetes automatically registers predictable A records for StatefulSet pods with the pattern `<pod-name>.<service-name>.<namespace>.svc.<cluster-domain>`."
            },
            {
                    "question": "What information does an `EndpointSlice` store for each backend endpoint that legacy `Endpoints` did not natively model in a first-class structured format?",
                    "options": [
                            "Docker image hash and container creation timestamp.",
                            "Endpoint conditions (`ready`, `serving`, `terminating`) and topology zone hints for topology-aware routing.",
                            "Host CPU utilization percentages.",
                            "Linux kernel routing table entries."
                    ],
                    "answer": 1,
                    "explanation": "EndpointSlice objects include structured endpoint conditions (`ready`, `serving`, `terminating`), node names, and `zone` topology information that enable Topology Aware Routing without cluster-wide broadcasts."
            },
            {
                    "question": "If a Pod in a StatefulSet is terminating (`deletionTimestamp` is set) but still finishing active connections, how does an `EndpointSlice` represent its state compared to `spec.publishNotReadyAddresses`?",
                    "options": [
                            "The slice immediately deletes the endpoint entry.",
                            "The endpoint's `conditions.ready` becomes `false`, but `conditions.terminating` becomes `true` (and `serving` remains `true` if configured), enabling graceful traffic draining.",
                            "The Pod is marked as a static pod.",
                            "The EndpointSlice crashes."
                    ],
                    "answer": 1,
                    "explanation": "EndpointSlices distinguish between `ready`, `serving`, and `terminating`. This allows traffic forwarders (kube-proxy, ingress controllers) to gracefully drain in-flight requests during rolling updates."
            }
    ],
    44: [
            {
                    "question": "What built-in admission mechanism replaced the deprecated `PodSecurityPolicy` (PSP) starting in Kubernetes 1.25+?",
                    "options": [
                            "AppArmor Controller",
                            "Pod Security Admission (PSA) enforcing Pod Security Standards (PSS)",
                            "SELinux DaemonSet",
                            "IPTables Security Agent"
                    ],
                    "answer": 1,
                    "explanation": "Pod Security Admission (PSA) is the native replacement for PSP. It evaluates pods against three standardized profiles (`privileged`, `baseline`, `restricted`) defined by the Pod Security Standards."
            },
            {
                    "question": "Which of the three Pod Security Standards (PSS) levels enforces the most stringent security best practices, prohibiting privilege escalation, host namespaces, and requiring rootless execution?",
                    "options": [
                            "`privileged`",
                            "`baseline`",
                            "`restricted`",
                            "`isolated`"
                    ],
                    "answer": 2,
                    "explanation": "`restricted` is the most secure profile; it mandates running as non-root, drops all default Linux capabilities except `NET_BIND_SERVICE`, forbids host namespaces, and requires volume restrictions."
            },
            {
                    "question": "How do cluster administrators configure Pod Security Admission policies on a target namespace?",
                    "options": [
                            "By creating custom iptables chains on worker nodes.",
                            "By applying standard labels to the namespace object (e.g., `pod-security.kubernetes.io/enforce: restricted`).",
                            "By editing `/etc/shadow` inside container images.",
                            "By mounting a ConfigMap to kubelet's static manifests directory."
                    ],
                    "answer": 1,
                    "explanation": "PSA is configured declaratively using namespace labels with three modes: `enforce` (rejects violating pods), `audit` (logs violations in audit logs), and `warn` (returns user-facing CLI warnings)."
            },
            {
                    "question": "What is the key difference between the `enforce` mode and the `audit` mode in Pod Security Admission?",
                    "options": [
                            "`enforce` modifies pod manifests to fix them, while `audit` deletes violating namespaces.",
                            "`enforce` rejects the pod creation request if it breaches the standard, whereas `audit` allows the pod to run but records an event in the API audit log.",
                            "`audit` restarts kube-apiserver on every violation.",
                            "`enforce` applies only to worker nodes; `audit` applies only to control plane nodes."
                    ],
                    "answer": 1,
                    "explanation": "`enforce` acts as an active gatekeeper that rejects HTTP POST/PUT requests for non-compliant pods. `audit` allows deployments to proceed without disruption while logging violations for compliance analysis."
            },
            {
                    "question": "Under the `baseline` Pod Security Standard profile, which of the following container configurations is permitted?",
                    "options": [
                            "Running in privileged mode (`securityContext.privileged: true`).",
                            "Sharing the host network namespace (`spec.hostNetwork: true`).",
                            "Running as root (`runAsUser: 0`) without privileged capabilities.",
                            "Sharing the host PID namespace (`spec.hostPID: true`)."
                    ],
                    "answer": 2,
                    "explanation": "The `baseline` profile prevents known privilege escalations (forbidding `privileged: true`, `hostPID`, `hostIPC`, `hostNetwork`), but intentionally allows running as root to support off-the-shelf container images that have not yet been refactored for rootless execution."
            },
            {
                    "question": "Why is namespace labeling preferred over custom third-party admission webhooks for basic pod hardening in standard Kubernetes?",
                    "options": [
                            "Because namespace labels do not require any external controllers, webhooks, or latency overhead; PSA is compiled directly into kube-apiserver.",
                            "Because third-party webhooks cannot inspect container manifests.",
                            "Because PSA automatically encrypts all container disk storage.",
                            "Because namespace labels work even if the API server is turned off."
                    ],
                    "answer": 0,
                    "explanation": "PSA is a built-in admission plugin in `kube-apiserver`. Enabling it via namespace labels incurs zero network webhook roundtrips and zero external dependencies, providing deterministic baseline security out of the box."
            }
    ],
    45: [
            {
                    "question": "What is the primary function of a `CustomResourceDefinition` (CRD) in Kubernetes?",
                    "options": [
                            "It compiles new C++ extensions directly into the Linux kernel on worker nodes.",
                            "It extends the Kubernetes API by registering new declarative resource types (kinds and API groups) backed by etcd storage without modifying Kubernetes core code.",
                            "It overrides the etcd consensus algorithm with Paxos.",
                            "It automatically generates Dockerfiles for container applications."
                    ],
                    "answer": 1,
                    "explanation": "CRDs allow developers to define custom REST endpoints and schemas in the Kubernetes API. The API server serves and stores them in etcd just like native Pods or Deployments."
            },
            {
                    "question": "In the Kubernetes Operator pattern, what component is responsible for turning declarative Custom Resources into actual running infrastructure?",
                    "options": [
                            "The Linux systemd init system.",
                            "A Custom Controller executing a continuous Reconcile Loop that watches CR events and brings actual state into alignment with desired state.",
                            "The DNS resolver inside CoreDNS.",
                            "The kube-proxy iptables rules generator."
                    ],
                    "answer": 1,
                    "explanation": "An Operator consists of a CRD plus a custom controller. The controller's reconcile loop continuously compares observed state against the custom resource spec and executes corrective operations (e.g. database backups, clustering)."
            },
            {
                    "question": "Which schema validation format is mandatory for defining the structure and data types of fields in a `CustomResourceDefinition` (`apiextensions.k8s.io/v1`)?",
                    "options": [
                            "Protocol Buffers v2",
                            "OpenAPI v3 JSON Schema (`spec.versions[*].schema.openAPIV3Schema`)",
                            "SQL DDL Schemas",
                            "XML Document Type Definitions (DTD)"
                    ],
                    "answer": 1,
                    "explanation": "Kubernetes requires CRDs in `apiextensions.k8s.io/v1` to define structural schemas using OpenAPI v3 JSON Schema for client-side and server-side validation."
            },
            {
                    "question": "What mechanism does an efficient Kubernetes controller use to watch for resource updates without overwhelming the API server with constant polling?",
                    "options": [
                            "Cron jobs querying `kubectl get` every second.",
                            "HTTP GET long-polling with chunked transfers.",
                            "Kubernetes Informers and Watch API (`watch=true`) utilizing HTTP chunked streaming and local caching.",
                            "Direct SSH connections to worker nodes."
                    ],
                    "answer": 2,
                    "explanation": "Controllers use client-go Informers and the API Watch stream. The API server streams resource change events (Added, Modified, Deleted) over an open HTTP connection, and informers store state in an in-memory cache."
            },
            {
                    "question": "What is the purpose of the `/status` subresource in a CustomResourceDefinition definition (`spec.versions[*].subresources.status`)?",
                    "options": [
                            "It logs all pod stdout streams to etcd.",
                            "It isolates the resource `.status` field so custom controllers can update status without mutating `.spec`, enforcing role-based permissions and preventing generation bumps.",
                            "It reboots the controller pod whenever a field changes.",
                            "It makes the resource read-only for all cluster administrators."
                    ],
                    "answer": 1,
                    "explanation": "Enabling the `/status` subresource splits updates: users modify `.spec`, while controllers update `.status` via `PUT /apis/.../customs/name/status`. This prevents race conditions and avoids incrementing `metadata.generation` on status-only updates."
            },
            {
                    "question": "What occurs when you delete a `CustomResourceDefinition` object using `kubectl delete crd <crd-name>`?",
                    "options": [
                            "Only the schema definition is removed; all existing instances of that custom resource remain in etcd.",
                            "The API server purges the custom resource endpoint AND immediately deletes all existing custom resource instances of that kind across all namespaces.",
                            "The worker nodes are drained immediately.",
                            "The API server rejects the deletion until all controllers are uninstalled."
                    ],
                    "answer": 1,
                    "explanation": "Deleting a CRD is a destructive operation: the API server unregisters the REST endpoint and cascades the immediate deletion of all custom resource instances across every namespace in the cluster."
            }
    ],
    46: [
            {
                    "question": "What is the primary difference in purpose between a `ResourceQuota` and a `LimitRange` in Kubernetes?",
                    "options": [
                            "ResourceQuota limits the aggregate resource consumption of an entire namespace, while LimitRange enforces constraints and default values on individual containers/Pods within that namespace.",
                            "ResourceQuota limits network bandwidth; LimitRange limits disk storage.",
                            "ResourceQuota is configured on nodes; LimitRange is configured on the control plane.",
                            "There is no difference; they are aliases for the same object."
                    ],
                    "answer": 0,
                    "explanation": "ResourceQuota sets a macroscopic ceiling for total resources (e.g. max 10 CPUs total across the whole namespace). LimitRange sets microscopic policies on individual containers (e.g. min 100m CPU, max 2 CPU, and default 500m CPU if omitted)."
            },
            {
                    "question": "If a developer submits a Pod manifest that does NOT specify `resources.requests` or `resources.limits`, and the namespace contains a `LimitRange` with `default` and `defaultRequest` values, what happens?",
                    "options": [
                            "The Pod creation is rejected with an HTTP 400 Bad Request error.",
                            "The LimitRanger admission controller automatically mutates the Pod manifest to inject the configured default requests and limits before persisting it to etcd.",
                            "The Pod is scheduled with unbounded CPU and RAM access.",
                            "The node kills the container after 10 seconds."
                    ],
                    "answer": 1,
                    "explanation": "The built-in `LimitRanger` admission controller mutates incoming pods that lack resource specifications, injecting the namespace's `default` (limits) and `defaultRequest` (requests) values."
            },
            {
                    "question": "What happens if a user submits a Pod specifying `resources.limits.memory: 8Gi`, but the namespace has an active `LimitRange` specifying `max.memory: 4Gi` for containers?",
                    "options": [
                            "The pod is accepted, but the container's memory is capped at 4Gi at runtime by cgroups.",
                            "The API server rejects the Pod creation with an admission error stating that the requested limit exceeds the maximum allowable container limit.",
                            "The API server automatically adds a second worker node.",
                            "The Pod is scheduled but permanently placed in Pending state."
                    ],
                    "answer": 1,
                    "explanation": "LimitRange validation occurs during the admission phase. If any container request or limit violates `min`, `max`, or `maxLimitRequestRatio`, the API server rejects the creation request immediately with a validation error."
            },
            {
                    "question": "Why is configuring a `LimitRange` with default requests especially critical in a namespace governed by a `ResourceQuota` that tracks compute resources?",
                    "options": [
                            "Because ResourceQuotas cannot function without a CNI plugin.",
                            "Because if a namespace has a CPU/memory ResourceQuota, any Pod submitted without explicit resource requests will be rejected by the Quota controller unless a LimitRange injects default requests.",
                            "Because LimitRange encrypts Secret keys used by ResourceQuotas.",
                            "Because ResourceQuota requires LimitRange to calculate billing costs."
                    ],
                    "answer": 1,
                    "explanation": "When a ResourceQuota tracks compute resources (like `requests.cpu`), every container in that namespace MUST declare requests. If users omit them, the quota controller rejects the pod unless a LimitRange is present to provide default requests automatically."
            },
            {
                    "question": "What constraint does the `maxLimitRequestRatio` field in a `LimitRange` object enforce on a container?",
                    "options": [
                            "It limits the maximum allowable ratio between a container's limit and its request (e.g. limit cannot be more than 2x the request), preventing excessive overcommit.",
                            "It enforces the ratio between CPU cores and memory in gigabytes.",
                            "It controls the ratio between pod replicas and worker node count.",
                            "It limits the ratio between TCP and UDP traffic."
                    ],
                    "answer": 0,
                    "explanation": "`maxLimitRequestRatio` caps how aggressively a container can burst beyond its guaranteed request (e.g. `limit / request <= 2`), protecting nodes from sudden resource starvation due to high overcommitment."
            },
            {
                    "question": "Which types of resources can a `LimitRange` restrict within a namespace?",
                    "options": [
                            "`Container`, `Pod`, and `PersistentVolumeClaim` (storage min/max requests).",
                            "Only CPU and Memory on Docker daemons.",
                            "Only API server network bandwidth.",
                            "Only physical server rack temperatures."
                    ],
                    "answer": 0,
                    "explanation": "A LimitRange can enforce constraints across three resource types: `Container` (min/max/default CPU and memory), `Pod` (total min/max across all containers), and `PersistentVolumeClaim` (min/max storage request sizes)."
            }
    ],
}
