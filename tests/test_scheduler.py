import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from spotme.scheduler import Scheduler, valid_time


class SchedulerTests(unittest.TestCase):
    def make_scheduler(self, callback=None):
        return Scheduler(lambda: {}, callback or (lambda event: None))

    def test_checkin_confirmation_sets_date_and_timestamp(self):
        when = datetime(2026, 11, 11, 8, 0, tzinfo=timezone.utc)
        scheduler = self.make_scheduler()
        with patch("spotme.scheduler.save_state"):
            scheduler.confirm_checkin(when)
        self.assertEqual(scheduler.fired["attendance_checkin_date"], "2026-11-11")
        self.assertEqual(scheduler.fired["attendance_checkin_at"], when.isoformat())
        self.assertEqual(scheduler.attendance_status(when), "DAFTAR MASUK DISAHKAN")

    def test_checkin_clears_checkout_marker(self):
        scheduler = self.make_scheduler()
        scheduler.fired["attendance_checkout_date"] = "2026-11-11"
        when = datetime(2026, 11, 11, 8, 0, tzinfo=timezone.utc)
        with patch("spotme.scheduler.save_state"):
            scheduler.confirm_checkin(when)
        self.assertNotIn("attendance_checkout_date", scheduler.fired)

    def test_checkout_status_takes_precedence(self):
        scheduler = self.make_scheduler()
        when = datetime(2026, 11, 11, 17, 0, tzinfo=timezone.utc)
        scheduler.fired.update({
            "attendance_checkin_date": "2026-11-11",
            "attendance_checkout_date": "2026-11-11",
        })
        self.assertEqual(scheduler.attendance_status(when), "DAFTAR KELUAR DISAHKAN")

    def test_attendance_status_resets_on_next_day(self):
        scheduler = self.make_scheduler()
        scheduler.fired["attendance_checkin_date"] = "2026-11-10"
        when = datetime(2026, 11, 11, 8, 0, tzinfo=timezone.utc)
        self.assertEqual(scheduler.attendance_status(when), "BELUM DAFTAR MASUK")

    def test_event_is_emitted_only_once(self):
        calls = []
        scheduler = self.make_scheduler(calls.append)
        with patch("spotme.scheduler.save_state"):
            self.assertTrue(scheduler._emit_once("event-1", {"title": "Test"}))
            self.assertFalse(scheduler._emit_once("event-1", {"title": "Test"}))
        self.assertEqual(len(calls), 1)

    def test_failed_event_callback_can_be_retried(self):
        calls = []
        def callback(event):
            calls.append(event)
            if len(calls) == 1:
                raise RuntimeError("temporary failure")
        scheduler = self.make_scheduler(callback)
        with patch("spotme.scheduler.save_state"):
            self.assertFalse(scheduler._emit_once("event-1", {"title": "Test"}))
            self.assertNotIn("event-1", scheduler.fired)
            self.assertTrue(scheduler._emit_once("event-1", {"title": "Test"}))
        self.assertEqual(len(calls), 2)

    def test_non_positive_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            Scheduler(lambda: {}, lambda event: None, interval=0)

    def test_valid_time(self):
        self.assertTrue(valid_time("07:25"))
        self.assertFalse(valid_time("25:61"))
        self.assertFalse(valid_time("7:25"))
        self.assertFalse(valid_time("07:5"))
        self.assertFalse(valid_time("0"))


if __name__ == "__main__":
    unittest.main()
