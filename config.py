"""
Configuration settings for KochiMetro DocuTrack
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = BASE_DIR / "sample_data"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
SAMPLE_DIR.mkdir(exist_ok=True)

# Document types and their keywords
DOCUMENT_TYPES = {
    "Invoice": ["invoice", "bill", "payment", "amount", "gst", "tax", "vendor"],
    "Safety Notice": ["safety", "circular", "drill", "emergency", "hazard", "accident", "precaution"],
    "HR Policy": ["policy", "hr", "human resource", "employee", "leave", "attendance", "training"],
    "Job Card": ["job card", "work order", "maintenance", "repair", "task", "assignment"],
    "Engineering Drawing": ["drawing", "blueprint", "design", "specification", "technical", "schematic"],
    "Government Circular": ["government", "circular", "notification", "order", "directive", "compliance"],
    "Operational Report": ["report", "operational", "daily", "weekly", "monthly", "performance", "metrics"]
}

# User roles and their document access
USER_ROLES = {
    "Engineer": ["Safety Notice", "Engineering Drawing", "Job Card", "Operational Report"],
    "Finance": ["Invoice", "Government Circular"],
    "HR": ["HR Policy", "Safety Notice", "Government Circular"],
    "Station Controller": ["Operational Report", "Safety Notice", "Job Card"],
    "Compliance Officer": ["Government Circular", "Safety Notice", "HR Policy"]
}

# Sample users for demo
SAMPLE_USERS = {
    "engineer1": {"name": "Rajesh Kumar", "role": "Engineer", "password": "eng123"},
    "finance1": {"name": "Priya Nair", "role": "Finance", "password": "fin123"},
    "hr1": {"name": "Suresh Menon", "role": "HR", "password": "hr123"},
    "station1": {"name": "Anoop Thomas", "role": "Station Controller", "password": "sta123"},
    "compliance1": {"name": "Maya Pillai", "role": "Compliance Officer", "password": "comp123"}
}

# Languages supported
SUPPORTED_LANGUAGES = ["en", "ml"]  # English and Malayalam

# File size limits (in MB)
MAX_FILE_SIZE = 50

# OCR settings
OCR_LANGUAGES = "eng+mal"  # Tesseract language codes