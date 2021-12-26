import logging
import os
import time

import requests

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.getLevelName(LOG_LEVEL),
    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

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


def get_hosts_separator():
    return os.environ.get("HOSTS_SEPARATOR", ",")


def get_hosts():
    return os.environ.get("HOSTS").split(get_hosts_separator())


def get_webhook_ok_url():
    return os.environ.get("WEBHOOK_OK_URL")


def get_webhook_fail_url():
    return os.environ.get("WEBHOOK_FAIL_URL")


def ping_webhook_url(url: str):
    if url:
        log.debug(f"calling webhook url: {url}")
        requests.get(url, timeout=5)
    else:
        log.debug("not calling webhook because URL is not set")


def on_success():
    log.info(f"set nest status to: {NEW_STATUS} ({r.status_code})")

    ping_webhook_url(get_webhook_ok_url())


def on_failure():
    log.info(f"failed to set nest status: '{r.text}' ({r.status_code})")

    ping_webhook_url(get_webhook_fail_url())


if __name__ == '__main__':
    HOSTS = get_hosts()
    log.info(f"found hosts: {HOSTS}")

    while True:
        NEW_STATUS = None
        for host in HOSTS:
            try:
                requests.get(f"http://{host}", timeout=5)
            except requests.exceptions.ConnectionError as e:
                if 'Connection refused' in str(e):
                    log.info(f"{host} is home")
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

            if r.status_code == 200:
                CURRENT_STATUS = NEW_STATUS
                on_success()
            else:
                on_failure()

        if CURRENT_STATUS == STATUS_HOME:
            sleep_delay = 300  # check less often when home
        else:
            sleep_delay = 15  # check more often when not home

        time.sleep(sleep_delay)
