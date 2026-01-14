"""
Data persistence layer for pale-signal.
Manages JSON file operations and data validation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Store data in user's home directory
DATA_DIR = Path.home() / ".pale-signal"
DATA_FILE = DATA_DIR / "data.json"


def _init_data_file():
    """Initialize data.json if it doesn't exist."""
    # Create directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w') as f:
            json.dump({"entries": []}, f, indent=2)


def load_data() -> Dict:
    """Load all data from JSON file."""
    _init_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data: Dict):
    """Save data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def validate_entry(entry: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate a single data entry.
    Returns (is_valid, error_message).
    """
    required_fields = ["date", "sleep_hours", "focus", "mood", "work_hours", "social", "timestamp"]
    
    # Check all fields present
    for field in required_fields:
        if field not in entry:
            return False, f"Missing required field: {field}"
    
    # Validate date format
    try:
        datetime.strptime(entry["date"], "%Y-%m-%d")
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format"
    
    # Validate timestamp format
    try:
        datetime.fromisoformat(entry["timestamp"])
    except (ValueError, TypeError):
        return False, "Timestamp must be in ISO format"
    
    # Validate types and ranges
    try:
        sleep_hours = float(entry["sleep_hours"])
        if sleep_hours < 0 or sleep_hours > 24:
            return False, "sleep_hours must be between 0 and 24"
        
        focus = int(entry["focus"])
        if focus < 1 or focus > 10:
            return False, "focus must be between 1 and 10"
        
        mood = int(entry["mood"])
        if mood < 1 or mood > 10:
            return False, "mood must be between 1 and 10"
        
        work_hours = float(entry["work_hours"])
        if work_hours < 0 or work_hours > 24:
            return False, "work_hours must be between 0 and 24"
        
        social = entry["social"]
        valid_social = ["none", "online", "casual", "meaningful", "deep"]
        if social not in valid_social:
            return False, f"social must be one of: {', '.join(valid_social)}"
            
    except (ValueError, TypeError) as e:
        return False, f"Invalid data type: {str(e)}"
    
    return True, None


def add_entry(entry: Dict) -> tuple[bool, Optional[str]]:
    """
    Add a new entry to the data store.
    Returns (success, error_message).
    """
    # Validate entry
    is_valid, error = validate_entry(entry)
    if not is_valid:
        return False, error
    
    # Load existing data
    data = load_data()
    
    # Check for duplicate date
    for existing in data["entries"]:
        if existing["date"] == entry["date"]:
            return False, f"Entry for {entry['date']} already exists"
    
    # Add entry and save
    data["entries"].append(entry)
    
    # Sort by date (newest first)
    data["entries"].sort(key=lambda x: x["date"], reverse=True)
    
    save_data(data)
    return True, None


def get_entries(days: Optional[int] = None) -> List[Dict]:
    """
    Get entries, optionally limited to the last N days.
    Returns entries sorted by date (newest first).
    """
    data = load_data()
    entries = data["entries"]
    
    if days is not None and days > 0:
        return entries[:days]
    
    return entries


def get_entry_by_date(date: str) -> Optional[Dict]:
    """Get a specific entry by date."""
    data = load_data()
    for entry in data["entries"]:
        if entry["date"] == date:
            return entry
    return None
