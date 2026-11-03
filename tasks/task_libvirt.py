"""The same task with the official libvirt binding only."""

import subprocess
import sys
from pathlib import Path

import libvirt

XML = """<domain type='kvm'>
  <name>{name}</name>
  <memory unit='MiB'>1024</memory>
  <currentMemory unit='MiB'>1024</currentMemory>
  <maxMemory slots='16' unit='MiB'>4096</maxMemory>
  <vcpu placement='static' current='2'>8</vcpu>
  <os><type arch='x86_64' machine='q35'>hvm</type></os>
  <features><acpi/><apic/></features>
  <cpu mode='host-passthrough'>
    <topology sockets='1' cores='8' threads='1'/>
    <numa><cell id='0' cpus='0-7' memory='1024' unit='MiB'/></numa>
  </cpu>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <controller type='usb' model='qemu-xhci'/>
    <interface type='user'><model type='virtio'/></interface>
    <graphics type='spice' autoport='yes'><listen type='address' address='127.0.0.1'/></graphics>
    <video><model type='virtio'/></video>
    <memballoon model='virtio'><stats period='1'/></memballoon>
  </devices>
</domain>"""


def run(uri: str, images: str) -> dict:
    disk = Path(images) / "task.qcow2"
    subprocess.run(["qemu-img", "create", "-q", "-f", "qcow2", str(disk), "64M"], check=True)
    conn = libvirt.open(uri)
    try:
        dom = conn.defineXML(XML.format(name="task", disk=disk))
        try:
            dom.create()
            live = libvirt.VIR_DOMAIN_AFFECT_LIVE
            dom.setMemoryFlags(768 * 1024, live)
            dom.setVcpusFlags(3, live)
            stats = dom.memoryStats()
            vcpus = dom.info()[3]
            if dom.isActive():
                dom.destroy()
        finally:
            dom.undefine()
    finally:
        conn.close()
        disk.unlink(missing_ok=True)
    return {"vcpus": vcpus, "memory_mib": stats.get("actual", 0) / 1024}


if __name__ == "__main__":
    print(run(sys.argv[1], sys.argv[2]))
