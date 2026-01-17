"""Apply effects to raw data."""

import random


def do_all_effects(params, grids, persons, samples):
    """Apply effects in order."""

    changes = {"parameters": params.model_dump(mode="json")}
    for effect in (_do_pollution, _do_delay, _do_person, _do_precision):
        changes.update(effect(params, grids, persons, samples))
    return changes


def _do_delay(params, grids, persons, samples):
    """Modify sample mass based on sampling date."""

    duration = (params.sample_date[1] - params.sample_date[0]).days
    daily = (params.sample_mass[1] - params.sample_mass[0]) / duration
    for s in samples:
        elapsed = (s.when - params.sample_date[0]).days
        growth = elapsed * daily
        s.mass += growth
    return {"daily": daily}


def _do_person(params, grids, persons, samples):
    """Modify sample mass based on the person doing the survey."""

    if params.clumsy_factor is None:
        return {}
    clumsy = random.choice(persons)
    for s in samples:
        if s.person == clumsy.id:
            s.mass -= params.sample_mass[0] * params.clumsy_factor
    return {"clumsy": clumsy.id}


def _do_pollution(params, grids, persons, samples):
    """Modify sample mass based on presence of pollution."""

    grids = {g.id: g for g in grids}
    for s in samples:
        pollution = grids[s.grid][s.x, s.y]
        s.mass += params.pollution_factor * pollution * s.mass
    return {}


def _do_precision(params, grids, persons, samples):
    """Adjust precision of mass measurements."""

    for s in samples:
        s.mass = round(s.mass, params.precision)
    return {}
