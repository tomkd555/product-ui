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
//                 plus fontFamily, textTransform, letterSpacing, backgroundClip and whether the background
//                 image is a gradient (for R16, R19), the padding and border sizes (`pad`, for R21, R22), the page `lang`, and, per box, borderRadius,
//                 backdropFilter, hasMedia and hasHeading (for R17, R18, R20);
//                 and the composition of the first <main> (else <body>): `scope` (its rect),
//                 `boxes` (elements drawn as an enclosure: a border on two or more sides, a fill that differs in value from the
//                 background behind it and is narrower than <main>, or a shadow that draws; with nesting depth and parent box), and
//                 `gaps` (per parent, the spacing between consecutive children, 0..200px rounded
//                 to 4px)
//                 For the checks ported from impeccable (R25 to R41): per text entry fontStyle, textAlign, hyphens,
//                 hTag, inHeading, inControl, ownH (height of the element's own text), fullLen (length of its subtree
//                 text) and, for a bordered or filled box, `cramp`; per box borderW, borderA, boxShadow and domParent;
//                 and the top-level h1s, labels (the element before each heading, with the raw colour of a dash as
//                 dashColor), edgeText, headingGaps, hiddenText (the whole document; scroll-linked reveals are probed
//                 by scrolling to the largest hidden boxes), occlusions (an elementFromPoint probe, so only text in the
//                 first viewport), repeatGroups, iconTiles, textOverflow (probed after scrolling to each candidate, 12
//                 at most) and portErrors (the sections of this group that threw, each caught on its own). The page's
//                 scroll position is restored after the probes; SHOT is taken before DUMP runs.
//                 For R42 to R48: per box inPattern (inside a data-pattern element) and hasField (holds a form
//                 control); and `patterns`, each data-pattern element with its id, rect, group (index of its
//                 parent among the pattern parents), outer (the pattern it sits in), shortCells (td texts of 3
//                 characters or fewer) and slots (slot, field, text, empty, hidden, root, the strongest
//                 fontSize and fontWeight inside it, textAlign, fontVariantNumeric, rect).
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
// no ancestor paints, or whose nearest painted background is an image or a gradient, is reported
// as white with `backgroundFallback: true`, so the checks can leave it out: that white is a
// colour nobody chose.
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
const DUMP_EXPR = `(async () => {
  const MAX_ELS = ${MAX_ELS}, MAX_CONTROLS = ${MAX_CONTROLS}, TEXT_CAP = ${TEXT_CAP}, LABEL_CAP = ${LABEL_CAP}, MAX_BOXES = ${MAX_BOXES}, MAX_GAP_PARENTS = ${MAX_GAP_PARENTS};
  const v = window, d = document;
  // [colour, fallback]: fallback is true when no ancestor paints a background.
  const painted = c => c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent';
  const alphaOfBg = c => { const m = /\\/\\s*([\\d.]+)(%?)\\s*\\)\\s*$/.exec(c); if (m) return m[2] ? m[1] / 100 : +m[1]; const r = /^rgba\\([^,]+,[^,]+,[^,]+,\\s*([\\d.]+)\\)$/.exec(c); return r ? +r[1] : 1; };
  // [colour, fallback, base]: the nearest painted background; when it is translucent, base is the nearest opaque
  // ancestor colour to composite it over (white when none paints). fallback is true when no ancestor paints at all, or when an image or a gradient lies over the nearest opaque colour.
  const bg = el => { let first = null; for (let e = el; e; e = e.parentElement) { const cs = v.getComputedStyle(e), c = cs.backgroundColor; if (cs.backgroundImage !== 'none') return [first || 'rgb(255, 255, 255)', true, undefined]; if (!painted(c)) continue; if (first === null) { first = c; if (alphaOfBg(c) >= 1) return [c, false, undefined]; continue; } if (alphaOfBg(c) >= 1) return [first, false, c]; } return first === null ? ['rgb(255, 255, 255)', true, undefined] : [first, false, 'rgb(255, 255, 255)']; };
  const ownText = el => Array.from(el.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\\s+/g, ' ').trim();
  const all = d.body.querySelectorAll('*');
  const text = [], textEls = [];
  for (const el of all) {
    if (text.length >= MAX_ELS) break;
    const own = ownText(el); if (!own) continue;
    const s = v.getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect(); if (!r.width && !r.height) continue;
    const [background, backgroundFallback, backgroundBase] = bg(el);
    text.push({ tag: el.tagName.toLowerCase(), id: el.id || undefined, cls: (el.className && typeof el.className === 'string') ? el.className.slice(0, 60) : undefined,
      text: own.slice(0, TEXT_CAP), color: s.color, background, backgroundFallback: backgroundFallback || undefined, backgroundBase,
      opacity: s.opacity !== '1' ? s.opacity : undefined, fontSize: s.fontSize, fontWeight: s.fontWeight,
      lineHeight: s.lineHeight, fontFamily: s.fontFamily, textTransform: s.textTransform !== 'none' ? s.textTransform : undefined,
      letterSpacing: s.letterSpacing !== 'normal' ? s.letterSpacing : undefined,
      backgroundClip: s.backgroundClip, webkitBackgroundClip: s.webkitBackgroundClip || undefined,
      backgroundImage: /gradient\\(/.test(s.backgroundImage), rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
      pad: { x: Math.round(parseFloat(s.paddingLeft) + parseFloat(s.paddingRight) + parseFloat(s.borderLeftWidth) + parseFloat(s.borderRightWidth)),
             y: Math.round(parseFloat(s.paddingTop) + parseFloat(s.paddingBottom) + parseFloat(s.borderTopWidth) + parseFloat(s.borderBottomWidth)) },
      clipped: el.scrollWidth > el.clientWidth + 1 && s.overflowX !== 'visible',
      disabled: el.closest('[disabled],[aria-disabled="true"]') ? true : undefined,
      fontStyle: s.fontStyle, textAlign: s.textAlign, hyphens: s.textAlign === 'justify' ? (s.hyphens || s.webkitHyphens) : undefined,
      hTag: (hh => hh ? hh.tagName.toLowerCase() : undefined)(el.closest('h1,h2')),
      inHeading: !!el.closest('h1,h2,h3,h4,h5,h6,[role="heading"]'),
      inControl: !!el.closest('a[href],button,[role="button"],[role="link"],[role="tab"]') });
    textEls.push(el);
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
  const COLOURISH = /^(#|rgb|hsl|oklch|oklab|lab|lch|color\\(|color-mix\\()/;
  for (const prop of Object.keys(tokens)) { if (!COLOURISH.test(tokens[prop])) continue; probe.style.color = ''; probe.style.color = 'var(' + prop + ')'; const c = v.getComputedStyle(probe).color; if (painted(c)) tokens[prop] = c; }
  probe.remove();
  // Composition of the first <main> (else <body>): enclosures and the spacing between siblings.
  const root = d.querySelector('main') || d.body;
  const rr = r => ({ x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
  const alphaOf = c => { if (!c || c === 'transparent') return 0; const m = /\\/\\s*([\\d.]+)(%?)\\s*\\)\\s*$/.exec(c); if (m) return m[2] ? m[1] / 100 : +m[1];
    const f = /^rgba\\(([^)]*)\\)$/.exec(c); if (f) { const p = f[1].split(','); if (p.length === 4) return +p[3]; } return 1; };
  // Two colours in any notation compare by their rendered pixel, within 1/255 per channel and in alpha.
  const px = (() => { const cv = d.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true });
    return c => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); return cx.getImageData(0, 0, 1, 1).data; }; })();
  const sameColour = (a, b) => { const p = px(a), q = px(b); return p.every((x, i) => Math.abs(x - q[i]) <= 1); };
  // A shadow draws when some layer has a visible colour and a non-zero length (Tailwind's shadow-none is a 0 0 #0000 layer).
  const shadowDraws = sh => sh !== 'none' && sh.split(/,(?![^(]*\\))/).some(l => { const c = (/\\w+\\([^)]*\\)/.exec(l) || ['rgb(0, 0, 0)'])[0]; return alphaOf(c) > 0 && /[1-9]/.test(l.replace(c, '')); });
  const rootRect = root.getBoundingClientRect();
  const NOT_BOX = new Set(['a','button','input','select','textarea','img','svg','canvas','video','td','th','tr','thead','tbody','table','li','summary','label']);
  const BOX_DISPLAY = new Set(['block','flex','grid','flow-root']);
  const SIDES = ['Top','Right','Bottom','Left'];
  const sel = el => { const c = (el.className && typeof el.className === 'string') ? el.className.trim().split(/\\s+/)[0] : ''; return el.tagName.toLowerCase() + (el.id ? '#' + el.id : c ? '.' + c : ''); };
  const boxes = [], boxAt = new Map(), gaps = [], domIds = new Map();
  const domId = e => { if (!domIds.has(e)) domIds.set(e, domIds.size); return domIds.get(e); };
  let boxesTotal = 0, gapsTotal = 0;
  for (const el of [root, ...root.querySelectorAll('*')]) {
    if (el.namespaceURI !== 'http://www.w3.org/1999/xhtml') continue;   // the insides of an svg are not layout
    if (el !== root && !NOT_BOX.has(el.tagName.toLowerCase())) {
      const s = v.getComputedStyle(el);
      if (BOX_DISPLAY.has(s.display) && s.visibility !== 'hidden') {
        const r = el.getBoundingClientRect();
        if (r.width >= 40 && r.height >= 40 &&
            (SIDES.filter(k => parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' && alphaOf(s['border' + k + 'Color']) > 0).length >= 2 ||
             (alphaOf(s.backgroundColor) > 0 && r.width < rootRect.width - 1 && !sameColour(s.backgroundColor, bg(el.parentElement)[0])) || shadowDraws(s.boxShadow))) {
          boxesTotal++;
          if (boxes.length < MAX_BOXES) {
            let a = el.parentElement; while (a && !boxAt.has(a)) a = a.parentElement;
            const up = a ? boxAt.get(a) : null;
            boxAt.set(el, { i: boxes.length, depth: up ? up.depth + 1 : 0 });
            boxes.push({ tag: el.tagName.toLowerCase(), id: el.id || undefined, cls: (el.className && typeof el.className === 'string') ? el.className.slice(0, 60) : undefined,
              rect: rr(r), depth: up ? up.depth + 1 : 0, parentBox: up ? up.i : null, domParent: domId(el.parentElement), children: el.childElementCount,
              hasDigit: /[0-9\\uFF10-\\uFF19]/.test(el.textContent),
              inPattern: !!el.closest('[data-pattern]') || undefined, hasField: !!el.querySelector('input,select,textarea') || undefined,
              borderRadius: s.borderRadius, backdropFilter: s.backdropFilter || s.webkitBackdropFilter || 'none',
              borderW: SIDES.map(k => s['border' + k + 'Style'] === 'none' ? 0 : parseFloat(s['border' + k + 'Width']) || 0),
              borderA: SIDES.map(k => alphaOf(s['border' + k + 'Color'])), boxShadow: s.boxShadow,
              hasMedia: !!el.querySelector('svg,img') || /^\\s*\\p{Extended_Pictographic}/u.test(el.textContent),
              hasHeading: !!el.querySelector('h1,h2,h3,h4,h5,h6,[role=heading]') });
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
  // ---- data for the checks ported from impeccable (R25 to R41, R4/R20/R21 extensions) ----
  // Each section runs on its own: a throw in one is recorded in portErrors and leaves the dump above it and
  // the other sections intact.
  const portErrors = [];
  const guard = (name, fn) => { try { fn(); } catch (e) { portErrors.push(name + ': ' + (e && e.message || e)); } };
  const guardAsync = async (name, fn) => { try { await fn(); } catch (e) { portErrors.push(name + ': ' + (e && e.message || e)); } };
  const cs1 = e => v.getComputedStyle(e);
  const num = x => parseFloat(x) || 0;
  const clip = (t, n) => (t || '').replace(/\\s+/g, ' ').trim().slice(0, n);
  const r1 = x => Math.round(x * 10) / 10;
  const visible = e => { const s = cs1(e); const r = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  const borderSides = s => SIDES.filter(k => num(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' && alphaOf(s['border' + k + 'Color']) > 0);
  // The rect of the element's own text nodes (deep: every text node below it).
  const textRect = (el, deep) => {
    const rg = d.createRange(); let l = 1e9, t = 1e9, r = -1e9, b = -1e9;
    const w = d.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!deep && n.parentNode !== el) continue;
      if (!n.textContent.trim()) continue;
      rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) { if (q.width <= 0 || q.height <= 0) continue; l = Math.min(l, q.left); t = Math.min(t, q.top); r = Math.max(r, q.right); b = Math.max(b, q.bottom); }
    }
    return r > l ? { l, t, r, b } : null;
  };
  const vw1 = v.innerWidth, vh1 = v.innerHeight;
  const sx0 = v.scrollX, sy0 = v.scrollY;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const frame = () => new Promise(r => { const t = setTimeout(r, 150); requestAnimationFrame(() => requestAnimationFrame(() => { clearTimeout(t); r(); })); });
  // Scroll so that the element's middle sits in the middle of the viewport (instant, whatever scroll-behavior says).
  const jump = el => { const r = el.getBoundingClientRect(); v.scrollTo({ left: v.scrollX, top: v.scrollY + r.top + r.height / 2 - vh1 / 2, behavior: 'instant' }); };
  const restoreScroll = () => v.scrollTo({ left: sx0, top: sy0, behavior: 'instant' });

  // R21: the height of each element's own text (lines are counted on it, not on the box), and the length of its subtree text.
  guard('ownText', () => {
    for (let i = 0; i < textEls.length; i++) {
      const t = textRect(textEls[i], false); if (t) text[i].ownH = r1(t.b - t.t);
      text[i].fullLen = textEls[i].textContent.trim().length;
    }
  });

  // R34: the space between a bordered or coloured box and its own text.
  guard('cramp', () => {
    for (let i = 0; i < textEls.length; i++) {
      const el = textEls[i], ent = text[i], s = cs1(el);
      if (ent.text.length <= 10 || el.textContent.trim().length <= 20 || s.display === 'inline' || (el.tagName === 'CODE' && !el.closest('pre'))) continue;
      const r = el.getBoundingClientRect(); if (r.width <= 100 || r.height <= 30) continue;
      const bv = SIDES.map(k => num(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' && alphaOf(s['border' + k + 'Color']) > 0);
      const bgv = alphaOf(s.backgroundColor) > 0 && !sameColour(s.backgroundColor, bg(el.parentElement)[0]);
      if (bv.filter(Boolean).length < 2 && !bgv) continue;
      const t = textRect(el, false); if (!t) continue;
      const bw = SIDES.map(k => num(s['border' + k + 'Width']));
      ent.cramp = { pad: SIDES.map(k => num(s['padding' + k])), bv, bg: bgv, bleed: bgv && r.left <= 2 && r.right >= d.documentElement.clientWidth - 2,
        inset: [r1(t.t - (r.top + bw[0])), r1((r.right - bw[1]) - t.r), r1((r.bottom - bw[2]) - t.b), r1(t.l - (r.left + bw[3]))] };
    }
  });

  // R29: the h1 elements, whole.
  let h1s = [];
  guard('h1s', () => {
    h1s = Array.from(d.querySelectorAll('h1')).filter(visible).slice(0, 5)
      .map(h => ({ text: clip(h.textContent, 160), fontSize: cs1(h).fontSize, rect: rr(h.getBoundingClientRect()) }));
  });

  // R26, R27, R28: the element before each heading, climbing up to 4 wrappers while the heading leads its parent.
  const SKIP_SEL = 'nav,form,table,thead,tbody,tfoot,figure,figcaption,ol,ul,li,[role="navigation"],[aria-label*="breadcrumb" i],[class*="breadcrumb" i],[aria-hidden="true"],[data-impeccable-allow-kickers]';
  const APP_SEL = '[role="tabpanel"],[role="dialog"],[role="application"],dialog';
  const CARD_SEL = 'article,button,a,li,[role="listitem"],[role="option"]';
  const labelBefore = h => { let cur = h; for (let lv = 0; lv <= 4; lv++) { const p = cur.previousElementSibling; if (p) return { el: p, levels: lv }; const par = cur.parentElement; if (!par || par === d.body || par === d.documentElement) return null; cur = par; } return null; };
  const typeEl = lab => { let e = lab; for (let i = 0; i < 3; i++) { if (ownText(e)) return e; const kids = Array.from(e.children).filter(c => c.textContent.trim()); if (kids.length !== 1) return e; e = kids[0]; } return e; };
  // The raw background colour of a dash drawn by ::before or ::after (8 to 80px by 1 to 6px); check_render.py decides whether it is an accent.
  const accentDash = lab => {
    for (const ps of ['::before', '::after']) {
      const p = v.getComputedStyle(lab, ps); if (!p.content || p.content === 'none' || p.content === 'normal') continue;
      const w = num(p.width), hh = num(p.height); if (!(w >= 8 && w <= 80 && hh >= 1 && hh <= 6) || alphaOf(p.backgroundColor) < 0.1) continue;
      return p.backgroundColor;
    }
    return '';
  };
  const labels = [];
  guard('labels', () => {
    for (const h of d.querySelectorAll('h1,h2,h3,h4,[role="heading"]')) {
      if (labels.length >= 60) break;
      if (!visible(h)) continue;
      const found = labelBefore(h); if (!found || !visible(found.el)) continue;
      const lab = found.el, te = typeEl(lab);
      const hr = h.getBoundingClientRect(), lr = lab.getBoundingClientRect(), tr = te.getBoundingClientRect();
      const hs = cs1(h), ls = cs1(te), card = h.closest(CARD_SEL);
      const gap = Math.max(0, hr.top - lr.bottom, hr.left - lr.right);
      const side = tr.right <= hr.left + 1 || tr.left >= hr.right - 1;
      labels.push({ hTag: h.tagName.toLowerCase(), hLevel: /^H[1-6]$/.test(h.tagName) ? +h.tagName[1] : (+h.getAttribute('aria-level') || 2),
        hText: clip(h.textContent, 80), hSize: hs.fontSize,
        lTag: lab.tagName.toLowerCase(), lText: clip(ownText(te) || te.textContent, 60), lFull: clip(lab.textContent, 80), lSize: ls.fontSize,
        lSpacing: ls.letterSpacing === 'normal' ? '0px' : ls.letterSpacing, lTransform: ls.textTransform, lVariant: ls.fontVariant + ' ' + ls.fontVariantCaps,
        lWeight: ls.fontWeight, lColor: ls.color, lFamily: ls.fontFamily,
        levels: found.levels, near: lr.width > 0 && lr.height > 0 && lr.top < hr.bottom && gap <= 96,
        beside: (side && !(tr.bottom <= hr.top - tr.height / 2)) || tr.top >= hr.bottom,
        skip: !!(h.closest(SKIP_SEL) || lab.closest(SKIP_SEL)), app: !!h.closest(APP_SEL), inCard: !!(card && card.contains(lab)),
        media: !!lab.querySelector('img,svg,picture,video'), dashColor: accentDash(lab) || undefined, hasTime: lab.tagName === 'TIME' || !!lab.querySelector('time') });
    }
  });

  // R35: paragraph text near the left or right viewport edge.
  const edgeText = [];
  guard('edgeText', () => {
    for (const el of d.querySelectorAll('p,li')) {
      if (edgeText.length >= 80) break;
      if (el.textContent.trim().length <= 40 || !visible(el)) continue;
      const t = textRect(el, true); if (!t) continue;
      const s = cs1(el), r = el.getBoundingClientRect(), header = el.closest('header');
      const cl = r.left + num(s.borderLeftWidth) + num(s.paddingLeft), cr = r.right - num(s.borderRightWidth) - num(s.paddingRight);
      if (Math.min(t.l, cl) >= 24 && vw1 - Math.max(t.r, cr) >= 24) continue;
      let fixedBar = false;
      for (let a = el.parentElement; a && a !== d.body; a = a.parentElement) if (cs1(a).position === 'fixed') { const ar = a.getBoundingClientRect(); if (ar.height > 0 && ar.height < vh1 * 0.5) { fixedBar = true; break; } }
      edgeText.push({ sel: sel(el), text: clip(el.textContent, 40), w: Math.round(r.width), tl: r1(t.l), tr: r1(t.r), cl: r1(cl), cr: r1(cr),
        lines: Math.max(1, Math.round((t.b - t.t) / (num(s.lineHeight) || num(s.fontSize) * 1.2))), align: s.textAlign, listItem: s.display === 'list-item',
        inNav: !!el.closest('nav') || !!(header && header.getBoundingClientRect().height <= vh1), ownBg: alphaOf(s.backgroundColor) > 0,
        positioned: s.position === 'fixed' || s.position === 'absolute', fixedBar });
    }
  });

  // R36: the space above and below each h2 to h4. An empty spacer block counts as space, an eyebrow label directly above a
  // heading belongs to the heading, and a block above that ends in running prose is reported as aboveProse.
  const headingGaps = [];
  guard('headingGaps', () => {
    const MEDIA = /^(IMG|PICTURE|VIDEO|CANVAS|SVG|IFRAME)$/, CONTROL = /^(INPUT|TEXTAREA|SELECT|BUTTON|METER|PROGRESS)$/, HEAD = /^H[1-6]$/;
    const fontSize = e => num(cs1(e).fontSize) || 16;
    const hasWords = e => Array.from(e.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    const bandDiffers = e => alphaOf(cs1(e).backgroundColor) > 0.05 && !sameColour(cs1(e).backgroundColor, bg(e.parentElement)[0]);
    const imageBand = e => { const s = cs1(e); if (s.backgroundImage === 'none' || /text/.test(s.backgroundClip) || /text/.test(s.webkitBackgroundClip || '')) return false;
      return s.backgroundSize === 'cover' || (/gradient\\(/.test(s.backgroundImage) && /^(auto( auto)?|100% 100%)$/.test(s.backgroundSize)); };
    const contents = e => cs1(e).display === 'contents';
    const paintsEdge = (e, side) => { const s = cs1(e); if (s.display === 'contents') return false; return alphaOf(s.backgroundColor) > 0.05 || imageBand(e) || num(s['border' + side + 'Width']) > 0 || shadowDraws(s.boxShadow); };
    const drawsTopEdge = e => { const s = cs1(e); if (s.display === 'contents') return false; return num(s.borderTopWidth) > 0 || imageBand(e) || (s.boxShadow && s.boxShadow !== 'none') || bandDiffers(e); };
    const drawsBottomEdge = e => { const s = cs1(e); if (s.display === 'contents') return false; return num(s.borderBottomWidth) > 0 || shadowDraws(s.boxShadow) || bandDiffers(e); };
    const renderedKids = e => Array.from(e.children).filter(k => { const s = cs1(k); if (s.display === 'none' || s.position === 'absolute' || s.position === 'fixed') return false; const r = k.getBoundingClientRect(); return r.width >= 1 && r.height >= 1; });
    const spacerPaints = e => { const s = cs1(e); if (s.display === 'contents') return false; const a = alphaOf(s.backgroundColor); if (a > 0.05 && (a < 1 || bandDiffers(e))) return true; return imageBand(e) || num(s.borderBottomWidth) > 0 || shadowDraws(s.boxShadow); };
    const emptyBox = (e, depth) => {
      if (spacerPaints(e) || MEDIA.test(e.tagName) || CONTROL.test(e.tagName) || e.tagName === 'HR' || num(cs1(e).borderTopWidth) > 0) return false;
      const kids = renderedKids(e); return kids.length === 0 || (depth > 0 && kids.every(k => emptyBox(k, depth - 1)));
    };
    // An empty box that only holds space open: no text, no picture, nothing painted.
    const isSpacer = e => e.textContent.trim() === '' && emptyBox(e, 4);
    const visFlow = e => { if (/^(SCRIPT|STYLE|TEMPLATE|NOSCRIPT)$/.test(e.tagName)) return false; const s = cs1(e);
      if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity <= 0.05 || /^(absolute|fixed|sticky)$/.test(s.position)) return false;
      const r = e.getBoundingClientRect(); return r.width >= 1 && r.height >= 1; };
    const overlapsX = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) >= 8;
    const flowBoxOf = (s, hr, fromEnd, pick) => {
      if (contents(s)) { const kids = Array.from(s.children); if (fromEnd) kids.reverse(); for (const k of kids) { const b = flowBoxOf(k, hr, fromEnd, pick); if (b && !isSpacer(b)) return b; } return null; }
      if (!visFlow(s)) return null; const sr = s.getBoundingClientRect(); return pick(sr) && overlapsX(sr, hr) ? s : null;
    };
    const lowestContent = e => {
      let cur = e;
      for (let i = 0; i < 8; i++) {
        const r = cur.getBoundingClientRect();
        if (paintsEdge(cur, 'Bottom') || MEDIA.test(cur.tagName)) return r.bottom;
        const kids = renderedKids(cur).filter(k => !isSpacer(k));
        if (!kids.length) return r.bottom - Math.max(0, num(cs1(cur).paddingBottom));
        cur = kids.reduce((a, b) => b.getBoundingClientRect().bottom > a.getBoundingClientRect().bottom ? b : a);
      }
      return cur.getBoundingClientRect().bottom;
    };
    const contentBottom = e => Math.min(lowestContent(e), e.getBoundingClientRect().bottom);
    const sideLandmark = e => /^(FOOTER|NAV|ASIDE|HEADER)$/.test(e.tagName) || /(^|\\s)(contentinfo|navigation|complementary|banner)(\\s|$)/i.test(e.getAttribute('role') || '');
    const mainLandmark = e => e.tagName === 'MAIN' || /(^|\\s)main(\\s|$)/i.test(e.getAttribute('role') || '');
    // The nearest block below the heading, and above the heading's cluster.
    const edgeBelow = (h, hr) => {
      const pick = sr => sr.top >= hr.bottom - 2;
      for (let n = h; n && n !== d.body;) {
        let nearest = null;
        for (let s = n.nextElementSibling; s; s = s.nextElementSibling) { const b = flowBoxOf(s, hr, false, pick); if (b && !isSpacer(b)) { const t = b.getBoundingClientRect().top; if (!nearest || t < nearest.t) nearest = { t, el: b }; } }
        if (nearest) return n !== h && sideLandmark(nearest.el) ? null : nearest;
        const p = n.parentElement; if (!p) return null;
        if (p !== d.body && !contents(p) && drawsBottomEdge(p)) return null;
        if (mainLandmark(p)) return null;
        n = p;
      }
      return null;
    };
    const edgeAbove = (start, top, hr) => {
      const pick = sr => sr.bottom <= top + 2;
      const inset = paintsEdge(start, 'Top') ? 0 : Math.max(0, num(cs1(start).paddingTop));
      for (let n = start; n && n !== d.body;) {
        let nearest = null;
        for (let s = n.previousElementSibling; s; s = s.previousElementSibling) { const b = flowBoxOf(s, hr, true, pick); if (b && !isSpacer(b)) { const bt = contentBottom(b); if (!nearest || bt > nearest.b) nearest = { b: bt, el: b }; } }
        if (nearest) return { bottom: nearest.b - inset, el: nearest.el };
        const p = n.parentElement; if (!p || p === d.body) return null;
        if (drawsTopEdge(p)) return null;
        n = p;
      }
      return null;
    };
    const previousBox = n => {
      for (let s = n.previousElementSibling; s; s = s.previousElementSibling) {
        if (contents(s)) { const inner = Array.from(s.children).reverse().find(k => { const r = k.getBoundingClientRect(); return r.width >= 1 && r.height >= 1; }); if (inner) return inner; }
        else { const r = s.getBoundingClientRect(); if (cs1(s).display !== 'none' && r.width >= 1 && r.height >= 1) return s; }
      }
      return null;
    };
    const subtree = (e, limit) => { const out = [], st = [e]; while (st.length && out.length < limit) { const c = st.pop(); out.push(c); st.push(...Array.from(c.children).reverse()); } return out; };
    const textSizeOf = e => fontSize(subtree(e, 60).find(hasWords) || e);
    const lineTops = e => { const rg = d.createRange(); rg.selectNodeContents(e); const tops = []; for (const q of rg.getClientRects()) { if (q.width > 0 && q.height > 0 && !tops.some(t => Math.abs(t - q.top) <= 2)) tops.push(q.top); } return tops; };
    const differs = (a, b) => { const p = px(cs1(a).color), q = px(cs1(b).color); return Math.abs(p[0] - q[0]) >= 32 || Math.abs(p[1] - q[1]) >= 32 || Math.abs(p[2] - q[2]) >= 32 || Math.abs(p[3] - q[3]) / 255 >= 0.25; };
    const italic = e => /^(italic|oblique)/.test(cs1(e).fontStyle);
    // A short line at body size that colour, italics or a much lighter weight sets apart (only when it opens its parent).
    const setApart = (line, heading, words) => {
      const container = line.parentElement; if (!container || clip(line.textContent, 200).length > 40) return false;
      const size = fontSize(words), lh = parseFloat(cs1(words).lineHeight), pitch = isFinite(lh) && lh > 0 ? lh : size * 1.2;
      const t = textRect(words, false); if (!(t && t.b - t.t > 0 && t.b - t.t < Math.max(pitch, size * 1.2) * 1.5)) return false;
      if (differs(words, container) && differs(words, heading)) return true;
      if (italic(words) && !italic(container) && !italic(heading)) return true;
      const wt = +cs1(words).fontWeight, around = +cs1(container).fontWeight;
      return isFinite(wt) && isFinite(around) && wt <= around - 300;
    };
    const readsAsEyebrow = (line, heading, textSize, opens) => {
      const hs = fontSize(heading), span = Math.max(heading.getBoundingClientRect().width, line.getBoundingClientRect().width);
      for (const e of subtree(line, 40)) {
        const er = e.getBoundingClientRect();
        if (paintsEdge(e, 'Bottom') && er.width >= 1 && er.width < span * 0.6 && e.textContent.trim()) return true;
        if (!hasWords(e)) continue;
        const size = fontSize(e); if (size > hs) continue;
        const es = cs1(e);
        if (size < textSize * 0.92 || es.textTransform === 'uppercase') return true;
        const tracking = parseFloat(es.letterSpacing); if (isFinite(tracking) && tracking >= 0.5) return true;
        const cased = Array.from(Array.from(e.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join('')).filter(c => c.toUpperCase() !== c.toLowerCase());
        if (cased.length >= 3 && cased.every(c => c === c.toUpperCase())) return true;
        if (opens && setApart(line, heading, e)) return true;
      }
      return false;
    };
    // The top of the heading's cluster: up to 3 label lines above it that read as its eyebrow or subtitle.
    const clusterTop = (h, hr, textSize, below) => {
      let topEl = h, top = hr.top, cursor = h, folded = 0;
      while (folded < 3) {
        const sib = previousBox(cursor);
        if (!sib) {
          const p = cursor.parentElement; if (!p || p === d.body) break;
          if (!(contents(p) || (Math.abs(p.getBoundingClientRect().top - top) <= 1 && !paintsEdge(p, 'Top')))) break;
          cursor = p; continue;
        }
        if (isSpacer(sib)) { cursor = sib; continue; }
        if (!visFlow(sib)) break;
        const sr = sib.getBoundingClientRect();
        if (!overlapsX(sr, hr)) break;
        const gap = top - sr.bottom; if (gap < 0 || sr.height > 60) break;
        const opens = previousBox(sib) === null, wide = gap >= 28;
        if (wide && !(opens && gap < below && gap <= 64)) break;
        const txt = sib.textContent.trim(); if (!txt.length || HEAD.test(sib.tagName) || txt.length > 80) break;
        const subtitle = !wide && opens && gap <= 2 && fontSize(sib) <= fontSize(h) && lineTops(sib).length === 1;
        if (!subtitle && !readsAsEyebrow(sib, h, textSize, opens)) break;
        topEl = sib; top = sr.top; cursor = sib; folded++;
      }
      return { el: topEl, top };
    };
    // The block above already separates the heading: a rule, a picture, a bottom border drawn alone, a heading.
    const separates = el => {
      const er = el.getBoundingClientRect();
      if (el.tagName === 'HR' || er.height <= 4) return true;
      if (!el.textContent.trim() && el.querySelector('img,picture,video,canvas,svg,iframe')) return true;
      let cur = el, framed = false;
      for (let i = 0; i < 8 && cur; i++) {
        const cr = cur.getBoundingClientRect(), cst = cs1(cur);
        framed = framed || num(cst.borderTopWidth) > 0 || num(cst.borderLeftWidth) > 0 || num(cst.borderRightWidth) > 0;
        if (!framed && num(cst.borderBottomWidth) > 0 && cr.width >= er.width * 0.9) return true;
        if (MEDIA.test(cur.tagName) && cr.width >= er.width * 0.5) return true;
        if (HEAD.test(cur.tagName)) return true;
        cur = Array.from(cur.children).reverse().find(k => { if (cs1(k).display === 'none') return false; const kr = k.getBoundingClientRect(); return kr.width >= 1 && kr.height >= 1 && kr.bottom >= er.bottom - 2; }) || null;
      }
      return false;
    };
    // The block above ends in running prose: 80 characters on 2 lines or more, smaller than the heading, no larger than
    // 1.25 times the body text, across at least half the heading's width.
    const closingText = block => {
      let cur = block;
      for (let i = 0; i < 12; i++) {
        if (MEDIA.test(cur.tagName) || drawsBottomEdge(cur)) return null;
        if (hasWords(cur)) return cur;
        const kids = renderedKids(cur).filter(k => !isSpacer(k)); if (!kids.length) return null;
        cur = kids.reduce((a, b) => b.getBoundingClientRect().bottom > a.getBoundingClientRect().bottom ? b : a);
      }
      return null;
    };
    const endsInProse = (block, h, textSize) => {
      const te = closingText(block); if (!te || HEAD.test(te.tagName)) return false;
      const size = fontSize(te); if (size >= fontSize(h) || size > textSize * 1.25) return false;
      if (clip(te.textContent, 200).length < 80 || te.getBoundingClientRect().width < h.getBoundingClientRect().width * 0.5) return false;
      return lineTops(te).length >= 2;
    };
    const cardish = (e, s) => ((s.boxShadow && s.boxShadow !== 'none') || borderSides(s).length >= 3) && (num(s.borderTopLeftRadius) > 0 || alphaOf(s.backgroundColor) > 0);
    for (const h of d.querySelectorAll('h2,h3,h4')) {
      if (headingGaps.length >= 60) break;
      if (!visible(h) || h.closest('blockquote,q') || clip(h.textContent, 10).length < 3 || cs1(h).display === 'inline') continue;
      const hr = h.getBoundingClientRect();
      let below = null, above = null, aboveEl = null, aboveProse = false;
      const eb = edgeBelow(h, hr);
      if (eb) {
        below = Math.max(0, eb.t - hr.bottom);
        const textSize = Math.max(fontSize(d.body), textSizeOf(eb.el));
        const ct = clusterTop(h, hr, textSize, below), ea = edgeAbove(ct.el, ct.top, hr);
        if (ea) { above = Math.max(0, ct.top - ea.bottom); aboveEl = ea.el; aboveProse = endsInProse(ea.el, h, textSize); }
      }
      let inCard = false;
      for (let a = h.parentElement; a && a !== d.body; a = a.parentElement) { const as = cs1(a); if (cardish(a, as) && a.getBoundingClientRect().height < 200) { inCard = true; break; } }
      headingGaps.push({ tag: h.tagName.toLowerCase(), text: clip(h.textContent, 60), above: above === null ? null : r1(above), below: below === null ? null : r1(below),
        topEdge: paintsEdge(h, 'Top'), inCard, aboveSeparates: !!aboveEl && separates(aboveEl), aboveProse });
    }
  });

  // R32: elementFromPoint probe over the lines of every text element in the first viewport.
  const occlusions = [];
  guard('occlusions', () => {
    const opaque = (e, s) => alphaOf(s.backgroundColor) > 0.6 || borderSides(s).length >= 2;
    const pinned = e => { for (let a = e; a && a !== d.body; a = a.parentElement) { const p = cs1(a).position; if (p === 'fixed' || p === 'sticky') return true; } return false; };
    for (let i = 0; i < textEls.length && occlusions.length < 30; i++) {
      const el = textEls[i];
      if (ownText(el).length < 2) continue;
      const t = textRect(el, false); if (!t) continue;
      let L = t.l, T = t.t, R = t.r, B = t.b;
      for (let a = el.parentElement; a && a !== d.documentElement; a = a.parentElement) {
        const as = cs1(a), cx = as.overflowX !== 'visible', cy = as.overflowY !== 'visible'; if (!cx && !cy) continue;
        const ar = a.getBoundingClientRect(); if (cx) { L = Math.max(L, ar.left); R = Math.min(R, ar.right); } if (cy) { T = Math.max(T, ar.top); B = Math.min(B, ar.bottom); }
      }
      if (R - L < 6 || B - T < 6 || B <= 0 || T >= vh1) continue;
      const s0 = cs1(el); if (+s0.opacity <= 0.02) continue;
      const cols = Math.max(6, Math.min(30, Math.round((R - L) / 12))), rows = Math.max(1, Math.min(4, Math.round((B - T) / 14)));
      let total = 0, hit = 0, by = null, kind = '', layered = false;
      for (let a = 0; a < cols; a++) {
        const x = L + (R - L) * ((a + 0.5) / cols); if (x < 1 || x > vw1 - 1) continue;
        for (let b = 0; b < rows; b++) {
          const y = T + (B - T) * ((b + 0.5) / rows); if (y < 1 || y > vh1 - 1) continue;
          total++;
          const top = d.elementFromPoint(x, y); if (!top || top === el || el.contains(top) || top.contains(el)) continue;
          const ts = cs1(top);
          if (ts.float !== 'none' || ts.pointerEvents === 'none' || +ts.opacity <= 0.02 || /^(img|video|canvas|picture|svg)$/i.test(top.tagName) || pinned(top)) continue;
          let k = '';
          if (opaque(top, ts)) k = 'box';
          else if (ownText(top)) { const tt = textRect(top, false); if (tt && x >= tt.l && x <= tt.r && y >= tt.t && y <= tt.b) k = 'text'; }
          if (!k) continue;
          hit++; if (!by) { by = sel(top); kind = k; layered = s0.position !== 'static' || ts.position !== 'static'; }
        }
      }
      if (total && hit / total >= 0.3) occlusions.push({ sel: sel(el), text: clip(ownText(el), 40), frac: Math.round(hit / total * 100) / 100, kind, by, layered });
    }
  });

  // R40: the same text at several distinct spots inside one card.
  const repeatGroups = [];
  guard('repeatGroups', () => {
    const REP_SKIP = 'table,select,datalist,nav,menu,[role="navigation"],[role="menu"],[role="menubar"],[role="listbox"],[role="grid"],[role="tablist"],[role="radiogroup"],[aria-hidden="true"]';
    const ICON_CLS = /icon|material-symbols|(^|\\s)fa[srlbd]?(\\s|-|$)/i;
    const containers = new Set();
    for (const e of Array.from(d.body.querySelectorAll('div,section,article,aside,main,figure,form,fieldset,details,li')).slice(0, 3000)) {
      if (e.closest(REP_SKIP)) continue;
      const s = cs1(e), shadow = s.boxShadow && s.boxShadow !== 'none';
      const edges = SIDES.filter(k => num(s['border' + k + 'Width']) >= 1).length;
      if ((shadow || edges >= 3) && (num(s.borderTopLeftRadius) > 0 || alphaOf(s.backgroundColor) > 0.1)) containers.add(e);
    }
    for (const c of containers) {
      if (repeatGroups.length >= 10) break;
      const desc = c.querySelectorAll('*'); if (desc.length > 250 || !visible(c)) continue;
      const groups = new Map();
      for (const e of desc) {
        let owned = false; for (let a = e.parentElement; a && a !== c; a = a.parentElement) if (containers.has(a)) { owned = true; break; }
        if (owned || e.closest(REP_SKIP) || ICON_CLS.test(typeof e.className === 'string' ? e.className : '')) continue;
        const t = ownText(e); if (t.length < 4 || t.length > 48 || !/[a-zA-Z]/.test(t) || !visible(e)) continue;
        const sig = []; for (let a = e; a && a !== c; a = a.parentElement) sig.push(a.tagName.toLowerCase() + '.' + (typeof a.className === 'string' ? a.className.trim().split(/\\s+/).filter(x => x && !/\\d{3,}|^(css|sc|jsx|svelte|astro)-/.test(x)).sort().join('.') : ''));
        if (!groups.has(t)) groups.set(t, []); groups.get(t).push(sig.join('>'));
      }
      for (const [t, sigs] of groups) if (sigs.length >= 3 && new Set(sigs).size >= 3) repeatGroups.push({ container: sel(c), text: t, count: sigs.length, distinct: new Set(sigs).size });
    }
  });

  // R20 extension: the element before each heading when it is a small painted container holding an icon.
  const iconTiles = [];
  guard('iconTiles', () => {
    for (const h of d.querySelectorAll('h1,h2,h3,h4,h5,h6')) {
      if (iconTiles.length >= 40) break;
      if (!visible(h)) continue;
      const found = labelBefore(h); if (!found) continue;
      const tile = found.el; if (/^H[1-6]$/.test(tile.tagName) || !visible(tile)) continue;
      const hr = h.getBoundingClientRect(), tr = tile.getBoundingClientRect();
      if (tr.width < 32 || tr.width > 128 || tr.height < 32 || tr.height > 128) continue;
      if (found.levels > 0 && !(tr.top < hr.bottom && Math.max(0, hr.top - tr.bottom, hr.left - tr.right) <= 96)) continue;
      const ts = cs1(tile), icon = tile.querySelector('svg, i[data-lucide], i[class*="fa-"], i[class*="icon"]');
      const emoji = !icon && !tile.children.length && /^\\s*\\p{Extended_Pictographic}/u.test(tile.textContent);
      const ir = icon && icon.getBoundingClientRect();
      iconTiles.push({ hTag: h.tagName.toLowerCase(), hText: clip(h.textContent, 60), hTop: r1(hr.top), w: r1(tr.width), h: r1(tr.height), bottom: r1(tr.bottom),
        bgAlpha: alphaOf(ts.backgroundColor), bgImage: ts.backgroundImage !== 'none', borderW: num(ts.borderTopWidth), radius: num(ts.borderTopLeftRadius),
        hasIcon: !!icon || emoji, iconW: ir ? r1(ir.width) : 0 });
    }
  });

  // R4 extension: text that spills out of its box (overflow visible) and meets another box. Each candidate is scrolled
  // into view before the elementsFromPoint probe (at most PROBE_MAX of them); the scroll position is restored after.
  const textOverflow = [];
  guard('textOverflow', () => {
    const PROBE_MAX = 12;
    let probes = 0;
    try {
      for (let i = 0; i < textEls.length && textOverflow.length < 20 && probes < PROBE_MAX; i++) {
        const el = textEls[i], s = cs1(el);
        if (s.overflowX !== 'visible' || el.clientWidth <= 0 || el.scrollWidth - el.clientWidth < 16) continue;
        let t = textRect(el, false); if (!t) continue;
        let r = el.getBoundingClientRect(), edge = r.left + el.clientLeft + el.clientWidth;
        if (!(t.r > edge + 1)) continue;
        probes++;
        jump(el);
        t = textRect(el, false); r = el.getBoundingClientRect(); edge = r.left + el.clientLeft + el.clientWidth;
        const tol = num(s.fontSize) * 0.25, mid = (t.t + t.b) / 2;
        let meets = null;
        for (let k = 0; k <= 8 && !meets; k++) {
          const x = Math.min(vw1 - 1, edge + 1 + (t.r + tol - edge) * k / 8);
          for (const o of d.elementsFromPoint(x, mid)) {
            if (o === el || el.contains(o) || o.contains(el) || o === d.documentElement || o === d.body) continue;
            const os = cs1(o);
            if (ownText(o) || alphaOf(os.backgroundColor) > 0 || borderSides(os).length || /^(img|svg|video|canvas)$/i.test(o.tagName)) { meets = sel(o); break; }
          }
        }
        textOverflow.push({ sel: sel(el), text: clip(ownText(el), 40), delta: el.scrollWidth - el.clientWidth, meets });
      }
    } finally { restoreScroll(); }
  });

  // R31: the characters of text at opacity 0 or visibility hidden after load, over the whole document. Closed interface,
  // unstarted sliders, timed fade-ins and boxes parked outside a clipping ancestor are left out; a box a scroll shows is shown.
  let hiddenText = { total: 0, hidden: 0, samples: [] };
  await guardAsync('hiddenText', async () => {
    const EXCL = /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|TITLE|HEAD|META|LINK|OPTION|OPTGROUP|SELECT|DATALIST|DIALOG)$/;
    const VIS = /^(hidden|collapse)$/;
    const words = tok => tok.replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
    const classes = e => (e.getAttribute('class') || '').split(/\\s+/).filter(Boolean);
    const says = (e, n) => (e.getAttribute(n) || '').trim().toLowerCase();
    const closedClass = tok => {
      const w = words(tok), has = x => w.includes(x), pair = (a, b) => w.some((x, i) => x === a && w[i + 1] === b);
      if (['offcanvas', 'drawer', 'megamenu', 'submenu', 'dropdown', 'flyout', 'modal', 'tabpanel', 'tabpane'].some(has) || pair('off', 'canvas') || pair('mega', 'menu') || pair('sub', 'menu')) return true;
      return ['content', 'panel', 'pane', 'body'].some(has) && (has('tab') || has('tabs') || has('accordion'));
    };
    let closedIds = null;
    const getClosedIds = () => {
      if (closedIds) return closedIds;
      const closed = new Set(), open = new Set();
      for (const t of d.querySelectorAll('[aria-controls]')) {
        const ex = says(t, 'aria-expanded'), se = says(t, 'aria-selected');
        for (const id of (t.getAttribute('aria-controls') || '').split(/\\s+/).filter(Boolean)) { if (ex === 'true' || se === 'true') open.add(id); else if (ex === 'false' || se === 'false') closed.add(id); }
      }
      for (const id of open) closed.delete(id);
      return closedIds = closed;
    };
    const tabOpen = el => {
      if (el.id && Array.from(d.querySelectorAll('[aria-controls]')).some(t => (t.getAttribute('aria-controls') || '').split(/\\s+/).includes(el.id) && (says(t, 'aria-selected') === 'true' || says(t, 'aria-expanded') === 'true'))) return true;
      const lab = (el.getAttribute('aria-labelledby') || '').trim(); if (!lab) return false;
      return Array.from(d.querySelectorAll('[aria-selected]')).some(t => says(t, 'aria-selected') === 'true' && t.id && lab.split(/\\s+/).includes(t.id));
    };
    const slidOff = a => {
      const s = cs1(a); if (s.position !== 'absolute' && s.position !== 'fixed') return false;
      const tf = s.transform.replace(/\\s/g, ''); if (!tf || tf === 'none' || tf === 'matrix(1,0,0,1,0,0)') return false;
      if (!/(^|,)(transform|all)(,|$)/.test(s.transitionProperty.replace(/\\s/g, '')) || !/[1-9]/.test(s.transitionDuration)) return false;
      const r = a.getBoundingClientRect(); return r.width > 0 && vw1 > 0 && (r.right <= 0 || r.left >= vw1);
    };
    const holdsPage = el => {
      if (el.tagName === 'MAIN' || el.tagName === 'H1' || says(el, 'role') === 'main' || el.querySelector('main,[role="main"],h1')) return true;
      return d.body.textContent.trim().length === 0 || el.textContent.trim().length * 2 >= d.body.textContent.trim().length;
    };
    // closed interface waiting for its trigger
    const closedContainer = el => {
      const ownRole = says(el, 'role'), cls = classes(el);
      const tabLike = ownRole === 'tabpanel' || cls.some(t => words(t).some(w => ['tab', 'tabs', 'tabpanel', 'tabpane'].includes(w)));
      const selected = tabLike && tabOpen(el);
      if (!selected && ['dialog', 'alertdialog', 'tabpanel'].includes(ownRole)) return true;
      if (!selected && cls.some(closedClass)) return true;
      const before = el.previousElementSibling;
      if (before) {
        const wraps = () => /^H[1-6]$/.test(before.tagName) || says(before, 'role') === 'heading' || before.children.length === 1;
        if (says(before, 'aria-expanded') === 'false' || (before.firstElementChild && says(before.firstElementChild, 'aria-expanded') === 'false' && wraps())) return true;
      }
      const s = cs1(el);
      if (s.position === 'fixed') {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && (r.right <= 0 || (vw1 > 0 && r.left >= vw1))) return true;
        if (VIS.test(s.visibility) && vw1 > 0 && vh1 > 0 && r.left <= 1 && r.top <= 1 && r.right >= vw1 - 1 && r.bottom >= vh1 - 1 && !holdsPage(el)) return true;
      }
      for (let a = el; a; a = a.parentElement) {
        if (a.tagName === 'NAV' || ['navigation', 'menu', 'menubar'].includes(says(a, 'role')) || slidOff(a) || a.hasAttribute('inert')) return true;
        if (a.id && getClosedIds().has(a.id)) return true;
      }
      return false;
    };
    // an absolutely positioned box wholly outside an ancestor that clips it
    const parkedOutsideClip = el => {
      if (cs1(el).position !== 'absolute') return false;
      const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
      let outside = false;
      for (let a = el.parentElement; a && a !== d.body && a !== d.documentElement; a = a.parentElement) {
        const as = cs1(a), cx = as.overflowX !== 'visible', cy = as.overflowY !== 'visible'; if (!cx && !cy) continue;
        const ar = a.getBoundingClientRect();
        if ((cx && ar.width < 1) || (cy && ar.height < 1)) return false;
        if ((cx && (r.right <= ar.left || r.left >= ar.right)) || (cy && (r.bottom <= ar.top || r.top >= ar.bottom))) outside = true;
      }
      return outside;
    };
    // sliders that never started
    const SLIDER_W = ['slider', 'carousel', 'swiper', 'slick', 'splide', 'glide', 'flickity', 'slideshow', 'revslider'];
    const SLIDE_W = ['slide', 'item', 'cell', 'card', 'pane', 'caption'];
    const sliderClass = e => classes(e).some(tok => { const w = words(tok); return w.some(x => SLIDER_W.includes(x)) && !w.some(x => SLIDE_W.includes(x)); });
    const showsWithin = (el, upto, ariaHides) => {
      if (VIS.test(cs1(el).visibility)) return false;
      for (let e = el; e; e = e.parentElement) {
        if (cs1(e).display === 'none' || (ariaHides && e.getAttribute('aria-hidden') === 'true') || +cs1(e).opacity <= 0.02) return false;
        if (e === upto) return true;
      }
      return true;
    };
    const sliderVerdict = new Map();
    const unstartedSlider = el => {
      let slider = null, depth = 0;
      for (let a = el; a && depth <= 6; a = a.parentElement, depth++) if (sliderClass(a)) { slider = a; break; }
      if (!slider) return false;
      if (sliderVerdict.has(slider)) return sliderVerdict.get(slider);
      const sw = slider.getBoundingClientRect().width;
      const pictured = e => { const r = e.getBoundingClientRect();
        return e !== slider && r.width >= 1 && r.height >= 1 && (!(sw > 0) || r.width >= 0.5 * sw) && (/^(IMG|PICTURE|VIDEO|CANVAS|svg)$/i.test(e.tagName) || cs1(e).backgroundImage.toLowerCase().includes('url(')); };
      const shows = e => (Array.from(e.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()) && showsWithin(e, slider, true)) || (pictured(e) && showsWithin(e, slider, false));
      const started = shows(slider) || Array.from(slider.querySelectorAll('*')).some(shows);
      sliderVerdict.set(slider, !started);
      return !started;
    };
    // animations (Web Animations API): a scroll or view timeline holds the box at 0; a timed fade-in or a loop shows it
    const own = el => (el.getAnimations ? el.getAnimations().filter(a => a.effect && a.effect.target === el && !a.effect.pseudoElement && a.animationName !== undefined) : []);
    const opacityFrames = a => { try { return a.effect.getKeyframes().filter(k => k.opacity !== undefined && k.opacity !== null && k.opacity !== ''); } catch (e) { return []; } };
    const onDocument = a => !a.timeline || a.timeline instanceof DocumentTimeline;
    const heldByScrollTimeline = el => own(el).some(a => opacityFrames(a).length && !onDocument(a));
    const opacityAnimationShows = el => {
      const fades = own(el).filter(a => opacityFrames(a).length); if (fades.length !== 1) return false;
      const a = fades[0]; if (!onDocument(a) || a.playState === 'paused') return false;
      const ks = opacityFrames(a), t = a.effect.getComputedTiming();
      if (t.iterations === Infinity) return ks.some(k => parseFloat(k.opacity) > 0.02);
      if (a.playState !== 'running' || !['forwards', 'both'].includes(t.fill) || a.effect.composite !== 'replace') return false;
      if (!(Number.isInteger(t.iterations) && t.iterations >= 1 && t.duration > 0 && Math.max(0, t.delay) + t.duration * t.iterations <= 60000)) return false;
      const odd = t.iterations % 2 === 1;
      const endsOnLast = { 'normal': true, 'reverse': false, 'alternate': odd, 'alternate-reverse': !odd }[t.direction];
      if (endsOnLast === undefined) return false;
      const k = endsOnLast ? ks[ks.length - 1] : ks[0];
      return k.offset === (endsOnLast ? 1 : 0) && parseFloat(k.opacity) > 0.02;
    };
    // 0 visible, 1 invisible, 3 left out (not rendered, or closed interface), 4 unstarted slider
    const cache = new Map();
    const state = e => {
      if (!e || e === d.body || e === d.documentElement) return 0;
      if (cache.has(e)) return cache.get(e);
      let st;
      if (EXCL.test(e.tagName)) st = 3;
      else {
        const ps = state(e.parentElement), s = cs1(e);
        if (ps === 3 || s.display === 'none' || e.hidden || e.getAttribute('aria-hidden') === 'true' || s.contentVisibility === 'hidden') st = 3;
        else if (ps === 4) st = 4;
        else if (ps === 1) st = 1;
        else if (+s.opacity <= 0.02 || VIS.test(s.visibility)) {
          const byVis = VIS.test(s.visibility);
          if (closedContainer(e) || parkedOutsideClip(e)) st = 3;
          else if (!byVis && (heldByScrollTimeline(e) || opacityAnimationShows(e))) st = 0;
          else if (unstartedSlider(e)) st = 4;
          else st = 1;
        } else st = 0;
      }
      cache.set(e, st); return st;
    };
    const els = Array.from(d.body.querySelectorAll('*'));
    const stride = Math.max(1, Math.ceil(els.length / 40000));   // an evenly spread sample on a very large document, each counted stride times
    let total = 0, hidden = 0;
    const hiddenEls = [], roots = new Map();
    for (let i = 0; i < els.length; i += stride) {
      const e = els[i], len = ownText(e).length; if (!len) continue;
      const st = state(e); if (st === 3 || st === 4) continue;
      total += len * stride;
      if (st === 1) {
        hidden += len * stride;
        let start = e; while (start.parentElement && cache.get(start.parentElement) === 1) start = start.parentElement;
        hiddenEls.push({ e, start, len: len * stride }); roots.set(start, (roots.get(start) || 0) + len * stride);
      }
    }
    // Scroll-linked reveals: scroll to the largest hidden boxes (8 at most) and measure again.
    const shown = new Set();
    if (total >= 200 && hidden >= 150 && hidden / total > 0.3) {
      const ask = async el => { jump(el); await frame(); await wait(250); const s = cs1(el); return +s.opacity > 0.02 && !VIS.test(s.visibility); };
      const heldInside = (el, start) => {
        let found = null; const hid = x => VIS.test(cs1(x).visibility);
        for (let b = el; b && b !== start; b = b.parentElement) {
          const op = parseFloat(cs1(b).opacity);
          if ((isFinite(op) && op <= 0.02) || (hid(b) && hid(el) && b.parentElement && !hid(b.parentElement))) found = b;
        }
        return found;
      };
      try {
        const shownRoots = new Set();
        for (const [r] of Array.from(roots).sort((a, b) => b[1] - a[1]).slice(0, 8)) if (await ask(r)) shownRoots.add(r);
        const inner = new Map();
        for (const { e, start, len } of hiddenEls) {
          if (!shownRoots.has(start)) continue;
          const b = heldInside(e, start); let ok = true;
          if (b) { if (!inner.has(b)) { if (inner.size >= 8) continue; inner.set(b, await ask(b)); } ok = inner.get(b); }
          if (ok) { hidden -= len; shown.add(e); }
        }
      } finally { restoreScroll(); }
    }
    hiddenText = { total, hidden: Math.max(0, hidden), samples: hiddenEls.filter(x => !shown.has(x.e)).slice(0, 3).map(x => clip(x.e.textContent, 40)) };
  });

  // R42 to R48: each element that names its pattern (data-pattern), with the slots it owns. A slot belongs to the
  // nearest data-pattern element above it; an element with both attributes is a slot of the pattern above it.
  const patterns = [];
  guard('patterns', () => {
    const MAX_PATTERNS = 300, MAX_SLOTS = 40, MAX_CELLS = 400;
    const roots = Array.from(d.querySelectorAll('[data-pattern]')).slice(0, MAX_PATTERNS);
    const index = new Map(roots.map((el, i) => [el, i]));
    const ownerOf = el => { let a = el.parentElement; while (a && !index.has(a)) a = a.parentElement; return a; };
    const parents = new Map(), byIndex = new Map();
    for (const el of roots) {
      const r = el.getBoundingClientRect(), s = v.getComputedStyle(el);
      if ((!r.width && !r.height) || s.visibility === 'hidden') continue;
      if (!parents.has(el.parentElement)) parents.set(el.parentElement, parents.size);
      const own = ownerOf(el);
      const p = { i: index.get(el), id: el.getAttribute('data-pattern'), tag: el.tagName.toLowerCase(), rect: rr(r),
        group: parents.get(el.parentElement), outer: own ? index.get(own) : null, slots: [] };
      const cells = Array.from(el.querySelectorAll('td')).slice(0, MAX_CELLS).map(td => (td.innerText || '').trim()).filter(t => t.length <= 3);
      if (cells.length) p.shortCells = cells;
      patterns.push(p); byIndex.set(p.i, p);
    }
    for (const el of d.querySelectorAll('[data-pattern-slot]')) {
      const own = ownerOf(el); if (!own) continue;
      const p = byIndex.get(index.get(own)); if (!p || p.slots.length >= MAX_SLOTS) continue;
      const s = v.getComputedStyle(el), r = el.getBoundingClientRect();
      const txt = (el.innerText || '').replace(/\\s+/g, ' ').trim();
      let size = parseFloat(s.fontSize), weight = +s.fontWeight || 400;
      for (const t of el.querySelectorAll('*')) { if (!ownText(t)) continue; const ts = v.getComputedStyle(t); if (ts.display === 'none') continue;
        const ps = parseFloat(ts.fontSize), pw = +ts.fontWeight || 400; if (ps > size || (ps === size && pw > weight)) { size = ps; weight = pw; } }
      p.slots.push({ slot: el.getAttribute('data-pattern-slot'), field: el.getAttribute('data-pattern-field') || undefined,
        text: txt.slice(0, TEXT_CAP), empty: !txt && !el.querySelector('img,svg,picture,video,canvas') && !(el.getAttribute('aria-label') || '').trim(),
        hidden: s.display === 'none' || s.visibility === 'hidden' || (!r.width && !r.height) || undefined,
        root: index.has(el) || undefined, fontSize: size, fontWeight: weight, textAlign: s.textAlign,
        numeric: s.fontVariantNumeric !== 'normal' ? s.fontVariantNumeric : undefined, rect: rr(r) });
    }
  });

  return { title: d.title, lang: d.documentElement.lang || '', viewport: { width: v.innerWidth, height: v.innerHeight }, htmlClass: d.documentElement.className || '',
    tokens,
    horizontalOverflow: d.documentElement.scrollWidth > d.documentElement.clientWidth,
    scrollWidth: d.documentElement.scrollWidth, pageHeight: d.documentElement.scrollHeight,
    headings: Array.from(d.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => ({ level: +h.tagName[1], text: h.textContent.trim().slice(0, TEXT_CAP) })),
    landmarks: ['header','nav','main','aside','footer','form','[role]'].map(sel => ({ sel, count: d.querySelectorAll(sel).length })),
    controlsTotal: controlEls.length,
    controls: Array.from(controlEls).slice(0, MAX_CONTROLS).map(el => { const r = el.getBoundingClientRect(); const s = v.getComputedStyle(el); return { tag: el.tagName.toLowerCase(), text: (el.textContent || el.value || el.getAttribute('aria-label') || '').trim().slice(0, LABEL_CAP), w: Math.round(r.width), h: Math.round(r.height),
      labelled: el.tagName !== 'INPUT' || !!(el.labels && el.labels.length) || !!el.getAttribute('aria-label') || !!el.getAttribute('aria-labelledby') || !!el.getAttribute('title'),
      ariaLabel: el.getAttribute('aria-label') || undefined,
      href: el.tagName === 'A' ? el.getAttribute('href') : undefined, type: el.getAttribute('type') || undefined,
      disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true' || undefined,
      inline: s.display === 'inline' || undefined }; }),
    elementsTotal: all.length, textTruncated: text.length >= MAX_ELS,
    scope: { tag: root.tagName.toLowerCase(), rect: rr(root.getBoundingClientRect()) },
    boxes, boxesTotal, gaps, gapsTotal,
    h1s, labels, edgeText, headingGaps, hiddenText, occlusions, repeatGroups, iconTiles, textOverflow, patterns, portErrors,
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
  // The screenshot comes first: the dump scrolls the page to probe reveals and overflow, and a reveal it triggers would show in the picture.
  if (process.env.SHOT) {
    const sc = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(process.env.SHOT, Buffer.from(sc.data, 'base64'));
  }
  if (process.env.DUMP) fs.writeFileSync(process.env.DUMP, JSON.stringify(await evaluate(DUMP_EXPR), null, 1));
  if (logs.length) console.log('CONSOLE_ERRORS', JSON.stringify(logs));
  ws.close(); quit(0);
})();
