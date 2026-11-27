#!/usr/bin/env python3
"""Bangun HTML Arab dari transkrip teks (3 format) علم المعاني, per bab (الفصل), dengan penanda halaman kitab/PDF.
pakai: gen_maani.py TEMPLAT.html OUT_DIR NAMA_PDF OFFSET FILE1.txt [FILE2.txt ...]
 (hlm. kitab = label halaman di berkas; hlm. PDF = label + OFFSET)"""
import re, sys, html, os, unicodedata
tpl_f, outdir, pdfname, OFF = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
PDFMAP = {int(a.split('=')[0][4:]): int(a.split('=')[1]) for a in sys.argv[5:] if a.startswith('map:')}
files = [a for a in sys.argv[5:] if not a.startswith('map:')]
AR = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
esc = lambda t: html.escape(t, quote=False)
def norm(t):
    t = re.sub('[ً-ٰٟـ]', '', unicodedata.normalize('NFKC', t))
    return re.sub('[^ء-ي]', '', re.sub('[إأآٱ]', 'ا', t).replace('ى', 'ي'))

PATS = [r'^صفحة\s+([٠-٩0-9]+)\s*(?:\(Halaman[^)]*\))?\s*$', r'^--- الصفحة\s+([٠-٩0-9]+)', r'^\[الصفحة\s+([٠-٩0-9]+)\]', r'^\[صفحة\s+([٠-٩0-9]+)\]']
def read_pages(fn):
    pages = []; cur = None
    raw = open(fn, encoding='utf-8-sig').read()
    raw = re.sub(r'<span[^>]*>|</span>|<div[^>]*>|</div>|<br\s*/?>', '\n', raw)
    for ln in raw.split('\n'):
        s = ln.rstrip('\r')
        for p in PATS:
            m = re.match(p, s.strip())
            if m: cur = [int(m.group(1).translate(AR)), []]; pages.append(cur); break
        else:
            if cur is not None: cur[1].append(s)
    return pages

def parse_page(lines):
    """-> daftar butir: ('p',t) ('li',t) ('verse',[h1,h2]) ('fn',t) ('chap',t) ('sub',t)"""
    items = []; fn = []; i = 0; n = len(lines); foot = False
    while i < n:
        raw = lines[i]; s = raw.strip(); i += 1
        if re.fullmatch(r'\[(?:الحواشي|الحاشية)\]\s*:?', s): foot = True; continue
        m = re.match(r'^\[(?:الحاشية|الحواشي)\]\s*:\s*(.+)$', s)
        if m: fn.append(m.group(1).replace(' *** ', ' … ')); continue
        if foot: fn.append(s.replace(' *** ', ' … ')); continue
        mh = re.match(r'^(#{1,3})\s+(.+)$', s)
        if mh:
            if len(mh.group(1)) >= 2: items.append(('sub', mh.group(2).strip())); continue
            s = mh.group(2).strip()
        if not s or re.fullmatch(r'_{5,}', s) or re.fullmatch(r'[*\-_=\s]+', s) or s in ('علم المعاني', 'الهوامش:', 'الهوامش'): continue
        if s == 'الشطر الأول':                       # tabel syair (format 2)
            while i < n and lines[i].strip() in ('', 'الشطر الثاني'): i += 1
            cells = []
            while i < n and lines[i].startswith('\t'):
                c = lines[i].strip(); i += 1
                if not c: break
                cells.append(c)
            for k in range(0, len(cells) - 1, 2): items.append(('verse', [cells[k], cells[k + 1]]))
            continue
        m = re.match(r'^هامش صفحة\s+[٠-٩0-9]+:\s*(.*)$', s)
        if m: fn.append(m.group(1)); continue
        if re.match(r'^\([٠-٩۰-۹]+\)\s', s): fn.append(s); continue
        if re.search(r'\s\*\*\*\s', s) and len(s) < 170:
            parts = [x.strip() for x in re.split(r'\s\*\*\*\s', s)]
            if len(parts) == 2: items.append(('verse', parts)); continue
        if len(s) < 170 and len(re.findall(r'\s\*\s', s)) == 1 and not s.startswith(('*', '﴿')):
            parts = [x.strip() for x in re.split(r'\s\*\s', s)]
            if len(parts) == 2: items.append(('verse', parts)); continue
        if re.search(r'\s{3,}\*\s{3,}', s):
            parts = [x.strip() for x in re.split(r'\s{3,}\*\s{3,}', s)]
            if len(parts) == 2: items.append(('verse', parts)); continue
        if ' — ' in s and len(s) < 150 and not re.search(r'[.:؟]\s*$', s):
            parts = [x.strip() for x in s.split(' — ')]
            if len(parts) == 2: items.append(('verse', parts)); continue
        if s.startswith('* '): items.append(('li', s[2:].strip())); continue
        items.append(('p', s))
    return items, fn

