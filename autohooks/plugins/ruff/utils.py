# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import importlib.util
from typing import Optional, Union

from autohooks.config import Config


def check_ruff_installed() -> None:
    if importlib.util.find_spec("ruff") is None:
        raise RuntimeError(
            "Could not find ruff. Please add ruff to your python environment"
        )


def get_ruff_config(config: Optional[Config]) -> Optional[Config]:
    return (
        config.get("tool", "autohooks", "plugins", "ruff") if config else None
    )


def ensure_iterable(value: Union[str, list[str]]) -> list[str]:
    if isinstance(value, str):
        return [value]
    return value


def get_ruff_arguments(
    config: Optional[Config], defaults: list[str]
) -> list[str]:
    if not config:
        return defaults

    arguments = ensure_iterable(config.get_value("arguments", defaults))

    return arguments
