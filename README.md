# SPOT-Me CLI

Aplikasi terminal Python untuk Linux/Kali, WSL dan Android Termux. Tiada Chrome, extension atau browser digunakan.

## Menu

```text
1. Tetapan Akaun
2. Tetapan Maklumat
3. Tetapan Masa
4. Keluar
```

### Tetapan Akaun
- User
- Password
- Lokasi

### Tetapan Maklumat
- Ulasan
- Sebab Bekerja Dari Rumah
- Sebab Lewat
- Sebab Tidak Cukup Jam
- Catatan Tugasan

### Tetapan Masa
- Masa Daftar Masuk
- Masa Daftar Keluar
- Auto Pergerakan (1 Jam)

Tetapan disimpan di `~/.config/spotme-cli/`. Password diasingkan daripada konfigurasi dan fail diberi permission 600; direktori diberi permission 700.

## Pasang

```bash
git clone https://github.com/fahmieabdrahim/spotme-cli.git
cd spotme-cli
chmod +x install.sh
./install.sh
spotme.py
```

Jika `spotme` belum dijumpai, tambah `~/.local/bin` ke PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Platform

- Linux/Kali/WSL: Python 3.10+.
- Android Termux: Python 3.10+.
- GPS Android: pasang aplikasi Termux:API dan pakej `termux-api`, kemudian benarkan akses lokasi.
- GPS Linux: perlukan GPSD dan penerima GPS yang disokong. WSL lazimnya tiada GPS terbina dalam.

## Ujian API

Apabila User dan Password telah disimpan, aplikasi cuba log masuk ke endpoint API SPOT-Me dan membaca endpoint status `/api/checking`. Respons sebenar dipaparkan di terminal. Jika struktur respons token atau endpoint berubah, mesej ralat dipaparkan.

## Jadual dan status pembangunan

Scheduler menggunakan jam tempatan peranti. Ia mengesan masa daftar masuk/keluar dan sela pergerakan setiap satu jam. Pada masa pergerakan, adapter GPS cuba membaca koordinat semasa peranti; koordinat tidak direka atau digantikan dengan lokasi tetap.

**Peringkat ini ialah asas terminal, konfigurasi, ujian login/status API, GPS dan scheduler.** Aliran tulis rekod kehadiran/pergerakan melalui API belum disambungkan; endpoint dan format transaksi tulis perlu disahkan daripada dokumentasi/API rasmi sebelum fungsi itu boleh dianggap siap. Tiada browser dibuka.

## Data setempat

- `config.json`: maklumat dan jadual.
- `credentials.json`: password.
- `state.json`: penanda event yang sudah dicetuskan.

Semua fail berada dalam `~/.config/spotme-cli/`.

## Lesen
MIT
