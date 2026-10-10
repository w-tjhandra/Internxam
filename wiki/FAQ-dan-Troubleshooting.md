# FAQ dan Troubleshooting

## Detail peserta menampilkan error saat membuka grafik DISC

Pastikan data hasil DISC cukup lengkap. Hasil historis yang kosong/tidak lengkap tidak semestinya menghentikan halaman; bagian grafik baru dapat menampilkan keterangan bila datanya tidak cukup.

## Peserta tidak dapat menyelesaikan DISC manual

Submit manual mensyaratkan semua 30 situasi terjawab. Peserta dapat memakai navigasi nomor soal untuk menemukan soal kosong. Jika waktu habis, jawaban tersimpan akan otomatis diproses sebagai hasil parsial.

## Peserta kehilangan koneksi

Jawaban yang berhasil dikirim tersimpan di backend. UI juga dapat mengantrekan jawaban situasi kerja saat offline dan mengirimnya lagi ketika koneksi pulih. Sebelum submit, pastikan indikator simpan tidak menunjukkan jawaban tertunda/gagal.

## Babak DISC tidak muncul

Admin perlu memeriksa toggle DISC pada pengaturan ujian. Jika dimatikan, peserta melewati babak baru. Hasil historis tidak dihapus oleh toggle.

## Backend gagal terhubung ke PostgreSQL

Pastikan PostgreSQL berjalan, `DB_DSN` valid, database telah dibuat, dan pengguna memiliki hak akses yang diperlukan. Periksa log backend untuk detail koneksi; jangan menaruh kredensial di tiket publik.

## Build frontend bermasalah

Jalankan perintah dari `frontend/`, pastikan dependency terpasang dan versi Node sesuai lingkungan proyek. Error `eslint-loader` dapat muncul sebagai konfigurasi legacy pada build; periksa apakah build tetap melaporkan `Compiled successfully` sebelum menyimpulkan gagal.
