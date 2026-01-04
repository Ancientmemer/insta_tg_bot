import json, os, time, random
from config import *

FILE = "data/mentions.json"

def load_mentions():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))

def save_mentions(data):
    json.dump(data, open(FILE, "w"), indent=2)

def add_mention(username):
    data = load_mentions()
    if username not in data:
        data.append(username)
        save_mentions(data)

def remove_mention(username):
    data = load_mentions()
    if username in data:
        data.remove(username)
        save_mentions(data)

def human_delay():
    time.sleep(random.randint(MENTION_DELAY_MIN, MENTION_DELAY_MAX))
