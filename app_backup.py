"""
KochiMetro DocuTrack - Main Application
A comprehensive document management system for KMRL with OCR, classification, and role-based access
"""
login_card_css = """
<style>
.material-login-card {
    max-width: 370px;
    """
    KochiMetro DocuTrack - Main Application
    A comprehensive document management system for KMRL with OCR, classification, and role-based access
    """
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
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--material-primary);
    margin-bottom: 0.2em;
    text-align: center;
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
    background: var(--material-surface);
    border-radius: var(--material-radius);
    box-shadow: var(--material-elevation);
    padding: 2.5rem 2rem 2rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.material-login-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--material-primary);
    margin-bottom: 0.2em;
    text-align: center;
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
""",
                unsafe_allow_html=True,
            )
            # Render login form inside the card using anchor
            st.markdown(
                """
<script>
const anchor = window.parent.document.getElementById('login-form-anchor');
if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
</script>
""",
                unsafe_allow_html=True,
            )
            # Use a container to keep form inside the card
            with st.container():
                st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                auth_manager.login_form()
                st.markdown('</div>', unsafe_allow_html=True)
            return
        # Get current user
        if not auth_manager.is_authenticated():
            # All HTML/CSS/JS multi-line strings must be at column 0
            login_card_css = """
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
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--material-primary);
    margin-bottom: 0.2em;
    text-align: center;
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
<div class=\"material-login-card\">
    <div class=\"material-login-title\">MetroVivaram</div>
    <div class=\"material-login-desc\">Intelligent Document Management System for KMRL</div>
    <div id=\"login-form-anchor\"></div>
</div>
"""
            login_card_js = """
<script>
const anchor = window.parent.document.getElementById('login-form-anchor');
if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
</script>
"""
            st.markdown(login_card_css, unsafe_allow_html=True)
            st.markdown(login_card_js, unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                auth_manager.login_form()
                st.markdown('</div>', unsafe_allow_html=True)
            return
                ),
                unsafe_allow_html=True,
            )
            # Render login form inside the card using anchor
            st.markdown(
                (
"""
<script>
const anchor = window.parent.document.getElementById('login-form-anchor');
if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
</script>
"""
                ),
                unsafe_allow_html=True,
            )
            # Use a container to keep form inside the card
            with st.container():
                st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                auth_manager.login_form()
                st.markdown('</div>', unsafe_allow_html=True)
            return
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main()
                        }
                        </style>
                        <div class="material-login-card">
                            <div class="material-login-title">MetroVivaram</div>
                            <div class="material-login-desc">Intelligent Document Management System for KMRL</div>
                            <div id="login-form-anchor"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        # Render login form inside the card using anchor
                        st.markdown("""
                        <script>
                        const anchor = window.parent.document.getElementById('login-form-anchor');
                        if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
                        </script>
                        """, unsafe_allow_html=True)
                        # Use a container to keep form inside the card
                        with st.container():
                            st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                            auth_manager.login_form()
                            st.markdown('</div>', unsafe_allow_html=True)
                        return
                    # Get current user
                    user_info = auth_manager.get_current_user()
                    # Responsive CSS for mobile-friendliness
                    st.markdown("""
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
                    """, unsafe_allow_html=True)
                    # Google Material Design inspired sidebar navigation
                    with st.sidebar:
                        st.markdown("""
                            <div style='padding:0.5em 0 1.5em 0;'>
                                <span style='font-size:1.3rem;font-weight:600;color:#1a73e8;'>{}</span><br>
                                <span style='font-size:0.95rem;color:#5f6368;'>{}</span>
                            </div>
                        """.format(user_info['name'], user_info['role']), unsafe_allow_html=True)
                        page = st.radio(
                            "",
                            ["Dashboard", "Upload", "Audit Log"],
                            key="navigation",
                            label_visibility="collapsed",
                            horizontal=False
                        )
                        st.markdown("<hr style='margin:1.5em 0 1em 0;border:0;border-top:1px solid #e0e0e0;'>", unsafe_allow_html=True)
                        # Prominent Logout Button
                        if st.button("Logout", key="logout_btn", help="Sign out of your account"):
                            auth_manager.logout()
                    # PWA install prompt banner (informational)
                    st.markdown("""
                        <div style='position:fixed;bottom:0;left:0;width:100vw;background:#1a73e8;color:#fff;padding:0.7em 1em;text-align:center;z-index:9999;'>
                            <b>Tip:</b> For a better experience, add MetroVivaram to your home screen or install as a PWA from your browser menu.
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
        """, unsafe_allow_html=True)


        # Material U Login Page
        if not auth_manager.is_authenticated():
            st.markdown("""
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
                font-size: 2.1rem;
                font-weight: 700;
                color: var(--material-primary);
                margin-bottom: 0.2em;
                text-align: center;
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
            """, unsafe_allow_html=True)
            # Render login form inside the card using anchor
            st.markdown("""
            <script>
            const anchor = window.parent.document.getElementById('login-form-anchor');
            if (anchor) anchor.scrollIntoView({behavior: 'smooth'});
            </script>
            """, unsafe_allow_html=True)
            # Use a container to keep form inside the card
            with st.container():
                st.markdown('<div class="material-login-form">', unsafe_allow_html=True)
                auth_manager.login_form()
                st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Get current user
        user_info = auth_manager.get_current_user()
        
        # Responsive CSS for mobile-friendliness
        st.markdown("""
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
        """, unsafe_allow_html=True)
        # Google Material Design inspired sidebar navigation
        with st.sidebar:
            st.markdown("""
                <div style='padding:0.5em 0 1.5em 0;'>
                    <span style='font-size:1.3rem;font-weight:600;color:#1a73e8;'>{}</span><br>
                    <span style='font-size:0.95rem;color:#5f6368;'>{}</span>
                </div>
            """.format(user_info['name'], user_info['role']), unsafe_allow_html=True)
            page = st.radio(
                "",
                ["Dashboard", "Upload", "Audit Log"],
                key="navigation",
                label_visibility="collapsed",
                horizontal=False
            )
            st.markdown("<hr style='margin:1.5em 0 1em 0;border:0;border-top:1px solid #e0e0e0;'>", unsafe_allow_html=True)
            # Prominent Logout Button
            if st.button("Logout", key="logout_btn", help="Sign out of your account"):
                auth_manager.logout()
            st.markdown("""
                <style>
                .stButton>button#logout_btn {
                    background: #ea4335;
                    color: #fff;
                    font-weight: 600;
                    border-radius: 8px;
                    padding: 0.6em 1.5em;
                    margin-top: 0.5em;
                    box-shadow: 0 2px 8px rgba(60,64,67,.08);
                    try:
                        auth_manager = AuthManager()
                        # Material U Login Page
                        if not auth_manager.is_authenticated():
                            st.markdown((
                                """
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
                    font-size: 2.1rem;
                    font-weight: 700;
                    color: var(--material-primary);
                    margin-bottom: 0.2em;
                    text-align: center;
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
                """
                            ), unsafe_allow_html=True)
                            # Render login form inside the card using anchor
                            responsive_css = """
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
                    """
                            st.markdown(responsive_css, unsafe_allow_html=True)
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
                """
                        ), unsafe_allow_html=True)
                        # Google Material Design inspired sidebar navigation
                        with st.sidebar:
                            st.markdown((
                                f"""
                <div style='padding:0.5em 0 1.5em 0;'>
                    <span style='font-size:1.3rem;font-weight:600;color:#1a73e8;'>{user_info['name']}</span><br>
                    <span style='font-size:0.95rem;color:#5f6368;'>{user_info['role']}</span>
                </div>
                """
                            ), unsafe_allow_html=True)
                            page = st.radio(
                                "",
                                ["Dashboard", "Upload", "Audit Log"],
                                key="navigation",
                                label_visibility="collapsed",
                                horizontal=False
                            )
                            st.markdown("<hr style='margin:1.5em 0 1em 0;border:0;border-top:1px solid #e0e0e0;'>", unsafe_allow_html=True)
                            # Prominent Logout Button
                            if st.button("Logout", key="logout_btn", help="Sign out of your account"):
                                auth_manager.logout()
                        # PWA install prompt banner (informational)
                        st.markdown((
                            """
                <div style='position:fixed;bottom:0;left:0;width:100vw;background:#1a73e8;color:#fff;padding:0.7em 1em;text-align:center;z-index:9999;'>
                    <b>Tip:</b> For a better experience, add MetroVivaram to your home screen or install as a PWA from your browser menu.
                </div>
                """
                        ), unsafe_allow_html=True)
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