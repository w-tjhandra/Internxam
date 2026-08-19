# PRD — SecureCBT (Sistem Ujian Online TKJ + Psikotes DISC)

## Problem Statement (asli)
Platform ujian online berbasis token sekali pakai untuk seleksi siswa: Tes TKJ (PG intermediate) dilanjutkan otomatis ke Psikotes DISC. Peserta masuk tanpa registrasi (token dari admin). Kamera & screen-share sebagai deterrent psikologis — TIDAK ada media direkam/disimpan, hanya log pelanggaran teks. Proctoring soft-lock + verifikasi Safe Exam Browser (toggle per konfigurasi).

## User Personas
- **Peserta (Guest):** siswa, akses via token 8 karakter, tanpa akun
- **Admin (Superuser):** guru/panitia — kelola token, soal, hasil (admin@axelbit.com)

## Arsitektur
- React SPA (CRA + craco), Tailwind + shadcn, phosphor icons, recharts — desain "Swiss High-Contrast" (Work Sans / IBM Plex Sans / IBM Plex Mono)
- FastAPI (server.py tunggal) + seed_data.py (27 soal TKJ + 24 grup DISC)
- MongoDB: admins, tokens, participants (embed answers+disc_result), questions, disc_items, violation_logs, exam_configs, login_attempts
- Timer server-side (tkj_started_at/disc_started_at + durasi config); token: unused→active→completed/expired/revoked
- Randomisasi soal + urutan opsi per peserta (question_order + option_order map, jawaban dipetakan balik saat skoring)
- Auth admin: JWT (12 jam) + bcrypt + brute-force lockout (5x/15mnt). Rate limit /api/exam/start 10/mnt/IP (in-memory)
- SEB: config require_seb + seb_browser_exam_key; validasi header X-SafeExamBrowser-RequestHash (sha256(url+BEK)) atau keberadaan header jika BEK kosong

## Sudah Diimplementasikan (Juni 2026 — MVP)
- [x] Auth admin JWT+bcrypt, seed admin, brute force protection
- [x] Token: generate batch (crypto-random, tanpa O/0/I/1), revoke, filter, export CSV+XLSX
- [x] Engine TKJ: 27 soal seed berkualitas (subnetting, VLAN, routing, keamanan, dll), timer server-side, autosave per soal, resume (refresh/re-entry token sama), grid navigasi, offline queue localStorage
- [x] DISC: 24 grup forced-choice (Paling/Kurang), skoring Most/Least/Change otomatis, profil dominan + interpretasi, transisi otomatis TKJ→DISC
- [x] Anti-cheat: fullscreen paksa + pause overlay, visibility detection (peringatan 1-2, auto-submit ke-3), camera watchdog (pause saat mati), preflight kamera+screen share (gimmick, tidak dikirim ke server), violation log teks ke DB, verifikasi header SEB (toggle)
- [x] Admin dashboard: KPI stats, manajemen token, CRUD bank soal + view item DISC, hasil & analitik (grafik DISC, log pelanggaran per peserta), export CSV/XLSX, konfigurasi ujian (durasi, jumlah soal, ambang, wajib-SEB + BEK)
- [x] Testing: backend 14/14 pass, frontend admin+landing pass (iteration_1)

## Backlog Prioritas
- P1: Edit item DISC via dashboard (sekarang read-only view; endpoint PUT /api/admin/disc-items sudah ada)
- P1: DialogDescription a11y pada dialog admin (warning console minor)
- P2: Live Monitor real-time (WebSocket) — data autosave sudah siap
- P2: Import soal massal (Excel)
- P2: Snapshot webcam saat pelanggaran (bukti visual ringan)
- P2: Multi-admin dengan role (operator vs superadmin)
- P2: Cleanup otomatis peserta 'active' terbengkalai (expiry saat ini hanya dicek saat re-entry)

## Catatan Teknis
- Preflight streams disimpan di module-level mediaStore (SPA, tidak putus antar route); jika peserta refresh di /exam, harus ulang preflight? Tidak — /exam tetap jalan tapi preview kamera kosong (stream null), watchdog tidak aktif. Re-entry token sama mengembalikan posisi soal terakhir.
- Kredensial: /app/memory/test_credentials.md
