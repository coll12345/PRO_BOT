import asyncio
from pyrogram import idle

# Import both apps
from bot import app as bot_app
from userbot import app as userbot_app

async def main():
    print("=" * 60)
    print("🚀 Starting TMPS Movie Bot + Userbot")
    print("=" * 60)

    # Start both clients
    await asyncio.gather(
        bot_app.start(),
        userbot_app.start()
    )

    print("✅ Bot started successfully!")
    print("✅ Userbot started successfully!")
    print("🔁 Running 24/7... Press Ctrl+C to stop.")
    print("=" * 60)

    # Keep running forever
    await idle()

    # Graceful shutdown (only reached on stop signal)
    await asyncio.gather(
        bot_app.stop(),
        userbot_app.stop()
    )
    print("🛑 Bots stopped.")

if __name__ == "__main__":
    asyncio.run(main())

