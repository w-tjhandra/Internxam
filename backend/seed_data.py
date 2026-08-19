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
