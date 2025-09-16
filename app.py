"""
KochiMetro DocuTrack - Main Application
A comprehensive document management system for KMRL with OCR, classification, and role-based access
"""
import streamlit as st
import sys
from config import DATA_DIR, UPLOAD_DIR, SAMPLE_USERS
from modules.auth_manager import AuthManager
from modules import database
from pages import dashboard, upload
import plotly.express as px

# App branding
LOGO_PATH = "uploads/carhire.pdf"  # Replace with your logo path or image
APP_NAME = "MetroVivaram"

# Material U CSS styles
login_card_css = '''
<style>
.material-login-card {
max-width: 370px;
margin: 7vh auto 0 auto;
background: var(--material-surface);
border-radius: var(--material-radius);
box-shadow: var(--material-elevation);
padding: 2.5rem 2rem 2rem 2rem;
display: flex;
flex-direction: column;
align-items: center;
}
.material-login-title {
font-size: 1.8rem;
font-weight: 600;
color: var(--material-primary);
margin-bottom: 0.5em;
text-align: center;
letter-spacing: 0.5px;
}
.material-login-desc {
color: #625B71;
font-size: 1.05rem;
margin-bottom: 1.5em;
text-align: center;
}
.material-login-form label {
font-weight: 500;
color: var(--material-primary);
margin-bottom: 0.2em;
}
.material-login-form input {
width: 100%;
margin-bottom: 1.2em;
}
.material-login-btn button {
width: 100%;
font-size: 1.1rem;
margin-top: 0.5em;
}
</style>
<div class="material-login-card">
<div class="material-login-title">MetroVivaram</div>
<div class="material-login-desc">Intelligent Document Management System for KMRL</div>
<div id="login-form-anchor"></div>
</div>
'''

login_card_js = '''
<script>
const anchor = window.parent.document.getElementById('login-form-anchor');
if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
</script>
'''

responsive_css = '''
<style>
@media (max-width: 600px) {
    .main-header, .stApp, .block-container, .stSidebar {
        padding: 0.5em !important;
        font-size: 1.05rem !important;
    }
    .stButton>button, .stTextInput>div>input {
        font-size: 1.1rem !important;
    }
    .stSidebar {
        width: 100vw !important;
    }
}
</style>
'''

# Role-based color themes
ROLE_THEMES = {
    "Engineer": {
        "primary": "#4CAF50",  # Green - Engineering/Technical
        "secondary": "#81C784",
        "accent": "#2E7D32",
        "surface_variant": "#1B3A1D"
    },
    "Finance": {
        "primary": "#FF9800",  # Orange - Finance/Money
        "secondary": "#FFB74D", 
        "accent": "#F57C00",
        "surface_variant": "#2D1F0A"
    },
    "HR": {
        "primary": "#E91E63",  # Pink - HR/People
        "secondary": "#F06292",
        "accent": "#C2185B", 
        "surface_variant": "#2A0E18"
    },
    "Station Controller": {
        "primary": "#2196F3",  # Blue - Operations/Control
        "secondary": "#64B5F6",
        "accent": "#1976D2",
        "surface_variant": "#0D1B2A"
    },
    "Compliance Officer": {
        "primary": "#9C27B0",  # Purple - Compliance/Authority  
        "secondary": "#BA68C8",
        "accent": "#7B1FA2",
        "surface_variant": "#1F0A26"
    }
}

