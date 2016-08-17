#!/usr/bin/env bash
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

ip_array=( $(hostname -I) )
players_url=${ip_array[0]}:8000

# Use local images
find -name "*.py" -exec sed -i "s?ocadotechnology/\(.*\):latest?ocadotechnology/\1:test?" {} \;
find -name "*.yaml" -exec sed -i "s?ocadotechnology/\(.*\):latest?ocadotechnology/\1:test?" {} \;
sed -i "s?https://staging-dot-decent-digit-629.appspot.com/aimmo?http://${players_url}/players?" aimmo-game-creator/rc-aimmo-game-creator.yaml 
find -name "*.py" -exec sed -i "s?https://staging-dot-decent-digit-629.appspot.com/aimmo?http://${players_url}/players?" {} \;

# Start cluster
if [ "$(./test-bin/minikube status)" != "Running" ]; then
    ./test-bin/minikube start --memory=2048 --cpus=2
fi

# Add to Docker
eval $(./test-bin/minikube docker-env)
export DOCKER_API_VERSION=1.20
export DOCKER_API_VERSION=$(docker version --format '{{.Server.APIVersion}}')
docker build aimmo-game -t ocadotechnology/aimmo-game:test
docker build aimmo-game-creator -t ocadotechnology/aimmo-game-creator:test
docker build aimmo-game-worker -t ocadotechnology/aimmo-game-worker:test

# Nuke then restart
./test-bin/kubectl delete rc --all
./test-bin/kubectl delete pods --all
./test-bin/kubectl delete services --all
set +e # Command fails if secret already exists (eg previous run)
./test-bin/kubectl create secret generic creator --from-literal=auth=insecure-creator-auth-token

# Wait for kubernetes service
./test-bin/kubectl get service kubernetes
while [ $? != 0 ]; do
    echo "Waiting for kubernetes service"
    sleep 1s
    ./test-bin/kubectl get service kubernetes
done
set -e

# Start aimmo
./test-bin/kubectl create -f aimmo-game-creator/rc-aimmo-game-creator.yaml

# Restore files
find -name "*.py" -exec sed -i "s?ocadotechnology/\(.*\):test?ocadotechnology/\1:latest?" {} \;
find -name "*.yaml" -exec sed -i "s?ocadotechnology/\(.*\):test?ocadotechnology/\1:latest?" {} \;
sed -i "s?http://${players_url}/players?https://staging-dot-decent-digit-629.appspot.com/aimmo?" aimmo-game-creator/rc-aimmo-game-creator.yaml
find -name "*.py" -exec sed -i "s?http://${players_url}/players?https://staging-dot-decent-digit-629.appspot.com/aimmo?" {} \;

# Run django
./example_project/manage.py migrate --noinput
./example_project/manage.py collectstatic --noinput
./example_project/manage.py runserver 0.0.0.0:8000
