import unittest
from unittest.mock import patch

from autohooks.plugins.ruff.utils import (
    check_ruff_installed,
    get_ruff_arguments,
)


class GetRuffArgumentsTestCase(unittest.TestCase):
    def test_get_default_ruff_arguments(self):
        args = get_ruff_arguments(None, ["foo", "bar"])
        self.assertEqual(args, ["foo", "bar"])
        self.assertIsInstance(args, list, "ensures args is a list")


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
