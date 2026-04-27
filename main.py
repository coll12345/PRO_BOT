import asyncio
import sys
import traceback
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import idle

from bot import app as bot_app, auto_delete_group_messages

# =========================
# DEPLOYMENT MODE (for Koyeb)
# =========================
BOT_ONLY_MODE = os.getenv("BOT_ONLY_MODE", "true").lower() == "true"

# =========================
# DUMMY HTTP SERVER (for Koyeb/hosting platforms)
# =========================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("🤖 TMPS Movie Bot is running!".encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def start_http_server(port=8000):
    """Start dummy HTTP server in background thread"""
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"🌐 HTTP Health Check Server started on port {port}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to start HTTP server: {e}")
        return False

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

async def stop_bot():
    print("\n🛑 Shutting down bot...")
    try:
        if bot_app.is_connected:
            await bot_app.stop()
            print("✅ Bot stopped")
    except Exception as e:
        print(f"⚠️ Error stopping bot: {e}")

async def main():
    print("\n" + "=" * 70)
    print("🚀 STARTING TMPS MOVIE BOT (BOT-ONLY MODE)")
    print("=" * 70 + "\n")

    # Start HTTP server for hosting platforms
    start_http_server(port=8000)

    # Start bot
    bot_ok = await start_bot()

    if not bot_ok:
        print("\n❌ FATAL: Bot failed to start. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("🎬 INITIALIZING BACKGROUND TASKS")
    print("=" * 70 + "\n")

    tasks = []

    print("🧹 Starting auto-delete group messages task...")
    try:
        tasks.append(asyncio.create_task(auto_delete_group_messages()))
    except Exception as e:
        print(f"⚠️ Error starting auto-delete task: {e}")

    print("\n" + "=" * 70)
    print("✅ BOT READY!")
    print("🔁 BOT RUNNING 24/7 - Press Ctrl+C to stop")
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
        await stop_bot()
        print("\n✅ Shutdown complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

