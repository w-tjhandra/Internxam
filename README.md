# Internxam

Internxam adalah aplikasi ujian dan asesmen peserta PKL. Aplikasi menyediakan ujian kemampuan teknis TKJ, asesmen skenario situasi kerja, dan asesmen perilaku berbasis situasi kerja yang merangkum kecenderungan DISC. Admin mengelola token, bank soal, konfigurasi ujian, dan membaca hasil peserta.

> Hasil asesmen skenario dan ringkasan DISC adalah bahan pertimbangan awal. Keduanya bukan diagnosis, bukan keputusan lulus/gagal, dan tidak menentukan posisi peserta secara otomatis. Keputusan penempatan tetap dibuat admin dengan mempertimbangkan konteks, minat, percakapan, dan hasil praktik.

## Fitur

- Alur peserta dengan token dan penyimpanan progres.
- Asesmen TKJ dengan pilihan jawaban diacak dan penilaian otomatis.
- Asesmen situasi kerja PKL dengan skor rubrik yang dapat ditinjau.
- Babak DISC berbasis 30 situasi kerja; durasi 60 menit; jawaban yang sudah tersimpan dikirim otomatis saat waktu habis.
- Dashboard admin untuk ringkasan aktivitas, pengelolaan token, soal TKJ, pengaturan ujian, dan hasil peserta.
- Detail peserta terpadu yang merangkum TKJ, skenario, dan DISC. Ringkasan DISC menggunakan diagram radar.
- Ekspor hasil ke CSV dan Excel.
- Proteksi ujian yang mencakup Safe Exam Browser (opsional), log pelanggaran, kamera, dan pemulihan progres.

## Teknologi

- **Frontend:** React, Create React App/CRACO, Tailwind CSS, Radix UI, Recharts.
- **Backend:** Python, FastAPI, Pydantic, asyncpg.
- **Database:** PostgreSQL.
- **Pembaruan langsung:** WebSocket admin.

## Struktur repo

```text
backend/
  app/
    core/         Konfigurasi dan keamanan
    db/           Skema, seeding, lifecycle koneksi
    routers/      API auth, admin, ujian, dan hasil
    schemas/      Validasi request
    services/     Alur ujian dan penskoran asesmen
  tests/
frontend/
  src/
    components/   Komponen antarmuka
    features/     Komponen per fitur asesmen
    pages/        Halaman peserta dan admin
docs/             Dokumentasi teknis proyek
wiki/             Naskah halaman untuk GitHub Wiki
issues/           Dokumen perencanaan lokal yang dipilih untuk dilacak
```

## Menjalankan untuk pengembangan

### Prasyarat

- Node.js dan npm (atau Yarn yang sesuai dengan `frontend/package.json`).
- Python sesuai versi yang dipakai tim dan paket di `backend/requirements.txt`.
- PostgreSQL yang dapat diakses dari backend.

### 1. Siapkan backend

Buat database PostgreSQL, lalu siapkan `backend/.env`:

```dotenv
DB_DSN=postgresql://USER:PASSWORD@127.0.0.1:5432/internxam
JWT_SECRET=GANTI_DENGAN_SECRET_ACAK_PANJANG
CORS_ORIGINS=http://localhost:3000,https://localhost:3000
```

Jangan commit `.env`, kata sandi, token, atau data peserta. Gunakan secret yang kuat dan kredensial database khusus untuk tiap lingkungan. Pada startup, aplikasi menyiapkan skema dan seeding melalui `backend/app/db/`.

Pasang dependency dan jalankan API:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Dokumentasi OpenAPI tersedia saat API berjalan pada `/docs` dan `/redoc`.

### 2. Siapkan frontend

Di terminal lain:

```bash
cd frontend
npm install
npm start
```

Frontend development dikonfigurasi menggunakan HTTPS. Jika backend tidak berada di konfigurasi proxy lokal, atur `REACT_APP_BACKEND_URL` di environment frontend ke origin backend, misalnya `http://127.0.0.1:8000`.

Alternatifnya, gunakan skrip `./start-dev.sh` dari root setelah dependency frontend/backend dan konfigurasi database siap. Skrip menjalankan frontend dan backend serta menghentikan keduanya ketika proses dihentikan.

## Akses admin

Admin masuk melalui `/admin/login`. Akun awal dibuat oleh proses seed backend pada database baru. Kredensial bootstrap tidak dicantumkan dalam dokumentasi repo; verifikasi dan ganti pengaturan akun awal sebelum lingkungan dapat diakses pengguna lain. Jangan gunakan akun bootstrap untuk produksi.

## Alur ujian

1. Admin membuat token dan membagikannya kepada peserta.
2. Peserta mengisi identitas, melakukan persiapan, lalu memulai ujian dengan token.
3. Peserta mengerjakan TKJ.
4. Peserta mengerjakan asesmen skenario situasi kerja.
5. Jika babak DISC diaktifkan di pengaturan admin, peserta mengerjakan 30 situasi kerja dalam 60 menit. Babak ini wajib diselesaikan saat aktif.
6. Submit manual DISC meminta semua soal dijawab. Saat waktu habis, jawaban tersimpan dikirim otomatis; pertanyaan tanpa jawaban tetap kosong.
7. Admin membuka detail peserta untuk membaca hasil asesmen bersama. Sistem tidak memilih atau merekomendasikan posisi.

## Pengaturan dan interpretasi

- DISC aktif secara default dan dapat dinyalakan/dimatikan admin.
- Hasil/interpretasi DISC hanya ditampilkan kepada admin.
- Grafik radar menggambarkan proporsi jawaban DISC yang terjawab, bukan probabilitas cocok pada suatu posisi.
- Hasil skenario merupakan asesmen pilot; skor tidak boleh dianggap prediktor kinerja yang telah tervalidasi.
- Ringkasan keseluruhan hanya merangkum data yang tersedia. Data parsial atau kosong perlu dibaca dengan hati-hati.

Rincian asumsi produk dan kriteria penerimaan ada di [PRD asesmen DISC](issues/prd-asesmen-disc-babak-ketiga.md).

## Pengujian dan build

Backend unit tests:

```bash
cd backend
python -m pytest tests/unit
```

Tes integrasi API memerlukan server dan database disposable. Lihat [panduan backend](backend/README.md) sebelum menjalankannya.

Frontend production build:

```bash
cd frontend
npm run build
```

## Dokumentasi

- [Indeks dokumentasi teknis](docs/README.md)
- [Arsitektur aplikasi](docs/architecture.md)
- [API](docs/api.md)
- [Asesmen dan interpretasi hasil](docs/assessments.md)
- [Pengoperasian dan keamanan](docs/operations.md)
- [Naskah GitHub Wiki](wiki/Home.md)
- [Mempublikasikan dokumentasi/wiki](docs/publishing.md)

## Catatan rilis

Pastikan review keamanan, pengaturan secret, akun admin, retensi data, backup PostgreSQL, dan kebijakan ujian diselesaikan sebelum deployment produksi. Instrumen situasi kerja perlu ditinjau oleh pemilik proses agar tetap aktual, jelas, adil, dan relevan dengan pekerjaan.
