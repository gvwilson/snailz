# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/snailz/refs/heads/main/pages/img/snailz-logo.svg" alt="snail logo" width="200px">

`snailz` is a synthetic data generator
that models a study of snails in the Pacific Northwest
which are growing to unusual size as a result of exposure to pollution.
The package can generate fully-reproducible datasets of varying sizes and with varying statistical properties,
and is intended primarily for classroom use.
For example,
an instructor can give each learner a unique dataset to analyze,
while learners can test their analysis pipelines using datasets they generate themselves.

> *The Story*
>
> Years ago,
> logging companies dumped toxic waste in a remote region of Vancouver Island.
> As the containers leaked and the pollution spread,
> some snails in the region began growing unusually large.
> Your team is now collecting and analyzing specimens from affected regions
> to determine if exposure to pollution is responsible.

`snailz` generates three related sets of data:

-   Grids: the survey grids where pollution levels are measured.
-   Persons: the scientists conducting the study.
-   Samples: the snails collected from the survey sites.

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

# Write default parameter values to the ./params.json file
$ snailz --defaults > params.json

# Generate all output files in the ./data directory
$ snailz --params params.json --outdir data
```

## Parameters

`snailz` reads controlling parameters from a JSON file,
and can generate a file with default parameter values as a starting point.
The parameters, their meanings, and their properties are:

| Name               | Purpose                                   | Default    |
| ------------------ | ----------------------------------------- | ---------: |
| `clumsy_factor`    | personal effect on mass measurement       | 0.5        |
| `grid_size`        | width and height of (square) survey grids | 11         |
| `locale`           | locale for person name generation         | et_EE      |
| `num_grids`        | number of survey grids                    | 3          |
| `num_persons`      | number of persons                         | 5          |
| `num_samples`      | number of samples                         | 20         |
| `pollution_factor` | pollution effect on mass                  | 0.3        |
| `precision`        | decimal places used to record masses      | 2          |
| `sample_date_max`  | maximum sample date                       | 2025-03-31 |
| `sample_date_min`  | minimum sample date                       | 2025-01-01 |
| `sample_mass_max`  | maximum sample mass                       | 1.5        |
| `sample_mass_min`  | minimum sample mass                       | 0.5        |
| `seed`             | random number generation seed             | 123456     |

## Data Dictionary

All of the generated data is stored in CSV files.

### Grids

The pollution readings for each survey grid are stored in a file <code>G<em>nnnn</em>.csv</code> (e.g., `G0003.csv`).
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

### Persons

`persons.csv` stores the scientists performing the study in CSV format (with column headers):

| id     | personal | family   |
| :----- | :------- | :------- |
| P06    | Artur    | Aasmäe   |
| P07    | Katrin   | Kool     |
| …      | …        | …        |

Its fields are:

| Field      | Purpose       | Properties             |
| ---------- | ------------- | ---------------------- |
| `id`       | identifier    | text, unique, required |
| `personal` | personal name | text, required         |
| `family`   | family name   | text, required         |

### Samples

`samples.csv` stores information about sampled snails in CSV format (with column headers):

| sample_id | grid_id | x  | y  | person | when       | mass |
| :-----    | :------ | -: | -: | -----: | ---------: | ---: |
| S0001     | G0001   | 9  | 8  | P0004  | 2025-01-16 | 1.02 |
| S0002     | G0001   | 8  | 9  | P0005  | 2025-03-30 | 2.39 |
| …         | …       | …  | …  | …      | …          | …    |

Its fields are:

| Field       | Purpose | Properties |
| ----------- | ------------------------ | ---------------------- |
| `sample_id` | specimen identifier      | text, unique, required |
| `grid_id`   | grid identifie           | text, required         |
| `x`         | X coordinate in grid     | integer, required      |
| `y`         | Y coordinate in grid     | integer, required      |
| `person`    | who collected the sample | text, required         |
| `when`      | date sample collected    | date, required         |
| `mass`      | sample weight in grams   | real, required         |

The output directory also contains a file called `changes.json`
that records parameters used to alter data,
such as the daily growth rate of snails
and the ID of the clumsy scientist whose measurements have systematic errors.

## Colophon

`snailz` was inspired by the [Palmer Penguins][penguins] dataset
and by conversations with [Rohan Alexander][alexander-rohan]
about his book [*Telling Stories with Data*][telling-stories].

The snail logo was created by [sunar.ko][snail-logo].

My thanks to everyone who built the tools this project relies on, including:

-   [`pydantic`][pydantic] for storing and validating data (including parameters).
-   [`pytest`][pytest] and [`faker`][faker] for testing.
-   [`ruff`][ruff] for checking the code.
-   [`uv`][uv] for managing packages and the virtual environment.

[alexander-rohan]: https://rohanalexander.com/
[faker]: https://faker.readthedocs.io/
[penguins]: https://allisonhorst.github.io/palmerpenguins/
[pydantic]: https://docs.pydantic.dev/
[pyfakefs]: https://pypi.org/project/pyfakefs/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
[telling-stories]: https://tellingstorieswithdata.com/
[uv]: https://docs.astral.sh/uv/
