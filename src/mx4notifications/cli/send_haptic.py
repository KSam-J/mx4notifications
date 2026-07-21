import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..core.mx_master_4 import FunctionID, MXMaster4

LABEL_MAP = {
    "s": "short",
    "short": "short",
    "l": "long",
    "long": "long",
    "d": "double",
    "double": "double",
    "n": "none",
    "none": "none",
    "o": "other",
    "other": "other",
}


def parse_payloads(payload_spec: str) -> list[int]:
    payload_spec = payload_spec.strip()
    if not payload_spec:
        raise ValueError("payload range cannot be empty")

    if "," in payload_spec:
        values = [part.strip() for part in payload_spec.split(",")]
        payloads = [int(value) for value in values if value]
    elif "-" in payload_spec:
        start_raw, end_raw = payload_spec.split("-", 1)
        start = int(start_raw.strip())
        end = int(end_raw.strip())
        if end < start:
            raise ValueError("range end must be greater than or equal to range start")
        payloads = list(range(start, end + 1))
    else:
        payloads = [int(payload_spec)]

    if not payloads:
        raise ValueError("no payloads were parsed")

    for payload in payloads:
        if payload < 0 or payload > 255:
            raise ValueError("payload values must be between 0 and 255")

    return list(dict.fromkeys(payloads))


def save_discovery_results(path: Path, payloads: list[int], results: list[dict]) -> None:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payloads_tested": payloads,
        "results": results,
        "labels": ["short", "long", "double", "none", "other"],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def prompt_haptic_type(payload: int) -> tuple[str, str]:
    print(f"\nSent payload {payload}. What type of haptic did you feel?")
    print("Choose: [s]hort, [l]ong, [d]ouble, [n]one, [o]ther, [q]uit")

    while True:
        choice = input("Type: ").strip().lower()
        if choice == "q":
            return "quit", ""

        label = LABEL_MAP.get(choice)
        if not label:
            print("Invalid choice. Use s/l/d/n/o/q.")
            continue

        if label == "other":
            notes = input("Describe what you felt: ").strip()
            return label, notes

        return label, ""


def send_haptic(payload: int = 0) -> bool:
    device = MXMaster4.find()
    if not device:
        logging.error("MX Master 4 not found!")
        return False

    with device as dev:
        try:
            dev.hidpp(FunctionID.Haptic, payload)
            logging.info("✓ Haptic payload %d sent!", payload)
            return True
        except Exception as e:
            logging.error("Failed to send haptic: %s", e)
            return False


def discover_haptics(payloads: list[int], output_path: Path | None) -> bool:
    device = MXMaster4.find()
    if not device:
        logging.error("MX Master 4 not found!")
        return False

    results: list[dict] = []
    completed_payloads: list[int] = []

    with device as dev:
        for payload in payloads:
            try:
                _, data = dev.hidpp(FunctionID.Haptic, payload)
            except Exception as e:
                logging.error("Failed to send payload %d: %s", payload, e)
                results.append(
                    {
                        "payload": payload,
                        "label": "error",
                        "notes": str(e),
                        "response_hex": "",
                    }
                )
                completed_payloads.append(payload)
                continue

            label, notes = prompt_haptic_type(payload)
            if label == "quit":
                break

            results.append(
                {
                    "payload": payload,
                    "label": label,
                    "notes": notes,
                    "response_hex": data.hex(),
                }
            )
            completed_payloads.append(payload)

    if not results:
        logging.warning("No discovery results were recorded.")
        return False

    print("\nDiscovery summary:")
    for entry in results:
        suffix = f" ({entry['notes']})" if entry["notes"] else ""
        print(f"- payload {entry['payload']}: {entry['label']}{suffix}")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_discovery_results(output_path, completed_payloads, results)
        logging.info("Saved discovery results to %s", output_path)

    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send haptic feedback to MX Master 4.")
    parser.add_argument(
        "--payload",
        type=int,
        default=0,
        help="Payload value for one-shot send mode (default: 0).",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run interactive discovery mode and classify haptic types.",
    )
    parser.add_argument(
        "--range",
        dest="payload_range",
        default="0-31",
        help="Discovery payload range/list. Examples: 0-31, 0-14, 0,4,8 (default: 0-31).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to discovery results JSON. Defaults to ./haptic_discovery_results.json.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write discovery results to a JSON file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if args.discover:
        try:
            payloads = parse_payloads(args.payload_range)
        except ValueError as e:
            parser.error(str(e))

        if args.no_save:
            output_path = None
        else:
            output_path = (
                Path(args.output)
                if args.output
                else Path("haptic_discovery_results.json")
            )
        return 0 if discover_haptics(payloads, output_path) else 1

    if args.payload < 0 or args.payload > 255:
        parser.error("--payload must be between 0 and 255")

    return 0 if send_haptic(args.payload) else 1


if __name__ == "__main__":
    raise SystemExit(main())
