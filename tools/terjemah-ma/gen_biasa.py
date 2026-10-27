import re, html, zipfile, difflib
SP='/tmp/claude-0/-home-user-Menerjemahkan-Zigzag/f395751c-a639-5518-8174-6a8772e78be1/scratchpad/'
F='/home/user/Menerjemahkan-Zigzag/Data/Data Lughoh per Semester/Semester 5/النحو (5)/syarh-ibnu-aqil-biasa.html'
DOCX="/home/user/Menerjemahkan-Zigzag/Data/Data Lughoh per Semester/Semester 5/النحو (5)/af'al at tafdhil.docx"
esc=lambda s: html.escape(s,quote=False)
tr={}
for l in open(SP+'trans_b10.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if l.strip():
        k,_,v=l.partition('|'); tr[int(k)]=v
har={}
for l_ in open(SP+'harakat_b10.txt',encoding='utf-8'):
    l_=l_.rstrip('\n')
    if l_.strip():
        k_,_,v_=l_.partition('|'); har[int(k_)]=v_.split()
cnt={'q':33,'h':2,'k':24}
state=None; first=False
n=0; body=[]; bait=False; allar=[]
def line_html(tokens):
    """tokens: list of (ar, cls, id) -> html; gabungkan run kelas sama"""
    out=[]; i=0
    while i<len(tokens):
        j=i
        while j<len(tokens) and tokens[j][1]==tokens[i][1] and (j==i or tokens[j][2] is None): j+=1
        txt=' '.join(t[0] for t in tokens[i:j])
        c=tokens[i][1]; idd=tokens[i][2]
        if c: out.append('<span class="%s"%s>%s</span>'%(c,(' id="%s"'%idd) if idd else '',esc(txt)))
        else: out.append(esc(txt))
        i=j
    return ' '.join(out)
for ln in open(SP+'bab10.txt',encoding='utf-8'):
    ln=ln.rstrip('\n')
    if not ln.strip() or ln.startswith('#'): continue
    cmd,_,rest=ln.partition(' ')
    if cmd=='BLK':
        kind,_,r2=rest.partition(' ')
        if kind=='p': body.append('<div class="blk blk-p">')
        elif kind=='nz':
            num,_,label=r2.partition(' ')
            body.append('<div class="blk blk-nz" id="nz-%s">\n<div class="tag"><span class="tag__k" lang="ar">نَظْمُ الْأَلْفِيَّةِ</span><span class="tag__t">%s</span></div>'%(num,esc(label.replace('_',' '))))
        elif kind=='sy':
            num,_,label=r2.partition(' ')
            body.append('<div class="blk blk-sy" id="sy-%s">\n<div class="tag"><span class="tag__k" lang="ar">شَاهِدٌ شِعْرِيٌّ</span><span class="tag__t">%s</span></div>'%(num,esc(label.replace('_',' '))))
        elif kind=='nzc':
            body.append('<div class="blk blk-nz">\n<div class="tag tag--cont"><span class="tag__k" lang="ar">نَظْمُ الْأَلْفِيَّةِ</span><span class="tag__t">lanjutan bait pada halaman berikutnya</span></div>')
        elif kind=='sycont':
            body.append('<div class="blk blk-sy">\n<div class="tag tag--cont"><span class="tag__k" lang="ar">شَاهِدٌ شِعْرِيٌّ</span><span class="tag__t">lanjutan bait kedua syahid No. ٢٨٥</span></div>')
    elif cmd=='BAIT':
        if bait: body.append('</div>')
        body.append('<div class="bait">'); bait=True
    elif cmd=='L':
        n+=1
        toks=[]; ti=0
        for t in rest.split():
            if t.startswith('@'):
                if t=='@/': state=None
                else:
                    kind=t[1]
                    if kind=='c': state=('c',None)
                    else:
                        cnt[kind]+=1
                        state=(kind,'%s-%d'%({'q':'qs','h':'hd','k':'kl'}[kind],cnt[kind]))
                    first=True
                continue
            ar=t.partition('=')[0]
            allar.append(ar)
            arv=har[n][ti]; ti+=1
            if state:
                toks.append((arv,state[0],state[1] if first else None)); first=False
            else: toks.append((arv,None,None))
        whole=len(set(t[1] for t in toks))==1 and toks[0][1] in ('q','h','k')
        cls='ayat'+(' r'+toks[0][1] if whole else '')
        body.append('<div class="%s"><p class="ar" lang="ar">%s</p><p class="id" lang="id">%s</p></div>'%(cls,line_html(toks),esc(tr[n])))
    elif cmd=='END':
        if bait: body.append('</div>'); bait=False
        body.append('</div>')
    elif cmd=='HAL':
        body.append('<div class="hal hal--akhir" id="hal-%s"><span>Juz 3 &middot; Hlm. %s</span></div>'%(rest,rest))
        if int(rest)<189: body.append('<div class="hal-awal"><span>Halaman %d</span></div>'%(int(rest)+1))
assert n==256 and sorted(tr)==list(range(1,257)),(n,len(tr))
newbody='<div class="hal-awal"><span>Halaman 174</span></div>\n'+'\n'.join(body)+'\n'

# --- validasi kata Arab terhadap docx (urutan kata sama persis)
HAR=re.compile('[ً-ٰٟـ]')
def norm(s):
    s=HAR.sub('',s); s=re.sub('[أإآٱ]','ا',s).replace('ى','ي').replace('ة','ه')
    return re.sub(r'[^ء-ي0-9٠-٩ ]',' ',s)
x=zipfile.ZipFile(DOCX).read('word/document.xml').decode()
paras=re.findall(r'<w:p[ >].*?</w:p>',x,flags=re.S)
txt=[]
for p in paras:
    t=html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>',p,flags=re.S)))
    txt.append(re.sub(r'الجزء: 3 - الصفحة: \d+',' ',t))
src=[w for w in norm(' '.join(txt)).split() if not re.fullmatch(r'[0-9٠-٩]+',w)]
mine=[w for w in norm(' '.join(allar)).split() if not re.fullmatch(r'[0-9٠-٩]+',w)]
sm=difflib.SequenceMatcher(None,src,mine,autojunk=False)
diffs=[(op,' '.join(src[a1:a2]),' '.join(mine[b1:b2])) for op,a1,a2,b1,b2 in sm.get_opcodes() if op!='equal']
print('kata sumber',len(src),'kata saya',len(mine),'beda:',diffs)

# --- sisipkan ke file
s=open(F,encoding='utf-8').read()
i=s.index('<header class="bab" id="bab-10">')
j_end=s.index('<div class="hal" id="hal-189">'); j_end=s.index('</div>',j_end)+len('</div>')
seg=s[i:j_end]
ring=re.search(r'<div class="ringkasan">.*?</div>\n',seg,flags=re.S).group(0)
newhdr='<header class="bab" id="bab-10"><h2 class="bab__ar" lang="ar">أفعل التفضيل</h2><p class="bab__id">Bab 10 &middot; Af\'al at-Tafdhil (Bentuk Perbandingan: &lsquo;lebih&rsquo; dan &lsquo;paling&rsquo;)</p></header>\n'
note173='<div class="hal" id="hal-173"><span style="color:#c0392b">&#9888; Hlm. 173 tidak ada di data sumber (file ini berhenti di hlm. 172, bab ini mulai dari hlm. 174)</span></div>\n'
s=s[:i]+newhdr+note173+ring+newbody.rstrip('\n')+s[j_end:]
# buang CSS zigzag, legenda zigzag, kata 'zigzag'
if '/* ---------- zigzag (bab 10)' in s:
    a=s.index('  /* ---------- zigzag (bab 10)'); b=s.index('  .kata.k .id { color: var(--k); }\n')+len('  .kata.k .id { color: var(--k); }\n')
    s=s[:a]+s[b:]
s=re.sub(r'\s*<li><span class="sw" lang="ar">كَلِمَةٌ</span> Bab 10 \(zigzag\).*?</li>\n','\n',s,flags=re.S)
s=re.sub(r'<p class="isi__ket">.*?</p>','<p class="isi__ket">Syarh Ibnu &lsquo;Aqil &lsquo;ala Alfiyyah Ibni Malik &middot; Juz 3, Hlm. 42&ndash;172 &amp; 174&ndash;189 &middot; 10 bab &middot; 88 kelompok nazham &middot; 66 syahid syair &middot; Terjemah biasa &middot; 1 baris Arab + 1 baris Indonesia</p>',s,count=1,flags=re.S)
s=s.replace("Af'al at-Tafdhil (Bentuk Perbandingan) &middot; zigzag","Af'al at-Tafdhil (Bentuk Perbandingan)")
if '.hal-awal' not in s:
    css="""  .hal--akhir { height: 0; margin: 0; overflow: hidden; }
  .hal-awal { display: flex; align-items: center; gap: 0.8rem; margin: 1.6rem 0 0.9rem; direction: ltr; color: var(--heading); }
  .hal-awal::before, .hal-awal::after { content: ''; flex: 1; height: 1px; background: var(--border); }
  .hal-awal span { font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; background: var(--pasal-bg); padding: 0.15rem 1rem; border-radius: 999px; }
"""
    s=s.replace('</style>',css+'</style>',1)
open(F,'w',encoding='utf-8').write(s)
print('zigzag tersisa:',len(re.findall('zigzag|baris tengah|class="kata',s)))
