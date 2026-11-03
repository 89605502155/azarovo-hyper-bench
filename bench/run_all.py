"""Run every benchmark with the sample sizes used in the article."""

from __future__ import annotations

import os
import subprocess
import sys

STEPS = [
    ["bench.imports", "--repeats", "30"],
    ["bench.operations", "--repeats", "2000"],
    ["bench.install", "--repeats", "3"],
    ["bench.loc"],
    ["bench.race", "--trials", "100", "--threads", "16"],
]
KVM_STEP = ["bench.kvm_context", "--repeats", "20"]


def main() -> None:
    steps = list(STEPS)
    if os.access("/dev/kvm", os.R_OK | os.W_OK):
        steps.append(KVM_STEP)
    else:
        print("no /dev/kvm: skipping bench.kvm_context")
    for module, *args in steps:
        print(f"\n=== {module} {' '.join(args)}", flush=True)
        subprocess.run([sys.executable, "-m", module, *args], check=True)


if __name__ == "__main__":
    main()
