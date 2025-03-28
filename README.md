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

In more detail:

-   `snailz` uses [invasion percolation](https://en.wikipedia.org/wiki/Invasion_percolation)
    to create a square grid of integers
    in which 0 marks sample sites without pollution and positive values show how polluted a site is.
    Invasion percolation guarantees that all of the polluted sites are connected,
    so one exercise is to try to find the origin of the pollution.
    (In the present version it is always the center of the grid,
    but that could easily be modified.)

-   The package also generates a set of snails (referred to as "specimens"),
    each of which has a genome represented as a single string of ACGT bases,
    a body mass,
    and the grid coordinates where it was collected.
    Individual genomes are created by mutating a reference genome at several randomly-selected loci.
    One combination of locus and single-nucleotide polymorphism are considered "significant":
    if a snail has that mutation at that locus *and* is collected from a polluted sample site,
    its mass is increased by an amount that depends on how polluted the site is.

-   `snailz` uses Python's [faker](https://faker.readthedocs.io/) module
    to generate a set of laboratory staff with personal and family names.

-   Every specimen is used in an assay,
    which is performed by a single member of staff on a particular date.
    Each assay is represented by two CSV files:
    a design file which records whether each well in the assay plate contained a control (C) or a specimen sample (S),
    and an assay file which records the response measured in each well.
    If the well contains a control, the assay value is a small (positive) amount of noise.
    If the well contains genetic material from a specimen that *doesn't* have the significant mutation,
    the assay value is some intermediate value with added noise,
    while the assay value for a specimen with the significant mutation is a larger value (also with noise).

-   Finally, a "raw" assay file is created by taking the clean ones
    and introducing zero or more deliberate formatting errors
    to simulate the kind of data that laboratories commonly produce.

## For Users

1.  `pip install snailz` (or the equivalent command for your Python environment).
1.  `snailz --help` to see available commands.

| Command   | Action |
| --------- | ------ |
| assays    | Generate assays for specimens within a date range. |
| convert   | Convert JSON data to CSV format. |
| grid      | Generate grid. |
| init      | Initialize parameter files for snailz. |
| mangle    | Modify assay files by reassigning people. |
| people    | Generate people. |
| specimens | Generate specimens. |

## Parameters

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
    -   `length`: genome length in characters
    -   `max_mass`: maximum specimen mass
    -   `min_mass`: minimum specimen mass
    -   `mut_scale`: scaling factor for mutated specimens
    -   `mutations`: number of mutations to introduce
    -   `number`: number of specimens to create
    -   `seed`: RNG seed
-   `assays.json`
    -   `baseline`: assay response for unmutated specimens
    -   `end_date`: date of final assay
    -   `mutant`: assay response for mutated specimens
    -   `noise`: noise to add to control cells
    -   `plate_size`: width and height of assay plate
    -   `seed`: RNG seed
    -   `start_date`: date of first assay

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
-   `specimens.json`: specimen data in JSON format.
