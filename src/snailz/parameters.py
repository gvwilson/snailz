"""Data generation parameters."""

from dataclasses import dataclass
from datetime import date
from faker.config import AVAILABLE_LOCALES

from ._base_mixin import BaseMixin
from ._utils import validate, validate_lat_lon


@dataclass
class Parameters(BaseMixin):
    """
    Store all data generation parameters.  See the main documentation page
    for a description of parameters' meanings.
    """

    seed: int = 12345
    num_grids: int = 1
    grid_separation: int = 4
    grid_size: int = 1
    grid_spacing: float = 10.0
    grid_std_dev: float = 0.5
    lat0: float = 48.8666632
    lon0: float = -124.1999992
    num_persons: int = 1
    supervisor_frac: float = 0.3
    locale: str = "et_EE"
    num_machines: int = 1
    ratings_frac: float = 0.5
    p_certified: float = 0.3
    num_assays: int = 1
    assay_size: int = 2
    assay_certified: float = 3.0
    genome_length: int = 1
    num_loci: int = 1
    p_mutation: float = 0.5
    num_specimens: int = 1
    mass_beta_0: float = 3.0
    mass_beta_1: float = 0.5
    mass_sigma: float = 0.3
    diam_ratio: float = 0.7
    diam_sigma: float = 0.7
    start_date: date = date(2026, 3, 1)
    end_date: date = date(2026, 5, 31)

    def __post_init__(self):
        """Validate fields."""

        validate(self.num_grids > 0, "require positive number of grids")
        validate(self.grid_size > 0, "require positive grid size")
        validate(self.grid_spacing > 0, "require positive grid spacing")
        validate_lat_lon("parameters", self.lat0, self.lon0)
        validate(self.num_persons > 0, "require positive number of persons")
        validate(
            self.supervisor_frac >= 0.0, "require non-negative supervisor fraction"
        )
        validate(self.locale in AVAILABLE_LOCALES, f"unknown locale {self.locale}")
        validate(self.num_machines > 0, "require positive number of machines")
        validate(0.0 <= self.ratings_frac <= 1.0, "require ratings fraction in [0..1]")
        validate(self.num_assays >= 1, "require at least one assay")
        validate(self.assay_size >= 2, "require assay size at least two")
        validate(self.genome_length > 0, "require positive genome length")
        validate(self.num_loci >= 0, "require non-negative number of loci")
        validate(
            0.0 <= self.p_mutation <= 1.0, "require mutation probability in [0..1]"
        )
        validate(self.num_specimens > 0, "require positive number of specimens")
        validate(
            self.start_date <= self.end_date, "require non-negative survey date range"
        )
