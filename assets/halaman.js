/* Perilaku bersama halaman terjemah: popup posisi dan fihris yang lebih rapi. */
(function () {
  'use strict';

  /* Tinggi popup dihitung dari tinggi layar yang benar-benar terlihat (visualViewport),
     supaya tidak melebihi layar di browser HP yang unit vh/dvh-nya tidak akurat. */
  var BATAS = [['dialog.modal--wide', 0.86, 720], ['dialog.pos-modal', 0.7, 640], ['dialog.lg-modal', 0.7, 560], ['dialog.pg-modal', 0.8, 660]];
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
