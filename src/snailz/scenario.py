"""Entire scenario."""

import csv
import random
import math
from pathlib import Path

from PIL.Image import Image
from pydantic import BaseModel, Field

from .params import ScenarioParams
from .assays import Assay
from .effects import apply_effects, assign_sample_locations
from .grid import Grid
from .images import make_image
from .machines import Machine
from .mangle import mangle_assay
from .persons import Person
from .specimens import AllSpecimens
from .utils import max_grid_value


class Scenario(BaseModel):
    """Entire synthetic data scenario."""

    params: ScenarioParams = Field(description="scenario parameters")
    grids: list[Grid] = Field(default_factory=list, description="sample site grids")
    specimens: AllSpecimens = Field(description="all specimens")
    machines: list[Machine] = Field(
        default_factory=[], description="laboratory machines"
    )
    persons: list[Person] = Field(default_factory=[], description="lab staff")
    assays: list[Assay] = Field(default_factory=[], description="assays")
    images: dict[str, Image] = Field(default_factory={}, description="assay images")

    # Allow arbitrary types to handle Image
    model_config = {"arbitrary_types_allowed": True, "extra": "forbid"}

    @staticmethod
    def generate(params):
        """Generate entire scenario.

        Parameters:
            params (ScenarioParams): controlling parameters

        Returns:
            (Scenario): all generated data.
        """
        machines = Machine.generate(params.num_machines)
        persons = Person.generate(params.locale, params.num_persons)
        grids = [Grid.generate(params.grid_size) for _ in range(params.num_sites)]
        specimens = AllSpecimens.generate(params.specimen_params, params.num_specimens)
        assign_sample_locations(grids, specimens)

        assays = []
        for s in specimens.samples:
            for i in range(params.assays_per_specimen):
                assays.append(
                    Assay.generate(
                        params.assay_params,
                        s,
                        random.choice(machines),
                        random.choice(persons),
                    )
                )

        all_readings = [a.readings for a in assays]
        scaling = float(math.ceil(max_grid_value(all_readings) + 1))
        images = {a.id: make_image(params.assay_params, a, scaling) for a in assays}

        result = Scenario(
            params=params,
            machines=machines,
            persons=persons,
            grids=grids,
            specimens=specimens,
            assays=assays,
            images=images,
        )
        apply_effects(result)
        return result

    def to_csv(self, root):
        """Write as CSV (and PNG).

        Parameters:
            root (str): root directory for output
        """

        root = Path(root)
        root.mkdir(exist_ok=True)

        with open(root / "machines.csv", "w") as stream:
            Machine.to_csv(csv.writer(stream), self.machines)

        with open(root / "persons.csv", "w") as stream:
            Person.to_csv(csv.writer(stream), self.persons)

        for grid in self.grids:
            with open(root / f"{grid.id}.csv", "w") as stream:
                print(grid, file=stream)

        with open(root / "specimens.csv", "w") as stream:
            self.specimens.to_csv(csv.writer(stream))

        with open(root / "assays.csv", "w") as stream:
            Assay.all_csv(csv.writer(stream), self.assays)

        for assay in self.assays:
            treatments_file = root / f"{assay.id}_treatments.csv"
            with open(treatments_file, "w") as stream:
                assay.to_csv(csv.writer(stream), True)

            readings_file = root / f"{assay.id}_readings.csv"
            raw_file = root / f"{assay.id}_raw.csv"
            with open(readings_file, "w") as stream:
                assay.to_csv(csv.writer(stream), False)
            mangle_assay(readings_file, raw_file, self.persons)

        for id, img in self.images.items():
            img_file = root / f"{id}.png"
            img.save(img_file)
