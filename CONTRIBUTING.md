# Contributing

Contributions are very welcome.
Please file issues or submit pull requests in our GitHub repository.
All contributors will be acknowledged,
but must abide by our Code of Conduct.

## Site Structure

-   `README.md`: overview
-   `LICENSE.md`: content license
-   `CODE_OF_CONDUCT.md`: code of conduct
-   `CONTRIBUTING.md`: this contributors' guide
-   `pyproject.toml`: Python package description
-   `Makefile`: repeatable commands
-   `src/snailz/`: Python source
    -   `src/snailz/params/`: sample data synthesis parameters
-   `data/`: sample synthesized data
-   `img/`: images

## Build and Release

-   `uv pip install build twine`
-   `python -m build`
-   `twine upload --verbose -u __token__ -p pypi-your-access-token dist/*`

## Labels

| Name             | Description                  | Color   |
| ---------------- | ---------------------------- | ------- |
| change           | something different          | #FBCA04 |
| feature          | new feature                  | #B60205 |
| fix              | something broken             | #5319E7 |
| good first issue | newcomers are always welcome | #D4C5F9 |
| talk             | question or discussion       | #0E8A16 |
| task             | one-off task                 | #1D76DB |

Please use [Conventional Commits][conventional] style for pull requests
by using `change:`, `feature:`, `fix:`, or `task:` as the first word
in the title of the commit message.
You may also use `publish:` if the PR just rebuilds the HTML version of the lesson.

[conventional]: https://www.conventionalcommits.org/
