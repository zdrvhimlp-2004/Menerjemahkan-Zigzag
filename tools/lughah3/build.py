# -*- coding: utf-8 -*-
"""Bangun Ilmu Lughah 3.html: 1 baris Arab (maks. 7 kata) + 1 baris Indonesia,
dengan Fihris, Kode Warna, dan nomor halaman.

  python3 tools/lughah3/build.py          # tulis ke Data/.../Ilmu Lughah 3.html
  python3 tools/lughah3/build.py --check  # hanya periksa, tidak menulis
"""
import os, re, sys, html as H
from collections import OrderedDict
from units import load_units, HERE, MAXW
from trans import load_trans, pieces_for
from heads import HEADS, PROMOTE, FALLBACK_ID, TABLE1_HEAD, TABLE1_TOTAL, TABLE2_HEAD

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'Data', 'Data Lughoh per Semester', 'Semester 5', 'علم اللغة (3)', 'Ilmu Lughah 3.html')

PAGE_WORDS = 330      # perkiraan kata Arab per halaman
PAGE_MIN_BAB = 110    # bab baru memulai halaman baru bila halaman berjalan sudah segini
COVER_UPTO = 6        # blok 0..6 = sampul

AR2LAT = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')


def esc(s):
    return H.escape(s, quote=False)


# ------------------------------------------------------------------ Arab
def quote_flags(toks):
    flags, inq = [], False
    for w, _, _ in toks:
        start, touched, i = inq, False, 0
        while i < len(w):
            ch = w[i]
            if ch == '"':
                inq = not inq; touched = True
            elif ch == '«':
                inq = True; touched = True
            elif ch == '»':
                inq = False; touched = True
            elif w.startswith('((', i):
                inq = True; touched = True; i += 1
            elif w.startswith('))', i):
                inq = False; touched = True; i += 1
            i += 1
        flags.append(start or touched)
    return flags, inq


def render_ar(chunk, qf):
    runs = []   # (bold, q, [words])
    for (w, b, _), q in zip(chunk, qf):
        if runs and runs[-1][0] == b and runs[-1][1] == q:
            runs[-1][2].append(w)
        else:
            runs.append((b, q, [w]))
    out = []
    for b, q, ws in runs:
        t = esc(' '.join(ws))
        if q: t = '<span class="c">%s</span>' % t
        if b: t = '<strong>%s</strong>' % t
        out.append(t)
    return ' '.join(out)


# ------------------------------------------------------------- Indonesia
def wrap_quotes(raw):
    t = esc(raw)
    if raw.count('"') % 2 == 0 and raw.count('"'):
        t = re.sub(r'"([^"]+)"', lambda m: '<span class="c">"%s"</span>' % m.group(1), t)
    if raw.count('«') == raw.count('»') and raw.count('«'):
        t = re.sub(r'«([^»]*)»', lambda m: '<span class="c">«%s»</span>' % m.group(1), t)
    return t


def render_id(piece, bold_mode):
    if bold_mode == 'all':
        return '<strong>%s</strong>' % wrap_quotes(piece)
    if bold_mode == 'label' and ':' in piece:
        k = piece.index(':') + 1
        return '<strong>%s</strong>%s' % (wrap_quotes(piece[:k]), wrap_quotes(piece[k:]))
    return wrap_quotes(piece)


def bold_mode_of(chunk):
    fl = [b for _, b, _ in chunk]
    if all(fl): return 'all'
    if fl[0] and any(fl): return 'label'
    return None


def ayat(ar_html, id_html):
    return '<div class="ayat"><p class="ar" lang="ar">%s</p><p class="id" lang="id">%s</p></div>' % (ar_html, id_html)


def render_unit(r, pieces):
    qf_all, left_open = quote_flags(r['toks'])
    if left_open:
        warn('kutip Arab tak seimbang di %s' % r['uid'])
    parts, pos = [], 0
    for chunk, piece in zip(r['chunks'], pieces):
        qf = qf_all[pos:pos + len(chunk)]
        pos += len(chunk)
        parts.append(ayat(render_ar(chunk, qf), render_id(piece, bold_mode_of(chunk))))
    kind = r['kind']
    if 'bernomor' in kind:
        assert r['num'], r['uid']
        return '<div class="blk blk-li has-no"><span class="blk__no">%s</span>%s</div>' % (r['num'], ''.join(parts))
    if 'list-item' in kind:
        return '<div class="blk blk-li">%s</div>' % ''.join(parts)
    return '<div class="blk blk-p">%s</div>' % ''.join(parts)


WARN = []
def warn(m): WARN.append(m)


# ------------------------------------------------------------------ tabel
def cell(ar, idt):
    return '<div class="sel" role="cell">%s</div>' % ayat(esc(ar), esc(idt)) if (ar or idt) else '<div class="sel" role="cell"></div>'


