#!/usr/bin/env sh
set -e
cd $(cd -P -- "$(dirname -- "$0")" && pwd -P)

if [ ! -d "test-bin" ]; then
    # Install minikube and kubernetes
    VERSION=$(curl -Ss "https://storage.googleapis.com/kubernetes-release/release/stable.txt")
    mkdir test-bin
    curl -Lo test-bin/minikube https://storage.googleapis.com/minikube/releases/v0.7.1/minikube-linux-amd64
    chmod +x test-bin/minikube
    curl -Lo test-bin/kubectl http://storage.googleapis.com/kubernetes-release/release/${VERSION}/bin/linux/amd64/kubectl
    chmod +x test-bin/kubectl
fi

# Use local images
find -name "*.py" -exec sed -i "s?ocadotechnology/\(.*\):latest?ocadotechnology/\1:test?" {} \;
find -name "*.yaml" -exec sed -i "s?ocadotechnology/\(.*\):latest?ocadotechnology/\1:test?" {} \;

# Start cluster
if [ "$(./test-bin/minikube status)" != "Running" ]; then
    ./test-bin/minikube start
fi

# Add to Docker
eval $(./test-bin/minikube docker-env)
export DOCKER_API_VERSION=$(docker version --format '{{.Server.APIVersion}}')
docker build aimmo-game -t ocadotechnology/aimmo-game:test
docker build aimmo-game-creator -t ocadotechnology/aimmo-game-creator:test
docker build aimmo-game-worker -t ocadotechnology/aimmo-game-worker:test

# Nuke then restart
./test-bin/kubectl delete rc --all
./test-bin/kubectl delete pods --all
./test-bin/kubectl create -f aimmo-game-creator/rc-aimmo-game-creator.yaml

# Restore files
find -name "*.py" -exec sed -i "s?ocadotechnology/\(.*\):test?ocadotechnology/\1:latest?" {} \;
find -name "*.yaml" -exec sed -i "s?ocadotechnology/\(.*\):test?ocadotechnology/\1:latest?" {} \;
