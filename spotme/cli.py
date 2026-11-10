from __future__ import annotations
import getpass
from .api import SpotMeAPI, SpotMeAPIError
from .automation import run_scheduled_event
from .config import load_config, save_config, load_credentials, save_password
from .scheduler import Scheduler, valid_time


def edit_text(label: str, key: str, cfg: dict):
    current = cfg.get(key, "")
    value = input(f"{label} [{current}]: ").strip()
    if value:
        cfg[key] = value
        save_config(cfg)
        print("Tetapan disimpan.")


def account_menu():
    while True:
        cfg = load_config()
        print("\nTETAPAN AKAUN")
        print("1. User")
        print("2. Password")
        print("3. Lokasi")
        print("4. Kembali")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            edit_text("User / MyKad", "user", cfg)
        elif choice == "2":
            password = getpass.getpass("Password baharu: ")
            if password:
                save_password(password)
                print("Password disimpan dalam fail berasingan dengan permission terhad.")
        elif choice == "3":
            edit_text("Lokasi", "lokasi", cfg)
        elif choice == "4":
            return
        else:
            print("Pilihan tidak sah.")


def info_menu():
    fields = [
        ("Ulasan", "ulasan"),
        ("Sebab Bekerja Dari Rumah", "sebab_wfh"),
        ("Sebab Lewat", "sebab_lewat"),
        ("Sebab Tidak Cukup Jam", "sebab_jam"),
        ("Catatan Tugasan", "catatan_tugasan"),
    ]
    while True:
        cfg = load_config()
        print("\nTETAPAN MAKLUMAT")
        for i, (label, _) in enumerate(fields, 1):
            print(f"{i}. {label}")
        print(f"{len(fields)+1}. Kembali")
        choice = input("\nPilihan: ").strip()
        if choice == str(len(fields)+1):
            return
        if choice.isdigit() and 1 <= int(choice) <= len(fields):
            label, key = fields[int(choice)-1]
            edit_text(label, key, cfg)
        else:
            print("Pilihan tidak sah.")


def time_menu():
    while True:
        cfg = load_config()
        print("\nTETAPAN MASA")
        print(f"1. Masa Daftar Masuk [{cfg['masa_masuk']}]")
        print(f"2. Masa Daftar Keluar [{cfg['masa_keluar']}]")
        print(f"3. Auto Pergerakan (1 Jam) [{'Ya' if cfg['auto_pergerakan'] else 'Tidak'}]")
        print("4. Kembali")
        choice = input("\nPilihan: ").strip()
        if choice == "1":
            value = input("Masa daftar masuk (HH:MM): ").strip()
            if valid_time(value):
                cfg["masa_masuk"] = value
                save_config(cfg)
                print("Masa disimpan.")
            else:
                print("Format tidak sah. Contoh: 07:25")
        elif choice == "2":
            value = input("Masa daftar keluar (HH:MM): ").strip()
            if valid_time(value):
                cfg["masa_keluar"] = value
                save_config(cfg)
                print("Masa disimpan.")
            else:
                print("Format tidak sah. Contoh: 16:35")
        elif choice == "3":
            cfg["auto_pergerakan"] = not cfg["auto_pergerakan"]
            save_config(cfg)
            print("Auto pergerakan: " + ("Ya" if cfg["auto_pergerakan"] else "Tidak"))
        elif choice == "4":
            return
        else:
            print("Pilihan tidak sah.")


def connect_api():
    cfg = load_config()
    credentials = load_credentials()
    if not cfg.get("user") or not credentials.get("password"):
        print("[INFO] Lengkapkan User dan Password dalam Tetapan Akaun untuk ujian sambungan.")
        return None
    client = SpotMeAPI()
    try:
        client.login(cfg["user"], credentials["password"])
        status = client.check_eligibility()
        print("[OK] Log masuk API SPOT-Me berjaya.")
        print("[OK] Status kelayakan berjaya dibaca.")
        for key, value in status.items():
            print(f"     {key}: {value}")
        return client
    except SpotMeAPIError as exc:
        print(f"[GAGAL] Sambungan API: {exc}")
        return None


def main():
    print("\nSPOTME CLI")
    print("Terminal Autopilot")
    print("Browser: tidak digunakan")
    print("Masa sistem: ikut jam peranti")
    connect_api()
    scheduler = Scheduler(load_config, lambda event: run_scheduled_event(event, load_config))
    scheduler.start()
    print("[AKTIF] Scheduler berjalan selagi aplikasi ini dibuka.")
    try:
        while True:
            print("\n1. Tetapan Akaun")
            print("2. Tetapan Maklumat")
            print("3. Tetapan Masa")
            print("4. Keluar")
            choice = input("\nPilihan: ").strip()
            if choice == "1":
                account_menu()
                connect_api()
            elif choice == "2":
                info_menu()
            elif choice == "3":
                time_menu()
            elif choice == "4":
                break
            else:
                print("Pilihan tidak sah.")
    except (KeyboardInterrupt, EOFError):
        print("\nMenutup SPOTME CLI...")
    finally:
        scheduler.stop()
        print("[STOP] Semua scheduler SPOTME CLI dihentikan.")


if __name__ == "__main__":
    main()
