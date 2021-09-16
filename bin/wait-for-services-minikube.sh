#!/bin/bash

echo "Waiting for minikube services."

services=$1

TIMEOUT=15

check_service () {
    service=${1//_/-}
    echo $service
    URL=`minikube service ${service} --url`
    curl $URL/health-check
}

check_services () {
    for service in ${services}; do
        check_service "${service}" || return 1;
    done
}

until check_services; do
    if [ ${TIMEOUT} -eq 0 ];then
      echo $" Max attempts reached, aborting."
      exit 1
    fi

    echo "Waiting."
    TIMEOUT=$(($TIMEOUT-1))
    sleep 10
done

echo "Services ready at minikube."