from instagrapi import Client
import os

SESSION_FILE = "data/session.json"
cl = Client()

def reset_client():
    global cl
    cl = Client()

def login(username, password):
    reset_client()
    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)

def load_session():
    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        cl.login_by_sessionid(cl.sessionid)
        return True
    return False

def logout():
    try:
        cl.logout()
    except:
        pass
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    reset_client()

def current_username():
    try:
        return cl.account_info().username
    except:
        return None

def get_client():
    return cl
