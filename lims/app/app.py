"""Laboratory information management system."""

import click
import csv
from pathlib import Path
import sqlite3
import sys

from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home():
    conn = _get_connection(app.config)
    assays = conn.execute("select * from assays order by performed").fetchall()
    return render_template("home.jinja", assays=assays)


@app.route("/assay/<ident>")
def assay(ident):
    assay_dir = Path(app.config["data"]) / "assays"
    with open(assay_dir / f"{ident}_treatments.csv", "r") as stream:
        treatments = [row for row in csv.reader(stream)]
    with open(assay_dir / f"{ident}_readings.csv", "r") as stream:
        readings = [row for row in csv.reader(stream)]
    metadata = [r[:2] for r in treatments[:5]]
    treatments = treatments[5:]
    readings = readings[5:]
    return render_template(
        "assay.jinja",
        ident=ident,
        metadata=metadata,
        treatments=treatments,
        readings=readings,
    )


@app.route("/machine/<ident>")
def machine(ident):
    conn = _get_connection(app.config)
    machine = conn.execute("select * from machines where ident=?", (ident,)).fetchone()
    assays = conn.execute(
        "select * from assays where machine=? order by performed", (ident,)
    ).fetchall()
    return render_template("machine.jinja", ident=ident, machine=machine, assays=assays)


@app.route("/person/<ident>")
def person(ident):
    conn = _get_connection(app.config)
    person = conn.execute("select * from persons where ident=?", (ident,)).fetchone()
    assays = conn.execute(
        "select * from assays where person=? order by performed", (ident,)
    ).fetchall()
    return render_template("person.jinja", ident=ident, person=person, assays=assays)


@app.errorhandler(404)
def err_no_page(e):
    return render_template("404.jinja"), 404


def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _get_connection(config):
    if "connection" not in config:
        db_path = Path(config["data"]) / "snailz.db"
        conn = sqlite3.connect(str(db_path))
        if config["memory"]:
            memory = sqlite3.connect(":memory:")
            conn.backup(memory)
            conn = memory
        conn.row_factory = _dict_factory
        config["connection"] = conn
    return config["connection"]


@click.command()
@click.option("--data", required=True, help="path to data directory")
@click.option("--memory", is_flag=True, default=False, help="use in-memory database")
def cli(data, memory):
    app.config["data"] = data
    app.config["memory"] = memory
    app.run(debug=True)


if __name__ == "__main__":
    cli()
