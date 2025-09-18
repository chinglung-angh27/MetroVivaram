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

# Optional real-time alerts
try:
    from modules.alert_manager import send_document_upload_alert, send_feedback_alert
    ALERTS_AVAILABLE = True
except ImportError:
    print("⚠️ Alert manager not available - running without real-time alerts")
    ALERTS_AVAILABLE = False


def show_upload_page(user_info):
    # Modern Material Design Header
    st.markdown("""
    <div class="material-page-header" style="margin-bottom:2rem;padding:1.5rem 0;border-bottom:1px solid var(--material-outline);">
        <h1 style="color:var(--material-primary);font-weight:700;font-size:2rem;margin-bottom:0.5rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">🚀</span>Document Upload Center
        </h1>
        <p style="color:#625B71;font-size:1.1rem;margin-bottom:0;line-height:1.5;">
            Upload documents with intelligent OCR, multi-language detection, and automatic processing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize processors
    ocr_processor = AdvancedOCRProcessor()
    classifier = DocumentClassifier()
    db = DocumentDatabase()
    summarizer = None  # Initialize only if needed

    # OCR Status Information
    st.markdown("""
    <div class="feature-section" style="margin-bottom:2rem;">
        <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">🔧</span>System Status
        </h3>
    """, unsafe_allow_html=True)
    
    # Check OCR availability and show status
    from modules.ocr_processor import TESSERACT_AVAILABLE
    if not TESSERACT_AVAILABLE:
        st.warning("""
        ⚠️ **OCR Functionality Limited**: Tesseract OCR is not available on this system.
        
        - ✅ **Text-based PDFs**: Can still extract text directly
        - ❌ **Images & Scanned PDFs**: OCR processing unavailable
        - 📄 **Recommendation**: Use text-based documents for best results
        
        *This is common on cloud platforms. The app works with text-extractable documents.*
        """)
    else:
        st.success("✅ **Full OCR Capabilities Available** - All document types supported including scanned images and PDFs.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Document Processing Configuration
    st.markdown("""
    <div class="feature-section" style="margin-bottom:2rem;">
        <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">🔍</span>Processing Options
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        auto_detect_language = st.checkbox(
            "🌐 Auto-detect language (English/Malayalam/Hybrid)", 
            value=True,
            disabled=not TESSERACT_AVAILABLE,
            help="Automatically detect and optimize OCR for English, Malayalam, or mixed content" + 
                 ("" if TESSERACT_AVAILABLE else " (Requires Tesseract OCR)")
        )
    with col2:
        show_ocr_details = st.checkbox(
            "📊 Show detailed processing analysis", 
            value=True,
            help="Display language analysis, confidence scores, and processing details"
        )

    # File Upload Section
    st.markdown("""
    <div class="feature-section" style="margin-bottom:2rem;">
        <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">📁</span>Select Files
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose file(s) to upload (supports images, PDFs, documents)",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF (text & scanned), Images (JPG, PNG, TIFF), Word documents, Text files"
    )

    # Batch Processing Configuration
    st.markdown("""
    <div class="feature-section" style="margin-bottom:2rem;">
        <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">⚙️</span>Batch Processing Options
        </h3>
        <p style="color:#625B71;margin-bottom:1.5rem;font-style:italic;">Settings applied to all selected files</p>
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
                    
                    # Display summary and feedback options
                    if summary and summary != "(Summarization skipped)":
                        st.markdown("### 📝 Generated Summary")
                        st.info(summary)
                        
                        # Enhanced Feedback section with modern design
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
                            
                            # Like/Dislike buttons with modern styling
                            like_col, dislike_col = st.columns(2)
                            with like_col:
                                if st.button("👍 Like", key=f"like_{uploaded_file.name}", help="This summary is helpful and accurate", use_container_width=True):
                                    st.session_state[f"feedback_{uploaded_file.name}"] = {"type": "like", "content": ""}
                                    st.success("✅ Thank you for your positive feedback!")
                            
                            with dislike_col:
                                if st.button("👎 Dislike", key=f"dislike_{uploaded_file.name}", help="This summary needs improvement", use_container_width=True):
                                    st.session_state[f"feedback_{uploaded_file.name}"] = {"type": "dislike", "content": ""}
                                    st.success("✅ Thank you for your feedback! We'll work to improve our summaries.")
                        
                        with col2:
                            st.markdown("<h5 style='color:var(--material-primary);margin-bottom:12px;font-weight:600;'>Detailed Feedback</h5>", unsafe_allow_html=True)
                            
                            # Text feedback input with modern styling
                            feedback_text = st.text_area(
                                "Share your thoughts (optional):",
                                placeholder="What could be improved about this summary? Any specific suggestions?",
                                key=f"feedback_text_{uploaded_file.name}",
                                height=80,
                                help="Your detailed feedback helps us improve our AI models"
                            )
                            
                            if st.button("📝 Submit Feedback", key=f"text_feedback_{uploaded_file.name}", help="Submit detailed feedback", use_container_width=True):
                                if feedback_text.strip():
                                    st.session_state[f"feedback_{uploaded_file.name}"] = {"type": "text", "content": feedback_text}
                                    st.success("✅ Thank you for your detailed feedback!")
                                else:
                                    st.warning("⚠️ Please enter some text feedback before submitting.")
                
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
                saved_document = db.add_document(document_data, user_info)
                
                # Send real-time alert for document upload (optional, non-blocking)
                if saved_document and ALERTS_AVAILABLE:
                    try:
                        send_document_upload_alert(saved_document, user_info)
                        print(f"📢 Real-time alert sent for document upload: {saved_document.get('filename')}")
                    except Exception as e:
                        print(f"⚠️ Failed to send upload alert (continuing): {e}")
                        # Continue without alerts - don't fail the upload
                
                # Handle feedback if any was submitted
                feedback_key = f"feedback_{uploaded_file.name}"
                if feedback_key in st.session_state:
                    feedback_data = st.session_state[feedback_key]
                    
                    # Get the document ID from the saved document
                    if saved_document and "id" in saved_document:
                        document_id = saved_document["id"]
                        
                        # Save feedback to database
                        feedback_result = db.add_feedback(
                            document_id=document_id,
                            feedback_type=feedback_data["type"],
                            feedback_content=feedback_data["content"],
                            user_info=user_info
                        )
                        
                        if feedback_result["success"]:
                            st.info(f"✅ Feedback saved for document: {feedback_data['type']}")
                            
                            # Send real-time alert for feedback (optional, non-blocking)
                            if ALERTS_AVAILABLE:
                                try:
                                    send_feedback_alert(
                                        document_id, 
                                        {
                                            "type": feedback_data["type"],
                                            "user_name": user_info.get('name', 'Unknown'),
                                            "text": feedback_data.get("content", "")
                                        },
                                        saved_document.get('filename', 'Unknown Document')
                                    )
                                    print(f"📢 Real-time feedback alert sent for document: {saved_document.get('filename')}")
                                except Exception as e:
                                    print(f"⚠️ Failed to send feedback alert (continuing): {e}")
                                    # Continue without alerts - don't fail the feedback submission
                        else:
                            st.warning(f"⚠️ Could not save feedback: {feedback_result['error']}")
                    
                    # Clear the feedback from session state
                    del st.session_state[feedback_key]
                
                st.success(f"✅ Document {file_path.name} processed and saved successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                import traceback
                with st.expander("🐛 Debug Information"):
                    st.code(traceback.format_exc())

        st.balloons()  # Celebration for successful uploads!

    # Recent Uploads Section with Preview
    st.markdown("""
    <div class="feature-section" style="margin-top:2rem;">
        <h3 style="color:var(--material-primary);font-weight:600;margin-bottom:1rem;display:flex;align-items:center;">
            <span style="margin-right:0.5rem;">📚</span>Recent Uploads
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        documents = db.load_data()
        recent_docs = sorted(documents, key=lambda x: x["upload_date"], reverse=True)[:5]
        if recent_docs:
            for doc in recent_docs:
                # Create expandable card for each recent document
                with st.expander(f"📄 {doc['filename']} - {doc.get('document_type', 'Unknown')} ({doc['upload_date'][:10]})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Type:** {doc.get('document_type', 'Unknown')}")
                        st.markdown(f"**Priority:** {doc.get('priority', 'Low')}")
                        st.markdown(f"**Size:** {doc.get('file_size_mb', 'Unknown')} MB")
                        if doc.get('summary'):
                            st.markdown("**Summary:**")
                            # Clean HTML from summary
                            import re
                            import html
                            clean_summary = re.sub(r'<[^>]+>', '', doc.get('summary', ''))
                            clean_summary = html.escape(clean_summary)
                            st.write(clean_summary[:300] + "..." if len(clean_summary) > 300 else clean_summary)
                    
                    with col2:
                        if st.button("👁️ Preview", key=f"preview_upload_{doc['id']}", help="Preview document content"):
                            show_upload_preview(doc)
                        
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
                                key=f"download_upload_{doc['id']}"
                            )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:2rem;color:#625B71;">
                <div style="font-size:2rem;margin-bottom:1rem;">📄</div>
                <h3 style="color:var(--material-primary);">No documents uploaded yet</h3>
                <p>Upload your first document to get started!</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error loading recent documents: {str(e)}")

def show_upload_preview(doc):
    """Display document content preview"""
    from pathlib import Path
    
    file_path = Path(f"/Users/ching/Desktop/KochiMetro_DocuTrack/uploads/{doc['filename']}")
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
                        for page in pdf_reader.pages[:2]:  # Show first 2 pages only
                            text_content += page.extract_text() + "\n"
                    
                    if text_content.strip():
                        st.text_area("📄 PDF Content:", text_content[:1500] + "..." if len(text_content) > 1500 else text_content, height=250, disabled=True)
                    else:
                        st.warning("No text could be extracted from PDF")
                        if doc.get('content'):
                            content_preview = doc['content'][:1500] + "..." if len(doc['content']) > 1500 else doc['content']
                            st.text_area("🔍 OCR Content:", content_preview, height=250, disabled=True)
                except ImportError:
                    st.warning("PyPDF2 not available for PDF preview")
                    if doc.get('content'):
                        content_preview = doc['content'][:1500] + "..." if len(doc['content']) > 1500 else doc['content']
                        st.text_area("🔍 Stored Content:", content_preview, height=250, disabled=True)
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
            
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # Display image
                st.image(str(file_path), caption=doc['filename'], use_column_width=True)
                if doc.get('content'):
                    content_preview = doc['content'][:800] + "..." if len(doc['content']) > 800 else doc['content']
                    st.text_area("🔍 OCR Text:", content_preview, height=150, disabled=True)
            
            elif file_ext == '.txt':
                # Display text file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                content_preview = content[:1500] + "..." if len(content) > 1500 else content
                st.text_area("📝 Text Content:", content_preview, height=250, disabled=True)
            
            else:
                # Show stored content for other file types
                if doc.get('content'):
                    content_preview = doc['content'][:1500] + "..." if len(doc['content']) > 1500 else doc['content']
                    st.text_area("📋 Extracted Content:", content_preview, height=250, disabled=True)
                else:
                    st.info("No content preview available for this file type.")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.warning(f"File not found: {doc['filename']}")
        if doc.get('content'):
            content_preview = doc['content'][:1500] + "..." if len(doc['content']) > 1500 else doc['content']
            st.text_area("🔍 Stored Content:", content_preview, height=250, disabled=True)

                        
