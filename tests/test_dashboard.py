import unittest
from datetime import datetime, timezone

from spotme.dashboard import build_dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 9, 30, tzinfo=timezone.utc)
        self.config = {"masa_masuk": "08:00", "masa_keluar": "17:00",
                       "auto_pergerakan": True}

    def test_portal_state_is_never_claimed_as_authenticated(self):
        joined = "\n".join(build_dashboard(self.config, {}, True, self.now))
        self.assertIn("Login portal       : BELUM DISAHKAN", joined)
        self.assertIn("tiada rekod dihantar ke portal", joined.lower())

    def test_movement_waits_for_confirmed_checkin(self):
        joined = "\n".join(build_dashboard(self.config, {}, True, self.now))
        self.assertIn("MENUNGGU pengesahan daftar masuk", joined)

    def test_next_hourly_movement_is_shown(self):
        state = {"attendance_checkin_date": "2026-11-12",
                 "attendance_checkin_at": "2026-11-12T08:00:00+00:00"}
        lines = build_dashboard(self.config, state, True, self.now)
        self.assertTrue(any("jam ke-2: 10:00" in line for line in lines))

    def test_checkout_stops_movement(self):
        state = {"attendance_checkin_date": "2026-11-12",
                 "attendance_checkout_date": "2026-11-12"}
        joined = "\n".join(build_dashboard(self.config, state, True, self.now))
        self.assertIn("DIHENTIKAN", joined)
        self.assertIn("Jadual hari ini selesai.", joined)


if __name__ == "__main__":
    unittest.main()
