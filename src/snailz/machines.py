"""Laboratory machinery."""

import random

from pydantic import BaseModel, Field

from .parameters import MachineParams
from . import model, utils


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

MAIN = [
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

SUFFIX = [
    "5000",
    "6000",
    "9000",
    "Alpha",
    "Beta",
    "Elite",
    "Lite",
    "Max",
    "Plus",
    "Prime",
    "Pro",
    "Ultra",
    "X",
]

# Probability of suffix on machine name
PROB_SUFFIX = 0.7


class Machine(BaseModel):
    """A piece of experimental machinery."""

    ident: str = Field(description="machine ID")
    name: str = Field(description="machine name")
    brightness: float = Field(default=1.0, ge=0, description="brightness amplification")


class AllMachines(BaseModel):
    """A set of generated machines."""

    items: list[Machine] = Field(description="all machinery")

    def to_csv(self) -> str:
        """Return a CSV string representation of the machines.

        Returns:
            A CSV-formatted string.
        """
        return utils.to_csv(
            self.items,
            ["ident", "name"],
            lambda m: [m.ident, m.name],
        )

    @staticmethod
    def generate(params: MachineParams) -> "AllMachines":
        """Generate laboratory machinery.

        Parameters:
            params: machine generation parameters

        Returns:
            A set of equipment.
        """
        name_gen = utils.unique_id("machine", _machine_name_generator)
        return AllMachines(
            items=[
                Machine(
                    ident=f"M000{i + 1}",
                    name=next(name_gen),
                    brightness=model.machine_brightness(params),
                )
                for i in range(params.number)
            ]
        )


def _machine_name_generator():
    """Generate random name for a machine."""
    name = f"{utils.choose_one(PREFIX)}{utils.choose_one(MAIN)}"
    if random.uniform(0.0, 1.0) < PROB_SUFFIX:
        name = f"{name} {utils.choose_one(SUFFIX)}"
    return name
