#!/usr/bin/env python3
"""Ubah halaman terjemah "Syadza Al-'Urf" menjadi versi Arab saja, tertaut ke PDF-nya.
pakai: conv_sarf.py SUMBER.html TUJUAN.html NAMA_PDF "JUDUL" "KETERANGAN" [PDF_HLM_AWAL_KITAB:AWAL_PDF]"""
import re, sys
src, dst, pdfname, judul, ket = sys.argv[1:6]
awal = sys.argv[6] if len(sys.argv) > 6 else ''
s = open(src, encoding='utf-8').read()
head, body = s.split('<body', 1)
body = '<body' + body

# 1. semua teks Indonesia
body = re.sub(r'<p class="(?:id|sub__id|bab__id|ringkasan__id|judul__id)"[^>]*>.*?</p>', '', body, flags=re.S)
body = re.sub(r'<div class="toc__id">.*?(<span class="toc__meta">.*?</span>)\s*</div>', r'\1', body, flags=re.S)
body = re.sub(r'<span class="tag__t">.*?</span>', '', body, flags=re.S)
body = re.sub(r'(<span class="sw[^"]*" lang="ar">[^<]*</span>).*?(</li>)', r'\1\2', body, flags=re.S)
body = re.sub(r'\s*<p class="isi__ket"[^>]*>.*?</p>', '\n    <p class="isi__ket" lang="ar">%s</p>' % ket, body, count=1, flags=re.S)
body = re.sub(r'<h2 class="legend__judul">.*?</h2>', '<h2 class="legend__judul" lang="ar">دَلِيلُ الْأَلْوَانِ</h2>', body, flags=re.S)
body = body.replace('aria-label="Kode Warna"', 'aria-label="دليل الألوان"').replace('aria-label="Kode warna"', 'aria-label="دليل الألوان"')
body = body.replace('aria-label="Fihris (Daftar Isi)"', 'aria-label="الفهرس"').replace('title="Fihris (Daftar Isi)"', 'title="الفهرس"').replace('aria-label="Fihris"', 'aria-label="الفهرس"')
body = body.replace('Fihris (Daftar Isi) <span lang="ar">الْفِهْرِسُ</span>', '<span lang="ar">الْفِهْرِسُ</span>')
body = body.replace('aria-label="Tutup"', 'aria-label="إغلاق"')
body = body.replace('title="Kode Warna"', 'title="دليل الألوان"').replace('title="Kode warna"', 'title="دليل الألوان"')

# 2. penanda halaman ganda: Hlm. Kitab + Hlm. PDF
def hal(n, p):
    return ('<div class="hal" id="hal-%s" data-kitab="%s"><span><i class="hal__t">Hlm. </i>%s</span>'
            '<button type="button" class="hal__pdf" data-pdf="%s" aria-label="Lihat PDF asli untuk Hlm. %s" title="Lihat PDF asli"></button></div>') % (n, n, p, p, p)
body = re.sub(r'<div class="hal hal--akhir"[^>]*>.*?</div>\n?', '', body, flags=re.S)
body = re.sub(r'<div class="hal-awal" id="hal-awal-(\d+)"><span>[^<]*</span><button[^>]*data-pdf="(\d+)"[^>]*></button></div>', lambda m: hal(m.group(1), m.group(2)), body)
body = re.sub(r'<div class="hal"><span>Juz \d+ &middot; Hlm\. (\d+)</span><button[^>]*data-pdf="(\d+)"[^>]*></button></div>', lambda m: hal(m.group(1), m.group(2)), body)
if awal:
    n, p = awal.split(':')
    body = body.replace('<div class="isi__wrap">', '<div class="isi__wrap">', 1)
    i = body.index('<header class="bab"') if '<header class="bab"' in body else body.index('<div class="ayat"')
    body = body[:i] + hal(n, p) + '\n' + body[i:]

# 2b. penanda tambahan: kitab:pdf:potongan-teks-tanpa-harakat (disisipkan sebelum blok yang memuat teks itu)
HAR = re.compile('[\u064b-\u0652\u0670]')
for ex in sys.argv[7:]:
    n, p, needle = ex.split(':', 2)
    for m in re.finditer(r'<p class="ar"[^>]*>(.*?)</p>', body, flags=re.S):
        if needle in HAR.sub('', re.sub('<[^>]+>', '', m.group(1))):
            k = body.rfind('<div class="ayat', 0, m.start())
            body = body[:k] + hal(n, p) + '\n' + body[k:]
            break
    else:
        print('TIDAK KETEMU:', ex)
# halaman yang tidak ada di sumber -> catatan berbahasa Arab
body = re.sub(r'<div class="hal-miss"><span>[^<]*?(\d+)[^<]*</span></div>', lambda m: '<div class="hal-miss"><span lang="ar">الصَّفْحَةُ %s غَيْرُ مَوْجُودَةٍ فِي النَّصِّ الْمَصْدَرِ</span></div>' % m.group(1).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')), body)

# 3. kepala: judul, PDF, CSS
head = re.sub(r'<title>.*?</title>', '<title>%s — النص العربي</title>' % judul, head, count=1)
head = re.sub(r'pdfpanel\.css\?v=\d+', 'pdfpanel.css?v=8', head)
body = re.sub(r'PDFPANEL=\{src:"[^"]*"[^}]*\}', 'PDFPANEL={src:"%s"}' % pdfname, body)
open(dst, 'w', encoding='utf-8').write(head + body)
print('penanda:', len(re.findall(r'class="hal" id', body)), '| sisa p.id:', len(re.findall(r'class="id"', body)))
