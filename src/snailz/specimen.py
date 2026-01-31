"""Sampled specimens."""

from dataclasses import dataclass
from datetime import date
import math
import random
from typing import ClassVar, Self

from ._base_mixin import BaseMixin
from ._utils import (
    IdGeneratorType,
    id_generator,
    random_date,
    validate,
    validate_lat_lon,
)
from .grid import Grid
from .parameters import Parameters
from .species import Species


# Mass and diameter precision.
SPECIMEN_PRECISION = 1


@dataclass
class Specimen(BaseMixin):
    """
    A single specimen.

    Attributes:
        ident: unique identifier
        lat: latitude where specimen collected (from grid cell)
        lon: longitude where specimen collected (from grid cell)
        genome: specimen genome
        mass: specimen mass (g)
        diameter: specimen diameter (mm)
        collected: date specimen was collected
    """

    table_name: ClassVar[str] = "specimen"
    _next_id: IdGeneratorType = id_generator("S", 4)

    ident: str = ""
    lat: float = 0.0
    lon: float = 0.0
    genome: str = ""
    mass: float = 0.0
    diameter: float = 0.0
    collected: date = date.min

    def __post_init__(self):
        """
        Validate fields and generate unique identifier.

        Raises:
            ValueError: If validation fails.
        """

        validate(self.ident == "", "specimen ID cannot be set externally")
        validate_lat_lon("specimen", self.lat, self.lon)
        validate(len(self.genome) > 0, "specimen must have genome")
        validate(self.mass > 0, "specimen must have positive mass")
        validate(self.diameter > 0, "specimen must have positive diameter")
        validate(
            self.collected > date.min, "specimen must have sensible collection date"
        )

        self.ident = next(self._next_id)
        self.mass = round(self.mass, SPECIMEN_PRECISION)
        self.diameter = round(self.diameter, SPECIMEN_PRECISION)

    @classmethod
    def make(cls, params: Parameters, grids: list[Grid], species: Species) -> list[Self]:
        """
        Construct multiple specimens.

        Args:
            params: Parameters object.
            grids: Grids that specimens are taken from.
            species: Species that specimens belong to.

        Returns:
            List of specimens.
        """

        result = []
        for _ in range(params.num_specimens):
            g = random.choice(grids)
            x = random.randint(0, g.size - 1)
            y = random.randint(0, g.size - 1)
            lat, lon = g.lat_lon(x, y)
            genome = species.random_genome(params)
            mass = cls.random_mass(params, g[x, y])
            diameter = cls.random_diameter(params, mass)
            collected = random_date(params.start_date, params.end_date)
            result.append(
                Specimen(
                    lat=lat,
                    lon=lon,
                    genome=genome,
                    mass=mass,
                    diameter=diameter,
                    collected=collected,
                )
            )

        return result

    @classmethod
    def random_diameter(cls, params: Parameters, mass: float) -> float:
        """
        Generate normal random diameter.

        Args:
            params: Parameters object.
            mass: pre-calculated mass.

        Returns:
            Random diameter for specimen.
        """

        return abs(random.gauss(mass * params.diam_ratio, params.diam_sigma))

    @classmethod
    def random_mass(cls, params: Parameters, pollution: float) -> float:
        """
        Generate log-normal mass distribution modified by pollution.

        Args:
            params: Parameters object.
            pollution: Pollution level in specimen's grid cell.

        Returns:
            Random mass for specimen.
        """

        mu = params.mass_beta_0 + params.mass_beta_1 * pollution
        log_mass = random.gauss(mu, params.mass_sigma)
        return math.exp(log_mass)
