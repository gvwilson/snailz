"""Generate snail assays."""

import csv
from datetime import date
import io
import random

from pydantic import BaseModel, Field, model_validator

from .grid import Grid
from .machines import Machine, AllMachines
from .parameters import AssayParams
from .persons import AllPersons
from .specimens import Specimen, AllSpecimens
from . import model, utils


NUM_ASSAY_HEADER_ROWS = 6


class Assay(BaseModel):
    """A single assay."""

    ident: str = Field(description="unique identifier")
    specimen: str = Field(description="which specimen")
    person: str = Field(description="who did the assay")
    machine: str = Field(description="machine ID")
    performed: date = Field(description="date assay was performed")
    readings: Grid[float] = Field(description="assay readings")
    treatments: Grid[str] = Field(description="samples or controls")

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def show_fields(self):
        return self

    def to_csv(self, kind: str) -> str:
        """Return a CSV string representation of the assay data.

        Parameters:
            kind: Either "readings" or "treatments"

        Returns:
            A CSV-formatted string with the assay data.

        Raises:
            ValueError: If 'kind' is not "readings" or "treatments"
        """
        if kind not in ["readings", "treatments"]:
            raise ValueError("data_type must be 'readings' or 'treatments'")

        # Get the appropriate data based on data_type
        data = self.readings if kind == "readings" else self.treatments
        assert isinstance(data, Grid)

        # Generate column headers (A, B, C, etc.) and calculate metadata padding
        column_headers = [""] + [chr(ord("A") + i) for i in range(data.width)]
        max_columns = len(column_headers)
        padding = [""] * (max_columns - 2)

        # Write data
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        pre = [
            ["id", self.ident] + padding,
            ["specimen", self.specimen] + padding,
            ["date", self.performed.isoformat()] + padding,
            ["by", self.person] + padding,
            ["machine", self.machine] + padding,
            column_headers,
        ]
        for row in pre:
            writer.writerow(row)

        for i, y in enumerate(range(data.height - 1, -1, -1)):
            row = [i + 1] + [data[x, y] for x in range(data.width)]
            writer.writerow(row)

        return output.getvalue()


class AllAssays(BaseModel):
    """All generated assays."""

    items: list[Assay] = Field(description="actual assays")

    def to_csv(self) -> str:
        """Return a CSV string representation of the assay summary data.

        Returns:
            A CSV-formatted string containing a summary of all assays
        """
        return utils.to_csv(
            self.items,
            ["ident", "specimen", "person", "performed", "machine"],
            lambda r: [
                r.ident,
                r.specimen,
                r.person,
                r.performed.isoformat(),
                r.machine,
            ],
        )

    @staticmethod
    def generate(
        params: AssayParams,
        persons: AllPersons,
        machines: AllMachines,
        specimens: AllSpecimens,
    ) -> "AllAssays":
        """Generate an assay for each specimen.

        Parameters:
            params: assay generation parameters
            persons: all staff members
            machines: all laboratory equipment
            specimens: specimens to generate assays for

        Returns:
            Assay list object
        """
        # Duplicate a few specimens and randomize order.
        subjects = model.assay_specimens(params, specimens)

        gen = utils.unique_id("assays", lambda: f"{random.randint(0, 999999):06d}")
        items = []
        for spec in subjects:
            performed = spec.collected + model.assay_performed(params)
            person = random.choice(persons.items)
            machine = random.choice(machines.items)
            treatments = _make_treatments(params)
            readings = _make_readings(params, spec, performed, machine, treatments)
            ident = next(gen)
            assert isinstance(ident, str)  # to satisfy type checking
            items.append(
                Assay(
                    ident=ident,
                    performed=performed,
                    specimen=spec.ident,
                    person=person.ident,
                    machine=machine.ident,
                    treatments=treatments,
                    readings=readings,
                )
            )

        return AllAssays(items=items)


def _make_readings(
    params: AssayParams,
    specimen: Specimen,
    performed: date,
    machine: Machine,
    treatments: Grid[str],
) -> Grid[float]:
    """Make a single assay."""
    readings = Grid(width=params.plate_size, height=params.plate_size, default=0.0)
    for x in range(params.plate_size):
        for y in range(params.plate_size):
            readings[x, y] = round(
                model.assay_reading(params, specimen, treatments[x, y], performed),
                utils.PRECISION,
            )
    return readings


def _make_treatments(params: AssayParams) -> Grid[str]:
    """Generate random treatments."""
    size = params.plate_size
    size_sq = size**2
    half = size_sq // 2
    available = list(("S" * half) + ("C" * (size_sq - half)))
    random.shuffle(available)
    treatments = Grid(width=size, height=size, default="")
    for x in range(size):
        for y in range(size):
            treatments[x, y] = available.pop()
    return treatments
