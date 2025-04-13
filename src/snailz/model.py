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

from .anneal import anneal
from .grid import Grid
from .parameters import AssayParams, MachineParams, SpecimenParams, SurveyParams
from .specimens import Specimen
from .surveys import Survey
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
    return list(
        sorted(random.sample(list(range(params.genome_length)), params.max_mutations))
    )


def specimen_adjust_mass(
    survey: Survey, max_pollution: float, specimen: Specimen
) -> float:
    """Adjust mass of specimen depending on pollution levels.

    Parameters:
        survey: survey that specimen is taken from
        max_pollution: maximum pollution level seen across all surveys
        specimen: specimen to adjust
    """
    pollution = survey.cells[specimen.location.x, specimen.location.y]
    if (pollution is None) or (pollution == 0.0):
        return specimen.mass
    scaling = 1.0 + 2.0 * utils.sigmoid(pollution / max_pollution)
    return specimen.mass * scaling


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


def specimen_genome(params: SpecimenParams, specimens: BaseModel) -> tuple[int, str]:
    """Generate genome for a particular specimen.

    Parameters:
        specimens: all specimens

    Returns:
        Random genome produced by mutating reference genome.
    """
    num_species = len(specimens.references)
    species = utils.choose_one(list(range(num_species)), weights=params.prob_species)
    genome = list(specimens.references[species])
    max_mutations = random.randint(1, len(specimens.loci[species]))
    locations = random.sample(specimens.loci[species], max_mutations)
    for loc in locations:
        genome[loc] = utils.choose_one(utils.BASES)
    result = "".join(genome)
    return species, result


def specimen_initial_mass(
    params: SpecimenParams,
    species: int,
    collected: date,
    is_mutant: bool,
) -> float:
    """Generate mass of a specimen.

    Parameters:
        params: specimen generation parameters
        collected: specimen collection date
        is_mutant: whether this specimen is a mutant

    Returns:
        Random mass.
    """

    # Initial mass
    mass_scale = params.mut_mass_scale if is_mutant else 1.0
    mean_mass = mass_scale * params.mean_masses[species]
    mass = abs(random.gauss(mean_mass, mean_mass * params.mass_rel_stdev))

    # Growth effects
    days_passed = (collected - params.start_date).days
    mass += params.daily_growth * days_passed * mass

    return mass


def specimens_num_per_survey(params: SpecimenParams, survey: Survey) -> int:
    """Number of specimens per survey.

    Parameters:
        params: specimen generation parameters
        survey: particular survey

    Returns:
        Number of specimens.
    """
    return random.randint(survey.size // 2, (3 * survey.size) // 2)


def specimens_place(survey: Survey, specimens: list[Specimen]) -> None:
    """Place specimens in grid.

    Parameters:
        survey: survey from which specimens taken
        specimens: to place
    """
    anneal(survey.size, specimens)


def specimen_reference_genome(params: SpecimenParams) -> str:
    """Make a random reference genome.

    Parameters:
        params: SpecimenParams with length attribute

    Returns:
        A randomly generated genome string of the specified length
    """
    return "".join(random.choices(utils.BASES, k=params.genome_length))


def survey_initialize_grid(size: int) -> Grid[int]:
    """Initialize values in survey grid.

    Parameters:
        size: size of survey grid

    Returns:
        Initialized grid.
    """
    cells = Grid(width=size, height=size, default=0)
    size_1 = size - 1
    center = size // 2
    moves = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    x, y = center, center
    cells[x, y] = 1
    while (x != 0) and (x != size_1) and (y != 0) and (y != size_1):
        cells[x, y] += 1
        m = random.choice(moves)
        x += m[0]
        y += m[1]
    return cells
