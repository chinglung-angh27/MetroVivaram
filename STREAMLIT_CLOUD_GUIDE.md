# MetroVivaram - Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud

### 1. Repository Setup
- ✅ Repository: `chinglung-angh27/MetroVivaram`
- ✅ Main file: `app.py`
- ✅ Requirements: `requirements.txt` (cloud-compatible)

### 2. Cloud-Specific Features
- **OpenCV Fallback**: Automatically uses PIL-based preprocessing when OpenCV is unavailable
- **Error Handling**: Graceful degradation for missing dependencies
- **Optimized**: Lightweight requirements for faster cloud deployment

### 3. Environment Variables (Optional)
No environment variables required - the app runs with default settings.

### 4. Deployment Steps
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `chinglung-angh27/MetroVivaram`
4. Set main file: `app.py`
5. Deploy!

### 5. Features Available on Cloud
- ✅ **Document Upload**: PDF, Image, Word document processing
- ✅ **OCR Processing**: Text extraction with language detection
- ✅ **Multi-Language**: English and Malayalam support
- ✅ **Document Management**: Search, classify, and organize documents
- ✅ **Material UI**: Modern, responsive interface
- ⚠️ **Image Preprocessing**: Basic PIL-only (OpenCV features disabled)

### 6. Local vs Cloud Differences
| Feature | Local | Cloud |
|---------|-------|-------|
| OCR Accuracy | High (OpenCV + PIL) | Good (PIL only) |
| Image Processing | Advanced | Basic |
| Performance | Fast | Good |
| All Other Features | ✅ | ✅ |

### 7. Troubleshooting
- **Import Errors**: All dependencies are now optional with fallbacks
- **Tesseract**: Cloud platform provides Tesseract by default
- **Memory**: Large PDF processing may be limited on free tier

### 8. Performance Tips
- Upload files < 10MB for best performance
- Use text-based PDFs when possible
- Enable batch processing for multiple files

---

**Your MetroVivaram app is now fully cloud-ready! 🌐**