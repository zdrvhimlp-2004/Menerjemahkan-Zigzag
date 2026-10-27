/* ============================================================
   DATA
   Pohon folder diambil otomatis dari folder Data/ lewat daftar.php
   . Tidak ada yang ditulis manual.
   ============================================================ */
let DATA = [];
let INDEX = [];
const isFolder = (n) => Array.isArray(n.c);

async function ambilDaftar() {
  const r = await fetch('daftar.php', { cache: 'no-cache' });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  const d = await r.json();
  if (!Array.isArray(d)) throw new Error('format daftar tidak dikenal');
  return d;
}

/* ============================================================
   RENDER
   ============================================================ */
const $ = (id) => document.getElementById(id);
const listEl = $('list'), crumbsEl = $('crumbs'), titleEl = $('sectionTitle');
const qEl = $('q'), searchBox = $('searchBox');

const SVG = {
  folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
  doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
  chev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg>',
  ext: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M8 7h9v9"/></svg>',
};

function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}
const isArabic = (t) => /[\u0600-\u06FF]/.test(t);
// logo file: kertas dengan label jenis; warna mengikuti jenis file
const JENIS = {
  html: ['HTML', '#ff9f5a'], htm: ['HTML', '#ff9f5a'],
  doc: ['DOC', '#6aa8ff'], docx: ['DOC', '#6aa8ff'], odt: ['DOC', '#6aa8ff'], rtf: ['DOC', '#6aa8ff'],
  pdf: ['PDF', '#ff6b6b'],
  xls: ['XLS', '#4fd18b'], xlsx: ['XLS', '#4fd18b'], csv: ['CSV', '#4fd18b'],
  ppt: ['PPT', '#ff8a65'], pptx: ['PPT', '#ff8a65'],
  md: ['MD', '#b6a6ff'], txt: ['TXT', '#aab4c0'], json: ['JSON', '#f2d15c'],
  png: ['IMG', '#d98cf0'], jpg: ['IMG', '#d98cf0'], jpeg: ['IMG', '#d98cf0'], gif: ['IMG', '#d98cf0'], webp: ['IMG', '#d98cf0'], svg: ['SVG', '#d98cf0'],
  mp3: ['MP3', '#5fd4d4'], mp4: ['MP4', '#5fd4d4'],
  zip: ['ZIP', '#f2d15c'], rar: ['ZIP', '#f2d15c'],
};
function iconFor(ext) {
  const [label, warna] = JENIS[ext] || [(ext || 'FILE').slice(0, 4).toUpperCase(), '#aab4c0'];
  const svg = '<svg style="width:28px;height:28px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2.5H7a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7.5z"/><path d="M14 2.5v5h5"/>'
    + '<text x="12" y="17" text-anchor="middle" font-family="system-ui,sans-serif" font-size="' + (label.length > 3 ? 4.6 : 5.8) + '" font-weight="700" fill="currentColor" stroke="none">' + label + '</text></svg>';
  return { svg, warna };
}

function titleSpan(name) {
  return span(isArabic(name) ? 't-ar ar' : 't-id', name);
}
function span(cls, text) { const s = el('span', cls); s.textContent = text; return s; }


function nodeAt(path) {
  let node = { c: DATA }, trail = [];
  for (const i of path) {
    node = node.c && node.c[i];
    if (!node) return null;
    trail.push(node);
  }
  return { node, trail };
}

// alamat memakai nama folder (bukan nomor urut) supaya tetap benar saat isi Data/ bertambah
function go(path) {
  const names = [];
  let node = { c: DATA };
  for (const i of path) { node = node.c[i]; names.push(encodeURIComponent(node.name)); }
  location.hash = '#/' + names.join('/');
}
function currentPath() {
  const names = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  const path = [];
  let kids = DATA;
  for (const raw of names) {
    let name = raw;
    try { name = decodeURIComponent(raw); } catch (e) { /* pakai apa adanya */ }
    const i = kids.findIndex((k) => isFolder(k) && k.name === name);
    if (i < 0) return [];
    path.push(i);
    kids = kids[i].c;
  }
  return path;
}

function buildItem(n, path, showPath) {
  const folder = isFolder(n);
  const soon = !folder && !n.href;
  const root = el(folder ? 'button' : soon ? 'div' : 'a', 'item' + (folder ? ' folder' : '') + (soon ? ' soon' : ''));
  if (folder) {
    root.type = 'button';
    root.addEventListener('click', () => { qEl.value = ''; syncSearch(); go(path); });
  } else if (!soon) {
    // dokumen Word dan halaman HTML dibuka di viewer
    root.href = /^(docx?|html?)$/.test(n.ext || '') ? 'viewer.html?f=' + encodeURIComponent(decodeURIComponent(n.href)) : n.href;
  }

  const ico = el('span', 'ico');
  if (folder) {
    ico.innerHTML = SVG.folder;
  } else {
    const j = iconFor(n.ext);
    ico.innerHTML = j.svg;
    ico.style.color = j.warna;
    ico.style.background = 'color-mix(in srgb, ' + j.warna + ' 16%, transparent)';
  }
  root.appendChild(ico);

  const txt = el('span', 'txt');
  txt.appendChild(titleSpan(n.name));
  if (showPath) txt.appendChild(span('sub', showPath));
  root.appendChild(txt);

  const end = el('span', 'end');
  if (!folder && !soon) end.innerHTML = SVG.ext;
  if (folder) {
    end.appendChild(span('count', String(n.c.length))); // jumlah kartu langsung di dalam folder
    end.insertAdjacentHTML('beforeend', SVG.chev);
  }
  if (soon) end.appendChild(span('badge', 'Segera'));
  root.appendChild(end);
  return root;
}

