"""Typical task with azarovo-hyper: define a guest ready for ballooning and
memory/vCPU hot-plug, start it, resize it, sample metrics, clean up."""

import sys

from azarovo_hyper import hyper


def run(uri: str, images: str) -> dict:
    vm = (
        hyper()
        .kvm(
            "task",
            uri=uri,
            images_dir=images,
            memory="1G",
            max_memory="4G",
            disk_size="64M",
            memory_overcommit=64,
        )
        .start()
    )
    vm.memory.set("768M")
    vm.cpu.set(3)
    sample = vm.metrics()
    vm.delete()
    return {"vcpus": sample.vcpus, "memory_mib": sample.memory.actual_mib}


if __name__ == "__main__":
    print(run(sys.argv[1], sys.argv[2]))
