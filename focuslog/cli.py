"""Command line interface for Focuslog."""


import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path
from .storage import load_tasks, save_tasks



def next_id(tasks: list[dict]) -> int:
    return max((task["id"] for task in tasks), default=0) + 1



def find_task(tasks: list[dict], task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise ValueError(f"task #{task_id} not found")



def normalize_tags(values: list[str]) -> list[str]:
    tags = []
    for value in values:
        tag = value.strip().lower()
        if not tag or "," in tag:
            raise ValueError("tags must be nonempty and cannot contain commas")
        if tag not in tags:
            tags.append(tag)
    return tags



def parse_due(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("due date must be YYYY-MM-DD") from exc



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="focuslog", description="A small local task tracker")
    parser.add_argument("--data", type=Path, default=Path(os.environ.get("FOCUSLOG_FILE", Path.home() / ".focuslog" / "tasks.json")), help="JSON task file")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("init", help="create an empty task file")
    cmd.add_argument("--force", action="store_true", help="replace an existing task file")
    cmd.set_defaults(handler=init_tasks)
    cmd = sub.add_parser("add", help="add a task")
    cmd.add_argument("title", help="task title")
    cmd.add_argument("--priority", choices=("low", "normal", "high"), default="normal")
    cmd.add_argument("--tag", action="append", default=[], help="repeat to add multiple tags")
    cmd.add_argument("--due", help="due date as YYYY-MM-DD")
    cmd.set_defaults(handler=add_task)
    cmd = sub.add_parser("list", help="show tasks")
    cmd.add_argument("--priority", choices=("low", "normal", "high"))
    cmd.add_argument("--sort-priority", action="store_true", help="show high priority first")
    cmd.add_argument("--tag", help="show tasks with this tag")
    cmd.add_argument("--due-before", help="show tasks due before YYYY-MM-DD")
    cmd.set_defaults(handler=list_tasks)
    cmd = sub.add_parser("done", help="mark a task complete")
    cmd.add_argument("id", type=int)
    cmd.set_defaults(handler=complete_task)
    cmd = sub.add_parser("remove", help="remove a task")
    cmd.add_argument("id", type=int)
    cmd.set_defaults(handler=remove_task)
    cmd = sub.add_parser("search", help="search task titles")
    cmd.add_argument("query")
    cmd.set_defaults(handler=search_tasks)
    cmd = sub.add_parser("stats", help="summarize task progress")
    cmd.set_defaults(handler=show_stats)
    cmd = sub.add_parser("edit", help="change a task")
    cmd.add_argument("id", type=int)
    cmd.add_argument("--title")
    cmd.add_argument("--priority", choices=("low", "normal", "high"))
    due_group = cmd.add_mutually_exclusive_group()
    due_group.add_argument("--due")
    due_group.add_argument("--clear-due", action="store_true")
    cmd.set_defaults(handler=edit_task)
    cmd = sub.add_parser("export", help="export tasks to CSV")
    cmd.add_argument("path", type=Path)
    cmd.set_defaults(handler=export_csv)
    return parser


def init_tasks(args: argparse.Namespace) -> int:
    if args.data.exists() and not args.force:
        raise ValueError(f"{args.data} already exists; use --force to replace it")
    save_tasks(args.data, [])
    print(f"Initialized {args.data}")
    return 0

def add_task(args: argparse.Namespace) -> int:
    title = args.title.strip()
    if not title:
        raise ValueError("title cannot be empty")
    tags = normalize_tags(args.tag)
    due = parse_due(args.due) if args.due else None
    tasks = load_tasks(args.data)
    task = {"id": next_id(tasks), "title": title, "done": False, "priority": args.priority, "tags": tags, "due": due}
    tasks.append(task)
    save_tasks(args.data, tasks)
    print(f"Added #{task['id']}: {title}")
    return 0

def list_tasks(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)
    if args.priority:
        tasks = [task for task in tasks if task.get("priority", "normal") == args.priority]
    if args.tag:
        tasks = [task for task in tasks if args.tag.lower() in task.get("tags", [])]
    if args.due_before:
        cutoff = parse_due(args.due_before)
        tasks = [task for task in tasks if task.get("due") and task["due"] < cutoff]
    if args.sort_priority:
        rank = {"high": 0, "normal": 1, "low": 2}
        tasks.sort(key=lambda task: (rank[task.get("priority", "normal")], task["id"]))
    if not tasks:
        print("No tasks found.")
        return 0
    for task in tasks:
        state = "x" if task["done"] else " "
        tags = ",".join(task.get("tags", [])) or "-"
        due = task.get("due") or "-"
        print(f"{task['id']:>3} [{state}] {task.get('priority', 'normal'):<6} {due:<10} {tags:<16} {task['title']}")
    return 0

def complete_task(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)
    task = find_task(tasks, args.id)
    if task["done"]:
        raise ValueError(f"task #{args.id} is already complete")
    task["done"] = True
    save_tasks(args.data, tasks)
    print(f"Completed #{args.id}")
    return 0

def remove_task(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)
    task = find_task(tasks, args.id)
    tasks.remove(task)
    save_tasks(args.data, tasks)
    print(f"Removed #{args.id}")
    return 0

def search_tasks(args: argparse.Namespace) -> int:
    query = args.query.strip().casefold()
    if not query:
        raise ValueError("search query cannot be empty")
    matches = [task for task in load_tasks(args.data) if query in task["title"].casefold()]
    if not matches:
        print("No tasks found.")
        return 0
    for task in matches:
        state = "x" if task["done"] else " "
        print(f"{task['id']:>3} [{state}] {task['title']}")
    return 0

def show_stats(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)
    total = len(tasks)
    done = sum(task["done"] for task in tasks)
    print(f"Total: {total}")
    print(f"Open: {total - done}")
    print(f"Complete: {done}")
    for priority in ("high", "normal", "low"):
        count = sum(not task["done"] and task.get("priority", "normal") == priority for task in tasks)
        print(f"Open {priority}: {count}")
    return 0

def edit_task(args: argparse.Namespace) -> int:
    if args.title is None and args.priority is None and args.due is None and not args.clear_due:
        raise ValueError("specify at least one change")
    title = args.title.strip() if args.title is not None else None
    if title is not None and not title:
        raise ValueError("title cannot be empty")
    due = parse_due(args.due) if args.due else None
    tasks = load_tasks(args.data)
    task = find_task(tasks, args.id)
    if title is not None:
        task["title"] = title
    if args.priority is not None:
        task["priority"] = args.priority
    if args.due is not None:
        task["due"] = due
    if args.clear_due:
        task["due"] = None
    save_tasks(args.data, tasks)
    print(f"Updated #{args.id}")
    return 0

def export_csv(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)
    args.path.parent.mkdir(parents=True, exist_ok=True)
    with args.path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("id", "title", "done", "priority", "tags", "due"))
        writer.writeheader()
        for task in tasks:
            writer.writerow({
                "id": task["id"],
                "title": task["title"],
                "done": str(task["done"]).lower(),
                "priority": task.get("priority", "normal"),
                "tags": ",".join(task.get("tags", [])),
                "due": task.get("due") or "",
            })
    print(f"Exported {len(tasks)} tasks to {args.path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"focuslog: {exc}", file=sys.stderr)
        return 2
