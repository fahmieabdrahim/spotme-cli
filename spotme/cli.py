from __future__ import annotations
import getpass
from pathlib import Path
from .automation import run_scheduled_event
from .api import SpotMeAPI
from .config import ROOT, ensure_root, load_config, save_config, load_credentials, save_password
from .scheduler import Scheduler, valid_time


HEADER = "SPOT-Me CLI\n" + "─" * 30


def clear_screen():
    print("\033[3J\033[2J\033[H", end="", flush=True)


def print_header():
    print(HEADER)


def edit_text(label: str, key: str, cfg: dict):
    value = input(f"{label}: ").strip()
    if value:
        cfg[key] = value
        save_config(cfg)
        print(f"[OK] {label} disimpan.")
    else:
        print(f"[INFO] {label} tidak diubah.")


def edit_account():
    cfg = load_config()
    print("\nUBAH TETAPAN AKAUN")
    print("Tekan Enter untuk kekalkan nilai sedia ada.")

    while True:
        value = input("User / MyKad: ").strip()
        if not value:
            print("[INFO] User tidak diubah.")
            break
        if any(ch.isspace() for ch in value):
            print("[RALAT] User tidak boleh mengandungi ruang kosong. Sila masukkan semula.")
            continue
        cfg["user"] = value
        save_config(cfg)
        print("[OK] User disimpan.")
        break

    while True:
        password = getpass.getpass("Password: ")
        if not password:
            print("[INFO] Password tidak diubah.")
            break
        if password.isspace():
            print("[RALAT] Password tidak boleh mengandungi ruang sahaja.")
            continue
        save_password(password)
        print("[OK] Password disimpan.")
        break

    while True:
        location = input("Lokasi: ").strip()
        if not location:
            print("[INFO] Lokasi tidak diubah.")
            break
        if len(location) < 2:
            print("[RALAT] Lokasi terlalu pendek. Masukkan lokasi yang lebih lengkap.")
            continue
        cfg["lokasi"] = location
        save_config(cfg)
        print("[OK] Lokasi disimpan.")
        break


def account_menu():
    while True:
        cfg = load_config()
        credentials = load_credentials()
        clear_screen()
        print_header()
        print("------------------------------")
        print(f"User     : {cfg.get('user') or '[Belum diisi]'}")
        print(f"Password : {'[Telah ditetapkan]' if credentials.get('password') else '[Belum diisi]'}")
        print(f"Lokasi   : {cfg.get('lokasi') or '[Belum diisi]'}")
        print("------------------------------")
        print("1. Edit")
        print("2. Exit")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            edit_account()
            input("\nTekan Enter untuk kembali...")
        elif choice == "2":
            return
        else:
            print("[RALAT] Pilihan tidak sah. Pilih 1 atau 2.")
            input("\nTekan Enter untuk cuba lagi...")


INFO_FIELDS = [
    ("Ulasan", "ulasan"),
    ("Sebab Bekerja Dari Rumah", "sebab_wfh"),
    ("Sebab Lewat", "sebab_lewat"),
    ("Sebab Tidak Cukup Jam", "sebab_jam"),
    ("Catatan Tugasan", "catatan_tugasan"),
]


def edit_info():
    cfg = load_config()
    print("\nUBAH TETAPAN MAKLUMAT")
    print("Tekan Enter untuk kekalkan nilai sedia ada.\n")
    for label, key in INFO_FIELDS:
        edit_text(label, key, cfg)


def info_menu():
    while True:
        cfg = load_config()
        clear_screen()
        print_header()
        print("TETAPAN MAKLUMAT")
        print("------------------------------")
        for label, key in INFO_FIELDS:
            print(f"{label}: {cfg.get(key) or '[Belum diisi]'}")
        print("------------------------------")
        print("1. Edit")
        print("2. Exit")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            edit_info()
            input("\nTekan Enter untuk kembali...")
        elif choice == "2":
            return
        else:
            print("[RALAT] Pilihan tidak sah. Pilih 1 atau 2.")
            input("\nTekan Enter untuk cuba lagi...")


def edit_time_settings():
    cfg = load_config()
    print("\nUBAH TETAPAN MASA")
    print("Tekan Enter untuk kekalkan nilai sedia ada.")
    print("Masukkan 0 jika mahu kosongkan masa.\n")

    for label, key in (
        ("Masa daftar masuk", "masa_masuk"),
        ("Masa daftar keluar", "masa_keluar"),
    ):
        while True:
            value = input(f"{label} (HH:MM): ").strip()
            if not value:
                print(f"[INFO] {label} tidak diubah.")
                break
            if value == "0" or valid_time(value):
                cfg[key] = value
                save_config(cfg)
                print(f"[OK] {label} disimpan.")
                break
            print("[RALAT] Format masa tidak sah. Gunakan HH:MM, contoh 07:25, atau 0.")

    while True:
        value = input(f"Auto Pergerakan Y/N [{ 'Y' if cfg.get('auto_pergerakan') else 'N' }]: ").strip().upper()
        if not value:
            print("[INFO] Auto Pergerakan tidak diubah.")
            break
        if value in ("Y", "N"):
            cfg["auto_pergerakan"] = value == "Y"
            save_config(cfg)
            print("[OK] Auto Pergerakan disimpan.")
            break
        print("[RALAT] Masukkan Y atau N.")


