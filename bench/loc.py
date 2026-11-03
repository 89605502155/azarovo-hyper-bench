"""Size of the code needed for the same task, in statements.

Counts logical statements (independent of line wrapping), excluding comments,
docstrings and the ``__main__`` launcher, and checks that both tasks run.
"""

from __future__ import annotations

import ast
import io
import tempfile
import tokenize
from pathlib import Path

import libvirt

from bench.common import ROOT, TEST_URI, save

TASKS = {"azarovo-hyper": "task_azarovo.py", "libvirt-python": "task_libvirt.py"}


def logical_lines(path: Path) -> int:
    """Number of statements (NEWLINE tokens), so formatting does not matter."""
    source = path.read_text()
    tree = ast.parse(source)
    skip: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
        ):
            skip.update(range(body[0].lineno, body[0].end_lineno + 1))
        if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test):
            skip.update(range(node.lineno, node.end_lineno + 1))
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return sum(1 for tok in tokens if tok.type == tokenize.NEWLINE and tok.start[0] not in skip)


def main() -> None:
    keeper = libvirt.open(TEST_URI)
    results = {}
    for name, file in TASKS.items():
        path = ROOT / "tasks" / file
        namespace: dict = {}
        exec(compile(path.read_text(), str(path), "exec"), namespace)
        with tempfile.TemporaryDirectory() as images:
            outcome = namespace["run"](TEST_URI, images)
        results[name] = {"statements": logical_lines(path), "outcome": outcome}
        print(f"{name:15} {results[name]['statements']:3d} statements  -> {outcome}")
    keeper.close()
    save("loc", {"tasks": results})


if __name__ == "__main__":
    main()
