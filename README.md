![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

# autohooks-plugin-ruff

[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-ruff.svg)](https://pypi.org/project/autohooks-plugin-ruff/)

An [autohooks](https://github.com/greenbone/autohooks) plugin for python code
formatting via [ruff](https://github.com/astral-sh/ruff).

## Installation

### Install using pip

> [!NOTE] The `pip install` command does no longer work out-of-the-box in newer
> distributions like Ubuntu >= 23.04 because of [PEP 668](https://peps.python.org/pep-0668).

You can install the latest stable release of autohooks-plugin-ruff from the
Python Package Index using [pip](https://pip.pypa.io/):

    python3 -m pip install --user autohooks-plugin-ruff

### Install using poetry

It is highly encouraged to use [poetry](https://python-poetry.org) for
maintaining your project's dependencies. Normally autohooks-plugin-ruff is
installed as a development dependency.

    poetry add --group dev autohooks-plugin-ruff

## Usage

To activate the ruff autohooks plugin please run

```shell
poetry run autohooks plugins add autohooks.plugins.ruff
```
    
or alternatively add the following setting to your
*pyproject.toml* file.

```toml
[tool.autohooks]
pre-commit = ["autohooks.plugins.ruff"]
```

What the plugin actually does is `ruff check .` on git commit, so you should be
able to use the exact same settings as in [ruff's docs](https://beta.ruff.rs/docs/settings/).

## Notes

This project only runs ruff as a pre-commit hook, so, all features from ruff
should be available too.

To activate this pre-commit hook remember to run this command before you start:

```shell
poetry run autohooks activate --mode poetry
```

## Maintainer

This project is maintained by [Greenbone AG](https://www.greenbone.net/).

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/autohooks-plugin-ruff/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-ruff/issues)
first.

## License

Copyright (C) 2023 - 2024 [Greenbone AG](https://www.greenbone.net/)

Licensed under the [GNU General Public License v3.0 or later](LICENSE).
