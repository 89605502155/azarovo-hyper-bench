"""Figure 1: numbered stages of starting a machine with race-free admission.

Column A (stages 1-6) prepares the guest, column B (stages 7-11) defines,
admits and runs it, column C (stages 12-13) handles a refusal. All arrows are
orthogonal, the shortest route without crossings.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

from plots.style import CM, save, setup

FONT = 10
BOX_H, DIA_H, GAP = 1.15, 1.75, 0.5
XA, WA = 3.3, 6.3
XB, WB = 10.2, 6.3
XC, WC = 15.25, 3.3
TALL = 1.7
GUTTER = (XA + WA / 2 + XB - WB / 2) / 2
BUS = 0.12
LINE = {"color": "black", "lw": 1.0, "solid_capstyle": "butt"}


def column(top: float, kinds: list[str]) -> list[float]:
    """Centres of a column of boxes ("b") and diamonds ("d") from ``top`` down."""
    centres, y = [], top
    for kind in kinds:
        h = BOX_H if kind == "b" else DIA_H
        centres.append(y - h / 2)
        y -= h + GAP
    return centres


def box(ax, x, y, w, text, h=BOX_H):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.15",
            fc="white",
            ec="black",
            lw=1.1,
        )
    )
    ax.text(x, y, text, ha="center", va="center", fontsize=FONT, linespacing=1.2)


def diamond(ax, x, y, w, text):
    pts = [(x, y + DIA_H / 2), (x + w / 2, y), (x, y - DIA_H / 2), (x - w / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, fc="#e8f0f8", ec="black", lw=1.1))
    ax.text(x, y, text, ha="center", va="center", fontsize=FONT, linespacing=1.2)


def arrow(ax, *points):
    xs, ys = zip(*points, strict=True)
    ax.plot(xs, ys, **LINE)
    ax.annotate(
        "",
        xy=points[-1],
        xytext=points[-2],
        arrowprops={
            "arrowstyle": "-|>",
            "color": "black",
            "lw": 1.0,
            "shrinkA": 0,
            "shrinkB": 0,
            "mutation_scale": 12,
        },
    )


def label(ax, x, y, text, ha="left"):
    ax.text(x, y, text, fontsize=FONT - 0.5, style="italic", ha=ha, va="center")


def main() -> None:
    setup()
    fig = plt.figure(figsize=(17 * CM, 13.6 * CM))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 13.6)
    ax.axis("off")
    a = column(13.4, ["b", "b", "b", "d", "d", "b"])
    b = column(13.4, ["b", "d", "b", "b", "b"])
    box(ax, XA, a[0], WA, "1. Проверка типов и знаков\nчисловых параметров")
    box(ax, XA, a[1], WA, "2. Формирование спецификации\nс учётом пресета и драйвера")
    box(ax, XA, a[2], WA, "3. Аренда соединения\nиз общего пула по URI")
    diamond(ax, XA, a[3], WA - 0.6, "4. Предварительно\n$d \\leq H$ ?")
    diamond(ax, XA, a[4], WA - 0.6, "5. Под замком $L$\n$d_{disk} \\leq H_{disk}$ ?")
    box(ax, XA, a[5], WA, "6. Создание образа диска\n(falloc), освобождение $L$")
    box(ax, XB, b[0], WB, "7. Генерация XML по шаблону,\nопределение домена")
    diamond(ax, XB, b[1], WB - 0.6, "8. Под замком $L$\nзамер $H$, $d \\leq H$ ?")
    box(ax, XB, b[2], WB, "9. Запуск домена,\nосвобождение $L$")
    box(ax, XB, b[3], WB, "10. Управление: балунинг,\nгорячее подключение, метрики")
    box(ax, XB, b[4], WB, "11. Остановка, возврат аренды\nи удаление созданных дисков")
    box(ax, XC, b[1], WC, "12. Откат:\nудаление\nдомена и образа", TALL)
    box(ax, XC, b[4], WC, "13. Отказ:\nInsufficient-\nResourcesError", TALL)

    def bottom(y, kind="b"):
        return y - (BOX_H if kind == "b" else DIA_H) / 2

    def top(y, kind="b"):
        return y + (BOX_H if kind == "b" else DIA_H) / 2

    arrow(ax, (XA, bottom(a[0])), (XA, top(a[1])))
    arrow(ax, (XA, bottom(a[1])), (XA, top(a[2])))
    arrow(ax, (XA, bottom(a[2])), (XA, top(a[3], "d")))
    arrow(ax, (XA, bottom(a[3], "d")), (XA, top(a[4], "d")))
    arrow(ax, (XA, bottom(a[4], "d")), (XA, top(a[5])))
    label(ax, XA + 0.15, bottom(a[3], "d") - 0.22, "да")
    label(ax, XA + 0.15, bottom(a[4], "d") - 0.22, "да")
    arrow(ax, (XA + WA / 2, a[5]), (GUTTER, a[5]), (GUTTER, b[0]), (XB - WB / 2, b[0]))
    arrow(ax, (XB, bottom(b[0])), (XB, top(b[1], "d")))
    arrow(ax, (XB, bottom(b[1], "d")), (XB, top(b[2])))
    label(ax, XB + 0.15, bottom(b[1], "d") - 0.22, "да")
    arrow(ax, (XB, bottom(b[2])), (XB, top(b[3])))
    arrow(ax, (XB, bottom(b[3])), (XB, top(b[4])))
    arrow(ax, (XB + (WB - 0.6) / 2, b[1]), (XC - WC / 2, b[1]))
    label(ax, XB + (WB - 0.6) / 2 + 0.08, b[1] + 0.32, "нет")
    arrow(ax, (XC, b[1] - TALL / 2), (XC, b[4] + TALL / 2))
    floor = bottom(a[5]) - 0.4
    left = XA - (WA - 0.6) / 2
    for y in (a[3], a[4]):
        ax.plot([left, BUS], [y, y], **LINE)
        label(ax, left - 0.08, y + 0.25, "нет", ha="right")
    arrow(ax, (BUS, a[3]), (BUS, floor), (XC, floor), (XC, b[4] - TALL / 2))
    ax.set_ylim(floor - 0.15, 13.5)
    fig.set_size_inches(17 * CM, (13.65 - floor) * CM)
    save(fig, "fig1_scheme")


if __name__ == "__main__":
    main()
