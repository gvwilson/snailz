"""Apply random effects."""

from datetime import timedelta
import random


def apply_effects(scenario):
    """Apply mix of random effects to scenario."""

    params = scenario.params
    specimens = scenario.specimens.samples

    # Modify specimen masses based on mutation
    for s in specimens:
        if s.is_mutant:
            s.mass *= params.specimen_params.mut_mass_scale

    # Modify mass based on pollution level
    grids = {g.id: g for g in scenario.grids}
    for s in specimens:
        if not s.is_mutant:
            continue
        level = grids[s.grid][s.x, s.y]
        s.mass += s.mass * params.pollution_scale * level

    # Modify sample readings based on delay in processing
    lookup = {s.id: s for s in specimens}
    for assay in scenario.assays:
        delta = (assay.performed - lookup[assay.specimen_id].sampled).days
        for x in range(assay.readings.size):
            for y in range(assay.readings.size):
                if assay.treatments[x, y] != "S":
                    continue
                drop = assay.readings[x, y] * params.delay_scale * delta
                assay.readings[x, y] = max(0.0, assay.readings[x, y] - drop)


def assign_sample_locations(grids, specimens):
    """Allocate specimens to grid locations."""

    size = grids[0].size
    assert all(g.size == size for g in grids), "Grid size(s) mis-match"

    coords = [(g.id, x, y) for g in grids for x in range(size) for y in range(size)]
    for s in specimens.samples:
        i = random.randint(0, len(coords) - 1)
        s.grid, s.x, s.y = coords[i]
        del coords[i]


def choose_assay_date(params, specimen):
    """Determine date assay performed."""

    return specimen.sampled + timedelta(days=random.randint(1, params.max_delay))
