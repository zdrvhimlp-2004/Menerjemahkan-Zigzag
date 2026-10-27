import re, json, sys, os
from prep import *
from seg import *
import seg

SURAH = {}
for i, n in enumerate("الفاتحة|البقرة|آل عمران|النساء|المائدة|الأنعام|الأعراف|الأنفال|التوبة|يونس|هود|يوسف|الرعد|إبراهيم|الحجر|النحل|الإسراء|الكهف|مريم|طه|الأنبياء|الحج|المؤمنون|النور|الفرقان|الشعراء|النمل|القصص|العنكبوت|الروم|لقمان|السجدة|الأحزاب|سبأ|فاطر|يس|الصافات|ص|الزمر|غافر|فصلت|الشورى|الزخرف|الدخان|الجاثية|الأحقاف|محمد|الفتح|الحجرات|ق|الذاريات|الطور|النجم|القمر|الرحمن|الواقعة|الحديد|المجادلة|الحشر|الممتحنة|الصف|الجمعة|المنافقون|التغابن|الطلاق|التحريم|الملك|القلم|الحاقة|المعارج|نوح|الجن|المزمل|المدثر|القيامة|الإنسان|المرسلات|النبأ|النازعات|عبس|التكوير|الانفطار|المطففين|الانشقاق|البروج|الطارق|الأعلى|الغاشية|الفجر|البلد|الشمس|الليل|الضحى|الشرح|التين|العلق|القدر|البينة|الزلزلة|العاديات|القارعة|التكاثر|العصر|الهمزة|الفيل|قريش|الماعون|الكوثر|الكافرون|النصر|المسد|الإخلاص|الفلق|الناس".split('|'), 1):
    SURAH[n] = i
ID_NAMES = "Al-Fatihah|Al-Baqarah|Ali 'Imran|An-Nisa'|Al-Ma'idah|Al-An'am|Al-A'raf|Al-Anfal|At-Taubah|Yunus|Hud|Yusuf|Ar-Ra'd|Ibrahim|Al-Hijr|An-Nahl|Al-Isra'|Al-Kahf|Maryam|Thaha|Al-Anbiya'|Al-Hajj|Al-Mu'minun|An-Nur|Al-Furqan|Asy-Syu'ara'|An-Naml|Al-Qashash|Al-'Ankabut|Ar-Rum|Luqman|As-Sajdah|Al-Ahzab|Saba'|Fathir|Yasin|Ash-Shaffat|Shad|Az-Zumar|Ghafir|Fushshilat|Asy-Syura|Az-Zukhruf|Ad-Dukhan|Al-Jatsiyah|Al-Ahqaf|Muhammad|Al-Fath|Al-Hujurat|Qaf|Adz-Dzariyat|Ath-Thur|An-Najm|Al-Qamar|Ar-Rahman|Al-Waqi'ah|Al-Hadid|Al-Mujadilah|Al-Hasyr|Al-Mumtahanah|Ash-Shaff|Al-Jumu'ah|Al-Munafiqun|At-Taghabun|Ath-Thalaq|At-Tahrim|Al-Mulk|Al-Qalam|Al-Haqqah|Al-Ma'arij|Nuh|Al-Jinn|Al-Muzzammil|Al-Muddatstsir|Al-Qiyamah|Al-Insan|Al-Mursalat|An-Naba'|An-Nazi'at|'Abasa|At-Takwir|Al-Infithar|Al-Muthaffifin|Al-Insyiqaq|Al-Buruj|Ath-Thariq|Al-A'la|Al-Ghasyiyah|Al-Fajr|Al-Balad|Asy-Syams|Al-Lail|Adh-Dhuha|Asy-Syarh|At-Tin|Al-'Alaq|Al-Qadr|Al-Bayyinah|Az-Zalzalah|Al-'Adiyat|Al-Qari'ah|At-Takatsur|Al-'Ashr|Al-Humazah|Al-Fil|Quraisy|Al-Ma'un|Al-Kautsar|Al-Kafirun|An-Nashr|Al-Lahab|Al-Ikhlas|Al-Falaq|An-Nas".split('|')
def norm_s(s):
    s = re.sub('[ً-ْٰـ]', '', s)
    s = re.sub('[أإآٱ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه')
    return s
SN = {norm_s(k): ID_NAMES[v - 1] for k, v in SURAH.items()}
SN[norm_s('الأنبيائ')] = 'Al-Anbiya\''
SN[norm_s('الأعراف')] = "Al-A'raf"
def ref_id(ref):
    """'[الزخرف ۸۱]' -> 'QS. Az-Zukhruf: 81' ; kembalikan (teks, ok)"""
    inner = nd(ref.strip('[] ').replace('،', ',')).replace('٬', ',')
    m = re.match(r'^\s*(?:سورة\s+)?([^\d:،,]+?)\s*[:：]?\s*([\d\s,،\-–]+)\s*$', inner)
    if not m:
        nm0 = SN.get(norm_s(inner.strip()))
        return (('QS. ' + nm0) if nm0 else ('QS. ' + inner), bool(nm0))
    name = norm_s(m.group(1).strip())
    nums = re.sub(r'\s+', ' ', m.group(2).strip()).replace(' ,', ',')
    nm = SN.get(name)
    if not nm: return ('QS. ' + inner, False)
    return ('QS. %s: %s' % (nm, nums.replace(',', ', ').replace('  ', ' ').strip()), True)

