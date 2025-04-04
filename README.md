# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/sz/main/img/snail-logo.svg" alt="snail logo" width="200px">

These synthetic data generators model a study of snails in the Pacific Northwest
that are growing to unusual size as a result of exposure to pollution.

## For Users

1.  `pip install snailz` (or the equivalent command for your Python environment).
1.  `snailz --help` to see available commands.

| Command   | Action |
| --------- | ------ |
| data      | Generate all data files. |
| params    | Generate parameter files with default values. |

To generate example data in a fresh directory:

```
# Create and activate Python virtual environment
$ uv venv
$ source .venv/bin/activate

# Install snailz and dependencies
$ uv pip install snailz

# Write default parameter values to ./params/ directory
$ snailz params --output params

# Generate all output files in ./data directory
$ snailz data --params params --output data
```

## Colophon

Snail logo by [sunar.ko][snail-logo].

[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
