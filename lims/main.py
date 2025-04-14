from pathlib import Path

import click
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import uvicorn


APP_DIR = Path(__file__).parent
SETTINGS = {
    "title": "Snailz LIMS",
    "description": "Laboratory Information Management System for Snailz",
}


# Initialize.
app = FastAPI(**SETTINGS)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
app.state.db_path = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    cursor = request.app.state.db_conn.cursor()
    values = {
        "n_assays": _get_one(cursor, "select count(*) from assays"),
        "n_machines": _get_one(cursor, "select count(*) from machines"),
        "n_persons": _get_one(cursor, "select count(*) from persons"),
        "n_specimens": _get_one(cursor, "select count(*) from specimens"),
        "n_surveys": _get_one(cursor, "select count(distinct survey) from specimens"),
    }
    return templates.TemplateResponse("home.html", {"request": request, **SETTINGS, **values})


@click.command()
@click.option("--db", type=str, required=True, help="Path to SQLite database file")
def main(db):
    """Run the Snailz LIMS application."""
    assert Path(db).is_file(), f"No such database file {db}"
    app.state.db_path = db
    app.state.db_conn = sqlite3.connect(db)
    uvicorn.run(app)


def _get_one(cursor, query):
    return cursor.execute(query).fetchone()[0]


if __name__ == "__main__":
    main()
