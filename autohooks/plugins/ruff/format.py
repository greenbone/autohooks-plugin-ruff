# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import subprocess
from typing import Optional

from autohooks.api import error, ok
from autohooks.api.git import (
    get_staged_status,
    stage_files_from_status_list,
    stash_unstaged_changes,
)
from autohooks.config import Config
from autohooks.plugins.ruff.utils import (
    check_ruff_installed,
    get_ruff_arguments,
    get_ruff_config,
)
from autohooks.precommit.run import ReportProgress

DEFAULT_ARGUMENTS = []


def get_ruff_format_config(config: Optional[Config]) -> Optional[Config]:
    config = get_ruff_config(config)
    return config.get("format") if config else None


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

    cmd = ["ruff", "format"] + get_ruff_arguments(
        get_ruff_format_config(config), DEFAULT_ARGUMENTS
    )

    if report_progress:
        report_progress.init(len(files))

    with stash_unstaged_changes(files):
        has_error = False
        for file in files:
            try:
                subprocess.run(
                    cmd + [str(file.absolute_path())],
                    check=True,
                    capture_output=True,
                )
                ok(f"Formatting {file.path} was successful.")
                if report_progress:
                    report_progress.update()
            except subprocess.CalledProcessError as e:
                error(f"Failed formatting {file.path}. {e.stderr.decode()}")
                has_error = True

        if not has_error:
            stage_files_from_status_list(files)

        return 1 if has_error else 0
