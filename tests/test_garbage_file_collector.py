import json
import os
import tempfile
import unittest
from unittest.mock import patch

from garbageFileCollector import FileDeleter


def write_file(path, content):
    with open(path, "wb") as file:
        file.write(content)
    return path


class GarbageFileCollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_path = os.path.join(self.temp_dir.name, "delete_list.json")
        self.deleter = FileDeleter(self.json_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_same_name_and_content_at_other_path_is_not_deleted(self):
        marked_dir = os.path.join(self.temp_dir.name, "marked")
        other_dir = os.path.join(self.temp_dir.name, "other")
        os.makedirs(marked_dir)
        os.makedirs(other_dir)
        content = b"identical contents"
        marked = write_file(os.path.join(marked_dir, "same.bin"), content)
        other = write_file(os.path.join(other_dir, "same.bin"), content)
        self.deleter.add_file_to_delete_list(marked)
        self.deleter.save_delete_list()

        with patch("builtins.input", return_value="y"):
            self.deleter.cleanup_folder(self.temp_dir.name)

        self.assertFalse(os.path.exists(marked))
        self.assertTrue(os.path.isfile(other))

    def test_renamed_file_is_not_deleted_by_old_path_entry(self):
        folder = os.path.join(self.temp_dir.name, "folder")
        os.makedirs(folder)
        original = write_file(os.path.join(folder, "before.bin"), b"content")
        self.deleter.add_file_to_delete_list(original)
        renamed = os.path.join(folder, "after.bin")
        os.rename(original, renamed)
        self.deleter.save_delete_list()

        self.deleter.cleanup_folder(folder)

        self.assertTrue(os.path.isfile(renamed))

    def test_folder_marking_matches_only_files_under_marked_folder(self):
        marked_dir = os.path.join(self.temp_dir.name, "marked")
        other_dir = os.path.join(self.temp_dir.name, "other")
        os.makedirs(marked_dir)
        os.makedirs(other_dir)
        content = b"folder contents"
        marked = write_file(os.path.join(marked_dir, "same.bin"), content)
        other = write_file(os.path.join(other_dir, "same.bin"), content)
        self.deleter.add_folder_to_delete_list(marked_dir)
        self.deleter.save_delete_list()

        with patch("builtins.input", return_value="y"):
            self.deleter.cleanup_folder(self.temp_dir.name)

        self.assertFalse(os.path.exists(marked))
        self.assertTrue(os.path.isfile(other))

    def test_legacy_entries_without_path_are_ignored(self):
        folder = os.path.join(self.temp_dir.name, "folder")
        os.makedirs(folder)
        path = write_file(os.path.join(folder, "legacy.bin"), b"legacy")
        with open(self.json_path, "w") as file:
            json.dump(
                [{"name": "legacy.bin", "size": 6, "checksum": "legacy"}],
                file
            )
        self.deleter = FileDeleter(self.json_path)

        self.deleter.cleanup_folder(folder)

        self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main()
