"""Installation footprint: time, number of distributions and disk size.

Each library is installed with uv into a fresh virtual environment with the
cache disabled, so every run downloads (and, for sdists, builds) from scratch.
``libvirt-python`` ships only as source and needs the libvirt headers and a C
compiler; the other packages install from wheels.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from bench.common import save, summary

REQUIREMENTS = {
    "azarovo-hyper": "azarovo-hyper==0.0.2",
    "libvirt-python": "libvirt-python==12.9.0",
    "pyvmomi": "pyvmomi==9.1.1.0",
    "proxmoxer": "proxmoxer==2.3.0",
    "openstacksdk": "openstacksdk==4.22.0",
    "pylxd": "pylxd==2.4.2",
    "python-vagrant": "python-vagrant==1.0.0",
}


def site_packages(venv: Path) -> Path:
    return next(venv.glob("lib/python*/site-packages"))


def size_mib(path: Path) -> float:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024**2


def install_once(requirement: str) -> dict[str, float]:
    with tempfile.TemporaryDirectory() as tmp:
        venv = Path(tmp) / "venv"
        python = f"{sys.version_info.major}.{sys.version_info.minor}"
        subprocess.run(["uv", "venv", "-q", "--python", python, str(venv)], check=True)
        empty = {p.name for p in site_packages(venv).iterdir()}
        start = time.perf_counter()
        subprocess.run(
            ["uv", "pip", "install", "-q", "--no-cache", "--python", str(venv), requirement],
            check=True,
        )
        seconds = time.perf_counter() - start
        packages = site_packages(venv)
        dists = [p for p in packages.glob("*.dist-info")]
        added = {p.name for p in packages.iterdir()} - empty
        return {
            "seconds": seconds,
            "distributions": len(dists),
            "size_mib": sum(
                size_mib(packages / name)
                if (packages / name).is_dir()
                else (packages / name).stat().st_size / 1024**2
                for name in added
            ),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if shutil.which("uv") is None:
        sys.exit("uv is required: https://docs.astral.sh/uv/")
    results = {}
    for name, requirement in REQUIREMENTS.items():
        runs = [install_once(requirement) for _ in range(args.repeats)]
        results[name] = {key: summary([r[key] for r in runs]) for key in runs[0]}
        r = {k: v["median"] for k, v in results[name].items()}
        print(
            f"{name:15} {r['seconds']:6.1f} s  {r['distributions']:3.0f} dists  "
            f"{r['size_mib']:7.1f} MiB"
        )
    save("install", {"repeats": args.repeats, "libraries": results})


if __name__ == "__main__":
    main()
