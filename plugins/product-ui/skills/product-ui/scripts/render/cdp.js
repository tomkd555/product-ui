// Headless-Chrome driver over CDP for review-design-lead. Requires Node 22+ (global WebSocket).
//
//   node cdp.js <url> <width> [js-expression]
//
// Environment:
//   SHOT=<png>    write a full-page screenshot
//   DUMP=<json>   write a DOM dump: headings, landmarks, controls (with href / type / disabled /
//                 inline), the custom properties declared on :root — including those nested in
//                 @layer, @media and Tailwind's @theme — with their computed values (a colour-valued
//                 property, color-mix included, resolved through a probe element), horizontal
//                 overflow, and the computed colour / background / opacity / font-size /
//                 font-weight / line-height / bounding rect of every element that carries text (a
//                 translucent background comes with `backgroundBase`, the opaque colour under it),
//                 and the composition of the first <main> (else <body>): `scope` (its rect),
//                 `boxes` (elements drawn as an enclosure: a border, a fill that differs from the
//                 background behind it, or a shadow; with nesting depth and parent box), and
//                 `gaps` (per parent, the spacing between consecutive children, 0..200px rounded
//                 to 4px)
//   CLASS=<name>  add this class to <html> after load and before capture (`dark` renders a
//                 theme.css dark block)
//   CHROME=<exe>  Chrome binary (default: the first of the install paths below that exists)
//   CDP_PORT      debugging port (default 9333)
//
// Stdout: the expression's value (default: document.title) as JSON, then, when the page
// logged any, a line `CONSOLE_ERRORS [...]` holding the errors and warnings it logged and any
// uncaught exception. Exit code 0 on success, 1 on a usage error, 2 when Chrome could not be
// started or reached, the navigation failed, an http(s) URL got no document response or an
// HTTP status of 400 or above, the expression threw, or 60 seconds passed.
//
// Chrome keeps oklch() as the computed value of a colour declared in oklch(), so the dump
// carries colour strings in whatever notation the stylesheet used; check_render.py parses
// them, measures contrast and matches them against tokens.json. An element whose background
// no ancestor paints is reported as white with `backgroundFallback: true`, so the checks can
// leave it out: that white is a colour nobody chose.
//
// The review lead renders through headless Chrome, so no browser extension is involved,
// and hands the auditors files.
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const [,, url, width, expr] = process.argv;
if (!url || !width) { console.error('usage: node cdp.js <url> <width> [js-expression]'); process.exit(1); }
const CHROME_PATHS = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
];
const CH = process.env.CHROME || CHROME_PATHS.find(p => fs.existsSync(p));
if (!CH) { console.error('no Chrome found in ' + CHROME_PATHS.join(', ') + '; set CHROME=<path to the binary>'); process.exit(2); }
const port = Number(process.env.CDP_PORT || 9333);
const HEIGHT = 1200;            // viewport height for both the window and the emulated device
const STARTUP_TRIES = 40;       // x 300 ms: how long Chrome gets to answer /json
const LOAD_TRIES = 40;          // x 250 ms: how long the page gets to reach readyState complete
const SETTLE_MS = 700;          // fonts and late layout after readyState complete
const WALL_CLOCK_MS = 60000;    // a dead socket ends the run with code 2
const MAX_ELS = 1500, MAX_CONTROLS = 300, TEXT_CAP = 80, LABEL_CAP = 40, MAX_BOXES = 400, MAX_GAP_PARENTS = 300;
const profile = (process.env.TEMP || process.env.TMPDIR || '/tmp') + '/cdp-profile-' + port + '-' + process.pid;

