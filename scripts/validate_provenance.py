#!/usr/bin/env python3
"""Offline structural check; does not authenticate a review or grant access."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trace_gate.provenance import validate_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--trusted-reviews", type=Path,
                        help="Host-authenticated review bindings, never model-generated approvals")
    args = parser.parse_args()
    try:
        reviews = json.loads(args.trusted_reviews.read_text()) if args.trusted_reviews else None
        receipt = validate_bundle(json.loads(args.bundle.read_text()), trusted_reviews=reviews)
    except Exception as exc:
        # jsonschema exceptions can contain instance values: never echo them.
        code = str(exc) if type(exc) is ValueError and str(exc).isupper() else type(exc).__name__
        print(json.dumps({"status": "FAIL_CLOSED", "error_code": code, "access_granted": False}))
        return 2
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
