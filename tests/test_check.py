# SPDX-FileCopyrightText: 2023-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from autohooks.api.git import StatusEntry
from autohooks.config import AutohooksConfig
from autohooks.precommit.run import ReportProgress
from pontos.testing import temp_file

from autohooks.plugins.ruff.check import (
    get_ruff_check_config,
    precommit,
)


def get_test_config_path(name):
    return Path(__file__).parent / name


class AutohooksRuffCheckTestCase(TestCase):
    def test_get_ruff_config(
        self,
    ):
        autohooks_config = AutohooksConfig.from_string(
            """
[tool.autohooks.plugins.ruff]
arguments = [
    "--test", "foo,bar",
    "--foo", "bar",
]
"""
        )

        ruff_config = get_ruff_check_config(autohooks_config.get_config())
        self.assertEqual(
            ruff_config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )

    def test_get_ruff_config_prefer_check_config(
        self,
    ):
        autohooks_config = AutohooksConfig.from_string(
            """
[tool.autohooks.plugins.ruff]
arguments = [
    "--bar", "foo,bar",
    "--baz", "bar",
]
[tool.autohooks.plugins.ruff.check]
arguments = [
    "--test", "foo,bar",
    "--foo", "bar",
]
"""
        )

        ruff_config = get_ruff_check_config(autohooks_config.get_config())
        self.assertEqual(
            ruff_config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )

    @patch("autohooks.plugins.ruff.check.get_staged_status")
    def test_precommit_no_files(
        self,
        get_staged_status_mock: MagicMock,
    ):
        get_staged_status_mock.return_value = []
        ret = precommit()

        self.assertEqual(ret, 0)

    @patch("autohooks.plugins.ruff.check.ok")
    @patch("autohooks.plugins.ruff.check.out")
    @patch("autohooks.plugins.ruff.check.error")
    @patch("autohooks.plugins.ruff.check.get_staged_status")
    def test_precommit_errors(
        self,
        get_staged_status_mock: MagicMock,
        error_mock: MagicMock,
        out_mock: MagicMock,
        ok_mock: MagicMock,
    ):
        config = AutohooksConfig.from_string("")
        code = """import subprocess

status = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
"""

        with temp_file(code, name="test.py") as file:
            get_staged_status_mock.return_value = [
                StatusEntry(
                    status_string=f"M  {file.name}",
                    root_path=file.parent,
                )
            ]

            ret = precommit(config.get_config())

            ok_mock.assert_not_called()
            out_mock.assert_called_once_with("Found 1 error.")
            error_mock.assert_called_once_with(
                f"{file.absolute()}:4:5: F821 Undefined name `cmd`"
            )

            self.assertEqual(ret, 1)

    @patch("autohooks.plugins.ruff.check.ok")
    @patch("autohooks.plugins.ruff.check.out")
    @patch("autohooks.plugins.ruff.check.error")
    @patch("autohooks.plugins.ruff.check.get_staged_status")
    def test_precommit_ok(
        self,
        get_staged_status_mock: MagicMock,
        error_mock: MagicMock,
        out_mock: MagicMock,
        ok_mock: MagicMock,
    ):
        progress = MagicMock(spec=ReportProgress)
        config = AutohooksConfig.from_string("")
        get_staged_status_mock.return_value = [
            StatusEntry(
                status_string="M  test_check.py",
                root_path=Path(__file__).parent,
            )
        ]
        ret = precommit(config.get_config(), progress)

        progress.init.assert_called_once_with(1)
        error_mock.assert_not_called()
        out_mock.assert_not_called()
        ok_mock.assert_called_once_with("Linting test_check.py was successful.")
        progress.update.assert_called_once()

        # Returncode 0 -> no errors
        self.assertEqual(ret, 0)
