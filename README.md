# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/snailz/main/pages/img/snail-logo.svg" alt="snail logo" width="200px">

`snailz` is a synthetic data generator
that models a study of snails in the Pacific Northwest
which are growing to unusual size as a result of exposure to pollution.
The package can generate fully-reproducible datasets of varying sizes and with varying statistical properties,
and is intended primarily for classroom use.
For example,
an instructor can give each learner a unique dataset to analyze,
while learners can test their analysis pipelines using datasets they generate themselves.
`snailz` can also be used to teach good software development practices:
it is well structured,
well tested,
and uses modern Python tools.

> *The Story*
>
> Years ago,
> logging companies dumped toxic waste in a remote region of Vancouver Island.
> As the containers leaked and the pollution spread,
> some of the tree snails in the region began growing unusually large.
> Your team is now collecting and analyzing specimens from affected regions
> to determine if a mutant gene makes snails more susceptible to the pollution.

`snailz` generates five related sets of data:

Persons
:   The scientists conducting the study.
    Persons are included in the dataset to simulate operator bias,
    i.e.,
    the tendency for different people to perform experiments in slightly different ways.

Machines
:   The equipment used to analyze the samples.
    Like persons, they are included to enable simulation of bias.

Surveys
:   The locations where specimens are collected.
    Each survey site is represented as a square grid of pollution measurements.

Specimens
:   The snails collected from the sites.
    The data records where the snail was found,
    the date it was collected,
    its mass,
    and a short fragment of its genome.

Assays
:   The chemical analysis of the snails' genomes.
    Each assay is performed by putting samples of a snail's tissue
    into some small wells in a plastic [microplate][microplate].
    An inert material is placed in other wells as a control;
    the wells are then treated with chemicals and photographed,
    and the brightness of each well shows how reactive the material was.
    Each assay is stored in two files:
    a design file showing which wells contain samples and controls,
    and a readings file with the measured responses.
    The images that the readings are taken from are also stored.

## Usage

1.  `pip install snailz` (or the equivalent command for your Python environment).
1.  `snailz --help` to see available commands.

To generate example data in a fresh directory:

```
# Create and activate Python virtual environment
$ uv venv
$ source .venv/bin/activate

# Install snailz and dependencies
$ uv pip install snailz

# Write default parameter values to ./params.json file
$ snailz params --output params.json

# Generate all output files in ./data directory
$ snailz data --params params.json --output data
```

## Parameters

`snailz` reads controlling parameters from a JSON file,
and can generate a file with default parameter values as a starting point.
The parameters, their meanings, and their properties are:

| Group | Name | Purpose | Notes | Default |
| ----- | ---- | ------- | ----- | -----__ |
| overall | `seed` | random number generation seed | non-negative integer | 7493418 |
| `assay` | `baseline` | assay reading for non-mutant specimens | non-negative real | 1.0 |
| | `degrade` | reading degradation per day between sample collection and assay | non-negative real | 0.05 |
| | `delay` | maximum days of delay between sample collection and assay | non-negative integer | 5 |
| | `mutant` | assay reading for mutant specimens | non-negative real, greater than `baseline` | 10.0 |
| | `rel_stdev` | relative standard deviation readings | non-negative real | 0.2 |
| | `plate_size` | number of rows and columns in assay plate | non-negative integer | 4 |
| | `image_noise` | noise to add to assay images | scale is 0-255 | 32 |
| | `p_duplicate_assay` | probability of duplicate assay | probability | 0.05 |
| `machine` | `variation` | systematic variation in readings | percentage | 0.05 |
| | `number` | number of machines | non-negative integer | 5 |
| `person` | `locale` | locale for random name generation | valid ISO locale | `et_EE` (Estonia) |
| | `number` | number of persons | non-negative integer | 5 |
| `specimen` | `length` | genome length in bases | non-negative integer | 20 |
| | `prob_species` | probability of each species | list of probabilities summing to 1.0 | [0.6, 0.4] |
| | `mean_masses` | mean unmutated snail mass per species | non-negative reals (same length as probabilities) | [10.0, 20.0] |
| | `start_date` | date of first assay | copied from surveys for convenience | 2024-03-01 |
| | `mut_mass_scale` | scaling factor for mutated snails | real greater or equal to 1.0 | 2.0 |
| | `mass_rel_stdev` | relative standard deviation in masses | non-negative real | 0.5 |
| | `max_mutations` | maximum number of mutations in genome | non-negative integer | 5 |
| | `daily_growth` | percentage increase in mass per day | non-negative real | 0.01 |
| | `p_missing_location` | probability that sample location is unknown | probability | 0.05 |
| `survey` | `number` | number of survey sites | non-negative integer | 3 |
| | `size` | survey grid size | non-negative integer | 15 |
| | `start_date` | overall survey start date | ISO date | 2024-03-01 |
| | `max_interval` | maximum number of days between specimen samples | non-negative integer | 7 |

