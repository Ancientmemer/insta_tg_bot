import json, os, time, random
from config import *

REPLIED = "data/replied_users.json"
MSG_FILE = "data/autoreply.txt"

def load_replied():
    if not os.path.exists(REPLIED):
        return {}
    return json.load(open(REPLIED))

def save_replied(data):
    json.dump(data, open(REPLIED, "w"), indent=2)

def get_reply():
    if not os.path.exists(MSG_FILE):
        return None
    return open(MSG_FILE).read().strip()

def should_reply(user_id):
    replied = load_replied()
    return str(user_id) not in replied

def mark_replied(user_id):
    replied = load_replied()
    replied[str(user_id)] = int(time.time())
    save_replied(replied)

def human_delay():
    time.sleep(random.randint(AUTOREPLY_DELAY_MIN, AUTOREPLY_DELAY_MAX))
