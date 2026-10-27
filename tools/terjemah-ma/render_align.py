"""Render teks Arab apa adanya dari sumber.

Baris-baris hasil pemrosesan (T) dibandingkan huruf-demi-huruf dengan teks sumber halaman (S).
- huruf yang hanya ada di T (ditambahkan oleh perapian saya)  -> dibuang + tanda peringatan
- huruf yang berbeda (diganti)                                -> ditampilkan huruf sumber + tanda
- huruf sumber yang tidak ada di T                            -> dikembalikan (tanpa tanda bila hanya tanda baca/kurung)
- dua huruf yang menempel di sumber tetapi dipisah spasi/baris di T -> tanda 'kata menempel'
Spasi tidak dianggap bagian teks.
"""
import re, html, difflib

LET = re.compile('[ء-يً-ْٰ٠-٩۰-۹]')
FN_MARK = re.compile(r'^\(\s*[0-9۰-۹٠-٩]\s*\)$')
MARK = {
    'tambah': 'Masalah di sumber: teks aslinya tidak memuat tanda/huruf di sini (mis. kurung ayat hilang, harakat tidak ada); ditampilkan apa adanya.',
    'beda': 'Masalah di sumber: teks sumber berbeda dari yang diharapkan; ditampilkan apa adanya.',
    'hilang': 'Masalah di sumber: ada teks yang tidak cocok dengan pola susunan (mis. judul halaman atau tanda yang menempel di tengah teks); ditampilkan apa adanya.',
    'menempel': 'Masalah di sumber: dua kata menempel (tanpa spasi) di teks aslinya.',
    'kurung': 'Masalah di sumber: tanda kurung ayat atau rujukan ayat tidak lengkap/tidak serasi.',
}
def flag(kind, extra=''):
    return '<mark class="tanda" title="%s">&#9888;</mark>' % html.escape(MARK[kind] + extra, quote=True)

def esc(s): return html.escape(s, quote=False)

