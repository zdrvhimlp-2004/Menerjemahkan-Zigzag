# -*- coding: utf-8 -*-
"""Judul Indonesia untuk heading (indeks blok di blocks.json -> terjemah judul)."""

HEADS = {
    7: "Tujuan Mata Kuliah",
    8: "1. Deskripsi Umum Mata Kuliah",
    10: "2. Tujuan Utama Mata Kuliah",
    16: "Topik-Topik Mata Kuliah",
    18: "Ilmu Bunyi, Prinsip-Prinsipnya, dan Bidang-Bidangnya",
    23: "Sisi-Sisi Ilmu Bunyi",
    35: "Bidang-Bidang Ilmu Bunyi",
    50: "Kajian Fonetik: Perkembangan dan Kemunculannya",
    52: "Kajian Fonetik pada Bangsa Arab",
    54: "Upaya dan Arah dalam Kajian Fonetik",
    68: "Upaya Para Ahli Arab Modern",
    73: "Fonetik Akustik (Fisika Bunyi)",
    76: "Konsep Bunyi",
    78: "Definisi Bunyi secara Fisika",
    88: "Karakteristik Bunyi",
    97: "Pembagian Materi Bunyi",
    101: "Fonologi (Ilmu Bunyi Abstrak)",
    104: "Perbedaan antara Fonologi dan Fonetik",
    107: "Konsep-Konsep Dasar Fonologi",
    111: "Pentingnya Fonologi",
    119: "Alat Ucap (Organ Artikulasi)",
    121: "Paru-Paru",
    125: "Batang Tenggorokan (Trakea)",
    127: "Laring (Pangkal Tenggorok)",
    130: "Pita Suara",
    137: "Tekak (Faring)",
    143: "Rongga Mulut",
    172: "Pembagian Bunyi menurut Makhraj (Fonetik Segmental)",
    176: "Makhraj Huruf",
    206: "Sifat-Sifat Bunyi",
    212: "Pertama: Kelompok Sifat yang Memiliki Lawan",
    219: "Kedua: Sifat yang Tidak Memiliki Lawan (Tujuh Sifat)",
    229: "Suku Kata (Silabel)",
    231: "Kaidah Pemenggalan Suku Kata pada Kata",
    239: "Jenis-Jenis Suku Kata dalam Bahasa Arab",
    250: "Performa Vokal (Olah Suara)",
    253: "Bidang-Bidang Performa Vokal",
    265: "Keterampilan dalam Memprofesionalkan Performa Vokal",
    278: "Variasi dalam Performa Vokal",
    286: "Jeda Vokal (Pemisah Bunyi)",
}

# heading H3 di sumber yang di halaman baru dijadikan bab (H2)
PROMOTE = {229}
# id untuk heading tanpa id di sumber
FALLBACK_ID = {8: 'wasf-amm', 10: 'hadaf-raisi'}

# keterangan tabel
TABLE1_HEAD = ('م', 'No.', 'قَائِمَةُ الْمَوْضُوعَاتِ', 'Daftar Topik', 'سَاعَاتٌ', 'Jam')
TABLE1_TOTAL = ('الْمَجْمُوعُ', 'Jumlah')
TABLE2_HEAD = ('م', 'No.', 'الصَّوْتُ', 'Bunyi')
