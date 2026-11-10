# SPOT-Me CLI

Aplikasi terminal Python untuk Linux/Kali, WSL dan Android Termux. Tidak memerlukan Chrome, extension atau browser.

## Main menu

```text
1. Account Settings
2. Information Settings
3. Schedule Settings
4. Run System
5. Exit
```

### Account Settings
- User / MyKad
- Password (disimpan berasingan dan tidak dipaparkan)
- Location

### Information Settings
- Ulasan
- Sebab Bekerja Dari Rumah
- Sebab Lewat
- Sebab Tidak Cukup Jam
- Catatan Tugasan

### Schedule Settings
- Masa daftar masuk
- Masa daftar keluar
- Auto Pergerakan (peringatan mengikut sela jadual)

## Install

```bash
git clone https://github.com/fahmieabdrahim/spotme-cli.git
cd spotme-cli
chmod +x install.sh
./install.sh
```

Buka terminal baharu dan jalankan:

```bash
spotme
```

Alias `spotme.py` turut disediakan oleh installer.

## Platform

- Linux/Kali/WSL: Python 3.10+.
- Android Termux: Python 3.10+.
- GPS Android: pasang Termux:API dan pakej `termux-api`, kemudian benarkan akses lokasi.
- GPS Linux: memerlukan GPSD dan penerima GPS yang disokong. WSL lazimnya tiada GPS terbina dalam.

## Scheduler

Scheduler menggunakan jam tempatan peranti. Ia mengesan masa daftar masuk/keluar dan sela pergerakan yang ditetapkan, kemudian memaparkan peringatan serta konteks peranti. Pada peristiwa pergerakan, adapter GPS cuba membaca koordinat semasa peranti; koordinat tidak direka atau digantikan dengan lokasi tetap.

Scheduler berjalan selagi aplikasi terminal kekal terbuka. Menutup aplikasi akan menghentikan scheduler.

**Run System (peringkat semasa):** menyemak sambungan asas ke portal SPOT-Me tanpa login, kemudian menjalankan scheduler setempat. Ia tidak mengesahkan akaun, membaca rekod peribadi, atau menghantar/mengubah rekod rasmi.

## API investigation

Status endpoint dan bukti terdahulu direkodkan dalam [docs/API_INVENTORY.md](docs/API_INVENTORY.md). Dokumen itu ialah log penyiasatan, bukan dokumentasi rasmi. Laluan yang hanya ditemui dalam JavaScript ditandakan belum disahkan. Run System menggunakan hanya ujian sambungan portal tanpa pengesahan akaun. Struktur login/token masih provisional; semakan status akaun dan rekod harian belum diaktifkan sehingga permintaan login yang sah disahkan.

Jangan masukkan kata laluan, MyKad, OTP, token, cookies, koordinat atau rekod peribadi ke dalam Git.

## Local data

Semua fail berada di `~/.config/spotme-cli/`:

- `config.json`: maklumat dan jadual.
- `credentials.json`: password.
- `state.json`: penanda event yang sudah dicetuskan.

Password diasingkan daripada konfigurasi. Direktori ditetapkan kepada permission 700 dan fail peribadi kepada permission 600 apabila sistem fail menyokongnya.

## License

MIT
