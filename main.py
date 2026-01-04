from pyrogram import Client, filters
from config import *

from insta.client import login, logout, load_session
from insta.unfollowers import get_unfollowers
from insta.mentions import add_mention, remove_mention
from insta.story_mentions import mention_users_on_story

import os


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
    except Exception as e:
        await msg.reply("❌ Usage: /login username password")


# =========================
# LOGOUT COMMAND
# =========================
@app.on_message(filters.command("logout") & filters.private)
@owner_only
async def logout_cmd(_, msg):
    logout()
    await msg.reply("✅ Logged out successfully")


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
