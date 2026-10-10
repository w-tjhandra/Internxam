# PRD: Asesmen DISC sebagai Babak Ketiga dan Arahan Penempatan Awal

- **Status:** Draft diperbarui berdasarkan arahan pemilik produk
- **Pemilik:** Tim Internxam
- **Jenis:** Product requirement
- **Tanggal:** 10 Oktober 2026

## Ringkasan

Tambahkan asesmen DISC sebagai babak ketiga dalam alur ujian peserta, setelah asesmen TKJ dan asesmen skenario situasi kerja. Hasil DISC membantu admin mendapatkan gambaran awal kecenderungan peserta sebagai salah satu bahan pertimbangan saat admin sendiri menentukan posisi awal peserta.

DISC digunakan sebagai **ringkasan pendukung kurasi dan penempatan awal**, bukan label tetap, diagnosis, nilai kelulusan, atau keputusan final. Sistem tidak menentukan atau merekomendasikan posisi; keputusan penempatan dibuat oleh admin dan dapat divalidasi melalui diskusi dengan peserta serta praktik kerja.

## Latar belakang dan masalah

Kantor memiliki beberapa posisi yang dapat ditempati peserta. Hasil TKJ membantu membaca kemampuan teknis, sementara hasil skenario memberi konteks tentang respons peserta terhadap situasi kerja. Keduanya belum selalu memberi arah yang jelas untuk menentukan posisi pertama yang sebaiknya dicoba.

Jika penempatan hanya berdasarkan intuisi, keputusan dapat terasa 50/50 dan sulit dibandingkan antar peserta. DISC diharapkan menambah data terstruktur untuk membentuk hipotesis awal tentang posisi yang patut dieksplorasi.

## Tujuan

- Menambahkan DISC sebagai babak ketiga setelah TKJ dan skenario.
- Memberi admin ringkasan kecenderungan DISC yang mudah dibaca.
- Menyediakan ringkasan kecenderungan DISC yang membantu admin mempertimbangkan penempatan.
- Membantu admin mengurangi ketergantungan pada intuisi tanpa mengklaim hasil sebagai kepastian.
- Membiarkan keputusan posisi sepenuhnya pada admin, dengan dukungan hasil DISC dan asesmen lainnya.

## Bukan tujuan

- Menggunakan DISC sebagai penentu lulus/gagal atau dasar tunggal pemilihan peserta.
- Menyatakan seseorang pasti cocok atau tidak cocok pada suatu posisi.
- Menghasilkan persentase probabilitas kecocokan sebelum tersedia validasi yang memadai.
- Menggantikan minat peserta, wawancara, observasi, kemampuan teknis, atau evaluasi praktik.
- Membuat profil DISC sebagai diagnosis atau penilaian karakter moral.

## Pengguna dan kebutuhan

### Peserta

Sebagai peserta, saya ingin menyelesaikan asesmen DISC dengan alur yang jelas dan mengetahui status penyelesaiannya, agar seluruh rangkaian ujian dapat saya selesaikan tanpa kehilangan progres.

### Admin/kurator

Sebagai admin, saya ingin melihat ringkasan hasil DISC bersama hasil asesmen lain, agar saya dapat menggunakannya sebagai bahan pertimbangan saat menentukan posisi peserta.

## Alur yang diusulkan

1. Peserta menyelesaikan babak TKJ.
2. Peserta menyelesaikan babak skenario situasi kerja.
3. Jika babak DISC aktif di dashboard admin, sistem memulai babak DISC dan menampilkan petunjuk singkat tentang cara menjawab. Babak ini wajib diselesaikan sebelum ujian dinyatakan selesai.
4. Peserta menjawab seluruh butir DISC dan mengirimkan hasil.
5. Sistem mencatat status penyelesaian rangkaian ujian setelah babak DISC selesai.
6. Peserta tidak melihat hasil atau interpretasi DISC setelah mengirimkan jawaban.
7. Admin membuka satu detail peserta untuk membaca ringkasan TKJ, skenario, dan DISC bersama-sama.
8. Admin mempertimbangkan ringkasan DISC bersama hasil asesmen lain dan menentukan sendiri posisi peserta.

