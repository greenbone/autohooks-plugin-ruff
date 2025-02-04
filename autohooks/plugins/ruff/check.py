# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import subprocess
import sys
from typing import Optional

from autohooks.api import error, ok, out
from autohooks.api.git import get_staged_status, stash_unstaged_changes
from autohooks.config import Config
from autohooks.plugins.ruff.utils import (
    check_ruff_installed,
    get_ruff_arguments,
    get_ruff_config,
)
from autohooks.precommit.run import ReportProgress

DEFAULT_ARGUMENTS = ["--output-format=concise"]


def get_ruff_check_config(config: Optional[Config]) -> Optional[Config]:
    config = get_ruff_config(config)
    if config and config.has_key("check"):
        config = config.get("check")
    return config


def precommit(
    config: Optional[Config] = None,
    report_progress: Optional[ReportProgress] = None,
    **kwargs,  # pylint: disable=unused-argument
) -> int:
    check_ruff_installed()

    files = [f for f in get_staged_status() if str(f.path).endswith(".py")]

    if not files:
        ok("No staged files to lint.")
        return 0

    cmd = ["ruff", "check"] + get_ruff_arguments(
        get_ruff_check_config(config), DEFAULT_ARGUMENTS
    )

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
            except subprocess.CalledProcessError as e:
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
