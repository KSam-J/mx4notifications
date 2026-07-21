import logging
import subprocess
from time import sleep

from hid import HIDException

from ..core.mx_master_4 import FunctionID, MXMaster4


def monitor_notifications(device):
    """Monitor D-Bus for notifications using dbus-monitor."""
    cmd = [
        "dbus-monitor",
        "--session",
        "interface='org.freedesktop.Notifications',member='Notify'",
    ]

    logging.info("Starting dbus-monitor...")
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if line:
                logging.debug("D-Bus: %s", line)
                if "member=Notify" in line or "method call" in line.lower():
                    try:
                        device.hidpp(FunctionID.Haptic, 0)
                        logging.info("✓ Haptic feedback triggered!")
                    except Exception as e:
                        if str(e) == "No such device":
                            raise
                        logging.error(
                            "Failed to trigger haptic: %s\n%s", e, e.__class__.__name__
                        )
    except (KeyboardInterrupt, HIDException):
        process.terminate()
        raise


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    while True:
        device = MXMaster4.find()
        if not device:
            logging.error("MX Master 4 not found!")
            sleep(2)
            continue

        try:
            with device as dev:
                logging.info("MX Master 4 connected!")
                logging.info("Listening for notifications... Press Ctrl+C to stop.")
                logging.info("Test with: notify-send 'Test' 'Message'")
                logging.info("")

                monitor_notifications(dev)
        except HIDException:
            continue
        except KeyboardInterrupt:
            logging.info("\nStopping...")
            break


if __name__ == "__main__":
    main()
