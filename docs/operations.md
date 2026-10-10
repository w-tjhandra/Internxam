# Pengoperasian dan keamanan

## Konfigurasi lingkungan

Backend membaca `backend/.env`. Variabel inti:

| Variabel | Tujuan |
|---|---|
| `DB_DSN` | URL koneksi PostgreSQL |
| `JWT_SECRET` | Secret penandatanganan sesi admin |
| `CORS_ORIGINS` | Origin frontend yang diizinkan, dipisahkan koma |

Frontend dapat menggunakan `REACT_APP_BACKEND_URL` untuk menetapkan origin API. Jika kosong, frontend menggunakan origin saat ini/proxy development. Nilai `REACT_APP_*` dimasukkan ke bundle browser—jangan simpan secret di sana.

Template contoh untuk pengembangan:

```dotenv
DB_DSN=postgresql://USER:PASSWORD@127.0.0.1:5432/internxam
JWT_SECRET=ISI_SECRET_ACAK_MINIMAL_32_BYTE
CORS_ORIGINS=https://localhost:3000
```

Jangan commit file `.env`, kredensial, cookie, bearer token, atau ekspor berisi data peserta.

## Startup dan schema

Startup API membuka pool PostgreSQL, menginisialisasi tabel/perubahan kolom, lalu menjalankan seeding. Gunakan database disposable untuk tes integrasi; seeding dan test API dapat membuat/mengubah record.

Perintah development:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Legacy entry point:

```bash
uvicorn server:app
```

## Pengujian

```bash
cd backend
python -m pytest tests/unit
```

Tes integrasi mengirim request ke server eksternal dan dapat menulis data. Jalankan hanya terhadap database lokal/disposable:

```bash
RUN_API_INTEGRATION_TESTS=1 \
REACT_APP_BACKEND_URL=http://127.0.0.1:8000 \
python -m pytest tests/integration/test_api.py
```

Frontend:

```bash
cd frontend
npm test -- --watchAll=false
npm run build
```

## Checklist sebelum deployment

- Tetapkan `JWT_SECRET` acak dengan entropy tinggi dan jangan pakai default development.
- Pastikan kredensial bootstrap admin tidak digunakan; ganti dan batasi akses admin.
- Batasi `CORS_ORIGINS` pada domain frontend resmi.
- Gunakan HTTPS di frontend dan API; amankan WebSocket dengan TLS melalui reverse proxy.
- Gunakan akun PostgreSQL dengan hak minimum yang diperlukan serta backup terenkripsi.
- Terapkan backup/restore dan uji pemulihan database.
- Tinjau kebijakan retensi data peserta, log pelanggaran, dan ekspor.
- Jangan tampilkan hasil DISC kepada peserta; akses hasil hanya melalui endpoint admin.
- Uji timer server-side, resume, submit timeout, SEB bila diwajibkan, dan alur token.
- Tinjau instrumen asesmen dan pemberitahuan penggunaan data sebelum ujian nyata.

## Operasional data

Ekspor hasil mengandung informasi peserta. Batasi akses unduh, simpan di lokasi terproteksi, dan hapus sesuai kebijakan organisasi. Jangan menaruh ekspor database atau file `.env` di repository.
