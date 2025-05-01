# Snailz Tests

This directory contains tests for the Snailz simulation framework using pytest.

## Running Tests

To run all tests:

```bash
uv run python -m pytest t2
```

To run tests with verbose output:

```bash
uv run python -m pytest t2 -v
```

To run a specific test file:

```bash
uv run python -m pytest t2/test_grid.py
```

## Test Coverage

The tests cover the core functionality of the Snailz package:

- **test_grid.py**: Tests for the Grid class, including creation, access, and CSV export
- **test_utils.py**: Tests for utility functions like ID generation, JSON serialization, and value finding
- **test_params.py**: Tests for parameter classes that control simulation behavior
- **test_specimens.py**: Tests for specimen generation and mutation handling
- **test_effects.py**: Tests for environmental effects on specimens
- **test_assays.py**: Tests for assay creation and data export

These tests verify the basic functionality of the simulation framework without modifying any existing code in the project.