def time_menu():
    while True:
        cfg = load_config()
        clear_screen()
        print_header()
        print("TETAPAN MASA")
        print("------------------------------")
        print(f"Masa Daftar Masuk  : {cfg.get('masa_masuk') or '0'}")
        print(f"Masa Daftar Keluar : {cfg.get('masa_keluar') or '0'}")
        print(f"Auto Pergerakan Y/N: {'Y' if cfg.get('auto_pergerakan') else 'N'}")
        print("------------------------------")
        print("1. Edit")
        print("2. Exit")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            edit_time_settings()
            input("\nTekan Enter untuk kembali...")
        elif choice == "2":
            return
        else:
            print("[RALAT] Pilihan tidak sah. Pilih 1 atau 2.")
            input("\nTekan Enter untuk cuba lagi...")


def validate_run_settings() -> list[str]:
    cfg = load_config()
    credentials = load_credentials()
    missing = []

    if not cfg.get("user"):
        missing.append("User / MyKad")
    if not credentials.get("password"):
        missing.append("Password")
    if not cfg.get("lokasi"):
        missing.append("Lokasi")
    if not (valid_time(cfg.get("masa_masuk", "")) or valid_time(cfg.get("masa_keluar", ""))):
        missing.append("Sekurang-kurangnya satu masa jadual (daftar masuk/keluar)")

    return missing



def write_scan_report(inspection: dict) -> Path:
    """Save detailed, non-secret portal scan findings outside the main screen."""
    ensure_root()
    report_path = ROOT / "api_scan.txt"
    hints = inspection.get("login_hints", {})
    lines = [
        "SPOT-Me portal scan report",
        "==========================",
        f"Reachable: {inspection.get('reachable', False)}",
        f"HTTP status: {inspection.get('http_status')}",
        f"JavaScript files: {inspection.get('scripts_scanned', 0)}/{inspection.get('scripts_found', 0)}",
        "",
        "API route candidates (not verified endpoints):",
        *[f"- {route}" for route in inspection.get("routes", [])],
        "",
        "Login hints (static frontend clues only):",
        f"POST method seen: {hints.get('post_method_seen', False)}",
        f"Request fields: {', '.join(hints.get('request_fields', [])) or 'Not detected'}",
        f"Token keys: {', '.join(hints.get('token_keys', [])) or 'Not detected'}",
        "",
        "Warnings:",
        *[f"- {warning}" for warning in inspection.get("warnings", [])],
        "",
        "No credentials, tokens, cookies, or JavaScript source are stored in this report.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        report_path.chmod(0o600)
    except OSError:
        pass
    return report_path


def main():
    scheduler = Scheduler(load_config, lambda event: run_scheduled_event(event, load_config))
    scheduler_running = False

    try:
        while True:
            clear_screen()
            print_header()
            print("1. Tetapan Akaun")
            print("2. Tetapan Maklumat")
            print("3. Tetapan Jadual")
            print("4. Jalankan Sistem")
            print("5. Keluar")
            if scheduler_running:
                print("\nStatus: SYSTEM RUNNING")

            choice = input("\nPilihan: ").strip()
            if choice == "1":
                account_menu()
            elif choice == "2":
                info_menu()
            elif choice == "3":
                time_menu()
            elif choice == "4":
                if scheduler_running:
                    print("\n[INFO] Sistem sudah pun berjalan.")
                else:
                    missing = validate_run_settings()
                    if missing:
                        print("\n[RALAT] Lengkapkan tetapan berikut dahulu:")
                        for item in missing:
                            print(f"- {item}")
                    else:
                        save_config(load_config())
                        api = SpotMeAPI(timeout=10)
                        print("\nDIAGNOSTIK SPOT-ME")
                        print("------------------------------")
                        reachable, status_code = api.check_portal_connection()
                        portal_status = "DALAM TALIAN" if reachable else "TIADA SAMBUNGAN"
                        http_label = f" (HTTP {status_code})" if status_code is not None else ""
                        print(f"Portal          : {portal_status}{http_label}")

                        inspection = api.inspect_portal()
                        hints = inspection.get("login_hints", {})
                        if inspection["reachable"]:
                            print(f"Imbasan portal  : SELESAI")
                            print(f"Fail JavaScript : {inspection['scripts_scanned']}/{inspection['scripts_found']}")
                            print(f"Calon API       : {len(inspection['routes'])} ditemui")
                            print(f"Kaedah login    : {'POST dikesan' if hints.get('post_method_seen') else 'Belum dikesan'}")
                            print(f"Medan permintaan: {', '.join(hints.get('request_fields', [])) or 'Belum dikesan'}")
                            print(f"Kunci token     : {', '.join(hints.get('token_keys', [])) or 'Belum dikesan'}")
                        else:
                            print("Imbasan portal  : TIDAK BERJAYA")
                        report_path = write_scan_report(inspection)
                        print(f"Laporan penuh   : {report_path}")
                        for warning in inspection.get("warnings", []):
                            print(f"Catatan         : {warning}")
                        print("------------------------------")
                        print("Login           : BELUM DICUBA")
                        print("Sebab           : Proses login dan OTP belum disahkan.")
                        scheduler.start()
                        scheduler_running = True
                        print("\n[OK] Tetapan disimpan.")
                        print("[OK] Jadual peringatan SPOT-Me bermula.")
                        print("[INFO] Biarkan aplikasi ini terbuka untuk terus menjalankan jadual.")
                        print("[INFO] Sistem hanya memantau masa dan memaparkan peringatan.")
                        print("[INFO] Tiada rekod kehadiran atau pergerakan dibaca atau dihantar.")
                input("\nTekan Enter untuk kembali ke menu...")
            elif choice == "5":
                break
            else:
                clear_screen()
                print_header()
                print("[RALAT] Pilihan tidak sah. Pilih 1 hingga 5.")
                input("\nTekan Enter untuk kembali...")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        scheduler.stop()
        clear_screen()


if __name__ == "__main__":
    main()
