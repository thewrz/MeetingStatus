"""Abstract base class for meeting detectors."""

from abc import ABC, abstractmethod


class MeetingDetector(ABC):
    """Abstract base class for detecting meetings from window titles."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this detector (e.g., 'teams', 'zoom')."""
        pass

    @abstractmethod
    def is_in_meeting(self, window_titles: list[str]) -> bool:
        """Check if any window title indicates an active meeting.

        Args:
            window_titles: List of visible window titles

        Returns:
            True if a meeting is detected, False otherwise
        """
        pass
