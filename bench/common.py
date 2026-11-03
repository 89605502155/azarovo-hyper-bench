"""Shared helpers: fresh-process runs, robust statistics, result files."""

from __future__ import annotations

import json
import os
import platform
import statistics
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TEST_URI = "test:///default"

PACKAGES = (
    "azarovo-hyper",
    "libvirt-python",
    "pyvmomi",
    "proxmoxer",
    "openstacksdk",
    "pylxd",
    "python-vagrant",
)


def summary(values: list[float]) -> dict[str, float]:
    """Median, quartiles and 95th percentile of a sample."""
    ordered = sorted(values)
    if len(ordered) == 1:
        v = ordered[0]
        return {"n": 1, "median": v, "p25": v, "p75": v, "p95": v, "min": v}
    q = statistics.quantiles(ordered, n=100, method="inclusive")
    return {
        "n": len(ordered),
        "median": statistics.median(ordered),
        "p25": q[24],
        "p75": q[74],
        "p95": q[94],
        "min": ordered[0],
    }


def fresh_python(code: str, env: dict[str, str] | None = None) -> dict:
    """Run ``code`` in a new interpreter; it must print one JSON object."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, **(env or {})},
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def environment() -> dict[str, str]:
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "missing"
    cpu = "unknown"
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return {
        "python": platform.python_version(),
        "kernel": platform.release(),
        "cpu": cpu,
        "cpus": str(os.cpu_count()),
        **versions,
    }


def save(name: str, data: dict) -> Path:
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps({"environment": environment(), **data}, indent=1))
    print(f"saved {path.relative_to(ROOT)}")
    return path
