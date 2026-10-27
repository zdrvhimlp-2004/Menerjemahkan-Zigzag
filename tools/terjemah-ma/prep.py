import json, re, sys
SP = '/tmp/claude-0/-home-user-Menerjemahkan-Zigzag/f395751c-a639-5518-8174-6a8772e78be1/scratchpad/ma/'

DIGS = '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩'
D = '[0-9' + DIGS + ']'
TR = str.maketrans(DIGS, '0123456789' * 2)
HAR = '[ً-ْٰ]'
HARC = re.compile(HAR)

def nd(s): return s.translate(TR)

# ---------------------------------------------------------------- pembersihan halaman
def strip_page_a(t, n):
    """file a: satu paragraf per halaman, header/nomor halaman menempel pada teks."""
    heads = ['الفصل الثالث / أحوال المسند', 'الفصل الرابع / أحوال متعلقات الفعل', 'الفصل الرابع أحوال متعلقات الفعل']
    for h in heads:
        t = t.replace(h, ' ')
    # 'علم المعاني' (header) hanya bila menempel pada nomor halaman / awal teks
    t = re.sub(r'(?<=%s)علم المعاني' % D, ' ', t)
    t = re.sub(r'علم المعاني(?=%s{3})' % D, ' ', t)
    t = re.sub(r'^\s*علم المعاني', ' ', t)
    t = re.sub(r'خروج الكلام عن مقتضى الظاهر(?=%s{3})' % D, ' ', t)
    # nomor halaman
    pat = re.compile(r'(?<!%s)(?:%s)(?!%s)' % (D, '|'.join(re.escape(x) for x in {str(n), str(n).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')), str(n).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))}), D))
    # jangan hapus di dalam [ ... ]
    out, last, cnt = [], 0, 0
    masked = re.sub(r'\[[^\]]*\]', lambda m: '\0' * len(m.group(0)), t)
    for m in pat.finditer(masked):
        out.append(t[last:m.start()]); last = m.end(); cnt += 1
    out.append(t[last:])
    t = ''.join(out)
    return re.sub(r'\s+', ' ', t).strip(), cnt

FN_START = re.compile(r'(?<=\S)\(\s*(%s)\s*\)(?=\s)' % D)

def split_footnotes(t):
    """pisahkan catatan kaki di akhir halaman: penanda (N) menempel pada kata sebelumnya."""
    ms = list(FN_START.finditer(t))
    ms = [m for m in ms if m.start() > len(t) * 0.35]
    if not ms:
        return t, []
    # mulai dari penanda pertama yang berurutan (1)
    first = None
    for m in ms:
        if nd(m.group(1)) == '1':
            first = m; break
    if first is None:
        first = ms[0]
    main = t[:first.start()].strip()
    fn = t[first.start():]
    parts = re.split(r'(?:(?<=\S)|^|(?<=\s))\(\s*%s\s*\)\s*' % D, fn)
    parts = [p.strip() for p in parts if p.strip()]
    return main, parts

if __name__ == '__main__':
    pages = json.load(open(SP + 'a_pages.json', encoding='utf-8'))
    bad = 0
    for n, t in pages:
        c, cnt = strip_page_a(t, n)
        main, fns = split_footnotes(c)
        if cnt != 1:
            bad += 1
            print('PAGENUM', n, cnt)
    print('pages with cnt!=1:', bad)
    for n, t in pages[:3] + pages[7:9]:
        c, cnt = strip_page_a(t, n)
        main, fns = split_footnotes(c)
        print('=====', n, cnt, len(main), fns)
        print(main[:300], '...', main[-200:])
