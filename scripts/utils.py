"""Analysis utilities."""

import csv

import polars as pl


NUM_METADATA_ROWS = 5


def combine_grids(grids):
    """Combine all grids into one."""
    result = []
    col_headers = None
    for name, g in grids.items():
        col_headers = [str(c) for c in range(len(g.columns))]
        g = g.rename(dict(zip(g.columns, col_headers)))
        g = g.with_row_count("row")
        g = g.melt(id_vars=["row"], variable_name="col", value_name="val")
        g = g.with_columns(pl.col("col").cast(pl.Int64))
        g = g.with_columns(pl.lit(name).alias("survey"))
        result.append(g)
    return pl.concat(result)


def read_assay(treatments_path, readings_path):
    """Read a combined assay."""
    treatments_meta, treatments_data = _assay_read_and_split(treatments_path, str)
    readings_meta, readings_data = _assay_read_and_split(readings_path, float)
    assert treatments_meta == readings_meta, (
        f"Metadata mis-match: {treatments_path} vs {readings_path}"
    )
    combined = treatments_data.rename({"val": "treatment"}).join(
        readings_data.rename({"val": "reading"}),
        on=["row", "col"],
        how="inner",
    )
    return {**treatments_meta, "data": combined}


def read_grids(data_dir_path):
    """Read all grids as unified Polars dataframe."""
    return {
        filename.stem: pl.read_csv(filename, has_header=False)
        for filename in data_dir_path.glob("surveys/*.csv")
    }


def _assay_read_and_split(filepath, convert):
    """Read CSV and split header from body."""
    with open(filepath, "r") as stream:
        rows = [r for r in csv.reader(stream)]
        header = {r[0]: r[1] for r in rows[:NUM_METADATA_ROWS]}

        columns = rows[NUM_METADATA_ROWS][1:]
        body = []
        for i, r in enumerate(rows[NUM_METADATA_ROWS + 1 :], start=1):
            assert i == int(r[0]), f"Bad row number(s) in {filepath}: {i} vs {r[0]}"
            for c, v in zip(columns, r[1:]):
                body.append((c, i, convert(v)))

        return header, pl.DataFrame(body, schema=("col", "row", "val"), orient="row")
