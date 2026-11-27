#!/usr/bin/env python3
"""Sisipkan halaman PDF yang belum diterjemahkan (teks OCR dari pengguna) ke HTML Arab العروض.
pakai: insert_ocr.py BERKAS.html OCR.txt [OCR2.txt ...] --pages 22,26,27 [--end]
 --end : halaman disisipkan di akhir isi (bukan sebelum penanda halaman berikutnya)"""
import re, sys, html, unicodedata, os
args = sys.argv[1:]
f = args[0]
pages_arg = args[args.index('--pages') + 1]
want = [int(x) for x in pages_arg.split(',')]
atend = '--end' in args
ocrs = [a for a in args[1:] if a.endswith('.txt')]
esc = lambda t: html.escape(t, quote=False)
TAT = 'ـ'

def parse(files):
    pg = {}; cur = None
    for fn in files:
        for ln in open(fn, encoding='utf-8').read().split('\n'):
            m = re.match(r'^Halaman\s+(\d+)\s*\|', ln, re.I)
            if m: cur = int(m.group(1)); pg[cur] = []; continue
            if re.match(r'^=+$', ln) or cur is None: continue
            pg[cur].append(ln.rstrip())
    return pg

TAF = set('فعولن مفاعيلن مفاعلن فعول فعو فاعلن فاعلاتن مستفعلن متفاعلن مفاعلتن مفعولات فعلن فعلاتن فعلات فاعلات حشو فاعي فعل مفاعي مفاعل مفاعلت مفعولن فالاتن فاع لاتن'.split())
def is_tafail(l):
    toks = [re.sub('[\u064b-\u0652\u0670]', '', t) for t in re.split(r'[\s/\-–]+', l) if t]
    return len(toks) >= 3 and all(t in TAF for t in toks)
SYMB = re.compile(r'^[\s/٥\-–0٠5|]+$')
HEAD = re.compile(r'^(مُحْتَوَيَاتُ|نَظْ?م|أسئلة|إجابة|شرح\s|العلة$|العلل الجارية|الفرق بين|وبين \()')
def ayat(t): return '<div class="ayat"><p class="ar" lang="ar">%s</p></div>' % esc(t)
def blk(*lines): return '<div class="blk blk-p">%s</div>' % ''.join(ayat(l) for l in lines)
def bait(h): return '<div class="bait"><div class="ayat">%s</div></div>' % ''.join('<p class="ar" lang="ar">%s</p>' % esc(x) for x in h)
def sy(baits): return '<div class="blk blk-sy"><div class="tag"><span class="tag__k" lang="ar">شَاهِدٌ شِعْرِيٌّ</span></div>%s</div>' % ''.join(bait(b) for b in baits)

def convert(lines):
    out = []; verse = []; foot = False; table = []
    def flush():
        nonlocal verse
        if verse: out.append(sy(verse)); verse = []
    def flush_table():
        nonlocal table
        if not table: return
        rows = []; cur = None
        for l in table:
            if l.startswith('+'):
                if cur: rows.append(cur); cur = None
                continue
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if cur is None: cur = cells
            else: cur = [(a + ' ' + b).strip() for a, b in zip(cur, cells)]
        if cur: rows.append(cur)
        names = None
        for r in rows:
            if r[0] == 'م':
                names = (r[1], r[2]); out.append('<h4 class="sub sub--3" lang="ar">%s — %s</h4>' % (esc(r[1]), esc(r[2])))
            else:
                out.append(blk('%s - %s: %s' % (r[0], names[0], r[1]), '%s: %s' % (names[1], r[2])))
        table = []
    for raw in lines:
        l = raw.replace(TAT, '').strip()
        if l.startswith('|') or l.startswith('+--'):
            flush(); table.append(l); continue
        flush_table()
        if not l: flush(); continue
        if re.match(r'^-{10,}$', l): flush(); foot = True; continue
        if re.fullmatch(r'[*\s]+', l) or SYMB.match(l): flush(); continue
        parts = re.split(r'\s{3,}', l)
        if len(parts) == 2 and not l.startswith(('-', '•')) and ('/' in parts[0] and ' / ' in l or True):
            if is_tafail(l) or ('/' in l and re.search(r'[/-]', l) and not re.search(r'[،:؛.]\s*$', parts[0])):   # baris tafa'il
                flush(); out.append(blk(parts[0], parts[1])); continue
            if len(parts[0]) < 90 and len(parts[1]) < 90:
                verse.append(parts); continue
        flush()
        if '/' in l and re.fullmatch(r'[ء-يً-ْ\s/\-–]+', l) and ' / ' in l:
            out.append(blk(l)); continue
        if HEAD.match(l) and len(l) < 70 and not re.search(r'[:.]\s*$', l):
            out.append('<h4 class="sub sub--3" lang="ar">%s</h4>' % esc(re.sub(r'^-\s*', '', l))); continue
        out.append(blk(re.sub(r'^[-•]\s+', '', l)))
    flush(); flush_table()
    return out

