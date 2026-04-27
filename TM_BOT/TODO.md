# 24/7 Deployment Plan for TMPS Movie Bot

## Information Gathered
- Two separate Pyrogram clients exist: `bot.py` (main bot) and `userbot.py` (indexer/userbot).
- Both must run simultaneously for full functionality.
- `bot.py` currently calls `app.run(main())` at the top level, blocking import.
- `userbot.py` is already import-safe (`if __name__ == "__main__":`).
- MongoDB Atlas is used (cloud-hosted, no local DB needed).
- Session files (`.session`) must be present at runtime.
- Dependencies: pyrogram, tgcrypto, pymongo, pytz, requests.

## Plan

### Step 1: Refactor `bot.py` ✅
- Wrap `app.run(main())` inside `if __name__ == "__main__":`.
- This allows safe importing of the `app` object into a unified runner.

### Step 2: Create `main.py` (Unified Entry Point) ✅
- Import both `app` objects from `bot.py` and `userbot.py`.
- Start both clients concurrently using `asyncio.gather`.
- Use `pyrogram.idle()` to keep the process alive indefinitely.
- This simplifies deployment to a single command: `python main.py`.

### Step 3: Create `Procfile` ✅
- Add `worker: python main.py` for Heroku/Railway/Render compatibility.

### Step 4: Create `Dockerfile` ✅
- Use `python:3.11-slim` base image.
- Copy all project files including `.session` files.
- Install requirements and set `CMD ["python", "main.py"]`.

### Step 5: Create `.dockerignore` ✅
- Exclude unnecessary files (`.git`, `__pycache__`, etc.).

### Step 6: Create `start.sh` ✅
- Simple bash script for Linux/VPS deployment.
- Activates virtual env (if exists) and runs `python main.py`.

### Step 7: Create `DEPLOY.md` ✅
- Step-by-step instructions for:
  - Railway / Render ( easiest free options )
  - Heroku
  - VPS / Dedicated Server
  - Local Windows (background with `pythonw` or NSSM)

## Dependent Files to Edit
- `bot.py` (minor refactor) ✅
- `userbot.py` (no changes needed) ✅

## Follow-up Steps
- Ensure `.session` files are included when pushing to cloud hosts.
- Install requirements: `pip install -r requirements.txt`.
- Start the bot: `python main.py` or via the platform's dashboard.

