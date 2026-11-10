from __future__ import annotations
import getpass
from .automation import run_scheduled_event
from .config import load_config, save_config, load_credentials, save_password
from .scheduler import Scheduler, valid_time


HEADER = r"""
███████╗██████╗  ██████╗ ████████╗   ███╗   ███╗███████╗
██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝   ████╗ ████║██╔════╝
███████╗██████╔╝██║   ██║   ██║█████╗██╔████╔██║█████╗
╚════██║██╔═══╝ ██║   ██║   ██║╚════╝██║╚██╔╝██║██╔══╝
███████║██║     ╚██████╔╝   ██║      ██║ ╚═╝ ██║███████╗
╚══════╝╚═╝      ╚═════╝    ╚═╝      ╚═╝     ╚═╝╚══════╝
"""


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
        print("1. Ubah")
        print("2. Keluar")
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
        print("1. Ubah")
        print("2. Keluar")
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
        print("1. Ubah")
        print("2. Keluar")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            edit_time_settings()
            input("\nTekan Enter untuk kembali...")
        elif choice == "2":
            return
        else:
            print("[RALAT] Pilihan tidak sah. Pilih 1 atau 2.")
            input("\nTekan Enter untuk cuba lagi...")


def main():
    scheduler = Scheduler(load_config, lambda event: run_scheduled_event(event, load_config))
    scheduler.start()
    try:
        while True:
            clear_screen()
            print_header()
            print("1. Tetapan Akaun")
            print("2. Tetapan Maklumat")
            print("3. Tetapan Masa")
            print("4. Keluar")
            choice = input("\nPilihan: ").strip()
            if choice == "1":
                account_menu()
            elif choice == "2":
                info_menu()
            elif choice == "3":
                time_menu()
            elif choice == "4":
                break
            else:
                clear_screen()
                print_header()
                print("[RALAT] Pilihan tidak sah. Pilih 1 hingga 4.")
                input("\nTekan Enter untuk kembali...")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        scheduler.stop()
        clear_screen()


if __name__ == "__main__":
    main()
