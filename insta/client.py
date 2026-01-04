from instagrapi import Client
import os

SESSION_FILE = "data/session.json"

cl = Client()

def load_session():
    if os.path.exists(SESSION_FILE) and os.path.getsize(SESSION_FILE) > 0:
        cl.load_settings(SESSION_FILE)
        cl.login_by_sessionid(cl.sessionid)
        return True
    return False

def login(username, password):
    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)

def logout():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
