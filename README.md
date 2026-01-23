# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/snailz/refs/heads/main/pages/img/snailz-logo.svg" alt="snail logo" width="200px">

`snailz` is a synthetic data generator
that models a study of snails in the Pacific Northwest
which are growing to unusual size as a result of exposure to pollution.
The package generates fully-reproducible datasets of varying sizes and with varying statistical properties,
and is intended for classroom use.
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

`snailz` generates several related datasets:

-   Grids: the survey grids where pollution levels are measured.
-   Persons: the scientists conducting the study.
-   Samples: the snails collected from the survey sites.
-   Machines: the equipment used in the survey.
-   Ratings: the scientists' proficiency ratings with the machines.

## Usage

To generate example data in a fresh directory:

```
# Create and activate Python virtual environment.
$ uv venv
$ source .venv/bin/activate

# Install snailz and dependencies.
$ uv pip install snailz

# Get help.
$ snailz --help

# Generate and display a dataset using the default parameters.
$ snailz --outdir -

# Write default parameter values to ./params.json for editing.
$ snailz --defaults > params.json

# Generate output with custom parameters in the ./data directory.
$ snailz --params params.json --outdir data
```

## Parameters

`snailz` reads controlling parameters from a JSON file,
and can generate a file with default parameter values as a starting point.
The parameters, their meanings, and their properties are:

| Name               | Purpose                                   | Default                  |
| ------------------ | ----------------------------------------- | -----------------------: |
| `clumsy_factor`    | personal effect on mass measurement       | 0.5                      |
| `grid_gap`         | minimum spacing between grids (m)         | 1000.0                   |
| `grid_size`        | width and height of (square) survey grids | 11                       |
| `grid_spacing`     | size of survey grid cell (m)              | 20                       |
| `lat0`             | reference latitude of grids (deg)         | 48.8666632               |
| `lon0`             | reference longitude of grids (deg)        | -124.1999992             |
| `locale`           | locale for person name generation         | et_EE                    |
| `num_grids`        | number of survey grids                    | 3                        |
| `num_machines`     | number of pieces of laboratory equipment  | 5                        |
| `num_persons`      | number of persons                         | 6                        |
| `num_samples`      | number of samples                         | 20                       |
| `pollution_factor` | pollution effect on mass                  | 0.3                      |
| `precision`        | decimal places used to record masses      | 2                        |
| `sample_date`      | min/max sample dates (YYYY-MM-DD)         | (2025-01-01, 2025-01-01) |
| `sample_size`      | sample mass mean and std. dev. (g)        | (50, 10)                 |
| `seed`             | random number generation seed             | 123456                   |

## Data Dictionary

All of the generated data is stored in CSV files
and in a SQLite database.

### Grids

The pollution readings for each survey grid
are stored in a file <code>G<em>nnnn</em>.csv</code> (e.g., `G0003.csv`).
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

The pollution readings for polluted grid cells are also stored in tidy format in `grids.csv`:

| grid_id | x  | y  | lat               | lon                | pollution |
| :------ | -: | -: | ----------------: | -----------------: | --------: |
| G0001   | 1  | 3  | 48.86720218670499 | -124.1997260797134 |         1 |
| G0001   | 2  | 3  | 48.86720218670499 | -124.1994529594268 |         1 |
| …       |  … |  … | …                 | …                  |         … |

Its fields are:

| Field       | Purpose                  | Properties             |
| ----------- | -------------            | ---------------------- |
| `grid_id`   | identifier               | text, unique, required |
| `x`         | X coordinate in grid     | integer, required      |
| `y`         | Y coordinate in grid     | integer, required      |
| `lat`       | latitude of grid cell    | real, required         |
| `lon`       | longitude of grid cell   | real, required         |
| `pollution` | pollution at that point  | integer, required      |

### Persons

`persons.csv` stores the scientists performing the study in CSV format (with column headers):

| person_id | personal | family   | supervisor_id |
| :-------- | :------- | :------- | :------------ |
| P06       | Artur    | Aasmäe   | P22           |
| P07       | Katrin   | Kool     |               |
| …         | …        | …        | …             |

Its fields are:

