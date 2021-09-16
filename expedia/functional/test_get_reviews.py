import sys, os
import requests

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper 
helper = helper.Helper("expedia")

def test_functional_get_reviews():
    response = requests.get("{}/review/hotels/hotel1".format(helper.get_service_url('api-gateway'), timeout=helper.get_timeout('api-gateway')))
    if not helper.fault_injected():
        assert response.status_code == 200
        assert response.json() == ML_RESPONSE
    else:
        # ML service unavailable, trigger fallback.
        if response.status_code == 200:
            assert response.json() == TIME_RESPONSE
        # Hotel is not valid (404 at either ML or time service.)
        elif response.status_code == 404:
            assert True
        # Reviews are unavailable (both services failed.)
        elif response.status_code == 503:
            assert True
        # We aren't expecting this behavior, so fail.
        else:
            assert False

ML_RESPONSE = {
    "reviews": [
        {
            "review": "Best hotel ever!",
            "rating": 10,
            "timestamp": "2018-07-21"
        },
        {
            "review": "The rooms are quite clean.",
            "rating": 8,
            "timestamp": "2019-03-01"
        },
        {
            "review": "Very nice service.",
            "rating": 9,
            "timestamp": "2017-05-09"
        }
    ]
}

TIME_RESPONSE = {
    "reviews": [
        {
            "review": "The rooms are quite clean.",
            "rating": 8,
            "timestamp": "2019-03-01"
        },
        {
            "review": "Best hotel ever!",
            "rating": 10,
            "timestamp": "2018-07-21"
        },
        {
            "review": "Very nice service.",
            "rating": 9,
            "timestamp": "2017-05-09"
        }
    ]
}

if __name__ == "__main__":
    test_functional_get_reviews()