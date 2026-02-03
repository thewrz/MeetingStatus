"""Meeting detectors for various conferencing applications."""

from .base import MeetingDetector
from .teams import TeamsDetector
from .zoom import ZoomDetector

__all__ = ["MeetingDetector", "TeamsDetector", "ZoomDetector"]