DISC aktif secara default sebagai babak wajib, namun admin memiliki kontrol on/off di dashboard pengaturan ujian. Ketika aktif, peserta harus menyelesaikannya agar status ujian menjadi selesai. Ketika nonaktif, alur ujian melewati babak DISC tanpa menghapus hasil historis. Status peserta harus membedakan dengan jelas antara DISC nonaktif, belum mulai, sedang mengerjakan, selesai, dan hasil yang tidak cukup untuk interpretasi. Detail transisi peserta yang sudah berada di tahap lama perlu ditetapkan sebelum implementasi agar hasil historis tetap terbaca dan tidak tertukar dengan format baru.

## Kebutuhan produk

### 1. Babak DISC untuk peserta

- DISC menjadi tahap ujian tersendiri setelah skenario.
- Instrumen baru berisi tepat 30 butir yang berangkat dari perilaku dan situasi kerja yang aktual, realistis, dan umum terjadi; hindari soal yang terasa seperti cerita rekaan/dongeng.
- Butir dirancang untuk mengamati kecenderungan perilaku kerja yang relevan, bukan menetapkan karakter seseorang secara mutlak.
- Susun instrumen baru; jangan mengandalkan instrumen historis yang ada sebagai dasar. Butir harus ditinjau agar relevan dengan pekerjaan aktual sebelum dipakai.
- Petunjuk menjelaskan cara memilih jawaban dan menekankan bahwa tidak ada jawaban benar atau salah.
- Jawaban tersimpan secara aman dan progres dapat dipulihkan mengikuti mekanisme penyimpanan progres ujian yang berlaku.
- Pengiriman manual meminta seluruh 30 butir terjawab; submit otomatis saat waktu habis tetap menyimpan hasil parsial, termasuk jika ada butir kosong.
- Batas waktu pengerjaan adalah 60 menit untuk 30 butir.
- Saat waktu habis, sistem otomatis mengirim jawaban yang sudah tersimpan. Jawaban yang belum dijawab tetap kosong, tidak dianggap sebagai jawaban tertentu, dan hasil menampilkan jumlah butir yang terjawab serta status submit otomatis.
- Setelah pengiriman berhasil, peserta mendapat konfirmasi bahwa babak DISC selesai.
- Babak DISC wajib selama toggle admin dalam keadaan aktif; ketika dimatikan, peserta melewati babak ini dan ujian dapat selesai tanpa hasil DISC baru.

### 2. Ringkasan hasil DISC

Hasil hanya terlihat bagi admin dan disatukan pada detail peserta yang sama dengan hasil asesmen lain. Admin dapat melihat:

- status dan kelengkapan babak DISC;
- skor untuk dimensi DISC yang dihitung sistem;
- profil/kecenderungan utama jika data memenuhi syarat interpretasi;
- jumlah jawaban yang terjawab dari 30 butir dan apakah hasil dikirim otomatis karena waktu habis;
- visualisasi ringkasan DISC berbentuk lingkaran/radar (bukan bar chart), dengan penjelasan profil di samping diagram;
- ringkasan naratif kecenderungan peserta untuk membantu admin mempertimbangkan penempatan;
- catatan bahwa hasil adalah indikasi awal dan bukan label atau penentu keputusan.

Data kosong, tidak lengkap, atau menggunakan format lama tidak boleh menyebabkan halaman hasil admin gagal dimuat. Jika hasil tidak dapat diinterpretasikan, tampilkan status/keterangan yang sesuai dan jangan tampilkan interpretasi yang seolah-olah pasti.

### 3. Ringkasan untuk mendukung pertimbangan penempatan

- Sistem menampilkan ringkasan DISC yang relevan untuk membantu admin mempertimbangkan penempatan.
- Sistem tidak memilih, memeringkat, atau merekomendasikan posisi secara otomatis.
- Admin sendiri menentukan posisi peserta berdasarkan ringkasan DISC, hasil asesmen lain, kebutuhan pekerjaan, dan pertimbangannya.
- Jika keputusan penempatan dicatat di sistem, keputusan tersebut dimasukkan oleh admin dan bukan dihasilkan otomatis.
- Sistem tidak menampilkan persentase kecocokan pada versi awal.

