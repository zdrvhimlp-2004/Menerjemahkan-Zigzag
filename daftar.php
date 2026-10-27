<?php
/*
 * Daftar isi otomatis: memindai folder Data/ dan mengeluarkan JSON pohon
 *   folder -> {"name": "...", "c": [ ... ]}
 *   file   -> {"name": "<judul halaman>", "href": "Data/.../file.html"}
 * Dipakai oleh assets/beranda.js (index.html).
 *
 * Di server dengan PHP : index.html memanggil daftar.php langsung (selalu terbaru).
 * Di hosting statis    : jalankan `php daftar.php > daftar.json` (otomatis lewat
 *                        .github/workflows/daftar.yml); beranda.js memakai daftar.json.
 */
const DATA_DIR = 'Data';
const EKSTENSI = ['html', 'htm', 'pdf'];

function judul_file(string $path, string $fallback): string {
    if (preg_match('/\.html?$/i', $path)) {
        $head = (string) @file_get_contents($path, false, null, 0, 4096);
        if (preg_match('~<title[^>]*>(.*?)</title>~is', $head, $m)) {
            $t = trim(html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5, 'UTF-8'));
            if ($t !== '') return $t;
        }
    }
    return $fallback;
}

function pindai(string $dir): array {
    $nama = array_values(array_diff(scandir($dir) ?: [], ['.', '..']));
    natcasesort($nama);
    $folder = $file = [];
    foreach ($nama as $n) {
        if ($n[0] === '.') continue;
        $path = $dir . '/' . $n;
        if (is_dir($path)) {
            $folder[] = ['name' => $n, 'c' => pindai($path)];
        } elseif (in_array(strtolower(pathinfo($n, PATHINFO_EXTENSION)), EKSTENSI, true)) {
            $href = implode('/', array_map('rawurlencode', explode('/', $path)));
            $file[] = ['name' => judul_file($path, pathinfo($n, PATHINFO_FILENAME)), 'href' => $href, 'file' => $n];
        }
    }
    return array_merge($folder, $file);
}

chdir(__DIR__);
$pohon = is_dir(DATA_DIR) ? pindai(DATA_DIR) : [];
if (PHP_SAPI !== 'cli') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-cache');
}
echo json_encode($pohon, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT), "\n";
