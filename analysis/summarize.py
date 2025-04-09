"""Summarize data."""

import click
from pathlib import Path
import sys

import polars as pl

import utils


@click.command()
@click.option("--data", type=click.Path(exists=True), required=True, help="Path to data directory")
def summarize(data):
    """Do data summarization."""
    assays_dir = Path(data) / "assays"
    dataframes = []
    for treatment_path in assays_dir.glob("*_treatments.csv"):
        readings_path = Path(str(treatment_path).replace("_treatments", "_readings"))
        assay = utils.read_assay(treatment_path, readings_path)
        df = assay["data"].group_by("treatment").agg(pl.mean("reading"))
        df = df.with_columns(pl.lit(assay["id"]).alias("assay"))
        dataframes.append(df)
    summary = pl.concat(dataframes).pivot(index="assay", columns="treatment", values="reading")
    summary = summary.with_columns((summary["S"] / summary["C"]).alias("ratio")).sort("ratio")
    print(summary)


if __name__ == "__main__":
    try:
        sys.exit(summarize())
    except AssertionError as exc:
        print(str(exc), sys.stderr)
        sys.exit(1)