def table1(rows):
    out = ['<div class="jadwal" role="table">']
    h = TABLE1_HEAD
    out.append('<div class="sat" role="row"><div class="sel sel--kepala" role="cell">%s</div><div class="sel sel--kepala" role="cell">%s</div><div class="sel sel--kepala" role="cell">%s</div></div>' % (
        ayat(esc(h[0]), esc(h[1])), ayat(esc(h[2]), esc(h[3])), ayat(esc(h[4]), esc(h[5]))))
    for row in rows[1:]:
        no, ar, idt, hrs = row[0][1], row[1][1], row[2][1], row[3][1]
        total = not no
        cls = 'sel sel--total' if total else 'sel'
        if total:
            ar, idt = TABLE1_TOTAL
        out.append('<div class="sat" role="row"><div class="%s" role="cell">%s</div><div class="%s" role="cell">%s</div><div class="%s" role="cell">%s</div></div>' % (
            cls, ayat(esc(no), esc(no.translate(AR2LAT))) if no else '',
            cls, ayat(esc(ar), esc(idt)),
            cls, ayat(esc(hrs), esc(hrs.translate(AR2LAT)))))
    out.append('</div>')
    return ''.join(out)


def table2(rows):
    h = TABLE2_HEAD
    out = ['<div class="jadwal" role="table">']
    out.append('<div class="sat sat--2" role="row"><div class="sel sel--kepala" role="cell">%s</div><div class="sel sel--kepala" role="cell">%s</div></div>' % (
        ayat(esc(h[0]), esc(h[1])), ayat(esc(h[2]), 'Bunyi &mdash; Sifat-sifat (diisi pelajar)')))
    for row in rows[1:]:
        snd, no = row[0][1], row[2][1]
        out.append('<div class="sat sat--2" role="row"><div class="sel" role="cell">%s</div><div class="sel" role="cell">%s</div></div>' % (
            ayat(esc(no), esc(no.translate(AR2LAT))), ayat(esc(snd), 'Sifat-sifat: &hellip;')))
    out.append('</div>')
    return ''.join(out)


