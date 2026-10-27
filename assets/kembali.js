/* Tombol "Folder" di halaman materi: kembali ke index, tepat di folder tempat file ini berada.
   Dipakai lewat <script src=".../assets/kembali.js"></script>; lokasi index dihitung dari lokasi skrip ini. */
(function () {
  var skrip = document.currentScript;
  if (!skrip) return;
  var dec = function (t) { try { return decodeURIComponent(t); } catch (e) { return t; } };
  var path = dec(location.pathname);
  var i = path.indexOf('/Data/');
  if (i < 0) return;
  var folder = path.slice(i + 6).split('/');
  folder.pop(); // buang nama file
  var index = skrip.src.replace(/assets\/kembali\.js.*$/, 'index.html');
  var a = document.createElement('a');
  a.className = 'tombol-kembali';
  a.href = index + '#/' + folder.map(encodeURIComponent).join('/');
  a.textContent = '← Folder';
  a.title = 'Kembali ke folder: ' + folder.join(' / ');
  var st = document.createElement('style');
  st.textContent = '.tombol-kembali{position:fixed;left:.9rem;bottom:.9rem;z-index:40;display:inline-flex;align-items:center;padding:.5rem .95rem;border-radius:999px;background:#1f4d3a;color:#fffdf7;font:600 .85rem/1 Poppins,system-ui,sans-serif;text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,.28);direction:ltr}'
    + '.tombol-kembali:hover{filter:brightness(1.12)}.tombol-kembali:focus-visible{outline:2px solid #fffdf7;outline-offset:2px}'
    + '@media print{.tombol-kembali{display:none}}';
  document.head.appendChild(st);
  document.body.appendChild(a);
})();
