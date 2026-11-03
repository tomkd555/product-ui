#!/usr/bin/env python3
"""Benchmark measure for the real-site patterns work: what each rendered item tells its reader.

Standard library only. Renders one benchmark screen through product-ui's `cdp.js`, finds the
item that shows each sample record, and scores which of the record's fields the item shows.
The benchmark specs live beside this file (`<id>/bench.json`, `<id>/data.json`); README.md
holds the method.

An item is the largest element that contains one record's locator and no other record's.
A record's locator is the first of `object.locators` whose value appears on the screen; every
locator value is unique across the sample data. A `single` screen scores the whole <main>
(else <body>) against its one record.

A field counts as shown when its value appears in the item's rendered text:

- text: the value, spaces ignored
- money, count: the number as a token, commas and spaces ignored (1,320,000 or 1320000)
- number: the number as written (4.6)
- date: 2026-11-05, 2026/11/05, 2026/11/5, 11/5, 11/05, 2026年11月5日 or 11月5日
- datetime: the time (10:30); the date may sit in a group heading above the item
- list: any one member
- lines: every line item's name

An empty value is not scored.

CLI:
    python measure.py <bench dir> <screen id> <url> --out <dir>
                      [--cdp <path to cdp.js>] [--src <app src dir> --skill <skill dir>] [--json]

Writes <out>/<bench>-<screen>.png, .dom.json and .json (the scores). With --src and
--skill, also runs the skill's check_copy.py over the app source and counts C18 to C21.

Exit codes: 0 = measured, 2 = the render failed.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CDP = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "plugins", "product-ui", "skills", "product-ui", "scripts", "render", "cdp.js"))
LABEL_CHECKS = ("C18", "C19", "C20", "C21")

# Runs inside the page: per record, the item that shows it.
PROBE = r"""(() => {
  const RECS = __RECS__, SINGLE = __SINGLE__;
  const root = document.querySelector('main') || document.body;
  const squash = s => (s || '').replace(/\s+/g, '');
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const holds = (el, rec) => rec.locs.some(v => v && squash(el.innerText).includes(squash(v)));
  const count = el => RECS.filter(r => holds(el, r)).length;
  if (SINGLE) return { single: true, text: root.innerText.slice(0, 6000) };
  const items = [];
  for (const rec of RECS) {
    let best = null;
    for (const loc of rec.locs) {
      if (!loc) continue;
      const want = squash(loc);
      const hits = [];
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
      for (let el = walker.currentNode; el; el = walker.nextNode()) {
        if (!(el instanceof HTMLElement) || !visible(el)) continue;
        if (!squash(el.innerText).includes(want)) continue;
        // the smallest element holding the locator: no child holds it too
        if ([...el.children].some(c => c instanceof HTMLElement && squash(c.innerText).includes(want))) continue;
        hits.push(el);
      }
      for (const hit of hits) {
        let item = hit;
        while (item.parentElement && item.parentElement !== root.parentElement && count(item.parentElement) <= 1) item = item.parentElement;
        const siblings = item.parentElement ? count(item.parentElement) : 0;
        if (!best || siblings > best.siblings) best = { item, siblings, loc };
      }
      if (best) break;
    }
    if (!best) { items.push({ id: rec.id, found: false }); continue; }
    const el = best.item, r = el.getBoundingClientRect();
    items.push({ id: rec.id, found: true, locator: best.loc, tag: el.tagName.toLowerCase(),
      text: el.innerText.slice(0, 1200), rect: { x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) },
      link: !!(el.closest('a[href]') || el.matches('[role="link"]')), inner_controls: el.querySelectorAll('a[href],button,[role="button"]').length,
      collection: best.siblings });
  }
  return { single: false, items };
})()"""


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def squash(text):
    return re.sub(r"\s+", "", text or "")


def number_tokens(text):
    return {t.replace(",", "") for t in re.findall(r"\d[\d,]*(?:\.\d+)?", text.replace(" ", ""))}


def date_forms(value):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not m:
        return [value]
    y, mo, d = m.group(1), m.group(2), m.group(3)
    mi, di = str(int(mo)), str(int(d))
    return [f"{y}-{mo}-{d}", f"{y}/{mo}/{d}", f"{y}/{mi}/{di}", f"{mi}/{di}", f"{mo}/{d}",
            f"{y}年{mi}月{di}日", f"{mi}月{di}日"]


def shown(kind, value, text):
    """Whether a field value of this kind appears in the rendered text."""
    if value in (None, "", []):
        return None
    flat = squash(text)
    if kind == "text":
        return squash(str(value)) in flat
    if kind in ("money", "count"):
        return str(value) in number_tokens(text)
    if kind == "number":
        return str(value) in number_tokens(text)
    if kind == "date":
        return any(f in flat for f in date_forms(value))
    if kind == "datetime":
        return value.split("T")[1] in flat if "T" in value else any(f in flat for f in date_forms(value))
    if kind == "list":
        return any(squash(v) in flat for v in value)
    if kind == "lines":
        return all(squash(line["item"]) in flat for line in value)
    return squash(str(value)) in flat


def render(cdp, url, rec_locs, single, out_png, out_dom):
    expr = PROBE.replace("__RECS__", json.dumps(rec_locs, ensure_ascii=False)).replace("__SINGLE__", "true" if single else "false")
    env = dict(os.environ, SHOT=out_png, DUMP=out_dom)
    proc = subprocess.run(["node", cdp, url, "1280", expr], capture_output=True, text=True, env=env, encoding="utf-8")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return None
    body = proc.stdout.split("\nCONSOLE_ERRORS", 1)[0]
    return json.loads(body)


def label_findings(src, skill):
    script = os.path.join(skill, "scripts", "check_copy.py")
    proc = subprocess.run([sys.executable, script, src, "--json"], capture_output=True, text=True, encoding="utf-8")
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        return {"error": proc.stderr.strip()[:400]}
    findings = data.get("findings", data if isinstance(data, list) else [])
    counts = {c: 0 for c in LABEL_CHECKS}
    for f in findings:
        cid = f.get("id") or f.get("check")
        if cid in counts:
            counts[cid] += 1
    return counts


def score(bench, data, screen, probe):
    fields = dict(bench["object"]["fields"])
    fields.update(screen.get("extra_fields", {}))
    records = data["records"]
    key = bench["object"]["locators"][0]
    job = screen["job_fields"]
    if probe["single"]:
        rec = next(r for r in records if r[key] == screen["record"])
        hits = {f: shown(fields[f][1], rec.get(f), probe["text"]) for f in fields}
        scored = {f: v for f, v in hits.items() if v is not None}
        return {"kind": "single", "record": screen["record"],
                "fields_shown": sorted(f for f, v in scored.items() if v),
                "fields_missing": sorted(f for f, v in scored.items() if not v),
                "job_fields_missing": [f for f in job if scored.get(f) is False]}
    by_id = {r[key]: r for r in records}
    rows = []
    for item in probe["items"]:
        rec = by_id[item["id"]]
        if not item["found"]:
            rows.append({"id": item["id"], "found": False})
            continue
        hits = {f: shown(fields[f][1], rec.get(f), item["text"]) for f in fields}
        scored = {f: v for f, v in hits.items() if v is not None}
        job_scored = [f for f in job if f in scored]
        rows.append({"id": item["id"], "found": True, "locator": item["locator"], "tag": item["tag"],
                     "link": item["link"], "inner_controls": item["inner_controls"], "height": item["rect"]["h"],
                     "fields_shown": sorted(f for f, v in scored.items() if v),
                     "job_shown": sum(1 for f in job_scored if scored[f]), "job_scored": len(job_scored)})
    found = [r for r in rows if r["found"]]
    n = len(found) or 1
    return {
        "kind": "collection",
        "records": len(rows),
        "found": len(found),
        "mean_fields_per_item": round(sum(len(r["fields_shown"]) for r in found) / n, 2),
        "fields_available": len(fields),
        "job_coverage": round(sum(r["job_shown"] / r["job_scored"] for r in found if r["job_scored"]) / n, 3),
        "items_with_all_job_fields": sum(1 for r in found if r["job_scored"] and r["job_shown"] == r["job_scored"]),
        "items_linked": sum(1 for r in found if r["link"]),
        "mean_item_height": round(sum(r["height"] for r in found) / n, 1),
        "never_shown": sorted(set(fields) - set().union(*[set(r["fields_shown"]) for r in found])) if found else sorted(fields),
        "items": rows,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bench")
    ap.add_argument("screen")
    ap.add_argument("url")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cdp", default=DEFAULT_CDP)
    ap.add_argument("--src")
    ap.add_argument("--skill")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    bench = load(os.path.join(args.bench, "bench.json"))
    data = load(os.path.join(args.bench, "data.json"))
    screen = next(s for s in bench["screens"] if s["id"] == args.screen)
    locs = bench["object"]["locators"]
    key = locs[0]
    rec_locs = [{"id": r[key], "locs": [str(r.get(k, "")) for k in locs]} for r in data["records"]]
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.join(args.out, f"{bench['id']}-{args.screen}")
    probe = render(args.cdp, args.url, rec_locs, screen["kind"] == "single", stem + ".png", stem + ".dom.json")
    if probe is None:
        print(f"render failed: {args.url}", file=sys.stderr)
        sys.exit(2)
    result = {"bench": bench["id"], "screen": args.screen, "url": args.url}
    result.update(score(bench, data, screen, probe))
    with open(stem + ".dom.json", encoding="utf-8") as f:
        dump = json.load(f)
    result["enclosures"] = len(dump.get("boxes", []))
    if args.src and args.skill:
        result["labels"] = label_findings(args.src, args.skill)
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["kind"] == "single":
        print(f"{bench['id']}/{args.screen}: shown {len(result['fields_shown'])}, missing {result['fields_missing']}, "
              f"job missing {result['job_fields_missing']}")
    else:
        print(f"{bench['id']}/{args.screen}: found {result['found']}/{result['records']}, "
              f"fields/item {result['mean_fields_per_item']}/{result['fields_available']}, "
              f"job coverage {result['job_coverage']}, all job fields {result['items_with_all_job_fields']}, "
              f"never shown {result['never_shown']}")


if __name__ == "__main__":
    main()
