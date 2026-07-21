# MX Master 4 Notification Haptics

Get haptic feedback on your Logitech MX Master 4 mouse whenever you receive desktop notifications on Linux (KDE Plasma, GNOME, or any freedesktop.org-compatible desktop environment).

## Features

- 🖱️ **HID++ Protocol Support** - Direct communication with Logitech MX Master 4
- 🔔 **D-Bus Notification Monitoring** - Listens for all desktop notifications
- 📳 **Haptic Feedback** - Provides tactile alerts for incoming notifications
- 🐧 **Desktop Agnostic** - Works with KDE, GNOME, and other Linux desktop environments
- 🔧 **Lightweight** - Minimal dependencies and resource usage

## Requirements

- Python 3.12+
- Logitech MX Master 4 mouse (connected via USB receiver or Bluetooth)
- Linux system with D-Bus (any modern desktop environment)
- `dbus-monitor` utility (usually pre-installed)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/lukasfri/mx4notifications.git
cd mx4notifications
```

2. Install dependencies using uv:

```bash
uv sync
```

Or using pip:

```bash
pip install hid dbus-python pygobject
```

## Usage

### Monitor Notifications

Run the watcher to receive haptic feedback on notifications:

```bash
uv run mx4notifications watch
```

The script will:

- Automatically detect and connect to your MX Master 4 mouse
- Monitor D-Bus for incoming notifications
- Trigger haptic feedback whenever a notification appears
- Run continuously until stopped with Ctrl+C

### Testing

Send a test notification to verify it's working:

```bash
notify-send "Test Notification" "You should feel vibration on your mouse!"
```

Send a one-shot haptic directly:

```bash
uv run mx4notifications-send-haptic
```

Send a specific haptic payload directly:

```bash
uv run mx4notifications-send-haptic --payload 7
```

Run interactive haptic discovery (default payload range `0-31`):

```bash
uv run mx4notifications-send-haptic --discover
```

The discovery flow sends each payload, asks what you felt (`short`, `long`, `double`, `none`, `other`), then writes JSON results to `./haptic_discovery_results.json` by default.

### Testing Haptic Patterns

Explore different haptic feedback patterns:

```bash
uv run mx4notifications-haptic-morse "... --- ..."
```

This command sends a Morse-like pattern so you can experiment with timed haptic sequences.

### Library layout

Reusable code now lives under `src/mx4notifications/`:

- `mx4notifications.core.mx_master_4` for HID++ device access
- `mx4notifications.cli.*` for watcher and utility command flows

Compatibility wrappers are kept in `src/*.py` during the transition, and standalone launchers live in `scripts/` if you want direct script entry points.

## How It Works

The application uses `dbus-monitor` to listen for notifications on the D-Bus session bus. When a notification is detected on the `org.freedesktop.Notifications` interface, it sends a HID++ command to the MX Master 4 to trigger its built-in haptic motor.

This works with any application that sends notifications through the standard freedesktop.org notification specification, including:

- System notifications
- Application alerts (Slack, Discord, email clients, etc.)
- Custom notifications sent via `notify-send`

## Troubleshooting

### Mouse Not Found

- Ensure your MX Master 4 is connected and powered on
- Check that the USB receiver is plugged in or Bluetooth is connected
- Try running `lsusb` to verify the device is recognized

### No Haptic Feedback

- Verify notifications are working: `notify-send "Test" "Message"`
- Check that `dbus-monitor` is installed: `which dbus-monitor`
- Run with debug logging to see D-Bus events

### Permission Issues

- You may need to add your user to the `input` group: `sudo usermod -a -G input $USER`
- Log out and back in for group changes to take effect

## License

MIT
