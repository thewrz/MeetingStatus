"""Microsoft Teams meeting detector."""

import re
from .base import MeetingDetector


class TeamsDetector(MeetingDetector):
    """Detect Microsoft Teams meetings from window titles."""

    # Valid process names for Microsoft Teams
    PROCESS_NAMES = [
        "teams",           # Classic Teams
        "ms-teams",        # New Teams on some systems
        "microsoft teams", # macOS process name
    ]

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

    @property
    def process_names(self) -> list[str]:
        return self.PROCESS_NAMES

    def is_meeting_title(self, title: str) -> bool:
        """Check if a Teams window title indicates an active meeting."""
        # Skip if it matches a "not meeting" pattern
        if any(regex.search(title) for regex in self._not_meeting_regexes):
            return False

        # Check if it matches any meeting pattern
        return any(regex.search(title) for regex in self._meeting_regexes)
