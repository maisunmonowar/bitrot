import unittest
from unittest.mock import patch

from bitRotChecker import FileScanner


class DuplicatePolicyTests(unittest.TestCase):
    def setUp(self):
        self.scanner = FileScanner(".")
        self.checksum = "a" * 64

    def test_copy_count_policy_boundaries(self):
        cases = (
            ("two copies", ("volume-a", "volume-b"), False),
            ("three copies split 2+1", ("volume-a", "volume-a", "volume-b"), False),
            ("three copies on one volume", ("volume-a",) * 3, True),
            ("four copies split 2+2", ("volume-a", "volume-a", "volume-b", "volume-b"), True),
            ("four copies across four volumes", tuple(f"volume-{i}" for i in range(4)), True),
        )

        for description, volumes, expected in cases:
            with self.subTest(description=description):
                paths = [f"/scan/{description}/{i}.bin" for i in range(len(volumes))]
                path_volumes = dict(zip(paths, volumes))
                self.scanner.restructured_dict = {
                    self.checksum: [{"fullpath": path} for path in paths]
                }

                with patch.object(
                    self.scanner,
                    "get_physical_drive",
                    side_effect=path_volumes.__getitem__,
                ):
                    result = self.scanner.find_duplicate_files()

                self.assertEqual(self.checksum in result, expected)


if __name__ == "__main__":
    unittest.main()
