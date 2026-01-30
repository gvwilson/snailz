"""Details of snail species."""

from dataclasses import dataclass, field
from pathlib import Path
import random
from typing import ClassVar
from .utils import BaseMixin


BASES = {
    "A": "CGT",
    "C": "AGT",
    "G": "ACT",
    "T": "ACG",
}


@dataclass
class Species(BaseMixin):
    """A set of generated specimens."""

    pivot_keys: ClassVar[list[str]] = ["loci"]
    table_name: ClassVar[str] = "species"

    reference: str = ""
    loci: list[int] = field(default_factory=list)
    susc_locus: int = 0
    susc_base: str = ""

    @classmethod
    def save_csv(cls, outdir, species):
        """Save objects as CSV."""

        assert isinstance(species, list)
        super().save_csv(outdir, species)

        with open(Path(outdir, "species_loci.csv"), "w", newline="") as stream:
            objects = cls._loci(species[0])
            writer = cls._csv_dict_writer(stream, list(objects[0].keys()))
            for obj in objects:
                writer.writerow(obj)

    @classmethod
    def save_db(cls, db, species):
        """Save objects to database."""

        assert isinstance(species, list)
        super().save_db(db, species)
        table = db["species_loci"]
        table.insert_all(cls._loci(species[0]), pk="ident")

    @classmethod
    def make(cls, params):
        reference = cls.reference_genome(params)
        loci = cls.random_loci(params, reference)
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
    def reference_genome(cls, params):
        """Make a random reference genome."""

        return "".join(random.choices(list(BASES.keys()), k=params.genome_length))

    @classmethod
    def random_loci(cls, params, reference):
        """Make random loci for mutations."""

        assert 0 <= params.num_loci <= len(reference), (
            f"cannot generate {params.num_loci} loci for genome of length {len(reference)}"
        )
        locations = random.sample(list(range(len(reference))), params.num_loci)
        locations.sort()
        return locations

    def random_genome(self, params):
        """Construct a random genome."""

        genome = list(self.reference)
        for loc in self.loci:
            if random.random() < params.p_mutation:
                genome[loc] = random.choice(BASES[genome[loc]])
        return "".join(genome)

    @classmethod
    def _loci(cls, species):
        """Convert mutation loci into dictionaries."""

        return [
            {"ident": i + 1, "locus": locus} for i, locus in enumerate(species.loci)
        ]
