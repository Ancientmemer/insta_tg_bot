import json
import random

MENTIONS_FILE = "data/mentions.json"
STATE_FILE = "data/assistant_state.json"

def load_mentions():
    with open(MENTIONS_FILE) as f:
        return json.load(f)["users"]

def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def detect_latest_story(cl):
    stories = cl.user_stories(cl.user_id)
    if not stories:
        return None
    return stories[0].id

def random_delay():
    return random.randint(7, 15)
