"""Apply effects to raw data."""

import random


def do_all_effects(params, data):
    """Apply effects in order."""

    changes = {}
    for effect in (_do_pollution, _do_delay, _do_machine, _do_precision):
        changes.update(effect(params, data))
    return changes


def _do_delay(params, data):
    """Modify sample mass based on sampling date."""

    duration = (params.sample_date[1] - params.sample_date[0]).days
    daily = params.sample_mass[1] / duration
    for s in data["samples"]:
        elapsed = (s.timestamp - params.sample_date[0]).days
        growth = elapsed * daily
        s.mass += growth
    return {"daily": daily}


def _do_machine(params, data):
    """Modify sample mass based on the machine used."""

    biased = random.choice(data["machines"])
    for s in data["samples"]:
        if s.machine_id == biased.machine_id:
            s.mass *= 1 + params.machine_factor
    return {"biased": biased.machine_id}


def _do_pollution(params, data):
    """Modify sample mass based on presence of pollution."""

    grids = {g.grid_id: g for g in data["grids"]}
    for s in data["samples"]:
        pollution = grids[s.grid_id][s.x, s.y]
        s.mass *= 1.0 + params.pollution_factor * pollution
        s.diameter *= 1.0 + params.pollution_factor * pollution
    return {}


def _do_precision(params, data):
    """Adjust precision of mass measurements."""

    for s in data["samples"]:
        s.mass = round(s.mass, params.precision)
        s.diameter = round(s.diameter, params.precision)
    return {}
