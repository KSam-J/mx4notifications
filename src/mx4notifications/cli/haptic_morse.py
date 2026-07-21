import logging
import time

from ..core.mx_master_4 import FunctionID, MXMaster4

# Adjustable waits after each pulse marker (in seconds).
# Both dot and dash currently send the same haptic payload (0); duration here
# controls spacing/timing, not a device-side "short" vs "long" haptic type.
DOT_DURATION = 0.1
DASH_DURATION = 0.3
GAP_DURATION = 0.2


def send_morse_haptic(pattern: str):
    """
    Sends a timed haptic pattern to the MX Master 4 mouse based on dots (.) and dashes (-).
    :param pattern: String containing '.' for short pulses and '-' for long pulses.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not all(ch in [".", "-", " "] for ch in pattern):
        logging.error("Invalid pattern: Only '.', '-', and spaces are allowed.")
        return False

    device = MXMaster4.find()
    if not device:
        logging.error("MX Master 4 not found!")
        return False

    with device as dev:
        try:
            for ch in pattern:
                if ch == ".":
                    dev.hidpp(FunctionID.Haptic, 0)
                    logging.info("Dot marker: payload 0 pulse")
                    time.sleep(DOT_DURATION)
                elif ch == "-":
                    dev.hidpp(FunctionID.Haptic, 0)
                    logging.info("Dash marker: payload 0 pulse")
                    time.sleep(DASH_DURATION)
                elif ch == " ":
                    logging.info("Space: pause")
                    time.sleep(GAP_DURATION)
                time.sleep(GAP_DURATION)

            logging.info("✓ Morse-like haptic pattern sent!")
            return True
        except Exception as e:
            logging.error("Failed to send haptic pattern: %s", e)
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Send a Morse-like haptic pattern.")
    parser.add_argument("pattern", nargs="?", default="... --- ...", help="Dots, dashes, and spaces")
    args = parser.parse_args()
    raise SystemExit(0 if send_morse_haptic(args.pattern) else 1)


if __name__ == "__main__":
    main()
