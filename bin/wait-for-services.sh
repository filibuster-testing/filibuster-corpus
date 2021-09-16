#!/bin/bash

echo "Waiting for services at localhost."

TIMEOUT=6

ports=$1

check_service () {
    echo "Curling for http://0.0.0.0:${1}/health-check"
    curl --fail http://0.0.0.0:${1}/health-check
}

check_services () {
    for port in ${ports}; do
        check_service "${port}" || return 1;
    done
}

until check_services; do
    if [ ${TIMEOUT} -eq 0 ];then
      echo $" Max attempts reached, aborting."
      exit 1
    fi

    kubectl get svc
    ps -f | grep 'kubectl' | grep 'port-forward'
    echo "Waiting."
    TIMEOUT=$(($TIMEOUT-1))
    sleep 10
done

echo "Services ready at localhost."