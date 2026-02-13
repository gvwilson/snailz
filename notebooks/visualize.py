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
    from snailz import in_memory, Parameters
    return in_memory, mo, Parameters


@app.cell
def _(in_memory, Parameters):
    conn = in_memory(Parameters())
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    table_names = [row[0] for row in cursor.fetchall()]
    rows = []
    for _name in table_names:
        count = conn.execute(f"SELECT COUNT(*) FROM [{_name}]").fetchone()[0]
        rows.append({"table": _name, "records": count})
    return rows,


@app.cell
def _(mo, rows):
    mo.ui.table(rows, selection=None)
    return


if __name__ == "__main__":
    app.run()