Notes:

1.  The pollution values in survey grids are generated by performing a random walk of the grid,
    adding one to each cell's value each time it is visited.
    The random walk starts when the polluted region reaches the boundary of the survey grid.

1.  Survey sites are sampled sequentially,
    i.e.,
    all of the samples from one site are collected before any samples are collected from the next.

1.  Some specimens' grid locations are missing from the final data.
    Their XY coordinates are missing in `specimens.csv` and `null` in `snailz.db`.

1.  Snails belong to one or more species,
    each of which has a different reference genome
    and (potentially) different mean mass.

1.  All snail genome fragments are the same length,
    and are generated by mutating the bases at a few randomly-chosen locations.
    One of those locations and one of the variant bases is selected at random for species 0;
    a snail with that mutant base in that location is a mutant of unusual size.

1.  The masses of all snails are scaled up by an amount that depends on
    how polluted their collection location is.
    This scaling uses a [sigmoid function][sigmoid] rather than a linear function.

1.  A few specimens are assayed twice instead of once.

1.  The actual readings for mutated and unmutated snails are randomly generated
    from normal distributions centered around `assay.baseline` and `assay.mutant`.
    The readings for control wells are just noise.

1.  Assay readings for both mutated and unmutated snails are lowered
    by an amount that depends on the number of days between the sample being collected
    and the assay being performed.

1.  Snails are placed on survey grids using simulated annealing.
    Each snail is initially put in a randomly-chosen location.
    Snails are then moved as if they were repulsive electrical charges,
    with large snails repelling their neighbors more than small ones.
    A "wall" of snails with unit mass surrounding the grid
    ensures that actual snails don't wander off.

## Data Dictionary

All of the generated data is stored in a single JSON file called `data.json`.
It can be read and analyzed directly,
but it is more realistic to use the data described below.

### Persons

`persons.csv` contains information about the scientists performing the study.
The file looks like this:

| ident  | personal | family   |
| :----- | :------- | :------- |
| aa1942 | Artur    | Aasmäe   |
| kk0085 | Katrin   | Kool     |
| …      | …        | …        |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `ident` | identifier | text, unique, required |
| `personal` | personal name | text, required |
| `family` | family name | text, required |

### Machines

`machines.csv` contains information about the machines used in the study.
The file looks like this:

| ident | name |
| ----- | ---- |
| M0001 | AeroProbe |
| M0002 | NanoCounter Plus |
| …     | … |


and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `ident` | identifier | text, unique, required |
| `name` | machine name | text, required |

Note that the systematic variation in readings introduced by different machines
is *not* stored in the generated data.

### Surveys

The `surveys` directory contains one CSV file for each survey site.
Each file's name has the form <code>S<em>nnn</em>.csv</code> (e.g., `S165.csv`),
where <code>S<em>nnn</em></code> is the survey site's unique identifier.
These CSV files do *not* have column headers;
instead, each contains a square integer matrix of pollution readings.
A typical file is:

