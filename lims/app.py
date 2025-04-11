"""Laboratory information management system."""

import click
import csv
from pathlib import Path
from pypika import Query, Table
import sqlite3

from flask import Flask, render_template


ASSAYS_TBL = Table("assays")
MACHINES_TBL = Table("machines")
PERSONS_TBL = Table("persons")

app = Flask(__name__)


@app.route("/")
def home():
    conn = _get_connection(app.config)
    q = Query.from_(ASSAYS_TBL).select("*").orderby("performed")
    assays = conn.execute(str(q)).fetchall()
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
    q = Query.from_(MACHINES_TBL).select("*").where(MACHINES_TBL.ident == ident)
    machine = conn.execute(str(q)).fetchone()
    q = (
        Query.from_(ASSAYS_TBL)
        .select("*")
        .where(ASSAYS_TBL.machine == ident)
        .orderby(ASSAYS_TBL.performed)
    )
    assays = conn.execute(str(q)).fetchall()
    return render_template("machine.jinja", ident=ident, machine=machine, assays=assays)


@app.route("/person/<ident>")
def person(ident):
    conn = _get_connection(app.config)
    q = Query.from_(PERSONS_TBL).select("*").where(PERSONS_TBL.ident == ident)
    person = conn.execute(str(q)).fetchone()
    q = (
        Query.from_(ASSAYS_TBL)
        .select("*")
        .where(ASSAYS_TBL.person == ident)
        .orderby(ASSAYS_TBL.performed)
    )
    assays = conn.execute(str(q)).fetchall()
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
