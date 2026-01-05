import os, json, asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters

from config import *
from insta.client import (
    login, logout, load_session,
    current_username, get_client
)
from insta.fetch import (
    fetch_followers,
    fetch_following,
    compare_unfollowers
)
from insta.mention_assistant import (
    load_mentions,
    load_state,
    save_state,
    detect_latest_story,
    random_delay
)

STATE_FILE = "data/state.json"
EXPORT_FILE = "exports/unfollowers.txt"

app = Client(
    "insta_full_safe_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- UTILS ----------------
def owner_only(func):
    async def wrapper(c, m):
        if m.from_user.id != OWNER_ID:
            return
        return await func(c, m)
    return wrapper

def now():
    return datetime.utcnow()

def load_global_state():
    if not os.path.exists(STATE_FILE):
        return {
            "account": None,
            "followers_time": None,
            "following_time": None,
            "mode": None  # data / mention
        }
    return json.load(open(STATE_FILE))

def save_global_state(s):
    json.dump(s, open(STATE_FILE, "w"), indent=2)

# ---------------- LOGIN ----------------
@app.on_message(filters.command("login") & filters.private)
@owner_only
async def _login(_, m):
    _, u, p = m.text.split(maxsplit=2)
    login(u, p)
    save_global_state({
        "account": u,
        "followers_time": None,
        "following_time": None,
        "mode": None
    })
    await m.reply(f"✅ Logged in as @{u}")

# ---------------- STATUS ----------------
@app.on_message(filters.command("status") & filters.private)
@owner_only
async def _status(_, m):
    u = current_username()
    if not u:
        return await m.reply("❌ Not logged in")
    await m.reply(f"🟢 Logged in as @{u}")

# ---------------- FOLLOWERS ----------------
@app.on_message(filters.command("followers") & filters.private)
@owner_only
async def _followers(_, m):
    if not load_session():
        return await m.reply("❌ Login first")

    s = load_global_state()
    if s["mode"] == "mention":
        return await m.reply("⚠️ Mention assistant running. Stop it first.")

    if s["followers_time"]:
        last = datetime.fromisoformat(s["followers_time"])
        if now() - last < timedelta(hours=24):
            return await m.reply("⏳ Followers already fetched today")

    s["mode"] = "data"
    save_global_state(s)

    count = fetch_followers()
    s["followers_time"] = now().isoformat()
    save_global_state(s)

    await m.reply(
        f"✅ Followers fetched: {count}\n"
        "⏳ Run /following after 15 minutes"
    )

# ---------------- FOLLOWING ----------------
@app.on_message(filters.command("following") & filters.private)
@owner_only
async def _following(_, m):
    if not load_session():
        return await m.reply("❌ Login first")

    s = load_global_state()
    if not s["followers_time"]:
        return await m.reply("❌ Run /followers first")

    last = datetime.fromisoformat(s["followers_time"])
    if now() - last < timedelta(minutes=15):
        return await m.reply("⏳ Wait 15 minutes after /followers")

    if s["following_time"]:
        lf = datetime.fromisoformat(s["following_time"])
        if now() - lf < timedelta(hours=24):
            return await m.reply("⏳ Following already fetched today")

    count = fetch_following()
    s["following_time"] = now().isoformat()
    save_global_state(s)

    await m.reply(
        f"✅ Following fetched: {count}\n"
        "📂 You can now use /unfollowers"
    )

# ---------------- UNFOLLOWERS (LOCAL) ----------------
@app.on_message(filters.command("unfollowers") & filters.private)
@owner_only
async def _unfollowers(_, m):
    try:
        users = compare_unfollowers()
        os.makedirs("exports", exist_ok=True)
        with open(EXPORT_FILE, "w") as f:
            for u in users:
                f.write(u + "\n")
        await m.reply_document(EXPORT_FILE)
    except Exception as e:
        await m.reply(f"⚠️ {e}")

# ---------------- ADD MENTION ----------------
@app.on_message(filters.command("addmention") & filters.private)
@owner_only
async def _addmention(_, m):
    _, u = m.text.split(maxsplit=1)
    path = "data/mentions.json"
    data = json.load(open(path))
    if u not in data["users"]:
        data["users"].append(u)
    json.dump(data, open(path, "w"), indent=2)
    await m.reply(f"✅ Added @{u}")

# ---------------- REMOVE MENTION ----------------
@app.on_message(filters.command("rmmention") & filters.private)
@owner_only
async def _rmmention(_, m):
    _, u = m.text.split(maxsplit=1)
    path = "data/mentions.json"
    data = json.load(open(path))
    if u not in data["users"]:
        return await m.reply("⚠️ Not in list")
    data["users"].remove(u)
    json.dump(data, open(path, "w"), indent=2)
    await m.reply(f"❌ Removed @{u}")

# ---------------- LIST MENTIONS ----------------
@app.on_message(filters.command("mentions") & filters.private)
@owner_only
async def _mentions(_, m):
    users = load_mentions()
    if not users:
        return await m.reply("📭 Mention list empty")
    txt = "📌 Mention list:\n\n"
    for u in users:
        txt += f"• @{u}\n"
    await m.reply(txt)

# ---------------- START MENTION ASSISTANT ----------------
@app.on_message(filters.command("mentionstart") & filters.private)
@owner_only
async def _mentionstart(_, m):
    if not load_session():
        return await m.reply("❌ Login first")

    s = load_global_state()
    if s["mode"] == "data":
        return await m.reply("⚠️ Data fetch mode active. Wait.")

    state = load_state()
    if state["running"]:
        return await m.reply("⚠️ Assistant already running")

    s["mode"] = "mention"
    save_global_state(s)

    state["running"] = True
    save_state(state)

    cl = get_client()
    await m.reply("👀 Waiting for new story (checking every 2 minutes)...")

    while True:
        await asyncio.sleep(120)
        state = load_state()
        if not state["running"]:
            break

        sid = detect_latest_story(cl)
        if sid and sid != state["last_story_id"]:
            state["last_story_id"] = sid
            save_state(state)

            users = load_mentions()
            await m.reply("📸 New story detected!")

            for u in users:
                d = random_delay()
                await asyncio.sleep(d)
                await m.reply(f"👉 Mention @{u} (waited {d}s)")

            await m.reply("✅ Mention assistant finished")
            state["running"] = False
            save_state(state)

            s["mode"] = None
            save_global_state(s)
            break

# ---------------- STOP MENTION ASSISTANT ----------------
@app.on_message(filters.command("mentionstop") & filters.private)
@owner_only
async def _mentionstop(_, m):
    state = load_state()
    state["running"] = False
    save_state(state)

    s = load_global_state()
    s["mode"] = None
    save_global_state(s)

    await m.reply("🛑 Mention assistant stopped")

# ---------------- LOGOUT ----------------
@app.on_message(filters.command("logout") & filters.private)
@owner_only
async def _logout(_, m):
    logout()
    await m.reply("✅ Logged out safely")

print("🤖 Full Safe Insta Bot running...")
app.run()