# ------------------------------------------------------------------ susun
def main():
    check_only = '--check' in sys.argv
    blocks, res = load_units()
    trans = load_trans()
    by_bi = OrderedDict()
    for r in res:
        by_bi.setdefault(r['bi'], []).append(r)

    items = []   # dict(type, words, ...)
    lines = 0
    for bi, b in enumerate(blocks):
        if b[0] in ('H2', 'H3'):
            level = 2 if (b[0] == 'H2' or bi in PROMOTE) else 3
            hid = b[1] if b[0] == 'H2' else (b[2] or FALLBACK_ID.get(bi) or 'sub-%d' % bi)
            ar = b[2] if b[0] == 'H2' else b[1]
            items.append({'type': 'head', 'level': level, 'id': hid, 'ar': ar, 'idt': HEADS[bi], 'words': 0, 'bi': bi})
        elif b[0] == 'TABLE':
            items.append({'type': 'table', 'rows': b[1], 'words': 60, 'bi': bi})
        else:
            for r in by_bi[bi]:
                p = pieces_for(r, trans)
                assert p is not None and len(p) == len(r['chunks']), r['uid']
                lines += len(r['chunks'])
                items.append({'type': 'unit', 'r': r, 'p': p, 'words': sum(len(c) for c in r['chunks']), 'bi': bi})

    # sampul = unit blok 0..COVER_UPTO
    cover = [it for it in items if it['type'] == 'unit' and it['bi'] <= COVER_UPTO]
    items = [it for it in items if not (it['type'] == 'unit' and it['bi'] <= COVER_UPTO)]
    items.insert(0, {'type': 'cover', 'units': cover, 'words': sum(c['words'] for c in cover)})

    # ---- halaman
    page, cur, prev_head = 1, 0, False
    for it in items:
        brk = False
        if it['type'] == 'head' and it['level'] == 2 and cur >= PAGE_MIN_BAB: brk = True
        elif it['type'] != 'head' and not prev_head and cur >= PAGE_WORDS: brk = True
        elif it['type'] == 'head' and it['level'] == 3 and cur >= PAGE_WORDS: brk = True
        if brk and it is not items[0]:
            page += 1; cur = 0
            it['newpage'] = page
        it['page'] = page
        cur += it['words']
        prev_head = it['type'] == 'head'
    npage = page

    # ---- fihris
    babs, nsub = [], 0
    for it in items:
        if it['type'] != 'head': continue
        if it['level'] == 2:
            babs.append({'id': it['id'], 'ar': it['ar'], 'idt': it['idt'], 'page': it['page'], 'subs': []})
        else:
            babs[-1]['subs'].append({'id': it['id'], 'ar': it['ar'], 'idt': it['idt'], 'page': it['page']}); nsub += 1
    ids = [x['id'] for x in babs] + [s['id'] for x in babs for s in x['subs']]
    assert len(ids) == len(set(ids)), 'id ganda'

    toc = ['<ol class="toc">']
    for n, bb in enumerate(babs, 1):
        toc.append('<li class="toc__bab"><details><summary><span class="toc__no">%d.</span><a class="toc__ar" lang="ar" href="#%s">%s</a><span class="toc__id">%s</span><span class="toc__meta">Hlm. %d%s</span></summary>' % (
            n, bb['id'], esc(bb['ar']), esc(bb['idt']), bb['page'], (' &middot; %d sub-bab' % len(bb['subs'])) if bb['subs'] else ''))
        if bb['subs']:
            toc.append('<div class="toc__sec"><ol>' + ''.join(
                '<li><a href="#%s"><span class="toc__t">%s</span><span class="toc__a" lang="ar">%s</span><span class="toc__ref">Hlm. %d</span></a></li>' % (
                    s['id'], esc(s['idt']), esc(s['ar']), s['page']) for s in bb['subs']) + '</ol></div>')
        toc.append('</details></li>')
    toc.append('</ol>')

    # ---- badan
    body = []
    babno = 0
    for it in items:
        if 'newpage' in it or it is items[0]:
            n = it.get('newpage', 1)
            body.append('<div class="hal" id="hal-%d"><span>Hlm. %d</span></div>' % (n, n))
        t = it['type']
        if t == 'cover':
            body.append('<div class="cover">' + ''.join(
                ayat(*(lambda r, p: (render_ar(r['chunks'][0], quote_flags(r['toks'])[0]), render_id(p[0], bold_mode_of(r['chunks'][0]))))(c['r'], c['p']))
                for c in it['units']) + '</div>')
        elif t == 'head':
            if it['level'] == 2:
                babno += 1
                body.append('<header class="bab" id="%s"><h2 class="bab__ar" lang="ar">%s</h2><p class="bab__id">Bab %d &middot; %s</p></header>' % (
                    it['id'], esc(it['ar']), babno, esc(it['idt'])))
            else:
                body.append('<h3 class="sub" id="%s" lang="ar">%s</h3><p class="sub__id">%s</p>' % (it['id'], esc(it['ar']), esc(it['idt'])))
        elif t == 'table':
            body.append(table1(it['rows']) if it['rows'][0][0][1] == 'م' and len(it['rows'][0]) == 4 else table2(it['rows']))
        else:
            body.append(render_unit(it['r'], it['p']))

    ket = ("Mata Kuliah 'Ilm al-Lughah (Linguistik) 3 &middot; Jurusan Bahasa Arab, Ma'had al-'Ulum al-Islamiyyah wa al-'Arabiyyah Indonesia &middot; "
           "Dosen: Dr. Ath-Thahir Ath-Thayyib Ath-Thahir &middot; %d bab &middot; %d sub-bab &middot; %d baris &middot; %d halaman (penomoran halaman dokumen ini) &middot; Terjemah biasa &middot; "
           "1 baris Arab (maks. %d kata) + 1 baris Indonesia" % (len(babs), nsub, lines, npage, MAXW))

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
    head = open(os.path.join(HERE, 'template_head.html'), encoding='utf8').read().replace('{{TITLE}}', 'علم اللغة ٣ — Terjemah Biasa')
    tail = open(os.path.join(HERE, 'template_tail.html'), encoding='utf8').read()
    doc = (head + '<body>\n\n<div id="crumb-bar" class="crumb" aria-hidden="true">\n  <span class="crumb__path"></span>\n  <span class="crumb__page"></span>\n</div>\n\n'
           '<section class="isi">\n  <div class="isi__wrap">\n'
           '    <h1 class="isi__judul">عِلْمُ اللُّغَةِ ٣: عِلْمُ الْأَصْوَاتِ</h1>\n'
           '    <p class="isi__ket">' + ket + '</p>\n\n' + legend + fihris + '\n' + '\n'.join(body) + '\n  </div>\n</section>\n\n' + tail)

    # ---- ringkasan pemeriksaan
    mx = max(len(c) for it in items if it['type'] == 'unit' for c in it['r']['chunks'])
    print('bab %d, sub-bab %d, baris %d, halaman %d, kata Arab maks/baris %d' % (len(babs), nsub, lines, npage, mx))
    for w in WARN: print('PERINGATAN:', w)
    assert mx <= MAXW
    if check_only: return
    open(OUT, 'w', encoding='utf8').write(doc)
    print('tulis', OUT, len(doc))


if __name__ == '__main__':
    main()
