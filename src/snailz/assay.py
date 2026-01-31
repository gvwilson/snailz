"""Pollution measurement."""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import random
from sqlite_utils import Database
from typing import ClassVar, Self

from ._base_mixin import BaseMixin
from ._utils import IdGeneratorType, id_generator, random_date
from .grid import Grid
from .parameters import Parameters
from .rating import Rating


ASSAY_PRECISION = 2


@dataclass
class Assay(BaseMixin):
    """
    A single pollution assay.

    Attributes:
        ident: unique identifier
        lat: latitude where assay performed (from grid cell)
        lon: longitude where assay performed (from grid cell)
        person_id: who performed assay (from persons)
        machine_id: machine used for assay (from machines)
        performed: date assay was performed
        contents: 'C' for control or 'T' for treatment
        readings: readings for contents
    """

    primary_key: ClassVar[str] = "ident"
    pivot_keys: ClassVar[set[str]] = {"contents", "readings"}
    table_name: ClassVar[str] = "assay"
    _next_id: IdGeneratorType = id_generator("A", 4)

    ident: str = ""
    lat: float = 0.0
    lon: float = 0.0
    person_id: str = ""
    machine_id: str = ""
    performed: date = date.min
    contents: str = ""
    readings: list[float] = field(default_factory=list)

    def __post_init__(self):
        """
        Generate unique identifier.
        """

        self.ident = next(self._next_id)

    @classmethod
    def make(
        cls, params: Parameters, grids: list[Grid], ratings: list[Rating]
    ) -> list[Self]:
        """
        Construct multiple assays.

        Args:
            params: Parameters object.
            grids: Grids that samples are taken from.
            ratings: Proficiencies with machines.

        Returns:
            List of assays.
        """

        result = []
        for _ in range(params.num_assays):
            g = random.choice(grids)
            x, y = random.randint(0, g.size - 1), random.randint(0, g.size - 1)
            lat, lon = g.lat_lon(x, y)
            rat = random.choice(ratings)
            performed = random_date(params.start_date, params.end_date)
            contents = cls._random_contents(params)
            readings = cls._random_readings(params, contents, g[x, y], rat.certified)
            result.append(
                Assay(
                    lat=lat,
                    lon=lon,
                    person_id=rat.person_id,
                    machine_id=rat.machine_id,
                    performed=performed,
                    contents=contents,
                    readings=readings,
                )
            )
        return result

    @classmethod
    def save_csv(cls, outdir: Path | str, assays: list[Self]):
        """
        Save assays as CSV. Scalar properties of all assays are saved in
        one file; assay measurements are pivoted to long form and saved
        in a separate file.

        Args:
            outdir: Output directory.
            assays: `Assay` objects to save.
        """

        super().save_csv(outdir, assays)

        with open(Path(outdir, "assay_readings.csv"), "w", newline="") as stream:
            objects = cls._assay_readings(assays)
            writer = cls._csv_dict_writer(stream, list(objects[0].keys()))
            for obj in objects:
                writer.writerow(obj)

    @classmethod
    def save_db(cls, db: Database, assays: list[Self]):
        """
        Save assays to database. Scalar properties of all assays are
        saved in one table; assay readings are pivoted to long form
        and saved in a separate table.

        Args:
            db: Database connector.
            assays: `Assay` objects to save.
        """

        super().save_db(db, assays)

        table = db["assay_readings"]
        table.insert_all(
            cls._assay_readings(assays),
            pk=("ident"),
            foreign_keys=[
                ("person_id", "person", "ident"),
                ("machine_id", "machine", "ident"),
            ],
        )

    @classmethod
    def _assay_readings(cls, assays: list[Self]) -> list[dict[str, str | float]]:
        """
        Get assay readings in long format for persistence.

        Args:
            assays: Assays to pivot.

        Returns:
            List of persistable dictionaries.
        """

        return [
            {"assay_id": a.ident, "contents": c, "reading": r}
            for a in assays
            for c, r in zip(a.contents, a.readings)
        ]

    @classmethod
    def _random_contents(cls, params: Parameters) -> str:
        """
        Generate random control or treatment indicators.

        Args:
            params: Control parameters.

        Returns:
            String of "CT".
        """

        num_controls = params.assay_size // 2
        num_treatments = params.assay_size - num_controls
        contents = ["C"] * num_controls + ["T"] * num_treatments
        random.shuffle(contents)
        return "".join(contents)

    @classmethod
    def _random_readings(
        cls, params: Parameters, contents: str, target: float, certified: bool
    ) -> list[float]:
        """
        Generate random readings clustered around target value.

        Args:
            params: Control parameters.
            contents: "CT" string showing control or treatment.
            target: Desired mean result.
            certified: Whether person is certified for machine being used.

        Returns:
            List of assay readings.
        """

        scale = params.assay_certified if certified else 1.0
        raw = [random.gauss(0, params.grid_std_dev) / scale for _ in contents]
        return [
            round(abs(r + target) if c == "T" else abs(r), ASSAY_PRECISION)
            for r, c in zip(raw, contents)
        ]
