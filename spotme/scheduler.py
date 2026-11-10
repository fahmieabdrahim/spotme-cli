from __future__ import annotations
import threading
import time
from datetime import datetime, timedelta
from .config import load_state, save_state


def valid_time(value: str) -> bool:
    try: datetime.strptime(value, "%H:%M"); return True
    except (TypeError, ValueError): return False

class Scheduler:
    """In-process scheduler driven by the device's local clock."""
    def __init__(self, config_getter, callback, interval: float = 1.0):
        self.config_getter = config_getter
        self.callback = callback
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = None
        self.fired = load_state()

    def start(self):
        if self.thread and self.thread.is_alive(): return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, name="spotme-scheduler", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=5)

    def _emit_once(self, event_id: str, event: dict):
        if self.fired.get(event_id): return
        self.fired[event_id] = True
        save_state(self.fired)
        self.callback(event)

    def _run(self):
        while not self.stop_event.is_set():
            cfg = self.config_getter()
            now = datetime.now().astimezone()
            day = now.date().isoformat()
            current = now.strftime("%H:%M")
            if valid_time(cfg.get("masa_masuk", "")) and current == cfg["masa_masuk"]:
                self._emit_once(f"{day}:checkin", {"kind": "checkin", "title": "Masa daftar masuk", "scheduled_at": now.isoformat()})
            if valid_time(cfg.get("masa_keluar", "")) and current == cfg["masa_keluar"]:
                self._emit_once(f"{day}:checkout", {"kind": "checkout", "title": "Masa daftar keluar", "scheduled_at": now.isoformat()})
            if cfg.get("auto_pergerakan") and valid_time(cfg.get("masa_masuk", "")) and valid_time(cfg.get("masa_keluar", "")):
                start = datetime.combine(now.date(), datetime.strptime(cfg["masa_masuk"], "%H:%M").time()).astimezone()
                end = datetime.combine(now.date(), datetime.strptime(cfg["masa_keluar"], "%H:%M").time()).astimezone()
                if start < now <= end:
                    elapsed_hours = int((now - start).total_seconds() // 3600)
                    if elapsed_hours >= 1:
                        target = start + timedelta(hours=elapsed_hours)
                        if now >= target and target <= end:
                            self._emit_once(f"{day}:movement:{elapsed_hours}", {"kind": "movement", "title": f"Pergerakan jam ke-{elapsed_hours}", "scheduled_at": target.isoformat()})
            self.stop_event.wait(self.interval)
