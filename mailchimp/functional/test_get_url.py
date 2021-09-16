import os
import sys
import requests

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)
import helper

helper = helper.Helper("mailchimp")


def test_functional_get_url():
    response = requests.get("http://{}:{}/urls/prettyurl".format(helper.resolve_requests_host(
        'load-balancer'), helper.get_port('load-balancer')), timeout=helper.get_timeout('load-balancer'))
    if not helper.fault_injected():
        assert response.status_code == 200
        assert response.json() == {"result": "internalurl"}
    else:
        # Incorrect failure handling by the app-server.
        if response.status_code == 503:
            assert True
        # Fallback triggered.
        elif response.status_code == 200:
            response_json = response.json()

            # If the failure was a Read-Only failure by the database, there will be an error in the output.
            #
            # This is here for documentation purposes, since the assertion will never fail if the key
            # is present, but makes it clear to the reader one possible outcome.
            #
            if 'alert' in response_json:
                assert response_json['alert'] == 'cannot write to DB'

            # If we were able to hit the secondary because of a failure in the primary, we'll still get
            # the correct response.  If not, it will return the original URL.
            #
            assert response_json['result'] in ['internalurl', 'prettyurl']
        else:
            assert False


if __name__ == '__main__':
    test_functional_get_url()
