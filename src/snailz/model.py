"""Key randomization functions in model."""

# Turn off attribute access reporting because this file is imported by
# files that define BaseModel-derived types whose names are needed
# here for parameter declarations.
# pyright: reportAttributeAccessIssue=false

from datetime import date, timedelta
import math
import random

from PIL import ImageFilter
from PIL.Image import Image as PilImage  # to satisfy type checking
from pydantic import BaseModel

from .grid import Point
from .parameters import AssayParams, MachineParams, SpecimenParams, SurveyParams
from . import utils


# Image parameters.
BLUR_RADIUS = 4


def assay_performed(params: AssayParams) -> timedelta:
    """Number of days between collection and assay being performed.

    Parameters:
        params: assay parameters

    Returns:
        Number of days.
    """
    return timedelta(days=random.randint(0, params.delay))


def assay_reading(
    params: AssayParams, specimen: object, treatment: str, performed: date
) -> float:
    """
    Calculate individual assay reading.

    Parameters:
        params: assay parameters
        specimen: specimen being assayed
        treatment: "C" for control or "S" for sample
        performed: date assay performed

    Returns:
        Reading value.
    """
    degradation = max(
        0.0, 1.0 - (params.degrade * (performed - specimen.collected).days)
    )
    if treatment == "C":
        base_value = 0.0
        stdev = params.rel_stdev
    elif specimen.is_mutant:
        base_value = params.mutant * degradation
        stdev = base_value * params.rel_stdev
    else:
        base_value = params.baseline * degradation
        stdev = base_value * params.rel_stdev

    return abs(random.gauss(base_value, stdev))


def assay_specimens(params: AssayParams, specimens: BaseModel) -> list:
    """Generate list of specimens to be assayed.

    Parameters:
        params: assay parameters
        specimens: all available specimens

    Returns:
        List of specimens (possibly containing duplicates).
    """
    extra = random.choices(
        specimens.items,
        k=math.floor(params.p_duplicate_assay * len(specimens.items)),
    )
    subjects = specimens.items + extra
    random.shuffle(subjects)
    return subjects


def days_to_next_survey(params: SurveyParams) -> timedelta:
    """Choose the number of days between surveys.

    Parameters:
        params: specimen generation parameters

    Returns:
        Days to the next survey.
    """
    return timedelta(days=random.randint(1, params.max_interval))


def image_noise(params: AssayParams, img: PilImage, img_size: int) -> PilImage:
    """Add noise effects to image.

    Parameters:
        img: pristine image

    Returns:
        Distorted image.
    """
    # Add uniform noise (not provided by pillow).
    for x in range(img_size):
        for y in range(img_size):
            noise = random.randint(-params.image_noise, params.image_noise)
            old_val = img.getpixel((x, y))
            assert isinstance(old_val, int)  # for type checking
            val = max(utils.BLACK, min(utils.WHITE, old_val + noise))
            img.putpixel((x, y), val)

    # Blur.
    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))

    return img


def machine_brightness(params: MachineParams) -> float:
    """Choose relative brightness of this machine's camera.

    Parameters:
        params: machine parameters

    Returns:
        Brightness level in that range.
    """

    return random.uniform(1.0 - params.variation, 1.0 + params.variation)


def mutation_loci(params: SpecimenParams) -> list[int]:
    """Make a list of mutable loci positions.

    Parameters:
        params: specimen generation parameters

    Returns:
        Randomly selected positions that can be mutated.
    """
    return list(sorted(random.sample(list(range(params.length)), params.max_mutations)))


def specimen_collection_date(survey: BaseModel) -> date:
    """Choose a collection date for a specimen.

    Parameters:
        survey: survey that specimen belongs to

    Returns:
        Date specimen was collected.
    """
    return date.fromordinal(
        random.randint(survey.start_date.toordinal(), survey.end_date.toordinal())
    )


def specimen_genome(specimens: BaseModel) -> str:
    """Generate genome for a particular specimen.

    Parameters:
        specimens: all specimens

    Returns:
        Random genome produced by mutating reference genome.
    """
    genome = list(specimens.reference)
    max_mutations = random.randint(1, len(specimens.loci))
    locations = random.sample(specimens.loci, max_mutations)
    for loc in locations:
        genome[loc] = utils.choose_one(utils.BASES)
    result = "".join(genome)
    return result


def specimen_locations(params: SpecimenParams, size: int) -> list[Point]:
    """Generate locations for specimens.

    - Initialize a set of all possible (x, y) points.
    - Repeatedly choose one at random and add to the result.
    - Remove all points within a random radius of that point.

    Parameters:
        params: specimen generation parameters
        size: grid size

    Returns:
        A list of specimen locations.
    """

    # Generate points by repeated spatial subtraction.
    available = {(x, y) for x in range(size) for y in range(size)}
    result = []
    while available:
        loc = utils.choose_one(list(available))
        result.append(loc)
        radius = random.uniform(params.spacing / 4, params.spacing)
        span = math.ceil(radius)
        for x in _calculate_span(size, loc[0], span):
            for y in _calculate_span(size, loc[1], span):
                available.discard((x, y))

    # Replace some points with markers for missing data
    missing = Point(x=-1, y=-1)
    return [
        missing
        if random.uniform(0.0, 1.0) < params.p_missing_location
        else Point(x=r[0], y=r[1])
        for r in result
    ]


def specimen_mass(
    params: SpecimenParams,
    max_pollution: float,
    collected: date,
    pollution_level: float | None,
    is_mutant: bool,
) -> float:
    """Generate mass of a specimen.

    Parameters:
        params: specimen generation parameters
        max_pollution: maximum pollution level across all surveys
        collected: specimen collection date
        pollution_level: this specimen's pollution level
        is_mutant: whether this specimen is a mutant

    Returns:
        Random mass.
    """

    # Initial mass
    mass_scale = params.mut_mass_scale if is_mutant else 1.0
    mean_mass = mass_scale * params.mean_mass
    mass = abs(random.gauss(mean_mass, mean_mass * params.mass_rel_stdev))

    # Growth effects
    days_passed = (collected - params.start_date).days
    mass += params.daily_growth * days_passed * mass

    # Pollution effects if location known
    if (pollution_level is not None) and (pollution_level > 0.0):
        scaling = 1.0 + 2.0 * utils.sigmoid(pollution_level / max_pollution)
        mass *= scaling

    return mass


def _calculate_span(size: int, coord: int, span: int) -> range:
    """
    Calculate axial range of cells close to a center point.

    Parameters:
        size: grid size
        coord: X or Y coordinate
        span: maximum width on either side

    Returns:
        Endpoint coordinates of span.
    """
    return range(max(0, coord - span), 1 + min(size, coord + span))
