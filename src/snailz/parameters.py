"""Data generation parameters."""

from dataclasses import dataclass
from datetime import date
from faker.config import AVAILABLE_LOCALES
from .utils import BaseMixin, validate, validate_lat_lon


@dataclass
class Parameters(BaseMixin):
    """Store all data generation parameters."""

    seed: int = 12345
    num_grids: int = 1
    grid_size: int = 1
    grid_spacing: float = 10.0
    lat0: float = 48.8666632
    lon0: float = -124.1999992
    num_persons: int = 1
    locale: str = "et_EE"
    num_machines: int = 1
    genome_length: int = 1
    num_loci: int = 1
    p_mutation: float = 0.5
    num_specimens: int = 1
    mass_beta_0: float = 3.0
    mass_beta_1: float = 0.5
    mass_sigma: float = 0.3
    diam_ratio: float = 0.7
    diam_sigma: float = 0.7
    survey_start: date = date(2026, 3, 1)
    survey_end: date = date(2026, 5, 31)

    def __post_init__(self):
        """Check locale."""

        validate(self.locale in AVAILABLE_LOCALES, f"unknown locale {self.locale}")
        validate_lat_lon("parameters", self.lat0, self.lon0)
