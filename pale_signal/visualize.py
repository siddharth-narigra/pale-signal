"""
Visualization module for pale-signal.
Creates clean, minimal plots using matplotlib.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid Tcl/Tk issues
import matplotlib.pyplot as plt
from typing import List, Dict, Optional


# Store plots in user's home directory
OUTPUT_DIR = Path.home() / ".pale-signal" / "output"


# Metric display names and thresholds
METRIC_CONFIG = {
    "sleep_hours": {
        "label": "Sleep (hours)",
        "threshold": 6.0,
        "threshold_label": "Recommended minimum"
    },
    "focus": {
        "label": "Focus (1-10)",
        "threshold": 5.0,
        "threshold_label": "Midpoint"
    },
    "mood": {
        "label": "Mood (1-10)",
        "threshold": 5.0,
        "threshold_label": "Midpoint"
    },
    "work_hours": {
        "label": "Work (hours)",
        "threshold": 8.0,
        "threshold_label": "Standard workday"
    },
    "social": {
        "label": "Social Interaction Type",
        "threshold": None,
        "threshold_label": None
    }
}


def plot_metric(entries: List[Dict], metric: str, show: bool = True):
    """
    Create a line plot for a single metric over time.
    
    Args:
        entries: List of data entries (sorted newest first)
        metric: Name of the metric to plot
        show: Whether to display the plot immediately
    """
    if not entries:
        print("No data to plot.")
        return
    
    if metric not in METRIC_CONFIG:
        print(f"Unknown metric: {metric}")
        return
    
    # Reverse entries to show oldest to newest on x-axis
    entries = list(reversed(entries))
    
    # Extract data
    dates = [entry["date"] for entry in entries]
    
    # For social metric, convert categories to numbers for plotting
    if metric == "social":
        social_map = {"none": 0, "online": 1, "casual": 2, "meaningful": 3, "deep": 4}
        values = [social_map.get(entry[metric], 0) for entry in entries]
    else:
        values = [entry[metric] for entry in entries]
    
    # Calculate rolling average (7-day)
    rolling_avg = []
    for i in range(len(values)):
        start_idx = max(0, i - 6)
        window = values[start_idx:i+1]
        rolling_avg.append(sum(window) / len(window))
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot main line
    ax.plot(dates, values, marker='o', linewidth=2, markersize=6, 
            label=METRIC_CONFIG[metric]["label"], color='#2563eb')
    
    # Plot rolling average
    if len(entries) >= 7:
        ax.plot(dates, rolling_avg, linestyle='--', linewidth=1.5, 
                label='7-day average', color='#dc2626', alpha=0.7)
    
    # Add threshold line if applicable
    threshold = METRIC_CONFIG[metric]["threshold"]
    if threshold is not None:
        ax.axhline(y=threshold, color='#64748b', linestyle=':', linewidth=1.5,
                   label=METRIC_CONFIG[metric]["threshold_label"])
    
    # Styling
    ax.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax.set_ylabel(METRIC_CONFIG[metric]["label"], fontsize=11, fontweight='bold')
    ax.set_title(f'{METRIC_CONFIG[metric]["label"]} Over Time', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # For social metric, add category labels on y-axis
    if metric == "social":
        ax.set_yticks([0, 1, 2, 3, 4])
        ax.set_yticklabels(['none', 'online', 'casual', 'meaningful', 'deep'])
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save to file instead of showing (avoids backend issues)
    filename = os.path.join(OUTPUT_DIR, f"{metric}_plot.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filename
