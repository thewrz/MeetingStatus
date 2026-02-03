"""Windows window title detection."""

import subprocess
from .base import Platform, WindowInfo


class WindowsPlatform(Platform):
    """Windows implementation using pywin32 or PowerShell fallback."""

    @property
    def name(self) -> str:
        return "windows"

    def _get_windows_pywin32(self) -> list[WindowInfo] | None:
        """Get windows with process info using pywin32."""
        try:
            import win32gui
            import win32process
            import psutil

            windows = []

            def enum_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            proc = psutil.Process(pid)
                            process_name = proc.name().lower()
                            # Remove .exe extension if present
                            if process_name.endswith(".exe"):
                                process_name = process_name[:-4]
                            windows.append(WindowInfo(title=title, process_name=process_name))
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # If we can't get process info, still include the window
                            windows.append(WindowInfo(title=title, process_name=""))
                return True

            win32gui.EnumWindows(enum_callback, None)
            return windows
        except ImportError:
            return None
        except Exception:
            return None

    def _get_windows_powershell(self) -> list[WindowInfo]:
        """Get windows with process info using PowerShell (fallback)."""
        ps_script = '''
        Get-Process | Where-Object {$_.MainWindowTitle} | ForEach-Object {
            $_.ProcessName + "|||" + $_.MainWindowTitle
        }
        '''

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return []

            windows = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if "|||" in line:
                    parts = line.split("|||", 1)
                    if len(parts) == 2:
                        process_name = parts[0].strip().lower()
                        title = parts[1].strip()
                        windows.append(WindowInfo(title=title, process_name=process_name))

            return windows
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_windows(self) -> list[WindowInfo]:
        """Get windows with process info, trying pywin32 first, then PowerShell."""
        # Try pywin32 first (faster and more reliable)
        windows = self._get_windows_pywin32()
        if windows is not None:
            return windows

        # Fall back to PowerShell
        return self._get_windows_powershell()

    def is_available(self) -> bool:
        """Check if window enumeration is available."""
        # pywin32 check
        try:
            import win32gui
            return True
        except ImportError:
            pass

        # PowerShell fallback check
        try:
            result = subprocess.run(
                ["powershell", "-Command", "echo test"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
