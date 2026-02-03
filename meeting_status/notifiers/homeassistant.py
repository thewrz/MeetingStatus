"""Home Assistant webhook notifier."""

import json
import logging
import requests

logger = logging.getLogger(__name__)


class HomeAssistantNotifier:
    """Send meeting status updates to Home Assistant."""

    def __init__(self, ha_url: str, ha_token: str):
        """Initialize the notifier.

        Args:
            ha_url: Home Assistant base URL (e.g., http://homeassistant.local:8123)
            ha_token: Long-lived access token
        """
        self.ha_url = ha_url.rstrip("/")
        self.ha_token = ha_token
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json",
        })

    def notify(self, in_meeting: bool) -> bool:
        """Send meeting status to Home Assistant LED sign script.

        Args:
            in_meeting: True if currently in a meeting

        Returns:
            True if notification was sent successfully
        """
        # Build the LED sign payload
        if in_meeting:
            led_payload = {"text": "MEET", "color": "red"}
        else:
            led_payload = {"text": "FREE", "color": "green"}

        # The service expects payload as an escaped JSON string
        service_data = {"payload": json.dumps(led_payload)}

        url = f"{self.ha_url}/api/services/script/send_to_led_sign"

        try:
            response = self._session.post(url, json=service_data, timeout=10)
            response.raise_for_status()
            logger.debug(f"Successfully sent status to Home Assistant: {led_payload}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send status to Home Assistant: {e}")
            return False

    def test_connection(self) -> bool:
        """Test the connection to Home Assistant.

        Returns:
            True if connection is successful
        """
        try:
            response = self._session.get(f"{self.ha_url}/api/", timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Home Assistant: {e}")
            return False
