import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import asyncio
from plugins.search_new import MOVIE_CHANNEL

API_ID = 30393136
API_HASH = "4b2a23c681028e19cba2f63155e00f31"
BOT_TOKEN = "8743247622:AAH5zXO4GXlxq2a-PWvy-Y3-Dpy8ds-9Ds0"

# CREATE APP
app = Client(
    "TMPS_Movie_bot_new",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

# =========================
# AUTO DELETE GROUP MESSAGES
# =========================
group_messages = {}  # chat_id -> list of message_ids

@app.on_message(filters.group & ~filters.service)
async def track_group_message(client, message):
    """Track every message in groups for auto-deletion."""
    chat_id = message.chat.id
    msg_id = message.id
    if chat_id not in group_messages:
        group_messages[chat_id] = []
    group_messages[chat_id].append(msg_id)

async def auto_delete_group_messages():
    """Background task: delete all tracked group messages every 10 minutes."""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        for chat_id, msg_ids in list(group_messages.items()):
            for msg_id in msg_ids:
                try:
                    await app.delete_messages(chat_id, msg_id)
                except Exception:
                    pass
            group_messages[chat_id] = []

# =========================
# SEND START MENU FUNCTION
# =========================
async def send_start_menu(client, message_or_callback):
    user = message_or_callback.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "User"
    user_mention = user.mention(full_name)

    ist = pytz.timezone('Asia/Kolkata')
    hour = datetime.now(ist).hour

    if 5 <= hour < 12:
        greet = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌅"
    elif 12 <= hour < 17:
        greet = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ ☀️"
    elif 17 <= hour < 21:
        greet = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌆"
    else:
        greet = "ɢᴏᴏᴅ ɴɪɢʜᴛ 🌙"

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Me To Your Own Group", url="https://t.me/TMPS_Movie_bot?startgroup=true")],
            [
                InlineKeyboardButton("💥 Movie Updates", url="https://t.me/+LzW13Oz_iqUxYTJl"),
                InlineKeyboardButton("🎬 Movie Group", url="https://t.me/+mLAgQEMIxa1kOGI1")
            ],
            [
                InlineKeyboardButton("💰 Earn Money", callback_data="earn"),
                InlineKeyboardButton("👨‍💻 About Me", callback_data="about")
            ],
            [InlineKeyboardButton("💎 Premium Membership 💎", callback_data="sub")]
        ]
    )

    text = f"""Hᴇʏ {user_mention} {greet} 👋

ɪ ᴄᴀɴ ᴘʀᴏᴠɪᴅᴇ ᴍᴏᴠɪᴇs ᴀɴᴅ sᴇʀɪᴇs,
ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴇɴᴊᴏʏ."""

    poster_exists = os.path.exists("poster.jpg")

    # If called via callback (Back button), delete old message first
    if hasattr(message_or_callback, "message"):
        try:
            await message_or_callback.message.delete()
        except:
            pass
        if poster_exists:
            await message_or_callback.message.reply_photo(
                photo="poster.jpg",
                caption=text,
                reply_markup=buttons,
            )
        else:
            await message_or_callback.message.reply_text(
                text,
                reply_markup=buttons,
            )

    else:
        if poster_exists:
            await message_or_callback.reply_photo(
                photo="poster.jpg",
                caption=text,
                reply_markup=buttons,
            )
        else:
            await message_or_callback.reply_text(
                text,
                reply_markup=buttons,
            )


# =========================
# /start COMMAND
# =========================
@app.on_message(filters.command("start"))
async def start(client, message):
    data = message.command[1] if len(message.command) > 1 else None
    if data and data.startswith("verify_"):
        try:
            parts = data.split("_")
            if len(parts) != 4:
                raise ValueError("Invalid")
            user_id = int(parts[1])
            msg_id = int(parts[2])
            received_hash = parts[3]
            import hashlib
            expected_hash = hashlib.md5(f"{user_id}{msg_id}tm_bot_secret".encode()).hexdigest()[:8]
            if received_hash == expected_hash and message.from_user.id == user_id:
                sent_msg = await client.copy_message(message.chat.id, MOVIE_CHANNEL, msg_id)
                await message.reply_text("✅ You are verified! Movie delivered 🎬\n⚠️ Movies Delete in 2min kindly share to saved message or friends")
                import asyncio
                async def delete_msg():
                    await asyncio.sleep(120)
                    try:
                        await sent_msg.delete()
                    except:
                        pass
                asyncio.create_task(delete_msg())
                return
        except:
            pass
    # Only plain /start shows menu - BRO handled above
    if not data:
        await send_start_menu(client, message)

