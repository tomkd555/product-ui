#!/usr/bin/env python3
"""product-ui: capture a specimen of a component from a live page, as structure only.

Standard library only. Renders the page through scripts/render/cdp.js, finds the elements a
CSS selector names (each one item of the component: a row, a card, a header), and records
for each the parts it holds in reading order: the role of each part (heading, text, link,
button, image, input), the type of its value (date, time, money, count, percent, number,
id, status, free), its emphasis rank inside the item and its length. The source of record is
references/patterns.md, "Adding a pattern from specimens".

What a specimen keeps and leaves out:
- It keeps the structure, the value types and the relations (rank, order, the count of items
  that share one structure). It keeps no text, no colour, no font, no image and no brand.
- The screenshot goes to --cache (a temporary directory by default) and only its SHA-256 is
  recorded, so the capture can be matched later without the image entering the repository.

Where it may run (--source):
- design-system: a design system's public documentation or demo page
- own-product: the user's own product
- oss-app: a demo of an open-source application
- public-site: any other site, only with --terms-checked, after reading the site's terms
  and finding that they allow automated access
Every source is also checked against the site's robots.txt, and a host on BLOCKED_HOSTS,
whose terms forbid automated or AI use, is refused.

CLI:
    python specimen.py <url> --selector <css> --source <kind> --id <id>
                       [--out <dir>] [--cache <dir>] [--terms-checked] [--json]

Writes <out>/<id>.json (default out: the skill's patterns/specimens/).

Exit codes: 0 = written, 1 = refused or nothing matched, 2 = the render failed.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.robotparser

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.normpath(os.path.join(HERE, "..", ".."))
CDP = os.path.join(SKILL_DIR, "scripts", "render", "cdp.js")
OUT_DIR = os.path.join(SKILL_DIR, "patterns", "specimens")
SOURCES = ("design-system", "own-product", "oss-app", "public-site")
# Hosts whose terms forbid scraping, automated access or use in AI work.
BLOCKED_HOSTS = {"mobbin.com": "the terms forbid scrapers and AI use (2026-05-16)"}
MAX_ITEMS = 20
USER_AGENT = "product-ui-specimen"

# Runs inside the page: per matched item, its leaf parts in reading order. Text stays in the
# dump only long enough for the types to be read in Python; the specimen keeps none of it.
PROBE = r"""(() => {
  const SEL = __SEL__, MAX = __MAX__;
  const items = Array.from(document.querySelectorAll(SEL)).slice(0, MAX);
  const role = el => {
    const t = el.tagName.toLowerCase(), r = el.getAttribute('role');
    if (/^h[1-6]$/.test(t) || r === 'heading') return 'heading';
    if (t === 'a' && el.hasAttribute('href') || r === 'link') return 'link';
    if (t === 'button' || r === 'button') return 'button';
    if (['img', 'picture', 'video', 'canvas'].includes(t) || r === 'img') return 'image';
    if (t === 'svg') { const b = el.getBoundingClientRect(); return b.width >= 32 && b.height >= 32 ? 'image' : null; }
    if (['input', 'select', 'textarea'].includes(t)) return 'input';
    return null;
  };
  const own = el => Array.from(el.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  const visible = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  return items.map(item => {
    const parts = [];
    const walk = (el, inside) => {
      if (!visible(el)) return;
      const r = role(el);
      const s = getComputedStyle(el);
      if (r && r !== 'heading') {
        parts.push({ role: r, text: (el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('alt') || '').replace(/\s+/g, ' ').trim().slice(0, 200),
          size: parseFloat(s.fontSize), weight: +s.fontWeight || 400, inside });
        return;
      }
      const t = own(el);
      if (t) parts.push({ role: r || inside || 'text', text: t.slice(0, 200), size: parseFloat(s.fontSize), weight: +s.fontWeight || 400,
        boxed: s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent' && parseFloat(s.paddingLeft) > 0 });
      for (const c of el.children) walk(c, r === 'heading' ? 'heading' : inside);
    };
    walk(item, null);
    const b = item.getBoundingClientRect();
    return { tag: item.tagName.toLowerCase(), w: Math.round(b.width), h: Math.round(b.height), parts };
  });
})()"""

TYPES = (
    ("date", re.compile(r"^(\d{4}[/.\-年]\d{1,2}([/.\-月]\d{1,2}日?)?|\d{1,2}月\d{1,2}日(（.）)?|\d{1,2}/\d{1,2}"
                        r"|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}(, \d{4})?)$")),
    ("time", re.compile(r"^\d{1,2}:\d{2}$")),
    ("money", re.compile(r"^[¥$€£]\s?[\d,]+(\.\d+)?$|^[\d,]+(\.\d+)?\s?円$")),
    ("percent", re.compile(r"^[-+]?\d+(\.\d+)?\s?[%％]$")),
    ("count", re.compile(r"^\d[\d,]*\s?(件|個|人|名|点|items?|results?)$", re.IGNORECASE)),
    ("number", re.compile(r"^[-+]?\d[\d,]*(\.\d+)?$")),
    ("id", re.compile(r"^#?[A-Z]{0,6}[-_]?\d[\w\-]{2,}$")),
)
STATUS = re.compile(r"^.{1,6}(済み|中|待ち)$|^(完了|未完了|未着手|未対応|下書き|公開|非公開|有効|無効)$")


def value_type(part):
    text = part["text"]
    if not text:
        return "none"
    for name, pattern in TYPES:
        if pattern.match(text):
            return name
    if STATUS.match(text) or (part.get("boxed") and len(text) <= 12 and " " not in text.strip()):
        return "status"
    return "free"


def ranks(parts):
    """Emphasis rank per part: 1 for the strongest (size, weight) pair in the item."""
    pairs = sorted({(p["size"], p["weight"]) for p in parts if p["text"]}, reverse=True)
    return [pairs.index((p["size"], p["weight"])) + 1 if p["text"] else None for p in parts]


def anatomy(item):
    parts = item["parts"]
    rank = ranks(parts)
    return [{"role": p["role"], "type": value_type(p), "rank": rank[i], "chars": len(p["text"])}
            for i, p in enumerate(parts)]


def signature(parts):
    return " | ".join(f"{p['role']}:{p['type']}" for p in parts)


def refuse_reason(url, source, terms_checked):
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    for blocked, why in BLOCKED_HOSTS.items():
        if host == blocked or host.endswith("." + blocked):
            return f"{host} is refused: {why}"
    if source == "public-site" and not terms_checked:
        return "a public site needs --terms-checked: read its terms first and capture only when they allow automated access"
    if host in ("localhost", "127.0.0.1") or host.endswith(".local"):
        return None
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(urllib.parse.urljoin(url, "/robots.txt"))
    try:
        robots.read()
    except OSError:
        return None
    if not robots.can_fetch(USER_AGENT, url):
        return f"robots.txt of {host} disallows {urllib.parse.urlparse(url).path}"
    return None


def main():
    parser = argparse.ArgumentParser(description="Capture a component specimen from a live page, as structure only.")
    parser.add_argument("url")
    parser.add_argument("--selector", required=True, help="CSS selector of one item of the component")
    parser.add_argument("--source", required=True, choices=SOURCES)
    parser.add_argument("--id", required=True, help="the specimen id: <source name>.<component>[.<n>]")
    parser.add_argument("--out", default=OUT_DIR)
    parser.add_argument("--cache", default=None, help="where the screenshot goes (a temporary directory by default)")
    parser.add_argument("--terms-checked", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    why = refuse_reason(args.url, args.source, args.terms_checked)
    if why:
        print(f"REFUSED: {why}")
        return 1
    cache = args.cache or tempfile.mkdtemp(prefix="specimen-")
    os.makedirs(cache, exist_ok=True)
    shot = os.path.join(cache, args.id + ".png")
    expr = PROBE.replace("__SEL__", json.dumps(args.selector)).replace("__MAX__", str(MAX_ITEMS))
    proc = subprocess.run(["node", CDP, args.url, "1280", expr], capture_output=True, text=True,
                          env=dict(os.environ, SHOT=shot), encoding="utf-8")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print(f"FAIL: the render failed: {args.url}")
        return 2
    items = json.loads(proc.stdout.split("\nCONSOLE_ERRORS", 1)[0])
    items = [i for i in items if i["parts"]]
    if not items:
        print(f"FAIL: `{args.selector}` matched no visible item with content at {args.url}")
        return 1
    shapes = [anatomy(i) for i in items]
    sigs = [signature(s) for s in shapes]
    common = max(set(sigs), key=sigs.count)
    sha = ""
    if os.path.isfile(shot):
        with open(shot, "rb") as handle:
            sha = hashlib.sha256(handle.read()).hexdigest()
    specimen = {
        "id": args.id,
        "source": {"kind": args.source, "url": args.url, "selector": args.selector,
                   "captured": datetime.date.today().isoformat(), "viewport": 1280, "screenshot_sha256": sha},
        "items": len(items),
        "items_sharing_the_anatomy": sigs.count(common),
        "item_tag": items[sigs.index(common)]["tag"],
        "anatomy": shapes[sigs.index(common)],
        "signature": common,
        "variants": sorted(set(sigs) - {common}),
        "status": "captured",
    }
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, args.id + ".json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(specimen, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    if args.json:
        print(json.dumps(specimen, ensure_ascii=False, indent=2))
    else:
        print(f"{args.id}: {len(items)} item(s), {sigs.count(common)} share `{common}`")
        print(f"PASS: wrote {path}; screenshot in {shot}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
