"""Generate snail assays."""

import csv
from datetime import date, timedelta
import io
import random

from pydantic import BaseModel, Field

from .persons import PersonList
from .specimens import Specimen, SpecimenList
from . import utils


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
        default=4, gt=0, description="Size of assay plate (must be positive)"
    )

    model_config = {"extra": "forbid"}


class Assay(BaseModel):
    """A single assay."""

    ident: str = Field(description="unique identifier")
    specimen: str = Field(description="which specimen")
    person: str = Field(description="who did the assay")
    performed: date = Field(description="date assay was performed")
    readings: list[list[float]] = Field(description="grid of assay readings")
    treatments: list[list[str]] = Field(description="grid of samples or controls")

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

        # Generate column headers (A, B, C, etc.) and calculate metadata padding
        plate_size = len(data)
        column_headers = [""] + [chr(ord("A") + i) for i in range(plate_size)]
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

        for i, row in enumerate(data, 1):
            writer.writerow([i] + row)

        return output.getvalue()


class AssayList(BaseModel):
    """All generated assays."""

    assays: list[Assay] = Field(description="actual assays")

    def to_csv(self) -> str:
        """Return a CSV string representation of the assay summary data.

        Returns:
            A CSV-formatted string containing a summary of all assays
        """
        return utils.to_csv(
            self.assays,
            ["ident", "specimen", "person", "performed"],
            lambda r: [r.ident, r.specimen, r.person, r.performed.isoformat()],
        )


def assays_generate(
    params: AssayParams, persons: PersonList, specimens: SpecimenList
) -> AssayList:
    """Generate an assay for each specimen.

    Parameters:
        params: assay generation parameters
        persons: all staff members
        specimens: specimens to generate assays for

    Returns:
        Assay list object
    """
    assays = []
    gen = utils.UniqueIdGenerator("assays", lambda: f"{random.randint(0, 999999):06d}")
    for s in specimens.specimens:
        performed = s.collected + timedelta(days=random.randint(0, params.delay))
        ident = gen.next()
        person = random.choice(persons.persons)
        treatments, readings = _make_assay(params, specimens, s, performed)
        assays.append(
            Assay(
                ident=ident,
                performed=performed,
                specimen=s.ident,
                person=person.ident,
                readings=readings,
                treatments=treatments,
            )
        )

    return AssayList(assays=assays)


def _make_assay(
    params: AssayParams, specimens: SpecimenList, s: Specimen, performed: date
) -> tuple[list[list[str]], list[list[float]]]:
    """Make a single assay."""
    treatments = _make_treatments(params)
    degradation = _calc_degradation(params, s.collected, performed)
    readings = [
        [
            _make_reading(params, s, _is_susceptible(specimens, s), treatments[col][row], degradation, row, col)
            for row in range(params.plate_size)
        ]
        for col in range(params.plate_size)
    ]
    return treatments, readings


def _calc_degradation(params: AssayParams, collected: date, assayed: date) -> float:
    """Calculate degradation based on days since collection."""
    return max(0.0, 1.0 - (params.degrade * (assayed - collected).days))


def _is_susceptible(specimens: SpecimenList, s: Specimen) -> bool:
    """Is this specimen susceptible to mutation effects?"""
    return s.genome[specimens.susc_locus] == specimens.susc_base


def _make_reading(
    params: AssayParams,
    specimen: Specimen,
    susceptible: bool,
    treatment: str,
    degradation: float,
    row: int,
    col: int,
) -> float:
    """Generate readings based on treatments and susceptibility."""

    # Control
    if treatment == "C":
        return round(random.uniform(0, params.noise), utils.PRECISION)

    # Treatment
    if susceptible:
        noise = params.noise * params.mutant / params.baseline
        base_value = params.mutant * degradation
    else:
        noise = params.noise
        base_value = params.baseline * degradation

    # Final value
    return round(base_value + random.uniform(0, noise), utils.PRECISION)


def _make_treatments(params: AssayParams) -> list[list[str]]:
    """Generate random treatments."""
    size = params.plate_size
    size_sq = size**2
    half = size_sq // 2
    available = list(("S" * half) + ("C" * (size_sq - half)))
    random.shuffle(available)
    return [
        [available[row + col * size] for row in range(size)]
        for col in range(size)
    ]
