# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import importlib.util
import subprocess
import sys
from typing import Iterable, List, Optional, Union

from autohooks.api import error, ok, out
from autohooks.api.git import get_staged_status, stash_unstaged_changes
from autohooks.config import Config
from autohooks.precommit.run import ReportProgress

DEFAULT_ARGUMENTS = []


def check_ruff_installed() -> None:
    if importlib.util.find_spec("ruff") is None:
        raise RuntimeError(
            "Could not find ruff. Please add ruff to your python environment"
        )


def get_ruff_config(config: Config) -> Config:
    return config.get("tool", "autohooks", "plugins", "ruff")


def ensure_iterable(value: Union[str, List[str]]) -> List[str]:
    if isinstance(value, str):
        return [value]
    return value


def get_ruff_arguments(config: Optional[Config]) -> Iterable[str]:
    if not config:
        return DEFAULT_ARGUMENTS

    ruff_config = get_ruff_config(config)
    arguments = ensure_iterable(
        ruff_config.get_value("arguments", DEFAULT_ARGUMENTS)
    )

    return arguments


def precommit(
    config: Optional[Config] = None,
    report_progress: Optional[ReportProgress] = None,
    **kwargs,  # pylint: disable=unused-argument
) -> int:
    check_ruff_installed()

    files = [f for f in get_staged_status() if str(f.path).endswith(".py")]

    if not files:
        ok("No staged files to format.")
        return 0

    cmd = ["ruff", "check"] + get_ruff_arguments(get_ruff_config(config))

    if report_progress:
        report_progress.init(len(files))

    with stash_unstaged_changes(files):
        ret = 0
        for file in files:
            try:
                subprocess.run(
                    cmd + [str(file.absolute_path())],
                    check=True,
                    capture_output=True,
                )
                ok(f"Linting {file.path} was successful.")
            except subprocess.CalledProcessError as e:  # pylint: disable=C0103
                ret = e.returncode
                format_errors = (
                    e.stdout.decode(
                        encoding=sys.getdefaultencoding(), errors="replace"
                    )
                    .rstrip()
                    .split("\n")
                )
                for line in format_errors:
                    if ".py" in line:
                        error(line)
                    else:
                        out(line)
            finally:
                if report_progress:
                    report_progress.update()

        return ret
