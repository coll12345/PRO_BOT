#!/usr/bin/env python3
"""Test script to verify bot startup without running 24/7"""
import asyncio
import sys

async def test_imports():
    """Test that all modules import successfully"""
    print("=" * 70)
    print("📋 TESTING IMPORTS...")
    print("=" * 70)
    
    try:
        print("✓ Importing bot module...")
        from bot import app as bot_app, auto_delete_group_messages
        print(f"  - Bot app instance: {bot_app}")
        print(f"  - Bot token configured: {'✓' if bot_app.bot_token else '✗'}")
        
        print("✓ Importing userbot module...")
        from userbot import app as userbot_app, periodic_index, verify_group
        print(f"  - Userbot app instance: {userbot_app}")
        print(f"  - Userbot API ID configured: {'✓' if userbot_app.api_id else '✗'}")
        
        print("✓ Importing plugins...")
        import plugins.commands
        import plugins.search_new
        import plugins.shortener
        print("  - All plugins loaded successfully")
        
        return bot_app, userbot_app
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

async def test_bot_start(app, name="Bot"):
    """Test if a bot can start and connect"""
    print(f"\n🔌 Testing {name} connection...")
    try:
        await app.start()
        me = await app.get_me()
        print(f"  ✓ Connected as @{me.username}")
        # Don't stop - let it stay connected for manual testing
        return True
    except Exception as e:
        print(f"  ✗ Failed to connect: {e}")
        return False

async def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "TMPS Movie Bot - Startup Test" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝\n")
    
    bot_app, userbot_app = await test_imports()
    
    if not bot_app or not userbot_app:
        print("\n❌ Import test failed - cannot proceed")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🚀 ATTEMPTING TO START BOTS...")
    print("=" * 70)
    
    # Test bot
    bot_ok = await test_bot_start(bot_app, "Bot")
    
    # Test userbot
    userbot_ok = await test_bot_start(userbot_app, "Userbot")
    
    print("\n" + "=" * 70)
    print("📊 STARTUP TEST RESULTS")
    print("=" * 70)
    print(f"Bot Status:     {'✓ OK' if bot_ok else '✗ FAILED'}")
    print(f"Userbot Status: {'✓ OK' if userbot_ok else '✗ FAILED'}")
    
    if bot_ok and userbot_ok:
        print("\n✅ Both bots are running! They will stay connected.")
        print("💡 To use the full system, run: python main.py")
        print("   Press Ctrl+C to stop and return to terminal")
        try:
            # Keep running until interrupted
            from pyrogram import idle
            await idle()
        except KeyboardInterrupt:
            print("\n\n⏸️ Stopping bots...")
            await bot_app.stop()
            await userbot_app.stop()
            print("✅ Stopped.")
    else:
        print("\n❌ One or more bots failed to start")
        print("   Check your API credentials and internet connection")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
