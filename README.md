# SPOT-Me CLI

Aplikasi CLI untuk Kali Linux, WSL dan Android Termux. Aplikasi kekal aktif selagi proses `spotme` berjalan; tetapan dimuatkan semula apabila aplikasi dibuka semula.

## Aliran fungsi
- Persediaan hari bekerja sekali sahaja; jadual menggunakan tarikh, hari dan jam sebenar peranti.
- Simpan ID pengguna, lokasi dan nilai ulasan/sebab/catatan tugasan.
- Tetapkan masa daftar masuk dan daftar keluar.
- Pada masa masuk/keluar, portal SPOT-Me dibuka secara automatik.
- Jika diaktifkan, tindakan pergerakan dijadualkan setiap satu jam bermula satu jam selepas masa masuk dan sehingga masa keluar.
- Pada masa pergerakan, Android Termux cuba membaca koordinat GPS sebenar melalui Termux:API, kemudian portal dibuka.
- `0. Exit` atau Ctrl+C menghentikan scheduler. Tiada proses latar ditinggalkan.
- Tetapan kekal selepas keluar dan digunakan semula apabila `spotme` dibuka lagi.

## Pengesahan rekod rasmi
Aplikasi menyediakan masa, tetapan dan bacaan GPS untuk semakan serta membuka portal pada masa jadual. Pengguna perlu menyemak dan mengesahkan penghantaran rekod rasmi di portal sendiri. Versi ini tidak menghantar daftar masuk, daftar keluar atau pergerakan secara senyap/automatik, dan tidak mereka masa atau koordinat.

Kata laluan tidak disimpan. Login portal dilakukan oleh pengguna. ID pengguna dan tetapan disimpan setempat dalam `~/.config/spotme-cli/` dengan permission terhad.

## GPS
- Android: pasang aplikasi Termux:API dan pakej `termux-api`; beri kebenaran lokasi kepada Termux.
- Kali/WSL: arahan GPS Termux tidak tersedia. Bacaan GPS memerlukan penerima GPS dan integrasi sistem yang sesuai.

## Keperluan
- Python 3.9 atau lebih baharu.
- Android: Termux + Termux:API (untuk GPS).

## Jalankan
```bash
python3 spotme.py
```

Pada persediaan pertama, pilih hari bekerja. Kemudian gunakan medan 1–11 untuk mengubah tetapan. Biarkan CLI terbuka supaya jadual berjalan.

## Medan tetapan
1. Pengguna / ID log masuk
2. Kata laluan (tidak disimpan)
3. Lokasi
4. Ulasan
5. Sebab bekerja dari rumah
6. Sebab lewat
7. Sebab tidak cukup jam
8. Catatan tugasan
9. Masa masuk
10. Masa keluar
11. Auto pergerakan setiap satu jam

## Lesen
MIT
