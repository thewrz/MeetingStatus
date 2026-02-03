"""Main entry point for Meeting Status Detector."""

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

from .config import Config
from .detectors import TeamsDetector, ZoomDetector
from .platforms import get_platform
from .notifiers import HomeAssistantNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global running
    logger.info("Received shutdown signal, stopping...")
    running = False


def get_detectors(detector_names: list[str]) -> list:
    """Get detector instances for the specified names."""
    available_detectors = {
        "teams": TeamsDetector,
        "zoom": ZoomDetector,
    }

    detectors = []
    for name in detector_names:
        name_lower = name.lower()
        if name_lower in available_detectors:
            detectors.append(available_detectors[name_lower]())
        else:
            logger.warning(f"Unknown detector: {name}")

    return detectors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect meeting status and report to Home Assistant"
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to config file (default: ./config.json or ~/.config/meeting_status/config.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't send notifications, just print status",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't poll)",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = Config.load(args.config)
    errors = config.validate()
    if errors and not args.dry_run:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        sys.exit(1)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize platform
    platform = get_platform()
    logger.info(f"Using platform: {platform.name}")

    if not platform.is_available():
        logger.error(f"Platform {platform.name} is not available. Required tools not found.")
        sys.exit(1)

    # Initialize detectors
    detectors = get_detectors(config.detectors)
    if not detectors:
        logger.error("No valid detectors configured")
        sys.exit(1)

    logger.info(f"Active detectors: {[d.name for d in detectors]}")

    # Initialize notifier
    notifier = None
    if not args.dry_run:
        notifier = HomeAssistantNotifier(config.ha_url, config.ha_token)
        if not notifier.test_connection():
            logger.error("Failed to connect to Home Assistant")
            sys.exit(1)
        logger.info("Connected to Home Assistant")

    # State tracking
    previous_in_meeting = None

    logger.info(f"Starting polling loop (interval: {config.poll_interval_seconds}s)")

    while running:
        try:
            # Get current windows with process info
            windows = platform.get_windows()
            logger.debug(f"Found {len(windows)} windows")

            # Check each detector
            in_meeting = False
            for detector in detectors:
                if detector.is_in_meeting(windows):
                    in_meeting = True
                    logger.debug(f"Meeting detected by {detector.name}")
                    break

            # Only send notification on state change
            if in_meeting != previous_in_meeting:
                status = "IN MEETING" if in_meeting else "NOT IN MEETING"
                logger.info(f"Status changed: {status}")

                if notifier:
                    if notifier.notify(in_meeting):
                        previous_in_meeting = in_meeting
                    else:
                        logger.warning("Failed to send notification, will retry")
                else:
                    # Dry run mode
                    print(f"[DRY RUN] Would send: {status}")
                    previous_in_meeting = in_meeting

            if args.once:
                break

            time.sleep(config.poll_interval_seconds)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            if args.once:
                sys.exit(1)
            time.sleep(config.poll_interval_seconds)

    logger.info("Shutting down")


if __name__ == "__main__":
    main()
