import os
import json
import subprocess
import ast

class Helper:
    def __init__(self, example):
        self.example_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), example)
        with open("{}/networking.json".format(self.example_path), "r") as f:
            self.networking = json.load(f)
        self.instrumentation_info = None

    def get_debug(self):
        # Debug has to be false to prevent multiprocess problem that inhibits coverage metrics.
        return False

    def resolve_with_docker_host(self, service_name):
        return os.environ.get('RUNNING_IN_DOCKER', '')

    def get_service_url(self, service_name):
        if os.environ.get('USE_MINIKUBE_NETWORKING', ''):
            cmd = 'minikube service {} --url'.format(service_name)
            out = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                stdout,stderr = out.communicate(timeout=10)
            except subprocess.TimeoutExpired as e:
                print(e)
                raise Exception('Minikube unresponsive, try running command \'{}\' to debug.'.format(cmd))
            return stdout.decode('ascii').rstrip()
        elif os.environ.get('USE_EKS_NETWORKING', ''):
            cmd = 'kubectl get service/{} -o json'.format(service_name)
            out = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                stdout,stderr = out.communicate(timeout=10)
            except subprocess.TimeoutExpired as e:
                print(e)
                raise Exception('k8s unresponsive, try running command \'{}\' to debug.'.format(cmd))
            info = json.loads(stdout)
            host_name = info['status']['loadBalancer']['ingress'][0]['hostname']
            return "http://{}:{}".format(host_name, self.get_port(service_name))
        else:
            host_name = self.resolve_requests_host(service_name)
            if os.environ.get('K8S_FAULT_INJECTION', ''):
                host_name = host_name.replace("_", "-")
            return "http://{}:{}".format(host_name, self.get_port(service_name))

    def resolve_requests_host(self, service_name):
        if (service_name == 'jaeger'):
            return self.jaeger_agent_host_name()
        if self.resolve_with_docker_host(service_name):
            return self.networking[service_name]['docker-host']
        return self.networking[service_name]['default-host']

    def get_port(self, service_name):
        if (service_name == 'jaeger'):
            return 16686
        return self.networking[service_name]['port']

    def get_grpc_port(self, service_name):
        return self.networking[service_name]['grpc-port']

    def get_timeout(self, service_name):
        if (service_name == 'jaeger'):
            return 5
        return self.networking[service_name]['timeout-seconds']

    def jaeger_agent_host_name(self):
        if self.resolve_with_docker_host('jaeger'):
            return "jaeger"
        return "localhost"

    def jaeger_agent_port(self):
        return 6831

    def instrumentation(self):
        if self.instrumentation_info == None:
            with open("{}/instrumentation.json".format(self.example_path), "r") as f:
                self.instrumentation_info = json.load(f)
        return self.instrumentation_info