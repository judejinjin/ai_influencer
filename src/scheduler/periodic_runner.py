"""
Runs content generation on a schedule.
Can be run as a long-lived process or triggered via system cron.
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


def run_trending():
    """Run the trending news content generator."""
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_from_trending.py"),
         "--count", "3", "--days", "3"],
        check=True,
    )


def run_weekly_repertoire():
    """Run the weekly repertoire generator."""
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_repertoire.py"),
         "--count", "5", "--pillar", "all"],
        check=True,
    )


def start_scheduler():
    """Start the periodic scheduler (blocking)."""
    schedule.every().day.at("08:00").do(run_trending)
    schedule.every().monday.at("09:00").do(run_weekly_repertoire)

    print("📅 Scheduler started.")
    print("  • Daily 8:00 AM — Trending news content generation")
    print("  • Monday 9:00 AM — Weekly repertoire refresh")
    print("  Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
