"""Generate snail assays."""

from datetime import date, timedelta
import io
from pathlib import Path
import random
from typing import cast

from pydantic import BaseModel, Field

from . import utils
from .specimens import AllSpecimens
from .people import AllPersons

# Subdirectory for writing individual assay files.
ASSAYS_SUBDIR = "assays"


class AssayParams(BaseModel):
    """Parameters for assay generation.

    - baseline: Baseline reading value (must be positive)
    - degrade: Rate at which sample responses decrease per day after first day (0-1)
    - delay: Maximum number of days between specimen collection and assay (must be positive)
    - mutant: Mutant reading value (must be positive)
    - noise: Noise level for readings (must be positive)
    - oops: Factor to multiply response values by for one random person (0 means no adjustment)
    - plate_size: Size of assay plate (must be positive)
    - seed: Random seed for reproducibility
    """

    baseline: float = Field(gt=0)
    degrade: float = Field(ge=0, le=1)
    delay: int = Field(gt=0)
    mutant: float = Field(gt=0)
    noise: float = Field(gt=0)
    oops: float = Field(ge=0)
    plate_size: int = Field(gt=0)
    seed: int = Field()

    model_config = {"extra": "forbid"}


class Assay(BaseModel):
    """A single assay.

    - performed: date assay was performed
    - ident: unique identifier
    - specimen_id: which specimen
    - person_id: who did the assay
    - readings: grid of assay readings
    - treatments: grid of samples or controls
    """

    performed: date
    ident: str
    specimen_id: str
    person_id: str
    readings: list[list[float]]
    treatments: list[list[str]]

    def to_csv(self, data_type: str) -> str:
        """Return a CSV string representation of the assay data.

        Parameters:
            data_type: Type of data to output, either "readings" or "treatments"

        Returns:
            A CSV-formatted string with the assay data in the format:
            id,<assay_id>
            specimen,<specimen_id>
            performed,<performed_date>
            performed_by,<person_id>
            ,A,B,C,...
            1,<data>,<data>,...
            2,<data>,<data>,...
            ...

            The CSV output uses Unix line endings (LF).

        Raises:
            ValueError: If data_type is not "readings" or "treatments"
        """
        if data_type not in ["readings", "treatments"]:
            raise ValueError("data_type must be 'readings' or 'treatments'")

        # Get the appropriate data based on data_type
        data = self.readings if data_type == "readings" else self.treatments

        # Generate column headers (A, B, C, etc.) and calculate metadata padding
        plate_size = len(data)
        column_headers = [""] + [chr(65 + i) for i in range(plate_size)]
        max_columns = len(column_headers)
        padding = [""] * (max_columns - 2)

        # Write metadata rows with Unix line endings
        output = io.StringIO()
        writer = utils.csv_writer(output)
        writer.writerow(["id", self.ident] + padding)
        writer.writerow(["specimen", self.specimen_id] + padding)
        writer.writerow(["performed", self.performed.isoformat()] + padding)
        writer.writerow(["performed_by", self.person_id] + padding)

        # Write data rows with row numbers
        writer.writerow(column_headers)
        for i, row in enumerate(data, 1):
            writer.writerow([i] + row)
        return output.getvalue()


class AllAssays(BaseModel):
    """Keep track of generated assays.

    - items: actual assays
    - params: parameters used in generation
    """

    items: list[Assay]
    params: AssayParams

    def to_csv(self) -> str:
        """Return a CSV string representation of the assay summary data.

        Returns:
            A CSV-formatted string containing a summary of all assays with fields:
            - ident: assay identifier
            - specimen_id: specimen identifier
            - performed: date the assay was performed
            - performed_by: person identifier

            The CSV output uses Unix line endings (LF).
        """
        output = io.StringIO()
        writer = utils.csv_writer(output)
        writer.writerow(["ident", "specimen_id", "performed", "performed_by"])
        for assay in self.items:
            writer.writerow(
                [
                    assay.ident,
                    assay.specimen_id,
                    assay.performed.isoformat(),
                    assay.person_id,
                ]
            )
        return output.getvalue()


