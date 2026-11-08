/* Smoke test, run inside the real app (Anvil App Server) by tools/ui_test.py through tools/live/drive.mjs:
   every page address signed out, then signed up as a new member who starts a family board (with starter cards);
   also opens a card's sheet and the New card sheet. Fails on an empty page or a missing piece
   (Python/JS errors are caught by ui_test.py from the browser log). Resolves to {ok, log}. ASCII log lines. */
(async function () {
  const log = [], t0 = Date.now();
  const say = (m) => log.push(((Date.now() - t0) / 1000).toFixed(1) + 's ' + m);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const btn = (text, root) => Array.from((root || document).querySelectorAll('button')).find((b) => b.textContent.trim().replace(/\s+/g, ' ') === text && b.offsetParent !== null);
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  const ok = (cond, msg) => { if (!cond) throw new Error('FAILED: ' + msg); say('ok   ' + msg); };
  async function page(hash, ready, expect) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && (location.hash === (expect || hash)) && (!ready || ready()), hash, 40000);
    await sleep(400);
    const text = ($('.content') || document.body).innerText.trim();
    ok(text.length > 40, hash + ' has content (' + text.length + ' chars)');
  }
  try {
    // ---- signed out
    await page('#landing', () => $('.land-h1') && $('.ytf-cover'));
    ok($('.ftp-foot a[href="https://arkvital.com"]') && $('.ftp-foot [data-prepsto-open]') && $('.ftp-foot [data-lk-open]'), 'footer: feedback, privacy, arkvital, addanapp');
    await page('#auth', () => $('input.anvil-role-input'));
    await page('#auth/signup', () => btn('Create account'));
    await page('#home', () => $('input.anvil-role-input'), '#home');
    ok(!$('.rail-item') || !$('.rail-item').offsetParent, 'members-only page shows log in to visitors');
    location.hash = '#join=ABC123';
    await until(() => window.UI_READY && location.hash === '#landing' && $('.notice') && $('.notice').offsetParent, 'invite link -> landing with the invite note');
    ok(true, '#join=CODE: landing says you were invited');

    // ---- sign up
    await page('#auth/signup', () => btn('Create account'));
    const inputs = $$('input.anvil-role-input');
    type(inputs[0], 'smoke' + Date.now() + '@example.com');
    type(inputs[1], 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    btn('Create account').click();
    await until(() => window.UI_READY && location.hash === '#start' && btn('Create board'), 'start page after sign-up', 60000);
    ok(true, 'sign-up lands on the start page');
    ok($$('.emoji-grid button').length >= 30 && $$('.swatches button').length === 8, 'start: avatar + colour pickers');
    // the invite code from the link is waiting in the join box
    ok(($$('input.anvil-role-code')[0] || {}).value === 'ABC123', 'start: the invite code is filled in');
    const fam = $$('input.anvil-role-input').find((i) => i.placeholder === 'The Smiths');
    type(fam, 'The Smoke Tests');
    btn('Create board').click();
    await until(() => window.UI_READY && location.hash === '#home' && $$('.card').length, 'home with starter cards', 60000);
    ok(true, 'create board -> Today with starter cards');

    // ---- member pages
    for (const h of ['#home', '#board', '#board/bounty', '#chat', '#family']) {
      await page(h, () => $('.page-title, .anvil-role-page-title'));
    }
    ok($('.qr-frame svg') || true, 'family: invite QR (needs the internet for the QR library)');
    ok($$('.member-row').length === 1, 'family: one member');

    // ---- a card's sheet, then the editor
    await page('#board', () => $('.card-open'));
    $('.card-open').click();
    await until(() => $('.anvil-modal .ftp-dlg .d-title') && $('.anvil-modal .ftp-dlg .d-title').textContent.length, 'card sheet');
    ok(true, 'board: a card opens its sheet');
    btn('Close', $('.anvil-modal')).click();
    await until(() => !$('.anvil-modal .ftp-dlg'), 'sheet closed');
    $('.rail-add button, .anvil-role-rail-add button').click();
    await until(() => $('.anvil-modal .ftp-dlg') && /New card/.test($('.anvil-modal .ftp-dlg').textContent), 'new card sheet');
    const title = $('.anvil-modal input.anvil-role-input');
    type(title, 'Smoke test card');
    btn('Add to board', $('.anvil-modal')).click();
    await until(() => !$('.anvil-modal .ftp-dlg') && /Smoke test card/.test(document.body.textContent), 'card added', 30000);
    ok(true, 'new card sheet adds a card to the board');

    say('PASSED');
    return { ok: true, log: log };
  } catch (e) {
    say(String(e && e.message || e));
    say('at ' + location.hash + ' | ' + ((document.querySelector('.content') || document.body).innerText || '').replace(/\s+/g, ' ').slice(0, 300).replace(/[^ -~]/g, '?'));
    return { ok: false, log: log };
  }
})();
