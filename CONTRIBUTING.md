# Contributing

Contributions are very welcome;
please contact us [by email][email] or by filing an issue in [our repository][repo].
All contributors must abide by our code of conduct.

## Setup and Operation

-   Install [uv][uv]
-   Create a virtual environment by running `uv venv` in the root directory
-   Activate it by running `source .venv/bin/activate` in your shell
-   Install dependencies by running `uv pip install -r pyproject.toml`

| make task | effect                                   |
| --------- | ---------------------------------------- |
| clean     | clean up                                 |
| commands  | show available commands (default)        |
| format    | re-format code                           |
| lint      | check code and project                   |

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
[repo]: https://github.com/gvwilson/snailz
[uv]: https://github.com/astral-sh/uv