def render_page(S, lines):
    """S: teks sumber halaman (str). lines: list of str (T). Kembalikan list (html, plain, flags) per baris."""
    # --- susun array huruf non-spasi
    Sch, Sidx = [], []
    for i, ch in enumerate(S):
        if not ch.isspace():
            Sch.append(ch); Sidx.append(i)
    Tch, Tpos = [], []
    for li, line in enumerate(lines):
        for k, ch in enumerate(line):
            if ch.isspace() or ch == '\x05':
                continue
            Tch.append(ch); Tpos.append((li, k))
    sm = difflib.SequenceMatcher(None, Tch, Sch, autojunk=False)
    nT = len(Tch)
    smap = [None] * nT                 # indeks S untuk huruf T yang sama
    tonly_first = {}                   # t pertama blok -> teks S pengganti ('' bila hanya hapus)
    tonly_skip = set()
    sonly = {}                         # posisi T -> list teks S yang hilang di T
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for d in range(i2 - i1): smap[i1 + d] = j1 + d
        elif tag in ('replace', 'delete'):
            tonly_first[i1] = ''.join(Sch[j1:j2]) if tag == 'replace' else ''
            for t in range(i1 + 1, i2): tonly_skip.add(t)
            tonly_first[i1] = (''.join(Sch[j1:j2]), tag)
        elif tag == 'insert':
            sonly.setdefault(i1, []).append(''.join(Sch[j1:j2]))
    # --- render
    out = [[] for _ in lines]          # potongan html per baris
    plain = [[] for _ in lines]
    nflag = [0] * len(lines)
    in_ref = [False] * len(lines)
    def emit(li, htm, pl=''):
        out[li].append(htm); plain[li].append(pl)
        if pl and not pl.isspace(): since[li] += len(pl)
    since = [99] * len(lines)           # jumlah huruf sejak tanda terakhir di baris
    def add_flag(li, kind):
        if since[li] <= 3: return
        out[li].append(flag(kind)); nflag[li] += 1; since[li] = 0
    # peta t -> (li,k) dan akhir baris
    t_by_line = {}
    for t, (li, k) in enumerate(Tpos): t_by_line.setdefault(li, []).append(t)
    first_t = {li: ts[0] for li, ts in t_by_line.items()}
    flagged_boundary = set()
    for li, line in enumerate(lines):
        pending_ref = False
        # S-only sebelum huruf pertama baris ini
        t0 = first_t.get(li)
        if t0 is not None and t0 in sonly:
            keep = []
            for blk in sonly[t0]:
                if FN_MARK.match(blk.strip()):
                    emit(li, esc(blk) + ' ', blk + ' ')       # nomor catatan kaki di awal baris
                else:
                    keep.append(blk)
            # blok lain dipindah ke akhir baris sebelumnya
            if keep:
                tgt = li - 1 if li > 0 else li
                for blk in keep:
                    emit(tgt, esc(blk), blk)
                    if LET.search(blk): add_flag(tgt, 'hilang')
            sonly[t0] = []
        tk = 0
        for k, ch in enumerate(line):
            if ch == '\x05':
                out[li].append('<span class="ref">'); in_ref[li] = True; plain[li].append('\x05'); continue
            if ch.isspace():
                # lihat huruf berikutnya pada baris ini
                nxt = next((c2 for c2 in line[k + 1:] if not c2.isspace() and c2 != '\x05'), None)
                if nxt is not None and tk > 0 and tk < len(t_by_line[li]):
                    ta, tb = t_by_line[li][tk - 1], t_by_line[li][tk]
                    if (smap[ta] is not None and smap[tb] is not None and smap[tb] == smap[ta] + 1 and Sidx[smap[tb]] == Sidx[smap[ta]] + 1
                            and LET.match(Tch[ta]) and LET.match(Tch[tb])):
                        continue
                emit(li, ch, ch); continue
            t = Tpos_index = None
            # cari t untuk (li,k)
            t = t_by_line[li][tk]; tk += 1
            if t != t0 and t in sonly and sonly[t]:
                for blk in sonly[t]:
                    emit(li, esc(blk), blk)
                    if LET.search(blk): add_flag(li, 'hilang')
                sonly[t] = []
            if t in tonly_skip:
                continue
            if t in tonly_first:
                rep, tag = tonly_first[t]
                if rep:
                    emit(li, esc(rep), rep)
                add_flag(li, 'beda' if rep else 'tambah')
                continue
            # huruf sama: cek penempelan dengan huruf sebelumnya
            if t > 0 and smap[t] is not None and smap[t - 1] is not None and smap[t] == smap[t - 1] + 1 and Sidx[smap[t]] == Sidx[smap[t - 1]] + 1:
                pli, pk = Tpos[t - 1]
                if (pli, pk) != (li, k - 1) and LET.match(Tch[t]) and LET.match(Tch[t - 1]) and t not in flagged_boundary:
                    flagged_boundary.add(t)
                    if pli == li:
                        add_flag(li, 'menempel')
                    else:
                        add_flag(pli, 'menempel')
            emit(li, esc(ch), ch)
        if in_ref[li]:
            out[li].append('</span>')
    # S-only di akhir seluruh teks
    if nT in sonly and lines:
        for blk in sonly[nT]:
            emit(len(lines) - 1, esc(blk), blk)
            if LET.search(blk): add_flag(len(lines) - 1, 'hilang')
    res = []
    for li in range(len(lines)):
        res.append((''.join(out[li]), ''.join(plain[li]), nflag[li]))
    return res

def fidelity(S, plains):
    """True bila teks yang ditampilkan (tanpa spasi) sama persis dengan S (tanpa spasi)."""
    a = re.sub(r'\s+', '', ''.join(plains))
    b = re.sub(r'\s+', '', S)
    return a == b, a, b
