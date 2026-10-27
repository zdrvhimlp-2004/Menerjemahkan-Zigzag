import re,sys
HAR=re.compile('[ً-ْٰـ]')
def N(x):
    return re.sub('[\u0623\u0625\u0622\u0671]','\u0627',HAR.sub('',x)).replace('\u0649','\u064a')
orig={}
n=0
for ln in open('bab10.txt',encoding='utf-8'):
    ln=ln.rstrip('\n')
    if ln.startswith('L '):
        n+=1; orig[n]=[t.partition('=')[0] for t in ln[2:].split() if not t.startswith('@')]
bad=0; got={}
for l in open('harakat_b10.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l.strip(): continue
    k,_,v=l.partition('|'); k=int(k); got[k]=v.split()
    o=orig[k]
    if len(o)!=len(got[k]): print('JUMLAH KATA BEDA',k,len(o),len(got[k])); bad+=1; continue
    for a,b in zip(o,got[k]):
        if N(a)!=N(b):
            print('HURUF BEDA',k,a,'|',b); bad+=1
print('baris:',len(got),'masalah:',bad)
