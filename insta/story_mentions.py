import time, random, json, os
from instagrapi.exceptions import FeedbackRequired, ChallengeRequired
from insta.client import cl
from insta.mentions import load_mentions
from config import *

PROCESSED = "data/processed_stories.json"

def load_processed():
    if not os.path.exists(PROCESSED):
        return {}
    return json.load(open(PROCESSED))

def save_processed(data):
    json.dump(data, open(PROCESSED, "w"), indent=2)

def get_latest_story():
    stories = cl.user_stories(cl.user_id)
    if not stories:
        return None
    stories.sort(key=lambda s: s.taken_at, reverse=True)
    return stories[0]

def mention_users_on_story():
    story = get_latest_story()
    if not story:
        return "❌ No active story found."

    processed = load_processed()
    sid = str(story.pk)

    if sid in processed:
        return "⚠️ This story already processed."

    usernames = load_mentions()
    if not usernames:
        return "❌ Mention list empty."

    count = 0

    for username in usernames:
        if count >= MAX_MENTIONS_PER_RUN:
            break

        try:
            user = cl.user_info_by_username(username)
            time.sleep(random.randint(MENTION_DELAY_MIN, MENTION_DELAY_MAX))

            cl.story_mention(
                story.pk,
                user.pk,
                x=0.5,
                y=0.5
            )

            count += 1

        except (FeedbackRequired, ChallengeRequired):
            return "🚨 Instagram warning detected. Stopped."
        except Exception:
            continue

    processed[sid] = int(time.time())
    save_processed(processed)

    return f"✅ Mentions completed: {count}"
