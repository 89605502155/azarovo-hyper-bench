# azarovo-hyper-bench

Reproducible benchmarks behind the article about
[azarovo-hyper](https://github.com/89605502155/azarovo-hyper)
([PyPI](https://pypi.org/project/azarovo-hyper/)), a high-level Python library for
KVM and Xen. Every number and figure of the article can be regenerated from this
repository.

[Русская версия](README.ru.md)

## What is compared

| Benchmark | Question | Module |
|---|---|---|
| Import | How long does `import` take and how much memory does it add? | `bench.imports` |
| Installation | Time, number of packages and disk size of a clean install | `bench.install` |
| Operations | Client-side cost of state, ballooning, vCPU change, metrics, definition | `bench.operations` |
| Code size | Statements needed for the same management task | `bench.loc`, `tasks/` |
| Race | Overbooking under 16 concurrent starts: check-then-act vs atomic admission | `bench.race` |
| KVM context | How long the same operations take on a real KVM guest | `bench.kvm_context` |

Libraries: azarovo-hyper 0.0.2, libvirt-python 12.9.0, pyvmomi 9.1.1.0,
proxmoxer 2.3.0, openstacksdk 4.22.0, pylxd 2.4.2, python-vagrant 1.0.0
(exact versions are pinned in `uv.lock`).

Operation benchmarks use libvirt's built-in `test:///default` driver. It runs
inside the calling process and does almost no work, so the measured time is
the cost of the library itself and not of a hypervisor. VMware, Proxmox,
OpenStack, LXD and Vagrant need running servers, so only import and
installation are compared for them.

## Requirements

Tested on **Ubuntu 26.04** (Linux only for now).

```bash
sudo apt install -y qemu-utils libvirt-daemon-system libvirt-clients \
                    pkg-config libvirt-dev python3-dev gcc      # gcc etc. build libvirt-python
curl -LsSf https://astral.sh/uv/install.sh | sh                  # if uv is missing
```

The compiler and headers are needed only because `libvirt-python`, one of the
compared libraries, is published as source code. azarovo-hyper itself needs none
of them. `/dev/kvm` is optional: without it `bench.kvm_context` is skipped.

## Run

```bash
git clone https://github.com/89605502155/azarovo-hyper-bench
cd azarovo-hyper-bench
uv sync --locked                       # exact versions from uv.lock
uv run python -m bench.run_all         # about 15 minutes, writes results/*.json
uv run python -m plots.make_all        # figures/*.tiff, 600 dpi
```

Single benchmarks accept the sample size, for example
`uv run python -m bench.operations --repeats 500` or
`uv run python -m bench.race --trials 20`.

The results used in the article are committed in `results/`, so
`uv run python -m plots.make_all` redraws the figures without measuring again.

## Results in the article

Measured on Intel Core i5-2500 (4 cores, 3.3 GHz), 19 GiB RAM, Ubuntu 26.04.1,
kernel 7.0, Python 3.12.13, libvirt 12.0.0, QEMU 10.2.1.

| Figure | File | Script |
|---|---|---|
| 1. Stages of starting a machine | `figures/fig1_scheme.tiff` | `plots/fig_scheme.py` |
| 2. Import and installation | `figures/fig2_footprint.tiff` | `plots/fig_footprint.py` |
| 3. Operation cost and share of KVM time | `figures/fig3_operations.tiff` | `plots/fig_operations.py` |
| 4. Overbooking under concurrent starts | `figures/fig4_race.tiff` | `plots/fig_race.py` |

Each JSON file in `results/` stores the environment (CPU, kernel, Python and
library versions) next to the samples: median, quartiles, 95th percentile.

## Layout

```
bench/     benchmarks (one module per question) and run_all.py
tasks/     the same management task written with azarovo-hyper and libvirt-python
plots/     figure scripts; style.py holds fonts, sizes and the 600 dpi TIFF export
results/   measured data used in the article
figures/   rendered figures
```

## License

[MIT](LICENSE)
