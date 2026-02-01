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

## Usage:

```
usage: snailz [-h]
              [--defaults]
	      [--outdir OUTDIR]
              [--override OVERRIDE [OVERRIDE ...]]
	      [--params PARAMS]
              [--profile]

options:
  -h, --help            show this help message and exit
  --defaults            show default parameters as JSON
  --outdir OUTDIR       output directory
  --override OVERRIDE [OVERRIDE ...]
                        name=value parameters to override defaults
  --params PARAMS       specify JSON parameter file
  --profile             enable profiling
```

See the documentation of the `Parameters` class
for a description of data generation parameters.

## Schema

<img src="https://raw.githubusercontent.com/gvwilson/snailz/refs/heads/main/pages/img/schema.svg" alt="snailz schema">

| table          | field         | type  | purpose |
| -------------- | ------------- | ----- | ------- |
| grid           | ident         | text  | unique identifier for each survey grid |
|                | size          | int   | height and width of survey grid in cells |
|                | spacing       | float | size of survey grid cell (meters) |
|                | lat0          | float | southernmost latitude of grid (fractional degrees) |
|                | lon0          | float | westernmost longitude of grid (fractional degrees) |
|                |               |       |         |
| grid_cells     | grid_id       | text  | foreign key reference to grid |
|                | lat           | float | foreign key reference to grid cell |
|                | lon           | float | foreign key reference to grid cell |
|                | value         | float | pollution measurement in that grid cell |
|                |               |       |         |
| machine        | ident         | text  | unique identifier for each piece of laboratory equipment |
|                | name          | text  | name of piece of laboratory equipment |
|                |               |       |         |
| person         | ident         | text  | unique identifier for member of staff |
|                | family        | text  | family name of staff member |
|                | personal      | text  | personal name of staff member |
|                | supervisor_id | text* | foreign key reference to person's supervisor |
|                |               |       |         |
| rating         | person_id     | text  | foreign key reference to person |
|                | machine_id    | text  | foreign key reference to machine |
|                | certified     | bool  | whether person is certified to use machine |
|                |               |       |         |
| assay          | ident         | text  | unique identifier for soil assay |
|                | lat           | float | foreign key reference to grid cell |
|                | lon           | float | foreign key reference to grid cell |
|                | person_id     | text  | foreign key reference to person who did assay |
|                | machine_id    | text  | foreign key reference to machine used to do assay |
|                | performed     | date  | date that assay was done |
|                |               |       |         |
| assay_readings | assay_id      | text  | foreign key reference to assay |
|                | reading_id    | int   | serial number within assay |
|                | contents      | text  | "C" or "T" showing control or treatment |
|                | reading       | float | pollution measurement |
|                |               |       |         |
| species        | reference     | text  | reference genome |
|                | susc_locus    | int   | location of susceptible locus within genome |
|                | susc_base     | text  | base that causes significant mutation at that locus |
|                |               |       |         |
| species_loci   | ident         | int   | unique locus serial number |
|                | locus         | int   | locus where mutation might occur |
|                |               |       |         |
| specimen       | ident         | text  | unique identifier for specimen |
|                | lat           | float | foreign key reference to grid cell |
|                | lon           | float | foreign key reference to grid cell |
|                | genome        | text  | specimen genome |
|                | mass          | float | specimen mass (g) |
|                | diameter      | float | specimen diameter (mm) |
|                | collected     | date  | when specimen was collected |

## Colophon

`snailz` was inspired by the [Palmer Penguins][penguins] dataset
and by conversations with [Rohan Alexander][alexander-rohan]
about his book [*Telling Stories with Data*][telling-stories].

My thanks to everyone who built the tools this project relies on, including:

-   [faker][faker] for synthesizing data.
-   [mkdocs][mkdocs] for documentation.
-   [ruff][ruff] for checking the code.
-   [sqlite][sqlite] and [sqlite-utils][sqlite-utils] for persistence.
-   [taskipy][taskipy] for running tasks.
-   [uv][uv] for managing packages and the virtual environment.

The snail logo was created by [sunar.ko][snail-logo].

## Acknowledgments

-   [*Greg Wilson*][wilson-greg] is a programmer, author, and educator based in Toronto.
    He was the co-founder and first Executive Director of Software Carpentry
    and received ACM SIGSOFT's Influential Educator Award in 2020.

[alexander-rohan]: https://rohanalexander.com/
[faker]: https://faker.readthedocs.io/
[mkdocs]: https://www.mkdocs.org/
[penguins]: https://allisonhorst.github.io/palmerpenguins/
[ruff]: https://docs.astral.sh/ruff/
[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
[sqlite]: https://sqlite.org/
[sqlite-utils]: https://sqlite-utils.datasette.io/en/stable/
[taskipy]: https://pypi.org/project/taskipy/
[telling-stories]: https://tellingstorieswithdata.com/
[uv]: https://docs.astral.sh/uv/
[wilson-greg]: https://third-bit.com/
