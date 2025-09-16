"""
Document upload page with enhanced error handling
"""
import streamlit as st
import os
from pathlib import Path
from modules.ocr_processor import OCRProcessor
from modules.document_classifier import DocumentClassifier
from modules.summarizer import DocumentSummarizer
from modules.database import DocumentDatabase
from config import UPLOAD_DIR, MAX_FILE_SIZE


def show_upload_page(user_info):
    st.markdown("""
    <div class="material-upload-header" style="margin-bottom:1.5em;">
        <h2 style="color:var(--material-primary);font-weight:700;margin-bottom:0.2em;">Upload Document</h2>
        <div style="color:#625B71;font-size:1.1rem;">Add new documents to your workspace</div>
    </div>
    """, unsafe_allow_html=True)
    ocr_processor = OCRProcessor()
    classifier = DocumentClassifier()
    db = DocumentDatabase()
    # Summarizer will be initialized only if needed
    summarizer = None



    uploaded_files = st.file_uploader(
        "Choose file(s) to upload (bulk supported)",
        type=["pdf", "png", "jpg", "jpeg", "docx", "txt", "doc"],
        accept_multiple_files=True
    )

    st.markdown("""
    <div class='stCard' style='background:#F4EFF4;padding:1.5em 1em 1em 1em;margin-bottom:1.5em;'>
        <b>Batch Options (applied to all selected files):</b>
        <div style='margin-top:1em;'>
            <div style='margin-bottom:0.7em;'>
                <label style='color:var(--material-primary);font-weight:500;'>Document Type (optional, overrides auto-classification)</label>
            </div>
    </div>
    """, unsafe_allow_html=True)
    batch_type = st.text_input("Document Type (optional, overrides auto-classification)", value="", key="batch_type")
    batch_priority = st.selectbox("Priority (optional, overrides auto)", ["", "High", "Medium", "Low"], key="batch_priority")
    expiry_date = st.date_input("Document Expiry Date (optional)", value=None, key="expiry_date")
    review_date = st.date_input("Review Date (optional)", value=None, key="review_date")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            import re
            def redact_sensitive(text):
                text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED EMAIL]', text)
                text = re.sub(r'\b\d{10,13}\b', '[REDACTED PHONE]', text)
                text = re.sub(r'₹?\s?\d{1,3}(,\d{3})*(\.\d+)?', '[REDACTED AMOUNT]', text)
                return text
            try:
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE:
                    st.markdown(f"<div class='stCard' style='background:#FFD8E4;color:#B3261E;'>File {uploaded_file.name} size ({file_size_mb:.1f}MB) exceeds maximum limit of {MAX_FILE_SIZE}MB</div>", unsafe_allow_html=True)
                    continue
                file_path = UPLOAD_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.markdown(f"<div class='stCard' style='background:#D0F8E5;color:#006B57;'>File uploaded: {file_path.name}</div>", unsafe_allow_html=True)
                with st.spinner(f"Extracting text from {uploaded_file.name} (OCR/Parsing)..."):
                    extracted_text = ocr_processor.process_document(uploaded_file)
                with st.spinner(f"Classifying {uploaded_file.name}..."):
                    classification = classifier.get_classification_details(extracted_text, uploaded_file.name)
                summary = "(Summarization skipped)"
                priority = classification["confidence"] > 50 and "High" or "Medium"
                do_summarize = True
                if file_size_mb > 2:
                    do_summarize = st.checkbox(f"Run summarization for {uploaded_file.name} (may be slow for large files)", value=False, key=f"summarize_{uploaded_file.name}")
                else:
                    do_summarize = st.checkbox(f"Run summarization for {uploaded_file.name}", value=True, key=f"summarize_{uploaded_file.name}")
                if do_summarize:
                    if summarizer is None:
                        summarizer = DocumentSummarizer()
                    with st.spinner(f"Summarizing {uploaded_file.name} (this may take a while)..."):
                        insights = summarizer.get_document_insights(
                            extracted_text,
                            classification["predicted_type"],
                            uploaded_file.name
                        )
                        summary = insights["summary"]
                        priority = insights.get("priority", priority)
                redacted_text = redact_sensitive(extracted_text)
                if redacted_text != extracted_text:
                    st.markdown(f"<div class='stCard' style='background:#FFF2CC;color:#7F5700;'>Sensitive information was detected and redacted in {uploaded_file.name}.</div>", unsafe_allow_html=True)
                extracted_text = redacted_text
                doc_type = batch_type if batch_type else classification["predicted_type"]
                doc_priority = batch_priority if batch_priority else priority
                document_data = {
                    "filename": file_path.name,
                    "file_type": uploaded_file.type,
                    "document_type": doc_type,
                    "classification_confidence": classification["confidence"],
                    "summary": summary,
                    "priority": doc_priority,
                    "file_path": str(file_path),
                    "expiry_date": str(expiry_date) if expiry_date else None,
                    "review_date": str(review_date) if review_date else None
                }
                db.add_document(document_data, user_info)
                st.markdown(f"<div class='stCard' style='background:#D0F8E5;color:#006B57;'>Document {file_path.name} processed and saved.</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='stCard' style='background:#FFD8E4;color:#B3261E;'>Error processing {uploaded_file.name}: {str(e)}</div>", unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:2em;color:var(--material-primary);font-weight:600;'>Recent Uploads</h3>", unsafe_allow_html=True)
    try:
        documents = db.load_data()
        recent_docs = sorted(documents, key=lambda x: x["upload_date"], reverse=True)[:5]
        if recent_docs:
            for doc in recent_docs:
                st.markdown(f"<div class='stCard' style='background:#fff;color:#381E72;margin-bottom:0.5em;'><b>{doc['filename']}</b> - {doc['document_type']} ({doc['upload_date'][:10]})</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='stCard' style='background:#F5F5F5;color:#757575;'>No documents uploaded yet.</div>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"<div class='stCard' style='background:#FFD8E4;color:#B3261E;'>Error loading recent documents: {str(e)}</div>", unsafe_allow_html=True)

                        
