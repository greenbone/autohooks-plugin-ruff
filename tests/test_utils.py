import unittest
from unittest.mock import patch

from autohooks.config import AutohooksConfig
from autohooks.plugins.ruff.utils import (
    check_ruff_installed,
    get_ruff_arguments,
    get_ruff_config,
)


class GetRuffArgumentsTestCase(unittest.TestCase):
    def test_get_default_ruff_arguments(self):
        args = get_ruff_arguments(None, ["foo", "bar"])
        self.assertEqual(args, ["foo", "bar"])
        self.assertIsInstance(args, list, "ensures args is a list")

    def test_get_ruff_arguments(self):
        config = AutohooksConfig.from_string(
            "arguments = ['--test', 'foo,bar', '--foo', 'bar']"
        )
        args = get_ruff_arguments(config.get_config(), ["foo", "bar"])
        self.assertEqual(
            args,
            ["--test", "foo,bar", "--foo", "bar"],
        )

    def test_get_ruff_arguments_is_list(self):
        config = AutohooksConfig.from_string("arguments = 'foo'")
        args = get_ruff_arguments(config.get_config(), ["foo", "bar"])
        self.assertEqual(args, ["foo"])


class CheckRuffInstalledTestCase(unittest.TestCase):
    def test_ruff_installed(self):
        with (
            self.assertRaisesRegex(
                RuntimeError,
                "Could not find ruff. Please add ruff to your python "
                "environment",
            ),
            patch("importlib.util.find_spec", return_value=None),
        ):
            check_ruff_installed()


class GetRufConfigTestCase(unittest.TestCase):
    def test_get_empty_ruff_config(
        self,
    ):
        autohooks_config = AutohooksConfig.from_string(
            """
            """
        )

        config = get_ruff_config(autohooks_config.get_config())
        self.assertTrue(config.is_empty())

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

        config = get_ruff_config(autohooks_config.get_config())
        self.assertEqual(
            config.get_value("arguments"),
            ["--test", "foo,bar", "--foo", "bar"],
        )
