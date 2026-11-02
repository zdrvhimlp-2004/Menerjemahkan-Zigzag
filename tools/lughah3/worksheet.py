import sys, re
from units import load_units
blocks, res = load_units()
a, b = int(sys.argv[1]), int(sys.argv[2])
for r in res:
    bi = r['bi']
    if not (a <= bi < b): continue
    if len(r['chunks']) == 1: continue
    print('@' + r['uid'], '[%s]' % r['kind'].replace('ayat', '').strip())
    for k, c in enumerate(r['chunks'], 1):
        print(' %d. %s' % (k, ' '.join(('*' + w + '*') if bd and False else w for w, bd, em in c)))
    print(' =', re.sub(r'<br\s*/?>', ' // ', re.sub(r'</?strong>', '', r['id'])))