// Chrome refuses to start as root on Linux unless its sandbox is off; everywhere else it keeps the sandbox.
const noSandbox = process.platform === 'linux' && process.getuid && process.getuid() === 0 ? ['--no-sandbox'] : [];
const chrome = spawn(CH, ['--headless=new', '--disable-gpu', ...noSandbox, `--remote-debugging-port=${port}`,
  `--window-size=${width},${HEIGHT}`, '--user-data-dir=' + profile, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const quit = code => { try { chrome.kill(); } catch (e) {} setTimeout(() => { try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) {} process.exit(code); }, 200); };
const fail = msg => { console.error(msg); quit(2); };
chrome.on('error', e => fail('cannot start chrome at ' + CH + ': ' + e.message));
process.on('unhandledRejection', e => fail('REJ ' + (e && e.stack || e)));
setTimeout(() => fail('timed out after ' + WALL_CLOCK_MS + ' ms'), WALL_CLOCK_MS).unref();

// Runs inside the page. Returns plain data only.
const DUMP_EXPR = `(() => {
  const MAX_ELS = ${MAX_ELS}, MAX_CONTROLS = ${MAX_CONTROLS}, TEXT_CAP = ${TEXT_CAP}, LABEL_CAP = ${LABEL_CAP}, MAX_BOXES = ${MAX_BOXES}, MAX_GAP_PARENTS = ${MAX_GAP_PARENTS};
  const v = window, d = document;
  // [colour, fallback]: fallback is true when no ancestor paints a background.
  const painted = c => c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent';
  const alphaOfBg = c => { const m = /\/\s*([\d.]+)(%?)\s*\)\s*$/.exec(c); if (m) return m[2] ? m[1] / 100 : +m[1]; const r = /^rgba\([^,]+,[^,]+,[^,]+,\s*([\d.]+)\)$/.exec(c); return r ? +r[1] : 1; };
  // [colour, fallback, base]: the nearest painted background; when it is translucent, base is the nearest opaque
  // ancestor colour to composite it over (white when none paints). fallback is true when no ancestor paints at all.
  const bg = el => { let first = null; for (let e = el; e; e = e.parentElement) { const c = v.getComputedStyle(e).backgroundColor; if (!painted(c)) continue; if (first === null) { first = c; if (alphaOfBg(c) >= 1) return [c, false, undefined]; continue; } if (alphaOfBg(c) >= 1) return [first, false, c]; } return first === null ? ['rgb(255, 255, 255)', true, undefined] : [first, false, 'rgb(255, 255, 255)']; };
  const ownText = el => Array.from(el.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\\s+/g, ' ').trim();
  const all = d.body.querySelectorAll('*');
  const text = [];
  for (const el of all) {
    if (text.length >= MAX_ELS) break;
    const own = ownText(el); if (!own) continue;
    const s = v.getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect(); if (!r.width && !r.height) continue;
    const [background, backgroundFallback, backgroundBase] = bg(el);
    text.push({ tag: el.tagName.toLowerCase(), id: el.id || undefined, cls: (el.className && typeof el.className === 'string') ? el.className.slice(0, 60) : undefined,
      text: own.slice(0, TEXT_CAP), color: s.color, background, backgroundFallback: backgroundFallback || undefined, backgroundBase,
      opacity: s.opacity !== '1' ? s.opacity : undefined, fontSize: s.fontSize, fontWeight: s.fontWeight,
      lineHeight: s.lineHeight, rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
      clipped: el.scrollWidth > el.clientWidth + 1 && s.overflowX !== 'visible',
      disabled: el.closest('[disabled],[aria-disabled="true"]') ? true : undefined });
  }
  const controlEls = d.querySelectorAll('a,button,input,select,textarea,[role=button],[tabindex]');
  // Custom properties declared for :root / html / .dark, at any nesting depth (@layer, @media,
  // @supports, Tailwind's @theme), with the value in force right now.
  const tokens = {};
  const rootStyle = v.getComputedStyle(d.documentElement);
  const ROOT_SEL = /(^|,)\\s*(:root|html|\\.dark)\\s*(?=$|,)/;
  const collect = rules => { for (const rule of Array.from(rules || [])) {
    if (rule.cssRules && rule.cssRules.length) { collect(rule.cssRules); continue; }
    if (!rule.style) continue;
    if (rule.selectorText && !ROOT_SEL.test(rule.selectorText)) continue;
    for (const prop of Array.from(rule.style)) if (prop.startsWith('--')) tokens[prop] = rootStyle.getPropertyValue(prop).trim();
  } };
  for (const sheet of Array.from(d.styleSheets)) { try { collect(sheet.cssRules); } catch (e) {} }
  // A custom property that holds a colour (a literal or a color-mix of other tokens) is resolved through a probe
  // element, so the checks can match an element's computed colour against the value the variable gives.
  const probe = d.createElement('span'); probe.style.position = 'absolute'; probe.style.left = '-9999px'; d.body.appendChild(probe);
  const COLOURISH = /^(#|rgb|hsl|oklch|oklab|lab|lch|color\(|color-mix\()/;
  for (const prop of Object.keys(tokens)) { if (!COLOURISH.test(tokens[prop])) continue; probe.style.color = ''; probe.style.color = 'var(' + prop + ')'; const c = v.getComputedStyle(probe).color; if (painted(c)) tokens[prop] = c; }
  probe.remove();
  // Composition of the first <main> (else <body>): enclosures and the spacing between siblings.
  const root = d.querySelector('main') || d.body;
  const rr = r => ({ x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
  const alphaOf = c => { if (!c || c === 'transparent') return 0; const m = /\\/\\s*([\\d.]+)(%?)\\s*\\)\\s*$/.exec(c); if (m) return m[2] ? m[1] / 100 : +m[1];
    const f = /^rgba\\(([^)]*)\\)$/.exec(c); if (f) { const p = f[1].split(','); if (p.length === 4) return +p[3]; } return 1; };
  const NOT_BOX = new Set(['a','button','input','select','textarea','img','svg','canvas','video','td','th','tr','thead','tbody','table','li','summary','label']);
  const BOX_DISPLAY = new Set(['block','flex','grid','flow-root']);
  const SIDES = ['Top','Right','Bottom','Left'];
  const sel = el => { const c = (el.className && typeof el.className === 'string') ? el.className.trim().split(/\\s+/)[0] : ''; return el.tagName.toLowerCase() + (el.id ? '#' + el.id : c ? '.' + c : ''); };
  const boxes = [], boxAt = new Map(), gaps = [];
  let boxesTotal = 0, gapsTotal = 0;
  for (const el of [root, ...root.querySelectorAll('*')]) {
    if (el.namespaceURI !== 'http://www.w3.org/1999/xhtml') continue;   // the insides of an svg are not layout
    if (el !== root && !NOT_BOX.has(el.tagName.toLowerCase())) {
      const s = v.getComputedStyle(el);
      if (BOX_DISPLAY.has(s.display) && s.visibility !== 'hidden') {
        const r = el.getBoundingClientRect();
        if (r.width >= 40 && r.height >= 40 &&
            (SIDES.some(k => parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' && alphaOf(s['border' + k + 'Color']) > 0) ||
             (alphaOf(s.backgroundColor) > 0 && s.backgroundColor !== bg(el.parentElement)[0]) || s.boxShadow !== 'none')) {
          boxesTotal++;
          if (boxes.length < MAX_BOXES) {
            let a = el.parentElement; while (a && !boxAt.has(a)) a = a.parentElement;
            const up = a ? boxAt.get(a) : null;
            boxAt.set(el, { i: boxes.length, depth: up ? up.depth + 1 : 0 });
            boxes.push({ tag: el.tagName.toLowerCase(), id: el.id || undefined, cls: (el.className && typeof el.className === 'string') ? el.className.slice(0, 60) : undefined,
              rect: rr(r), depth: up ? up.depth + 1 : 0, parentBox: up ? up.i : null, children: el.childElementCount,
              hasDigit: /[0-9\\uFF10-\\uFF19]/.test(el.textContent) });
          }
        }
      }
    }
    if (el.childElementCount >= 2) {
      const kids = Array.from(el.children).map(k => k.getBoundingClientRect()).filter(r => r.width > 0 && r.height > 0).sort((p, q) => p.y - q.y || p.x - q.x);
      const values = [];
      for (let i = 1; i < kids.length; i++) {
        const p = kids[i - 1], q = kids[i];
        const g = Math.round((q.y >= p.y + p.height ? q.y - (p.y + p.height) : q.x - (p.x + p.width)) / 4) * 4;
        if (g >= 0 && g <= 200) values.push(g || 0);
      }
      if (values.length) { gapsTotal++; if (gaps.length < MAX_GAP_PARENTS) gaps.push({ parent: sel(el), values }); }
    }
  }
  return { title: d.title, viewport: { width: v.innerWidth, height: v.innerHeight }, htmlClass: d.documentElement.className || '',
    tokens,
    horizontalOverflow: d.documentElement.scrollWidth > d.documentElement.clientWidth,
    scrollWidth: d.documentElement.scrollWidth, pageHeight: d.documentElement.scrollHeight,
    headings: Array.from(d.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => ({ level: +h.tagName[1], text: h.textContent.trim().slice(0, TEXT_CAP) })),
    landmarks: ['header','nav','main','aside','footer','form','[role]'].map(sel => ({ sel, count: d.querySelectorAll(sel).length })),
    controlsTotal: controlEls.length,
    controls: Array.from(controlEls).slice(0, MAX_CONTROLS).map(el => { const r = el.getBoundingClientRect(); const s = v.getComputedStyle(el); return { tag: el.tagName.toLowerCase(), text: (el.textContent || el.value || el.getAttribute('aria-label') || '').trim().slice(0, LABEL_CAP), w: Math.round(r.width), h: Math.round(r.height),
      labelled: el.tagName !== 'INPUT' || !!(el.labels && el.labels.length) || !!el.getAttribute('aria-label') || !!el.getAttribute('aria-labelledby') || !!el.getAttribute('title'),
      href: el.tagName === 'A' ? el.getAttribute('href') : undefined, type: el.getAttribute('type') || undefined,
      disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true' || undefined,
      inline: s.display === 'inline' || undefined }; }),
    elementsTotal: all.length, textTruncated: text.length >= MAX_ELS,
    scope: { tag: root.tagName.toLowerCase(), rect: rr(root.getBoundingClientRect()) },
    boxes, boxesTotal, gaps, gapsTotal,
    text };
})()`;

(async () => {
  let page;
  for (let i = 0; i < STARTUP_TRIES && !page; i++) {
    await sleep(300);
    try {
      const targets = await new Promise((res, rej) => http.get(`http://127.0.0.1:${port}/json`, r => { let b = ''; r.on('data', d => b += d); r.on('end', () => { try { res(JSON.parse(b)); } catch (e) { rej(e); } }); }).on('error', rej));
      page = targets.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
    } catch (e) {}
  }
  if (!page) fail('chrome did not answer with a page target on port ' + port);
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const pending = {};
  // Resolves with the whole CDP reply, so a command failure ({error}) is visible to the caller.
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pending[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
  const logs = [];
  let mainStatus = null;   // HTTP status of the document itself; a 404 page renders like any other
  const arg = a => ('value' in a ? String(a.value) : (a.description || a.type));
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; }
    if (m.method === 'Network.responseReceived' && m.params.type === 'Document' && mainStatus === null) mainStatus = m.params.response.status;
    if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) logs.push(m.params.type + ': ' + m.params.args.map(arg).join(' '));
    if (m.method === 'Runtime.exceptionThrown') logs.push('exception: ' + m.params.exceptionDetails.text + ' ' + ((m.params.exceptionDetails.exception || {}).description || ''));
  };
  ws.onclose = () => { for (const k in pending) pending[k]({ error: { message: 'socket closed' } }); };
  ws.onerror = () => fail('websocket error');
  await new Promise(r => ws.onopen = r);
  const call = async (method, params) => { const m = await send(method, params); if (m.error) fail(method + ' failed: ' + m.error.message); return m.result || {}; };
  await call('Runtime.enable'); await call('Page.enable'); await call('Network.enable');
  // mobile:false keeps the layout viewport at exactly <width> CSS px; with mobile:true
  // Chrome widens the viewport to fit overflowing content, which hides the overflow
  // this review exists to find.
  await call('Emulation.setDeviceMetricsOverride', { width: Number(width), height: HEIGHT, deviceScaleFactor: 1, mobile: false });
  const nav = await call('Page.navigate', { url });
  if (nav.errorText) fail('navigate failed: ' + nav.errorText);
  for (let i = 0; i < LOAD_TRIES; i++) { await sleep(250); const r = await call('Runtime.evaluate', { expression: "document.readyState === 'complete'", returnByValue: true }); if (r.result && r.result.value) break; }
  await sleep(SETTLE_MS);
  // A server that has not bound its port yet yields Chrome's own error page, which renders and
  // dumps like any other; the missing document response is what tells them apart.
  if (/^https?:/.test(url) && mainStatus === null) fail('no document response from ' + url + ' (is the server up?)');
  if (mainStatus !== null && mainStatus >= 400) fail('document returned HTTP ' + mainStatus + ' for ' + url);
  if (process.env.CLASS) {
    await call('Runtime.evaluate', { expression: `document.documentElement.classList.add(${JSON.stringify(process.env.CLASS)})` });
    await sleep(SETTLE_MS / 2);
  }
  const evaluate = async expression => {
    const r = await call('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) fail('expression threw: ' + r.exceptionDetails.text + ' ' + ((r.exceptionDetails.exception || {}).description || ''));
    return 'value' in r.result ? r.result.value : r.result;
  };
  console.log(JSON.stringify(await evaluate(expr || 'document.title'), null, 1));
  if (process.env.DUMP) fs.writeFileSync(process.env.DUMP, JSON.stringify(await evaluate(DUMP_EXPR), null, 1));
  if (process.env.SHOT) {
    const sc = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(process.env.SHOT, Buffer.from(sc.data, 'base64'));
  }
  if (logs.length) console.log('CONSOLE_ERRORS', JSON.stringify(logs));
  ws.close(); quit(0);
})();
