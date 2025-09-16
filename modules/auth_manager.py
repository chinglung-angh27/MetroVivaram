"""
Simple authentication manager for user login and role management
"""
import streamlit as st
from config import SAMPLE_USERS

class AuthManager:
    def __init__(self):
        self.users = SAMPLE_USERS
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        if username in self.users:
            user_data = self.users[username]
            if user_data["password"] == password:
                return {
                    "username": username,
                    "name": user_data["name"],
                    "role": user_data["role"],
                    "authenticated": True
                }
        return None
    
    def login_form(self):
        """Display login form with Material U design"""
        st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;margin-top:3em;'>
                <div style='font-size:1.15rem;color:#444;margin-bottom:2.5em;'>Sign in to access your account</div>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<div style='display:flex;flex-direction:column;align-items:center;'>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Sign In")
            st.markdown("</div>", unsafe_allow_html=True)
        if submit_button:
            user_info = self.authenticate_user(username, password)
            if user_info:
                st.session_state.user_info = user_info
                st.success(f"Welcome, {user_info['name']} ({user_info['role']})")
                st.rerun()
            else:
                st.error("Invalid username or password")
        # Material U style demo accounts (optional, can be removed for production)
        st.markdown("""
            <div style='margin-top:2.5em;text-align:center;color:#888;font-size:0.98rem;'>
                <b>Demo Accounts</b><br>
                Engineer: <code>engineer1</code> / <code>eng123</code> &nbsp;|&nbsp;
                Finance: <code>finance1</code> / <code>fin123</code> &nbsp;|&nbsp;
                HR: <code>hr1</code> / <code>hr123</code> &nbsp;|&nbsp;
                Station: <code>station1</code> / <code>sta123</code> &nbsp;|&nbsp;
                Compliance: <code>compliance1</code> / <code>comp123</code>
            </div>
            <style>
            .stTextInput>div>input {
                border-radius: 8px;
                border: 1.5px solid #e0e0e0;
                padding: 0.7em 1em;
                font-size: 1.08rem;
                background: #fafbfc;
                margin-bottom: 1.1em;
            }
            .stButton>button {
                background: #1a73e8;
                color: #fff;
                font-weight: 600;
                border-radius: 8px;
                padding: 0.7em 2.2em;
                font-size: 1.08rem;
                margin-top: 0.5em;
                box-shadow: 0 2px 8px rgba(60,64,67,.08);
                border: none;
                transition: background 0.2s;
            }
            .stButton>button:hover {
                background: #1765c1;
            }
            </style>
        """, unsafe_allow_html=True)
        return False
    
    def logout(self):
        """Logout current user"""
        if "user_info" in st.session_state:
            del st.session_state.user_info
        st.rerun()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return "user_info" in st.session_state and st.session_state.user_info.get("authenticated", False)
    
    def get_current_user(self):
        """Get current user information"""
        return st.session_state.get("user_info", None)
    
    def require_auth(self):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            return self.login_form()
        return True