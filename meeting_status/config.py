"""Configuration handling for Meeting Status Detector."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Application configuration."""

    ha_url: str
    ha_token: str
    poll_interval_seconds: int = 2
    detectors: list[str] = field(default_factory=lambda: ["teams", "zoom"])

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "Config":
        """Load configuration from file and/or environment variables.

        Environment variables take precedence over config file values.
        """
        config_data = {}

        # Try to load from config file
        if config_file and config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)
        else:
            # Check default locations
            default_paths = [
                Path.cwd() / "config.json",
                Path.home() / ".config" / "meeting_status" / "config.json",
            ]
            for path in default_paths:
                if path.exists():
                    with open(path) as f:
                        config_data = json.load(f)
                    break

        # Environment variables override config file
        ha_url = os.environ.get("HA_URL", config_data.get("ha_url", ""))
        ha_token = os.environ.get("HA_TOKEN", config_data.get("ha_token", ""))

        poll_interval = os.environ.get("MEETING_STATUS_POLL_INTERVAL")
        if poll_interval:
            poll_interval_seconds = int(poll_interval)
        else:
            poll_interval_seconds = config_data.get("poll_interval_seconds", 2)

        detectors_env = os.environ.get("MEETING_STATUS_DETECTORS")
        if detectors_env:
            detectors = [d.strip() for d in detectors_env.split(",")]
        else:
            detectors = config_data.get("detectors", ["teams", "zoom"])

        return cls(
            ha_url=ha_url,
            ha_token=ha_token,
            poll_interval_seconds=poll_interval_seconds,
            detectors=detectors,
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not self.ha_url:
            errors.append("HA_URL or ha_url is required")
        if not self.ha_token:
            errors.append("HA_TOKEN or ha_token is required")
        if self.poll_interval_seconds < 1:
            errors.append("Poll interval must be at least 1 second")
        return errors
