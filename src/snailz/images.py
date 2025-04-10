"""Generate assay images."""

import math

from PIL import Image, ImageDraw
from PIL.Image import Image as PilImage  # to satisfy type checking
from pydantic import BaseModel

from .assays import AssayParams, Assay, AllAssays

from . import model, utils


# Image parameters.
BORDER_WIDTH = 8
WELL_SIZE = 32


class AllImages(BaseModel):
    """A set of generated images."""

    model_config = {"arbitrary_types_allowed": True, "extra": "forbid"}

    @staticmethod
    def generate(params: AssayParams, assays: AllAssays) -> dict:
        """Generate image files.

        Parameters:
            params: assay generation parameters
            assays: generated assays

        Returns:
            A dictionary of assay IDs and generated images.
        """
        max_reading = _find_max_reading(assays, params.plate_size)
        scaling = float(math.ceil(max_reading + 1))
        return {a.ident: _make_image(params, a, scaling) for a in assays.items}


def _find_max_reading(assays: AllAssays, p_size: int) -> float:
    """Find maximum assay reading value.

    Parameters:
        assays: generated assays
        p_size: plate size

    Returns:
        Largest reading value across all assays.
    """
    result = 0.0
    for a in assays.items:
        for x in range(p_size):
            for y in range(p_size):
                result = max(result, a.readings[x, y])
    return result


def _make_image(params: AssayParams, assay: Assay, scaling: float) -> PilImage:
    """Generate a single image.

    Parameters:
        params: assay parameters
        assay: assay to generate image for
        scaling: color scaling factor

    Returns:
       Image.
    """
    # Create blank image.
    p_size = params.plate_size
    img_size = (p_size * WELL_SIZE) + ((p_size + 1) * BORDER_WIDTH)
    img = Image.new("L", (img_size, img_size), color=utils.BLACK)

    # Fill with pristine reading values.
    spacing = WELL_SIZE + BORDER_WIDTH
    draw = ImageDraw.Draw(img)
    for ix, x in enumerate(range(BORDER_WIDTH, img_size, spacing)):
        for iy, y in enumerate(range(BORDER_WIDTH, img_size, spacing)):
            color = math.floor(utils.WHITE * assay.readings[ix, iy] / scaling)
            draw.rectangle((x, y, x + WELL_SIZE, y + WELL_SIZE), color)

    # Distort
    return model.image_noise(params, img, img_size)
