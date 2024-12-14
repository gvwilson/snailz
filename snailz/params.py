'''Parameter dataclasses and utilities.'''

from argparse import Namespace
from dataclasses import dataclass, field
from datetime import datetime
from importlib.resources import files
import json
from pathlib import Path
from typing import List
import pytz

# Use ISO date format.
DATE_FORMAT = '%Y-%m-%d'

# Start and end dates for experiemnts.
DEFAULT_START_DATE = datetime.strptime('2023-11-01', DATE_FORMAT).replace(tzinfo=pytz.UTC)
DEFAULT_END_DATE = datetime.strptime('2023-11-10', DATE_FORMAT).replace(tzinfo=pytz.UTC)

# Parameter files to include in package.
PARAMETER_FILES = (
    'params/assays.json',
    'params/genomes.json',
    'params/grids.json',
    'params/samples.json',
    'params/sites.csv',
    'params/staff.json',
    'params/surveys.csv',
)


@dataclass
class AssayParams:
    '''Parameters for assay data generation.'''

    assay_staff: list
    assay_types: list
    assay_duration: list
    assay_plates: list
    control_val: float = 5.0
    controls: List[str] = field(default_factory=list)
    enddate: str = None
    experiments: int = 1
    filename_length: int = 8
    fraction: float = None
    invalid: float = 0.1
    seed: int = None
    startdate: str = None
    stdev: float = 3.0
    treated_val: float = 8.0
    treatment: str = None

    def __post_init__(self):
        '''Fill in missing dates and convert to standard format.'''
        if self.startdate is None:
            self.startdate = DEFAULT_START_DATE
        elif isinstance(self.startdate, str):
            self.startdate = datetime.strptime(self.startdate, DATE_FORMAT).replace(tzinfo=pytz.UTC)
        elif not self.startdate.tzinfo:
            self.startdate = self.startdate.replace(tzinfo=pytz.UTC)

        if self.enddate is None:
            self.enddate = DEFAULT_END_DATE
        elif isinstance(self.enddate, str):
            self.enddate = datetime.strptime(self.enddate, DATE_FORMAT).replace(tzinfo=pytz.UTC)
        elif not self.enddate.tzinfo:
            self.enddate = self.enddate.replace(tzinfo=pytz.UTC)


@dataclass
class GenomeParams:
    '''Gene sequence parameters.'''
    snp_probs: list
    length: int
    num_genomes: int
    num_snp: int
    prob_other: float
    seed: int = None


@dataclass
class GridParams:
    '''Invasion percolation parameters.'''
    depth: int
    height: int
    seed: int
    width: int


@dataclass
class SampleParams:
    '''Sampled snail parameters.'''
    min_snail_size: float = None
    max_snail_size: float = None
    mutant: float = None
    normal: float = None
    seed: int = None


@dataclass
class StaffParams:
    '''Staff parameters.'''
    locale: str = 'et_EE'
    num: int = None
    seed: int = None


def export_params(options: Namespace) -> None:
    '''Export parameter files.

    This function is used to write default parameter files when the package is installed.

    -   options.outdir: directory to write to.
    '''
    outdir = Path(options.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    root = files(__name__.split('.')[0])
    for filename in PARAMETER_FILES:
        src = root.joinpath(filename)
        dst = outdir.joinpath(Path(filename).name)
        dst.write_bytes(src.read_bytes())


def load_params(cls: type, filename: str) -> object:
    '''Load parameters from file and return as object.

    Args:
        cls: class to instantiate.
        filename: file containing JSON representation of parameters.

    Returns:
        Populated instance of the given class.
    '''
    return cls(**json.loads(Path(filename).read_text()))
