"""Figure 3: client-side cost of operations and its share of real KVM time."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from plots.style import CM, COLORS, load, save, setup

OPS = ["state", "balloon", "vcpus_unchecked", "vcpus", "metrics", "define"]
LABELS = ["Состоя-\nние", "Балу-\nнинг", "vCPU\nбез про-\nверки", "vCPU\nс про-\nверкой",
          "Мет-\nрики", "Опреде-\nление\nдомена"]  # fmt: skip
NAMES = ["Состояние", "Балунинг", "vCPU без проверки", "vCPU с проверкой", "Метрики",
         "Определение домена"]  # fmt: skip
KVM = {"balloon": "balloon", "vcpus_unchecked": "vcpus", "vcpus": "vcpus",
       "metrics": "metrics", "define": "define"}  # fmt: skip
IMPLS = [("libvirt", "libvirt-python"), ("python", "azarovo-hyper (привязка)"),
         ("native", "azarovo-hyper (ctypes)")]  # fmt: skip


def latency(ax, ops: dict) -> None:
    x = np.arange(len(OPS))
    width = 0.27
    for i, (impl, label) in enumerate(IMPLS):
        med = [ops[impl][op]["median"] for op in OPS]
        ax.bar(x + (i - 1) * width, med, width, label=label, color=COLORS[impl],
               edgecolor="black", lw=0.4)  # fmt: skip
    ax.set_yscale("log")
    ax.set_ylabel("Медиана, мкс")
    ax.set_xticks(x, LABELS)
    ax.set_title("а) Время одной операции на стороне клиента", loc="left")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="x", visible=False)


def share(ax, ops: dict, kvm: dict) -> None:
    shown = [op for op in OPS if op in KVM]
    values = [ops["native"][op]["median"] / (kvm[KVM[op]]["median"] * 1000) * 100 for op in shown]
    names = [NAMES[OPS.index(op)] for op in shown][::-1]
    bars = ax.barh(names, values[::-1], color=COLORS["native"])
    ax.set_xlabel("% от времени той же операции на KVM")
    ax.set_title("б) Доля накладных расходов azarovo-hyper (ctypes)", loc="left")
    ax.grid(axis="y", visible=False)
    for bar, value in zip(bars, values[::-1], strict=True):
        text = f"{value:.1f} %".replace(".", ",")
        ax.text(value + 0.12, bar.get_y() + bar.get_height() / 2, text, va="center", fontsize=10.5)
    ax.set_xlim(0, max(values) * 1.25)


def main() -> None:
    setup()
    ops, kvm = load("operations")["results"], load("kvm_context")["results"]
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(17 * CM, 14 * CM),
                                      gridspec_kw={"height_ratios": [1.35, 1]})  # fmt: skip
    latency(top, ops)
    share(bottom, ops, kvm)
    fig.tight_layout(h_pad=1.4)
    save(fig, "fig3_operations")


if __name__ == "__main__":
    main()
