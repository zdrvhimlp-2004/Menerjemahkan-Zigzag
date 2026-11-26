import docx,re,html,sys
from docx.table import Table
from docx.text.paragraph import Paragraph
DOCX=sys.argv[3]
TPL=sys.argv[4]
OUT=sys.argv[1]; PDFNAME=sys.argv[2]
AR2EN=str.maketrans('٠١٢٣٤٥٦٧٨٩','0123456789'); EN2AR=str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩')
esc=lambda t: html.escape(t,quote=False)
d=docx.Document(DOCX)
items=[]
for ch in d.element.body.iterchildren():
    tag=ch.tag.split('}')[1]
    if tag=='p': items.append(('p',Paragraph(ch,d)))
    elif tag=='tbl': items.append(('t',Table(ch,d)))
ORD=re.compile(r'^\s*(أولا|أولاً|ثانيا|ثانياً|ثالثا|ثالثاً|رابعا|رابعاً|خامسا|خامساً|سادسا|سادساً|سابعا|سابعاً|ثامنا|ثامناً|تاسعا|تاسعاً|عاشرا|عاشراً)\s*:')
LI=re.compile(r'^\s*(?:[•\-–]\s*|\.?\d+[\.\)\s]\s*)')
def strip_no(t): return re.sub(r'^\s*0*\d+\s*\.?\s*','',t).strip()
out=[]; toc=[]   # toc: dict(bab_id,title,page,subs=[(id,title,page)])
page=0; nbab=0; nsub=0
def hal(n):
    return '<div class="hal" id="hal-%d" data-kitab="%d"><span><i class="hal__t">Hlm. </i>%d</span><button type="button" class="hal__pdf" data-pdf="%d" aria-label="Lihat PDF asli untuk Hlm. %d" title="Lihat PDF asli"></button></div>'%(n,n,n,n,n)
def para(t,cls):
    return '<div class="blk %s"><div class="ayat"><p class="ar" lang="ar">%s</p></div></div>'%(cls,esc(t))
CLEAN=lambda t: re.sub(r'\*\*|</?\w+[^>]*>','',html.unescape(t))
for kind,o in items:
    t0=o.text
    s=o.style.name
    m=re.search(r'---\s*صفحة\s*([٠-٩0-9]+)\s*---',t0)
    if m:
        np_=int(m.group(1).translate(AR2EN))
        if np_!=page: page=np_; out.append(hal(page))
        t0=(t0[:m.start()]+'\n'+t0[m.end():]).strip()   # teks yang menempel pada penanda tetap diproses
        if not CLEAN(t0).strip(): continue
    t=CLEAN(t0)
    if not t.strip(): continue
    if page==35 and re.sub('[\u064b-\u065f]','',t).lstrip().startswith('الناس قد أثموا'):   # koreksi: di PDF 3 baris syair ini sudah di hlm. 36
        page=36; out.append(hal(36))
    if page==1:                       # sampul: apa adanya, satu baris satu paragraf
        for line in t.split('\n'):
            if line.strip(): out.append(para(line.strip(),'blk-p'))
        continue
    if s=='Heading 1':
        nbab+=1; tt=t.strip()
        toc.append(dict(id='bab-%d'%nbab,title=tt,page=page,subs=[]))
        out.append('<header class="bab" id="bab-%d"><h2 class="bab__ar" lang="ar">%s</h2></header>'%(nbab,esc(tt))); continue
    if s in ('Heading 2','Heading 3','Heading 4'):
        nsub+=1; tt=re.sub(r'^\s*[•\-–]\s*','',t).strip()
        if toc and s in ('Heading 2','Heading 3'): toc[-1]['subs'].append(('sub-%d'%nsub,tt,page))
        if s=='Heading 2': out.append('<h3 class="sub" id="sub-%d" lang="ar">%s</h3>'%(nsub,esc(tt)))
        else: out.append('<h4 class="sub sub--3" id="sub-%d" lang="ar">%s</h4>'%(nsub,esc(tt)))
        continue
    for line in t.split('\n'):
        line=line.strip()
        if not line: continue
        if LI.match(line) and not re.match(r'^https?:',line):
            out.append(para(line,'blk-li')); continue
        out.append(para(line,'blk-p'))
# --- fihris
last=page
tocl=['<ol class="toc">']
for k,b in enumerate(toc):
    end=(toc[k+1]['page']-0) if k+1<len(toc) else last
    end=max(end,b['page'])
    rng='Hlm. %d'%b['page']+('&ndash;%d'%end if end!=b['page'] else '')
    tocl.append('<li class="toc__bab"><details><summary><span class="toc__no">%d.</span><a class="toc__ar" lang="ar" href="#%s">%s</a><span class="toc__meta">%s</span></summary>'%(k+1,b['id'],esc(b['title']),rng))
    if b['subs']:
        tocl.append('<div class="toc__sec"><ol>'+''.join('<li><a href="#%s"><span class="toc__a" lang="ar">%s</span><span class="toc__ref">Hlm. %d</span></a></li>'%(i,esc(tt),p) for i,tt,p in b['subs'])+'</ol></div>')
    tocl.append('</details></li>')
tocl.append('</ol>')
# --- rakit dari templat
T=open(TPL,encoding='utf-8').read().split('\n')
h1=next(i for i,l in enumerate(T) if l.startswith('<div class="hal" id="hal-1"'))
ol=next(i for i,l in enumerate(T) if l.startswith('<ol class="toc">'))
olend=next(i for i,l in enumerate(T) if i>ol and l.strip()=='</ol>')
e=next(i for i,l in enumerate(T) if '</section>' in l and i>h1)
head=T[:ol]+tocl+T[olend+1:h1]
tail=T[e-1:]   # '  </div>' + '</section>' ...
s='\n'.join(head+out+tail)
TITLE='البحث عن النثر في العصر الوسيط'
s=re.sub(r'<title>.*?</title>','<title>%s — النص العربي</title>'%TITLE,s,count=1)
s=re.sub(r'<h1 class="isi__judul" lang="ar">.*?</h1>','<h1 class="isi__judul" lang="ar">%s</h1>'%TITLE,s,count=1)
s=re.sub(r'<p class="isi__ket" lang="ar">.*?</p>','<p class="isi__ket" lang="ar">النُّصُوصُ الْأَدَبِيَّةُ (٤) · الْمُسْتَوَى الْخَامِسُ · النَّصُّ الْعَرَبِيُّ فَقَطْ (%s صَفْحَةً بِحَسَبِ أَرْقَامِ الصَّفَحَاتِ فِي الْأَصْلِ)</p>'%str(last).translate(EN2AR),s,count=1)
s=re.sub(r'PDFPANEL=\{src:"[^"]*"\}','PDFPANEL={src:"%s"}'%PDFNAME,s)
s=s.replace('title="Kode Warna">?</button>','title="دليل الألوان">?</button>')
open(OUT,'w',encoding='utf-8').write(s)
print('halaman',last,'bab',len(toc),'sub',nsub,'baris isi',len(out))
