# -*- coding: utf-8 -*-
"""Bangun halaman HTML terjemah biasa Ilmu Ma'ani (Fasal 1, hlm. 41-96):
1 baris Arab (maks. 7 kata, berharakat) + 1 baris Indonesia, dengan Fihris, Kode Warna, dan nomor halaman.

  python3 tools/maani-fasal1/build.py          # tulis HTML
  python3 tools/maani-fasal1/build.py --check  # hanya periksa (maks 7 kata, cakupan harakat)

Data: tools/maani-fasal1/data.txt
  @bab id|arab|indonesia|hlm        judul bab (h2)
  @sub id|arab|indonesia|hlm        judul sub-bab (h3)
  @hal N                            penanda halaman
  ARAB|INDONESIA                    satu baris terjemah (Arab maks. 7 kata)
  -ARAB|INDONESIA                   baris poin (daftar butir)
  *ARAB|INDONESIA                   baris tebal (judul butir/istilah)
  Kutipan dalam "..." otomatis diberi warna contoh/kutipan.
"""
import os, re, sys, html as H
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
LUG = os.path.join(ROOT, 'tools', 'lughah3')
OUT = os.path.join(ROOT, 'Data', 'Data Lughoh per Semester', 'Semester 5', 'البلاغة (5)', 'Kitab Ilmu Al Maani (Fasal 1 Isnad Khabari)(Hlm 41-96).html')
MAXW = 7
HAR = re.compile('[ً-ْٰ]')
esc = lambda s: H.escape(s, quote=False)

def words(ar): return [w for w in ar.split() if re.search('[ء-ي]', w)]
def har_cover(ar):
    ws = words(ar); letters = re.findall('[ء-ي]', ar)
    return (len(HAR.findall(ar)) / max(1, len(letters)))

def wrap_q(t):
    t = esc(t)
    return re.sub(r'(&quot;|")([^"]+?)\1', lambda m: '<span class="c">"%s"</span>' % m.group(2), t) if t.count('"') % 2 == 0 and t.count('"') else t

def line(kind, ar, idn):
    cls = 'ayat list-item' if kind == '-' else 'ayat'
    a = esc(ar); i = esc(idn)
    if kind == '*': a = '<strong>%s</strong>' % a; i = '<strong>%s</strong>' % i
    if ar.count('"') % 2 == 0 and ar.count('"'):
        a = re.sub(r'"([^"]+)"', lambda m: '<span class="c">"%s"</span>' % m.group(1), a)
    if idn.count('"') % 2 == 0 and idn.count('"'):
        i = re.sub(r'"([^"]+)"', lambda m: '<span class="c">"%s"</span>' % m.group(1), i)
    return '<div class="%s"><p class="ar" lang="ar">%s</p><p class="id" lang="id">%s</p></div>' % (cls, a, i)

