"""Microsoft Teams meeting detector."""

import re
from .base import MeetingDetector


class TeamsDetector(MeetingDetector):
    """Detect Microsoft Teams meetings from window titles."""

    # Patterns that indicate an active meeting
    MEETING_PATTERNS = [
        # Classic Teams patterns
        r"Meeting in ",
        r"Meeting with ",
        r"Call with ",
        # New Teams (work or school) patterns
        r"^.+\s+\|\s+Microsoft Teams$",  # "Meeting Name | Microsoft Teams"
        # Meeting window with participant info
        r"\d+:\d+:\d+",  # Timer showing call duration like "00:05:23"
        r"^\d+ participant",  # "3 participants" style
    ]

    # Patterns that indicate NOT in a meeting (to filter false positives)
    NOT_MEETING_PATTERNS = [
        r"^Microsoft Teams$",  # Just the main window
        r"^Chat \|",  # Chat window
        r"^Calendar \|",  # Calendar view
        r"^Activity \|",  # Activity feed
        r"^Teams \|",  # Teams list
        r"^Files \|",  # Files view
    ]

    def __init__(self):
        self._meeting_regexes = [re.compile(p, re.IGNORECASE) for p in self.MEETING_PATTERNS]
        self._not_meeting_regexes = [re.compile(p, re.IGNORECASE) for p in self.NOT_MEETING_PATTERNS]

    @property
    def name(self) -> str:
        return "teams"

    def is_in_meeting(self, window_titles: list[str]) -> bool:
        """Check if any Teams window indicates an active meeting."""
        for title in window_titles:
            # Skip if it matches a "not meeting" pattern
            if any(regex.search(title) for regex in self._not_meeting_regexes):
                continue

            # Check if it matches any meeting pattern
            if any(regex.search(title) for regex in self._meeting_regexes):
                return True

        return False
