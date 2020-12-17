import os
import time

import requests

STATUS_HOME = "home"
STATUS_AWAY = "away"

CURRENT_STATUS = None
HOSTS = None


def get_nest_access_token():
    return os.environ.get("NEST_ACCESS_TOKEN")


def get_nest_structure():
    return os.environ.get("NEST_STRUCTURE")


def get_nest_user():
    return os.environ.get("NEST_USER")


def get_nest_rest_endpoint():
    return os.environ.get("NEST_REST_ENDPOINT")


def get_hosts():
    return os.environ.get("HOSTS").split(",")


if __name__ == '__main__':
    HOSTS = get_hosts()

    while True:
        NEW_STATUS = None
        for host in HOSTS:
            try:
                requests.get(f"http://{host}", timeout=5)
            except requests.exceptions.ConnectionError as e:
                if 'Connection refused' in str(e):
                    print(f"{host} is home")
                    NEW_STATUS = STATUS_HOME
                    break
                else:
                    NEW_STATUS = STATUS_AWAY

        if CURRENT_STATUS != NEW_STATUS:
            r = requests.patch(f"{get_nest_rest_endpoint()}/users/{get_nest_user()}/structures/{get_nest_structure()}", json={
                'mode': NEW_STATUS
            }, headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + get_nest_access_token()
            })

            CURRENT_STATUS = NEW_STATUS
            print(f"set status to: {NEW_STATUS} -> {r.status_code}")

        if CURRENT_STATUS == STATUS_HOME:
            time.sleep(300)  # check less often when home
        else:
            time.sleep(15)  # check more often when not home
