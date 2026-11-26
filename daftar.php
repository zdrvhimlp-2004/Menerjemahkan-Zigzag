<?php
/*
 * Daftar isi otomatis: memindai folder Data/ dan mengeluarkan JSON pohon
 *   folder -> {"name": "...", "c": [ ... ]}
 *   file   -> {"name": "<nama file tanpa ekstensi>", "ext": "html", "href": "Data/.../file.html"}
 * Dipakai oleh assets/beranda.js (index.html).
 *
 * Dipanggil index.html setiap dibuka, jadi isi folder Data/ selalu terbaru (butuh server PHP).
 *
 * Urutan tampil: tiap folder boleh punya berkas tersembunyi .urutan.json berisi {"urutan": ["nama", ...]}
 * (nama file DAN nama subfolder, lengkap dengan ekstensi). Yang tercantum diurutkan sesuai daftar;
 * yang tidak tercantum ditaruh paling akhir. Tanpa berkas itu, urutannya: folder dulu, lalu file (abjad).
 */
const DATA_DIR = 'Data';

const URUTAN_FILE = '.urutan.json';   // berkas tersembunyi (diawali titik): urutan tampil di folder ini

/* kunci pembanding nama: Unicode NFC + huruf kecil, supaya nama Arab yang diketik ulang tetap cocok */
function kunci(string $s): string {
    if (class_exists('Normalizer')) { $n = Normalizer::normalize($s, Normalizer::FORM_C); if ($n !== false) $s = $n; }
    return mb_strtolower($s);
}

/* baca daftar urutan dari .urutan.json di folder ini: {"urutan": ["nama1", "nama2", ...]} */
function bacaUrutan(string $dir): array {
    $f = $dir . '/' . URUTAN_FILE;
    if (!is_file($f)) return [];
    $j = json_decode((string) file_get_contents($f), true);
    $daftar = is_array($j) ? ($j['urutan'] ?? []) : [];
    $peta = [];
    foreach (is_array($daftar) ? array_values($daftar) : [] as $i => $nm) {
        if (is_string($nm) && !isset($peta[kunci($nm)])) $peta[kunci($nm)] = $i;
    }
    return $peta;
}

function pindai(string $dir): array {
    $nama = array_values(array_diff(scandir($dir) ?: [], ['.', '..']));
    natcasesort($nama);
    $folder = $file = [];
    foreach ($nama as $n) {
        if ($n[0] === '.') continue;
        $path = $dir . '/' . $n;
        if (is_dir($path)) {
            $folder[] = ['_n' => $n, 'name' => $n, 'c' => pindai($path)];
        } else {
            $href = implode('/', array_map('rawurlencode', explode('/', $path)));
            $file[] = ['_n' => $n, 'name' => trim(pathinfo($n, PATHINFO_FILENAME)), 'ext' => strtolower(pathinfo($n, PATHINFO_EXTENSION)), 'href' => $href];
        }
    }
    $semua = array_merge($folder, $file);   // urutan bawaan: folder dulu, lalu file (abjad alami)
    $peta = bacaUrutan($dir);
    if ($peta) {
        // yang tercantum di .urutan.json mengikuti urutannya; yang tidak tercantum ditaruh paling akhir (urutan bawaan)
        $ada = [];
        foreach ($semua as $i => $it) $ada[$i] = $peta[kunci($it['_n'])] ?? PHP_INT_MAX;
        $idx = array_keys($semua);
        usort($idx, fn($a, $b) => $ada[$a] <=> $ada[$b] ?: $a <=> $b);
        $semua = array_map(fn($i) => $semua[$i], $idx);
    }
    foreach ($semua as &$it) unset($it['_n']);
    return $semua;
}

chdir(__DIR__);
$pohon = is_dir(DATA_DIR) ? pindai(DATA_DIR) : [];
if (PHP_SAPI !== 'cli') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-cache');
}
echo json_encode($pohon, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT), "\n";
