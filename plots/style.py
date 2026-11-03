"""Common look of all figures: large fonts, journal column width, 600 dpi TIFF."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
CM = 1 / 2.54
WIDTH = 17 * CM  # A4 with 20 mm margins leaves 170 mm
DPI = 600

COLORS = {
    "azarovo-hyper": "#1b5e9e",
    "native": "#1b5e9e",
    "python": "#6aa6d8",
    "libvirt": "#d27d2d",
    "libvirt-python": "#d27d2d",
    "pyvmomi": "#7a7a7a",
    "proxmoxer": "#9c9c9c",
    "openstacksdk": "#5f5f5f",
    "pylxd": "#b5b5b5",
    "python-vagrant": "#8a8a8a",
}


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "axes.titlesize": 12,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "savefig.dpi": DPI,
        }
    )


def load(name: str) -> dict:
    return json.loads((RESULTS / f"{name}.json").read_text())


def save(fig: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / f"{name}.tiff"
    fig.savefig(
        path,
        dpi=DPI,
        format="tiff",
        pil_kwargs={"compression": "tiff_lzw"},
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)
    print(f"saved {path.relative_to(ROOT)}")
    return path
