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

    def test_portal_inspection_finds_routes_from_same_origin_scripts(self):
        client = SpotMeAPI()
        html_response = MagicMock()
        html_response.status = 200
        html_response.read.return_value = b'<html><script src="/assets/app.js"></script></html>'
        html_response.geturl.return_value = "https://spotme.jdn.gov.my/"
        js_response = MagicMock()
        js_response.read.return_value = b'const login="/api/v2/login"; const daily="/api/harian";'
        js_response.geturl.return_value = "https://spotme.jdn.gov.my/assets/app.js"

        with patch("spotme.api.urllib.request.urlopen") as urlopen:
            urlopen.side_effect = [
                MagicMock(__enter__=MagicMock(return_value=html_response),
                          __exit__=MagicMock(return_value=False)),
                MagicMock(__enter__=MagicMock(return_value=js_response),
                          __exit__=MagicMock(return_value=False)),
            ]
            result = client.inspect_portal()

        self.assertTrue(result["reachable"])
        self.assertEqual(result["scripts_scanned"], 1)
        self.assertIn("/api/v2/login", result["routes"])
        self.assertIn("/api/harian", result["routes"])

    def test_portal_inspection_does_not_fetch_off_origin_script(self):
        client = SpotMeAPI()
        html_response = MagicMock()
        html_response.status = 200
        html_response.read.return_value = b'<script src="https://evil.example/app.js"></script>'
        html_response.geturl.return_value = "https://spotme.jdn.gov.my/"
        with patch("spotme.api.urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = html_response
            result = client.inspect_portal()
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(result["scripts_scanned"], 0)

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
