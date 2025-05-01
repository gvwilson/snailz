from datetime import date, timedelta
import math
import random
from typing import ClassVar

from pydantic import BaseModel, Field

from .params import DEFAULT_START_DATE, SpecimenParams
from .utils import PRECISION, generic_id_generator


BASES = "ACGT"
OTHERS = {
    "A": "CGT",
    "C": "AGT",
    "G": "ACT",
    "T": "CGT",
}


class Specimen(BaseModel):
    """Store a single specimen specimen."""

    id: str = Field(description="unique ID")
    genome: str = Field(min_length=1, description="genome")
    is_mutant: bool = Field(description="is this a mutant?")
    mass: float = Field(gt=0, description="mass (g)")
    grid: str = Field(default="", description="sample grid ID")
    x: int = Field(default=-1, description="sample X coordinate")
    y: int = Field(default=-1, description="sample Y coordinate")
    sampled: date = Field(default=DEFAULT_START_DATE, description="Date sample taken")

    _id_generator: ClassVar = generic_id_generator(lambda i: f"S{i:04d}")

    @staticmethod
    def generate(params, ref_genome, is_mutant, susc_locus, susc_base):
        """Generate a single specimen.

        Parameters:
            params (SpecimenParams): parameters
            ref_genome (str): reference genome
            is_mutant (bool): is this specimen a mutant?
            susc_locus (int): susceptible locus in genome
            susc_base (str): base indicating mutant

        Returns:
            (Specimen): randomly-generated specimen.
        """

        genome = [
            random.choice(OTHERS[b])
            if random.uniform(0.0, 1.0) < params.mut_prob
            else b
            for i, b in enumerate(ref_genome)
        ]
        if is_mutant:
            genome[susc_locus] = susc_base
        mass = abs(random.gauss(params.mass_mean, params.mass_sd))

        days = random.randint(0, 1 + (params.end_date - params.start_date).days)
        sampled = params.start_date + timedelta(days=days)

        return Specimen(
            id=next(Specimen._id_generator),
            genome="".join(genome),
            is_mutant=is_mutant,
            mass=mass,
            sampled=sampled,
        )


class AllSpecimens(BaseModel):
    """Store a set of specimens."""

    params: SpecimenParams = Field(description="generation parameters")
    ref_genome: str = Field(description="reference genome")
    susc_locus: int = Field(description="susceptible locus")
    susc_base: str = Field(description="susceptible mutation")
    samples: list[Specimen] = Field(description="specimens")

    @staticmethod
    def generate(params, num):
        """Generate specimens.

        Parameters:
            params (SpecimenParams): parameters
            num (int): number of specimens required

        Returns:
            (AllSpecimens): collection of randomly-generated specimens.
        """

        if num <= 0:
            raise ValueError(f"invalid number of specimens {num}")

        ref_genome = "".join(random.choices(BASES, k=params.genome_length))
        susc_locus = random.choice(list(range(len(ref_genome))))
        susc_base = random.choice(OTHERS[ref_genome[susc_locus]])

        mutant_ids = set(
            random.choices(list(range(num)), k=math.ceil(params.mut_frac * num))
        )

        samples = [
            Specimen.generate(
                params, ref_genome, i in mutant_ids, susc_locus, susc_base
            )
            for i in range(num)
        ]

        return AllSpecimens(
            params=params,
            ref_genome=ref_genome,
            susc_locus=susc_locus,
            susc_base=susc_base,
            samples=samples,
        )

    def to_csv(self, writer):
        """Save specimens as CSV.

        Parameters:
            writer (stream): where to write
        """
        writer.writerow(["id", "genome", "mass", "grid", "x", "y", "sampled"])
        writer.writerows(
            [
                s.id,
                s.genome,
                round(s.mass, PRECISION),
                s.grid,
                s.x,
                s.y,
                s.sampled.isoformat(),
            ]
            for s in self.samples
        )
