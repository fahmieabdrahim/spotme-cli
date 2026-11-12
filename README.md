# SPOT-Me CLI

Aplikasi terminal Python untuk Linux/Kali, WSL dan Android Termux. Tidak memerlukan Chrome, extension atau browser.

## Pusat Informasi

Paparan utama merangkum status sistem, sambungan portal, pengesahan kehadiran setempat, jadual dan tindakan seterusnya. Status setempat tidak dianggap sebagai bukti transaksi portal.

## Menu utama

```text
1. Tetapan Akaun
2. Tetapan Maklumat
3. Tetapan Jadual
4. Sahkan Daftar Masuk
5. Sahkan Daftar Keluar
6. Jalankan Sistem
7. Keluar
```

## Fungsi

- **Tetapan Akaun:** User / MyKad, password dan lokasi. Password disimpan berasingan dan tidak dipaparkan.
- **Tetapan Maklumat:** ulasan, sebab bekerja dari rumah, sebab lewat, sebab tidak cukup jam dan catatan tugasan.
- **Tetapan Jadual:** masa daftar masuk/keluar dan pilihan peringatan Pergerakan Harian.
- **Pengesahan kehadiran:** pengguna mengesahkan sendiri bahawa daftar masuk/keluar berjaya di portal.
- **Peringatan Pergerakan Harian:** hanya aktif selepas daftar masuk disahkan; berhenti selepas daftar keluar disahkan atau apabila masa daftar keluar yang ditetapkan tiba.

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

Scheduler menggunakan jam tempatan peranti dan berjalan selagi aplikasi terminal kekal terbuka. Menutup aplikasi akan menghentikan scheduler. Peringatan daftar masuk/keluar mengikut masa yang ditetapkan. Peringatan pergerakan dikira setiap satu jam selepas masa daftar masuk yang disahkan.

Jika handler peringatan gagal, event tidak ditandakan selesai supaya scheduler boleh mencuba semula pada kitaran seterusnya. State disimpan di dalam `~/.config/spotme-cli/state.json`.

**Penting:** aplikasi ini memaparkan peringatan dan konteks peranti sahaja. Ia tidak menghantar atau mengubah rekod kehadiran/pergerakan di portal.

## Pemeriksaan portal dan status integrasi

Run System menguji sambungan portal, kemudian mengimbas landing page dan sehingga 15 fail JavaScript awam daripada domain portal yang sama. Ia melaporkan calon laluan API serta petunjuk medan login/token. Calon daripada imbasan bukan kontrak API yang disahkan.

Login, OTP, pembacaan rekod peribadi dan penyegerakan status kehadiran belum diaktifkan. Rujuk [docs/API_INVENTORY.md](docs/API_INVENTORY.md) untuk tahap bukti setiap laluan. Jangan anggap HTTP 200 atau penemuan nama route sebagai bukti bahawa login atau integrasi telah berjaya.

Jangan masukkan kata laluan, MyKad, OTP, token, cookies, koordinat atau rekod peribadi ke dalam Git.

## Data setempat

Semua fail berada di `~/.config/spotme-cli/`:

- `config.json`: maklumat dan jadual.
- `credentials.json`: password.
- `state.json`: status pengesahan dan event yang sudah dicetuskan.
- `api_scan.txt`: laporan imbasan portal tanpa credentials/token/cookies.

Password diasingkan daripada konfigurasi. Direktori ditetapkan kepada permission 700 dan fail peribadi kepada permission 600 apabila sistem fail menyokongnya.

## Ujian

Jalankan dari direktori projek:

```bash
python -m unittest discover -v
python -m compileall -q spotme tests
```

## License

MIT
