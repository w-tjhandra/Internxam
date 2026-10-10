"""Versioned, work-situation DISC-style assessment content and scoring."""

WORK_DISC_VERSION = "work-disc-situations-v1"

DIMENSIONS = ("D", "I", "S", "C")

DIMENSION_LABELS = {
    "D": "Dominance",
    "I": "Influence",
    "S": "Steadiness",
    "C": "Compliance",
}

DIMENSION_SUMMARIES = {
    "D": "Cenderung mengambil inisiatif, menetapkan prioritas, dan mendorong penyelesaian tugas.",
    "I": "Cenderung membangun komunikasi, melibatkan orang lain, dan menjaga pertukaran informasi.",
    "S": "Cenderung menjaga konsistensi, membantu rekan, dan mengikuti pekerjaan sampai tuntas.",
    "C": "Cenderung memeriksa informasi, memperhatikan detail, dan mengikuti prosedur kerja.",
}

_RAW_ITEMS = [
    (
        "Pengguna melaporkan koneksi internet terputus saat beberapa pekerjaan sedang berjalan. Apa yang paling mungkin kamu lakukan lebih dulu?",
        "Memastikan dampak dan mengambil langkah awal yang diizinkan agar layanan segera tertangani.",
        "Menghubungi pengguna terkait untuk mengumpulkan gejala dan menjaga mereka mendapat kabar.",
        "Membantu pengguna tetap bekerja dengan alternatif sementara sambil mengikuti penanganan.",
        "Mencatat gejala dan memeriksa koneksi serta indikator perangkat secara berurutan.",
    ),
    (
        "Kamu menerima beberapa permintaan bantuan sekaligus, semuanya dianggap penting. Bagaimana kamu memulai?",
        "Menetapkan urutan berdasarkan dampak dan mulai menangani yang paling mendesak.",
        "Menghubungi peminta untuk menyamakan ekspektasi dan mengoordinasikan bantuan.",
        "Menanggapi satu per satu dengan tenang sambil memastikan tidak ada yang terlewat.",
        "Mencatat setiap permintaan, tenggat, dan informasi yang diperlukan sebelum mengurutkan.",
    ),
    (
        "Sebelum memasang aplikasi yang diminta rekan kerja, apa yang paling mungkin kamu lakukan?",
        "Memastikan kebutuhan dan izin, lalu segera menjalankan langkah pemasangan yang disetujui.",
        "Berdiskusi dengan rekan tentang kebutuhan aplikasi dan menjelaskan prosesnya.",
        "Membantu rekan mengikuti proses yang berlaku dan memastikan ia siap menggunakan aplikasi.",
        "Memeriksa sumber aplikasi, kompatibilitas, izin, dan panduan pemasangan.",
    ),
    (
        "Sebuah tugas kelompok tertunda karena belum jelas siapa yang mengerjakan bagian berikutnya. Apa respons awalmu?",
        "Mengusulkan pembagian tugas dan mengambil tanggung jawab untuk bagian yang belum tertangani.",
        "Mengajak anggota kelompok menyepakati pembagian kerja bersama.",
        "Menawarkan bantuan pada anggota yang kewalahan dan menjaga pekerjaan tetap berjalan.",
        "Memeriksa daftar pekerjaan dan ketergantungan tugas agar pembagian tidak menimbulkan celah.",
    ),
    (
        "Kamu menemukan data inventaris perangkat berbeda dengan kondisi fisik. Apa langkah yang paling menggambarkan caramu?",
        "Memastikan perangkat yang terdampak dan segera mengoordinasikan koreksi data.",
        "Menghubungi orang yang terakhir memperbarui data untuk mengklarifikasi perbedaannya.",
        "Membantu menghitung ulang inventaris bersama petugas terkait sampai selesai.",
        "Mencocokkan nomor aset, lokasi, dan catatan sebelum mengubah data inventaris.",
    ),
    (
        "Saat membantu menyiapkan komputer baru, pembimbing memberi beberapa pekerjaan sekaligus. Apa yang biasanya kamu lakukan?",
        "Mengidentifikasi langkah yang membuka jalan untuk pekerjaan lain dan mulai dari sana.",
        "Mengonfirmasi kebutuhan pengguna dan berkomunikasi dengan pihak yang terlibat.",
        "Mengerjakan daftar persiapan secara konsisten hingga komputer siap digunakan.",
        "Mengikuti checklist konfigurasi dan memeriksa setiap pengaturan penting.",
    ),
    (
        "Rekan meminta kata sandi akun bersama melalui pesan pribadi agar pekerjaan cepat selesai. Bagaimana kamu menanggapinya?",
        "Menolak berbagi kata sandi dan mengarahkan ke cara akses yang diizinkan.",
        "Menjelaskan dengan ramah risikonya dan membantu menghubungi pengelola akses.",
        "Mendampingi rekan mencari alternatif resmi tanpa membuatnya terhenti sendirian.",
        "Memeriksa prosedur akses dan memastikan permintaan ditangani sesuai kebijakan.",
    ),
    (
        "Printer kantor berhenti mencetak menjelang rapat. Apa hal pertama yang cenderung kamu lakukan?",
        "Memeriksa gangguan utama dan menentukan tindakan aman tercepat untuk memulihkan layanan.",
        "Menanyakan kebutuhan cetak dan memberi kabar tentang penanganan atau alternatif.",
        "Membantu pengguna memindahkan pekerjaan ke printer lain sambil menunggu perbaikan.",
        "Memeriksa antrean cetak, koneksi, kertas, dan pesan error secara sistematis.",
    ),
    (
        "Kamu diminta mengubah konfigurasi jaringan, tetapi ruang lingkup perubahan belum jelas. Apa yang paling mungkin kamu lakukan?",
        "Meminta batas perubahan dan kewenangan, lalu menetapkan langkah berikutnya.",
        "Menyelaraskan pemahaman dengan peminta dan pembimbing sebelum mulai.",
        "Menunggu arahan yang cukup sambil membantu pekerjaan lain yang aman dilakukan.",
        "Mencari dokumentasi, dampak, dan prosedur perubahan sebelum menyentuh konfigurasi.",
    ),
    (
        "Pengguna menyampaikan keluhan dengan nada kesal karena masalahnya berulang. Bagaimana kamu biasanya merespons?",
        "Mengambil alih penanganan dan menyepakati tindakan serta waktu pembaruan berikutnya.",
        "Mendengarkan keluhan, menunjukkan empati, dan menjaga komunikasi tetap terbuka.",
        "Tetap tenang, memberi ruang bagi pengguna menjelaskan, lalu mendampingi sampai ada solusi.",
        "Mencatat detail kejadian berulang untuk memastikan pemeriksaan berdasarkan fakta.",
    ),
    (
        "Kamu hampir menyelesaikan konfigurasi perangkat, lalu menemukan satu nilai berbeda dari dokumentasi. Apa yang dilakukan?",
        "Menentukan apakah perbedaan menghalangi tugas dan segera mengklarifikasi keputusan yang dibutuhkan.",
        "Menghubungi pembimbing atau rekan yang memahami perubahan untuk mendapatkan konteks.",
        "Menunda langkah terkait dan melanjutkan bagian aman agar pekerjaan tetap tertata.",
        "Membandingkan versi dokumentasi dan konfigurasi aktual sebelum melanjutkan.",
    ),
    (
        "Dalam briefing pagi, tim membahas pekerjaan yang harus selesai hari itu. Peran apa yang paling alami kamu ambil?",
        "Memastikan prioritas, penanggung jawab, dan hasil yang harus dicapai jelas.",
        "Menyampaikan informasi dan memastikan anggota tim saling memahami kebutuhan.",
        "Membantu menjaga koordinasi dan mengingatkan tindak lanjut yang sudah disepakati.",
        "Mencatat rincian tugas, dependensi, dan kriteria selesai.",
    ),
    (
        "Kamu diminta memperbarui daftar akun pengguna. Bagaimana kamu mengurangi risiko kesalahan?",
        "Menyelesaikan pembaruan yang sudah jelas dan mengangkat entri yang menghambat.",
        "Mengonfirmasi perubahan dengan pemilik akun atau peminta agar informasinya tepat.",
        "Memproses daftar secara teratur dan meminta pemeriksaan rekan bila diperlukan.",
        "Mencocokkan identitas dan hak akses sebelum menyimpan tiap perubahan.",
    ),
    (
        "Seorang rekan baru belum memahami cara mengirim permintaan dukungan TI. Apa yang paling mungkin kamu lakukan?",
        "Menunjukkan jalur yang benar dan mendorongnya mengirim permintaan dengan informasi lengkap.",
        "Menyambutnya, menjelaskan alurnya dengan mudah, dan mengenalkannya ke kontak yang tepat.",
        "Mendampinginya mencoba langkah-langkah sampai ia merasa nyaman melakukannya sendiri.",
        "Memberikan panduan ringkas yang menjelaskan informasi wajib dan urutan pengajuan.",
    ),
    (
        "Kamu menemukan kabel di ruang kerja tidak diberi label dan berpotensi membingungkan saat perawatan. Bagaimana kamu menanganinya?",
        "Mengatur agar kabel penting diidentifikasi dan risiko salah cabut segera dikurangi.",
        "Bertanya kepada pengguna perangkat dan mengoordinasikan pelabelan yang mudah dipahami.",
        "Membantu menata dan memberi label kabel satu demi satu tanpa mengganggu pengguna.",
        "Menelusuri kedua ujung kabel dan mencatat koneksinya sebelum memberi label.",
    ),
    (
        "Tenggat laporan inventaris semakin dekat, tetapi ada beberapa data yang belum dikonfirmasi. Apa yang paling mungkin kamu lakukan?",
        "Menetapkan data yang paling kritis dan meminta konfirmasi segera agar laporan bisa dituntaskan.",
        "Menghubungi pemilik data dengan jelas tentang informasi yang dibutuhkan dan tenggatnya.",
        "Menyelesaikan data yang sudah pasti sambil rutin menindaklanjuti sisanya.",
        "Menandai nilai yang belum terverifikasi dan memisahkannya dari data yang sudah valid.",
    ),
    (
        "Sistem meminta pembaruan perangkat lunak, tetapi perangkat itu sedang dipakai untuk pekerjaan penting. Bagaimana kamu memulai?",
        "Menentukan waktu dan langkah yang memungkinkan pembaruan selesai dengan gangguan minimum.",
        "Mengabari pengguna dan menyepakati waktu pembaruan yang tidak mengejutkan.",
        "Membantu pengguna menyimpan pekerjaannya dan kembali setelah proses selesai.",
        "Memeriksa catatan pembaruan, kebutuhan restart, dan prosedur pencadangan.",
    ),
    (
        "Kamu melihat rekan melewatkan langkah pemeriksaan pada pekerjaan yang memengaruhi data pengguna. Apa yang kamu lakukan?",
        "Menghentikan langkah berisiko dengan sopan dan meminta pemeriksaan dilakukan sebelum lanjut.",
        "Mengingatkan rekan secara terbuka dan menjaga diskusi tetap nyaman.",
        "Menawarkan bantuan untuk memeriksa bersama tanpa mempermalukan rekan.",
        "Menunjukkan langkah prosedur yang terlewat dan alasan pemeriksaannya diperlukan.",
    ),
    (
        "Saat rapat, ada perbedaan pendapat tentang cara menangani gangguan layanan. Apa pendekatanmu?",
        "Mengarahkan diskusi pada dampak dan keputusan yang perlu dibuat sekarang.",
        "Mengajak pihak terkait menyampaikan pandangan dan mencari kesepakatan.",
        "Mendengarkan semua pihak dan membantu tim tetap bekerja sama selama diskusi.",
        "Membandingkan usulan dengan bukti, risiko, dan prosedur yang berlaku.",
    ),
    (
        "Kamu menerima permintaan bantuan yang informasinya hanya berbunyi 'komputer bermasalah'. Apa yang paling mungkin kamu lakukan?",
        "Menghubungi peminta untuk mendapat detail minimum, lalu menentukan tindakan pertama.",
        "Memulai percakapan yang ramah agar peminta nyaman menjelaskan masalahnya.",
        "Memandu peminta menjelaskan gejala satu per satu dengan sabar.",
        "Mengumpulkan pesan error, waktu kejadian, dan perubahan terakhir secara rinci.",
    ),
    (
        "Sebuah pekerjaan rutin perlu dilakukan setiap minggu dan sering terlupa oleh tim. Apa yang cenderung kamu usulkan?",
        "Menetapkan penanggung jawab dan tenggat agar tugas tersebut benar-benar selesai.",
        "Mengingatkan tim melalui kanal komunikasi yang mudah diperhatikan.",
        "Membuat jadwal rutin dan membantu menjaga kebiasaan tim menjalankannya.",
        "Membuat checklist dengan bukti pelaksanaan dan langkah verifikasi.",
    ),
    (
        "Kamu selesai memperbaiki koneksi satu komputer. Apa yang paling mungkin kamu lakukan sebelum menutup permintaan?",
        "Memastikan pengguna bisa bekerja kembali dan menyatakan tugas selesai.",
        "Mengonfirmasi kepada pengguna bahwa koneksi sudah pulih dan menanyakan hal lain yang terkait.",
        "Memastikan pengguna nyaman menggunakan koneksi kembali dan bersedia membantu bila ada kendala.",
        "Menguji koneksi dan mencatat penyebab serta tindakan perbaikan pada tiket.",
    ),
    (
        "Pembimbing memberi masukan bahwa catatan pekerjaanmu kurang mudah dipahami. Apa respons yang paling menggambarkanmu?",
        "Meminta contoh perubahan yang dibutuhkan dan segera memperbaiki catatan tersebut.",
        "Mendiskusikan format catatan yang akan membantu tim saling berbagi informasi.",
        "Menerima masukan dengan tenang dan menerapkannya secara konsisten pada tugas berikutnya.",
        "Meninjau catatan lama untuk menemukan bagian yang tidak lengkap atau ambigu.",
    ),
    (
        "Kamu perlu memindahkan perangkat kerja ke ruangan lain yang digunakan beberapa tim. Apa yang kamu lakukan lebih dulu?",
        "Menentukan urutan pemindahan agar perangkat penting segera kembali tersedia.",
        "Mengabari tim terdampak dan menyepakati waktu pemindahan bersama.",
        "Membantu mengemas, memindahkan, dan menata perangkat agar tidak tertinggal.",
        "Mencatat nomor aset, kondisi, dan sambungan sebelum perangkat dipindahkan.",
    ),
    (
        "Ada file yang tidak sengaja dibagikan kepada penerima yang keliru. Apa langkah pertamamu?",
        "Menghentikan akses yang keliru secepatnya melalui prosedur yang diizinkan.",
        "Menghubungi pemilik file dan pihak terkait agar mereka mengetahui tindakan yang sedang dilakukan.",
        "Membantu pihak terdampak mengikuti langkah aman dan memastikan kebutuhan kerja tetap tertangani.",
        "Memeriksa jenis file, cakupan akses, dan waktu kejadian untuk pelaporan yang akurat.",
    ),
    (
        "Kamu diminta membantu tugas baru yang belum pernah kamu kerjakan. Bagaimana kamu biasanya memulai?",
        "Memahami hasil yang diharapkan dan mencoba langkah awal yang aman.",
        "Bertanya kepada orang yang berpengalaman dan membangun komunikasi selama belajar.",
        "Mengikuti arahan tahap demi tahap dan meminta umpan balik secara berkala.",
        "Membaca panduan dan mencatat persyaratan sebelum mulai mengerjakan.",
    ),
    (
        "Saat menyiapkan ruang rapat, satu perangkat tidak berfungsi sementara peserta segera datang. Apa yang kamu lakukan?",
        "Memilih solusi praktis yang aman agar rapat dapat segera dimulai.",
        "Mengabari penyelenggara dan menawarkan alternatif perangkat atau cara presentasi.",
        "Membantu menyiapkan alternatif dengan tenang sampai penyelenggara siap.",
        "Memeriksa sumber masalah dan memastikan alternatif berfungsi sebelum digunakan.",
    ),
    (
        "Kamu melihat dua catatan tiket untuk masalah yang tampaknya sama. Apa yang paling mungkin kamu lakukan?",
        "Menggabungkan penanganan agar upaya tidak terpecah dan ada penanggung jawab yang jelas.",
        "Mengonfirmasi dengan pelapor apakah masalahnya sama dan menyampaikan pembaruan.",
        "Menjaga kedua pelapor mendapat tindak lanjut sampai masalah mereka dipastikan selesai.",
        "Membandingkan waktu, gejala, dan perangkat sebelum menghubungkan tiket.",
    ),
    (
        "Sebelum menyerahkan perangkat pinjaman kepada pengguna, hal apa yang paling kamu prioritaskan?",
        "Memastikan perangkat siap dipakai dan proses serah terima tidak tertunda.",
        "Menjelaskan cara penggunaan dan memastikan pengguna tahu ke mana meminta bantuan.",
        "Mendampingi pengguna mencoba perangkat agar transisi berjalan nyaman.",
        "Memeriksa kondisi, kelengkapan, akun, dan catatan peminjaman dengan teliti.",
    ),
    (
        "Di akhir hari, ada pekerjaan yang belum selesai dan perlu diteruskan oleh rekan esok pagi. Bagaimana kamu menutup pekerjaan?",
        "Menentukan langkah berikut dan memastikan ada pemilik tugas untuk melanjutkannya.",
        "Menyampaikan status kepada rekan terkait agar mereka siap melanjutkan.",
        "Membuat serah terima yang tenang dan memastikan rekan tidak kehilangan konteks.",
        "Mencatat langkah yang sudah dilakukan, hasil, dan pemeriksaan yang masih tertunda.",
    ),
]


