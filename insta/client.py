from instagrapi import Client
import os, json

SESSION_FILE = "data/session.json"

cl = Client()

def is_logged_in():
    return os.path.exists(SESSION_FILE)

def login(username, password):
    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)

def load_session():
    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        cl.login_by_sessionid(cl.sessionid)
        return True
    return False

def logout():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
