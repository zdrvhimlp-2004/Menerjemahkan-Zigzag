#!/usr/bin/env python3
"""Sejajarkan baris-baris HTML Arab dengan halaman PDF (hasil OCR) lalu pasang ulang penanda halaman.
pakai: align_pages.py BERKAS.html FOLDER_OCR   (FOLDER_OCR berisi p-001.png.txt ... dari tesseract; hlm. kitab = hlm. PDF)"""
import re, sys, html, unicodedata, os
f, ocdir = sys.argv[1:3]
NP = len([x for x in os.listdir(ocdir) if x.endswith('.txt')])
LO, HI = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, NP)
OFF = int(sys.argv[5]) if len(sys.argv) > 5 else 0          # hlm. kitab = hlm. PDF - OFF
def norm(t):
    t = unicodedata.normalize('NFKC', t)
    t = re.sub('[ً-ٰٟـ]', '', t)
    t = re.sub('[إأآٱ]', 'ا', t).replace('ى', 'ي').replace('ة', 'ه')
    t = re.sub('[^ء-ي]', '', t)
    return t.replace('ا', '').replace('ل', '')
N = 4
sh = lambda s: {s[i:i + N] for i in range(len(s) - N + 1)}
PG = {}
for p in range(1, NP + 1):
    PG[p] = sh(norm(open(os.path.join(ocdir, 'p-%03d.png.txt' % p), encoding='utf-8').read()))
lines = open(f, encoding='utf-8').read().split('\n')
HALRE = re.compile(r'^\s*<div class="hal" id="hal-\d+" data-kitab="\d+">')
lines = [l for l in lines if not HALRE.match(l)]
ELRE = re.compile(r'^\s*<(header class="bab"|div class="ringkasan"|h[234] class="sub|div class="blk|div class="ayat|div class="syiir|h[2-4] class="(?:bagian|pasal)__judul|p class="(?:bagian|pasal)__judul)')
idx = [i for i, l in enumerate(lines) if ELRE.match(l)]
def span(k):
    i = idx[k]; j = idx[k + 1] if k + 1 < len(idx) else len(lines)
    for q in range(i, j):
        if '</section>' in lines[q] or '<script' in lines[q]: j = q; break
    return ' '.join(lines[i:j])
texts = [norm(html.unescape(re.sub(r'<[^>]+>', ' ', span(k)))) for k in range(len(idx))]
isring = ['class="ringkasan"' in lines[i] for i in idx]
S = [sh(t) if not r else set() for t, r in zip(texts, isring)]
n = len(idx)
# DP monoton: halaman tidak menurun
NEG = -1e18
score = [[0.0] * (NP + 1) for _ in range(n)]
for i in range(n):
    if not S[i]: continue
    for p in range(LO, HI + 1):
        score[i][p] = len(S[i] & PG[p])
dp = [[NEG] * (NP + 1) for _ in range(n)]
bk = [[0] * (NP + 1) for _ in range(n)]
for p in range(LO, HI + 1): dp[0][p] = score[0][p]
JUMP = 1.5                              # biaya melompati halaman (halaman yang tidak diterjemahkan jarang)
for i in range(1, n):
    best, arg = NEG, LO
    for p in range(LO, HI + 1):
        cand = dp[i - 1][p - 1] if p > LO else NEG
        # terbaik dari halaman q<=p dengan penalti (p-q)*JUMP
        if best > NEG: best -= JUMP
        if dp[i - 1][p] > best: best, arg = dp[i - 1][p], p
        stay = dp[i - 1][p] + 0.3
        if stay >= best:
            dp[i][p] = stay + score[i][p]; bk[i][p] = p
        else:
            dp[i][p] = best + score[i][p]; bk[i][p] = arg
p = max(range(LO, HI + 1), key=lambda q: dp[n - 1][q])
pages = [0] * n
for i in range(n - 1, -1, -1):
    pages[i] = p; p = bk[i][p]
# ringkasan mengikuti judul bab di atasnya; elemen tanpa isyarat ikut tetangga (sudah monoton)
def hal(n):
    k = n - OFF
    return ('<div class="hal" id="hal-%s" data-kitab="%s"><span><i class="hal__t">Hlm. </i>%s</span>'
            '<button type="button" class="hal__pdf" data-pdf="%s" aria-label="Lihat PDF asli untuk Hlm. %s" title="Lihat PDF asli"></button></div>') % (k, k, n, n, n)
out = []; prev = 0; pos = {}
for k, i in enumerate(idx):
    pos[i] = pages[k]
ins = {}
for k, i in enumerate(idx):
    if pages[k] != prev:
        # penanda diletakkan sebelum judul bab bila elemen sebelumnya adalah judul/ringkasan yang tidak berpindah halaman
        ins[i] = pages[k]; prev = pages[k]
res = []
for i, l in enumerate(lines):
    if i in ins: res.append(hal(ins[i]))
    res.append(l)
s = '\n'.join(res)
# daftar isi: hitung ulang halaman dari penanda baru
idpage = {}
for k, i in enumerate(idx):
    m = re.search(r'id="((?:bab|sub)-\d+)"', lines[i])
    if m: idpage[m.group(1)] = pages[k]
last = pages[-1]
babs = [(k, re.search(r'id="(bab-\d+)"', lines[i]).group(1)) for k, i in enumerate(idx) if '<header class="bab"' in lines[i] and re.search(r'id="(bab-\d+)"', lines[i])]
bab_rng = {}
for j, (k, bid) in enumerate(babs):
    end = pages[babs[j + 1][0] - 1] if j + 1 < len(babs) else last
    bab_rng[bid] = (pages[k], max(end, pages[k]))
def rng(a, b): a -= OFF; b -= OFF; return 'Hlm. %d' % a + ('&ndash;%d' % b if b != a else '')
s = re.sub(r'(<a class="toc__ar" lang="ar" href="#(bab-\d+)">.*?</a>)<span class="toc__meta">[^<]*</span>',
           lambda m: m.group(1) + '<span class="toc__meta">%s</span>' % rng(*bab_rng[m.group(2)]) if m.group(2) in bab_rng else m.group(0), s)
s = re.sub(r'(<a href="#(sub-\d+)"><span class="toc__a" lang="ar">.*?</span>)<span class="toc__ref">[^<]*</span>',
           lambda m: m.group(1) + '<span class="toc__ref">Hlm. %d</span>' % (idpage[m.group(2)] - OFF) if m.group(2) in idpage else m.group(0), s)
open(f, 'w', encoding='utf-8').write(s)
ps = sorted(set(pages))
print(os.path.basename(f)[34:75], 'elemen', n, 'halaman', ps[0], '-', ps[-1], '| penanda', len(ins), '| lompatan>1:', [ (a, b) for a, b in zip(ps, ps[1:]) if b - a > 1][:12])
