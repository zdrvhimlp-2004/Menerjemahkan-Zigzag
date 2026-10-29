import re, json, sys, html, subprocess, os
from build2 import *
import build2
from render_align import render_page, fidelity, flag
from prep import strip_page_a

REPO = '/home/user/Menerjemahkan-Zigzag/'
TEMPLATE = REPO + 'Data/Data Lughoh per Semester/Semester 5/النحو (5)/Kitab Syarh Ibnu Aqil (Bab Al Idlofah-Afal At Tafdhil).html'
OUTDIR = REPO + 'Data/Data Lughoh per Semester/Semester 5/البلاغة (5)/'
esc = lambda s: html.escape(s, quote=False)

CFG = {
 'a': dict(out="Kitab Ilmu Al Maani (Hlm 209-237)(Bag 4).html", title='علم المعاني - دراسة بلاغية ونقدية لمسائل المعاني',
           ket="Dari file: &laquo;&#x639;&#x644;&#x645; &#x627;&#x644;&#x645;&#x639;&#x627;&#x646;&#x64a; - &#x62f;&#x631;&#x627;&#x633;&#x629; &#x628;&#x644;&#x627;&#x63a;&#x64a;&#x629; &#x648;&#x646;&#x642;&#x62f;&#x64a;&#x629; &#x644;&#x645;&#x633;&#x627;&#x626;&#x644; &#x627;&#x644;&#x645;&#x639;&#x627;&#x646;&#x64a; Halaman 209 - 260&raquo; &middot; Hlm. 209&ndash;260 &middot; Terjemah biasa &middot; 1 baris Arab + 1 baris Indonesia, maksimal 7 kata Arab per baris &middot; teks Arab = transkrip sumber apa adanya; tanda &#9888; = ada masalah di teks sumber",
           start=('', 'Bagian awal (sebelum judul pasal pertama di file ini)')),
}