```
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,1,1,0,0,0,0
0,0,0,0,0,0,0,0,1,2,1,0,0,0,0
0,0,0,0,0,0,0,0,2,1,0,0,0,0,0
0,0,0,0,0,0,0,1,2,0,0,0,0,0,0
0,0,0,0,0,0,0,1,2,1,0,0,0,0,0
0,0,0,0,0,0,0,0,1,2,0,0,0,0,0
0,0,0,0,0,0,0,2,2,1,0,0,0,0,0
0,0,0,0,0,0,0,1,3,0,0,0,0,0,0
0,0,0,0,0,0,0,1,3,1,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### Specimens

`specimens.csv` holds information about individual snails in CSV format (with column headers).
The file looks like this:

| ident  | survey |  x |  y | collected  | genome               | mass |
| :----- | :----- | -: | -: | :--------- | :------------------- | ---: |
| KHNKDL | S165   | 11 |  4 | 2024-03-01 | GCAACCGGACCGCCGTAAGG | 3.82 |
| DZYIPY | S165   |  3 |  7 | 2024-03-01 | TCATACGGACCGCCGTAAGG | 3.53 |
| … | … | … | … | … | … | … |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `ident` | specimen identifier | text, unique, required |
| `survey` | survey identifier | text, required |
| `x` | collection X coordinate within survey grid | integer, required |
| `y` | collection Y coordinate within survey grid | integer, required |
| `collected` | collection date | ISO date, required |
| `genome` | base sequence | text, required |
| `mass` | snail weight in grams | real, required |

Note that the CSV file does *not* record which species the snail belongs to
or whether it is a mutant.

### Assays

Summary information about all assays is stored in `assays.csv`.
The file looks like this:

| ident  | specimen | person | performed  |
| :----  | :------- | :----- | :--------- |
| 386915 | KHNKDL   | km3478 | 2024-03-05 |
| 508199 | DZYIPY   | mt8294 | 2024-03-01 |
| …      | …        | …      | …          |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `ident` | assay identifier | text, required |
| `specimen` | specimen identifier | text, required |
| `person` | scientist identifier | text, required |
| `performed` | assay date | ISO date, required |

The `assays` directory contains three files for each assay:

1.  a design file <code><em>nnnnnn</em>_treatments.csv</code>
    showing whether specimen samples or control material was placed in each well of the assay plate;

2.  a readings file <code><em>nnnnnn</em>_readings.csv</code>
    with the reading from each well;
    and

3.  an image file <code><em>nnnn</em>.png</code> showing the image that the readings were taken from.
    (In actuality `snailz` generates the readings first and then the image.)

Each CSV file contains a multi-line header with metadata followed by
a table of well values with row and column labels.
A typical design file is:

```
id,037356,,,
specimen,AMEMRZ,,,
date,2024-03-11,,,
by,pv8677,,,
machine,M0002,,,
,A,B,C,D
1,S,C,C,S
2,C,C,S,C
3,S,C,S,S
4,C,S,C,S
```

while a typical readings file is:

```
id,037356,,,
specimen,AMEMRZ,,,
date,2024-03-11,,,
by,pv8677,,,
machine,M0002,,,
,A,B,C,D
1,1.09,0.08,0.02,1.1
2,0.02,0.02,1.0,0.07
3,1.03,0.03,1.1,1.07
4,0.09,1.02,0.04,1.01
```

The first five rows of each file are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id`  | assay identifier | text, required |
| `specimen` | specimen identifier | text, required |
| `date` | assay date | ISO date, required |
| `by` | scientist identifier | text |
| `machine` | machine identifier | text |

The `assays` directory also contains files called <code><em>nnnnnn</em>_raw.csv</code>.
Each of these files contains the same data as the assay's readings file,
but has some deliberate errors:
header rows may be missing or out of order,
data may be indented,
and so on.
These files are provided so that people can learn how to deal with messy real-world data.

### Database

All of the data about people, specimens, and assays is also stored in
a SQLite database called `snailz.db`,
whose structure is shown below.

<div align="center">
  <img src="https://raw.githubusercontent.com/gvwilson/snailz/main/pages/img/schema.svg" alt="database schema">
</div>

### Data File Structure

```
data
├── params.json
├── data.json
├── persons.csv
├── machines.csv
├── surveys
│   ├── S165.csv
│   ├── S410.csv
│   └── …
├── specimens.csv
├── assays.csv
├── assays
│   ├── 037356_treatments.csv
│   ├── 037356.png
│   ├── 037356_raw.csv
│   ├── 037356_readings.csv
│   ├── 092025_treatments.csv
│   ├── 092025.png
│   ├── 092025_raw.csv
│   ├── 092025_readings.csv
│   └── …
└── snailz.db
```

## Colophon

`snailz` was inspired by the [Palmer Penguins][penguins] dataset
and by conversations with [Rohan Alexander][alexander-rohan]
about his book [*Telling Stories with Data*][telling-stories].

The snail logo was created by [sunar.ko][snail-logo].

My thanks to everyone who built the tools this project relies on, including:

-   [`click`][click] for building the command-line interface.
-   [`doit`][doit] to run commands.
-   [`mkdocs`][mkdocs] for documentation.
-   [`pydantic`][pydantic] for storing and validating data (including parameters).
-   [`pytest`][pytest], [`pyfakefs`][pyfakefs], and [`faker`][faker] for testing.
-   [`ruff`][ruff] and [`pyright`][pyright] for checking the code.
-   [`uv`][uv] for managing packages and the virtual environment.

[alexander-rohan]: https://rohanalexander.com/
[click]: https://click.palletsprojects.com/
[doit]: https://pydoit.org/
[faker]: https://faker.readthedocs.io/
[mkdocs]: https://www.mkdocs.org/
[microplate]: https://en.wikipedia.org/wiki/Microplate
[penguins]: https://allisonhorst.github.io/palmerpenguins/
[pydantic]: https://docs.pydantic.dev/
[pyfakefs]: https://pypi.org/project/pyfakefs/
[pyright]: https://pypi.org/project/pyright/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[sigmoid]: https://en.wikipedia.org/wiki/Sigmoid_function
[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
[telling-stories]: https://tellingstorieswithdata.com/
[uv]: https://docs.astral.sh/uv/
