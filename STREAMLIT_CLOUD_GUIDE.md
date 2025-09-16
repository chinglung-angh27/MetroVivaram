# MetroVivaram - Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud

### 1. Repository Setup
- ✅ Repository: `chinglung-angh27/MetroVivaram`
- ✅ Main file: `app.py`
- ✅ Requirements: `requirements.txt` (cloud-compatible)
- ✅ System packages: `packages.txt` and `apt.txt` (for Tesseract OCR)

### 2. Cloud-Specific Features
- **Tesseract Auto-Install**: Automatically installs via packages.txt/apt.txt
- **OpenCV Fallback**: Uses PIL-based preprocessing when OpenCV unavailable
- **Error Handling**: Graceful degradation for missing dependencies
- **User Notifications**: Clear status messages for OCR availability

### 3. System Dependencies
The following files ensure Tesseract OCR works on Streamlit Cloud:
- `packages.txt`: System packages (tesseract-ocr, language packs)
- `apt.txt`: Alternative package installation method
- `requirements.txt`: Python dependencies

### 4. Deployment Steps
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `chinglung-angh27/MetroVivaram`
4. Set main file: `app.py`
5. Deploy! (Tesseract will be installed automatically)

### 5. Features Available on Cloud
- ✅ **Document Upload**: PDF, Image, Word document processing
- ✅ **OCR Processing**: Full text extraction with language detection
- ✅ **Multi-Language**: English and Malayalam support via Tesseract
- ✅ **Document Management**: Search, classify, and organize documents
- ✅ **Material UI**: Modern, responsive interface
- ✅ **Image Preprocessing**: PIL-based (OpenCV features gracefully disabled)

### 6. Local vs Cloud Comparison
| Feature | Local | Cloud |
|---------|-------|-------|
| OCR Accuracy | High (OpenCV + PIL) | High (PIL + Tesseract) |
| Tesseract OCR | ✅ | ✅ (Auto-installed) |
| Image Processing | Advanced (OpenCV) | Basic (PIL) |
| Performance | Fast | Good |
| All Other Features | ✅ | ✅ |

### 7. Troubleshooting
- **Tesseract Errors**: Now handled with auto-installation via packages.txt
- **OCR Unavailable**: App shows clear status and continues with text-based PDFs
- **Memory Limits**: Large PDF processing may be limited on free tier
- **Build Issues**: Check logs for package installation status

### 8. Performance Tips
- Upload files < 10MB for best performance on free tier
- Text-based PDFs process faster than scanned images
- Enable batch processing for multiple files
- Use the detailed analysis view to monitor OCR performance

---

**Your MetroVivaram app is now fully cloud-ready with automatic Tesseract installation! 🌐**