"""Test image generation."""

from datetime import date

from PIL.Image import Image as PilImage

from snailz.assays import Assay
from snailz.grid import Grid
from snailz.images import make_image
from snailz.params import AssayParams


def test_image_generation(fs):
    params = AssayParams().model_copy(update={"plate_size": 2})
    readings = Grid(size=2, data=[[1.0, 2.0], [3.0, 4.0]])
    treatments = Grid(size=2, data=[["S", "S"], ["C", "C"]])
    assay = Assay(
        id="a1",
        specimen_id="s1",
        machine_id="m1",
        person_id="p1",
        performed=date(2025, 4, 1),
        readings=readings,
        treatments=treatments,
    )

    img = make_image(params, assay, 1.0)
    assert isinstance(img, PilImage)
