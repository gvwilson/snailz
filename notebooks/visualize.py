# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "snailz",
# ]
# ///

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from datetime import date
    from faker.config import AVAILABLE_LOCALES
    from snailz import in_memory, Parameters
    return AVAILABLE_LOCALES, Parameters, date, in_memory, mo


@app.cell
def _(mo):
    seed = mo.ui.number(value=12345, label="Seed")
    return (seed,)


@app.cell
def _(mo):
    num_grids = mo.ui.number(value=1, start=1, label="Number of grids")
    grid_size = mo.ui.number(value=1, start=1, label="Grid size (cells)")
    grid_spacing = mo.ui.number(value=10.0, start=0.1, step=0.1, label="Grid spacing (m)")
    grid_separation = mo.ui.number(value=4, start=1, label="Grid separation")
    grid_std_dev = mo.ui.number(value=0.5, start=0.0, step=0.1, label="Grid std dev")
    lat0 = mo.ui.number(value=48.8666632, start=-90.0, stop=90.0, step=0.0001, label="Latitude")
    lon0 = mo.ui.number(value=-124.1999992, start=-180.0, stop=180.0, step=0.0001, label="Longitude")
    return grid_separation, grid_size, grid_spacing, grid_std_dev, lat0, lon0, num_grids


@app.cell
def _(AVAILABLE_LOCALES, mo):
    num_persons = mo.ui.number(value=1, start=1, label="Number of persons")
    supervisor_frac = mo.ui.slider(value=0.3, start=0.0, stop=1.0, step=0.05, label="Supervisor fraction")
    locale = mo.ui.dropdown(options=sorted(AVAILABLE_LOCALES), value="et_EE", label="Locale")
    return locale, num_persons, supervisor_frac


@app.cell
def _(mo):
    num_machines = mo.ui.number(value=1, start=1, label="Number of machines")
    ratings_frac = mo.ui.slider(value=0.5, start=0.0, stop=1.0, step=0.05, label="Ratings fraction")
    p_certified = mo.ui.slider(value=0.3, start=0.0, stop=1.0, step=0.05, label="P(certified)")
    return num_machines, p_certified, ratings_frac


@app.cell
def _(mo):
    num_assays = mo.ui.number(value=1, start=1, label="Number of assays")
    assay_size = mo.ui.number(value=2, start=2, label="Assay size")
    assay_certified = mo.ui.number(value=3.0, start=0.0, step=0.1, label="Assay certified narrowing")
    return assay_certified, assay_size, num_assays


@app.cell
def _(mo):
    genome_length = mo.ui.number(value=1, start=1, label="Genome length")
    num_loci = mo.ui.number(value=1, start=0, label="Number of loci")
    p_mutation = mo.ui.slider(value=0.5, start=0.0, stop=1.0, step=0.05, label="P(mutation)")
    return genome_length, num_loci, p_mutation


@app.cell
def _(mo):
    num_specimens = mo.ui.number(value=1, start=1, label="Number of specimens")
    mass_beta_0 = mo.ui.number(value=3.0, step=0.1, label="Mass beta_0")
    mass_beta_1 = mo.ui.number(value=0.5, step=0.1, label="Mass beta_1")
    mass_sigma = mo.ui.number(value=0.3, start=0.0, step=0.1, label="Mass sigma")
    diam_ratio = mo.ui.number(value=0.7, start=0.0, step=0.1, label="Diameter ratio")
    diam_sigma = mo.ui.number(value=0.7, start=0.0, step=0.1, label="Diameter sigma")
    return diam_ratio, diam_sigma, mass_beta_0, mass_beta_1, mass_sigma, num_specimens


@app.cell
def _(date, mo):
    start_date = mo.ui.date(value=date(2026, 3, 1), label="Start date")
    end_date = mo.ui.date(value=date(2026, 5, 31), label="End date")
    p_date_missing = mo.ui.slider(value=0.1, start=0.0, stop=1.0, step=0.05, label="P(date missing)")
    return end_date, p_date_missing, start_date


