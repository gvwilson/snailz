"""Test image generation."""

from datetime import date

from PIL.Image import Image as PilImage

from snailz.assays import AssayParams, Assay, AllAssays
from snailz.grid import Grid
from snailz.images import AllImages


def test_image_generation(fs):
    readings = Grid(width=2, height=2, default=0.0, data=[[1.0, 2.0], [3.0, 4.0]])
    treatments = Grid(width=2, height=2, default="C", data=[["S", "S"], ["C", "C"]])
    assays = AllAssays(
        items=[
            Assay(
                ident="a1",
                specimen="s1",
                person="p1",
                machine="m1",
                performed=date(2025, 4, 1),
                readings=readings,
                treatments=treatments,
            )
        ]
    )
    params = AssayParams().model_copy(update={"plate_size": 2})

    images = AllImages.generate(params, assays)
    assert len(images) == len(assays.items)
    assert "a1" in images
    assert isinstance(images["a1"], PilImage)
