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


def generate_ascii_plot(entries: List[Dict], metric: str, width: int = 60, height: int = 15):
    """
    Generate a simple ASCII plot for terminal display.
    
    Args:
        entries: List of data entries (sorted newest first)
        metric: Name of the metric to plot
        width: Width of the plot in characters
        height: Height of the plot in lines
    """
    if not entries or metric not in METRIC_CONFIG:
        return ""
    
    # Reverse to show oldest to newest
    entries = list(reversed(entries))
    
    # Extract values
    if metric == "social":
        social_map = {"none": 0, "online": 1, "casual": 2, "meaningful": 3, "deep": 4}
        values = [social_map.get(entry[metric], 0) for entry in entries]
    else:
        values = [entry[metric] for entry in entries]
    
    if not values:
        return ""
    
    # Normalize values to fit in height
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val != min_val else 1
    
    # Create plot grid
    plot = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot points
    for i, val in enumerate(values):
        x = int((i / (len(values) - 1)) * (width - 1)) if len(values) > 1 else width // 2
        y = height - 1 - int(((val - min_val) / val_range) * (height - 1))
        y = max(0, min(height - 1, y))
        plot[y][x] = '●'
        
        # Connect with lines
        if i > 0:
            prev_val = values[i - 1]
            prev_x = int(((i - 1) / (len(values) - 1)) * (width - 1)) if len(values) > 1 else width // 2
            prev_y = height - 1 - int(((prev_val - min_val) / val_range) * (height - 1))
            prev_y = max(0, min(height - 1, prev_y))
            
            # Simple line drawing
            if prev_x < x:
                for px in range(prev_x + 1, x):
                    py = prev_y + int((y - prev_y) * (px - prev_x) / (x - prev_x))
                    if 0 <= py < height:
                        plot[py][px] = '─'
    
    # Build output
    output = []
    output.append(f"\n{METRIC_CONFIG[metric]['label']} (Last {len(entries)} days)")
    output.append("┌" + "─" * width + "┐")
    for row in plot:
        output.append("│" + "".join(row) + "│")
    output.append("└" + "─" * width + "┘")
    output.append(f"  Min: {min_val:.1f}  Max: {max_val:.1f}  Avg: {sum(values)/len(values):.1f}")
    
    return "\n".join(output)


def auto_open_file(filepath: str):
    """
    Automatically open a file with the default system application.
    Cross-platform support for Windows, Mac, and Linux.
    """
    try:
        import platform
        import subprocess
        
        system = platform.system()
        if system == 'Windows':
            os.startfile(filepath)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', filepath], check=False)
        else:  # Linux and others
            subprocess.run(['xdg-open', filepath], check=False)
    except Exception:
        # Silently fail if auto-open doesn't work
        pass
