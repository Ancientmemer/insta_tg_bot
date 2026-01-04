from pyrogram import Client, filters
from config import *
from insta.client import *
from insta.unfollowers import get_unfollowers
from insta.mentions import add_mention, remove_mention
from insta.story_mentions import mention_users_on_story
import os

app = Client(
    "insta_admin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def owner_only(func):
    async def wrapper(client, message):
        if message.from_user.id != OWNER_ID:
            return
        return await func(client, message)
    return wrapper

@app.on_message(filters.command("login") & filters.private)
@owner_only
async def login_cmd(_, msg):
    try:
        _, u, p = msg.text.split(maxsplit=2)
        login(u, p)
        await msg.reply("✅ Instagram login successful")
    except:
        await msg.reply("❌ /login username password")

@app.on_message(filters.command("logout") & filters.private)
@owner_only
async def logout_cmd(_, msg):
    logout()
    await msg.reply("✅ Logged out")

@app.on_message(filters.command("unfollowers") & filters.private)
@owner_only
async def unf_cmd(_, msg):
    if not load_session():
        return await msg.reply("❌ Login first")

    data = get_unfollowers()
    os.makedirs("exports", exist_ok=True)
    with open("exports/unfollowers.txt", "w") as f:
        f.write("\n".join(data))

    await msg.reply_document("exports/unfollowers.txt")

@app.on_message(filters.command("addmention") & filters.private)
@owner_only
async def add_m(_, msg):
    _, u = msg.text.split()
    add_mention(u)
    await msg.reply(f"✅ Added @{u}")

@app.on_message(filters.command("rmmention") & filters.private)
@owner_only
async def rm_m(_, msg):
    _, u = msg.text.split()
    remove_mention(u)
    await msg.reply(f"❌ Removed @{u}")

@app.on_message(filters.command("mentionall") & filters.private)
@owner_only
async def mention_all(_, msg):
    if not load_session():
        return await msg.reply("❌ Login first")

    res = mention_users_on_story()
    await msg.reply(res)

app.run()
