from pyrogram import Client, filters
from config import *
from insta.client import *
from insta.unfollowers import *
from insta.mentions import *
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
async def login_cmd(client, message):
    try:
        _, u, p = message.text.split(maxsplit=2)
        login(u, p)
        await message.reply("✅ Instagram login successful")
    except:
        await message.reply("❌ Usage: /login username password")

@app.on_message(filters.command("logout") & filters.private)
@owner_only
async def logout_cmd(client, message):
    logout()
    await message.reply("✅ Logged out")

@app.on_message(filters.command("unfollowers") & filters.private)
@owner_only
async def unf_cmd(client, message):
    if not load_session():
        return await message.reply("❌ Login first")

    data = get_unfollowers()
    os.makedirs("exports", exist_ok=True)
    with open("exports/unfollowers.txt", "w") as f:
        f.write("\n".join(data))

    await message.reply_document("exports/unfollowers.txt")

@app.on_message(filters.command("addmention") & filters.private)
@owner_only
async def add_m(client, message):
    _, u = message.text.split()
    add_mention(u)
    await message.reply(f"✅ Added @{u}")

@app.on_message(filters.command("rmmention") & filters.private)
@owner_only
async def rm_m(client, message):
    _, u = message.text.split()
    remove_mention(u)
    await message.reply(f"❌ Removed @{u}")

@app.on_message(filters.command("autoreply") & filters.private)
@owner_only
async def ar(client, message):
    msg = message.text.replace("/autoreply", "").strip()
    os.makedirs("data", exist_ok=True)
    open("data/autoreply.txt", "w").write(msg)
    await message.reply("✅ Autoreply message saved")

app.run()
