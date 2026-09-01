"""Command line interface for Focuslog."""


import argparse
import os
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="focuslog", description="A small local task tracker")
    parser.add_argument("--data", type=Path, default=Path(os.environ.get("FOCUSLOG_FILE", Path.home() / ".focuslog" / "tasks.json")), help="JSON task file")
    sub = parser.add_subparsers(dest="command", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"focuslog: {exc}", file=sys.stderr)
        return 2
