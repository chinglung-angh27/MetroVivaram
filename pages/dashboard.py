"""
Enhanced role-based dashboard page with improved UI
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.database import DocumentDatabase
from modules.alert_manager import send_feedback_alert
from config import USER_ROLES
from datetime import datetime, timedelta

def show_dashboard_page(user_info):
    # Role-based welcome message
    user_role = user_info.get('role', '') if user_info else ''
    user_name = user_info.get('name', 'User') if user_info else 'User'
    management_roles = ["HR", "Compliance Officer"]
    
    if user_role in management_roles:
        role_indicator = "🔒 Management Access"
        role_color = "#FF9800"
    else:
        role_indicator = "👥 User Access"
        role_color = "#2196F3"
    
    # Modern Material Design Header
    st.markdown(f"""
    <div class="material-page-header" style="margin-bottom:2rem;padding:1.5rem 0;border-bottom:1px solid var(--material-outline);">
        <h1 style="color:var(--material-primary);font-weight:700;font-size:2rem;margin-bottom:0.5rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">📊</span>Dashboard
        </h1>
        <p style="color:#625B71;font-size:1.1rem;margin-bottom:0.8rem;line-height:1.5;">
            Welcome to your document workspace, {user_name}
        </p>
        <div style="display:inline-flex;align-items:center;background:{role_color}15;color:{role_color};padding:0.5rem 1rem;border-radius:20px;font-size:0.9rem;font-weight:500;">
            <span style="margin-right:0.3rem;">{role_indicator.split()[0]}</span>
            {role_indicator} • {user_role}
        </div>
    </div>
    """, unsafe_allow_html=True)
    try:
        db = DocumentDatabase()
        # Get ALL documents first, then apply filters - not just role-based
        all_documents = db.load_data()  # Load all documents from database
        user_documents = all_documents  # Show all documents by default
        
        # Notification Section
        st.markdown("""
        <div class="feature-section" style="margin-bottom:2rem;">
            <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                <span style="margin-right:0.5rem;">🔔</span>System Notifications
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Apply role-based access control for actions, but show all documents
        accessible_documents = db.get_documents_by_role(user_info['role'])  # For action permissions
        
        # --- In-app Notifications ---
        if 'last_seen_upload' not in st.session_state:
            st.session_state['last_seen_upload'] = ''
        
        # Check for new uploads across the system
        new_uploads_all = [doc for doc in all_documents if doc['upload_date'] > st.session_state['last_seen_upload']]
        # Check for high priority documents user can access
        high_priority_accessible = [doc for doc in accessible_documents if doc.get('priority') == 'High']
        
        if new_uploads_all:
            st.markdown(f"<div class='stCard' style='background:var(--material-surface-variant);color:var(--material-primary);margin-bottom:1em;padding:1rem;border-radius:var(--material-radius);border:1px solid var(--material-outline);'>🔔 <b>{len(new_uploads_all)} new document(s)</b> uploaded to the system since your last visit.</div>", unsafe_allow_html=True)
            st.session_state['last_seen_upload'] = max(doc['upload_date'] for doc in new_uploads_all)
        
        if high_priority_accessible:
            st.markdown(f"<div class='stCard' style='background:var(--material-surface-variant);color:#CF6679;margin-bottom:1em;padding:1rem;border-radius:var(--material-radius);border:1px solid var(--material-outline);'>⚠️ <b>{len(high_priority_accessible)} high-priority document(s)</b> require your attention (accessible to your role).</div>", unsafe_allow_html=True)

        # --- Expiry and Review Reminders ---
        today = datetime.now().date()
        # Check expiry/review for accessible documents only
        upcoming_expiry = [doc for doc in accessible_documents if doc.get('expiry_date') and doc['expiry_date'] != 'None' and datetime.strptime(doc['expiry_date'], '%Y-%m-%d').date() <= today + timedelta(days=7)]
        upcoming_review = [doc for doc in accessible_documents if doc.get('review_date') and doc['review_date'] != 'None' and datetime.strptime(doc['review_date'], '%Y-%m-%d').date() <= today + timedelta(days=7)]
        if upcoming_expiry:
            st.markdown(f"<div class='stCard' style='background:var(--material-surface-variant);color:#FF9800;margin-bottom:1em;padding:1rem;border-radius:var(--material-radius);border:1px solid var(--material-outline);'>⏰ <b>{len(upcoming_expiry)} document(s)</b> expiring within 7 days (that you can access).</div>", unsafe_allow_html=True)
        if upcoming_review:
            st.markdown(f"<div class='stCard' style='background:var(--material-surface-variant);color:#4CAF50;margin-bottom:1em;padding:1rem;border-radius:var(--material-radius);border:1px solid var(--material-outline);'>🔄 <b>{len(upcoming_review)} document(s)</b> due for review within 7 days (that you can access).</div>", unsafe_allow_html=True)

        # Document Overview Section
        st.markdown("""
        <div class="feature-section" style="margin-bottom:2rem;">
            <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                <span style="margin-right:0.5rem;">📈</span>Document Overview
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Actions
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📤 Upload New", key="upload_new", help="Upload new documents", width="stretch"):
                st.session_state.current_page = "Upload"
                st.rerun()
        
        with col2:
            if st.button("📝 Audit Log", key="audit_log", help="View system audit log", width="stretch"):
                st.session_state.current_page = "Audit Log"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Material UI inspired metrics - show system-wide stats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:24px 16px 16px 16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                        f"<div style='font-size:2.2rem;font-weight:600;color:var(--material-primary);'>📄 {len(all_documents)}</div>"
                        f"<div style='color:#FFFFFF;font-size:1.1rem;'>Total System Documents</div></div>", unsafe_allow_html=True)
        with col2:
            high_priority_all = len([doc for doc in all_documents if doc.get('priority') == 'High'])
            st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:24px 16px 16px 16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                        f"<div style='font-size:2.2rem;font-weight:600;color:#CF6679;'>⚠️ {high_priority_all}</div>"
                        f"<div style='color:#FFFFFF;font-size:1.1rem;'>High Priority Documents</div></div>", unsafe_allow_html=True)

        # Document Preview Section
        if all_documents:
            st.markdown("""
            <div class="feature-section" style="margin-bottom:2rem;">
                <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                    <span style="margin-right:0.5rem;">📖</span>Recent Documents
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show recent documents (last 5)
            recent_docs = sorted(all_documents, key=lambda x: x['upload_date'], reverse=True)[:5]
            
            for doc in recent_docs:
                # Create expandable preview for each document
                with st.expander(f"📄 {doc['filename']} - {doc.get('type', 'Unknown')} ({doc.get('priority', 'Low')} Priority)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Upload Date:** {doc['upload_date']}")
                        st.markdown(f"**File Size:** {doc.get('file_size_mb', 'Unknown')} MB")
                        if doc.get('detected_language'):
                            st.markdown(f"**Language:** {doc.get('detected_language')}")
                        
                        # Show summary if available
                        if doc.get('summary'):
                            st.markdown("**Summary:**")
                            # Clean HTML from summary
                            import re
                            import html
                            clean_summary = re.sub(r'<[^>]+>', '', doc.get('summary', ''))
                            clean_summary = html.escape(clean_summary)
                            st.write(clean_summary)
                    
                    with col2:
                        # Download button
                        file_path = f"/Users/ching/Desktop/KochiMetro_DocuTrack/uploads/{doc['filename']}"
                        try:
                            with open(file_path, 'rb') as file:
                                file_data = file.read()
                            st.download_button(
                                label="📥 Download",
                                data=file_data,
                                file_name=doc['filename'],
                                mime='application/octet-stream',
                                key=f"download_dash_{doc['id']}"
                            )
                        except FileNotFoundError:
                            st.error("File not found")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        
                        # Show content preview button
                        if st.button("👁️ Preview Content", key=f"preview_{doc['id']}"):
                            show_document_preview(doc)

        # --- Feedback Analytics (Management Only) ---
        # Only show detailed analytics to HR and Compliance Officer roles
        management_roles = ["HR", "Compliance Officer"]
        user_role = user_info.get('role', '') if user_info else ''
        
        if user_role in management_roles:
            st.markdown("""
            <div class="feature-section" style="margin-bottom:2rem;">
                <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:0.5rem;display:flex;align-items:center;">
                    <span style="margin-right:0.5rem;">📊</span>Feedback Analytics
                </h3>
                <p style="color:#888;font-size:0.9rem;margin-bottom:1.5rem;">🔒 Management view - Detailed feedback analytics and insights</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                feedback_analytics = db.get_feedback_analytics()
                if feedback_analytics['total_feedback'] > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:var(--material-primary);'>💬 {feedback_analytics['total_feedback']}</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Total Feedback</div></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:#4CAF50;'>👍 {feedback_analytics['likes']}</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Likes</div></div>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:#FF5722;'>👎 {feedback_analytics['dislikes']}</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Dislikes</div></div>", unsafe_allow_html=True)
                    with col4:
                        satisfaction_rate = round((feedback_analytics['likes'] / (feedback_analytics['likes'] + feedback_analytics['dislikes']) * 100), 1) if (feedback_analytics['likes'] + feedback_analytics['dislikes']) > 0 else 0
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:#FF9800;'>📈 {satisfaction_rate}%</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Satisfaction Rate</div></div>", unsafe_allow_html=True)
                    
                    # Recent feedback with text comments (Management only)
                    if feedback_analytics['text_feedback_count'] > 0:
                        st.markdown("""
                        <div style="margin-top:2rem;">
                            <h4 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                                <span style="margin-right:0.5rem;">💬</span>Recent Text Feedback
                            </h4>
                        </div>
                        """, unsafe_allow_html=True)
                        recent_feedback = db.get_recent_feedback_with_text(limit=5)
                        for feedback in recent_feedback:
                            doc = next((d for d in all_documents if d['id'] == feedback['document_id']), None)
                            doc_name = doc['filename'] if doc else f"Document ID: {feedback['document_id']}"
                            feedback_color = "#4CAF50" if feedback['feedback_type'] == 'like' else "#FF5722" if feedback['feedback_type'] == 'dislike' else "#757575"
                            feedback_icon = "👍" if feedback['feedback_type'] == 'like' else "👎" if feedback['feedback_type'] == 'dislike' else "💬"
                            
                            st.markdown(f"""
                            <div class='stCard' style='background:var(--material-surface-variant);border-radius:12px;padding:12px;margin-bottom:8px;border-left:4px solid {feedback_color};'>
                                <div style='display:flex;align-items:center;margin-bottom:4px;'>
                                    <span style='font-size:1.2rem;margin-right:8px;'>{feedback_icon}</span>
                                    <strong style='color:var(--material-primary);'>{doc_name}</strong>
                                    <span style='margin-left:auto;color:#666;font-size:0.8rem;'>{feedback['timestamp'][:19]}</span>
                                </div>
                                <div style='color:#FFFFFF;font-style:italic;margin-left:28px;'>"{feedback['text_feedback']}"</div>
                                <div style='color:#888;font-size:0.8rem;margin-left:28px;margin-top:4px;'>by {feedback['user_name']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📋 No feedback has been submitted yet. Encourage users to provide feedback on document summaries!")
            except Exception as e:
                st.warning(f"Could not load feedback analytics: {str(e)}")
        else:
            # Limited view for non-management roles
            st.markdown("""
            <div class="feature-section" style="margin-bottom:2rem;">
                <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:0.5rem;display:flex;align-items:center;">
                    <span style="margin-right:0.5rem;">📊</span>Feedback Status
                </h3>
                <p style="color:#888;font-size:0.9rem;margin-bottom:1.5rem;">👥 User view - Basic feedback information</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                feedback_analytics = db.get_feedback_analytics()
                if feedback_analytics['total_feedback'] > 0:
                    # Show only basic satisfaction rate for non-management users
                    satisfaction_rate = round((feedback_analytics['likes'] / (feedback_analytics['likes'] + feedback_analytics['dislikes']) * 100), 1) if (feedback_analytics['likes'] + feedback_analytics['dislikes']) > 0 else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:var(--material-primary);'>💬 {feedback_analytics['total_feedback']}</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Total Feedback</div></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='stCard' style='background:var(--material-surface);border-radius:20px;padding:16px;box-shadow:var(--material-elevation);margin-bottom:16px;border:1px solid var(--material-outline);'>"
                                    f"<div style='font-size:1.8rem;font-weight:600;color:#FF9800;'>📈 {satisfaction_rate}%</div>"
                                    f"<div style='color:#FFFFFF;font-size:0.9rem;'>Satisfaction Rate</div></div>", unsafe_allow_html=True)
                    
                    st.info("📊 Detailed feedback analytics are available to management personnel.")
                else:
                    st.info("📋 No feedback has been submitted yet. You can provide feedback on document summaries below!")
            except Exception as e:
                st.warning(f"Could not load feedback information: {str(e)}")

        # --- Advanced Search & Filters ---
        st.markdown("<h3 style='margin-top:0.5em;color:var(--material-primary);font-weight:600;'>📋 All Documents - Search & Filter</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#FFFFFF;margin-bottom:1em;'>🔍 Showing all documents in the system. Use filters below to narrow down results. Download permissions are based on your role.</p>", unsafe_allow_html=True)
        search_query = st.text_input("Full-text search", "", key="dashboard_search_query")
        colf1, colf2, colf3, colf4, colf5 = st.columns(5)
        with colf1:
            date_from = st.date_input("From Date", value=None, key="filter_date_from")
        with colf2:
            date_to = st.date_input("To Date", value=None, key="filter_date_to")
        with colf3:
            uploader = st.text_input("Uploader", "", key="filter_uploader")
        with colf4:
            doc_type = st.text_input("Type", "", key="filter_type")
        with colf5:
            priority = st.selectbox("Priority", ["", "High", "Medium", "Low"], key="filter_priority")
        # Tag filter (optional)
        tag = st.text_input("Tag", "", key="filter_tag")

        # Filter logic
        filtered_docs = user_documents
        if search_query:
            filtered_docs = [doc for doc in filtered_docs if search_query.lower() in (doc.get('summary','') + doc.get('filename','') + doc.get('document_type','')).lower()]
        if uploader:
            filtered_docs = [doc for doc in filtered_docs if uploader.lower() in doc.get('uploaded_by','').lower()]
        if doc_type:
            filtered_docs = [doc for doc in filtered_docs if doc_type.lower() in doc.get('document_type','').lower()]
        if priority:
            filtered_docs = [doc for doc in filtered_docs if doc.get('priority','') == priority]
        if tag:
            filtered_docs = [doc for doc in filtered_docs if tag.lower() in ' '.join(doc.get('tags',[])).lower()]
        if date_from:
            filtered_docs = [doc for doc in filtered_docs if doc.get('upload_date','')[:10] >= str(date_from)]
        if date_to:
            filtered_docs = [doc for doc in filtered_docs if doc.get('upload_date','')[:10] <= str(date_to)]

        if filtered_docs:
            table_data = []
            for doc in filtered_docs:
                # Universal access - all users can perform all actions
                actions = ['view', 'edit', 'approve', 'delete']
                
                table_data.append({
                    'File': doc['filename'][:24] + '...' if len(doc['filename']) > 24 else doc['filename'],
                    'Type': doc['document_type'],
                    'Priority': doc['priority'],
                    'Date': doc['upload_date'][:10],
                    'Uploader': doc.get('uploaded_by',''),
                    'Tags': ', '.join(doc.get('tags',[])),
                    'Allowed': ', '.join(actions)
                })
            st.dataframe(table_data, use_container_width=True, hide_index=True)
            # --- Download and Export Options ---
            st.markdown("""
            <div class="feature-section" style="margin-top:2rem;">
                <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                    <span style="margin-right:0.5rem;">📥</span>Download & Export
                </h3>
            </div>
            """, unsafe_allow_html=True)
            import os
            # All users can download all documents
            downloadable_docs = filtered_docs
            
            if downloadable_docs:
                st.markdown("**Available Downloads** (universal access):")
                for doc in downloadable_docs:
                    file_path = doc.get('file_path')
                    if file_path and os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"📄 Download {doc['filename']}",
                                data=f,
                                file_name=doc['filename'],
                                mime=doc.get('file_type', 'application/octet-stream'),
                                key=f"download_{doc['id']}"
                            )
            else:
                st.info("No documents available for download.")
                
            # Export analytics/statistics as CSV
            if st.button("Export Document Table as CSV", key="export_csv"):
                import io
                import csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(table_data[0].keys()) if table_data else [])
                writer.writeheader()
                writer.writerows(table_data)
                st.download_button(
                    label="Download CSV",
                    data=output.getvalue(),
                    file_name="documents_export.csv",
                    mime="text/csv",
                    key="download_csv_btn"
                )
        else:
            st.info("No documents found for the selected filters.")

        # --- Summarize Feature ---
        st.markdown("<h3 style='margin-top:2em;color:var(--material-primary);font-weight:600;'>Summarize a Document</h3>", unsafe_allow_html=True)
        # All users can summarize all documents
        summarizable_docs = filtered_docs if 'filtered_docs' in locals() else all_documents
        if summarizable_docs:
            doc_options = {f"{doc['filename']} ({doc['document_type']}, {doc['upload_date'][:10]})": doc for doc in summarizable_docs}
            selected_label = st.selectbox("Select a document to summarize", list(doc_options.keys()), key="dashboard_summarize_select")
            if selected_label:
                selected_doc = doc_options[selected_label]
                if st.button("Summarize Selected Document", key="dashboard_summarize_btn"):
                    from modules.summarizer import DocumentSummarizer
                    import os
                    summarizer = DocumentSummarizer()
                    with st.spinner("Summarizing selected document (this may take a while)..."):
                        file_path = selected_doc.get("file_path")
                        extracted_text = ""
                        if file_path and os.path.exists(file_path):
                            try:
                                with open(file_path, "rb") as f:
                                    ext = os.path.splitext(file_path)[1].lower()
                                    fake_file = f
                                    from modules.ocr_processor import OCRProcessor
                                    if ext == ".pdf":
                                        extracted_text = OCRProcessor().extract_text_from_pdf(fake_file)
                                    elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
                                        extracted_text = OCRProcessor().extract_text_from_image(fake_file)
                                    elif ext == ".docx":
                                        extracted_text = OCRProcessor().extract_text_from_docx(fake_file)
                                    elif ext == ".txt":
                                        extracted_text = f.read().decode("utf-8")
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
                        else:
                            extracted_text = selected_doc.get("summary", "")
                        if not extracted_text:
                            st.warning("No text found in the selected document.")
                        else:
                            insights = summarizer.get_document_insights(
                                extracted_text,
                                selected_doc.get("document_type", "Unknown"),
                                selected_doc.get("filename", "")
                            )
                            st.markdown("**Summary:**")
                            st.info(insights["summary"])
                            
                            # --- Enhanced Feedback Feature for Dashboard Summary ---
                            st.markdown("""
                            <div style='background:linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);border-radius:16px;padding:24px;margin:24px 0;border:1px solid rgba(255,255,255,0.1);box-shadow:0 8px 32px rgba(0,0,0,0.3);'>
                                <div style='display:flex;align-items:center;margin-bottom:16px;'>
                                    <div style='background:rgba(255,255,255,0.15);border-radius:50%;width:48px;height:48px;display:flex;align-items:center;justify-content:center;margin-right:16px;'>
                                        <span style='font-size:24px;'>💬</span>
                                    </div>
                                    <div>
                                        <h3 style='color:#FFFFFF;margin:0;font-weight:600;font-size:1.4rem;'>Rate this Summary</h3>
                                        <p style='color:rgba(255,255,255,0.8);margin:4px 0 0 0;font-size:0.95rem;'>Help us improve our AI summaries with your feedback</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create modern feedback UI with better spacing
                            col1, col2 = st.columns([2, 3], gap="large")
                            
                            with col1:
                                st.markdown("<h5 style='color:var(--material-primary);margin-bottom:12px;font-weight:600;'>Quick Rating</h5>", unsafe_allow_html=True)
                                
                                # Like button with custom styling
                                like_col, dislike_col = st.columns(2)
                                with like_col:
                                    if st.button("👍 Like", key=f"dashboard_like_{selected_doc['id']}", help="This summary is helpful and accurate", use_container_width=True):
                                        try:
                                            feedback_result = db.add_feedback(
                                                document_id=selected_doc['id'],
                                                feedback_type='like',
                                                user_name=user_info.get('name', 'Unknown User'),
                                                user_role=user_info.get('role', 'Unknown'),
                                                text_feedback=None
                                            )
                                            if feedback_result:
                                                st.success("✅ Thank you for your positive feedback!")
                                                
                                                # Send real-time alert for feedback (optional, non-blocking)
                                                try:
                                                    send_feedback_alert(
                                                        selected_doc['id'], 
                                                        {
                                                            "type": "like",
                                                            "user_name": user_info.get('name', 'Unknown User'),
                                                            "text": ""
                                                        },
                                                        selected_doc.get('filename', 'Unknown Document')
                                                    )
                                                except Exception as e:
                                                    print(f"⚠️ Failed to send feedback alert (continuing): {e}")
                                                    # Continue without alerts - don't fail the feedback
                                            else:
                                                st.error("❌ Failed to save feedback. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error saving feedback: {str(e)}")
                                
                                with dislike_col:
                                    if st.button("👎 Dislike", key=f"dashboard_dislike_{selected_doc['id']}", help="This summary needs improvement", use_container_width=True):
                                        try:
                                            feedback_result = db.add_feedback(
                                                document_id=selected_doc['id'],
                                                feedback_type='dislike',
                                                user_name=user_info.get('name', 'Unknown User'),
                                                user_role=user_info.get('role', 'Unknown'),
                                                text_feedback=None
                                            )
                                            if feedback_result:
                                                st.success("✅ Thank you for your feedback! We'll work to improve our summaries.")
                                                
                                                # Send real-time alert for feedback (optional, non-blocking)
                                                try:
                                                    send_feedback_alert(
                                                        selected_doc['id'], 
                                                        {
                                                            "type": "dislike",
                                                            "user_name": user_info.get('name', 'Unknown User'),
                                                            "text": ""
                                                        },
                                                        selected_doc.get('filename', 'Unknown Document')
                                                    )
                                                except Exception as e:
                                                    print(f"⚠️ Failed to send feedback alert (continuing): {e}")
                                                    # Continue without alerts - don't fail the feedback
                                            else:
                                                st.error("❌ Failed to save feedback. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error saving feedback: {str(e)}")
                            
                            with col2:
                                st.markdown("<h5 style='color:var(--material-primary);margin-bottom:12px;font-weight:600;'>Detailed Feedback</h5>", unsafe_allow_html=True)
                                
                                # Text feedback input with modern styling
                                text_feedback = st.text_area(
                                    "Share your thoughts (optional):",
                                    placeholder="What could be improved about this summary? Any specific suggestions?",
                                    key=f"dashboard_text_feedback_{selected_doc['id']}",
                                    height=80,
                                    help="Your detailed feedback helps us improve our AI models"
                                )
                                
                                if st.button("� Submit Feedback", key=f"dashboard_text_submit_{selected_doc['id']}", help="Submit detailed feedback", use_container_width=True):
                                    if text_feedback and text_feedback.strip():
                                        try:
                                            feedback_result = db.add_feedback(
                                                document_id=selected_doc['id'],
                                                feedback_type='text',
                                                user_name=user_info.get('name', 'Unknown User'),
                                                user_role=user_info.get('role', 'Unknown'),
                                                text_feedback=text_feedback.strip()
                                            )
                                            if feedback_result:
                                                st.success("✅ Thank you for your detailed feedback!")
                                                
                                                # Send real-time alert for text feedback (optional, non-blocking)
                                                try:
                                                    send_feedback_alert(
                                                        selected_doc['id'], 
                                                        {
                                                            "type": "text",
                                                            "user_name": user_info.get('name', 'Unknown User'),
                                                            "text": text_feedback.strip()
                                                        },
                                                        selected_doc.get('filename', 'Unknown Document')
                                                    )
                                                except Exception as e:
                                                    print(f"⚠️ Failed to send feedback alert (continuing): {e}")
                                                    # Continue without alerts - don't fail the feedback
                                                
                                                # Clear the text input after successful submission
                                                st.session_state[f"dashboard_text_feedback_{selected_doc['id']}"] = ""
                                            else:
                                                st.error("❌ Failed to save feedback. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error saving feedback: {str(e)}")
                                    else:
                                        st.warning("⚠️ Please enter some text feedback before submitting.")
                            
                            # Show existing feedback for this document with enhanced design
                            existing_feedback = db.get_document_feedback(selected_doc['id'])
                            if existing_feedback:
                                st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
                                
                                # Enhanced feedback summary section
                                feedback_summary = {
                                    'likes': len([f for f in existing_feedback if f['type'] == 'like']),
                                    'dislikes': len([f for f in existing_feedback if f['type'] == 'dislike']),
                                    'comments': len([f for f in existing_feedback if f['type'] == 'text' and f.get('text')])
                                }
                                
                                st.markdown("""
                                <div style='background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:12px;padding:20px;margin:16px 0;'>
                                    <h5 style='color:#FFFFFF;margin:0 0 16px 0;font-weight:600;display:flex;align-items:center;'>
                                        <span style='margin-right:8px;'>📊</span>
                                        Feedback Summary for this Document
                                    </h5>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Modern metrics cards
                                metric_col1, metric_col2, metric_col3 = st.columns(3, gap="medium")
                                
                                with metric_col1:
                                    st.markdown(f"""
                                    <div style='background:linear-gradient(135deg, #4CAF50, #45a049);border-radius:12px;padding:20px;text-align:center;color:white;box-shadow:0 4px 12px rgba(76,175,80,0.3);'>
                                        <div style='font-size:2.5rem;font-weight:700;margin-bottom:8px;'>👍</div>
                                        <div style='font-size:2rem;font-weight:600;margin-bottom:4px;'>{feedback_summary['likes']}</div>
                                        <div style='font-size:0.9rem;opacity:0.9;'>Likes</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with metric_col2:
                                    st.markdown(f"""
                                    <div style='background:linear-gradient(135deg, #FF5722, #E64A19);border-radius:12px;padding:20px;text-align:center;color:white;box-shadow:0 4px 12px rgba(255,87,34,0.3);'>
                                        <div style='font-size:2.5rem;font-weight:700;margin-bottom:8px;'>👎</div>
                                        <div style='font-size:2rem;font-weight:600;margin-bottom:4px;'>{feedback_summary['dislikes']}</div>
                                        <div style='font-size:0.9rem;opacity:0.9;'>Dislikes</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with metric_col3:
                                    st.markdown(f"""
                                    <div style='background:linear-gradient(135deg, #2196F3, #1976D2);border-radius:12px;padding:20px;text-align:center;color:white;box-shadow:0 4px 12px rgba(33,150,243,0.3);'>
                                        <div style='font-size:2.5rem;font-weight:700;margin-bottom:8px;'>💬</div>
                                        <div style='font-size:2rem;font-weight:600;margin-bottom:4px;'>{feedback_summary['comments']}</div>
                                        <div style='font-size:0.9rem;opacity:0.9;'>Comments</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Show recent text feedback with enhanced styling
                                text_feedbacks = [f for f in existing_feedback if f['type'] == 'text' and f.get('text')]
                                if text_feedbacks:
                                    st.markdown("""
                                    <div style='margin-top:24px;'>
                                        <h6 style='color:var(--material-primary);font-weight:600;margin-bottom:16px;display:flex;align-items:center;'>
                                            <span style='margin-right:8px;'>💭</span>
                                            Recent Comments
                                        </h6>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    for i, feedback in enumerate(text_feedbacks[-3:]):  # Show last 3 comments
                                        gradient_colors = [
                                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                            "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                                            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
                                        ]
                                        gradient = gradient_colors[i % len(gradient_colors)]
                                        
                                        st.markdown(f"""
                                        <div style='background:{gradient};border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 4px 12px rgba(0,0,0,0.15);'>
                                            <div style='background:rgba(255,255,255,0.15);border-radius:8px;padding:12px;margin-bottom:8px;'>
                                                <div style='color:#FFFFFF;font-style:italic;line-height:1.5;font-size:0.95rem;'>
                                                    "{feedback['text']}"
                                                </div>
                                            </div>
                                            <div style='display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,0.8);font-size:0.8rem;'>
                                                <span style='font-weight:500;'>👤 {feedback['user_name']}</span>
                                                <span>🕒 {feedback['timestamp'][:19]}</span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)

                # --- Version History Feature ---
                st.markdown("""
                <div style="margin-top:2rem;">
                    <h4 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
                        <span style="margin-right:0.5rem;">📜</span>Version History
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                version_history = db.get_version_history(selected_doc['id'])
                if version_history and len(version_history) > 1:
                    version_labels = [f"v{v['version']} - {v['upload_date'][:19]} by {v['uploaded_by']}" for v in version_history]
                    selected_version_idx = st.selectbox("Select a version to view/restore", list(range(len(version_labels))), format_func=lambda i: version_labels[i], key="dashboard_version_select")
                    version_data = version_history[selected_version_idx]
                    st.json({k: v for k, v in version_data.items() if k not in ['file_path']})
                    if version_data['version'] != selected_doc.get('version', 1):
                        if st.button(f"Restore v{version_data['version']} as current", key=f"restore_v{version_data['version']}"):
                            try:
                                db.restore_version(selected_doc['id'], version_data['version'], user_info)
                                st.success(f"Restored version {version_data['version']} as current.")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error restoring version: {str(e)}")
                elif version_history:
                    st.info("Only one version exists for this document.")
                else:
                    st.info("No version history found for this document.")
        else:
            st.info("No documents available for summarization.")
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def show_document_preview(doc):
    """Display document content preview in a modal-like expander"""
    from pathlib import Path
    from config import UPLOAD_DIR
    
    file_path = UPLOAD_DIR / doc['filename']
    file_ext = Path(doc['filename']).suffix.lower()
    
    st.markdown(f"### 📖 Preview: {doc['filename']}")
    
    if file_path.exists():
        try:
            if file_ext == '.pdf':
                # Try to show PDF content
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        text_content = ""
                        for page in pdf_reader.pages[:3]:  # Show first 3 pages only
                            text_content += page.extract_text() + "\n"
                    
                    if text_content.strip():
                        st.text_area("📄 PDF Content (First 3 pages):", text_content[:2000] + "..." if len(text_content) > 2000 else text_content, height=300, disabled=True)
                    else:
                        st.warning("No text could be extracted from PDF")
                        if doc.get('content'):
                            content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
                            st.text_area("🔍 OCR Content:", content_preview, height=300, disabled=True)
                except ImportError:
                    st.warning("PyPDF2 not available for PDF preview")
                    if doc.get('content'):
                        content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
                        st.text_area("🔍 Stored Content:", content_preview, height=300, disabled=True)
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
                    if doc.get('content'):
                        content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
                        st.text_area("🔍 Stored Content:", content_preview, height=300, disabled=True)
            
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # Display image
                st.image(str(file_path), caption=doc['filename'], use_column_width=True)
                if doc.get('content'):
                    content_preview = doc['content'][:1000] + "..." if len(doc['content']) > 1000 else doc['content']
                    st.text_area("🔍 OCR Text:", content_preview, height=200, disabled=True)
            
            elif file_ext == '.txt':
                # Display text file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                content_preview = content[:2000] + "..." if len(content) > 2000 else content
                st.text_area("📝 Text Content:", content_preview, height=300, disabled=True)
            
            else:
                # Show stored content for other file types
                if doc.get('content'):
                    content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
                    st.text_area("📋 Extracted Content:", content_preview, height=300, disabled=True)
                else:
                    st.info("No content preview available for this file type.")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            if doc.get('content'):
                content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
                st.text_area("🔍 Stored Content:", content_preview, height=300, disabled=True)
    else:
        st.warning(f"File not found: {doc['filename']}")
        if doc.get('content'):
            content_preview = doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content']
            st.text_area("🔍 Stored Content:", content_preview, height=300, disabled=True)