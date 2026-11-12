from __future__ import annotations

from datetime import datetime, timedelta

from .scheduler import valid_time


def _today_target(value: str, now: datetime) -> datetime | None:
    if not valid_time(value):
        return None
    hour, minute = (int(part) for part in value.split(":"))
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _next_movement(state: dict, now: datetime, checkout: datetime | None):
    value = state.get("attendance_checkin_at")
    if not value:
        return None
    try:
        start = datetime.fromisoformat(value)
        if start.tzinfo is None:
            start = start.replace(tzinfo=now.tzinfo)
        start = start.astimezone(now.tzinfo)
    except (TypeError, ValueError, OverflowError):
        return None
    if start.date() != now.date():
        return None
    elapsed = max(0, int((now - start).total_seconds() // 3600))
    for number in range(max(1, elapsed + 1), 25):
        target = start + timedelta(hours=number)
        if checkout and target > checkout:
            return None
        if f"{now.date().isoformat()}:movement:{number}" not in state:
            return number, target
    return None


def build_dashboard(config: dict, state: dict, running: bool,
                    now: datetime | None = None) -> list[str]:
    """Build truthful operational status; no line implies a portal write succeeded."""
    now = now or datetime.now().astimezone()
    day = now.date().isoformat()
    checked_in = state.get("attendance_checkin_date") == day
    checked_out = state.get("attendance_checkout_date") == day
    lines = [
        "",
        "PUSAT INFORMASI",
        "─" * 48,
        f"Masa peranti       : {now.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"Sistem             : {'BERJALAN' if running else 'BELUM DIJALANKAN'}",
        "Sambungan portal   : DIAGNOSTIK SAHAJA",
        "Login portal       : BELUM DISAHKAN",
        f"Kehadiran setempat : {'DAFTAR KELUAR DISAHKAN' if checked_out else 'DAFTAR MASUK DISAHKAN' if checked_in else 'BELUM DISAHKAN'}",
        f"Jadual masuk       : {config.get('masa_masuk') or 'Tidak ditetapkan'}",
        f"Jadual keluar      : {config.get('masa_keluar') or 'Tidak ditetapkan'}",
    ]
    if checked_out:
        movement = "DIHENTIKAN — daftar keluar disahkan secara manual"
        next_action = "Jadual hari ini selesai."
    elif not config.get("auto_pergerakan"):
        movement = "DIMATIKAN dalam tetapan"
        next_action = "Sistem menunggu pengesahan daftar masuk/keluar secara manual."
    elif not checked_in:
        movement = "MENUNGGU pengesahan daftar masuk"
        target = _today_target(config.get("masa_masuk", ""), now)
        if target and target <= now:
            next_action = "Masa daftar masuk telah tiba; tindakan portal masih perlu disahkan."
        elif target:
            next_action = f"Peringatan daftar masuk dijadualkan pada {target.strftime('%H:%M')}."
        else:
            next_action = "Tetapkan masa daftar masuk untuk mengaktifkan jadual."
    else:
        movement = "MENUNGGU sela satu jam; tiada rekod dihantar ke portal"
        checkout = _today_target(config.get("masa_keluar", ""), now)
        upcoming = _next_movement(state, now, checkout)
        if upcoming:
            number, target = upcoming
            next_action = f"Peringatan pergerakan jam ke-{number}: {target.strftime('%H:%M')}."
        elif checkout:
            next_action = f"Daftar keluar dijadualkan pada {checkout.strftime('%H:%M')}."
        else:
            next_action = "Tetapkan masa daftar keluar untuk melengkapkan jadual."
    lines.extend([
        f"Pergerakan         : {movement}",
        f"Tindakan seterusnya: {next_action}",
        "Nota               : CLI memantau jadual dan memberi peringatan sahaja.",
        "                     Tiada rekod dihantar ke portal; login dan OTP belum disahkan.",
        "─" * 48,
    ])
    return lines


def render_dashboard(config: dict, scheduler, running: bool,
                     now: datetime | None = None) -> None:
    for line in build_dashboard(config, scheduler.fired, running, now):
        print(line)
