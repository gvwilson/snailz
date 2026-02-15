"""Data generation parameters."""

from dataclasses import dataclass
from datetime import date
from faker.config import AVAILABLE_LOCALES
import json
from typing import Any

from ._utils import validate, validate_lat_lon


# Indentation for JSON output.
JSON_INDENT = 2


@dataclass
class Parameters:
    """
    Store all data generation parameters.
    """

    seed: int = 12345
    """Random number generator seed for reproducible data generation."""

    num_grids: int = 1
    """Number of survey grids to create."""

    grid_size: int = 1
    """Width and height of each survey grid in cells."""

    grid_spacing: float = 10.0
    """Size of each grid cell in meters."""

    grid_separation: int = 4
    """Minimum separation between grid origin points as multiple of total grid size."""

    grid_std_dev: float = 0.5
    """Standard deviation of noise applied to grid pollution values."""

    lat0: float = 48.8666632
    """Reference latitude for all grids."""

    lon0: float = -124.1999992
    """Reference longitude for all grids."""

    num_persons: int = 1
    """Number of persons to generate."""

    supervisor_frac: float = 0.3
    """Fraction of persons who are supervisors of other persons."""

    locale: str = "et_EE"
    """Locale for generating personal and family names of persons."""

    num_machines: int = 1
    """Number of machines to generate."""

    ratings_frac: float = 0.5
    """Fraction of (person, machine) pairs to be given ratings."""

    p_certified: float = 0.3
    """Probability that a particular person is certified for a particular machine."""

    num_assays: int = 1
    """Number of soil pollution assays to generate."""

    assay_size: int = 2
    """Number of control or treatment values to include in each assay."""

    assay_certified: float = 3.0
    """How much to narrow standard deviation in assay pollution if operator is certified."""

    genome_length: int = 1
    """Length of species genome in bases."""

    num_loci: int = 1
    """Number of loci in genome at which mutations may occur."""

    p_mutation: float = 0.5
    """Probability of mutation at each locus."""

    num_specimens: int = 1
    """Number of snail specimens to create."""

    p_variety_missing: float = 0.1
    """Probability that specimen variety is missing."""

    mass_beta_0: float = 3.0
    """Fixed mean for log-normal snail mass generation."""

    mass_beta_1: float = 0.5
    """Scaling factor for pollution in mean of log-normal snail mass generation."""

    mass_sigma: float = 0.3
    """Standard deviation in log-normal generation of snail mass."""

    diam_ratio: float = 0.7
    """Mean of ratio of snail diameter to mass."""

    diam_sigma: float = 0.7
    """Standard deviation in snail diameter generation."""

    start_date: date = date(2026, 3, 1)
    """Start date of survey."""

    end_date: date = date(2026, 5, 31)
    """End date of survey."""

    p_date_missing: float = 0.1
    """Probability that specimen collection date is missing."""

    def __post_init__(self):
        """Validate fields."""

        if isinstance(self.start_date, str):
            self.start_date = date.fromisoformat(self.start_date)
        if isinstance(self.end_date, str):
            self.end_date = date.fromisoformat(self.end_date)

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
            0.0 <= self.p_variety_missing <= 1.0, "require missing variety probability in [0..1]"
        )
        validate(
            self.start_date <= self.end_date, "require non-negative survey date range"
        )
        validate(
            0.0 <= self.p_date_missing <= 1.0, "require missing date probability in [0..1]"
        )

    def as_json(self, indent: int = JSON_INDENT) -> str:
        """
        Convert parameters to a JSON string.

        Args:
            indent: Indentation.

        Returns:
            JSON string representation of persistable fields.
        """
        return json.dumps(self.__dict__, indent=indent, default=_serialize_json)


def _serialize_json(obj: Any) -> str:
    """
    Custom JSON serializer.

    Args:
        obj: What to persist.

    Returns:
        String representation of object.
    """

    assert isinstance(obj, date)
    return obj.isoformat()
