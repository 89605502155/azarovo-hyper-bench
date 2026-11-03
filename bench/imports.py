"""Cost of importing each library: wall time and resident memory growth.

Every sample runs in a fresh interpreter, so caches of earlier imports never
help. The time covers only the import statement, not interpreter start-up.
"""

from __future__ import annotations

import argparse

from bench.common import fresh_python, save, summary

#: library -> import statement of its public entry point
LIBRARIES = {
    "azarovo-hyper": "import azarovo_hyper",
    "libvirt-python": "import libvirt",
    "pyvmomi": "from pyVim import connect",
    "proxmoxer": "from proxmoxer import ProxmoxAPI",
    "openstacksdk": "import openstack",
    "pylxd": "import pylxd",
    "python-vagrant": "import vagrant",
}

PROBE = """
import json, time
def rss():
    for line in open("/proc/self/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
before = rss()
start = time.perf_counter()
{statement}
elapsed = time.perf_counter() - start
print(json.dumps({{"seconds": elapsed, "rss_kib": rss() - before}}))
"""


def measure(statement: str, repeats: int) -> dict:
    runs = [fresh_python(PROBE.format(statement=statement)) for _ in range(repeats)]
    return {
        "milliseconds": summary([r["seconds"] * 1000 for r in runs]),
        "rss_mib": summary([r["rss_kib"] / 1024 for r in runs]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=30)
    args = parser.parse_args()
    results = {}
    for name, statement in LIBRARIES.items():
        results[name] = measure(statement, args.repeats)
        ms, mib = results[name]["milliseconds"]["median"], results[name]["rss_mib"]["median"]
        print(f"{name:15} import {ms:8.1f} ms   +{mib:6.1f} MiB")
    save("imports", {"repeats": args.repeats, "libraries": results})


if __name__ == "__main__":
    main()
