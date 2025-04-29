"""Apply random effects."""

from datetime import timedelta
import random


def apply_effects(scenario):
    """Apply mix of random effects to scenario."""

    # Modify specimen masses based on mutation
    specimen_params = scenario.params.specimen_params
    for specimen in scenario.specimens.samples:
        if specimen.is_mutant:
            specimen.mass *= specimen_params.mut_mass_scale


def assign_sample_locations(grids, specimens):
    """Allocate specimens to grid locations."""

    size = grids[0].size
    assert all(g.size == size for g in grids), f"Grid size(s) mis-match"

    coords = [
        (g.id, x, y) for g in grids for x in range(size) for y in range(size)
    ]
    for s in specimens.samples:
        i = random.randint(0, len(coords) - 1)
        s.grid, s.x, s.y = coords[i]
        del coords[i]


def choose_assay_date(params, specimen):
    """Determine date assay performed."""

    return specimen.sampled + timedelta(days=random.randint(1, params.max_delay))

