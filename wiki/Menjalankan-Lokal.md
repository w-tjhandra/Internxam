# Menjalankan Lokal

## Prasyarat

- Node.js/npm.
- Python dan dependency backend.
- PostgreSQL lokal atau database development yang diizinkan.

## Backend

Buat `backend/.env` yang tidak di-commit:

```dotenv
DB_DSN=postgresql://USER:PASSWORD@127.0.0.1:5432/internxam
JWT_SECRET=GANTI_DENGAN_SECRET_ACAK
CORS_ORIGINS=https://localhost:3000
```

Kemudian:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

Di terminal lain:

```bash
cd frontend
npm install
npm start
```

Skrip root `./start-dev.sh` dapat digunakan untuk menjalankan kedua server bersama-sama setelah dependency dan database disiapkan.

## Tes dan build

```bash
cd backend
python -m pytest tests/unit
```

```bash
cd frontend
npm run build
npm test -- --watchAll=false
```

Tes integrasi backend menggunakan API dan database; jalankan hanya pada lingkungan tes yang dapat dibuang. Detail ada di [README proyek](../README.md) dan [dokumentasi operasi](../docs/operations.md).
