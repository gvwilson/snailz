"""Apply effects to raw data."""

import random


def do_all_effects(params, data):
    """Apply effects in order."""

    changes = {"parameters": params.model_dump(mode="json")}
    for effect in (_do_pollution, _do_delay, _do_person, _do_precision):
        changes.update(effect(params, data["grids"], data["persons"], data["samples"]))
    return changes


def _do_delay(params, grids, persons, samples):
    """Modify sample mass based on sampling date."""

    duration = (params.sample_date[1] - params.sample_date[0]).days
    daily = params.sample_size[1] / duration
    for s in samples:
        elapsed = (s.timestamp - params.sample_date[0]).days
        growth = elapsed * daily
        s.mass += growth
    return {"daily": daily}


def _do_person(params, grids, persons, samples):
    """Modify sample mass based on the person doing the survey."""

    if params.clumsy_factor is None:
        return {}
    clumsy = random.choice(persons)
    for s in samples:
        if s.person_id == clumsy.person_id:
            s.mass *= 1 + params.clumsy_factor
    return {"clumsy": clumsy.person_id}


def _do_pollution(params, grids, persons, samples):
    """Modify sample mass based on presence of pollution."""

    grids = {g.grid_id: g for g in grids}
    for s in samples:
        pollution = grids[s.grid_id][s.x, s.y]
        s.mass *= 1.0 + params.pollution_factor * pollution
        s.diameter *= 1.0 + params.pollution_factor * pollution
    return {}


def _do_precision(params, grids, persons, samples):
    """Adjust precision of mass measurements."""

    for s in samples:
        s.mass = round(s.mass, params.precision)
        s.diameter = round(s.diameter, params.precision)
    return {}
