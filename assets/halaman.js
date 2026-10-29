/* Perilaku bersama halaman terjemah: popup posisi dan fihris yang lebih rapi. */
(function () {
  'use strict';

  /* Tinggi popup dihitung dari tinggi layar yang benar-benar terlihat (visualViewport),
     supaya tidak melebihi layar di browser HP yang unit vh/dvh-nya tidak akurat. */
  var BATAS = [['dialog.modal--wide', 0.86, 720], ['dialog.pos-modal', 0.7, 640], ['dialog.lg-modal', 0.7, 560], ['dialog.pg-modal', 0.8, 660], ['dialog.ph-modal', 0.9, 780]];
  var tinggiLihat = function () {
    var h = window.innerHeight;
    if (window.visualViewport) h = Math.min(h, window.visualViewport.height);
    h = Math.min(h, document.documentElement.clientHeight || h);
    /* di sebagian WebView/aplikasi, innerHeight lebih besar dari layar fisik */
    if (window.screen && screen.height && window.matchMedia && matchMedia('(pointer: coarse)').matches) h = Math.min(h, screen.height * 0.88);
    return h;
  };
  var pasKan = function (d) {
    BATAS.forEach(function (b) {
      if (d.matches(b[0])) {
        var hv = tinggiLihat();
        var h = Math.min(hv * b[1], b[2]);
        d.style.setProperty('max-height', h + 'px', 'important');
        d.style.setProperty('height', 'auto', 'important');
        d.style.setProperty('bottom', 'auto', 'important');
        d.style.setProperty('margin', '0 auto', 'important');
        var nyata = d.getBoundingClientRect().height || h;
        var off = window.visualViewport ? window.visualViewport.offsetTop : 0;
        d.style.setProperty('top', Math.max(12, off + (hv - nyata) / 2) + 'px', 'important');
      }
    });
  };
  var pasKanSemua = function () { Array.prototype.forEach.call(document.querySelectorAll('dialog[open]'), pasKan); };
  if (window.HTMLDialogElement) {
    var asliShow = HTMLDialogElement.prototype.showModal;
    HTMLDialogElement.prototype.showModal = function () { asliShow.apply(this, arguments); pasKan(this); };
  }
  window.addEventListener('resize', pasKanSemua);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', pasKanSemua);

  var $ = function (id) { return document.getElementById(id); };
  var norm = function (s) {
    return (s || '').toLowerCase()
      .replace(/[ً-ٰٟـ]/g, '')
      .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه');
  };
  var topOf = function (el) { return el.getBoundingClientRect().top + window.scrollY; };
  var latest = function (els, y) {
    var cur = -1;
    for (var i = 0; i < els.length; i++) { if (topOf(els[i]) <= y) cur = i; else break; }
    return cur;
  };

  /* ---------- popup posisi ---------- */
  var crumb = $('crumb-bar');
  if (crumb) {
    var pathEl = crumb.querySelector('.crumb__path');
    var pageEl = crumb.querySelector('.crumb__page');
    crumb.removeAttribute('aria-hidden');
    crumb.setAttribute('role', 'button');
    crumb.setAttribute('tabindex', '0');
    crumb.setAttribute('aria-haspopup', 'dialog');
    crumb.setAttribute('title', 'Lihat posisi saat ini');

    var dlg = document.createElement('dialog');
    dlg.className = 'pos-modal';
    dlg.setAttribute('aria-label', 'Posisi saat ini');
    dlg.innerHTML =
      '<div class="pos__head"><h2>Posisi saat ini</h2><button type="button" class="pos__x" aria-label="Tutup">&times;</button></div>' +
      '<div class="pos__body">' +
        '<div class="pos__levels"></div>' +
        '<div class="pos__row"></div>' +
        '<div><div class="pos__pct"><span>Progres membaca</span><b></b></div><div class="pos__bar"><i></i></div></div>' +
        '<div class="pos__acts">' +
          '<button type="button" class="pos__btn pos__btn--utama" data-act="toc">Buka Fihris (Daftar Isi)</button>' +
          '<button type="button" class="pos__btn" data-act="prev">&larr; Bab sebelumnya</button>' +
          '<button type="button" class="pos__btn" data-act="next">Bab berikutnya &rarr;</button>' +
          '<button type="button" class="pos__btn" data-act="top" style="grid-column:1/-1">Ke awal halaman</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(dlg);

    var levels = dlg.querySelector('.pos__levels');
    var row = dlg.querySelector('.pos__row');
    var bar = dlg.querySelector('.pos__bar i');
    var pct = dlg.querySelector('.pos__pct b');
    var btn = function (a) { return dlg.querySelector('[data-act="' + a + '"]'); };
    var tocBtn = $('btn-toc');
    if (!tocBtn) btn('toc').hidden = true;

    var babs = Array.prototype.slice.call(document.querySelectorAll('header.bab, h2.pasal__judul'));
    var LABEL = ['Bab', 'Bagian', 'Sub-bagian'];

    var fill = function () {
      var parts = (pathEl ? pathEl.textContent : '').split(' › ').filter(Boolean);
      levels.innerHTML = '';
      parts.forEach(function (t, i) {
        var d = document.createElement('div');
        d.className = 'pos__lv';
        var s = document.createElement('small'); s.textContent = LABEL[Math.min(i, 2)];
        var v = document.createElement('span'); v.textContent = t;
        if (/[؀-ۿ]/.test(t) && !/[A-Za-z]/.test(t)) v.className = 'ar';
        d.appendChild(s); d.appendChild(v); levels.appendChild(d);
      });
      row.innerHTML = '';
      var page = pageEl && pageEl.style.display !== 'none' ? pageEl.textContent.trim() : '';
      if (page) row.insertAdjacentHTML('beforeend', '<span class="pos__chip">Halaman <b>' + page.replace(/^Hlm\.\s*/, '') + '</b></span>');
      var idx = latest(babs, window.scrollY + 96);
      if (babs.length > 1 && idx >= 0) row.insertAdjacentHTML('beforeend', '<span class="pos__chip">Bab ke <b>' + (idx + 1) + '</b> dari <b>' + babs.length + '</b></span>');
      var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      var p = Math.max(0, Math.min(100, Math.round(window.scrollY / max * 100)));
      bar.style.width = p + '%';
      pct.textContent = p + '%';
      btn('prev').hidden = btn('next').hidden = babs.length < 2;
      btn('prev').disabled = idx <= 0;
      btn('next').disabled = idx >= babs.length - 1;
      dlg._idx = idx;
    };
    var openPos = function () { fill(); dlg.showModal(); };
    crumb.addEventListener('click', openPos);
    crumb.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPos(); } });

    dlg.addEventListener('click', function (e) {
      var r = dlg.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) { dlg.close(); return; }
      var t = e.target.closest('button');
      if (!t) return;
      if (t.classList.contains('pos__x')) { dlg.close(); return; }
      var act = t.getAttribute('data-act');
      if (act === 'toc') { dlg.close(); if (tocBtn) tocBtn.click(); }
      else if (act === 'top') { dlg.close(); window.scrollTo({ top: 0 }); }
      else if (act === 'prev' || act === 'next') {
        var i = dlg._idx + (act === 'next' ? 1 : -1);
        if (i >= 0 && i < babs.length) { dlg.close(); window.scrollTo({ top: topOf(babs[i]) - 16 }); }
      }
    });
  }

  /* ---------- fihris: pencarian + penanda posisi sekarang ---------- */
  var toc = $('fihris');
  var tocDlg = $('fihris-modal');
  if (toc && tocDlg) {
    tocDlg.classList.add('modal--wide');
    document.body.appendChild(tocDlg); /* sama seperti panel pengaturan: langsung di bawah body */

    /* Halaman lama punya fihris "datar" (ol > li > a + .toc__id + ul). Samakan jadi kartu bab. */
    var flat = toc.querySelector('ol.toc');
    if (flat && !flat.querySelector('.toc__bab')) {
      var mk = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
      var split = function (idEl) {
        var m = idEl && idEl.querySelector('.toc__meta');
        var meta = m ? m.textContent.replace(/^[\s\u00b7]+/, '').trim() : '';
        var t = '';
        if (idEl) Array.prototype.forEach.call(idEl.childNodes, function (nd) { if (nd !== m) t += nd.textContent; });
        return { t: t.trim(), meta: meta };
      };
      Array.prototype.slice.call(flat.children).forEach(function (li, i) {
        var a = li.querySelector(':scope > a.toc__ar');
        var top = split(li.querySelector(':scope > .toc__id'));
        var subUl = li.querySelector(':scope > ul');
        var subs = subUl ? Array.prototype.slice.call(subUl.children) : [];
        var card = mk('li', 'toc__bab');
        var det = document.createElement('details');
        var sum = document.createElement('summary');
        sum.appendChild(mk('span', 'toc__no', String(i + 1)));
        if (a) { var link = a.cloneNode(true); sum.appendChild(link); }
        sum.appendChild(mk('span', 'toc__id', top.t));
        sum.appendChild(mk('span', 'toc__meta', [top.meta, subs.length ? subs.length + ' bagian' : ''].filter(Boolean).join(' \u00b7 ')));
        det.appendChild(sum);
        if (subs.length) {
          var sec = mk('div', 'toc__sec'), ol = document.createElement('ol');
          subs.forEach(function (sl) {
            var sa = sl.querySelector('a.toc__ar'); if (!sa) return;
            var p = split(sl.querySelector('.toc__id'));
            var item = document.createElement('li'), ia = document.createElement('a');
            ia.setAttribute('href', sa.getAttribute('href'));
            ia.appendChild(mk('span', 'toc__t', p.t));
            var ar = mk('span', 'toc__a', sa.textContent); ar.setAttribute('lang', 'ar'); ia.appendChild(ar);
            if (p.meta) ia.appendChild(mk('span', 'toc__ref', p.meta));
            item.appendChild(ia); ol.appendChild(item);
          });
          sec.appendChild(ol); det.appendChild(sec);
        }
        card.appendChild(det);
        flat.replaceChild(card, li);
      });
    }

    var headEl = toc.querySelector('.daftar-isi__head');
    if (!headEl) {
      headEl = document.createElement('div'); headEl.className = 'daftar-isi__head';
      var h = toc.querySelector('.daftar-isi__judul');
      toc.insertBefore(headEl, toc.firstChild);
      if (h) headEl.appendChild(h);
      var tg = document.createElement('button');
      tg.type = 'button'; tg.className = 'toc__btn'; tg.id = 'toc-toggle'; tg.setAttribute('data-open', '0'); tg.textContent = 'Buka semua';
      headEl.appendChild(tg);
      tg.addEventListener('click', function () {
        var open = tg.getAttribute('data-open') !== '1';
        toc.querySelectorAll('details').forEach(function (d) { d.open = open; });
        tg.setAttribute('data-open', open ? '1' : '0');
        tg.textContent = open ? 'Tutup semua' : 'Buka semua';
      });
    }
    toc.addEventListener('click', function (e) { if (e.target.closest('a[href^="#"]')) tocDlg.close(); });

    var list = toc.querySelector('.toc');
    var bars = Array.prototype.slice.call(toc.querySelectorAll('.toc__bab'));

    var tools = document.createElement('div');
    tools.className = 'toc__tools';
    tools.innerHTML = '<input type="search" class="toc__cari" placeholder="Cari di fihris…" aria-label="Cari di fihris" autocomplete="off">';
    headEl.insertAdjacentElement('afterend', tools);
    var input = tools.querySelector('input');
    var kosong = document.createElement('li');
    kosong.className = 'toc__kosong'; kosong.hidden = true; kosong.textContent = 'Tidak ada yang cocok.';
    list.appendChild(kosong);

    var rows = bars.map(function (li) {
      var subs = Array.prototype.slice.call(li.querySelectorAll('.toc__sec li'));
      return {
        li: li,
        own: norm((li.querySelector('summary') || {}).textContent),
        subs: subs.map(function (s) { return { li: s, text: norm(s.textContent) }; })
      };
    });

    var filter = function () {
      var q = norm(input.value.trim());
      var terms = q ? q.split(/\s+/) : [];
      var any = false;
      rows.forEach(function (r) {
        if (!terms.length) {
          r.li.hidden = false; r.subs.forEach(function (s) { s.li.hidden = false; });
          any = true; return;
        }
        var ownHit = terms.every(function (t) { return r.own.indexOf(t) > -1; });
        var subHit = 0;
        r.subs.forEach(function (s) {
          var hit = terms.every(function (t) { return (s.text + ' ' + r.own).indexOf(t) > -1; });
          s.li.hidden = !(hit || ownHit);
          if (hit || ownHit) subHit++;
        });
        var show = ownHit || subHit > 0;
        r.li.hidden = !show;
        if (show) { any = true; var d = r.li.querySelector('details'); if (d) d.open = true; }
      });
      kosong.hidden = any;
    };
    input.addEventListener('input', filter);

    var marks = function () {
      var y = window.scrollY + 120;
      var babLinks = bars.map(function (li) { var a = li.querySelector('.toc__ar'); return a ? document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))) : null; });
      var bi = -1;
      babLinks.forEach(function (el, i) { if (el && topOf(el) <= y) bi = i; });
      bars.forEach(function (li, i) { li.classList.toggle('is-now', i === bi); });
      toc.querySelectorAll('.toc__sec li').forEach(function (s) { s.classList.remove('is-now'); });
      var subLinks = Array.prototype.slice.call(toc.querySelectorAll('.toc__sec a[href^="#"]'));
      var cur = null;
      subLinks.forEach(function (a) {
        var el = document.getElementById(a.getAttribute('href').slice(1));
        if (el && topOf(el) <= y) cur = a;
      });
      if (cur) cur.parentNode.classList.add('is-now');
      return { bab: bi >= 0 ? bars[bi] : null, sub: cur };
    };

    var openBtn = $('btn-toc');
    if (openBtn) openBtn.addEventListener('click', function () {
      input.value = ''; filter();
      var m = marks();
      if (m.bab) {
        var d = m.bab.querySelector('details'); if (d) d.open = true;
        setTimeout(function () { (m.sub ? m.sub.parentNode : m.bab).scrollIntoView({ block: 'center' }); }, 30);
      }
    });
  }
})();

