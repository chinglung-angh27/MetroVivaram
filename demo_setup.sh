#!/bin/bash

# MetroVivaram Demo Deployment Script

echo "🚀 MetroVivaram Demo Setup"
echo "=========================="

echo "Choose deployment option:"
echo "1) Local Network Sharing (same WiFi)"
echo "2) Streamlit Cloud Setup (GitHub required)"
echo "3) Add Demo Access Control"
echo "4) Show current demo accounts"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "📡 Setting up local network sharing..."
        echo "Your app will be accessible to anyone on the same WiFi network"
        
        # Get local IP
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
        echo "Your local IP: $LOCAL_IP"
        
        echo "Starting Streamlit with network access..."
        echo "Share this URL with demo attendees: http://$LOCAL_IP:8501"
        echo "Press Ctrl+C to stop the server"
        echo ""
        
        source .venv/bin/activate
        streamlit run app.py --server.address 0.0.0.0 --server.port 8501
        ;;
        
    2)
        echo "☁️ Streamlit Cloud Setup"
        echo "Follow these steps:"
        echo ""
        echo "1. Create GitHub repository:"
        echo "   git init"
        echo "   git add ."
        echo "   git commit -m 'MetroVivaram Demo'"
        echo "   git branch -M main"
        echo "   git remote add origin YOUR_GITHUB_URL"
        echo "   git push -u origin main"
        echo ""
        echo "2. Go to https://share.streamlit.io/"
        echo "3. Connect your GitHub account"
        echo "4. Deploy this repository"
        echo "5. Share the generated URL"
        ;;
        
    3)
        echo "🔒 Adding Demo Access Control..."
        
        # Enable demo access in app.py
        sed -i.bak 's/# if not st.session_state.demo_access_granted:/if not st.session_state.demo_access_granted:/' app.py
        sed -i.bak 's/#     show_demo_access_screen()/    show_demo_access_screen()/' app.py
        sed -i.bak 's/#     return/    return/' app.py
        
        echo "✅ Demo access control enabled!"
        echo "Access code: METRO2025"
        echo "Share this code with your demo attendees"
        echo ""
        echo "To disable later, edit app.py and comment out the demo access lines"
        ;;
        
    4)
        echo "👥 Demo Accounts Available:"
        echo ""
        echo "Engineer Account:"
        echo "  Username: engineer1"
        echo "  Password: eng123"
        echo "  Role: Can view technical documents, safety notices"
        echo ""
        echo "Finance Account:"
        echo "  Username: finance1"
        echo "  Password: fin123"
        echo "  Role: Can view invoices, financial documents"
        echo ""
        echo "HR Account:"
        echo "  Username: hr1"
        echo "  Password: hr123"
        echo "  Role: Can view HR policies, employee documents"
        echo ""
        echo "Station Controller:"
        echo "  Username: station1"
        echo "  Password: sta123"
        echo "  Role: Can view operational reports, safety notices"
        echo ""
        echo "Compliance Officer:"
        echo "  Username: compliance1"
        echo "  Password: comp123"
        echo "  Role: Can view all compliance documents"
        echo ""
        echo "✨ All accounts now have universal access to all features!"
        ;;
        
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac