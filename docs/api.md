# API

Base path API adalah `/api`. Request/response menggunakan JSON kecuali endpoint ekspor. Dokumentasi OpenAPI interaktif tersedia pada `/docs` ketika backend berjalan.

## Autentikasi

- Login admin: `POST /auth/login`.
- Identitas admin aktif: `GET /auth/me`.
- Endpoint `/admin/*` memerlukan bearer token admin. Frontend menyimpan access token di `localStorage` untuk sesi dashboard.
- Endpoint ujian peserta menggunakan `participant_id` dan `token` dalam request body. Endpoint ujian tertentu juga memeriksa kebijakan Safe Exam Browser (SEB).

Jangan kirim token admin atau token peserta dalam query string atau log yang dapat diakses publik.

## Admin

| Method | Path | Keterangan |
|---|---|---|
| `GET` | `/admin/stats` | Statistik dashboard |
| `GET`, `PUT` | `/admin/config` | Membaca/mengubah durasi, jumlah soal, SEB, dan toggle DISC |
| `POST` | `/admin/tokens/generate` | Membuat token peserta |
| `GET` | `/admin/tokens` | Daftar token; query `status` opsional |
| `POST` | `/admin/tokens/{token_id}/revoke` | Menonaktifkan token yang masih dapat direvoke |
| `GET` | `/admin/tokens/export` | Ekspor token (`format=csv` atau `xlsx`) |
| `GET`, `POST` | `/admin/questions` | Membaca dan membuat soal TKJ |
| `POST` | `/admin/questions/import` | Import soal dari CSV/Excel |
| `PUT`, `DELETE` | `/admin/questions/{qid}` | Mengubah/menghapus soal TKJ |
| `GET`, `PUT` | `/admin/disc-items` | Konten DISC historis |
| `GET` | `/admin/scenario-items` | Bank asesmen skenario dan metadata versinya |
| `GET` | `/admin/results` | Daftar ringkasan hasil peserta |
| `GET` | `/admin/results/{pid}` | Detail hasil peserta, termasuk ringkasan DISC admin-only |
| `GET` | `/admin/results/export` | Ekspor hasil (`format=csv` atau `xlsx`) |

## Ujian peserta

Semua body terkait sesi menggunakan:

```json
{
  "participant_id": "ID_PESERTA",
  "token": "TOKEN_UJIAN"
}
```

| Method | Path | Keterangan |
|---|---|---|
| `GET` | `/exam/seb-status` | Status kebijakan/deteksi SEB |
| `POST` | `/exam/start` | Memulai atau melanjutkan sesi |
| `POST` | `/exam/session` | Memulihkan state sesi |
| `POST` | `/exam/answer` | Menyimpan jawaban TKJ |
| `POST` | `/exam/tkj/submit` | Menyelesaikan tahap TKJ |
| `POST` | `/exam/scenario/answer` | Menyimpan jawaban skenario |
| `POST` | `/exam/scenario/submit` | Menyelesaikan skenario dan memulai DISC bila aktif |
| `POST` | `/exam/work-disc/answer` | Menyimpan pilihan untuk satu situasi DISC |
| `POST` | `/exam/work-disc/submit` | Submit manual DISC; seluruh soal harus terjawab |
| `POST` | `/exam/disc/answer` | Endpoint format DISC historis |
| `POST` | `/exam/disc/submit` | Submit format DISC historis |
| `POST` | `/exam/violation` | Mencatat kejadian keamanan ujian |
| `WebSocket` | `/api/admin/ws/live` | Peristiwa ujian untuk dashboard admin |

## Timeout dan status DISC

Babak DISC baru aktif secara default dan dapat dimatikan melalui konfigurasi admin. Durasi ditetapkan 60 menit. Saat timeout, backend menyelesaikan sesi menggunakan jawaban yang sudah tersimpan dan butir kosong dibiarkan tidak terjawab. Hasil detail/admin mencatat kelengkapan dan apakah submit timeout terjadi.

Jika menambah atau mengubah endpoint, pastikan daftar route dan dependency keamanan diperbarui pada test route.
