/* ==========================================================================
   Fun To Plan - client UI
   A small vanilla-JS single page app mounted by Form1 (client_code/Form1).
   All data comes from the server via `bridge(action, payloadJson)` which
   returns (a Promise of) a JSON string: {ok, data} or {ok:false, error, code}.
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------ constants */
  var ICONS = {
    home: 'M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z',
    board: 'M4 4h4v16H4zM10 4h4v10h-4zM16 4h4v13h-4z',
    chat: 'M4 5h16v11H9l-5 4z',
    family: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21v-1a6 6 0 0 1 6-6h2a6 6 0 0 1 6 6v1M16 3.5a4 4 0 0 1 0 7.5M22 21v-1a6 6 0 0 0-4-5.6',
    plus: 'M12 5v14M5 12h14',
    check: 'M5 12.5l4.5 4.5L19 7.5',
    calendar: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4',
    star: 'M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z',
    repeat: 'M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4',
    qr: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM18 14h2v2h-2zM14 18h2v2h-2zM18 18h2v2h-2z',
    send: 'M4 12 20 4l-6 16-3-7z',
    close: 'M6 6l12 12M18 6 6 18',
    shield: 'M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6zM9 12l2 2 4-4',
    eye: 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    thumb: 'M7 10v11H4V10zM7 10l4-7a2 2 0 0 1 3 2l-1 5h6a2 2 0 0 1 2 2.3l-1.4 7A2 2 0 0 1 17.6 21H7',
    trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
    edit: 'M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4',
    play: 'M8 5v14l11-7z',
    camera: 'M4 7h3l2-3h6l2 3h3v13H4zM12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
    logout: 'M15 4h4v16h-4M10 8l-4 4 4 4M6 12h11',
    moon: 'M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z',
    clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2',
    pin: 'M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21zM12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
    undo: 'M9 14 4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3',
    link: 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1',
    copy: 'M8 8h12v12H8zM4 16V4h12',
    share: 'M12 3v12M7 8l5-5 5 5M5 13v7h14v-7',
    trophy: 'M7 4h10v5a5 5 0 0 1-10 0zM7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3M12 14v4M8 21h8M9 18h6',
    hand: 'M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM3 21v-1a6 6 0 0 1 6-6h2M19 14v6M16 17h6',
    up: 'M12 19V5M6 11l6-6 6 6',
    down: 'M12 5v14M6 13l6 6 6-6',
    flat: 'M5 9h14M5 15h14',
    msg: 'M5 5h14v10H10l-5 4z',
    refresh: 'M20 11a8 8 0 0 0-14.5-4.5L4 8M4 4v4h4M4 13a8 8 0 0 0 14.5 4.5L20 16M20 20v-4h-4',
    sparkle: 'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z',
    gear: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z',
    user: 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21v-1a7 7 0 0 1 7-7h2a7 7 0 0 1 7 7v1',
    back: 'M15 18l-6-6 6-6',
    arrow: 'M5 12h14M13 6l6 6-6 6',
    device: 'M7 3h10a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM11 18h2'
  };
  var BROWNIE = '<svg class="brownie" viewBox="0 0 24 24" aria-hidden="true">' +
    '<rect class="b-cake" x="3" y="6" width="18" height="14" rx="3.5"/>' +
    '<path class="b-top" d="M3 9.5A3.5 3.5 0 0 1 6.5 6h11A3.5 3.5 0 0 1 21 9.5v2q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0q-1.5 1.5-3 0z"/>' +
    '<circle class="b-dot" cx="8" cy="15.5" r="1"/><circle class="b-dot" cx="13.5" cy="17" r="1"/><circle class="b-dot" cx="16.5" cy="14.2" r=".9"/></svg>';

  var AVATARS = ['🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐸', '🐵', '🦉', '🐧', '🐳', '🦄', '🐝', '🐢', '🐙', '🦖', '🐶', '🐱', '🚀', '⭐', '🌈', '🍀', '🍩', '🎸', '👩', '👨', '👧', '👦', '👵', '👴'];
  var COLORS = ['#e5484d', '#f07c2a', '#f2b51d', '#2fa36b', '#3a7be0', '#8a5cd6', '#e0559a', '#2b2a33'];
  var LEVELS = [[0, 'Rookie'], [30, 'Helper'], [80, 'Sidekick'], [150, 'Teammate'], [250, 'Ace'], [400, 'Hero'], [600, 'Champion'], [850, 'Captain'], [1150, 'Legend'], [1500, 'Mythic']];
  var KIND = {
    task: { icon: 'check', label: 'Task' },
    event: { icon: 'calendar', label: 'Event' },
    want: { icon: 'star', label: 'Want' }
  };
  var COLS = [
    { id: 'todo', label: 'To do' },
    { id: 'doing', label: 'In progress' },
    { id: 'review', label: 'Review' },
    { id: 'done', label: 'Done' }
  ];
  var RECUR = { none: 'Never', daily: 'Daily', weekdays: 'Weekdays', weekly: 'Weekly', biweekly: 'Every 2 weeks', monthly: 'Monthly' };
  var DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var POLL_MS = 8000;

  /* ------------------------------------------------------------ state */
  var S = {
    phase: 'boot',          // boot | landing | auth | onboard | app
    authMode: 'login',
    email: null,
    st: null,               // server state
    mm: {},                 // members by id
    bySeq: {},              // items by seq
    view: store('ftp.view') || 'home',
    filter: 'all',
    col: 'todo',
    lb: 'week',
    theme: store('ftp.theme') || 'light',
    pendingJoin: null,
    preview: null,
    sheet: null,
    detail: null,
    ed: null,
    pick: {},
    poll: null,
    syncing: false,
    stream: null
  };
  var bridge = null, app = null, stage = null, layer = null, toasts = null;

  /* ------------------------------------------------------------ preboot
     Runs as soon as this script loads, while Anvil's startup spinner is still
     up: match the page to the saved theme, and use our tab icon instead of
     Anvil's default one. */
  function useOurIcons() {
    if (!document.querySelector('link[rel~="icon"][data-ftp]')) return;
    var links = document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]');
    for (var i = 0; i < links.length; i++) {
      if (!links[i].hasAttribute('data-ftp')) links[i].parentNode.removeChild(links[i]);
    }
  }
  document.documentElement.setAttribute('data-ftp-theme', S.theme);
  useOurIcons();
  document.addEventListener('DOMContentLoaded', useOurIcons);

  /* ------------------------------------------------------------ utils */
  function store(k, v) {
    try {
      if (arguments.length > 1) { window.localStorage.setItem(k, v); return v; }
      return window.localStorage.getItem(k);
    } catch (e) { return null; }
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function ic(name, cls) {
    return '<svg class="ic ' + (cls || '') + '" viewBox="0 0 24 24" aria-hidden="true"><path d="' + ICONS[name] + '"/></svg>';
  }
  function $(sel, ctx) { return (ctx || app).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || app).querySelectorAll(sel)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function todayStr() { return ymd(new Date()); }
  function parseYmd(s) { if (!s) return null; var p = s.slice(0, 10).split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function addDays(d, n) { var x = new Date(d.getTime()); x.setDate(x.getDate() + n); return x; }
  function dayDiff(d) {
    var a = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    var t = new Date(); t = new Date(t.getFullYear(), t.getMonth(), t.getDate());
    return Math.round((a - t) / 864e5);
  }
  function fmtDay(d) {
    var diff = dayDiff(d);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Tomorrow';
    if (diff === -1) return 'Yesterday';
    if (diff > 1 && diff < 7) return DOW[d.getDay()];
    return DOW[d.getDay()] + ' ' + d.getDate() + ' ' + MON[d.getMonth()];
  }
  function fmtTime(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function fmtWhen(iso) { var d = new Date(iso); return fmtDay(d) + ' · ' + fmtTime(d); }
  function ago(iso) {
    var s = (Date.now() - new Date(iso).getTime()) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago';
    if (s < 7 * 86400) return Math.floor(s / 86400) + 'd ago';
    var d = new Date(iso); return d.getDate() + ' ' + MON[d.getMonth()];
  }
  function levelOf(points) {
    var p = Math.max(0, points || 0), i = 0;
    while (i + 1 < LEVELS.length && p >= LEVELS[i + 1][0]) i++;
    var cur = LEVELS[i], nxt = LEVELS[i + 1];
    return { n: i + 1, title: cur[1], next: nxt ? nxt[0] : null, toNext: nxt ? nxt[0] - p : 0, pct: nxt ? (p - cur[0]) / (nxt[0] - cur[0]) : 1 };
  }
  function bp(n, extra) { return '<span class="pill bp ' + (extra || '') + '">' + BROWNIE + (n || 0) + '</span>'; }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }

  /* ------------------------------------------------------------ data helpers */
  function me() { return S.st && S.mm[S.st.me]; }
  function isOwner() { var m = me(); return !!m && m.role === 'owner'; }
  function activeMembers() {
    return (S.st ? S.st.members : []).filter(function (m) { return m.active; })
      .sort(function (a, b) { return (a.joined || '') < (b.joined || '') ? -1 : 1; });
  }
  function itemById(id) {
    if (!S.st) return null;
    for (var i = 0; i < S.st.items.length; i++) if (S.st.items[i].id === id) return S.st.items[i];
    return null;
  }
  function indexState() {
    S.mm = {}; S.bySeq = {};
    S.st.members.forEach(function (m) { S.mm[m.id] = m; });
    S.st.items.forEach(function (it) { S.bySeq[it.seq] = it; });
  }
  function eff(it) {
    if (it.kind === 'event') {
      return it.event_at && new Date(it.event_at).getTime() < Date.now() - 3 * 3600e3 ? 'done' : 'todo';
    }
    return it.status;
  }
  function statusLabel(it) {
    var s = eff(it);
    if (it.kind === 'event') return s === 'done' ? 'Happened' : 'Upcoming';
    if (it.kind === 'want') return { todo: 'Wanted', doing: 'On it', review: 'Review', done: 'Got it' }[s];
    return { todo: 'To do', doing: 'In progress', review: 'Review', done: 'Done' }[s];
  }
  var PRI = { high: 0, normal: 1, low: 2 };
  function sortOpen(a, b) {
    var ad = a.kind === 'event' ? a.event_at : a.due_date, bd = b.kind === 'event' ? b.event_at : b.due_date;
    if (PRI[a.priority] !== PRI[b.priority]) return PRI[a.priority] - PRI[b.priority];
    if (ad && bd && ad !== bd) return ad < bd ? -1 : 1;
    if (ad && !bd) return -1;
    if (!ad && bd) return 1;
    return b.seq - a.seq;
  }
  function sortDone(a, b) {
    var ad = a.completed_at || a.event_at || '', bd = b.completed_at || b.event_at || '';
    return ad < bd ? 1 : -1;
  }
  function weekTotal() {
    return activeMembers().reduce(function (s, m) { return s + Math.max(0, m.week_points); }, 0);
  }
  function unreadCount() {
    if (!S.st) return 0;
    var seen = store('ftp.seen.' + S.st.family.id) || '';
    return S.st.messages.filter(function (m) { return m.kind === 'chat' && m.author !== S.st.me && m.created > seen; }).length;
  }
  function markChatSeen() {
    if (!S.st || !S.st.messages.length) return;
    store('ftp.seen.' + S.st.family.id, S.st.messages[S.st.messages.length - 1].created);
  }
  function needsYou() {
    if (!S.st) return [];
    var mine = S.st.me, many = activeMembers().length > 1;
    return S.st.items.filter(function (it) {
      if (it.kind === 'task' && it.status === 'review') return !many || it.completed_by !== mine;
      if (it.kind === 'task' && (it.status === 'todo' || it.status === 'doing')) return it.assignee === mine;
      if (it.kind === 'event' && eff(it) === 'todo') {
        var d = dayDiff(new Date(it.event_at));
        return d >= 0 && d <= 7 && it.acks.indexOf(mine) < 0;
      }
      return false;
    }).sort(function (a, b) {
      var ra = a.status === 'review' ? 0 : 1, rb = b.status === 'review' ? 0 : 1;
      return ra - rb || sortOpen(a, b);
    });
  }

  /* ------------------------------------------------------------ server */
  function api(action, payload) {
    var p = Object.assign({ _today: todayStr(), _tz: new Date().getTimezoneOffset() }, payload || {});
    var out;
    try { out = bridge(action, JSON.stringify(p)); } catch (e) { return Promise.reject(e); }
    return Promise.resolve(out).then(function (raw) {
      var res = typeof raw === 'string' ? JSON.parse(raw) : raw;
      if (!res || !res.ok) {
        var err = new Error((res && res.error) || 'Something went wrong.');
        err.code = res && res.code;
        throw err;
      }
      return res.data;
    });
  }
  function run(action, payload, btn) {
    var label = null;
    if (btn && btn.tagName === 'BUTTON') {
      label = btn.innerHTML; btn.disabled = true;
      btn.innerHTML = '<span class="spin"></span>';
    }
    return api(action, payload).then(function (data) {
      applyData(data);
      return data;
    }, function (e) {
      handleErr(e);
      return null;
    }).then(function (data) {
      if (btn && label !== null && btn.isConnected) { btn.disabled = false; btn.innerHTML = label; }
      return data;
    });
  }
  function handleErr(e) {
    var code = e && e.code;
    if (code === 'auth') { goAuth(); return; }
    if (code === 'session') { toast('Your session expired. Reloading…', true); setTimeout(function () { window.location.reload(); }, 1400); return; }
    if (code === 'nofamily') { S.st = null; setPhase('onboard'); return; }
    if (code === 'gone') { closeSheet(); }
    toast((e && e.message) || 'Something went wrong.', true);
  }
  function applyData(d) {
    if (!d) return;
    if (d.email) S.email = d.email;
    if (d.detail && S.detail && d.detail.item.id === S.detail.id) S.detail.data = d.detail;
    if ('state' in d) {
      if (d.state) {
        S.st = d.state; indexState();
        if (S.phase !== 'app') { setPhase('app'); startPolling(); afterEnterApp(); }
        else refresh();
      } else if (S.phase !== 'onboard') {
        S.st = null; stopPolling(); closeSheet(true); setPhase('onboard');
      }
    }
  }
  function startPolling() {
    stopPolling();
    S.poll = setInterval(tick, POLL_MS);
  }
  function stopPolling() { if (S.poll) clearInterval(S.poll); S.poll = null; }
  function tick() {
    if (document.hidden || S.phase !== 'app' || S.syncing || !S.st) return;
    S.syncing = true;
    api('sync', { version: S.st.version }).then(function (d) {
      if (!d.unchanged) applyData(d);
      if (!d.unchanged && !d.state) toast('You are no longer part of that family board.');
    }, function (e) {
      if (e.code === 'auth' || e.code === 'session') handleErr(e);
    }).then(function () { S.syncing = false; });
  }

  /* ------------------------------------------------------------ feedback */
  function toast(msg, isErr) {
    var t = document.createElement('div');
    t.className = 'toast' + (isErr ? ' err-t' : '');
    t.innerHTML = (isErr ? '' : ic('sparkle', 'ic-sm')) + '<span>' + esc(msg) + '</span>';
    toasts.appendChild(t);
    setTimeout(function () { t.classList.add('out'); }, 2600);
    setTimeout(function () { t.remove(); }, 2950);
  }
  function burst(rect, html) {
    var x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
    var y = rect ? rect.top + rect.height / 2 : window.innerHeight / 2;
    var b = document.createElement('div');
    b.className = 'burst'; b.style.left = x + 'px'; b.style.top = y + 'px';
    var colors = ['#e5484d', '#f2b51d', '#3a7be0', '#2fa36b', '#f07c2a', '#8a5cd6', '#fff0a0', '#cfe4ff', '#ffd2dc'];
    var s = '<div class="gain">' + html + '</div>';
    for (var i = 0; i < 22; i++) {
      var a = (Math.PI * 2 * i) / 22 + Math.random() * 0.4, dist = 60 + Math.random() * 90;
      s += '<i class="bit" style="left:-5px;top:-5px;background:' + colors[i % colors.length] +
        ';--dx:' + Math.round(Math.cos(a) * dist) + 'px;--dy:' + Math.round(Math.sin(a) * dist - 30) +
        'px;--rot:' + Math.round(Math.random() * 360) + 'deg;border-radius:' + (i % 3 ? '3px' : '50%') + '"></i>';
    }
    b.innerHTML = s;
    app.appendChild(b);
    setTimeout(function () { b.remove(); }, 1600);
  }

  /* ------------------------------------------------------------ small components */
  function avatar(m, size) {
    if (!m) return '<span class="avatar ' + (size || '') + ' empty">?</span>';
    return '<span class="avatar ' + (size || '') + '" style="--c:' + esc(m.color) + '" title="' + esc(m.name) + '">' + esc(m.avatar) + '</span>';
  }
  function typeChip(kind) { return '<span class="type t-' + kind + '" title="' + KIND[kind].label + '">' + ic(KIND[kind].icon) + '</span>'; }
  function prioIcon(p) {
    if (p === 'high') return '<span class="prio high" title="High priority">' + ic('up') + '</span>';
    if (p === 'low') return '<span class="prio low" title="Low priority">' + ic('down') + '</span>';
    return '';
  }
  function statusPill(it) { return '<span class="status s-' + eff(it) + '"><i></i>' + statusLabel(it) + '</span>'; }
  function dueMeta(it) {
    var done = eff(it) === 'done';
    if (it.kind === 'task' && it.due_date) {
      var d = parseYmd(it.due_date), diff = dayDiff(d);
      var cls = !done && diff < 0 ? 'warn' : (!done && diff === 0 ? 'soon' : '');
      return '<span class="meta ' + cls + '">' + ic('clock') + fmtDay(d) + '</span>';
    }
    if (it.kind === 'event' && it.event_at) {
      var soon = !done && dayDiff(new Date(it.event_at)) === 0;
      return '<span class="meta ' + (soon ? 'soon' : '') + '">' + ic('calendar') + fmtWhen(it.event_at) + '</span>';
    }
    return '';
  }
  function cardHTML(it, opts) {
    opts = opts || {};
    var who = S.mm[it.assignee];
    var meta = dueMeta(it);
    if (it.kind === 'event' && it.location) meta += '<span class="meta">' + ic('pin') + esc(it.location) + '</span>';
    if (it.recurrence && it.recurrence !== 'none') meta += '<span class="meta" title="Repeats ' + RECUR[it.recurrence].toLowerCase() + '">' + ic('repeat') + (it.rotate ? 'turns' : '') + '</span>';
    if (it.requires_approval) meta += '<span class="meta" title="Needs approval">' + ic('shield') + '</span>';
    if (it.kind === 'want' && it.link) meta += '<span class="meta">' + ic('link') + '</span>';
    if (it.comment_count) meta += '<span class="meta">' + ic('msg') + it.comment_count + '</span>';
    if (it.acks.length) meta += '<span class="meta" title="Acknowledged">' + ic(it.kind === 'want' ? 'thumb' : 'eye') + it.acks.length + '</span>';
    var right = '';
    if (opts.cta) right = opts.cta;
    else if (who) right = avatar(who, 'xs');
    else if (it.kind === 'task' && eff(it) !== 'done') right = '<span class="open-slot">open</span>';
    return '<div class="card k-' + it.kind + (eff(it) === 'done' ? ' is-done' : '') + '" role="button" tabindex="0" data-act="open" data-id="' + it.id + '">' +
      '<div class="card-top">' + typeChip(it.kind) + '<span class="key">' + esc(it.key) + '</span>' + prioIcon(it.priority) +
      '<span class="sp"></span>' + (opts.status ? statusPill(it) : '') + (it.points ? bp(it.points) : '') + '</div>' +
      '<div class="card-title">' + esc(it.title) + '</div>' +
      '<div class="card-meta">' + meta + '<span class="sp"></span>' + right + '</div>' +
      '</div>';
  }
  function emptyBox(emoji, text) { return '<div class="empty"><span class="big">' + emoji + '</span>' + text + '</div>'; }
  function sectionHead(title, count, extra) {
    return '<div class="section-head"><span class="section-title">' + title + '</span>' +
      (count != null ? '<span class="count">' + count + '</span>' : '') + '<span class="sp"></span>' + (extra || '') + '</div>';
  }
  function rich(text) {
    var out = esc(text);
    out = out.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    out = out.replace(/\bFAM-(\d+)\b/g, function (all, n) {
      var it = S.bySeq[n];
      return it ? '<a class="keylink" data-act="open" data-id="' + it.id + '">' + all + '</a>' : '<span class="keylink">' + all + '</span>';
    });
    return out;
  }

  /* ------------------------------------------------------------ QR code */
  function rr(x, y, w, h, r) {
    return 'M' + (x + r) + ',' + y + 'h' + (w - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 ' + r + ',' + r + 'v' + (h - 2 * r) +
      'a' + r + ',' + r + ' 0 0 1 -' + r + ',' + r + 'h-' + (w - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 -' + r + ',-' + r +
      'v-' + (h - 2 * r) + 'a' + r + ',' + r + ' 0 0 1 ' + r + ',-' + r + 'z';
  }
  function qrSVG(text) {
    if (typeof window.qrcode !== 'function') return null;
    var qr;
    try { qr = window.qrcode(0, 'M'); qr.addData(text); qr.make(); } catch (e) { return null; }
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
    return '<svg viewBox="0 0 ' + n + ' ' + n + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Invite QR code">' + parts.join('') + '</svg>';
  }
  function inviteLink() {
    var base = window.location.origin + window.location.pathname;
    return base + '#join=' + S.st.family.code;
  }

  /* ------------------------------------------------------------ phases */
  function setPhase(p) {
    S.phase = p;
    render();
  }
  function goAuth() {
    stopPolling(); closeSheet(true);
    S.st = null;
    setPhase('landing');
  }
  function render() {
    app.setAttribute('data-theme', S.theme);
    if (S.phase === 'boot') {
      stage.innerHTML = '<div class="splash"><div class="big-logo"><div class="inner">' + ic('check') + '</div></div></div>';
    } else if (S.phase === 'landing') {
      renderLanding();
    } else if (S.phase === 'auth') {
      renderAuth();
    } else if (S.phase === 'onboard') {
      renderOnboard();
    } else {
      renderShell();
      renderView(true);
    }
  }
  function refresh() {
    if (S.phase !== 'app') return;
    renderView(false);
    renderNav();
    if (S.sheet && S.sheet.type === 'detail') {
      var it = itemById(S.detail.id);
      if (!it) { closeSheet(); toast('That card was removed.'); return; }
      if (S.detail.data && S.detail.data.comments.length !== it.comment_count) loadDetail();
      renderDetail();
    }
  }
  function afterEnterApp() {
    if (S.pendingJoin) {
      if (S.st.family.code !== S.pendingJoin) toast('You are already on a family board. Leave it first to join another one.');
      S.pendingJoin = null;
    }
  }

  /* ------------------------------------------------------------ landing page */
  // What logged-out visitors see first: what the app is and how it works,
  // before they are asked to log in or sign up.
  var DEMO_FAM = [
    { name: 'Mom', avatar: '🦊', color: COLORS[1] },
    { name: 'Dad', avatar: '🐻', color: COLORS[6] },
    { name: 'Alex', avatar: '🐼', color: COLORS[0] },
    { name: 'Mia', avatar: '🦄', color: COLORS[2] }
  ];
  function demoCard(kind, key, title, meta, right, pts) {
    return '<div class="card demo k-' + kind + '" aria-hidden="true">' +
      '<div class="card-top">' + typeChip(kind) + '<span class="key">' + key + '</span><span class="sp"></span>' + (pts ? bp(pts) : '') + '</div>' +
      '<div class="card-title">' + title + '</div>' +
      '<div class="card-meta">' + meta + '<span class="sp"></span>' + right + '</div></div>';
  }
  function demoBoardHTML() {
    var m = function (name, icon, extra) { return '<span class="meta">' + ic(icon) + (name || '') + '</span>' + (extra || ''); };
    return '<div class="land-demo neu">' +
      '<div class="land-demo-head"><div><div class="page-kicker">Family board</div><div class="b">The Rivera family</div></div><span class="sp"></span>' +
      '<div class="stack">' + DEMO_FAM.map(function (x) { return avatar(x, 'sm'); }).join('') + '</div></div>' +
      '<div class="list">' +
      demoCard('task', 'FAM-12', 'Take out the recycling', m('Tue', 'clock') + m('turns', 'repeat'), avatar(DEMO_FAM[2], 'xs'), 10) +
      demoCard('task', 'FAM-14', 'Wash the car', m('Sat', 'clock') + m('', 'shield'), '<span class="open-slot">open</span>', 25) +
      demoCard('event', 'FAM-15', 'Picnic at the park', m('Sun · 12:00', 'calendar') + m('3', 'eye'), avatar(DEMO_FAM[0], 'xs')) +
      demoCard('want', 'FAM-18', 'New board game for game night', m('', 'link') + m('4', 'thumb'), avatar(DEMO_FAM[3], 'xs')) +
      '</div>' +
      '<div class="land-gain">' + BROWNIE + '+10 for Alex</div>' +
      '</div>';
  }
  function renderLanding() {
    var invited = !!S.pendingJoin;
    var steps = [
      ['Start a family board', 'Make an account, name your board and pick an avatar. It takes about a minute.'],
      ['Invite your people', 'Everyone else scans the board\'s QR code or types its 6-letter code. Up to 4 people per board.'],
      ['Plan, pitch in, earn', 'Add tasks, events and wants. Finish tasks to earn brownie points and level up.']
    ];
    var kinds = [
      ['task', 'Tasks', 'Chores and to-dos. Give one to someone or leave it open, set a due date and priority, and add brownie points as a reward.'],
      ['event', 'Events', 'Plans with a date, time and place. Everyone taps “I\'m in” so you know who\'s coming.'],
      ['want', 'Wants', 'Wishes for the family or for one person, with an optional link. Others can +1 the ones they like too.']
    ];
    var feats = [
      ['hand', 'Bounties anyone can claim', 'Put points on a task and leave it open. Whoever claims it and finishes it gets the points.'],
      ['shield', 'Optional approval', 'Mark a task as needing a check. When it\'s done, someone else approves it before the points are paid.'],
      ['repeat', 'Repeating tasks and turns', 'Repeat daily, on weekdays, weekly, every 2 weeks or monthly. Turn on “Take turns” to pass the job around.'],
      ['board', 'A board for the whole family', 'Cards move from To do to In progress, Review and Done. Filter by type, your own cards, or open bounties.'],
      ['chat', 'Family chat', 'Chat together and see a feed of what got done. Type FAM-12 to link a card. Every card has its own comments too.'],
      ['eye', 'See who\'s seen it', 'Every card shows who has read it, who\'s coming, or who +1\'d it. No more “I didn\'t know”.'],
      ['trophy', 'Levels and a podium', 'Climb from Rookie to Mythic, chase a weekly family goal, and see who\'s on top this week.'],
      ['device', 'Phone, computer, day or night', 'Made for phones first, with a wider board on computers and a dark night mode for evenings.']
    ];
    var faqs = [
      ['Who is it for?', 'Households of 2 to 4 people: parents and kids, couples, or roommates. Each board holds up to 4 people.'],
      ['Does everyone need to install an app?', 'No. Fun To Plan runs in the web browser on phones and computers. Each person makes their own account and joins with the board\'s code.'],
      ['Who can see our board?', 'Only the people on your board. Every change goes through the server, which checks that you belong to the family first.'],
      ['How do we get started without a blank board?', 'When you create a board you can add a few starter cards that show how things work. Delete them whenever you like.'],
      ['What if someone leaves?', 'Anyone can leave a board and rejoin later with the code, and they keep their brownie points. The person who made the board can also remove members.']
    ];
    var cta = invited
      ? '<button class="btn btn-dark btn-lg" data-act="land-auth" data-mode="signup">Join your family' + ic('arrow') + '</button>' +
        '<button class="btn btn-lg" data-act="land-auth" data-mode="login">I have an account</button>'
      : '<button class="btn btn-dark btn-lg" data-act="land-auth" data-mode="signup">Get started' + ic('arrow') + '</button>' +
        '<button class="btn btn-lg" data-act="land-auth" data-mode="login">I have an account</button>';

    stage.innerHTML =
      '<div class="land"><div class="land-inner">' +
      '<header class="land-nav"><div class="brand-logo">' + ic('check') + '</div><div class="brand-name">Fun To Plan</div><span class="sp"></span>' +
      '<button class="icon-btn" data-act="theme" aria-label="Switch light or night mode">' + ic('moon') + '</button>' +
      '<button class="btn btn-sm" data-act="land-auth" data-mode="login">Log in</button></header>' +

      (invited ? '<div class="notice">' + ic('qr') + '<span>You\'ve been invited to a family board! Have a look around, then create an account (or log in) to join.</span></div>' : '') +

      '<section class="land-hero">' +
      '<div class="land-copy">' +
      '<span class="pill pill-in">' + ic('family') + 'For families of 2 to 4</span>' +
      '<h1 class="land-h1">The family to-do list that <span class="grad-text">feels like a game.</span></h1>' +
      '<p class="land-lead">Fun To Plan puts chores, plans and wish lists on one shared board. Everyone can see what\'s going on, pitch in, and earn <b>brownie points</b> for getting things done.</p>' +
      '<div class="land-cta">' + cta + '</div>' +
      '<p class="small muted b">Works in the browser on phones and computers. No app store needed.</p>' +
      '</div>' +
      demoBoardHTML() +
      '</section>' +

      '<section class="land-sec"><div class="page-kicker">How it works</div><h2 class="land-h2">Up and running in three steps</h2>' +
      '<ol class="land-steps">' + steps.map(function (s, i) {
        return '<li class="neu pad"><span class="land-num">' + (i + 1) + '</span><div class="b">' + s[0] + '</div><p class="land-p">' + s[1] + '</p></li>';
      }).join('') + '</ol></section>' +

      '<section class="land-sec"><div class="page-kicker">One board, three kinds of cards</div><h2 class="land-h2">Everything the family needs to keep track of</h2>' +
      '<div class="land-grid3">' + kinds.map(function (k) {
        return '<div class="neu pad land-kind"><div class="row">' + typeChip(k[0]) + '<span class="section-title">' + k[1] + '</span></div><p class="land-p">' + k[2] + '</p></div>';
      }).join('') + '</div>' +
      '<p class="land-p muted center">Each card gets a short key like <span class="key">FAM-12</span>, so it\'s easy to talk about in chat.</p></section>' +

      '<section class="land-sec"><div class="page-kicker">Features</div><h2 class="land-h2">Small touches that keep everyone on the same page</h2>' +
      '<div class="land-feats">' + feats.map(function (f) {
        return '<div class="land-feat"><span class="land-ic">' + ic(f[0]) + '</span><div><div class="b">' + f[1] + '</div><p class="land-p">' + f[2] + '</p></div></div>';
      }).join('') + '</div></section>' +

      '<section class="land-sec"><div class="neu pad land-points">' +
      '<div class="land-points-head">' + BROWNIE.replace('class="brownie"', 'class="brownie land-brownie"') +
      '<div><div class="page-kicker">Brownie points</div><h2 class="land-h2">Why the chores actually get done</h2></div></div>' +
      '<ul class="land-list">' +
      '<li>Add points to a task. Whoever finishes it earns them.</li>' +
      '<li>If a task needs approval, the points are paid once someone else says it\'s done.</li>' +
      '<li>Points add up to levels, a weekly family goal, and a podium for the week and for all time.</li>' +
      '<li>Reopen a finished card and its points are taken back, so the score stays fair.</li>' +
      '</ul>' +
      '<div class="land-levels">' + LEVELS.map(function (l) { return '<span class="pill">' + l[1] + ' <span class="muted">' + l[0] + '</span></span>'; }).join('') + '</div>' +
      '</div></section>' +

      '<section class="land-sec"><div class="page-kicker">Questions</div><h2 class="land-h2">Good to know</h2>' +
      '<div class="land-faq">' + faqs.map(function (q) {
        return '<details class="neu"><summary>' + q[0] + ic('down') + '</summary><p class="land-p">' + q[1] + '</p></details>';
      }).join('') + '</div></section>' +

      '<section class="land-sec"><div class="land-final">' +
      '<h2 class="land-h2">' + (invited ? 'Your family is waiting.' : 'Ready to make chores a bit more fun?') + '</h2>' +
      '<p class="land-p">' + (invited ? 'Create an account or log in, pick an avatar, and you\'re on the board.' : 'Start a board, invite your family, and hand out the first brownie points today.') + '</p>' +
      '<div class="land-cta center-cta">' + cta + '</div></div></section>' +

      '<footer class="land-foot small muted b">Fun To Plan · one shared board for the whole family' + legalLink(' · ') + ' · ' + ideaLink() + '</footer>' +
      '</div></div>';
  }

  /* ------------------------------------------------------------ auth screen */
  function renderAuth() {
    var signup = S.authMode === 'signup';
    stage.innerHTML =
      '<div class="auth"><div class="auth-inner">' +
      '<div><button type="button" class="btn btn-sm btn-ghost" data-act="land-back">' + ic('back') + 'Back</button></div>' +
      '<div class="auth-hero"><div class="big-logo"><div class="inner">' + ic('check') + '</div></div>' +
      '<div><div class="auth-title">Fun To Plan</div></div>' +
      '<p class="auth-sub">One shared board for the whole family. Tasks, events, wants, chat and brownie points.</p></div>' +
      (S.pendingJoin ? '<div class="notice">' + ic('qr') + '<span>You\'ve been invited to a family board! Log in or create an account to join.</span></div>' : '') +
      '<form class="neu pad form" data-form="auth" novalidate>' +
      '<div class="seg"><button type="button" class="' + (signup ? '' : 'on') + '" data-act="auth-mode" data-mode="login">Log in</button>' +
      '<button type="button" class="' + (signup ? 'on' : '') + '" data-act="auth-mode" data-mode="signup">Sign up</button></div>' +
      '<label class="field"><span class="label">Email</span><input class="input" name="email" type="email" autocomplete="email" inputmode="email" placeholder="you@family.com" required></label>' +
      '<label class="field"><span class="label">Password</span><input class="input" name="password" type="password" autocomplete="' + (signup ? 'new-password' : 'current-password') + '" placeholder="' + (signup ? 'At least 6 characters' : 'Your password') + '" required></label>' +
      (signup && window.LegalKit ? LegalKit.consentField() : '') +
      '<div class="err" data-err></div>' +
      '<button class="btn btn-dark btn-lg btn-block" type="submit">' + (signup ? 'Create account' : 'Log in') + '</button>' +
      (signup ? '' : '<div class="center"><button type="button" class="link-btn" data-act="forgot">Forgot password?</button></div>') +
      '</form>' +
      '<p class="center small muted b">New here? <button type="button" class="link-btn" data-act="land-back">See how Fun To Plan works</button></p>' +
      '<p class="center tiny muted b">' + legalLink('') + ' · ' + ideaLink() + '</p>' +
      '</div></div>';
    var first = $('[name=email]');
    if (first && window.matchMedia && window.matchMedia('(min-width: 760px)').matches) first.focus();
  }

  /* ------------------------------------------------------------ onboarding */
  function profilePickerHTML(prof) {
    S.pick.avatar = prof.avatar; S.pick.color = prof.color;
    return '<label class="field"><span class="label">Your name</span><input class="input" name="display_name" maxlength="24" value="' + esc(prof.name) + '" placeholder="Mom, Dad, Alex…"></label>' +
      '<div class="field"><span class="label">Avatar</span><div class="emoji-grid" data-group="avatar">' +
      AVATARS.map(function (a) { return '<button type="button" class="' + (a === prof.avatar ? 'on' : '') + '" data-act="pick" data-val="' + a + '">' + a + '</button>'; }).join('') +
      '</div></div>' +
      '<div class="field"><span class="label">Color</span><div class="swatches" data-group="color">' +
      COLORS.map(function (c) { return '<button type="button" class="swatch ' + (c === prof.color ? 'on' : '') + '" data-act="pick" data-val="' + c + '" aria-label="' + c + '"><i style="background:' + c + '"></i></button>'; }).join('') +
      '</div></div>';
  }
  function readProfile(scope) {
    var nameEl = $('[name=display_name]', scope);
    return { display_name: nameEl ? nameEl.value.trim() : '', avatar: S.pick.avatar, color: S.pick.color };
  }
  function renderOnboard() {
    var guess = (S.email || '').split('@')[0].replace(/[._-]+/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); }).slice(0, 24);
    var prof = { name: guess, avatar: AVATARS[Math.floor(Math.random() * 8)], color: COLORS[0] };
    var pv = S.preview;
    stage.innerHTML =
      '<div class="auth"><div class="auth-inner auth-wide">' +
      '<div class="auth-hero"><div class="big-logo"><div class="inner">' + ic('family') + '</div></div>' +
      '<div class="auth-title">Welcome aboard!</div><p class="auth-sub">Pick how the family will see you, then start a board or join one.</p></div>' +
      (S.pendingJoin ? '<div class="notice">' + ic('qr') + '<span>You are invited! Pick your name and avatar, then tap <b>Join family</b>.</span></div>' : '') +
      '<div class="neu pad form" id="ob-profile">' + profilePickerHTML(prof) + '</div>' +
      '<div class="onboard-grid' + (S.pendingJoin ? ' invited' : '') + '">' +
      '<form class="neu pad form" data-form="join" novalidate>' +
      '<div class="row">' + '<span class="type t-task">' + ic('qr') + '</span><span class="section-title">Join a family</span></div>' +
      '<p class="muted small b">Scan the QR code on a family member\'s phone, or type their 6-letter code.</p>' +
      '<input class="input input-code" name="code" maxlength="6" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="ABC123" value="' + esc(S.pendingJoin || '') + '">' +
      '<div id="join-preview">' + (pv ? previewHTML(pv) : '') + '</div>' +
      '<div class="err" data-err></div>' +
      '<div class="row">' +
      ('BarcodeDetector' in window ? '<button type="button" class="btn" data-act="scan">' + ic('camera') + 'Scan</button>' : '') +
      '<button class="btn btn-dark btn-block" type="submit">Join family</button></div>' +
      '</form>' +
      '<form class="neu pad form" data-form="create" novalidate>' +
      '<div class="row"><span class="type t-event">' + ic('plus') + '</span><span class="section-title">Start a new family board</span></div>' +
      '<p class="muted small b">You\'ll get a QR code to invite up to 3 more people.</p>' +
      '<label class="field"><span class="label">Family name</span><input class="input" name="family_name" maxlength="40" placeholder="The Smiths"></label>' +
      '<div class="switch-row"><div class="sp"><div class="t">Add starter cards</div><div class="s">A few examples to show how it works</div></div><button type="button" class="toggle on" data-act="toggle" data-key="seed" aria-label="Add starter cards"></button></div>' +
      '<div class="err" data-err></div>' +
      '<button class="btn btn-blue btn-block btn-lg" type="submit">' + ic('sparkle') + 'Create board</button>' +
      '</form>' +
      '</div>' +
      '<p class="center small muted b">Signed in as ' + esc(S.email || '') + ' · <button class="link-btn" data-act="logout">Log out</button></p>' +
      '</div></div>';
    if (S.pendingJoin && !pv) previewJoin(S.pendingJoin);
  }
  function previewHTML(pv) {
    return '<div class="preview-fam"><div class="stack">' + pv.members.map(function (m) { return avatar(m, 'sm'); }).join('') + '</div>' +
      '<div class="b">' + esc(pv.name) + '</div><div class="small muted b">' + pv.members.length + ' of 4 seats taken' + (pv.full ? ' · this board is full' : '') + '</div></div>';
  }
  function previewJoin(code) {
    api('preview_join', { code: code }).then(function (pv) {
      S.preview = pv;
      var box = $('#join-preview'); if (box) box.innerHTML = previewHTML(pv);
      var err = $('[data-form=join] [data-err]'); if (err) err.textContent = '';
    }, function (e) {
      var err = $('[data-form=join] [data-err]'); if (err) err.textContent = e.message;
      if (e.code === 'auth') goAuth();
    });
  }

  /* ------------------------------------------------------------ app shell */
  var NAV = [
    { id: 'home', label: 'Home', icon: 'home' },
    { id: 'board', label: 'Board', icon: 'board' },
    { id: 'chat', label: 'Chat', icon: 'chat' },
    { id: 'family', label: 'Family', icon: 'family' }
  ];
  function renderShell() {
    stage.innerHTML =
      '<aside class="rail" id="ftp-rail"></aside>' +
      '<main class="main" id="ftp-main"><div class="content" id="ftp-view"></div></main>' +
      '<nav class="tabbar" id="ftp-tabbar"></nav>';
    renderNav();
  }
  function badgeFor(id) {
    if (id === 'chat') { var u = unreadCount(); return u ? '<span class="dot">' + (u > 9 ? '9+' : u) + '</span>' : ''; }
    if (id === 'home') { var n = needsYou().length; return n ? '<span class="dot">' + n + '</span>' : ''; }
    return '';
  }
  function renderNav() {
    var rail = $('#ftp-rail'), tab = $('#ftp-tabbar');
    if (!rail || !tab) return;
    var m = me();
    rail.innerHTML =
      '<div class="rail-brand"><span class="brand-logo">' + ic('check') + '</span><div><div class="brand-name">Fun To Plan</div><div class="brand-sub">' + esc(S.st.family.name) + '</div></div></div>' +
      '<nav class="rail-nav">' + NAV.map(function (n) {
        return '<button class="rail-item ' + (S.view === n.id ? 'on' : '') + '" data-act="nav" data-view="' + n.id + '">' + ic(n.icon) + n.label + badgeFor(n.id) + '</button>';
      }).join('') + '</nav>' +
      '<button class="btn btn-dark btn-lg rail-add" data-act="new">' + ic('plus') + 'New card</button>' +
      '<div class="rail-spacer"></div>' +
      (m ? '<button class="rail-me" data-act="nav" data-view="family">' + avatar(m) + '<div class="sp"><div class="b">' + esc(m.name) + '</div><div class="small muted b">Lv ' + levelOf(m.points).n + ' · ' + levelOf(m.points).title + '</div></div>' + bp(m.points) + '</button>' : '');
    var items = NAV.map(function (n) {
      return '<button class="tab ' + (S.view === n.id ? 'on' : '') + '" data-act="nav" data-view="' + n.id + '" aria-label="' + n.label + '">' + ic(n.icon) + n.label + badgeFor(n.id) + '</button>';
    });
    items.splice(2, 0, '<div><button class="tab-add" data-act="new" aria-label="New card">' + ic('plus') + '</button></div>');
    tab.innerHTML = items.join('');
  }
  function renderView(fresh) {
    var view = $('#ftp-view'), main = $('#ftp-main');
    if (!view) return;
    if (S.view === 'chat') {
      var list = $('#chat-list');
      if (list && !fresh) {
        var nearBottom = main.scrollHeight - main.scrollTop - main.clientHeight < 140;
        list.innerHTML = chatListHTML();
        if (nearBottom) main.scrollTop = main.scrollHeight;
      } else {
        view.innerHTML = viewChat();
        main.scrollTop = main.scrollHeight;
      }
      markChatSeen();
      return;
    }
    var html = S.view === 'board' ? viewBoard() : S.view === 'family' ? viewFamily() : viewHome();
    view.innerHTML = html;
    if (fresh) main.scrollTop = 0;
  }
  function go(viewId) {
    S.view = viewId; store('ftp.view', viewId);
    renderView(true);
    renderNav();
  }

  /* ------------------------------------------------------------ home */
  function greeting() {
    var h = new Date().getHours();
    if (h < 5) return 'Hey night owl';
    if (h < 12) return 'Good morning';
    if (h < 18) return 'Good afternoon';
    return 'Good evening';
  }
  function ring(pct) {
    var c = 2 * Math.PI * 38, off = c * (1 - Math.max(0.02, Math.min(1, pct)));
    return '<svg viewBox="0 0 88 88"><defs><linearGradient id="ftp-ring-grad" x1="0" y1="1" x2="1" y2="0">' +
      '<stop offset="0" stop-color="#2fa36b"/><stop offset=".35" stop-color="#f2b51d"/><stop offset=".7" stop-color="#f07c2a"/><stop offset="1" stop-color="#e5484d"/></linearGradient></defs>' +
      '<circle class="track" cx="44" cy="44" r="38"/><circle class="fill" cx="44" cy="44" r="38" stroke-dasharray="' + c.toFixed(1) + '" stroke-dashoffset="' + off.toFixed(1) + '"/></svg>';
  }
  function viewHome() {
    var m = me(), lv = levelOf(m.points), fam = S.st.family;
    var needs = needsYou();
    var bounties = S.st.items.filter(function (it) { return it.kind === 'task' && it.status === 'todo' && !it.assignee && it.points > 0; }).sort(sortOpen);
    var events = S.st.items.filter(function (it) { return it.kind === 'event' && eff(it) === 'todo' && dayDiff(new Date(it.event_at)) <= 14; })
      .sort(function (a, b) { return a.event_at < b.event_at ? -1 : 1; });
    var recent = S.st.items.filter(function (it) { return it.kind !== 'event' && it.status === 'done'; }).sort(sortDone).slice(0, 4);
    var wt = weekTotal(), goal = fam.weekly_goal, gp = Math.min(1, wt / goal);

    var h = '<div class="page-head"><div class="sp"><div class="page-kicker">' + esc(fam.name) + '</div><div class="page-title">Today</div></div>' +
      '<button class="icon-btn" data-act="theme" aria-label="Toggle night mode">' + ic('moon') + '</button></div>';

    h += '<div class="grid-2"><div>';
    h += '<div class="neu hero"><div class="ring">' + ring(lv.pct) + '<div class="ring-inner"><span class="lvl">LEVEL</span><span class="num">' + lv.n + '</span></div></div>' +
      '<div style="min-width:0"><div class="hero-hello">' + greeting() + ',</div><div class="hero-name">' + esc(m.name) + ' ' + esc(m.avatar) + '</div>' +
      '<div class="hero-stats"><span class="pill pill-black">' + ic('trophy') + esc(lv.title) + '</span>' + bp(m.points) +
      '<span class="pill pill-in">+' + Math.max(0, m.week_points) + ' this week</span></div>' +
      '<div class="hero-next">' + (lv.next ? lv.toNext + ' brownie points to level ' + (lv.n + 1) : 'Max level reached. Legendary!') + '</div></div></div>';
    h += '</div><div>';
    h += '<div class="neu goal" style="margin-top:0"><div class="row"><span class="page-kicker">Family goal · last 7 days</span><span class="sp"></span>' + bp(wt) + '</div>' +
      '<div class="bar"><i style="width:' + Math.round(gp * 100) + '%"></i></div>' +
      '<div class="row" style="margin-top:12px"><div class="stack">' + activeMembers().map(function (x) { return avatar(x, 'xs'); }).join('') + '</div>' +
      '<span class="small b muted">' + (wt >= goal ? 'Goal smashed! Treat yourselves 🎉' : (goal - wt) + ' brownie points to go together') + '</span></div></div>';
    h += '</div></div>';

    h += '<div class="section">' + sectionHead('Needs you', needs.length || '') +
      (needs.length ? '<div class="list">' + needs.slice(0, 8).map(function (it) {
        var cta = '';
        if (it.status === 'review') cta = '<button class="btn btn-sm btn-dark" data-act="approve" data-id="' + it.id + '">' + ic('shield', 'ic-sm') + 'Approve</button>';
        else if (it.kind === 'event') cta = '<button class="btn btn-sm" data-act="ack" data-id="' + it.id + '">' + ic('thumb', 'ic-sm') + 'I\'m in</button>';
        else cta = '<button class="btn btn-sm" data-act="complete" data-id="' + it.id + '">' + ic('check', 'ic-sm') + 'Done</button>';
        return cardHTML(it, { cta: cta, status: it.status === 'review' });
      }).join('') + '</div>' : emptyBox('🌤️', 'All clear! Nothing waiting on you.')) + '</div>';

    h += '<div class="grid-2">';
    h += '<div class="section">' + sectionHead('Open bounties', bounties.length || '', '<button class="btn btn-sm btn-ghost" data-act="board-filter" data-f="bounty">See all</button>') +
      (bounties.length ? '<div class="list">' + bounties.slice(0, 5).map(function (it) {
        return cardHTML(it, { cta: '<button class="btn btn-sm btn-blue" data-act="claim" data-id="' + it.id + '">' + ic('hand', 'ic-sm') + 'Claim</button>' });
      }).join('') + '</div>' : emptyBox('🍫', 'No open bounties. Add a task with brownie points!')) + '</div>';
    h += '<div class="section">' + sectionHead('Coming up', events.length || '') +
      (events.length ? '<div class="list">' + events.slice(0, 5).map(function (it) { return cardHTML(it); }).join('') + '</div>' : emptyBox('📅', 'No events in the next two weeks.')) + '</div>';
    h += '</div>';

    if (recent.length) {
      h += '<div class="section">' + sectionHead('Recently done') + '<div class="list">' + recent.map(function (it) {
        var who = S.mm[it.completed_by];
        return '<div class="card" role="button" tabindex="0" data-act="open" data-id="' + it.id + '"><div class="card-row">' + avatar(who, 'sm') +
          '<div class="sp" style="min-width:0"><div class="card-title">' + esc(it.title) + '</div><div class="small muted b">' + esc(who ? who.name : 'Someone') + ' · ' + ago(it.completed_at) + '</div></div>' +
          (it.points_awarded ? bp('+' + it.points_awarded) : statusPill(it)) + '</div></div>';
      }).join('') + '</div></div>';
    }
    return h;
  }

  /* ------------------------------------------------------------ board */
  var FILTERS = [
    { id: 'all', label: 'All', icon: 'board' },
    { id: 'task', label: 'Tasks', icon: 'check' },
    { id: 'event', label: 'Events', icon: 'calendar' },
    { id: 'want', label: 'Wants', icon: 'star' },
    { id: 'mine', label: 'Mine', icon: 'user' },
    { id: 'bounty', label: 'Bounties', icon: 'trophy' }
  ];
  function filtered() {
    var f = S.filter, mine = S.st.me;
    return S.st.items.filter(function (it) {
      if (f === 'task' || f === 'event' || f === 'want') return it.kind === f;
      if (f === 'mine') return it.assignee === mine;
      if (f === 'bounty') return it.kind === 'task' && it.points > 0;
      return true;
    });
  }
  function viewBoard() {
    var fam = S.st.family, all = S.st.items;
    var open = all.filter(function (it) { return eff(it) !== 'done'; }).length;
    var done = all.length - open;
    var pct = all.length ? done / all.length : 0;
    var items = filtered();
    var cols = {};
    COLS.forEach(function (c) { cols[c.id] = []; });
    items.forEach(function (it) { cols[eff(it)].push(it); });
    COLS.forEach(function (c) { cols[c.id].sort(c.id === 'done' ? sortDone : sortOpen); });

    var h = '<div class="page-head"><div class="sp"><div class="page-kicker">Board</div><div class="page-title">Family epic</div></div>' +
      '<button class="btn btn-dark" data-act="new">' + ic('plus') + 'Card</button></div>';
    h += '<div class="neu epic"><span class="epic-tag">' + ic('sparkle', 'ic-sm') + 'EPIC · FAMILY</span>' +
      '<div class="epic-title">' + esc(fam.name) + '</div>' +
      '<div class="bar"><i style="width:' + Math.round(pct * 100) + '%"></i></div>' +
      '<div class="epic-stats"><span><b>' + open + '</b>open</span><span><b>' + done + '</b>done (30 days)</span>' +
      '<span><b>' + all.filter(function (it) { return it.kind === 'task' && it.status === 'review'; }).length + '</b>in review</span>' +
      '<span class="sp"></span><div class="stack">' + activeMembers().map(function (m) { return avatar(m, 'xs'); }).join('') + '</div></div></div>';

    h += '<div class="board-tools"><div class="chips">' + FILTERS.map(function (f) {
      return '<button class="chip ' + (S.filter === f.id ? 'on' : '') + '" data-act="filter" data-f="' + f.id + '">' + ic(f.icon, 'ic-sm') + f.label + '</button>';
    }).join('') + '</div>';
    h += '<div class="seg col-seg">' + COLS.map(function (c) {
      return '<button class="' + (S.col === c.id ? 'on' : '') + '" data-act="col" data-col="' + c.id + '">' + c.label.replace('In progress', 'Doing') + ' <span class="muted">' + cols[c.id].length + '</span></button>';
    }).join('') + '</div></div>';

    h += '<div class="board">' + COLS.map(function (c) {
      var list = cols[c.id];
      var body = list.length ? list.map(function (it) { return cardHTML(it); }).join('') :
        emptyBox(c.id === 'review' ? '🛡️' : c.id === 'done' ? '🏁' : c.id === 'doing' ? '🛠️' : '✨',
          c.id === 'review' ? 'Finished tasks that need approval land here.' : c.id === 'done' ? 'Finished cards show up here for 30 days.' : c.id === 'doing' ? 'Start a card to move it here.' : 'Nothing to do. Add a card!');
      return '<section class="board-col ' + (S.col === c.id ? 'on' : '') + '"><div class="col-head">' + c.label + '<span class="count">' + list.length + '</span></div>' +
        '<div class="col-body">' + body + '</div></section>';
    }).join('') + '</div>';
    return h;
  }

  /* ------------------------------------------------------------ chat */
  function chatListHTML() {
    var msgs = S.st.messages, out = [], lastDay = '';
    if (!msgs.length) return emptyBox('💬', 'Say hi to the family!');
    msgs.forEach(function (m) {
      var d = new Date(m.created), day = ymd(d);
      if (day !== lastDay) { out.push('<div class="day-sep">' + fmtDay(d) + '</div>'); lastDay = day; }
      var a = S.mm[m.author];
      if (m.kind === 'system') {
        out.push('<div class="sys">' + (a ? avatar(a, 'xs') : '') + '<span><b>' + esc(a ? a.name : 'Someone') + '</b> ' + rich(m.text) + '</span></div>');
        return;
      }
      var mine = m.author === S.st.me;
      out.push('<div class="msg ' + (mine ? 'mine' : '') + '">' + (mine ? '' : avatar(a, 'sm')) +
        '<div class="bubble">' + (mine ? '' : '<span class="who">' + esc(a ? a.name : 'Someone') + '</span>') + rich(m.text) +
        '<span class="when">' + fmtTime(d) + '</span></div></div>');
    });
    return out.join('');
  }
  function viewChat() {
    return '<div class="chat-wrap"><div class="page-head"><div class="sp"><div class="page-kicker">' + esc(S.st.family.name) + '</div><div class="page-title">Family chat</div></div>' +
      '<div class="stack">' + activeMembers().map(function (m) { return avatar(m, 'sm'); }).join('') + '</div></div>' +
      '<div class="chat-list" id="chat-list">' + chatListHTML() + '</div>' +
      '<form class="composer" data-form="chat"><textarea class="textarea" name="text" rows="1" maxlength="1000" placeholder="Message the family…"></textarea>' +
      '<button class="send" type="submit" aria-label="Send">' + ic('send') + '</button></form></div>';
  }

  /* ------------------------------------------------------------ family */
  function viewFamily() {
    var fam = S.st.family, m = me(), lv = levelOf(m.points), members = activeMembers();
    var owner = isOwner();
    var h = '<div class="page-head"><div class="sp"><div class="page-kicker">Family</div><div class="page-title">' + esc(fam.name) + '</div></div>' +
      (owner ? '<button class="icon-btn" data-act="family-settings" aria-label="Family settings">' + ic('gear') + '</button>' : '') + '</div>';

    h += '<div class="grid-2"><div>';
    // invite
    var qr = qrSVG(inviteLink());
    var spots = fam.max_members - members.length;
    h += '<div class="neu invite">' +
      (qr ? '<div class="qr-frame" data-act="invite" role="button" tabindex="0" aria-label="Show big QR code">' + qr + '</div>' : '') +
      '<div class="col" style="gap:14px"><div><div class="section-title">Invite the family</div>' +
      '<div class="small muted b">' + (spots > 0 ? 'Scan with a phone camera to join. ' + plural(spots, 'seat') + ' left.' : 'Your board is full (4 people).') + '</div></div>' +
      '<div class="code-tiles">' + fam.code.split('').map(function (c) { return '<span>' + c + '</span>'; }).join('') + '</div>' +
      '<div class="seats">' + [0, 1, 2, 3].map(function (i) { var x = members[i]; return x ? avatar(x, 'sm') : '<span class="seat">·</span>'; }).join('') + '</div>' +
      '<div class="row wrap"><button class="btn btn-sm" data-act="copy-link">' + ic('copy', 'ic-sm') + 'Copy link</button>' +
      (navigator.share ? '<button class="btn btn-sm" data-act="share-link">' + ic('share', 'ic-sm') + 'Share</button>' : '') +
      '<button class="btn btn-sm btn-dark" data-act="invite">' + ic('qr', 'ic-sm') + 'Big QR</button></div></div></div>';

    // leaderboard
    var key = S.lb === 'week' ? 'week_points' : 'points';
    var ranked = members.slice().sort(function (a, b) { return b[key] - a[key]; });
    var slots = [ranked[1], ranked[0], ranked[2]], places = [2, 1, 3], medals = ['🥈', '🥇', '🥉'];
    h += '<div class="section">' + sectionHead('Brownie leaderboard', null,
      '<div class="seg dark" style="width:190px"><button class="' + (S.lb === 'week' ? 'on' : '') + '" data-act="lb" data-lb="week">7 days</button><button class="' + (S.lb === 'all' ? 'on' : '') + '" data-act="lb" data-lb="all">All time</button></div>') +
      '<div class="neu podium">' + slots.map(function (x, i) {
        if (!x) return '<div class="pod p' + places[i] + ' empty-pod"><span class="avatar lg empty">?</span><div class="nm">Open seat</div><div class="pillar"><span class="place">' + medals[i] + '</span></div></div>';
        return '<div class="pod p' + places[i] + '">' + avatar(x, 'lg') + '<div class="nm">' + esc(x.name) + '</div>' +
          '<div class="pillar"><span class="place">' + medals[i] + '</span><span class="pts">' + BROWNIE + Math.max(0, x[key]) + '</span></div></div>';
      }).join('') + '</div></div>';
    h += '</div><div>';

    // members
    h += '<div class="section" style="margin-top:0">' + sectionHead('Members', members.length + ' / ' + fam.max_members) + '<div class="neu">' +
      members.map(function (x) {
        var l = levelOf(x.points);
        return '<div class="member-row">' + avatar(x) + '<div class="sp" style="min-width:0"><div class="row" style="gap:6px"><span class="nm">' + esc(x.name) + '</span>' +
          (x.id === m.id ? '<span class="pill pill-blue">you</span>' : '') + (x.role === 'owner' ? '<span class="pill pill-in">owner</span>' : '') + '</div>' +
          '<div class="lvl-chip">Lv ' + l.n + ' ' + l.title + ' · ' + plural(x.done_30, 'card') + ' done this month</div></div>' + bp(x.points) +
          (owner && x.id !== m.id ? '<button class="icon-btn flat" data-act="remove-member" data-id="' + x.id + '" aria-label="Remove ' + esc(x.name) + '">' + ic('close', 'ic-sm') + '</button>' : '') +
          '</div>';
      }).join('') + '</div></div>';

    // settings
    h += '<div class="section">' + sectionHead('Settings') + '<div class="neu">' +
      setting('profile', 'user', 'Edit my profile', esc(m.avatar + ' ' + m.name) + ' · Level ' + lv.n + ' ' + lv.title) +
      (owner ? setting('family-settings', 'gear', 'Family settings', 'Name and weekly brownie goal') : '') +
      '<div class="setting"><span class="ic-wrap">' + ic('moon') + '</span><div class="sp"><div class="t">Night mode</div><div class="s">The fridge after dark</div></div>' +
      '<button class="toggle ' + (S.theme === 'night' ? 'on' : '') + '" data-act="theme" aria-label="Night mode"></button></div>' +
      (owner ? setting('regen-code', 'refresh', 'New join code', 'Old QR codes and links stop working') : '') +
      (window.LegalKit ? '<button class="setting" data-lk-open="overview"><span class="ic-wrap">' + ic('shield') + '</span><div class="sp"><div class="t">Privacy &amp; Terms</div><div class="s">Your data, your rights, the rules</div></div></button>' : '') +
      setting('leave', 'logout', 'Leave family', 'Your cards stay on the board', true) +
      setting('logout', 'logout', 'Log out', esc(S.email || ''), false) +
      '</div></div>';
    h += '</div></div>';
    h += '<p class="center tiny muted b" style="margin-top:26px">Fun To Plan · made for families of 2–4 · board ' + esc(fam.code) + '</p>';
    return h;
  }
  // "Privacy & Terms" link (opens the shared legal page from legal-kit.js)
  function legalLink(prefix) {
    return window.LegalKit ? prefix + '<button type="button" class="link-btn" data-lk-open="overview">Privacy &amp; Terms</button>' : '';
  }
  // "Suggest an idea": the Prepsto feedback panel (widget.js in anvil.yaml head_html slides it in; plain link otherwise)
  function ideaLink() {
    return '<a class="link-btn" href="https://prepsto.com/#f/dj4ujb9" target="_blank" rel="noopener" data-prepsto-open>Suggest an idea</a>';
  }
  function setting(act, icon, title, sub, danger) {
    return '<button class="setting ' + (danger ? 'danger' : '') + '" data-act="' + act + '"><span class="ic-wrap">' + ic(icon) + '</span><div class="sp"><div class="t">' + title + '</div><div class="s">' + sub + '</div></div></button>';
  }

  /* ------------------------------------------------------------ sheets */
  function openSheet(o) {
    closeSheet(true);
    S.sheet = o;
    layer.innerHTML = '<div class="backdrop" data-act="close-sheet"></div>' +
      '<div class="sheet" role="dialog" aria-modal="true"><div class="sheet-grip"></div>' +
      '<div class="sheet-head" id="sheet-head">' + (o.head || '<span class="sheet-title">' + esc(o.title || '') + '</span><span class="sp"></span>') +
      '<button class="icon-btn" data-act="close-sheet" aria-label="Close">' + ic('close') + '</button></div>' +
      '<div class="sheet-body" id="sheet-body">' + (o.body || '') + '</div>' +
      (o.foot ? '<div class="sheet-foot" id="sheet-foot">' + o.foot + '</div>' : '') + '</div>';
    void layer.offsetWidth;
    layer.classList.add('open');
    if (o.focus) { var f = $(o.focus, layer); if (f && window.innerWidth > 700) setTimeout(function () { f.focus(); }, 250); }
  }
  function closeSheet(immediate) {
    var o = S.sheet;
    S.sheet = null;
    if (o && o.onClose) o.onClose();
    if (o && o.type === 'detail') S.detail = null;
    if (!layer) return;
    layer.classList.remove('open');
    if (immediate) { layer.innerHTML = ''; return; }
    setTimeout(function () { if (!layer.classList.contains('open')) layer.innerHTML = ''; }, 320);
  }
  function confirmBox(title, text, okLabel, danger) {
    return new Promise(function (resolve) {
      var done = false;
      function fin(v) { if (!done) { done = true; resolve(v); } }
      openSheet({
        type: 'confirm', title: title,
        body: '<p class="b" style="color:var(--ink-2)">' + esc(text) + '</p>',
        foot: '<button class="btn sp" data-act="close-sheet">Cancel</button><button class="btn sp ' + (danger ? 'btn-danger' : 'btn-dark') + '" data-act="confirm-ok">' + esc(okLabel) + '</button>',
        onClose: function () { fin(false); },
        resolve: function () { fin(true); }
      });
    });
  }
  function promptBox(title, placeholder, okLabel) {
    return new Promise(function (resolve) {
      var done = false;
      function fin(v) { if (!done) { done = true; resolve(v); } }
      openSheet({
        type: 'prompt', title: title, focus: 'textarea',
        body: '<textarea class="textarea" name="prompt" maxlength="500" placeholder="' + esc(placeholder) + '"></textarea>',
        foot: '<button class="btn sp" data-act="close-sheet">Cancel</button><button class="btn sp btn-dark" data-act="confirm-ok">' + esc(okLabel) + '</button>',
        onClose: function () { fin(null); },
        resolve: function () { var t = $('[name=prompt]', layer); fin(t ? t.value.trim() : ''); }
      });
    });
  }

  /* ---------- detail */
  function openDetail(id) {
    var it = itemById(id);
    if (!it) return;
    S.detail = { id: id, data: null };
    openSheet({
      type: 'detail', head: '', body: '',
      foot: '<form class="row" style="flex:1" data-form="comment"><input class="input" name="text" maxlength="1000" autocomplete="off" placeholder="Add a comment…">' +
        '<button class="send" type="submit" aria-label="Post comment">' + ic('send') + '</button></form>'
    });
    renderDetail();
    loadDetail();
  }
  function loadDetail() {
    if (!S.detail) return;
    var id = S.detail.id;
    api('item_detail', { id: id }).then(function (d) {
      if (S.detail && S.detail.id === id) { S.detail.data = d; renderDetail(); }
    }, function (e) { if (e.code === 'gone') { closeSheet(); toast(e.message, true); } });
  }
  function actBtn(act, label, icon, cls, id) {
    return '<button class="btn ' + (cls || '') + '" data-act="' + act + '" data-id="' + id + '">' + ic(icon) + label + '</button>';
  }
  function detailActions(it) {
    var b = [], s = it.status, mine = S.st.me, id = it.id;
    if (it.kind === 'task') {
      if (s === 'todo') {
        if (!it.assignee) b.push(actBtn('claim', 'Claim', 'hand', '', id));
        b.push(actBtn('start', 'Start', 'play', '', id));
        b.push(actBtn('complete', 'Mark done', 'check', 'btn-dark', id));
      } else if (s === 'doing') {
        b.push(actBtn('unstart', 'Back to to-do', 'undo', '', id));
        b.push(actBtn('complete', 'Mark done', 'check', 'btn-dark', id));
      } else if (s === 'review') {
        if (it.completed_by !== mine || activeMembers().length < 2) {
          b.push(actBtn('reject', 'Send back', 'undo', '', id));
          b.push(actBtn('approve', 'Approve' + (it.points ? ' · pay ' + it.points : ''), 'shield', 'btn-dark', id));
        } else {
          b.push('<div class="waiting">' + ic('clock') + 'Waiting for someone else to approve…</div>');
          b.push(actBtn('reopen', 'Withdraw', 'undo', '', id));
        }
      } else if (s === 'done') {
        b.push(actBtn('reopen', 'Reopen', 'undo', '', id));
      }
    } else if (it.kind === 'want') {
      if (s === 'todo') b.push(actBtn('start', 'On it', 'play', '', id));
      if (s === 'doing') b.push(actBtn('unstart', 'Not yet', 'undo', '', id));
      if (s === 'todo' || s === 'doing') b.push(actBtn('complete', 'Got it!', 'star', 'btn-dark', id));
      if (s === 'done') b.push(actBtn('reopen', 'Want it again', 'undo', '', id));
    }
    return b.join('');
  }
  function metaRow(k, v) { return '<div class="d-meta-row"><span class="k">' + k + '</span><span class="v">' + v + '</span></div>'; }
  function personV(id, fallback) {
    var m = S.mm[id];
    return m ? avatar(m, 'xs') + esc(m.name) + (m.active ? '' : ' <span class="muted">(left)</span>') : '<span class="muted">' + fallback + '</span>';
  }
  function renderDetail() {
    if (!S.detail || !S.sheet || S.sheet.type !== 'detail') return;
    var data = S.detail.data;
    var it = itemById(S.detail.id) || (data && data.item);
    if (!it) return;
    var head = $('#sheet-head', layer), body = $('#sheet-body', layer);
    if (!head || !body) return;
    head.innerHTML = typeChip(it.kind) + '<span class="key">' + esc(it.key) + '</span>' + statusPill(it) + '<span class="sp"></span>' +
      '<button class="icon-btn" data-act="edit" data-id="' + it.id + '" aria-label="Edit">' + ic('edit') + '</button>' +
      '<button class="icon-btn" data-act="close-sheet" aria-label="Close">' + ic('close') + '</button>';

    var badges = '';
    if (it.points) badges += '<span class="pill bp">' + BROWNIE + it.points + ' brownie points</span>';
    if (it.priority !== 'normal') badges += '<span class="pill ' + (it.priority === 'high' ? 'pill-black' : '') + '">' + ic(it.priority === 'high' ? 'up' : 'down') + it.priority + ' priority</span>';
    if (it.recurrence !== 'none') badges += '<span class="pill">' + ic('repeat') + RECUR[it.recurrence] + (it.rotate ? ' · takes turns' : '') + ' · #' + it.occurrence + '</span>';
    if (data && data.series_done) badges += '<span class="pill pill-in">' + ic('trophy') + 'done ' + plural(data.series_done, 'time') + '</span>';
    if (it.requires_approval) badges += '<span class="pill">' + ic('shield') + 'needs approval</span>';

    var meta = '';
    if (it.kind === 'task') {
      meta += metaRow('Assignee', it.assignee ? personV(it.assignee) : '<span class="open-slot">open to anyone</span>');
      meta += metaRow('Due', it.due_date ? dueMeta(it) : '<span class="muted">No due date</span>');
    } else if (it.kind === 'event') {
      meta += metaRow('When', fmtWhen(it.event_at));
      if (it.location) meta += metaRow('Where', ic('pin', 'ic-sm') + esc(it.location));
      if (it.assignee) meta += metaRow('Host', personV(it.assignee));
    } else {
      meta += metaRow('For', it.assignee ? personV(it.assignee) : '<span class="muted">The whole family</span>');
      if (it.link) meta += metaRow('Link', '<a href="' + esc(it.link) + '" target="_blank" rel="noopener">' + esc(it.link.replace(/^https?:\/\//, '').slice(0, 60)) + '</a>');
    }
    meta += metaRow('Created', personV(it.created_by, 'Someone') + '<span class="muted small">' + ago(it.created) + '</span>');
    if (it.completed_by && (it.status === 'done' || it.status === 'review')) {
      meta += metaRow(it.kind === 'want' ? 'Got by' : 'Done by', personV(it.completed_by) + '<span class="muted small">' + ago(it.completed_at) + '</span>');
    }
    if (it.approved_by) meta += metaRow('Approved', personV(it.approved_by));

    var acked = it.acks.indexOf(S.st.me) >= 0;
    var ackLabel = it.kind === 'event' ? (acked ? 'You\'re in' : 'I\'m in') : it.kind === 'want' ? (acked ? 'You +1\'d' : 'Me too') : (acked ? 'Acknowledged' : 'Got it');
    var ackWord = it.kind === 'event' ? 'Coming' : it.kind === 'want' ? 'Wanted by' : 'Seen by';
    var ackers = it.acks.map(function (id) { return S.mm[id]; }).filter(Boolean);

    var comments = data ? data.comments : null;
    var cm = comments === null ? '<div class="small muted b" style="padding:8px 4px"><span class="spin"></span></div>' :
      comments.length ? comments.map(function (c) {
        var a = S.mm[c.author];
        return '<div class="comment">' + avatar(a, 'sm') + '<div class="bubble"><span class="who">' + esc(a ? a.name : 'Someone') + ' · ' + ago(c.created) + '</span>' + rich(c.text) + '</div></div>';
      }).join('') : '<div class="small muted b" style="padding:4px">No comments yet.</div>';

    body.innerHTML =
      '<div class="d-title">' + esc(it.title) + '</div>' +
      (it.notes ? '<div class="d-notes">' + rich(it.notes) + '</div>' : '') +
      (badges ? '<div class="d-badges">' + badges + '</div>' : '') +
      '<div class="d-meta">' + meta + '</div>' +
      '<div class="ack-row"><div class="sp"><div class="label" style="padding:0">' + ackWord + '</div>' +
      '<div class="row" style="margin-top:6px">' + (ackers.length ? '<div class="stack">' + ackers.map(function (m) { return avatar(m, 'xs'); }).join('') + '</div>' : '<span class="small muted b">Nobody yet</span>') + '</div></div>' +
      '<button class="btn btn-sm ' + (acked ? 'pressed' : 'btn-blue') + '" data-act="ack" data-id="' + it.id + '">' + ic(acked ? 'check' : 'thumb', 'ic-sm') + ackLabel + '</button></div>' +
      '<div class="d-actions">' + detailActions(it) + '</div>' +
      '<div class="section" style="margin-top:22px">' + sectionHead('Comments', it.comment_count || '') + '<div class="comments">' + cm + '</div></div>';
  }

  /* ---------- editor */
  function openEditor(id, kind) {
    var it = id ? itemById(id) : null;
    var now = new Date(), nextHour = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1);
    var ev = it && it.event_at ? new Date(it.event_at) : nextHour;
    S.ed = it ? {
      id: it.id, kind: it.kind, title: it.title, notes: it.notes, assignee: it.assignee, due_date: it.due_date || '',
      event_date: ymd(ev), event_time: fmtTime(ev), location: it.location, link: it.link, priority: it.priority,
      points: it.points, recurrence: it.recurrence, rotate: it.rotate, requires_approval: it.requires_approval
    } : {
      id: null, kind: kind || (S.view === 'board' && ['task', 'event', 'want'].indexOf(S.filter) >= 0 ? S.filter : 'task'),
      title: '', notes: '', assignee: null, due_date: '', event_date: ymd(ev), event_time: fmtTime(ev), location: '', link: '',
      priority: 'normal', points: 0, recurrence: 'none', rotate: false, requires_approval: false
    };
    var canDelete = it && (it.created_by === S.st.me || isOwner());
    openSheet({
      type: 'editor', title: it ? 'Edit ' + it.key : 'New card', focus: '[name=title]',
      body: '<div class="form" id="ed-form">' + editorHTML() + '</div>',
      foot: (canDelete ? '<button class="icon-btn" data-act="delete-item" data-id="' + it.id + '" aria-label="Delete card" style="color:var(--danger)">' + ic('trash') + '</button>' : '') +
        '<button class="btn btn-dark btn-lg sp" data-act="save-item">' + ic('check') + (it ? 'Save changes' : 'Add to board') + '</button>'
    });
  }
  function seg(key, options, cur, dark) {
    return '<div class="seg ' + (dark ? 'dark' : '') + '">' + options.map(function (o) {
      return '<button type="button" class="' + (String(cur) === String(o[0]) ? 'on' : '') + '" data-act="ed-set" data-k="' + key + '" data-v="' + o[0] + '">' + o[1] + '</button>';
    }).join('') + '</div>';
  }
  function personPick(key, cur, noneLabel) {
    var opts = [{ id: '', name: noneLabel, avatar: noneLabel === 'Anyone' ? '✋' : '👪', color: '#9aa8b6' }].concat(activeMembers());
    return '<div class="pick">' + opts.map(function (m) {
      var on = (cur || '') === m.id;
      return '<button type="button" class="pick-item ' + (on ? 'on' : '') + '" data-act="ed-set" data-k="' + key + '" data-v="' + m.id + '">' +
        '<span class="avatar sm" style="--c:' + m.color + '">' + esc(m.avatar) + '</span><span class="nm">' + esc(m.name) + '</span></button>';
    }).join('') + '</div>';
  }
  function editorHTML() {
    var e = S.ed, h = '';
    h += seg('kind', [['task', ic('check', 'ic-sm') + 'Task'], ['event', ic('calendar', 'ic-sm') + 'Event'], ['want', ic('star', 'ic-sm') + 'Want']], e.kind, true);
    var ph = { task: 'Take out the recycling', event: 'Grandma\'s birthday dinner', want: 'New football for the park' }[e.kind];
    h += '<label class="field"><span class="label">Title</span><input class="input" name="title" maxlength="140" value="' + esc(e.title) + '" placeholder="' + ph + '"></label>';
    h += '<label class="field"><span class="label">Notes</span><textarea class="textarea" name="notes" maxlength="2000" placeholder="Details, links, who to ask…">' + esc(e.notes) + '</textarea></label>';
    if (e.kind === 'task') {
      var t = todayStr(), tm = ymd(addDays(new Date(), 1)), sat = new Date();
      sat = addDays(sat, (6 - sat.getDay() + 7) % 7 || 7);
      h += '<div class="field"><span class="label">Who\'s on it</span>' + personPick('assignee', e.assignee, 'Anyone') + '</div>';
      h += '<div class="field"><span class="label">Due</span><input class="input" type="date" name="due_date" value="' + esc(e.due_date) + '">' +
        '<div class="quick">' + [['Today', t], ['Tomorrow', tm], ['Weekend', ymd(sat)], ['No date', '']].map(function (q) {
          return '<button type="button" class="chip ' + (e.due_date === q[1] ? 'on' : '') + '" data-act="ed-set" data-k="due_date" data-v="' + q[1] + '">' + q[0] + '</button>';
        }).join('') + '</div></div>';
      h += '<div class="field"><span class="label">Priority</span>' + seg('priority', [['low', 'Low'], ['normal', 'Normal'], ['high', 'High']], e.priority) + '</div>';
      h += '<div class="field"><span class="label">Bounty · brownie points</span><div class="stepper">' +
        '<button type="button" class="icon-btn" data-act="ed-points" data-d="-5" aria-label="Less">−</button>' +
        '<div class="val">' + BROWNIE + e.points + '</div>' +
        '<button type="button" class="icon-btn" data-act="ed-points" data-d="5" aria-label="More">+</button><span class="sp"></span></div>' +
        '<div class="quick">' + [0, 5, 10, 20, 50].map(function (n) {
          return '<button type="button" class="chip ' + (e.points === n ? 'on' : '') + '" data-act="ed-set" data-k="points" data-v="' + n + '">' + (n ? n : 'None') + '</button>';
        }).join('') + '</div></div>';
      h += '<div class="field"><span class="label">Repeat</span><div class="chips" style="padding-top:2px">' + Object.keys(RECUR).map(function (k) {
        return '<button type="button" class="chip ' + (e.recurrence === k ? 'on' : '') + '" data-act="ed-set" data-k="recurrence" data-v="' + k + '">' + (k === 'none' ? '' : ic('repeat', 'ic-sm')) + RECUR[k] + '</button>';
      }).join('') + '</div></div>';
      if (e.recurrence !== 'none') {
        h += switchRow('rotate', e.rotate, 'Take turns', 'Each repeat goes to the next family member');
      }
      h += switchRow('requires_approval', e.requires_approval, 'Needs approval', 'Someone else confirms it\'s done before brownie points are paid');
    } else if (e.kind === 'event') {
      h += '<div class="form-row"><label class="field"><span class="label">Date</span><input class="input" type="date" name="event_date" value="' + esc(e.event_date) + '"></label>' +
        '<label class="field"><span class="label">Time</span><input class="input" type="time" name="event_time" value="' + esc(e.event_time) + '"></label></div>';
      h += '<label class="field"><span class="label">Where</span><input class="input" name="location" maxlength="120" value="' + esc(e.location) + '" placeholder="Home, school, the park…"></label>';
      h += '<div class="field"><span class="label">Host</span>' + personPick('assignee', e.assignee, 'Family') + '</div>';
      h += '<div class="small muted b" style="padding-left:4px">Everyone can tap “I\'m in” to acknowledge.</div>';
    } else {
      h += '<div class="field"><span class="label">Who wants it</span>' + personPick('assignee', e.assignee, 'Family') + '</div>';
      h += '<label class="field"><span class="label">Link</span><input class="input" name="link" maxlength="400" inputmode="url" value="' + esc(e.link) + '" placeholder="https://… (optional)"></label>';
      h += '<div class="field"><span class="label">How much</span>' + seg('priority', [['low', 'Nice to have'], ['normal', 'Want'], ['high', 'Really want']], e.priority) + '</div>';
    }
    return h;
  }
  function switchRow(key, on, title, sub) {
    return '<div class="switch-row"><div class="sp"><div class="t">' + title + '</div><div class="s">' + sub + '</div></div>' +
      '<button type="button" class="toggle ' + (on ? 'on' : '') + '" data-act="ed-flip" data-k="' + key + '" aria-label="' + title + '"></button></div>';
  }
  function collectEditor() {
    var f = $('#ed-form', layer);
    if (!f || !S.ed) return;
    ['title', 'notes', 'due_date', 'event_date', 'event_time', 'location', 'link'].forEach(function (k) {
      var el = $('[name=' + k + ']', f);
      if (el) S.ed[k] = el.value;
    });
  }
  function rerenderEditor() {
    var f = $('#ed-form', layer), body = $('#sheet-body', layer);
    if (!f) return;
    var top = body ? body.scrollTop : 0;
    f.innerHTML = editorHTML();
    if (body) body.scrollTop = top;
  }
  function saveEditor(btn) {
    collectEditor();
    var e = S.ed;
    if (!e.title.trim()) { toast('Give the card a title.', true); var t = $('[name=title]', layer); if (t) t.focus(); return; }
    var p = { id: e.id, kind: e.kind, title: e.title, notes: e.notes, assignee: e.assignee || null, priority: e.priority };
    if (e.kind === 'task') {
      p.due_date = e.due_date || null; p.points = e.points; p.recurrence = e.recurrence;
      p.rotate = e.rotate; p.requires_approval = e.requires_approval;
    } else if (e.kind === 'event') {
      if (!e.event_date) { toast('Pick a date for the event.', true); return; }
      var parts = e.event_date.split('-'), tp = (e.event_time || '12:00').split(':');
      p.event_at = new Date(+parts[0], +parts[1] - 1, +parts[2], +tp[0], +tp[1]).toISOString();
      p.location = e.location;
    } else {
      p.link = e.link;
    }
    var isNew = !e.id;
    run('save_item', p, btn).then(function (d) {
      if (!d) return;
      closeSheet();
      var it = itemById(d.saved);
      toast(isNew ? (it ? it.key + ' added to the board' : 'Card added') : 'Saved');
    });
  }

  /* ---------- other sheets */
  function openInvite() {
    var fam = S.st.family, qr = qrSVG(inviteLink());
    openSheet({
      type: 'invite', title: 'Join ' + fam.name,
      body: '<div class="col" style="align-items:center;gap:18px;padding-bottom:6px">' +
        (qr ? '<div class="qr-frame big">' + qr + '</div>' : '<div class="empty">QR codes need an internet connection. Use the code below.</div>') +
        '<div class="code-tiles">' + fam.code.split('').map(function (c) { return '<span>' + c + '</span>'; }).join('') + '</div>' +
        '<p class="center small muted b" style="max-width:320px">Open the phone camera and point it at the code, or type the code on the “Join a family” screen.</p></div>',
      foot: '<button class="btn sp" data-act="copy-link">' + ic('copy') + 'Copy link</button>' +
        (navigator.share ? '<button class="btn btn-dark sp" data-act="share-link">' + ic('share') + 'Share</button>' : '')
    });
  }
  function openProfile() {
    var m = me();
    openSheet({
      type: 'profile', title: 'My profile', focus: '[name=display_name]',
      body: '<div class="form" id="prof-form">' + profilePickerHTML({ name: m.name, avatar: m.avatar, color: m.color }) + '</div>',
      foot: '<button class="btn btn-dark btn-lg sp" data-act="save-profile">' + ic('check') + 'Save</button>'
    });
  }
  function openFamilySettings() {
    var fam = S.st.family;
    S.pick.goal = fam.weekly_goal;
    openSheet({
      type: 'family', title: 'Family settings',
      body: '<div class="form" id="fam-form"><label class="field"><span class="label">Family name</span><input class="input" name="name" maxlength="40" value="' + esc(fam.name) + '"></label>' +
        '<div class="field"><span class="label">Weekly brownie goal (whole family)</span><div class="stepper">' +
        '<button type="button" class="icon-btn" data-act="goal" data-d="-10">−</button><div class="val" id="goal-val">' + BROWNIE + fam.weekly_goal + '</div>' +
        '<button type="button" class="icon-btn" data-act="goal" data-d="10">+</button></div></div></div>',
      foot: '<button class="btn btn-dark btn-lg sp" data-act="save-family">' + ic('check') + 'Save</button>'
    });
  }
  function openScanner() {
    if (!('BarcodeDetector' in window) || !navigator.mediaDevices) { toast('Use your phone\'s camera app to scan the QR code.'); return; }
    var stopped = false;
    function stop() {
      stopped = true;
      if (S.stream) { S.stream.getTracks().forEach(function (t) { t.stop(); }); S.stream = null; }
    }
    openSheet({
      type: 'scan', title: 'Scan invite QR',
      body: '<div class="scanner"><video playsinline muted autoplay></video><div class="frame"></div></div><p class="center small muted b" style="margin-top:14px">Point at the QR code on the other phone.</p>',
      onClose: stop
    });
    var video = $('video', layer);
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(function (stream) {
      if (stopped) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
      S.stream = stream; video.srcObject = stream;
      var det = new window.BarcodeDetector({ formats: ['qr_code'] });
      (function loop() {
        if (stopped) return;
        det.detect(video).then(function (codes) {
          var raw = codes.length ? String(codes[0].rawValue || '') : '';
          var m = /join=([A-Z0-9]{6})/i.exec(raw) || /^\s*([A-Z0-9]{6})\s*$/i.exec(raw);
          if (m) {
            closeSheet();
            var code = m[1].toUpperCase(), input = $('[name=code]');
            if (input) input.value = code;
            S.pendingJoin = code; previewJoin(code);
            toast('Code found: ' + code);
          } else setTimeout(loop, 300);
        }, function () { setTimeout(loop, 600); });
      })();
    }, function () { closeSheet(); toast('Camera not available. Type the code instead.', true); });
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve) {
      var t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) { /* ignore */ }
      t.remove(); resolve();
    });
  }
  function setTheme(t) {
    S.theme = t; store('ftp.theme', t);
    app.setAttribute('data-theme', t);
    document.documentElement.setAttribute('data-ftp-theme', t);
    document.documentElement.style.background = t === 'night' ? '#1e2126' : '#f1ede4';
    var meta = document.querySelector('meta[name=theme-color]');
    if (meta) meta.setAttribute('content', t === 'night' ? '#1e2126' : '#f1ede4');
  }

  /* ------------------------------------------------------------ actions */
  function itemAct(action, extra) {
    return function (el) {
      var id = el.getAttribute('data-id');
      var rect = el.getBoundingClientRect();
      var p = Object.assign({ id: id, _detail: !!(S.sheet && S.sheet.type === 'detail') }, extra || {});
      return run(action, p, el).then(function (d) {
        if (!d) return;
        var fx = d.fx;
        if (fx && (fx.kind === 'done' || fx.kind === 'approved')) {
          burst(rect, fx.points ? BROWNIE + '+' + fx.points + ' brownie points' : (fx.kind === 'approved' ? 'Approved ✓' : 'Done! ✓'));
        } else if (fx && fx.kind === 'review') toast('Sent for approval ✋');
        else if (fx && fx.kind === 'want') burst(rect, 'Got it! 🎁');
        if (action === 'claim') toast('It\'s yours! Go get those brownie points.');
      });
    };
  }
  var ACT = {
    'nav': function (el) { closeSheet(); go(el.getAttribute('data-view')); },
    'new': function (el) { openEditor(null, el.getAttribute('data-kind')); },
    'open': function (el) { openDetail(el.getAttribute('data-id')); },
    'edit': function (el) { openEditor(el.getAttribute('data-id')); },
    'filter': function (el) { S.filter = el.getAttribute('data-f'); renderView(false); },
    'board-filter': function (el) { S.filter = el.getAttribute('data-f'); go('board'); },
    'col': function (el) { S.col = el.getAttribute('data-col'); renderView(false); },
    'lb': function (el) { S.lb = el.getAttribute('data-lb'); renderView(false); },
    'close-sheet': function () { closeSheet(); },
    'confirm-ok': function () { var o = S.sheet; if (o && o.resolve) o.resolve(); closeSheet(); },
    'theme': function () { setTheme(S.theme === 'night' ? 'light' : 'night'); if (S.phase === 'app') renderView(false); },
    'complete': itemAct('complete'),
    'approve': itemAct('approve'),
    'reopen': itemAct('reopen'),
    'claim': itemAct('claim'),
    'ack': itemAct('ack'),
    'start': itemAct('move', { to: 'doing' }),
    'unstart': itemAct('move', { to: 'todo' }),
    'reject': function (el) {
      var id = el.getAttribute('data-id'), reopenDetail = S.sheet && S.sheet.type === 'detail';
      promptBox('Send back for another try', 'What still needs doing? (optional)', 'Send back').then(function (reason) {
        if (reason === null) { if (reopenDetail) openDetail(id); return; }
        run('reject', { id: id, reason: reason }).then(function (d) { if (d) { toast('Sent back ↩'); if (reopenDetail) openDetail(id); } });
      });
    },
    'delete-item': function (el) {
      var id = el.getAttribute('data-id'), it = itemById(id);
      confirmBox('Delete ' + (it ? it.key : 'card') + '?', 'This removes the card and its comments for everyone. Brownie points already earned are kept.', 'Delete', true).then(function (ok) {
        if (ok) run('delete_item', { id: id }).then(function (d) { if (d) toast('Card deleted'); });
      });
    },
    'save-item': function (el) { saveEditor(el); },
    'ed-set': function (el) {
      collectEditor();
      var k = el.getAttribute('data-k'), v = el.getAttribute('data-v');
      S.ed[k] = k === 'points' ? parseInt(v, 10) || 0 : (k === 'assignee' ? (v || null) : v);
      rerenderEditor();
    },
    'ed-flip': function (el) { collectEditor(); var k = el.getAttribute('data-k'); S.ed[k] = !S.ed[k]; rerenderEditor(); },
    'ed-points': function (el) { collectEditor(); S.ed.points = Math.max(0, Math.min(500, S.ed.points + parseInt(el.getAttribute('data-d'), 10))); rerenderEditor(); },
    'pick': function (el) {
      var group = el.parentNode.getAttribute('data-group');
      S.pick[group] = el.getAttribute('data-val');
      $$('button', el.parentNode).forEach(function (b) { b.classList.toggle('on', b === el); });
    },
    'toggle': function (el) { el.classList.toggle('on'); },
    'goal': function (el) {
      S.pick.goal = Math.max(10, Math.min(5000, (S.pick.goal || 100) + parseInt(el.getAttribute('data-d'), 10)));
      var v = $('#goal-val', layer); if (v) v.innerHTML = BROWNIE + S.pick.goal;
    },
    'auth-mode': function (el) { S.authMode = el.getAttribute('data-mode'); renderAuth(); },
    'land-auth': function (el) { S.authMode = el.getAttribute('data-mode') || 'signup'; setPhase('auth'); },
    'land-back': function () { setPhase('landing'); },
    'forgot': function () {
      var email = ($('[name=email]') || {}).value || '';
      if (!email.trim()) { var err = $('[data-err]'); if (err) err.textContent = 'Type your email above first, then tap “Forgot password?”.'; return; }
      api('reset_password', { email: email }).then(function () { toast('Password reset email sent. Check your inbox.'); }, function (e) { toast(e.message, true); });
    },
    'logout': function () {
      api('logout').then(function () { S.email = null; goAuth(); }, function () { goAuth(); });
    },
    'scan': function () { openScanner(); },
    'invite': function () { openInvite(); },
    'copy-link': function () { copyText(inviteLink()).then(function () { toast('Invite link copied'); }); },
    'share-link': function () {
      var fam = S.st.family;
      navigator.share({ title: 'Join ' + fam.name + ' on Fun To Plan', text: 'Join our family board! Code: ' + fam.code, url: inviteLink() }).catch(function () { });
    },
    'profile': function () { openProfile(); },
    'save-profile': function (el) {
      var p = readProfile($('#prof-form', layer));
      run('update_profile', p, el).then(function (d) { if (d) { closeSheet(); toast('Profile updated'); } });
    },
    'family-settings': function () { openFamilySettings(); },
    'save-family': function (el) {
      var name = ($('[name=name]', layer) || {}).value || '';
      run('update_family', { name: name, weekly_goal: S.pick.goal }, el).then(function (d) { if (d) { closeSheet(); toast('Family settings saved'); } });
    },
    'regen-code': function () {
      confirmBox('Make a new join code?', 'The current QR code and invite links will stop working. People already in the family stay.', 'New code').then(function (ok) {
        if (ok) run('regen_code').then(function (d) { if (d) toast('New code: ' + S.st.family.code); });
      });
    },
    'remove-member': function (el) {
      var m = S.mm[el.getAttribute('data-id')];
      if (!m) return;
      confirmBox('Remove ' + m.name + '?', m.name + ' will lose access to the board. Their open tasks become open to anyone.', 'Remove', true).then(function (ok) {
        if (ok) run('remove_member', { member_id: m.id }).then(function (d) { if (d) toast(m.name + ' was removed'); });
      });
    },
    'leave': function () {
      confirmBox('Leave ' + S.st.family.name + '?', 'You can rejoin later with the code and keep your brownie points.', 'Leave', true).then(function (ok) {
        if (ok) run('leave_family').then(function (d) { if (d) toast('You left the family board'); });
      });
    }
  };

  var FORMS = {
    auth: function (f) {
      var err = $('[data-err]', f), btn = $('button[type=submit]', f);
      var email = f.email.value.trim(), password = f.password.value;
      if (!email || !password) { err.textContent = 'Enter your email and password.'; return; }
      if (S.authMode === 'signup' && window.LegalKit && !LegalKit.consentChecked(f)) return;
      err.textContent = '';
      var label = btn.innerHTML; btn.disabled = true; btn.innerHTML = '<span class="spin"></span>';
      api(S.authMode === 'signup' ? 'signup' : 'login', { email: email, password: password }).then(function (d) {
        S.email = d.email || email;
        if (d.state) applyData(d); else setPhase('onboard');
      }, function (e) {
        if (!btn.isConnected) return;
        btn.disabled = false; btn.innerHTML = label;
        err.textContent = e.message;
      });
    },
    create: function (f) {
      var err = $('[data-err]', f);
      var name = f.family_name.value.trim();
      if (!name) { err.textContent = 'Give your family board a name.'; f.family_name.focus(); return; }
      var p = readProfile($('#ob-profile'));
      p.family_name = name;
      p.seed = $('[data-key=seed]', f).classList.contains('on');
      run('create_family', p, $('button[type=submit]', f)).then(function (d) { if (d && d.state) { S.view = 'home'; renderShell(); renderView(true); toast('Your family board is ready! Invite the others from the Family tab.'); } });
    },
    join: function (f) {
      var err = $('[data-err]', f);
      var code = f.code.value.trim().toUpperCase();
      if (code.length !== 6) { err.textContent = 'Codes have 6 letters and numbers.'; return; }
      var p = readProfile($('#ob-profile'));
      p.code = code;
      run('join_family', p, $('button[type=submit]', f)).then(function (d) {
        if (d && d.state) { S.pendingJoin = null; S.preview = null; S.view = 'home'; renderShell(); renderView(true); toast('Welcome to ' + d.state.family.name + '! 👋'); }
      });
    },
    chat: function (f) {
      var t = f.text, text = t.value.trim();
      if (!text) return;
      t.value = ''; t.style.height = '';
      run('send_message', { text: text }).then(function (d) {
        if (!d) { t.value = text; return; }
        var main = $('#ftp-main'); main.scrollTop = main.scrollHeight;
      });
    },
    comment: function (f) {
      var t = f.text, text = t.value.trim();
      if (!text || !S.detail) return;
      t.value = '';
      run('comment', { id: S.detail.id, text: text, _detail: true }).then(function (d) {
        if (!d) { t.value = text; return; }
        var body = $('#sheet-body', layer); if (body) body.scrollTop = body.scrollHeight;
      });
    }
  };

  function onClick(e) {
    var t = e.target.closest('[data-act]');
    if (!t || !app.contains(t)) return;
    var fn = ACT[t.getAttribute('data-act')];
    if (!fn) return;
    e.preventDefault();
    fn(t, e);
  }
  function onSubmit(e) {
    var f = e.target, fn = FORMS[f.getAttribute('data-form')];
    if (!fn) return;
    e.preventDefault();
    fn(f);
  }
  function onKey(e) {
    if (e.key === 'Escape' && S.sheet) { closeSheet(); return; }
    var t = e.target;
    if ((e.key === 'Enter' || e.key === ' ') && t.getAttribute && t.getAttribute('role') === 'button' && t.hasAttribute('data-act')) {
      e.preventDefault(); onClick({ target: t, preventDefault: function () { } });
      return;
    }
    if (e.key === 'Enter' && !e.shiftKey && t.name === 'text' && t.tagName === 'TEXTAREA') {
      var f = t.closest('form');
      if (f && window.matchMedia('(hover: hover)').matches) { e.preventDefault(); onSubmit({ target: f, preventDefault: function () { } }); }
    }
  }
  function onInput(e) {
    var t = e.target;
    if (t.tagName === 'TEXTAREA' && t.closest('.composer')) {
      t.style.height = 'auto'; t.style.height = Math.min(140, t.scrollHeight) + 'px';
    }
    if (t.name === 'code' && S.phase === 'onboard') {
      t.value = t.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
      if (t.value.length === 6) previewJoin(t.value);
      else { S.preview = null; var box = $('#join-preview'); if (box) box.innerHTML = ''; }
    }
  }

  /* ------------------------------------------------------------ mount */
  function readJoinHash() {
    var m = /join=([A-Z0-9]{6})/i.exec(window.location.hash || '');
    if (m) {
      S.pendingJoin = m[1].toUpperCase();
      try { window.history.replaceState(null, '', window.location.pathname + window.location.search); } catch (e) { /* ignore */ }
    }
  }
  function mount(node, bridgeFn) {
    if (app) return;
    bridge = bridgeFn;
    var host = (node && node.querySelector && node.querySelector('.ftp-mount')) || node || document.body;
    app = document.createElement('div');
    app.className = 'ftp-app';
    app.innerHTML = '<div class="stage" id="ftp-stage" style="flex:1;display:flex;min-width:0;min-height:0"></div><div class="layer" id="ftp-layer"></div><div class="toasts" id="ftp-toasts"></div>';
    host.appendChild(app);
    stage = app.querySelector('#ftp-stage');
    layer = app.querySelector('#ftp-layer');
    toasts = app.querySelector('#ftp-toasts');
    app.addEventListener('click', onClick);
    app.addEventListener('submit', onSubmit);
    app.addEventListener('keydown', onKey);
    app.addEventListener('input', onInput);
    document.addEventListener('visibilitychange', function () { if (!document.hidden) tick(); });
    window.addEventListener('hashchange', function () {
      readJoinHash();
      if (S.pendingJoin && S.phase === 'onboard') renderOnboard();
      else if (S.pendingJoin && S.phase === 'app') afterEnterApp();
    });
    setTheme(S.theme);
    readJoinHash();
    render();
    api('bootstrap').then(function (d) {
      S.email = d.email;
      if (d.state) applyData(d); else setPhase('onboard');
    }, function (e) {
      setPhase('landing');
      if (e.code !== 'auth') toast(e.message, true);
    });
  }

  window.FunToPlan = { mount: mount, version: '1.0.0' };
})();
