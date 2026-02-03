"""Abstract base class for meeting detectors."""

from abc import ABC, abstractmethod
from ..platforms.base import WindowInfo


class MeetingDetector(ABC):
    """Abstract base class for detecting meetings from window info."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this detector (e.g., 'teams', 'zoom')."""
        pass

    @property
    @abstractmethod
    def process_names(self) -> list[str]:
        """Return list of valid process names for this application.

        Process names should be lowercase without extension.
        """
        pass

    @abstractmethod
    def is_meeting_title(self, title: str) -> bool:
        """Check if a window title indicates an active meeting.

        Args:
            title: Window title string

        Returns:
            True if the title indicates a meeting
        """
        pass

    def is_in_meeting(self, windows: list[WindowInfo]) -> bool:
        """Check if any window indicates an active meeting.

        Only considers windows from matching process names.

        Args:
            windows: List of WindowInfo objects

        Returns:
            True if a meeting is detected, False otherwise
        """
        for window in windows:
            # Check if this window belongs to a matching process
            if window.process_name and window.process_name not in self.process_names:
                continue

            # If process name is empty (couldn't be determined), skip this window
            # to avoid false positives
            if not window.process_name:
                continue

            # Check if the title indicates a meeting
            if self.is_meeting_title(window.title):
                return True

        return False
