"""
Simple file-based database for storing document metadata and summaries
"""
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
from config import DATA_DIR

class DocumentDatabase:
    def __init__(self):
        self.db_file = DATA_DIR / "documents.json"
        self.audit_file = DATA_DIR / "audit_log.json"
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create database files if they don't exist"""
        if not self.db_file.exists():
            self.save_data([])
        
        if not self.audit_file.exists():
            self.save_audit_log([])
    
    def load_data(self):
        """Load documents from JSON file"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading database: {str(e)}")
            return []
    
    def save_data(self, data):
        """Save documents to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving to database: {str(e)}")
    
    def load_audit_log(self):
        """Load audit log from JSON file"""
        try:
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return []
    
    def save_audit_log(self, data):
        """Save audit log to JSON file"""
        try:
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving audit log: {str(e)}")
    
    def add_document(self, document_data, user_info, parent_doc_id=None):
        """Add a new document or new version to the database, with permissions"""
        documents = self.load_data()
        now = datetime.now()
        if parent_doc_id:
            doc_id = parent_doc_id
            version_number = self.get_next_version_number(doc_id)
        else:
            doc_id = f"DOC_{now.strftime('%Y%m%d_%H%M%S')}_{len(documents)}"
            version_number = 1
        # Universal permissions: all users can access all features
        all_roles = ["Engineer", "Finance", "HR", "Station Controller", "Compliance Officer"]
        default_permissions = {
            "view": all_roles,
            "edit": all_roles,
            "approve": all_roles,
            "delete": all_roles
        }
        document_record = {
            "id": doc_id,
            "filename": document_data["filename"],
            "file_type": document_data["file_type"],
            "upload_date": now.isoformat(),
            "uploaded_by": user_info["name"],
            "uploader_role": user_info["role"],
            "document_type": document_data["document_type"],
            "classification_confidence": document_data.get("classification_confidence", 0),
            "summary": document_data["summary"],
            "action_items": document_data.get("action_items", []),
            "deadlines": document_data.get("deadlines", []),
            "risks": document_data.get("risks", []),
            "priority": document_data.get("priority", "Medium"),
            "language": document_data.get("language", "unknown"),
            "text_stats": document_data.get("text_stats", {}),
            "key_information": document_data.get("key_information", {}),
            "file_path": document_data.get("file_path", ""),
            "tags": document_data.get("tags", []),
            "status": "Active",
            "version": version_number,
            "permissions": default_permissions
        }
        self.save_version(doc_id, version_number, document_record)
        documents = [doc for doc in documents if doc["id"] != doc_id]
        documents.append(document_record)
        self.save_data(documents)
        action = "UPLOAD" if version_number == 1 else "NEW_VERSION"
        self.log_activity(action, doc_id, user_info, f"{action} document: {document_data['filename']} (v{version_number})")
        return doc_id

    def save_version(self, doc_id, version_number, document_record):
        """Save a version of a document to a separate file"""
        version_dir = Path("data/versions")
        version_dir.mkdir(parents=True, exist_ok=True)
        version_file = version_dir / f"{doc_id}_v{version_number}.json"
        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(document_record, f, indent=2, ensure_ascii=False)

    def get_next_version_number(self, doc_id):
        """Get the next version number for a document"""
        version_dir = Path("data/versions")
        existing = [f for f in version_dir.glob(f"{doc_id}_v*.json")]
        if not existing:
            return 1
        nums = [int(f.stem.split("_v")[-1]) for f in existing]
        return max(nums) + 1

    def get_version_history(self, doc_id):
        """Return all versions for a document (sorted by version)"""
        version_dir = Path("data/versions")
        files = sorted(version_dir.glob(f"{doc_id}_v*.json"), key=lambda f: int(f.stem.split("_v")[-1]))
        versions = []
        for f in files:
            with open(f, "r", encoding="utf-8") as vf:
                versions.append(json.load(vf))
        return versions

    def restore_version(self, doc_id, version_number, user_info):
        """Restore a specific version as the current version"""
        version_dir = Path("data/versions")
        version_file = version_dir / f"{doc_id}_v{version_number}.json"
        if not version_file.exists():
            raise FileNotFoundError(f"Version {version_number} not found for {doc_id}")
        with open(version_file, "r", encoding="utf-8") as f:
            version_data = json.load(f)
        # Update main db
        documents = self.load_data()
        documents = [doc for doc in documents if doc["id"] != doc_id]
        documents.append(version_data)
        self.save_data(documents)
        self.log_activity("RESTORE_VERSION", doc_id, user_info, f"Restored version {version_number}")
        return True
    
    def get_documents_by_role(self, user_role):
        """Get all documents - role restrictions removed for universal access"""
        documents = self.load_data()
        # Return all active documents regardless of role
        filtered_docs = [
            doc for doc in documents
            if doc["status"] == "Active"
        ]
        return filtered_docs
    
    def search_documents(self, query, user_role=None):
        """Search documents by content, filename, or metadata"""
        documents = self.load_data()
        
        if user_role:
            documents = self.get_documents_by_role(user_role)
        
        query_lower = query.lower()
        results = []
        
        for doc in documents:
            score = 0
            
            # Search in filename
            if query_lower in doc["filename"].lower():
                score += 10
            
            # Search in summary
            if query_lower in doc["summary"].lower():
                score += 8
            
            # Search in document type
            if query_lower in doc["document_type"].lower():
                score += 6
            
            # Search in action items
            for action in doc.get("action_items", []):
                if query_lower in action.lower():
                    score += 5
            
            # Search in risks
            for risk in doc.get("risks", []):
                if query_lower in risk.lower():
                    score += 5
            
            # Search in key information
            for key, value in doc.get("key_information", {}).items():
                if query_lower in str(value).lower():
                    score += 4
            
            if score > 0:
                doc["search_score"] = score
                results.append(doc)
        
        # Sort by relevance score
        results.sort(key=lambda x: x["search_score"], reverse=True)
        
        return results
    
    def get_document_by_id(self, doc_id):
        """Get a specific document by ID"""
        documents = self.load_data()
        for doc in documents:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def log_activity(self, action, doc_id, user_info, details=""):
        """Log user activity for audit purposes"""
        audit_log = self.load_audit_log()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "document_id": doc_id,
            "user_name": user_info["name"],
            "user_role": user_info["role"],
            "details": details,
            "ip_address": "localhost"  # In real app, get actual IP
        }
        
        audit_log.append(log_entry)
        self.save_audit_log(audit_log)
    
    def get_audit_log(self, limit=100):
        """Get recent audit log entries"""
        audit_log = self.load_audit_log()
        return audit_log[-limit:] if len(audit_log) > limit else audit_log
    
    def get_statistics(self):
        """Get database statistics"""
        documents = self.load_data()
        
        if not documents:
            return {
                "total_documents": 0,
                "documents_by_type": {},
                "documents_by_priority": {},
                "recent_uploads": 0
            }
        
        # Count by document type
        type_counts = {}
        priority_counts = {}
        
        for doc in documents:
            doc_type = doc["document_type"]
            priority = doc.get("priority", "Medium")
            
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Count recent uploads (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_count = 0
        
        for doc in documents:
            upload_date = datetime.fromisoformat(doc["upload_date"])
            if upload_date > week_ago:
                recent_count += 1
        
        return {
            "total_documents": len(documents),
            "documents_by_type": type_counts,
            "documents_by_priority": priority_counts,
            "recent_uploads": recent_count
        }