# =========================
# EARN MONEY BUTTON
# =========================
@app.on_callback_query(filters.regex("earn"))
async def earn_money(client, callback_query):
    text = """• ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴍᴏɴᴇʏ ꜰʀᴏᴍ ᴏᴜʀ ʙᴏᴛ •

✦ ʜᴇʀᴇ ᴀʀᴇ ꜱᴏᴍᴇ ꜱᴛᴇᴘꜱ ʙʏ ꜰᴏʟʟᴏᴡɪɴɢ ᴡʜɪᴄʜ ʏᴏᴜ ᴄᴀɴ ᴇᴀʀɴ ᴀ ʟᴏᴛ ᴏꜰ ᴍᴏɴᴇʏ ꜰʀᴏᴍ ᴏᴜʀ ʙᴏᴛ!

sᴛᴇᴘ 𝟷 : ʏᴏᴜ ᴍᴜsᴛ ʜᴀᴠᴇ ᴀᴛʟᴇᴀsᴛ ᴏɴᴇ ɢʀᴏᴜᴘ.
ꜱᴛᴇᴘ 2 : ᴄʀᴇᴀᴛᴇ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴏɴ ᴀɴʏ ᴛʀᴜsᴛᴇᴅ sʜᴏʀᴛɴᴇʀ ᴡᴇʙsɪᴛᴇ.
ꜱᴛᴇᴘ 3 : ᴄᴏᴘʏ ʏᴏᴜʀ ᴀᴘɪ ᴛᴏᴋᴇɴ ꜰʀᴏᴍ ʟɪɴᴋ ꜱᴏʀᴛɴᴇʀ ᴡᴇʙꜱɪᴛᴇ ᴛᴏᴏʟs sᴇᴄᴛɪᴏɴ.
ꜱᴛᴇᴘ 4 : ꜱᴇɴᴅ ʏᴏᴜʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ɪɴ ᴛʜᴇ ɢɪᴠᴇɴ ꜰᴏʀᴍᴀᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.

/sᴇᴛʟɪɴᴋ ᴡᴇʙꜱɪᴛᴇɴᴀᴍᴇ ᴀᴘɪᴛᴏᴋᴇɴ
ᴇx: /setlink example.com f7d3d6a03b890eea722a5c9a39ccae13575000c7

➥ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ǫᴜᴇꜱᴛɪᴏɴ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴏᴜʀ ʙᴏᴛ ᴏʀ ʜᴀᴠᴇ ꜰᴏᴜɴᴅ ᴀɴʏ ʙᴜɢ ɪɴ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ᴘʟᴇᴀꜱᴇ ᴅᴏ ɴᴏᴛ ʜᴇꜱɪᴛᴀᴛᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ.
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back"),
                InlineKeyboardButton("📩 Contact", url="https://t.me/TMPS_help_bot")
            ]
        ]
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

# =========================
# BACK BUTTON
# =========================
@app.on_callback_query(filters.regex("back"))
async def back(client, callback_query):
    await send_start_menu(client, callback_query)

# =========================
# SUBSCRIPTION / PREMIUM BUTTON
# =========================
@app.on_callback_query(filters.regex("sub"))
async def subscription(client, callback_query):
    text = """💎 ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴠɪᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ 💎

Unlock EVERYTHING with TMPS Premium and NEVER wait for movies again! 🚀

💰 Plans:
• ₹59 / 1 Month
• ₹159 / 3 Months
• ₹599 / 12 Months

🎬 Why Premium?
🔥 No Ads – Stream & download without interruptions
⚡ Ultra-Fast Downloads – Direct files, zero waiting
📥 Daily New Movies – Get the latest blockbusters instantly
💾 High-Quality Files – 1080p, HEVC, 10-bit options
🌟 Exclusive Content – Only for premium members
📱 Watch Anywhere – Mobile, tablet, or desktop

🎉 Join the VIP club NOW & enjoy movies like a PRO!

⏳ Don’t waste time, every second without Premium is a missed blockbuster! 💥
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back"),
                InlineKeyboardButton("📩 Contact", url="https://t.me/TMPS_help_bot")
            ]
        ]
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

# =========================
# ABOUT ME BUTTON (Fancy Font)
# =========================
@app.on_callback_query(filters.regex("about"))
async def about_me(client, callback_query):
    text = """🤖  ᴀʙᴏᴜᴛ ᴛᴍᴘꜱ ᴍᴏᴠɪᴇ ʙᴏᴛ 🤖

ᴛᴍᴘꜱ ᴍᴏᴠɪᴇ ʙᴏᴛ ɪꜱ ʏᴏᴜʀ ᴜʟᴛɪᴍᴀᴛᴇ ᴍᴏᴠɪᴇ ᴘʀᴏᴠɪᴅᴇʀ,
ᴅᴇʟɪᴠᴇʀɪɴɢ ʀᴇǫᴜᴇꜱᴛᴇᴅ ᴍᴏᴠɪᴇꜱ ᴅɪʀᴇᴄᴛʟʏ ᴀɴᴅ ᴀʟꜱᴏ ᴜᴘʟᴏᴀᴅɪɴɢ ᴛʜᴇ ʟᴀᴛᴇꜱᴛ ʀᴇʟᴇᴀꜱᴇꜱ 🎬🍿

🧑‍💻  𝐀𝐛ᴏᴜᴛ ᴍᴇ 🧑‍💻

‣ ᴍʏ ɴᴀᴍᴇ : NIG*** 🤖
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : [Meet him](https://t.me/TMPS_help_bot)

💡 ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ǫᴜᴇꜱᴛɪᴏɴ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴛʜᴇ ʙᴏᴛ ᴏʀ ɴᴏᴛɪᴄᴇ ᴀɴʏ ʙᴜɢ, ᴅᴏ ɴᴏᴛ ʜᴇꜱɪᴛᴀᴛᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ.

Enjoy movies, hassle-free! 🎬🍿
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back"),
                InlineKeyboardButton("📩 Contact", url="https://t.me/TMPS_help_bot")
            ]
        ]
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=False
    )

# Bot is started from main.py

