# Arsitektur

## Gambaran umum

```text
Browser peserta/admin
        |
        | HTTPS/HTTP JSON API
        v
React frontend  <---- WebSocket live admin
        |
        v
FastAPI application
  ├── auth router
  ├── admin router
  ├── exam router
  ├── results router
  └── workflow/scoring services
        |
        v
PostgreSQL (asyncpg)
```

Frontend menggunakan React Router untuk halaman peserta dan dashboard admin. Pemanggilan HTTP dilakukan melalui Axios. Backend FastAPI mengelompokkan endpoint berdasarkan domain dan menyimpan data asesmen dalam PostgreSQL.

## Struktur backend

- `app/main.py`: membuat aplikasi FastAPI, memasang middleware CORS, dan mendaftarkan router.
- `app/runtime.py`: pool database, konfigurasi bersama, autentikasi admin, helper waktu/export, dan WebSocket.
- `app/routers/auth.py`: login admin dan pemeriksaan sesi admin.
- `app/routers/admin.py`: token, soal TKJ, konfigurasi ujian, dan statistik.
- `app/routers/exam.py`: pembuatan sesi, jawaban, submit tahap, dan log pelanggaran.
- `app/routers/results.py`: daftar hasil, detail peserta, dan ekspor.
- `app/services/exam_workflow.py`: transisi tahap, snapshot soal, state resume, dan orkestrasi penilaian.
- `app/services/scenario_assessment.py`: scoring asesmen skenario.
- `app/services/work_disc.py`: bank soal berversi dan scoring asesmen DISC berbasis situasi kerja.
- `app/db/schema.py`: pembuatan/migrasi ringan tabel serta data awal.
- `app/db/lifecycle.py`: membuka pool, inisialisasi skema, seeding, dan penutupan pool.

`server.py` menyediakan kompatibilitas untuk import ASGI lama. Entry point pengembangan yang disarankan adalah `app.main:app`.

## Struktur frontend

- `src/App.js`: daftar route.
- `src/pages/`: landing, persiapan peserta, ruang ujian, dan halaman dashboard.
- `src/features/exam/components/`: UI asesmen per tahap.
- `src/pages/admin/`: dashboard, token, bank soal, hasil, dan pengaturan.
- `src/lib/api.js`: konfigurasi Axios dan API base URL.
- `src/setupProxy.js`: proxy API untuk pengembangan lokal bila diaktifkan.

## Siklus sesi ujian

1. `/api/exam/start` memvalidasi token dan membuat/memulihkan peserta.
2. `tkj` menyimpan jawaban teknis; submit membentuk snapshot skenario.
3. `scenario` menyimpan jawaban dan hasil rubrik.
4. Jika `work_disc_enabled` aktif, penyelesaian skenario memulai `work_disc` dan membuat snapshot versi soal untuk peserta.
5. `work_disc` menyimpan jawaban per situasi; submit penuh atau timeout menghasilkan ringkasan DISC.
6. Sistem menandai sesi selesai dan token single sebagai selesai.
7. Endpoint admin membaca ringkasan tersimpan; jawaban DISC tidak dikirim ke endpoint publik untuk menampilkan interpretasi peserta.

Stage `disc` dan kolom `disc_result` lama dipertahankan untuk data historis. Tahap baru bernama `work_disc` agar format historis tidak bercampur dengan asesmen baru.

## Data dan versi

Tabel inti meliputi:

- `admins`, `login_attempts`: akun admin dan pembatasan login.
- `exam_configs`: waktu ujian, kebijakan SEB, dan toggle babak DISC.
- `tokens`: token ujian, status, dan kapasitas pemakaian.
- `questions`: bank soal TKJ.
- `participants`: identitas peserta, tahap, jawaban, hasil, snapshot, timestamp, dan status submit otomatis.
- `violation_logs`: catatan kejadian selama ujian.

Bank soal situasi kerja DISC dan aturan skor memiliki versi. Snapshot pertanyaan peserta diperlukan agar perubahan konten tidak mengubah asesmen yang sedang berjalan.

## Prinsip perubahan

- Perubahan schema harus idempotent saat aplikasi startup.
- Snapshot dan versi instrumen harus disimpan untuk menjaga keterlacakan hasil.
- Jangan menaruh jawaban benar TKJ atau metadata dimensi DISC di payload peserta.
- Saat menambah stage, periksa semua jalur resume, timer, timeout, pelanggaran, daftar hasil, dan ekspor.
- Perubahan data peserta perlu menjaga kompatibilitas data historis.
