"""Windows window title detection."""

import subprocess
from .base import Platform


class WindowsPlatform(Platform):
    """Windows implementation using pywin32 or PowerShell fallback."""

    @property
    def name(self) -> str:
        return "windows"

    def _get_titles_pywin32(self) -> list[str] | None:
        """Get window titles using pywin32."""
        try:
            import win32gui

            titles = []

            def enum_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        titles.append(title)
                return True

            win32gui.EnumWindows(enum_callback, None)
            return titles
        except ImportError:
            return None
        except Exception:
            return None

    def _get_titles_powershell(self) -> list[str]:
        """Get window titles using PowerShell (fallback)."""
        ps_script = '''
        Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -ExpandProperty MainWindowTitle
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

            titles = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
            return titles
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_window_titles(self) -> list[str]:
        """Get window titles, trying pywin32 first, then PowerShell."""
        # Try pywin32 first (faster and more reliable)
        titles = self._get_titles_pywin32()
        if titles is not None:
            return titles

        # Fall back to PowerShell
        return self._get_titles_powershell()

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
