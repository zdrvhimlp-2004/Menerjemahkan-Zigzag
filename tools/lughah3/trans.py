import glob, os, re, difflib
from units import load_units, HERE

def load_trans():
    t, cur = {}, None
    for f in sorted(glob.glob(os.path.join(HERE, 'trans_*.txt'))):
        for line in open(f, encoding='utf8').read().split('\n'):
            line = line.rstrip()
            if line.startswith('@'):
                cur = line[1:].strip(); t[cur] = []
            elif line.strip() and cur:
                t[cur].append(line.strip())
    return t

def pieces_for(r, t):
    if len(r['chunks']) == 1:
        return [re.sub(r'</?strong>|</?em>', '', r['id']).strip()]
    return t.get(r['uid'])

if __name__ == '__main__':
    blocks, res = load_units()
    t = load_trans()
    miss, bad, low = [], [], []
    for r in res:
        p = pieces_for(r, t)
        if p is None: miss.append(r['uid']); continue
        if len(p) != len(r['chunks']): bad.append((r['uid'], len(r['chunks']), len(p))); continue
        src = re.sub(r'</?(strong|em)>', '', r['id'])
        a = re.sub(r'\W+', ' ', src.lower()); b = re.sub(r'\W+', ' ', ' '.join(p).lower())
        ratio = difflib.SequenceMatcher(None, a.split(), b.split()).ratio()
        if ratio < 0.8: low.append((r['uid'], round(ratio, 2)))
    print('belum:', len(miss), miss[:12])
    print('jumlah beda:', bad)
    print('mirip rendah:', low)
