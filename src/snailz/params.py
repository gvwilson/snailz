"""Entire data generation scenario."""

from datetime import date
from pydantic import BaseModel, Field


DEFAULT_LOCALE = "et_EE"
DEFAULT_START_DATE = date(2025, 4, 1)
DEFAULT_END_DATE = date(2025, 4, 30)


class AssayParams(BaseModel):
    """Parameters for assay generation."""

    plate_size: int = Field(default=4, gt=0, description="plate size")
    mean_control: float = Field(default=0.0, ge=0.0, description="mean control reading")
    mean_normal: float = Field(
        default=2.0, ge=0.0, description="mean normal specimen reading"
    )
    mean_mutant: float = Field(
        default=5.0, ge=0.0, description="mean mutant specimen reading"
    )
    reading_noise: float = Field(
        default=0.5, ge=0.0, description="standard deviation of plate reading noise"
    )
    image_noise: int = Field(
        default=32,
        ge=0,
        le=255,
        description="plate image noise (grayscale 0-255)",
    )
    max_delay: int = Field(default=7, description="delay in performing assay (days)")

    model_config = {"extra": "forbid"}


class SpecimenParams(BaseModel):
    """Parameters for specimen generation."""

    mass_mean: float = Field(default=10.0, gt=0, description="Mean mass")
    mass_sd: float = Field(
        default=1.0, gt=0, description="Relative standard deviation in mass"
    )
    genome_length: int = Field(default=20, gt=0, description="Length of genomes")
    mut_mass_scale: float = Field(
        default=2.0, description="Scaling for mutant snail mass"
    )
    mut_frac: float = Field(
        default=0.2, ge=0.0, le=1.0, description="Fraction of significant mutants"
    )
    mut_prob: float = Field(
        default=0.05, ge=0.0, le=1.0, description="Probability of point mutation"
    )
    start_date: date = Field(
        default=DEFAULT_START_DATE, description="sampling start date"
    )
    end_date: date = Field(default=DEFAULT_END_DATE, description="sampling end date")

    model_config = {"extra": "forbid"}


class ScenarioParams(BaseModel):
    """Parameters for entire scenario."""

    rng_seed: int = Field(description="random number generation seed")
    grid_size: int = Field(default=15, gt=0, description="sample grid size")
    num_sites: int = Field(default=3, gt=0, description="number of sample sites")
    num_specimens: int = Field(
        default=10, gt=0, description="total number of specimens"
    )
    num_machines: int = Field(default=5, gt=0, description="number of lab machines")
    num_persons: int = Field(default=5, gt=0, description="number of lab staff")
    locale: str = Field(default=DEFAULT_LOCALE, description="name generation locale")
    assays_per_specimen: int = Field(default=2, gt=0, description="assays per specimen")
    pollution_scale: float = Field(
        default=0.1, ge=0, description="pollution scaling factor"
    )
    delay_scale: float = Field(default=0.05, ge=0, description="delay scaling factor")
    specimen_params: SpecimenParams = Field(
        description="specimen generation parameters"
    )
    assay_params: AssayParams = Field(description="assay generation parameters")

    model_config = {"extra": "forbid"}
