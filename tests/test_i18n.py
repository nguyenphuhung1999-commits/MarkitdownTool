import unittest

from i18n import STRINGS, translate


class LocalizationTests(unittest.TestCase):
    def test_every_catalog_entry_has_english_and_vietnamese_text(self):
        for key, value in STRINGS.items():
            with self.subTest(key=key):
                self.assertEqual(len(value), 2)
                self.assertTrue(value[0])
                self.assertTrue(value[1])

    def test_english_is_default(self):
        self.assertEqual(translate("settings"), "Settings")

    def test_vietnamese_can_be_selected(self):
        self.assertEqual(translate("settings", "vi"), "Cài đặt")

    def test_template_values_are_interpolated_in_both_languages(self):
        self.assertEqual(translate("files_selected", "en", count=3), "Selected 3 files.")
        self.assertEqual(translate("files_selected", "vi", count=3), "Đã chọn 3 tệp.")


if __name__ == "__main__":
    unittest.main()