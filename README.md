# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/snailz/main/img/snail-logo.svg" alt="snail logo" width="200px">

These synthetic data generators model genomic analysis of snails in
the Pacific Northwest that are growing to unusual size as a result of
exposure to pollution. At a high level:

-   A *grid* is created to record the *pollution levels* at a sampling site.
-   One or more *specimens* are collected from the grid.
    Each specimen has a *genome* and a *mass*.
-   *Laboratory staff* design and perform *assays* of those genomes.
-   Each assay is represented by a *design file* and an *assay file*.
-   Assay files are mangled to create *raw* files with formatting glitches.

In more detail,
`snailz` uses [invasion percolation](https://en.wikipedia.org/wiki/Invasion_percolation)
to create a square grid of integers
in which 0 marks sample sites without pollution and positive values show how polluted a site is.
Invasion percolation guarantees that all of the polluted sites are connected,
so one exercise is to try to find the origin of the pollution.
(It is always the center of the grid in the present version of the software,
but that could easily be modified.)
Grids are stored as JSON and converted to CSV;
the default parameters included with the package generated the following small grid,
which uses spaces instead of zeroes for clarity:

```
+-----------------------------+
|                             |
|                             |
|                             |
|              2              |
|            2 3              |
|        2   5 3              |
|    4 1 3 4 5                |
|    1 3 5 4 5 2 5 5          |
|        3 2     1   3        |
|          3 1 5 4 3 1 5 1 2 1|
|            1   3       1    |
|              4 4 2          |
|            2 4              |
|              3              |
|                             |
+-----------------------------+
```

The package also generates a set of snails (referred to as "specimens"),
each of which has a genome represented as a single string of ACGT bases,
a body mass,
the grid coordinates where it was collected,
and a collection date.
Individual genomes are created by mutating a reference genome at several randomly-selected loci.
One combination of locus and single-nucleotide polymorphism are considered "significant":
if a snail has that mutation at that locus *and* is collected from a polluted sample site,
its mass is increased by an amount that depends on how polluted the site is.
The snail's territory is then calculated by counting the number of grid cells
that are closer to it than to any other snail;
if a cell is equidistant from two or more snails,
its area is divided equally among them.
Once again the results are saved as both JSON and CSV,
and the default parameters included with the package generate specimens like these:

| ident  |  x |  y | genome          | mass  | collected_on | territory |
| :----- | -: | -: | :-------------- | ----: | :----------- | :-------- |
| AZ5PXJ |  6 |  8 | GACGATGTTAGAGCT | 22.95 | 2025-03-12   | 9.0       |
| AZP8M5 |  9 |  0 | ACGGATGTTAGAGCT | 20.00 | 2025-03-07   | 7.0       |
| AZJMU7 |  1 |  6 | CTAGATGTTAGAGCT | 23.41 | 2025-03-15   | 22.33     |
| AZGH04 |  0 |  7 | AGGGATGTTAGAGCT | 18.07 | 2025-03-10   | 8.83      |
| …      |  … |  … | …               | …     | …            | …         |

`snailz` uses Python's [faker](https://faker.readthedocs.io/) module
to generate a set of laboratory staff with personal and family names,
which are saved as JSON and CSV.
The defaults include:

| ident  | personal | family   |
| :----- | :------- | :------- |
| aa1942 | Artur    | Aasmäe   |
| kk0085 | Katrin   | Kool     |
| ta4600 | Aivar    | Toomsalu |
| ea5044 | Anne     | Eller    |
| …      | …        | …        |

Every specimen is used in an assay,
which is performed by a single member of staff on a particular date.
Each assay is represented by two CSV files:
a design file which records whether each well in the assay plate contained a control (C) or a specimen sample (S),
and an assay file which records the response measured in each well.
If the well contains a control, the assay value is a small (positive) amount of noise.
If the well contains genetic material from a specimen that *doesn't* have the significant mutation,
the assay value is some intermediate value with added noise,
while the assay value for a specimen with the significant mutation is a larger value (also with noise).
All assay data is saved in a single JSON file;
a summary of all assays is saved as CSV like this:

| ident  | specimen_id | performed  | performed_by |
| :----  | :---------- | :--------- | :----------- |
| 878987 | AZ5PXJ      | 2023-02-09 | ta4600       |
| 274653 | AZP8M5      | 2023-01-22 | ea5044       |
| 129820 | AZJMU7      | 2023-02-03 | bt0138       |
| 707990 | AZGH04      | 2023-02-15 | kk0085       |
| …      | …           | …          | …            |

Each assay design is saved as CSV like this:

```
id,230779,,,
specimen,AZQTWF,,,
performed,2023-02-04,,,
performed_by,aa1942,,,
,A,B,C,D
1,S,S,S,C
2,S,C,C,C
3,C,S,C,C
4,C,C,C,C
```

and each assay result like this:

```
id,277650,,,
specimen,AZTZNU,,,
performed,2023-02-13,,,
performed_by,aa1942,,,
,A,B,C,D
1,0.09,0.03,10.75,0.05
2,10.43,10.36,10.47,0.01
3,0.08,10.58,0.06,0.04
4,10.19,0.08,0.05,0.09
```

To make simulated data more realistic:

1.  Responses for both mutated and unmutated specimens decrease over time
    depending on the value of the degradation parameter
    to simulate the effects of processing delay.

1.  If the `oops` parameter is given a value greater than zero,
    one experimenter is chosen at random
    and all of their response values scaled up by this amount
    to simulate operator error.

1.  A "raw" assay file is also created by taking the clean ones
    and introducing zero or more deliberate formatting errors
    to simulate the kind of data that laboratories commonly produce.

Finally,
a SQLite database file is created that stores the people, specimens, and assay summary information
in tables with the obvious names and columns.

## For Users

1.  `pip install snailz` (or the equivalent command for your Python environment).
1.  `snailz --help` to see available commands.

| Command   | Action |
| --------- | ------ |
| all       | Generate all data files. |
| assays    | Generate assays for specimens. |
| convert   | Convert JSON data to CSV format. |
| database  | Create a SQLite database from CSV files. |
| grid      | Generate grid. |
| init      | Initialize parameter files for snailz. |
| mangle    | Modify assay files by reassigning people. |
| people    | Generate people. |
| specimens | Generate specimens. |

To generate example data in a fresh directory:

```
# Create and activate Python virtual environment
$ uv venv
$ source .venv/bin/activate

# Install snailz and dependencies
$ uv pip install snailz

# Copy default parameter values into ./params/*.json
$ snailz init --output params

# Regenerate all output files in ./tmp
$ snailz all --params params --output tmp
```

To generate individual data files:

```
# Create a grid JSON file in ./tmp/grid.json and a CSV file in ./tmp/grid.csv
$ snailz grid --params params/grid.json --output tmp/grid.json
$ snailz convert --kind grid --input tmp/grid.json --output tmp/grid.csv

# Create people JSON and CSV files in ./tmp/people.json and ./tmp/people.csv
$ snailz people --params params/people.json --output tmp/people.json
$ snailz convert --kind people --input tmp/people.json --output tmp/people.csv

# Create specimen JSON and CSV files in ./tmp/specimens.json and ./tmp/specimens.csv
$ snailz specimens --params params/specimens.json --grid tmp/grid.json --output tmp/specimens.json
$ snailz convert --kind specimens --input tmp/specimens.json --output tmp/specimens.csv

# Create assay JSON and CSV files in ./tmp/assays.json, ./tmp/assays.csv, and ./tmp/assays/*.csv
$ snailz assays --params params/assays.json --specimens tmp/specimens.json --people tmp/people.json --output tmp/assays.json
$ snailz convert --kind assays --input tmp/assays.json --output tmp
```

## Parameters and Workflow

<img src="https://raw.githubusercontent.com/gvwilson/snailz/main/img/workflow.png" alt="workflow">

`./params` contains the parameter files used to control generation of the reference dataset.

-   `grid.json`
    -   `depth`: integer range of random values in cells
    -   `seed`: RNG seed
    -   `size`: width and height of (square) grid in cells
-   `people.json`
    -   `locale`: language and region to use for name generation
    -   `number`: number of staff to create
    -   `seed`: RNG seed
-   `specimens.json`
    -   `end_date`: end date for specimen collection
    -   `length`: genome length in characters
    -   `max_mass`: maximum specimen mass
    -   `min_mass`: minimum specimen mass
    -   `mut_scale`: scaling factor for mutated specimens
    -   `mutations`: number of mutations to introduce
    -   `number`: number of specimens to create
    -   `seed`: RNG seed
    -   `start_date`: start date for specimen collection
-   `assays.json`
    -   `baseline`: assay response for unmutated specimens
    -   `delay`: maximum days between specimen collection and assay
    -   `degrade`: rate at which sample responses decrease per day after first day (0-1)
    -   `mutant`: assay response for mutated specimens
    -   `noise`: noise to add to control cells
    -   `oops`: scaling factor for operator error
    -   `plate_size`: width and height of assay plate
    -   `seed`: RNG seed

Note: there are no parameters for assay file mangling.

## Data Dictionary

`doit all` creates these files in `tmp` using the sample parameters in `params`:

-   `assays/`
    -   `NNNNNN_assay.csv`: tidy, consistently-formatted CSV file with assay result.
    -   `NNNNNN_design.csv`: tidy, consistently-formatted CSV file with assay design.
    -   `NNNNNN_raw.csv`: CSV file derived from `NNNNNN_assay.csv` with randomly-introduced formatting errors.
-   `assays.csv`: CSV file containing summary of assay metadata with columns.
    -   `ident`: assay identifier (integer).
    -   `specimen_id`: specimen identifier (text).
    -   `performed`: assay date (date).
    -   `performed_by`: person identifier (text).
-   `assays.json`: all assay data in JSON format.
-   `grid.csv`: CSV file containing pollution grid values.
    -   This file is a matrix of values with no column IDs or row IDs.
-   `grid.json`: grid data as JSON.
-   `people.csv`: CSV file describing experimental staff members.
    -   `ident`: person identifier (text)
    -   `personal`: personal name (text)
    -   `family`: family name (text)
-   `people.json`: staff member data in JSON format.
-   `specimens.csv`: CSV file containing details of snail specimens.
    -   `ident`: specimen identifier (text)
    -   `x`: X coordinate of collection cell (integer)
    -   `y`: Y coordinate of collection cell (integer)
    -   `genome`: base sequence (text)
    -   `mass`: snail mass (real)
    -   `collected_on`: date when specimen was collected (date)
-   `specimens.json`: specimen data in JSON format.
