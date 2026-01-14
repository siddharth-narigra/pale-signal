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
╠═══════════════════════════════════════════════════════════╣
║          Track daily signals. Build awareness.            ║
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
    using_dummy = False
    
    if not entries:
        # No data at all
        print("\nNo data yet.")
        response = input("Would you like to see a demo with sample data? (y/n): ").strip().lower()
        if response == 'y':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(days)
            using_dummy = True
        else:
            print("\nStart tracking with: pale-signal add")
            return
    
    elif len(entries) < 3:
        # Some data but limited
        print(f"\nYou have {len(entries)} entries. 3+ recommended for meaningful stats.")
        print("\nOptions:")
        print("  1. View your data anyway")
        print("  2. See demo with sample data")
        print("  3. Add more data first")
        
        choice = input("\nChoose (1/2/3): ").strip()
        if choice == '1':
            pass  # Use their data
        elif choice == '2':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(days)
            using_dummy = True
        else:
            print("\nAdd data with: pale-signal add")
            return
    
    if using_dummy:
        print("\n" + "=" * 60)
        print("  DEMO MODE - This is sample data, not your actual data")
        print("=" * 60)
    
    summary = analytics.generate_summary(entries, days)
    print("\n" + summary)
    
    if using_dummy:
        print("-" * 60)
        print("This was demo data. Start tracking with: pale-signal add")
        print("-" * 60)


def cmd_plot(metric: str):
    """Plot a specific metric over time."""
    entries = data_store.get_entries()
    using_dummy = False
    
    if not entries:
        # No data at all
        print("\nNo data yet.")
        response = input("Would you like to see a demo with sample data? (y/n): ").strip().lower()
        if response == 'y':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(30)
            using_dummy = True
        else:
            print("\nStart tracking with: pale-signal add")
            return
    
    elif len(entries) < 3:
        # Some data but limited
        print(f"\nYou have {len(entries)} entries. 3+ recommended for meaningful plots.")
        print("\nOptions:")
        print("  1. Plot your data anyway")
        print("  2. See demo with sample data")
        print("  3. Add more data first")
        
        choice = input("\nChoose (1/2/3): ").strip()
        if choice == '1':
            pass  # Use their data
        elif choice == '2':
            from . import dummy_data
            entries = dummy_data.generate_dummy_data(30)
            using_dummy = True
        else:
            print("\nAdd data with: pale-signal add")
            return
    
    valid_metrics = ["sleep_hours", "focus", "mood", "work_hours", "social"]
    if metric not in valid_metrics:
        print(f"ERROR: Invalid metric: {metric}")
        print(f"Valid metrics: {', '.join(valid_metrics)}")
        return
    
    if using_dummy:
        print("\n" + "=" * 60)
        print("  DEMO MODE - This is sample data, not your actual data")
        print("=" * 60)
    
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
    
    parser = argparse.ArgumentParser(
        prog='pale-signal',
        description='Track daily signals. Build awareness.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    subparsers.add_parser('add', help='Add today\'s data')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='View statistics')
    summary_parser.add_argument('--days', type=int, default=30, metavar='N', help='Days to show (default: 30)')
    
    # Plot command
    plot_parser = subparsers.add_parser('plot', help='Generate plot')
    plot_parser.add_argument('metric', choices=['sleep_hours', 'focus', 'mood', 'work_hours', 'social'])
    
    args = parser.parse_args()
    
    if args.command == 'add':
        cmd_add()
    elif args.command == 'summary':
        cmd_summary(args.days)
    elif args.command == 'plot':
        cmd_plot(args.metric)
    else:
        # Show banner + quick reference (not full help)
        show_banner()
        print("Commands:")
        print("  pale-signal add              Log today's data")
        print("  pale-signal summary          View your stats")
        print("  pale-signal plot <metric>    Generate a plot")
        print("")
        print("Metrics: sleep_hours, focus, mood, work_hours, social")
        print("")
        print("Run 'pale-signal -h' for more options.")
        sys.exit(0)


if __name__ == '__main__':
    main()
