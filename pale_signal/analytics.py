"""
Analytics and statistics for pale-signal.
Computes rolling averages, correlations, and threshold-based insights.
"""

import statistics
from typing import List, Dict, Tuple


def calculate_average(entries: List[Dict], metric: str) -> float:
    """Calculate average for a specific metric."""
    if not entries:
        return 0.0
    
    values = [entry[metric] for entry in entries]
    return statistics.mean(values)


def calculate_rolling_average(entries: List[Dict], metric: str, window: int = 7) -> float:
    """Calculate rolling average for the last N entries."""
    if not entries:
        return 0.0
    
    recent = entries[:window]
    return calculate_average(recent, metric)


def calculate_correlation(entries: List[Dict], metric1: str, metric2: str) -> float:
    """
    Calculate Pearson correlation coefficient between two metrics.
    Returns value between -1 and 1.
    """
    if len(entries) < 2:
        return 0.0
    
    values1 = [float(entry[metric1]) for entry in entries]
    values2 = [float(entry[metric2]) for entry in entries]
    
    # Calculate means
    mean1 = statistics.mean(values1)
    mean2 = statistics.mean(values2)
    
    # Calculate correlation
    numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
    
    sum_sq1 = sum((v1 - mean1) ** 2 for v1 in values1)
    sum_sq2 = sum((v2 - mean2) ** 2 for v2 in values2)
    
    denominator = (sum_sq1 * sum_sq2) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def identify_flags(entries: List[Dict]) -> List[str]:
    """
    Identify threshold-based flags in the data.
    Returns list of insight strings.
    """
    if not entries:
        return []
    
    flags = []
    
    # Count low sleep days (< 6 hours)
    low_sleep_count = sum(1 for e in entries if e["sleep_hours"] < 6)
    if low_sleep_count > 0:
        pct = (low_sleep_count / len(entries)) * 100
        flags.append(f"WARNING: Low sleep (<6h): {low_sleep_count}/{len(entries)} days ({pct:.1f}%)")
    
    # Count low focus days (< 4)
    low_focus_count = sum(1 for e in entries if e["focus"] < 4)
    if low_focus_count > 0:
        pct = (low_focus_count / len(entries)) * 100
        flags.append(f"WARNING: Low focus (<4): {low_focus_count}/{len(entries)} days ({pct:.1f}%)")
    
    # Count low mood days (< 4)
    low_mood_count = sum(1 for e in entries if e["mood"] < 4)
    if low_mood_count > 0:
        pct = (low_mood_count / len(entries)) * 100
        flags.append(f"WARNING: Low mood (<4): {low_mood_count}/{len(entries)} days ({pct:.1f}%)")
    
    # Count high work days (> 10 hours)
    high_work_count = sum(1 for e in entries if e["work_hours"] > 10)
    if high_work_count > 0:
        pct = (high_work_count / len(entries)) * 100
        flags.append(f"WARNING: Long work days (>10h): {high_work_count}/{len(entries)} days ({pct:.1f}%)")
    
    return flags


def get_top_correlations(entries: List[Dict]) -> List[Tuple[str, str, float]]:
    """
    Calculate correlations between all metric pairs.
    Returns list of (metric1, metric2, correlation) tuples, sorted by absolute correlation.
    """
    if len(entries) < 2:
        return []
    
    # Exclude social since it's categorical
    metrics = ["sleep_hours", "focus", "mood", "work_hours"]
    correlations = []
    
    for i, m1 in enumerate(metrics):
        for m2 in metrics[i+1:]:
            corr = calculate_correlation(entries, m1, m2)
            correlations.append((m1, m2, corr))
    
    # Sort by absolute correlation (strongest first)
    correlations.sort(key=lambda x: abs(x[2]), reverse=True)
    
    return correlations


def generate_summary(entries: List[Dict], days: int) -> str:
    """
    Generate a textual summary with statistics and insights.
    """
    if not entries:
        return "No data available."
    
    actual_days = len(entries)
    
    lines = []
    lines.append(f"Summary for last {days} days ({actual_days} entries)")
    lines.append("=" * 60)
    lines.append("")
    
    # Averages
    lines.append("AVERAGES:")
    lines.append(f"  Sleep:     {calculate_average(entries, 'sleep_hours'):.1f} hours")
    lines.append(f"  Focus:     {calculate_average(entries, 'focus'):.1f} / 10")
    lines.append(f"  Mood:      {calculate_average(entries, 'mood'):.1f} / 10")
    lines.append(f"  Work:      {calculate_average(entries, 'work_hours'):.1f} hours")
    
    # Social breakdown
    social_counts = {}
    for e in entries:
        social_type = e.get("social", "none")
        social_counts[social_type] = social_counts.get(social_type, 0) + 1
    
    lines.append("  Social:")
    for social_type in ["none", "online", "casual", "meaningful", "deep"]:
        count = social_counts.get(social_type, 0)
        if count > 0:
            pct = (count / actual_days) * 100
            lines.append(f"    {social_type:12s} - {count}/{actual_days} days ({pct:.1f}%)")
    lines.append("")
    
    # Rolling averages (7-day)
    if actual_days >= 7:
        lines.append("7-DAY ROLLING AVERAGES:")
        lines.append(f"  Sleep:     {calculate_rolling_average(entries, 'sleep_hours', 7):.1f} hours")
        lines.append(f"  Focus:     {calculate_rolling_average(entries, 'focus', 7):.1f} / 10")
        lines.append(f"  Mood:      {calculate_rolling_average(entries, 'mood', 7):.1f} / 10")
        lines.append(f"  Work:      {calculate_rolling_average(entries, 'work_hours', 7):.1f} hours")
        lines.append("")
    
    # Correlations
    correlations = get_top_correlations(entries)
    if correlations:
        lines.append("TOP CORRELATIONS:")
        for m1, m2, corr in correlations[:3]:
            strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
            direction = "positive" if corr > 0 else "negative"
            lines.append(f"  {m1} <-> {m2}: {corr:+.2f} ({strength} {direction})")
        lines.append("")
    
    # Flags
    flags = identify_flags(entries)
    if flags:
        lines.append("FLAGS:")
        for flag in flags:
            lines.append(f"  {flag}")
        lines.append("")
    
    return "\n".join(lines)
