#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${KIND_CLUSTER_NAME:-zine}"

kubectl config use-context "kind-${CLUSTER_NAME}" >/dev/null
echo '== Nodes =='
kubectl get nodes -o wide
echo
echo '== Kubernetes component health =='
kubectl get pods -n kube-system -o wide
echo
echo '== Runtime =='
kubectl get nodes -o custom-columns='NAME:.metadata.name,RUNTIME:.status.nodeInfo.containerRuntimeVersion'
echo
echo '== kind node containers =='
docker ps --filter "name=${CLUSTER_NAME}-" --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
