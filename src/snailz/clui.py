"""Command-line interface."""

import argparse
import json
import sys

from .params import AssayParams, ScenarioParams, SpecimenParams
from .scenario import Scenario
from .utils import json_dump


DEFAULT_SEED = 123456
DEFAULT_PARAMS = ScenarioParams(
    rng_seed=DEFAULT_SEED, specimen_params=SpecimenParams(), assay_params=AssayParams()
)


def cli():
    """Main driver."""

    args = parse_args()

    if args.defaults:
        print(json_dump(DEFAULT_PARAMS))
        return

    if args.outdir is None:
        print("output directory required (used --outdir)", file=sys.stderr)
        sys.exit(1)

    if args.params:
        try:
            params = ScenarioParams.model_validate(json.load(open(args.params, "r")))
        except Exception as exc:
            print(f"unable to read parameters from {args.params}: {exc}")
            sys.exit(1)
    else:
        params = ScenarioParams(
            rng_seed=DEFAULT_SEED,
            specimen_params=SpecimenParams(),
            assay_params=AssayParams(),
        )

    random.seed(params.rng_seed)
    scenario = Scenario.generate(params)
    scenario.to_csv(args.outdir)


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--defaults", action="store_true", help="show default parameters"
    )
    parser.add_argument("--outdir", default=None, help="output directory")
    parser.add_argument("--params", default=None, help="JSON parameter file")
    return parser.parse_args()


if __name__ == "__main__":
    cli()