/* Tombol "?" (kode tampilan): dibuat otomatis di halaman yang belum punya, dari jenis teks yang ada di halaman. */
(function () {
  'use strict';
  if (document.getElementById('btn-legend')) return;
  var wrap = document.querySelector('.isi__wrap');
  if (!wrap) return;
  var has = function (s) { return !!wrap.querySelector(s); };
  var demo = function (cls, ar) { return '<div class="ayat ' + cls + ' lg-demo"><p class="ar" lang="ar">' + ar + '</p></div>'; };
  var E = [];
  if (has('.kata')) {
    E.push(['<span class="lg-kata"><span class="kata"><span class="ar" lang="ar">كَلِمَةٌ</span><span class="id">kata</span></span></span>', 'Kata Arab, dengan arti Indonesia miring di bawahnya']);
    E.push(['<span style="font-size:1.6rem;line-height:1;color:var(--heading,#1f4d3a)">&larr;</span>', 'Satu baris maksimal 7 kata, dibaca dari kanan ke kiri']);
  } else {
    if (has('.ayat:not([class~="quran"]):not([class~="footnote-row"]):not([class~="list-item"]):not([class~="poem"]):not([class~="numbered"])')) E.push([demo('', 'الشَّرْحُ'), 'Isi &mdash; penjelasan materi, Arab di atas dan terjemah di bawahnya']);
    if (has('.ayat.quran')) E.push([demo('quran', 'آيَةٌ'), 'Ayat Al-Qur&rsquo;an atau dalil']);
    if (has('.ayat.poem')) E.push([demo('poem', 'شِعْرٌ'), 'Syair &mdash; contoh bait']);
    if (has('.ayat.list-item')) E.push([demo('list-item', 'نُقْطَةٌ'), 'Poin &mdash; daftar dan butir materi']);
    if (has('.ayat.numbered')) E.push([demo('numbered', 'بَنْدٌ'), 'Butir bernomor']);
    if (has('.ayat.footnote-row')) E.push([demo('footnote-row', 'حَاشِيَةٌ'), 'Catatan kaki &mdash; keterangan tambahan']);
    if (has('.ayat .ref')) E.push(['<span class="ayat lg-ref"><span class="ar ref" lang="ar">[البقرة: ٢]</span></span>', 'Rujukan &mdash; nama surat dan nomor ayat atau sumber']);
  }
  if (!E.length) return;

  var fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'fab fab--legend'; fab.id = 'btn-legend'; fab.title = 'Kode Tampilan'; fab.setAttribute('aria-label', 'Kode Tampilan');
  fab.setAttribute('aria-haspopup', 'dialog'); fab.textContent = '?';
  document.body.appendChild(fab);
  var dlg = document.createElement('dialog');
  dlg.className = 'lg-modal'; dlg.setAttribute('aria-label', 'Kode Tampilan');
  dlg.innerHTML = '<div class="lg__head"><h2>Kode Tampilan</h2><button type="button" class="lg__x" aria-label="Tutup">&times;</button></div>' +
    '<ul class="lg__list">' + E.map(function (e) { return '<li><div class="lg__sw">' + e[0] + '</div><span class="lg__t">' + e[1] + '</span></li>'; }).join('') + '</ul>';
  document.body.appendChild(dlg);
  fab.addEventListener('click', function () { dlg.showModal(); });
  dlg.addEventListener('click', function (e) {
    var r = dlg.getBoundingClientRect();
    if (e.target.closest('.lg__x') || e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
  });
})();

/* Tombol "Pilih Halaman": daftar semua halaman (Hlm.) dengan kotak centang, lalu salin atau kirim teksnya
   (Arab saja, Indonesia saja, atau keduanya) ke papan klip, Claude, ChatGPT, dan lainnya. */
(function () {
  'use strict';
  var wrap = document.querySelector('.isi__wrap');
  if (!wrap || !document.createRange) return;

  /* ---------- 1. penanda halaman -> daftar halaman ---------- */
  var angka = function (el) { var m = (el.textContent || '').match(/(\d+)\s*$/); return m ? parseInt(m[1], 10) : null; };
  var penanda = Array.prototype.slice.call(wrap.querySelectorAll('.hal, .hal-awal')).map(function (el) {
    return { el: el, n: angka(el), akhir: el.classList.contains('hal--akhir') };
  }).filter(function (m) { return m.n !== null; });
  if (!penanda.length) return;

  var SEL_AR = 'p.ar, h2.bab__ar, h2.pasal__judul, h3.bagian__judul, h3.sub, h4.sub__judul, .ringkasan__ar';
  var SEL_ID = 'p.id, p.bab__id, .judul__id, .sub__id, .ringkasan__id';
  var HARAKAT = /[ً-ْٰٕ]/g;

  var adaIsi = function (frag) { return !!frag.querySelector('.ar, .id, .shatr'); };
  var rentang = function (dari, sampai) {
    var r = document.createRange();
    if (dari) r.setStartAfter(dari); else r.setStart(wrap, 0);
    if (sampai) r.setEndBefore(sampai); else r.setEndAfter(wrap.lastChild);
    var frag = r.cloneContents();
    Array.prototype.forEach.call(frag.querySelectorAll('dialog, script, style, nav, button, .catatan, .legend, .toc, mark'), function (x) { x.remove(); });
    return frag;
  };
  /* awal isi sebelum penanda pertama: lewati header, catatan, dan dialog di bagian atas */
  var awalIsi = null;
  Array.prototype.forEach.call(wrap.querySelectorAll('dialog, .catatan, .isi__ket, .isi__judul'), function (x) {
    if (x.compareDocumentPosition(penanda[0].el) & Node.DOCUMENT_POSITION_FOLLOWING) awalIsi = x;
  });

  var halaman = [];
  var tambah = function (n, frag) {
    if (n === null || n < 1 || !adaIsi(frag)) return;
    for (var i = 0; i < halaman.length; i++) if (halaman[i].n === n) { halaman[i].frags.push(frag); return; }
    halaman.push({ n: n, frags: [frag] });
  };
  for (var i = -1; i < penanda.length; i++) {
    var a = i >= 0 ? penanda[i] : null;
    var b = i + 1 < penanda.length ? penanda[i + 1] : null;
    var frag = rentang(a ? a.el : awalIsi, b ? b.el : null);
    var n;
    if (a && !a.akhir) n = a.n;                       /* sesudah penanda awal: halaman itu */
    else if (b && b.akhir) n = b.n;                   /* sebelum penanda akhir: halaman itu */
    else if (b && !b.akhir) n = b.n - 1;              /* sisa sebelum penanda awal pertama */
    else n = a ? a.n + 1 : null;
    tambah(n, frag);
  }
  if (!halaman.length) return;
  halaman.sort(function (x, y) { return x.n - y.n; });

  /* ---------- 2. ambil teks ---------- */
  var bersih = function (t) { return t.replace(/[ \t ]+/g, ' ').replace(/ *\n */g, '\n').trim(); };
  var teksEl = function (el) {
    var c = el.cloneNode(true);
    Array.prototype.forEach.call(c.querySelectorAll('br'), function (br) { br.replaceWith('\n'); });
    var sh = c.querySelectorAll('.shatr');
    if (sh.length) Array.prototype.forEach.call(sh, function (x, k) { if (k) x.insertAdjacentText('beforebegin', '    '); });
    return bersih(c.textContent);
  };
  /* baris tiap halaman: [{t:'ar'|'id', s:'...'}] sesuai urutan di halaman */
  var baris = function (h) {
    if (h.baris) return h.baris;
    var out = [];
    h.frags.forEach(function (f) {
      Array.prototype.forEach.call(f.querySelectorAll(SEL_AR + ', ' + SEL_ID), function (el) {
        var t = el.matches(SEL_AR) ? 'ar' : 'id';
        var s = teksEl(el);
        if (s) out.push({ t: t, s: s });
      });
    });
    h.baris = out; return out;
  };
  var cuplikan = function (h) {
    var b = baris(h).filter(function (x) { return x.t === 'ar'; });
    return b.length ? b[0].s.replace(HARAKAT, '').slice(0, 70) : '';
  };

  /* ---------- 3. tombol dan popup ---------- */
  var fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'fab fab--ph'; fab.id = 'btn-ph';
  fab.title = 'Pilih halaman'; fab.setAttribute('aria-label', 'Pilih halaman'); fab.setAttribute('aria-haspopup', 'dialog');
  fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="m8.5 12.2 2.4 2.4 4.6-5"/></svg>';
  document.body.appendChild(fab);

  var PROMPT = [
    ['', 'Tanpa instruksi (teks saja)'],
    ['Jelaskan isi teks berikut dengan bahasa Indonesia yang sederhana dan runtut. Sebutkan istilah penting beserta artinya.', 'Jelaskan isinya'],
    ['Terjemahkan teks Arab berikut ke bahasa Indonesia yang natural dan mudah dipahami. Pertahankan istilah teknis, dan beri catatan pada bagian yang sulit.', 'Terjemahkan teks Arab'],
    ['Periksa terjemahan Indonesia berikut terhadap teks Arabnya. Tunjukkan bagian yang keliru atau kurang tepat, lalu beri perbaikannya.', 'Koreksi terjemahan'],
    ['Buatkan 10 soal pilihan ganda dengan 2 pilihan jawaban dari teks berikut, lengkap dengan kunci jawaban dan penjelasan singkat.', 'Buat soal pilihan ganda'],
    ['Ringkas teks berikut menjadi poin-poin utama yang mudah dihafal.', 'Ringkas'],
    ['Lakukan i\'rab dan analisis nahwu/sharaf untuk teks Arab berikut, kalimat demi kalimat.', 'I\'rab dan analisis nahwu'],
    ['Jelaskan aspek balaghah (ilmu ma\'ani, bayan, badi\') pada teks berikut beserta contohnya.', 'Analisis balaghah'],
    ['__kustom__', 'Instruksi sendiri…']
  ];
  var simpan = function (k, v) { try { localStorage.setItem('ph.' + k, v); } catch (e) { /* abaikan */ } };
  var muat = function (k, d) { try { var v = localStorage.getItem('ph.' + k); return v === null ? d : v; } catch (e) { return d; } };

  var dlg = document.createElement('dialog');
  dlg.className = 'ph-modal'; dlg.setAttribute('aria-label', 'Pilih halaman');
  dlg.innerHTML =
    '<div class="ph__head"><h2>Pilih Halaman <small class="ph__jml"></small></h2><button type="button" class="ph__x" aria-label="Tutup">&times;</button></div>' +
    '<div class="ph__cepat">' +
      '<div class="ph__baris">' +
        '<button type="button" class="ph__chip" data-a="semua">Semua</button>' +
        '<button type="button" class="ph__chip" data-a="kosong">Kosongkan</button>' +
        '<button type="button" class="ph__chip" data-a="balik">Balik</button>' +
        '<button type="button" class="ph__chip" data-a="sini">Halaman saat ini</button>' +
        '<button type="button" class="ph__chip" data-a="lanjut">+ Lanjut 5 hlm</button>' +
      '</div>' +
      '<div class="ph__baris ph__rentang">' +
        '<label>Dari <select class="ph__dari" aria-label="Dari halaman"></select></label>' +
        '<label>sampai <select class="ph__sampai" aria-label="Sampai halaman"></select></label>' +
        '<button type="button" class="ph__chip ph__chip--utama" data-a="rentang">Centang rentang</button>' +
        '<button type="button" class="ph__chip" data-a="lepas">Lepas rentang</button>' +
      '</div>' +
      '<p class="ph__tip">Tips: tahan Shift lalu klik dua halaman untuk mencentang semua di antaranya.</p>' +
    '</div>' +
    '<ul class="ph__daftar"></ul>' +
    '<div class="ph__aksi" hidden>' +
      '<div class="ph__opsi">' +
        '<label>Isi <select class="ph__fmt" aria-label="Isi yang disalin">' +
          '<option value="ar">Arab saja</option><option value="id">Indonesia saja</option><option value="dua">Arab + Indonesia (berselang)</option><option value="arid">Arab dulu, lalu Indonesia</option>' +
        '</select></label>' +
        '<label class="ph__cek"><input type="checkbox" class="ph__tanpa"> Tanpa harakat</label>' +
        '<label class="ph__cek"><input type="checkbox" class="ph__hlm" checked> Sertakan nomor halaman</label>' +
      '</div>' +
      '<div class="ph__opsi"><label>Instruksi untuk AI <select class="ph__prompt" aria-label="Instruksi untuk AI"></select></label></div>' +
      '<textarea class="ph__kustom" rows="3" placeholder="Tulis instruksi sendiri, misalnya: Jelaskan i\'rab kalimat berikut…" hidden></textarea>' +
      '<div class="ph__tombol">' +
        '<button type="button" class="ph__btn ph__btn--utama" data-k="salin">Salin teks</button>' +
        '<button type="button" class="ph__btn" data-k="claude">Buka di Claude</button>' +
        '<button type="button" class="ph__btn" data-k="chatgpt">Buka di ChatGPT</button>' +
        '<button type="button" class="ph__btn" data-k="perplexity">Buka di Perplexity</button>' +
        '<button type="button" class="ph__btn" data-k="unduh">Unduh .txt</button>' +
        '<button type="button" class="ph__btn" data-k="bagi">Bagikan…</button>' +
        '<button type="button" class="ph__btn" data-k="lihat">Lihat hasil</button>' +
      '</div>' +
      '<p class="ph__info" aria-live="polite"></p>' +
      '<pre class="ph__pratinjau" hidden></pre>' +
    '</div>';
  document.body.appendChild(dlg);

  var q = function (s) { return dlg.querySelector(s); };
  var daftar = q('.ph__daftar'), aksi = q('.ph__aksi'), jml = q('.ph__jml'), info = q('.ph__info');
  var dari = q('.ph__dari'), sampai = q('.ph__sampai'), fmt = q('.ph__fmt'), tanpa = q('.ph__tanpa'), hlm = q('.ph__hlm');
  var sel = q('.ph__prompt'), kustom = q('.ph__kustom'), pra = q('.ph__pratinjau');
  var kotak = [], terakhir = -1;

  PROMPT.forEach(function (p, k) { var o = document.createElement('option'); o.value = k; o.textContent = p[1]; sel.appendChild(o); });
  halaman.forEach(function (h, k) {
    var li = document.createElement('li'); li.className = 'ph__item';
    var lb = document.createElement('label');
    var cb = document.createElement('input'); cb.type = 'checkbox'; cb.value = k; cb.setAttribute('aria-label', 'Halaman ' + h.n);
    var no = document.createElement('b'); no.textContent = 'Hlm. ' + h.n;
    var cp = document.createElement('span'); cp.className = 'ph__cup'; cp.setAttribute('lang', 'ar'); cp.textContent = cuplikan(h);
    lb.appendChild(cb); lb.appendChild(no); lb.appendChild(cp);
    var go = document.createElement('button'); go.type = 'button'; go.className = 'ph__go'; go.title = 'Lompat ke halaman ini'; go.setAttribute('aria-label', 'Lompat ke halaman ' + h.n); go.setAttribute('data-k', k); go.innerHTML = '&#8599;';
    li.appendChild(lb); li.appendChild(go); daftar.appendChild(li);
    kotak.push(cb);
    [dari, sampai].forEach(function (s2) { var o = document.createElement('option'); o.value = k; o.textContent = h.n; s2.appendChild(o); });
  });
  sampai.value = String(halaman.length - 1);

  var terpilih = function () { return kotak.map(function (c, k) { return c.checked ? k : -1; }).filter(function (k) { return k >= 0; }); };
  var segarkan = function () {
    var t = terpilih();
    kotak.forEach(function (c) { c.closest('.ph__item').classList.toggle('is-on', c.checked); });
    jml.textContent = t.length ? t.length + ' dari ' + halaman.length + ' dipilih' : halaman.length + ' halaman';
    aksi.hidden = !t.length; pra.hidden = true; info.textContent = '';
    if (t.length) {
      var h1 = halaman[t[0]].n, h2 = halaman[t[t.length - 1]].n;
      info.textContent = 'Terpilih: ' + (t.length === 1 ? 'Hlm. ' + h1 : 'Hlm. ' + h1 + '–' + h2 + ' (' + t.length + ' halaman)');
    }
  };
  var set = function (k0, k1, on) { for (var k = Math.min(k0, k1); k <= Math.max(k0, k1); k++) kotak[k].checked = on; };
  var halamanSekarang = function () {
    var y = window.scrollY + 96, cur = 0;
    penanda.forEach(function (m) { if (m.el.getBoundingClientRect().top + window.scrollY <= y) cur = m.n; });
    var k = 0; halaman.forEach(function (h, i) { if (h.n <= cur) k = i; });
    return k;
  };

  var ambilPrompt = function () {
    var p = PROMPT[parseInt(sel.value, 10)];
    if (!p) return '';
    return p[0] === '__kustom__' ? kustom.value.trim() : p[0];
  };
  var susun = function () {
    var out = [];
    terpilih().forEach(function (k) {
      var h = halaman[k], b = baris(h), f = fmt.value;
      var ar = b.filter(function (x) { return x.t === 'ar'; }).map(function (x) { return x.s; });
      var id = b.filter(function (x) { return x.t === 'id'; }).map(function (x) { return x.s; });
      var bagian;
      if (f === 'ar') bagian = ar; else if (f === 'id') bagian = id;
      else if (f === 'dua') bagian = b.map(function (x) { return x.s; });
      else bagian = ar.concat(['']).concat(id);
      var teks = bagian.join('\n');
      if (tanpa.checked) teks = teks.replace(HARAKAT, '');
      out.push((hlm.checked ? '[Hlm. ' + h.n + ']\n' : '') + teks);
    });
    var isi = out.join('\n\n');
    var p = ambilPrompt();
    return p ? p + '\n\n' + isi : isi;
  };

  var salinKe = function (teks) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(teks);
    return new Promise(function (ok, gagal) {
      var t = document.createElement('textarea'); t.value = teks; t.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
      document.body.appendChild(t); t.select();
      var b = false; try { b = document.execCommand('copy'); } catch (e) { /* abaikan */ }
      t.remove(); b ? ok() : gagal(new Error('gagal'));
    });
  };
  var kabar = function (t) { info.textContent = t; };
  var SITUS = {
    claude: ['Claude', 'https://claude.ai/new', 'q'],
    chatgpt: ['ChatGPT', 'https://chatgpt.com/', 'q'],
    perplexity: ['Perplexity', 'https://www.perplexity.ai/search', 'q']
  };
  var BATAS_URL = 5500;

  dlg.addEventListener('click', function (e) {
    var r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) { dlg.close(); return; }
    var x = e.target.closest('button'); if (!x) return;
    if (x.classList.contains('ph__x')) { dlg.close(); return; }
    var go = x.classList.contains('ph__go') ? parseInt(x.getAttribute('data-k'), 10) : -1;
    if (go >= 0) {
      var m = penanda.filter(function (p) { return p.n === halaman[go].n && !p.akhir; })[0] || penanda.filter(function (p) { return p.n === halaman[go].n; })[0];
      dlg.close();
      if (m) window.scrollTo({ top: m.el.getBoundingClientRect().top + window.scrollY - 70 });
      return;
    }
    var a = x.getAttribute('data-a');
    if (a) {
      var d = parseInt(dari.value, 10), s = parseInt(sampai.value, 10);
      if (a === 'semua') kotak.forEach(function (c) { c.checked = true; });
      else if (a === 'kosong') kotak.forEach(function (c) { c.checked = false; });
      else if (a === 'balik') kotak.forEach(function (c) { c.checked = !c.checked; });
      else if (a === 'sini') { var k = halamanSekarang(); kotak.forEach(function (c) { c.checked = false; }); kotak[k].checked = true; daftar.children[k].scrollIntoView({ block: 'center' }); }
      else if (a === 'lanjut') { var t = terpilih(); var from = t.length ? t[t.length - 1] + 1 : halamanSekarang(); set(from, Math.min(from + 4, kotak.length - 1), true); }
      else if (a === 'rentang') set(d, s, true);
      else if (a === 'lepas') set(d, s, false);
      segarkan(); return;
    }
    var k2 = x.getAttribute('data-k');
    if (!k2) return;
    var teks = susun();
    if (k2 === 'lihat') { pra.textContent = teks; pra.hidden = !pra.hidden; return; }
    if (k2 === 'salin') { salinKe(teks).then(function () { kabar('Tersalin (' + teks.length + ' karakter).'); }, function () { kabar('Gagal menyalin. Gunakan "Lihat hasil" lalu salin manual.'); }); return; }
    if (k2 === 'unduh') {
      var t2 = terpilih(), nama = (document.title.split(' — ')[0] || 'teks').replace(/[\\/:*?"<>|]+/g, '').slice(0, 60).trim();
      var blob = new Blob([teks], { type: 'text/plain;charset=utf-8' }), u = URL.createObjectURL(blob);
      var el = document.createElement('a'); el.href = u; el.download = nama + ' hlm ' + halaman[t2[0]].n + (t2.length > 1 ? '-' + halaman[t2[t2.length - 1]].n : '') + '.txt';
      document.body.appendChild(el); el.click(); el.remove(); setTimeout(function () { URL.revokeObjectURL(u); }, 2000);
      kabar('File .txt diunduh.'); return;
    }
    if (k2 === 'bagi') {
      if (navigator.share) navigator.share({ text: teks }).catch(function () { /* dibatalkan */ });
      else salinKe(teks).then(function () { kabar('Berbagi tidak didukung di browser ini; teks disalin.'); });
      return;
    }
    var st = SITUS[k2]; if (!st) return;
    var lewat = st[2] && encodeURIComponent(teks).length <= BATAS_URL;
    var url = lewat ? st[1] + '?' + st[2] + '=' + encodeURIComponent(teks) : st[1];
    var w = window.open(url, '_blank', 'noopener');
    salinKe(teks).then(function () {
      kabar(lewat ? 'Teks dikirim ke ' + st[0] + ' (juga tersalin).' : 'Teks tersalin. Tempel (Tahan lama atau Ctrl+V) di kolom chat ' + st[0] + '.');
    }, function () { kabar(lewat ? 'Teks dikirim ke ' + st[0] + '.' : 'Gagal menyalin. Gunakan "Lihat hasil" lalu salin manual.'); });
    if (!w) kabar('Pop-up diblokir browser. Izinkan pop-up lalu coba lagi.');
  });
  daftar.addEventListener('click', function (e) {
    var c = e.target.closest('input[type="checkbox"]'); if (!c) return;
    var k = parseInt(c.value, 10);
    if (e.shiftKey && terakhir >= 0) set(terakhir, k, c.checked);
    terakhir = k; segarkan();
  });
  sel.addEventListener('change', function () { kustom.hidden = PROMPT[parseInt(sel.value, 10)][0] !== '__kustom__'; simpan('prompt', sel.value); });
  kustom.addEventListener('input', function () { simpan('kustom', kustom.value); });
  fmt.addEventListener('change', function () { simpan('fmt', fmt.value); });
  tanpa.addEventListener('change', function () { simpan('tanpa', tanpa.checked ? '1' : '0'); });
  hlm.addEventListener('change', function () { simpan('hlm', hlm.checked ? '1' : '0'); });
  fmt.value = muat('fmt', 'ar'); tanpa.checked = muat('tanpa', '0') === '1'; hlm.checked = muat('hlm', '1') === '1';
  sel.value = muat('prompt', '0'); kustom.value = muat('kustom', ''); kustom.hidden = PROMPT[parseInt(sel.value, 10) || 0][0] !== '__kustom__';

  fab.addEventListener('click', function () {
    segarkan(); dlg.showModal();
    var k = halamanSekarang(); if (daftar.children[k]) daftar.children[k].scrollIntoView({ block: 'center' });
  });
})();
