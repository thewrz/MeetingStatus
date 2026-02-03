"""macOS window title detection."""

import subprocess
from .base import Platform


class MacOSPlatform(Platform):
    """macOS implementation using AppleScript."""

    @property
    def name(self) -> str:
        return "macos"

    def get_window_titles(self) -> list[str]:
        """Get window titles using osascript/AppleScript."""
        script = '''
        tell application "System Events"
            set windowTitles to {}
            repeat with proc in (every process whose background only is false)
                try
                    repeat with w in (every window of proc)
                        set end of windowTitles to name of w
                    end repeat
                end try
            end repeat
            return windowTitles
        end tell
        '''

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return []

            # AppleScript returns comma-separated list
            output = result.stdout.strip()
            if not output:
                return []

            # Parse the AppleScript list output
            # Format is typically: "title1, title2, title3"
            titles = [t.strip() for t in output.split(", ") if t.strip()]
            return titles
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def is_available(self) -> bool:
        """Check if osascript is available (always true on macOS)."""
        try:
            result = subprocess.run(
                ["which", "osascript"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