def load_tr(tag):
    tr = {}
    for l in open(SP + 'trans_%s.txt' % tag, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l.strip(): continue
        k, _, v = l.partition('|'); tr[k] = v
    return tr

def build_sequence(tag):
    hp = SP + 'heads_%s.json' % tag
    heads = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    build2.FIXES.extend(heads.pop('_fix', []))
    seq = build_a(heads) if tag == 'a' else build_b(heads)
    return number(seq, tag)

def ref_html(ref):
    return ref

def assemble(tag, lo=None, hi=None, out=None):
    cfg = CFG[tag]
    tr = load_tr(tag)
    pages = build_sequence(tag)
    if lo: pages = [(n, us) for n, us in pages if lo <= n <= hi]
    babs = []          # {'id','ar','id_','pg','subs':[], 'syahid':[]}
    body = []
    cnt = {'q': 0, 'sy': 0, 'sub': 0, 'bab': 0}
    cur_bab = None
    def new_bab(ar, idn, pg, ar_html=None):
        nonlocal cur_bab
        cnt['bab'] += 1
        cur_bab = {'n': cnt['bab'], 'ar': ar, 'id': idn, 'pg': pg, 'pg2': pg, 'subs': [], 'syahid': []}
        babs.append(cur_bab)
        if ar:
            body.append('<header class="bab" id="bab-%d"><h2 class="bab__ar" lang="ar">%s</h2><p class="bab__id">%s</p></header>' % (cnt['bab'], ar_html or esc(ar), esc(idn)))
        else:
            body.append('<div id="bab-%d"></div>' % cnt['bab'])
    first_page = pages[0][0]
    last_page = pages[-1][0]
    cfg = dict(cfg, ket=cfg['ket'].replace('209&ndash;260', '%d&ndash;%d' % (first_page, last_page)))
    if cfg['start'] and not (pages[0][1] and pages[0][1][0]['k'] == 'h1'):
        new_bab('', cfg['start'][1], first_page)
    open_p = False
    def close_p():
        nonlocal open_p
        if open_p: body.append('</div>'); open_p = False
    def line(i, ar, extra_ar='', extra_id='', cls='ayat'):
        t = tr.get(i)
        if t is None: raise SystemExit('belum diterjemahkan: ' + i)
        return '<div class="%s"><p class="ar" lang="ar">%s%s</p><p class="id" lang="id">%s%s</p></div>' % (cls, R[i][0], extra_ar, esc(t), extra_id)
    srcpages = dict((n_, t_) for n_, t_ in json.load(open(SP + ('a_pages.json' if tag == 'a' else 'b_pages.json'), encoding='utf-8')))
    fid_bad = []
    flags_total = 0
    for n, us in pages:
        cur_bab and cur_bab.update(pg2=n)
        S, _cnt = strip_page_a(srcpages[n], n)
        flat_ids, flat_txt = [], []
        for u in us:
            for j_, (i_, l_) in enumerate(zip(u['ids'], u['lines'])):
                t_ = l_
                if u['k'] == 'q' and u['ref'] and j_ == len(u['ids']) - 1:
                    t_ = l_ + '\x05' + re.sub(r'\s+', ' ', u['ref'])
                flat_ids.append(i_); flat_txt.append(t_)
        rr = render_page(S, flat_txt)
        R = {i_: r_ for i_, r_ in zip(flat_ids, rr)}
        okf, A_, B_ = fidelity(S, [r_[1].replace('\x05', '') for r_ in rr])
        if not okf: fid_bad.append(n)
        flags_total += sum(r_[2] for r_ in rr)
        for u in us:
            k = u['k']
            if k != 'p': close_p()
            if k == 'h1':
                new_bab(R[u['ids'][0]][1].replace('\x05', ''), tr[u['ids'][0]], n, ar_html=R[u['ids'][0]][0])
            elif k == 'h2':
                cnt['sub'] += 1
                if cur_bab is None: new_bab('', cfg['start'][1], n)
                cur_bab['subs'].append((cnt['sub'], R[u['ids'][0]][1].replace('\x05', ''), tr[u['ids'][0]], n))
                body.append('<h3 class="sub" id="sub-%d" lang="ar">%s</h3><p class="sub__id">%s</p>' % (cnt['sub'], R[u['ids'][0]][0], esc(tr[u['ids'][0]])))
            elif k == 'p':
                if not open_p: body.append('<div class="blk blk-p">'); open_p = True
                for i, l in zip(u['ids'], u['lines']): body.append(line(i, l))
            elif k == 'q':
                cnt['q'] += 1; qid = 'qs-%d' % cnt['q']
                body.append('<div class="blk blk-q" id="%s">' % qid)
                lastp = R[u['ids'][-1]][1]
                refp = lastp.split('\x05')[1].strip() if '\x05' in lastp else ''
                rid = ref_id(refp)[0] if refp else ''
                firstp = R[u['ids'][0]][1].strip()
                verse_last = lastp.split('\x05')[0].strip()
                op_ = firstp[:1]; cl_ = verse_last[-1:]
                bad_br = not ((op_ == '\ufd3f' and cl_ == '\ufd3e') or (op_ == '(' and cl_ == ')') or (op_ == '[' and cl_ == ']'))
                for j, (i, l) in enumerate(zip(u['ids'], u['lines'])):
                    last = j == len(u['ids']) - 1
                    ei = (' <span class="ref">(%s)</span>' % esc(rid)) if (last and rid) else ''
                    if last and bad_br:
                        # sisipkan tanda sebelum rujukan
                        h_ = R[i][0]
                        h_ = h_.replace('<span class="ref">', flag('kurung') + '<span class="ref">', 1) if '<span class="ref">' in h_ else h_ + flag('kurung')
                        R[i] = (h_, R[i][1], R[i][2] + 1)
                    body.append(line(i, l, '', ei, 'ayat rq'))
                body.append('</div>')
                if cur_bab is not None:
                    cur_bab['syahid'].append(('q', qid, verse_last.strip('\ufd3f\ufd3e()[] '), rid))
            elif k == 'sy':
                cnt['sy'] += 1; sid = 'sy-%d' % cnt['sy']
                body.append('<div class="blk blk-sy" id="%s"><div class="tag"><span class="tag__k" lang="ar">شَاهِدٌ شِعْرِيٌّ</span><span class="tag__t">Syair</span></div>' % sid)
                ls = list(zip(u['ids'], u['lines']))
                for a in range(0, len(ls), 2):
                    body.append('<div class="bait">' + ''.join(line(i, l) for i, l in ls[a:a + 2]) + '</div>')
                body.append('</div>')
                if cur_bab is not None:
                    cur_bab['syahid'].append(('sy', sid, R[u['ids'][0]][1], ''))
            elif k == 'fn':
                body.append('<div class="blk blk-fn">')
                for i, l in zip(u['ids'], u['lines']): body.append(line(i, l, cls='ayat fn'))
                body.append('</div>')
        close_p()
        body.append('<div class="hal" id="hal-%d"><span>Hlm. %d</span></div>' % (n, n))

    print('halaman dengan teks berbeda dari sumber:', fid_bad, '| jumlah tanda:', flags_total)
    # ---- Fihris
    def short(t, k=7):
        w = t.split(); return ' '.join(w[:k]) + (' …' if len(w) > k else '')
    fih = []
    for b in babs:
        subs = ''.join('<li><a href="#sub-%d"><span class="toc__t">%s</span><span class="toc__a" lang="ar">%s</span></a></li>\n' % (s[0], esc(s[2]), esc(s[1])) for s in b['subs'])
        sy = []
        for kind, sid, txt, ref in b['syahid']:
            if kind == 'q':
                sy.append('<li><a href="#%s"><span class="chip chip--q">Al-Qur\'an</span><span class="toc__a" lang="ar">&#xFD3F;%s&#xFD3E;</span><span class="toc__ref">%s</span></a></li>' % (sid, esc(short(txt, 9)), esc(ref)))
            else:
                sy.append('<li><a href="#%s"><span class="chip chip--sy">Syair</span><span class="toc__a" lang="ar">%s</span></a></li>' % (sid, esc(short(txt))))
        meta = 'Hlm. %d&ndash;%d &middot; %d sub-bab &middot; %d syahid' % (b['pg'], b['pg2'], len(b['subs']), len(b['syahid']))
        fih.append('<li class="toc__bab"><details>\n<summary><span class="toc__no">%d.</span><a class="toc__ar" lang="ar" href="#bab-%d">%s</a><span class="toc__id">%s</span><span class="toc__meta">%s</span></summary>\n%s%s</details></li>\n' % (
            b['n'], b['n'], esc(b['ar']), esc(b['id']), meta,
            ('<div class="toc__sec"><h4>Sub-bab <small>(%d)</small></h4><ol>\n%s</ol></div>\n' % (len(b['subs']), subs)) if b['subs'] else '',
            ('<div class="toc__sec"><h4>Syahid <small>(%d)</small></h4><ul class="toc__sy">\n%s\n</ul></div>\n' % (len(b['syahid']), '\n'.join(sy))) if sy else ''))

    # ---- rakit dari template
    tpl = open(TEMPLATE, encoding='utf-8').read()
    head = tpl[:tpl.index('<body>')]
    head = re.sub(r'<title>.*?</title>', '<title>%s — Terjemah Biasa</title>' % esc(cfg['title']), head, count=1)
    css = """
  .ayat.rq .ar { color: var(--q); }
  .ayat.rq .id { color: var(--ar-color); opacity: 0.85; }
  .blk-q { margin: 0.6rem 0; }
  .blk-fn { border-right: 3px solid var(--muted); padding: 0 clamp(0.6rem, 2vw, 1rem); margin: 0.9rem 0; opacity: 0.9; }
  .blk-fn .ayat .ar { font-size: 0.85em; color: var(--muted); }
  .blk-fn .ayat .id { font-size: 0.85em; }
  .blk-sy .ayat .ar { color: var(--sy-ink); }
  .blk-sy .ayat .id { color: var(--sy-id); }
  .blk-sy .bait { padding: 0.15rem 0 0.25rem; }
  .blk-sy .bait + .bait { margin-top: 0.45rem; }\n  mark.tanda { background: none; color: #c0392b; font-size: 0.75em; margin: 0 0.15em; cursor: help; }\n"""
    head = head.replace('</style>', css + '</style>', 1)
    legend = ('<li><span class="sw sw--isi" lang="ar">الشَّرْحُ</span> Isi &mdash; penjelasan penulis</li>\n'
              '          <li><span class="sw q" lang="ar">﴿آيَةٌ﴾</span> Ayat Al-Qur&rsquo;an (lengkap dengan nama surat dan nomor ayat)</li>\n'
              '          <li><span class="sw sw--sy" lang="ar">شَاهِدٌ</span> Syahid syair &mdash; bait atau sebagian bait</li>\n'
              '          <li><span class="sw" lang="ar" style="opacity:.8">حَاشِيَةٌ</span> Catatan kaki</li>\n'
              '          <li><span class="sw" style="color:#c0392b">&#9888;</span> Ada masalah di teks sumber (kata menempel, tanda kurung atau rujukan ayat tidak lengkap, dsb.). Teks Arab tetap ditampilkan apa adanya; arahkan kursor ke tanda untuk penjelasan.</li>\n')
    toc_head = '''    <dialog id="legend-modal" class="modal" aria-label="Kode Warna">
      <button type="button" class="modal__close" data-close aria-label="Tutup">&times;</button>
      <section class="legend" aria-label="Kode warna">
        <h2 class="legend__judul">Kode Warna</h2>
        <ul>
          %s        </ul>
      </section>
    </dialog>
''' % legend
    fm = ('    <dialog id="fihris-modal" class="modal" aria-label="Fihris (Daftar Isi)">\n'
          '      <button type="button" class="modal__close" data-close aria-label="Tutup">&times;</button>\n'
          '      <nav class="daftar-isi" id="fihris" aria-label="Fihris">\n'
          '        <div class="daftar-isi__head">\n'
          '          <h2 class="daftar-isi__judul">Fihris (Daftar Isi) <span lang="ar">الْفِهْرِسُ</span></h2>\n'
          '          <button type="button" class="toc__btn" id="toc-toggle" data-open="0">Buka semua</button>\n'
          '        </div>\n'
          '        <ol class="toc">\n' + ''.join(fih) + '        </ol>\n'
          '      </nav>\n'
          '    </dialog>')
    body_html = '\n'.join(body)
    tail = tpl[tpl.rindex('</section>'):]
    doc = head + '<body>\n\n<div id="crumb-bar" class="crumb" aria-hidden="true">\n  <span class="crumb__path"></span>\n  <span class="crumb__page"></span>\n</div>\n\n<section class="isi">\n  <div class="isi__wrap">\n' \
          + '    <h1 class="isi__judul" lang="ar">%s</h1>\n    <p class="isi__ket">%s</p>\n\n' % (esc(cfg['title']), cfg['ket']) + toc_head + fm + '\n\n' + body_html + '\n\n  </div>\n' + tail
    path = out or (OUTDIR + cfg['out'])
    open(path, 'w', encoding='utf-8').write(doc)
    print('ok', path, len(doc), 'baris', sum(len(u['ids']) for _, us in pages for u in us), cnt)

if __name__ == '__main__':
    tag = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else None
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else None
    assemble(tag, lo, hi, out=sys.argv[4] if len(sys.argv) > 4 else None)
