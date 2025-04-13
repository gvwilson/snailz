"""Simulated annealing to place snailz."""

from datetime import date
import math
import random


from .grid import Grid, Point
from .specimens import Specimen


# Arbitrary date for initializing wall specimens
DATE = date(1970, 1, 1)

# How far wall points are from grid
BORDER = 4

# How many steps for annealing
STEPS = 100


def anneal(size: int, specimens: list[Specimen]) -> None:
    """Calculate specimen positions using simulated annealing.

    Parameters:
        size: grid size
        specimens: partially-initialized specimens to place
    """
    _initial_placement(size, specimens)
    grid = _make_grid(size, specimens)
    wall = _make_wall(size)
    for i in range(STEPS):
        _move(grid, wall, specimens)


def _initial_placement(size: int, specimens: list[Specimen]) -> None:
    """Randomly initialize specimen placement.

    Parameters:
        size: grid size
        specimens: partially-initialized specimens to place
    """
    candidates = [(x, y) for x in range(size) for y in range(size)]
    for i, (x, y) in enumerate(random.sample(candidates, len(specimens))):
        specimens[i].location.x = x
        specimens[i].location.y = y


def _make_grid(size: int, specimens: list[Specimen]) -> Grid[str]:
    """Make initial grid to track specimen positions during placement.

    Parameters:
        size: grid size
        specimens: partially-initialized specimens to place
    """
    grid = Grid(width=size, height=size, default="")
    for s in specimens:
        grid[s.location.x, s.location.y] = s.ident
    return grid


def _make_wall(size: int) -> list[Specimen]:
    """Make a wall of unit-mass specimens to keep actual specimens in the grid.

    Parameters:
        size: grid size
    """
    result = []
    bounds = (-BORDER, size + BORDER - 1)
    for x in range(*bounds):
        for y in bounds:
            result.append(
                Specimen(
                    ident="",
                    survey_id="",
                    species=0,
                    location=Point(x=x, y=y),
                    collected=DATE,
                    genome="",
                    mass=1.0,
                )
            )
    for y in range(1 - BORDER, size + BORDER - 2):
        for x in bounds:
            result.append(
                Specimen(
                    ident="",
                    survey_id="",
                    species=0,
                    location=Point(x=x, y=y),
                    collected=DATE,
                    genome="",
                    mass=1.0,
                )
            )
    return result


def _move(grid: Grid[str], wall: list[Specimen], specimens: list[Specimen]) -> None:
    """Move a randomly-selected specimen one step.

    Parameters:
        grid: temporary grid showing specimen positions
        wall: barrier around outside of grid
        specimens: specimens being moved
    """
    i = random.randint(0, len(specimens) - 1)
    s = specimens[i]
    f_point_x, f_point_y = _point_point_force(specimens, i)
    f_wall_x, f_wall_y = _wall_point_force(wall, s)
    new_x = _clip(grid.width, s.location.x, f_point_x + f_wall_x)
    new_y = _clip(grid.height, s.location.y, f_point_y + f_wall_y)
    if grid[new_x, new_y] == "":
        grid[s.location.x, s.location.y] = ""
        s.location.x = new_x
        s.location.y = new_y
        grid[s.location.x, s.location.y] = s.ident


def _point_point_force(specimens: list[Specimen], i: int) -> tuple[float, float]:
    """Calculate force on specimen 'i' from other specimens.

    Parameters:
        specimens: all specimens
        i: which specimen is being moved

    Returns:
        XY components of force.
    """
    fx, fy = 0.0, 0.0
    for j, s in enumerate(specimens):
        if i == j:
            continue
        dx, dy = _single_force(specimens[i], s)
        fx += dx
        fy += dy
    return fx, fy


def _wall_point_force(wall: list[Specimen], specimen: Specimen) -> tuple[float, float]:
    """Calculate force on selected specimen from fixed wall.

    Parameters:
        wall: fixed wall containing specimens
        specimen: specimen being moved

    Returns:
        XY components of force.
    """
    fx, fy = 0.0, 0.0
    for w in wall:
        dx, dy = _single_force(specimen, w)
        fx += dx
        fy += dy
    return fx, fy


def _single_force(s0: Specimen, s1: Specimen) -> tuple[float, float]:
    """Calculate force on specimen from another specimen.

    Parameters:
        s0: specimen being moved
        s1: specimen acting on it

    Returns:
        XY components of force.
    """
    loc0 = s0.location
    loc1 = s1.location
    dx = loc1.x - loc0.x
    dy = loc1.y - loc0.y
    r_sq = dx**2 + dy**2
    assert r_sq > 0, f"{s0} vs. {s1}"
    r = math.sqrt(r_sq)
    f = s0.mass * s1.mass / r_sq
    fx = -f * dx / r
    fy = -f * dy / r
    return fx, fy


def _clip(size: int, coord: int, force: float) -> int:
    """Calculate new coordinate (old-1, old+1, or 0 depending on force).

    Parameters:
        size: grid size
        coord: X or Y coordinate
        force: force in that direction

    Returns:
        New coordinate.
    """
    if (force < 0) and (coord > 0):
        return coord - 1
    if (force > 0) and (coord < size - 1):
        return coord + 1
    return coord
