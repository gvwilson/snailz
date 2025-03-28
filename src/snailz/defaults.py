"""Default parameter values."""

from datetime import date

from .assays import AssayParams
from .grid import GridParams
from .people import PeopleParams
from .specimens import SpecimenParams


DEFAULT_ASSAY_PARAMS = AssayParams(
    baseline=1.0,
    end_date=date.fromisoformat("2023-02-15"),
    mutant=10.0,
    noise=0.1,
    plate_size=4,
    seed=7421398,
    start_date=date.fromisoformat("2023-01-10"),
)

DEFAULT_GRID_PARAMS = GridParams(
    depth=8,
    seed=7421398,
    size=15,
)

DEFAULT_PEOPLE_PARAMS = PeopleParams(
    locale="et_EE",
    number=5,
    seed=12772301,
)

DEFAULT_SPECIMEN_PARAMS = SpecimenParams(
    length=15,
    max_mass=33.0,
    min_mass=15.0,
    mut_scale=0.5,
    mutations=3,
    number=20,
    seed=4712389,
)
