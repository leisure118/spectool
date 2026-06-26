# spectool

`spectool` is a deterministic command-line toolbox for ACSL specification generation and Frama-C/WP verification for C programs. It is designed for LLM-assisted or human-assisted formal specification workflows, where mechanically repeatable tasks should be handled by reliable commands: function extraction, project slicing, ACSL injection, Frama-C/WP execution, failed-goal localization, and policy checks for `//@ admit` usage.

`spectool` does not call an LLM. All commands are scriptable. The intended role of the tool is to act as a deterministic backend: a user or external agent writes, modifies, or repairs ACSL annotations, while `spectool` extracts context, injects annotations, invokes Frama-C/WP, parses results, and returns structured JSON.

## 1. Installation

Using a virtual environment is recommended to avoid system Python restrictions such as PEP 668:

```bash
git clone https://github.com/leisure118/spectool.git
cd spectool/spectool
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
spectool --help
```

If you do not want to install the package, you can also run it directly from the repository root:

```bash
PYTHONPATH=spectool python3 -m CLI --help
PYTHONPATH=spectool python3 -m CLI doctor --proj .
```

## 2. Quick Demo

Check external tools and the project directory:

```bash
spectool doctor --proj ..
```

List or extract functions from a C file:

```bash
spectool extract --src ../dataset/autobench/1.c
```

Run Frama-C/WP on a C file with ACSL annotations:

```bash
spectool verify -f input.acsl.c --timeout 8 --save-stdout wp.log
```

Locate failed goals from WP output:

```bash
spectool locate-fail --wp wp.log --src input.acsl.c
```

Check whether an `.acsl.c` file contains invalid `//@ admit` usage:

```bash
spectool check-admit -f input.acsl.c
```

## 3. Version Check

Check the installed Python package version:

```bash
cd spectool
python - <<'PY'
import CLI
print(CLI.__version__)
PY
```

The expected output is:

```text
0.1.0
```

The version is defined in:

- `[project].version` in `spectool/pyproject.toml`
- `__version__` in `spectool/CLI/__init__.py`

## 4. Command-Line Interface Contract

All subcommands follow the same interface convention:

- stdout: JSON only, suitable for scripts, agents, and CI;
- stderr: human-readable logs;
- exit code:
  - `0`: success;
  - `2`: external tool missing or unusable;
  - `3`: invalid input;
  - `1`: unexpected internal error.

Main commands:

| Command | Purpose |
|---|---|
| `doctor` | Check Frama-C, veri-clang, provers, and project directory availability. |
| `extract` | List functions in a C file or extract one function. |
| `slice` | Generate a minimal slice for a target function. |
| `inject` | Inject ACSL function contracts and loop annotations into a C file. |
| `verify` | Invoke Frama-C/WP and return `{result, proved, total}`. |
| `locate-fail` | Parse WP output and locate failed goals. |
| `check-admit` | Check whether `.acsl.c` files contain invalid `//@ admit` usage. |
| `init-contracts` / `fill-contracts` / `save-contract` | Maintain bottom-up function contract state. |

View the full command help:

```bash
spectool --help
spectool <command> --help
```

## 5. External Dependencies

The Python package itself only uses the standard library. The following tools are external dependencies:

- Frama-C: the main backend for `verify`;
- Alt-Ergo or Z3: provers used by Frama-C/WP;
- veri-clang: used for some repo-scale analysis scenarios, but not required by every command.

`doctor` reports whether external tools are available. If Frama-C or a prover is missing, commands that do not require verification, such as extraction, injection, and admit checking, can still be used.

## 6. Repository Layout

```text
.
├── LICENSE                  # MIT License
├── README.md                # Installation, demo, and usage guide
├── .claude/skills/          # Skill descriptions for specification workflows
├── dataset/                 # AutoBench, live24, and live25 C benchmarks
├── scripts/                 # Helper scripts
└── spectool/
    ├── CLI/                 # Python CLI package
    │   ├── commands/        # One command per file
    │   └── vendored/        # Core extraction, injection, and WP-output parsing logic
    ├── SKILL.md             # Tool capability summary
    └── pyproject.toml       # Python package metadata and console script
```
