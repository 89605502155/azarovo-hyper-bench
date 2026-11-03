"""Client-side cost of common operations, measured on libvirt's test driver.

``test:///default`` runs inside the calling process and does almost no work,
so the time of each call is the cost of the library itself, not of a
hypervisor. Three implementations are compared:

* ``libvirt``  -- the official binding called directly (the baseline);
* ``native``   -- azarovo-hyper with its ctypes backend (the default);
* ``python``   -- azarovo-hyper on top of the official binding.

``connect`` is open+close for the binding (it has no pool) and a lease from
the shared pool for azarovo-hyper. ``vcpus`` includes the race-free capacity
check; ``vcpus_unchecked`` is the same call with ``check_resources=False``.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from bench.common import TEST_URI, fresh_python, save, summary

OPERATIONS = ("connect", "state", "balloon", "vcpus", "vcpus_unchecked", "metrics", "define")
RAW_XML = """<domain type='test'><name>{name}</name><memory unit='MiB'>512</memory>
<vcpu current='2'>8</vcpu><os><type arch='x86_64'>hvm</type></os>
<devices><disk type='file' device='disk'><source file='/tmp/x.qcow2'/>
<target dev='vda' bus='virtio'/></disk></devices></domain>"""


def timed(call: Callable[[int], object], repeats: int, warmup: int = 50) -> list[float]:
    for i in range(warmup):
        call(i)
    samples = []
    for i in range(repeats):
        start = time.perf_counter_ns()
        call(i)
        samples.append((time.perf_counter_ns() - start) / 1000)
    return samples


def raw_suite(repeats: int) -> dict[str, list[float]]:
    import libvirt

    conn = libvirt.open(TEST_URI)
    dom = conn.lookupByName("test")
    live = libvirt.VIR_DOMAIN_AFFECT_LIVE

    def metrics(_i: int) -> None:
        dom.info()
        dom.memoryStats()
        dom.blockStats("vda")

    def define(i: int) -> None:
        conn.defineXML(RAW_XML.format(name=f"raw{i}")).undefine()

    return {
        "connect": timed(lambda _i: libvirt.open(TEST_URI).close(), repeats),
        "state": timed(lambda _i: dom.state(), repeats),
        "balloon": timed(lambda i: dom.setMemoryFlags((300 + i % 2 * 100) * 1024, live), repeats),
        "vcpus": timed(lambda i: dom.setVcpusFlags(1 + i % 2, live), repeats),
        "vcpus_unchecked": timed(lambda i: dom.setVcpusFlags(1 + i % 2, live), repeats),
        "metrics": timed(metrics, repeats),
        "define": timed(define, max(repeats // 5, 50), warmup=10),
    }


def azarovo_suite(repeats: int) -> dict[str, list[float]]:
    import libvirt
    from azarovo_hyper import Hyper, ResourcePolicy

    keeper = libvirt.open(TEST_URI)  # the test driver forgets its state otherwise
    images = Path(tempfile.mkdtemp())
    disk = images / "shared.qcow2"
    disk.write_bytes(b"")
    hyper = Hyper(resources=ResourcePolicy(memory_overcommit=64))
    vm = hyper.kvm("bench", uri=TEST_URI, disk=disk, memory="512M", min_memory="128M").start()
    lax = hyper.kvm("lax", uri=TEST_URI, disk=disk, memory="512M", check_resources=False).start()

    def define(i: int) -> None:
        hyper.kvm(f"az{i}", uri=TEST_URI, disk=disk, memory="512M").define().delete(
            remove_disk=False
        )

    results = {
        "connect": timed(lambda _i: hyper.pool.acquire(TEST_URI).release(), repeats),
        "state": timed(lambda _i: vm.state, repeats),
        "balloon": timed(lambda i: vm.memory.set(300 + i % 2 * 100), repeats),
        "vcpus": timed(lambda i: vm.cpu.set(2 + i % 2), repeats),
        "vcpus_unchecked": timed(lambda i: lax.cpu.set(2 + i % 2), repeats),
        "metrics": timed(lambda _i: vm.metrics(), repeats),
        "define": timed(define, max(repeats // 5, 50), warmup=10),
    }
    vm.delete(remove_disk=False)
    lax.delete(remove_disk=False)
    keeper.close()
    return results


def worker(implementation: str, repeats: int) -> None:
    suite = raw_suite if implementation == "libvirt" else azarovo_suite
    samples = suite(repeats)
    print(json.dumps({op: summary(values) for op, values in samples.items()}))


IMPLEMENTATIONS = {
    "libvirt": {},
    "native": {"AZAROVO_LIBVIRT_BACKEND": "native"},
    "python": {"AZAROVO_LIBVIRT_BACKEND": "python"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=2000)
    parser.add_argument("--worker", choices=IMPLEMENTATIONS)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.repeats)
        return
    results = {}
    for name, env in IMPLEMENTATIONS.items():
        code = f"import sys; sys.argv=['x','--worker','{name}','--repeats','{args.repeats}']\n"
        code += "from bench.operations import main; main()"
        results[name] = fresh_python(code, env)
        line = "  ".join(f"{op}={results[name][op]['median']:.1f}" for op in OPERATIONS)
        print(f"{name:8} median us: {line}")
    save("operations", {"repeats": args.repeats, "unit": "microseconds", "results": results})


if __name__ == "__main__":
    sys.exit(main())
