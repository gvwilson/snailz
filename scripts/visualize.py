"""Summarize data."""

import click
import math
from pathlib import Path
import sys

import plotly.express as px

import utils


@click.command()
@click.option(
    "--data", type=click.Path(exists=True), required=True, help="Path to data directory"
)
@click.option(
    "--make",
    type=click.Choice(["grid"], case_sensitive=False),
    required=True,
    help="What to visualize",
)
@click.option("--output", type=click.Path(), default=None, help="Path to output file")
@click.option("--show", is_flag=True, default=False, help="Show figure")
def visualize(data, make, output, show):
    """Do visualization."""
    if make == "grid":
        fig = _make_grids(data)
        if show:
            fig.show()
        if output:
            fig.write_image(output)


def _make_grids(data):
    """Make survey grid visualization."""
    grids = utils.read_grids(Path(data))
    df = utils.combine_grids(grids)

    facet_col_wrap = round(math.sqrt(len(grids)))
    fig = px.density_heatmap(
        df,
        x="col",
        y="row",
        z="val",
        facet_col="survey",
        facet_col_wrap=facet_col_wrap,  # Create a grid layout based on sqrt
        color_continuous_scale="dense",
    )

    # Remove title from colorbar
    fig.update_layout(coloraxis_colorbar_title_text=None)

    return fig


if __name__ == "__main__":
    try:
        sys.exit(visualize())
    except AssertionError as exc:
        print(str(exc), sys.stderr)
        sys.exit(1)
