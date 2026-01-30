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
