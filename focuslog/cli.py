"""Command line interface for Focuslog."""


import argparse
import os
import sys
from pathlib import Path
from .storage import load_tasks, save_tasks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="focuslog", description="A small local task tracker")
    parser.add_argument("--data", type=Path, default=Path(os.environ.get("FOCUSLOG_FILE", Path.home() / ".focuslog" / "tasks.json")), help="JSON task file")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("init", help="create an empty task file")
    cmd.add_argument("--force", action="store_true", help="replace an existing task file")
    cmd.set_defaults(handler=init_tasks)
    return parser


def init_tasks(args: argparse.Namespace) -> int:
    if args.data.exists() and not args.force:
        raise ValueError(f"{args.data} already exists; use --force to replace it")
    save_tasks(args.data, [])
    print(f"Initialized {args.data}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"focuslog: {exc}", file=sys.stderr)
        return 2
