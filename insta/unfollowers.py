import os
import json
import time
import random
from datetime import datetime, timedelta

from insta.client import cl, load_session

DATA_DIR = "data"
BASELINE_FILE = os.path.join(DATA_DIR, "followers_baseline.json")

# =========================
# SAFETY CONFIG
# =========================
MAX_PAGES = 4              # max pages per fetch
PAGE_SIZE = 80             # users per page
PAGE_DELAY = (6, 12)       # seconds between pages
FOLLOWERS_FOLLOWING_GAP = (120, 240)  # 2–4 min gap
MIN_HOURS_BETWEEN_CHECKS = 12


# =========================
# UTILS
# =========================
def _sleep_range(rng):
    time.sleep(random.randint(rng[0], rng[1]))


def _now():
    return datetime.utcnow()


def _load_baseline():
    if not os.path.exists(BASELINE_FILE):
        return None
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)


def _save_baseline(followers_set):
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "last_checked": _now().isoformat(),
        "followers": sorted(list(followers_set))
    }
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _too_soon(last_checked):
    last = datetime.fromisoformat(last_checked)
    return _now() - last < timedelta(hours=MIN_HOURS_BETWEEN_CHECKS)


# =========================
# SAFE FETCHERS
# =========================
def _safe_fetch_followers(user_id):
    followers = set()
    pages = 0

    for user, _ in cl.user_followers_v1_chunked(
        user_id,
        amount=PAGE_SIZE
    ):
        followers.add(user.username)

        if len(followers) % PAGE_SIZE == 0:
            pages += 1
            if pages >= MAX_PAGES:
                break
            _sleep_range(PAGE_DELAY)

    return followers


def _safe_fetch_following(user_id):
    following = set()
    pages = 0

    _sleep_range(FOLLOWERS_FOLLOWING_GAP)

    for user, _ in cl.user_following_v1_chunked(
        user_id,
        amount=PAGE_SIZE
    ):
        following.add(user.username)

        if len(following) % PAGE_SIZE == 0:
            pages += 1
            if pages >= MAX_PAGES:
                break
            _sleep_range(PAGE_DELAY)

    return following


# =========================
# PUBLIC API
# =========================
def init_unfollowers_baseline():
    if not load_session():
        raise Exception("Not logged in")

    followers = _safe_fetch_followers(cl.user_id)
    _save_baseline(followers)

    return len(followers)


def get_unfollowers_safe():
    if not load_session():
        raise Exception("Not logged in")

    baseline = _load_baseline()
    if not baseline:
        raise Exception("Baseline not found. Run /unfollowers init first")

    if _too_soon(baseline["last_checked"]):
        raise Exception("Checked recently. Please wait before next check")

    old_followers = set(baseline["followers"])

    current_followers = _safe_fetch_followers(cl.user_id)
    current_following = _safe_fetch_following(cl.user_id)

    unfollowers = sorted(list(current_following - current_followers))

    # update baseline slowly (followers only)
    _save_baseline(current_followers)

    return unfollowers
