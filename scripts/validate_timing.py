#!/usr/bin/env python3
"""Validate spoken-script length and simple shot-plan limits."""

import argparse
import json
import sys
import unicodedata


LIMITS = {
    (15, "talk"): {"min": 55, "max": 75, "segments": 4, "actions": 2},
    (15, "demo"): {"min": 45, "max": 65, "segments": 4, "actions": 2},
    (30, "talk"): {"min": 115, "max": 150, "segments": 5, "actions": 2},
    (30, "demo"): {"min": 95, "max": 125, "segments": 5, "actions": 3},
    (60, "talk"): {"min": 220, "max": 280, "segments": 8, "actions": 3},
    (60, "demo"): {"min": 190, "max": 250, "segments": 8, "actions": 5},
}


def speech_unit_count(text: str) -> int:
    """Count visible spoken units while ignoring whitespace and punctuation."""
    count = 0
    for char in text:
        category = unicodedata.category(char)
        if category.startswith(("P", "Z", "C", "S")):
            continue
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, choices=(15, 30, 60), required=True)
    parser.add_argument("--mode", choices=("talk", "demo"), required=True)
    parser.add_argument("--segments", type=int, required=True)
    parser.add_argument("--actions", type=int, required=True)
    parser.add_argument("--text")
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    limits = LIMITS[(args.duration, args.mode)]
    units = speech_unit_count(text)

    checks = {
        "length": limits["min"] <= units <= limits["max"],
        "segments": args.segments <= limits["segments"],
        "actions": args.actions <= limits["actions"],
    }
    result = {
        "pass": all(checks.values()),
        "duration_seconds": args.duration,
        "mode": args.mode,
        "speech_units": units,
        "allowed_speech_units": [limits["min"], limits["max"]],
        "segments": args.segments,
        "max_segments": limits["segments"],
        "actions": args.actions,
        "max_actions": limits["actions"],
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
