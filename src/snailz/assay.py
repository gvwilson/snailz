"""Pollution measurement."""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import random
from typing import ClassVar, Generator
from ._base_mixin import BaseMixin
from ._utils import id_generator, random_date


ASSAY_PRECISION = 2


@dataclass
class Assay(BaseMixin):
    """A single pollution assay."""

    primary_key: ClassVar[str] = "ident"
    pivot_keys: ClassVar[set[str]] = {"contents", "readings"}
    table_name: ClassVar[str] = "assay"
    _next_id: ClassVar[Generator[str, None, None]] = id_generator("A", 4)

    ident: str = ""
    lat: float = 0.0
    lon: float = 0.0
    person_id: str = ""
    machine_id: str = ""
    performed: date = date.min
    contents: str = ""
    readings: list[float] = field(default_factory=list)

    def __post_init__(self):
        """Validate and fill in."""

        self.ident = next(self._next_id)

    @classmethod
    def make(cls, params, grids, ratings):
        """Construct assays."""

        result = []
        for _ in range(params.num_assays):
            g = random.choice(grids)
            x, y = random.randint(0, g.size - 1), random.randint(0, g.size - 1)
            lat, lon = g.lat_lon(x, y)
            r = random.choice(ratings)
            performed = random_date(params.start_date, params.end_date)
            contents = cls._random_contents(params)
            readings = cls._random_readings(params, contents, g[x, y])
            result.append(
                Assay(
                    lat=lat,
                    lon=lon,
                    person_id=r.person_id,
                    machine_id=r.machine_id,
                    performed=performed,
                    contents=contents,
                    readings=readings,
                )
            )
        return result

    @classmethod
    def save_csv(cls, outdir, objects):
        """Save objects as CSV."""

        super().save_csv(outdir, objects)

        with open(Path(outdir, "assay_readings.csv"), "w", newline="") as stream:
            objects = cls._assay_readings(objects)
            writer = cls._csv_dict_writer(stream, list(objects[0].keys()))
            for obj in objects:
                writer.writerow(obj)

    @classmethod
    def save_db(cls, db, objects):
        """Save objects to database."""

        super().save_db(db, objects)

        table = db["assay_readings"]
        table.insert_all(
            cls._assay_readings(objects),
            pk=("ident"),
            foreign_keys=[
                ("person_id", "person", "ident"),
                ("machine_id", "machine", "ident"),
            ],
        )

    @classmethod
    def _assay_readings(cls, objects):
        """Get assay readings in long format for persistence."""

        return [
            {"assay_id": a.ident, "contents": c, "reading": r}
            for a in objects
            for c, r in zip(a.contents, a.readings)
        ]

    @classmethod
    def _random_contents(cls, params):
        """Generate random control or sample indicators."""

        num_controls = params.assay_size // 2
        num_treatments = params.assay_size - num_controls
        contents = ["C"] * num_controls + ["T"] * num_treatments
        random.shuffle(contents)
        return "".join(contents)

    @classmethod
    def _random_readings(cls, params, contents, target):
        """Generate random readings with predetermined mean."""

        raw = [random.gauss(0, params.grid_std_dev) for _ in contents]
        return [
            round(abs(r + target) if c == "T" else abs(r), ASSAY_PRECISION)
            for r, c in zip(raw, contents)
        ]
