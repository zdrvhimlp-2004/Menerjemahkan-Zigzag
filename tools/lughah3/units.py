"""Ilmu Lughah 3: pecah paragraf Arab menjadi baris <= 7 kata.

Sumber blok: tools/lughah3/blocks.json (hasil ekstrak dari versi paragraf panjang).
Setiap paragraf dipecah per <br> menjadi 'unit'; tiap unit dipecah DP menjadi chunk <= MAXW kata,
dengan preferensi memotong di tanda baca, lalu sebelum kata sambung/preposisi.
"""
import re, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
MAXW = 7
TASHKEEL = re.compile('[ً-ٰٟ]')

def plain(w):
    return TASHKEEL.sub('', w)

NO_BREAK_AFTER = {'في', 'من', 'على', 'الى', 'إلى', 'عن', 'أن', 'إن', 'أنّ', 'إنّ', 'ان', 'لا', 'ما', 'قد', 'لم', 'لن',
                  'مع', 'بين', 'حتى', 'ثم', 'أو', 'او', 'كما', 'إذا', 'اذا', 'هو', 'هي', 'هذا', 'هذه', 'ذلك', 'تلك', 'التي',
                  'الذي', 'الذين', 'اللاتي', 'عند', 'بعد', 'قبل', 'مثل', 'نحو', 'غير', 'كل', 'بعض', 'ذات', 'ذو', 'أي', 'كان',
                  'كانت', 'ليس', 'لكن', 'لكنّ', 'إلا', 'الا', 'أما', 'إما', 'لو', 'لما', 'كي', 'بل', 'ثمّ', 'أيضا', 'فقط'}
BREAK_BEFORE_SOFT = {'ثم', 'أو', 'لكن', 'حتى', 'إذا', 'اذا', 'بل', 'مثل', 'نحو', 'كما', 'إلا', 'وهو', 'وهي', 'التي', 'الذي',
                     'الذين', 'لأن', 'لان', 'لأنه', 'لأنها', 'حيث', 'أي', 'مع', 'عند', 'بين', 'بعد', 'قبل', 'منها', 'منه'}
PREP = {'في', 'من', 'على', 'إلى', 'الى', 'عن', 'مع', 'بين'}

def tokenize(html):
    """-> list of units; unit = list of (word, bold, em). Dipisah oleh <br>."""
    units, cur = [], []
    bold = em = False
    for part in re.split(r'(<[^>]+>)', html):
        if not part:
            continue
        if part.startswith('<'):
            t = part.lower()
            if t.startswith('<br'):
                units.append(cur); cur = []
            elif t == '<strong>': bold = True
            elif t == '</strong>': bold = False
            elif t == '<em>': em = True
            elif t == '</em>': em = False
            continue
        for w in part.replace('&nbsp;', ' ').split():
            cur.append((w, bold, em))
    units.append(cur)
    return [u for u in units if u]

def break_cost(toks, i):
    """biaya memotong setelah token ke-i (toks[i] di akhir baris)."""
    w = toks[i][0]; nxt = toks[i + 1][0]
    pw, pn = plain(w), plain(nxt)
    c = 9
    if re.search(r'[.؟!:؛]["»”)]*$', w): c = 0
    elif re.search(r'[،,]["»”)]*$', w): c = 1
    elif re.search(r'["»”)]$', w) and not re.search(r'^["«“(]', w): c = 3
    else:
        base = re.sub(r'[^ء-ي]', '', pn)
        if base.startswith('و') and len(base) > 3: c = 3
        elif base.startswith('ف') and len(base) > 3 and base not in ('فقط',): c = 4
        elif base in BREAK_BEFORE_SOFT: c = 4
        elif base in PREP: c = 5
        elif base.startswith(('ل', 'ب', 'ك')) and len(base) > 4: c = 7
    pb = re.sub(r'[^ء-ي]', '', pw)
    if c > 1 and (pb in NO_BREAK_AFTER or len(pb) <= 1): c += 8
    if re.match(r'^["«“(]', nxt) is None and re.search(r'^["«“(]', w): c += 6
    return c

def chunk(toks, maxw=MAXW):
    n = len(toks)
    INF = 10 ** 9
    best = [INF] * (n + 1); prev = [0] * (n + 1)
    best[0] = 0
    for j in range(1, n + 1):
        for i in range(max(0, j - maxw), j):
            if best[i] >= INF: continue
            L = j - i
            cost = best[i] + 4 + (0 if j == n else break_cost(toks, j - 1))
            if L == 1 and j != n and i != 0: cost += 3
            if L <= 2: cost += (3 - L)
            cost += abs(L - 5) * 0.15
            if cost < best[j]:
                best[j] = cost; prev[j] = i
    out, j = [], n
    while j > 0:
        i = prev[j]; out.append(toks[i:j]); j = i
    return out[::-1]

def load_units():
    blocks = json.load(open(os.path.join(HERE, 'blocks.json')))
    res = []
    for bi, b in enumerate(blocks):
        kind = b[0]
        if kind.startswith('ayat'):
            ar_units = tokenize(b[1])
            id_parts = [p.strip() for p in re.split(r'<br\s*/?>', b[2])]
            assert len(ar_units) == len(id_parts), (bi, len(ar_units), len(id_parts))
            for k, (u, idp) in enumerate(zip(ar_units, id_parts)):
                num = None
                if k == 0 and u and re.match(r'^[\u0660-\u0669]+\.$', u[0][0]):
                    num = u[0][0][:-1].translate(str.maketrans('\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669', '0123456789'))
                    u = u[1:]
                    idp = re.sub(r'^\s*[0-9]+\.\s*', '', idp)
                res.append({'num': num, 'uid': 'u%03d%s' % (bi, '' if len(ar_units) == 1 else chr(97 + k)), 'bi': bi, 'kind': kind,
                            'first': k == 0, 'last': k == len(ar_units) - 1, 'toks': u, 'id': idp,
                            'chunks': chunk(u)})
    return blocks, res

if __name__ == '__main__':
    blocks, res = load_units()
    n = sum(len(r['chunks']) for r in res)
    print(len(res), 'unit', n, 'baris', max(len(c) for r in res for c in r['chunks']), 'kata maks')