def get_theme_css(user_role=None):
    """Generate CSS with role-specific theme colors"""
    if user_role and user_role in ROLE_THEMES:
        theme = ROLE_THEMES[user_role]
        primary = theme["primary"]
        secondary = theme["secondary"] 
        accent = theme["accent"]
        surface_variant = theme["surface_variant"]
    else:
        # Default theme (purple)
        primary = "#BB86FC"
        secondary = "#03DAC6"
        accent = "#6200EE"
        surface_variant = "#292B32"
    
    return f"""
    <style>
    :root {{
        --material-primary: {primary};
        --material-on-primary: #1C1B1F;
        --material-secondary: {secondary};
        --material-accent: {accent};
        --material-background: #181A20;
        --material-surface: #23242B;
        --material-surface-variant: {surface_variant};
        --material-outline: #79747E;
        --material-error: #CF6679;
        --material-radius: 20px;
        --material-elevation: 0 2px 8px 0 rgba(187,134,252,0.10);
        --material-font: 'Google Sans', 'Roboto', 'Arial', sans-serif;
    }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--material-background) !important;
        font-family: var(--material-font) !important;
        color: #FFFFFF !important;
        font-size: 1.1rem;
        line-height: 1.7;
    }}
    .stApp {{
        background: var(--material-background) !important;
        padding: 0.5rem 0.5rem 2.5rem 0.5rem !important;
        color: #FFFFFF !important;
    }}
    /* Improve text visibility */
    .stMarkdown, .stText, p, span, div {{
        color: #FFFFFF !important;
    }}
    .stDataFrame {{
        background: var(--material-surface) !important;
        border-radius: var(--material-radius) !important;
    }}
    .stDataFrame table {{
        background: var(--material-surface) !important;
        color: #FFFFFF !important;
    }}
    .stDataFrame th {{
        background: var(--material-surface-variant) !important;
        color: var(--material-primary) !important;
        font-weight: 600 !important;
    }}
    .stDataFrame td {{
        background: var(--material-surface) !important;
        color: #FFFFFF !important;
        border-color: var(--material-outline) !important;
    }}
    /* Card, Inputs, Headings, Responsive, etc. */
    .stCard[style*='color:#B3261E'] {{ background: var(--material-surface) !important; color: #FFFFFF !important; }}
    .stCard[style*='color:#006B57'] {{ background: var(--material-surface) !important; color: #FFFFFF !important; }}
    .stCard {{
        background: var(--material-surface) !important;
        border-radius: var(--material-radius) !important;
        padding: 1.5rem !important;
        box-shadow: var(--material-elevation) !important;
        border: 1px solid var(--material-outline) !important;
        color: #FFFFFF !important;
    }}
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {{
        color: var(--material-primary) !important;
        font-weight: 600 !important;
    }}
    .stTextInput > div > input, .stSelectbox > div > div, .stTextArea > div > textarea {{
        background: var(--material-surface) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--material-outline) !important;
        border-radius: 12px !important;
    }}
    .stTextInput > div > input:focus, .stSelectbox > div > div:focus, .stTextArea > div > textarea:focus {{
        border-color: var(--material-primary) !important;
        box-shadow: 0 0 0 1px var(--material-primary) !important;
    }}
    .stButton > button {{
        background: var(--material-primary) !important;
        color: var(--material-on-primary) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        text-shadow: none !important;
    }}
    .stButton > button:hover {{
        background: var(--material-accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    .stButton > button:focus {{
        background: var(--material-primary) !important;
    }}
    .stDownloadButton > button {{
        background: #A374E8 !important;
        color: #FFFFFF !important;
    }}
    .stSidebar {{
        background: var(--material-surface) !important;
        font-family: var(--material-font) !important;
        border-right: 1px solid var(--material-outline) !important;
        box-shadow: 2px 0 8px rgba(0,0,0,0.1) !important;
        position: relative !important;
        min-height: 100vh !important;
    }}
    .stSidebar .stRadio > label {{
        color: #FFFFFF !important;
    }}
    /* Enhanced button styling for navigation */
    .stSidebar .stButton > button {{
        background: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        margin-bottom: 0.3rem !important;
    }}
    .stSidebar .stButton > button:hover {{
        background: var(--material-surface-variant) !important;
        border-color: var(--material-outline) !important;
        transform: translateX(2px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }}
    .stSidebar .stButton > button:focus {{
        background: var(--material-primary) !important;
        color: var(--material-on-primary) !important;
        border-color: var(--material-primary) !important;
    }}
    .stSelectbox > div {{
        background: var(--material-surface) !important;
    }}
    .stSelectbox option {{
        background: var(--material-surface) !important;
        color: #FFFFFF !important;
    }}
    .stNumberInput > div > input {{
        background: var(--material-surface-variant) !important;
        color: #FFFFFF !important;
    }}
    .stDateInput > div > input {{
        background: var(--material-surface) !important;
        color: #FFFFFF !important;
    }}
    .stFileUploader {{
        background: var(--material-surface-variant) !important;
        border-radius: var(--material-radius) !important;
        color: #FFFFFF !important;
    }}
    .stProgress > div > div {{
        background: var(--material-surface-variant) !important;
    }}
    .stProgress > div > div > div {{
        background: var(--material-primary) !important;
    }}
    .stInfo {{
        background: var(--material-surface-variant) !important;
        border-left: 4px solid var(--material-secondary) !important;
        color: #FFFFFF !important;
    }}
    .stSuccess {{
        background: var(--material-surface-variant) !important;
        border-left: 4px solid #4CAF50 !important;
        color: #FFFFFF !important;
    }}
    .stError {{
        background: var(--material-surface-variant) !important;
        border-left: 4px solid var(--material-error) !important;
        color: #FFFFFF !important;
    }}
    @media (max-width: 900px) {{
        section[data-testid="stSidebar"] {{
            margin: 0.5rem 0.2rem;
            padding: 1rem 0.5rem;
            min-width: 120px;
            max-width: 100vw;
        }}
        .stApp {{
            padding: 0.2rem 0.2rem 2.5rem 0.2rem !important;
        }}
        .stCard {{
            padding: 0.7rem !important;
        }}
        /* Mobile navigation adjustments */
        .nav-item {{
            padding: 10px 12px !important;
            font-size: 0.9rem !important;
        }}
        .nav-icon {{
            margin-right: 8px !important;
            font-size: 1.1rem !important;
        }}
    }}
    }}
    @media (max-width: 600px) {{
        .stApp {{
            padding: 0.1rem 0.1rem 2.5rem 0.1rem !important;
        }}
        h1, h2, h3 {{
            font-size: 1.2rem !important;
        }}
        .stCard {{
            font-size: 0.98rem !important;
        }}
        section[data-testid="stSidebar"] {{
            padding: 0.5rem 0.2rem;
        }}
    }}
    </style>
    """

