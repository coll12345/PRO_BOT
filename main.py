import asyncio
import sys
import traceback
import threading
import os
import time
import glob
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import idle

from bot import app as bot_app, auto_delete_group_messages

# =========================
# DEPLOYMENT MODE (for Koyeb)
# =========================
BOT_ONLY_MODE = os.getenv("BOT_ONLY_MODE", "true").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

# =========================
# SESSION CLEANUP (prevent SQLite lock on Koyeb)
# =========================
def cleanup_session_journals():
    """Remove stale .session-journal files that block Pyrogram startup."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    patterns = [
        os.path.join(base_dir, "*.session-journal"),
        os.path.join(base_dir, "*.session-journal-*"),
    ]
    removed = 0
    for pattern in patterns:
        for fpath in glob.glob(pattern):
            try:
                os.remove(fpath)
                print(f"🧹 Cleaned stale session file: {os.path.basename(fpath)}")
                removed += 1
            except Exception as e:
                print(f"⚠️ Could not remove {fpath}: {e}")
    if removed == 0:
        print("🧹 No stale session journals found")
    return removed

# =========================
# EXPLICIT PLUGIN IMPORTS (fail loud)
# =========================
print("📦 Loading plugins...")
try:
    import plugins.commands
    print("  ✓ plugins.commands loaded")
except Exception as e:
    print(f"  ❌ plugins.commands failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import plugins.search_new
    print("  ✓ plugins.search_new loaded")
except Exception as e:
    print(f"  ❌ plugins.search_new failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import plugins.shortener
    print("  ✓ plugins.shortener loaded")
except Exception as e:
    print(f"  ❌ plugins.shortener failed: {e}")
    import traceback
    traceback.print_exc()

print("📦 All plugins loaded!")

# =========================
# VERIFY HANDLERS REGISTERED
# =========================
print("\n📊 Checking registered handlers on bot_app...")
try:
    handlers_count = len(bot_app.handlers)
    print(f"  Total handler groups: {handlers_count}")
    for group_num, handler_list in enumerate(bot_app.handlers):
        print(f"  Group {group_num}: {len(handler_list)} handler(s)")
        for handler in handler_list[:3]:  # Show first 3
            print(f"    - {handler}")
except Exception as e:
    print(f"  Error checking handlers: {e}")



# =========================
# HEALTH CHECK SERVER (real bot status)
# =========================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            connected = bot_app.is_connected if bot_app else False
            if connected:
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("🤖 TMPS Movie Bot is running!".encode('utf-8'))
            else:
                self.send_response(503)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("❌ Bot disconnected".encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Server error: {e}".encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress logging

def start_http_server(port=PORT):
    """Start HTTP health check server in background thread"""
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"🌐 HTTP Health Check Server started on port {port}")
        return server
    except Exception as e:
        print(f"⚠️ Failed to start HTTP server: {e}")
        return None

# =========================
# BOT LIFECYCLE
# =========================
async def start_bot():
    try:
        print("📱 Starting Bot Client...")
        await bot_app.start()
        me = await bot_app.get_me()
        print(f"✅ Bot started: @{me.username} (ID: {me.id})")
        # Give dispatcher time to fully initialize
        await asyncio.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
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

async def restart_bot():
    """Restart bot client if it disconnected"""
    print("🔄 Attempting bot restart...")
    try:
        if bot_app.is_connected:
            await bot_app.stop()
            await asyncio.sleep(2)
        await bot_app.start()
        me = await bot_app.get_me()
        print(f"✅ Bot reconnected: @{me.username}")
        await asyncio.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Bot restart failed: {e}")
        return False

# =========================
# WATCHDOG (auto-restart on disconnect)
# =========================
async def bot_watchdog():
    """Monitor bot connection and auto-restart if dead"""
    while True:
        await asyncio.sleep(30)
        try:
            is_connected = getattr(bot_app, "is_connected", False)
            if not is_connected:
                print("⚠️ Watchdog: Bot disconnected! Attempting restart...")
                ok = await restart_bot()
                if not ok:
                    print("❌ Watchdog: Restart failed, will retry in 60s")
                    await asyncio.sleep(60)
            else:
                # Optional: ping Telegram to verify real connectivity
                pass
        except Exception as e:
            print(f"⚠️ Watchdog error: {e}")
            traceback.print_exc()
            await asyncio.sleep(30)

# =========================
# BACKGROUND TASKS (auto-restart on crash)
# =========================
async def resilient_task(coro, name):
    """Wrap a coroutine so it auto-restarts on crash"""
    while True:
        try:
            print(f"🚀 Starting {name}...")
            await coro()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"💥 {name} crashed: {e}")
            traceback.print_exc()
            print(f"🔁 {name} will restart in 10 seconds...")
            await asyncio.sleep(10)

# =========================
# MAIN
# =========================
async def main():
    print("\n" + "=" * 70)
    print("🚀 STARTING TMPS MOVIE BOT")
    print("=" * 70 + "\n")

    # Clean stale session files before starting
    cleanup_session_journals()

    # Start HTTP server for hosting platforms
    http_server = start_http_server(port=PORT)
    if not http_server:
        print("❌ FATAL: Could not start HTTP server. Exiting.")
        sys.exit(1)

    # Start bot
    bot_ok = await start_bot()
    if not bot_ok:
        print("\n❌ FATAL: Bot failed to start. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("🎬 INITIALIZING BACKGROUND TASKS")
    print("=" * 70 + "\n")

    tasks = []

    # Bot watchdog (monitors connection)
    tasks.append(asyncio.create_task(bot_watchdog(), name="watchdog"))

    # Auto-delete group messages (resilient wrapper)
    tasks.append(asyncio.create_task(
        resilient_task(auto_delete_group_messages, "AutoDelete"),
        name="auto_delete"
    ))

    print("\n" + "=" * 70)
    print("✅ BOT READY!")
    print(f"🔁 BOT RUNNING 24/7 on port {PORT}")
    print("=" * 70 + "\n")

    # Keep alive
    try:
        await idle()
    except KeyboardInterrupt:
        print("\n\n⏸️ Received shutdown signal...")
    except Exception as idle_err:
        print(f"\n⚠️ idle() exited unexpectedly: {idle_err}")
        # Fallback: sleep loop with periodic health checks
        while True:
            await asyncio.sleep(60)
            is_connected = getattr(bot_app, "is_connected", False)
            if not is_connected:
                print("⚠️ idle fallback: bot disconnected, attempting restart...")
                await restart_bot()
    finally:
        print("\n🧹 Cleaning up background tasks...")
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await stop_bot()
        if http_server:
            http_server.shutdown()
        print("\n✅ Shutdown complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
