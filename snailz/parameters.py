"""Data generation parameters."""

from datetime import date

from faker.config import AVAILABLE_LOCALES
from pydantic import BaseModel, Field, model_validator


class Parameters(BaseModel):
    """Store all data generation parameters."""

    seed: int = Field(default=123456, description="RNG seed", gt=0)
    precision: int = Field(default=2, gt=0, description="floating point digits")
    num_persons: int = Field(default=5, description="number of persons")
    num_grids: int = Field(default=3, gt=0, description="number of sample grids")
    num_samples: int = Field(default=20, gt=0, description="number of samples")
    locale: str = Field(default="et_EE", description="name generation locale")
    grid_size: int = Field(default=11, gt=0, description="sample grid size")
    sample_mass_min: float = Field(
        default=0.5, gt=0, description="minimum sample sample mass"
    )
    sample_mass_max: float = Field(
        default=1.5, gt=0, description="maximum sample sample mass"
    )
    sample_date_min: date = Field(
        default=date(2025, 1, 1), description="sampling start date"
    )
    sample_date_max: date = Field(
        default=date(2025, 3, 31), description="sampling end date"
    )
    pollution_factor: float = Field(
        default=0.3, gt=0, description="pollution effect on mass"
    )
    clumsy_factor: float = Field(
        default=0.5, gt=0, description="clumsy operator effect on mass"
    )

    @model_validator(mode="after")
    def validate_locale(self):
        """Check locale."""

        if self.locale not in AVAILABLE_LOCALES:
            raise ValueError(f"unknown locale {self.locale}")
        return self

    @model_validator(mode="after")
    def validate_sample_mass(self):
        """Check sample mass."""
        if self.sample_mass_max < self.sample_mass_min:
            raise ValueError(
                f"invalid sample size limits [{self.sample_mass_min}, {self.sample_mass_max}]"
            )
        return self

    @model_validator(mode="after")
    def validate_sample_date(self):
        """Check sample dates."""
        if self.sample_date_max < self.sample_date_min:
            raise ValueError(
                f"invalid sample date limits [{self.sample_date_min}, {self.sample_date_max}]"
            )
        return self