# Inject the theme CSS into the app
def apply_theme(user_role=None):
    """Apply the theme CSS based on user role"""
    st.markdown(get_theme_css(user_role), unsafe_allow_html=True)

# --- Audit Log Page (Material U style) ---
def show_audit_page(user_info=None):
    st.markdown("""
    <div class="main-header" style="background: var(--material-surface); padding: 1.5rem; border-radius: var(--material-radius); margin-bottom: 1rem; border: 1px solid var(--material-outline);">
        <h2 style="color: var(--material-primary); margin-bottom: 0.5rem;">📝 Audit Log</h2>
        <p style="color: #FFFFFF; margin: 0;">Recent user activity and document access logs</p>
    </div>
    """, unsafe_allow_html=True)
    db = database.DocumentDatabase()
    audit_log = db.get_audit_log(limit=100)
    if audit_log:
        table = []
        for e in reversed(audit_log):
            table.append({
                'Action': e.get('action', ''),
                'User': e.get('user_name', ''),
                'Role': e.get('user_role', ''),
                'Doc ID': e.get('document_id', 'N/A'),
                'Details': e.get('details', '')
            })
        st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.info("No log entries found.")

def show_analytics_page(user_info):
    """Enhanced analytics and statistics page"""
    st.markdown("""
    <div class="main-header" style="background: var(--material-surface); padding: 1.5rem; border-radius: var(--material-radius); margin-bottom: 1rem; border: 1px solid var(--material-outline);">
        <h2 style="color: var(--material-primary); margin-bottom: 0.5rem;">📊 Analytics Dashboard</h2>
        <p style="color: #FFFFFF; margin: 0;">Comprehensive insights and document statistics</p>
    </div>
    """, unsafe_allow_html=True)
    db = database.DocumentDatabase()
    stats = db.get_statistics()
    # Enhanced metrics display
    st.subheader("📈 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Documents", stats['total_documents'], delta=None)
    with col2:
        st.metric("📂 Document Types", len(stats['documents_by_type']), delta=None)
    with col3:
        st.metric("📅 Recent Uploads", stats['recent_uploads'], delta=None)
    with col4:
        high_priority = stats['documents_by_priority'].get('High', 0)
        st.metric("⚠️ High Priority", high_priority, delta=None)
    if stats['total_documents'] > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Document Types Distribution")
            type_data = stats['documents_by_type']
            if type_data:
                fig = px.bar(
                    x=list(type_data.keys()),
                    y=list(type_data.values()),
                    title="Documents by Type",
                    color=list(type_data.values()),
                    color_continuous_scale="Blues"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("⚠️ Priority Breakdown")
            priority_data = stats['documents_by_priority']
            if priority_data:
                colors = {'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
                fig = px.pie(
                    values=list(priority_data.values()),
                    names=list(priority_data.keys()),
                    title="Priority Distribution",
                    color=list(priority_data.keys()),
                    color_discrete_map=colors
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig, use_container_width=True)

def show_demo_access_screen():
    """Demo access control screen"""
    st.markdown("""
        <style>
        .demo-access-card {
            max-width: 400px;
            margin: 10vh auto 0 auto;
            background: var(--material-surface);
            border-radius: var(--material-radius);
            box-shadow: var(--material-elevation);
            padding: 3rem 2rem;
            text-align: center;
        }
        .demo-title {
            font-size: 2rem;
            font-weight: 600;
            color: var(--material-primary);
            margin-bottom: 1rem;
        }
        .demo-subtitle {
            color: #625B71;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        </style>
        <div class="demo-access-card">
            <div class="demo-title">🚀 MetroVivaram Demo</div>
            <div class="demo-subtitle">Enter the demo access code to continue</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("demo_access_form"):
        access_code = st.text_input("Demo Access Code", type="password", placeholder="Enter access code...")
        submit = st.form_submit_button("Access Demo", use_container_width=True)
        
        if submit:
            # Change this to your preferred demo access code
            if access_code == "METRO2025":
                st.session_state.demo_access_granted = True
                st.success("✅ Access granted! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid access code. Please contact the demo organizer.")
    
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #625B71; font-size: 0.9rem;">
            <p>This is a demonstration of KMRL's Document Management System</p>
            <p>Contact: <a href="mailto:demo@metrovivaram.com" style="color: var(--material-primary);">demo@metrovivaram.com</a></p>
        </div>
    """, unsafe_allow_html=True)

def main():
    try:
        # Demo access control - uncomment to enable
        if 'demo_access_granted' not in st.session_state:
            st.session_state.demo_access_granted = False
        
        # Demo access screen (enable this for controlled demo access)
        # if not st.session_state.demo_access_granted:
        #     show_demo_access_screen()
        #     return
        
        auth_manager = AuthManager()
        
        # Material U Login Page
        if not auth_manager.is_authenticated():
            # Apply default theme for login page
            apply_theme()
            
            st.markdown(login_card_css, unsafe_allow_html=True)
            st.markdown(login_card_js, unsafe_allow_html=True)
            
            # Use a container to keep form inside the card
            with st.container():
                st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                auth_manager.login_form()
                st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Get current user
        user_info = auth_manager.get_current_user()
        
        # Apply role-specific theme
        apply_theme(user_info['role'])
        
        # Responsive CSS for mobile-friendliness
        st.markdown(responsive_css, unsafe_allow_html=True)
        
        # Modern Material U Navigation Sidebar
        with st.sidebar:
            # User Profile Card
            st.markdown(f"""
                <div style='
                    background: var(--material-surface-variant);
                    border-radius: 16px;
                    padding: 1.2rem;
                    margin-bottom: 1.5rem;
                    border: 1px solid var(--material-outline);
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
                '>
                    <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                        <div style='
                            background: var(--material-primary);
                            color: var(--material-on-primary);
                            width: 48px;
                            height: 48px;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: 600;
                            font-size: 1.2rem;
                            margin-right: 0.8rem;
                        '>
                            {user_info['name'][0].upper()}
                        </div>
                        <div>
                            <div style='font-size:1.1rem; font-weight:600; color:#FFFFFF; margin-bottom:0.2rem;'>
                                {user_info['name']}
                            </div>
                            <div style='font-size:0.85rem; color:var(--material-primary); font-weight:500;'>
                                {user_info['role']}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation Menu with Material U styling
            st.markdown("""
                <style>
                .nav-item {
                    display: flex;
                    align-items: center;
                    padding: 12px 16px;
                    margin: 4px 0;
                    border-radius: 12px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-decoration: none;
                    color: #FFFFFF;
                    font-weight: 500;
                    font-size: 0.95rem;
                    background: transparent;
                    border: none;
                    width: 100%;
                }
                .nav-item:hover {
                    background: var(--material-surface-variant);
                    transform: translateX(4px);
                }
                .nav-item.active {
                    background: var(--material-primary);
                    color: var(--material-on-primary);
                    font-weight: 600;
                }
                .nav-icon {
                    margin-right: 12px;
                    font-size: 1.2rem;
                    width: 24px;
                    text-align: center;
                }
                .nav-container {
                    margin-bottom: 1.5rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Initialize session state for navigation
            if 'current_page' not in st.session_state:
                st.session_state.current_page = "Dashboard"
            
            # Navigation items with icons
            nav_items = [
                {"name": "Dashboard", "icon": "📊", "label": "Dashboard"},
                {"name": "Upload", "icon": "📤", "label": "Upload Documents"},
                {"name": "Audit Log", "icon": "📝", "label": "Audit Log"}
            ]
            
            st.markdown('<div class="nav-container">', unsafe_allow_html=True)
            
            for item in nav_items:
                active_class = "active" if st.session_state.current_page == item["name"] else ""
                
                if st.button(
                    f"{item['icon']} {item['label']}", 
                    key=f"nav_{item['name']}", 
                    help=f"Navigate to {item['label']}",
                    use_container_width=True
                ):
                    st.session_state.current_page = item["name"]
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Divider
            st.markdown("""
                <div style='
                    height: 1px;
                    background: linear-gradient(90deg, transparent, var(--material-outline), transparent);
                    margin: 1.5rem 0;
                '>
                </div>
            """, unsafe_allow_html=True)
            
            # Enhanced Logout Button
            st.markdown("""
                <style>
                .logout-btn {
                    background: linear-gradient(135deg, #ff4444, #cc3333) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 12px !important;
                    padding: 12px 20px !important;
                    font-weight: 600 !important;
                    font-size: 0.95rem !important;
                    width: 100% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    transition: all 0.2s ease !important;
                    box-shadow: 0 2px 8px rgba(255, 68, 68, 0.3) !important;
                }
                .logout-btn:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 4px 12px rgba(255, 68, 68, 0.4) !important;
                    background: linear-gradient(135deg, #ff5555, #dd4444) !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", key="logout_btn", help="Sign out of your account", use_container_width=True):
                auth_manager.logout()
            
            # Set the page variable based on session state
            page = st.session_state.current_page
        
        # PWA install prompt banner (informational)
        st.markdown("""
            <div style='position:fixed;bottom:0;left:0;width:100vw;background:var(--material-primary);color:#1C1B1F;padding:0.7em 1em;text-align:center;z-index:9999;font-weight:600;'>
                <b>💡 Tip:</b> For a better experience, add MetroVivaram to your home screen or install as a PWA from your browser menu.
            </div>
        """, unsafe_allow_html=True)
        
        # Breadcrumb Navigation
        page_icons = {
            "Dashboard": "📊",
            "Upload": "📤", 
            "Audit Log": "📝"
        }
        
        st.markdown(f"""
            <div style='
                background: var(--material-surface);
                border-radius: 12px;
                padding: 0.8rem 1.2rem;
                margin-bottom: 1.5rem;
                border: 1px solid var(--material-outline);
                display: flex;
                align-items: center;
                justify-content: space-between;
            '>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 1.4rem; margin-right: 0.5rem;'>{page_icons.get(page, "📄")}</span>
                    <div>
                        <div style='font-size: 0.75rem; color: var(--material-primary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;'>
                            Current Page
                        </div>
                        <div style='font-size: 1.1rem; color: #FFFFFF; font-weight: 600; margin-top: 0.1rem;'>
                            {page}
                        </div>
                    </div>
                </div>
                <div style='
                    background: var(--material-primary);
                    color: var(--material-on-primary);
                    padding: 0.4rem 0.8rem;
                    border-radius: 8px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                '>
                    {user_info['role']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Main content area
        if page == "Dashboard":
            dashboard.show_dashboard_page(user_info)
        elif page == "Upload":
            upload.show_upload_page(user_info)
        elif page == "Audit Log":
            show_audit_page(user_info)
            
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main()