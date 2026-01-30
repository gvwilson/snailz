"""Laboratory machinery."""

from dataclasses import dataclass
import random
from typing import ClassVar, Generator
from ._base_mixin import BaseMixin
from ._utils import id_generator, validate


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


@dataclass
class Machine(BaseMixin):
    """A piece of experimental machinery."""

    primary_key: ClassVar[str] = "ident"
    foreign_keys: ClassVar[list[tuple[str, str, str]]] = []
    table_name: ClassVar[str] = "machine"
    _next_id: ClassVar[Generator[str, None, None]] = id_generator("M", 4)

    ident: str = ""
    name: str = ""

    def __post_init__(self):
        """Validate and fill in."""

        validate(self.ident == "", "machine ID cannot be set externally")
        validate(len(self.name) > 0, "name cannot be empty")

        self.ident = next(self._next_id)

    @classmethod
    def make(cls, params):
        """Make machines."""

        assert params.num_machines <= len(PREFIX) * len(SUFFIX), (
            f"cannot generate {params.num_machines} machine names"
        )
        pairs = [(p, s) for p in PREFIX for s in SUFFIX]
        return [
            Machine(name=f"{p} {s}")
            for (p, s) in random.sample(pairs, k=params.num_machines)
        ]
