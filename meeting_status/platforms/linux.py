"""Linux window title detection."""

import os
import shutil
import subprocess
from .base import Platform, WindowInfo


class LinuxPlatform(Platform):
    """Linux implementation using wmctrl or xdotool."""

    @property
    def name(self) -> str:
        return "linux"

    def _get_process_name(self, pid: int) -> str:
        """Get process name from PID using /proc filesystem."""
        try:
            # Try to get the executable name from /proc/<pid>/comm
            comm_path = f"/proc/{pid}/comm"
            if os.path.exists(comm_path):
                with open(comm_path) as f:
                    return f.read().strip().lower()

            # Fallback: try to get from /proc/<pid>/exe symlink
            exe_path = f"/proc/{pid}/exe"
            if os.path.exists(exe_path):
                exe = os.readlink(exe_path)
                return os.path.basename(exe).lower()
        except (OSError, IOError):
            pass
        return ""

    def _get_windows_wmctrl(self) -> list[WindowInfo]:
        """Get windows using wmctrl with PID info."""
        try:
            # Use -lp to get PID along with window info
            result = subprocess.run(
                ["wmctrl", "-lp"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return []

            windows = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # wmctrl -lp format: <window-id> <desktop> <pid> <hostname> <title>
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    try:
                        pid = int(parts[2])
                        title = parts[4]
                        process_name = self._get_process_name(pid)
                        windows.append(WindowInfo(title=title, process_name=process_name))
                    except (ValueError, IndexError):
                        continue
            return windows
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _get_windows_xdotool(self) -> list[WindowInfo]:
        """Get windows using xdotool."""
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
            windows = []

            for wid in window_ids:
                if not wid:
                    continue
                try:
                    # Get window name
                    name_result = subprocess.run(
                        ["xdotool", "getwindowname", wid],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    if name_result.returncode != 0 or not name_result.stdout.strip():
                        continue

                    title = name_result.stdout.strip()

                    # Get window PID
                    pid_result = subprocess.run(
                        ["xdotool", "getwindowpid", wid],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    process_name = ""
                    if pid_result.returncode == 0 and pid_result.stdout.strip():
                        try:
                            pid = int(pid_result.stdout.strip())
                            process_name = self._get_process_name(pid)
                        except ValueError:
                            pass

                    windows.append(WindowInfo(title=title, process_name=process_name))
                except subprocess.TimeoutExpired:
                    continue

            return windows
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_windows(self) -> list[WindowInfo]:
        """Get windows with process info, trying multiple methods."""
        # Try wmctrl first (most reliable for X11)
        if shutil.which("wmctrl"):
            windows = self._get_windows_wmctrl()
            if windows:
                return windows

        # Fall back to xdotool
        if shutil.which("xdotool"):
            windows = self._get_windows_xdotool()
            if windows:
                return windows

        return []

    def is_available(self) -> bool:
        """Check if wmctrl or xdotool is available."""
        return bool(shutil.which("wmctrl") or shutil.which("xdotool"))
