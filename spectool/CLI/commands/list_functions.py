"""spectool list-functions — enumerate all C functions in a project directory."""

import os

from ..registry import command
from ..io import emit_json, fail
from ..vendored import slice_engine


@command(name="list-functions",
         help="List all C functions found in a project directory.")
def configure(parser):
    parser.add_argument("--project-dir", required=True,
                        help="Path to the project source directory.")


def run(args):
    if not os.path.isdir(args.project_dir):
        fail("project directory not found: %s" % args.project_dir)

    _, all_functions, _, _ = slice_engine.build_project_index(args.project_dir)

    funcs = []
    for name, info in sorted(all_functions.items()):
        funcs.append({
            "name": name,
            "file": info["file"],
            "start_line": info["sig_start"] + 1,
            "end_line": info["end"] + 1,
            "lines": info["end"] - info["sig_start"] + 1,
        })

    emit_json({
        "ok": True,
        "count": len(funcs),
        "functions": funcs,
    })
