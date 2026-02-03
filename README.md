# Meeting Status Detector

A cross-platform Python application that detects Microsoft Teams and Zoom meeting status via window titles and reports to Home Assistant.

> **Note:** This application currently sends status updates to a specific Home Assistant script (`send_to_led_sign`) designed for an MQTT-connected LED sign. Future versions will support updating a Home Assistant helper entity directly, allowing you to use the meeting status in any automation you want.

## Features

- Cross-platform support: Windows, macOS, and Linux
- Detects meetings from Microsoft Teams and Zoom
- **Executable verification**: Only detects meetings from actual Teams/Zoom processes, preventing false positives from other applications with similar window titles
- Reports status to Home Assistant via webhook
- Only sends updates when status changes (not polling Home Assistant constantly)
- Configurable via environment variables or JSON config file

## Requirements

- Python 3.10+
- Home Assistant with a long-lived access token
- Platform-specific requirements:
  - **Linux**: `wmctrl` or `xdotool`
  - **macOS**: No additional requirements (uses AppleScript)
  - **Windows**: `pywin32` and `psutil` (optional, falls back to PowerShell)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/thewrz/MeetingStatus.git
cd MeetingStatus
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install platform-specific tools

**Linux (Arch/Manjaro):**
```bash
sudo pacman -S wmctrl
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt install wmctrl
```

**macOS:** No additional tools needed.

**Windows:** The `pywin32` and `psutil` packages are automatically installed from requirements.txt.

### 4. Create a Home Assistant Long-Lived Access Token

1. In Home Assistant, click on your profile (lower left corner)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Give it a name and save the token

### 5. Set up the LED Sign Script in Home Assistant

Create a script in Home Assistant called `send_to_led_sign` that accepts a JSON payload with `text` and `color` fields. The meeting status detector will call this script with:

- **In meeting:** `{"text": "MEET", "color": "red"}`
- **Not in meeting:** `{"text": "FREE", "color": "cyan"}`

### 6. Configure the application

Copy the example config and edit it:

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "ha_url": "http://your-ha-instance:8123",
  "ha_token": "your-long-lived-access-token",
  "poll_interval_seconds": 2,
  "detectors": ["teams", "zoom"]
}
```

Or use environment variables:

```bash
export HA_URL="http://your-ha-instance:8123"
export HA_TOKEN="your-long-lived-access-token"
export MEETING_STATUS_POLL_INTERVAL=2
export MEETING_STATUS_DETECTORS="teams,zoom"
```

## Usage

### Run once (test mode)

```bash
python -m meeting_status --once -v
```

### Run with dry-run (no Home Assistant updates)

```bash
python -m meeting_status --dry-run -v
```

### Run continuously

```bash
python -m meeting_status
```

### Command-line options

| Option | Description |
|--------|-------------|
| `-c, --config FILE` | Path to config file |
| `-v, --verbose` | Enable verbose logging |
| `--dry-run` | Print status without sending to Home Assistant |
| `--once` | Run once and exit (don't poll continuously) |

## Running as a Service

### Linux (systemd)

Create `~/.config/systemd/user/meeting-status.service`:

```ini
[Unit]
Description=Meeting Status Detector
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/MeetingStatus
ExecStart=/usr/bin/python -m meeting_status
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user enable meeting-status
systemctl --user start meeting-status
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.meeting-status.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.meeting-status</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-m</string>
        <string>meeting_status</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/MeetingStatus</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.meeting-status.plist
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create a new task
3. Set trigger to "At log on"
4. Set action to run `python -m meeting_status` in the MeetingStatus directory
5. Enable "Run whether user is logged on or not"

## How It Works

The application polls for visible windows at a configurable interval (default: 2 seconds). For each window, it checks:

1. **Process verification**: The window must belong to an actual Teams or Zoom executable
2. **Title pattern matching**: The window title must match patterns indicating an active meeting

This two-step approach prevents false positives from other applications that might have similar window titles (e.g., a text file named "zoom meeting.txt").

**Microsoft Teams patterns:**
- "Meeting with" or "Meeting in"
- "Call with"
- Timer showing call duration (e.g., "00:05:23")

**Zoom patterns:**
- "Zoom Meeting"
- "Zoom Webinar"

When the meeting status changes, the application sends a request to the Home Assistant `send_to_led_sign` script.

## Future Plans

- Support for updating a Home Assistant helper entity (input_boolean or input_select) directly, enabling flexible use in any automation
- Additional meeting application detectors (Google Meet, Webex, etc.)

## License

MIT License - see [LICENSE](LICENSE) for details.
