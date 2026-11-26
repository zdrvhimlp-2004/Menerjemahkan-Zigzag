<?php
/*
 * Membuat / memperbarui berkas tersembunyi .urutan.json di setiap folder di bawah Data/.
 *
 * Pakai (dari root repo):   php tools/urutan/buat.php
 *
 * - Folder yang belum punya .urutan.json: dibuat, isinya urutan tampil saat ini (folder dulu, lalu file).
 * - Folder yang sudah punya: urutan lama dipertahankan; nama yang sudah tidak ada dibuang;
 *   nama baru (file/folder baru) ditambahkan di bagian akhir.
 * Setelah itu urutan bisa diubah dengan menyunting berkas .urutan.json secara manual.
 *
 * Mode rapi:   php tools/urutan/buat.php --rapikan
 *   Menyusun ulang SEMUA folder dengan aturan baku (urutan lama diabaikan):
 *     1. الموضوعات.html (paling atas)   2. subfolder   3. file .pdf (HTML yang tertaut ke PDF-nya persis sesudahnya)   4. file .html   5. file .docx   6. lainnya
 *   Di tiap kelompok: berkas "pokok" dulu, lalu berkas "Latihan"; "Daftar Isi" di depan, berkas bertanda ✏ setelah berkas biasa, lalu menurut halaman awal "(Hlm N-M)" bila ada;
 *   selebihnya abjad alami (angka berurutan).
 * Nama yang tidak tercantum di berkas akan ditampilkan paling akhir oleh daftar.php.
 */
const FILE = '.urutan.json';
$RAPI = in_array('--rapikan', $argv ?? [], true);
chdir(__DIR__ . '/../..');

function kunci(string $s): string {
    if (class_exists('Normalizer')) { $n = Normalizer::normalize($s, Normalizer::FORM_C); if ($n !== false) $s = $n; }
    return mb_strtolower($s);
}

function bawaan(string $dir): array {
    $nama = array_values(array_diff(scandir($dir) ?: [], ['.', '..']));
    natcasesort($nama);
    $folder = $file = [];
    foreach ($nama as $n) {
        if ($n[0] === '.') continue;
        if (is_dir($dir . '/' . $n)) $folder[] = $n; else $file[] = $n;
    }
    return array_merge($folder, $file);
}

/* aturan "rapi": kelompok -> latihan belakangan -> abjad alami */
function rapi(string $dir, array $now): array {
    $kel = function (string $n) use ($dir): int {
        if (mb_strtolower($n) === 'الموضوعات.html') return 0;
        if (is_dir($dir . '/' . $n)) return 1;
        $e = strtolower(pathinfo($n, PATHINFO_EXTENSION));
        return $e === 'pdf' ? 2 : ($e === 'html' || $e === 'htm' ? 3 : ($e === 'docx' || $e === 'doc' ? 4 : 5));
    };
    usort($now, function ($a, $b) use ($kel) {
        $ka = $kel($a); $kb = $kel($b);
        if ($ka !== $kb) return $ka <=> $kb;
        $la = stripos($a, 'latihan') !== false ? 1 : 0; $lb = stripos($b, 'latihan') !== false ? 1 : 0;
        if ($la !== $lb) return $la <=> $lb;
        // "Daftar Isi" paling depan di dalam kelompoknya; berkas bertanda pensil (✏) setelah berkas biasa
        $da = stripos($a, 'daftar') === 0 ? 0 : 1; $db = stripos($b, 'daftar') === 0 ? 0 : 1;
        if ($da !== $db) return $da <=> $db;
        $pa = strncmp($a, "\u{270F}", strlen("\u{270F}")) === 0 ? 1 : 0; $pb = strncmp($b, "\u{270F}", strlen("\u{270F}")) === 0 ? 1 : 0;
        if ($pa !== $pb) return $pa <=> $pb;
        // berkas kitab bertanda "(Hlm N-M)": urut menurut halaman awal; yang tanpa halaman setelahnya
        $ha = preg_match('/\(Hlm\s*(\d+)/i', $a, $m) ? (int) $m[1] : PHP_INT_MAX;
        $hb = preg_match('/\(Hlm\s*(\d+)/i', $b, $m) ? (int) $m[1] : PHP_INT_MAX;
        if ($ha !== $hb) return $ha <=> $hb;
        return strnatcasecmp($a, $b);
    });
    // HTML yang tertaut ke sebuah PDF (PDFPANEL src) ditaruh persis setelah PDF aslinya
    $nfc = function (string $s): string { return class_exists('Normalizer') ? mb_strtolower(Normalizer::normalize($s, Normalizer::FORM_C)) : mb_strtolower($s); };
    foreach ($now as $h) {
        if (!preg_match('/\.html?$/i', $h) || mb_strtolower($h) === 'الموضوعات.html') continue;
        $isi = (string) @file_get_contents($dir . '/' . $h);
        if (!preg_match('/PDFPANEL\s*=\s*\{\s*src\s*:\s*"([^"]+)"/', $isi, $m)) continue;
        $tujuan = $nfc(basename($m[1]));
        $pdf = null;
        foreach ($now as $x) if (preg_match('/\.pdf$/i', $x) && $nfc($x) === $tujuan && dirname($m[1]) === '.') $pdf = $x;
        if ($pdf === null) continue;
        $now = array_values(array_filter($now, function ($x) use ($h) { return $x !== $h; }));
        $pos = array_search($pdf, $now, true);
        while (isset($now[$pos + 1]) && ($GLOBALS['_sudah'][$dir][$now[$pos + 1]] ?? false)) $pos++;
        array_splice($now, $pos + 1, 0, [$h]);
        $GLOBALS['_sudah'][$dir][$h] = true;
    }
    return $now;
}

$dibuat = $diubah = $tetap = 0;
function proses(string $dir): void {
    global $dibuat, $diubah, $tetap;
    $now = bawaan($dir);
    $f = $dir . '/' . FILE;
    $lama = [];
    if (is_file($f)) {
        $j = json_decode((string) file_get_contents($f), true);
        $lama = is_array($j) && is_array($j['urutan'] ?? null) ? array_values(array_filter($j['urutan'], 'is_string')) : [];
    }
    $petaNow = [];
    foreach ($now as $n) $petaNow[kunci($n)] = $n;
    global $RAPI;
    $hasil = []; $dipakai = [];
    if ($RAPI) { $lama = rapi($dir, $now); }      // abaikan urutan lama, pakai aturan rapi
    foreach ($lama as $nm) {                       // pertahankan urutan lama untuk nama yang masih ada
        $k = kunci($nm);
        if (isset($petaNow[$k]) && !isset($dipakai[$k])) { $hasil[] = $petaNow[$k]; $dipakai[$k] = true; }
    }
    foreach ($now as $n) if (!isset($dipakai[kunci($n)])) $hasil[] = $n;   // nama baru di akhir
    $isi = ['_catatan' => 'Urutan tampil di folder ini (nama file dan subfolder). Nama yang tidak tercantum ditaruh paling akhir.', 'urutan' => $hasil];
    $json = json_encode($isi, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . "\n";
    if (!is_file($f)) { file_put_contents($f, $json); $dibuat++; }
    elseif (file_get_contents($f) !== $json) { file_put_contents($f, $json); $diubah++; }
    else $tetap++;
    foreach ($now as $n) if (is_dir($dir . '/' . $n)) proses($dir . '/' . $n);
}
proses('Data');
echo "dibuat: $dibuat, diperbarui: $diubah, tidak berubah: $tetap\n";