function render() {
  const path = currentPath();
  const hit = nodeAt(path);
  if (!hit) { go([]); return; }
  const { node, trail } = hit;

  // breadcrumb
  crumbsEl.replaceChildren();
  const home = el('button'); home.textContent = 'Beranda';
  home.onclick = () => go([]);
  if (path.length) {
    crumbsEl.appendChild(home);
    trail.forEach((t, i) => {
      crumbsEl.appendChild(span('sep', '/'));
      const name = t.name;
      if (i === trail.length - 1) {
        crumbsEl.appendChild(span('cur', name));
      } else {
        const b = el('button'); b.textContent = name;
        b.onclick = () => go(path.slice(0, i + 1));
        crumbsEl.appendChild(b);
      }
    });
  }

  titleEl.replaceChildren();

  // daftar
  listEl.replaceChildren();
  const kids = node.c;
  if (!kids.length) {
    listEl.appendChild(el('div', 'empty', 'Belum ada isi di sini.'));
  } else {
    kids.forEach((k, i) => listEl.appendChild(buildItem(k, path.concat(i))));
  }
  document.title = path.length ? trail[trail.length - 1].name + ' — As-Salmaniyyah' : 'As-Salmaniyyah';
}

/* ============================================================
   SEARCH
   ============================================================ */
// buang harakat/tatwil & samakan bentuk huruf Arab supaya pencarian longgar
const norm = (s) => (s || '').toLowerCase()
  .replace(/[ً-ٰٟـ]/g, '')
  .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
  .replace(/[٠-٩]/g, (d) => d.charCodeAt(0) - 0x0660);

function flatten(nodes, path = [], names = [], out = []) {
  nodes.forEach((n, i) => {
    const p = path.concat(i);
    const name = n.name;
    out.push({ n, path: p, names });
    if (isFolder(n)) flatten(n.c, p, names.concat(name), out);
  });
  return out;
}

function syncSearch() {
  searchBox.classList.toggle('has-text', !!qEl.value);
}

function search() {
  syncSearch();
  const q = norm(qEl.value.trim());
  if (!q) { render(); return; }
  const terms = q.split(/\s+/);

  const results = INDEX.filter(({ n, names }) => {
    const hay = norm([n.name].concat(names).join(' '));
    return terms.every((t) => hay.includes(t));
  });

  crumbsEl.replaceChildren();
  titleEl.replaceChildren(el('small', null, results.length + ' hasil untuk “' + qEl.value.trim() + '”'));
  listEl.replaceChildren();
  if (!results.length) {
    listEl.appendChild(el('div', 'empty', 'Tidak ada yang cocok.'));
    return;
  }
  results.forEach(({ n, path, names }) => listEl.appendChild(buildItem(n, path, names.join(' › '))));
}

qEl.addEventListener('input', search);
$('clearQ').addEventListener('click', () => { qEl.value = ''; search(); qEl.focus(); });

/* ============================================================
   LAYAR PENUH
   ============================================================ */
const btnFull = $('btnFull');
const IKON_FULL = {
  masuk: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
  keluar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5"/></svg>',
};
function sinkronFull() {
  const aktif = !!document.fullscreenElement;
  btnFull.innerHTML = aktif ? IKON_FULL.keluar : IKON_FULL.masuk;
  btnFull.title = btnFull.ariaLabel = aktif ? 'Keluar layar penuh' : 'Layar penuh';
}
if (document.fullscreenEnabled) {
  btnFull.addEventListener('click', () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  });
  document.addEventListener('fullscreenchange', sinkronFull);
  sinkronFull();
} else {
  btnFull.hidden = true; // mis. iPhone: browser tidak mendukung layar penuh untuk halaman web
}

window.addEventListener('hashchange', () => { if (!qEl.value) render(); else { qEl.value = ''; syncSearch(); render(); } });
listEl.replaceChildren(el('div', 'empty', 'Memuat daftar…'));
ambilDaftar().then((d) => {
  DATA = d;
  INDEX = flatten(DATA);
  render();
}).catch(() => {
  listEl.replaceChildren(el('div', 'empty', 'Daftar tidak bisa dimuat. Pastikan situs berjalan di server yang mendukung PHP (daftar.php).'));
});

