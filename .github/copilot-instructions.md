# Copilot Instructions for `mx4notifications`

## Build, test, and lint commands

This repository currently ships as runnable entry points (no dedicated build, lint, or automated test suite is configured in `pyproject.toml`).

### Environment setup

```bash
pdm install
```

Alternative dependency install:

```bash
pip install hid dbus-python pygobject
```

### Run the main app

```bash
pdm run mx4notifications-watch
```

### Single-test / smoke-test commands

Send one haptic pulse directly (quick device test):

```bash
pdm run mx4notifications-send-haptic
```

Trigger one desktop notification while the watcher is running:

```bash
notify-send "Test Notification" "You should feel vibration on your mouse!"
```

Explore all built-in haptic IDs:

```bash
pdm run python src/mx_master_4.py
```

## High-level architecture

The project is organized around one hardware protocol layer plus small executable modules:

1. `src/mx_master_4.py` is the core HID++ integration layer.
   - Discovers Logitech devices via `hid.enumerate(LOGITECH_VID)` and filters by `usage_page == 65280`.
   - Wraps device lifecycle with a context manager (`with device as dev:`).
   - Encodes HID++ requests (`hidpp`) and decodes responses (`read`) including short vs long report handling.
2. `src/mx4notifications/cli/watch.py` is the long-running notification bridge.
   - Spawns `dbus-monitor` for `org.freedesktop.Notifications` `Notify` calls.
   - On matching lines, sends `FunctionID.Haptic` commands through `MXMaster4`.
   - Runs a reconnect loop: if HID disconnects (`HIDException` / `No such device` path), it re-finds the mouse and resumes.
3. `src/mx4notifications/cli/send_haptic.py` and `src/mx4notifications/cli/haptic_morse.py` are utility entry points that reuse `MXMaster4` for one-shot/manual patterns.

## Key conventions in this codebase

- Keep HID protocol details centralized in `MXMaster4`; scripts should call `dev.hidpp(...)` rather than writing raw HID packets.
- Always open hardware access with the `MXMaster4` context manager (`with device as dev:`) to ensure proper close behavior.
- For standard vibration behavior, use `FunctionID.Haptic` with payload `0` (current default pulse used by watcher and helper scripts).
- In the notification watcher flow, device-loss errors should bubble to the outer reconnect loop rather than being silently ignored.
- Runtime entry points are exposed via `project.scripts` in `pyproject.toml`, with implementations under `src/mx4notifications/cli/`.
- Linux desktop notifications are consumed through the external `dbus-monitor` process; this runtime dependency is required for `mx4notifications.cli.watch`.
