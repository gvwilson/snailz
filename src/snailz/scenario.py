"""Entire scenario."""

import csv
import random
import math
from pathlib import Path
import sys

from PIL.Image import Image
from pydantic import BaseModel, Field

from .params import AssayParams, SpecimenParams, ScenarioParams
from .assays import Assay
from .grid import Grid
from .images import make_image
from .machines import Machine
from .mangle import mangle_assay
from .persons import Person
from .specimens import AllSpecimens


class Scenario(BaseModel):
    """Entire synthetic data scenario."""

    params: ScenarioParams = Field(description="scenario parameters")
    grids: list[Grid] = Field(default_factory=list, description="sample site grids")
    specimens: AllSpecimens = Field(description="all specimens")
    sampled: dict[str, tuple[str, tuple[int, int]]] = Field(
        default_factory=dict, description="where specimens taken"
    )
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
        """Generate entire scenario."""
        grids = [Grid.generate(params.grid_size) for _ in range(params.num_sites)]
        specimens = AllSpecimens.generate(params.specimen_params, params.num_specimens)
        machines = Machine.generate(params.num_machines)
        persons = Person.generate(params.locale, params.num_persons)

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

        scaling = float(math.ceil(_max_reading(assays) + 1))
        images = {a.id: make_image(params.assay_params, a, scaling) for a in assays}

        return Scenario(
            params=params,
            grids=grids,
            specimens=specimens,
            sampled=Scenario.sample(params.grid_size, grids, specimens.samples),
            machines=Machine.generate(params.num_machines),
            persons=Person.generate(params.locale, params.num_persons),
            assays=assays,
            images=images,
        )

    @staticmethod
    def sample(size, grids, specimens):
        """Allocate specimens to grids."""
        grid_ids = [g.id for g in grids]
        coords = {
            g.id: [(x, y) for x in range(size) for y in range(size)] for g in grids
        }
        result = {}
        for s in specimens:
            gid = random.choice(grid_ids)
            loc = random.choice(range(len(coords[gid])))
            result[s.id] = (gid, coords[gid][loc])
            del coords[gid][loc]
        return result

    def to_csv(self, root):
        """Write to multi-CSV."""

        root = Path(root)
        root.mkdir(exist_ok=True)

        with open(root / "machines.csv", "w") as stream:
            Machine.to_csv(csv.writer(stream), self.machines)

        with open(root / "persons.csv", "w") as stream:
            Person.to_csv(csv.writer(stream), self.persons)

        for grid in self.grids:
            with open(root / f"{grid.id}.csv", "w") as stream:
                Grid.to_csv(csv.writer(stream), grid)

        with open(root / "specimens.csv", "w") as stream:
            self.specimens.to_csv(csv.writer(stream))

        with open(root / "assays.csv", "w") as stream:
            Assay.all_csv(csv.writer(stream), self.assays)

        for assay in self.assays:
            treatments_file = root / f"{assay.id}_treatments.csv"
            with open(treatments_file, "w") as stream:
                assay.to_csv(csv.writer(stream), False)

            readings_file = root / f"{assay.id}_readings.csv"
            raw_file = root / f"{assay.id}_raw.csv"
            with open(readings_file, "w") as stream:
                assay.to_csv(csv.writer(stream), True)
            mangle_assay(readings_file, raw_file, self.persons)

        for id, img in self.images.items():
            img_file = root / f"{id}.png"
            img.save(img_file)


def _max_reading(assays):
    """Find maximum reading across all assays."""

    result = 0.0
    for a in assays:
        for x in range(a.readings.size):
            for y in range(a.readings.size):
                result = max(result, a.readings[x, y])
    return result
