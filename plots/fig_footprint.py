"""Figure 2: cost of importing and installing each library (medians, IQR whiskers, log axes)."""

from __future__ import annotations

import matplotlib.pyplot as plt

from plots.style import CM, COLORS, load, save, setup

ORDER = ["azarovo-hyper", "libvirt-python", "pyvmomi", "proxmoxer", "openstacksdk",
         "pylxd", "python-vagrant"]  # fmt: skip
PANELS = (
    ("imports", "milliseconds", "а) Время импорта, мс"),
    ("imports", "rss_mib", "б) Рост памяти при импорте, МиБ"),
    ("install", "seconds", "в) Время установки, с"),
    ("install", "size_mib", "г) Объём установки, МиБ"),
)


def panel(ax, stats: dict, key: str, title: str) -> None:
    names = ORDER[::-1]  # barh draws bottom-up: reverse so azarovo-hyper is on top
    med = [stats[n][key]["median"] for n in names]
    low = [m - stats[n][key]["p25"] for m, n in zip(med, names, strict=True)]
    high = [stats[n][key]["p75"] - m for m, n in zip(med, names, strict=True)]
    bars = ax.barh(names, med, xerr=[low, high], color=[COLORS[n] for n in names],
                   error_kw={"lw": 0.8, "capsize": 2})  # fmt: skip
    ax.set_title(title, loc="left")
    ax.set_xscale("log")  # values span two orders of magnitude: small ones stay visible
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", which="minor", alpha=0.12)
    for bar, value, h in zip(bars, med, high, strict=True):
        text = f"{value:.1f}".replace(".", ",")
        ax.text((value + h) * 1.18, bar.get_y() + bar.get_height() / 2, text,
                va="center", fontsize=10)  # fmt: skip
    ax.set_xlim(min(med) * 0.5, max(m + h for m, h in zip(med, high, strict=True)) * 4)


def main() -> None:
    setup()
    data = {"imports": load("imports")["libraries"], "install": load("install")["libraries"]}
    fig, axes = plt.subplots(2, 2, figsize=(17 * CM, 12.5 * CM), sharey=True)
    for ax, (source, key, title) in zip(axes.flat, PANELS, strict=True):
        panel(ax, data[source], key, title)
    fig.tight_layout(w_pad=1.2, h_pad=1.0)
    save(fig, "fig2_footprint")


if __name__ == "__main__":
    main()
