#!/usr/bin/env python3
"""Ubah bagian terjemah "al-Mursyid al-Wafi fil-'Arudh" menjadi versi Arab saja, tertaut ke PDF (hlm. kitab = hlm. PDF).
pakai: conv_arudh.py SUMBER.html TUJUAN.html NAMA_PDF "JUDUL-TAB" "KETERANGAN" """
import re, sys
src, dst, pdfname, judul, ket = sys.argv[1:6]
s = open(src, encoding='utf-8').read()
head, body = s.split('<body', 1)
body = '<body' + body

# 1. semua teks Indonesia
body = re.sub(r'<p class="(?:id|sub__id|bab__id|ringkasan__id|judul__id)"[^>]*>.*?</p>', '', body, flags=re.S)
body = re.sub(r'<p class="ringkasan__judul">.*?</p>', '<p class="ringkasan__judul" lang="ar">ملخص الباب</p>', body, flags=re.S)
body = re.sub(r'<div class="toc__id">.*?(<span class="toc__meta">.*?</span>)\s*</div>', r'\1', body, flags=re.S)
body = re.sub(r'<span class="(?:toc__t|tag__t|toc__id)">.*?</span>', '', body, flags=re.S)
body = re.sub(r'(<span class="toc__meta">Hlm\.[^<]*?)(?: &middot; \d+ sub-bab)?</span>', r'\1</span>', body)
body = re.sub(r'\s*<div class="catatan".*?</div>', '', body, flags=re.S)
body = re.sub(r'(<span class="sw[^"]*" lang="ar">[^<]*</span>).*?(</li>)', r'\1\2', body, flags=re.S)
body = re.sub(r'\s*<p class="isi__ket"[^>]*>.*?(?=\n\s*<(?:p|div|dialog|section)\b)', '', body, flags=re.S)
body = body.replace('<h1 class="isi__judul"', '<h1 class="isi__judul"', 1)
body = re.sub(r'(<h1 class="isi__judul"[^>]*>.*?</h1>)', r'\1\n    <p class="isi__ket" lang="ar">%s</p>' % ket, body, count=1, flags=re.S)
body = re.sub(r'<h2 class="legend__judul">.*?</h2>', '<h2 class="legend__judul" lang="ar">دَلِيلُ الْأَلْوَانِ</h2>', body, flags=re.S)
for a, b in [('aria-label="Kode Warna"', 'aria-label="دليل الألوان"'), ('aria-label="Kode warna"', 'aria-label="دليل الألوان"'),
             ('title="Kode Warna"', 'title="دليل الألوان"'), ('title="Kode warna"', 'title="دليل الألوان"'),
             ('aria-label="Fihris (Daftar Isi)"', 'aria-label="الفهرس"'), ('title="Fihris (Daftar Isi)"', 'title="الفهرس"'), ('aria-label="Fihris"', 'aria-label="الفهرس"'),
             ('Fihris (Daftar Isi) <span lang="ar">الْفِهْرِسُ</span>', '<span lang="ar">الْفِهْرِسُ</span>'),
             ('aria-label="Tutup"', 'aria-label="إغلاق"'), ('>Buka semua<', '>فتح الكل<'), ("'Tutup semua' : 'Buka semua'", "'إغلاق الكل' : 'فتح الكل'")]:
    body = body.replace(a, b)

# 2. penanda halaman ganda: hlm. kitab = hlm. PDF
def hal(n):
    return ('<div class="hal" id="hal-%s" data-kitab="%s"><span><i class="hal__t">Hlm. </i>%s</span>'
            '<button type="button" class="hal__pdf" data-pdf="%s" aria-label="Lihat PDF asli untuk Hlm. %s" title="Lihat PDF asli"></button></div>') % (n, n, n, n, n)
body, nh = re.subn(r'<div class="hal"(?: id="hal-\d+")?><span>(?:Juz \d+ &middot; )?Hlm\. (\d+)</span>(?:<button[^>]*></button>)?</div>', lambda m: hal(m.group(1)), body)

# 3. kepala dan skrip
head = re.sub(r'<title>.*?</title>', '<title>%s — النص العربي</title>' % judul, head, count=1)
if 'pdfpanel.css' not in head:
    head = re.sub(r'(<link rel="stylesheet" href="[^"]*halaman\.css[^"]*">)', r'\1\n<link rel="stylesheet" href="../../../../assets/pdfpanel.css?v=8">', head, count=1)
body = re.sub(r'pdfpanel\.css\?v=\d+', 'pdfpanel.css?v=8', body)
if 'PDFPANEL' not in body:
    body = body.replace('<script src="../../../../assets/halaman.js', '<script>window.PDFPANEL={src:"%s"};</script>\n<script src="../../../../assets/pdfpanel.js?v=7"></script>\n<script src="../../../../assets/halaman.js' % pdfname, 1)
open(dst, 'w', encoding='utf-8').write(head + body)
print('penanda:', nh, '| sisa p.id:', len(re.findall(r'class="id"', body)))
