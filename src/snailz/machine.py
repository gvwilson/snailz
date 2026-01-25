"""Laboratory machinery."""

from pydantic import BaseModel, Field
import random
from typing import ClassVar

from . import utils


PREFIX = [
    "Aero",
    "Auto",
    "Bio",
    "Centri",
    "Chroma",
    "Cryo",
    "Electro",
    "Fluoro",
    "Hydro",
    "Micro",
    "Nano",
    "Omni",
    "Poly",
    "Pyro",
    "Therma",
    "Ultra",
]

SUFFIX = [
    "Analyzer",
    "Bath",
    "Chamber",
    "Counter",
    "Extractor",
    "Fuge",
    "Incubator",
    "Mixer",
    "Pipette",
    "Probe",
    "Reactor",
    "Reader",
    "Scope",
    "Sensor",
    "Station",
]


class Machine(BaseModel):
    """A piece of experimental machinery."""

    _id_gen: ClassVar[utils.id_gen] = utils.id_gen("M", 4)

    machine_id: str = Field(
        description="machine ID", json_schema_extra={"primary_key": True}
    )
    name: str = Field(description="machine name")

    @staticmethod
    def make(params):
        """Generate a list of machines."""

        assert params.num_machines <= len(PREFIX) * len(SUFFIX), (
            f"cannot generate {params.num_machines} machine names"
        )
        pairs = [(p, s) for p in PREFIX for s in SUFFIX]
        return [
            Machine(machine_id=next(Machine._id_gen), name=f"{p} {s}")
            for i, (p, s) in enumerate(random.sample(pairs, k=params.num_machines))
        ]
