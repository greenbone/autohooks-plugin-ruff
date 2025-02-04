# SPDX-FileCopyrightText: 2023-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pontos.testing import temp_file

from autohooks.api.git import StatusEntry
from autohooks.config import load_config_from_pyproject_toml
from autohooks.plugins.ruff.check import (
    DEFAULT_ARGUMENTS,
    get_ruff_arguments,
    get_ruff_config,
    precommit,
)


def get_test_config_path(name):
    return Path(__file__).parent / name


class AutohooksRuffCheckTestCase(TestCase):
    def test_get_ruff_config(
        self,
    ):
        config_path = get_test_config_path("pyproject.test.toml")
        self.assertTrue(config_path.is_file())

        autohooks_config = load_config_from_pyproject_toml(config_path)

        ruff_config = get_ruff_config(autohooks_config.get_config())
        self.assertEqual(
            ruff_config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )

    @patch("autohooks.plugins.ruff.check.get_ruff_config")
    def test_get_ruff_arguments(
        self,
        _get_ruff_config: MagicMock,
    ):
        config_path = get_test_config_path("pyproject.test.toml")
        args = get_ruff_arguments(
            load_config_from_pyproject_toml(config_path)
            .get_config()
            .get("tool", "autohooks", "plugins", "ruff"),
            DEFAULT_ARGUMENTS,
        )
        self.assertIsInstance(args, list, "ensures args is a list")
        self.assertEqual(args, ["--test", "foo,bar", "--foo", "bar"])

        _get_ruff_config.assert_not_called()

    @patch("autohooks.plugins.ruff.check.get_staged_status")
    def test_precommit_no_files(
        self,
        get_staged_status_mock: MagicMock,
    ):
        get_staged_status_mock.return_value = []
        ret = precommit()

        self.assertEqual(ret, 0)

    @patch("autohooks.plugins.ruff.check.get_ruff_arguments")
    @patch("autohooks.plugins.ruff.check.get_ruff_config")
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
        _get_ruff_config: MagicMock,
        get_ruff_arguments_mock: MagicMock,
    ):
        code = """import subprocess

status = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
"""
        get_ruff_arguments_mock.return_value = DEFAULT_ARGUMENTS

        with temp_file(code, name="test.py") as file:
            get_staged_status_mock.return_value = [
                StatusEntry(
                    status_string=f"M  {file.name}",
                    root_path=file.parent,
                )
            ]

            ret = precommit()

            ok_mock.assert_not_called()
            out_mock.assert_called_once_with("Found 1 error.")
            error_mock.assert_called_once_with(
                f"{file.absolute()}:4:5: F821 Undefined name `cmd`"
            )

            self.assertEqual(ret, 1)

    @patch("autohooks.plugins.ruff.check.get_ruff_arguments")
    @patch("autohooks.plugins.ruff.check.get_ruff_config")
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
        _get_ruff_config,
        get_ruff_arguments_mock: MagicMock,
    ):
        get_ruff_arguments_mock.return_value = DEFAULT_ARGUMENTS

        get_staged_status_mock.return_value = [
            StatusEntry(
                status_string="M  test_check.py",
                root_path=Path(__file__).parent,
            )
        ]
        ret = precommit()

        error_mock.assert_not_called()
        out_mock.assert_not_called()
        ok_mock.assert_called_once_with("Linting test_check.py was successful.")

        # Returncode 0 -> no errors
        self.assertEqual(ret, 0)
