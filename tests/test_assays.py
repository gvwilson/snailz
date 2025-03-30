"""Test assay generation."""

import csv
import io
import pytest
import random
from datetime import date, timedelta
from unittest.mock import patch

from snailz import assays_generate, specimens_generate, people_generate
from snailz.assays import Assay, AllAssays, AssayParams
from snailz.defaults import (
    DEFAULT_ASSAY_PARAMS,
    DEFAULT_SPECIMEN_PARAMS,
    DEFAULT_PEOPLE_PARAMS,
)
from snailz.specimens import BASES, AllSpecimens, Specimen, Point

from utils import check_params_stored


@pytest.fixture
def people():
    """Default set of people."""
    return people_generate(DEFAULT_PEOPLE_PARAMS)


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

    params = AssayParams(
        baseline=1.0,
        delay=14,
        degrade=0.05,
        mutant=10.0,
        noise=0.1,
        oops=0.0,
        plate_size=3,
        seed=12345,
    )

    return AllAssays(
        items=[sample_assay, second_assay],
        params=params,
    )


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
        ("delay", 0),
        ("degrade", -0.2),
        ("degrade", 1.2),
        ("oops", -0.1),
        ("extra", 99),
    ],
)
def test_assays_fail_bad_parameter_value(name, value):
    """Test assay generation fails with invalid parameter values."""
    params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValueError):
        AssayParams(**params_dict)


def test_assays_fail_missing_parameter():
    """Test assay generation fails with missing parameters."""
    for key in DEFAULT_ASSAY_PARAMS.model_dump().keys():
        params_dict = DEFAULT_ASSAY_PARAMS.model_dump()
        del params_dict[key]
        with pytest.raises(ValueError):
            AssayParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124])
def test_assays_valid_result(seed, people):
    """Test that assay generation returns the expected structure."""
    random.seed(seed)
    params = DEFAULT_ASSAY_PARAMS.model_copy(update={"seed": seed})
    # Ensure DEFAULT_SPECIMEN_PARAMS is used with start_date and end_date already set
    specimens = specimens_generate(DEFAULT_SPECIMEN_PARAMS)
    # Verify that all specimens have a collected_on date
    assert all(spec.collected_on is not None for spec in specimens.individuals)
    result = assays_generate(params, people, specimens)
    check_params_stored(params, result)

    assert len(result.items) == len(specimens.individuals)
    for i, assay in enumerate(result.items):
        specimen = specimens.individuals[i]
        # Check that assay date is between collection date and collection date + delay days
        assert (
            specimen.collected_on
            <= assay.performed
            <= specimen.collected_on + timedelta(days=params.delay)
        )
        assert len(assay.ident) == len(result.items[0].ident)
        assert assay.ident.isdigit()
        assert len(assay.treatments) == params.plate_size
        assert len(assay.readings) == params.plate_size
        for row in range(params.plate_size):
            assert len(assay.treatments[row]) == params.plate_size
            assert len(assay.readings[row]) == params.plate_size
            for treatment in assay.treatments[row]:
                assert treatment in ["S", "C"]


def test_assay_reading_values(people):
    """Test that assay readings follow the specified distributions."""
    random.seed(DEFAULT_ASSAY_PARAMS.seed)
    params = DEFAULT_ASSAY_PARAMS.model_copy(
        update={
            "baseline": 5.0,
            "mutant": 20.0,
            "noise": 1.0,
            "degrade": 0.1,
            "oops": 0.0,
        }
    )
    susc_locus = 3
    reference = "ACGTACGTACGTACG"
    susc_base = reference[susc_locus]

    # Create two specimens: one susceptible, one not
    susceptible_individual = Specimen(
        genome=reference,  # Has the susceptible base at the susceptible locus
        ident="AB1234",
        mass=1.0,
        site=Point(),
        collected_on=date(2025, 3, 10),
    )

    # Modify a copy of the reference genome to not have the susceptible base
    non_susceptible_genome = list(reference)
    non_susceptible_genome[susc_locus] = next(b for b in BASES if b != susc_base)
    non_susceptible_individual = Specimen(
        genome="".join(non_susceptible_genome),
        ident="AB5678",
        mass=1.0,
        site=Point(),
        collected_on=date(2025, 3, 15),
    )

    specimens = AllSpecimens(
        individuals=[susceptible_individual, non_susceptible_individual],
        loci=[susc_locus],
        params=DEFAULT_SPECIMEN_PARAMS,
        reference=reference,
        susceptible_base=susc_base,
        susceptible_locus=susc_locus,
    )

    result = assays_generate(params, people, specimens)

    # Test reading values for susceptible specimen
    susceptible_assay = result.items[0]

    # Calculate days since collection and expected degradation factor
    days_since_collection = (
        susceptible_assay.performed - susceptible_individual.collected_on
    ).days
    degradation_days = max(0, days_since_collection - 1)  # No degradation on day 1
    degradation_factor = 1.0 - (params.degrade * degradation_days)
    degradation_factor = max(0.0, degradation_factor)

    expected_mutant_value = params.mutant * degradation_factor

    for row in range(params.plate_size):
        for col in range(params.plate_size):
            if susceptible_assay.treatments[row][col] == "C":
                # Control cells should have values between 0 and noise
                assert 0 <= susceptible_assay.readings[row][col] <= params.noise
            else:
                # Susceptible cells should have degraded mutant value plus scaled noise
                reading = susceptible_assay.readings[row][col]
                scaled_noise = params.noise * params.mutant / params.baseline
                assert (
                    expected_mutant_value
                    <= reading
                    <= expected_mutant_value + scaled_noise
                )

    # Test reading values for non-susceptible specimen
    non_susceptible_assay = result.items[1]

    # Calculate days since collection and expected degradation factor
    days_since_collection = (
        non_susceptible_assay.performed - non_susceptible_individual.collected_on
    ).days
    degradation_days = max(0, days_since_collection - 1)  # No degradation on day 1
    degradation_factor = 1.0 - (params.degrade * degradation_days)
    degradation_factor = max(0.0, degradation_factor)

    expected_baseline_value = params.baseline * degradation_factor

    for row in range(params.plate_size):
        for col in range(params.plate_size):
            if non_susceptible_assay.treatments[row][col] == "C":
                # Control cells should have values between 0 and noise
                assert 0 <= non_susceptible_assay.readings[row][col] <= params.noise
            else:
                # Non-susceptible cells should have degraded baseline value plus noise
                reading = non_susceptible_assay.readings[row][col]
                assert (
                    expected_baseline_value
                    <= reading
                    <= expected_baseline_value + params.noise
                )


