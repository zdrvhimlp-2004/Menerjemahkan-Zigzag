#!/usr/bin/env python3
"""Tambahkan link 'الموضوعات' ke index.html untuk semua mata kuliah di semN.py (aman dijalankan berulang)."""
import glob, importlib.util, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, '..', '..', 'index.html')
s = open(INDEX, encoding='utf-8').read()

mods = []
for f in sorted(glob.glob(os.path.join(HERE, 'sem*.py'))):
    spec = importlib.util.spec_from_file_location('m', f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    mods.append(m)

# konstanta folder per semester
for m in mods:
    if "const S%d = " % m.SEM not in s:
        s = s.replace("const S5 = ", "const S%d = 'Data/Data Lughoh per Semester/Semester %d/'; // folder asli di repo\nconst S5 = " % (m.SEM, m.SEM), 1) if m.SEM != 5 else s

for m in mods:
    for judul, folder, _ in m.COURSES:
        tag = "S%d + '%s/maudhuat.html'" % (m.SEM, folder)
        if tag in s:
            continue
        linkline = "        link('الموضوعات', %d, %s),\n" % (m.SEM, tag)
        pat_a = re.compile(r"l\('%s', (\d+)\),"  % re.escape(judul))
        pat_b = re.compile(r"(l\('%s', \d+, \[\n)" % re.escape(judul))
        if len(pat_a.findall(s)) == 1:
            s = pat_a.sub(lambda mo: "l('%s', %s, [\n%s      ])," % (judul, mo.group(1), linkline), s)
        elif len(pat_b.findall(s)) == 1:
            s = pat_b.sub(lambda mo: mo.group(1) + linkline, s)
        else:
            print('GAGAL (tidak ditemukan / ganda):', m.SEM, judul)

open(INDEX, 'w', encoding='utf-8').write(s)
print('selesai')
