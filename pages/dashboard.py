"""
Enhanced role-based dashboard page with improved UI
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.database import DocumentDatabase
from config import USER_ROLES
from datetime import datetime, timedelta

def show_dashboard_page(user_info):
    st.markdown("""
    <div class="material-dashboard-header" style="margin-bottom:1.5em;">
        <h2 style="color:var(--material-primary);font-weight:700;margin-bottom:0.2em;">Dashboard</h2>
        <div style="color:#625B71;font-size:1.1rem;">Welcome to your document workspace</div>
    </div>
    """, unsafe_allow_html=True)
    try:
        db = DocumentDatabase()
        # Get ALL documents first, then apply filters - not just role-based
        all_documents = db.load_data()  # Load all documents from database
        user_documents = all_documents  # Show all documents by default
        
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

        # Material U inspired metrics - show system-wide stats
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
            st.markdown("<h3 style='margin-top:2em;'>Download & Export</h3>", unsafe_allow_html=True)
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

                # --- Version History Feature ---
                st.markdown("<h4 style='margin-top:2em;'>Version History</h4>", unsafe_allow_html=True)
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