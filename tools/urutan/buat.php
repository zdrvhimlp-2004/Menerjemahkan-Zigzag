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
 * Nama yang tidak tercantum di berkas akan ditampilkan paling akhir oleh daftar.php.
 */
const FILE = '.urutan.json';
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
    $hasil = []; $dipakai = [];
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
