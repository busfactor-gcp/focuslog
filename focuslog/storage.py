'''Simple local JSON persistence.'''

import json
import os
import tempfile
from pathlib import Path


def load_tasks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != 1 or not isinstance(payload.get("tasks"), list):
        raise ValueError(f"unsupported task file: {path}")
    return payload["tasks"]


def save_tasks(path: Path, tasks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".focuslog-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"schema": 1, "tasks": tasks}, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
