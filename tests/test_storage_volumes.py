import hashlib
import os
import tempfile
import unittest
from unittest.mock import patch

from bitRotChecker import FileScanner


def write_file(path, content):
    with open(path, "wb") as file:
        file.write(content)
    return path


class StorageVolumeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.scan_root = os.path.join(self.temp_dir.name, "scan")
        os.makedirs(self.scan_root)
        self.scanner = FileScanner(self.scan_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_different_folders_on_same_volume_have_same_id(self):
        first_dir = os.path.join(self.scan_root, "first")
        second_dir = os.path.join(self.scan_root, "second", "nested")
        os.makedirs(first_dir)
        os.makedirs(second_dir)
        first = write_file(os.path.join(first_dir, "one.bin"), b"one")
        second = write_file(os.path.join(second_dir, "two.bin"), b"two")

        first_volume = self.scanner.get_storage_volume(first)
        second_volume = self.scanner.get_storage_volume(second)

        self.assertIsNotNone(first_volume)
        self.assertEqual(first_volume, second_volume)

    def test_separate_volumes_are_distinguished_when_available(self):
        if os.name == "nt":
            candidates = [f"{letter}:\\" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        else:
            candidates = ["/", "/tmp", "/proc", "/dev", "/sys", "/run"]
        volumes = {
            self.scanner.get_storage_volume(path)
            for path in candidates
            if os.path.exists(path)
        }
        volumes.discard(None)

        if len(volumes) < 2:
            self.skipTest("host exposes fewer than two identifiable volumes")
        self.assertGreaterEqual(len(volumes), 2)

    def test_missing_path_has_unknown_volume(self):
        self.assertIsNone(self.scanner.get_storage_volume(os.path.join(self.scan_root, "missing.bin")))

    def test_uncertain_volume_prevents_duplicate_cleanup(self):
        content = b"four copies"
        checksum = hashlib.sha256(content).hexdigest()
        paths = [
            write_file(os.path.join(self.scan_root, f"{index}.bin"), content)
            for index in range(4)
        ]
        self.scanner.restructured_dict[checksum] = [
            {"fullpath": path, "size": len(content)} for path in paths
        ]
        volume_ids = {
            paths[0]: ("posix", 1),
            paths[1]: ("posix", 2),
            paths[2]: ("posix", 3),
            paths[3]: None,
        }

        with patch.object(
            self.scanner,
            "get_storage_volume",
            side_effect=volume_ids.__getitem__,
        ):
            duplicates = self.scanner.find_duplicate_files()
            self.assertIn(checksum, duplicates)
            with self.assertRaisesRegex(ValueError, "mounted volume identity is unknown"):
                self.scanner.build_duplicate_deletion_plan(duplicates)

        self.assertTrue(all(os.path.isfile(path) for path in paths))

    def test_uncertain_volume_does_not_guess_per_volume_limit(self):
        content = b"three copies"
        checksum = hashlib.sha256(content).hexdigest()
        paths = [
            write_file(os.path.join(self.scan_root, f"{index}.bin"), content)
            for index in range(3)
        ]
        self.scanner.restructured_dict[checksum] = [
            {"fullpath": path, "size": len(content)} for path in paths
        ]
        volume_ids = {
            paths[0]: ("posix", 1),
            paths[1]: ("posix", 1),
            paths[2]: None,
        }

        with patch.object(
            self.scanner,
            "get_storage_volume",
            side_effect=volume_ids.__getitem__,
        ):
            self.assertEqual(self.scanner.find_duplicate_files(), [])
            self.assertIn(checksum, self.scanner.uncertain_volume_checksums)


if __name__ == "__main__":
    unittest.main()
