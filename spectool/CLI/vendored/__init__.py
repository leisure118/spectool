"""Vendored, cleaned-up extractions from the two code quarries.

Every module here is a fresh, self-contained reimplementation of a deterministic
fragment originally found in autospec+/ or FM-Agent/ — with all LLM calls,
global state, and cross-project imports removed (docs/design.md §4, §5.4).
spectool depends only on this package + external binaries; the quarry dirs may
be deleted after extraction.
"""
