"""
document_utils.py
-----------------
Cryptographic hashing and document validation utilities for the
Blockchain-Based Secure Document Verification System.
"""

import hashlib
import os
import uuid
from datetime import datetime
from typing import Tuple

# Supported file extensions for document integrity verification
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 Megabytes safety ceiling


def calculate_sha256(file_bytes: bytes) -> str:
    """
    Calculate the SHA-256 cryptographic hash of the provided byte stream.
    
    Args:
        file_bytes: Raw binary bytes of the document.
        
    Returns:
        Hexadecimal string representation of the 256-bit hash (64 characters).
    """
    if not isinstance(file_bytes, (bytes, bytearray)):
        raise TypeError("Input data must be bytes or bytearray.")
    return hashlib.sha256(file_bytes).hexdigest()


def generate_document_id(prefix: str = "DOC") -> str:
    """
    Generate a human-readable unique document identifier.
    
    Format: DOC-YYYYMMDD-<6_HEX_CHARS>
    Example: DOC-20261020-F7A9B2
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_part}-{random_part}"


def get_file_extension(filename: str) -> str:
    """Extract and normalize the file extension in lower case."""
    _, ext = os.path.splitext(filename or "")
    return ext.lower()


def is_supported_file_type(filename: str) -> bool:
    """Check if the filename has an allowed extension."""
    ext = get_file_extension(filename)
    return ext in SUPPORTED_EXTENSIONS


def validate_document(
    filename: str, file_bytes: bytes, max_size_bytes: int = MAX_FILE_SIZE_BYTES
) -> Tuple[bool, str]:
    """
    Validate the uploaded document against size, emptiness, and file type criteria.
    
    Returns:
        Tuple of (is_valid: bool, error_message: str).
    """
    if not filename or not filename.strip():
        return False, "File must have a valid non-empty name."
    
    if file_bytes is None or len(file_bytes) == 0:
        return False, "The uploaded file is empty (0 bytes). Cannot generate hash."
    
    if len(file_bytes) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return False, f"File exceeds maximum allowed size of {max_mb:.0f} MB."
    
    if not is_supported_file_type(filename):
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        return False, f"Unsupported file type '{get_file_extension(filename)}'. Supported formats: {allowed}."
    
    return True, ""


def format_file_size(size_bytes: int) -> str:
    """Format bytes into a human-readable string (B, KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def compare_hashes(hash_a: str, hash_b: str) -> bool:
    """
    Compare two SHA-256 hashes safely (case-insensitive and stripped).
    """
    if not hash_a or not hash_b:
        return False
    return hash_a.strip().lower() == hash_b.strip().lower()