### 4. Pengaturan ujian dan akses hasil

- Dashboard admin menyediakan toggle on/off untuk babak DISC.
- DISC aktif secara default dan wajib diselesaikan peserta selama toggle aktif.
- Hanya admin yang dapat melihat skor, grafik, dan interpretasi DISC.
- Menonaktifkan DISC berlaku untuk alur ujian yang menggunakan konfigurasi tersebut dan tidak menghapus atau menyembunyikan hasil historis.

### 5. Detail peserta dan ekspor

- Hasil DISC ditampilkan bersama hasil TKJ dan skenario pada detail peserta.
- Ringkasan DISC pada detail peserta menggunakan diagram lingkaran/radar, bukan bar chart, dengan interpretasi di sampingnya.
- Tabel daftar peserta menunjukkan status penyelesaian babak DISC.
- Ekspor hasil menyediakan status serta kolom ringkasan DISC yang konsisten dengan tampilan admin.
- Nilai yang belum tersedia dibedakan dari nilai nol.

## Prinsip interpretasi dan bahasa

Gunakan frasa seperti:

- “Kecenderungan ini dapat menjadi titik awal untuk mengeksplorasi…”
- “Posisi berikut layak dipertimbangkan dan divalidasi…”
- “Konfirmasi melalui percakapan atau tugas praktik…”

Hindari frasa seperti:

- “Peserta pasti cocok/tidak cocok…”
- “DISC membuktikan peserta memiliki kemampuan…”
- “Peluang cocok 80%” tanpa dasar validasi empiris.

Ringkasan DISC harus dibaca bersama minat peserta, hasil TKJ, hasil skenario, dan bukti dari praktik kerja. Keputusan posisi tetap dibuat admin setelah mempertimbangkan konteks peserta dan kebutuhan pekerjaan.

## Kebutuhan data dan administrasi

Data asesmen minimal mencakup:

- jawaban DISC peserta;
- status aktif/nonaktif DISC pada konfigurasi ujian;
- versi instrumen dan aturan penskoran;
- skor per dimensi serta status kelengkapan;
- waktu mulai dan selesai, serta penanda submit otomatis bila berlaku;
- catatan penempatan atau tindak lanjut yang dimasukkan admin, bila sistem menyediakan pencatatannya.

Perubahan pada instrumen atau aturan penskoran/interpretasi harus memiliki versi agar hasil lama tetap dapat ditafsirkan berdasarkan definisi yang digunakan saat peserta mengerjakan asesmen.

## Kriteria penerimaan

- [ ] Alur ujian peserta memiliki tiga babak berurutan: TKJ, skenario, lalu DISC.
- [ ] Babak DISC aktif secara default, wajib diselesaikan ketika aktif, dan dapat diaktifkan/nonaktifkan admin melalui dashboard.
- [ ] Saat DISC dinonaktifkan, peserta dapat menyelesaikan alur tanpa babak DISC dan data historis tetap dipertahankan.
- [ ] Instrumen DISC baru berjumlah tepat 30 butir dan tidak bergantung pada instrumen historis yang belum ditinjau.
- [ ] Babak DISC memiliki batas waktu 60 menit.
- [ ] Pengiriman manual meminta seluruh butir terjawab; saat waktu habis, sistem otomatis mengirim jawaban yang tersimpan, membiarkan butir tak terjawab kosong, dan mencatat status submit otomatis.
- [ ] Hasil DISC dan interpretasinya hanya dapat dilihat admin.
- [ ] Status peserta menunjukkan tahap DISC ketika peserta sedang mengerjakannya.
- [ ] Jawaban dan progres DISC tersimpan dan dapat dipulihkan sesuai mekanisme yang berlaku.
- [ ] Sistem menangani submit, pengiriman ulang, dan kondisi waktu habis tanpa menggandakan atau menghilangkan hasil.
- [ ] Hasil akhir baru menandai seluruh rangkaian ujian selesai setelah kebijakan penyelesaian DISC terpenuhi.
- [ ] Admin dapat membedakan peserta yang belum mulai, sedang mengerjakan, selesai, atau memiliki hasil yang tidak cukup untuk interpretasi DISC.
- [ ] Admin dapat membaca hasil DISC bersama hasil TKJ dan skenario.
- [ ] Detail satu peserta menyajikan ringkasan TKJ, skenario, dan DISC secara terpadu.
- [ ] Ringkasan DISC menggunakan diagram lingkaran/radar (bukan bar chart) dengan penjelasan ringkas di samping diagram.
- [ ] Data DISC kosong/tidak lengkap atau format historis tidak menyebabkan error pada halaman detail, tabel, maupun ekspor.
- [ ] Sistem tidak memilih, memeringkat, atau merekomendasikan posisi otomatis; admin menentukan penempatan dengan menggunakan ringkasan sebagai salah satu bahan pertimbangan.
- [ ] Tidak ada label lulus/gagal, diagnosis, keputusan otomatis, atau persentase kecocokan DISC.

