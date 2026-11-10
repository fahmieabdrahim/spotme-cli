from __future__ import annotations
from datetime import datetime
from .gps import get_location


def run_scheduled_event(event: dict, config_getter) -> None:
    """Run the terminal-side event handler and collect live device context."""
    cfg = config_getter()
    print("\\n" + "=" * 56)
    print(f"[JADUAL] {event['title']}")
    print(f"Masa peranti: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    print(f"Lokasi tetapan: {cfg.get('lokasi') or '(belum ditetapkan)'}")
    print(f"Ulasan: {cfg.get('ulasan', '')}")
    print(f"Sebab bekerja dari rumah: {cfg.get('sebab_wfh', '')}")
    print(f"Sebab lewat: {cfg.get('sebab_lewat', '')}")
    print(f"Sebab tidak cukup jam: {cfg.get('sebab_jam', '')}")
    print(f"Catatan tugasan: {cfg.get('catatan_tugasan', '')}")
    if event.get("kind") == "movement":
        gps, error = get_location()
        if gps:
            print(f"GPS semasa: {gps['latitude']}, {gps['longitude']}")
            print(f"Ketepatan: {gps.get('accuracy', 'N/A')}")
        else:
            print(f"GPS: {error}")
    print("=" * 56)