NUMH = re.compile(r'^[٠-٩0-9]+\s*[-–]\s*\S.{0,66}$')
def kind(t):
    if re.match(r'^الفصل\s+\S+', t) and len(t) <= 50 and re.search(r'^الفصل\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)\b', t): return 'chap'
    if NUMH.match(t) and not re.search(r'[.،]$', t) and len(t) <= 70 and not re.search(r'[﴿«]', t): return 'sub'
    if len(t) <= 60 and t.endswith(':') and t.startswith('ال') and not re.search(r'[﴿«]', t): return 'sub'
    if re.match(r'^(أسلوب|الأسلوب|أدوات|طرق|الأغراض|أغراض)\s', t) and len(t) <= 40 and not re.search(r'[.،:]$', t): return 'sub'
    if re.search(r'(^|\s)قول|^(تأمل|انظر|وانظر|ومثله|ومنه|وكقول|كما في|وقول|وخذ|الجزء الثاني|أحوال الجملة)', t): return 'p'
    if len(t) <= 45 and len(t.split()) >= 2 and not re.search(r'[.:،؛?؟!)\]»﴾]$', t) and not re.search(r'[﴿«(\[]', t) and re.search('[\u0621-\u064a]', t): return 'sub'
    if re.fullmatch(r'تقديم\s*:?', t): return 'sub'
    return 'p'

# --- baca semua halaman
allp = []
for f in files: allp += read_pages(f)
allp.sort(key=lambda x: x[0])
seen = set(); chapters = []     # setiap bab: dict(key,title,pages=[(label,items,fn)])
cur = None
def chap_key(t): return norm(re.split(r'[:/]', t)[0])
for label, lines in allp:
    items, fn = parse_page(lines)
    out = []; first3 = 0
    for it in items:
        if it[0] == 'p':
            t = it[1]
            if kind(t) == 'chap':
                key = chap_key(t)
                if key in seen:
                    t2 = re.sub(r'\s*/\s*', ': ', t)
                    for c in chapters:
                        if c['key'] == key and len(t2) > len(c['title']): c['title'] = t2
                    continue
                seen.add(key)
                title = re.sub(r'\s*/\s*', ': ', t)
                cur = dict(key=key, title=title, pages=[]); chapters.append(cur)
                out.append(('chap', title)); continue
            if cur and ':' in cur['title'] and norm(t) == norm(cur['title'].split(':', 1)[1]): continue   # subjudul terpisah
            k = kind(t)
            out.append((k, t) if k != 'p' else it); continue
        out.append(it)
    if cur is None:
        cur = dict(key='awal', title='', pages=[]); chapters.append(cur)
    cur['pages'].append((label, out, fn))

if len(chapters) > 1 and chapters[0]['key'] == 'awal':
    chapters[1]['pages'] = chapters[0]['pages'] + chapters[1]['pages']; chapters.pop(0)

# --- HTML
def hal(label):
    pdf = PDFMAP.get(label, label + OFF)
    return ('<div class="hal" id="hal-%d" data-kitab="%d"><span><i class="hal__t">Hlm. </i>%d</span>'
            '<button type="button" class="hal__pdf" data-pdf="%d" aria-label="Lihat PDF asli untuk Hlm. %d" title="Lihat PDF asli"></button></div>') % (label, label, pdf, pdf, pdf)
