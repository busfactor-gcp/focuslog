# Focuslog

A small task list for your terminal. Focuslog tracks priorities, tags, and due dates in a local JSON file, with no account or service to set up. It runs on Python 3.10+ without runtime dependencies.

## Quick start

```sh
python -m focuslog add "Send proposal" --priority high --tag work --due 2026-10-01
python -m focuslog list --sort-priority
python -m focuslog done 1
python -m focuslog stats
```

Run `python -m pip install .` to use `focuslog` in place of `python -m focuslog`. Use `--help` to explore commands for editing, searching, removing, and clearing tasks.

## Your data

Tasks live in `~/.focuslog/tasks.json`. Pass `--data PATH` **before** a command or set `FOCUSLOG_FILE` to use another file. Focuslog creates it on the first `add`; `init` creates an empty one.

Move tasks between files with `export` and `import`:

```sh
python -m focuslog export tasks.csv
python -m focuslog --data another.json import tasks.csv
```

Run the tests with `python -m unittest discover -s tests`.
