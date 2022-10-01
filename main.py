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

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'


def get_nest_access_token():
    return os.environ.get("NEST_ACCESS_TOKEN")


def get_google_refresh_token():
    return os.environ.get("GOOGLE_REFRESH_TOKEN")


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


def get_jwt_from_google_refresh_token():
    # get access token from google refresh token
    r_google_token = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'refresh_token': get_google_refresh_token(),
            'client_id': '733249279899-1gpkq9duqmdp55a7e5lft1pr2smumdla.apps.googleusercontent.com',  # Client ID of the Nest iOS application
            'grant_type': 'refresh_token',
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': USER_AGENT,
        })

    if r_google_token.status_code != 200:
        raise ValueError(f"failed to get google access token: {r_google_token.text}")

    google_access_token = r_google_token.json()['access_token']

    # get nest jwt from google access token
    r_nest_jwt = requests.post(
        'https://nestauthproxyservice-pa.googleapis.com/v1/issue_jwt',
        json={
            'embed_google_oauth_access_token': True,
            'expire_after': '3600s',
            'google_oauth_access_token': google_access_token,
            'policy_id': 'authproxy-oauth-policy'
        },
        headers={
            'Authorization': 'Bearer ' + google_access_token,
            'User-Agent': USER_AGENT,
            'Referer': 'https://home.nest.com',
        }
    )

    if r_nest_jwt.status_code != 200:
        raise ValueError(f"failed to get nest jwt: {r_nest_jwt.text}")

    return r_nest_jwt.json()['jwt']


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
            if get_nest_access_token():
                log.debug("using nest account access method")
                auth = get_nest_access_token()
            else:
                log.debug("using google account access method")
                auth = get_jwt_from_google_refresh_token()

            r = requests.patch(f"{get_nest_rest_endpoint()}/users/{get_nest_user()}/structures/{get_nest_structure()}", json={
                'mode': NEW_STATUS
            }, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth}'
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
