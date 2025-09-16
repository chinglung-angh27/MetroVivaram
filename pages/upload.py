"""
Document upload page with enhanced OCR and multi-language support
"""
import streamlit as st
import os
from pathlib import Path
from modules.ocr_processor import AdvancedOCRProcessor
from modules.document_classifier import DocumentClassifier
from modules.summarizer import DocumentSummarizer
from modules.database import DocumentDatabase
from config import UPLOAD_DIR, MAX_FILE_SIZE


def show_upload_page(user_info):
    st.markdown("""
    <div class="material-upload-header" style="margin-bottom:1.5em;">
        <h2 style="color:var(--material-primary);font-weight:700;margin-bottom:0.2em;">🚀 Advanced Document Upload</h2>
        <div style="color:#625B71;font-size:1.1rem;">Upload documents with intelligent OCR, multi-language detection, and automatic processing</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize processors
    ocr_processor = AdvancedOCRProcessor()
    classifier = DocumentClassifier()
    db = DocumentDatabase()
    summarizer = None  # Initialize only if needed

    # OCR Settings
    st.markdown("""
    <div class='stCard' style='background:var(--material-surface-variant);padding:1.5rem;margin-bottom:1.5rem;'>
        <h3 style='color:var(--material-primary);margin-bottom:1rem;'>🔍 OCR Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        auto_detect_language = st.checkbox(
            "🌐 Auto-detect language (English/Malayalam/Hybrid)", 
            value=True,
            help="Automatically detect and optimize OCR for English, Malayalam, or mixed content"
        )
    with col2:
        show_ocr_details = st.checkbox(
            "📊 Show detailed OCR analysis", 
            value=True,
            help="Display language analysis, confidence scores, and processing details"
        )

    uploaded_files = st.file_uploader(
        "Choose file(s) to upload (supports images, PDFs, documents)",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF (text & scanned), Images (JPG, PNG, TIFF), Word documents, Text files"
    )

    st.markdown("""
    <div class='stCard' style='background:#F4EFF4;padding:1.5rem;margin-bottom:1.5rem;'>
        <h4 style='color:var(--material-primary);margin-bottom:1rem;'>⚙️ Batch Processing Options</h4>
        <p style='color:#625B71;margin-bottom:1rem;'>Settings applied to all selected files:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        batch_type = st.text_input(
            "📄 Document Type (optional)",
            value="",
            help="Override automatic classification for all files"
        )
        batch_priority = st.selectbox(
            "⚡ Priority Level",
            ["Auto-detect", "High", "Medium", "Low"],
            help="Set priority level for all uploaded documents"
        )
    
    with col2:
        expiry_date = st.date_input(
            "📅 Expiry Date (optional)",
            value=None,
            help="Set document expiration date"
        )
        review_date = st.date_input(
            "🔄 Review Date (optional)",
            value=None,
            help="Schedule document review date"
        )

    if uploaded_files:
        st.markdown(f"""
        <div class='stCard' style='background:var(--material-primary);color:var(--material-on-primary);padding:1rem;margin:1.5rem 0;'>
            <h4 style='margin:0;'>🔄 Processing {len(uploaded_files)} file(s)...</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for i, uploaded_file in enumerate(uploaded_files, 1):
            st.markdown(f"""
            <div style='border-left: 4px solid var(--material-primary); padding-left: 1rem; margin: 2rem 0;'>
                <h4 style='color:var(--material-primary); margin-bottom: 0.5rem;'>📄 File {i}/{len(uploaded_files)}: {uploaded_file.name}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # File size check
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE:
                    st.error(f"❌ File size ({file_size_mb:.1f}MB) exceeds maximum limit of {MAX_FILE_SIZE}MB")
                    continue
                
                # Save file
                file_path = UPLOAD_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ File saved: {file_path.name}")
                
                # Advanced OCR Processing
                with st.spinner("🔍 Performing advanced OCR analysis..."):
                    ocr_result = ocr_processor.process_document(uploaded_file, auto_detect_language)
                
                # Display OCR results
                if show_ocr_details:
                    with st.expander(f"🔍 OCR Analysis for {uploaded_file.name}", expanded=True):
                        if 'error' in ocr_result:
                            st.error(f"❌ OCR Error: {ocr_result['error']}")
                        else:
                            # Processing summary
                            summary = ocr_processor.get_processing_summary(ocr_result)
                            st.info(summary)
                            
                            # Language analysis details
                            lang_info = ocr_result['language_analysis']
                            if lang_info['is_hybrid']:
                                st.markdown(f"""
                                **🌐 Hybrid Document Detected:**
                                - English content: {lang_info['english_percentage']:.1f}%
                                - Malayalam content: {lang_info['malayalam_percentage']:.1f}%
                                - Confidence: {ocr_result['confidence']:.1%}
                                """)
                            else:
                                st.markdown(f"""
                                **🗣️ Language Analysis:**
                                - Primary language: **{lang_info['primary_language'].title()}**
                                - Confidence: {ocr_result['confidence']:.1%}
                                """)
                            
                            # Text statistics
                            stats = ocr_result['text_stats']
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Words", stats['words'])
                            with col2:
                                st.metric("Characters", stats['characters'])
                            with col3:
                                st.metric("Lines", stats['lines'])
                            with col4:
                                st.metric("Sentences", stats.get('sentences', 'N/A'))
                            
                            # Show extracted text preview
                            if ocr_result['text'].strip():
                                st.text_area(
                                    "📝 Extracted Text Preview (first 500 characters)",
                                    ocr_result['text'][:500] + "..." if len(ocr_result['text']) > 500 else ocr_result['text'],
                                    height=150,
                                    disabled=True
                                )
                            else:
                                st.warning("⚠️ No text could be extracted from this document")
                
                extracted_text = ocr_result.get('text', '')
                
                # Document Classification
                with st.spinner("🏷️ Classifying document..."):
                    classification = classifier.get_classification_details(extracted_text, uploaded_file.name)
                
                # Smart redaction for sensitive information
                import re
                def redact_sensitive(text):
                    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED EMAIL]', text)
                    text = re.sub(r'\b\d{10,13}\b', '[REDACTED PHONE]', text)
                    text = re.sub(r'₹?\s?\d{1,3}(,\d{3})*(\.\d+)?', '[REDACTED AMOUNT]', text)
                    return text
                
                redacted_text = redact_sensitive(extracted_text)
                if redacted_text != extracted_text:
                    st.warning("🔒 Sensitive information detected and automatically redacted")
                extracted_text = redacted_text
                
                # Document Summarization
                summary = "(Summarization skipped)"
                priority = "Medium"
                
                # Smart summarization based on file size and content
                should_summarize = file_size_mb <= 2  # Auto-summarize smaller files
                if file_size_mb > 2:
                    should_summarize = st.checkbox(
                        f"📄 Generate summary for {uploaded_file.name} (large file - may take time)",
                        value=False
                    )
                else:
                    should_summarize = st.checkbox(
                        f"📄 Generate summary for {uploaded_file.name}",
                        value=True
                    )
                
                if should_summarize and extracted_text.strip():
                    if summarizer is None:
                        summarizer = DocumentSummarizer()
                    
                    with st.spinner("📝 Generating intelligent summary..."):
                        insights = summarizer.get_document_insights(
                            extracted_text,
                            classification["predicted_type"],
                            uploaded_file.name
                        )
                        summary = insights["summary"]
                        priority = insights.get("priority", priority)
                
                # Prepare document data
                doc_type = batch_type if batch_type else classification["predicted_type"]
                doc_priority = batch_priority if batch_priority != "Auto-detect" else priority
                
                # Store OCR analysis results
                document_data = {
                    "filename": file_path.name,
                    "file_type": uploaded_file.type,
                    "document_type": doc_type,
                    "classification_confidence": classification["confidence"],
                    "summary": summary,
                    "priority": doc_priority,
                    "file_path": str(file_path),
                    "expiry_date": str(expiry_date) if expiry_date else None,
                    "review_date": str(review_date) if review_date else None,
                    # New OCR fields
                    "language_analysis": ocr_result.get('language_analysis', {}),
                    "extraction_method": ocr_result.get('extraction_method', 'unknown'),
                    "ocr_confidence": ocr_result.get('confidence', 0.0),
                    "text_stats": ocr_result.get('text_stats', {})
                }
                
                # Save to database
                db.add_document(document_data, user_info)
                
                st.success(f"✅ Document {file_path.name} processed and saved successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                import traceback
                with st.expander("🐛 Debug Information"):
                    st.code(traceback.format_exc())

        st.balloons()  # Celebration for successful uploads!

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

                        
