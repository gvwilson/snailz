"""Generate snail assays."""

import csv
from datetime import date, timedelta
import io
import math
import random

from pydantic import BaseModel, Field, model_validator

from .grid import Grid
from .machines import Machine, AllMachines
from .persons import AllPersons
from .specimens import Specimen, AllSpecimens
from . import utils


DEFAULT_PLATE_SIZE = 4
NUM_ASSAY_HEADER_ROWS = 6


class AssayParams(BaseModel):
    """Parameters for assay generation."""

    baseline: float = Field(default=2.0, ge=0.0, description="Baseline reading value")
    degrade: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Rate at which sample responses decrease per day after first day (0..1)",
    )
    delay: int = Field(
        default=5,
        gt=0,
        description="Maximum number of days between specimen collection and assay",
    )
    mutant: float = Field(
        default=5.0, gt=0.0, description="Mutant reading value (must be positive)"
    )
    reading_noise: float = Field(
        default=0.2, ge=0.0, description="Noise level for readings (must be positive)"
    )
    plate_size: int = Field(
        default=DEFAULT_PLATE_SIZE,
        gt=0,
        description="Size of assay plate (must be positive)",
    )
    image_noise: int = Field(
        default=32,
        ge=0,
        le=255,
        description="Plate image noise (grayscale 0-255)",
    )
    p_duplicate_assay: float = Field(
        default=0.05, ge=0, description="Probably that an assay is repeated"
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_fields(self):
        """Validate requirements on fields."""
        if self.mutant < self.baseline:
            raise ValueError("mutant value must be greater than baseline")
        return self


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
        extra = random.choices(
            specimens.items,
            k=math.floor(params.p_duplicate_assay * len(specimens.items)),
        )
        subjects = specimens.items + extra
        random.shuffle(subjects)

        gen = utils.unique_id("assays", lambda: f"{random.randint(0, 999999):06d}")
        items = []
        for spec in subjects:
            performed = spec.collected + timedelta(days=random.randint(0, params.delay))
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


def _calc_degradation(params: AssayParams, collected: date, assayed: date) -> float:
    """Calculate degradation based on days since collection."""
    return max(0.0, 1.0 - (params.degrade * (assayed - collected).days))


def _make_readings(
    params: AssayParams,
    specimen: Specimen,
    performed: date,
    machine: Machine,
    treatments: Grid[str],
) -> Grid[float]:
    """Make a single assay."""
    degradation = _calc_degradation(params, specimen.collected, performed)
    readings = Grid(width=params.plate_size, height=params.plate_size, default=0.0)
    for x in range(params.plate_size):
        for y in range(params.plate_size):
            if treatments[x, y] == "C":
                base_value = 0.0
            elif specimen.is_mutant:
                base_value = params.mutant * degradation
            else:
                base_value = params.baseline * degradation
            readings[x, y] = round(
                base_value + random.uniform(0.0, params.reading_noise), utils.PRECISION
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
