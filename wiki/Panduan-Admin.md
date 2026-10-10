# Panduan Admin

## Masuk dashboard

1. Buka `/admin/login`.
2. Masuk menggunakan akun admin yang disediakan pengelola.
3. Jangan berbagi token login atau membiarkan sesi admin terbuka di perangkat bersama.

## Pengaturan ujian

Pada menu **Pengaturan**, admin dapat:

- mengatur durasi TKJ dan asesmen skenario;
- mengatur jumlah soal TKJ serta ambang pelanggaran;
- mengaktifkan kewajiban Safe Exam Browser (SEB);
- menyalakan/mematikan babak situasi kerja DISC.

Babak DISC aktif secara default dan wajib dikerjakan jika aktif. Durasi tetap 60 menit. Perubahan toggle berdampak pada alur ujian yang memakai konfigurasi, bukan menghapus hasil terdahulu.

## Mengelola token dan soal

- Buat token dari halaman **Token** dan sampaikan token secara pribadi ke peserta.
- Periksa status token untuk mengetahui apakah token belum dipakai, aktif, atau selesai.
- Kelola soal TKJ pada **Bank Soal**. Soal mengandung kunci jawaban dan aksesnya terbatas untuk admin.

## Membaca hasil peserta

1. Buka menu **Hasil & Analitik**.
2. Cari peserta menggunakan nama/sekolah/token.
3. Buka **Detail** untuk melihat ringkasan keseluruhan, hasil skenario, ringkasan DISC, dan log pelanggaran.
4. Cermati status kelengkapan serta penanda submit otomatis.
5. Gunakan ringkasan sebagai dasar pertanyaan lanjutan; tentukan penempatan sendiri.

Hasil DISC hanya tersedia bagi admin. Untuk DISC baru, diagram radar menampilkan proporsi pilihan dari soal yang dijawab, bukan persen kecocokan suatu posisi. Hasil parsial perlu dibaca dengan lebih hati-hati.

## Ekspor

Gunakan tombol CSV atau Excel hanya jika diperlukan. Berkas berisi data peserta; simpan secara aman dan ikuti kebijakan retensi organisasi.
