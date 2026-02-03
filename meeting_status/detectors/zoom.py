"""Zoom meeting detector."""

import re
from .base import MeetingDetector


class ZoomDetector(MeetingDetector):
    """Detect Zoom meetings from window titles."""

    # Valid process names for Zoom
    PROCESS_NAMES = [
        "zoom",            # Main Zoom process
        "zoom.us",         # Zoom on some systems
        "zoomus",          # Alternative naming
        "caphost",         # Zoom meeting host process (Windows)
        "cpthost",         # Another Zoom process
    ]

    # Patterns that indicate an active meeting
    MEETING_PATTERNS = [
        r"Zoom Meeting",
        r"Zoom Webinar",
        r"^Zoom$",  # Main Zoom window during meeting
        # Meeting ID in title (9-11 digit number)
        r"\b\d{9,11}\b.*Zoom",
        r"Zoom.*\b\d{9,11}\b",
    ]

    # Patterns that indicate NOT in a meeting
    NOT_MEETING_PATTERNS = [
        r"^Zoom Cloud Meetings$",  # Main app window when not in meeting
        r"^Zoom - Free Account$",
        r"^Zoom - Pro$",
        r"^Zoom - Licensed$",
        r"^Zoom Workplace$",  # New Zoom desktop app
        r"Settings",
        r"^Chat$",
        r"^Contacts$",
    ]

    def __init__(self):
        self._meeting_regexes = [re.compile(p, re.IGNORECASE) for p in self.MEETING_PATTERNS]
        self._not_meeting_regexes = [re.compile(p, re.IGNORECASE) for p in self.NOT_MEETING_PATTERNS]

    @property
    def name(self) -> str:
        return "zoom"

    @property
    def process_names(self) -> list[str]:
        return self.PROCESS_NAMES

    def is_meeting_title(self, title: str) -> bool:
        """Check if a Zoom window title indicates an active meeting."""
        # Skip if it matches a "not meeting" pattern
        if any(regex.search(title) for regex in self._not_meeting_regexes):
            return False

        # Check if it matches any meeting pattern
        return any(regex.search(title) for regex in self._meeting_regexes)
