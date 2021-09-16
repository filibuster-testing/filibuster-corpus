#!/bin/bash

echo "Start k8s."
services=$1
aws_account_id=$2
region=$3

for i in $(find . -name *.yaml); do
    export AWS_ACCOUNT_ID=$aws_account_id && export REGION=$region && cat "$i" | envsubst | kubectl apply -f -
done
if [[ $services == *"jaeger"* ]]; then
  kubectl apply $(find ../jaeger-k8s -name *.yaml | awk ' { print " -f " $1 } ')
fi
kubectl get pods

TIMEOUT=10

numServices=$(wc -w <<< ${services})
expected=$(( $numServices + 1 ))

# Wait for all pods.

while [ $(kubectl get pods --field-selector=status.phase=Running | wc -l) != $expected ]; do 
    if [ ${TIMEOUT} -eq 0 ];then
      echo $" Max attempts reached, aborting."
      exit 1
    fi
   kubectl get pods
   echo $(kubectl get pods --field-selector=status.phase=Running | wc -l)
   echo "Waiting for pods to be running."
   sleep 60
   TIMEOUT=$(($TIMEOUT-1))
done

echo "Finished starting k8s."