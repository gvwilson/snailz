"""Generate assay images."""

import math
import numpy as np

from PIL import Image, ImageFilter


# Image parameters.
BLACK = 0
WHITE = 255
BORDER_WIDTH = 8
WELL_SIZE = 32
BLUR_RADIUS = 4


def make_image(params, assay, scaling):
    """Generate a single image."""

    # Create blank image array.
    p_size = params.plate_size
    img_size = (p_size * WELL_SIZE) + ((p_size + 1) * BORDER_WIDTH)
    array = np.full((img_size, img_size), BLACK, dtype=np.uint8)

    # Fill with pristine reading values.
    spacing = WELL_SIZE + BORDER_WIDTH
    for ix, x in enumerate(range(BORDER_WIDTH, img_size, spacing)):
        for iy, y in enumerate(range(BORDER_WIDTH, img_size, spacing)):
            color = math.floor(WHITE * assay.readings[ix, iy] / scaling)
            array[y : y + WELL_SIZE + 1, x : x + WELL_SIZE + 1] = color

    # Add noise to numpy array before converting to image
    array = _image_noise(params, array, img_size)

    # Convert to PIL Image
    img = Image.fromarray(array)

    # Apply blur filter
    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))

    return img


def _image_noise(params, array, img_size):
    """Add noise effects to numpy array before conversion to image."""

    # Generate random noise array of the same shape
    noise = np.random.randint(
        -params.image_noise,
        params.image_noise + 1,
        size=(img_size, img_size),
        dtype=np.int16,
    )

    # Add noise to the original array
    noisy_array = np.clip(array.astype(np.int16) + noise, BLACK, WHITE).astype(np.uint8)

    return noisy_array
