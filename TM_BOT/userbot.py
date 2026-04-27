from pyrogram import Client, filters
from pymongo import MongoClient, ASCENDING
import asyncio

API_ID = 30393136
API_HASH = "4b2a23c681028e19cba2f63155e00f31"

# ✅ CHANNEL ID (Private Group)
MOVIE_CHANNEL = -1002195257765

# ✅ MongoDB
MONGO_URI = "mongodb+srv://Dileep:dileep123@cluster0.gejzy.mongodb.net/?retryWrites=true&w=majority"
mongo = MongoClient(MONGO_URI)
db = mongo["movie_bot"]
collection = db["movies"]

# ✅ UNIQUE INDEX (NO DUPLICATES EVER)
collection.create_index([("id", ASCENDING)], unique=True)

# ✅ TEXT INDEX (FAST SEARCH)
collection.create_index([("name", "text")])

# ✅ USERBOT
app = Client("userbot", api_id=API_ID, api_hash=API_HASH)


# =========================
# 🔥 AUTO SAVE NEW MOVIES (24/7 LIVE)
# =========================
@app.on_message(filters.chat(MOVIE_CHANNEL) & (filters.document | filters.video))
async def save_new(client, message):
    try:
        file = message.document or message.video

        if file and file.file_name:
            data = {
                "name": file.file_name.lower(),
                "id": message.id,
                "caption": message.caption or "",
                "file_id": file.file_id,
                "size": file.file_size
            }

            try:
                collection.insert_one(data)
                print(f"✅ NEW SAVED: {file.file_name}")
            except:
                pass  # duplicate, ignore

    except Exception as e:
        print("⚠️ Error saving new movie:", e)


# =========================
# 🚀 SMART INDEX (SKIP ALREADY INDEXED)
# =========================
async def smart_index():
    print("\n" + "="*60)
    print("🚀 SMART INDEX STARTED (skipping already saved files)...")
    print("="*60)

    try:
        # Get all already saved message IDs from DB
        existing_ids = set(
            doc["id"] for doc in collection.find({}, {"id": 1, "_id": 0})
        )
        print(f"📦 Already in DB: {len(existing_ids)} files")

        last_id = 0
        total_scanned = 0
        total_new = 0
        batch = []

        while True:
            try:
                messages = []

                async for msg in app.get_chat_history(
                    MOVIE_CHANNEL,
                    offset_id=last_id,
                    limit=200
                ):
                    messages.append(msg)

                if not messages:
                    print("📭 Reached end of messages")
                    break

                for message in messages:
                    total_scanned += 1

                    # ⚡ SKIP if already in DB
                    if message.id in existing_ids:
                        continue

                    file = message.document or message.video

                    if file and file.file_name:
                        batch.append({
                            "name": file.file_name.lower(),
                            "id": message.id,
                            "caption": message.caption or "",
                            "file_id": file.file_id,
                            "size": file.file_size
                        })
                        total_new += 1

                last_id = messages[-1].id

                if len(batch) >= 100:
                    try:
                        collection.insert_many(batch, ordered=False)
                        print(f"⚡ Batch inserted: {len(batch)} new files | Total scanned: {total_scanned}")
                    except Exception as insert_err:
                        print(f"⚠️ Batch insert error: {insert_err}")
                    batch.clear()

            except Exception as e:
                print(f"⚠️ Error in loop: {e}")
                await asyncio.sleep(5)

        # Insert remaining
        if batch:
            try:
                collection.insert_many(batch, ordered=False)
                print(f"⚡ Final batch inserted: {len(batch)} new files")
            except Exception as e:
                print(f"⚠️ Final batch error: {e}")

        print(f"\n✅ SMART INDEX DONE")
        print(f"   📊 New files added: {total_new}")
        print(f"   📈 Total scanned: {total_scanned}")
        print(f"   💾 Total in DB: {len(existing_ids) + total_new}")
        print("="*60 + "\n")

    except Exception as e:
        print(f"❌ Smart index fatal error: {e}")
        await asyncio.sleep(10)


# =========================
# 🔁 PERIODIC RE-INDEX (every 6 hours)
# =========================
async def periodic_index():
    # Run immediately on startup
    await smart_index()
    
    while True:
        print("⏳ Next re-index in 6 hours...")
        await asyncio.sleep(6 * 60 * 60)  # 6 hours
        await smart_index()


# =========================
# ✅ VERIFY GROUP ACCESS
# =========================
async def verify_group():
    try:
        chat = await app.get_chat(MOVIE_CHANNEL)
        print(f"✅ Group accessed: {chat.title}")
        print(f"📊 Group ID: {chat.id}")
        print(f"👥 Members: {chat.members_count}")
        return True
    except Exception as e:
        print(f"❌ Cannot access group: {e}")
        return False


# Userbot is started from main.py