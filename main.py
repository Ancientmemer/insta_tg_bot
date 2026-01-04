from pyrogram import Client, filters
from config import *

from insta.client import login, logout, load_session, is_logged_in, cl
from insta.unfollowers import get_unfollowers
from insta.mentions import add_mention, remove_mention
from insta.story_mentions import mention_users_on_story

import os
import time
from datetime import datetime


# =========================
# TELEGRAM BOT INIT
# =========================
app = Client(
    "insta_admin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# =========================
# OWNER ONLY DECORATOR
# =========================
def owner_only(func):
    async def wrapper(client, message):
        if message.from_user.id != OWNER_ID:
            return
        return await func(client, message)
    return wrapper


# =========================
# LOGIN COMMAND
# =========================
@app.on_message(filters.command("login") & filters.private)
@owner_only
async def login_cmd(_, msg):
    try:
        _, username, password = msg.text.split(maxsplit=2)
        login(username, password)
        await msg.reply("✅ Instagram login successful")
    except:
        await msg.reply("❌ Usage: /login username password")


# =========================
# LOGOUT COMMAND
# =========================
@app.on_message(filters.command("logout") & filters.private)
@owner_only
async def logout_cmd(_, msg):
    if not is_logged_in():
        return await msg.reply("ℹ️ Already logged out from Instagram")

    logout()
    await msg.reply("✅ Logged out successfully")


# =========================
# STATUS COMMAND
# =========================
@app.on_message(filters.command("status") & filters.private)
@owner_only
async def status_cmd(_, msg):
    if is_logged_in():
        await msg.reply("🟢 Status: Logged in to Instagram")
    else:
        await msg.reply("🔴 Status: Logged out from Instagram")


# =========================
# WHOAMI COMMAND
# =========================
@app.on_message(filters.command("whoami") & filters.private)
@owner_only
async def whoami_cmd(_, msg):
    if not load_session():
        return await msg.reply("❌ Not logged in. Use /login first")

    try:
        me = cl.account_info()
        await msg.reply(
            f"👤 Instagram Account Info:\n\n"
            f"• Username: @{me.username}\n"
            f"• Full name: {me.full_name}\n"
            f"• Followers: {me.follower_count}\n"
            f"• Following: {me.following_count}\n"
            f"• Posts: {me.media_count}"
        )
    except Exception as e:
        await msg.reply(f"⚠️ Error fetching account info: {e}")


# =========================
# SESSION INFO COMMAND
# =========================
@app.on_message(filters.command("sessioninfo") & filters.private)
@owner_only
async def sessioninfo_cmd(_, msg):
    if not is_logged_in():
        return await msg.reply("🔴 No active Instagram session")

    try:
        session_file = "data/session.json"
        last_login_ts = os.path.getmtime(session_file)
        last_login_time = datetime.fromtimestamp(last_login_ts)

        await msg.reply(
            "🧾 Session Info:\n\n"
            f"• Status: Logged in\n"
            f"• Last login: {last_login_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• Session file: session.json\n"
            f"• Session valid: Yes"
        )
    except Exception as e:
        await msg.reply(f"⚠️ Error reading session info: {e}")


# =========================
# UNFOLLOWERS COMMAND
# =========================
@app.on_message(filters.command("unfollowers") & filters.private)
@owner_only
async def unfollowers_cmd(_, msg):
    if not load_session():
        return await msg.reply("❌ Login first using /login")

    await msg.reply("⏳ Fetching unfollowers, please wait...")

    try:
        users = get_unfollowers()

        if not users:
            return await msg.reply("✅ No unfollowers found")

        os.makedirs("exports", exist_ok=True)
        file_path = "exports/unfollowers.txt"

        with open(file_path, "w") as f:
            for u in users:
                f.write(u + "\n")

        await msg.reply_document(file_path)

    except Exception as e:
        await msg.reply(f"⚠️ Error: {e}")


# =========================
# ADD MENTION USER
# =========================
@app.on_message(filters.command("addmention") & filters.private)
@owner_only
async def add_mention_cmd(_, msg):
    try:
        _, username = msg.text.split(maxsplit=1)
        add_mention(username)
        await msg.reply(f"✅ Added @{username} to mention list")
    except:
        await msg.reply("❌ Usage: /addmention username")


# =========================
# REMOVE MENTION USER
# =========================
@app.on_message(filters.command("rmmention") & filters.private)
@owner_only
async def remove_mention_cmd(_, msg):
    try:
        _, username = msg.text.split(maxsplit=1)
        remove_mention(username)
        await msg.reply(f"❌ Removed @{username} from mention list")
    except:
        await msg.reply("❌ Usage: /rmmention username")


# =========================
# MENTION ALL (STORY)
# =========================
@app.on_message(filters.command("mentionall") & filters.private)
@owner_only
async def mention_all_cmd(_, msg):
    if not load_session():
        return await msg.reply("❌ Login first using /login")

    await msg.reply("⏳ Processing story mentions. This will take time...")

    result = mention_users_on_story()
    await msg.reply(result)


# =========================
# START BOT
# =========================
print("🤖 Insta Admin Bot running...")
app.run()
