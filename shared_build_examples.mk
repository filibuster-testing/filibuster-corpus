ifndef GITHUB_WORKFLOW
	PYTHON=python
else
	PYTHON=python3
endif

## Reqs

jaeger_port=16686

define reqs-target
  reqs:: ; cd services/$1 && make reqs
endef

$(foreach service,$(services),$(eval $(call reqs-target,$(service))))

## Unit tests

define unit-target
  unit:: ; cd services/$1 && make test
endef

$(foreach service,$(services),$(eval $(call unit-target,$(service))))

## Jaeger

jaeger-start: jaeger-stop
	docker run --name jaeger -d -p 6831:6831/udp -p $(jaeger_port):$(jaeger_port) public.ecr.aws/u9z3w9o0/jaeger:latest

jaeger-stop:
	((docker stop jaeger && docker rm jaeger) || exit 0)

## Functional tests

FUNCTIONAL = functional
functional: $(FUNCTIONAL)/test_*.py
	for file in $^ ; do \
		echo "Found functional test" $${file} ; \
		python3 $${file} ; \
		done

## Docker

define docker-target
  docker:: ; cd services/$1 && make docker
endef
$(foreach service,$(services),$(eval $(call docker-target,$(service))))

AWS_ACCOUNT_ID=194095331551
REGION=us-east-2

docker-push:: docker-build
docker-push:: ; aws ecr describe-repositories --repository-names $(example) --query "repositories[].repositoryName" --no-paginate || aws ecr create-repository --repository-name $(example) 2>&1 > /dev/null
docker-push:: ; aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
define docker-push-target
  docker-push:: ; docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/$(example):$1
endef
$(foreach service,$(services),$(eval $(call docker-push-target,$(service))))

# ecr-public isn't region specific, have to use us-east-1 for this to work: https://github.com/aws/aws-cli/issues/5917
refresh-aws-credentials:
	if [ -z "$(CODEBUILD_BUILD_ID)" ]; then \
	  	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com; \
		aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/u9z3w9o0; \
    else \
        echo "Not refreshing credentials, running inside AWS."; \
    fi

docker-build: refresh-aws-credentials generate-protos
	docker build --build-arg example=$(example) --build-arg disable_instrumentation=$(DISABLE_INSTRUMENTATION) --build-arg disable_server_communication=$(DISABLE_SERVER_COMMUNICATION) --build-arg run_counterexample=$(RUN_COUNTEREXAMPLE) -t $(example):configuration -f ../Dockerfile ..
	AWS_ACCOUNT_ID=$(AWS_ACCOUNT_ID) REGION=$(REGION) docker-compose build
	docker pull public.ecr.aws/u9z3w9o0/jaeger:latest

docker-start:
	DISABLE_INSTRUMENTATION=$(DISABLE_INSTRUMENTATION) make docker-build
	AWS_ACCOUNT_ID=$(AWS_ACCOUNT_ID) REGION=$(REGION) docker-compose up -d

docker-stop:
	AWS_ACCOUNT_ID=$(AWS_ACCOUNT_ID) REGION=$(REGION) docker-compose stop

define docker-connect-to-network-target
  	docker-connect-to-network:: ; docker network connect exampleToJaeger cinema_$(1)_1
endef

$(foreach service,$(services),$(eval $(call docker-connect-to-network-target,$(service))))

define docker-disconnect-from-network-target
  	docker-disconnect-from-network:: ; docker network disconnect exampleToJaeger cinema_$(1)_1
endef

$(foreach service,$(services),$(eval $(call docker-disconnect-from-network-target,$(service))))

## Local

generate-protos:
	@echo "Generating protocol buffer files..."
	if [ -d "protos/" ]; then \
		mkdir -p protos/out; \
		python3 -m grpc_tools.protoc -I./protos --python_out=protos/out --grpc_python_out=protos/out ./protos/*.proto; \
		make install-protos; \
	fi

define install-protos-target
  install-protos:: ; (cp -Rpv protos/out/* services/$1/$1 || exit 0)
endef
$(foreach service,$(services),$(eval $(call install-protos-target,$(service))))

local-start:: ; find . -name ".coverage*" -exec rm -v {} \;
local-start:: ; rm -rf htmlcov
local-start:: ; make generate-protos
local-start:: ; tmux new-session -d -s application
define local-start-target
  local-start:: ; cd services/$1; make start
endef
$(foreach service,$(services),$(eval $(call local-start-target,$(service))))

define local-stop-target
  local-stop:: ; (pkill -INT -o -f coverage.*$1.app || exit 0)
endef
$(foreach service,$(services),$(eval $(call local-stop-target,$(service))))
local-stop:: ; echo "Give time for coverage to close gracefully before we nuke the entire session with SIGKILL..."
local-stop:: ; sleep 5
local-stop:: ; (tmux kill-session -t application || exit 0)
local-stop:: ; find . -name ".coverage*" -exec cp -Rpv {} . \;
local-stop:: ; coverage combine
local-stop:: ; coverage html --omit="/usr/local/lib*,*site-packages*" --include="*app.py*"

## Kubernetes

pre-minikube-start:
	make docker-push
	minikube start
	kubectl create secret generic regcred --from-file=.dockerconfigjson=$(HOME)/.docker/config.json --type=kubernetes.io/dockerconfigjson

minikube-stop:
	kubectl delete all --all --all-namespaces
	kubectl delete secret regcred --ignore-not-found
	minikube stop
	minikube delete

pre-k8s-eks: docker-push
	@echo Setting env.
	(kubectl create configmap env --from-env-file env.txt || exit 0)

	@echo Setting up env.
	(kubectl create configmap cmd-env --from-literal BYPASS_RESTART_RESTOP=$(BYPASS_RESTART_RESTOP) --from-literal RUN_COUNTEREXAMPLE=$(RUN_COUNTEREXAMPLE) --from-literal DISABLE_SERVER_COMMUNICATION=$(DISABLE_SERVER_COMMUNICATION) --from-literal DISABLE_DYNAMIC_REDUCTION=$(DISABLE_DYNAMIC_REDUCTION) --from-literal SET_ERROR_CONTENT=$(SET_ERROR_CONTENT) --from-literal DISABLE_INSTRUMENTATION=$(DISABLE_INSTRUMENTATION) || exit 0)

	@echo ***************************************************************************************************************
	@echo
	@echo This regcred only works if the credentialStore in Docker is disabled, otherwise, the config.json will contain
	@echo  no authorization tokens.  Set credentialStore to an empty string in your Docker config.json to disable.
	@echo
	@echo If you see imagePullBackOff errors, this may be the root cause.
	@echo
	@echo ***************************************************************************************************************

	(kubectl create secret generic regcred --from-file=.dockerconfigjson=$(HOME)/.docker/config.json --type=kubernetes.io/dockerconfigjson || exit 0)

post-k8s-eks:
	kubectl delete configmap env --ignore-not-found
	kubectl delete configmap cmd-env --ignore-not-found
	kubectl delete secret regcred --ignore-not-found
