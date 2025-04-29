"""Generate assay images."""

import math
import numpy as np

from PIL import Image
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
            assays: assays to generate images for

        Returns:
            A dictionary of assay IDs and generated images.
        """
        scaling = float(math.ceil(assays.max_reading() + 1))
        return {a.ident: _make_image(params, a, scaling) for a in assays.items}


def _make_image(params: AssayParams, assay: Assay, scaling: float) -> PilImage:
    """Generate a single image.

    Parameters:
        params: assay parameters
        assay: assay to generate image for
        scaling: color scaling factor

    Returns:
       Image.
    """
    # Create blank image array.
    p_size = params.plate_size
    img_size = (p_size * WELL_SIZE) + ((p_size + 1) * BORDER_WIDTH)
    array = np.full((img_size, img_size), utils.BLACK, dtype=np.uint8)

    # Fill with pristine reading values.
    spacing = WELL_SIZE + BORDER_WIDTH
    for ix, x in enumerate(range(BORDER_WIDTH, img_size, spacing)):
        for iy, y in enumerate(range(BORDER_WIDTH, img_size, spacing)):
            color = math.floor(utils.WHITE * assay.readings[ix, iy] / scaling)
            array[y : y + WELL_SIZE + 1, x : x + WELL_SIZE + 1] = color

    # Add noise to numpy array before converting to image
    array = model.image_noise(params, array, img_size)

    # Convert to PIL Image
    img = Image.fromarray(array)

    # Apply blur filter
    return model.image_blur(img)