def main():
    check = '--check' in sys.argv
    items = []; nlines = 0; warn = []
    for n, raw in enumerate(open(os.path.join(HERE, 'data.txt'), encoding='utf8'), 1):
        s = raw.rstrip('\n')
        if not s.strip() or s.startswith('#'): continue
        if s.startswith('@hal '): items.append(('hal', int(s[5:]))); continue
        if s[:5] in ('@bab ', '@sub '):
            i, ar, idn, hal = [x.strip() for x in s[5:].split('|')]
            items.append((s[1:4], i, ar, idn, int(hal))); continue
        kind = s[0] if s[0] in '-*' else ''
        ar, _, idn = (s[1:] if kind else s).partition('|')
        ar, idn = ar.strip(), idn.strip()
        w = len(words(ar))
        if w > MAXW: warn.append('baris %d: %d kata Arab (maks %d): %s' % (n, w, MAXW, ar[:40]))
        if har_cover(ar) < 0.6: warn.append('baris %d: harakat kurang (%.0f%%): %s' % (n, har_cover(ar) * 100, ar[:40]))
        if not idn: warn.append('baris %d: terjemah Indonesia kosong' % n)
        items.append(('ln', kind, ar, idn)); nlines += 1
    pages = [x[1] for x in items if x[0] == 'hal']
    babs = []
    for x in items:
        if x[0] == 'bab': babs.append({'id': x[1], 'ar': x[2], 'idt': x[3], 'page': x[4], 'subs': []})
        elif x[0] == 'sub': babs[-1]['subs'].append({'id': x[1], 'ar': x[2], 'idt': x[3], 'page': x[4]})
    ids = [b['id'] for b in babs] + [s['id'] for b in babs for s in b['subs']]
    assert len(ids) == len(set(ids)), 'id ganda'
    nsub = sum(len(b['subs']) for b in babs)
    print('bab %d, sub-bab %d, baris %d, halaman %d (hlm. %d-%d)' % (len(babs), nsub, nlines, len(pages), min(pages), max(pages)))
    for w in warn: print('PERINGATAN:', w)
    if check: return
    # fihris
    toc = ['<ol class="toc">']
    for n, bb in enumerate(babs, 1):
        toc.append('<li class="toc__bab"><details><summary><span class="toc__no">%d.</span><a class="toc__ar" lang="ar" href="#%s">%s</a><span class="toc__id">%s</span><span class="toc__meta">Hlm. %d%s</span></summary>' % (
            n, bb['id'], esc(bb['ar']), esc(bb['idt']), bb['page'], (' &middot; %d sub-bab' % len(bb['subs'])) if bb['subs'] else ''))
        if bb['subs']:
            toc.append('<div class="toc__sec"><ol>' + ''.join('<li><a href="#%s"><span class="toc__t">%s</span><span class="toc__a" lang="ar">%s</span><span class="toc__ref">Hlm. %d</span></a></li>' % (
                s['id'], esc(s['idt']), esc(s['ar']), s['page']) for s in bb['subs']) + '</ol></div>')
        toc.append('</details></li>')
    toc.append('</ol>')
    # badan
    body = []; babno = 0; cur = None; has = {}
    for i, x in enumerate(items):
        if x[0] == 'hal': cur = x[1]; has[cur] = 0
        elif x[0] == 'ln': has[cur] += 1
    for x in items:
        if x[0] == 'hal':
            body.append('<div class="hal" id="hal-%d"><span>Hlm. %d</span></div>' % (x[1], x[1]))
            if not has[x[1]]: body.append('<p class="belum" lang="id">Terjemah hlm. %d belum diisi.</p>' % x[1])
        elif x[0] == 'bab':
            babno += 1
            body.append('<header class="bab" id="%s"><h2 class="bab__ar" lang="ar">%s</h2><p class="bab__id">Bab %d &middot; %s</p></header>' % (x[1], esc(x[2]), babno, esc(x[3])))
        elif x[0] == 'sub':
            body.append('<h3 class="sub" id="%s" lang="ar">%s</h3><p class="sub__id">%s</p>' % (x[1], esc(x[2]), esc(x[3])))
        else:
            body.append(line(x[1], x[2], x[3]))
    legend = '''    <dialog id="legend-modal" class="modal" aria-label="Kode Warna">
      <button type="button" class="modal__close" data-close aria-label="Tutup">&times;</button>
      <section class="legend" aria-label="Kode warna">
        <h2 class="legend__judul">Kode Warna</h2>
        <ul>
          <li><span class="sw sw--isi" lang="ar">الشَّرْحُ</span> Isi &mdash; penjelasan dan uraian materi</li>
          <li><span class="sw sw--pt" lang="ar">نُقْطَةٌ</span> Poin &mdash; daftar butir, tujuan, dan contoh bernomor/berhuruf</li>
          <li><span class="sw sw--isi" lang="ar"><strong>عُنْوَانٌ</strong></span> Tulisan tebal &mdash; judul butir atau istilah yang sedang dijelaskan</li>
          <li><span class="sw c" lang="ar">مِثَالٌ</span> Contoh, istilah, dan kutipan (dalam tanda kutip)</li>
        </ul>
      </section>
    </dialog>
'''
    fihris = '''    <dialog id="fihris-modal" class="modal modal--wide" aria-label="Fihris (Daftar Isi)">
      <button type="button" class="modal__close" data-close aria-label="Tutup">&times;</button>
      <nav class="daftar-isi" id="fihris" aria-label="Fihris">
        <div class="daftar-isi__head">
          <h2 class="daftar-isi__judul">Fihris (Daftar Isi) <span lang="ar">الْفِهْرِسُ</span></h2>
          <button type="button" class="toc__btn" id="toc-toggle" data-open="0">Buka semua</button>
        </div>
''' + '\n'.join(toc) + '''
      </nav>
    </dialog>
'''
    head = open(os.path.join(LUG, 'template_head.html'), encoding='utf8').read().replace('{{TITLE}}', 'أحوال الإسناد الخبري — Terjemah Biasa')
    head = head.replace('</style>', '  .belum { direction: ltr; text-align: center; font-size: 0.8rem; color: var(--muted); font-style: italic; padding: 0.4rem 0; }\n</style>', 1)
    tail = open(os.path.join(LUG, 'template_tail.html'), encoding='utf8').read()
    ket = "'Ilm al-Ma'ani &middot; Ilmu Ma'ani dan Fasal 1: Keadaan Isnad Khabari &middot; hlm. %d&ndash;%d &middot; %d baris terisi &middot; Terjemah biasa &middot; 1 baris Arab (maks. %d kata) + 1 baris Indonesia" % (min(pages), max(pages), nlines, MAXW)
    doc = (head + '<body>\n\n<div id="crumb-bar" class="crumb" aria-hidden="true">\n  <span class="crumb__path"></span>\n  <span class="crumb__page"></span>\n</div>\n\n'
           '<section class="isi">\n  <div class="isi__wrap">\n    <h1 class="isi__judul">أَحْوَالُ الْإِسْنَادِ الْخَبَرِيِّ</h1>\n    <p class="isi__ket">' + ket + '</p>\n\n' + legend + fihris + '\n' + '\n'.join(body) + '\n  </div>\n</section>\n\n' + tail)
    open(OUT, 'w', encoding='utf8').write(doc)
    print('tulis', OUT, len(doc))

if __name__ == '__main__': main()
