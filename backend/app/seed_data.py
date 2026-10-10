"""Seed question banks and versioned scenario assessment content."""

TKJ_QUESTIONS = [
    {"text": "Sebuah jaringan menggunakan IP 192.168.10.0/26. Berapa jumlah host maksimum yang dapat digunakan dalam satu subnet?", "options": ["62 host", "64 host", "30 host", "126 host"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "sedang"},
    {"text": "Perangkat yang bekerja pada Layer 2 OSI dan meneruskan frame berdasarkan MAC address adalah...", "options": ["Switch", "Router", "Hub", "Repeater"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "mudah"},
    {"text": "Subnet mask 255.255.255.240 setara dengan notasi CIDR...", "options": ["/28", "/26", "/27", "/29"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "sedang"},
    {"text": "Protokol yang digunakan untuk memberikan alamat IP secara otomatis kepada client dalam jaringan adalah...", "options": ["DHCP", "DNS", "FTP", "SNMP"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "mudah"},
    {"text": "Urutan warna kabel UTP standar T568B dari pin 1 adalah...", "options": ["Putih-oranye, oranye, putih-hijau, biru, putih-biru, hijau, putih-coklat, coklat", "Putih-hijau, hijau, putih-oranye, biru, putih-biru, oranye, putih-coklat, coklat", "Oranye, putih-oranye, hijau, putih-biru, biru, putih-hijau, coklat, putih-coklat", "Putih-biru, biru, putih-oranye, hijau, putih-hijau, oranye, putih-coklat, coklat"], "correct_index": 0, "category": "Perkabelan", "difficulty": "sedang"},
    {"text": "Kabel crossover digunakan untuk menghubungkan...", "options": ["Dua perangkat sejenis, misalnya PC ke PC", "PC ke switch", "Switch ke router", "Modem ke router"], "correct_index": 0, "category": "Perkabelan", "difficulty": "mudah"},
    {"text": "Sebuah host memiliki IP 172.16.35.10/20. Alamat network dari host tersebut adalah...", "options": ["172.16.32.0", "172.16.35.0", "172.16.16.0", "172.16.0.0"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "sulit"},
    {"text": "Protokol pada layer transport yang bersifat connection-oriented dan menjamin data sampai secara berurutan adalah...", "options": ["TCP", "UDP", "ICMP", "ARP"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "mudah"},
    {"text": "Fungsi utama NAT (Network Address Translation) pada router adalah...", "options": ["Menerjemahkan IP privat menjadi IP publik agar dapat mengakses internet", "Memberikan IP otomatis ke client", "Memfilter konten website berbahaya", "Mempercepat transfer data lokal"], "correct_index": 0, "category": "Routing", "difficulty": "sedang"},
    {"text": "Pada MikroTik, perintah untuk menambahkan gateway default melalui terminal adalah...", "options": ["ip route add gateway=192.168.1.1", "ip gateway set 192.168.1.1", "route default 192.168.1.1", "set gateway ip=192.168.1.1"], "correct_index": 0, "category": "Routing", "difficulty": "sedang"},
    {"text": "VLAN pada switch berfungsi untuk...", "options": ["Memisahkan broadcast domain secara logis tanpa perangkat tambahan", "Menggabungkan beberapa switch menjadi satu", "Mempercepat koneksi antar port", "Mengubah MAC address perangkat"], "correct_index": 0, "category": "Jaringan Lanjut", "difficulty": "sedang"},
    {"text": "Port default yang digunakan oleh layanan SSH adalah...", "options": ["22", "23", "21", "80"], "correct_index": 0, "category": "Server", "difficulty": "mudah"},
    {"text": "Perintah Linux untuk melihat konfigurasi antarmuka jaringan (versi modern pengganti ifconfig) adalah...", "options": ["ip addr show", "netcfg -a", "showif", "ipconfig /all"], "correct_index": 0, "category": "Sistem Operasi", "difficulty": "sedang"},
    {"text": "Direktori pada Linux yang berisi file konfigurasi sistem adalah...", "options": ["/etc", "/bin", "/home", "/var"], "correct_index": 0, "category": "Sistem Operasi", "difficulty": "mudah"},
    {"text": "RAID level yang melakukan mirroring penuh sehingga data tetap aman jika satu disk rusak adalah...", "options": ["RAID 1", "RAID 0", "RAID 5", "JBOD"], "correct_index": 0, "category": "Perangkat Keras", "difficulty": "sedang"},
    {"text": "Saat komputer dinyalakan terdengar bunyi beep panjang berulang. Pada umumnya ini menandakan masalah pada...", "options": ["RAM", "Hard disk", "Power supply", "Keyboard"], "correct_index": 0, "category": "Perangkat Keras", "difficulty": "sedang"},
    {"text": "Sebuah PC dapat mengakses IP lokal tetapi tidak bisa membuka website, sedangkan ping ke 8.8.8.8 berhasil. Kemungkinan besar masalahnya ada pada...", "options": ["Konfigurasi DNS", "Kabel jaringan", "Gateway", "IP conflict"], "correct_index": 0, "category": "Troubleshooting", "difficulty": "sulit"},
    {"text": "Hasil ping menampilkan pesan 'Request Timed Out'. Artinya adalah...", "options": ["Host tujuan tidak memberikan balasan dalam batas waktu", "Alamat IP tidak valid", "DNS tidak dapat menerjemahkan domain", "Kabel LAN terpasang terbalik"], "correct_index": 0, "category": "Troubleshooting", "difficulty": "mudah"},
    {"text": "Mode keamanan wireless yang paling kuat di antara pilihan berikut adalah...", "options": ["WPA2-AES", "WEP 128-bit", "WPA-TKIP", "Open dengan MAC filter"], "correct_index": 0, "category": "Keamanan", "difficulty": "sedang"},
    {"text": "Firewall yang memfilter lalu lintas berdasarkan alamat IP, port, dan protokol bekerja dengan metode...", "options": ["Packet filtering", "Proxy filtering", "Content filtering", "MAC cloning"], "correct_index": 0, "category": "Keamanan", "difficulty": "sedang"},
    {"text": "Serangan yang membanjiri server dengan lalu lintas dari banyak sumber hingga layanan lumpuh disebut...", "options": ["DDoS", "Phishing", "SQL Injection", "Brute force"], "correct_index": 0, "category": "Keamanan", "difficulty": "mudah"},
    {"text": "Alamat IPv6 memiliki panjang...", "options": ["128 bit", "32 bit", "64 bit", "256 bit"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "mudah"},
    {"text": "Topologi jaringan di mana semua node terhubung ke satu titik pusat disebut topologi...", "options": ["Star", "Bus", "Ring", "Mesh"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "mudah"},
    {"text": "Sebuah kantor membutuhkan 5 subnet dari network 192.168.1.0/24 dengan jumlah subnet semaksimal mungkin masing-masing minimal 25 host. Subnet mask yang tepat adalah...", "options": ["255.255.255.224 (/27)", "255.255.255.192 (/26)", "255.255.255.240 (/28)", "255.255.255.128 (/25)"], "correct_index": 0, "category": "Jaringan Dasar", "difficulty": "sulit"},
    {"text": "Kabel fiber optic jenis single-mode memiliki karakteristik...", "options": ["Inti kecil (±9 µm), jarak jauh, sumber cahaya laser", "Inti besar (±62,5 µm), jarak dekat, sumber cahaya LED", "Menggunakan tembaga sebagai inti", "Hanya untuk jaringan lokal antar lantai"], "correct_index": 0, "category": "Perkabelan", "difficulty": "sedang"},
    {"text": "Layanan server yang menerjemahkan nama domain menjadi alamat IP adalah...", "options": ["DNS Server", "Web Server", "DHCP Server", "Mail Server"], "correct_index": 0, "category": "Server", "difficulty": "mudah"},
    {"text": "Pada instalasi Debian/Ubuntu server, perintah untuk memasang paket web server Apache adalah...", "options": ["apt install apache2", "yum add apache", "install apache2 now", "dpkg get apache2"], "correct_index": 0, "category": "Server", "difficulty": "mudah"},
    {"text": "Proxy server yang menyimpan salinan halaman web agar akses berikutnya lebih cepat menjalankan fungsi...", "options": ["Caching", "Routing", "Bridging", "Tunneling"], "correct_index": 0, "category": "Server", "difficulty": "sedang"},
]

DISC_GROUPS = [
    ["Tegas dalam mengambil keputusan", "Antusias dan bersemangat", "Sabar menghadapi orang lain", "Teliti mengikuti aturan"],
    ["Berani menghadapi tantangan", "Mudah bergaul dengan siapa saja", "Setia dan dapat diandalkan", "Berhati-hati sebelum bertindak"],
    ["Suka memimpin kelompok", "Pandai meyakinkan orang", "Pendengar yang baik", "Perfeksionis dalam bekerja"],
    ["Cepat mengambil tindakan", "Optimis memandang keadaan", "Tenang dalam tekanan", "Sistematis dan terorganisir"],
    ["Kompetitif ingin selalu menang", "Humoris dan menghibur", "Konsisten dalam rutinitas", "Analitis memecahkan masalah"],
    ["Percaya diri tinggi", "Ekspresif menunjukkan perasaan", "Ramah dan hangat", "Akurasi adalah prioritas"],
    ["Berkemauan keras", "Mudah mempengaruhi orang lain", "Menghindari konflik", "Patuh pada prosedur"],
    ["Suka mengambil risiko", "Spontan dan ceria", "Stabil dan tidak mudah berubah", "Berpikir logis dan objektif"],
    ["Langsung pada inti masalah", "Suka menjadi pusat perhatian", "Mendukung keputusan kelompok", "Menuntut standar tinggi"],
    ["Mandiri tidak bergantung orang lain", "Terbuka pada orang baru", "Lembut dalam berbicara", "Rapi dan terstruktur"],
    ["Menyukai perubahan cepat", "Pandai membangun suasana", "Setia pada kebiasaan lama", "Cermat memeriksa detail"],
    ["Berorientasi pada hasil", "Berorientasi pada orang", "Berorientasi pada kerja sama", "Berorientasi pada kualitas"],
    ["Berani menyampaikan pendapat berbeda", "Mudah memaafkan", "Menjaga perasaan orang lain", "Berpegang pada fakta"],
    ["Menikmati persaingan", "Menikmati keramaian", "Menikmati ketenangan", "Menikmati kesempurnaan"],
    ["Menuntut diri dan orang lain", "Memotivasi orang di sekitar", "Menerima keadaan apa adanya", "Mengikuti aturan dengan disiplin"],
    ["Tegar menghadapi kritik", "Antusias mencoba hal baru", "Sabar menunggu hasil", "Waspada terhadap kesalahan"],
    ["Suka memegang kendali", "Suka bercerita dan berbagi", "Suka membantu tanpa pamrih", "Suka merencanakan dengan matang"],
    ["Bertindak cepat dan tegas", "Berbicara dengan meyakinkan", "Bekerja dengan tempo stabil", "Bekerja dengan ketelitian tinggi"],
    ["Tidak takut konfrontasi", "Mudah akrab dengan orang asing", "Setia menjaga hubungan lama", "Kritis menilai suatu ide"],
    ["Ambisius mengejar target", "Ceria membawa energi positif", "Tenang menenangkan orang lain", "Disiplin menjaga kualitas"],
    ["Pemberani mengambil keputusan sulit", "Persuasif dalam bernegosiasi", "Konsisten menepati janji", "Objektif berdasarkan data"],
    ["Menyukai tantangan besar", "Menyukai apresiasi dan pujian", "Menyukai lingkungan harmonis", "Menyukai instruksi yang jelas"],
    ["Dominan dalam diskusi", "Aktif memulai percakapan", "Pendamai saat terjadi konflik", "Skeptis sampai ada bukti"],
    ["Fokus pada tujuan akhir", "Fleksibel dan mudah menyesuaikan", "Dapat dipercaya memegang rahasia", "Metodis mengikuti langkah demi langkah"],
    ["Mendorong batas kemampuan diri", "Menyemarakkan suasana pertemuan", "Menyukai keharmonisan dalam kelompok", "Memeriksa ulang setiap pekerjaan"],
    ["Berpikir dan bertindak secara independen", "Pandai mengambil hati orang", "Membangun hubungan jangka panjang", "Menginginkan segala sesuatu terukur"],
    ["Cepat bosan dengan rutinitas", "Mengekspresikan diri secara terbuka", "Mengerjakan tugas dengan tekun", "Menelaah instruksi dengan seksama"],
    ["Mengarahkan orang untuk bertindak", "Suka berkolaborasi dengan banyak pihak", "Peduli pada kesejahteraan rekan kerja", "Mengutamakan fakta dan logika"],
    ["Cenderung mendominasi pembicaraan", "Optimis menghadapi kegagalan", "Lebih suka menjadi pengamat", "Berpikir secara kronologis"],
    ["Bertindak sebagai inisiator utama", "Menyebarkan antusiasme ke orang lain", "Menyesuaikan diri dengan ritme tim", "Berhati-hati membuat asumsi"],
    ["Tegas mempertahankan prinsip", "Cepat akrab dalam lingkungan baru", "Bersedia mengalah demi kedamaian", "Taat pada aturan main yang berlaku"],
    ["Mengambil alih jika tidak ada pemimpin", "Sering menjadi pencair suasana", "Merespons konflik secara damai", "Fokus pada penyempurnaan proses"],
    ["Menginginkan kebebasan berekspresi", "Menikmati aktivitas sosial", "Melaksanakan tugas dengan konsisten", "Menyusun pedoman kerja yang jelas"],
    ["Berorientasi pada pencapaian tertinggi", "Membujuk orang dengan pesona", "Menjaga stabilitas lingkungan", "Menilai risiko sebelum memulai"],
    ["Bersikap blak-blakan dan langsung", "Tidak ragu meminta bantuan", "Toleran terhadap perbedaan pendapat", "Melakukan verifikasi data"],
    ["Cepat menangkap inti pembicaraan", "Mempunyai jaringan pertemanan luas", "Memberikan dukungan emosional", "Tunduk pada otoritas dan regulasi"],
]

def build_disc_items():
    dims = ["D", "I", "S", "C"]
    items = []
    for gi, group in enumerate(DISC_GROUPS):
        statements = [{"text": t, "dimension": dims[si]} for si, t in enumerate(group)]
        items.append({"group_index": gi, "statements": statements})
    return items

DISC_INTERPRETATIONS = {
    "D": "Dominance — tegas, berorientasi hasil, cepat mengambil keputusan, menyukai tantangan dan kendali.",
    "I": "Influence — komunikatif, antusias, persuasif, senang berinteraksi dan memotivasi orang lain.",
    "S": "Steadiness — sabar, konsisten, dapat diandalkan, menyukai stabilitas dan kerja sama tim.",
    "C": "Compliance — teliti, analitis, sistematis, mengutamakan akurasi dan standar yang tinggi.",
}

SCENARIO_ASSESSMENT_VERSION = "pkl-work-scenarios-v1"
SCENARIO_ASSESSMENT_DISCLAIMER = (
    "Asesmen skenario versi pilot. Hasil hanya bahan diskusi dan belum divalidasi "
    "sebagai prediktor kinerja atau dasar tunggal keputusan seleksi."
)
SCENARIO_INDICATORS = [
    {
        "id": "problem_solving",
        "label": "Pemecahan masalah dan eskalasi",
        "description": "Mengumpulkan informasi, mencoba langkah aman, dan meminta bantuan saat diperlukan.",
    },
    {
        "id": "careful_work",
        "label": "Ketelitian dan keselamatan kerja",
        "description": "Memeriksa dampak, menjaga data/layanan, dan mengikuti prosedur sebelum bertindak.",
    },
    {
        "id": "learning",
        "label": "Belajar dari arahan dan umpan balik",
        "description": "Meminta penjelasan, menerapkan masukan, lalu memeriksa hasil pekerjaannya.",
    },
    {
        "id": "team_communication",
        "label": "Komunikasi dan kerja sama",
        "description": "Memberi kabar yang jelas, menghargai rekan, dan mengoordinasikan pekerjaan.",
    },
]

SCENARIO_ITEMS = [
    {
        "id": "problem-1",
        "indicator": "problem_solving",
        "situation": "Seorang pengguna melapor tidak bisa terhubung ke jaringan. Kamu belum tahu apakah masalahnya hanya terjadi pada satu perangkat atau semua pengguna. Apa langkah pertamamu?",
        "options": [
            {"text": "Meminta detail gejala dan cakupan masalah, lalu melakukan pemeriksaan dasar yang diizinkan.", "score": 3, "rationale": "Mengumpulkan bukti dan mulai dari pemeriksaan yang aman."},
            {"text": "Mencoba satu pemeriksaan dasar pada perangkat tersebut, lalu menanyakan gejala tambahan jika belum teratasi.", "score": 2, "rationale": "Memulai troubleshooting dasar; cakupan masalah bisa diklarifikasi lebih awal."},
            {"text": "Langsung mengganti beberapa pengaturan jaringan agar koneksi segera pulih.", "score": 0, "rationale": "Mengubah konfigurasi sebelum memahami dampak dan penyebab."},
            {"text": "Meneruskan laporan ke pembimbing tanpa mengumpulkan informasi awal.", "score": 1, "rationale": "Melakukan eskalasi, tetapi belum menyertakan informasi yang membantu pemeriksaan."},
        ],
    },
    {
        "id": "problem-2",
        "indicator": "problem_solving",
        "situation": "Setelah mengikuti panduan yang diberikan, masalah belum selesai dan kamu belum yakin langkah berikutnya aman. Apa yang kamu lakukan?",
        "options": [
            {"text": "Menyampaikan pemeriksaan yang sudah dilakukan dan hasilnya, lalu meminta arahan sebelum mencoba langkah berisiko.", "score": 3, "rationale": "Melaporkan bukti dan mengeskalasi saat batas kewenangan atau keamanan tercapai."},
            {"text": "Mencari dokumentasi tepercaya dan mencoba langkah non-invasif yang sesuai panduan.", "score": 2, "rationale": "Menggunakan sumber belajar dan membatasi percobaan pada langkah berisiko rendah."},
            {"text": "Terus mencoba perubahan sampai salah satunya berhasil.", "score": 0, "rationale": "Melanjutkan perubahan tanpa mengendalikan risiko atau memverifikasi dampak."},
            {"text": "Berhenti bekerja dan menunggu tanpa memberi kabar kepada pembimbing.", "score": 1, "rationale": "Tidak mengambil langkah berisiko, tetapi hambatan dan kebutuhan bantuan tidak dikomunikasikan."},
        ],
    },
    {
        "id": "careful-1",
        "indicator": "careful_work",
        "situation": "Kamu diminta membantu mengubah konfigurasi perangkat jaringan yang digunakan beberapa orang. Apa yang sebaiknya dilakukan sebelum perubahan?",
        "options": [
            {"text": "Memastikan ruang lingkup dan izin, memeriksa prosedur/back-up yang berlaku, lalu mengonfirmasi rencana dengan pembimbing.", "score": 3, "rationale": "Memeriksa kewenangan, dampak, prosedur, dan rencana sebelum perubahan."},
            {"text": "Membaca instruksi yang ada dan bertanya kepada pembimbing jika ada langkah yang belum jelas.", "score": 2, "rationale": "Mengikuti instruksi serta mencari klarifikasi; pemeriksaan dampak dapat dibuat lebih eksplisit."},
            {"text": "Langsung menerapkan perubahan karena tugas sudah diberikan.", "score": 0, "rationale": "Belum memastikan dampak, izin, maupun prosedur pemulihan."},
            {"text": "Meminta rekan melakukan perubahan agar kamu tidak bertanggung jawab jika terjadi masalah.", "score": 1, "rationale": "Menghindari tindakan, tetapi tidak memastikan pekerjaan dilakukan melalui prosedur yang benar."},
        ],
    },
    {
        "id": "careful-2",
        "indicator": "careful_work",
        "situation": "Kamu menemukan daftar akun dan kata sandi di berkas bersama yang dapat dibuka banyak orang. Apa respons yang paling tepat?",
        "options": [
            {"text": "Tidak menyebarkan atau menggunakan berkas itu, lalu segera memberi tahu pembimbing melalui jalur yang aman.", "score": 3, "rationale": "Membatasi paparan informasi sensitif dan melaporkan melalui jalur yang tepat."},
            {"text": "Menghapus berkas tersebut agar tidak bisa dilihat orang lain, lalu memberi tahu pembimbing.", "score": 1, "rationale": "Berniat membatasi paparan, tetapi mengubah atau menghapus bukti tanpa arahan dapat mengganggu penanganan."},
            {"text": "Mengirim salinan berkas ke grup tim agar semua orang tahu ada masalah.", "score": 0, "rationale": "Memperluas paparan informasi sensitif."},
            {"text": "Mengabaikannya karena bukan bagian dari tugas yang diberikan.", "score": 0, "rationale": "Tidak melaporkan risiko keamanan yang terlihat."},
        ],
    },
    {
        "id": "learning-1",
        "indicator": "learning",
        "situation": "Pembimbing menunjukkan kesalahan pada catatan kerja yang kamu buat. Bagaimana kamu merespons?",
        "options": [
            {"text": "Meminta contoh bagian yang perlu diperbaiki, memperbarui catatan, lalu memeriksa ulang sebelum menyerahkan.", "score": 3, "rationale": "Mengklarifikasi masukan, menerapkannya, dan memverifikasi hasil."},
            {"text": "Mencatat masukan dan segera memperbaiki bagian yang sudah kamu pahami.", "score": 2, "rationale": "Menerapkan masukan; klarifikasi dapat diminta untuk bagian yang masih belum jelas."},
            {"text": "Menjelaskan bahwa kesalahan terjadi karena instruksi kurang jelas tanpa memeriksa catatan bersama.", "score": 0, "rationale": "Berfokus membela diri dan belum mengubah atau memeriksa hasil kerja."},
            {"text": "Mengubah catatan secepatnya tanpa memastikan bagian yang dimaksud.", "score": 1, "rationale": "Berusaha memperbaiki, tetapi tidak mengklarifikasi sehingga kesalahan dapat berulang."},
        ],
    },
    {
        "id": "learning-2",
        "indicator": "learning",
        "situation": "Kamu mendapat tugas menggunakan alat yang belum pernah dipakai. Tidak ada keadaan darurat dan pembimbing sedang menangani pekerjaan lain. Apa yang kamu lakukan?",
        "options": [
            {"text": "Membaca petunjuk atau dokumentasi yang disarankan, mencoba di lingkungan aman jika tersedia, dan menyiapkan pertanyaan spesifik.", "score": 3, "rationale": "Belajar mandiri dengan batas aman dan meminta bantuan secara terarah."},
            {"text": "Mencoba fitur dasar setelah membaca petunjuk singkat, lalu berhenti jika tugas menyentuh sistem yang belum dipahami.", "score": 2, "rationale": "Mencoba langkah dasar sambil membatasi risiko."},
            {"text": "Mengubah pengaturan pada sistem yang dipakai pengguna untuk belajar langsung.", "score": 0, "rationale": "Belajar melalui perubahan pada sistem aktif tanpa memastikan izin dan keamanan."},
            {"text": "Tidak mulai mencari informasi dan menunggu sampai pembimbing menyelesaikannya.", "score": 1, "rationale": "Menghindari risiko, tetapi belum menggunakan sumber belajar yang tersedia."},
        ],
    },
    {
        "id": "team-1",
        "indicator": "team_communication",
        "situation": "Kamu belum dapat menyelesaikan bagian tugas sesuai waktu yang disepakati karena menemukan kendala. Apa yang kamu sampaikan kepada tim?",
        "options": [
            {"text": "Memberi kabar sebelum tenggat, menjelaskan pekerjaan dan kendala yang sudah diperiksa, lalu menyepakati langkah berikutnya.", "score": 3, "rationale": "Memberi pembaruan tepat waktu, berbasis fakta, dan mengoordinasikan tindak lanjut."},
            {"text": "Memberi tahu bahwa tugas terlambat dan meminta tambahan waktu.", "score": 2, "rationale": "Mengomunikasikan keterlambatan, tetapi belum menjelaskan kendala dan rencana tindak lanjut."},
            {"text": "Menunggu sampai ditanya karena belum punya solusi.", "score": 0, "rationale": "Menunda komunikasi sehingga tim sulit menyesuaikan rencana."},
            {"text": "Mengatakan tugas sudah hampir selesai walaupun belum memeriksa kemajuannya.", "score": 0, "rationale": "Memberi informasi yang tidak terverifikasi."},
        ],
    },
    {
        "id": "team-2",
        "indicator": "team_communication",
        "situation": "Seorang rekan menyarankan langkah yang berbeda dari cara yang kamu pahami. Kalian belum tahu cara mana yang sesuai prosedur. Apa yang kamu lakukan?",
        "options": [
            {"text": "Membandingkan kedua usulan dengan dokumentasi/prosedur dan meminta pembimbing memutuskan jika masih ada ketidakjelasan.", "score": 3, "rationale": "Mendiskusikan bukti, merujuk prosedur, dan mengeskalasi ketidakpastian."},
            {"text": "Mendengarkan alasan rekan dan memeriksa kembali instruksi tugas sebelum memilih langkah.", "score": 2, "rationale": "Mendengarkan dan memeriksa instruksi; eskalasi dapat dilakukan bila belum terselesaikan."},
            {"text": "Tetap melakukan cara sendiri supaya pekerjaan lebih cepat selesai.", "score": 0, "rationale": "Mengabaikan koordinasi dan belum memastikan cara yang aman."},
            {"text": "Mengikuti usulan rekan agar tidak terjadi perdebatan.", "score": 1, "rationale": "Menghindari konflik, tetapi belum memeriksa kesesuaian langkah dengan prosedur."},
        ],
    },
]
