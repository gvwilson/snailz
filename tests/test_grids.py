"""Test grid generation."""

from datetime import timedelta

from snailz.grids import GridParams, Grid, grids_generate


def test_generate_grids_correct_length():
    params = GridParams()
    grids = grids_generate(params)
    assert len(grids.grids) == params.number
    for g in grids.grids:
        assert len(g.cells) == params.size
        assert all(len(r) == params.size for r in g.cells)


def test_generate_grids_correct_dates():
    params = GridParams()
    max_date = (
        params.start_date
        + timedelta(days=params.number - 1)
        + timedelta(days=params.number * params.max_interval)
    )
    grids = grids_generate(params)
    for g in grids.grids:
        assert params.start_date <= g.start_date
        assert g.start_date <= g.end_date
        assert g.end_date <= max_date


def test_convert_grid_to_csv():
    size = 3
    params = GridParams().model_copy(update={"size": size})
    fixture = Grid(
        ident="G000",
        size=size,
        start_date=params.start_date,
        end_date=params.start_date,
        cells=[list(range(size)) for _ in range(size)],
    )
    result = fixture.to_csv()
    assert result == "2,2,2\n1,1,1\n0,0,0\n"
