import asyncio
import sys
import traceback
from pyrogram import idle

from bot import app as bot_app, auto_delete_group_messages
from userbot import app as userbot_app, periodic_index, verify_group

async def start_bot():
    try:
        print("📱 Starting Bot Client...")
        await bot_app.start()
        me = await bot_app.get_me()
        print(f"✅ Bot started: @{me.username} (ID: {me.id})")
        return True
    except Exception as e:
        print(f"❌ Bot failed: {e}")
        traceback.print_exc()
        return False

async def start_userbot():
    try:
        print("👤 Starting Userbot Client...")
        await userbot_app.start()
        me = await userbot_app.get_me()
        print(f"✅ Userbot started: @{me.username or me.id} (ID: {me.id})")
        return True
    except Exception as e:
        print(f"❌ Userbot failed: {e}")
        traceback.print_exc()
        return False

async def stop_all():
    print("\n🛑 Shutting down bots...")
    try:
        if bot_app.is_connected:
            await bot_app.stop()
            print("✅ Bot stopped")
    except Exception as e:
        print(f"⚠️ Error stopping bot: {e}")
    try:
        if userbot_app.is_connected:
            await userbot_app.stop()
            print("✅ Userbot stopped")
    except Exception as e:
        print(f"⚠️ Error stopping userbot: {e}")
    print("🛑 All bots stopped.")

async def main():
    print("\n" + "=" * 70)
    print("🚀 STARTING TMPS MOVIE BOT + USERBOT")
    print("=" * 70 + "\n")

    # Start sequentially to avoid race conditions on Windows
    bot_ok = await start_bot()
    userbot_ok = await start_userbot()

    if not bot_ok and not userbot_ok:
        print("\n❌ FATAL: Both bots failed to start. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("🎬 INITIALIZING BACKGROUND TASKS")
    print("=" * 70 + "\n")

    tasks = []

    if userbot_ok:
        try:
            print("🔐 Verifying userbot group access...")
            access_ok = await verify_group()
            if access_ok:
                print("✅ Group access verified. Starting periodic movie indexing...")
                tasks.append(asyncio.create_task(periodic_index()))
            else:
                print("⚠️ Group access failed. Movie indexing disabled.")
        except Exception as e:
            print(f"⚠️ Error verifying group: {e}")

    if bot_ok:
        print("🧹 Starting auto-delete group messages task...")
        try:
            tasks.append(asyncio.create_task(auto_delete_group_messages()))
        except Exception as e:
            print(f"⚠️ Error starting auto-delete task: {e}")

    print("\n" + "=" * 70)
    print("✅ ALL SYSTEMS READY!")
    print("🔁 BOTS RUNNING 24/7 - Press Ctrl+C to stop")
    print("=" * 70 + "\n")

    try:
        await idle()
    except KeyboardInterrupt:
        print("\n\n⏸️ Received shutdown signal...")
    except Exception as idle_err:
        print(f"\n⚠️ idle() exited unexpectedly: {idle_err}")
        # Fallback keep-alive
        while True:
            await asyncio.sleep(3600)
    finally:
        print("\n🧹 Cleaning up background tasks...")
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await stop_all()
        print("\n✅ Shutdown complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

