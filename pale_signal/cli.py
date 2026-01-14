"""
pale-signal: A lightweight, local-first Python tool for tracking daily life signals.

Usage:
    pale-signal add
    pale-signal summary [--days N]
    pale-signal plot <metric>
"""

import argparse
import sys
import os
import platform
from datetime import datetime

from . import data_store
from . import analytics
from . import visualize


ASCII_BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗  █████╗ ██╗     ███████╗    ███████╗██╗ ██████╗ ║
║   ██╔══██╗██╔══██╗██║     ██╔════╝    ██╔════╝██║██╔════╝ ║
║   ██████╔╝███████║██║     █████╗█████╗███████╗██║██║  ███╗║
║   ██╔═══╝ ██╔══██║██║     ██╔══╝╚════╝╚════██║██║██║   ██║║
║   ██║     ██║  ██║███████╗███████╗    ███████║██║╚██████╔╝║
║   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝╚═╝ ╚═════╝ ║
║                                                           ║
║          Track daily signals. Build awareness.            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""


def show_banner():
    """Display ASCII art banner."""
    print(ASCII_BANNER)


def cmd_add():
    """Interactive command to add today's data."""
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().isoformat()
    
    print(f"\nAdding data for {today}")
    print("=" * 60)
    
    # Check if entry already exists
    existing = data_store.get_entry_by_date(today)
    if existing:
        print(f"WARNING: Entry for {today} already exists.")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled.")
            return
    
    # Collect data
    entry = {"date": today, "timestamp": timestamp}
    
    try:
        # Sleep hours
        sleep = input("Sleep hours (0-24): ").strip()
        entry["sleep_hours"] = float(sleep)
        
        # Focus
        focus = input("Focus (1-10): ").strip()
        entry["focus"] = int(focus)
        
        # Mood
        mood = input("Mood (1-10): ").strip()
        entry["mood"] = int(mood)
        
        # Work hours
        work = input("Work hours (0-24): ").strip()
        entry["work_hours"] = float(work)
        
        # Social - with validation loop
        valid_social = ["none", "online", "casual", "meaningful", "deep"]
        while True:
            print("Social interaction type:")
            print("  none       - No social interaction")
            print("  online     - Online/digital only (chat, video call)")
            print("  casual     - Brief in-person (small talk, errands)")
            print("  meaningful - Quality time with friends/family")
            print("  deep       - Deep conversation or bonding")
            social = input("Choose (none/online/casual/meaningful/deep): ").strip().lower()
            
            if social in valid_social:
                entry["social"] = social
                break
            else:
                print(f"ERROR: Invalid choice '{social}'. Please choose from: {', '.join(valid_social)}")
                print("")
        
    except (ValueError, KeyboardInterrupt):
        print("\nERROR: Invalid input or cancelled.")
        return
    
    # Validate and save
    is_valid, error = data_store.validate_entry(entry)
    if not is_valid:
        print(f"ERROR: Validation error: {error}")
        return
    
    # If overwriting, remove old entry first
    if existing:
        data = data_store.load_data()
        data["entries"] = [e for e in data["entries"] if e["date"] != today]
        data_store.save_data(data)
    
    success, error = data_store.add_entry(entry)
    if success:
        print(f"\nSUCCESS: Data saved for {today} at {timestamp}")
    else:
        print(f"ERROR: {error}")


def cmd_summary(days: int):
    """Display summary statistics for the last N days."""
    entries = data_store.get_entries(days)
    
    if not entries or len(entries) < 3:
        print("\nInsufficient data for meaningful summary.")
        print(f"You have {len(entries) if entries else 0} entries. At least 3 entries recommended.")
        
        response = input("\nWould you like to use dummy data for testing? (y/n): ").strip().lower()
        if response == 'y':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(days)
            print(f"\nUsing {len(entries)} days of dummy data for demonstration.\n")
        else:
            print("\nAdd more data with: pale-signal add")
            return
    
    summary = analytics.generate_summary(entries, days)
    print("\n" + summary)


def cmd_plot(metric: str):
    """Plot a specific metric over time."""
    entries = data_store.get_entries()
    
    if not entries or len(entries) < 3:
        print("\nInsufficient data for plotting.")
        print(f"You have {len(entries) if entries else 0} entries. At least 3 entries recommended.")
        
        response = input("\nWould you like to use dummy data for testing? (y/n): ").strip().lower()
        if response == 'y':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(30)
            print(f"\nUsing {len(entries)} days of dummy data for demonstration.\n")
        else:
            print("\nAdd more data with: pale-signal add")
            return
    
    valid_metrics = ["sleep_hours", "focus", "mood", "work_hours", "social"]
    if metric not in valid_metrics:
        print(f"ERROR: Invalid metric: {metric}")
        print(f"Valid metrics: {', '.join(valid_metrics)}")
        return
    
    # Show ASCII plot in terminal
    ascii_plot = visualize.generate_ascii_plot(entries, metric)
    if ascii_plot:
        print(ascii_plot)
    
    # Generate and save PNG plot
    filename = visualize.plot_metric(entries, metric)
    print(f"\nHigh-resolution plot saved to: {filename}")
    
    # Auto-open the plot
    print("Opening plot...")
    visualize.auto_open_file(filename)


def main():
    """Main CLI entry point."""
    
    epilog = """
Examples:
  pale-signal add                    Add today's data interactively
  pale-signal summary                View last 30 days summary
  pale-signal summary --days 7       View last 7 days summary
  pale-signal plot sleep_hours       Generate sleep hours plot
  pale-signal plot mood              Generate mood plot

Data Location:
  All data is stored in: ~/.pale-signal/
  - data.json: Your daily entries
  - output/: Generated plots

For more information, visit: https://github.com/siddharth-narigra/pale-signal
"""
    
    parser = argparse.ArgumentParser(
        prog='pale-signal',
        description='A lightweight, local-first CLI tool for tracking and analyzing daily life signals',
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser(
        'add',
        help='Add today\'s data',
        description='Interactively add daily signal data (sleep, focus, mood, work hours, social interaction)'
    )
    
    # Summary command
    summary_parser = subparsers.add_parser(
        'summary',
        help='Display summary statistics',
        description='Display statistical summary including averages, correlations, and flags'
    )
    summary_parser.add_argument(
        '--days',
        type=int,
        default=30,
        metavar='N',
        help='Number of days to summarize (default: 30)'
    )
    
    # Plot command
    plot_parser = subparsers.add_parser(
        'plot',
        help='Plot a metric over time',
        description='Generate a time series plot for a specific metric with rolling averages'
    )
    plot_parser.add_argument(
        'metric',
        type=str,
        choices=['sleep_hours', 'focus', 'mood', 'work_hours', 'social'],
        help='Metric to plot (sleep_hours, focus, mood, work_hours, social)'
    )
    
    args = parser.parse_args()
    
    # Show banner for help or when no command given
    if not args.command or args.command in ['add', 'summary', 'plot']:
        if not args.command:
            show_banner()
    
    if args.command == 'add':
        cmd_add()
    elif args.command == 'summary':
        cmd_summary(args.days)
    elif args.command == 'plot':
        cmd_plot(args.metric)
    else:
        show_banner()
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
