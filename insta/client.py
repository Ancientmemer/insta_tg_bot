from instagrapi import Client as InstaClient
import os

SESSION_FILE = "data/session.json"

cl = InstaClient()


def _reset_client():
    global cl
    cl = InstaClient()


def load_session():
    if os.path.exists(SESSION_FILE) and os.path.getsize(SESSION_FILE) > 0:
        cl.load_settings(SESSION_FILE)
        cl.login_by_sessionid(cl.sessionid)
        return True
    return False


def login(username, password):
    global cl

    # reset client before login (VERY IMPORTANT)
    _reset_client()

    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)


def logout():
    global cl

    try:
        # logout from instagram side
        cl.logout()
    except:
        pass

    # remove local session
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    # reset client completely
    _reset_client()


def is_logged_in():
    return os.path.exists(SESSION_FILE) and os.path.getsize(SESSION_FILE) > 0