def test_assay_to_csv_readings(sample_assay):
    """Test individual assay to_csv method creates CSV representation for readings."""
    csv_content = sample_assay.to_csv(data_type="readings")
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
    csv_content = sample_assay.to_csv(data_type="treatments")
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
    with pytest.raises(ValueError):
        sample_assay.to_csv(data_type="invalid")


def test_assay_degradation(people):
    """Test that sample responses decrease with time since collection."""
    random.seed(1234)
    # Set a high degradation rate to clearly see the effect
    params = AssayParams(
        baseline=5.0,
        delay=14,
        degrade=0.2,  # 20% reduction per day after first day
        mutant=20.0,
        noise=0.1,
        oops=0.0,
        plate_size=3,
        seed=1234,
    )

    # Create specimen with fixed collection date
    collection_date = date(2025, 3, 1)
    specimen = Specimen(
        genome="ACGT",
        ident="TEST01",
        mass=1.0,
        site=Point(),
        collected_on=collection_date,
    )

    specimens_obj = AllSpecimens(
        individuals=[specimen],
        loci=[0],
        params=DEFAULT_SPECIMEN_PARAMS,
        reference="ACGT",
        susceptible_base="A",
        susceptible_locus=0,
    )

    # Force the assay performed date - 1 day after collection (no degradation)
    with patch("random.randint", return_value=1):
        result_day1 = assays_generate(params, people, specimens_obj)

    # 5 days after collection (4 days of degradation at 20% per day)
    with patch("random.randint", return_value=5):
        result_day5 = assays_generate(params, people, specimens_obj)

    # 10 days after collection (9 days of degradation at 20% per day)
    with patch("random.randint", return_value=10):
        result_day10 = assays_generate(params, people, specimens_obj)

    # Find sample (non-control) readings from each assay
    day1_samples = []
    day5_samples = []
    day10_samples = []

    for row in range(params.plate_size):
        for col in range(params.plate_size):
            if result_day1.items[0].treatments[row][col] == "S":
                day1_samples.append(result_day1.items[0].readings[row][col])
            if result_day5.items[0].treatments[row][col] == "S":
                day5_samples.append(result_day5.items[0].readings[row][col])
            if result_day10.items[0].treatments[row][col] == "S":
                day10_samples.append(result_day10.items[0].readings[row][col])

    # Check that readings decrease with time
    assert sum(day1_samples) > sum(day5_samples) > sum(day10_samples)

    # Calculate expected degradation factors
    day1_factor = 1.0  # No degradation on day 1
    day5_factor = 1.0 - (params.degrade * 4)  # 4 days of degradation
    day10_factor = 1.0 - (
        params.degrade * 9
    )  # 9 days of degradation (might be 0 if fully degraded)
    day10_factor = max(0.0, day10_factor)  # Ensure it's not negative

    # Verify the average readings follow expected degradation pattern
    # Allow some tolerance for random noise
    avg_day1 = sum(day1_samples) / len(day1_samples)
    avg_day5 = sum(day5_samples) / len(day5_samples)

    # Expected ratio of day 5 to day 1 should be approximately the degradation factor
    expected_ratio = day5_factor / day1_factor
    actual_ratio = avg_day5 / avg_day1

    # Allow for some tolerance due to random noise
    assert abs(actual_ratio - expected_ratio) < 0.2