def ayat(t): return '<div class="ayat"><p class="ar" lang="ar">%s</p></div>' % esc(t)
def blk(t, c='blk-p'): return '<div class="blk %s">%s</div>' % (c, ayat(t))
def sy(baits): return '<div class="blk blk-sy"><div class="tag"><span class="tag__k" lang="ar">شَاهِدٌ شِعْرِيٌّ</span></div>%s</div>' % ''.join('<div class="bait"><div class="ayat">%s</div></div>' % ''.join('<p class="ar" lang="ar">%s</p>' % esc(x) for x in b) for b in baits)

T = open(tpl_f, encoding='utf-8').read().split('\n')
ol = next(i for i, l in enumerate(T) if l.startswith('<ol class="toc">'))
olend = next(i for i, l in enumerate(T) if i > ol and l.strip() == '</ol>')
h1 = next(i for i, l in enumerate(T) if l.startswith('<div class="hal" id="hal-'))
e = next(i for i, l in enumerate(T) if '</section>' in l and i > h1)
# kepala terakhir sebelum penanda pertama (mis. isi__wrap) -> pakai T[:ol] + toc + T[olend+1:h1]; ekor T[e-1:]
for ch in chapters:
    if ch['key'] == 'awal' and not ch['title']: pass
body = []; toc = []; nbab = 0; nsub = 0
chap_files = []
for ch in chapters:
    body = []; toc_subs = []; babid = None
    pg0 = ch['pages'][0][0]; pg1 = ch['pages'][-1][0]
    for label, items, fn in ch['pages']:
        body.append(hal(label)); verse = []
        def flush():
            global verse
            if verse: body.append(sy(verse)); verse = []
        for k, v in items:
            if k == 'verse': verse.append(v); continue
            flush()
            if k == 'chap':
                body.append('<header class="bab" id="bab-1"><h2 class="bab__ar" lang="ar">%s</h2></header>' % esc(v)); babid = v
            elif k == 'sub':
                nsub += 1; toc_subs.append(('sub-%d' % nsub, v, label))
                body.append('<h3 class="sub" id="sub-%d" lang="ar">%s</h3>' % (nsub, esc(v)))
            elif k == 'li': body.append(blk(v, 'blk-li'))
            else: body.append(blk(v))
        flush()
        for t in fn: body.append(blk(t))
    title = ch['title'] or 'الجزء الثاني'
    tocl = ['<ol class="toc">', '<li class="toc__bab"><details><summary><span class="toc__no">1.</span><a class="toc__ar" lang="ar" href="#bab-1">%s</a><span class="toc__meta">Hlm. %d&ndash;%d</span></summary>' % (esc(title), pg0, pg1)]
    if toc_subs:
        tocl.append('<div class="toc__sec"><ol>' + ''.join('<li><a href="#%s"><span class="toc__a" lang="ar">%s</span><span class="toc__ref">Hlm. %d</span></a></li>' % (i, esc(t), p) for i, t, p in toc_subs) + '</ol></div>')
    tocl += ['</details></li>', '</ol>']
    s = '\n'.join(T[:ol] + tocl + T[olend + 1:h1] + body + T[e - 1:])
    s = re.sub(r'<title>.*?</title>', '<title>%s — النص العربي</title>' % esc(title), s, count=1)
    s = re.sub(r'<h1 class="isi__judul"[^>]*>.*?</h1>', '<h1 class="isi__judul" lang="ar">%s</h1>' % esc(title), s, count=1)
    s = re.sub(r'<p class="isi__ket"[^>]*>.*?</p>', '<p class="isi__ket" lang="ar">عِلْمُ الْمَعَانِي · دِرَاسَةٌ بَلَاغِيَّةٌ وَنَقْدِيَّةٌ لِمَسَائِلِ الْمَعَانِي · %s · النَّصُّ الْعَرَبِيُّ فَقَطْ</p>' % esc(title), s, count=1)
    chap_files.append((title, pg0, pg1, s, len(body), len(toc_subs)))
for title, a, b, s, nb, ns in chap_files:
    fn = os.path.join(outdir, re.sub(r'[\\/:*?"<>|]', '-', title) + '.html')
    open(fn, 'w', encoding='utf-8').write(s)
    print(title, '| hlm', a, '-', b, '| blok', nb, '| sub', ns, '->', os.path.basename(fn))
