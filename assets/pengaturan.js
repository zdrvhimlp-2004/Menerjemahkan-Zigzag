/* Pengaturan teks halaman terjemah: harakat, terjemahan, collapse/expand, cari, baca kitab. */
(function () {
  'use strict';
  var CFG = Object.assign({ collapse: false }, window.PENGATURAN || {});
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var KEY = 'pengaturan:' + location.pathname;
  var HAR = /[ً-ْٰ]/g;
  var norm = function (s) {
    return (s || '').toLowerCase().replace(HAR, '').replace(/ـ/g, '')
      .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه');
  };
  var I = function (c) { return '<i class="fa-solid ' + c + '" aria-hidden="true"></i>'; };

  var S = { harakat: true, terj: 'tampil', collapse: CFG.collapse, rate: 0.9, bacaTerj: false };
  try { var raw = JSON.parse(localStorage.getItem(KEY) || 'null'); if (raw) Object.assign(S, raw); } catch (e) {}
  var save = function () { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };

  var wrapEl = $('.isi__wrap .teks') || $('.isi__wrap') || document.body;
  var toastEl = document.createElement('div');
  toastEl.className = 'pg-toast'; document.body.appendChild(toastEl);
  var toastT = 0;
  var toast = function (t) { toastEl.textContent = t; toastEl.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 2200); };

  /* ======================= HARAKAT ======================= */
  /* satuan teks: .ayat (halaman biasa) atau .baris zigzag (di luar judul) */
  var UNIT = '.ayat, .baris';
  var units = function () { return $$(UNIT).filter(function (el) { return !el.closest('.sec__head, h1, header.bab, h3.sub, .cover'); }); };
  var idTeks = function (u) { return $$('.id', u).map(function (e) { return e.textContent.trim(); }).filter(Boolean).join(' '); };
  var arTexts = [];   // {node, asli}
  var asliMap = new Map();
  (function collect() {
    $$('.ayat .ar, .kata .ar, h2.bab__ar, h3.sub, .ringkasan__ar, .toc__ar, .toc__a, .bab__ar, .sub__ar, .tag__k').forEach(function (el) {
      var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      var n; while ((n = w.nextNode())) { if (/[؀-ۿ]/.test(n.nodeValue) && !asliMap.has(n)) { asliMap.set(n, n.nodeValue); arTexts.push({ node: n, asli: n.nodeValue }); } }
    });
  })();
  function terapkanHarakat() {
    arTexts.forEach(function (o) { o.node.nodeValue = S.harakat ? o.asli : o.asli.replace(HAR, ''); });
  }
  var asliArab = function (ayat) {
    return $$('.ar', ayat).map(function (p) {
      var w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT, null), t = '', n;
      while ((n = w.nextNode())) { t += asliMap.has(n) ? asliMap.get(n) : n.nodeValue; }
      return t;
    }).join(' ');
  };

  /* ======================= TERJEMAHAN ======================= */
  function terapkanTerjemahan() {
    document.body.classList.toggle('t-sembunyi', S.terj === 'sembunyi');
    document.body.classList.toggle('t-klik', S.terj === 'klik');
    if (S.terj !== 'klik') $$('.show-id').forEach(function (a) { a.classList.remove('show-id'); });
  }
  var revealT = new WeakMap();
  document.addEventListener('click', function (e) {
    if (S.terj !== 'klik') return;
    var a = e.target.closest(UNIT);
    if (!a || e.target.closest('a, .sec__head, dialog')) return;
    a.classList.add('show-id');
    clearTimeout(revealT.get(a));
    revealT.set(a, setTimeout(function () { a.classList.remove('show-id'); }, 3000));
  });

  /* ======================= COLLAPSE / EXPAND ======================= */
  var secs = [];
  (function buildSections() {
    var types = [['.bab__judul', null], ['header.bab', null], ['.pasal__judul', null], ['.bagian__judul', null], ['h3.sub', null], ['div.sub', null], ['.sub__judul', null]];
    var present = types.filter(function (t) { return $(t[0], wrapEl); });
    present.forEach(function (t, i) { t[1] = i + 1; });
    if (!present.length) return;
    var sel = present.map(function (t) { return t[0]; }).join(',');
    var levelOf = function (el) { for (var i = 0; i < present.length; i++) if (el.matches(present[i][0])) return present[i][1]; return 0; };
    var COMP = '.judul__id, .sub__id, .bab__id';
    var kids = Array.prototype.slice.call(wrapEl.children);
    var stack = [];
    for (var i = 0; i < kids.length; i++) {
      var c = kids[i];
      if (c.matches(sel)) {
        var L = levelOf(c);
        while (stack.length && stack[stack.length - 1].level >= L) stack.pop();
        var wrap = document.createElement('div'); wrap.className = 'sec'; wrap.setAttribute('data-level', L);
        var body = document.createElement('div'); body.className = 'sec__body';
        var parentBody = stack.length ? stack[stack.length - 1].body : null;
        if (parentBody) parentBody.appendChild(wrap); else wrapEl.insertBefore(wrap, c);
        var heads = [c];
        while (kids[i + 1] && kids[i + 1].matches(COMP)) { heads.push(kids[i + 1]); i++; }
        heads.forEach(function (h) { wrap.appendChild(h); });
        wrap.appendChild(body);
        c.classList.add('sec__head');
        var ch = document.createElement('i'); ch.className = 'fa-solid fa-chevron-down sec__chev'; ch.setAttribute('aria-hidden', 'true'); c.appendChild(ch);
        c.setAttribute('role', 'button'); c.setAttribute('tabindex', '0');
        var sec = { wrap: wrap, head: c, body: body, level: L };
        secs.push(sec); stack.push(sec);
        (function (s) {
          var toggle = function (ev) { if (!document.body.classList.contains('mode-collapse')) return; if (ev.target.closest('a')) return; s.wrap.classList.toggle('is-collapsed'); };
          s.head.addEventListener('click', toggle);
          s.head.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(ev); } });
        })(sec);
      } else if (stack.length) {
        stack[stack.length - 1].body.appendChild(c);
      }
    }
  })();
  function setCollapseAll(v) { secs.forEach(function (s) { s.wrap.classList.toggle('is-collapsed', v); }); }
  function terapkanCollapse(initial) {
    document.body.classList.toggle('mode-collapse', !!S.collapse && secs.length > 0);
    if (initial && S.collapse) setCollapseAll(true);
  }
  function reveal(el) {
    var n = el;
    while (n && n !== document.body) { if (n.classList && n.classList.contains('sec')) n.classList.remove('is-collapsed'); n = n.parentNode; }
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    var t = id && document.getElementById(id);
    if (t) reveal(t);
  }, true);
  window.addEventListener('hashchange', function () { var t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) { reveal(t); t.scrollIntoView(); } });

  /* ======================= CARI ======================= */
  var bar = document.createElement('div');
  bar.className = 'cari-bar';
  bar.innerHTML = I('fa-magnifying-glass') + '<input type="search" placeholder="Cari di halaman ini…" aria-label="Cari" autocomplete="off"><span class="jml"></span>' +
    '<button type="button" data-a="prev" aria-label="Sebelumnya">' + I('fa-chevron-up') + '</button><button type="button" data-a="next" aria-label="Berikutnya">' + I('fa-chevron-down') + '</button><button type="button" data-a="x" aria-label="Tutup">' + I('fa-xmark') + '</button>';
  document.body.appendChild(bar);
  var cInput = $('input', bar), cJml = $('.jml', bar);
  var hits = [], cur = -1, pool = null;
  function buildPool() {
    pool = $$('.ayat, .baris, .sec__head').filter(function (el) { return el.classList.contains('sec__head') || !el.closest('.sec__head, h1, .cover'); }).map(function (el) {
      var ar = $$('.ar', el).map(function (p) { return p.textContent; }).join(' ');
      return { el: el, ar: norm(el.classList.contains('sec__head') ? el.textContent : asliArab(el)), id: idTeks(el).toLowerCase() + ' ' + (el.classList.contains('sec__head') ? el.textContent.toLowerCase() : '') };
    });
  }
  function clearHits() { $$('.cari-hit, .cari-now').forEach(function (e) { e.classList.remove('cari-hit', 'cari-now'); }); hits = []; cur = -1; cJml.textContent = ''; }
  function jump(i) {
    if (!hits.length) return;
    cur = (i + hits.length) % hits.length;
    $$('.cari-now').forEach(function (e) { e.classList.remove('cari-now'); });
    var el = hits[cur]; el.classList.add('cari-now'); reveal(el);
    el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    cJml.textContent = (cur + 1) + ' / ' + hits.length;
  }
  function cari() {
    clearHits();
    var q = cInput.value.trim();
    if (!q) return;
    if (!pool) buildPool();
    var nq = norm(q), lq = q.toLowerCase();
    pool.forEach(function (o) { if (o.ar.indexOf(nq) > -1 || o.id.indexOf(lq) > -1) { o.el.classList.add('cari-hit'); hits.push(o.el); } });
    if (!hits.length) { cJml.textContent = '0'; return; }
    jump(0);
  }
  cInput.addEventListener('input', cari);
  cInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); jump(cur + (e.shiftKey ? -1 : 1)); } else if (e.key === 'Escape') bukaCari(false); });
  bar.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; var a = b.getAttribute('data-a'); if (a === 'prev') jump(cur - 1); else if (a === 'next') jump(cur + 1); else if (a === 'x') bukaCari(false); });
  function bukaCari(v) {
    bar.classList.toggle('is-open', v);
    var sw = $('#pg-cari'); if (sw) sw.checked = v;
    if (v) { setTimeout(function () { cInput.focus(); cInput.select(); }, 30); } else { clearHits(); }
  }

  /* ======================= BACA KITAB ======================= */
  var synth = ('speechSynthesis' in window && 'SpeechSynthesisUtterance' in window) ? window.speechSynthesis : null;
  var voices = [];
  var loadVoices = function () { if (synth) voices = synth.getVoices(); };
  if (synth) { loadVoices(); synth.addEventListener('voiceschanged', loadVoices); }
  var isAr = function (v) { return /^ar([-_]|$)/i.test(v.lang) || /arab|عرب/i.test(v.name); };
  var isId = function (v) { return /^id([-_]|$)/i.test(v.lang); };
  var R = { on: false, paused: false, list: [], i: 0, token: 0, terj: false };
  var player = document.createElement('div');
  player.className = 'pemutar';
  player.innerHTML = '<button type="button" data-a="prev" aria-label="Sebelumnya">' + I('fa-backward-step') + '</button><button type="button" class="utama" data-a="play" aria-label="Jeda / lanjut">' + I('fa-pause') + '</button><button type="button" data-a="next" aria-label="Berikutnya">' + I('fa-forward-step') + '</button><button type="button" data-a="stop" aria-label="Berhenti">' + I('fa-stop') + '</button><span class="info"></span>';
  document.body.appendChild(player);
  var pInfo = $('.info', player), pPlay = $('[data-a="play"]', player);
  var cleanTxt = function (t) { return t.replace(/\.{3}/g, '،').replace(/[«»"]/g, '').replace(/\s+/g, ' ').trim(); };
  function speak(text, lang, done) {
    var my = R.token;
    if (!synth) { setTimeout(done, 300); return; }
    var u = new SpeechSynthesisUtterance(text);
    var pool2 = lang === 'ar' ? voices.filter(isAr) : voices.filter(isId);
    u.lang = lang === 'ar' ? 'ar-SA' : 'id-ID';
    if (pool2[0]) { u.voice = pool2[0]; u.lang = pool2[0].lang; }
    u.rate = lang === 'ar' ? S.rate : 1;
    var finished = false, started = false;
    var fin = function () { if (finished || my !== R.token) return; finished = true; clearTimeout(guard); clearTimeout(boot); done(); };
    var guard = setTimeout(fin, 5000 + text.length * 140);
    var boot = setTimeout(function () { if (!started && !synth.speaking) fin(); }, 2500);
    u.onstart = function () { started = true; };
    u.onend = fin; u.onerror = fin;
    synth.speak(u);
  }
  function stopSpeech() { R.token++; if (synth) { try { synth.cancel(); } catch (e) {} } }
  function tandai(a) { $$('.is-reading').forEach(function (e) { e.classList.remove('is-reading'); }); if (a) a.classList.add('is-reading'); }
  function bacaBaris() {
    if (!R.on || R.paused) return;
    if (R.i >= R.list.length) { berhenti(true); return; }
    var a = R.list[R.i];
    reveal(a); tandai(a);
    a.scrollIntoView({ block: 'center', behavior: 'smooth' });
    pInfo.textContent = (R.i + 1) + ' / ' + R.list.length;
    var my = ++R.token, idx = R.i;
    var lanjut = function () { if (my === R.token && R.on && !R.paused) { R.i = idx + 1; bacaBaris(); } };
    var ar = cleanTxt(asliArab(a));
    var idT = idTeks(a);
    synthDelay(function () {
      speak(ar, 'ar', function () {
        if (R.terj && idT) speak(idT, 'id', lanjut); else lanjut();
      });
    });
  }
  function synthDelay(fn) { setTimeout(fn, 40); }
  function mulaiBaca(terj) {
    if (!synth) { toast('Browser ini tidak mendukung suara.'); return; }
    stopSpeech();
    R.list = units(); R.terj = !!terj; R.on = true; R.paused = false;
    var y = window.innerHeight * 0.25, start = 0;
    for (var i = 0; i < R.list.length; i++) { var r = R.list[i].getClientRects(); if (r.length && r[0].top >= 0) { start = i; break; } }
    R.i = start;
    player.classList.add('is-open'); setIcon(pPlay, 'fa-pause');
    if (voices.length && !voices.some(isAr)) toast('Suara Arab belum terpasang di perangkat; bacaan bisa tidak terdengar.');
    bacaBaris();
  }
  function setIcon(btn, c) { btn.innerHTML = I(c); }
  function berhenti(selesai) { R.on = false; R.paused = false; stopSpeech(); tandai(null); player.classList.remove('is-open'); if (selesai) toast('Selesai dibaca'); }
  player.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var a = b.getAttribute('data-a');
    if (a === 'stop') berhenti(false);
    else if (a === 'play') { if (R.paused) { R.paused = false; setIcon(pPlay, 'fa-pause'); bacaBaris(); } else { R.paused = true; stopSpeech(); setIcon(pPlay, 'fa-play'); } }
    else if (a === 'next') { stopSpeech(); R.i = Math.min(R.list.length - 1, R.i + 1); R.paused = false; setIcon(pPlay, 'fa-pause'); bacaBaris(); }
    else if (a === 'prev') { stopSpeech(); R.i = Math.max(0, R.i - 1); R.paused = false; setIcon(pPlay, 'fa-pause'); bacaBaris(); }
  });
  document.addEventListener('click', function (e) {
    if (!R.on) return;
    var a = e.target.closest(UNIT);
    if (!a || e.target.closest('a')) return;
    var i = R.list.indexOf(a);
    if (i > -1) { stopSpeech(); R.i = i; R.paused = false; setIcon(pPlay, 'fa-pause'); bacaBaris(); }
  });

  /* ======================= PANEL ======================= */
  var fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'fab fab--set'; fab.id = 'btn-set'; fab.title = 'Pengaturan teks'; fab.setAttribute('aria-label', 'Pengaturan teks');
  fab.innerHTML = I('fa-gear'); document.body.appendChild(fab);
  var dlg = document.createElement('dialog');
  dlg.className = 'pg-modal'; dlg.setAttribute('aria-label', 'Pengaturan teks');
  dlg.innerHTML =
    '<div class="pg__head"><h2>' + I('fa-gear') + ' Pengaturan Teks</h2><button type="button" class="pg__x" aria-label="Tutup">' + I('fa-xmark') + '</button></div>' +
    '<div class="pg__body">' +
      '<div class="pg__grup" id="pg-grup-fs"><h3>Tampilan</h3><button type="button" class="pg__btn" id="pg-fs" style="width:100%"></button></div>' +
      '<div class="pg__grup"><h3>Teks Arab</h3>' +
        '<div class="pg__baris"><div>Tampilkan harakat<small>Matikan untuk membaca tanpa harakat</small></div><label class="pg__sw"><input type="checkbox" id="pg-harakat"><span></span></label></div></div>' +
      '<div class="pg__grup"><h3>Terjemahan</h3><div class="pg__radio">' +
        '<label><input type="radio" name="pg-terj" value="tampil"> Selalu tampil</label>' +
        '<label><input type="radio" name="pg-terj" value="klik"> Muncul saat diklik saja (3 detik)</label>' +
        '<label><input type="radio" name="pg-terj" value="sembunyi"> Tanpa terjemahan</label></div></div>' +
      '<div class="pg__grup"><h3>Bab dan Sub-bab</h3>' +
        '<div class="pg__baris"><div>Mode collapse<small>Klik judul untuk membuka atau menutup</small></div><label class="pg__sw"><input type="checkbox" id="pg-collapse"><span></span></label></div>' +
        '<div class="pg__btns" style="margin-top:.5rem"><button type="button" class="pg__btn" id="pg-buka">' + I('fa-angles-down') + ' Buka semua</button><button type="button" class="pg__btn" id="pg-tutup">' + I('fa-angles-up') + ' Tutup semua</button></div></div>' +
      '<div class="pg__grup"><h3>Pencarian</h3>' +
        '<div class="pg__baris"><div>Bar pencarian<small>Cari kata Arab (tanpa harakat) atau Indonesia</small></div><label class="pg__sw"><input type="checkbox" id="pg-cari"><span></span></label></div></div>' +
      '<div class="pg__grup"><h3>Baca kitab (suara browser)</h3>' +
        '<div class="pg__btns"><button type="button" class="pg__btn pg__btn--utama" id="pg-baca">' + I('fa-volume-high') + ' Baca kitab</button><button type="button" class="pg__btn pg__btn--utama" id="pg-baca-t">' + I('fa-language') + ' Baca + terjemahan</button></div>' +
        '<div class="pg__baris" style="margin-top:.5rem"><div>Kecepatan baca</div><select class="pg__sel" id="pg-rate"><option value="0.7">Pelan</option><option value="0.9">Sedang</option><option value="1.1">Normal</option><option value="1.4">Cepat</option><option value="1.8">Cepat sekali</option></select></div></div>' +
    '</div>';
  document.body.appendChild(dlg);
  /* layar penuh */
  var de = document.documentElement;
  var fsReq = de.requestFullscreen || de.webkitRequestFullscreen;
  var fsBtn = $('#pg-fs', dlg);
  var fsOn = function () { return !!(document.fullscreenElement || document.webkitFullscreenElement); };
  var fsLabel = function () { fsBtn.innerHTML = fsOn() ? I('fa-compress') + ' Keluar layar penuh' : I('fa-expand') + ' Layar penuh'; };
  if (fsReq) {
    fsLabel();
    fsBtn.addEventListener('click', function () {
      try {
        if (fsOn()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
        else { var r = fsReq.call(de); if (r && r.catch) r.catch(function () { toast('Layar penuh tidak diizinkan di sini.'); }); }
      } catch (e) { toast('Layar penuh tidak didukung.'); }
    });
    document.addEventListener('fullscreenchange', fsLabel);
    document.addEventListener('webkitfullscreenchange', fsLabel);
  } else { $('#pg-grup-fs', dlg).hidden = true; }
  fab.addEventListener('click', function () { sinkron(); dlg.showModal(); });
  dlg.addEventListener('click', function (e) {
    var r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) { dlg.close(); return; }
    if (e.target.closest('.pg__x')) dlg.close();
  });
  function sinkron() {
    $('#pg-harakat').checked = S.harakat;
    $$('input[name="pg-terj"]', dlg).forEach(function (r) { r.checked = r.value === S.terj; });
    $('#pg-collapse').checked = !!S.collapse;
    $('#pg-rate').value = String(S.rate);
    $('#pg-cari').checked = bar.classList.contains('is-open');
    var none = !secs.length; $('#pg-collapse').disabled = none; $('#pg-buka').disabled = none; $('#pg-tutup').disabled = none;
  }
  $('#pg-harakat').addEventListener('change', function (e) { S.harakat = e.target.checked; terapkanHarakat(); pool = null; save(); });
  $$('input[name="pg-terj"]', dlg).forEach(function (r) { r.addEventListener('change', function () { if (r.checked) { S.terj = r.value; terapkanTerjemahan(); save(); } }); });
  $('#pg-collapse').addEventListener('change', function (e) { S.collapse = e.target.checked; terapkanCollapse(false); if (S.collapse) setCollapseAll(true); save(); });
  $('#pg-buka').addEventListener('click', function () { if (!S.collapse) { S.collapse = true; terapkanCollapse(false); $('#pg-collapse').checked = true; save(); } setCollapseAll(false); });
  $('#pg-tutup').addEventListener('click', function () { if (!S.collapse) { S.collapse = true; terapkanCollapse(false); $('#pg-collapse').checked = true; save(); } setCollapseAll(true); });
  $('#pg-cari').addEventListener('change', function (e) { bukaCari(e.target.checked); if (e.target.checked) dlg.close(); });
  $('#pg-rate').addEventListener('change', function (e) { S.rate = parseFloat(e.target.value); save(); });
  $('#pg-baca').addEventListener('click', function () { dlg.close(); mulaiBaca(false); });
  $('#pg-baca-t').addEventListener('click', function () { dlg.close(); mulaiBaca(true); });

  /* ======================= INISIALISASI ======================= */
  terapkanHarakat(); terapkanTerjemahan(); terapkanCollapse(true);
  if (location.hash) { var t0 = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t0) { reveal(t0); setTimeout(function () { t0.scrollIntoView(); }, 50); } }
  window.addEventListener('beforeunload', stopSpeech);
})();
