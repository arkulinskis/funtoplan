/* ftp-fx.js: the few things Fun To Plan draws in JavaScript, called from Python (client_code/ftp.py).
     FTP.burst(x, y, label, points)   confetti + a "+10 brownie points" label at a screen point
     FTP.qr(el, text)                 draws the invite QR code (rounded modules, fridge-magnet eyes) into el
     FTP.scan(video, onCode, onFail)  reads an invite QR code with the camera (BarcodeDetector); FTP.stopScan()
     FTP.copy(text)                   copies text; returns a Promise
   Everything else (pages, lists, dialogs) is Python Forms. */
(function () {
  'use strict';
  var FTP = window.FTP = window.FTP || {};
  var BROWNIE = '<svg class="brownie" viewBox="0 0 24 24" aria-hidden="true">' +
    '<rect class="b-cake" x="3" y="6" width="18" height="14" rx="3.5"/>' +
    '<path class="b-top" d="M3 9.5A3.5 3.5 0 0 1 6.5 6h11A3.5 3.5 0 0 1 21 9.5v2q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0z"/>' +
    '<circle class="b-dot" cx="8" cy="15.5" r="1"/><circle class="b-dot" cx="13.5" cy="17" r="1"/><circle class="b-dot" cx="16.5" cy="14.2" r=".9"/></svg>';

  FTP.burst = function (x, y, label, points) {
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var b = document.createElement('div');
    b.className = 'burst'; b.style.left = x + 'px'; b.style.top = y + 'px';
    b.setAttribute('aria-hidden', 'true');
    var gain = document.createElement('div');
    gain.className = 'gain';
    gain.innerHTML = points ? BROWNIE : '';
    gain.appendChild(document.createTextNode(label));
    b.appendChild(gain);
    var colors = ['#e5484d', '#f2b51d', '#3a7be0', '#2fa36b', '#f07c2a', '#8a5cd6', '#fff0a0', '#cfe4ff', '#ffd2dc'];
    for (var i = 0; i < (reduce ? 0 : 22); i++) {
      var a = (Math.PI * 2 * i) / 22 + Math.random() * 0.4, dist = 60 + Math.random() * 90;
      var bit = document.createElement('i');
      bit.className = 'bit';
      bit.style.cssText = 'left:-5px;top:-5px;background:' + colors[i % colors.length] + ';--dx:' + Math.round(Math.cos(a) * dist) +
        'px;--dy:' + Math.round(Math.sin(a) * dist - 30) + 'px;--rot:' + Math.round(Math.random() * 360) + 'deg;border-radius:' + (i % 3 ? '3px' : '50%');
      b.appendChild(bit);
    }
    document.body.appendChild(b);
    setTimeout(function () { b.remove(); }, 1600);
  };

  function rr(x, y, w, h, r) {
    return 'M' + (x + r) + ',' + y + 'h' + (w - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 ' + r + ',' + r + 'v' + (h - 2 * r) +
      'a' + r + ',' + r + ' 0 0 1 -' + r + ',' + r + 'h-' + (w - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 -' + r + ',-' + r +
      'v-' + (h - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 ' + r + ',-' + r + 'z';
  }
  /* true when drawn; false when the QR library didn't load (no internet) */
  FTP.qr = function (el, text) {
    if (!el) return false;
    if (typeof window.qrcode !== 'function') { el.textContent = ''; return false; }
    var qr;
    try { qr = window.qrcode(0, 'M'); qr.addData(text); qr.make(); } catch (e) { return false; }
    var n = qr.getModuleCount(), parts = [];
    function inEye(r, c) { return (r < 7 && c < 7) || (r < 7 && c >= n - 7) || (r >= n - 7 && c < 7); }
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        if (qr.isDark(r, c) && !inEye(r, c)) parts.push('<rect class="m" x="' + (c + 0.08) + '" y="' + (r + 0.08) + '" width="0.84" height="0.84" rx="0.32"/>');
      }
    }
    [[0, 0], [0, n - 7], [n - 7, 0]].forEach(function (p) {
      var y = p[0], x = p[1];
      parts.push('<path class="eye" fill-rule="evenodd" d="' + rr(x, y, 7, 7, 2) + rr(x + 1, y + 1, 5, 5, 1.4) + '"/>');
      parts.push('<path class="eye" d="' + rr(x + 2, y + 2, 3, 3, 0.9) + '"/>');
    });
    el.innerHTML = '<svg viewBox="0 0 ' + n + ' ' + n + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Invite QR code">' + parts.join('') + '</svg>';
    return true;
  };

  var scanning = { stream: null, stopped: true };
  FTP.canScan = function () { return 'BarcodeDetector' in window && !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia); };
  FTP.stopScan = function () {
    scanning.stopped = true;
    if (scanning.stream) { scanning.stream.getTracks().forEach(function (t) { t.stop(); }); scanning.stream = null; }
  };
  FTP.scan = function (video, onCode, onFail) {
    FTP.stopScan();
    scanning.stopped = false;
    if (!FTP.canScan()) { onFail('Use your phone\'s camera app to scan the QR code.'); return; }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(function (stream) {
      if (scanning.stopped) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
      scanning.stream = stream; video.srcObject = stream;
      var det = new window.BarcodeDetector({ formats: ['qr_code'] });
      (function loop() {
        if (scanning.stopped) return;
        det.detect(video).then(function (codes) {
          var raw = codes.length ? String(codes[0].rawValue || '') : '';
          var m = /join=([A-Z0-9]{6})/i.exec(raw) || /^\s*([A-Z0-9]{6})\s*$/i.exec(raw);
          if (m) { FTP.stopScan(); onCode(m[1].toUpperCase()); } else setTimeout(loop, 300);
        }, function () { setTimeout(loop, 600); });
      })();
    }, function () { onFail('Camera not available. Type the code instead.'); });
  };

  FTP.copy = function (text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve) {
      var t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) { /* ignore */ }
      t.remove(); resolve();
    });
  };
})();
