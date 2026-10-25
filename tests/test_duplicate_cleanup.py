import hashlib
import os
import tempfile
import unittest

from bitRotChecker import FileScanner


def write_file(path, content):
    with open(path, "wb") as file:
        file.write(content)
    return path


def checksum(content):
    return hashlib.sha256(content).hexdigest()


class DuplicateCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.scan_root = os.path.join(self.temp_dir.name, "scan")
        os.makedirs(self.scan_root)
        self.scanner = FileScanner(self.scan_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_group(self, digest, paths):
        self.scanner.restructured_dict[digest] = [
            {"fullpath": path, "size": os.path.getsize(path)} for path in paths
        ]

    def test_root_level_duplicates_keep_one_copy(self):
        content = b"same root content"
        paths = [
            write_file(os.path.join(self.scan_root, name), content)
            for name in ("one.bin", "two.bin", "three.bin")
        ]
        self.add_group(checksum(content), paths)

        plan, retained = self.scanner.build_duplicate_deletion_plan([checksum(content)])
        self.assertEqual(len(plan[checksum(content)]), 2)
        self.scanner.execute_duplicate_deletion_plan(plan, retained)

        self.assertTrue(os.path.isfile(retained[checksum(content)]))
        self.assertEqual(sum(os.path.exists(path) for path in paths), 1)

    def test_nested_duplicates_are_in_scope_and_keep_one_copy(self):
        nested = os.path.join(self.scan_root, "nested")
        os.makedirs(nested)
        content = b"same nested content"
        paths = [
            write_file(os.path.join(nested, name), content)
            for name in ("one.bin", "two.bin", "three.bin")
        ]
        self.add_group(checksum(content), paths)

        plan, retained = self.scanner.build_duplicate_deletion_plan([checksum(content)])
        self.scanner.execute_duplicate_deletion_plan(plan, retained)

        self.assertTrue(os.path.isfile(retained[checksum(content)]))
        self.assertEqual(sum(os.path.exists(path) for path in paths), 1)

    def test_copy_outside_scan_root_is_retained(self):
        content = b"external safe copy"
        inside = write_file(os.path.join(self.scan_root, "inside.bin"), content)
        outside = write_file(os.path.join(self.temp_dir.name, "outside.bin"), content)
        self.add_group(checksum(content), [inside, outside])

        plan, retained = self.scanner.build_duplicate_deletion_plan([checksum(content)])
        self.assertEqual(plan[checksum(content)], [inside])
        self.assertEqual(retained[checksum(content)], outside)
        self.scanner.execute_duplicate_deletion_plan(plan, retained)

        self.assertFalse(os.path.exists(inside))
        self.assertTrue(os.path.isfile(outside))

    def test_no_verified_copy_aborts_without_deleting(self):
        content = b"current file content"
        path = write_file(os.path.join(self.scan_root, "file.bin"), content)
        self.add_group("0" * 64, [path])

        with self.assertRaises(ValueError):
            self.scanner.build_duplicate_deletion_plan(["0" * 64])
        self.assertTrue(os.path.isfile(path))

    def test_nearby_sibling_directory_is_not_in_scan_scope(self):
        content = b"sibling"
        sibling = os.path.join(self.temp_dir.name, "scan-other")
        os.makedirs(sibling)
        path = write_file(os.path.join(sibling, "file.bin"), content)
        self.add_group(checksum(content), [path])

        plan, retained = self.scanner.build_duplicate_deletion_plan([checksum(content)])

        self.assertEqual(plan[checksum(content)], [])
        self.assertEqual(retained[checksum(content)], path)


if __name__ == "__main__":
    unittest.main()
