"""
Document Classification module using keyword-based rules
"""
import re
from config import DOCUMENT_TYPES
from fuzzywuzzy import fuzz
import streamlit as st

class DocumentClassifier:
    def __init__(self):
        self.document_types = DOCUMENT_TYPES
        
    def classify_document(self, text, filename=""):
        """Classify document based on content and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        scores = {}
        
        # Score each document type based on keyword matches
        for doc_type, keywords in self.document_types.items():
            score = 0
            
            # Check keywords in text content
            for keyword in keywords:
                # Exact matches get higher score
                if keyword.lower() in text_lower:
                    score += 10
                
                # Fuzzy matches get lower score
                for word in text_lower.split():
                    if len(word) > 3:  # Only check words longer than 3 chars
                        fuzzy_score = fuzz.ratio(keyword.lower(), word)
                        if fuzzy_score > 80:
                            score += 5
            
            # Check keywords in filename
            for keyword in keywords:
                if keyword.lower() in filename_lower:
                    score += 15  # Filename matches get higher weight
            
            scores[doc_type] = score
        
        # Find the best match
        if not scores or max(scores.values()) == 0:
            return "Unknown", 0, scores
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        return best_type, confidence, scores
    
    def get_classification_details(self, text, filename=""):
        """Get detailed classification information"""
        doc_type, confidence, all_scores = self.classify_document(text, filename)
        
        # Sort scores for display
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "predicted_type": doc_type,
            "confidence": confidence,
            "all_scores": sorted_scores,
            "is_confident": confidence > 20  # Threshold for confidence
        }
    
    def extract_key_information(self, text, doc_type):
        """Extract key information based on document type"""
        key_info = {}
        text_lower = text.lower()
        
        if doc_type == "Invoice":
            # Look for invoice number, amount, date
            invoice_patterns = [
                r'invoice\s*(?:no|number)?\s*:?\s*([A-Z0-9\-/]+)',
                r'bill\s*(?:no|number)?\s*:?\s*([A-Z0-9\-/]+)'
            ]
            amount_patterns = [
                r'(?:total|amount|sum)\s*:?\s*₹?\s*([0-9,]+\.?[0-9]*)',
                r'₹\s*([0-9,]+\.?[0-9]*)'
            ]
            
            for pattern in invoice_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    key_info['invoice_number'] = match.group(1)
                    break
            
            for pattern in amount_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    key_info['amount'] = match.group(1)
                    break
        
        elif doc_type == "Safety Notice":
            # Look for dates, urgency indicators
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})'
            ]
            
            urgency_keywords = ['urgent', 'immediate', 'emergency', 'critical', 'mandatory']
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    key_info['dates'] = matches
                    break
            
            for keyword in urgency_keywords:
                if keyword in text_lower:
                    key_info['urgency'] = keyword
                    break
        
        elif doc_type == "Job Card":
            # Look for job numbers, equipment, dates
            job_patterns = [
                r'job\s*(?:card|no|number)?\s*:?\s*([A-Z0-9\-/]+)',
                r'work\s*order\s*:?\s*([A-Z0-9\-/]+)'
            ]
            
            for pattern in job_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    key_info['job_number'] = match.group(1)
                    break
        
        return key_info