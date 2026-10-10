# Mempublikasikan dokumentasi dan GitHub Wiki

## Dokumentasi di repository

`README.md`, `docs/`, dan `wiki/` dapat di-commit sebagai bagian dari repository aplikasi. Tautan pada README membantu pembaca menavigasi dokumentasi setelah repository di-push.

## GitHub Wiki berbeda dari folder repository

Folder lokal `wiki/` adalah naskah sumber yang dapat direview dan disimpan bersama kode. GitHub tidak otomatis memublikasikan folder tersebut sebagai tab **Wiki** repository. GitHub Wiki disimpan pada repository Git terpisah bernama `<owner>/<repo>.wiki.git`.

Untuk menerbitkan halaman ke GitHub Wiki:

1. Aktifkan fitur Wiki pada repository GitHub bila belum aktif.
2. Clone repository wiki menggunakan URL GitHub Wiki yang ditampilkan GitHub.
3. Salin isi berkas Markdown dari folder lokal `wiki/` ke repository Wiki.
4. Pastikan nama halaman mengikuti slug GitHub Wiki (contoh `Home.md`, `Panduan-Admin.md`).
5. Periksa tautan antar halaman pada tampilan Wiki, lalu commit dan push ke repository wiki.

Contoh alur perintah (ganti placeholder dengan repo milikmu):

```bash
git clone https://github.com/OWNER/REPO.wiki.git internxam-wiki
cp wiki/*.md internxam-wiki/
cd internxam-wiki
git add *.md
git commit -m "Add Internxam wiki documentation"
git push
```

Jalankan perintah dari root repo aplikasi untuk langkah `cp`, atau sesuaikan path sumber. Untuk repository privat, gunakan metode autentikasi GitHub yang sudah dikonfigurasi secara lokal; jangan menanam token akses di perintah, file, atau dokumentasi.

Perintah salin tersebut menyalin file sumber apa adanya. Bila GitHub Wiki tidak mengubah tautan relatif folder, sesuaikan tautan halaman agar mengarah ke halaman Wiki yang benar.
