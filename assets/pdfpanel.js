/* Panel PDF asli: tombol "PDF" di tiap pembatas Hlm. membuka halaman PDF yang bersesuaian (pdf.js).
   Pakai: window.PDFPANEL = { src: 'nama-file.pdf' } sebelum memuat berkas ini; tiap tombol .hal__pdf bernilai data-pdf = nomor halaman PDF. */
(function () {
  var CFG = window.PDFPANEL || {};
  if (!CFG.src || !document.querySelector('.hal__pdf')) return;
  /* pdf.js disimpan di repo (assets/pdfjs), jadi tidak bergantung pada CDN */
  var BASE = (document.currentScript && document.currentScript.src || '').replace(/[^\/]*$/, '');
  var SRC = CFG.src.split('/').map(encodeURIComponent).join('/');
  var LIB = BASE + 'pdfjs/pdf.min.js', WORKER = BASE + 'pdfjs/pdf.worker.min.js';
  var panel = document.createElement('div');
  panel.className = 'pdfp';
  panel.setAttribute('role', 'region'); panel.setAttribute('aria-label', 'PDF asli');
  panel.innerHTML = '<div class="pdfp__bar"><button type="button" class="pdfp__b" data-a="prev" aria-label="Halaman sebelumnya">&#8249;</button><span class="pdfp__ttl"></span><button type="button" class="pdfp__b" data-a="next" aria-label="Halaman berikutnya">&#8250;</button><button type="button" class="pdfp__b pdfp__grip" aria-label="Seret untuk mengubah ukuran panel" title="Seret untuk mengubah ukuran panel (klik dua kali: reset)"><svg class="pdfp__gv" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v16M8 8l4-4 4 4M8 16l4 4 4-4"/></svg><svg class="pdfp__gh" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4"/></svg></button><button type="button" class="pdfp__b" data-a="zoom-" aria-label="Perkecil">&minus;</button><button type="button" class="pdfp__b" data-a="zoom+" aria-label="Perbesar">+</button><button type="button" class="pdfp__b" data-a="close" aria-label="Tutup">&times;</button></div><div class="pdfp__body"></div>';
  document.body.appendChild(panel);
  var ttl = panel.querySelector('.pdfp__ttl'), body = panel.querySelector('.pdfp__body');
  var prev = panel.querySelector('[data-a=prev]'), next = panel.querySelector('[data-a=next]');
  var doc = null, loading = null, page = 1, zoom = 1, token = 0, hlm = '';
  var wide = function () { return window.innerWidth >= 1100; };
  var H = wide() ? 100 : 55;
  /* layar lebar: panel di sisi kanan, gagang mengubah LEBAR (kiri/kanan); layar sempit: panel di bawah, gagang mengubah TINGGI */
  function setW(px) {
    var w = Math.max(320, Math.min(window.innerWidth * 0.8, px));
    panel.style.setProperty('--pdfw', w + 'px');
    document.body.style.setProperty('--pdfw', w + 'px');
  }
  function resetW() { panel.style.removeProperty('--pdfw'); document.body.style.removeProperty('--pdfw'); }
  function setH(v) {
    H = Math.max(25, Math.min(wide() ? 100 : 90, v));
    panel.style.setProperty('--pdfh', H);
    document.body.style.setProperty('--pdfh', H);
  }
  function syncHtml() {
    var btns = document.querySelectorAll('.hal__pdf'), m = null, mp = -1, first = null, fp = 1e9;
    Array.prototype.forEach.call(btns, function (b) {
      var v = parseInt(b.getAttribute('data-pdf'), 10);
      if (v <= page && v >= mp) { mp = v; m = b.parentNode; }
      if (v < fp) { fp = v; first = b.parentNode; }
    });
    m = m || first;
    if (!m) return;
    for (var e = m.parentNode; e && e !== document.body; e = e.parentNode) {
      if (e.classList && e.classList.contains('is-collapsed')) e.classList.remove('is-collapsed');
    }
    window.scrollTo({ top: m.getBoundingClientRect().top + window.pageYOffset - 90, behavior: 'smooth' });
  }

  function load() {
    if (loading) return loading;
    loading = new Promise(function (ok, no) {
      var sc = document.createElement('script');
      sc.src = LIB; sc.onload = ok; sc.onerror = no; document.head.appendChild(sc);
    }).then(function () {
      pdfjsLib.GlobalWorkerOptions.workerSrc = WORKER;
      return pdfjsLib.getDocument(SRC).promise;
    }).then(function (d) { doc = d; return d; });
    loading.catch(function () { loading = null; });
    return loading;
  }
  function msg(t) { body.innerHTML = '<p class="pdfp__msg"></p>'; body.firstChild.textContent = t; }
  function render() {
    var my = ++token;
    ttl.textContent = (CFG.label || 'Hlm.') + ' ' + page + (doc ? ' / ' + doc.numPages : '');
    prev.disabled = page <= 1; next.disabled = !doc || page >= doc.numPages;
    if (!doc) { msg('Memuat PDF\u2026'); return; }
    doc.getPage(page).then(function (pg) {
      if (my !== token) return;
      var avail = Math.max(240, body.clientWidth - 16);
      var base = pg.getViewport({ scale: 1 });
      var scale = (avail / base.width) * zoom, dpr = window.devicePixelRatio || 1;
      var vp = pg.getViewport({ scale: scale * dpr });
      var c = document.createElement('canvas');
      c.width = Math.floor(vp.width); c.height = Math.floor(vp.height);
      c.style.width = Math.floor(vp.width / dpr) + 'px'; c.style.maxWidth = zoom > 1 ? 'none' : '100%';
      return pg.render({ canvasContext: c.getContext('2d'), viewport: vp }).promise.then(function () {
        if (my !== token) return;
        body.innerHTML = ''; body.appendChild(c); body.scrollTop = 0;
      });
    }).catch(function () { if (my === token) msg('Gagal menampilkan halaman PDF.'); });
  }
  function open(p, h) {
    page = p; hlm = h; zoom = 1; setH(H);
    panel.classList.add('pdfp--on'); document.body.classList.add('pdfp-open');
    render();
    if (!doc) load().then(render, function () { msg('PDF tidak bisa dimuat. Periksa koneksi internet lalu coba lagi.'); });
  }
  /* gagang di bilah panel: seret ke kiri/kanan (layar lebar) atau atas/bawah (layar sempit); klik dua kali untuk reset */
  var grip = panel.querySelector('.pdfp__grip'), gid = null, x0 = 0, w0 = 0;
  grip.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    gid = e.pointerId; x0 = e.clientX; w0 = panel.getBoundingClientRect().width; grip.setPointerCapture(gid); panel.classList.add('pdfp--drag'); e.preventDefault();
  });
  grip.addEventListener('pointermove', function (e) {
    if (e.pointerId !== gid) return;
    if (wide()) setW(w0 + (x0 - e.clientX)); else setH((window.innerHeight - e.clientY) / window.innerHeight * 100);
  });
  function endGrip(e) { if (e.pointerId === gid) { gid = null; panel.classList.remove('pdfp--drag'); if (wide() && doc) render(); } }
  grip.addEventListener('pointerup', endGrip); grip.addEventListener('pointercancel', endGrip);
  grip.addEventListener('dblclick', function () { if (wide()) { resetW(); if (doc) render(); } else setH(55); });
  function close() { panel.classList.remove('pdfp--on'); document.body.classList.remove('pdfp-open'); token++; }
  /* tombol PDF di tiap pembatas "Hlm. N": buka PDF di halaman yang sama */
  Array.prototype.forEach.call(document.querySelectorAll('.hal__pdf'), function (b) {
    b.addEventListener('click', function () {
      open(parseInt(b.getAttribute('data-pdf'), 10), b.getAttribute('data-pdf'));
      var el = b.parentNode, top = el.getBoundingClientRect().top;
      if (top > window.innerHeight * (window.innerWidth >= 1100 ? 0.9 : 0.4)) window.scrollBy({ top: top - 90, behavior: 'smooth' });
    });
  });
  panel.addEventListener('click', function (e) {
    var a = e.target.getAttribute && e.target.getAttribute('data-a'); if (!a) return;
    if (a === 'close') close();
    else if (a === 'prev' && page > 1) { page--; hlm = ''; render(); syncHtml(); }
    else if (a === 'next' && doc && page < doc.numPages) { page++; hlm = ''; render(); syncHtml(); }
    else if (a === 'zoom+') { zoom = Math.min(3, zoom + 0.25); render(); }
    else if (a === 'zoom-') { zoom = Math.max(0.5, zoom - 0.25); render(); }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel.classList.contains('pdfp--on')) close(); });
})();

