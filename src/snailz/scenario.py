"""Represent snailz parameters."""

from pathlib import Path
import shutil

from pydantic import BaseModel, Field

from .assays import AllAssays
from .images import AllImages
from .machines import AllMachines
from .mangle import mangle_assays
from .parameters import ScenarioParams
from .persons import AllPersons
from .specimens import AllSpecimens
from .surveys import AllSurveys
from . import utils


class ScenarioData(BaseModel):
    """Represent all generated data combined."""

    assays: AllAssays = Field(description="all assays")
    images: dict = Field(description="all images")
    machines: AllMachines = Field(description="all machines")
    params: ScenarioParams = Field(description="all parameters")
    persons: AllPersons = Field(description="all persons")
    specimens: AllSpecimens = Field(description="all specimens")
    surveys: AllSurveys = Field(description="all surveys")

    model_config = {"extra": "forbid"}

    @staticmethod
    def generate(params: ScenarioParams, with_images: bool = True) -> "ScenarioData":
        """Generate data."""
        machines = AllMachines.generate(params.machine)
        surveys = AllSurveys.generate(params.survey)
        persons = AllPersons.generate(params.person)
        specimens = AllSpecimens.generate(params.specimen, surveys)
        assays = AllAssays.generate(params.assay, persons, machines, specimens)
        images = AllImages.generate(params.assay, assays) if with_images else {}
        return ScenarioData(
            assays=assays,
            images=images,
            machines=machines,
            params=params,
            persons=persons,
            specimens=specimens,
            surveys=surveys,
        )

    @staticmethod
    def save(out_dir: Path, data: "ScenarioData", full: bool) -> None:
        """Save all data.

        Parameters:
            out_dir: where to write
            data: what to write
            full: save all details
        """

        # Preparation
        if not out_dir.is_dir():
            raise ValueError(f"{out_dir} is not a directory")
        assays_dir = _ensure_dir(out_dir / utils.ASSAYS_DIR)
        surveys_dir = _ensure_dir(out_dir / utils.SURVEYS_DIR)

        # One big JSON
        with open(out_dir / utils.DATA_JSON, "w") as writer:
            writer.write(utils.json_dump(data, indent=None))

        # Assays
        with open(out_dir / utils.ASSAYS_CSV, "w") as writer:
            writer.write(data.assays.to_csv())
        for assay in data.assays.items:
            for which in ["readings", "treatments"]:
                with open(assays_dir / f"{assay.ident}_{which}.csv", "w") as writer:
                    writer.write(assay.to_csv(which))

        # Images
        for ident, image in data.images.items():
            image.save(assays_dir / f"{ident}.png")

        # Machines
        with open(out_dir / utils.MACHINES_CSV, "w") as writer:
            writer.write(data.machines.to_csv())

        # Mangled assays
        mangle_assays(out_dir / utils.ASSAYS_DIR, data.persons)

        # Persons
        with open(out_dir / utils.PERSONS_CSV, "w") as writer:
            writer.write(data.persons.to_csv())

        # Specimens
        with open(out_dir / utils.SPECIMENS_CSV, "w") as writer:
            writer.write(data.specimens.to_csv(full=full))

        # Surveys
        for survey in data.surveys.items:
            with open(surveys_dir / f"{survey.ident}.csv", "w") as writer:
                writer.write(survey.to_csv())


def _ensure_dir(dir_path: Path) -> Path:
    """Ensure that directory exists and is empty."""
    if dir_path.is_dir():
        shutil.rmtree(dir_path)
    dir_path.mkdir(exist_ok=True)
    return dir_path
