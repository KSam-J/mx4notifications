from .haptic_morse import main as morse_main
from .send_haptic import main as send_main
from .watch import main as watch_main


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="mx4notifications")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("watch", help="Monitor desktop notifications and trigger haptics")

    send_parser = subcommands.add_parser("send-haptic", help="Send a single haptic payload")
    send_parser.add_argument("args", nargs=argparse.REMAINDER)

    morse_parser = subcommands.add_parser("haptic-morse", help="Send a Morse-like pattern")
    morse_parser.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.command == "watch":
        return watch_main()
    if args.command == "send-haptic":
        import sys

        sys.argv = [sys.argv[0], *args.args]
        return send_main()
    if args.command == "haptic-morse":
        import sys

        sys.argv = [sys.argv[0], *args.args]
        return morse_main()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
