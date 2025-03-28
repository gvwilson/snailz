# Contributing

Contributions are very welcome.  Please file issues or submit pull
requests in our GitHub repository.  All contributors will be
acknowledged, but must abide by our Code of Conduct.

## Please

-   Use [Conventional Commits][conventional].
-   [Open an issue][repo] *before* creating a pull request.

## Setup

1.  Fork or clone [the repository][repo].
1.  `uv sync --extra dev" to install an editable version of this
    package along with all its dependencies (including developer
    dependencies).
1.  Use <code>uv run <em>COMMAND</em></code> to run commands
    in the virtual environments.
    In particular, use `uv run doit list` to see available commands
    and <code>uv run doit <em>COMMAND</em></code> to run a command.

Alternatively:

1.  Create a fresh Python environment: `uv venv`
1.  Activate that environment: `source .venv/bin/activate`
1.  Install dependencies and editable version of package: `uv pip install -e '.[dev]'`

## Actions

`uv run doit list` prints a list of available commands.

| Command   | Action |
| --------- | ------ |
| all       | Regenerate all data using example parameters. |
| assays    | Generate sample assays file. |
| build     | Build the Python package in the current directory. |
| coverage  | Run tests with coverage. |
| docs      | Generate documentation using MkDocs. |
| format    | Reformat code. |
| grid      | Generate sample grid file. |
| init      | Regenerate default parameters. |
| lint      | Check the code format. |
| mangle    | Mangle generated assay files. |
| people    | Generate sample people file. |
| specimens | Generate sample specimens file. |
| test      | Run tests. |
| tidy      | Clean all build artifacts. |
| typing    | Check types with pyright. |

## Publishing

1.  `twine upload --verbose -u __token__ -p pypi-your-access-token dist/*`

[conventional]: https://www.conventionalcommits.org/
[repo]: https://github.com/gvwilson/snailz
