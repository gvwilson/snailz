"""Sampled specimens."""

from dataclasses import dataclass
from datetime import date
import math
import random
from typing import ClassVar, Generator
from .utils import (
    SPECIMEN_PRECISION,
    BaseMixin,
    id_generator,
    random_date,
    validate,
    validate_lat_lon,
)


@dataclass
class Specimen(BaseMixin):
    """A single specimen."""

    table_name: ClassVar[str] = "specimen"
    _next_id: ClassVar[Generator[str, None, None]] = id_generator("S", 4)

    ident: str = ""
    lat: float = 0.0
    lon: float = 0.0
    genome: str = ""
    mass: float = 0.0
    diameter: float = 0.0
    collected: date = date.min

    def __post_init__(self):
        """Validate and fill in."""

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
    def make(cls, params, grids, species):
        "Make specimens."

        result = []
        for _ in range(params.num_specimens):
            g = random.choice(grids)
            x = random.randint(0, g.size - 1)
            y = random.randint(0, g.size - 1)
            lat, lon = g.lat_lon(x, y)
            genome = species.random_genome(params)
            mass = cls.random_mass(params, g[x, y])
            diameter = cls.random_diameter(params, mass)
            collected = random_date(params.survey_start, params.survey_end)
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
    def random_mass(cls, params, pollution):
        """Generate log-normal mass distribution modified by pollution."""

        mu = params.mass_beta_0 + params.mass_beta_1 * pollution
        log_mass = random.gauss(mu, params.mass_sigma)
        return math.exp(log_mass)

    @classmethod
    def random_diameter(cls, params, mass):
        """Generate random diameter."""

        return abs(random.gauss(mass * params.diam_ratio, params.diam_sigma))
