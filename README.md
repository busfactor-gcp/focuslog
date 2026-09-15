# Focuslog

Focuslog is a fictional, offline task tracker built as a Python CLI. It stores tasks in a local JSON file and has no runtime dependencies beyond Python 3.10+.

## Try it

```sh
python -m focuslog add "Draft proposal" --priority high --tag work --due 2026-10-01
python -m focuslog list --sort-priority
python -m focuslog done 1
python -m focuslog stats
```

Use `python -m focuslog --help` for all commands. Set `FOCUSLOG_FILE` or pass `--data PATH` before a command to choose a task file. The default is `~/.focuslog/tasks.json`. Data is created on the first `add`, or with `init`.

Commands include `add`, `list`, `done`, `remove`, `edit`, `search`, `stats`, `export`, `import`, and `clear-completed`. CSV export and import make it easy to move tasks between files.

Run tests with `python -m unittest discover -s tests`.
