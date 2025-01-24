import os
from datetime import datetime
from typing import Optional

def get_pdf_paths(directory: str) -> list:
    """Get all PDF file paths from a directory."""
    if not os.path.exists(directory):
        raise ValueError(f"Directory {directory} does not exist")
    return [os.path.join(directory, file) 
            for file in os.listdir(directory) 
            if file.lower().endswith(".pdf")]

def format_date(date_str: str) -> Optional[str]:
    """Format PDF date string to ISO format."""
    try:
        if date_str.startswith("D:"):
            date_str = date_str[2:14]  # Extract YYYYMMDDHHMM
            return datetime.strptime(date_str, "%Y%m%d%H%M").isoformat()
        return datetime.now().isoformat()
    except (ValueError, AttributeError):
        return datetime.now().isoformat()