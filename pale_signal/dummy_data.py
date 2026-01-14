"""
Dummy data generator for pale-signal.
Provides sample data for testing and demonstration.
"""

from datetime import datetime, timedelta
import random


def generate_dummy_data(days=30):
    """
    Generate dummy data for testing.
    Returns a list of entries for the last N days.
    """
    entries = []
    today = datetime.now()
    
    # Social types for variety
    social_types = ["none", "online", "casual", "meaningful", "deep"]
    
    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        timestamp = (today - timedelta(days=i)).isoformat()
        
        # Generate realistic-looking data with some patterns
        base_sleep = 7.0 + random.uniform(-1.5, 1.5)
        base_focus = 6 + random.randint(-2, 3)
        base_mood = 6 + random.randint(-2, 3)
        
        # Correlate work hours inversely with sleep
        work_hours = 8.0 - (base_sleep - 7.0) + random.uniform(-1, 1)
        work_hours = max(4.0, min(12.0, work_hours))
        
        entry = {
            "date": date,
            "sleep_hours": round(max(4.0, min(10.0, base_sleep)), 1),
            "focus": max(1, min(10, base_focus)),
            "mood": max(1, min(10, base_mood)),
            "work_hours": round(work_hours, 1),
            "social": random.choice(social_types),
            "timestamp": timestamp
        }
        entries.append(entry)
    
    return entries
