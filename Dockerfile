ARG example
ARG disable_instrumentation
ARG disable_server_communication
ARG run_counterexample

FROM ubuntu:latest as configuration 

ARG example
ARG disable_instrumentation
ARG disable_server_communication
ARG run_counterexample

RUN apt -y update && \
    apt -y upgrade && \
    apt install -y python3-pip && \
    apt install -y build-essential libssl-dev libffi-dev python3-dev && \
    apt install -y git

COPY ./helper.py application/examples/helper.py
COPY ./${example}/networking.json application/examples/${example}/networking.json
COPY ./${example}/functional application/examples/${example}/functional
COPY ./${example}/services application/examples/${example}/services
COPY ./${example}/base_requirements.txt ./base_requirements.txt

RUN cd /tmp && \
    git clone https://github.com/filibuster-testing/filibuster.git && \
    cd filibuster && \
    make install

RUN pip3 install -r base_requirements.txt

# ENV RUNNING_IN_DOCKER=1 
# ENV DISABLE_INSTRUMENTATION=${disable_instrumentation}
# ENV DISABLE_SERVER_COMMUNICATION=${disable_server_communication}
# ENV RUN_COUNTEREXAMPLE=${run_counterexample}