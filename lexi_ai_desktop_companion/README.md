# Lexi.AI Desktop Companion

A local, template-based desktop project companion.

This first build does **not** call an online AI model. It generates project notes, design signals, briefs, tasks, and safe workspaces from local templates and keyword heuristics.

## Features

- Local project memory
- Template-based project note generation
- Template-based design signal generation
- Brief generation
- Safe workspace creation
- No destructive file actions
- Versioned writes instead of overwrites
- Optional autonomous draft mode
- Tkinter desktop UI
- No external dependencies

## Run

```bash
python main.py
```

Use Python 3.10 or newer.

## Data location

By default, Lexi stores local data here:

```txt
~/.lexi_ai_companion/
```

Inside that folder:

```txt
data/
  projects.json
  logs.jsonl
workspaces/
  your-project/
```

## Safety model

Lexi can generate drafts automatically, but it does not delete files, execute shell commands, or overwrite workspace files directly.

Workspace creation asks for confirmation first.

Existing files are preserved by writing versioned files instead.

## Optional packaging

After testing locally, you can package the app with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

PyInstaller is optional and not required to run the project.
