from pyrogram import Client
import requests
import random
from pymongo import MongoClient

# MongoDB for group configs (shared with commands)
MONGO_URI = "mongodb+srv://Dileep:dileep123@cluster0.gejzy.mongodb.net/?retryWrites=true&w=majority"
mongo = MongoClient(MONGO_URI)
shorteners_db = mongo["movie_bot"]["shorteners"]

# Default real token from user
DEFAULT_TOKEN = "7d1a2701da1c2321f60bdb4a13748292b8a0131e"
AROLINKS_BASE = "https://arolinks.com/api"

async def get_group_token(chat_id: int) -> str:
    """Get group-specific token or default"""
    config = shorteners_db.find_one({"chat_id": chat_id})
    return config["token"] if config else DEFAULT_TOKEN

async def shorten(client: Client, long_url: str, chat_id: int = None) -> str:
    """
    Shorten URL using AroLinks API (group-aware token)
    """
    token = DEFAULT_TOKEN
    if chat_id:
        token = await get_group_token(chat_id)
    
    try:
        params = {
            "api": token,
            "url": long_url,
            "format": "text"  # Direct short URL or empty on error
        }
        
        resp = requests.get(AROLINKS_BASE, params=params, timeout=15)
        
        short_url = resp.text.strip()
        if short_url and "arolinks.com" in short_url:
            return short_url
        else:
            print(f"Arolinks failed: {resp.text}")
            return long_url  # fallback
            
    except Exception as e:
        print(f"Shortener error: {e}")
        return long_url

async def test_arolinks():
    """Test API"""
    from pyrogram import Client
    app = Client("test")
    async with app:
        short = await shorten(app, "https://google.com", None)
        print(f"Test short: {short}")

