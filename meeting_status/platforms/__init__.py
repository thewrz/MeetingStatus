"""Platform-specific window title detection."""

import sys
from .base import Platform

def get_platform() -> Platform:
    """Get the appropriate platform implementation for the current OS."""
    if sys.platform == "win32":
        from .windows import WindowsPlatform
        return WindowsPlatform()
    elif sys.platform == "darwin":
        from .macos import MacOSPlatform
        return MacOSPlatform()
    else:
        from .linux import LinuxPlatform
        return LinuxPlatform()

__all__ = ["Platform", "get_platform"]
