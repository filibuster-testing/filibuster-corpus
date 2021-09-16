import os
import sys
import requests

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)
import helper
helper = helper.Helper("mailchimp")

def test_functional_get_url_random():
    random_url = "randomurl"
    response = requests.get("http://{}:{}/urls/{}".format(helper.resolve_requests_host('load-balancer'),
            helper.get_port('load-balancer'), random_url), timeout=helper.get_timeout('load-balancer'))
    if not helper.fault_injected():
        assert response.status_code == 200
        assert response.json() == {"result": random_url}
    else:
        # Incorrect failure handling by the app-server.
        if response.status_code == 503:
            assert True
        # Fallback triggered.
        elif response.status_code == 200:
            assert response.json()["result"] == random_url
        else:
            assert False


if __name__ == '__main__':
    test_functional_get_url_random()