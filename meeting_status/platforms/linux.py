"""Linux window title detection."""

import shutil
import subprocess
from .base import Platform


class LinuxPlatform(Platform):
    """Linux implementation using wmctrl or xdotool."""

    @property
    def name(self) -> str:
        return "linux"

    def _get_titles_wmctrl(self) -> list[str]:
        """Get window titles using wmctrl."""
        try:
            result = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return []

            titles = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # wmctrl -l format: <window-id> <desktop> <hostname> <title>
                # Title is everything after the third space-separated field
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    titles.append(parts[3])
            return titles
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _get_titles_xdotool(self) -> list[str]:
        """Get window titles using xdotool."""
        try:
            # Get all window IDs
            result = subprocess.run(
                ["xdotool", "search", "--name", ""],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return []

            window_ids = result.stdout.strip().split("\n")
            titles = []

            for wid in window_ids:
                if not wid:
                    continue
                try:
                    name_result = subprocess.run(
                        ["xdotool", "getwindowname", wid],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    if name_result.returncode == 0 and name_result.stdout.strip():
                        titles.append(name_result.stdout.strip())
                except subprocess.TimeoutExpired:
                    continue

            return titles
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _get_titles_qdbus(self) -> list[str]:
        """Get window titles using qdbus (KDE/Plasma)."""
        try:
            result = subprocess.run(
                ["qdbus", "org.kde.KWin", "/KWin", "org.kde.KWin.queryWindowInfo"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # This is a simplified approach; real implementation would need parsing
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_window_titles(self) -> list[str]:
        """Get window titles, trying multiple methods."""
        # Try wmctrl first (most reliable for X11)
        if shutil.which("wmctrl"):
            titles = self._get_titles_wmctrl()
            if titles:
                return titles

        # Fall back to xdotool
        if shutil.which("xdotool"):
            titles = self._get_titles_xdotool()
            if titles:
                return titles

        return []

    def is_available(self) -> bool:
        """Check if wmctrl or xdotool is available."""
        return bool(shutil.which("wmctrl") or shutil.which("xdotool"))
