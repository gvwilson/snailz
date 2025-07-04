"""Tests for main module."""

import json
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

from snailz.main import main, _parse_args, _initialize, _synthesize, _save
from snailz.parameters import Parameters


def test_parse_args_defaults():
    """Test argument parsing with default values."""

    with patch("sys.argv", ["snailz"]):
        args = _parse_args()
        assert args.defaults is False
        assert args.outdir is None
        assert args.params is None


def test_parse_args_with_options():
    """Test argument parsing with all options."""

    with patch(
        "sys.argv",
        ["snailz", "--defaults", "--outdir", "/tmp", "--params", "config.json"],
    ):
        args = _parse_args()
        assert args.defaults is True
        assert args.outdir == "/tmp"
        assert args.params == "config.json"


def test_initialize_with_defaults():
    """Test initialization with default parameters."""

    args = MagicMock()
    args.params = None
    with patch("random.seed") as mock_seed:
        params = _initialize(args)
        assert isinstance(params, Parameters)
        mock_seed.assert_called_once_with(params.seed)


def test_initialize_with_params_file():
    """Test initialization with parameters file."""

    args = MagicMock()
    args.params = "test_params.json"
    test_params = {"seed": 42, "num_persons": 10, "locale": "en_US"}
    mock_file = mock_open(read_data=json.dumps(test_params))
    with patch("builtins.open", mock_file), patch("random.seed") as mock_seed:
        params = _initialize(args)
        assert params.seed == 42
        assert params.num_persons == 10
        assert params.locale == "en_US"
        mock_seed.assert_called_once_with(42)


def test_synthesize_data():
    """Test data synthesis function."""

    params = Parameters(num_grids=2, num_persons=3, num_samples=5)
    grids, persons, samples = _synthesize(params)

    assert len(grids) == 2
    assert len(persons) == 3
    assert len(samples) == 5

    assert all(g.id.startswith("G") for g in grids)
    assert all(p.id.startswith("P") for p in persons)
    assert all(s.id.startswith("S") for s in samples)


def test_save_to_stdout():
    """Test saving data to stdout."""

    args = MagicMock()
    args.outdir = "-"

    params = Parameters(num_grids=1, num_persons=1, num_samples=1)
    grids, persons, samples = _synthesize(params)
    changes = {"test": "data"}

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        _save(args, grids, persons, samples, changes)
        output = mock_stdout.getvalue().split("\n")
        assert len([ln for ln in output if ln.startswith("S")]) == 1
        assert len([ln for ln in output if ln.startswith("P")]) == 1


def test_save_to_directory(tmp_path):
    """Test saving data to directory."""

    args = MagicMock()
    args.outdir = str(tmp_path)

    params = Parameters(num_grids=1, num_persons=1, num_samples=1)
    grids, persons, samples = _synthesize(params)
    changes = {"test": "data"}

    _save(args, grids, persons, samples, changes)

    # Check that files were created
    assert (tmp_path / f"{grids[0].id}.csv").exists()
    assert (tmp_path / "persons.csv").exists()
    assert (tmp_path / "samples.csv").exists()
    assert (tmp_path / "changes.json").exists()

    # Verify content
    persons_content = (tmp_path / "persons.csv").read_text()
    assert "id,family,personal" in persons_content

    samples_content = (tmp_path / "samples.csv").read_text()
    assert "sample_id,grid_id,x,y,pollution,person,when,mass" in samples_content


def test_save_creates_directory(tmp_path):
    """Test that save creates output directory if it doesn"t exist."""

    new_dir = tmp_path / "new_output"
    args = MagicMock()
    args.outdir = str(new_dir)

    params = Parameters(num_grids=1, num_persons=1, num_samples=1)
    grids, persons, samples = _synthesize(params)
    changes = {}

    _save(args, grids, persons, samples, changes)

    assert new_dir.exists()
    assert new_dir.is_dir()


def test_main_with_defaults():
    """Test main function with --defaults flag."""

    with (
        patch("sys.argv", ["snailz", "--defaults"]),
        patch("sys.stdout", new_callable=StringIO) as mock_stdout,
    ):
        result = main()
        assert result == 0
        output = mock_stdout.getvalue()
        assert "seed" in output
        assert "123456" in output


def test_main_full_workflow(tmp_path):
    """Test complete main workflow."""

    test_params = {"seed": 42, "num_grids": 1, "num_persons": 2, "num_samples": 3}
    params_file = tmp_path / "params.json"
    params_file.write_text(json.dumps(test_params))

    output_dir = tmp_path / "output"

    with patch(
        "sys.argv",
        ["snailz", "--params", str(params_file), "--outdir", str(output_dir)],
    ):
        result = main()
        assert result == 0
        assert output_dir.exists()
        assert (
            len(list(output_dir.glob("*.csv"))) >= 3
        )  # At least grid, persons, samples
        assert (output_dir / "changes.json").exists()