## Ukuran keberhasilan

- Admin dapat membaca kecenderungan DISC sebagai salah satu bahan pertimbangan saat menentukan posisi awal peserta.
- Admin menggunakan hasil sebagai masukan untuk percakapan atau praktik, bukan keputusan tunggal.
- Keputusan penempatan tetap berada pada admin, bukan pada hasil otomatis sistem.
- Tidak terjadi error ketika admin membuka hasil peserta yang DISC-nya kosong, tidak lengkap, atau berasal dari format lama.

## Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Admin menganggap ringkasan sebagai keputusan objektif/final | Tampilkan penjelasan dan batasan interpretasi secara konsisten; admin tetap menentukan penempatan. |
| Ringkasan DISC dianggap sebagai rekomendasi posisi yang pasti | Jangan memetakan hasil ke posisi secara otomatis; tampilkan batasan interpretasi dan biarkan admin menentukan penempatan. |
| Instrumen memberi kesan presisi yang belum tervalidasi | Hindari persentase kecocokan dan klaim prediktif; simpan versi instrumen dan aturan skor. |
| Peserta tidak menyelesaikan babak ketiga | Simpan progres, tampilkan status tahap dengan jelas, dan terapkan kebijakan waktu/submit yang sama-sama dipahami. |
| Hasil lama tidak mengikuti struktur hasil terbaru | Pertahankan kompatibilitas pembacaan data historis dan tampilkan status data secara eksplisit. |
| Butir tidak cukup relevan atau realistis terhadap pekerjaan | Tinjau instrumen baru terhadap kejadian dan perilaku kerja yang benar-benar umum terjadi sebelum dipakai. |

## Di luar cakupan versi pertama

- Model statistik atau machine learning untuk memprediksi kinerja/retensi.
- Validasi DISC sebagai alat psikometrik atau klaim validitas klinis.
- Keputusan penempatan otomatis tanpa peninjauan admin.
- Pemeringkatan peserta untuk seleksi atau perbandingan nilai personal antar peserta.

## Pertanyaan terbuka sebelum implementasi

Belum ada pertanyaan terbuka yang tersisa dari keputusan produk yang sudah dibahas. Rancangan instrumen 30 butir tetap perlu ditinjau sebelum digunakan untuk memastikan butirnya jelas, realistis, dan berhubungan dengan perilaku kerja yang ingin diamati.

## Keputusan produk yang sudah ditetapkan

- DISC menjadi babak ketiga dan wajib ketika fitur aktif; admin dapat menyalakan atau mematikannya dari dashboard.
- Gunakan instrumen baru sebanyak 30 pertanyaan berbasis kejadian/perilaku kerja nyata dan aktual, bukan narasi rekaan.
- Durasi DISC adalah 60 menit. Saat waktunya habis, sistem otomatis mengirim jawaban tersimpan dan membiarkan butir yang belum dijawab tetap kosong.
- Hasil DISC hanya terlihat admin.
- Sistem memberikan ringkasan DISC sebagai bahan pertimbangan; admin sendiri yang menentukan posisi, tanpa rekomendasi posisi otomatis.
- Detail peserta menampilkan ringkasan seluruh asesmen dalam satu tempat; bagian DISC memakai diagram lingkaran/radar dan interpretasi di sampingnya.
- Retensi dan akses data mengikuti hasil asesmen lain, dengan pembatasan bahwa ringkasan DISC tidak ditampilkan kepada peserta.
