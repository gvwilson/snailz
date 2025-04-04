"""Test specimen generation."""

from datetime import date

from snailz.grids import Point, Grid, GridList
from snailz.specimens import SpecimenParams, SpecimenList, Specimen, specimens_generate


def test_generate_specimens_correct_length():
    size = 3
    num = 5
    temp = [
        Grid(
            ident=f"G00{i}",
            size=size,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            cells=[list(range(size)) for _ in range(size)],
        )
        for i in range(num)
    ]
    grids = GridList(grids=temp)
    params = SpecimenParams()
    specimens = specimens_generate(params, grids)
    assert len(specimens.specimens) == num


def test_convert_specimens_to_csv():
    fixture = SpecimenList(
        loci=[1],
        reference="AAAA",
        susc_base="C",
        susc_locus=0,
        specimens=[
            Specimen(
                ident="S01",
                grid_id="G01",
                collected=date(2023, 7, 5),
                genome="ACGT",
                location=Point(x=1, y=1),
                mass=0.1,
            ),
            Specimen(
                ident="S03",
                grid_id="G03",
                collected=date(2024, 7, 5),
                genome="TGCA",
                location=Point(x=3, y=3),
                mass=0.3,
            ),
        ],
    )
    result = fixture.to_csv()
    expected = (
        "\n".join(
            [
                "ident,grid,collected,genome,x,y,mass",
                "S01,G01,2023-07-05,ACGT,1,1,0.1",
                "S03,G03,2024-07-05,TGCA,3,3,0.3",
            ]
        )
        + "\n"
    )
    assert result == expected
