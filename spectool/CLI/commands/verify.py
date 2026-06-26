"""spectool verify — run frama-c -wp and report proved/total goals.

The core, highest-frequency command (docs/design.md §5.3). Deterministic judge.
"""

import os

from ..registry import command
from ..io import emit_json, fail, log, EXIT_TOOL_MISSING
from ..vendored import framac


@command(name="verify", help="Run frama-c -wp on an annotated C file; report proved/total goals.")
def configure(parser):
    parser.add_argument("-f", "--file", required=True, help="Annotated C file to verify.")
    parser.add_argument("--timeout", type=int, default=8, help="Per-goal WP prover timeout (s).")
    parser.add_argument("--save-stdout", default=None,
                        help="Optional path to write raw WP stdout (for locate-fail).")


def run(args):
    if not os.path.exists(args.file):
        fail("input C file not found: %s" % args.file)

    try:
        res = framac.run_framac_with_wp(args.file, timeout=args.timeout)
    except FileNotFoundError as e:
        fail(str(e), code=EXIT_TOOL_MISSING)

    rtype = res["result_type"]
    stdout_file = args.save_stdout
    if stdout_file:
        with open(stdout_file, "w", encoding="utf-8") as f:
            f.write(res["stdout"])
        log("[verify] WP stdout saved to %s" % stdout_file)

    if rtype == "Invalid":
        # Not a "tool missing" — frama-c ran but produced no usable goals.
        emit_json({
            "result": "Invalid",
            "proved": None,
            "total": None,
            "raw_result_type": rtype,
            "stdout_file": stdout_file,
            "elapsed_sec": res["elapsed_sec"],
            "timed_out": res["timed_out"],
            "hint": "frama-c could not generate goals (syntax error, missing include, or aborted).",
        })

    verdict = framac.verdict_of(rtype)
    proved, total = framac.parse_proved(rtype)
    if verdict == "Unknown":
        emit_json({
            "result": "Unknown",
            "proved": proved,
            "total": total,
            "raw_result_type": rtype,
            "stdout_file": stdout_file,
            "elapsed_sec": res["elapsed_sec"],
            "stderr_tail": res["stderr"][-2000:],
        })

    emit_json({
        "result": verdict,           # trusts Pass_/Fail_ prefix (handles tolerated goals)
        "proved": proved,
        "total": total,
        "raw_result_type": rtype,
        "stdout_file": stdout_file,
        "elapsed_sec": res["elapsed_sec"],
    })