| Field           | Purpose       | Properties             |
| --------------- | ------------- | ---------------------- |
| `person_id`     | identifier    | text, unique, required |
| `personal`      | personal name | text, required         |
| `family`        | family name   | text, required         |
| `supervisor_id` | identifier    | text                   |

### Samples

`samples.csv` stores information about sampled snails in CSV format (with column headers):

| sample_id | grid_id | x  | y  | pollution | person_id | timestamp  | mass | diameter |
| :-----    | :------ | -: | -: | --------: | --------: | ---------: | ---: | -------: |
| S0001     | G0001   | 9  | 8  | 0         | P0004     | 2025-01-16 | 71.5 | 29.6     |
| S0002     | G0001   | 8  | 9  | 1         | P0005     | 2025-03-30 | 62.1 | 28.9     |
| …         | …       | …  | …  | …         | …         | …          | …    |

Its fields are:

| Field       | Purpose                  | Properties             |
| ----------- | ------------------------ | ---------------------- |
| `sample_id` | specimen identifier      | text, unique, required |
| `grid_id`   | grid identifier          | text, required         |
| `x`         | X coordinate in grid     | integer, required      |
| `y`         | Y coordinate in grid     | integer, required      |
| `pollution` | pollution at that point  | integer, required      |
| `person_id` | who collected the sample | text, required         |
| `timestamp` | date sample collected    | date, required         |
| `mass`      | sample weight (g)        | real, required         |
| `diameter`  | sample diameter (mm)     | real, required         |

### Machines

`machines.csv` stores a list of machines used in the survey:

| machine_id | name          |
| :--------- | :------------ |
| M0001      | Therma Sensor |
| M0002      | Nano Fuge     |
| …          | …             |

Its fields are:

| Field        | Purpose                  | Properties             |
| ------------ | ------------------------ | ---------------------- |
| `machine_id` | machine identifier       | text, unique, required |
| `name`       | machine name             | text, required         |

### Ratings

`ratings.csv` stores the proficiency ratings of scientists with various machines:

| person_id | machine_id | rating |
| :-------- | :--------- | -----: |
| P0006     | M0004      | 1      |
| P0001     | M0003      |        |
| …         | …          | …      |

Its fields are:

| Field        | Purpose                       | Properties             |
| ------------ | ----------------------------- | ---------------------- |
| `person_id`  | who has the rating            | text, required         |
| `machine_id` | the machine they are rated on | text, required         |
| `rating`     | numeric rating                | integer                |

### Extra Files

The output directory also contains a file called `changes.json`
that records parameters used to alter data,
such as the daily growth rate of snails
and the ID of the clumsy scientist whose measurements have systematic errors.

## Colophon

`snailz` was inspired by the [Palmer Penguins][penguins] dataset
and by conversations with [Rohan Alexander][alexander-rohan]
about his book [*Telling Stories with Data*][telling-stories].

My thanks to everyone who built the tools this project relies on, including:

-   [`faker`][faker] for data generation.
-   [`mkdocs`][mkdocs] for documentation.
-   [`pydantic`][pydantic] for storing and validating data (including parameters).
-   [`pytest`][pytest] for testing.
-   [`ruff`][ruff] for checking the code.
-   [`taskipy`][taskipy] for running tasks.
-   [`uv`][uv] for managing packages and the virtual environment.

The snail logo was created by [sunar.ko][snail-logo].

## Acknowledgments

-   [*Greg Wilson*][wilson-greg] is a programmer, author, and educator based in Toronto.
    He was the co-founder and first Executive Director of Software Carpentry
    and received ACM SIGSOFT's Influential Educator Award in 2020.

[alexander-rohan]: https://rohanalexander.com/
[faker]: https://faker.readthedocs.io/
[mkdocs]: https://www.mkdocs.org/
[penguins]: https://allisonhorst.github.io/palmerpenguins/
[pydantic]: https://docs.pydantic.dev/
[pyfakefs]: https://pypi.org/project/pyfakefs/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
[taskipy]: https://pypi.org/project/taskipy/
[telling-stories]: https://tellingstorieswithdata.com/
[uv]: https://docs.astral.sh/uv/
[wilson-greg]: https://third-bit.com/
