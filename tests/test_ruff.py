# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from autohooks.api.git import StatusEntry
from autohooks.config import load_config_from_pyproject_toml

from autohooks.plugins.ruff.ruff import (DEFAULT_ARGUMENTS,
                                         check_ruff_installed,
                                         get_ruff_arguments, get_ruff_config,
                                         precommit)


def get_test_config_path(name):
    return Path(__file__).parent / name


class AutohooksRuffTestCase(TestCase):
    def test_ruff_installed(self):
        with self.assertRaises(RuntimeError), patch(
            "importlib.util.find_spec", return_value=None
        ):
            check_ruff_installed()

    def test_get_ruff_config(self):
        config_path = get_test_config_path("pyproject.test.toml")
        self.assertTrue(config_path.is_file())

        autohooksconfig = load_config_from_pyproject_toml(config_path)

        ruff_config = get_ruff_config(autohooksconfig.get_config())
        self.assertEqual(
            ruff_config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )

    def test_get_ruff_arguments(self):
        args = get_ruff_arguments(None)
        self.assertEqual(args, DEFAULT_ARGUMENTS)

        config_path = get_test_config_path("pyproject.test.toml")
        args = get_ruff_arguments(
            load_config_from_pyproject_toml(config_path).get_config()
        )
        self.assertEqual(args, ["--test", "foo,bar", "--foo", "bar"])

    @patch("autohooks.plugins.ruff.ruff.get_staged_status")
    @patch("autohooks.plugins.ruff.ruff.ok")
    def test_precommit_no_files(self, _ok_mock, get_staged_status_mock):
        get_staged_status_mock.return_value = []
        ret = precommit()
        self.assertFalse(ret)

    @unittest.skip("still to do")
    def test_precommit_errors(
        self,
        staged_mock,
        _error_mock,
        _out_mock,
        _ok_mock,  # _mock_stdout
    ):
        ret = precommit()
        self.assertTrue(ret)

    @patch("autohooks.plugins.ruff.ruff.get_ruff_arguments")
    @patch("autohooks.plugins.ruff.ruff.get_ruff_config")
    @patch("autohooks.plugins.ruff.ruff.ok")
    @patch("autohooks.plugins.ruff.ruff.out")
    @patch("autohooks.plugins.ruff.ruff.error")
    @patch("autohooks.plugins.ruff.ruff.get_staged_status")
    def test_precommit_ok(
        self,
        staged_mock,
        _error_mock,
        _out_mock,
        _ok_mock,  # _mock_stdout
        _get_ruff_config,
        _get_ruff_arguments_mock,
    ):
        _get_ruff_arguments_mock.return_value = DEFAULT_ARGUMENTS

        test_case_list = [
            "test_ruff.exe",
            str(Path(__file__)),
        ]
        for test_case in test_case_list:
            with self.subTest(test_case):
                staged_mock.return_value = [
                    StatusEntry(
                        status_string=f"M  {test_case}",
                        root_path=Path(__file__).parent,
                    )
                ]
                ret = precommit()
                # Returncode 0 -> no errors
                self.assertFalse(ret)
