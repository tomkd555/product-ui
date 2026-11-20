#!/usr/bin/env python3
"""product-ui: copy the ready-made parts of assets/kit into a project.

Standard library only. The kit holds the parts every screen of an application repeats: the shell, the
formats of dates and amounts, the behaviour of a collection (search, filters, views, sort, pages in the
URL), the status badge, the empty state, the bulk bar, the confirmation step and the form field. A part
is copied once and then belongs to the project, which adapts it; assets/kit/kit.json names what each
part gives and what a project changes in it. The source of record is references/components.md (The kit).

The parts are written for the `shadcn` stack: React, Tailwind v4 through theme.css, the shadcn/ui
components under `@/components/ui` and react-router-dom.

The parts named `desktop-*` (layout `electron` in kit.json) are the document window of an Electron
application (references/desktop.md). They are copied only into a project with electron-vite's layout,
`src/main` and `src/renderer/src`: the main and preload parts go to `src/main` and `src/preload`, the types
both processes share to `src/shared`, and the renderer parts under `src/renderer/src`, which is where the
`@/` alias points. In such a project, with no part named, the desktop parts are copied.

CLI:
    python kit.py <project-dir> [part ...] [--force] [--json]
    python kit.py --list [--json]

With no part named, every part is copied. A part brings the parts it needs. The destination is
`<project-dir>/src` where that directory exists, else `<project-dir>`; it is the directory the `@/`
alias points to (`src/renderer/src` in an electron-vite project). A file the project already holds is kept unless --force is given.

Exit codes: 0 = done, 1 = an unknown part or a missing directory.
"""

import argparse
import json
import os
import re
import shutil
import sys

KIT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "kit")


def load_parts():
    with open(os.path.join(KIT_DIR, "kit.json"), encoding="utf-8") as handle:
        return json.load(handle)["parts"]


def with_needs(names, by_name):
    """The named parts and the parts they need, in the order of kit.json."""
    wanted, queue = set(), list(names)
    while queue:
        name = queue.pop()
        if name not in wanted:
            wanted.add(name)
            queue += by_name[name].get("needs", [])
    return [name for name in by_name if name in wanted]


def is_electron_vite(project):
    """Whether the project has electron-vite's layout: src/main and src/renderer/src."""
    return (os.path.isdir(os.path.join(project, "src", "main"))
            and os.path.isdir(os.path.join(project, "src", "renderer", "src")))


def installed_packages(project):
    try:
        with open(os.path.join(project, "package.json"), encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return set(data.get("dependencies") or {}) | set(data.get("devDependencies") or {})


def imports_stylesheet(root, name):
    """Whether a stylesheet directly under `root` already imports `name`."""
    pattern = re.compile(r"@import\s+[\"'][^\"']*" + re.escape(name) + r"[\"']")
    for entry in sorted(os.listdir(root)):
        if entry.endswith(".css") and entry != name:
            with open(os.path.join(root, entry), encoding="utf-8") as handle:
                if pattern.search(handle.read()):
                    return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Copy the ready-made parts of the kit into a project.")
    parser.add_argument("project", nargs="?", help="the project directory")
    parser.add_argument("parts", nargs="*", help="the parts to copy (default: every part)")
    parser.add_argument("--list", action="store_true", help="print the parts and what each gives")
    parser.add_argument("--force", action="store_true", help="replace a file the project already holds (of the named parts, else of every part)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    parts = load_parts()
    by_name = {part["name"]: part for part in parts}
    if args.list:
        if args.json:
            print(json.dumps(parts, ensure_ascii=False, indent=2))
        else:
            for part in parts:
                print(f"{part['name']} ({part['file']})\n  gives: {part['gives']}\n  customise: {part['customise']}")
        return 0
    if not args.project or not os.path.isdir(args.project):
        print(f"FAIL: no such directory: {args.project}", file=sys.stderr)
        return 1
    unknown = [name for name in args.parts if name not in by_name]
    if unknown:
        print(f"FAIL: unknown part: {', '.join(unknown)}; --list prints the parts", file=sys.stderr)
        return 1

    project = os.path.abspath(args.project)
    electron = is_electron_vite(project)
    if electron:
        root = os.path.join(project, "src", "renderer", "src")
    else:
        root = os.path.join(project, "src") if os.path.isdir(os.path.join(project, "src")) else project
    desktop = [name for name, part in by_name.items() if part.get("layout") == "electron"]
    wrong = [name for name in args.parts if name in desktop and not electron]
    if wrong:
        print(f"FAIL: {', '.join(wrong)} needs electron-vite's layout (src/main and src/renderer/src) in {project}", file=sys.stderr)
        return 1
    default = desktop if electron else [name for name in by_name if name not in desktop]
    # On electron-vite the window's parts always go in; a named part (form-field, line-grid) is one a pane or the
    # document area imports, and it joins them.
    chosen = with_needs((desktop + [n for n in args.parts if n not in desktop]) if electron else (args.parts or default), by_name)
    # --force replaces the parts named on the command line; with none named it replaces every chosen part.
    forced = set(args.parts) if args.parts else set(chosen)
    copied, kept, ui, npm, imports = [], [], [], [], []
    for name in chosen:
        part = by_name[name]
        if part.get("layout") == "electron":
            target = os.path.join(project, "src", *part["target"].split("/"))
        else:
            target = os.path.join(root, *part["file"].split("/"))
        if os.path.exists(target) and not (args.force and name in forced):
            kept.append(part.get("target", part["file"]))
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(os.path.join(KIT_DIR, *part["file"].split("/")), target)
            copied.append(part.get("target", part["file"]))
        ui += [c for c in part.get("ui", []) if c not in ui]
        npm += [p for p in part.get("npm", []) if p not in npm]
        if part.get("import") and not imports_stylesheet(root, part["file"]):
            imports.append(part["import"])

    ui_dir = os.path.join(root, "components", "ui")
    missing_ui = [c for c in ui if not os.path.exists(os.path.join(ui_dir, c + ".tsx"))]
    packages = installed_packages(project)
    missing_npm = [p for p in npm if packages is None or p not in packages]
    result = {"status": "PASS", "root": root, "copied": copied, "kept": kept,
              "shadcn_add": missing_ui, "npm_install": missing_npm, "stylesheet_imports": imports}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    for path in copied:
        print(f"copied: {path}")
    for path in kept:
        print(f"kept (the project's own file): {path}")
    if missing_ui:
        print(f"next: npx shadcn@latest add {' '.join(missing_ui)}")
    if missing_npm:
        print(f"next: npm install {' '.join(missing_npm)}")
    for line in imports:
        print(f"next: add to the project's stylesheet, after the import of theme.css: {line}")
    print(f"PASS: {len(copied)} copied, {len(kept)} kept, into {root}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
