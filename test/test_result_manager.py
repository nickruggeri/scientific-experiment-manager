import re
import unittest
from pathlib import Path

import numpy as np

from sem.manager import ResultManager
from sem.re_patterns import BOOL_PATTERN, FLOAT_PATTERN, INT_PATTERN

TEST_DIR = Path(__file__).absolute().parent


class TestManager(unittest.TestCase):

    root_dir = TEST_DIR / "sample_result_folder"

    def test_folder_parsing_full(self):
        # Test if full folder structure is parsed.
        parsers = [
            re.compile(
                f"K=(?P<K>{INT_PATTERN})_multiplier=(?P<multiplier>{FLOAT_PATTERN})"
            ),
            re.compile("results"),
            re.compile(f"sample_(?P<sample>{BOOL_PATTERN})"),
        ]
        self.assertTrue(self.root_dir.exists())

        manager = ResultManager(self.root_dir, parsers)
        manager.parse_paths()

        df = manager.df
        self.assertTrue(df.shape[0] == 12)
        self.assertTrue(
            list(df.columns)
            == [
                "__PATH__",
                "K",
                "multiplier",
                "sample",
            ]
        )

        gb = df.groupby(
            [
                "K",
                "multiplier",
                "sample",
            ]
        )
        self.assertTrue(gb.ngroups == 12)
        self.assertTrue(all(len(v) == 1 for v in gb.groups.values()))

        gb = df.groupby(["K"])
        self.assertTrue(gb.ngroups == 2)
        self.assertTrue(all(len(v) == 6 for v in gb.groups.values()))

    def get_partial_parse_manager(self):
        # Test if parsing works correctly when excluding some paths
        arguments = [
            {"multiplier": FLOAT_PATTERN, "K": INT_PATTERN},
            "results",
            "sample_True",
        ]
        manager = ResultManager.from_arguments(self.root_dir, arguments, auto_sort=True)
        manager.parse_paths()

        return arguments, manager

    def test_folder_parsing_partial(self):
        _, manager = self.get_partial_parse_manager()
        self.assertTrue(manager.df.shape == (6, 3))
        self.assertTrue(
            list(manager.df.columns)
            == [
                "__PATH__",
                "K",
                "multiplier",
            ]
        )

    def test_filtering_equal(self):
        _, manager = self.get_partial_parse_manager()
        filtered = manager.filter_results(equal={"K": "3"})
        self.assertTrue(filtered.shape == (3, 3))
        self.assertTrue(np.unique(filtered.K) == "3")

    def test_filtering_contained(self):
        _, manager = self.get_partial_parse_manager()
        filtered = manager.filter_results(contained={"K": ["2", "4"]})
        self.assertTrue(filtered.shape == (3, 3))
        self.assertTrue(np.unique(filtered.K) == "2")

    def test_path_creation(self):
        root = "/tmp"
        values = "folder_name"
        path = ResultManager.create_default_path(root, values)
        self.assertTrue(path == Path(root) / values)

        root = ".."
        values = [
            {"arg2": 1, "arg1": False, "abc": "abcd"},
            "subfolder",
            {"test": [1, 2, 3]},
        ]
        path = ResultManager.create_default_path(root, values, auto_sort=False)
        expected_path = (
            Path(root) / "arg2=1_arg1=False_abc=abcd" / "subfolder" / "test=[1, 2, 3]"
        )
        self.assertTrue(path == expected_path)

        path = ResultManager.create_default_path(root, values, auto_sort=True)
        expected_path = (
            Path(root) / "abc=abcd_arg1=False_arg2=1" / "subfolder" / "test=[1, 2, 3]"
        )
        self.assertTrue(path == expected_path)
