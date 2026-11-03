"""Render every figure of the article from the files in results/."""

from plots import fig_footprint, fig_operations, fig_race, fig_scheme

for module in (fig_scheme, fig_footprint, fig_operations, fig_race):
    module.main()
