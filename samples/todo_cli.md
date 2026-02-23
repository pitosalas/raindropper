# Project Specification: todo-cli

## What
A command-line tool for managing a personal to-do list. Tasks are stored locally in a JSON file.

## Who
Individual developers who prefer the terminal over GUI apps.

## Problem
Switching to a browser or GUI app to track tasks breaks flow. A fast CLI keeps you in the terminal.

## Key Features
- Add a task with a short description
- List all tasks (with index, description, done status)
- Mark a task done by index
- Delete a task by index
- Persist tasks across sessions (JSON file in user home dir)

## Constraints
- Python 3.10+
- No third-party dependencies (stdlib only: `json`, `argparse`, `pathlib`)
- Single-file script: `todo.py`
- Runs on macOS and Linux

## Out of Scope
- Due dates, priorities, or tags
- Syncing across machines
- TUI or interactive mode