@app.cell
def _(
    assay_certified,
    assay_size,
    diam_ratio,
    diam_sigma,
    end_date,
    grid_separation,
    grid_size,
    grid_spacing,
    grid_std_dev,
    lat0,
    locale,
    lon0,
    mass_beta_0,
    mass_beta_1,
    mass_sigma,
    mo,
    num_assays,
    num_grids,
    num_loci,
    num_machines,
    num_persons,
    num_specimens,
    genome_length,
    p_certified,
    p_date_missing,
    p_mutation,
    ratings_frac,
    seed,
    start_date,
    supervisor_frac,
):
    _survey = mo.vstack([
        mo.md("### Survey Grids"),
        mo.hstack([num_grids, grid_size, grid_spacing, grid_separation], justify="start"),
        mo.hstack([grid_std_dev, lat0, lon0], justify="start"),
    ])
    _personnel = mo.vstack([
        mo.md("### Personnel"),
        mo.hstack([num_persons, supervisor_frac, locale], justify="start"),
    ])
    _machines = mo.vstack([
        mo.md("### Machines"),
        mo.hstack([num_machines, ratings_frac, p_certified], justify="start"),
    ])
    _assays = mo.vstack([
        mo.md("### Assays"),
        mo.hstack([num_assays, assay_size, assay_certified], justify="start"),
    ])
    _genome = mo.vstack([
        mo.md("### Genome"),
        mo.hstack([genome_length, num_loci, p_mutation], justify="start"),
    ])
    _specimens = mo.vstack([
        mo.md("### Specimens"),
        mo.hstack([num_specimens, mass_beta_0, mass_beta_1], justify="start"),
        mo.hstack([mass_sigma, diam_ratio, diam_sigma], justify="start"),
    ])
    _dates = mo.vstack([
        mo.md("### Dates"),
        mo.hstack([start_date, end_date, p_date_missing], justify="start"),
    ])
    run_button = mo.ui.run_button(label="Generate Database")
    mo.vstack([
        mo.md("## Snailz Parameters"),
        seed,
        _survey,
        _personnel,
        _machines,
        _assays,
        _genome,
        _specimens,
        _dates,
        run_button,
    ])
    return (run_button,)


@app.cell
def _(
    Parameters,
    assay_certified,
    assay_size,
    diam_ratio,
    diam_sigma,
    end_date,
    grid_separation,
    grid_size,
    grid_spacing,
    grid_std_dev,
    in_memory,
    lat0,
    locale,
    lon0,
    mass_beta_0,
    mass_beta_1,
    mass_sigma,
    mo,
    num_assays,
    num_grids,
    num_loci,
    num_machines,
    num_persons,
    num_specimens,
    genome_length,
    p_certified,
    p_date_missing,
    p_mutation,
    ratings_frac,
    run_button,
    seed,
    start_date,
    supervisor_frac,
):
    mo.stop(not run_button.value)
    params = Parameters(
        seed=seed.value,
        num_grids=num_grids.value,
        grid_size=grid_size.value,
        grid_spacing=grid_spacing.value,
        grid_separation=grid_separation.value,
        grid_std_dev=grid_std_dev.value,
        lat0=lat0.value,
        lon0=lon0.value,
        num_persons=num_persons.value,
        supervisor_frac=supervisor_frac.value,
        locale=locale.value,
        num_machines=num_machines.value,
        ratings_frac=ratings_frac.value,
        p_certified=p_certified.value,
        num_assays=num_assays.value,
        assay_size=assay_size.value,
        assay_certified=assay_certified.value,
        genome_length=genome_length.value,
        num_loci=num_loci.value,
        p_mutation=p_mutation.value,
        num_specimens=num_specimens.value,
        mass_beta_0=mass_beta_0.value,
        mass_beta_1=mass_beta_1.value,
        mass_sigma=mass_sigma.value,
        diam_ratio=diam_ratio.value,
        diam_sigma=diam_sigma.value,
        start_date=start_date.value,
        end_date=end_date.value,
        p_date_missing=p_date_missing.value,
    )
    conn = in_memory(params)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    table_names = [row[0] for row in cursor.fetchall()]
    rows = []
    for _name in table_names:
        count = conn.execute(f"SELECT COUNT(*) FROM [{_name}]").fetchone()[0]
        rows.append({"table": _name, "records": count})
    return (rows,)


@app.cell
def _(mo, rows):
    mo.ui.table(rows, selection=None)
    return


if __name__ == "__main__":
    app.run()
