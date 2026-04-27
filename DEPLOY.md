# 🚀 TMPS Movie Bot — 24/7 Deployment Guide

## ⚠️ IMPORTANT: Session Files
Your `.session` files **must** be present at runtime. Do NOT delete them.
- `TMPS_Movie_bot_new.session` (Bot session)
- `userbot.session` (Userbot session)

If deploying to the cloud, make sure these files are included in your upload/repo.

---

## 🟢 Option 1: Railway (Recommended — Free Tier Available)

1. Go to [railway.app](https://railway.app) and sign up with GitHub.
2. Create a **New Project** → **Deploy from GitHub repo**.
3. Select your repo. Railway will auto-detect the `Procfile`.
4. Add your `.session` files to the repo (or use Railway Volume for persistence).
5. Click **Deploy**. The bot starts automatically and runs 24/7.

---

## 🟢 Option 2: Render (Free Tier)

1. Go to [render.com](https://render.com) and sign up.
2. Create a **New Web Service** → Connect your GitHub repo.
3. Set:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Make sure `.session` files are in the repo.
5. Click **Create Web Service**. It will run continuously.

> 💡 For free tier, use a **Background Worker** instead of Web Service to avoid sleeping.

---

## 🟢 Option 3: Heroku

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Push code:
   ```bash
   git add .
   git commit -m "deploy"
   git push heroku main
   ```
5. Heroku reads the `Procfile` and starts `python main.py` automatically.
6. Scale worker: `heroku ps:scale worker=1`

> ⚠️ Heroku free tier no longer exists. Requires paid dyno for 24/7.

---

## 🟢 Option 4: VPS / Dedicated Server (Linux)

### Step 1: Upload files
Use SFTP/SCP or Git to upload the project to your server.

### Step 2: Install dependencies
```bash
cd ~/TM_BOT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Run in background (Screen)
```bash
screen -S tmps_bot
bash start.sh
# Press Ctrl+A then D to detach
```

### Step 4: Or use Systemd (auto-restart on crash)
Create service file:
```bash
sudo nano /etc/systemd/system/tmps-bot.service
```

Paste:
```ini
[Unit]
Description=TMPS Movie Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/TM_BOT
ExecStart=/home/your_username/TM_BOT/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tmps-bot
sudo systemctl start tmps-bot
sudo systemctl status tmps-bot
```

---

## 🟢 Option 5: Local Windows (Run in Background)

### Method A: pythonw (no console window)
```cmd
pythonw main.py
```

### Method B: NSSM (Windows Service)
1. Download [NSSM](https://nssm.cc/download).
2. Open CMD as Administrator:
   ```cmd
   nssm install TMPS_Bot
   ```
3. Set:
   - Path: `C:\Python311\python.exe` (or your Python path)
   - Arguments: `main.py`
   - Startup directory: `D:\TM_BOT`
4. Click **Install service**.
5. Start service: `nssm start TMPS_Bot`

---

## 🧪 Quick Test Locally
```bash
pip install -r requirements.txt
python main.py
```

You should see both bots start successfully.

---

## 📁 Files Added for Deployment
- `main.py` — Unified entry point (runs both bots together)
- `Procfile` — For Railway/Heroku
- `Dockerfile` — For Docker deployments
- `.dockerignore` — Keeps Docker builds small
- `start.sh` — Quick start script for Linux/VPS
- `DEPLOY.md` — This guide

---

Happy Deploying! 🎬🤖

