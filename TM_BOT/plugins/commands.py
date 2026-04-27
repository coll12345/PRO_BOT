from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .shortener import shorteners_db  # Shared MongoDB

# Global ADMINS
ADMINS = [5036765942, 8418744969, 5695787932]  # @ITSMEEANONYMOUSSSS @ImNobodyYouKnow @ITSMEEANONYMOUSSS

# Helper: Check if user is admin
async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False

@Client.on_message(filters.command("setlink"))
async def setlink(client: Client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ Admin only!")
        return
    if len(message.command) < 3:
        await message.reply_text("/setlink <site> <token>")
        return
    site = message.command[1]
    token = " ".join(message.command[2:])
    chat_id = message.chat.id
    shorteners_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "site": site, "token": token}},
        upsert=True
    )
    print(f"Set token for {chat_id}: {token[:10]}...")
    await message.reply_text("✅ Set!")

@Client.on_message(filters.command("showlink"))
async def showlink(client: Client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ Admin only!")
        return
    config = shorteners_db.find_one({"chat_id": message.chat.id})
    if config:
        await message.reply_text(f"Site: {config['site']}")
    else:
        await message.reply_text("Default token used.")

@Client.on_message(filters.command("rmlink"))
async def rmlink(client: Client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ Admin only!")
        return
    shorteners_db.delete_one({"chat_id": message.chat.id})
    await message.reply_text("✅ Removed.")

# Stubs
@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bot started.")

@Client.on_message(filters.command("id"))
async def get_id(client, message):
    await message.reply_text(f"ID: {message.from_user.id}")
