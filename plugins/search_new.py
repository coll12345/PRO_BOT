from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import math
import asyncio
import hashlib
from .shortener import shorten
from bot import app, MOVIE_CHANNEL

# CONFIG
MONGO_URI = "mongodb+srv://Dileep:dileep123@cluster0.gejzy.mongodb.net/?retryWrites=true&w=majority"

mongo = MongoClient(MONGO_URI)
db = mongo["movie_bot"]
collection = db["movies"]

# Speed: ensure indexes exist
try:
    collection.create_index([("name", "text")])
    collection.create_index([("id", 1)], unique=True)
except Exception as e:
    print(f"Index creation warning (may already exist): {e}")

RESULTS_PER_PAGE = 10
MAX_RESULTS = 100

user_results = {}
user_queries = {}


@app.on_message(filters.text & ~filters.regex(r'^/') & filters.private)
async def search_movie(client, message):
    query = message.text.lower().strip()
    
    print(f"DEBUG: Search handler triggered with query: '{query}'")

    if not query:
        print(f"DEBUG: Empty query, ignoring")
        return

    # Try fast text search first
    try:
        results = list(collection.find(
            {"$text": {"$search": query}},
            {"name": 1, "id": 1, "size": 1, "score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(MAX_RESULTS))
    except Exception:
        results = []

    # Fallback to regex if text search yields nothing
    if not results:
        results = list(collection.find(
            {"name": {"$regex": query, "$options": "i"}},
            {"name": 1, "id": 1, "size": 1}
        ).limit(MAX_RESULTS))

    if not results:
        user = message.from_user
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "User"
        user_mention = user.mention(full_name)

        text = f"""Hey {user_mention} 👋

😕 No results found for: {message.text}

💡 Try this:
• Check spelling carefully
• Use short keywords
• Avoid extra words

🎬 Still not found?
It may not be available in my database yet."""

        google_url = f"https://www.google.com/search?q={message.text.replace(' ', '+')}+movie"

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search on Google", url=google_url)]
        ])

        await message.reply_text(
            text,
            reply_markup=buttons,
            disable_web_page_preview=True,
        )
        return

    user_results[message.from_user.id] = results
    user_queries[message.from_user.id] = message.text

    await send_page(client, message, message.from_user.id, 0)


async def send_page(client, message, user_id, page):
    results = user_results.get(user_id)
    if not results:
        return

    total_pages = math.ceil(len(results) / RESULTS_PER_PAGE)
    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = results[start:end]

    user = message.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "User"
    user_mention = user.mention(full_name)
    query = user_queries.get(user_id, "your search")

    text = f"""Hey {user_mention} 😍

🎬 Found for: {query}
📄 Page {page + 1} of {total_pages}"""

    buttons = []

    for movie in page_results:
        size = round(movie.get("size", 0) / (1024 * 1024), 2)
        size_text = f"{round(size/1024, 2)} GB" if size > 1024 else f"{size} MB"
        name = movie["name"][:55]

        buttons.append([
            InlineKeyboardButton(
                f"🎥 {size_text} | {name}",
                callback_data=f"get_{movie['id']}"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+2}"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton("🗑 Close", callback_data="close_results")])

    try:
        if message.from_user and message.from_user.is_self:
            await message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            raise Exception("Not a bot message")
    except Exception:
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query(filters.regex("get_"))
async def movie_link_handler(client, callback_query):
    msg_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    hash_key = hashlib.md5(f"{user_id}{msg_id}tm_bot_secret".encode()).hexdigest()[:8]
    me = await client.get_me()
    deep_link = f"https://t.me/{me.username}?start=verify_{user_id}_{msg_id}_{hash_key}"
    verify_url = await shorten(client, deep_link, callback_query.message.chat.id)

    # Fetch movie details from DB
    movie_doc = collection.find_one({"id": msg_id})
    file_name = movie_doc["name"] if movie_doc else "Unknown File"

    text = f"""🔗 Verification URL - Open for Movies
{verify_url}

👆 Click → Ads → Your movie files! 🎬

📁 {file_name}

For More Movies Join :- @TMPS_Movies"""
    buttons = [[InlineKeyboardButton("🔗 Open Verification Link", url=verify_url)]]

    await callback_query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=False
    )
    await callback_query.answer("Link generated!")


@app.on_callback_query(filters.regex("page_"))
async def change_page(client, callback_query):
    page = int(callback_query.data.split("_")[1]) - 1
    message = callback_query.message
    await send_page(client, message, callback_query.from_user.id, page)
    await callback_query.answer()


@app.on_callback_query(filters.regex("ignore"))
async def ignore(client, callback_query):
    await callback_query.answer()


@app.on_callback_query(filters.regex("close_results"))
async def close_results(client, callback_query):
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.answer("Closed")

