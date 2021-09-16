import os
import sys
import requests

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper 
helper = helper.Helper("audible")

def only_stats_failure():
    return (helper.fault_injected_on_flask_service('stats') and
        not helper.fault_injected_on_flask_service('asset-metadata') and
        not helper.fault_injected_on_flask_service('audio-assets'))

def test_functional_get_audiobook():    
    response = requests.get("{}/users/user1/books/book2".format(helper.get_service_url("audible-app")), timeout=helper.get_timeout("audible-app"))
    # If only the stats service (non-critical) failed, 200 response OK.
    if not helper.fault_injected() or only_stats_failure():
        assert response.status_code == 200
        assert response.content == RESPONSE_SUCCESS
    else:
        # Any of the required services are unavailable.
        if response.status_code == 503:
            assert True
        # Error when book is not found.
        elif response.status_code == 404:
            assert True
        # Either license missing or book not owned by user.
        elif response.status_code == 403:
            assert True
        else:
            print("status_code: " + str(response.status_code))
            assert False

RESPONSE_SUCCESS = b"This is book 2."

if __name__ == "__main__":
    test_functional_get_audiobook()