def test_assay_oops_factor(people):
    """Test that oops factor correctly affects assay values for one random person."""
    random.seed(1234)

    # Create test parameters with oops factor
    params = AssayParams(
        baseline=5.0,
        delay=1,
        degrade=0.0,  # No degradation to simplify testing
        mutant=20.0,
        noise=0.1,
        oops=0.5,  # 50% increase in values
        plate_size=3,
        seed=1234,
    )

    # Create a few specimens
    specimens = []
    for i in range(3):
        specimens.append(
            Specimen(
                genome="ACGT",
                ident=f"TEST{i:02d}",
                mass=1.0,
                site=Point(),
                collected_on=date(2025, 3, 1),
            )
        )

    specimens_obj = AllSpecimens(
        individuals=specimens,
        loci=[0],
        params=DEFAULT_SPECIMEN_PARAMS,
        reference="ACGT",
        susceptible_base="A",
        susceptible_locus=0,
    )

    # Generate assays with oops factor
    with patch(
        "random.choice", side_effect=lambda x: x[0]
    ):  # Force first person to be selected for both oops and assay assignment
        result_with_oops = assays_generate(params, people, specimens_obj)

    # Generate assays without oops factor for comparison
    params_no_oops = params.model_copy(update={"oops": 0.0})
    with patch(
        "random.choice", side_effect=lambda x: x[0]
    ):  # Keep consistent person assignment
        result_without_oops = assays_generate(params_no_oops, people, specimens_obj)

    # Check that all assays are performed by the same person (the first one)
    first_person_id = people.individuals[0].ident
    for assay in result_with_oops.items:
        assert assay.person_id == first_person_id

    # Check that assay values are increased by the oops factor for non-control cells
    for i, assay in enumerate(result_with_oops.items):
        for row in range(params.plate_size):
            for col in range(params.plate_size):
                if (
                    assay.treatments[row][col] == "S"
                ):  # Only check sample cells, not controls
                    with_oops = assay.readings[row][col]
                    without_oops = result_without_oops.items[i].readings[row][col]
                    # The value with oops should be approximately (1 + oops) times the value without oops
                    # Using a larger tolerance due to randomness in the test
                    assert abs(with_oops / without_oops - (1 + params.oops)) < 0.05
                else:  # Control cells
                    # Control cells should be the same regardless of oops factor
                    with_oops = assay.readings[row][col]
                    without_oops = result_without_oops.items[i].readings[row][col]
                    assert with_oops == without_oops

    # Generate assays with different random person assignments
    # Some assays should be affected by oops, others not
    random.seed(5678)  # Different seed to get varied person assignments
    params_mixed = params.model_copy(update={"seed": 5678})
    mixed_result = assays_generate(params_mixed, people, specimens_obj)

    # Check if at least one assay has a different person than the oops person
    oops_person_id = None
    non_oops_person_found = False

    # Find the oops person's ID (it will be set in the first few assays)
    for assay in mixed_result.items:
        if oops_person_id is None:
            for row in range(params.plate_size):
                for col in range(params.plate_size):
                    if assay.treatments[row][col] == "S":
                        # Find a non-control cell and compare it with a baseline
                        # If it's significantly higher than baseline * (1 + noise ratio), it's the oops person
                        reading = assay.readings[row][col]
                        baseline = (
                            params.baseline + params.noise
                        )  # Max possible baseline reading
                        if reading > baseline * 1.2:  # Adding a margin for noise
                            oops_person_id = assay.person_id
                            break
                if oops_person_id is not None:
                    break
        else:
            # We found the oops person, now check if we have non-oops persons
            if assay.person_id != oops_person_id:
                non_oops_person_found = True
                break

    # Ensure we identified an oops person and found at least one non-oops person
    assert oops_person_id is not None
    assert non_oops_person_found


def test_assays_to_csv(sample_assays):
    """Test assays to_csv method creates CSV representation."""
    csv_content = sample_assays.to_csv()
    rows = list(csv.reader(io.StringIO(csv_content)))

    assert rows[0] == ["ident", "specimen_id", "performed", "performed_by"]
    assert len(rows) == 3

    assert rows[1][0] == sample_assays.items[0].ident
    assert rows[1][1] == sample_assays.items[0].specimen_id
    assert rows[1][2] == sample_assays.items[0].performed.isoformat()
    assert rows[1][3] == sample_assays.items[0].person_id

    assert rows[2][0] == sample_assays.items[1].ident
    assert rows[2][1] == sample_assays.items[1].specimen_id
    assert rows[2][2] == sample_assays.items[1].performed.isoformat()
    assert rows[2][3] == sample_assays.items[1].person_id
