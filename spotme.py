#!/usr/bin/env python3
"""SPOT-Me CLI — jadual tempatan, GPS sebenar dan pembukaan portal.

Aplikasi berjalan selagi CLI terbuka. Rekod rasmi kekal di bawah kawalan pengguna:
aplikasi tidak menghantar daftar masuk/keluar/pergerakan secara automatik.
"""
from __future__ import annotations

import getpass
import json
import queue
import shutil
import subprocess
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

PORTAL = "https://spotme.jdn.gov.my"
ROOT = Path.home() / ".config" / "spotme-cli"
CONFIG = ROOT / "config.json"
STATE = ROOT / "state.json"
DAY_NAMES = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]

FIELDS = {
    "1": ("Pengguna / ID log masuk", "pengguna", ""),
    "2": ("Kata laluan (tidak disimpan)", "password", ""),
    "3": ("Lokasi", "lokasi", ""),
    "4": ("Ulasan", "ulasan", "HBH"),
    "5": ("Sebab bekerja dari rumah", "sebab_wfh", "Hari Bekerja Hibrid (HBH)"),
    "6": ("Sebab lewat", "sebab_lewat", "Tiada"),
    "7": ("Sebab tidak cukup jam", "sebab_jam", "Tiada"),
    "8": ("Catatan tugasan", "catatan_tugasan",
          "Menyediakan reka bentuk grafik mengikut arahan dan tempoh pelaksanaan yang ditetapkan"),
    "9": ("Masa masuk (HH:MM)", "masa_masuk", "07:25"),
    "10": ("Masa keluar (HH:MM)", "masa_keluar", "16:35"),
    "11": ("Auto pergerakan setiap 1 jam (ya/tidak)", "auto_pergerakan", True),
}
DEFAULTS = {
    "pengguna": "", "lokasi": "", "ulasan": "HBH",
    "sebab_wfh": "Hari Bekerja Hibrid (HBH)", "sebab_lewat": "Tiada",
    "sebab_jam": "Tiada",
    "catatan_tugasan": "Menyediakan reka bentuk grafik mengikut arahan dan tempoh pelaksanaan yang ditetapkan",
    "masa_masuk": "07:25", "masa_keluar": "16:35",
    "auto_pergerakan": True, "hari_bekerja": [0, 1, 2, 3, 4],
}


def ensure_dirs():
    ROOT.mkdir(parents=True, exist_ok=True)
    try:
        ROOT.chmod(0o700)
    except OSError:
        pass


def save_json(path, data):
    ensure_dirs()
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        temp.chmod(0o600)
    except OSError:
        pass
    temp.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def load_config():
    cfg = DEFAULTS.copy()
    saved = load_json(CONFIG, {})
    if isinstance(saved, dict):
        cfg.update(saved)
    return cfg


def valid_time(value):
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except (TypeError, ValueError):
        return False


def setup_days(cfg):
    print("\nHari bekerja: 0 Isnin, 1 Selasa, 2 Rabu, 3 Khamis, 4 Jumaat, 5 Sabtu, 6 Ahad")
    raw = input("Pilih hari bekerja, pisahkan dengan koma [0,1,2,3,4]: ").strip() or "0,1,2,3,4"
    try:
        days = sorted({int(x.strip()) for x in raw.split(",") if x.strip()})
        if not days or any(x < 0 or x > 6 for x in days):
            raise ValueError
        cfg["hari_bekerja"] = days
    except ValueError:
        print("Pilihan tidak sah. Hari bekerja ditetapkan Isnin hingga Jumaat.")
        cfg["hari_bekerja"] = [0, 1, 2, 3, 4]
    save_json(CONFIG, cfg)


def edit_field(choice, cfg):
    label, key, default = FIELDS[choice]
    if key == "password":
        secret = getpass.getpass("Kata laluan portal (tidak disimpan): ")
        print("Kata laluan diterima untuk sesi ini sahaja; login portal dibuat oleh pengguna.")
        del secret
        return
    current = cfg.get(key, default)
    if isinstance(default, bool):
        raw = input(f"{label} [{'ya' if current else 'tidak'}]: ").strip().lower()
        if raw in ("ya", "y", "yes", "1"):
            cfg[key] = True
        elif raw in ("tidak", "t", "no", "n", "0"):
            cfg[key] = False
        elif raw:
            print("Masukkan ya atau tidak.")
            return
    else:
        raw = input(f"{label} [{current}]: ").strip()
        if raw:
            if key in ("masa_masuk", "masa_keluar") and not valid_time(raw):
                print("Format masa mesti HH:MM, contoh 07:25.")
                return
            cfg[key] = raw
    save_json(CONFIG, cfg)
    print("Tetapan disimpan.")


