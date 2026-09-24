#!/usr/bin/env python3
"""
scripts/update_demos.py
Improves thin demo sections in original_zine_data.json for topics that
have very basic or no meaningful commands.
"""

import json

IMPROVED_DEMOS = {
    1: """SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl cluster-info
  2. kubectl get nodes -o wide
  3. kubectl get pods -A -o wide --field-selector status.phase=Running | head -20
  4. kubectl get namespaces

WHAT YOU SHOULD SEE
  cluster-info prints the control-plane and CoreDNS API URLs — the single
  management endpoint for the entire cluster.
  get nodes shows every node with ROLES (control-plane vs <none>), STATUS,
  INTERNAL-IP, and which container runtime version is running.
  get pods -A shows all running workloads across all namespaces — the
  cluster's unified view of every running container.
  This is the 'one complex' — one command, all nodes, all pods.

CLEANUP
  (nothing to clean up)

NOTE
  Compare this to the alternative: SSH into each machine and run
  'docker ps' manually. That is the pre-Kubernetes world.""",

    2: """SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get nodes --show-labels | grep -E 'control-plane|NAME'
  2. kubectl get pods -n kube-system -o wide
  3. kubectl describe node zine-control-plane | grep -E 'Taints|Roles|Conditions' | head -10
  4. kubectl get lease -n kube-node-lease

WHAT YOU SHOULD SEE
  Step 1: control-plane node is labelled node-role.kubernetes.io/control-plane.
  Step 2: kube-system shows api-server, etcd, scheduler, controller-manager Pods
    all running on the control-plane node — not on worker nodes.
  Step 3: the control-plane node shows Taint: node-role.kubernetes.io/control-plane:NoSchedule
    — this is what prevents application Pods from landing on it.
  Step 4: each node has a Lease object it renews every 10 seconds — the lightweight
    heartbeat mechanism replacing heavy Node status updates in modern Kubernetes.

CLEANUP
  (nothing to clean up)

NOTE
  The Taint/NoSchedule confirms the two-region split: control plane components
  run on dedicated nodes, application workloads run on worker nodes.""",

    22: """SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl get storageclass
  2. kubectl get storageclass standard -o yaml | grep -E 'provisioner|volumeBindingMode|reclaimPolicy'
  3. cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sc-demo-pvc
  namespace: zine-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard
EOF
  4. kubectl get pvc sc-demo-pvc -n zine-demo
  5. kubectl get pv | grep sc-demo-pvc

WHAT YOU SHOULD SEE
  Step 1: lists available StorageClasses; one marked (default) is used when
    no storageClassName is specified in a PVC.
  Step 2: shows the provisioner (e.g. rancher.io/local-path for kind) and
    volumeBindingMode — WaitForFirstConsumer means provisioning waits for a Pod.
  Step 4/5: PVC moves to Bound and a PV is dynamically created matching the class.
  This proves dynamic provisioning: no admin pre-created the PV — the StorageClass did it.

CLEANUP
  kubectl delete pvc sc-demo-pvc -n zine-demo
  kubectl delete namespace zine-demo""",

    23: """SETUP
  kubectl create namespace zine-demo

STEPS
  1. kubectl create role pod-reader --verb=get,list,watch --resource=pods -n zine-demo
  2. kubectl get role pod-reader -n zine-demo -o yaml
  3. kubectl auth can-i list pods -n zine-demo --as system:serviceaccount:zine-demo:default
  4. kubectl create rolebinding pod-reader-binding --role=pod-reader --serviceaccount=zine-demo:default -n zine-demo
  5. kubectl auth can-i list pods -n zine-demo --as system:serviceaccount:zine-demo:default

WHAT YOU SHOULD SEE
  Step 2: the Role YAML shows 'verbs', 'resources', and the namespace scope.
  Step 3: 'no' — the default ServiceAccount has no permissions before binding.
  Step 5: 'yes' — the RoleBinding activates the Role for the ServiceAccount.
  This proves the two-step RBAC model: Role defines permissions, RoleBinding activates them.

CLEANUP
  kubectl delete rolebinding pod-reader-binding -n zine-demo
  kubectl delete role pod-reader -n zine-demo
  kubectl delete namespace zine-demo""",

    25: """SETUP
  (none: uses what is already in the cluster)

STEPS
  1. kubectl get clusterroles | grep -v system: | head -10
  2. kubectl describe clusterrole view | grep -E 'Name:|Resources:|Verbs:' | head -15
  3. kubectl auth can-i list nodes --as system:serviceaccount:default:default
  4. kubectl create clusterrole node-viewer --verb=get,list --resource=nodes
  5. kubectl auth can-i list nodes --as system:serviceaccount:default:default
  6. kubectl create clusterrolebinding node-viewer-binding --clusterrole=node-viewer --serviceaccount=default:default
  7. kubectl auth can-i list nodes --as system:serviceaccount:default:default

WHAT YOU SHOULD SEE
  Step 2: ClusterRole 'view' shows cluster-scoped resources and their allowed verbs.
  Step 3: 'no' — default SA cannot list Nodes (cluster-scoped resource).
  Step 5: still 'no' — ClusterRole alone does nothing without a ClusterRoleBinding.
  Step 7: 'yes' — ClusterRoleBinding activates the ClusterRole cluster-wide.
  Nodes are non-namespaced resources; only ClusterRole can grant access to them.

CLEANUP
  kubectl delete clusterrolebinding node-viewer-binding
  kubectl delete clusterrole node-viewer""",

    29: """SETUP
  kubectl create namespace zine-demo-ns

STEPS
  1. kubectl get namespace zine-demo-ns -o yaml | grep -E 'finalizers|phase|status'
  2. kubectl run test-pod --image=nginx -n zine-demo-ns
  3. kubectl get pods -n zine-demo-ns
  4. kubectl delete namespace zine-demo-ns &
  5. sleep 2
  6. kubectl get namespace zine-demo-ns
  7. kubectl get pods -n zine-demo-ns

WHAT YOU SHOULD SEE
  Step 1: the namespace has 'kubernetes' finalizer — this must be cleared before deletion.
  Step 4-6: while deleting, the namespace enters 'Terminating' state. The Namespace
    controller waits for all resources inside (Pods, Services, PVCs) to be deleted before
    the namespace object itself is removed from etcd.
  Step 7: pods are being terminated as part of the cascading namespace cleanup.
  If a resource has a stuck finalizer, the namespace stays 'Terminating' indefinitely.

CLEANUP
  wait   # wait for background delete to complete
  (namespace auto-cleaned)""",
}


with open("scripts/original_zine_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

updated = 0
for item in data:
    num = item["num"]
    if num in IMPROVED_DEMOS:
        item["demo"] = IMPROVED_DEMOS[num].strip()
        updated += 1

with open("scripts/original_zine_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Improved demos for {updated} topics.")
