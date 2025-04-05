"""Generate snail assays."""

import csv
from datetime import date, timedelta
import io
import random

from pydantic import BaseModel, Field, model_validator

from .grid import Grid
from .persons import AllPersons
from .specimens import Specimen, AllSpecimens
from . import utils


DEFAULT_PLATE_SIZE = 4


class AssayParams(BaseModel):
    """Parameters for assay generation."""

    baseline: float = Field(default=1.0, gt=0, description="Baseline reading value")
    degrade: float = Field(
        default=0.05,
        ge=0,
        le=1,
        description="Rate at which sample responses decrease per day after first day (0..1)",
    )
    delay: int = Field(
        default=5,
        gt=0,
        description="Maximum number of days between specimen collection and assay",
    )
    mutant: float = Field(
        default=10.0, gt=0, description="Mutant reading value (must be positive)"
    )
    noise: float = Field(
        default=0.1, gt=0, description="Noise level for readings (must be positive)"
    )
    plate_size: int = Field(
        default=DEFAULT_PLATE_SIZE, gt=0, description="Size of assay plate (must be positive)"
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
    performed: date = Field(description="date assay was performed")
    readings: Grid[float] | None = Field(default=None, description="assay readings")
    treatments: Grid[str] | None = Field(default=None, description="samples or controls")

    model_config = {"extra": "forbid"}

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
            ["ident", "specimen", "person", "performed"],
            lambda r: [r.ident, r.specimen, r.person, r.performed.isoformat()],
        )


def assays_generate(
    params: AssayParams, persons: AllPersons, specimens: AllSpecimens
) -> AllAssays:
    """Generate an assay for each specimen.

    Parameters:
        params: assay generation parameters
        persons: all staff members
        specimens: specimens to generate assays for

    Returns:
        Assay list object
    """
    locus = specimens.susc_locus
    base = specimens.susc_base
    items = []
    gen = utils.UniqueIdGenerator("assays", lambda: f"{random.randint(0, 999999):06d}")
    for spec in specimens.items:
        performed = spec.collected + timedelta(days=random.randint(0, params.delay))
        ident = gen.next()
        person = random.choice(persons.items)
        treatments = _make_treatments(params)
        readings = _make_assay(params, locus, base, spec, performed, treatments)
        items.append(
            Assay(
                ident=ident,
                performed=performed,
                specimen=spec.ident,
                person=person.ident,
                treatments=treatments,
                readings=readings,
            )
        )
    return AllAssays(items=items)


def _make_assay(
    params: AssayParams, locus: int, base: str, specimen: Specimen, performed: date, treatments: Grid[str]
) -> Grid[float]:
    """Make a single assay."""
    degradation = _calc_degradation(params, specimen.collected, performed)
    readings = Grid(width=params.plate_size, height=params.plate_size, default=0.0)
    for x in range(params.plate_size):
        for y in range(params.plate_size):
            readings[x, y] = _make_reading(params, specimen, locus, base, treatments[x, y], degradation)
    return readings


def _calc_degradation(params: AssayParams, collected: date, assayed: date) -> float:
    """Calculate degradation based on days since collection."""
    return max(0.0, 1.0 - (params.degrade * (assayed - collected).days))


def _make_reading(
    params: AssayParams,
    specimen: Specimen,
    locus: int,
    base: str,
    treatment: str,
    degradation: float,
) -> float:
    """Generate readings based on treatments and susceptibility."""

    # Control
    if treatment == "C":
        return round(random.uniform(0, params.noise), utils.PRECISION)

    # Treatment
    if specimen.genome[locus] == base:
        noise = params.noise * params.mutant / params.baseline
        base_value = params.mutant * degradation
    else:
        noise = params.noise
        base_value = params.baseline * degradation

    # Final value
    return round(base_value + random.uniform(0, noise), utils.PRECISION)


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
            treatments[x, y] = available[x * size + y]
    return treatments
