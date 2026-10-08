import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from language_manager import install_language, uninstall_language


class LanguageManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_install_downloads_to_application_managed_tessdata(self):
        payload = b"traineddata" * 200

        class Response:
            headers = {"Content-Length": str(len(payload))}

            def __enter__(self):
                self.offset = 0
                return self

            def __exit__(self, *_args):
                return False

            def read(self, size):
                chunk = payload[self.offset:self.offset + size]
                self.offset += len(chunk)
                return chunk

        with patch("language_manager.urllib.request.urlopen", return_value=Response()) as urlopen:
            target = install_language("vie", self.project_dir)

        self.assertEqual(target, self.project_dir / "tesseract" / "tessdata" / "vie.traineddata")
        self.assertEqual(target.read_bytes(), payload)
        self.assertIn("tesseract-ocr/tessdata_fast", urlopen.call_args.args[0].full_url)

    def test_uninstall_only_removes_application_managed_package(self):
        managed_dir = self.project_dir / "tesseract" / "tessdata"
        managed_dir.mkdir(parents=True)
        managed_package = managed_dir / "vie.traineddata"
        managed_package.write_bytes(b"model")

        self.assertTrue(uninstall_language("vie", self.project_dir))
        self.assertFalse(managed_package.exists())
        self.assertFalse(uninstall_language("eng", self.project_dir))

    def test_invalid_language_code_is_rejected_before_download(self):
        with patch("language_manager.urllib.request.urlopen") as urlopen:
            with self.assertRaises(ValueError):
                install_language("../eng", self.project_dir)

        urlopen.assert_not_called()

    def test_orientation_data_cannot_be_removed(self):
        with self.assertRaisesRegex(ValueError, "osd"):
            uninstall_language("osd", self.project_dir)


if __name__ == "__main__":
    unittest.main()