def assays_generate(
    params: AssayParams, people: AllPersons, specimens: AllSpecimens
) -> AllAssays:
    """Generate an assay for each specimen.

    Parameters:
        params: AssayParams object containing assay generation parameters
        people: People object with staff members
        specimens: Specimens object with individual specimens to generate assays for

    Returns:
        Assays object containing generated assays and parameters
    """
    individuals = specimens.individuals
    susc_locus = specimens.susceptible_locus
    susc_base = specimens.susceptible_base
    items = []

    gen = utils.UniqueIdGenerator("assays", lambda: f"{random.randint(0, 999999):06d}")

    # If oops factor is greater than 0, select one person randomly to have their values adjusted
    oops_person_id = None
    if params.oops > 0:
        oops_person = random.choice(people.individuals)
        oops_person_id = oops_person.ident

    for individual in individuals:
        # Set assay date to specimen collection date plus a random number of days (0 to delay)
        assay_date = individual.collected_on + timedelta(
            days=random.randint(0, params.delay)
        )
        assay_id = gen.next()

        # Generate treatments randomly with equal probability
        treatments = []
        for row in range(params.plate_size):
            treatment_row = []
            for col in range(params.plate_size):
                treatment_row.append(random.choice(["S", "C"]))
            treatments.append(treatment_row)

        # Calculate degradation factor based on days since collection
        days_since_collection = (assay_date - individual.collected_on).days
        degradation_days = max(
            0, days_since_collection - 1
        )  # No degradation on first day
        degradation_factor = max(0.0, 1.0 - (params.degrade * degradation_days))

        # Randomly select a person to perform the assay
        person = random.choice(people.individuals)
        person_id = person.ident

        # Generate readings based on treatments and susceptibility
        readings = []
        is_susceptible = individual.genome[susc_locus] == susc_base
        for row in range(params.plate_size):
            reading_row = []
            for col in range(params.plate_size):
                if treatments[row][col] == "C":
                    # Control cells have values uniformly distributed between 0 and noise
                    # Controls are not affected by degradation or oops factor
                    value = random.uniform(0, params.noise)
                else:
                    if is_susceptible:
                        # Susceptible specimens
                        noise = params.noise * params.mutant / params.baseline
                        base_value = params.mutant * degradation_factor
                    else:
                        # Non-susceptible specimens
                        noise = params.noise
                        base_value = params.baseline * degradation_factor

                    # Calculate value and adjust for oops
                    value = base_value + random.uniform(0, noise)
                    if params.oops > 0 and person_id == oops_person_id:
                        value = value * (1 + params.oops)

                reading_row.append(round(value, utils.PRECISION))

            readings.append(reading_row)

        # Create the assay record
        items.append(
            Assay(
                performed=assay_date,
                ident=assay_id,
                specimen_id=individual.ident,
                person_id=person_id,
                readings=readings,
                treatments=treatments,
            )
        )

    return AllAssays(items=items, params=params)


def assays_to_csv(input: str | Path, output: str | Path | None) -> None:
    """Write assays to standard output or files."""
    data = utils.load_data("assays", input, AllAssays)

    # Type casting for the type checker - this tells the type checker
    # that data is an AllAssays instance, but doesn't perform any runtime checks
    data = cast(AllAssays, data)

    # For stdout, only output the summary
    if output is None:
        content = data.to_csv()
        print(content, end="")
        return

    output_path = Path(output)
    with open(output_path / "assays.csv", "w") as writer:
        writer.write(data.to_csv())

    # Create assays subdirectory
    assays_dir = output_path / ASSAYS_SUBDIR
    assays_dir.mkdir(exist_ok=True)

    # Write individual assay files
    for assay in data.items:
        # Design file
        design_file = assays_dir / f"{assay.ident}_design.csv"
        with open(design_file, "w") as writer:
            writer.write(assay.to_csv(data_type="treatments"))

        # Readings file
        assay_file = assays_dir / f"{assay.ident}_assay.csv"
        with open(assay_file, "w") as writer:
            writer.write(assay.to_csv(data_type="readings"))