def read_gps():
    command = shutil.which("termux-location")
    if not command:
        return None, "GPS Termux:API tidak tersedia pada peranti ini."
    try:
        result = subprocess.run(
            [command, "-p", "gps", "-r", "once"],
            capture_output=True, text=True, timeout=30, check=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None, "GPS gagal dibaca. Semak Termux:API dan kebenaran lokasi."
        data = json.loads(result.stdout)
        lat, lon = data.get("latitude"), data.get("longitude")
        if lat is None or lon is None:
            return None, "Respons GPS tidak mengandungi latitude/longitude."
        return {"latitude": lat, "longitude": lon,
                "accuracy": data.get("accuracy"),
                "time": datetime.now().astimezone().isoformat(timespec="seconds")}, None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None, "GPS tidak dapat dibaca. Semak Termux:API dan kebenaran lokasi."


def open_portal():
    try:
        webbrowser.open(PORTAL, new=2)
    except Exception:
        pass


def event_text(event, cfg):
    lines = [
        f"Jenis tindakan: {event['title']}",
        f"Masa peranti: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"Lokasi tetapan: {cfg.get('lokasi') or '(belum ditetapkan)'}",
        f"Ulasan: {cfg.get('ulasan', '')}",
        f"Sebab WFH: {cfg.get('sebab_wfh', '')}",
        f"Sebab lewat: {cfg.get('sebab_lewat', '')}",
        f"Sebab tidak cukup jam: {cfg.get('sebab_jam', '')}",
        f"Catatan tugasan: {cfg.get('catatan_tugasan', '')}",
    ]
    if event["kind"] == "movement":
        gps, error = read_gps()
        if gps:
            lines.append(f"GPS sebenar sekarang: {gps['latitude']}, {gps['longitude']}")
            lines.append(f"Ketepatan GPS: {gps.get('accuracy', 'tidak dinyatakan')} meter")
            lines.append(f"Masa bacaan GPS: {gps['time']}")
        else:
            lines.append(error or "GPS tidak tersedia.")
    return "\n".join(lines)


def scheduler(cfg, stop, events):
    fired = load_json(STATE, {})
    while not stop.is_set():
        now = datetime.now()
        day_key = now.date().isoformat()
        if now.weekday() in cfg.get("hari_bekerja", []):
            hhmm = now.strftime("%H:%M")
            for key, title, kind in (
                ("masa_masuk", "Daftar masuk", "checkin"),
                ("masa_keluar", "Daftar keluar", "checkout"),
            ):
                event_id = f"{day_key}:{key}"
                if valid_time(cfg.get(key, "")) and hhmm == cfg[key] and fired.get(event_id) != "done":
                    handle_event({"id": event_id, "title": title, "kind": kind}, cfg)
                    fired[event_id] = "done"
                    save_json(STATE, fired)

            if cfg.get("auto_pergerakan") and valid_time(cfg.get("masa_masuk", "")) and valid_time(cfg.get("masa_keluar", "")):
                start = datetime.combine(now.date(), datetime.strptime(cfg["masa_masuk"], "%H:%M").time())
                end = datetime.combine(now.date(), datetime.strptime(cfg["masa_keluar"], "%H:%M").time())
                elapsed = (now - start).total_seconds()
                if start < now <= end and elapsed >= 3600:
                    hour = int(elapsed // 3600)
                    target = start + timedelta(hours=hour)
                    event_id = f"{day_key}:movement:{hour}"
                    if now >= target and fired.get(event_id) != "done":
                        handle_event({"id": event_id, "title": f"Pergerakan setiap 1 jam (#{hour})", "kind": "movement"}, cfg)
                        fired[event_id] = "done"
                        save_json(STATE, fired)
        stop.wait(1)


def show_config(cfg):
    print("\nTetapan semasa")
    for number, (label, key, default) in FIELDS.items():
        value = "Tidak disimpan" if key == "password" else cfg.get(key, default)
        if key == "auto_pergerakan":
            value = "Ya" if value else "Tidak"
        print(f"{number}. {label}: {value}")
    days = [DAY_NAMES[x] for x in cfg.get("hari_bekerja", []) if 0 <= x <= 6]
    print("Hari bekerja: " + ", ".join(days))


def handle_event(event, cfg):
    print("\n" + "=" * 58)
    print(f"JADUAL AKTIF: {event['title']}")
    print(event_text(event, cfg))
    print("=" * 58)
    print("Portal akan dibuka. Semak maklumat dan buat pengesahan rasmi sendiri.")
    open_portal()


def main():
    ensure_dirs()
    cfg = load_config()
    if not CONFIG.exists():
        print("Persediaan pertama SPOT-Me CLI")
        setup_days(cfg)

    events = queue.Queue()
    stop = threading.Event()
    worker = threading.Thread(target=scheduler, args=(cfg.copy(), stop, events), daemon=True)
    worker.start()

    print("\nSPOT-Me CLI aktif — biarkan tetingkap ini terbuka untuk jadual berjalan.")
    print("Masa mengikut jam peranti. GPS sebenar dibaca pada masa pergerakan.")
    try:
        while True:
            while not events.empty():
                handle_event(events.get_nowait(), cfg)
            print("\n1-11. Ubah tetapan | S. Lihat tetapan | P. Buka portal | 0. Exit")
            print("Tekan Enter untuk terus memantau jadual.")
            choice = input("\nPilihan: ").strip().lower()
            if choice == "0":
                break
            if choice == "s":
                show_config(cfg)
            elif choice == "p":
                open_portal()
            elif choice in FIELDS:
                edit_field(choice, cfg)
                cfg = load_config()
                # Jadual menggunakan salinan tetapan terkini selepas edit.
                stop.set()
                worker.join(timeout=2)
                stop.clear()
                worker = threading.Thread(target=scheduler, args=(cfg.copy(), stop, events), daemon=True)
                worker.start()
            elif choice:
                print("Pilihan tidak sah.")
    except (KeyboardInterrupt, EOFError):
        print("\nMenutup SPOT-Me CLI...")
    finally:
        stop.set()
        worker.join(timeout=3)
        print("SPOT-Me CLI dihentikan. Tiada scheduler ditinggalkan.")


if __name__ == "__main__":
    main()
