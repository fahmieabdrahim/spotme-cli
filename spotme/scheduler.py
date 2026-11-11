from __future__ import annotations

import threading
from datetime import datetime, timedelta
from .config import load_state, save_state


def valid_time(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
        return False
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


class Scheduler:
    """In-process scheduler driven by the device's local clock."""

    def __init__(self, config_getter, callback, interval: float = 1.0):
        if interval <= 0:
            raise ValueError("interval mesti lebih besar daripada sifar")
        self.config_getter = config_getter
        self.callback = callback
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = None
        self.fired = load_state()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run, name="spotme-scheduler", daemon=True
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=max(5, self.interval + 1))

    def confirm_checkin(self, when: datetime | None = None) -> None:
        """Record the user's manual confirmation that portal check-in succeeded."""
        when = when or datetime.now().astimezone()
        day = when.date().isoformat()
        self.fired["attendance_checkin_date"] = day
        self.fired["attendance_checkin_at"] = when.isoformat()
        self.fired.pop("attendance_checkout_date", None)
        save_state(self.fired)

    def confirm_checkout(self, when: datetime | None = None) -> None:
        """Record the user's manual confirmation that portal check-out succeeded."""
        when = when or datetime.now().astimezone()
        self.fired["attendance_checkout_date"] = when.date().isoformat()
        save_state(self.fired)

    def attendance_status(self, when: datetime | None = None) -> str:
        when = when or datetime.now().astimezone()
        day = when.date().isoformat()
        if self.fired.get("attendance_checkout_date") == day:
            return "DAFTAR KELUAR DISAHKAN"
        if self.fired.get("attendance_checkin_date") == day:
            return "DAFTAR MASUK DISAHKAN"
        return "BELUM DAFTAR MASUK"

    def next_schedule(self, when: datetime | None = None) -> tuple[str, datetime] | None:
        """Return the next local reminder target; this does not claim portal login."""
        when = when or datetime.now().astimezone()
        day = when.date().isoformat()
        checked_in = self.fired.get("attendance_checkin_date") == day
        checked_out = self.fired.get("attendance_checkout_date") == day
        if checked_out:
            return None

        cfg = self.config_getter()
        key = "masa_keluar" if checked_in else "masa_masuk"
        label = "daftar keluar" if checked_in else "daftar masuk"
        value = cfg.get(key, "")
        if not valid_time(value):
            return None

        hour, minute = (int(part) for part in value.split(":"))
        target = when.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= when:
            target += timedelta(days=1)
        return label, target

    def _emit_once(self, event_id: str, event: dict) -> bool:
        """Emit an event once; failed callbacks remain eligible for retry."""
        if self.fired.get(event_id):
            return False
        try:
            self.callback(event)
        except Exception as exc:
            print(f"[RALAT] Peringatan '{event.get('title', event_id)}' gagal: {exc}")
            return False
        self.fired[event_id] = True
        save_state(self.fired)
        return True

    def _run(self):
        while not self.stop_event.is_set():
            try:
                cfg = self.config_getter()
                now = datetime.now().astimezone()
                day = now.date().isoformat()
                current = now.strftime("%H:%M")

                if valid_time(cfg.get("masa_masuk", "")) and current == cfg["masa_masuk"]:
                    self._emit_once(
                        f"{day}:checkin",
                        {"kind": "checkin", "title": "Masa daftar masuk",
                         "scheduled_at": now.isoformat()},
                    )

                if valid_time(cfg.get("masa_keluar", "")) and current == cfg["masa_keluar"]:
                    self._emit_once(
                        f"{day}:checkout",
                        {"kind": "checkout", "title": "Masa daftar keluar",
                         "scheduled_at": now.isoformat()},
                    )

                # Pergerakan hanya berjalan selepas daftar masuk disahkan,
                # dan berhenti selepas daftar keluar disahkan atau waktu keluar tiba.
                checkin_at = self.fired.get("attendance_checkin_at")
                confirmed_today = self.fired.get("attendance_checkin_date") == day
                checked_out_today = self.fired.get("attendance_checkout_date") == day

                if (
                    cfg.get("auto_pergerakan")
                    and confirmed_today
                    and not checked_out_today
                    and valid_time(cfg.get("masa_keluar", ""))
                    and checkin_at
                ):
                    try:
                        start = datetime.fromisoformat(checkin_at)
                        if start.tzinfo is None:
                            start = start.astimezone()
                        end_time = datetime.strptime(
                            cfg["masa_keluar"], "%H:%M"
                        ).time()
                        end = datetime.combine(now.date(), end_time).astimezone()

                        if start.date() == now.date() and start < now < end:
                            elapsed_hours = int((now - start).total_seconds() // 3600)
                            if elapsed_hours >= 1:
                                target = start + timedelta(hours=elapsed_hours)
                                if target <= end and now >= target:
                                    self._emit_once(
                                        f"{day}:movement:{elapsed_hours}",
                                        {
                                            "kind": "movement",
                                            "title": f"Pergerakan jam ke-{elapsed_hours}",
                                            "scheduled_at": target.isoformat(),
                                        },
                                    )
                    except (TypeError, ValueError, OverflowError):
                        # Invalid persisted timestamps must never activate movement.
                        pass
            except Exception as exc:
                # Keep the scheduler alive if configuration or one iteration fails.
                print(f"[RALAT] Kitaran scheduler gagal: {exc}")

            self.stop_event.wait(self.interval)
