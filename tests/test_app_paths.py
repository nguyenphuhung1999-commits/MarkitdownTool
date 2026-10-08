import tempfile
import unittest
from pathlib import Path

from app_paths import (
    APP_NAME,
    build_app_paths,
    copy_data_preserving_existing,
    find_application_resource,
    local_app_data,
    migrate_legacy_config,
)


class AppPathsTests(unittest.TestCase):
    def test_application_resource_lookup_checks_install_bundle_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            install = root / "install"
            bundle = root / "bundle"
            source = root / "source"
            bundle.mkdir()
            source.mkdir()
            legal_file = source / "LICENSE.md"
            legal_file.write_text("license", encoding="utf-8")

            self.assertEqual(find_application_resource("LICENSE.md", install, bundle, source), legal_file)
            with self.assertRaises(ValueError):
                find_application_resource("../LICENSE.md", install, bundle, source)

    def test_default_paths_use_per_user_local_app_data(self):
        paths = build_app_paths(Path(r"C:\Apps\MarkitdownTool"), Path(r"C:\Users\User\AppData\Local"))

        self.assertEqual(paths.install_dir, Path(r"C:\Apps\MarkitdownTool"))
        self.assertEqual(paths.settings_dir, Path(r"C:\Users\User\AppData\Local") / APP_NAME)
        self.assertEqual(paths.data_dir, paths.settings_dir)
        self.assertEqual(paths.tessdata_dir, paths.data_dir / "tesseract" / "tessdata")

    def test_user_can_configure_a_separate_data_directory(self):
        paths = build_app_paths(Path("app"), Path("local"), Path("D:/MarkitdownData"))

        self.assertEqual(paths.data_dir, Path("D:/MarkitdownData"))
        self.assertEqual(paths.config_file, Path("local") / APP_NAME / "config.json")

    def test_data_copy_never_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "old"
            destination = root / "new"
            source.mkdir()
            destination.mkdir()
            (source / "existing.txt").write_text("old", encoding="utf-8")
            (destination / "existing.txt").write_text("keep", encoding="utf-8")
            (source / "new.txt").write_text("copy", encoding="utf-8")

            copy_data_preserving_existing(source, destination)

            self.assertEqual((destination / "existing.txt").read_text(encoding="utf-8"), "keep")
            self.assertEqual((destination / "new.txt").read_text(encoding="utf-8"), "copy")
            self.assertTrue((source / "existing.txt").exists())

    def test_data_copy_rejects_a_nested_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "data"
            source.mkdir()
            with self.assertRaisesRegex(ValueError, "inside"):
                copy_data_preserving_existing(source, source / "nested")

    def test_legacy_config_is_copied_only_when_new_config_is_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            legacy = root / "old" / "config.json"
            current = root / "new" / "config.json"
            legacy.parent.mkdir()
            legacy.write_text("legacy", encoding="utf-8")

            self.assertTrue(migrate_legacy_config(legacy, current))
            self.assertEqual(current.read_text(encoding="utf-8"), "legacy")
            self.assertFalse(migrate_legacy_config(legacy, current))
            self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy")

    def test_local_app_data_prefers_windows_environment(self):
        self.assertEqual(local_app_data({"LOCALAPPDATA": r"C:\Users\User\AppData\Local"}), Path(r"C:\Users\User\AppData\Local"))


if __name__ == "__main__":
    unittest.main()