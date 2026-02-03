"""macOS window title detection."""

import subprocess
from .base import Platform, WindowInfo


class MacOSPlatform(Platform):
    """macOS implementation using AppleScript."""

    @property
    def name(self) -> str:
        return "macos"

    def get_windows(self) -> list[WindowInfo]:
        """Get windows with process info using osascript/AppleScript."""
        # AppleScript that returns process name and window title pairs
        # Format: "process_name|||window_title" separated by ":::"
        script = '''
        tell application "System Events"
            set windowData to {}
            repeat with proc in (every process whose background only is false)
                try
                    set procName to name of proc
                    repeat with w in (every window of proc)
                        set winTitle to name of w
                        set end of windowData to procName & "|||" & winTitle
                    end repeat
                end try
            end repeat
            set AppleScript's text item delimiters to ":::"
            return windowData as text
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

            output = result.stdout.strip()
            if not output:
                return []

            windows = []
            for item in output.split(":::"):
                item = item.strip()
                if "|||" in item:
                    parts = item.split("|||", 1)
                    if len(parts) == 2:
                        process_name = parts[0].strip().lower()
                        title = parts[1].strip()
                        windows.append(WindowInfo(title=title, process_name=process_name))

            return windows
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
