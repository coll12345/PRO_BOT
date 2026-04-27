# TMPS Movie Bot - Fixed Issues & Solutions

## Problems Identified & Fixed

### 1. **Conflicting app.run() Calls**
   **Problem:** Both `bot.py` and `userbot.py` had their own `main()` functions calling `app.run()`, which conflicted with `main.py` trying to start both apps.
   
   **Solution:** Removed the `main()` function and `if __name__ == "__main__"` blocks from both files. Now `main.py` has complete control over starting both bots.

### 2. **Missing Plugin Handler Registration**
   **Problem:** `plugins/commands.py` had conflicting handlers (`/start` and `/id` stubs) using `@Client.on_message()` that could interfere with the main bot handlers.
   
   **Solution:** Removed the conflicting stub handlers to prevent conflicts with the actual `/start` handler in `bot.py`.

### 3. **Incomplete main.py Error Handling**
   **Problem:** main.py had minimal error logging and didn't import plugins explicitly, so handlers might not be registered.
   
   **Solution:** Enhanced `main.py` to:
   - Explicitly import all plugin modules to register their handlers
   - Add comprehensive error handling with tracebacks
   - Check if clients are properly connected before stopping
   - Display detailed startup/shutdown logging
   - Handle Ctrl+C gracefully
   - Add system exit codes for failures

## How to Run the Fixed Bot

### Option 1: Full System (Recommended)
```bash
python main.py
```
This starts:
- Telegram Bot (responds to /start, searches movies, handles links)
- Userbot (auto-indexes movies from channel, runs periodic indexing)
- All background tasks and handlers

### Option 2: Test Startup First
```bash
python test_startup.py
```
This tests:
- All imports work correctly
- Bot can connect to Telegram
- Userbot can authenticate
- Shows detailed connection info

## Expected Behavior After Fix

### Bot (@TMPS_Movie_bot)
- ✅ Responds to `/start` command with greeting menu
- ✅ Handles movie search requests
- ✅ Provides short links for movie downloads
- ✅ Auto-deletes tracked group messages every 10 minutes

### Userbot
- ✅ Auto-saves new movies uploaded to MOVIE_CHANNEL (-1002195257765)
- ✅ Re-indexes entire channel every 6 hours
- ✅ Stores movies in MongoDB for fast searching

### Group Functionality
- ✅ Accepts /setlink command (admin only)
- ✅ Can show and remove link configurations
- ✅ Automatically cleans up messages

## Troubleshooting

If bots still don't respond after running:

1. **Check API Credentials**
   ```bash
   python test_startup.py
   ```
   This will show connection status and errors clearly.

2. **Verify Bot Token**
   - In `bot.py`, line 11: BOT_TOKEN should be active
   - Get new token from @BotFather if expired

3. **Verify Userbot Session**
   - In `userbot.py`, the `app = Client("userbot", ...)` creates session file
   - Delete `.session` files if authentication fails
   - Re-authenticate if needed

4. **MongoDB Connection**
   - Verify MONGO_URI in `userbot.py`
   - Check if connection is accessible from your network

5. **Movie Channel Access**
   - Userbot must be a member of MOVIE_CHANNEL (-1002195257765)
   - Check that the channel ID is correct

## Architecture

```
main.py (starts both bots)
├── bot.py (Telegram Bot)
│   ├── Handler: /start → show menu
│   ├── Handler: movie search
│   ├── Handler: link generation
│   └── Background: auto-delete messages
└── userbot.py (Userbot)
    ├── Handler: auto-save movies
    ├── Background: periodic indexing
    └── Database: MongoDB connection

    plugins/ (Shared handlers)
    ├── commands.py (admin commands)
    ├── search_new.py (search logic)
    └── shortener.py (link shortening)
```

## Quick Start

1. Ensure dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test to verify setup:
   ```bash
   python test_startup.py
   ```

3. If test passes, start the full system:
   ```bash
   python main.py
   ```

The bots will now run 24/7 and respond to Telegram messages properly!
