import re, json
from prep import HARC, D, nd, TR, FN_START, split_footnotes, strip_page_a

HARS = 'ًٌٍَُِّْٰ'

def nharak(w):
    return len(HARC.findall(w))

def vocalized(w):
    n = nharak(w)
    return n >= 2 or (n >= 1 and len(re.sub(HAR_RE, '', w)) <= 3)

HAR_RE = re.compile('[ً-ْٰ]')

# ---- pecah token yang menempel: ":يا" , "عَدَمُهذا" , "مَرْهُوبُإِنْ"
SAFE_TAILS = {'وا', 'ان', 'ين', 'ون', 'ها', 'هم', 'نا', 'ني', 'كم', 'ما', 'هن', 'ته', 'ات', 'ية', 'ءا'}
def split_glue(w):
    # tanda baca : lalu huruf
    m = re.match(r'^(.*?[:؛،,])([ء-يً-ْٰ].*)$', w)
    if m and m.group(1) != ':' or m and m.group(1) == ':':
        if m and m.group(2) and not re.match(r'^[0-9]', m.group(2)):
            return split_glue(m.group(1)) + split_glue(m.group(2)) if m.group(1) != w else [w]
    # harakah + إ  (hamzah bawah di tengah kata = kata baru)
    m = re.match(r'^(.*[ً-ْ])(إ[ً-ْ].*)$', w)
    if m:
        return [m.group(1)] + split_glue(m.group(2))
    # ekor tanpa harakat >= 3 huruf setelah harakah terakhir
    m = re.match(r'^(.*[ً-ْ])([ء-ي]{3,})$', w)
    if m and nharak(m.group(1)) >= 2:
        return [m.group(1), m.group(2)]
    m = re.match(r'^(.*[ً-ْ])([ء-ي]{2})$', w)
    if m and m.group(2) not in SAFE_TAILS and nharak(m.group(1)) >= 3:
        return [m.group(1), m.group(2)]
    return [w]

def tokens(text):
    out = []
    for w in text.split():
        out.extend(split_glue(w))
    return out

# ---- ayat
VERSE = re.compile(r'([﴿(])\s*([^﴾)]*?)\s*([﴾)])\s*((?:\[[^\]]*\])?)')

def find_verses(text):
    res = []
    for m in VERSE.finditer(text):
        inner = m.group(2)
        ws = inner.split()
        brackets = m.group(1) == '﴿' or m.group(3) == '﴾'
        if len(ws) >= 2 and ((sum(1 for w in ws if nharak(w) >= 2) >= max(2, len(ws) // 2)) or (brackets and m.group(4) and len(ws) >= 3)):
            res.append((m.start(), m.end(), m.group(1) + inner.strip() + m.group(3), m.group(4)))
    return res

# ---- puisi: run kata bertasykil (di luar ayat)
def find_poems(toks, minlen=6):
    n = len(toks)
    voc = [(vocalized(t) and t not in ('...', ':')) or t == '¶' for t in toks]
    regs, i = [], 0
    while i < n:
        if not voc[i]:
            i += 1; continue
        j = i
        while j + 1 < n:
            nxt = None
            for g in (1, 2, 3):
                if j + g < n and voc[j + g]:
                    ok = all(toks[j + q] not in (':', '...') and not re.search(r'[.،؟]$', toks[j + q]) for q in range(1, g))
                    if g == 1 or (ok and (j - i) >= 1 and g <= 3):
                        nxt = g
                    break
            if nxt is None: break
            j += nxt
        # hapus ekor tak bertasykil
        while j > i and not voc[j]: j -= 1
        if j - i + 1 >= minlen:
            l = i
            # sertakan 1 kata tak bertasykil tepat setelah ':'
            if l >= 2 and toks[l - 1] not in (':',) and (toks[l - 2] == ':' or toks[l - 2].endswith(':')) and len(toks[l - 1]) <= 5:
                l -= 1
            elif l >= 1 and toks[l - 1] == ':' and False:
                pass
            regs.append((l, j))
        i = j + 1
    return regs

def poem_lines(toks):
    if '¶' in toks or '...' in toks:
        segs, cur = [], []
        for t in toks:
            if t in ('¶', '...'):
                if cur: segs.append(cur)
                cur = []
            else: cur.append(t)
        if cur: segs.append(cur)
        out = []
        for sg in segs: out.extend(chunk_words(sg, 7))
        return out
    ws = list(toks)
    n = len(ws)
    if n <= 14:
        h = n // 2
        return [ws[:h], ws[h:]] if n > 7 else [ws]
    return chunk_words(ws, 7)

# ---- pemecah baris <= 7 kata
BREAK_AFTER = re.compile(r'[،,.:؛؟?!]$|\.\.\.$')
def chunk_words(ws, maxw=7):
    n = len(ws)
    if n <= maxw:
        return [ws]
    k = -(-n // maxw)
    target = n / k
    lines, start = [], 0
    for j in range(1, k):
        ideal = round(start + target) if False else round(j * target)
        best, bs = None, -99
        for c in range(max(start + 2, ideal - 2), min(n - 1, ideal + 2, start + maxw) + 1):
            sc = 0
            if BREAK_AFTER.search(ws[c - 1]): sc += 3
            if ws[c].startswith(('و', 'ف')) and len(ws[c]) > 2: sc += 1
            sc -= abs(c - ideal) * 0.6
            if sc > bs: bs, best = sc, c
        if best is None: best = min(start + maxw, ideal)
        lines.append(ws[start:best]); start = best
    lines.append(ws[start:])
    # jaminan <= maxw
    out = []
    for l in lines:
        while len(l) > maxw:
            out.append(l[:maxw]); l = l[maxw:]
        out.append(l)
    return out

SENT_END = re.compile(r'(?:\.\.\.|\.\.|[.؟?!])$')
def split_prose(text):
    """pecah teks prosa menjadi 'kalimat' lalu baris <=7 kata. kembalikan list baris (str)."""
    ws = []
    for w in text.split():
        if re.fullmatch(r'[.…،,:؛؟?!"«»\-–—]+', w):
            if ws and w not in ('،', ','): ws[-1] += w
            elif not ws and w in ('،', ','): continue
            elif ws: ws[-1] += w
            else: ws.append(w)
        else: ws.append(w)
    sents, cur = [], []
    for w in ws:
        if re.match(r'^[0-9۰-۹٠-٩]+\s*[-–]', w) and len(cur) >= 3:
            sents.append(cur); cur = []
        cur.append(w)
        if SENT_END.search(w) and len(cur) >= 3:
            sents.append(cur); cur = []
    if cur: sents.append(cur)
    lines = []
    for s in sents:
        for l in chunk_words(s):
            lines.append(' '.join(l))
    return lines
