"""Figure 1: numbered stages of starting a machine with race-free admission.

Column A (stages 1-6) prepares the guest, column B (stages 7-11) defines,
admits and runs it, column C (stages 12-13) handles a refusal. Arrows are
orthogonal, never cross and keep at least 0.5 cm from unrelated blocks.
Stage numbers are bold white digits in filled circles on the block corners.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

from plots.style import CM, save, setup

FONT = 10
BOX_H, DIA_H, GAP = 1.15, 1.75, 0.55
XA, WA = 3.65, 5.7  # column A spans 0.8 .. 6.5
XB, WB = 10.55, 5.7  # column B spans 7.7 .. 13.4
XC, WC = 15.4, 3.1  # column C spans 13.85 .. 16.95
DIA_W = 5.0
GUTTER = (XA + WA / 2 + XB - WB / 2) / 2  # 0.6 cm from both columns
BUS = 0.2  # 0.6 cm left of column A
BADGE = 0.3
NAVY = "#1b4f8a"
LINE = {"color": "black", "lw": 1.1, "solid_capstyle": "butt"}


def column(top: float, kinds: str) -> list[float]:
    """Centres of a column of boxes ("b") and diamonds ("d") from ``top`` down."""
    centres, y = [], top
    for kind in kinds:
        h = BOX_H if kind == "b" else DIA_H
        centres.append(y - h / 2)
        y -= h + GAP
    return centres


def badge(ax, x: float, y: float, number: int) -> None:
    ax.add_patch(Circle((x, y), BADGE, fc=NAVY, ec=NAVY, zorder=4))
    ax.text(x, y, str(number), ha="center", va="center", color="white", fontsize=10.5,
            fontweight="bold", zorder=5)


def box(ax, x, y, w, number, text, h=BOX_H):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                fc="white", ec="black", lw=1.1))  # fmt: skip
    badge(ax, x - w / 2 + 0.1, y + h / 2 - 0.1, number)  # on the top-left corner
    ax.text(x, y, text, ha="center", va="center", fontsize=FONT, linespacing=1.2)


def diamond(ax, x, y, number, text):
    pts = [(x, y + DIA_H / 2), (x + DIA_W / 2, y), (x, y - DIA_H / 2), (x - DIA_W / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, fc="#e8f0f8", ec="black", lw=1.1))
    badge(ax, x - DIA_W / 4 - 0.45, y + DIA_H / 4 + 0.4, number)
    ax.text(x, y, text, ha="center", va="center", fontsize=FONT, linespacing=1.2)


def arrow(ax, *points):
    xs, ys = zip(*points, strict=True)
    ax.plot(xs, ys, **LINE)
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops={"arrowstyle": "-|>", "color": "black", "lw": 1.1,
                            "shrinkA": 0, "shrinkB": 0, "mutation_scale": 12})  # fmt: skip


def label(ax, x, y, text, ha="left"):
    ax.text(x, y, text, fontsize=FONT - 0.5, style="italic", ha=ha, va="center")


def edges(y: float, kind: str = "b") -> tuple[float, float]:
    h = BOX_H if kind == "b" else DIA_H
    return y + h / 2, y - h / 2


def main() -> None:
    setup()
    fig = plt.figure(figsize=(17 * CM, 14 * CM))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 17)
    ax.axis("off")
    a = column(13.6, "bbbddb")
    b = column(13.6, "bdbbb")
    box(ax, XA, a[0], WA, 1, "Проверка типов\nи знаков параметров")
    box(ax, XA, a[1], WA, 2, "Сборка спецификации\nиз пресета и драйвера")
    box(ax, XA, a[2], WA, 3, "Аренда соединения\nиз общего пула по URI")
    diamond(ax, XA, a[3], 4, "Предварительно\n$d \\leq H$ ?")
    diamond(ax, XA, a[4], 5, "Под замком $L$\n$d_{disk} \\leq H_{disk}$ ?")
    box(ax, XA, a[5], WA, 6, "Создание образа диска\n(falloc), освобождение $L$")
    box(ax, XB, b[0], WB, 7, "XML по шаблону,\nопределение домена")
    diamond(ax, XB, b[1], 8, "Под замком $L$\nзамер $H$, $d \\leq H$ ?")
    box(ax, XB, b[2], WB, 9, "Запуск домена,\nосвобождение $L$")
    box(ax, XB, b[3], WB, 10, "Управление: балунинг,\nгорячее подключение,\nметрики", 1.45)
    box(ax, XB, b[4], WB, 11, "Остановка, возврат\nаренды, удаление\nсозданных дисков", 1.45)
    box(ax, XC, b[1], WC, 12, "Откат:\nудаление\nдомена\nи образа", 1.9)
    box(ax, XC, b[4], WC, 13, "Отказ:\nInsufficient-\nResources-\nError", 1.9)

    for upper, lower, kinds in ((a[0], a[1], "bb"), (a[1], a[2], "bb"), (a[2], a[3], "bd"),
                                (a[3], a[4], "dd"), (a[4], a[5], "db")):  # fmt: skip
        arrow(ax, (XA, edges(upper, kinds[0])[1]), (XA, edges(lower, kinds[1])[0]))
    label(ax, XA + 0.15, edges(a[3], "d")[1] - 0.25, "да")
    label(ax, XA + 0.15, edges(a[4], "d")[1] - 0.25, "да")
    arrow(ax, (XA + WA / 2, a[5]), (GUTTER, a[5]), (GUTTER, b[0]), (XB - WB / 2, b[0]))
    arrow(ax, (XB, edges(b[0])[1]), (XB, edges(b[1], "d")[0]))
    arrow(ax, (XB, edges(b[1], "d")[1]), (XB, edges(b[2])[0]))
    label(ax, XB + 0.15, edges(b[1], "d")[1] - 0.25, "да")
    arrow(ax, (XB, edges(b[2])[1]), (XB, b[3] + 0.725))
    arrow(ax, (XB, b[3] - 0.725), (XB, b[4] + 0.725))
    arrow(ax, (XB + DIA_W / 2, b[1]), (XC - WC / 2, b[1]))
    label(ax, XB + DIA_W / 2 + 0.1, b[1] + 0.3, "нет")
    arrow(ax, (XC, b[1] - 0.95), (XC, b[4] + 0.95))
    floor = min(edges(a[5])[1], b[4] - 0.725) - 0.6
    for y in (a[3], a[4]):
        ax.plot([XA - DIA_W / 2, BUS], [y, y], **LINE)
        label(ax, XA - DIA_W / 2 - 0.1, y + 0.3, "нет", ha="right")
    arrow(ax, (BUS, a[3]), (BUS, floor), (XC, floor), (XC, b[4] - 0.95))
    ax.set_ylim(floor - 0.2, 14.0)
    fig.set_size_inches(17 * CM, (14.2 - floor) * CM)
    save(fig, "fig1_scheme")


if __name__ == "__main__":
    main()
