# Fix Plan — Bot Running on Koyeb But Not Working

## Issues
1. Fake health check always returns 200 even if bot is dead
2. Hardcoded port 8000 ignores Koyeb's PORT env var
3. No reconnection watchdog — bot can die silently
4. `poster.jpg` crash risk on `/start`
5. Silent plugin import failures
6. Background task crashes are never restarted

## Steps
- [x] Step 1: Update `main.py` — dynamic PORT, real health check, watchdog, explicit plugin imports, auto-restart tasks
- [x] Step 2: Update `bot.py` — add `poster.jpg` existence check with text-only fallback
- [x] Step 3: Update `Dockerfile` — add `ENV PORT=8000` and `EXPOSE 8000`
- [x] Step 4: Update `requirements.txt` — pin `pyrogram>=2.0.0`
- [x] Step 5: Verify all files are correct

