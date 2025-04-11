"""Summarize data."""

import click
from pathlib import Path
from sklearn.mixture import GaussianMixture
import sys

import polars as pl

import utils


@click.command()
@click.option(
    "--data", type=click.Path(exists=True), required=True, help="Path to data directory"
)
@click.option(
    "--format",
    type=click.Choice(["csv", "df", "count"], case_sensitive=False),
    required=True,
    help="Output format: CSV, dataframe, or count",
)
def summarize(data, format):
    """Do data summarization."""

    # Load assays.
    assays_dir = Path(data) / "assays"
    dataframes = []
    for treatment_path in assays_dir.glob("*_treatments.csv"):
        readings_path = Path(str(treatment_path).replace("_treatments", "_readings"))
        assay = utils.read_assay(treatment_path, readings_path)
        df = assay["data"].group_by("treatment").agg(pl.mean("reading"))
        df = df.with_columns(pl.lit(assay["id"]).alias("assay"))
        dataframes.append(df)

    # Calculate specimen-to-control ratios.
    summary = (
        pl.concat(dataframes)
        .pivot(index="assay", on="treatment", values="reading")
        .rename({"C": "control", "S": "specimen"})
    )
    summary = summary.with_columns(
        (summary["specimen"] / summary["control"]).alias("ratio")
    ).sort("ratio")

    # Classify.
    ratios = summary.select("ratio").to_numpy()
    gmm = GaussianMixture(n_components=2, random_state=42)
    gmm.fit(ratios)
    probabilities = gmm.predict_proba(ratios)
    summary = summary.with_columns(
        [
            pl.Series("p_1", probabilities[:, 0]),
            pl.Series("p_2", probabilities[:, 1]),
        ]
    )

    # Label.
    summary = summary.with_columns(
        pl.when((pl.col("p_1") > 0.8) & (pl.col("p_2") < 0.2))
        .then(pl.lit("group_1"))
        .when((pl.col("p_1") < 0.2) & (pl.col("p_2") > 0.8))
        .then(pl.lit("group_2"))
        .otherwise(pl.lit("unknown"))
        .alias("label")
    )

    # Report.
    with pl.Config() as cfg:
        cfg.set_tbl_rows(len(summary))
        cfg.set_float_precision(3)
        if format == "csv":
            summary.write_csv(sys.stdout, float_precision=3)
        elif format == "df":
            print(summary)
        elif format == "count":
            temp = summary.group_by("label").agg(pl.len().alias("count"))
            print(temp)


if __name__ == "__main__":
    try:
        sys.exit(summarize())
    except AssertionError as exc:
        print(str(exc), sys.stderr)
        sys.exit(1)
