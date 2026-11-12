# TASK 2 — Run & Assess Application

**Waktu evaluasi:** 21 Oktober 2026, 18:46 WIB (Asia/Jakarta)

**Evaluasi ulang:** 21 Oktober 2026, 18:54 WIB (Asia/Jakarta)

## 1. Prerequisites

- Python 3.8.10 dan virtual environment `backend/venv` tersedia.
- Paket backend yang diperiksa sudah terpasang: FastAPI, SQLAlchemy, Alembic, Uvicorn, psycopg2, dan Pydantic.
- Node.js 20.20.2, npm 10.8.2, serta `frontend/node_modules` tersedia.
- Frontend memakai `VITE_API_URL` dengan fallback ke `http://localhost:8000`. Backend memakai `DATABASE_URL` dengan fallback ke PostgreSQL lokal. Nilai kredensial tidak dicatat di dokumen ini.
- README mencantumkan PostgreSQL, migrasi Alembic, Uvicorn, dan `npm run dev` sebagai alur setup.
- Docker CLI dan `docker-compose` tersedia, tetapi akses ke Docker daemon ditolak. Status container, volume, dan data yang mungkin tersimpan di dalamnya tidak dapat diperiksa.

## 2. Startup Results

- **Backend:** berhasil startup di `http://127.0.0.1:8000`.
- **Frontend:** Vite berhasil startup di `http://127.0.0.1:5173`. Untuk menghindari perubahan file repository, frontend dijalankan dari salinan sementara di `/tmp`.
- **Database pada evaluasi pertama:** tidak tersedia di `127.0.0.1:5432`; koneksi ditolak.
- **Database pada evaluasi ulang:** koneksi berhasil digunakan oleh endpoint produk dan storefront setelah pengguna menjalankan `sudo docker start ecommerce_db_1`. Namun, identitas container, status Docker, dan volume tidak dapat dikonfirmasi langsung karena akses ke socket Docker tetap ditolak.
- Backend dan frontend tetap berjalan untuk evaluasi ulang. Frontend berjalan dari salinan sementara di `/tmp`, bukan dari working tree.

## 3. Verification Results

- `GET /` pada backend: **200 OK**.
- `GET /openapi.json`: **200 OK**.
- `GET /` pada frontend: **200 OK**.
- `GET /brands/default`: **200 OK**. Request pertama timeout saat kompilasi awal; percobaan berikutnya berhasil.
- Pada evaluasi pertama, `GET /products/?brand_id=1`: **500 Internal Server Error**, karena backend gagal terkoneksi ke PostgreSQL.
- Pada evaluasi ulang, `GET /products/?brand_id=1`: **200 OK**.
- Pada evaluasi ulang, `GET /storefront/default/config`: **200 OK** dan `GET /products/catalog?brand_id=1`: **200 OK**.
- Pada evaluasi ulang, permintaan dengan `Origin: http://127.0.0.1:5173` menerima header CORS yang mengizinkan origin tersebut; respons endpoint yang diuji **200 OK**.
- `alembic current` berhasil membaca versi database dan melaporkan `20260501_0013 (head)`. Tidak ada migrasi yang dijalankan.
- Integrasi backend-database untuk endpoint yang diuji terverifikasi. Integrasi dan alur pengguna melalui browser belum diuji penuh.

## 4. Issues Found

- Pada evaluasi pertama, log backend mencatat `sqlalchemy.exc.OperationalError`: koneksi ke `localhost:5432` ditolak. Kondisi ini tidak terulang pada endpoint database-backed yang diuji saat evaluasi ulang.
- Pemeriksaan Docker tetap gagal dengan `permission denied` pada socket Docker. Karena itu status dan konfigurasi container serta volume database tidak dapat diverifikasi langsung, walaupun koneksi aplikasi ke database berhasil pada evaluasi ulang.
- Vite melakukan kompilasi route dan optimasi dependency saat startup. Setelah proses awal, route yang diuji merespons normal.

## 5. Limitations

- Isi dan kebijakan persistensi volume database belum diperiksa. Versi migrasi yang dilaporkan database adalah `20260501_0013 (head)`; migrasi tidak diterapkan.
- Tes otomatis tidak dijalankan.
- Pemeriksaan frontend dilakukan melalui HTTP, bukan pengujian interaksi browser penuh.
- Pada saat dokumentasi ini diperbarui, `git status --short` menunjukkan file yang saat itu bernama `docs/discovery/run-asses-app.md` (sekarang `docs/discovery/run-assessment.md`) sebagai file untracked. Branch `master` dan commit terakhir `7c3f2a0` adalah hasil pemeriksaan sebelumnya; status tersebut tidak menyatakan working tree bersih.
- Tidak ada kode aplikasi, konfigurasi, atau data database yang diubah dalam evaluasi. File dokumentasi ini adalah satu-satunya file repository yang sedang ditambahkan/diperbarui; salinan frontend sementara berada di `/tmp`.

## 6. Recommended Next Steps

1. Sebelum tindakan terhadap container atau volume, verifikasi container dan volume melalui sesi yang memiliki akses Docker; sesi evaluasi ini tidak dapat membacanya.
2. Koneksi backend-database dan versi migrasi sudah terbukti pada endpoint yang diuji; hindari menjalankan migrasi karena tidak diperlukan untuk verifikasi ini.
3. Lakukan pemeriksaan browser penuh untuk memastikan interaksi frontend dan pemanggilan API dari UI, karena sejauh ini frontend diuji melalui HTTP dan CORS.
