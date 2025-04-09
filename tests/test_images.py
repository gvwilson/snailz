"""Test image generation."""

from datetime import date

from PIL.Image import Image as PilImage  # to satisfy type checking

from snailz.assays import AssayParams, Assay, AllAssays
from snailz.grid import Grid
from snailz.images import AllImages


READINGS = Grid(width=2, height=2, default=0.0, data=[[1.0, 2.0], [3.0, 4.0]])
TREATMENTS = Grid(width=2, height=2, default="C", data=[["S", "S"], ["C", "C"]])
ASSAYS = AllAssays(
    items=[Assay(ident="a1", specimen="s1", person="p1", machine="m1",
                 performed=date(2025, 4, 1), readings=READINGS, treatments=TREATMENTS)]
)
ASSAY_PARAMS = AssayParams().model_copy(update={"plate_size": 2})

def test_image_generation(fs):
    images = AllImages.generate(ASSAY_PARAMS, ASSAYS)
    assert len(images) == len(ASSAYS.items)
    assert "a1" in images
    assert isinstance(images["a1"], PilImage)
