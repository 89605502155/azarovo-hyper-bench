"""Figure 4: guests running after concurrent starts, naive vs atomic admission."""

from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt

from plots.style import CM, load, save, setup


def main() -> None:
    setup()
    race = load("race")
    fit, trials = race["capacity"], race["trials"]
    fig, ax = plt.subplots(figsize=(17 * CM, 6.8 * CM))
    styles = (
        ("naive", "Проверка, затем действие", "#d27d2d", -0.2),
        ("atomic", "Атомарный допуск (библиотека)", "#1b5e9e", 0.2),
    )
    for key, label, color, shift in styles:
        counts = Counter(race["results"][key]["running"])
        xs = sorted(counts)
        ax.bar(
            [x + shift for x in xs],
            [counts[x] / trials * 100 for x in xs],
            0.38,
            label=label,
            color=color,
            edgecolor="black",
            lw=0.4,
        )
    ax.axvline(fit + 0.5, color="black", ls="--", lw=1.0)
    ax.text(fit + 0.65, 55, f"ёмкость хоста: {fit}", fontsize=10.5)
    ax.set_xlabel(f"Число работающих гостей после {race['threads']} одновременных запусков")
    ax.set_ylabel("Доля испытаний, %")
    ax.set_ylim(0, 105)
    ax.set_xticks(range(0, race["threads"] + 1))
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    save(fig, "fig4_race")


if __name__ == "__main__":
    main()
