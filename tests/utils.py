"""Test utilities."""


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
