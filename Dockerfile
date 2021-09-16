ARG example
ARG disable_instrumentation
ARG disable_server_communication
ARG run_counterexample

FROM public.ecr.aws/u9z3w9o0/ubuntu:latest as configuration 

ARG example
ARG disable_instrumentation
ARG disable_server_communication
ARG run_counterexample

RUN apt -y update && \
    apt -y upgrade && \
    apt install -y python3-pip && \
    apt install -y build-essential libssl-dev libffi-dev python3-dev

COPY ./helper.py application/examples/helper.py
COPY ./jaeger-k8s application/examples/jaeger-k8s
COPY ./${example}/networking.json application/examples/${example}/networking.json
COPY ./${example}/instrumentation.json application/examples/${example}/instrumentation.json
COPY ./${example}/functional application/examples/${example}/functional
COPY ./${example}/services application/examples/${example}/services

COPY ./${example}/base_requirements.txt ./base_requirements.txt
RUN pip3 install -r base_requirements.txt

ENV RUNNING_IN_DOCKER=1 
ENV DISABLE_INSTRUMENTATION=${disable_instrumentation}
ENV DISABLE_SERVER_COMMUNICATION=${disable_server_communication}
ENV RUN_COUNTEREXAMPLE=${run_counterexample}