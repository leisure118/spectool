"""spectool doctor — environment health check.

Per docs/design.md §8.5: since the toolchain ships in the acslagent image, this
is a "mount + versions" sanity check rather than an install verifier. Reports
which external binaries are present and their versions so Claude can confirm
the workspace is wired up before starting.
"""

import os
import shutil
import subprocess

from ..registry import command
from ..io import emit_json


_BINARIES = [
    ("frama-c", os.environ.get("SPECTOOL_FRAMAC", "frama-c"), ["-version"]),
    ("veri-clang", os.environ.get("SPECTOOL_VERI_CLANG", "veri-clang"), ["--version"]),
    ("alt-ergo", "alt-ergo", ["--version"]),
    ("z3", "z3", ["--version"]),
]


@command(name="doctor",
         help="Check that frama-c / veri-clang / provers are present and report versions.")
def configure(parser):
    parser.add_argument("--proj", default=".", help="Project root to confirm is accessible.")


def _probe(binary, version_args):
    path = shutil.which(binary)
    if not path:
        return {"present": False, "path": None, "version": None}
    version = None
    try:
        out = subprocess.run([binary] + version_args, capture_output=True, text=True, timeout=20)
        version = (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else None
    except Exception:
        pass
    return {"present": True, "path": path, "version": version}


def run(args):
    tools = {}
    for label, binary, vargs in _BINARIES:
        tools[label] = _probe(binary, vargs)

    proj_ok = os.path.isdir(args.proj) and os.access(args.proj, os.W_OK)

    # frama-c + at least one prover is the minimum to run `verify`.
    core_ok = tools["frama-c"]["present"] and (
        tools["alt-ergo"]["present"] or tools["z3"]["present"]
    )

    missing = [name for name, info in tools.items() if not info["present"]]

    emit_json({
        "ready": bool(core_ok and proj_ok),
        "core_ready": bool(core_ok),
        "proj_writable": proj_ok,
        "proj": os.path.abspath(args.proj),
        "tools": tools,
        "missing": missing,
        "note": "core_ready requires frama-c + (alt-ergo or z3). veri-clang only needed for repo-scale analyze.",
    })
