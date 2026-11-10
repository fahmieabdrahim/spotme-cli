import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from spotme.api import SpotMeAPI, SpotMeAPIError
from spotme.config import DEFAULTS
from spotme.scheduler import valid_time


class CoreTests(unittest.TestCase):
    def test_default_schedule_is_unset(self):
        self.assertEqual(DEFAULTS["masa_masuk"], "0")
        self.assertEqual(DEFAULTS["masa_keluar"], "0")
        self.assertFalse(DEFAULTS["auto_pergerakan"])

    def test_valid_time(self):
        self.assertTrue(valid_time("07:25"))
        self.assertTrue(valid_time("16:35"))
        self.assertFalse(valid_time("25:61"))
        self.assertFalse(valid_time("7.25"))
        self.assertFalse(valid_time(""))
        self.assertFalse(valid_time("0"))

    def test_menu_configuration_has_no_workday_setting(self):
        self.assertNotIn("hari_bekerja", DEFAULTS)

    def test_portal_connection_reports_http_status_without_reading_content(self):
        client = SpotMeAPI()
        response = MagicMock()
        response.status = 200
        with patch("spotme.api.urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = response
            self.assertEqual(client.check_portal_connection(), (True, 200))
            response.read.assert_not_called()

    def test_portal_connection_reports_network_failure(self):
        client = SpotMeAPI()
        with patch("spotme.api.urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
            self.assertEqual(client.check_portal_connection(), (False, None))

    def test_daily_movements_rejects_invalid_date_before_request(self):
        client = SpotMeAPI()
        with patch.object(client, "_request") as request:
            with self.assertRaises(ValueError):
                client.daily_movements("2026-02-30")
            request.assert_not_called()

    def test_daily_movements_rejects_non_iso_date(self):
        client = SpotMeAPI()
        with patch.object(client, "_request") as request:
            with self.assertRaises(ValueError):
                client.daily_movements("10/11/2026")
            request.assert_not_called()

    def test_http_error_does_not_expose_response_body(self):
        client = SpotMeAPI()
        error = urllib.error.HTTPError(
            "https://spotme.jdn.gov.my/api/checking",
            401,
            "Unauthorized",
            {},
            None,
        )
        with patch("spotme.api.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(SpotMeAPIError) as caught:
                client.check_eligibility()
        self.assertNotIn("password", str(caught.exception).lower())
        self.assertNotIn("unauthorized", str(caught.exception).lower())
        self.assertIn("HTTP 401", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
