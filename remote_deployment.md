# Quick Remote Deployment Guide

## Option 1: Streamlit Community Cloud (FREE)

### Step 1: Create GitHub Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "MetroVivaram Document Management System"
git branch -M main

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOURUSERNAME/KochiMetro_DocuTrack.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `KochiMetro_DocuTrack`
5. Main file path: `app.py`
6. Click "Deploy!"

### Step 3: Get Your Public URL
You'll get a URL like: 
`https://yourusername-kochimetro-docutrack-app-abc123.streamlit.app/`

**This URL works from anywhere in the world!**

---

## Option 2: ngrok (Instant Tunnel)

If you want to quickly tunnel your local app:

### Install ngrok:
```bash
# Install ngrok
brew install ngrok/ngrok/ngrok

# Or download from: https://ngrok.com/download
```

### Usage:
```bash
# Terminal 1: Run your app
source .venv/bin/activate
streamlit run app.py

# Terminal 2: Create tunnel
ngrok http 8501
```

You'll get a public URL like: `https://abc123.ngrok.io`

---

## Option 3: Railway (Alternative Cloud)

1. Go to https://railway.app/
2. Connect GitHub
3. Deploy from your repository
4. Get public URL

---

## Which option do you prefer?

**Streamlit Cloud** is the best for permanent demos and sharing.
**ngrok** is best for quick testing and temporary access.