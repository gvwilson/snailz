"""Test assay generation."""

import csv
import io
import pytest
import random
from datetime import date

from snailz import assays_generate, specimens_generate, people_generate
from snailz.assays import Assay, AllAssays, AssayParams
from snailz.defaults import (
    DEFAULT_ASSAY_PARAMS,
    DEFAULT_SPECIMEN_PARAMS,
    DEFAULT_PEOPLE_PARAMS,
)
from snailz.specimens import BASES, AllSpecimens, Specimen, Point

from utils import check_params_stored


@pytest.mark.parametrize(
    "name, value",
    [
        ("baseline", 0),
        ("baseline", -1.5),
        ("mutant", 0),
        ("mutant", -2.0),
        ("noise", 0),
        ("noise", -0.1),
        ("plate_size", 0),
        ("plate_size", -3),
    ],
)
def test_assays_fail_bad_parameter_value(name, value):
    """Test assay generation fails with invalid parameter values."""
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValueError):
        AssayParams(**params_dict)


def test_assays_fail_date_order():
    """Test assay generation fails when end date is before start date."""
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict["start_date"] = date.fromisoformat("2025-01-01")
    params_dict["end_date"] = date.fromisoformat("2024-01-01")
    with pytest.raises(ValueError):
        AssayParams(**params_dict)


def test_assays_fail_missing_parameter():
    """Test assay generation fails with missing parameters."""
    for key in DEFAULT_ASSAY_PARAMS.model_dump().keys():
        params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
        del params_dict[key]
        with pytest.raises(ValueError):
            AssayParams(**params_dict)


def test_assays_fail_extra_parameter():
    """Test assay generation fails with extra parameters."""
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict["extra"] = 1.0
    with pytest.raises(ValueError):
        AssayParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124])
def test_assays_valid_result(seed):
    """Test that assay generation returns the expected structure."""
    random.seed(seed)

    # Prepare parameters
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict["seed"] = seed
    params = AssayParams(**params_dict)

    # Generate specimens and people for assays
    specimens = specimens_generate(DEFAULT_SPECIMEN_PARAMS)
    people = people_generate(DEFAULT_PEOPLE_PARAMS)

    # Generate assays
    result = assays_generate(params, specimens, people)
    check_params_stored(params, result)

    # Check result has correct structure
    assert hasattr(result, "items")
    assert isinstance(result.items, list)

    # Check number of assays matches number of specimens
    assert len(result.items) == len(specimens.individuals)

    # Check each assay
    for assay in result.items:
        # Check date is within range
        assert params.start_date <= assay.performed <= params.end_date

        # Check identifier format
        assert len(assay.ident) == len(result.items[0].ident)
        assert assay.ident.isdigit()

        # Check plate structure
        assert len(assay.treatments) == params.plate_size
        assert len(assay.readings) == params.plate_size
        for row in range(params.plate_size):
            assert len(assay.treatments[row]) == params.plate_size
            assert len(assay.readings[row]) == params.plate_size
            for treatment in assay.treatments[row]:
                assert treatment in ["S", "C"]


def test_assay_reading_values():
    """Test that assay readings follow the specified distributions."""
    random.seed(DEFAULT_ASSAY_PARAMS.seed)

    # Prepare parameters with controlled values for easier testing
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict["baseline"] = 5.0
    params_dict["mutant"] = 20.0
    params_dict["noise"] = 1.0
    params = AssayParams(**params_dict)

    # Create a controlled specimen with known susceptibility
    susc_locus = 3
    reference = "ACGTACGTACGTACG"
    susc_base = reference[susc_locus]

    # Create two specimens: one susceptible, one not
    susceptible_individual = Specimen(
        genome=reference,  # Has the susceptible base at the susceptible locus
        ident="AB1234",
        mass=1.0,
        site=Point(),
    )

    # Modify a copy of the reference genome to not have the susceptible base
    non_susceptible_genome = list(reference)
    non_susceptible_genome[susc_locus] = next(b for b in BASES if b != susc_base)
    non_susceptible_individual = Specimen(
        genome="".join(non_susceptible_genome), ident="AB5678", mass=1.0, site=Point()
    )

    specimens = AllSpecimens(
        individuals=[susceptible_individual, non_susceptible_individual],
        loci=[susc_locus],
        params=DEFAULT_SPECIMEN_PARAMS,
        reference=reference,
        susceptible_base=susc_base,
        susceptible_locus=susc_locus,
    )

    # Create mock people data
    people = people_generate(DEFAULT_PEOPLE_PARAMS)

    # Generate assays with fixed random seed for reproducibility
    result = assays_generate(params, specimens, people)

    # Test reading values for susceptible specimen
    susceptible_assay = result.items[0]
    for row in range(params.plate_size):
        for col in range(params.plate_size):
            if susceptible_assay.treatments[row][col] == "C":
                # Control cells should have values between 0 and noise
                assert 0 <= susceptible_assay.readings[row][col] <= params.noise
            else:
                # Susceptible cells should have mutant value plus scaled noise
                reading = susceptible_assay.readings[row][col]
                scaled_noise = params.noise * params.mutant / params.baseline
                assert params.mutant <= reading <= params.mutant + scaled_noise

    # Test reading values for non-susceptible specimen
    non_susceptible_assay = result.items[1]
    for row in range(params.plate_size):
        for col in range(params.plate_size):
            if non_susceptible_assay.treatments[row][col] == "C":
                # Control cells should have values between 0 and noise
                assert 0 <= non_susceptible_assay.readings[row][col] <= params.noise
            else:
                # Non-susceptible cells should have baseline value plus noise
                reading = non_susceptible_assay.readings[row][col]
                assert params.baseline <= reading <= params.baseline + params.noise


