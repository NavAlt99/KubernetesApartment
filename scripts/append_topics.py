#!/usr/bin/env python3
"""
Append Topics 42 through 46 to demos-complete.md.
"""

TOPICS_MD = """
## 42. Probes & Health Checks (Liveness, Readiness, Startup)

**Part 1 — Technical Discussion:** Kubernetes relies on three native probe mechanisms executed directly by the worker node's `kubelet` to determine whether a container process is healthy, initialized, and capable of serving user traffic.

### The Three Probe Types
- **`startupProbe`:** Determines whether the application within the container has successfully started. While the `startupProbe` is running, all `livenessProbe` and `readinessProbe` evaluations are paused. If it fails `failureThreshold` times, the container is killed and restarted according to `restartPolicy`. This protects slow-booting legacy or JVM apps.
- **`livenessProbe`:** Periodically validates whether the application is alive and healthy. If the probe fails consecutively, kubelet terminates the container process and initiates a restart. This catches deadlocks, infinite loops, and unrecoverable thread starvation.
- **`readinessProbe`:** Determines whether the container is ready to accept incoming network traffic. If it fails, the Pod condition `Ready` is set to `False`, and Kubernetes endpoints controllers immediately remove the Pod IP from Service backends and `EndpointSlices`. Crucially, **the container is not restarted**.

### Supported Probe Handlers
1. `httpGet`: Initiates an HTTP GET request to a specified port and path. Status codes 200–399 indicate success.
2. `tcpSocket`: Attempts to open a TCP socket connection on a specified port. Successful connection indicates health.
3. `exec`: Executes a command inside the container namespace. Exit code 0 indicates success.
4. `grpc`: Issues a standard gRPC health check request (`grpc.health.v1.HealthCheckRequest`).

```yaml
# comprehensive-probes.yaml
apiVersion: v1
kind: Pod
metadata:
  name: resilient-web-app
  labels:
    app: resilient-web
spec:
  containers:
  - name: api
    image: nginx:alpine
    ports:
    - containerPort: 80
    startupProbe:
      httpGet:
        path: /healthz
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 30 # Gives app up to 150 seconds to initialize
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 80
      periodSeconds: 5
      successThreshold: 1
      failureThreshold: 2
```

![Probes & Health Checks technical illustration](generated/kubernetes-apartment-complex/42-technical.png)

**Technical perspective:** Probes decouple process execution from traffic readiness. A frequent anti-pattern is confusing liveness with readiness: if an external database goes down and a service responds with 500 errors, failing a liveness probe will cause kubelet to restart all pods simultaneously in a cascading thundering herd. In contrast, failing a readiness probe safely withdraws the pods from the load balancer until the database recovers, preserving process state.

**Part 2 — Analogy / Zine:** The resident building safety and inspection protocol: Startup verifies the water heater and gas mains are fully connected before the tenant unpacks; Liveness verifies the tenant hasn't fainted from carbon monoxide (if so, call paramedics/evacuate); Readiness verifies the apartment door is unlocked and tidy before allowing postal carriers and guests inside.

![Probes & Health Checks zine illustration](generated/kubernetes-apartment-complex/42-zine.png)

**Zine explanation:** The illustration translates container lifecycle checks into apartment safety routines.

* **Zine Text & Layout:**
* (Top): "Probes & Health Checks — The Apartment Inspection Protocols"
* (Caption): "Startup protects boot time, Liveness restarts frozen apps, and Readiness gates front-door traffic."

**Further reading**

- [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod Lifecycle and Container States](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [CKA Study Notes: Application Lifecycle Management](CKA_Study_Notes/04-application-lifecycle-management.md)

### Demo — Probes & Health Checks (Liveness, Readiness, Startup)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (probe-demo.yaml)
  apiVersion: v1
  kind: Pod
  metadata:
    name: probe-demo
    namespace: zine-demo
    labels:
      app: probe-demo
  spec:
    containers:
    - name: web
      image: busybox
      command: ["sh", "-c", "touch /tmp/ready; sleep 20; rm -f /tmp/ready; sleep 600"]
      readinessProbe:
        exec:
          command: ["cat", "/tmp/ready"]
        initialDelaySeconds: 2
        periodSeconds: 3

STEPS
  1. kubectl apply -f probe-demo.yaml
  2. kubectl get pod probe-demo -n zine-demo -w
  3. Notice after 2 seconds READY becomes 1/1.
  4. After 20 seconds /tmp/ready is deleted.
  5. Watch READY transition to 0/1 without the container being killed or restarted.

WHAT YOU SHOULD SEE
  The container remains Running with RESTARTS=0, but READY transitions to 0/1 because readiness governs Service traffic inclusion, not container lifecycle.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Demonstrates how readiness probes isolate pods from traffic without incurring restart penalties.
</pre></div>


## 43. EndpointSlices & Headless Services

**Part 1 — Technical Discussion:** In high-scale Kubernetes clusters, traditional monolithic `Endpoints` objects created severe performance bottlenecks: any change to a single Pod IP in a 5,000-pod service triggered full serialization and broadcast of the entire multi-megabyte object to every worker node running `kube-proxy`. Kubernetes introduced **`EndpointSlice`** (`discovery.k8s.io/v1`) to partition endpoints into smaller, scalable subsets (default 100 endpoints per slice).

### Headless Services (`clusterIP: None`)
When an application requires direct peer-to-peer network connections without intermediate layer-4 proxying or virtual IP load balancing (common in distributed databases, StatefulSets, Kafka, and ZooKeeper), a **Headless Service** is configured with `spec.clusterIP: None`.

- **DNS Behavior:** Instead of returning a single ClusterIP, CoreDNS returns direct DNS `A`/`AAAA` records containing the individual IP addresses of all backing Pods.
- **Predictable SRV Records:** StatefulSet members obtain deterministic FQDNs:
  `$(pod-name).$(service-name).$(namespace).svc.cluster.local`

```yaml
# headless-stateful-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: database-headless
  namespace: data-tier
spec:
  clusterIP: None # Defines a Headless Service
  selector:
    app: distributed-db
  ports:
  - port: 5432
    name: postgres
```

```yaml
# sample-endpointslice.yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: database-headless-abc12
  namespace: data-tier
  labels:
    kubernetes.io/service-name: database-headless
addressType: IPv4
ports:
  - name: postgres
    port: 5432
    protocol: TCP
endpoints:
  - addresses:
      - "10.244.1.42"
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: worker-node-02
    zone: us-east-1a
```

![EndpointSlices & Headless Services technical illustration](generated/kubernetes-apartment-complex/43-technical.png)

**Technical perspective:** EndpointSlices model rich metadata including `conditions.terminating` and `zone` topology hints. This enables **Topology Aware Routing**, allowing kube-proxy to route traffic preferentially to Pods within the same availability zone, slashing cross-zone egress latency and cloud transit bandwidth costs.

**Part 2 — Analogy / Zine:** The resident intercom and direct telephone directory: Instead of forcing every piece of mail and caller to pass through a single crowded front desk receptionist (ClusterIP), a direct intercom system (Headless Service) allows visitors to buzz individual apartments directly. For massive towers with thousands of units, the front lobby organizes tenant names into modular 100-resident ring binders (EndpointSlices) rather than a single monolithic phone book.

![EndpointSlices & Headless Services zine illustration](generated/kubernetes-apartment-complex/43-zine.png)

**Zine explanation:** Translating direct service discovery and scalable endpoint chunking into building intercom directories.

* **Zine Text & Layout:**
* (Top): "EndpointSlices & Headless Services — The Direct Intercom"
* (Caption): "Bypasses virtual IPs to give stateful pods direct DNS records and chunks endpoints for massive scale."

**Further reading**

- [EndpointSlices Documentation](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [CKA Study Notes: Networking & Service Discovery](CKA_Study_Notes/07-networking.md)

### Demo — EndpointSlices & Headless Services

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (headless-demo.yaml)
  apiVersion: v1
  kind: Service
  metadata:
    name: db-headless
    namespace: zine-demo
  spec:
    clusterIP: None
    selector:
      app: db
    ports:
    - port: 80
      name: http
  ---
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: db-nodes
    namespace: zine-demo
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: db
    template:
      metadata:
        labels:
          app: db
      spec:
        containers:
        - name: nginx
          image: nginx:alpine

STEPS
  1. kubectl apply -f headless-demo.yaml
  2. kubectl get svc db-headless -n zine-demo     # CLUSTER-IP will show None
  3. kubectl get endpointslices -n zine-demo -l kubernetes.io/service-name=db-headless
  4. kubectl describe endpointslice -n zine-demo -l kubernetes.io/service-name=db-headless

WHAT YOU SHOULD SEE
  The EndpointSlice displays each individual Pod IP address with conditions (ready=true), node name, and protocol mapping, while the Service has no virtual cluster IP.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Headless services power stateful clustering where pods need to establish direct socket connections to specific peers.
</pre></div>


## 44. Pod Security Standards (PSS) & Admission (PSA)

**Part 1 — Technical Discussion:** Following the deprecation and removal of `PodSecurityPolicy` (PSP) in Kubernetes 1.25+, the native **Pod Security Admission (PSA)** controller implements built-in security policies based on the CNCF **Pod Security Standards (PSS)**.

### The Three Security Profiles
1. **`Privileged`:** Completely unrestricted policy. Containers may run as root, share host namespaces (`hostPID`, `hostNetwork`, `hostIPC`), access raw host block devices, and enable all Linux capabilities. Intended only for system daemons and CNI/CSI drivers.
2. **`Baseline`:** Minimally restrictive policy that prevents known privilege escalations with minimal configuration friction. Forbids `privileged: true`, host namespaces, host ports, and capabilities beyond a safe default list, but **allows running as root user**.
3. **`Restricted`:** Heavily hardened policy enforcing modern cloud-native security best practices. Mandates:
   - Rootless execution (`runAsNonRoot: true`, `runAsUser: > 0`).
   - Disallowing privilege escalation (`allowPrivilegeEscalation: false`).
   - Dropping all capabilities (`drop: ["ALL"]`) with optional addition of `NET_BIND_SERVICE`.
   - Read-only root filesystems (`readOnlyRootFilesystem: true`).
   - Restricted volume types (only `configMap`, `secret`, `emptyDir`, `projected`, `downwardAPI`, `persistentVolumeClaim`).

### Namespace Policy Configuration
PSA is configured declaratively using standardized namespace labels across three evaluation modes:
- `pod-security.kubernetes.io/enforce`: Rejects pods that violate the standard.
- `pod-security.kubernetes.io/audit`: Allows violating pods to run, but generates an audit log entry.
- `pod-security.kubernetes.io/warn`: Returns user-facing CLI warnings upon submission without blocking.

```yaml
# hardened-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: finance-workloads
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

```yaml
# compliant-restricted-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-microservice
  namespace: finance-workloads
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginxinc/nginx-unprivileged:alpine
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

![Pod Security Standards technical illustration](generated/kubernetes-apartment-complex/44-technical.png)

**Technical perspective:** Built-in PSA eliminates the operational overhead, latency penalty, and failure modes of maintaining external third-party mutating admission webhooks for baseline cluster hygiene. By pinning `enforce-version: v1.31`, teams avoid surprise validation breaks when upgrading Kubernetes control plane versions.

**Part 2 — Analogy / Zine:** Building safety codes and fire marshal regulations: The building manager tags wings with standardized safety tiers: Maintenance Workshops (Privileged — heavy equipment and blowtorches allowed), Residential Suites (Baseline — standard appliances, no commercial stoves), and High-Security Bio-Clean Wing (Restricted — fireproof furnishings, non-combustible clothing, and zero open flames permitted). The fire marshal checks every blueprint at the door and blocks entry if fire codes are breached.

![Pod Security Standards zine illustration](generated/kubernetes-apartment-complex/44-zine.png)

**Zine explanation:** Mapping cluster isolation profiles to building safety standards and fire marshal code enforcement.

* **Zine Text & Layout:**
* (Top): "Pod Security Standards — Building Safety Codes"
* (Caption): "Privileged, Baseline, and Restricted profiles enforced natively at admission without external webhooks."

**Further reading**

- [Pod Security Standards Documentation](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [CKA Study Notes: Security Primitives & Hardening](CKA_Study_Notes/06-security.md)

### Demo — Pod Security Standards (PSS) & Admission (PSA)

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace pss-demo
  kubectl label namespace pss-demo pod-security.kubernetes.io/enforce=restricted

YAML  (insecure-pod.yaml)
  apiVersion: v1
  kind: Pod
  metadata:
    name: insecure-pod
    namespace: pss-demo
  spec:
    containers:
    - name: nginx
      image: nginx:alpine

STEPS
  1. kubectl apply -f insecure-pod.yaml
  2. Observe the immediate API admission rejection error:
     'Error from server (Forbidden): pods "insecure-pod" is forbidden: violates PodSecurity "restricted:latest"...'
  3. Notice it lists violations: runAsNonRoot != true, allowPrivilegeEscalation != false, capabilities.drop != ALL.

WHAT YOU SHOULD SEE
  The API server strictly denies the request without persisting the object to etcd or scheduling it to any worker node.

CLEANUP
  kubectl delete namespace pss-demo

NOTE
  Demonstrates declarative zero-trust namespace admission enforcement without third-party plugins.
</pre></div>


## 45. CustomResourceDefinitions (CRDs) & Operators

**Part 1 — Technical Discussion:** Kubernetes is engineered as a fully extensible platform. A **CustomResourceDefinition (CRD)** (`apiextensions.k8s.io/v1`) registers new resource endpoints in the Kubernetes API, allowing developers to define domain-specific abstractions (e.g. `PostgreSQLCluster`, `KafkaTopic`, `BackupSchedule`) that behave identically to native primitives.

### The Operator Pattern
A CRD defines only the **schema** (desired state); it has no operational intelligence. An **Operator** pairs a CRD with a **Custom Controller** that runs a continuous **Reconcile Loop**:
1. **Observe:** The controller watches Custom Resources and dependent child resources using `client-go` Informers and Watch streams.
2. **Analyze:** Compares the actual observed cluster state against the desired state declared in `.spec`.
3. **Act:** Executes corrective operations (provisioning StatefulSets, triggering automated database backups, executing failover promotions).

```yaml
# postgres-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.database.example.com
spec:
  group: database.example.com
  names:
    kind: PostgresCluster
    listKind: PostgresClusterList
    plural: postgresclusters
    singular: postgrescluster
    shortNames:
    - pg
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["replicas", "storageSize"]
            properties:
              replicas:
                type: integer
                minimum: 1
                maximum: 5
              storageSize:
                type: string
                pattern: "^[0-9]+(Gi|Mi)$"
    subresources:
      status: {}
```

```yaml
# my-database-instance.yaml
apiVersion: database.example.com/v1alpha1
kind: PostgresCluster
metadata:
  name: production-db
  namespace: data
spec:
  replicas: 3
  storageSize: 50Gi
```

![CustomResourceDefinitions & Operators technical illustration](generated/kubernetes-apartment-complex/45-technical.png)

**Technical perspective:** Operators encode domain-specific human operational knowledge into self-healing software. Using the `/status` subresource allows operators to record cluster conditions and health metrics without triggering incrementing updates to `.metadata.generation`, preventing infinite reconciliation loops.

**Part 2 — Analogy / Zine:** Specialized external facility contractors: The building installs custom, computerized commercial HVAC refrigeration chillers (Custom Resource). Standard on-site apartment janitors do not know how to rebuild chiller compressors, so management hires a specialized 24/7 HVAC engineering contractor (The Operator). The contractor constantly monitors pressure sensors and coolant levels (Informer) and automatically tunes valves and replaces filters to keep the building chillers operating perfectly (Reconcile Loop).

![CustomResourceDefinitions & Operators zine illustration](generated/kubernetes-apartment-complex/45-zine.png)

**Zine explanation:** Translating Kubernetes custom APIs and autonomous controllers into specialized facility equipment and dedicated maintenance contractors.

* **Zine Text & Layout:**
* (Top): "CRDs & Operators — Specialized Facility Contractors"
* (Caption): "CRDs define new building blueprints; Operators continuously tune actual machinery to match specifications."

**Further reading**

- [Custom Resources Documentation](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- [Operator Pattern Overview](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [Kubebuilder Book](https://book.kubebuilder.io/)

### Demo — CustomResourceDefinitions (CRDs) & Operators

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (crd-demo.yaml)
  apiVersion: apiextensions.k8s.io/v1
  kind: CustomResourceDefinition
  metadata:
    name: apptenants.apartment.demo
  spec:
    group: apartment.demo
    names:
      kind: AppTenant
      plural: apptenants
      shortNames:
      - at
    scope: Namespaced
    versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: ["plan"]
              properties:
                plan:
                  type: string
                  enum: ["basic", "premium"]
  ---
  apiVersion: apartment.demo/v1
  kind: AppTenant
  metadata:
    name: tenant-suite-401
    namespace: zine-demo
  spec:
    plan: premium

STEPS
  1. kubectl apply -f crd-demo.yaml
  2. kubectl get crd apptenants.apartment.demo
  3. kubectl get apptenant -n zine-demo
  4. kubectl describe at tenant-suite-401 -n zine-demo

WHAT YOU SHOULD SEE
  The custom resource is stored and queried via standard kubectl commands just like a native Pod or Deployment, with full schema validation enforced.

CLEANUP
  kubectl delete crd apptenants.apartment.demo
  kubectl delete namespace zine-demo

NOTE
  Deleting a CRD automatically deletes all instances of that resource across all namespaces.
</pre></div>


## 46. LimitRange

**Part 1 — Technical Discussion:** While a `ResourceQuota` controls the **macroscopic** total aggregate resource consumption across an entire namespace, a **`LimitRange`** (`v1`) enforces **microscopic** resource boundaries and defaults on individual containers, pods, or PersistentVolumeClaims within that namespace.

### Core Capabilities of LimitRange
1. **Default Requests & Limits Injection:** If a developer submits a Pod manifest that omits compute requests or limits, the built-in `LimitRanger` admission controller mutates the incoming object to inject configured default values before persisting it to etcd.
2. **Min & Max Bounds Enforcement:** Enforces minimum and maximum allowable bounds for CPU, memory, and storage. Requests or limits outside these bounds cause the API server to reject pod creation immediately.
3. **Burst Ratio Enforcement (`maxLimitRequestRatio`):** Limits how aggressively a container can burst beyond its guaranteed request (e.g. `limit / request <= 2`), curbing extreme resource overcommit and safeguarding node stability.

```yaml
# app-namespace-limits.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-resource-rules
  namespace: engineering
spec:
  limits:
  - type: Container
    default: # Default limit injected if omitted
      cpu: 500m
      memory: 512Mi
    defaultRequest: # Default request injected if omitted
      cpu: 100m
      memory: 128Mi
    max: # Maximum allowed container limit
      cpu: "2"
      memory: 2Gi
    min: # Minimum allowed container request
      cpu: 50m
      memory: 64Mi
    maxLimitRequestRatio:
      cpu: 4
      memory: 4
  - type: PersistentVolumeClaim
    min:
      storage: 1Gi
    max:
      storage: 50Gi
```

![LimitRange technical illustration](generated/kubernetes-apartment-complex/46-technical.png)

**Technical perspective:** A `LimitRange` is mandatory when paired with compute `ResourceQuotas`. If a namespace has a ResourceQuota on `requests.cpu`, Kubernetes rejects any Pod that omits CPU requests; configuring a `LimitRange` ensures default requests are automatically injected, allowing unconfigured pods to run smoothly without manual boilerplate.

**Part 2 — Analogy / Zine:** Apartment appliance power draw caps and breaker panel fuses: While the utility company monitors the whole building's monthly electrical bill (ResourceQuota), each apartment suite has its own circuit breaker panel (LimitRange). You cannot plug in an industrial plasma cutter that draws 50 amps (Max Limit), and if you plug in an unbranded microwave without stating its power consumption, the building assumes a baseline 5 amp draw (Default Request).

![LimitRange zine illustration](generated/kubernetes-apartment-complex/46-zine.png)

**Zine explanation:** Translating per-container compute constraints and default request injection into apartment circuit breaker limits.

* **Zine Text & Layout:**
* (Top): "LimitRange — Appliance Power Draw Limits"
* (Caption): "Sets min/max boundaries and injects default CPU/memory requests to prevent noisy neighbors."

**Further reading**

- [Configure Default Memory and CPU Requests and Limits](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/)
- [Limit Ranges Resource Guide](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [CKA Study Notes: Scheduling & Resource Limits](CKA_Study_Notes/02-scheduling.md)

### Demo — LimitRange

<div style="background:#000;color:#fff;border-radius:8px;padding:1rem;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.25);"><pre style="background:transparent;color:#fff;margin:0;white-space:pre-wrap;">
SETUP
  kubectl create namespace zine-demo

YAML  (limitrange-demo.yaml)
  apiVersion: v1
  kind: LimitRange
  metadata:
    name: demo-limits
    namespace: zine-demo
  spec:
    limits:
    - type: Container
      default:
        cpu: 250m
        memory: 256Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
  ---
  apiVersion: v1
  kind: Pod
  metadata:
    name: unconfigured-pod
    namespace: zine-demo
  spec:
    containers:
    - name: web
      image: nginx:alpine

STEPS
  1. kubectl apply -f limitrange-demo.yaml
  2. kubectl get pod unconfigured-pod -n zine-demo -o yaml | grep -A 5 resources:

WHAT YOU SHOULD SEE
  Although the submitted Pod omitted resources, the LimitRanger admission controller injected requests (100m CPU, 128Mi RAM) and limits (250m CPU, 256Mi RAM) automatically.

CLEANUP
  kubectl delete namespace zine-demo

NOTE
  Essential for multi-tenant clusters to prevent rogue containers from consuming unlimited host resources.
</pre></div>
"""

with open("demos-complete.md", "a", encoding="utf-8") as f:
    f.write(TOPICS_MD)

print("Successfully appended Topics 42 through 46 to demos-complete.md.")