def fix_glue(t):
    t = re.sub(r'(\.{2,})(?=[ء-ي"«(])', r'\1 ', t)
    t = re.sub(r'(?<=[ء-ي\)ً-ْ])\.(?=[ء-ي])', '. ', t)
    t = re.sub(r'(?<=[ء-يً-ْ])،(?=[ء-ي])', '، ', t)
    t = re.sub(r'(?<=[ء-ي])(\(%s\))' % D, r' \1', t)
    t = re.sub(r'(\(%s\))(?=[ء-ي])' % D, r'\1 ', t)
    return t

FIXES = []
def units_from_text(main, heads):
    for a, c in FIXES:
        if a.startswith('~'):
            pat = '[\u064b-\u0652\u0670]*'.join(re.escape(ch) if ch != ' ' else ' ' for ch in a[1:])
            main = re.sub(pat, lambda m: c.replace('\\0', m.group(0)), main, count=1)
        else:
            main = main.replace(a, c)
    main = fix_glue(main)
    verses = find_verses(main)
    ph = []; out = []; last = 0
    for (a, b, inner, ref) in verses:
        out.append(main[last:a]); out.append('\x01%d\x01' % len(ph)); ph.append(('q', inner, ref)); last = b
    out.append(main[last:]); t = ''.join(out)
    for h, kind in heads:
        if h in t:
            t = t.replace(h, '\x02%d\x02' % len(ph), 1); ph.append((kind, h, None))
        else:
            print('!! heading tidak ditemukan:', h, file=sys.stderr)
    parts = re.split(r'(\x01\d+\x01|\x02\d+\x02)', t)
    units = []
    for p in parts:
        m = re.fullmatch(r'[\x01\x02](\d+)[\x01\x02]', p)
        if m:
            kind, a, b = ph[int(m.group(1))]; units.append((kind, a, b)); continue
        if not p.strip(): continue
        toks = tokens(p)
        regs = find_poems(toks)
        pos = 0
        for (l, r) in regs:
            if l > pos: units.append(('p', ' '.join(toks[pos:l]), None))
            units.append(('sy', [' '.join(h) for h in poem_lines(toks[l:r + 1])], None))
            pos = r + 1
        if pos < len(toks): units.append(('p', ' '.join(toks[pos:]), None))
    return units

def lines_of(unit):
    k, a, b = unit
    if k in ('h1', 'h2', 'h3'): return [a]
    if k == 'q':
        return [' '.join(l) for l in chunk_words(a.split(), 7)]
    if k == 'sy': return a
    if k in ('p', 'fn'): return split_prose(a)
    raise ValueError(k)

def build_a(heads):
    pages = json.load(open(SP + 'a_pages.json', encoding='utf-8'))
    seq = []
    for n, t in pages:
        c, cnt = strip_page_a(t, n)
        main, fns = split_footnotes(c)
        us = units_from_text(main, heads.get(str(n), []))
        for i, f in enumerate(fns, 1):
            us.append(('fn', fix_glue(f), i))
        seq.append((n, us))
    return seq

def number(seq, tag):
    """beri id stabil: tag+halaman-urutan. kembalikan struktur: list (page, [unit dict])"""
    res = []
    for n, us in seq:
        idx = 0; out = []
        for (k, a, b) in us:
            ls = lines_of((k, a, b))
            ids = []
            for l in ls:
                idx += 1; ids.append('%s%d-%03d' % (tag, n, idx))
            out.append({'k': k, 'lines': ls, 'ids': ids, 'ref': b if k in ('q', 'fn') else None})
        res.append((n, out))
    return res

if __name__ == '__main__':
    tag = sys.argv[1]
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    hp = SP + 'heads_%s.json' % tag
    heads = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    FIXES.extend(heads.pop('_fix', []))
    seq = build_a(heads) if tag == 'a' else build_b(heads)
    for n, us in number(seq, tag):
        if not (lo <= n <= hi): continue
        print('======== HAL', n)
        for u in us:
            for i, l in zip(u['ids'], u['lines']):
                extra = ''
                if u['k'] == 'q' and i == u['ids'][-1]: extra = '   [REF %s]' % (ref_id(u['ref'])[0] if u['ref'] else '-')
                print('%s|%s|%s%s' % (i, u['k'], l, extra))
