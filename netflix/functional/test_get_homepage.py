import os
import sys
import requests

from filibuster.assertions import was_fault_injected

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper 
helper = helper.Helper("netflix")

def test_functional_get_homepage():
    response = requests.get("{}/netflix/homepage/users/chris_rivers".format(helper.get_service_url("mobile-client")), timeout=helper.get_timeout("mobile-client"))
    if not was_fault_injected():
        assert response.status_code == 200
        homepage = response.json()
        assert homepage["user-profile"] == USER_PROFILE
        assert homepage["bookmarks"] == BOOKMARKS
        assert homepage["my-list"] == MY_LIST
        assert homepage["recommendations"] == USER_REC
        assert homepage["ratings"] == RATINGS
    else:
        # 503, API gateway down, unavailable, or server error.
        if response.status_code == 503:
            assert True
        # 404, invalid user.
        elif response.status_code == 404:
            assert True
        # 
        elif response.status_code == 200:
            homepage = response.json()
            
            if homepage["my-list"] == MY_LIST and \
                    homepage["ratings"] == RATINGS and \
                    homepage.get("recommendations", None) in [USER_REC] and \
                    homepage.get("trending") in [TRENDING] and \
                    homepage["user-profile"] == USER_PROFILE:
                assert True
            elif homepage["my-list"] == MY_LIST and \
                    homepage["ratings"] == RATINGS and \
                    homepage.get("recommendations", None) in [GLOBAL_REC] and \
                    homepage.get("bookmarks", None) in [BOOKMARKS] and \
                    homepage["user-profile"] == USER_PROFILE:
                assert True
            elif homepage["my-list"] == MY_LIST and \
                    homepage["ratings"] == RATINGS and \
                    homepage.get("recommendations", None) in [GLOBAL_REC] and \
                    homepage["trending"] == TRENDING and \
                    homepage["user-profile"] == USER_PROFILE:
                assert True
            elif homepage["my-list"] == MY_LIST and \
                    homepage["ratings"] == RATINGS and \
                    homepage.get("bookmarks", None) in [BOOKMARKS] and \
                    homepage.get("trending", None) in [TRENDING] and \
                    homepage["user-profile"] == USER_PROFILE:
                assert True
            elif homepage["my-list"] == MY_LIST and \
                    homepage["ratings"] == RATINGS and \
                    homepage.get("trending", None) in [TRENDING] and \
                    homepage["user-profile"] == USER_PROFILE:
                assert True
            elif homepage["user-profile"] == USER_PROFILE and \
                    homepage["bookmarks"] == BOOKMARKS and \
                    homepage["my-list"] == MY_LIST and \
                    homepage["recommendations"] == USER_REC and \
                    homepage["ratings"] == RATINGS:
                assert True
            else:
                assert False
        else:
            assert False

USER_PROFILE = {
    "id": "chris_rivers",
          "name": "Chris Rivers",
          "email": "chris_rivers@netflix.com"
}

BOOKMARKS = [{'movie': "Harry Potter and the Philosopher's Stone", 'timecode': '01:20:00'}, {'movie': 'Harry Potter and the Chamber of Secrets', 'timecode': '00:01:20'}]

TRENDING = ['The Croods', 'Red Dot', 'We Can Be Heroes']

MY_LIST = ['Harry Potter and the Prisoner of Azkaban', 'Harry Potter and the Goblet of Fire']

USER_REC = ['Harry Potter and the Order of the Phoenix', 'Harry Potter and the Half-Blood Prince', 'Harry Potter and the Deathly Hallows']

GLOBAL_REC = ['Inception', 'Shutter Island', 'The Dark Night']

RATINGS = [{'movie': "Harry Potter and the Philosopher's Stone", 'rating': 5}, {'movie': 'Twilight', 'rating': 4}]

if __name__ == "__main__":
    test_functional_get_homepage()
