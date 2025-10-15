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

from autohooks.plugins.ruff.format import (
    get_ruff_format_config,
    precommit,
)


class AutohooksRuffFormatTestCase(TestCase):
    def test_get_ruff_format_config(
        self,
    ):
        autohooks_config = AutohooksConfig.from_string(
            """
[tool.autohooks.plugins.ruff]
arguments = ["--bar", "foo,bar", "--baz", "bar"]

[tool.autohooks.plugins.ruff.format]
arguments = ["--test", "foo,bar", "--foo", "bar"]
"""
        )

        ruff_config = get_ruff_format_config(autohooks_config.get_config())
        self.assertEqual(
            ruff_config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )

    @patch("autohooks.plugins.ruff.format.get_staged_status")
    def test_precommit_no_files(
        self,
        get_staged_status_mock: MagicMock,
    ):
        get_staged_status_mock.return_value = []
        ret = precommit()

        self.assertEqual(ret, 0)

    @patch("autohooks.plugins.ruff.format.ok")
    @patch("autohooks.plugins.ruff.format.error")
    @patch("autohooks.plugins.ruff.format.get_staged_status")
    @patch("autohooks.plugins.ruff.format.stage_files_from_status_list")
    def test_precommit_error(
        self,
        stage_files_from_status_list_mock: MagicMock,
        get_staged_status_mock: MagicMock,
        error_mock: MagicMock,
        ok_mock: MagicMock,
    ):
        config = AutohooksConfig.from_string("")
        code = """import subprocess

status = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
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
            error_mock.assert_called()
            stage_files_from_status_list_mock.assert_not_called()
            self.assertIn(
                f"Failed formatting {file.name}", error_mock.call_args[0][0]
            )

            self.assertEqual(ret, 1)

    @patch("autohooks.plugins.ruff.format.ok")
    @patch("autohooks.plugins.ruff.format.error")
    @patch("autohooks.plugins.ruff.format.get_staged_status")
    @patch("autohooks.plugins.ruff.format.stage_files_from_status_list")
    def test_precommit_ok(
        self,
        stage_files_from_status_list_mock: MagicMock,
        get_staged_status_mock: MagicMock,
        error_mock: MagicMock,
        ok_mock: MagicMock,
    ):
        config = AutohooksConfig.from_string("")
        progress = MagicMock(spec=ReportProgress)
        status = StatusEntry(
            status_string="M  test_format.py",
            root_path=Path(__file__).parent,
        )
        get_staged_status_mock.return_value = [status]
        ret = precommit(config.get_config(), progress)
        progress.init.assert_called_once_with(1)

        error_mock.assert_not_called()
        ok_mock.assert_called_once_with(
            "Formatting test_format.py was successful."
        )
        progress.update.assert_called_once()
        stage_files_from_status_list_mock.assert_called_once_with([status])

        # Returncode 0 -> no errors
        self.assertEqual(ret, 0)
