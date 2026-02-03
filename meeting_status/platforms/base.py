"""Abstract base class for platform-specific window detection."""

from abc import ABC, abstractmethod


class Platform(ABC):
    """Abstract base class for platform-specific window title detection."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name (e.g., 'linux', 'macos', 'windows')."""
        pass

    @abstractmethod
    def get_window_titles(self) -> list[str]:
        """Get a list of all visible window titles.

        Returns:
            List of window title strings
        """
        pass

    def is_available(self) -> bool:
        """Check if this platform implementation is available.

        Returns:
            True if the required tools/APIs are available
        """
        return True