def test_assay_date_handling():
    """Test that Assay model can handle date strings and date objects."""
    # Create Assay with date object
    date_obj = date(2023, 1, 1)
    assay1 = Assay(
        performed=date_obj,
        ident="123456",
        specimen_id="abc123",
        person_id="xyz789",
        readings=[[1.0, 2.0], [3.0, 4.0]],
        treatments=[["S", "C"], ["C", "S"]],
    )

    # Create the same Assay with date string
    assay2 = Assay(
        performed="2023-01-01",  # String date should be automatically converted
        ident="123456",
        specimen_id="abc123",
        person_id="xyz789",
        readings=[[1.0, 2.0], [3.0, 4.0]],
        treatments=[["S", "C"], ["C", "S"]],
    )

    # Both should have identical date objects
    assert isinstance(assay1.performed, date)
    assert isinstance(assay2.performed, date)
    assert assay1.performed == assay2.performed == date_obj


@pytest.fixture
def sample_assay():
    """Create a sample assay for testing CSV output."""
    return Assay(
        performed=date(2023, 1, 15),
        ident="123456",
        specimen_id="AB1234",
        person_id="ab0123",
        readings=[
            [1.5, 2.5, 3.5],
            [4.5, 5.5, 6.5],
            [7.5, 8.5, 9.5],
        ],
        treatments=[
            ["S", "C", "S"],
            ["C", "S", "C"],
            ["S", "C", "S"],
        ],
    )


@pytest.fixture
def sample_assays(sample_assay):
    """Create a sample Assays instance with multiple assays."""
    # Create a second assay with different values
    second_assay = Assay(
        performed=date(2023, 2, 20),
        ident="789012",
        specimen_id="AB5678",
        person_id="cd4567",
        readings=[
            [0.5, 1.0, 1.5],
            [2.0, 2.5, 3.0],
            [3.5, 4.0, 4.5],
        ],
        treatments=[
            ["C", "S", "C"],
            ["S", "C", "S"],
            ["C", "S", "C"],
        ],
    )

    # Create a valid AssayParams object
    from snailz.assays import AssayParams

    params = AssayParams(
        baseline=1.0,
        end_date=date(2023, 12, 31),
        mutant=10.0,
        noise=0.1,
        plate_size=3,
        seed=12345,
        start_date=date(2023, 1, 1),
    )

    return AllAssays(
        items=[sample_assay, second_assay],
        params=params,
    )


def test_assays_to_csv(sample_assays):
    """Test assays to_csv method creates CSV representation."""
    # Get the CSV content
    csv_content = sample_assays.to_csv()

    # Parse the CSV output
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check header
    assert rows[0] == ["ident", "specimen_id", "performed", "performed_by"]

    # Check we have the right number of rows (header + 2 assays)
    assert len(rows) == 3

    # Check first assay data
    assert rows[1][0] == sample_assays.items[0].ident
    assert rows[1][1] == sample_assays.items[0].specimen_id
    assert rows[1][2] == sample_assays.items[0].performed.isoformat()
    assert rows[1][3] == sample_assays.items[0].person_id

    # Check second assay data
    assert rows[2][0] == sample_assays.items[1].ident
    assert rows[2][1] == sample_assays.items[1].specimen_id
    assert rows[2][2] == sample_assays.items[1].performed.isoformat()
    assert rows[2][3] == sample_assays.items[1].person_id


def test_assay_to_csv_readings(sample_assay):
    """Test individual assay to_csv method creates CSV representation for readings."""
    # Get the CSV content for readings
    csv_content = sample_assay.to_csv(data_type="readings")

    # Parse the CSV output
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check metadata
    assert rows[0][:2] == ["id", sample_assay.ident]
    assert rows[1][:2] == ["specimen", sample_assay.specimen_id]
    assert rows[2][:2] == ["performed", sample_assay.performed.isoformat()]
    assert rows[3][:2] == ["performed_by", sample_assay.person_id]

    # Check column headers
    assert rows[4][:4] == ["", "A", "B", "C"]

    # Check data rows
    for i, row in enumerate(
        sample_assay.readings, 5
    ):  # 5 is the starting row index after headers
        assert float(rows[i][1]) == row[0]
        assert float(rows[i][2]) == row[1]
        assert float(rows[i][3]) == row[2]


def test_assay_to_csv_treatments(sample_assay):
    """Test individual assay to_csv method creates CSV representation for treatments."""
    # Get the CSV content for treatments
    csv_content = sample_assay.to_csv(data_type="treatments")

    # Parse the CSV output
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check metadata
    assert rows[0][:2] == ["id", sample_assay.ident]
    assert rows[1][:2] == ["specimen", sample_assay.specimen_id]
    assert rows[2][:2] == ["performed", sample_assay.performed.isoformat()]
    assert rows[3][:2] == ["performed_by", sample_assay.person_id]

    # Check column headers
    assert rows[4][:4] == ["", "A", "B", "C"]

    # Check data rows
    for i, row in enumerate(
        sample_assay.treatments, 5
    ):  # 5 is the starting row index after headers
        assert rows[i][1] == row[0]
        assert rows[i][2] == row[1]
        assert rows[i][3] == row[2]


def test_assay_to_csv_invalid_data_type(sample_assay):
    """Test to_csv raises error for invalid data type."""
    with pytest.raises(
        ValueError, match="data_type must be 'readings' or 'treatments'"
    ):
        sample_assay.to_csv(data_type="invalid")
