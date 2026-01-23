"""Data generation parameters."""

from datetime import date
from faker.config import AVAILABLE_LOCALES
from pydantic import BaseModel, Field, model_validator


class Parameters(BaseModel):
    """Store all data generation parameters."""

    seed: int = Field(default=123456, description="RNG seed", gt=0)
    precision: int = Field(default=1, gt=0, description="floating point digits")
    num_persons: int = Field(default=6, description="number of persons")
    num_grids: int = Field(default=3, gt=0, description="number of sample grids")
    num_samples: int = Field(default=20, gt=0, description="number of samples")
    locale: str = Field(default="et_EE", description="name generation locale")
    grid_size: int = Field(default=11, gt=0, description="sample grid size")
    grid_spacing: float = Field(default=20.0, gt=0, description="grid cell spacing (m)")
    grid_gap: float = Field(default=1000.0, gt=0, description="gap between grids")
    lat0: float = Field(
        default=48.8666632, ge=-90.0, le=90.0, description="grid reference latitude"
    )
    lon0: float = Field(
        default=-124.1999992,
        ge=-180.0,
        le=180.0,
        description="grid reference longitude",
    )
    sample_size: tuple[float, float] = Field(
        default=(50, 10), description="sample mass mean and stdev"
    )
    sample_date: tuple[date, date] = Field(
        default=(date(2025, 1, 1), date(2025, 3, 31)),
        description="sampling date bounds",
    )
    pollution_factor: float = Field(
        default=0.3, gt=0, description="pollution effect on sample size"
    )
    clumsy_factor: float | None = Field(
        default=0.5, description="clumsy operator effect on mass (if any)"
    )
    num_machines: int = Field(default=5, gt=0, description="number of machines")

    @model_validator(mode="after")
    def validate_clumsy_factor(self):
        """Check clumsiness factor."""

        if self.clumsy_factor is None:
            pass
        elif self.clumsy_factor > 0:
            pass
        else:
            raise ValueError(f"bad clumsy factor {self.clumsy_factor}")
        return self

    @model_validator(mode="after")
    def validate_locale(self):
        """Check locale."""

        if self.locale not in AVAILABLE_LOCALES:
            raise ValueError(f"unknown locale {self.locale}")
        return self

    @model_validator(mode="after")
    def validate_sample_date(self):
        """Check sample dates."""

        if self.sample_date[1] < self.sample_date[0]:
            raise ValueError(f"invalid sample date bounds {self.sample_date}")
        return self
