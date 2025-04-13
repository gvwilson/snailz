"""Summarize data."""

import click
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
    fig = px.density_heatmap(
        df,
        x="col",
        y="row",
        z="val",
        facet_col="survey",
        color_continuous_scale=[
            [0, "rgb(128,128,128)"],  # gray at 0
            [0.000001, "rgb(220,235,255)"],  # lightest blue just above 0
            [0.5, "rgb(65,105,225)"],  # medium blue
            [1, "rgb(0,0,139)"],
        ],
    )

    # Remove title from colorbar
    fig.update_layout(coloraxis_colorbar_title_text=None)

    # Make subplots square
    min_row, max_row = df["row"].min(), df["row"].max()
    fig.update_layout(
        yaxis={"scaleanchor": "x", "scaleratio": 1, "range": [min_row, max_row]},
        yaxis2={"scaleanchor": "x2", "scaleratio": 1, "range": [min_row, max_row]},
    )

    return fig


if __name__ == "__main__":
    try:
        sys.exit(visualize())
    except AssertionError as exc:
        print(str(exc), sys.stderr)
        sys.exit(1)
