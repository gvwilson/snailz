"""Test utilities."""

from datetime import date

from snailz.assays import AssayParams
from snailz.grid import GridParams
from snailz.people import PeopleParams
from snailz.specimens import SpecimenParams

# Create Pydantic parameter objects instead of dictionaries
ASSAY_PARAMS = AssayParams(
    baseline=1.0,
    end_date=date.fromisoformat("2023-12-31"),
    mutant=10.0,
    noise=0.1,
    plate_size=4,
    seed=4712389,
    start_date=date.fromisoformat("2023-01-01"),
)

GRID_PARAMS = GridParams(
    depth=8,
    seed=7421398,
    size=15,
)

PEOPLE_PARAMS = PeopleParams(
    locale="et_EE",
    number=15,
    seed=9812374,
)

SPECIMEN_PARAMS = SpecimenParams(
    length=15,
    max_mass=33.0,
    min_mass=15.0,
    mut_scale=0.5,
    mutations=3,
    number=20,
    seed=4712389,
)


def check_params_stored(params, result):
    """Check that params are properly stored.

    Verifies that the Pydantic params object is correctly stored in the result.

    Args:
        params: A Pydantic params object (GridParams, PeopleParams, etc.)
        result: The result object containing a params field (Grid, People, etc.)
    """
    # Get all fields from the params object
    param_dict = params.model_dump()

    # Check that all attributes and values match
    for key, expected_value in param_dict.items():
        # Verify attribute exists
        assert hasattr(result.params, key), (
            f"Attribute '{key}' missing from result.params"
        )

        # Get the actual value from result.params
        actual_value = getattr(result.params, key)

        # Check values match
        assert actual_value == expected_value, (
            f"result.params.{key} is {actual_value} not {expected_value}"
        )
