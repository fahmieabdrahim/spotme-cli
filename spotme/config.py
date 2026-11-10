from __future__ import annotations
import json
from pathlib import Path

ROOT = Path.home() / ".config" / "spotme-cli"
CONFIG_FILE = ROOT / "config.json"
CREDENTIALS_FILE = ROOT / "credentials.json"
STATE_FILE = ROOT / "state.json"

DEFAULTS = {
    "user": "", "lokasi": "", "ulasan": "HBH",
    "sebab_wfh": "Hari Bekerja Hibrid (HBH)",
    "sebab_lewat": "Tiada", "sebab_jam": "Tiada",
    "catatan_tugasan": "Menyediakan reka bentuk grafik mengikut arahan dan tempoh pelaksanaan yang ditetapkan",
    "masa_masuk": "07:25", "masa_keluar": "16:35",
    "auto_pergerakan": True,
}


def ensure_root() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    try:
        ROOT.chmod(0o700)
    except OSError:
        pass


def _write_private(path: Path, data: dict) -> None:
    ensure_root()
    temp = path.with_suffix(path.suffix + ".tmp")
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


def _read(path: Path, default: dict) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else default.copy()
    except (OSError, json.JSONDecodeError):
        return default.copy()


def load_config() -> dict:
    data = DEFAULTS.copy()
    data.update(_read(CONFIG_FILE, {}))
    return data


def save_config(data: dict) -> None:
    _write_private(CONFIG_FILE, data)


def load_credentials() -> dict:
    return _read(CREDENTIALS_FILE, {"password": ""})


def save_password(password: str) -> None:
    _write_private(CREDENTIALS_FILE, {"password": password})


def load_state() -> dict:
    return _read(STATE_FILE, {})


def save_state(data: dict) -> None:
    _write_private(STATE_FILE, data)
