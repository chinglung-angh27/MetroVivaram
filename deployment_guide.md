# MetroVivaram Demo Deployment Guide

## Option 1: Streamlit Community Cloud (Recommended - FREE)

### Steps:
1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/KochiMetro_DocuTrack.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Share the URL:**
   - You'll get a URL like: `https://yourusername-kochimetro-docutrack-app-xyz123.streamlit.app/`
   - Share this URL with your demo attendees

### Benefits:
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy to share (just send URL)
- ✅ Auto-updates when you push to GitHub
- ✅ Works on all devices (mobile/desktop)

---

## Option 2: Local Network Sharing

### Make your local app accessible to others on the same network:

1. **Find your local IP:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Run with network access:**
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

3. **Share the URL:**
   - Others can access via: `http://YOUR_IP_ADDRESS:8501`
   - Example: `http://192.168.1.100:8501`

### Benefits:
- ✅ No setup required
- ✅ Full control
- ❌ Only works on same network
- ❌ Requires your computer to stay on

---

## Option 3: Cloud VPS Deployment

### For more professional hosting:

1. **Get a VPS** (DigitalOcean, AWS, etc.)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install streamlit
   ```

3. **Upload your app and run:**
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

### Benefits:
- ✅ Professional domain
- ✅ Always online
- ✅ Custom SSL certificates
- ❌ Costs money
- ❌ Requires server management

---

## Option 4: Add Demo Access Control

### Add a simple demo access code to your existing app:
- I can add a "Demo Access Code" screen before login
- Give the code only to your demo attendees
- Easy to implement and control access

## Demo Tips:

### For Your Presentation:
1. **Prepare Demo Accounts:**
   - engineer1 / eng123
   - finance1 / fin123
   - hr1 / hr123
   - station1 / sta123
   - compliance1 / comp123

2. **Demo Script:**
   - Show login with different roles
   - Upload a sample document
   - Demonstrate OCR extraction
   - Show document classification
   - Display analytics dashboard
   - Test search and filters
   - Show summarization feature

3. **Mobile Demo:**
   - The app is responsive
   - Works great on tablets/phones
   - Perfect for on-the-go demos

### Data for Demo:
- You already have 18+ realistic documents
- All features are working
- Analytics show meaningful data

## Which Option Do You Prefer?

Let me know which deployment method you'd like to use, and I'll help you set it up!