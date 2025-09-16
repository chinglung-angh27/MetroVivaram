"""
Advanced OCR Processing module for extracting text from images and PDFs
Supports English, Malayalam, and hybrid content detection with Tesseract OCR
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import PyPDF2
from pdf2image import convert_from_bytes
import io
import streamlit as st
from langdetect import detect, LangDetectException
import logging
import cv2
import numpy as np
import re
from typing import Dict, List, Tuple, Optional

class AdvancedOCRProcessor:
    def __init__(self):
        """Initialize OCR processor with multi-language support"""
        self.supported_languages = {
            'english': 'eng',
            'malayalam': 'mal',
            'hybrid': 'eng+mal'
        }
        self.logger = logging.getLogger(__name__)
        
    def detect_content_language(self, text: str) -> Dict[str, any]:
        """
        Detect language content and provide confidence scores
        """
        if not text.strip():
            return {
                'primary_language': 'unknown',
                'languages_detected': [],
                'is_hybrid': False,
                'confidence': 0.0
            }
        
        # Check for Malayalam Unicode range
        malayalam_pattern = r'[\u0d00-\u0d7f]+'
        malayalam_matches = re.findall(malayalam_pattern, text)
        has_malayalam = len(malayalam_matches) > 0
        
        # Check for English content
        english_pattern = r'[a-zA-Z]+'
        english_matches = re.findall(english_pattern, text)
        has_english = len(english_matches) > 0
        
        # Calculate language percentages
        total_chars = len(text.replace(' ', ''))
        malayalam_chars = sum(len(match) for match in malayalam_matches)
        english_chars = sum(len(match) for match in english_matches)
        
        malayalam_percentage = (malayalam_chars / total_chars * 100) if total_chars > 0 else 0
        english_percentage = (english_chars / total_chars * 100) if total_chars > 0 else 0
        
        # Determine primary language and hybrid status
        is_hybrid = has_malayalam and has_english and min(malayalam_percentage, english_percentage) > 10
        
        if is_hybrid:
            primary_language = 'hybrid'
            languages_detected = ['english', 'malayalam']
            confidence = min(malayalam_percentage, english_percentage) / 100
        elif malayalam_percentage > english_percentage:
            primary_language = 'malayalam'
            languages_detected = ['malayalam']
            confidence = malayalam_percentage / 100
        elif english_percentage > 0:
            primary_language = 'english'
            languages_detected = ['english']
            confidence = english_percentage / 100
        else:
            # Fallback to langdetect
            try:
                detected_lang = detect(text)
                primary_language = 'english' if detected_lang == 'en' else 'unknown'
                languages_detected = [primary_language] if primary_language != 'unknown' else []
                confidence = 0.7
            except LangDetectException:
                primary_language = 'unknown'
                languages_detected = []
                confidence = 0.0
        
        return {
            'primary_language': primary_language,
            'languages_detected': languages_detected,
            'is_hybrid': is_hybrid,
            'confidence': confidence,
            'malayalam_percentage': malayalam_percentage,
            'english_percentage': english_percentage
        }
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(thresh)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(1.2)
        
        return processed_image
    
    def extract_text_from_image(self, image_file, auto_detect_language: bool = True) -> Dict[str, any]:
        """
        Extract text from image using OCR with automatic language detection
        """
        try:
            # Load and preprocess image
            image = Image.open(image_file)
            processed_image = self.preprocess_image(image)
            
            results = {}
            
            if auto_detect_language:
                # Try different language combinations
                lang_configs = [
                    ('hybrid', 'eng+mal'),
                    ('english', 'eng'),
                    ('malayalam', 'mal')
                ]
                
                best_result = None
                best_confidence = 0
                
                for lang_name, lang_code in lang_configs:
                    try:
                        # Custom OCR config for better accuracy
                        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\u0d00-\u0d7f\u0020\u002e\u002c\u003a\u003b\u0028\u0029\u002d\u002f'
                        
                        text = pytesseract.image_to_string(
                            processed_image, 
                            lang=lang_code,
                            config=custom_config
                        )
                        
                        if text.strip():
                            lang_analysis = self.detect_content_language(text)
                            
                            # Calculate overall confidence
                            ocr_confidence = len(text.strip()) / 100  # Simple heuristic
                            total_confidence = (lang_analysis['confidence'] + min(ocr_confidence, 1.0)) / 2
                            
                            if total_confidence > best_confidence:
                                best_confidence = total_confidence
                                best_result = {
                                    'text': text,
                                    'language_analysis': lang_analysis,
                                    'ocr_language': lang_name,
                                    'confidence': total_confidence
                                }
                    
                    except Exception as e:
                        self.logger.warning(f"OCR failed for {lang_name}: {str(e)}")
                        continue
                
                if best_result:
                    results = best_result
                else:
                    # Fallback to basic English OCR
                    text = pytesseract.image_to_string(processed_image, lang='eng')
                    lang_analysis = self.detect_content_language(text)
                    results = {
                        'text': text,
                        'language_analysis': lang_analysis,
                        'ocr_language': 'english',
                        'confidence': 0.5
                    }
            else:
                # Use hybrid language model by default
                text = pytesseract.image_to_string(processed_image, lang='eng+mal')
                lang_analysis = self.detect_content_language(text)
                results = {
                    'text': text,
                    'language_analysis': lang_analysis,
                    'ocr_language': 'hybrid',
                    'confidence': lang_analysis['confidence']
                }
            
            # Add text statistics and extraction method
            results['text_stats'] = self.get_text_stats(results['text'])
            results['extraction_method'] = 'ocr_image'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing OCR on image: {str(e)}")
            return {
                'text': '',
                'language_analysis': self.detect_content_language(''),
                'ocr_language': 'unknown',
                'confidence': 0.0,
                'text_stats': self.get_text_stats(''),
                'extraction_method': 'error',
                'error': str(e)
            }
    
    def extract_text_from_pdf(self, pdf_file, auto_detect_language: bool = True) -> Dict[str, any]:
        """
        Extract text from PDF file - handles both text-based and scanned PDFs
        """
        try:
            # First, try to extract text directly (for text-based PDFs)
            pdf_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            direct_text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                direct_text += page.extract_text() + "\n"
            
            # If we got meaningful text, analyze it
            if direct_text.strip() and len(direct_text.strip()) > 50:
                lang_analysis = self.detect_content_language(direct_text)
                return {
                    'text': direct_text,
                    'language_analysis': lang_analysis,
                    'extraction_method': 'direct_text',
                    'confidence': lang_analysis['confidence'],
                    'text_stats': self.get_text_stats(direct_text)
                }
            
            # If no text or very little text, treat as scanned PDF
            pdf_file.seek(0)  # Reset file pointer
            pdf_bytes = pdf_file.read()
            
            # Convert PDF pages to images
            try:
                images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=3)  # Limit to first 3 pages for performance
            except Exception as e:
                return {
                    'text': direct_text,  # Return whatever we got
                    'language_analysis': self.detect_content_language(direct_text),
                    'extraction_method': 'direct_text_fallback',
                    'confidence': 0.3,
                    'text_stats': self.get_text_stats(direct_text),
                    'error': f"PDF to image conversion failed: {str(e)}"
                }
            
            # Perform OCR on each page
            all_text = ""
            total_confidence = 0
            page_count = 0
            
            for i, image in enumerate(images):
                # Convert to bytes for processing
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                
                # Perform OCR on this page
                page_result = self.extract_text_from_image(img_byte_arr, auto_detect_language)
                
                if page_result['text'].strip():
                    all_text += f"\n--- Page {i+1} ---\n" + page_result['text'] + "\n"
                    total_confidence += page_result['confidence']
                    page_count += 1
            
            # Calculate average confidence
            avg_confidence = total_confidence / page_count if page_count > 0 else 0
            
            # Analyze the combined text
            lang_analysis = self.detect_content_language(all_text)
            
            return {
                'text': all_text,
                'language_analysis': lang_analysis,
                'extraction_method': 'ocr_scanned_pdf',
                'confidence': avg_confidence,
                'pages_processed': page_count,
                'text_stats': self.get_text_stats(all_text)
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            return {
                'text': '',
                'language_analysis': self.detect_content_language(''),
                'extraction_method': 'error',
                'confidence': 0.0,
                'text_stats': self.get_text_stats(''),
                'error': str(e)
            }
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            try:
                from docx import Document
            except ImportError:
                st.warning("python-docx not installed. Installing...")
                import subprocess
                subprocess.check_call(["pip", "install", "python-docx"])
                from docx import Document
            
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            lang_analysis = self.detect_content_language(text)
            return {
                'text': text,
                'language_analysis': lang_analysis,
                'extraction_method': 'docx_direct',
                'confidence': lang_analysis['confidence'],
                'text_stats': self.get_text_stats(text)
            }
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX: {str(e)}")
            return {
                'text': '',
                'language_analysis': self.detect_content_language(''),
                'extraction_method': 'error',
                'confidence': 0.0,
                'text_stats': self.get_text_stats(''),
                'error': str(e)
            }
    
    def process_document(self, uploaded_file, auto_detect_language: bool = True) -> Dict[str, any]:
        """
        Main method to process any document type with advanced OCR
        """
        file_type = uploaded_file.type
        filename = uploaded_file.name.lower()
        
        try:
            if file_type == "application/pdf" or filename.endswith('.pdf'):
                return self.extract_text_from_pdf(uploaded_file, auto_detect_language)
            elif file_type in ["image/jpeg", "image/jpg", "image/png", "image/tiff"] or any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']):
                return self.extract_text_from_image(uploaded_file, auto_detect_language)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename.endswith('.docx'):
                return self.extract_text_from_docx(uploaded_file)
            elif file_type == "text/plain" or filename.endswith('.txt'):
                text = str(uploaded_file.read(), "utf-8")
                lang_analysis = self.detect_content_language(text)
                return {
                    'text': text,
                    'language_analysis': lang_analysis,
                    'extraction_method': 'plain_text',
                    'confidence': 1.0,
                    'text_stats': self.get_text_stats(text)
                }
            else:
                return {
                    'text': '',
                    'language_analysis': self.detect_content_language(''),
                    'extraction_method': 'unsupported',
                    'confidence': 0.0,
                    'text_stats': self.get_text_stats(''),
                    'error': f"Unsupported file type: {file_type}"
                }
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            return {
                'text': '',
                'language_analysis': self.detect_content_language(''),
                'extraction_method': 'error',
                'confidence': 0.0,
                'text_stats': self.get_text_stats(''),
                'error': str(e)
            }
    
    def get_text_stats(self, text: str) -> Dict[str, int]:
        """Get comprehensive statistics about the extracted text"""
        if not text:
            return {"words": 0, "characters": 0, "lines": 0, "sentences": 0}
        
        words = len(text.split())
        characters = len(text)
        lines = len(text.split('\n'))
        
        # Count sentences (simple heuristic)
        sentences = len(re.split(r'[.!?]+', text.strip()))
        
        return {
            "words": words,
            "characters": characters,
            "lines": lines,
            "sentences": sentences
        }
    
    def get_processing_summary(self, result: Dict[str, any]) -> str:
        """
        Generate a human-readable summary of the OCR processing
        """
        if 'error' in result:
            return f"❌ Processing failed: {result['error']}"
        
        lang_info = result['language_analysis']
        stats = result['text_stats']
        
        # Language summary
        if lang_info['is_hybrid']:
            lang_summary = f"🌐 Hybrid content (English: {lang_info['english_percentage']:.1f}%, Malayalam: {lang_info['malayalam_percentage']:.1f}%)"
        else:
            lang_summary = f"🗣️ Primary language: {lang_info['primary_language'].title()}"
        
        # Stats summary
        stats_summary = f"📊 {stats['words']} words, {stats['characters']} characters, {stats['lines']} lines"
        
        # Confidence summary
        confidence_emoji = "🟢" if result['confidence'] > 0.8 else "🟡" if result['confidence'] > 0.5 else "🔴"
        confidence_summary = f"{confidence_emoji} Confidence: {result['confidence']:.1%}"
        
        # Method summary
        extraction_method = result.get('extraction_method', 'ocr_processing')
        method_summary = f"⚙️ Method: {extraction_method.replace('_', ' ').title()}"
        
        return f"{lang_summary}\n{stats_summary}\n{confidence_summary}\n{method_summary}"


# Backward compatibility - maintain old class name as alias
class OCRProcessor(AdvancedOCRProcessor):
    """Backward compatibility alias for existing code"""
    def __init__(self, languages="eng+mal"):
        super().__init__()
        self.languages = languages
    
    def extract_text_from_pdf(self, pdf_file):
        """Backward compatible method"""
        result = super().extract_text_from_pdf(pdf_file)
        return result.get('text', '')
    
    def extract_text_from_image(self, image_file):
        """Backward compatible method"""
        result = super().extract_text_from_image(image_file)
        return result.get('text', '')
    
    def detect_language(self, text):
        """Backward compatible method"""
        lang_analysis = self.detect_content_language(text)
        return lang_analysis['primary_language']