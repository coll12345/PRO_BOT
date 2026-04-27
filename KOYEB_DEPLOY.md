# 🚀 KOYEB DEPLOYMENT GUIDE - TMPS Movie Bot

## ✅ Bot Status: READY FOR DEPLOYMENT

Your bot is now in **BOT-ONLY MODE** optimized for Koyeb:
- ✅ Non-interactive (no phone prompts)
- ✅ HTTP health check on port 8000 (keeps it alive)
- ✅ 24/7 operation without database locks
- ✅ Responds to all Telegram commands

---

## 📋 DEPLOYMENT STEPS

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "TMPS Movie Bot - Ready for Koyeb"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tm_bot.git
git push -u origin main
```

### Step 2: Create `Procfile` (Already exists)
Verify it contains:
```
worker: python main.py
```

### Step 3: Create `.env` File (Optional)
```
BOT_ONLY_MODE=true
PORT=8000
```

### Step 4: Deploy to Koyeb

**Via Koyeb Dashboard:**

1. Go to https://app.koyeb.com
2. Click **"Create Service"**
3. Choose **"GitHub"** as source
4. Connect your GitHub account
5. Select repository: `tm_bot`
6. Set deployment settings:
   - **Name:** `tmps-movie-bot`
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `python main.py`
   - **Port:** `8000`

7. Set **Environment Variables:**
   - `BOT_ONLY_MODE` = `true`

8. Click **"Deploy"**

---

## 🔍 KOYEB CONFIGURATION

### Health Check Setup
- **Type:** HTTP
- **URL:** `http://localhost:8000/`
- **Expected Response:** `200 OK`
- **Interval:** 30 seconds

### Port Configuration
- **Port:** 8000
- **Protocol:** HTTP

### Resources
- **Memory:** 256MB (minimum, free tier)
- **CPU:** Shared

---

## ✅ VERIFICATION

### After Deployment:

1. **Check Logs:**
   ```
   View logs in Koyeb dashboard
   You should see:
   🌐 HTTP Health Check Server started on port 8000
   📱 Starting Bot Client...
   ✅ Bot started: @TMPS_Movie_bot
   ✅ BOT READY!
   ```

2. **Test Bot on Telegram:**
   - Message bot with `/start`
   - Bot should respond with greeting menu
   - Try searching for movies
   - Test buttons (Earn Money, About, Premium)

3. **Monitor Health:**
   - Go to Koyeb dashboard
   - Check "Health" tab
   - Should show ✅ **Healthy**

---

## 🛠️ TROUBLESHOOTING

### Bot shows as "Unhealthy" on Koyeb

**Solution:** Check that:
- Port 8000 is not blocked
- HTTP server is starting (check logs)
- Bot is actually connecting to Telegram

### Bot stops after 30 minutes

**Reason:** Free tier auto-suspends inactive services  
**Solution:** 
- Upgrade to paid plan, OR
- Keep bot active by having users interact with it regularly

### "database is locked" error

**Already Fixed!** The bot-only mode avoids userbot session conflicts.

---

## 📦 FILES NEEDED ON KOYEB

Make sure these files are in your GitHub repo:
```
✅ main.py           (Updated for bot-only mode)
✅ bot.py            (Telegram bot handlers)
✅ userbot.py        (Not used, but optional)
✅ requirements.txt  (Dependencies)
✅ Procfile          (Koyeb startup command)
✅ plugins/          (Command handlers)
✅ poster.jpg        (Bot greeting image)
```

---

## 🔑 ENVIRONMENT VARIABLES FOR KOYEB

Set these in Koyeb dashboard under "Environment Variables":

```
BOT_ONLY_MODE=true
```

Optional (for future enhancement):
```
MONGO_URI=your_mongodb_connection
API_ID=30393136
API_HASH=4b2a23c681028e19cba2f63155e00f31
```

---

## 💡 IMPORTANT NOTES

1. **BOT_TOKEN** is already in `bot.py` - no need to expose it in env vars
2. **poster.jpg** must be in the same directory as Procfile
3. **Free tier:** One dyno that auto-stops after 30 min of inactivity
4. **Paid tier:** Continuous operation

---

## 🎯 DEPLOYMENT CHECKLIST

- [ ] All files committed to GitHub
- [ ] `Procfile` exists and contains `worker: python main.py`
- [ ] `requirements.txt` has all dependencies
- [ ] GitHub repo is public (or Koyeb has access)
- [ ] Koyeb Health Check configured to `http://localhost:8000/`
- [ ] Bot responds with "🤖 TMPS Movie Bot is running!"
- [ ] Tested `/start` command on Telegram
- [ ] Monitored logs in Koyeb dashboard

---

## 🚀 GO LIVE!

Once deployed, your bot will:
- ✅ Run 24/7 on Koyeb
- ✅ Respond instantly to Telegram users
- ✅ Auto-restart on crashes
- ✅ Use HTTP health checks to stay alive

**Questions?** Check Koyeb logs for detailed error messages!
