from __future__ import annotations
import json
import shutil
import subprocess
from datetime import datetime


def get_location() -> tuple[dict | None, str | None]:
    """Read the device's current GPS fix; never substitutes configured coordinates."""
    termux = shutil.which("termux-location")
    if termux:
        command = [termux, "-p", "gps", "-r", "once"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=35, check=False)
            if result.returncode != 0:
                return None, result.stderr.strip() or "Termux:API tidak dapat membaca GPS."
            data = json.loads(result.stdout)
            lat, lon = data.get("latitude"), data.get("longitude")
            if lat is None or lon is None:
                return None, "Koordinat GPS tidak diterima daripada peranti."
            return {"latitude": lat, "longitude": lon, "accuracy": data.get("accuracy"),
                    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"), "source": "termux"}, None
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            return None, f"Ralat GPS Termux: {exc}"

    gpspipe = shutil.which("gpspipe")
    if gpspipe:
        try:
            result = subprocess.run([gpspipe, "-w", "-n", "10"], capture_output=True, text=True, timeout=15, check=False)
            for line in result.stdout.splitlines():
                try: item = json.loads(line)
                except json.JSONDecodeError: continue
                if item.get("class") == "TPV" and item.get("lat") is not None and item.get("lon") is not None:
                    return {"latitude": item["lat"], "longitude": item["lon"], "accuracy": item.get("eph"),
                            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"), "source": "gpsd"}, None
            return None, "GPSD belum memberikan fix GPS."
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, f"Ralat GPSD: {exc}"
    return None, "Tiada penyedia GPS dikesan. Android memerlukan Termux:API; Linux memerlukan GPSD/penerima GPS."