def build_work_disc_items() -> list[dict]:
    items = []
    for index, (situation, *texts) in enumerate(_RAW_ITEMS):
        items.append(
            {
                "id": f"work-disc-{index + 1:02d}",
                "situation": situation,
                "options": [
                    {"text": text, "dimension": dimension}
                    for dimension, text in zip(DIMENSIONS, texts, strict=True)
                ],
            }
        )
    return items


def score_work_disc(items: list[dict], answers: dict, auto_submitted: bool = False) -> dict:
    counts = {dimension: 0 for dimension in DIMENSIONS}
    valid_item_ids = {item["id"] for item in items}

    for item_id, selected_index in answers.items():
        if item_id not in valid_item_ids or not isinstance(selected_index, int):
            continue
        item = next(item for item in items if item["id"] == item_id)
        if 0 <= selected_index < len(item["options"]):
            dimension = item["options"][selected_index]["dimension"]
            if dimension in counts:
                counts[dimension] += 1

    answered = sum(counts.values())
    percentages = {
        dimension: round(count * 100 / answered, 1) if answered else 0
        for dimension, count in counts.items()
    }
    ranked = sorted(DIMENSIONS, key=lambda dimension: (-counts[dimension], DIMENSIONS.index(dimension)))

    return {
        "version": WORK_DISC_VERSION,
        "status": "complete" if answered == len(items) else "partial",
        "answered_items": answered,
        "total_items": len(items),
        "auto_submitted": auto_submitted,
        "counts": counts,
        "scores": percentages,
        "ranked_dimensions": ranked,
        "summary": [
            {
                "dimension": dimension,
                "label": DIMENSION_LABELS[dimension],
                "score": percentages[dimension],
                "description": DIMENSION_SUMMARIES[dimension],
            }
            for dimension in ranked
        ],
        "disclaimer": (
            "Ringkasan indikatif berdasarkan pilihan pada situasi kerja. "
            "Gunakan sebagai salah satu bahan pertimbangan, bukan label atau "
            "keputusan penempatan otomatis."
        ),
    }
