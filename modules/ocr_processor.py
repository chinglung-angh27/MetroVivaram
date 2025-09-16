"""
OCR Processing module for extracting text from images and PDFs
"""
import pytesseract
from PIL import Image
import PyPDF2
import io
import streamlit as st
from langdetect import detect
import logging

class OCRProcessor:
    def __init__(self, languages="eng+mal"):
        self.languages = languages
        
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            # If no text found, it might be a scanned PDF
            if not text.strip():
                st.warning("No text found in PDF. This might be a scanned document. OCR processing would be needed.")
                return ""
            
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def extract_text_from_image(self, image_file):
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.languages)
            return text
        except Exception as e:
            st.error(f"Error performing OCR on image: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    def process_document(self, uploaded_file):
        """Main method to process any document type"""
        file_type = uploaded_file.type
        text = ""
        
        if file_type == "application/pdf":
            text = self.extract_text_from_pdf(uploaded_file)
        elif file_type in ["image/jpeg", "image/jpg", "image/png", "image/tiff"]:
            text = self.extract_text_from_image(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = self.extract_text_from_docx(uploaded_file)
        elif file_type == "text/plain":
            text = str(uploaded_file.read(), "utf-8")
        else:
            st.error(f"Unsupported file type: {file_type}")
            return ""
        
        return text
    
    def detect_language(self, text):
        """Detect the primary language of the text"""
        try:
            if not text.strip():
                return "unknown"
            
            detected = detect(text)
            return detected
        except:
            return "unknown"
    
    def get_text_stats(self, text):
        """Get basic statistics about the extracted text"""
        if not text:
            return {"words": 0, "characters": 0, "lines": 0}
        
        words = len(text.split())
        characters = len(text)
        lines = len(text.split('\n'))
        
        return {
            "words": words,
            "characters": characters,
            "lines": lines
        }