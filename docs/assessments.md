# Asesmen dan interpretasi

## Tahapan

Rangkaian standar:

1. **TKJ** — soal pilihan ganda kemampuan teknis. Urutan soal dan pilihan diacak per sesi. Backend menilai jawaban terhadap kunci.
2. **Skenario situasi kerja PKL** — respons terhadap situasi kerja yang dinilai melalui rubrik per indikator. Versi saat ini dinyatakan sebagai pilot dan bukan prediktor kinerja tervalidasi.
3. **Situasi kerja DISC** — 30 situasi aktual/realistis dengan satu pilihan respons per butir. Durasi 60 menit. Tahap wajib ketika toggle admin aktif.

Admin dapat menonaktifkan babak DISC baru. Hasil historis DISC tetap ada dan terpisah dari format baru.

## Penyimpanan dan submit

- Jawaban autosaved ke backend untuk dapat dipulihkan ketika peserta memuat ulang halaman.
- UI memberi status penyimpanan dan antrean offline untuk jawaban situasi kerja.
- Submit manual mensyaratkan semua butir terjawab.
- Saat waktu DISC habis, jawaban yang sudah tersimpan otomatis diproses. Pertanyaan kosong tidak dihitung sebagai respons pada dimensi mana pun.
- Hasil menyimpan versi instrumen, jumlah jawaban, skor proporsional per dimensi, dan status submit otomatis.

## Ringkasan DISC

Setiap situasi memiliki empat opsi dengan dimensi perilaku berbeda. Opsi diacak untuk tiap snapshot peserta. Skor menunjukkan proporsi dari pilihan yang dijawab untuk D, I, S, dan C; skor bukan probabilitas, ranking kecocokan posisi, diagnosis, maupun ukuran kemampuan teknis.

Admin melihat diagram radar dan penjelasan kecenderungan. Untuk hasil parsial, ringkasan harus menyatakan jumlah respons dan dibaca dengan kehati-hatian. Jika tidak ada jawaban, jangan menyimpulkan profil.

## Ringkasan keseluruhan peserta

Detail admin merangkum:

- capaian teknis TKJ, termasuk skor dan persentase bila data tersedia;
- jumlah skenario terjawab dan indikator rubrik relatif tinggi/perlu didalami;
- dimensi DISC yang paling banyak dipilih pada situasi terjawab;
- kelengkapan asesmen dan batas interpretasi data.

Ringkasan menggabungkan bukti, bukan menghasilkan nilai total gabungan atau keputusan posisi otomatis. Admin tetap menentukan penempatan setelah mempertimbangkan minat peserta, kebutuhan pekerjaan, wawancara, dan praktik.

## Kualitas dan tata kelola instrumen

- Tinjau seluruh butir bersama pemilik proses dan orang yang memahami pekerjaan sehari-hari sebelum dipakai pada peserta nyata.
- Pastikan tiap opsi masuk akal, tidak ada pilihan yang tampak “paling benar”, dan bahasa sesuai usia/latar peserta.
- Simpan versi konten serta snapshot saat ujian dimulai.
- Perubahan rubrik/skor memerlukan review agar tidak memberi kesan akurasi yang belum dibuktikan.
- Jangan membandingkan peserta sebagai peringkat tunggal atau memakai DISC sebagai satu-satunya dasar seleksi/penempatan.
