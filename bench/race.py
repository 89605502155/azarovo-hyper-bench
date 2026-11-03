"""Overbooking under concurrent starts: naive check-then-act vs atomic admission.

Several threads start guests at the same moment while the host has room for
only ``capacity`` of them. The naive policy measures the host and then starts
the guest outside any lock, which is the usual "check, then act" pattern. The
atomic policy is azarovo-hyper's default: measuring, checking and starting
happen under one host-wide lock. A trial is overbooked when more guests run
than fit.
"""

from __future__ import annotations

import argparse
import contextlib
import tempfile
import threading
import uuid
from pathlib import Path

import libvirt
from azarovo_hyper import Hyper, InsufficientResourcesError, ResourcePolicy
from azarovo_hyper.domain.resources import shortfalls
from azarovo_hyper.errors import InsufficientResourcesError as Refused
from azarovo_hyper.resources import Admission

from bench.common import TEST_URI, save, summary

GUEST_MIB = 1024


class NaiveAdmission(Admission):
    """Same arithmetic as the library, but the check and the action are separate."""

    @contextlib.contextmanager
    def reserve(self, demand, *, policy, connection, disk_dir=None):
        if policy.check_resources and demand and (demand.memory_mib or demand.vcpus):
            problems = shortfalls(
                demand, policy=policy, usage=connection().usage(), free_disk_mib=None
            )
            if problems:
                raise Refused("not enough host resources", tuple(problems))
        yield


def headroom(policy: ResourcePolicy) -> float:
    from azarovo_hyper.adapters.libvirt_connection import LibvirtConnection
    from azarovo_hyper.domain.resources import memory_headroom

    connection = LibvirtConnection(TEST_URI)
    try:
        return memory_headroom(connection.usage(), policy)
    finally:
        connection.close()


def capacity(policy: ResourcePolicy, disk: Path) -> int:
    """How many guests fit, measured with one probe guest.

    The test driver reports a fixed host and a fixed resident size for every
    guest, so each running guest takes ``cost`` MiB of headroom; a start is
    allowed while a full ceiling (``GUEST_MIB``) still fits.
    """
    before = headroom(policy)
    probe = (
        Hyper(resources=policy)
        .kvm("probe", uri=TEST_URI, disk=disk, memory=GUEST_MIB, min_memory=128, vcpus=1)
        .start(wait=False)
    )
    cost = before - headroom(policy)
    probe.delete(remove_disk=False)
    return 0 if before < GUEST_MIB else 1 + int((before - GUEST_MIB) // cost)


def trial(admission: Admission, policy: ResourcePolicy, threads: int, images: Path) -> int:
    hyper = Hyper(admission=admission, resources=policy)
    disk = images / "shared.qcow2"
    machines = [
        hyper.kvm(
            f"r{uuid.uuid4().hex[:8]}",
            uri=TEST_URI,
            disk=disk,
            memory=GUEST_MIB,
            min_memory=128,
            vcpus=1,
        )
        for _ in range(threads)
    ]
    barrier = threading.Barrier(threads)

    def go(vm):
        barrier.wait()
        with contextlib.suppress(InsufficientResourcesError):
            vm.start(wait=False)

    workers = [threading.Thread(target=go, args=(vm,)) for vm in machines]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    running = sum(vm.is_running for vm in machines)
    for vm in machines:
        if vm.exists:
            vm.delete(remove_disk=False)
    hyper.close()
    return running


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--threads", type=int, default=16)
    args = parser.parse_args()
    keeper = libvirt.open(TEST_URI)
    keeper.lookupByName("test").destroy()  # an empty host: only our guests count
    policy = ResourcePolicy(memory_overcommit=2.0, host_memory_reserve=0)
    images = Path(tempfile.mkdtemp())
    (images / "shared.qcow2").write_bytes(b"")
    fit = capacity(policy, images / "shared.qcow2")
    results = {}
    for name, admission in (("naive", NaiveAdmission()), ("atomic", Admission())):
        running = [trial(admission, policy, args.threads, images) for _ in range(args.trials)]
        over = [max(r - fit, 0) for r in running]
        results[name] = {
            "running": running,
            "overbooked_trials": sum(o > 0 for o in over),
            "overbooked_guests": summary([float(o) for o in over]),
        }
        print(
            f"{name:7} capacity={fit}  overbooked in {results[name]['overbooked_trials']}"
            f"/{args.trials} trials, max extra guests {max(over)}"
        )
    keeper.close()
    save(
        "race",
        {
            "trials": args.trials,
            "threads": args.threads,
            "capacity": fit,
            "guest_mib": GUEST_MIB,
            "results": results,
        },
    )


if __name__ == "__main__":
    main()
