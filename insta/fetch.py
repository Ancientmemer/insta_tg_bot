import json, time, random, os
from insta.client import get_client

FOLLOWERS_FILE = "data/followers.json"
FOLLOWING_FILE = "data/following.json"

def human_sleep():
    time.sleep(random.randint(5, 12))

def fetch_followers():
    cl = get_client()
    users = cl.user_followers(cl.user_id, amount=300)
    result = []

    for i, u in enumerate(users.values(), start=1):
        result.append(u.username)
        if i % 50 == 0:
            human_sleep()

    json.dump(result, open(FOLLOWERS_FILE, "w"), indent=2)
    return len(result)

def fetch_following():
    cl = get_client()
    users = cl.user_following(cl.user_id, amount=300)
    result = []

    for i, u in enumerate(users.values(), start=1):
        result.append(u.username)
        if i % 50 == 0:
            human_sleep()

    json.dump(result, open(FOLLOWING_FILE, "w"), indent=2)
    return len(result)

def compare_unfollowers():
    if not os.path.exists(FOLLOWERS_FILE) or not os.path.exists(FOLLOWING_FILE):
        raise Exception("Followers / Following data missing")

    followers = set(json.load(open(FOLLOWERS_FILE)))
    following = set(json.load(open(FOLLOWING_FILE)))

    return sorted(list(following - followers))
