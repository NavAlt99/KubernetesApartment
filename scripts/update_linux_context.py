#!/usr/bin/env python3
"""
scripts/update_linux_context.py

Enhances the Linux OS/Kernel sections in enriched_topics_*.py with contextual bridges
explaining WHY Kubernetes requires each Linux feature before detailing the kernel mechanics.
"""

import sys

def apply_replacements(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    applied = 0
    for old_str, new_str in replacements:
        if old_str in content:
            content = content.replace(old_str, new_str, 1)
            applied += 1
        else:
            print(f"Warning: pattern not found in {filepath}:\n{old_str[:70]}...")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {applied}/{len(replacements)} sections in {filepath}")

# 1. enriched_topics_1_10.py
replacements_1_10 = [
    (
        "### Linux Kernel & OS Foundation\n- **Namespaces (Isolation):**",
        "### Linux Kernel & OS Foundation\nBefore Kubernetes can schedule multiple workloads on shared machines, the Linux kernel must provide isolation so containers cannot interfere with each other's processes, files, or network. Two foundational kernel primitives make this multi-tenant execution possible:\n- **Namespaces (Isolation):**"
    ),
    (
        "### Linux OS Node Requirements\n- **Kernel Forwarding & Netfilter:**",
        "### Linux OS Node Requirements\nWorker nodes run standard Linux distributions whose default network and memory settings conflict with container orchestration. The host kernel must be explicitly tuned to permit cross-interface forwarding and predictable memory allocation:\n- **Kernel Forwarding & Netfilter:**"
    ),
    (
        "### Linux System & Network Concepts\n- **mTLS Mutual Authentication:**",
        "### Linux System & Network Concepts\nThe API server is the single security perimeter for cluster management. Rather than relying on simple passwords or unprotected HTTP, Kubernetes relies on the operating system's cryptographic TLS stack and persistent connection multiplexing to safeguard cluster communications:\n- **mTLS Mutual Authentication:**"
    ),
    (
        "### Linux Storage & Performance Realities\n- **Fsync Latency Requirement:**",
        "### Linux Storage & Performance Realities\netcd guarantees strong consistency for all cluster state. To prevent split-brain situations or corrupted state machines during node crashes, it relies directly on synchronous Linux filesystem flush operations where disk speed dictates cluster health:\n- **Fsync Latency Requirement:**"
    ),
    (
        "### Linux Capacity Evaluation\n- The scheduler reads node capacity summaries",
        "### Linux Capacity Evaluation\nThe scheduler cannot simply rely on static node specifications because host daemons and background tasks continuously consume memory and CPU. It queries live kernel status files exposed by the Linux subsystem:\n- The scheduler reads node capacity summaries"
    ),
    (
        "### Linux OS Integration\n- Static pods execute container runtimes while the control plane is offline or uninitialized.",
        "### Linux OS Integration\nStatic Pods solve a chicken-and-egg dilemma: components like the API server and etcd must run as containers, but the API server does not exist yet to schedule them. The kubelet uses the host's Linux filesystem directly to bootstrap these core services:\n- Static pods execute container runtimes while the control plane is offline or uninitialized."
    ),
    (
        "### Linux System & Kernel Mechanisms\n- **cgroup Management:**",
        "### Linux System & Kernel Mechanisms\nThe kubelet is the primary bridge between Kubernetes API declarations and actual Linux process management. When an engineer defines resource limits or restart policies, the kubelet translates those high-level directives into host-level Linux kernel structures:\n- **cgroup Management:**"
    ),
    (
        "### Linux Netfilter & Connection Tracking\n- **DNAT (Destination NAT):**",
        "### Linux Netfilter & Connection Tracking\nClusterIP addresses are virtual constructs with no physical network cards or MAC addresses attached. When a packet targets a Service, the Linux kernel's packet processing framework intercepts the connection before standard routing can discard it:\n- **DNAT (Destination NAT):**"
    )
]

# 2. enriched_topics_11_20.py
replacements_11_20 = [
    (
        "### Linux OS & Kernel Foundation\n- **Namespaces:** Isolates visibility per container",
        "### Linux OS & Kernel Foundation\nContainers do not exist as independent virtual machines; they are regular Linux processes constrained by the kernel. The container runtime orchestrates these native kernel boundaries whenever a pod starts:\n- **Namespaces:** Isolates visibility per container"
    ),
    (
        "### Linux Namespace Sharing\n- Processes in the Pod share the network namespace",
        "### Linux Namespace Sharing\nThe sidecar pattern functions because Kubernetes groups containers under shared Linux namespaces rather than isolating each container entirely. This selective boundary sharing enables sidecars to assist the main app with zero network overhead:\n- Processes in the Pod share the network namespace"
    ),
    (
        "### Linux Execution Flow\n- Kubelet starts the init container sandbox",
        "### Linux Execution Flow\nInit containers enforce strict prerequisites before main applications boot. The kubelet relies on Linux process exit status codes to coordinate this startup pipeline:\n- Kubelet starts the init container sandbox"
    ),
    (
        "### Linux Kernel Networking Mechanisms\n- **Virtual Ethernet (veth) Pairs:**",
        "### Linux Kernel Networking Mechanisms\nEvery container starts inside an empty, isolated network namespace without interfaces. The CNI plugin connects this isolated bubble to the host and cluster network using virtual Linux networking devices:\n- **Virtual Ethernet (veth) Pairs:**"
    ),
    (
        "### Linux DNS Resolution & resolv.conf\n- Kubelet automatically populates `/etc/resolv.conf`",
        "### Linux DNS Resolution & resolv.conf\nApplications expect to discover services using simple DNS names like 'auth-db' instead of dynamic IP addresses. To facilitate this transparently, the kubelet configures the standard Linux resolver file inside every container filesystem:\n- Kubelet automatically populates `/etc/resolv.conf`"
    ),
    (
        "### Linux Kernel Enforcement\n- NetworkPolicies are **not** enforced by core Kubernetes",
        "### Linux Kernel Enforcement\nA NetworkPolicy is purely a declarative specification in etcd; core Kubernetes contains no packet filtering engine. Real traffic filtering depends entirely on kernel-level packet inspection configured by the CNI:\n- NetworkPolicies are **not** enforced by core Kubernetes"
    ),
    (
        "### Linux Storage Subsystem Integration\n- Backed by the **Container Storage Interface (CSI)** standard.",
        "### Linux Storage Subsystem Integration\nKubernetes PersistentVolumes abstract away cloud and SAN storage systems. However, before an application container can read or write files, the host Linux kernel must format the physical block device and bind-mount it into the container's isolated filesystem:\n- Backed by the **Container Storage Interface (CSI)** standard."
    )
]

# 3. enriched_topics_21_30.py
replacements_21_30 = [
    (
        "### Workload Consumption\n- Pods mount storage by referencing the PVC name",
        "### Workload Consumption\nFrom the container's perspective, storage must appear as a standard local folder. The kubelet bridges the cluster storage abstraction to the container using Linux mount namespace mechanics:\n- Pods mount storage by referencing the PVC name"
    ),
    (
        "### Dynamic Provisioning Lifecycle\n- When a PVC is created without a matching static PV",
        "### Dynamic Provisioning Lifecycle\nManual volume provisioning cannot keep pace with ephemeral container lifecycles. StorageClasses automate the Linux block device lifecycle by instructing host drivers to create, format, and attach storage on demand:\n- When a PVC is created without a matching static PV"
    ),
    (
        "### Linux Kernel Namespace vs. K8s Namespace\n- **Crucial Distinction:**",
        "### Linux Kernel Namespace vs. K8s Namespace\nEngineers frequently conflate Kubernetes namespaces with Linux kernel namespaces. While they share a name, they operate at completely different tiers of the system stack:\n- **Crucial Distinction:**"
    ),
    (
        "### Linux System Resource Partitioning\n- **Systemd Slice Mapping:**",
        "### Linux System Resource Partitioning\nResourceQuotas cap resource consumption at the API level, but physical node protection requires kernel-level enforcement. The kubelet maps cluster quotas down to Linux cgroup trees on worker nodes:\n- **Systemd Slice Mapping:**"
    )
]

# 4. enriched_topics_31_41.py
replacements_31_41 = [
    (
        "### Linux Process Termination & Restart Policy\n- Container specs inside Jobs only support",
        "### Linux Process Termination & Restart Policy\nBatch computing requires knowing when a task has finished successfully versus crashed. The Job controller evaluates Linux process exit codes returned by the container runtime to determine job completion:\n- Container specs inside Jobs only support"
    ),
    (
        "### Linux Kernel Cgroup In-Place Updates\n- Historical Kubernetes required pod eviction",
        "### Linux Kernel Cgroup In-Place Updates\nTraditional container resizing required terminating the process and recreating the pod. Modern Kubernetes leverages dynamic Linux cgroup controller updates to adjust CPU and memory without restarting running applications:\n- Historical Kubernetes required pod eviction"
    )
]

if __name__ == "__main__":
    apply_replacements("scripts/enriched_topics_1_10.py", replacements_1_10)
    apply_replacements("scripts/enriched_topics_11_20.py", replacements_11_20)
    apply_replacements("scripts/enriched_topics_21_30.py", replacements_21_30)
    apply_replacements("scripts/enriched_topics_31_41.py", replacements_31_41)
    print("All Linux context enrichments applied.")
