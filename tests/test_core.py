import unittest
from spotme.config import DEFAULTS
from spotme.scheduler import valid_time


class CoreTests(unittest.TestCase):
    def test_default_schedule(self):
        self.assertEqual(DEFAULTS["masa_masuk"], "07:25")
        self.assertEqual(DEFAULTS["masa_keluar"], "16:35")
        self.assertTrue(DEFAULTS["auto_pergerakan"])

    def test_valid_time(self):
        self.assertTrue(valid_time("07:25"))
        self.assertTrue(valid_time("16:35"))
        self.assertFalse(valid_time("25:61"))
        self.assertFalse(valid_time("7.25"))
        self.assertFalse(valid_time(""))

    def test_menu_configuration_has_no_workday_setting(self):
        self.assertNotIn("hari_bekerja", DEFAULTS)


if __name__ == "__main__":
    unittest.main()
