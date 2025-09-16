#!/bin/bash

echo "🚀 MetroVivaram - Permanent Deployment Setup"
echo "============================================="

echo ""
echo "This will help you deploy MetroVivaram to Streamlit Cloud for permanent remote access."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Checking project files..."

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
else
    echo "❌ requirements.txt missing"
    exit 1
fi

# Check app.py
if [ -f "app.py" ]; then
    echo "✅ app.py exists"
else
    echo "❌ app.py missing"
    exit 1
fi

# Check .streamlit/config.toml
if [ -f ".streamlit/config.toml" ]; then
    echo "✅ Streamlit config exists"
else
    echo "❌ Streamlit config missing"
fi

echo ""
echo "📝 Preparing for deployment..."

# Add all files to git
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No new changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "MetroVivaram Document Management System - Ready for deployment"
    echo "✅ Changes committed"
fi

echo ""
echo "🌐 Next Steps for Permanent Deployment:"
echo ""
echo "1. Create GitHub Repository:"
echo "   - Go to https://github.com"
echo "   - Click 'New repository'"
echo "   - Name: MetroVivaram-DocuTrack"
echo "   - Make it Public"
echo "   - Don't initialize with README"
echo "   - Click 'Create repository'"
echo ""
echo "2. Push to GitHub:"
echo "   Copy and run these commands:"
echo "   git remote add origin https://github.com/YOURUSERNAME/MetroVivaram-DocuTrack.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io/"
echo "   - Sign in with GitHub"
echo "   - Click 'New app'"
echo "   - Select your repository"
echo "   - Main file: app.py"
echo "   - Click 'Deploy!'"
echo ""
echo "4. Get Your Permanent URL:"
echo "   - You'll get: https://yourusername-metrovivaram-docutrack-app-xyz123.streamlit.app/"
echo "   - This URL works forever from anywhere!"
echo ""
echo "📱 Demo Accounts for Testing:"
echo "   - engineer1 / eng123"
echo "   - finance1 / fin123"
echo "   - hr1 / hr123"
echo "   - station1 / sta123"
echo "   - compliance1 / comp123"
echo ""
echo "🎯 Your app is mobile-optimized and ready for demos!"

echo ""
read -p "Press Enter to continue or Ctrl+C to exit..."

echo ""
echo "💡 Pro Tips:"
echo "- Your app will auto-update when you push changes to GitHub"
echo "- The URL will work on all devices (phone, tablet, desktop)"
echo "- It's completely free with no time limits"
echo "- Perfect for sharing with clients and stakeholders"
echo ""
echo "🚀 Ready to deploy! Follow the steps above."