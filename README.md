# SPOT-Me CLI

Pembantu CLI ringan untuk Kali Linux, WSL dan Android Termux.

## Fungsi
- Simpan tetapan pengguna dan butiran borang secara setempat.
- Simpan hari bekerja semasa persediaan pertama.
- Peringatan daftar masuk/keluar mengikut jam peranti.
- Peringatan pergerakan setiap satu jam.
- Buka portal SPOT-Me pada waktu ditetapkan.
- Pada Android Termux, cuba baca GPS sebenar melalui Termux:API.
- Tetapan disimpan dalam ~/.config/spotme-cli/ dengan permission terhad.

## Had penting
Versi ini tidak menghantar atau mengesahkan rekod kehadiran/pergerakan secara automatik. Ia membuka portal dan memaparkan peringatan/lokasi supaya pengguna boleh menyemak maklumat dan membuat pengesahan rasmi sendiri. Tiada masa atau koordinat direka atau dipalsukan.

Pada Kali/WSL, GPS tidak tersedia secara automatik melainkan ada penerima GPS dan perisian yang sesuai. Pada Android, pasang aplikasi Termux:API dan pakej termux-api, kemudian beri kebenaran lokasi.

Kata laluan tidak disimpan. ID pengguna dan tetapan lain disimpan dalam fail konfigurasi tempatan.

## Keperluan
- Python 3.9 atau lebih baharu.
- Android: Termux dan Termux:API (pilihan, untuk GPS/notifikasi).

## Jalankan
    python3 spotme.py

Pada kali pertama, pilih hari bekerja. Kemudian isi/ubah medan 1–11 melalui menu. Tetapan kekal selepas aplikasi ditutup.

Aplikasi perlu kekal berjalan untuk memantau waktu. Pilih 0. Exit atau tekan Ctrl+C untuk menghentikan scheduler. Jalankan semula spotme untuk memuatkan tetapan tersimpan.

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