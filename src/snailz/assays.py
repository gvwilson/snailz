"""Generate snail assays."""

from datetime import date, timedelta
import csv
import io
from pathlib import Path
import random

from pydantic import BaseModel, Field, model_validator

from . import utils
from .specimens import AllSpecimens
from .people import AllPersons

# Subdirectory for writing individual assay files.
ASSAYS_SUBDIR = "assays"


class AssayParams(BaseModel):
    """Parameters for assay generation.

    - baseline: Baseline reading value (must be positive)
    - end_date: End date for assay generation
    - mutant: Mutant reading value (must be positive)
    - noise: Noise level for readings (must be positive)
    - plate_size: Size of assay plate (must be positive)
    - seed: Random seed for reproducibility
    - start_date: Start date for assay generation (must not be after end_date)
    """

    baseline: float = Field(gt=0)
    end_date: date = Field()
    mutant: float = Field(gt=0)
    noise: float = Field(gt=0)
    plate_size: int = Field(gt=0)
    seed: int = Field()
    start_date: date = Field()

    @model_validator(mode="after")
    def validate_date_range(self):
        """Validate that start_date is not after end_date."""
        if self.start_date > self.end_date:
            raise ValueError("start date must be less than or equal to end date")
        return self

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
        writer = csv.writer(output, **utils.CSV_SETTINGS)
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
        writer = csv.writer(output, utils.CSV_SETTINGS)
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
    params: AssayParams, specimens: AllSpecimens, people: AllPersons
) -> AllAssays:
    """Generate an assay for each specimen.

    Parameters:
        params: AssayParams object containing assay generation parameters
        specimens: Specimens object with individual specimens to generate assays for
        people: People object with staff members

    Returns:
        Assays object containing generated assays and parameters
    """
    days_delta = (params.end_date - params.start_date).days + 1
    individuals = specimens.individuals
    susc_locus = specimens.susceptible_locus
    susc_base = specimens.susceptible_base
    items = []

    gen = utils.UniqueIdGenerator("assays", lambda: f"{random.randint(0, 999999):06d}")

    for individual in individuals:
        assay_date = params.start_date + timedelta(
            days=random.randint(0, days_delta - 1)
        )
        assay_id = gen.next()

        # Generate treatments randomly with equal probability
        treatments = []
        for row in range(params.plate_size):
            treatment_row = []
            for col in range(params.plate_size):
                treatment_row.append(random.choice(["S", "C"]))
            treatments.append(treatment_row)

        # Generate readings based on treatments and susceptibility
        readings = []
        is_susceptible = individual.genome[susc_locus] == susc_base
        for row in range(params.plate_size):
            reading_row = []
            for col in range(params.plate_size):
                if treatments[row][col] == "C":
                    # Control cells have values uniformly distributed between 0 and noise
                    reading_row.append(random.uniform(0, params.noise))
                elif is_susceptible:
                    # Susceptible specimens (with susceptible base at susceptible locus)
                    # Base mutant value plus noise scaled by mutant/baseline ratio
                    scaled_noise = round(
                        params.noise * params.mutant / params.baseline, utils.PRECISION
                    )
                    reading_row.append(params.mutant + random.uniform(0, scaled_noise))
                else:
                    # Non-susceptible specimens
                    # Base baseline value plus uniform noise
                    reading_row.append(
                        params.baseline + random.uniform(0, params.noise)
                    )
            # Handle limited precision.
            reading_row = [round(r, utils.PRECISION) for r in reading_row]
            readings.append(reading_row)

        # Randomly select a person to perform the assay
        person = random.choice(people.individuals)

        # Create the assay record
        items.append(
            Assay(
                performed=assay_date,
                ident=assay_id,
                specimen_id=individual.ident,
                person_id=person.ident,
                readings=readings,
                treatments=treatments,
            )
        )

    return AllAssays(items=items, params=params)


def assays_to_csv(input: str, output: str | None) -> None:
    """Write assays to standard output or files."""
    data = utils.load_data("assays", input, AllAssays)

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
