# stitch-ptrn

A Python tool for solving and visualizing the **Open Chinese Postman Problem (Open CPP)** on undirected graphs and multigraphs (supporting parallel edges with weights).

The solver finds the minimum-cost walk that traverses every edge at least once starting from a specified `source` node and ending at a `target` node, using Minimum Weight Perfect Matching (MWPM) and Hierholzer's algorithm.

## Environment Setup

### 1. Install `uv` (if not already installed)

Verify installation:
```bash
uv --version
```

### 2. Install Project Dependencies

Clone the repository and run `uv sync` from the project root:

```bash
uv sync
```

This will automatically:
- Download/detect Python 3.14 (pinned in `.python-version`).
- Create a virtual environment at `.venv/`.
- Install dependencies (`networkx`, `matplotlib`, and their prerequisites) locked in `uv.lock`.

## Execution

### Run with `uv run`

Execute the script directly inside the project environment without manual activation:

```bash
uv run python Open_CPP.py
```

### Run with Activated Virtual Environment (Optional)

You can also activate the virtual environment manually:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

python Open_CPP.py
```

## VS Code Setup

The repository includes pre-configured settings:
- **Interpreter Path** (`.vscode/settings.json`): Automatically targets `${workspaceFolder}/.venv/bin/python`.
- **Debugging** (`.vscode/launch.json`): Press <kbd>F5</kbd> in VS Code to run and debug the active file with `debugpy`.
  - You need to open a `.py` file to debug the active python script

## Project Structure

```
stitch-pattern/
├── .python-version      # Pinned Python version (3.14)
├── .vscode/             # VS Code launch and settings configurations
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Deterministic dependency lockfile
├── Open_CPP.py          # Core algorithm, visualization, and example script
└── README.md            # Setup and usage guide
```