def norm(t):
    t = unicodedata.normalize('NFKC', t)
    t = re.sub('[ً-ٰٟـ]', '', t)
    t = re.sub('[إأآٱ]', 'ا', t).replace('ى', 'ي').replace('ة', 'ه')
    t = re.sub('[^ء-ي]', '', t)
    return t.replace('ا', '').replace('ل', '')
sh = lambda s: {s[i:i + 4] for i in range(len(s) - 3)}
def hal(n):
    return ('<div class="hal" id="hal-%s" data-kitab="%s"><span><i class="hal__t">Hlm. </i>%s</span>'
            '<button type="button" class="hal__pdf" data-pdf="%s" aria-label="Lihat PDF asli untuk Hlm. %s" title="Lihat PDF asli"></button></div>') % (n, n, n, n, n)

pg = parse(ocrs)
src = open(f, encoding='utf-8').read().split('\n')
HALRE = re.compile(r'^<div class="hal" id="hal-(\d+)"')
marks = [(i, int(HALRE.match(l).group(1))) for i, l in enumerate(src) if HALRE.match(l)]
ELRE = re.compile(r'^<(header class="bab"|div class="ringkasan"|h[234] class="sub|div class="blk)')
newtxt = norm(' '.join(' '.join(pg[p]) for p in want if p in pg)); NS = sh(newtxt)
removed = []; insert = {}      # indeks baris -> daftar baris disisipkan sebelum
# kelompokkan halaman menurut penanda berikutnya
groups = {}
for p in sorted(want):
    if p not in pg: print('halaman tidak ada di OCR:', p); continue
    nxt = next(((i, q) for i, q in marks if q > p), None)
    key = 'END' if (atend or nxt is None) else nxt[0]
    groups.setdefault(key, []).append(p)
drop = set()
for key, ps in groups.items():
    # wilayah dedup: dari penanda sebelum penanda-sebelum sampai penanda setelah penanda berikut
    if key == 'END':
        lo = marks[-3][0] if len(marks) >= 3 else 0; hi = len(src)
        pos = max(i for i, l in enumerate(src) if ELRE.match(l)) + 1
    else:
        k = [i for i, _ in marks].index(key)
        lo = marks[max(0, k - 2)][0]; hi = marks[min(len(marks) - 1, k + 1)][0]; pos = key
    for i in range(lo, hi):
        if src[i].startswith('<div class="blk'):
            t = norm(html.unescape(re.sub(r'<[^>]+>', ' ', src[i])))
            s = sh(t)
            if len(t) >= 40 and s and len(s & NS) / len(s) >= 0.92:
                drop.add(i); removed.append(re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', src[i])))[:80])
    blocks = []
    for p in ps:
        blocks.append(hal(p)); blocks += convert(pg[p])
    insert.setdefault(pos, []).extend(blocks)
res = []
for i, l in enumerate(src):
    if i in insert: res += insert[i]
    if i not in drop: res.append(l)
if len(src) in insert: res += insert[len(src)]
open(f, 'w', encoding='utf-8').write('\n'.join(res))
print(os.path.basename(f)[34:75], '| halaman disisipkan:', sorted(p for ps in groups.values() for p in ps), '| elemen dobel dibuang:', len(removed))
for r in removed: print('  -', r)
