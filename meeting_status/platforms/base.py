"""Abstract base class for platform-specific window detection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """Information about a window."""

    title: str
    process_name: str  # Executable name (e.g., "teams", "zoom", "notepad")


class Platform(ABC):
    """Abstract base class for platform-specific window title detection."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name (e.g., 'linux', 'macos', 'windows')."""
        pass

    @abstractmethod
    def get_windows(self) -> list[WindowInfo]:
        """Get a list of all visible windows with their process info.

        Returns:
            List of WindowInfo objects containing title and process name
        """
        pass

    def is_available(self) -> bool:
        """Check if this platform implementation is available.

        Returns:
            True if the required tools/APIs are available
        """
        return True
