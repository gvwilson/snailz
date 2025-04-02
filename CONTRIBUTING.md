# Contributing

Contributions are very welcome.
Please file issues or submit pull requests in our GitHub repository.
All contributors will be acknowledged, but must abide by our Code of Conduct.

## Please

-   [Open an issue][repo] *before* creating a pull request
    so that other contributors can give feedback before you do a lot of work.
-   Use [Conventional Commits][conventional].

## Setup

1.  Fork or clone [the repository][repo].
1.  `uv sync --extra dev" to install an editable version of this package
    along with all its dependencies (including developer dependencies).
1.  Use <code>uv run <em>COMMAND</em></code> to run commands
    in the virtual environment.
    For example,
    use `uv run doit list` to see available commands
    and <code>uv run doit <em>COMMAND</em></code> to run a command.

Alternatively:

1.  Create a fresh Python environment: `uv venv`
1.  Activate that environment: `source .venv/bin/activate`
1.  Install dependencies and editable version of package: `uv pip install -e '.[dev]'`

## Actions

`uv run doit list` prints a list of available commands.

| Command   | Action |
| --------- | ------ |
| build     | Build the Python package in the current directory. |
| coverage  | Run tests with coverage. |
| docs      | Generate documentation using MkDocs. |
| format    | Reformat code. |
| lint      | Check the code format. |
| params    | Regenerate default parameter filess. |
| test      | Run tests. |
| tidy      | Clean all build artifacts. |

## Publishing

Use `twine upload --verbose -u __token__ -p pypi-your-access-token dist/*`.

[conventional]: https://www.conventionalcommits.org/
[repo]: https://github.com/gvwilson/sz
