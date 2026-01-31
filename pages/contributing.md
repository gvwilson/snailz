# Contributing

Contributions are very welcome;
please contact us [by email][email] or by filing an issue in [our repository][repo].
All contributors must abide by our code of conduct.

## Setup

1.  Install [uv][uv].
1.  Create a virtual environment by running `uv venv` in the root directory.
1.  Activate it by running `source .venv/bin/activate` in your shell.
1.  Install dependencies by running `uv sync --extra dev`.

## Actions

Run `task --list` for a list of available actions.

| task   | description         |
| ------ | ------------------- |
| build  | build package       |
| check  | check code issues   |
| clean  | clean up            |
| docs   | build documentation |
| fix    | fix code issues     |
| format | format code         |
| serve  | serve documentation |
| test   | run tests           |

## Project Organization

```
.
├── CODE_OF_CONDUCT.md  # code of conduct
├── CONTRIBUTING.md     # contributors' guide
├── LICENSE.md          # project license
├── README.md           # project description
├── docs/               # generated HTML files: do not edit
├── mkdocs.yml          # MkDocs configuration file
├── pages               # Markdown source for site
│   ├── *.md            # top-level pages
│   └── img/*.*         # image files
├── pyproject.toml      # Python project file
├── src/                # source directory
│   └── snailz/*.py     # package directory
├── tests/*.py          # test files
└── uv.lock             # dependency lock file: do not edit
```

## FAQ

Do you need any help?
:   Yes—please see the issues in [our repository][repo].

What sort of feedback would be useful?
:   Everything is welcome,
    from pointing out mistakes in the code to suggestions for better explanations.

How should contributions be formatted?
:   Please use [Conventional Commits][conventional].

[conventional]: https://www.conventionalcommits.org/
[email]: mailto:gvwilson@third-bit.com
[repo]: https://github.com/gvwilson/t
[uv]: https://github.com/astral-sh/uv
