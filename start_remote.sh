#!/bin/bash

echo "🌐 MetroVivaram Remote Access Setup"
echo "=================================="

echo ""
echo "🚀 Starting your app for remote access..."
echo ""

# Start Streamlit in background
echo "Starting Streamlit app..."
source .venv/bin/activate
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
STREAMLIT_PID=$!

# Wait a moment for Streamlit to start
echo "Waiting for app to start..."
sleep 5

# Check if Streamlit is running
if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✅ Streamlit app is running on port 8501"
else
    echo "❌ Failed to start Streamlit app"
    exit 1
fi

echo ""
echo "🔗 Creating public tunnel with ngrok..."
echo ""

# Start ngrok
echo "Starting ngrok tunnel..."
ngrok http 8501

# When ngrok is stopped, clean up
echo ""
echo "🧹 Cleaning up..."
kill $STREAMLIT_PID 2>/dev/null
echo "✅ Stopped Streamlit app"