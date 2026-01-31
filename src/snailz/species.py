"""Details of snail species."""

from dataclasses import dataclass, field
from pathlib import Path
import random
from sqlite_utils import Database
from typing import ClassVar, Self

from ._base_mixin import BaseMixin
from .parameters import Parameters


BASES = {
    "A": "CGT",
    "C": "AGT",
    "G": "ACT",
    "T": "ACG",
}


@dataclass
class Species(BaseMixin):
    """
    A set of generated specimens.

    Attributes:
        reference: reference genome
        loci: locations within genome of possible mutations
        susc_locus: locus of susceptibility mutation
        susc_base: base at `susc_locus` conferring mutation
    """

    pivot_keys: ClassVar[set[str]] = {"loci"}
    table_name: ClassVar[str] = "species"

    reference: str = ""
    loci: list[int] = field(default_factory=list)
    susc_locus: int = 0
    susc_base: str = ""

    @classmethod
    def make(cls, params: Parameters) -> list[Self]:
        """
        Construct a list containing a single species. (The result
        is returned in a list to be consistent with other classes'
        `make` methods.)

        Args:
            params: Parameters object.

        Returns:
            List containin a single `Species`.
        """
        reference = cls._reference_genome(params)
        loci = cls._random_loci(params, reference)
        susc_locus = random.choice(loci)
        susc_base = random.choice(BASES[reference[susc_locus]])
        return [
            Species(
                reference=reference,
                loci=loci,
                susc_locus=susc_locus,
                susc_base=susc_base,
            )
        ]

    @classmethod
    def save_csv(cls, outdir: Path | str, species: list[Self]):
        """
        Save species as CSV. `species` must be passed in a list to be
        consistent with other classes' `save_csv` methods. Scalar
        properties of the species are saved in one file; mutation loci
        values are pivoted to long form and saved in a separate file.

        Args:
            outdir: Output directory.
            species: List containing `Species` to save.

        """

        assert isinstance(species, list)
        super().save_csv(outdir, species)

        with open(Path(outdir, "species_loci.csv"), "w", newline="") as stream:
            objects = species[0]._loci_to_dict()
            writer = cls._csv_dict_writer(stream, list(objects[0].keys()))
            for obj in objects:
                writer.writerow(obj)

    @classmethod
    def save_db(cls, db: Database, species: list[Self]):
        """
        Save species to database. `species` must be passed in a
        list to be consistent with other classes' `save_csv` methods.
        Scalar properties of the species are saved in one table;
        mutation loci values are pivoted to long form and saved in a
        separate table.

        Args:
            db: Database connector.
            species: List containing `Species` to save.
        """

        assert isinstance(species, list)
        super().save_db(db, species)
        table = db["species_loci"]
        table.insert_all(species[0]._loci_to_dict(), pk="ident")

    @classmethod
    def _random_loci(cls, params: Parameters, reference: str) -> list[int]:
        """
        Generate random loci for mutations.

        Args:
            params: Parameters object.
            reference: Reference genome.

        Returns:
            List of indices of locations where mutations might occur.
        """

        assert 0 <= params.num_loci <= len(reference), (
            f"cannot generate {params.num_loci} loci for genome of length {len(reference)}"
        )
        locations = random.sample(list(range(len(reference))), params.num_loci)
        locations.sort()
        return locations

    @classmethod
    def _reference_genome(cls, params: Parameters) -> str:
        """
        Make a random reference genome.

        Args:
            params: Parameters object.

        Returns:
            String of ACGT bases.
        """

        return "".join(random.choices(list(BASES.keys()), k=params.genome_length))

    def random_genome(self, params: Parameters) -> str:
        """
        Make a random genome based on a reference genome.

        Args:
            params: Parameters object.

        Returns:
            String of ACGT bases.
        """

        genome = list(self.reference)
        for loc in self.loci:
            if random.random() < params.p_mutation:
                genome[loc] = random.choice(BASES[genome[loc]])
        return "".join(genome)

    def _loci_to_dict(self):
        """Convert mutation loci into dictionaries for persistence."""

        return [{"ident": i + 1, "locus": locus} for i, locus in enumerate(self.loci)]
