# Kubernetes Apartment Complex

An illustrated, hands-on guide to Kubernetes control-plane components, node
runtime, networking, storage, RBAC, workload controllers, and autoscaling.

## Contents

- [Complete demo guide](demos-complete.md) — 41 runnable topics with technical
  explanations, zine illustrations, further reading, and kind/Docker demos.
- [Generated illustrations](generated/kubernetes-apartment-complex/) — one
  technical image and one apartment-complex zine image per topic.
- [Zine prompt pack](kubernetes-full-controllers-zine-prompts.fixed.md)

## Local prerequisites

The demos target a disposable multi-node [kind](https://kind.sigs.k8s.io/)
cluster on Docker Desktop. The host uses Docker to run the kind node
containers; kubelet uses containerd inside those nodes through CRI.

See `demos-complete.md` for the cluster configuration, add-on requirements,
cleanup commands, and macOS-specific node inspection commands.
