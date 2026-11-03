"""Duration of the same operations on a real KVM guest (qemu:///session).

This is hypervisor time, measured with the official binding only. It puts the
library overhead from ``operations.py`` into proportion. Needs /dev/kvm and
libvirt; skipped otherwise.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import libvirt

from bench.common import save, summary
from tasks.task_libvirt import XML

URI = os.environ.get("BENCH_KVM_URI", "qemu:///session")


def ms(call) -> float:
    start = time.perf_counter()
    call()
    return (time.perf_counter() - start) * 1000


def cycle(dom, samples: dict[str, list[float]], live: int) -> None:
    """Start, resize, sample and stop one defined guest, timing each step."""
    samples["start"].append(ms(dom.create))
    samples["balloon"].append(ms(lambda: dom.setMemoryFlags(768 * 1024, live)))
    samples["vcpus"].append(ms(lambda: dom.setVcpusFlags(3, live)))
    samples["metrics"].append(ms(lambda: (dom.info(), dom.memoryStats(), dom.blockStats("vda"))))
    samples["stop"].append(ms(dom.destroy))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        sys.exit("needs /dev/kvm")
    conn = libvirt.open(URI)
    live = libvirt.VIR_DOMAIN_AFFECT_LIVE
    samples: dict[str, list[float]] = {
        k: [] for k in ("define", "start", "balloon", "vcpus", "metrics", "stop")
    }
    with tempfile.TemporaryDirectory(dir=Path.home() / ".cache") as images:
        disk = Path(images) / "kvm.qcow2"
        subprocess.run(["qemu-img", "create", "-q", "-f", "qcow2", str(disk), "64M"], check=True)
        for i in range(args.repeats):
            xml = XML.format(name=f"ctx{i}", disk=disk)
            start = time.perf_counter()
            dom = conn.defineXML(xml)
            samples["define"].append((time.perf_counter() - start) * 1000)
            cycle(dom, samples, live)
            dom.undefine()
    conn.close()
    results = {k: summary(v) for k, v in samples.items()}
    for k, v in results.items():
        print(f"{k:8} median {v['median']:9.2f} ms")
    save("kvm_context", {"uri": URI, "unit": "milliseconds", "results": results})


if __name__ == "__main__":
    main()
